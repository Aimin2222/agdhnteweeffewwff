"""Local, bounded diagnostic excerpts for user-initiated camera QA exports."""
from pathlib import Path
import json
from statistics import median

TAIL_LIMIT_BYTES = 1_000_000
DIAGNOSTICS = Path(__file__).resolve().parents[1] / 'diagnostics'
LOG_NAMES = ('runtime.log', 'crash.log', 'last_error.txt', 'audio.log',
             'capture.log', 'selftest_latest.json', 'reference_review_latest.log',
             'capture_worker_latest.log')


def collect_qa_support(folder, *, diagnostics=None, log=lambda _m: None,
                       build_identity=None, expected_capture_count=10):
    origin = Path(diagnostics) if diagnostics is not None else DIAGNOSTICS
    target = Path(folder) / 'QA_Support'
    report = {'files': [], 'errors': [], 'truncated': [], 'tail_limit_bytes': TAIL_LIMIT_BYTES}
    def error(message):
        report['errors'].append(message)
        log('診断情報の追加をスキップ（録画結果は保持）: ' + message)
    try:
        target.mkdir(parents=True, exist_ok=True)
        notes = (
            '# AutoCine 一括テスト結果\n\n'
            '作成されたQA ZIPをすべて、この会話へ添付してください。外部への自動送信はありません。\n'
            'results.json：撮影・切替・キルフレーム・計画ID・失敗とZIP一覧。\n'
            'RED/BLUE_camera_3frames.jpg：動画の前/中/後の時間割合サンプル。実キル瞬間を自動特定した画像ではありません。\n'
            'RED/BLUEのreview_all.mp4：カメラごとの連続比較。\n'
            'Transitions：場面切替。KillFrames：登場動作。\n'
            'QA_Support：各最大1MBの診断末尾（元のバイトを保持）。途中からのJSONは完全なJSONではありません。\n'
            'capture_freshness.json：直近の録画で新しく取得できた画面の割合。出力fpsとは区別します。\n'
            '画面内の主役や構図はWindows実機で目視確認が必要です。\n'
        )
        if build_identity is not None:
            notes += (
                f"\n実行版: {build_identity.get('installed_version', 'unknown')}\n"
                f"QA実装版: {build_identity.get('qa_build_version', 'unknown')}\n"
                f"カメラコードID: {build_identity.get('camera_code_fingerprint')}\n"
                f"版不一致: {build_identity.get('version_mismatch')}\n"
                '古いresults.jsonの映像と混同しないでください。\n'
                'flat_upper_background_ratioは時間割合3時点の空/単色領域の目安で、キル検出ではありません。\n'
            )
        (target/'READ_ME_FIRST_JA.md').write_text(notes, encoding='utf-8')
        report['files'].append('QA_Support/READ_ME_FIRST_JA.md')
    except OSError as exc:
        error(f'{type(exc).__name__}: {exc}')
        return report
    for name in LOG_NAMES:
        if name == 'capture_worker_latest.log':
            workers = [p for p in origin.glob('capture_worker_*.log') if p.is_file() and not p.is_symlink()]
            source = max(workers, key=lambda p: p.stat().st_mtime_ns) if workers else origin/name
        else:
            source = origin/name
        try:
            if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(origin.resolve()):
                continue
            with source.open('rb') as handle:
                handle.seek(0, 2)
                size = handle.tell()
                handle.seek(max(0, size-TAIL_LIMIT_BYTES))
                payload = handle.read(TAIL_LIMIT_BYTES)
            if size > TAIL_LIMIT_BYTES:
                report['truncated'].append(name)
            (target/name).write_bytes(payload)  # copy excerpts without re-encoding original bytes
            report['files'].append('QA_Support/'+name)
        except OSError as exc:
            error(f'{name}: {type(exc).__name__}: {exc}')
    try:
        perf_dir = origin/'performance'
        rows = []
        if perf_dir.is_dir() and not perf_dir.is_symlink():
            paths = sorted(perf_dir.glob('render_*.json'), key=lambda p: p.stat().st_mtime_ns,
                           reverse=True)
            for path in paths:
                if len(rows) >= max(0, int(expected_capture_count)):
                    break
                if path.is_symlink() or not path.is_file() or path.stat().st_size > TAIL_LIMIT_BYTES:
                    continue
                try:
                    data = json.loads(path.read_text(encoding='utf-8'))
                except (ValueError, UnicodeError, OSError):
                    continue
                pipeline = data.get('pipeline', {})
                if pipeline.get('stage') != 'capture':
                    continue
                frames = pipeline.get('frames')
                fresh = pipeline.get('fresh_frames')
                seconds = pipeline.get('duration_s')
                if not (isinstance(frames, int) and isinstance(fresh, int) and
                        isinstance(seconds, (int, float)) and frames > 0 and seconds > 0 and
                        0 <= fresh <= frames):
                    continue
                rows.append({'frames': frames, 'fresh_frames': fresh,
                             'fresh_ratio': round(fresh/frames, 4),
                             'fresh_fps': round(fresh/seconds, 2),
                             'output_fps': pipeline.get('output_fps')})
        if rows:
            summary = {'capture_count': len(rows), 'fresh_fps_median': round(median(r['fresh_fps'] for r in rows), 2),
                       'fresh_ratio_median': round(median(r['fresh_ratio'] for r in rows), 4),
                       'captures': list(reversed(rows))}
            (target/'capture_freshness.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
            report['files'].append('QA_Support/capture_freshness.json')
    except (OSError, ValueError) as exc:
        error(f'capture_freshness: {type(exc).__name__}: {exc}')
    return report
