from pathlib import Path
from PIL import Image
import hashlib,json
root=Path(__file__).resolve().parent;repo=root.parents[2]
catalog=json.loads((root/'effect_specs/review_v1/animation_catalog.json').read_text(encoding='utf-8'))
records=[]
for spec in catalog['specs']:
    folder=(repo/spec['layers']['ornament']).parent
    for path in sorted(folder.glob('*.png')):
        im=Image.open(path);assert im.mode=='RGBA';hist=im.getchannel('A').histogram()
        records.append(dict(design_id=spec['id'],source_record=spec['layers']['source_record'],file=path.relative_to(repo).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),dimensions=im.size,mode=im.mode,transparent_pixels=hist[0],partial_pixels=sum(hist[1:255]),opaque_pixels=hist[255],kind='original_ornament_copy' if path.name=='ornament_rgba.png' else 'derived_glow' if path.name=='glow_rgba.png' else 'original_component_fragment',status='review_user_selection_pending',final_approved=False))
report=dict(design_count=35,effect_png_count=len(records),assets=records,final_approved_count=0)
(root/'EFFECT_ASSET_INVENTORY_V1.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('effect_png_count',len(records))
