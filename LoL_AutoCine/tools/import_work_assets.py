"""Import immutable Work deliverables from one pinned commit, never edit originals.

Run explicitly offline from a verified cache or use --download. No runtime/UI fetch.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path, PurePosixPath
import urllib.parse
import urllib.request
from PIL import Image

COMMIT = '30fdce48dd83a2f73083cf99b569f6fdb71ffffc'
OLD_COMMIT = '88872ce9b37bf8c2c1ffc1a2b515ea4a3425aa7c'
PREFIX = 'LoL_AutoCine/assets/kill_frames_chatgpt/'
BASE = 'https://raw.githubusercontent.com/Aimin2222/agdhnteweeffewwff/'
METADATA_SHA256={
    'full_production_v5/production.json':'b3b8d9c14c9690efa3b8ba24bb6b7ab0f8d61212698b960f7580c23d36c1ef1d',
    'production_push_20261019/FINAL_IMAGE_INDEX.json':'c69e29ddf6d85e495711d7d9684692419b5198c102d67c6076dc98e3001695a1',
    'completion_attempt_20261019/LATEST_PEAK_SET.json':'8f70dc0e3adcd43c6a953e0c8ca6da883d3d65934fe3bf765a86c16dc2eb2d2f',
    'production_push_20261019/SIX_MOTION_RECOVERED.json':'07d6beefd124909f7688d8b26305dea63003cb2b9081df2a4881f7db08a049cd',
    'effect_specs/review_v1/animation_catalog.json':'52c88df5f232dd7b22a4260e9d5b34febaf5ef7863dd846b3cc79ee32cc6f50e',
}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def safe_relative(path):
    p = PurePosixPath(path)
    if p.is_absolute() or '..' in p.parts or not str(p).startswith(PREFIX):
        raise ValueError('Unsafe Work source path')
    return str(p)

def import_assets(cache, output, download=False):
    cache, output = Path(cache).resolve(), Path(output).resolve()
    if __import__('os').name == 'nt':
        cache, output = Path('\\\\?\\'+str(cache)), Path('\\\\?\\'+str(output))
    output.mkdir(parents=True, exist_ok=True)
    def source(path, expected=None, commit=COMMIT):
        path = safe_relative(path)
        local = cache / path
        if local.exists():
            data = local.read_bytes()
        elif download:
            data = urllib.request.urlopen(BASE + commit + '/' + urllib.parse.quote(path), timeout=60).read()
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_bytes(data)
        else:
            raise FileNotFoundError(local)
        if expected and digest(data) != expected:
            raise ValueError('SHA256 mismatch: ' + path)
        return data
    def metadata(name):
        data = source(PREFIX + name, METADATA_SHA256.get(name))
        dest = output / 'provenance' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return json.loads(data)
    production = metadata('full_production_v5/production.json')
    final = metadata('production_push_20261019/FINAL_IMAGE_INDEX.json')
    peaks = metadata('completion_attempt_20261019/LATEST_PEAK_SET.json')
    motions = metadata('production_push_20261019/SIX_MOTION_RECOVERED.json')
    layers = metadata('effect_specs/review_v1/animation_catalog.json')
    approved = {a['key']:a for a in final['entries'] if a['final_approved']}
    def copy_image(path, sha, target, commit=COMMIT):
        data = source(path, sha, commit)
        dest = output / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.read_bytes() != data:
            raise ValueError('Refusing overwrite: '+str(dest))
        if not dest.exists():
            dest.write_bytes(data)
        with Image.open(dest) as im:
            if im.mode != 'RGBA':
                raise ValueError('Not RGBA: '+path)
            width, height = im.size
        return dict(path='assets/work_kill_assets/'+target,sha256=digest(data),width=width,height=height,mode='RGBA',source_path=path,source_commit=commit)
    def frame(a):
        key=a['key']; ap=approved.get(key)
        path, sha = (ap['image'],ap['sha256']) if ap else (a['output'],a['sha256'])
        row=copy_image(path,sha,'frames/'+key+'/frame.png',COMMIT if ap else OLD_COMMIT)
        row.update(id=key,key=key,label='No.'+a['number']+' '+a['id'],number=a['number'],theme=a['theme'],intensity=a['intensity'],status='approved' if ap else 'review',final_approved=bool(ap),portrait_boxes=None,quality_scope='static image only' if ap else 'unapproved review candidate',qa_flags=a.get('quality_flags',[]))
        if ap:
            row['portrait_shape']='circle'
            row['portrait_boxes']=[[187.2,184.2,681.6,681.6],[1657.2,184.2,681.6,681.6]]
            row['portrait_circles']=[[528,525,340.8],[1998,525,340.8]]
            row['portrait_layout_source']='frame.svg evenodd inner ring radius56.8 in viewBox420x175; scale6'
            for field in ('svg','quality_review'):
                data=source(ap[field]); dest=output/'provenance'/Path(ap[field]).name; dest.write_bytes(data)
        return row
    for a in production['assets']:
        (output/'frames'/a['key']).mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        frames=list(pool.map(frame,production['assets']))
    layer_specs={x['id']:x for x in layers['specs']}
    def peak(a):
        ident=a['id']; spec=metadata('effect_specs/frame_based_review_v2/'+ident+'.json')
        row=copy_image(a['repository_path'],a['sha256'],'effects/'+ident+'/impact_rgba.png')
        row.update(id=ident,label=layer_specs[ident]['label'],status='review',final_approved=False,variant='both',duration=.35 if ident=='A' else .65 if ident=='C' else .8,spec=spec,placement=spec['placement'],layers=layer_specs[ident]['layers'],edge_nonzero=a['edge_nonzero'],native_2k=a['native_2k'],motion_for_this_peak_sha=a['motion_for_this_peak_sha'])
        return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        effects=list(pool.map(peak,peaks['assets']))
    # Older layer files are source fragments/ornaments/glows, not 311 new particles.
    layer_paths=set()
    for s in layer_specs.values():
        ls=s['layers']; layer_paths.update([ls['ornament'],ls['glow']]); layer_paths.update(p['file'] for p in ls.get('particles',[]))
    def layer(path):
        data=source(path); rel='legacy_layers/'+path.split('/effect_assets/review_v1/',1)[1]
        dest=output/rel; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(data)
        return dict(source_path=path,path='assets/work_kill_assets/'+rel,sha256=digest(data),source_commit=COMMIT,status='review')
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        legacy=list(pool.map(layer,sorted(layer_paths)))
    catalog=dict(schema_version=1,source_commit=COMMIT,source_branch='chatgpt/killframes-source-numbering-20261014',frames=frames,effects=effects,motions=motions['modes'],motion_definition=motions,legacy_layers=legacy,counts=dict(frames=len(frames),static_approved=sum(x['status']=='approved' for x in frames),effects=len(effects),effects_approved=0,legacy_layers=len(legacy),edge_warnings=peaks['edge_warning'],below_native_2k=peaks['below_native_2k']))
    if len(frames)!=652 or len({x['id'] for x in frames})!=652 or catalog['counts']['static_approved']!=1:
        raise ValueError('Unexpected counts; not publishing catalog')
    (output/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
    return catalog['counts']

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache',required=True)
    parser.add_argument('--output',default=str(Path(__file__).resolve().parents[1]/'assets/work_kill_assets'))
    parser.add_argument('--download',action='store_true')
    args=parser.parse_args()
    print(json.dumps(import_assets(args.cache,args.output,args.download)))
