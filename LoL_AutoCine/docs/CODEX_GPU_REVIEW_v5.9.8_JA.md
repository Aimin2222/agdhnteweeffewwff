# v5.9.8 GPU担当の接続レビュー

受領エンジン全体の置換は行わない。scene_keyframesとmontage_fxの既存位置を保持し、新しいsmart_highlight_enabled/style/highlight_pulseを末尾に追加する。v5.8.5/v5.9.6/v5.9.7の位置引数互換性を検証する。

新しいcore/highlight_pulse.pyはGPU所有として保管する。CPU標準eqの時間式を既存build_graphの接続点へ限定して追加。highlight_pulse=0、イベントなし、静止画には追加しない。スマート計画有効フラグだけでグラフを変えない。最大8イベントに式を制限し、強度を0〜1へ制限。録音・エンコーダー・GPUアップロード/ダウンロード・モンタージュ・TargetLockは変更しない。

core/jobs.py、camera、clockなど共有ファイルは今回変更していないため、docs/CODEX_SHARED_API_REVIEW_v5.9.7.jsonをそのまま使用する。UIブランチはGPUファイルを持たず、GPUブランチはUIファイルを変更しない。新しいGPU/テストファイルの所有者検査も実Gitで確認する。

UI→Shot→Templateの新フィールド、通常・明示スマートの切替、旧JSON/既存個別設定の優先、Undo/RedoはUI所有側で検証。色と短時間アクセント・音声・時刻は実FFmpeg/合成映像で確認し、実LoL/Windows/Native録音/実NVENCとは区別する。
