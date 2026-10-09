from pathlib import Path
import core.jobs as jobs


def test_montage_failure_keeps_outputs(monkeypatch, tmp_path):
    class Dummy:
        pass
    # Avoid real recording: inject a successful clip pipeline and force concat failure.
    monkeypatch.setattr(jobs, 'group_clips', lambda kills, pre, post, merge: [(0.0, 1.0, [kills[0]]), (2.0, 3.0, [kills[1]])])
    monkeypatch.setattr(jobs, 'record_one_clip', lambda *a, **k: jobs.ClipTake(duration=1.0))
    out = tmp_path / 'x.mp4'
    monkeypatch.setattr(jobs, 'apply_effects', lambda raw, final, *a, **k: final.write_bytes(b'ok'))
    monkeypatch.setattr(jobs, 'concat_clips', lambda *a, **k: (_ for _ in ()).throw(RuntimeError('concat fail')))
    class T: pre=1; post=1; merge_multikill=False; hide_hud=False; game_audio=False; style='cinema'
    class P:
        name='A'; champion='Ahri'
        def label(self): return 'A / Ahri'
    class API: pass
    res=jobs.run_auto_edit(API(), Dummy(), P(), [type('K',(),{'time':1.0})(), type('K',(),{'time':2.0})()], T(), tmp_path, True)
    assert len(res.outputs)==2
    assert res.montage is None
    assert any('montage:' in x[1] for x in res.failed)
