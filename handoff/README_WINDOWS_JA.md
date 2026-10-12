# v5.10.23-test Framing / Reference / GPUFull

完全版 **handoff/LoL_AutoCine_v5.10.23_Framing_Reference_GPUFull_Windows_Full.zip** をGitHubで開き **Download raw file**。または **codex/lol-autocine-v51023-framing-reference-handoff** の **Code → Download ZIP**。旧版と別フォルダへ展開してLoL_AutoCine/START_GPU.bat。Windows取得にmainマージ/環境Publishは不要。

RED1のZ+3を外しX+4、RED FPS固定42度と追加biasを除き実offsetからpitch+3（18〜52に制限）。fps_back1.60/高さ/手動0・180を保持。RED2/4/5の数値不変。BLUE各第三者距離1.10/1.08/1.08/1.08、FPS back1.38に引く受領候補。キャッシュ分離/TargetLock/ディレクターgain/APIを維持。実画角改善はWindows未確認。

参考BATは.venv/venv/PATH python/py -3からPIL/imageioをimportできる候補を選択。ダブルクリックで動画→フォルダ選択、全部cancelは比較出力なし、ドラッグ単体/フォルダとZIP展開案内も保持。ASCII/UTF8/unbuffered、Python直後のstatus保存、TEMP/diagnosticsログ。Python不足/入力不在/ZIP指定にも今回ログを残す。helperは日本語stemを保持して別動画を同じreference出力へ上書きする候補を修正、picker parent/root解放、元動画/空フォルダ/前回Path補正を保持。静止比較はCPU、通常GPU加工経路外、外部送信なし。

reference_review_latest.logをQA_Supportの既知7ファイルへ追加、各1MB末尾原byteコピー/元ログ不変/symlink除外。前回ワンクリックQA/complete cache/partial・二重押し・stop/1MBstream・500MB直接ZIP/最終JSON一致/元動画・JSON・旧ZIPを保持。3時点は時間割合で実キル/主役AI判定ではない。

GPU全22FX/60fps/LoL専用音声/録画/NVENC/選択policy/診断/CPUfallback/ミラー応答を保持、effects本体byte不変。Linux/Xvfb全739成功、失敗/skip/除外なし、63.704秒。関連76件成功。日本語名の実60fps MP4から6時点画像/JSON/ZIPと原本不変、picker lifecycle/別出力/relative pitchと手動/高さを確認。Windows/LoL画角・BAT候補選択・日本語パス・NVIDIA速度は未確認。過去native139/132は原因未確定、成功を恒久修正と扱わない。

完全ZIP515ファイル、差分適用後517ソース一致、全119refs bundle（binary属性でWindows改行変換を防止）。差分基準は前回Codex v5.10.22-test。実機手順LoL_AutoCine/docs/WINDOWS_TEST_v51023_JA.md。

## ローカルGit復元
```sh
git clone --single-branch --branch codex/lol-autocine-v51023-framing-reference-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v51023_Handoff
git clone --branch integration/v5.10.23 LoL_AutoCine_v51023_Handoff/handoff/LoL_AutoCine_v5.10.23_Framing_Reference_GPUFull_all_branches.bundle LoL_AutoCine_v51023_Dev
cd LoL_AutoCine_v51023_Dev
git branch feature/gpu-cameraqa-v51023 origin/feature/gpu-cameraqa-v51023
git branch feature/ui-cameraqa-v51023 origin/feature/ui-cameraqa-v51023
git status --short
```

全refsはorigin/*へ復元、originはローカルbundle。設定/録画/プロジェクトを保管。担当ガードはdocs/CODEX_INTEGRATION_v51023_JA.md。
