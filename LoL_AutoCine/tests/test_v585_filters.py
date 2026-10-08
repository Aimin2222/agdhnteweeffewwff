"""Offline 1080p FFmpeg graph tests. No LoL or Windows device required."""
import sys, subprocess, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from core.effects import Template, build_graph, FFMPEG

def probe(t, kind):
    graph = build_graph(t, duration=0.5, has_title=False, pre_filters='scale=1920:1080:flags=lanczos')
    cmd = [FFMPEG, '-y', '-hide_banner', '-loglevel', 'error', '-f', 'lavfi', '-i',
           'testsrc2=size=1920x1080:rate=10:duration=0.4', '-filter_complex', graph,
           '-map','[vout]', '-frames:v','3', '-f','null','-']
    s = time.perf_counter()
    p = subprocess.run(cmd,capture_output=True,text=True,timeout=180)
    if p.returncode: raise AssertionError(f'{kind} {p.stderr[-1800:]}')
    print(kind,'PASS',round(time.perf_counter()-s,2),'seconds')

if __name__=='__main__':
    t = Template(grade='tealorange', bloom=0.28, grain=0.1, vignette=.3, bars=.0, transition='flash')
    probe(t,'bloom')
    t.bloom=0
    t.dof_enabled=True
    t.dof_blur=10
    probe(t,'dof')
    t.bloom=0.28
    probe(t,'dof+bloom')
    t.video_effects['focus_blur']=.25
    probe(t,'dof+bloom+focus_blur')
