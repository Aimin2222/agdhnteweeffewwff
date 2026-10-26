"""Non-vacuous checks: the candidate must fire, at the expected frame."""
from pathlib import Path
import json,subprocess
import numpy as np
R=Path(__file__).resolve().parents[2];O=R/'outputs/autocine_implementation_specs_20261026'
FF='C:/Users/saoan/Documents/Codex/2026-10-18/lol-autocine-work-windows-pc-usb/work/runtime-bin/ffmpeg.exe'
a=json.loads((O/'FLASH_BOUNDARY_RESULTS.json').read_text('utf-8-sig'));rows=[]
def render(graph,fps):
 p=subprocess.run([FF,'-hide_banner','-nostdin','-loglevel','error','-f','lavfi','-i',f'color=c=gray:s=64x36:r={fps}:d=2','-vf',','.join(graph+['format=gray']),'-f','rawvideo','-pix_fmt','gray','pipe:1'],capture_output=True,timeout=15)
 assert p.returncode==0,p.stderr;return np.frombuffer(p.stdout,np.uint8).reshape(-1,36,64)
for x in a['cases']:
 v=x.get('v5_tick_gate_probe')
 if not v:continue
 b=render([],x['fps']);c=render(v['graph'],x['fps']);ix=np.flatnonzero(np.any(c!=b,axis=(1,2)));first=int(ix[0]) if len(ix) else None;starts=v['event_start_frames']
 rows.append({'fps':x['fps'],'strength':x['strength'],'expected_first_changed_frame':starts[0],'actual_first_changed_frame':first,'onset_is_exact':first==starts[0],'second_event_frame_is_nonzero':bool(np.any(c[starts[1]]!=b[starts[1]])),'decoded_frames':len(c)})
(O/'FLASH_V5_POSITIVE_ONSET_RESULTS.json').write_text(json.dumps({'scope':'six CFR probes only; confirms effect is not always zero','cases':rows,'pass':all(x['onset_is_exact'] and x['second_event_frame_is_nonzero'] for x in rows)},indent=2),encoding='utf-8');print(json.dumps(rows))
