"""Local, bounded diagnostic excerpts for user-initiated camera QA exports."""
from pathlib import Path

TAIL_LIMIT_BYTES = 1_000_000
DIAGNOSTICS = Path(__file__).resolve().parents[1] / 'diagnostics'
LOG_NAMES = ('runtime.log', 'crash.log', 'last_error.txt', 'audio.log',
             'capture.log', 'selftest_latest.json')


def collect_qa_support(folder, *, diagnostics=None, log=lambda _m: None):
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
            '画面内の主役や構図はWindows実機で目視確認が必要です。\n'
        )
        (target/'READ_ME_FIRST_JA.md').write_text(notes, encoding='utf-8')
        report['files'].append('QA_Support/READ_ME_FIRST_JA.md')
    except OSError as exc:
        error(f'{type(exc).__name__}: {exc}')
        return report
    for name in LOG_NAMES:
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
    return report
