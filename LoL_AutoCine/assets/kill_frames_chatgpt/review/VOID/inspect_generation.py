"""Inspection only: generated PNG bytes are copied without modification."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, shutil, sys

out = Path(__file__).parent
source = Path(sys.argv[1])
generated = [Path(p) for p in sys.argv[2:]]
records = []
for i, path in enumerate(generated, 1):
    target = out / f'016_weak_slit_attempt_{i:02d}_review_rgba.png'
    shutil.copyfile(path, target)
    im = Image.open(target)
    a = im.getchannel('A')
    hist = a.histogram()
    edges = {
        'top': a.crop((0, 0, im.width, 1)),
        'bottom': a.crop((0, im.height-1, im.width, im.height)),
        'left': a.crop((0, 0, 1, im.height)),
        'right': a.crop((im.width-1, 0, im.width, im.height)),
    }
    record = dict(file=target.name, mode=im.mode, dimensions=im.size,
                  sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                  git_blob_sha1=hashlib.sha1(b'blob '+str(target.stat().st_size).encode()+b'\0'+target.read_bytes()).hexdigest(),
                  bytes=target.stat().st_size, transparent_pixels=hist[0],
                  partial_alpha_pixels=sum(hist[1:255]), opaque_pixels=hist[255],
                  alpha_bbox=a.getbbox(),
                  edge_nonzero_pixels={k: sum(v.histogram()[1:]) for k,v in edges.items()},
                  status='qa_failed_not_final', visual_review='See QA_REVIEW_JA.md')
    records.append(record)
    # QA composites are separate artifacts; never rewrite the generated asset.
    panels=[]
    for color in ('white', 'black', '#777777'):
        bg=Image.new('RGBA', im.size, color)
        bg.alpha_composite(im)
        bg.thumbnail((1440,480))
        panels.append(bg.convert('RGB'))
    qa=Image.new('RGB', (1440, 160+sum(p.height for p in panels)), '#cccccc')
    ref=Image.open(source).crop((55,260,685,420)).convert('RGB')
    qa.paste(ref, (10,0))
    ImageDraw.Draw(qa).text((700,25),'TOP: exact source row / BELOW: generated on white, black, gray',fill='black')
    y=160
    for panel in panels:
        qa.paste(panel, (0,y)); y+=panel.height
    qa.save(out/f'016_attempt_{i:02d}_comparison.jpg',quality=95)

(out/'inventory.json').write_text(json.dumps(dict(source_number='016',
    source_file='image-gen-10(2).png',
    source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    generator='built-in image_gen', final_approved=False, assets=records),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records,indent=2))
