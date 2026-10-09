# v5.9.0 SceneStudio UI統合・引き渡し記録

## 取り込んだ変更

ChatGPT側の `LoL_AutoCine_v5.9.0_SceneStudio_UIOnly.zip` の15ファイルを確認し、
UIブランチへ取り込んだ。既存と同じ4ファイルは変更にならず、追加・更新は11ファイル。
別途 `VERSION.txt` を `5.9.0 SceneStudio UI Integration` に更新した。
ZIPのSHA256は `b13d9b2409c920ebc5fbad92d30571e9f8b2c82c9dde5eddbe3c261b0ff9a4f5`。

- `legacy_app.py`: シーン別設定・保存・Undo/Redo・スマート自動編集の接続。
- `ui/scene_project.py`: ショット設定、JSON保存、自動保存、変更履歴。
- `ui/scene_batch.py`: 既存 `run_auto_edit` をシーンごとに呼ぶ任意のアダプター。
- `ui/motion_graph.py`: 既存CameraPlanから計算するグラフ。実ゲーム映像のプレビューではない。
- 新規SceneStudioテスト2ファイルと日本語仕様・設計・統合・実機テスト文書。

シーン別モードは初期状態でOFF。OFFでは従来の `run_auto_edit` を直接呼び、
隣接キルのグループ化を維持する。ONでは1シーンずつ書き出すため、隣接キルも別クリップになる。
自由キーフレーム編集、シーン並べ替え、サムネイル、GPUエフェクト高速化は今回の変更に含まれない。

## 保護したファイルとGit

`core/` 全体、`app.py`、`requirements.txt`、Windows起動バッチ、Native Audio Helperを
v5.8.5基準およびGPUブランチと比較し、変更がないことを確認した。
GPU実装の修正はまだ行っていない。NVENC使用をGPUエフェクト実行と扱わない。

| ブランチ | 役割 |
|---|---|
| `baseline/v5.8.5`, `stable/v5.8.5` | 元ZIPの比較基準 |
| `codex/initial-audit` | 初回の構造・テスト・GPU監査 |
| `feature/ui-editor-v586` | 前回UI差分を保持 |
| `feature/ui-scenestudio-v590` | 今回のUI差分。元ZIPのソースを維持 |
| `feature/gpu-engine` | GPU側作業とGit衝突検出ツール |
| `integration/v5.8.6` | 前回の統合結果を保持 |
| `integration/v5.9.0` | 今回の統合結果 |

Codex側で衝突検出ツールに新規SceneStudioテストの所有者を追加した。
実際の分岐Git履歴を作るテスト11件により、担当外変更、共有API変更、競合、
統合後のGPU巻き戻しを検出できることを確認した。
新しいUIブランチはCLIの既定値ではないため、明示する。

```sh
cd /workspace/LoL_AutoCine
.venv/bin/python tools/check_parallel_integration.py --ui feature/ui-scenestudio-v590
.venv/bin/python tools/check_parallel_integration.py --ui feature/ui-scenestudio-v590 --integration integration/v5.9.0
git status --short
```

ガードはコミット済みの先端を比較する。未コミットの変更は別途確認する。
実行結果は競合なし・担当外変更なし・統合先のGPU/UI巻き戻しなし。

## 検証結果

- SceneStudio、GUI契約、既存UI、機能保持、OrbitTargetLock、全キル安全性、既存FFmpeg回帰、Git衝突検出: **33件成功**。
- `tests/test_checked_dispatch.py`: App起動、チェック済みシーンの従来経路、二重起動防止が成功。描画部分はスタブ。
- Python構文: 48ファイル成功。`pip check`: 依存関係の不整合なし。
- 実FFmpegとモックReplay API・合成映像・合成音声を使った機能検証: シーン別ONでは2クリップとモンタージュ、OFFでは隣接2キルを1クリップへグループ化。すべて1080p、約60fps、カラーとAAC音声を確認し、映像・音声の長さ差が0.3秒未満。対象プレイヤーと元Templateの保持も確認。

10fpsに落とした予備検証では、1クリップの映像3.300秒に対し音声3.655秒となり、
0.3秒未満の条件に失敗した。低fpsでの末尾・時間同期は追加調査事項。
60fps試験の最初の「平均fpsが文字列 `60/1` と完全一致」という条件は、mux後の約59.982fpsを
不適切に失敗としたため、既存の総合テストと同様に数値誤差1fps未満の確認へ修正した。
アプリのコードや既存テストのassertは変更していない。

v5.8.5監査時の総合runnerの5失敗（音声WAV不足4件・小さい静止画とBloomのサイズ不一致1件）と、
GUI通し試験のCPU環境240秒タイムアウトは既知の未解決事項。今回、同じ高負荷テストを再実行していない。
Windows、実LoL、GPU、LoL専用Native音声の実機動作は未検証。
生ログは `/workspace/.onboarding-results/autocine/` にあり、Gitへ追加していない。
自動保存の `projects/`、個人設定、診断ログ、録画、音声はローカル除外する。

## Windowsへの取得と保存先

作業元は `/workspace/LoL_AutoCine`。これはZIPから作成したローカルGitでremoteがない。
クラウドの選択済みGitHubリポジトリ `Aimin2222/agdhnteweeffewwff` は別の静的サイト。
ユーザーの「接続済みなら新しいブランチとPR」という追加依頼に基づき、
専用ブランチの `LoL_AutoCine/` サブフォルダに追跡済みソースのコピーを保存する。
既存サイトのファイルやmainへのマージは行わない。元の全8ブランチはGit bundleで同梱する。
GitHubの保存・PR作成は各操作の結果で判定し、成功するまでは保存済み・PR作成済みと扱わない。

生成ZIPのチャット内リンクは利用できていない。GitHubへ保存できた場合は、そのブランチページで
「Code → Download ZIP」またはWindowsのGit cloneを使う。
GitHubへ保存できない場合、利用可能な代替はチャットへ差分・ファイル本文をテキストで掲載し、
PC側で保存すること。この実行環境には生成ファイルをチャット添付へ登録するツールがない。
クラウドのローカルファイルだけを永続保存・PCへの取得完了と扱わない。

今回のUIOnly ZIPは単体起動できない。手元のv5.8.6 Fullなどの完全なプロジェクトに重ねる。
GPUコードの古い全体ZIPをCodex作業へ上書きしない。アプリのUIソースは受領ZIPと同じで、
Codex固有の追加は監査文書、衝突検出ツール・テスト、VERSIONメタデータ。

## 今後のCodex側の開発順序

1. GPUとエンコーダーを実行プローブで区別し、失敗理由を診断ログに残す。
2. NVENC初期化失敗時のCPUエンコーダー再試行と、最終ファイルの成功判定を小差分で整える。
3. 対応する効果のGPU経路、色保持、音声同期を実機・非対応環境で検証する。
4. 正常経路とフォールバック経路の同条件ベンチマークを比較する。

共有APIの変更はUI側との接続点をレビューし、並行ブランチの所有者ガードと回帰確認を続ける。
