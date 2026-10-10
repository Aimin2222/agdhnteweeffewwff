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
             'tools/gpu_render_test.py','START_CPU_EFFECTS_COMPARE.bat','START_GPU_HYBRID.bat','TEST_GPU_RENDER.bat',
             "tools/setup_gpu_ffmpeg.py", "START_GPU.bat",
             "core/focus_fx.py", "core/preview.py",
             "core/montage_fx.py",
             "core/highlight_pulse.py",
             "core/kill_icons.py", "tests/test_v5991_portrait_pairs.py",
             "core/performance_diagnostics.py", "tests/test_v585_filters.py",
             "tests/test_v585_diagnostics.py", "tests/test_v31_regressions.py"}
UI_FILES = {"tests/test_v5106_hover_help.py", "tests/test_v5105_preview_responsiveness.py", "tests/test_v5105_killfeed_glow_side_help.py", "tests/test_v5104_notebook_livefx_camera.py", "legacy_app.py", "tests/test_editor_ui_contract.py",
            "tests/test_checked_dispatch.py", "tests/gui_smoke.py",
            "tests/test_scene_studio.py", "tests/test_scene_studio_gui.py",
            "tests/test_scene_sequence.py", "tests/test_scene_keyframes_v592.py",
            "tests/test_v593_mode_camera.py", "tests/test_v594_live_preview.py",
            "tests/test_v595_workspace.py", "tests/test_v596_hud_batch.py",
            "tests/test_v597_studio.py", "tests/test_v598_highlight_director.py",
            "tests/test_v599_automontage_killbadges.py", "tests/test_v510_ui_gpu_killframe.py",
            "tests/test_v5101_scroll_check_warmup.py", "tests/test_v5102_circle_focus_preset.py",
            "tests/test_v5103_nonblocking_dispatch.py"}
SHARED_FILES = {"core/jobs.py", "core/camera.py", "core/camera_clock.py", "core/audio.py",
                "core/scanner.py", "app.py", "requirements.txt",
                "core/procloop.py", "core/audio_worker.py", "core/capture.py",
                "core/capture_process.py", "core/capture_worker.py"}
INFRA_FILES = {
    'tests/test_parallel_integration.py',
    'tools/check_parallel_integration.py',
    'tools/package_v5100.py',
    'tools/package_v5101.py',
    'tools/package_v5103.py',
    'tools/package_v5103_capture60.py',
    'tools/package_v5103_capturefix.py',
    'tools/package_v5103_exportopt.py',
    'tools/package_v5103_gpu.py',
    'tools/package_v5103_hangfix.py',
    'tools/package_v5103_mirrorfix.py',
    'tools/package_v5104.py',
    'tools/package_v5105.py',
    'tools/package_v5106.py',
    'tools/package_v599.py',
}


def owner(path: str) -> str:
    if path in GPU_FILES or path.startswith(("core/gpu_", "tests/test_gpu_")):
        return "gpu"
    if path in UI_FILES or path.startswith("ui/"):
        return "ui"
    if path in SHARED_FILES:
        return "shared"
    if path in INFRA_FILES or path.startswith("docs/") or path in {"VERSION.txt", ".gitignore"}:
        return "metadata"
    if path == "assets/champion_icons/README_JA.txt":
        return "metadata"
    if path.startswith(("README", "CODEX_", "START_HERE", "patches/history/")) or path in {"ui_changes_v5.9.1.patch", "patches/v594_to_v595.patch"}:
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


def inspect(repo: Path, base: str, gpu: str, ui: str, integration: str | None = None,
            shared_review: dict | None = None) -> dict:
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
    reviewed = {}
    if shared_review is not None:
        if (not isinstance(shared_review, dict) or shared_review.get("schema_version") != 1
                or shared_review.get("base") != refs["base"]
                or not isinstance(shared_review.get("files"), dict)):
            raise ValueError("共有APIレビューの形式または基準コミットが不一致です")
        branch_objects = {branch: objects(repo, refs[branch]) for branch in ("gpu", "ui")}
        for path, approval in shared_review["files"].items():
            if (owner(path) != "shared" or not isinstance(approval, dict)
                    or approval.get("branch") not in ("gpu", "ui")
                    or not isinstance(approval.get("object"), str)):
                raise ValueError("共有APIレビューのファイル指定が不正です")
            branch = approval["branch"]
            other = "ui" if branch == "gpu" else "gpu"
            # A review applies only to this exact file object on its designated branch.
            # Later edits, deletions, and changes on the other branch still require review.
            if (path in changes[branch] and path not in changes[other]
                    and branch_objects[branch].get(path) == approval["object"]):
                reviewed[path] = approval["object"]
        shared = [path for path in shared if path not in reviewed]
    overlap = sorted(changes["ui"] & changes["gpu"])
    # merge-tree writes only Git objects, never files/index/branch refs.
    merge = git(repo, "merge-tree", "--write-tree", "--name-only", "--messages", refs["gpu"], refs["ui"])
    if merge.returncode not in (0, 1):
        raise ValueError("Git merge-treeを検証できません: " + merge.stderr.strip())
    mismatches = {"gpu": [], "ui": []}
    shared_mismatches = []
    if integration:
        integrated = objects(repo, refs["integration"])
        for branch in ("gpu", "ui"):
            expected = objects(repo, refs[branch])
            mismatches[branch] = sorted(path for path in expected.keys() | integrated.keys()
                                        if owner(path) == branch and expected.get(path) != integrated.get(path))
        shared_mismatches = sorted(path for path, expected in reviewed.items()
                                   if integrated.get(path) != expected)
    blockers = bool(wrong_ui or wrong_gpu or shared or overlap or merge.returncode
                    or mismatches["gpu"] or mismatches["ui"] or shared_mismatches)
    return {
        "status": "review_required" if blockers else "ok", "refs": refs,
        "ui_changed": sorted(changes["ui"]), "gpu_changed": sorted(changes["gpu"]),
        "ui_changed_gpu_files": wrong_ui, "gpu_changed_ui_files": wrong_gpu,
        "shared_files_requiring_review": shared, "both_changed_files": overlap,
        "shared_files_reviewed": sorted(reviewed),
        "merge_conflicts": merge.returncode == 1,
        "merge_details": merge.stdout.strip() if merge.returncode else "",
        "integration_gpu_mismatches": mismatches["gpu"],
        "integration_ui_mismatches": mismatches["ui"],
        "integration_shared_mismatches": shared_mismatches,
        "scope": "committed branch tips only; inspect git status for uncommitted work",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--base", default="stable/v5.8.5")
    parser.add_argument("--gpu", default="feature/gpu-engine")
    parser.add_argument("--ui", default="feature/ui-editor-v586")
    parser.add_argument("--integration", help="After merging, verify committed owned files match their source branches")
    parser.add_argument("--shared-review", type=Path,
                        help="Explicit JSON review of exact shared file objects; other changes remain blocked")
    args = parser.parse_args()
    try:
        review = None
        if args.shared_review:
            path = args.shared_review if args.shared_review.is_absolute() else args.repo / args.shared_review
            review = json.loads(path.read_text(encoding="utf-8"))
        report = inspect(args.repo, args.base, args.gpu, args.ui, args.integration, review)
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "unverified", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
