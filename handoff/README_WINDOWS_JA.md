# v5.10.27-test カメラ修正候補

**LoL_AutoCine_v5.10.27_CameraAxes_GPUFull_Windows_Full.zip** をGitHubで開き **Download raw file**。旧版と別フォルダーに展開しLoL_AutoCine/START_GPU.bat。環境Publish/mainマージは不要。

版: 5.10.27-test / カメラfingerprint: d24f6d6fa573b4e2 / ソースHEAD: 1804a72d83e64bed5ec21803eda6b6954efbc2da。

同じリプレイ・対象・イベントで「開発用：全カメラテスト・30MB ZIP」を1回押す。RED3/5の良好構図を最初に確認し、RED1の距離、RED2反転、RED4地形裏、BLUE6〜10の戦闘/被写体/追従を比較。結果の全part ZIP・results・診断を送る。実機合格はまだ宣言しない。詳しいチェックはdocs/WINDOWS_TEST_v51027_JA.md。

BLUEのFPSで水平回転354度付近を俯角Yへ送り、RED third_cinemaで約-192度のZロールを送っていた。BLUE全5種とRED2/4のみ、実際の送信offsetからX=水平回転/Y=俯角/Z=0の対象視線を計算し、遅いAPIの平滑化後も位置と視線を一致させる。RED1自動サイドだけ距離8%増加。RED3/5の位置/回転/FOV/speedは旧版の固定数値と一致。

10モードの設定/キャッシュ/視線方針を独立化。対象・モード・attachment・ゼロoffset・座標範囲が一致するtop/fps基準を再取得し、staleな他対象の世界座標で成功扱いにしない。録画/音声開始前に最終姿勢を確認し、未反映なら開始せず中止。QAにinitial_pose_checksを追加。UI/GPU22FX/NVENC/LoL専用音声/60fps/録画器/設定を旧版で上書きしない。開発用ボタン1つ、送信用だけ540p/各30MB以下を維持。

検証: Linux/Xvfb全853件成功、失敗/エラー/skip0、全89モジュールで全収集件数完了。10モード独立性/RED3・5固定数値/軸汚染/座標stale/初回未反映時の録画非開始/一枚だけの初期フレーム/低速APIを検証。Git担当ガード、UTF8、compile/pip check正常。全557tracked bytesで差分適用一致、ZIP CRC/SHA、全141ブランチbundle、旧配布物257件を保持。

実機受領164710全27動画をFFprobe計測・FFmpeg完全デコードし、カメラ10本の開始/イベント前後を抽出。Windows修正後の実構図は未確認。同一リプレイ・同じイベントでRED3/5保護とBLUE/RED2/4改善の再撮影が必要。共有Tk native crash原因とprogram_opencl不足は今回解決と扱わない。個人動画/座標ログ/診断ZIPをGitへ含めない。

新しい比較用Draft PR。main/PR29/42/43へマージしない。Windows手順: LoL_AutoCine/docs/WINDOWS_TEST_v51027_JA.md。

CI: https://github.com/Aimin2222/agdhnteweeffewwff/actions/runs/38372750998 — Linux853件/Windows79件、失敗・エラー・skip0。Windows実widget開発ボタン1個。ZIP SHA/CRC正常。CI対象は固定payload86443c9738f5a2279524536a34515b16fe7e7e31。全ソース557/141refsの別フォルダー復元一致、復元58テストとTk成功、再セットアップ後も個人設定/プロジェクト/診断を保持。環境draft revision46保存/読戻し一致、Publishなし。Draft PR44未マージ。
