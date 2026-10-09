# LoL AutoCine — Codex 開発引き継ぎ書

更新: 2026-10-08 / ベース: **v5.8.5**

> これは ChatGPT での反復開発の要点をまとめた移行資料です。過去チャット全発言の完全な書き起こしではありません。実際の仕様・実装は同梱ソースを読み、差異があればユーザーに確認してください。

## 0. 製品の方向性
Windows向けLeague of Legendsリプレイの自動シネマティック動画作成ツール。ゲームのリプレイAPIを使い、キル/アシストの検出、対象選択、固定カメラ追従、演出・エフェクト、クリップとモンタージュ生成を、初心者でもなるべくワンクリックで使える形にする。

- UIとコミュニケーションは日本語。
- **既存機能を削除したり、確認なくUIやカメラを作り直したりしない。** 小規模な変更・回帰テスト・Git差分レビューを優先。
- 使いやすさと自由度の両立。基礎操作は簡単、詳細調整は展開式/スクロール式エディタに。
- GPUでの映像処理・GPUエンコードを目指す。ただし「NVENCが利用できた」ことと「GPUエフェクトが実行された」ことを区別する。
- ノイズ・白黒化・クラッシュ・速度異常・音声欠落を再発させない。

## 1. 現在の基準ファイルとユーザー検証
- **v5.8.4**: Windows実機で「チェックしたシーンだけ作成」のクラッシュが解消したことをユーザーが確認。回帰時の安定基準。
- **v5.8.5**: CPU Bloomの負荷軽減、DOFの焦点マスク軽量化、OpenCL能力判定/診断を改善。ユーザーがエフェクトOFF、Focus Blur、DOF、複数クリップのテストを実行。すべてカラーで書き出せたと報告。直近の診断ZIPでは5件の映像書き出しが成功と報告。
- v5.8.5診断時の書き出し所要時間の参考値: 9秒前後のクリップで60fpsは約69〜71秒、144fps/DOFは約111秒。条件差があるため正確な速度比較は同一条件で再実験すること。
- **GPUエフェクトは未稼働**。現状確認できるのはNVIDIA NVENCエンコードで、エフェクトはCPU経路へフォールバック。ユーザー環境でFFmpegに必要なOpenCLフィルタ（例: `avgblur_opencl`）が不足する可能性が高い。**GPUエフェクト導入済みと誤って表示しないこと。**
- 実機GPU: NVIDIA GeForce GTX 1070 Ti (VRAM 8GB)。OS: Windows。LoL Replay API/音声録音はユーザー環境でテスト。
- LoL音声はNative Windows Process Loopbackで成功済み。映像はカラー・音声ありのクリップ生成を確認。

## 2. 重大な不具合の歴史 / 絶対に戻さない
1. `scale_cuda,hwdownload,format=yuv420p`: FFmpegの `Invalid output format yuv420p for hwframe download` で全クリップ失敗。v5.7.8ではCPUスケーリング + NVENCへ戻して復旧。GPU→CPUの転送フォーマットとデバイス互換性は実行テスト必須。
2. LoLゲーム音声: デスクトップ全体の音を取り込むのは仕様違反。Windowsの `ActivateAudioInterfaceAsync` と `AUDIOCLIENT_PROCESS_LOOPBACK_PARAMS` / `PROCESS_LOOPBACK_MODE_INCLUDE_TARGET_PROCESS_TREE` を使うNative C++ヘルパー方式。 `tools/native_audio/`、`BUILD_AUDIO_HELPER.bat`、`ENSURE_CPP_BUILD_TOOLS.bat` などを維持。
3. オーディオC++: `GetMixFormat` で `0x80004001`、`captureClient` 未定義などの過去バグがあった。修正済み経路を壊さない。
4. カメラ: `OrbitTargetLock` は固定したプレイヤーを常に画角中心に置く。0/90/180/270度Orbitでロストさせない。ブルー/レッドサイドの向き、空からの斜め後ろ視点、カメラ高さを勝手に変えない。良好と評価された「三人称斜め後ろ」は維持。
5. クリップが約8倍速になった過去バグ。リプレイ時刻と録画の実時間の整合を維持。
6. 書き出しがモノクロになる過去バグ。プレビューと最終MP4の色を保持。
7. Focus Blur/DOFの重さでフリーズ・異常終了。CPUフィルターの重い1080p全面Blurを避ける。強度・色・焦点の見た目も回帰テスト。
8. 「チェックしたシーンだけ作成」で異常終了コード `-805306369`。v5.8.4で正しい経路に段階別ログ、二重起動防止、プレビュー負荷軽減を実装。ユーザーが正常動作確認。
9. TkinterのUIスレッド以外から変数 `.get()` 等を読むと `RuntimeError: main thread is not in main loop`。バックグラウンドワーカーからTkアクセスしない。UI操作はメインスレッドへ配送。
10. 以前の`COLLECT_DIAGNOSTICS.bat`が `No logs found` と表示。現在は Pythonのログ収集スクリプト経由に改善。ログ保存場所も回帰確認。

## 3. 維持する機能（ソースとUIの棚卸しを優先）
- Replay API、`.rofl`、最近のリプレイ、プレイヤー一覧/固定、LoL画面ミラー、HUD切り替え、キル/アシスト/両方スキャン、チェック式シーン一覧、選択移動、選択/全部/チェック済みクリップ作成、モンタージュ。
- カメラ: 三人称追従/シネマティック、FPS風、トップダウンなどの既存選択肢、Orbit・自動Orbit・ドリー・FOV変化・スムージング・キル前後のタイムライン、ブルー/レッドサイド対応。
- 各種効果: Focus Blur、DOF、Bloom(ブルーム)、フォグ、カーブ補正、Color/LUT、Vignette、Radial/Zoom Blur、Glitch、Camera Shake、Wiggle、Mirror/Slice、Film Burnなど既存設定。
- 参考動画URL/ローカルファイルからのテンプレート、プリセット、BGM、LoLのみの録音、プレビュー、書き出し形式/FPS、GPU監視、診断/キャンセル/進捗、ログ採取。
- 初心者向けワンクリック操作を保つ。新機能の追加で既存UIのボタン/スライダー/チェック欄を隠さない。

## 4. UI方針
- v4.2 UIStudio系の白基調3ペインをベースにする。
- 中央は「上に固定ミラー/カメラプレビュー」「下に独立スクロール可能なエディタ」、ドラッグで高さ調整可。
- エディタ: タイムライン/カメラ/エフェクト/カラー/曲線/DOF焦点可視化など。
- スライダーには数値表示と直接入力。プレビューは再生/停止。出力先選択。シーン一覧のチェック欄・移動ボタンが隠れない。
- GPU優先（ただし実際に実行したパスを表示）。出力基本は1080p MP4。必要時にFPS詳細設定。ユーザーは60/144fpsにも関心。

## 5. 実装場所の目安（実ソースを必ず確認）
- `app.py`, `legacy_app.py`: 起動/UI/操作ハンドリング
- `core/replay_api.py`, `core/scanner.py`, `core/players.py`: リプレイ情報/検出
- `core/camera.py`: TargetLock/カメラ
- `core/capture.py`, `core/recorder.py`: 映像取り込み・クリップ録画
- `core/effects.py`, `core/render_fx.py`, `core/gpu_pipeline.py`: フィルタグラフ/FFmpeg/GPU判定
- `core/audio.py`, `core/procloop.py`, `tools/native_audio/`: LoL音声
- `core/performance_diagnostics.py`, `tools/collect_diagnostics.py`: 計測/ZIP
- `tests/`: 回帰テスト
- `START.bat`, `RUN_TESTS.bat`, `COLLECT_DIAGNOSTICS.bat`: Windowsの入口
- `README_v5.8.5_JA.md`: 現時点で新しい実装メモ
古いREADMEや文字化けしたdocs名もある。重要度を確認して整理するが、根拠なく削除しない。

## 6. 今後の優先順位
**第1段階（Codex移行直後）**: ソースの全体監査。Git初期化/ブランチ、テスト実行、依存ライブラリとWindows専用箇所のマッピング。既存機能を壊さないための回帰テストを追加。実装変更は最小限。

**第2段階**: GPU経路の自動判定と診断の真実性確保。GTX 1070 Tiで利用可能なOpenCL/Direct3D等の経路を実機診断。CUDAスケールの過去の失敗経路をそのまま復活させない。OpenCL利用可能でも実行フォーマット互換性を確認。

**第3段階**: Focus Blur/Bloom/DOFなど重いフィルターを個別にGPU化。オリジナル映像とのカラー・効果比較、実際にGPUで動いた証拠、速度/VRAM/CPUの比較が通ったものだけ段階採用。フォールバック常設。

**第4段階**: 編集UIの整理・FPS負荷改善・配布形態(exe)とインストーラの整備。

## 7. 必須テスト（Windows/LoL実機が必要な項目を明示）
1. 起動、Replay API、プレイヤー固定/切り替え。
2. チェック済み1シーンと2シーン連続生成、二重クリック防止。
3. エフェクト全OFF / Focus Blur / DOF / Bloom 別々に適用し、カラーと効果があること。
4. 出力音声がLoLゲーム音**のみ**、同期がずれないこと。
5. クリップ時間・再生速度・カメラ対象ロストなし・FPS指定一致。
6. GPU/NVENC有効時およびGPUフィルター非対応時の自動CPUフォールバック。
7. `COLLECT_DIAGNOSTICS.bat` で診断ZIP生成。JSONに実行コマンド・実際のフィルター・成功/失敗・処理時間・CPU/GPU計測値を残す。
8. 後方互換の Python構文チェック/既存 `tests/` を実行する。環境依存の失敗は「未実施」「要Windows実機」と明記。

## 8. 開発時のやりとり
- ユーザーに日本語で説明し、修正箇所・テスト結果・未検証箇所を区別。
- 既存機能を勝手に削らない。実装の大規模変更は事前に設計と段階計画。
- 修正ごとに差分と回帰テストの記録を残す。
- 手動計測より診断ZIPを優先し、GPU計測は実行フィルター/デバイスログとの整合を見る。
- Windows実機でしか確かめられない部分は成功したと主張しない。

## 9. 追加資料
ユーザーが実機で取得した `AutoCine_Diagnostics.zip` は**この移行パッケージには含めない**。必要ならユーザーがCodexの作業フォルダに別途配置する。実機の経路・処理時間を確認できる重要資料だが、ログ内のユーザー名/パスなどを不要に公開リポジトリへ置かない。
