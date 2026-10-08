"""Check parallel branch ownership and merge conflicts without changing the checkout.

Exit 0: no review blockers; exit 1: conflict/ownership/shared API review needed;
exit 2: refs, base ancestry, or Git capability could not be verified.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess


GPU_FILES = {"core/effects.py", "core/gpu_pipeline.py", "core/recorder.py",
             "core/performance_diagnostics.py", "tests/test_v585_filters.py",
             "tests/test_v585_diagnostics.py", "tests/test_v31_regressions.py"}
UI_FILES = {"legacy_app.py", "tests/test_editor_ui_contract.py",
            "tests/test_checked_dispatch.py", "tests/gui_smoke.py",
            "tests/test_scene_studio.py", "tests/test_scene_studio_gui.py"}
SHARED_FILES = {"core/jobs.py", "core/camera.py", "core/audio.py",
                "core/scanner.py", "app.py", "requirements.txt",
                "core/procloop.py", "core/audio_worker.py", "core/capture.py"}
INFRA_FILES = {"tools/check_parallel_integration.py", "tests/test_parallel_integration.py"}


def owner(path: str) -> str:
    if path in GPU_FILES or path.startswith(("core/gpu_", "tests/test_gpu_")):
        return "gpu"
    if path in UI_FILES or path.startswith("ui/"):
        return "ui"
    if path in SHARED_FILES:
        return "shared"
    if path in INFRA_FILES or path.startswith("docs/") or path in {"VERSION.txt", ".gitignore"}:
        return "metadata"
    if path.startswith(("README", "CODEX_")):
        return "metadata"
    return "shared"


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def checked_git(repo: Path, *args: str) -> str:
    result = git(repo, *args)
    if result.returncode:
        raise ValueError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def objects(repo: Path, commit: str) -> dict:
    result = git(repo, "ls-tree", "-r", "-z", commit)
    if result.returncode:
        raise ValueError(result.stderr.strip())
    entries = {}
    for item in result.stdout.split("\0"):
        if item:
            info, path = item.split("\t", 1)
            entries[path] = info
    return entries


def inspect(repo: Path, base: str, gpu: str, ui: str, integration: str | None = None) -> dict:
    # Resolve first so names beginning with '-' cannot be interpreted as options.
    refs = {name: checked_git(repo, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}")
            for name, ref in {"base": base, "gpu": gpu, "ui": ui}.items()}
    if integration:
        refs["integration"] = checked_git(repo, "rev-parse", "--verify", "--end-of-options", integration + "^{commit}")
    changes = {}
    for branch in ("gpu", "ui"):
        ancestor = git(repo, "merge-base", "--is-ancestor", refs["base"], refs[branch])
        if ancestor.returncode:
            raise ValueError(f"共通基準 {base} は {branch} の祖先ではありません")
        result = git(repo, "diff", "--no-renames", "--name-only", "-z", refs["base"], refs[branch])
        if result.returncode:
            raise ValueError(result.stderr.strip())
        changes[branch] = set(result.stdout.rstrip("\0").split("\0")) if result.stdout else set()
    wrong_ui = sorted(p for p in changes["ui"] if owner(p) == "gpu")
    wrong_gpu = sorted(p for p in changes["gpu"] if owner(p) == "ui")
    shared = sorted(p for p in changes["ui"] | changes["gpu"] if owner(p) == "shared")
    overlap = sorted(changes["ui"] & changes["gpu"])
    # merge-tree writes only Git objects, never files/index/branch refs.
    merge = git(repo, "merge-tree", "--write-tree", "--name-only", "--messages", refs["gpu"], refs["ui"])
    if merge.returncode not in (0, 1):
        raise ValueError("Git merge-treeを検証できません: " + merge.stderr.strip())
    mismatches = {"gpu": [], "ui": []}
    if integration:
        integrated = objects(repo, refs["integration"])
        for branch in ("gpu", "ui"):
            expected = objects(repo, refs[branch])
            mismatches[branch] = sorted(path for path in expected.keys() | integrated.keys()
                                        if owner(path) == branch and expected.get(path) != integrated.get(path))
    blockers = bool(wrong_ui or wrong_gpu or shared or overlap or merge.returncode
                    or mismatches["gpu"] or mismatches["ui"])
    return {
        "status": "review_required" if blockers else "ok", "refs": refs,
        "ui_changed": sorted(changes["ui"]), "gpu_changed": sorted(changes["gpu"]),
        "ui_changed_gpu_files": wrong_ui, "gpu_changed_ui_files": wrong_gpu,
        "shared_files_requiring_review": shared, "both_changed_files": overlap,
        "merge_conflicts": merge.returncode == 1,
        "merge_details": merge.stdout.strip() if merge.returncode else "",
        "integration_gpu_mismatches": mismatches["gpu"],
        "integration_ui_mismatches": mismatches["ui"],
        "scope": "committed branch tips only; inspect git status for uncommitted work",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--base", default="stable/v5.8.5")
    parser.add_argument("--gpu", default="feature/gpu-engine")
    parser.add_argument("--ui", default="feature/ui-editor-v586")
    parser.add_argument("--integration", help="After merging, verify committed owned files match their source branches")
    args = parser.parse_args()
    try:
        report = inspect(args.repo, args.base, args.gpu, args.ui, args.integration)
    except ValueError as exc:
        print(json.dumps({"status": "unverified", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
