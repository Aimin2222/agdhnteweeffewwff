"""Single-residency RGBA video effects. CPU prepares resources once per template.

Production devices are strictly OpenCL GPUs. No Python per-frame pixel loop.
Keep the legacy renderer available when a driver/filter or resource fails.
"""
from __future__ import annotations

from functools import lru_cache
import math
import os
from pathlib import Path
import subprocess
import tempfile

from .gpu_bloom import OPENCL_DEVICE, _gaussian_table, shader_source


EFFECT_ORDER = ('motion_camera', 'camera_shake', 'wiggle', 'spin_motion',
                'zoom_blur', 'radial_blur', 'glitch', 'kaleidoscope', 'vhs_damage',
                'block_motion', 'chroma_leak', 'flash', 'focus_blur', 'vignette_fx',
                'glint', 'vr_blur', 'vr_light_leak', 'sphere_blur', 'panel_wipe',
                'stretch_wipe', 'mirror', 'slice')


def mode():
    value = os.environ.get('AUTOCINE_GPU_EFFECTS', 'full').lower()
    return value if value in {'full', 'hybrid', 'cpu'} else 'full'


def esc(path):
    return str(path).replace('\\', '/').replace(':', r'\:').replace("'", r"\'")


def number(value):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('GPU parameter must be finite')
    return f'{value:.9f}f'


@lru_cache(maxsize=16)
def _bake_color(ffmpeg, filters):
    """Bake FFmpeg's exact eq/colorbalance/curves/LUT definitions on a 33³ cube.

    Use 4:4:4 for the calibration grid: neighboring pixels represent unrelated
    colors and must never share subsampled chroma. Only this tiny calibration
    frame uses software filters; footage samples the resulting LUT on the GPU.
    """
    import numpy as np
    side = 33
    b, g, r = np.indices((side, side, side))
    raw = np.stack((r, g, b), axis=-1)
    raw = np.rint(raw * (255 / (side - 1))).astype('uint8').tobytes()
    cmd = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-filter_threads', '1',
           '-f', 'rawvideo', '-pixel_format', 'rgb24', '-video_size', '1089x33',
           '-i', 'pipe:0', '-vf', 'format=yuv444p,' + filters + ',format=rgb24',
           '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', 'pipe:1']
    result = subprocess.run(cmd, input=raw, capture_output=True, timeout=20)
    if result.returncode or len(result.stdout) != len(raw):
        raise RuntimeError('GPU color LUT preparation failed: ' + result.stderr.decode('utf-8', 'replace')[-600:])
    return result.stdout


COMMON = r'''
const sampler_t nearest_sampler = CLK_NORMALIZED_COORDS_FALSE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_NEAREST;
float noise_at(int2 p, uint frame, uint channel) {
    uint x=(uint)p.x*1973u+(uint)p.y*9277u+frame*26699u+channel*31847u+911u;
    x=(x^(x>>16))*2246822519u; x=(x^(x>>13))*3266489917u; x^=x>>16;
    return (float)(x&65535u)/65535.0f-0.5f;
}
float3 rgb_noise(int2 p,uint frame,float amount) {
    return (float3)(noise_at(p,frame,0),noise_at(p,frame,1),noise_at(p,frame,2))*amount;
}
float4 sample_at(read_only image2d_t src,float2 uv) {
    return read_imagef(src,linear_sampler,uv);
}
float3 apply_lut(read_only image2d_t lut,float3 c) {
    float3 v=clamp(c,0.0f,1.0f)*32.0f;
    int3 lo=convert_int3(floor(v)), hi=min(lo+1,(int3)(32)); float3 f=v-convert_float3(lo);
    float3 a=read_imagef(lut,nearest_sampler,(int2)(lo.y*33+lo.x,lo.z)).xyz;
    float3 b=read_imagef(lut,nearest_sampler,(int2)(lo.y*33+hi.x,lo.z)).xyz;
    float3 c0=read_imagef(lut,nearest_sampler,(int2)(hi.y*33+lo.x,lo.z)).xyz;
    float3 d=read_imagef(lut,nearest_sampler,(int2)(hi.y*33+hi.x,lo.z)).xyz;
    float3 e=read_imagef(lut,nearest_sampler,(int2)(lo.y*33+lo.x,hi.z)).xyz;
    float3 f0=read_imagef(lut,nearest_sampler,(int2)(lo.y*33+hi.x,hi.z)).xyz;
    float3 g=read_imagef(lut,nearest_sampler,(int2)(hi.y*33+lo.x,hi.z)).xyz;
    float3 h=read_imagef(lut,nearest_sampler,(int2)(hi.y*33+hi.x,hi.z)).xyz;
    return mix(mix(mix(a,b,f.x),mix(c0,d,f.x),f.y),mix(mix(e,f0,f.x),mix(g,h,f.x),f.y),f.z);
}
float vignette_factor(float2 uv,float2 size,float angle) {
    float d=length((uv-0.5f)*size)/length(size*0.5f);
    float v=cos(min(1.570796327f,d*angle)); return v*v*v*v;
}
float3 eq_rgb(float3 rgb,float contrast,float brightness,float saturation) {
    // BT.601 is FFmpeg eq's default matrix for unspecified RGB input.
    float y=dot(rgb,(float3)(0.299f,0.587f,0.114f));
    float scaled=clamp(contrast*((16.0f+219.0f*y)/255.0f-0.5f)+0.5f+brightness,16.0f/255.0f,235.0f/255.0f);
    float new_y=(scaled*255.0f-16.0f)/219.0f;
    return clamp((rgb-y)*saturation+new_y,0.0f,1.0f);
}
// Bicubic scaling keeps fine HUD/portrait edges; same-size sampling is exact.
float cubic(float x) {
    x=fabs(x); return x<=1.0f ? (1.5f*x-2.5f)*x*x+1.0f :
        x<2.0f ? ((-0.5f*x+2.5f)*x-4.0f)*x+2.0f : 0.0f;
}
float4 resize_bicubic(read_only image2d_t src,float2 uv) {
    float2 size=(float2)(get_image_width(src),get_image_height(src));
    float2 xy=uv*size-0.5f; int2 base=convert_int2(floor(xy)); float2 f=xy-convert_float2(base);
    float4 out=(float4)(0);
    for(int y=-1;y<=2;y++)for(int x=-1;x<=2;x++)
        out+=read_imagef(src,nearest_sampler,base+(int2)(x,y))*cubic((float)x-f.x)*cubic((float)y-f.y);
    return clamp(out,0.0f,1.0f);
}
kernel void color_scale(write_only image2d_t dst,uint index,read_only image2d_t src,read_only image2d_t lut) {
    int2 p=(int2)(get_global_id(0),get_global_id(1));
    if(p.x>=get_image_width(dst)||p.y>=get_image_height(dst))return;
    float2 uv=uv_for(dst,p);
    float4 c=(get_image_width(src)==get_image_width(dst)&&get_image_height(src)==get_image_height(dst)) ?
        sample_at(src,uv) : resize_bicubic(src,uv);
    write_imagef(dst,p,(float4)(apply_lut(lut,c.xyz),c.w));
}
'''


def kernel(name, body, inputs=1):
    declarations = ','.join('read_only image2d_t ' + n for n in ('src', 'aux', 'old1', 'old2', 'old3')[:inputs])
    return f'''\nkernel void {name}(write_only image2d_t dst,uint index,{declarations}) {{
    int2 p=(int2)(get_global_id(0),get_global_id(1));
    if(p.x>=get_image_width(dst)||p.y>=get_image_height(dst))return;
    float2 uv=uv_for(dst,p),size=(float2)(get_image_width(dst),get_image_height(dst));
    float time=(float)index/FPS;
    float4 c=sample_at(src,uv);
    {body}
    write_imagef(dst,p,clamp(c,0.0f,1.0f));
}}\n'''


def event_gate(events, before=0, after=0):
    return '(' + ' || '.join(f'(time>={number(max(0,a-before))} && time<={number(b+after)})'
                            for a,b in events) + ')' if events else '0'


class GPUFullStage:
    """Own temporary CL/LUT resources until FFmpeg finishes, including retries."""
    def __init__(self, template, duration, events, *, ffmpeg, title_index=None,
                 badge_index=1, badges=(), lut_index=1, size=(1920,1080)):
        self.folder = tempfile.TemporaryDirectory(prefix='autocine-full-gpu-')
        self.path = Path(self.folder.name)/'effects.cl'
        self.lut = Path(self.folder.name)/'color.png'
        self.effects = set()
        self.graph = ''
        try:
            self._build(template, duration, events, ffmpeg, title_index, badge_index,
                        badges, lut_index, size)
        except BaseException:
            self.close()
            raise

    def close(self):
        self.folder.cleanup()

    def _build(self, t, duration, events, ffmpeg, title_index, badge_index, badges, lut_index, size):
        from PIL import Image
        from .effects import color_filters, FOG_RGB
        from .kill_icons import badge_plan, normalize_options, normalize
        active = {k: max(0.,min(1.,float(v))) for k,v in t.video_effects.items() if float(v)>.001}
        unknown = set(active)-set(EFFECT_ORDER)
        if unknown:
            raise ValueError('Unsupported GPU effects: '+','.join(sorted(unknown)))
        if not 1 <= int(t.fps) <= 240:
            raise ValueError('Invalid GPU FPS')
        # Include source LUT contents/mtime in cache identity through its filter
        # string: external LUTs bypass the cache so edits take effect immediately.
        filters = ','.join(color_filters(t))
        raw = (_bake_color.__wrapped__ if t.lut_path else _bake_color)(ffmpeg, filters)
        Image.frombytes('RGB',(1089,33),raw).convert('RGBA').save(self.lut)
        code = '#define FPS '+number(t.fps)+'\n'+shader_source(t)+COMMON
        stages = [f'[0:v]fps=fps={int(t.fps)}:round=near,setpts=PTS-STARTPTS,format=rgba,hwupload[fg_src]',
                  f'[{lut_index}:v]settb=1/{int(t.fps)},setpts=0,format=rgba,hwupload[fg_lut]']
        serial = 0
        current = 'fg_src'
        w,h = size
        def program(name, inputs=1, output_size=None):
            return f"program_opencl=source='{esc(self.path)}':kernel={name}:inputs={inputs}" + (
                f':size={output_size[0]}x{output_size[1]}' if output_size else '')
        def step(name, body=None, extra=(), output_size=None):
            nonlocal serial,current,code
            if body is not None:
                code += kernel(name,body,1+len(extra))
            serial += 1
            out=f'fg_{serial}'
            stages.append(''.join(f'[{x}]' for x in (current,*extra))+program(name,1+len(extra),output_size)+f'[{out}]')
            current=out
        def blur(name,sigma,merge=None):
            nonlocal serial,current,code
            code += _gaussian_table(name,sigma)+f'\nBLUR_KERNEL({name}_x,{name},0)\nBLUR_KERNEL({name}_y,{name},1)\n'
            if merge:
                stages.append(f'[{current}]split=2[{name}_orig][{name}_work]')
                current=name+'_work'
            step(name+'_x',output_size=(max(1,w//2),max(1,h//2)))
            step(name+'_y')
            if merge:
                blurred=current
                current=name+'_orig'
                step(name+'_combine',merge,(blurred,),size)
            else:
                step('copy_rgba',output_size=size)
        def temporal(name, frames):
            nonlocal current
            labels=[f'{name}_lag{i}' for i in range(frames)]
            stages.append(f'[{current}]split={frames}'+''.join('['+x+']' for x in labels))
            for i in range(1,frames):
                stages.append(f'[{labels[i]}]loop=loop={i}:size=1:start=0,setpts=N/({int(t.fps)}*TB)[{labels[i]}_d]')
                labels[i]+='_d'
            current=labels[0]
            # tmix uses past frames; duplicated first frame pads startup. A
            # normalized sum avoids the legacy zoom scale=4 clipping bug.
            names=('src','aux','old1','old2','old3')[:frames]
            weights=(1,2,1) if frames==3 else (1,2,1,1,1)
            body='c=('+'+'.join(f'{number(k)}*sample_at({n},uv)' for k,n in zip(weights,names))+')/'+number(sum(weights))+';'
            step(name+'_temporal',body,tuple(labels[1:]))
        step('color_scale',extra=('fg_lut',),output_size=size)
        self.effects.add('color_grade')
        self.effects.add('scale')
        if t.lut_path and Path(t.lut_path).exists(): self.effects.add('lut')
        if t.curve_enabled: self.effects.add('curves')
        for name in EFFECT_ORDER:
            k=active.get(name,0)
            if not k: continue
            self.effects.add(name)
            body=''
            if name in {'motion_camera','camera_shake','wiggle'}:
                crop,amp,px,py,factor=(.94,3+18*k,2.7,3.1,.55) if name=='motion_camera' else (
                    (.96,2+22*k,.12,.095,.7) if name=='camera_shake' else (.98,1+10*k,.55,.43,.7))
                fy='sin' if name=='wiggle' else 'cos'
                body=f'float2 q=0.5f+(uv-0.5f)*{number(crop)}+(float2)(sin(6.2831853f*time/{number(px)})*{number(amp)},{fy}(6.2831853f*time/{number(py)})*{number(amp*factor)})/size; c=sample_at(src,q);'
            elif name=='spin_motion':
                body=f'float a=sin(6.2831853f*time/0.8f)*{number(.015+.09*k)}; float2 q=(uv-0.5f)*size; q=(float2)(cos(a)*q.x+sin(a)*q.y,-sin(a)*q.x+cos(a)*q.y)/size+0.5f; c=(q.x<0||q.x>1||q.y<0||q.y>1)?(float4)(0,0,0,1):sample_at(src,q);'
            elif name in {'radial_blur','zoom_blur'}:
                if name=='zoom_blur':
                    step(name+'_scale',f'float z=1.0f+{number(.025+.10*k)}*fabs(sin(6.2831853f*time/1.6f)); c=sample_at(src,0.5f+(uv-0.5f)/z);')
                temporal(name,5 if name=='radial_blur' and k>=.6 else 3)
                continue
            elif name in {'glitch','vhs_damage','chroma_leak'}:
                px=int(2+18*k) if name=='glitch' else int(1+7*k) if name=='vhs_damage' else int(4+32*k)
                body=f'c.x=sample_at(src,uv-(float2)({number(px)}/size.x,0)).x; c.z=sample_at(src,uv+(float2)({number(px)}/size.x,0)).z;'
                if name!='chroma_leak':
                    amount=int(6+20*k) if name=='glitch' else int(10+25*k)
                    body+=f'c.xyz+=rgb_noise(p,index,{number(amount/255)});'
                else: body='if('+event_gate(events,.02,.08)+'){'+body+'}'
            elif name=='kaleidoscope':
                body=f'float3 other=sample_at(src,(float2)(1-uv.x,uv.y)).xyz; c.xyz=mix(c.xyz,1-(1-c.xyz)*(1-other),{number(.12+.35*k)});'
            elif name=='block_motion':
                bs=int(12+44*k)
                # Average once per block, then replicate in a second GPU pass.
                grid=(math.ceil(w/bs),math.ceil(h/bs))
                step('block_average',f'int2 start=p*{bs}; float4 sum=(float4)(0); int count=0; for(int y=0;y<{bs};y++)for(int x=0;x<{bs};x++){{int2 q=start+(int2)(x,y); if(q.x<get_image_width(src)&&q.y<get_image_height(src)){{sum+=read_imagef(src,nearest_sampler,q); count++;}}}} c=sum/(float)max(1,count);',output_size=grid)
                step('block_replicate',f'c=read_imagef(src,nearest_sampler,p/{bs});',output_size=size)
                continue
            elif name=='flash':
                center=events[0][0] if events else 0
                body=f'if({event_gate(events,0,.15)}) c.xyz=eq_rgb(c.xyz,1,{number(.18+.65*k)}*exp(-18.0f*fabs(time-{number(center)})),1);'
            elif name in {'focus_blur','vr_blur','sphere_blur'}:
                sigma=1+8*k if name=='focus_blur' else 1+7*k if name=='vr_blur' else .8+5*k
                blur(name,sigma); continue
            elif name=='vignette_fx':
                body=f'c.xyz*=vignette_factor(uv,size,{number(1.05-.45*k)});'
            elif name=='glint':
                body='float3 blur=(float3)(0); const float weights[5]={1,4,6,4,1}; for(int y=-2;y<=2;y++)for(int x=-2;x<=2;x++)blur+=weights[x+2]*weights[y+2]*sample_at(src,uv+(float2)(x,y)/size).xyz; c.xyz=clamp(c.xyz+0.45f*(c.xyz-blur/256.0f),0.0f,1.0f);'
                body+=f'c.xyz=eq_rgb(c.xyz,{number(1+.25*k)},{number(.02+.08*k)},1);'
            elif name=='vr_light_leak':
                # FFmpeg colorize replaces chroma, and mix controls retained
                # source lightness (it is not RGB overlay opacity).
                import colorsys
                color=colorsys.hls_to_rgb(28/360,.62,.85)
                body=f'if({event_gate(events,.10,.28)}){{float3 tint=(float3)({",".join(number(x) for x in color)}); float ty=dot(tint,(float3)(0.299f,0.587f,0.114f)); float y=dot(c.xyz,(float3)(0.299f,0.587f,0.114f)); c.xyz=tint+{number(.10+.28*k)}*(y-ty);}}'
            elif name in {'panel_wipe','stretch_wipe'}:
                length=(.45 if name=='panel_wipe' else .35)+.25*k
                body=f'c.xyz*=clamp(time/{number(length)},0.0f,1.0f);'
            elif name=='mirror': body='c=sample_at(src,(float2)(1-uv.x,uv.y));'
            elif name=='slice': body=f'c=sample_at(src,(float2)(uv.x+{number(.02+.18*k)}*(float)index-floor(uv.x+{number(.02+.18*k)}*(float)index),uv.y));'
            step(name,body)
        pulse=max(0.,min(1.,float(t.highlight_pulse)))
        if pulse>.001 and events:
            wave='+'.join(f'exp(-22.0f*fabs(time-{number(a)}))' for a,_ in events[:8])
            step('highlight_pulse',f'float v=min(1.0f,{wave}); c.xyz=eq_rgb(c.xyz,1,{number(.11*pulse)}*v,1+{number(.10*pulse)}*v);')
            self.effects.add('highlight_pulse')
        if t.dof_enabled and t.dof_blur>.01:
            if t.dof_shape=='band':
                near=max(1.,t.dof_near_distance); focus=max(near,t.dof_focus_distance); far=max(focus+1,t.dof_far_distance)
                fc=max(.05,min(.95,focus/(near+focus+far)))
                span=max(.02,min(max(.02,min(.48,(focus-near)/(focus+far))),max(.02,min(.48,(far-focus)/(focus+far)))))
                mask=f'clamp(fabs(uv.y-{number(fc)})/{number(span)}-1,0.0f,1.0f)'
            else:
                from .focus_fx import focus_settings
                cx,cy,radius,feather=focus_settings(t)
                mask=f'clamp((length((uv-(float2)({number(cx)},{number(cy)}))*(float2)(size.x/size.y,1))-{number(radius)})/{number(feather)},0.0f,1.0f)'
            blur('full_dof',max(.1,min(20,t.dof_blur))*1.15, f'c=mix(c,sample_at(aux,uv),{mask});')
            self.effects.add('dof')
        if t.bloom>0:
            blur('full_bloom',11,f'float3 b=clamp(sample_at(aux,uv).xyz-0.05f,0.0f,1.0f); c.xyz=mix(c.xyz,1-(1-c.xyz)*(1-b),{number(min(.6,.45*t.bloom))});')
            self.effects.add('bloom')
        body=''
        if t.vignette>0:
            body+=f'c.xyz*=vignette_factor(uv,size,{number(1.1-.5*min(1,t.vignette))});'
            self.effects.add('vignette')
        if t.grain>0:
            body+=f'c.xyz+=rgb_noise(p,index,{number(int(18*t.grain)/255)});'
            self.effects.add('grain')
        if t.bpm>0:
            body+=f'c.xyz=eq_rgb(c.xyz,1,0.10f*exp(-9.0f*fmod(time,{number(60/t.bpm)})),1);'
            self.effects.add('bpm')
        if t.bars>0:
            edge=.12*min(1,t.bars)
            body+=f'if(uv.y<{number(edge)}||uv.y>1-{number(edge)})c.xyz=(float3)(0);'
            self.effects.add('bars')
        if t.fog_enabled and t.fog_strength>.001:
            rgb=FOG_RGB.get(t.fog_preset,FOG_RGB['teal'])
            body+=f'c.xyz=mix(c.xyz,(float3)({",".join(number(int(x*255)/255) for x in rgb)}),{number(min(.45,t.fog_strength*.35))});'
            self.effects.add('fog')
        if body: step('finish_base',body)
        if title_index is not None:
            label='fg_title'
            stages.append(f'[{title_index}:v]settb=1/{int(t.fps)},setpts=0,format=rgba,hwupload[{label}]')
            end=max(1,duration-.6)-.5
            alpha=f'clamp((time-0.3f)/0.5f,0.0f,1.0f)*clamp(1-(time-{number(end)})/0.5f,0.0f,1.0f)'
            self._overlay(step,'title',label,'(size.x-ow)/2','size.y*0.14f',alpha)
            self.effects.add('title')
        # Clip transitions precede kill overlays, preserving the existing order.
        if t.transition in {'flash','fade'}:
            a,b=(.18,.22) if t.transition=='flash' else (.3,.35)
            start=float(f'{max(.1,duration-b):.2f}')
            col='(float3)(1)' if t.transition=='flash' else '(float3)(0)'
            step('clip_transition',f'float alpha=clamp(time/{number(a)},0.0f,1.0f)*clamp(1-(time-{number(start)})/{number(b)},0.0f,1.0f); c.xyz=mix({col},c.xyz,alpha);')
            self.effects.add('transition')
        position,scale,seconds,opacity=normalize_options(t.kill_icon_position,t.kill_icon_scale,t.kill_icon_duration,t.kill_icon_opacity)
        plan=badge_plan(badges,duration,seconds)
        for n,entry in enumerate(plan):
            label=f'fg_badge_{n}'
            stages.append(f'[{badge_index+entry["index"]}:v]settb=1/{int(t.fps)},setpts=0,format=rgba,hwupload[{label}]')
            # GPU scales and applies opacity; PNG rasterization happens once.
            x='size.x-ow-32' if position.startswith('right') else '32.0f'
            if normalize(t.kill_icon_style)=='impact':
                x+=f'+7*sin(35*(time-{number(entry["time"])}))*exp(-11*fabs(time-{number(entry["time"])}))'
            # Same scaled badge height + unscaled editor gap as CPU compositing.
            from .kill_icons import normalize_stack_gap
            row=int(round(116*scale + normalize_stack_gap(getattr(t, 'kill_stack_gap', 4))))*entry['row']
            y=f'62.0f+{row}' if position.endswith('top') else f'size.y-oh-62-{row}'
            alpha=f'{number(opacity)}*(time>={number(entry["start"])} && time<={number(entry["end"])})'
            self._overlay(step,f'badge_{n}',label,x,y,alpha,scale)
        if plan: self.effects.add('kill_icons')
        # program_opencl does not advertise its input frame rate. Re-establish
        # timestamps and rate with metadata filters to prevent default 25fps
        # output, duplicate EOF frames, or endless PNG-driven framesync.
        count=max(1,math.ceil(duration*int(t.fps)))
        stages.append(f'[{current}]trim=end_frame={count},setpts=N/({int(t.fps)}*TB),fps=fps={int(t.fps)}:round=near,hwdownload,format=rgba[vout]')
        self.graph=';'.join(stages)
        self.path.write_text(code,encoding='utf-8')

    @staticmethod
    def _overlay(step,name,label,x,y,alpha,scale=1):
        body=f'float ow=floor(get_image_width(aux)*{number(scale)}/2)*2,oh=floor(get_image_height(aux)*{number(scale)}/2)*2; float2 q=(convert_float2(p)-(float2)({x},{y}))/(float2)(ow,oh); if(q.x>=0&&q.x<1&&q.y>=0&&q.y<1){{float4 b=sample_at(aux,q); c.xyz=mix(c.xyz,b.xyz,b.w*({alpha}));}}'
        step(name,body,(label,))


@lru_cache(maxsize=1)
def full_runtime_probe(ffmpeg):
    """Compile all kernels; exercise LUT, temporal memory and compositing on GPU."""
    from .effects import Template
    stage=None
    try:
        t=Template(grade='standard',bloom=0,vignette=0,grain=0,transition='cut',
                   video_effects={'radial_blur':.2,'mirror':1})
        stage=GPUFullStage(t,.1,[(.02,.05)],ffmpeg=ffmpeg,lut_index=1,size=(64,64))
        cmd=[ffmpeg,'-hide_banner','-loglevel','error','-init_hw_device',OPENCL_DEVICE,
             '-filter_hw_device','ocl','-f','lavfi','-i','color=c=0x4080c0:s=64x64:r=60:d=0.1',
             '-i',str(stage.lut),
             '-filter_complex',stage.graph,'-map','[vout]','-frames:v','3','-f','null','-']
        r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=20)
        return r.returncode==0, '' if r.returncode==0 else r.stderr[-1200:]
    except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired) as e:
        return False,str(e)[-1200:]
    finally:
        if stage is not None: stage.close()


@lru_cache(maxsize=32)
def decode_probe(ffmpeg, source, mtime_ns):
    """Probe real NVDEC decoding for this input; codec support is not inferred."""
    try:
        r=subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-hwaccel','cuda',
                          '-i',str(source),'-an','-frames:v','1','-f','null','-'],
                         capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=8)
        return r.returncode==0, '' if r.returncode==0 else r.stderr[-450:]
    except (OSError,subprocess.TimeoutExpired) as e:
        return False,str(e)[-450:]


def render_gpu_montage(ffmpeg, source, output, style, cuts, encoding, logger=None):
    """Optional GPU cut accents; stream-copy audio and retain the input clock."""
    import re
    from .gpu_pipeline import detect
    from .effects import Template
    from .performance_diagnostics import run_render, _encoder_name
    if mode() != 'full' or not detect().full_gpu_runtime_ok:
        return False
    try:
        header=subprocess.run([ffmpeg,'-hide_banner','-i',str(source)],capture_output=True,
                              text=True,encoding='utf-8',errors='replace',timeout=10)
        rate=re.search(r'Video:.*?([0-9]+(?:\.[0-9]+)?) fps',header.stderr)
        if not rate: raise ValueError('Montage frame rate could not be verified')
        fps=float(rate[1])
        if not math.isfinite(fps) or fps<=0: raise ValueError('Invalid montage FPS')
        # Constant frame rate is required by frame-index timing. App exports
        # integer CFR; foreign fractional/VFR clips keep the existing t graph.
        if abs(fps-round(fps))>.001: raise ValueError('Non-integer montage FPS: CPU timing preserved')
        width,height=(.09,.22) if style=='flash' else (.18,-.24)
        pulse='+'.join(f'{number(height)}*max(0.0f,1-fabs(time-{number(c)})/{number(width)})' for c in cuts)
        with tempfile.TemporaryDirectory(prefix='autocine-montage-gpu-') as folder:
            path=Path(folder)/'montage.cl'
            path.write_text('#define FPS '+number(fps)+'\n'+shader_source(Template())+COMMON+
                            kernel('montage',f'c.xyz=eq_rgb(c.xyz,1,{pulse or "0.0f"},1);'),encoding='utf-8')
            filt=f"format=rgba,hwupload,program_opencl=source='{esc(path)}':kernel=montage,setpts=N/({int(fps)}*TB),fps={int(fps)},hwdownload,format=rgba"
            args=list(encoding)
            if 'h264_nvenc' in args and '-pix_fmt' in args: args[args.index('-pix_fmt')+1]='rgba'
            cmd=[ffmpeg,'-y','-hide_banner','-loglevel','error','-init_hw_device',OPENCL_DEVICE,
                 '-filter_hw_device','ocl','-i',str(source),'-vf',filt,'-map','0:v:0','-map','0:a?',
                 *args,'-c:a','copy','-movflags','+faststart',str(output)]
            r=run_render(cmd,output=output,gpu_effects=['montage_'+style],effect_values={},timeout=900,
                         pipeline_info={'stage':'montage','full_gpu_pipeline':True,'cpu_video_effects':[],
                                        'montage_style':style,'input_fps':fps,'filter_graph':filt})
            if r.returncode or not Path(output).is_file() or Path(output).stat().st_size<1024:
                raise RuntimeError(r.stderr[-800:] or 'GPU montage output missing')
            if logger:
                logger(f'モンタージュ演出を適用: {style} / 切り替え {len(cuts)}回 / 映像フィルター=OpenCL GPU / エンコーダー={_encoder_name(r.args)} / 音声=copy')
            return True
    except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired) as exc:
        if logger: logger('GPUモンタージュ失敗 → 同じ演出をCPUで再試行: '+str(exc)[-400:])
        return False
