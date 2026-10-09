"""v5.8.5 minimal GPU selection and diagnostics correctness tests."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from core.gpu_pipeline import GPUCapabilities, gpu_prefix, selected_gpu_effects
from tools.collect_diagnostics import collect, SRC, DST
from tempfile import TemporaryDirectory
from unittest.mock import patch

# No GPU effects for an NVENC-only machine, no false claim of GPU processing.
c = GPUCapabilities(nvenc=True, gblur_opencl=True, opencl_runtime_ok=False)
assert selected_gpu_effects({'focus_blur':.5},c)==set()
assert gpu_prefix({'focus_blur':.5},c)==('',set())
# Verified OpenCL selects real upstream avgblur_opencl with NV12 frame format.
c = GPUCapabilities(nvenc=True,gblur_opencl=True,opencl_runtime_ok=True)
fg,used=gpu_prefix({'focus_blur':.5},c)
assert used=={'focus_blur'} and 'avgblur_opencl' in fg
assert 'hwdownload,format=nv12' in fg
assert ',gblur_opencl=' not in fg

with TemporaryDirectory() as t:
    root=Path(t); folder=root/'diagnostics'; folder.mkdir()
    (folder/'performance').mkdir()
    (folder/'performance'/'one.json').write_text('{"ok":true}',encoding='utf-8')
    with patch('tools.collect_diagnostics.SRC',folder),patch('tools.collect_diagnostics.DST',root/'out.zip'),patch('tools.collect_diagnostics.ROOT',root):
        assert collect()
    import zipfile
    with zipfile.ZipFile(root/'out.zip') as z:
        assert 'diagnostics/performance/one.json' in z.namelist()
print('V585_DIAGNOSTICS_TEST_PASS')
