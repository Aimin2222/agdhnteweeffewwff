# v5.10.14 Studio / GPU統合レビュー

GPU: feature/gpu-montage-v51014、UI: feature/ui-studio-v51014、統合: integration/v5.10.14。原本: archive/received-ui-v51014（入れ子ZIPの内側パッチを正確に保存）。既存72ブランチと過去の配布物を保持。

受領変更のうち、core/camera.pyは共有APIとしてGPU担当がレビュー、core/montage_fx.pyはGPU担当だけが変更。旧GPUファイルをUI版で丸ごと上書きしない。Template/CameraPlan/run_auto_edit/音声録音の呼出契約は維持する。

- UI: シーン・カメラ・カラー・FX・出力の5作業領域、Ctrl+1〜5、詳細4タブ、折りたたみ、検索/グループ付き図鑑、500ms仕上がりホバー、DOF実フレーム比較。既存設定変数を共有し、領域切替/折りたたみで値を消さない。
- 応答性: 受領図鑑のメイン/拡大画像生成と比較プレビューのフレーム取得・縮小・画像加工をワーカーへ移す。Tk/PhotoImage/設定取得はUIスレッドのみ。最新要求1件と180ms間引き、サムネイル最大3枚/45ms、閉じる/外部destroyでワーカーとafterを停止。失敗理由を表示する。装飾の静止画生成とミラー近似表示はCPUであり、GPU動画加工と区別する。
- GPU: 切替演出は全10選択肢（cutは従来の高速コピー、残り9種類はGPU Full/OpenCL）。GPU非対応/実行失敗時はCPUフォールバックと実フィルターを診断に記録。NVENCとGPUエフェクトを混同しない。
- GPUの映像時刻: 元動画の映像フレーム数をffprobe、無い場合はデコードなしの映像パケットコピーで取得。60fps入力に対し時刻/trim/出力フレーム数を明示し、AAC末尾の長さを映像フレーム数として使わない。音声はcopy。色付き演出は小さいLUTを一度準備してOpenCLで毎フレーム適用する。旧主GPUレンダーの60fps修正は保持。
- 互換性: 旧日本語切替演出名も読み込める。キル演出は実キル時刻がある場合だけ加え、既定kill_time=0の手動0/±90°ビューを維持。スマート構図の最終±55°制限も維持。
- カメラ: 受領RED通常三人称のpitch符号補正はこのモードのみに限定。BLUE/シネマ/FPS/Lolnamの俯角は変更せず、姿勢・位置の同じ基準とTargetLockを保持する。RED自動192°と今回の通常三人称補正はWindows実映像で未検証。

共有8ファイルの正確なblobをJSONで確認する。担当衝突ガード:

```sh
.venv/bin/python tools/check_parallel_integration.py --gpu feature/gpu-montage-v51014 --ui feature/ui-studio-v51014 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.14.json --integration integration/v5.10.14
```

OpenCLの切替演出9種類は検証専用CPU PoCLでカーネル/フレーム数/60fps/音声同一性とCPU参照との差を確認した。製品のGPU検出はCPU OpenCLを拒否したまま。Windows/NVIDIA/LoLの速度や今回のカメラの良否は未確認。

完全版とCodex統合v5.10.13基準のGit差分を配布。WindowsまとめテストはWINDOWS_TEST_v51014_JA.md。音声/録画/検出/既存GPU比較バッチとPNG37種類は保持。診断や個人設定はGit/ZIPへ含めない。
