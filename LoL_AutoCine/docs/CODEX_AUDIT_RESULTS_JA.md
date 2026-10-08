# 初回監査・実行結果

監査日: 2026-10-08。対象: アップロードされたLoL AutoCine v5.8.5。指定された3文書を全文確認した。ユーザーの希望はローカルで継続開発すること。GitHubへの公開/pushは実施していない。

## 実施したこと

1. 安全にZIPを新規展開し、全体構成・Windows依存・UI/カメラ/音声/FFmpeg/診断/テストの境界を調査。
2. ローカルGitの基準ブランチ`baseline/v5.8.5`と調査ブランチ`codex/initial-audit`を作成。基準コミットは`96b928a7385537317e73bad5235a28984fe94716`。
3. `.venv`へ依存関係とpytestを導入。Xvfbは署名・パッケージハッシュを検証するAPTで取得し、`/workspace/.onboarding-tools`内へ展開。システム領域へインストールしていない。
4. 既存構文チェック・モック/合成素材テスト・GUIテストを実行し、失敗原因を切り分け。
5. GPUフィルターの選択条件と実行/表示/診断の整合性を監査。GPUがないクラウドでNVENC搭載表示と実際の失敗の不一致を再現。
6. 構成図、GPU原因分析・実機診断コマンド、ローカルGit/Windows開発手順、この実行結果を追加。
7. 再利用用`install_script`と`start_skill`をクラウド環境ドラフトへ保存。インストール手順は初回相当と再実行の両方で成功。保存は公開・新規タスク復元の成功を意味しない。

## テスト結果

Linux CPU環境、Python 3.12.14、imageio-ffmpeg付属FFmpeg 7.0.2、Xvfbを使用。既存テスト/アプリ本体は変更していない。

| チェック | 結果 | 確認できたこと・限界 |
|---|---|---|
| 全38 Pythonファイルのpy_compile | 成功 | 構文正常。ランタイム/Windows APIの保証ではない。 |
| pip check | 成功 | 導入済み依存に宣言上の矛盾なし。 |
| install.sh 初回相当・再実行 | 両方成功 | 仮想環境、依存導入、構文、Tk/Xvfbの準備が再実行可能。 |
| pytest: allkill_safety / feature_preservation / orbit_target_lock | 9件成功、失敗/skipなし | モンタージュ失敗時の素材保持、既存設定・テンプレート、Orbit 0/+90/-90度。 |
| pytest: v31_regressions | 2件成功、失敗/skipなし | 実FFmpegで映像効果＋音声互換引数の出力、カメラ安全デフォルト。 |
| test_v585_diagnostics.py | スクリプト成功 | NVENCのみではGPU効果を選ばない、検証済みOpenCL時のNV12グラフ、診断ZIP集約。Mock能力でありGPU実機成功ではない。 |
| test_v585_filters.py | 4ケース成功 | Bloom、DOF、DOF＋Bloom、DOF＋Bloom＋Focus Blur。1080p実FFmpegグラフを各3フレーム実行。 |
| test_checked_dispatch.py | スクリプト成功 | App起動、チェック済み2件の配送、段階ログ、busy即時設定、ワーカー完了。レンダーはスタブ。 |
| tests/run_tests.py | **16件中11成功・5失敗、終了1** | 成功/失敗詳細は下表。冒頭のfeature_preservationの5関数も実行されたが、16件の集計とは別で重複するため加算しない。 |
| tests/gui_smoke.py | **失敗、終了1** | 10プレイヤー、4シーン、ミラー、カメラプレビュー、音声付き最初のクリップまで確認。CPUでジョブが240秒制限に収まらず`done["ok"]`がfalse。全出力/モンタージュ/正確静止画の完了は未確認。 |
| Windows・LoL・GTX 1070 Ti・Native Helper | 未実行 | このLinuxクラウドに対応OS、LoL、GPUデバイスがない。実機検証が必要。 |
| 参考動画URLのダウンロード | 未実行 | yt-dlpは導入したが、個別動画サービスの接続/取得は今回の検証対象外。 |

## 総合runnerの詳細

| ケース | 結果 |
|---|---|
| t01 設定パッチ、t02 10プレイヤー、t03 対象プレイヤー走査、t04 グルーピング、t05 カメラ曲線 | 成功 |
| t06 全テンプレート/グレード | 失敗: 最初のテンプレートはゲーム音ONだがWAVを渡さない。以後のテンプレート/グレードは未実行。 |
| t07 デスクトップ入力へ切替しない | 成功 |
| t08 自動編集end-to-end | **成功**: モックAPI、合成映像/音声、対象固定、3クリップ、音声ストリーム、FPS、モンタージュを検証。約282.6秒。 |
| t09 再生停滞ガード | 成功 |
| t10 UTF-8パス/名前 | 失敗: ゲーム音ONのTemplateにWAVを渡さない。 |
| t11 HUD安全モード | 失敗: 音声factory未指定でWAVがない。さらに後続の「HUD要求がない」期待は現行HUD実装と不一致で未到達。 |
| t12 FPS風カメラの安全フォールバック | 成功 |
| t13 音声ミックス/同期 | 失敗: 音声なし`n`ケースもgame_audio=TrueでWAVがなく拒否される。先行g/gb/bは成功、後続offケースは未実行。 |
| t14 WAV無音埋め、t15 ビネット単調性 | 成功 |
| t16 テンプレートプレビュー | 失敗: 正確静止画のBloom合成に480x270と1920x1080が混在。後続テンプレートの比較は未実行。 |

音声不足の4失敗を解消するために、アプリが無音出力を成功扱いするよう戻してはいけない。現行仕様に合わせてテスト素材/WAVや音声OFF設定を整備する別の小差分が必要。HUDはモックへ直接`hide_hud`/`restore_hud`を呼び、現在は要求が1件/復元後2件発生することを確認した。安全モード仕様の説明と実装の差は勝手に変えず、今後のテスト整理で扱う。

プレビューについては同じ480x270素材と既存グラフで、Bloomありは`First input link ... size 480x270 ... second ... size 1920x1080`で失敗し、診断用にBloomだけOFFにした場合は終了0を確認。FFmpeg未導入ではなく、現行グラフ/プレビューのサイズ前提の不具合と判断した。GUI通し試験の途中の2本目に音声がまだなかったことは、レンダー・後段mux完了前にテストが打ち切った結果であり、完成MP4の音声欠落と断定しない。

## GPUの実行結果

- デフォルトのimageio付属Linux FFmpeg 7.0.2: avgblur_opencl、unsharp_opencl、h264_nvencは非搭載。CPU効果/CPUエンコード判定。実行したレンダーJSONでもGPU効果attempted/confirmed=falseと整合。
- システムFFmpeg 7.1.5: avgblur_opencl、unsharp_opencl、h264_nvencは搭載。OpenCL 1フレーム検査は平台なし(-1001)で終了237。NVENC 1フレーム検査はlibcuda.so.1をロードできず終了255。
- それでも現行backend_nameの表示は`NVIDIA NVENC + CPU Effects fallback`。搭載の有無と実際に使えるかの混同をこの環境で再現できた。
- Windowsの実際のFFmpeg・ドライバー・デバイス・ログがないため、GTX 1070 TiでのCPUフォールバックの直接原因は未確定。最有力はアプリ使用FFmpegのOpenCLフィルター欠落。Bloom/DOFについてはそもそも現行GPU対象ではない。

詳細と次の修正順序は`CODEX_GPU_ANALYSIS_JA.md`を参照。今回の監査をGPUエフェクト導入完了や高速化成功と扱わない。

## 変更一覧と成果物

追加したGit管理ファイル:

- `docs/CODEX_ARCHITECTURE_JA.md`
- `docs/CODEX_GPU_ANALYSIS_JA.md`
- `docs/CODEX_LOCAL_DEVELOPMENT_JA.md`
- `docs/CODEX_AUDIT_RESULTS_JA.md`

元ZIPの全非診断ファイルについて、内容がバイト単位で一致することを再確認した。既存ソース/UI/カメラ/音声/テスト/requirements/.gitignore/文書に差分はない。Gitメタデータ、ignored .venv/pycache、診断出力、ワークスペース外部のセットアップhelperは作業に必要なローカル成果物。

生の実行証拠はクラウドの`/workspace/.onboarding-results/autocine/`に保存。総合ログ、pytestログ、GUIログ、能力検査JSON、プレビュー原因JSON、導入パッケージ一覧、インストール/再実行ログを含む。これらはGitへコミットせず、ローカル移行ZIPにも含めない。

## 次に進める範囲

ローカルGitで現状を保持し、Linuxでソース編集・モック回帰を実行できる開発基盤は用意できた。全既存テスト成功やWindows本番動作はまだ確認できていない。

次の第一候補は、**GPU能力と実行結果を分ける診断の小規模修正**。その後にWindows実機の1フレーム検査、Focus Blurのみの段階採用、Bloom/DOF個別評価へ進む。既存カメラ、LoL専用音声、UIレイアウトの全面改修は行わない。クラウド設定は保存済みドラフトであり未公開。ユーザーがクラウドで再利用する場合は環境設定を確認・保存して公開する。手元で継続する場合は付属Git bundleとWindows手順を使う。
