# v5.9.7 安全統合・検証記録

## 統合対象と保持したもの

受領したLoL_AutoCine_v5.9.7_Codex_MergeChanges.zipは差分版。統合の継続依頼として扱い、添付資料の診断ZIP/動画送付推奨を外部送信の依頼とは扱わない。

- UI: 上段3ペイン＋下段全幅エディタ、コンパクト表示、日本語ラベル、チェック表示、カメラグラフのキル/キーフレーム/カーソル表示、DOF概念図、モンタージュ切替の設定を採用。
- core/effects.pyのフルファイルは採用しない。既存scene_keyframes位置互換修正を保持し、新しいmontage_fxを末尾に追加。新フィールドを除いたASTはv5.9.6と完全一致。
- core/jobs.pyは通常cutを既存concat_clipsへ直接渡し、flash/darkだけレビュー済み独立アダプターへ渡す。関数署名・音声工場・録画・カメラ・時計・HUD復元を維持。
- core/montage_fx.pyはCPU eqで明るさを短時間変化させる追加エンコード。音声はstream copy、fps強制を除去、失敗時は音声入り元連結へ復旧。GPUエンコードとGPUエフェクトを区別して診断し、NVENC選択時の失敗だけCPU再試行。
- 既存coreの20ファイルはバイト一致。Native録音ヘルパーとWindows起動バッチも変更なし。v5.9.5のかんたん編集出力同期修正、v5.9.6のHUDと一括適用を保持。

## Git担当と衝突検出

UI: feature/ui-studio-v597、GPU: feature/gpu-engine、統合: integration/v5.9.7。旧版ブランチを残す。

```sh
.venv/bin/python tools/check_parallel_integration.py --ui feature/ui-studio-v597 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.9.7.json --integration integration/v5.9.7
```

終了0: 担当違反・共有未承認・merge衝突・GPU/UI巻き戻しなし。旧v5.9.6レビューではjobsの新変更を検出し終了1。新規montageモジュールをGPU所有、受領UIテストをUI所有として実Git履歴による検出をテスト。レビューは正確なblobと担当にだけ適用し、後の変更へ無条件に承認を引き継がない。

## 検証

- pytest tests -q: 115件成功、失敗/skipなし（15.46秒、Tk/Xvfb）。元の位置引数、v5.9.6キー配列の位置、局所化キー往復、全幅レイアウト、HUD、コピー/一括適用、Undo/Redo、自動保存、カメラ、UIスレッド制約を検証。
- Python63ファイルの構文、pip check、git diff --checkが成功。
- NVENC失敗→CPU、CPU失敗をGPU失敗と誤表示しないこと、タイムアウト/小さい出力/フィルター失敗→元連結復旧、音声copyとfps維持、ffprobeなしのffmpegによる時間取得を回帰テスト。
- 実Tk→worker→jobs→Director→モックReplay API: キー5個、対象固定、health HUD指定と終了復元、チェックした2シーンのみ一括適用、1 Undo/Redo、自動保存JSON往復、設定コピー独立、保存済みプロジェクトがプレビューで変わらないことを確認。全幅UIで旧ワークスペース切替も成功。
- 実FFmpeg: 1080p/60fpsと640x360/144fpsの合成クリップを通常/flash/darkで出力。音声AACデータは元の連結と完全一致、長さ差0秒、fps・解像度・bt709カラータグを維持。つなぎ目の明るさだけ変化し、離れた時刻のフレーム平均差0を確認。GPU実行ではなくCPU libx264による検証。

- Appの既存呼出し境界から実jobs/録画/FFmpegまで通し実行。シーン別モードと従来モードの双方で2クリップ＋flashモンタージュを1080p/60fpsで生成。逆順シーン、キー配列転送、対象固定、Template不変、カラー、非無音の合成音声を確認。映像と音声の末尾長差は最大約0.029秒（実LoL音声の検証ではない）。

ローカル証跡: /workspace/.onboarding-results/autocine/v597-*。補助は /workspace/.onboarding-tools/autocine/verify-v597-studio.py、verify-v597-montage.py、verify-v597-render.py。生成動画・音声・診断・設定はGitへ含めない。

## 未検証と今後

Windows、実LoL、GTX 1070 Ti、Native Process Loopback録音、実NVENC成功は未検証。合成音声とモックAPIを実機検証と混同しない。CPU Bloom/DOFのGPU高速化は未実装。モンタージュ演出は追加の映像エンコードが必要で、高速化そのものではない。

旧tests/run_tests.pyの初回16件中11成功/5失敗（WAVなしの旧4条件、低解像度静止画と1080p固定Bloomの不一致）、旧CPU GUI通し試験240秒未完了は今回再実行せず、115件pytestの結果と区別する。

Windowsでは旧版を別フォルダに残し、START.batで起動してペイン伸縮、チェック表示/選択/スクロール、日本語名の設定保存、HUD3種、HPバー中心の名前設定、2シーン一括適用とUndo、通常/flash/darkの色・fps・LoLのみの音声・対象追従を確認する。YouTube/X参考映像の再現は未検証。

次のGPU作業は能力列挙と実行プローブの区別、フォールバック理由、Bloom/DOFの小さな段階導入と色・音声・同期・速度の比較を優先する。旧hwdownload,format=yuv420p経路を安易に復活させない。

取得用GitHubブランチには完全ソースと全ブランチbundleを保存し、mainへマージしない。Windowsへの取得に環境Publishは不要。セットアップの将来クラウド反映だけ、保存済みドラフトの確認・保存・Publishが必要。
