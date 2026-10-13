"""Source provenance and alpha gates, never mistaken for visual acceptance."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image
import pytest

APP=Path(__file__).resolve().parents[1];ROOT=APP/'assets/kill_frames'
MANIFEST=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))

@pytest.mark.parametrize('entry',MANIFEST['assets'],ids=lambda a:a['theme']+'/'+a['file'].split('/')[-1])
def test_each_png_is_exact_source_rgb_with_nontrivial_alpha_and_clear_portrait_holes(entry):
    source=APP/'assets/kill_concepts'/entry['source_file'];out=ROOT/entry['file'];mask=ROOT/entry['mask_file']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==entry['source_sha256']
    assert hashlib.sha256(out.read_bytes()).hexdigest()==entry['sha256']
    assert hashlib.sha256(mask.read_bytes()).hexdigest()==entry['mask_sha256']
    im=Image.open(out);assert im.mode=='RGBA'
    expected=np.asarray(Image.open(source).convert('RGB').crop(entry['crop_box']))
    pixels=np.asarray(im);assert np.array_equal(pixels[:,:,:3],expected)  # no repainting, color transfer or resampling
    a=pixels[:,:,3];assert np.any(a==0) and np.any(a==255) and np.any((a>0)&(a<255))
    assert np.array_equal(np.asarray(Image.open(mask)),a)
    for hole in entry['portrait_holes']:
        coords=next(iter(hole.values()));x=int((coords[0]+coords[2])/2)-entry['crop_box'][0];y=int((coords[1]+coords[3])/2)-entry['crop_box'][1]
        # Check a 20x20 central face patch, not only a single transparent pixel.
        assert np.max(a[y-10:y+10,x-10:x+10])==0
    assert entry['status']=='needs_manual_mask'  # numeric validation never grants artwork acceptance


def test_only_three_requested_themes_and_five_assets_each():
    assert MANIFEST['generated_or_inpainted'] is False
    assert MANIFEST['status']=='prototype_not_approved'
    assert {a['theme'] for a in MANIFEST['assets']}=={'winter_festival','project','elderwood'}
    for theme in ('winter_festival','project','elderwood'):
        assert {Path(a['file']).stem for a in MANIFEST['assets'] if a['theme']==theme}=={'frame_weak','frame_strong','center_melee','center_ranged','center_hybrid'}
        qa=Image.open(ROOT/'qa'/f'{theme}_comparison.png');assert qa.size==(2080,1100)
        # Different backgrounds must produce distinct composited pixels.
        strips=[np.asarray(qa.crop((i*520,50,(i+1)*520,240))) for i in range(4)]
        assert not np.array_equal(strips[0],strips[1]) and not np.array_equal(strips[1],strips[2]) and not np.array_equal(strips[2],strips[3])
