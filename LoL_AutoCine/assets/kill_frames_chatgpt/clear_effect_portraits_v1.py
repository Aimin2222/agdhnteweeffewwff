from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import json,numpy as np
root=Path(__file__).resolve().parent;repo=root.parents[2]
inventory=json.loads((root/'original_alpha/review_v1/inventory.json').read_text(encoding='utf-8'))
by_file={r['file']:r for r in inventory['assets']}
catalog_path=root/'effect_specs/review_v1/animation_catalog.json';catalog=json.loads(catalog_path.read_text(encoding='utf-8'))
for spec in catalog['specs']:
    rec=by_file[spec['layers']['source_record']];path=repo/spec['layers']['glow'];im=Image.open(path).convert('RGBA');mask=Image.new('L',im.size);d=ImageDraw.Draw(mask)
    for hole in rec['portrait_holes']:
        kind,values=next(iter(hole.items()));pts=np.asarray(values).reshape(-1,2)-np.array(rec['crop_box'][:2])+np.array([24,24])
        if kind=='polygon':d.polygon([tuple(p) for p in pts],fill=255)
        else:getattr(d,kind)(tuple(pts.reshape(-1)),fill=255)
    im.putalpha(ImageChops.multiply(im.getchannel('A'),ImageChops.invert(mask)));im.save(path)
    spec['layers']['glow_declared_portrait_holes_cleared']=True
catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Cleared glow portrait holes for',len(catalog['specs']),'designs')
