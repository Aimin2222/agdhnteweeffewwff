from lab_common import *
from PIL import Image
import hashlib,collections
limited=load(V3/'SOURCE_LIMITATIONS_INHERITED_V3.json');names={Path(x['source']).name for x in limited['assets']}
cmd=['rg','--files',str(R.parent.parent),'-g','*.png','-g','*.jpg','-g','*.jpeg','-g','*.webp','-g','*.psd','-g','*.kra','-g','*.svg']
r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace');paths=[Path(x) for x in r.stdout.splitlines()];matches=[]
for p in paths:
 if p.name in names or ('40テーマ' in p.name and ('対決' in p.name or 'アイコン' in p.name)):
  try:
   b=p.read_bytes()
   with Image.open(p) as im:dims=list(im.size)
   matches.append({'relative_location':str(p.relative_to(R.parent.parent)).replace('\\','/'),'filename':p.name,'sha256':hashlib.sha256(b).hexdigest(),'dimensions':dims,'bytes':len(b)})
  except Exception as e:matches.append({'filename':p.name,'error':type(e).__name__})
save('SOURCE19_SEARCH_V4.json',{'scope':'read-only file inventory inside user Codex documents workspace; no arbitrary whole-drive scan','image_or_design_paths_examined':len(paths),'matches':matches,'distinct_hashes':sorted({x['sha256'] for x in matches if 'sha256' in x}),'items':[dict(x,investigation_status='REVIEW_REQUIRED',extra_complete_source_found=False) for x in limited['assets']],'automatic_reconstruction':False,'full_source_still_required':True,'search_return_code':r.returncode})
print(json.dumps({'paths_examined':len(paths),'matches':len(matches),'distinct_hashes':len({x['sha256'] for x in matches if 'sha256' in x})}))
