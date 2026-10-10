from core.effects import Template, one_click_templates, FOG_PRESETS
from core.camera import STYLES, CameraPlan

def test_preserved_effect_fields():
    t=Template()
    for k in ("exposure","vibrance","cam_height","dist_scale","bloom","vignette","grain","bars","temperature","contrast","fog_enabled","fog_preset","curve_enabled","curve_points","dof_enabled","dof_blur","dof_focus_distance","capture_fps","fps"):
        assert hasattr(t,k), k

def test_preserved_templates():
    ts=one_click_templates()
    for name in ("ジャネット風シネマ","自然め追従 (三人称)","クリーン (色補正なし)","ノワール強め","ダークグレー","ティール・ドリーム","ネオン・モンタージュ","夕焼けシネマ","ヴィンテージ・フィルム"):
        assert name in ts, name

def test_camera_controls_all_modes():
    for k in ("follow","fps","cinema","orbit","top","cinema_top"):
        assert k in STYLES
    p=CameraPlan(style="cinema",height=250,dist_scale=0.6,kill_times=(10.0,13.0))
    assert p.height==250 and p.dist_scale==0.6
    assert p._cue(13.0)>0.9

def test_output_fps_split():
    t=Template()
    assert t.capture_fps==144 and t.fps==60

def test_fog_presets():
    assert set(FOG_PRESETS) == {"teal","sand","white","emerald","cream"}
