from pathlib import Path
import subprocess, tempfile, sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.effects import Template, apply_effects, FFMPEG
from core.camera import TRY_TPS

def test_effect_audio_compatibility_and_filters():
    with tempfile.TemporaryDirectory() as d:
        d=Path(d); src=d/'src.mp4'; out=d/'out.mp4'
        subprocess.run([FFMPEG,'-y','-loglevel','error','-f','lavfi','-i','testsrc2=size=320x180:rate=30:duration=1', '-f','lavfi','-i','sine=frequency=440:duration=1', '-shortest', '-pix_fmt','yuv420p', str(src)],check=True)
        wav=d/'game.wav'
        subprocess.run([FFMPEG,'-y','-loglevel','error','-f','lavfi','-i','sine=frequency=220:duration=1', str(wav)],check=True)
        t=Template(game_audio=True, fog_enabled=True, fog_strength=.4, curve_enabled=True, dof_enabled=True, dof_blur=2)
        apply_effects(src,out,t,1.0,[],game_audio=wav,audio_offset=.0)
        assert out.exists() and out.stat().st_size > 1000

def test_safe_tps_default():
    assert TRY_TPS is False
