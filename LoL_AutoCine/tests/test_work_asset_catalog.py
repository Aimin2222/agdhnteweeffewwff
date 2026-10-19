"""Offline integrity/QA-boundary tests for immutable imported Work assets."""
import hashlib
import json
import math
from pathlib import Path
from PIL import Image
import pytest

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/'assets/work_kill_assets/catalog.json'

@pytest.fixture(scope='module')
def catalog():
    return json.loads(CATALOG.read_text(encoding='utf-8'))

def test_source_counts_and_quality_gate(catalog):
    assert catalog['source_commit']=='30fdce48dd83a2f73083cf99b569f6fdb71ffffc'
    assert len(catalog['frames'])==len({a['id'] for a in catalog['frames']})==652
    assert [a['id'] for a in catalog['frames'] if a['status']=='approved']==['083/a_simple_main']
    assert len(catalog['effects'])==35
    assert all(a['status']=='review' and not a['final_approved'] for a in catalog['effects'])
    assert len(catalog['legacy_layers'])==311
    assert len(catalog['motions'])==6
    assert sum(a['edge_nonzero']>0 for a in catalog['effects'])==3
    assert sum(not a['native_2k'] for a in catalog['effects'])==31

def test_all_files_byte_identical_to_recorded_sources(catalog):
    for row in catalog['frames']+catalog['effects']+catalog['legacy_layers']:
        path=(ROOT/row['path']).resolve()
        assert path.is_relative_to((ROOT/'assets/work_kill_assets').resolve())
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256'],row['id'] if 'id' in row else row['path']
        with Image.open(path) as image:
            assert image.mode=='RGBA'
            if 'width' in row:
                assert image.size==(row['width'],row['height'])

def test_approved_portrait_geometry_is_transparent(catalog):
    approved=next(a for a in catalog['frames'] if a['status']=='approved')
    assert approved['portrait_shape']=='circle'
    assert approved['sha256']=='b1b360c15d860e1fdd12ff01af67f5c1b9693538fa6d2b5babb9c0aa3602440f'
    with Image.open(ROOT/approved['path']) as image:
        alpha=image.getchannel('A')
        for cx,cy,radius in approved['portrait_circles']:
            # Exclude the SVG antialias fringe, using the source QA strict radius.
            strict=56.45*6
            assert radius==340.8
            for y in range(math.ceil(cy-strict),math.floor(cy+strict)+1):
                dx=math.sqrt(max(0,strict**2-(y-cy)**2))
                for x in range(math.ceil(cx-dx),math.floor(cx+dx)+1):
                    assert alpha.getpixel((x,y))==0

def test_unreviewed_holes_never_invent_geometry(catalog):
    assert all(a['portrait_boxes'] is None for a in catalog['frames'] if a['status']=='review')
    for effect in catalog['effects']:
        assert effect['placement']['aspect']=='preserve, do not stretch'
        assert effect['placement']['width_relative_to_frame']>0
