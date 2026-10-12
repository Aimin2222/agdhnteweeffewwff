# LoL AutoCine v5.10.23: カメラと参考動画解析BATの修正・Windows実機テスト

## 状態と証拠
- 最新ユーザー送信の v5.10.22 比較画像とresults(6).jsonでは、RED2, RED4, RED5は良い／RED1は主役が右寄り／RED3は戦闘が画面上部に外れる／BLUE全体を引きたい、と報告された。
- QA結果にはCameraQA 10件、montage 3種、spatial transitions 6種、登場モーション6種、分割ZIP3件が存在。コードで生成成功しても画角の正しさは保証されない。
- ChatGPT側のcontainer・Python環境で添付MP4 ZIPがClientError/InvalidArgumentErrorになり、添付MP4は直接再生・解析できない。**GitHub容量超過やユーザーのZIP破損を原因と断言しない。** GitHub ActionsでソースとWindows BATのテストは可能。
- ユーザー添付の診断ZIPに今回直接アクセスできなかったので、BATクラッシュ原因はログを見た確定診断ではない。v5.10.23は複数の確実にあり得る原因への対策。

## カメラ設定
距離／回転の個別値は `core/camera_tuning.py` の (チーム, モード) キーごとに別々。CameraPlan、Replay API、録画エンジンは共有されるため、完全にプログラム別というわけではない。制御エンジンには単独のカメラモードだけを条件で適用する。

- RED #1 `third`：距離1.13は維持し、不要なZ軸3度ロールを削除、X軸+4度の小幅な中央寄せを試す。数値が実機で正しいかは未確認。
- RED #2 `third_cinema`：既存の距離・角度変更なし。保護。
- RED #3 `fps`：距離1.60倍は維持し、過去のX-4/Y+4度を消去。**固定42度の下向き角度を廃止し、相対カメラ位置のatan2から主役へ向くピッチを計算する。** 不要な大幅画角変更・静的補正を減らす。
- RED #4 `lolnam_cinema`：変更なし。保護。
- RED #5 `geo_aim`：変更なし。保護。
- BLUE #6/7/9/10：既存の距離倍率をそれぞれ1.10、1.08、1.08、1.08に引き上げ、角度補正値は現状維持。
- BLUE #8 FPS：後方距離1.22 → 1.38。角度補正は変更なし。
- BLUE #7など以前良かった構図が悪化する場合、まずモード単位で倍率を元に戻す。共通API制御を無条件に書き換えない。

## MAKE_REFERENCE_SHEETS.bat
ZIPである必要はない。MP4、MOV、MKV、WEBMファイルのドラッグ、あるいは動画フォルダーをドラッグする。ZIPを渡す場合は展開。BATをダブルクリックしても、動画ファイル／フォルダー選択ダイアログを開く。
- Windows CMDの誤解析を防ぐためBAT本体はASCIIのみ。
- 使用可能な候補（.venv、venv、PATHのpython、py -3）を一つずつ検査し、`PIL`と`imageio_ffmpeg`を実際にimportできるPythonだけを選ぶ。GitHub Windowsテストで `py -3` が別環境を指し、`ModuleNotFoundError: No module named 'PIL'` が再現したため、この検証を追加。必要なライブラリがどの候補にも無い場合はコマンドを案内する。
- Windowsの日本語フォルダー・ファイルパスも想定。成功時は元ファイルの隣に `_AutoCineReferenceReview_...`、フォルダーの場合は中の `_AutoCineReferenceReview` に比較画像ZIP。
- 失敗時に画面を閉じず、ログを `diagnostics/reference_review_latest.log` と `%TEMP%\AutoCine_ReferenceReview_latest.log` に保存してユーザーが送れるようにする。
- テスト用の短いMP4でBAT動作を確認するWindows CIとpytestを追加。**実際のxMedia動画を確認できたという意味ではない**。

## Windowsで確認してほしいこと
1. [ ] 別フォルダーにv5.10.23を展開、起動確認。
2. [ ] RED #2/#4/#5が以前と同等に見えるか。
3. [ ] RED #1の主役が中央に寄ったか。カメラ傾斜・上下反転がないか。
4. [ ] RED #3にキル前・瞬間・後の主役と敵が映るか。
5. [ ] BLUE #6〜#10が適度に後方から映り、キルの瞬間も見切れないか。
6. [ ] `MAKE_REFERENCE_SHEETS.bat`を**ダブルクリック**→MP4を選択して1本の比較画像ZIPが作れるか。
7. [ ] 続いてMP4ファイルをBATへドラッグし同じ結果になるか。
8. [ ] xMediaの動画が保存されているフォルダーをBATへドラッグして複数MP4の比較画像が作れるか。
9. [ ] BATが落ちる場合は `diagnostics/reference_review_latest.log` をそのまま添付。日本語の個人名・パスがログに含まれる場合は公開前に注意。
10. [ ] 開発用の「接続→全体スキャン→動画・画像→500MB ZIP」を試合スキャン前に1回実行して自動完了するか。
11. [ ] 音声・NVENC・HUD・ミラー・1080p60を確認。

## 配布
GitHub Releasesに単体のWindowsフルZIPとCodex v5.10.15差分ZIPを直接配置。ZIPの中のZIPは作らない。main/元のCodex PRの統合ブランチは変更しない。
