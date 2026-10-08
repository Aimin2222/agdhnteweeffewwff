"""Exercise the branch guard with actual divergent temporary Git histories."""
from pathlib import Path
import subprocess

import pytest

from tools.check_parallel_integration import inspect, objects


def command(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def commit_file(root, name, contents):
    file = root / name
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(contents, encoding="utf-8")
    command(root, "add", name)
    command(root, "commit", "-m", "test change")


def history(root, gpu_file, ui_file):
    command(root, "init", "-b", "stable")
    command(root, "config", "user.name", "Integration Test")
    command(root, "config", "user.email", "test@localhost")
    for name in {gpu_file, ui_file}:
        file = root / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("base\n", encoding="utf-8")
    command(root, "add", ".")
    command(root, "commit", "-m", "test baseline")
    command(root, "switch", "-c", "gpu")
    commit_file(root, gpu_file, "GPU branch\n")
    command(root, "switch", "-c", "ui", "stable")
    commit_file(root, ui_file, "UI branch\n")


@pytest.mark.parametrize("ui_file", [
    "legacy_app.py", "tests/test_scene_studio.py", "tests/test_scene_studio_gui.py",
    "tests/test_scene_sequence.py", "tests/test_scene_keyframes_v592.py",
])
def test_independent_changes_preserve_checkout(tmp_path, ui_file):
    history(tmp_path, "core/effects.py", ui_file)
    before = command(tmp_path, "rev-parse", "HEAD")
    contents = (tmp_path / ui_file).read_bytes()
    report = inspect(tmp_path, "stable", "gpu", "ui")
    assert report["status"] == "ok"
    assert command(tmp_path, "rev-parse", "HEAD") == before
    assert (tmp_path / ui_file).read_bytes() == contents
    assert command(tmp_path, "status", "--porcelain") == ""


@pytest.mark.parametrize("gpu_file,ui_file,key", [
    ("docs/gpu.md", "core/effects.py", "ui_changed_gpu_files"),
    ("legacy_app.py", "docs/ui.md", "gpu_changed_ui_files"),
    ("tests/test_scene_studio.py", "docs/ui.md", "gpu_changed_ui_files"),
    ("tests/test_scene_studio_gui.py", "docs/ui.md", "gpu_changed_ui_files"),
    ("tests/test_scene_sequence.py", "docs/ui.md", "gpu_changed_ui_files"),
    ("tests/test_scene_keyframes_v592.py", "docs/ui.md", "gpu_changed_ui_files"),
    ("core/effects.py", "core/jobs.py", "shared_files_requiring_review"),
])
def test_ownership_and_shared_api_are_blocked(tmp_path, gpu_file, ui_file, key):
    history(tmp_path, gpu_file, ui_file)
    report = inspect(tmp_path, "stable", "gpu", "ui")
    assert report["status"] == "review_required"
    assert report[key]


def test_same_file_conflict_is_detected(tmp_path):
    history(tmp_path, "docs/shared.md", "docs/shared.md")
    report = inspect(tmp_path, "stable", "gpu", "ui")
    assert report["both_changed_files"] == ["docs/shared.md"]
    assert report["merge_conflicts"] is True
    assert command(tmp_path, "status", "--porcelain") == ""


def test_unrelated_baseline_is_not_reported_safe(tmp_path):
    history(tmp_path, "core/effects.py", "legacy_app.py")
    command(tmp_path, "switch", "--orphan", "unrelated")
    commit_file(tmp_path, "README.md", "unrelated\n")
    with pytest.raises(ValueError, match="祖先"):
        inspect(tmp_path, "unrelated", "gpu", "ui")


def test_post_merge_gpu_rollback_is_detected(tmp_path):
    history(tmp_path, "core/effects.py", "legacy_app.py")
    command(tmp_path, "switch", "-c", "integration", "gpu")
    command(tmp_path, "merge", "--no-ff", "ui", "-m", "test merge")
    assert inspect(tmp_path, "stable", "gpu", "ui", "integration")["status"] == "ok"
    commit_file(tmp_path, "core/effects.py", "base\n")
    report = inspect(tmp_path, "stable", "gpu", "ui", "integration")
    assert report["status"] == "review_required"
    assert report["integration_gpu_mismatches"] == ["core/effects.py"]


def shared_review(root):
    return {"schema_version": 1, "base": command(root, "rev-parse", "stable"),
            "files": {"core/jobs.py": {"branch": "gpu", "object": objects(root, "gpu")["core/jobs.py"]}}}


def test_shared_review_is_explicit_and_applies_to_exact_object(tmp_path):
    history(tmp_path, "core/jobs.py", "legacy_app.py")
    assert inspect(tmp_path, "stable", "gpu", "ui")["shared_files_requiring_review"] == ["core/jobs.py"]
    review = shared_review(tmp_path)
    report = inspect(tmp_path, "stable", "gpu", "ui", shared_review=review)
    assert report["status"] == "ok" and report["shared_files_reviewed"] == ["core/jobs.py"]
    command(tmp_path, "switch", "gpu")
    commit_file(tmp_path, "core/jobs.py", "later unreviewed change\n")
    report = inspect(tmp_path, "stable", "gpu", "ui", shared_review=review)
    assert report["status"] == "review_required"
    assert report["shared_files_requiring_review"] == ["core/jobs.py"]


def test_shared_review_does_not_cover_other_branch_or_new_shared_file(tmp_path):
    history(tmp_path, "core/jobs.py", "legacy_app.py")
    review = shared_review(tmp_path)
    commit_file(tmp_path, "core/jobs.py", "UI also changed this shared API\n")
    commit_file(tmp_path, "core/audio.py", "unreviewed shared audio API\n")
    report = inspect(tmp_path, "stable", "gpu", "ui", shared_review=review)
    assert report["status"] == "review_required"
    assert report["shared_files_requiring_review"] == ["core/audio.py", "core/jobs.py"]
    assert report["shared_files_reviewed"] == []


def test_reviewed_shared_file_rollback_after_merge_is_detected(tmp_path):
    history(tmp_path, "core/jobs.py", "legacy_app.py")
    review = shared_review(tmp_path)
    command(tmp_path, "switch", "-c", "integration", "gpu")
    command(tmp_path, "merge", "--no-ff", "ui", "-m", "test reviewed merge")
    assert inspect(tmp_path, "stable", "gpu", "ui", "integration", review)["status"] == "ok"
    commit_file(tmp_path, "core/jobs.py", "base\n")
    report = inspect(tmp_path, "stable", "gpu", "ui", "integration", review)
    assert report["status"] == "review_required"
    assert report["integration_shared_mismatches"] == ["core/jobs.py"]


@pytest.mark.parametrize("change", ["stale_base", "gpu_owned_file", "invalid_branch"])
def test_invalid_shared_review_never_reports_safe(tmp_path, change):
    history(tmp_path, "core/jobs.py", "legacy_app.py")
    review = shared_review(tmp_path)
    if change == "stale_base":
        review["base"] = "0" * 40
    elif change == "gpu_owned_file":
        review["files"]["core/effects.py"] = {"branch": "gpu", "object": "unused"}
    else:
        review["files"]["core/jobs.py"]["branch"] = "other"
    with pytest.raises(ValueError):
        inspect(tmp_path, "stable", "gpu", "ui", shared_review=review)
