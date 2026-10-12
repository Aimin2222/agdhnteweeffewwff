"""Two-source spatial transitions on the existing OpenCL GPU device; QA only."""
from pathlib import Path
import math
import tempfile

from . import gpu_full


class SpatialStage:
    def __init__(self, style, length, duration, *, width=1920, height=1080, fps=60):
        self.folder = tempfile.TemporaryDirectory(prefix='autocine-spatial-')
        self.path = Path(self.folder.name) / 'spatial.cl'
        offset = length - duration
        steps = {
            'fade': 'c=mix(a,b,q);',
            'wipeleft': 'c=uv.x>=1.0f-q?b:a;',
            'slideright': 'c=uv.x<q?read_imagef(second,s,(float2)(uv.x+1.0f-q,uv.y)):read_imagef(first,s,(float2)(uv.x-q,uv.y));',
            'circleopen': 'float2 aspect=(float2)((float)get_image_width(dst)/get_image_height(dst),1); c=length((uv-.5f)*aspect)<=q*length(.5f*aspect)?b:a;',
            'pixelize': 'float block=1.0f+36.0f*sin(3.14159265f*q); float2 pixel=floor(uv*size/block)*block+block*.5f; c=mix(read_imagef(first,s,pixel/size),read_imagef(second,s,pixel/size),q);',
            'smoothup': 'float eased=q*q*(3.0f-2.0f*q); c=uv.y<1.0f-eased?read_imagef(first,s,(float2)(uv.x,uv.y+eased)):read_imagef(second,s,(float2)(uv.x,uv.y-1.0f+eased));',
        }
        try:
            body = steps[style]
            self.path.write_text(f'''const sampler_t s=CLK_NORMALIZED_COORDS_TRUE|CLK_ADDRESS_CLAMP_TO_EDGE|CLK_FILTER_LINEAR;
kernel void spatial(write_only image2d_t dst,uint index,read_only image2d_t first,read_only image2d_t second) {{
 int2 p=(int2)(get_global_id(0),get_global_id(1));
 if(p.x>=get_image_width(dst)||p.y>=get_image_height(dst))return;
 float2 size=(float2)(get_image_width(dst),get_image_height(dst)),uv=(convert_float2(p)+.5f)/size;
 float time=(float)index/{fps}.0f,q=clamp((time-{offset:.9f}f)/{duration:.9f}f,0.0f,1.0f);
 float4 a=read_imagef(first,s,uv),b=read_imagef(second,s,uv),c=a;
 if(q<=0)c=a;else if(q>=1)c=b;else{{{body}}}
 write_imagef(dst,p,clamp(c,0.0f,1.0f));
}}''', encoding='utf-8')
            prepare = f'trim=duration={length:.9f},fps=fps={fps},setpts=PTS-STARTPTS,format=rgba,hwupload'
            count = math.ceil((2*length-duration)*fps)
            stop_frames = max(0, count-math.ceil(length*fps))
            start_frames = round(offset*fps)
            # Clone hardware frames before/after the overlap; do not download
            # to software xfade or upload decoded padding frames repeatedly.
            self.graph = (f'[0:v]{prepare},tpad=stop_mode=clone:stop={stop_frames}[a];'
                          f'[1:v]{prepare},tpad=start_mode=clone:start={start_frames}[b];'
                          f'[a][b]program_opencl=source=\'{gpu_full.esc(self.path)}\':kernel=spatial:inputs=2:size={width}x{height},'
                          f'trim=end_frame={count},setpts=N/({fps}*TB),fps=fps={fps},hwdownload,format=rgba[v]')
        except Exception:
            self.close()
            raise

    def close(self):
        self.folder.cleanup()
