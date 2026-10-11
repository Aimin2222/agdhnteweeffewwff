# -*- coding: utf-8 -*-
"""Release builder for v5.10.15. Produces two verified, separate ZIP files."""
from pathlib import Path
import subprocess
import sys
import zipfile

repo = Path(__file__).resolve().parents[2]
app = repo / "LoL_AutoCine"
out = repo / "builds" / "v5.10.15"
out.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(app))
from core.kill_icons import ASSET_STYLES
for code, filename in ASSET_STYLES.items():
    p = app / "assets" / "kill_badges" / filename
    if not p.is_file():
        raise FileNotFoundError(f"{code}: {p}")
assert len(ASSET_STYLES) == 37

full = out / "LoL_AutoCine_v5.10.15_UX_Camera_Windows_Full.zip"
with zipfile.ZipFile(full, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(app.rglob("*")):
        if not p.is_file() or p.suffix in (".pyc", ".pyo"):
            continue
        if any(part in ("__pycache__", ".pytest_cache", "diagnostics") for part in p.parts):
            continue
        z.write(p, p.relative_to(repo))

subprocess.run(["git", "fetch", "--quiet", "origin",
                "autocine/v5.10.14-ui-camera-full"], cwd=repo, check=True)
patch_text = subprocess.check_output(["git", "diff", "--binary",
    "origin/autocine/v5.10.14-ui-camera-full", "HEAD",
    "--", "LoL_AutoCine"], cwd=repo)
if not patch_text:
    raise RuntimeError("No Codex changes found")
patch = out / "v5.10.15_from_v5.10.14.patch"
patch.write_bytes(patch_text)
readme = (
    "LoL AutoCine v5.10.15 Codex統合用差分\\n"
    "基準: autocine/v5.10.14-ui-camera-full\\n"
    "先に git apply --check v5.10.15_from_v5.10.14.patch を実行。\\n"
    "問題なければ git apply ... で適用し、Python/GUIテストを再実行してください。\\n"
    "GPU/音声コアはCodex側の最新変更を優先してください。\\n"
)
codex = out / "LoL_AutoCine_v5.10.15_UX_Camera_Codex_MergeChanges.zip"
with zipfile.ZipFile(codex, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    z.writestr("CODEX_README_JA.txt", readme)
    z.write(patch, patch.name)
    for file, arc in [
        (app / "docs" / "SPEC_v5.10.15_JA.md", "SPEC_v5.10.15_JA.md"),
        (app / "TESTLIST_v5.10.15_JA.md", "TESTLIST_v5.10.15_JA.md"),
    ]:
        z.write(file, arc)

for archive in (full, codex):
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError(f"ZIP corruption: {archive}: {bad}")
    print(f"VERIFIED {archive} ({archive.stat().st_size} bytes)")
