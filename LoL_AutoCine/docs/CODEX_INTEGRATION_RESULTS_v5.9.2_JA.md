# v5.9.1 / v5.9.2 安全統合の結果

## 取り込み元と変更範囲

- v5.9.1: `LoL_AutoCine_v5.9.1_Codex_UI_Changes.zip`。SHA256 `522c2763b95509ff52de13e9ef2151a744491ef9ea6bac4b388a2092505c48b3`。
- v5.9.2: `LoL_AutoCine_v5.9.2_Codex_MergeChanges.zip`。SHA256 `d33f1f7fdeb7cb56027f0628023162db5520705aaf3784fd30ae613f1d9f1741`。

前回の `integration/v5.9.0` を保持し、順番にパッチの `git apply --check` を実行した。
v5.9.1はUI・シーン順序、v5.9.2はUI・キーフレーム・シーン別FX・手動サムネイルを取り込んだ。
受領ZIPのUIソースと適用後ファイルのバイト一致を確認した。
v5.9.2は全体を上書きせず、UIとcoreのパッチを分けて適用した。

`feature/ui-sequence-v591` と `feature/ui-keyframes-v592` に受領UIを保存した。
共有APIとGPU設定フィールドの追加はCodex側でレビューし、`feature/gpu-engine` へ保存した。
両方を `integration/v5.9.2` へGit mergeで統合した。旧基準・旧UI・旧統合ブランチは削除していない。

## 共有APIの互換性と保護対象

`core/effects.py` はTemplate末尾の `scene_keyframes` フィールド追加のみ。
フィールドを除いたAST全体がv5.9.0と同一で、FFmpeg・GPUエフェクト・エンコード処理本体は変更していない。
`core/jobs.py` はキーフレームをCameraPlanへ渡す接続だけを追加した。
`core/camera.py` は検証済みのキー値を既存のキャラクター中心Orbit・距離・FOVに加える。
座標系、最低高さ、対象プレイヤーの保持、非三人称の挙動を保護する。

受領コードに対し、従来の互換性を保つ小修正を2点加えた。

1. TemplateとCameraPlanの新フィールドを末尾へ移し、旧位置引数を保持した。
2. 空キーフレーム・非三人称では従来のFOVをそのまま返す。新しい32〜100度制限はキー有効時だけ適用する。

GPUランタイム、録画、キャプチャ、音声・Native Helper、スキャナー、起動バッチ、依存宣言は前回から無変更。
GPU高速化を今回実装したとは扱わない。詳細は `CODEX_SHARED_API_REVIEW_v5.9.2_JA.md` を参照する。

## 検証結果

- **`pytest tests` 全67件成功**。Xvfb上でGUIも実行した。
- Python構文51ファイル成功。`pip check` 成功。
- キーフレームなしのカメラをv5.9.0と168条件で比較し、FOV・速度・スケール・Orbit・回転が一致することを確認した（座標の浮動小数誤差は1e-8未満）。
- Gitガード21件成功。担当外変更、共有API変更、競合、古いGPUへの巻き戻しに加え、共有APIレビューの古いハッシュ・別担当の変更・未レビューの別API・統合後の共有ファイル巻き戻しも検出した。
- 実FFmpeg・モックReplay API・合成映像/音声で新旧両経路が成功。
  - ON: 検出時刻と逆順の2シーンを出力し、同順のモンタージュを作成。キーフレームが実際のCameraDirectorへ渡ることを確認した。
  - ONの1シーンへ色温度0.2、Bloom0.12、Focus Blur0.05、DOF0.5を指定して書き出した。
  - OFF: 同じ隣接2キルを従来どおり1クリップへ結合し、個別順序・キーフレームを使わないことを確認した。
  - 全4出力が1080p・約60fps・カラー・AAC音声付き。非無音の音声を復号して確認し、映像と音声の長さ差は最大約0.039秒だった。
  - 対象プレイヤーと元Templateの保持を確認した。

生ログ・合成録画・音声・個人プロジェクトはGitへ追加していない。
証跡は `/workspace/.onboarding-results/autocine/v592-*` に保存した。
Windows、実LoL、実GPU、LoLプロセス専用Native録音は未検証で、合成音声の成功と区別する。
旧総合runnerの5失敗・旧GUI通し試験の240秒タイムアウト・10fpsの末尾差は今回の修正対象ではない。
変更していない高負荷の旧総合runnerは再実行していない。詳細はv5.9.0監査記録を参照する。

## Gitによる衝突検出

共同レビュー対象の `core/camera.py` と `core/jobs.py` は、レビューJSONに基準・担当・Git blobハッシュを保存した。
指定した内容だけを承認し、後続変更は再レビューを要求する。UI所有者の境界は変更しない。
レビューJSONなしでは共有変更を検出して終了1になる。

```sh
python tools/check_parallel_integration.py --ui feature/ui-keyframes-v592 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.9.2.json
python tools/check_parallel_integration.py --ui feature/ui-keyframes-v592 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.9.2.json --integration integration/v5.9.2
git status --short
```

前後のガードで競合・担当外変更・GPU/UI/共有APIの巻き戻しがないことを確認した。
ガードの対象はコミット済み先端なので、未コミットの変更も別途確認する。

## Windowsへの取得と実機確認

保存元は `/workspace/LoL_AutoCine`。全11ブランチをGit bundleで保存する。
前回の取得用GitHubブランチへ他の変更が追加されていたため、最新の前回ブランチを基準に
新しい `codex/lol-autocine-v592-handoff` を作る。前回版とその変更を上書きしない。
PRの比較先は前回の `codex/lol-autocine-v590-handoff` とし、mainにはマージしない。
push・PR作成は各操作の成功を別々に確認する。

Windows PCではGitHubの新ブランチの **Code → Download ZIP** から取得し、
展開した `LoL_AutoCine/` を別フォルダで使う。`handoff/README_WINDOWS_JA.md` に履歴復元手順を保存する。
チャット内の生成ZIPリンクは使わない。依存とNative Helperは従来の起動・構築手順を維持する。

受領 `legacy_app.py` のウィンドウタイトルは `v5.9.0` のまま。UI所有者の元ソースを維持しており、
今回の実際のバージョンは `VERSION.txt` のv5.9.2とこの統合記録で判別する。
サムネイルは現在のミラーフレームを手動保存するもので、自動撮影ではない。
保存済み画像はJSON外の `projects/thumbnails/` にあるため、利用者のPC間移行時は画像もコピーする。

実機では、シーン別OFFの1シーン、ONの並べ替えた2シーン、キーによるカメラ追従、
FXを1種類ずつ、LoLだけの音声・同期・カラー、JSON v1/v2の読み込み、Undo/Redo、サムネイルを確認する。
問題時は診断ZIPを取得し、実施した操作番号と合わせて共有する。GPUの今後の作業は、
実行プローブと診断の正確性、NVENC失敗時の安全なCPU再試行、個別効果の段階的最適化の順に進める。
