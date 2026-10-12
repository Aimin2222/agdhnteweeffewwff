# LoL AutoCine v5.10.24 — カメラ中央固定・参照動画ZIP直接読込・自動QA

## 何を確認したか
- ユーザーが2026-10-12のCameraQA_20261012_203223について送付したRED/BLUE比較画像、切替比較画像と`results(8).json`では全10種類を出力できた。ただしRED 1（画面の右寄り）、RED 3（右端のわずかな被写体）、BLUE 6 PRE（構図不満）が残る。
- `results(8).json`のRED 1 は`initial_camera_offset=[325.26,884.66,927.11]`、回転X=-188°。そこから主役へ向く幾何学方位は約-161°。RED 3は`initial_camera_offset=[399.75,713.60,1281.16]`、回転X=-192°、幾何学方位は約-163°。約27〜29°の食い違いを認めた。カメラが主役を画面端に置く原因となり得る。
- RED 2・4・5は画角良好とのユーザー評価なので、その固有設定を変更しない。BLUE 6のPREにはなお画質・画角レビューが必要。
- `results(8).json`のvideo anomaly validatorはRED 1とBLUE 6にbaseline camera stale可能性を表示。一方でRED 3をフラグなしと判定しているため、数値検査の漏れ（向きの差）を修正対象とした。
- ユーザー提供`reference_review_latest(1).log`には29本の動画を処理し、`x_media_all_merged\\_AutoCineReferenceReview\\ReferenceReview_contact_sheets.zip`を作成した成功記録がある。ログに文字化けした名前が見えるが、BATの実行失敗を示していない。
- このチャットのPythonとコンテナはClientError/InvalidArgumentErrorのため、当該3つのQA ZIPから生MP4を直接取り出せなかった。これはGitHubのリポジトリ容量不足やユーザーMP4の破損を証明するものではない。比較画像およびJSONと過去の実機レポートに基づいた改修である。

## 実装
### カメラ
`core/camera_tuning.py:target_center_rotation(offset)` は主役からカメラへの世界座標相対位置 (dx,dy,dz) を入力し、RED側の確立されたEuler軸（X=水平方位、Y=下向き仰角、Z=0）で幾何学的な「主役を見る」回転を返す。水平方位はatan2(-dx,-dz)、俯角はatan2(dy,hypot(dx,dz))。不正・非有限のオフセットは拒否。画角が確定した他のRED構図には適用しない。
- RED #1（通常3人称）: 固定Heading+小幅なYawバイアスに代え、実カメラの相対位置から回転を計算する。これに伴い手動X+4°補正を削除。
- RED #3（FPS風）: 以前の固定約-192°回転は、実位置ベクトルが約-163°を要求する時に右端を向く。実際の補正後オフセットからX/Y回転を同時に求め、キル前・中・後の各フレームで同じ座標系を共有。距離1.60倍は既存値を維持。
- RED #2/#4/#5: 既存の距離/角度/カメラ方式を変更しない。
- BLUE #6〜#10: 今回は固有パラメータ・追従方式を変更しない。BLUE 6 PREは比較画像と実動画で優先検証し、他モードを巻き込む変更を避ける。
- カメラエンジン、Replay API、TargetLock、音声、GPU/NVENC、60fps、HUDはそのまま。カメラ方式/サイドごとの設定と新規planの内部フラグで修正範囲を限定。
- `CAMERA_QA_POSE`に幾何学回転とRED中央固定ON/OFFを追加。これにより本番カメラがどの方向を向く設定だったか後から数値確認できる。幾何学的中央一致と実映像でチャンピオンが中央に映ることは別であり、Windows実機確認必須。

### 参考動画解析BAT
- 既存のMP4/MOV/MKV/WEBM単体および動画フォルダーに加え、**動画を含むZIPを直接ドラッグして使用可能**。ZIP内では有効な動画拡張子のみ、最大120本、各1GBまで・合計4GBまでを一時展開し、終了後は掃除する。ZIP内のパスを使わず安全なファイル名を生成して展開し、オリジナル名の対応表`reference_archive_names.json`を出力ZIPへ同梱。
- 不正ZIP・動画の入っていないZIPは理由を表示してエラー終了（正常な参照ZIPと区別）。
- 成功時には比較画像ZIPの**フルパスを表示し、CI以外では保存先フォルダーを開く**。ファイルがどこに保存されたか分からない問題を減らす。
- PIL/imageio-ffmpegが使用できるPythonを優先し、文字化けしやすいBATソース本体はASCIIで維持。実行ログは`diagnostics/reference_review_latest.log`および`%TEMP%\\AutoCine_ReferenceReview_latest.log`へ保存。
- 既に日本語が文字化けした形で保存されたファイル名を、文字コード設定だけで自動復元する機能ではない。元ファイル名はZIP内部の対応表で照合する。

## Windowsでしてほしいテスト
1. [ ] v5.10.24フルZIPを**別フォルダーに展開**して起動する。
2. [ ] 右側の開発用ワンクリックテストを一度だけ押す。接続→全体スキャン→RED/BLUE動画・比較画像→最大500MB分割ZIPまで自動実行。
3. [ ] RED #1のキル前/中/後の主役が画面中央付近に映るか。斜め回転・画面の上下反転がないか。
4. [ ] RED #3のキル瞬間も主役と敵が見えるか（右端の欠け解消）。FPS風らしい視点が維持されているか。
5. [ ] RED #2/#4/#5が前回同様の構図か（最優先の退行防止）。
6. [ ] BLUE #6のキル前の画角が以前と同様か、最初のシーンで主役・敵が画面に映るか。他のBLUE #7〜#10が変わっていないか。
7. [ ] `MAKE_REFERENCE_SHEETS.bat`をダブルクリック→MP4を選択→結果の保存先フォルダーが自動で開くか。
8. [ ] MP4・動画フォルダー・動画を含むZIPをBATにドラッグしてそれぞれ比較画像ZIPが作られるか。
9. [ ] `x_media_all_merged`動画の比較画像ZIPは`_AutoCineReferenceReview\\ReferenceReview_contact_sheets.zip`にあるか。再生成の際に29本の処理が進むか。
10. [ ] 1080p/60fps、LoLゲーム音、GPU/NVENC、HUD、ミラー、既存37種キルフレーム・遷移FXが以前どおり。
11. [ ] 生成されたCameraQA全part ZIPとresults.jsonを共有。再発時は`diagnostics/reference_review_latest.log`も添付する。

## テストと配布
- `tests/test_v51024_red_center_zip_reference.py`でRED 1・3のカメラ相対幾何・角度同期、RED 2/4/5保護、ZIP内パストラバーサル阻止とZIPからの比較画像生成を検証。
- GitHub Windows CIで短いテストMP4/日本語パス/有効動画ZIP/壊れたZIPを確認。
- 全回帰テストと文字コード検査に成功した場合にのみWindows用フル版ZIP・Codex統合用差分ZIP（それぞれ単体で、二重ZIPなし）をReleaseへ配置。
- Codex差分は既存Codex v5.10.15のGPU Fullとの適用前差分レビューが必要。mainと元のCodexブランチは直接変更しない。
