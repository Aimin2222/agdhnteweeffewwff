"""Render actual pixels and exercise the FFmpeg compositing clock offline."""
import hashlib
import json
import subprocess
from types import SimpleNamespace
import pytest
from PIL import Image
from core import work_kill_assets as work
from core.effects import Template, FFMPEG
from core.kill_icons import MOTION_STYLES


@pytest.fixture
def pack(tmp_path, monkeypatch):
    folder = tmp_path/'assets/work_kill_assets'
    folder.mkdir(parents=True)
    frame = Image.new('RGBA', (252,105))
    from PIL import ImageDraw
    d = ImageDraw.Draw(frame)
    for x in (52,199): d.ellipse((x-36,16,x+36,88),outline='gold',width=3)
    d.rectangle((121,30,131,75), fill='gold')
    frame.save(folder/'frame.png')
    Image.new('RGBA', (100,50), (255,0,255,160)).save(folder/'peak.png')
    def record(name, identifier, state):
        p = folder/name
        im = Image.open(p)
        return dict(id=identifier,label=identifier,status=state,path=str(p.relative_to(tmp_path)),
                    sha256=hashlib.sha256(p.read_bytes()).hexdigest(), width=im.width,height=im.height)
    item = record('frame.png','083/a_simple_main','approved')
    item['portrait_boxes'] = [[19,19,66,66],[166,19,66,66]]
    pending = dict(item, id='review')
    pending['status']='review'
    effect = record('peak.png','A','review')
    effect['duration']=.35
    (folder/'catalog.json').write_text(json.dumps(dict(frames=[item,pending],effects=[effect])))
    monkeypatch.setattr(work,'ROOT',tmp_path)
    monkeypatch.setattr(work,'CATALOG',folder/'catalog.json')
    red,blue = tmp_path/'red.png',tmp_path/'blue.png'
    Image.new('RGBA',(64,64),'red').save(red)
    Image.new('RGBA',(64,64),'blue').save(blue)
    return tmp_path,red,blue


def test_quality_gate_integrity_and_native_layers(pack):
    folder,a,b=pack
    assert len(work.list_assets()) == 1
    with pytest.raises(ValueError): work.resolve_asset('review')
    with pytest.raises(ValueError): work.resolve_asset('A','effects')
    image=work.render_pair('083/a_simple_main',a,b)
    assert image.size==(252,105)
    assert image.getpixel((52,52))==(255,0,0,255)
    assert image.getpixel((199,52))==(0,0,255,255)
    assert image.getpixel((125,52))==(255,215,0,255)
    assert image.getpixel((19,19))[3]==0  # circular portrait, no square corner leak
    (folder/'assets/work_kill_assets/frame.png').write_bytes(b'altered')
    with pytest.raises(ValueError,match='SHA256'): work.resolve_asset('083/a_simple_main')


def test_event_plan_multikill_and_peak_masks(pack):
    folder,a,b=pack
    t=Template(work_kill_frame_id='083/a_simple_main',work_kill_effect_id='A',work_kill_review=True)
    kills=[SimpleNamespace(killer='A',victim='B')]*4
    entries=work.make_event_work_badges(folder/'out.mp4',t,kills,[(1,.42),(1.1,.42),(1.2,.42),(1.3,.42)],
            [dict(name='A',raw_champion='Annie'),dict(name='B',raw_champion='Ahri')],icon_lookup=lambda p:a if p['name']=='A' else b)
    assert len(entries)==12
    plan=work.layer_plan(entries,3,1.55)
    assert all(0<=x['row']<3 for x in plan)
    assert min(x['start'] for x in plan)==pytest.approx(1)
    peak=Image.open(entries[1][0])
    assert peak.getpixel((52,52))[3]==0
    assert work.peak_opacity(-.01)==0
    assert [work.peak_opacity(x,.35) for x in (0,.04,.08,.2,.35)]==pytest.approx([0,.8,1,.65,0])
    assert work.strength('weak')==.45


@pytest.mark.parametrize('motion',list(MOTION_STYLES))
def test_preview_clock_and_six_entrances(pack,motion):
    _,a,b=pack
    t=Template(work_kill_frame_id='083/a_simple_main',kill_icon_motion=motion)
    assert work.render_preview_pair(t,a,b,-.01).getbbox() is None
    assert work.render_preview_pair(t,a,b,2).getbbox() is None
    visible=work.render_preview_pair(t,a,b,.35)
    assert visible.getbbox() is not None
    # Every entrance settles at exactly the unchanged layout.
    t.kill_icon_motion='instant'
    reference=work.render_preview_pair(t,a,b,1)
    t.kill_icon_motion=motion
    settled=work.render_preview_pair(t,a,b,1)
    assert settled.getbbox()==reference.getbbox()


def test_ffmpeg_peak_composition_runs_and_does_not_shorten_output(pack):
    folder,a,b=pack
    t=Template(work_kill_frame_id='083/a_simple_main',work_kill_effect_id='A',work_kill_review=True)
    entries=work.make_event_work_badges(folder/'out.mp4',t,[SimpleNamespace(killer='A',victim='B')],[(.1,.42)],
            [dict(name='A',raw_champion='Annie'),dict(name='B',raw_champion='Ahri')],icon_lookup=lambda p:a)
    graph=work.with_work_badges('[0:v]null[vout]',1,entries,duration=.5,scale=.3)
    command=[FFMPEG,'-hide_banner','-loglevel','error','-f','lavfi','-i','color=black:s=320x180:r=60:d=0.5']
    for path,_ in entries: command += ['-loop','1','-framerate','60','-t','0.5','-i',str(path)]
    command+=['-filter_complex',graph,'-map','[vout]','-t','0.5','-pix_fmt','rgba','-f','rawvideo','pipe:1']
    result=subprocess.run(command,capture_output=True,timeout=45)
    assert result.returncode==0,result.stderr.decode(errors='replace')
    assert len(result.stdout)==320*180*4*30


def test_gpu_work_graph_uses_same_order_clock_and_shader_opacity(pack):
    from core.gpu_full import GPUFullStage
    folder,a,b=pack
    t=Template(work_kill_frame_id='083/a_simple_main',work_kill_effect_id='A',work_kill_review=True,
               work_kill_strength='weak',kill_icon_motion='slide_right')
    entries=work.make_event_work_badges(folder/'out.mp4',t,[SimpleNamespace(killer='A',victim='B')],[(.1,.42)],
            [dict(name='A',raw_champion='Annie'),dict(name='B',raw_champion='Ahri')],icon_lookup=lambda p:a)
    assert [x['kind'] for x in work.layer_plan(entries,1,1.55)]==['frame','peak','frame']
    stage=GPUFullStage(t,1,[],ffmpeg=FFMPEG,badges=entries,badge_index=1,lut_index=4)
    try:
        shader=stage.path.read_text()
        assert 'work_kill_assets' in stage.effects
        assert '0.450000' in shader
        assert 'time>=0.100000000f' in shader
        assert shader.count('kernel void badge_')==3
        assert 'geq=' not in stage.graph and stage.graph.count('hwdownload')==1
    finally: stage.close()


def test_template_roundtrip_preserves_explicit_review_and_camera_fields():
    original=Template(work_kill_frame_id='083/a_simple_main', work_kill_effect_id='D_project',
                      work_kill_review=True,work_kill_strength='weak',camera_control_mode='fixed_auto',
                      camera_auto_excluded=['fps'],camera_auto_qa_approved={'red':['third_person']})
    restored=Template(**json.loads(json.dumps(original.to_dict())))
    assert restored.to_dict()==original.to_dict()


def test_mirror_dimensions_scale_the_whole_1080p_layout(pack):
    _,a,b=pack
    t=Template(work_kill_frame_id='083/a_simple_main')
    full=work.render_preview_pair(t,a,b,.4)
    half=work.render_preview_pair(t,a,b,.4,size=(960,540))
    expected=full.resize((960,540),Image.Resampling.LANCZOS)
    assert half.tobytes()==expected.tobytes()


def test_actual_approved_native_asset_stays_immutable(pack):
    # Fixture restores local ROOT, so read the repository catalog explicitly.
    from pathlib import Path
    root=Path(work.__file__).resolve().parents[1]
    data=json.loads((root/'assets/work_kill_assets/catalog.json').read_text(encoding='utf-8'))
    approved=[x for x in data['frames'] if x['status']=='approved']
    assert [x['id'] for x in approved]==['083/a_simple_main']
    item=approved[0]
    path=root/item['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']
    with Image.open(path) as image:
        assert image.mode=='RGBA' and image.size==(2520,1050)
        for cx,cy,r in item['portrait_circles']:
            assert image.getpixel((round(cx),round(cy)))[3]==0
