from pathlib import Path

from tools.package_camera_work_20261019 import ROOT_BATS, packaged_file


def test_secondary_batch_launchers_remain_runnable_from_organized_folder():
    root = Path(__file__).resolve().parents[1]
    bats = list(root.glob('*.bat'))
    assert len(bats) >= 20
    outputs = {}
    for path in bats:
        packaged_name, data = packaged_file(f'LoL_AutoCine/{path.name}', path.read_bytes())
        assert packaged_name not in outputs
        outputs[packaged_name] = data
        if path.name in ROOT_BATS:
            assert packaged_name == f'LoL_AutoCine/{path.name}'
        else:
            assert packaged_name == f'LoL_AutoCine/Developer_Tools/{path.name}'
            assert b'cd /d "%~dp0..\\"' in data
    assert 'LoL_AutoCine/START.bat' in outputs
    assert 'LoL_AutoCine/COLLECT_DIAGNOSTICS.bat' in outputs
