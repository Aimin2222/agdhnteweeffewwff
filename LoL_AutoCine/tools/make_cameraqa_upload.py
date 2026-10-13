"""Developer-only: repackage an existing CameraQA folder without re-recording."""
import argparse
import json
from pathlib import Path
from core.qa_upload import prepare_upload_copies, MAX_ZIP_BYTES, EXCLUDE_DIRS
from core.qa_package import split_test_results


def repackage(folder, *, encoder_policy="auto", log=print):
    folder = Path(folder).resolve()
    report = folder / "results.json"
    manifest = json.loads(report.read_text(encoding="utf-8"))
    if manifest.get("kind") != "live_replay_camera_test":
        raise ValueError("CameraQAのresults.jsonがあるフォルダーを選んでください")
    copies, upload = prepare_upload_copies(folder, encoder_policy=encoder_policy, log=log)
    # Preserve the input report outside the upload archive, including old paths.
    root = next((folder / '.qa_upload').glob('export*'))
    backup = root / 'results_original.json'
    generation = 1
    while backup.exists():
        generation += 1; backup = root / f'results_original_{generation:03d}.json'
    backup.write_bytes(report.read_bytes())
    manifest["qa_upload"] = upload
    def update(paths):
        manifest["qa_archives"] = [str(p) for p in paths]
        manifest.pop("qa_packaging_error", None)
        report.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return split_test_results(folder, max_bytes=MAX_ZIP_BYTES, source_overrides=copies,
                              exclude_dirs=EXCLUDE_DIRS, log=log, report_update=update)


def main():
    parser = argparse.ArgumentParser(description="既存CameraQAを送信用540p60・各30MB以下へ変換（開発用）")
    parser.add_argument("folder", help="results.jsonがあるCameraQAフォルダー")
    parser.add_argument("--encoder-policy", choices=("auto", "gpu", "cpu"), default="auto")
    args = parser.parse_args()
    for path in repackage(args.folder, encoder_policy=args.encoder_policy):
        print(path)


if __name__ == "__main__":
    main()
