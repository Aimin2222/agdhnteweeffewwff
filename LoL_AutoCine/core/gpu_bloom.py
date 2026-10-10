"""GPU-only OpenCL RGBA blur/compositing, with no Python frame copy loop."""
from pathlib import Path
import math
import tempfile
from .focus_fx import focus_settings

OPENCL_DEVICE = 'opencl=ocl:,device_type=gpu'


def _gaussian_table(name, sigma):
    """Normalize once per template, not exp/divide for every GPU pixel."""
    radius = math.ceil(3 * sigma)
    weights = [math.exp(-.5 * k * k / (sigma * sigma)) for k in range(radius + 1)]
    total = weights[0] + 2 * sum(weights[1:])
    values = ','.join(f'{w / total:.12f}f' for w in weights)
    return f'__constant float {name}_weights[] = {{{values}}};\n#define {name}_radius {radius}\n'


def _finite(value, lower, upper):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('GPU effect parameter must be finite')
    return max(lower, min(upper, value))


def shader_source(template):
    cx, cy, radius, feather = focus_settings(template)
    if not all(math.isfinite(v) for v in (cx, cy, radius, feather)):
        raise ValueError('Invalid focus settings')
    sigma = _finite(template.dof_blur, .1, 20)*1.15
    opacity = min(.6, .45*_finite(template.bloom, 0, 2))
    # Half-resolution separable Gaussian; normalized sampling also resizes.
    tables = _gaussian_table('bloom', 11.0) + _gaussian_table('dof', sigma)
    return tables + r'''
const sampler_t linear_sampler = CLK_NORMALIZED_COORDS_TRUE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_LINEAR;
float2 uv_for(write_only image2d_t dst, int2 pos) {
    return (convert_float2(pos)+0.5f)/(float2)(get_image_width(dst),get_image_height(dst));
}
float4 gaussian(read_only image2d_t src, float2 uv, __constant float *weights, int radius, int vertical, float2 texel) {
    float2 step = vertical ? (float2)(0,texel.y) : (float2)(texel.x,0);
    float4 sum=weights[0]*read_imagef(src,linear_sampler,uv);
    for(int k=1;k<=radius;k++) {
        sum+=weights[k]*(read_imagef(src,linear_sampler,uv+step*(float)k)
                       +read_imagef(src,linear_sampler,uv-step*(float)k));
    }
    return sum;
}
#define BLUR_KERNEL(name,kind,axis) \
kernel void name(write_only image2d_t dst, uint index, read_only image2d_t src) { \
    int2 p=(int2)(get_global_id(0),get_global_id(1)); \
    if(p.x>=get_image_width(dst)||p.y>=get_image_height(dst))return; \
    float2 texel=(float2)(1.0f/get_image_width(dst),1.0f/get_image_height(dst)); \
    write_imagef(dst,p,gaussian(src,uv_for(dst,p),kind##_weights,kind##_radius,axis,texel)); \
}
BLUR_KERNEL(bloom_x,bloom,0)
BLUR_KERNEL(bloom_y,bloom,1)
BLUR_KERNEL(dof_x,dof,0)
BLUR_KERNEL(dof_y,dof,1)
kernel void bloom_merge(write_only image2d_t dst,uint index,read_only image2d_t src,read_only image2d_t blurred) {
    int2 p=(int2)(get_global_id(0),get_global_id(1));
    if(p.x>=get_image_width(dst)||p.y>=get_image_height(dst))return;
    float2 uv=uv_for(dst,p); float4 a=read_imagef(src,linear_sampler,uv);
    float4 b=read_imagef(blurred,linear_sampler,uv);
    b.xyz=clamp(b.xyz-0.05f,0.0f,1.0f);
    float3 screened=1.0f-(1.0f-a.xyz)*(1.0f-b.xyz);
    write_imagef(dst,p,(float4)(mix(a.xyz,screened,BLOOM_OPACITY),a.w));
}
kernel void dof_merge(write_only image2d_t dst,uint index,read_only image2d_t src,read_only image2d_t blurred) {
    int2 p=(int2)(get_global_id(0),get_global_id(1));
    if(p.x>=get_image_width(dst)||p.y>=get_image_height(dst))return;
    float2 uv=uv_for(dst,p);
    float2 delta=uv-(float2)(CENTER_X,CENTER_Y);
    delta.x*=((float)get_image_width(dst)/get_image_height(dst));
    float mask=clamp((length(delta)-FOCUS_RADIUS)/FOCUS_FEATHER,0.0f,1.0f);
    float4 a=read_imagef(src,linear_sampler,uv),b=read_imagef(blurred,linear_sampler,uv);
    write_imagef(dst,p,mix(a,b,mask));
}
kernel void copy_rgba(write_only image2d_t dst,uint index,read_only image2d_t src) {
    int2 p=(int2)(get_global_id(0),get_global_id(1));
    if(p.x>=get_image_width(dst)||p.y>=get_image_height(dst))return;
    write_imagef(dst,p,read_imagef(src,linear_sampler,uv_for(dst,p)));
}
'''.replace('BLOOM_OPACITY', f'{opacity:.6f}f').replace(
        'CENTER_X', f'{cx:.6f}f').replace('CENTER_Y', f'{cy:.6f}f').replace(
        'FOCUS_RADIUS', f'{radius:.6f}f').replace('FOCUS_FEATHER', f'{feather:.6f}f')


class GPUBlurStage:
    def __init__(self, template, caps):
        self.effects = set()
        self.path = None
        self.graph = ''
        if not getattr(caps, 'rgba_gpu_runtime_ok', False):
            return
        if template.dof_enabled and template.dof_blur > .01 and template.dof_shape == 'circle':
            self.effects.add('dof')
        if template.bloom > 0:
            self.effects.add('bloom')
        if not self.effects:
            return
        source = shader_source(template)
        f = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.cl', prefix='autocine-gpu-', delete=False)
        self.path = Path(f.name)
        try:
            with f:
                f.write(source)
        except BaseException:
            self.close()
            raise
        escaped = str(self.path).replace('\\','/').replace(':',r'\:').replace("'",r"\'")
        def program(kernel, inputs=1, half=False):
            return (f"program_opencl=source='{escaped}':kernel={kernel}:inputs={inputs}" +
                    (':size=960x540' if half else ''))
        stages = ['format=rgba,hwupload']
        # Both effects remain in GPU memory; download once after compositing.
        for name in ('dof','bloom'):
            if name not in self.effects:
                continue
            stages.append(f'split=2[{name}gpu_orig][{name}gpu_work];'
                          f'[{name}gpu_work]{program(name+"_x",half=True)},'
                          f'{program(name+"_y")}[{name}gpu_blur];'
                          f'[{name}gpu_orig][{name}gpu_blur]{program(name+"_merge",inputs=2)}')
        self.graph = ','.join(stages)+',hwdownload,format=rgba'

    def close(self):
        if self.path is not None:
            try:
                self.path.unlink(missing_ok=True)
            except OSError:
                pass
