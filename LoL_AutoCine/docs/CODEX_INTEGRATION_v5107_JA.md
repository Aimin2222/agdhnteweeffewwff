# v5.10.7 ミラー設定操作・GPU比較テスト起動修正

受領v5.10.6の差分基準は取得用v5.10.5 ResponsiveUI。現在のGPU Full版へファイル上書きをせず、必要な差分だけ統合しました。GPUのeffects/gpu_pipeline/gpu_full/recorder/montage/previewとLoL専用音声を保持しています。

## 診断から確認できたこと

最新受領診断は映像加工16回すべて成功（returncode=0、gpu_effects_confirmed=true、full_gpu_pipeline=true）。NVDEC・OpenCL GPU・h264_nvenc、1080p・60fpsで処理しています。約7.1秒の映像で加工7.8〜10.2秒、約17.5秒では18.6〜20.5秒。GPU比較テストのgpu_batch記録は含まれず、TEST_GPU_RENDERの6ケース完了は確認できません。35秒ごとのfatal_pythonスタックは実行中の定期採取であり、それだけではクラッシュを示しません。サンプルではミラーワーカーのPillow縮小が4/5回、Tk側のPhotoImage転送が1回見られました。設定エリア単体の操作計測はないため、すべてのラグ原因を確定したものではありません。

## 修正

- ミラーのBGRA→RGBをPillow raw decoderへ変更。全解像度のNumPyチャンネル並べ替えとLANCZOS縮小を避け、BILINEAR・縮小前処理を使用。WGCの不透明とは限らないalphaは合成に使いません。
- 表示サイズへの拡大もワーカーで行い、Tk側の画像resizeを除去。Canvasの画像/説明itemを再利用し、毎フレームdelete/createしません。
- 設定・スライダー・スクロール・タブ操作中はミラーのみ最大640x360の簡易加工、更新間隔167ms。操作後は960x540、FX約15fps/素のミラー最大20fpsへ戻ります。表示はウィンドウへ合わせて拡大します。書き出し1080p/60fps、144Hzカメラ、録画FPSは変更しません。
- テンプレートのTk値読み取り/JSON化を変更時だけへ。変数traceは無効化通知のみで、ワーカーはTkへ触れません。数値入力の一時的な空欄は次回再取得します。
- TEST_GPU_RENDERは通常起動と同じpy -3を優先し、使えなければローカルvenv、pythonへ。終了コードとPython選択を診断に残し、すべての経路でpauseします。存在しないWindows用.venvを必須にしません。
- GPUテストはエンジンimport/ファイル選択より前に起動記録を作成。失敗・中断・キャンセル・6ケース完了を区別し、コンソールとUTF-8ログへ記録します。
- 受領UI差分からRED側Orbitのside_yaw、遅れて増えるアシストの取り込み、手動/通常全シーン作成の検出モードsnapshot、ガラス斬撃/中央なしを統合。既存のホバー/クリック説明、音声失敗後の復帰は維持し、準備失敗時のミラー復帰を補いました。TargetLock計算は変更しません。重複mirror_restoreモジュールは追加せず、現在の再試行付き関数を使用します。

ライブミラーは引き続きCPUによる近似プレビューで、Tkへの画素転送もCPUです。映像書き出しのGPU成功と混同しません。CPU使用率0や今回Windows実機でラグが解消したとは主張しません。

## 並行開発の保存

GPU/共有: feature/gpu-test-launch-v5107
UI: feature/ui-mirror-v5107
統合: integration/v5.10.7
旧54ブランチの先端を維持し、共有camera/jobs/scanner等のGit blobを個別レビューします。

```sh
.venv/bin/python tools/check_parallel_integration.py --gpu feature/gpu-test-launch-v5107 --ui feature/ui-mirror-v5107 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.7.json --integration integration/v5.10.7
```

受領パッチ原本はpatches/history/v5106_from_codex_v5105.patchへ保存。コード原本やユーザーの生診断/録画/個人設定を取得用Gitへ追加しません。回帰検証結果はhandoff/VERIFICATION_v5.10.7.json。Linux/Tkの検証とWindows/NVIDIA/LoL実機の確認は区別します。
