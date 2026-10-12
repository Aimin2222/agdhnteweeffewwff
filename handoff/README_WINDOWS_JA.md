# v5.10.22-test OneClick / UTF8 / QA / GPUFull

完全版 **handoff/LoL_AutoCine_v5.10.22_OneClick_UTF8_QA_GPUFull_Windows_Full.zip** をGitHubで開き **Download raw file**。または **codex/lol-autocine-v51022-oneclick-utf8-qa-handoff** の **Code → Download ZIP**。旧版と別フォルダへ展開してLoL_AutoCine/START_GPU.bat。Windows取得にmainマージ/環境Publishは不要。

開発QAはUI snapshotから1ワーカーで接続→全体scan→撮影→画像・演出→直接ZIP。complete cache再利用、二重押し/partial/失敗/停止を処理。既存通常出力と開発bundleも保持。MAKE_REFERENCE_SHEETS/RUN_AUTOTESTをASCII、Python UTF8環境/終了コードを保持。auditは単体/配布内Git双方でtracked sourceだけ確認し個人未追跡ファイルを読まない。

QA_Supportに読み方と指定6ログ末尾各最大1MBを元バイトでコピー。元ログ不変、symlink除外、書込失敗で録画を無効化しない。中止でsupport/ZIPは開始しない。既知名かつ1MB以下のQA_SupportログだけZIPへ含める。1MBstream/500MB上限/元動画・JSON・旧ZIP/再出力別名/最終JSON一致を保持。時間割合3時点で実キル/主役のAI判定ではない。外部送信なし。

RED1距離1.13/Z+3度、RED3 FPS back1.60/X-4/Y+4、RED5 geo距離1.12/X-4、BLUE8 FPS back1.22は受領試験値。RED2/4/BLUE7/9の数値を保持。FPS高さは倍率と別、手動0/180は自動angle biasを外して保持。キャッシュ分離/TargetLock/ディレクターgain/旧APIとTemplate任意Noneを保持。実構図・傾き改善はWindows未確認。

GPU全22FX/60fps/LoL専用音声/録画/NVENC/選択policy/診断/CPUfallback/ミラー応答を保持、描画本体はbyte不変。Linux/Xvfb全719成功、失敗/skip/除外なし、60.969秒。関連初回63成功/1失敗は.logがZIPから除外されたため修正、追加チェック含む65成功。その後全件で確認。Windows/LoL画角・日本語パス/BAT実行・NVIDIA速度は未確認。過去native139/132は原因未確定、成功を恒久修正とは扱わない。

完全ZIP506ファイル、差分適用後508ソース一致、全115refs bundle（binary属性でWindows改行変換を防止）。差分基準は前回Codex v5.10.21-test。実機手順LoL_AutoCine/docs/WINDOWS_TEST_v51022_JA.md。

## ローカルGit復元
```sh
git clone --single-branch --branch codex/lol-autocine-v51022-oneclick-utf8-qa-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v51022_Handoff
git clone --branch integration/v5.10.22 LoL_AutoCine_v51022_Handoff/handoff/LoL_AutoCine_v5.10.22_OneClick_UTF8_QA_GPUFull_all_branches.bundle LoL_AutoCine_v51022_Dev
cd LoL_AutoCine_v51022_Dev
git branch feature/gpu-cameraqa-v51022 origin/feature/gpu-cameraqa-v51022
git branch feature/ui-cameraqa-v51022 origin/feature/ui-cameraqa-v51022
git status --short
```

全refsはorigin/*へ復元、originはローカルbundle。設定/録画/プロジェクトを保管。担当ガードはdocs/CODEX_INTEGRATION_v51022_JA.md。
