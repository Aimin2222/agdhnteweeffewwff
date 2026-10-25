from pathlib import Path
import json,hashlib,base64,sys
root=Path(__file__).resolve().parents[2];w=root/'work/autocine_research_v4_20261025'
manifest=json.loads((w/'upload_manifest.json').read_text('utf-8'))
if sys.argv[1]=='list':print(json.dumps(manifest));sys.exit(0)
p=Path(manifest[int(sys.argv[1])]['local']).resolve();assert p.is_relative_to((root/'outputs').resolve())
offset=int(sys.argv[2]);assert offset%4==0
with p.open('rb') as f:f.seek(offset//4*3);chunk=base64.b64encode(f.read(600000)).decode('ascii')
print(json.dumps({'total':((p.stat().st_size+2)//3)*4,'chunk':chunk}))
