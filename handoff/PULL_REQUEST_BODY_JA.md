開発QAを未接続/未スキャンから1回で開始できるようにし、UI snapshot→1ワーカーで接続・全体scan・QA撮影・演出/画像・直接ZIPを連続実行。complete cache再利用、二重押し抑制、partial/失敗/停止時は録画しない。既存通常出力/開発bundle/ミラー応答を保持。

2 BATをASCII化しPython UTF8環境と失敗終了コードを保持。tracked UTF8 auditを追加し、受領root.parent基準をGit root基準へ補正して単体/配布内Git双方で個人ファイルを読まず検査。

QA_Supportへ読み方と指定6診断の末尾各最大1MBを元バイトのままコピー。source不変/symlink除外/失敗で成功録画を無効化しない/中止時追加しない。既存ZIPが.logを除外したため、QA_Support直下の既知名・1MB以下だけ許可。1MBstream/500MB/元動画・JSON・旧ZIP/別名再出力/最終JSON一致/直接ZIPを保持。時間割合サンプルを実キル時刻自動認識と表示しない。外部送信なし。

受領RED1/3/5・BLUE8の引き構図と限定角度は試験候補。RED2/4/BLUE7/9を保持。FPS高さと手動0/180、有限値/倍率制限、キャッシュ分離/TargetLock/ディレクターgain/APIを維持。実構図とZ角の見え方はWindows未確認。

受領指定v15基準へ独立apply --check/適用し、受領v21の15パス差分だけ現行Codex v21へレビュー統合。旧GPU全22FX/60fps/LoL専用音声/録画/NVENC/診断/fallback/37PNG/111refs/202旧配布物を保持、全115refs bundleと共有8blobレビュー。エフェクト/録画/音声の本体はbyte不変。添付の実機/CI612件/Release記述は受領側資料として区別。

検証: Linux/Xvfb全719成功（失敗/skip/除外なし、60.969秒）。関連初回63成功/1失敗で.log除外を検出し修正、追加チェック含む65成功。実workerでTk snapshot/二重押し、cache/partial/stop、1MB tail原本不変/ZIP内ログと最終JSON一致、FPS height/manual、単体・nested Gitでignored不正UTFファイルを監査しないこと、旧GPU/UI/音声/ZIP回帰を確認。完全ZIP CRC/ソース一致/差分apply/個人ファイル除外/旧refsと配布物保持を検証。Windows/NVIDIA/LoL画角と日本語BAT実行は未確認、過去native終了原因は未確定。

前回v5.10.21を比較先とするDraft PR。mainへマージしません。完全ZIP→Download raw file、別フォルダSTART_GPU.bat。実機手順docs/WINDOWS_TEST_v51022_JA.md。
