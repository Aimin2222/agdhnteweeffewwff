v5.9.1のモンタージュ順序編集と、v5.9.2のキーフレーム・シーン別FX・手動サムネイルを、前回の取得用ブランチへ統合します。Windowsではこのブランチの「Code → Download ZIP」から完全な `LoL_AutoCine/` を取得できます。

GPUエフェクト処理本体・録画・LoL専用音声を維持し、Templateへの設定追加とレビュー済みのカメラ接続だけをcoreへ取り込みました。空キーフレーム時の従来FOVと旧位置引数を保つ小修正も加えています。共有APIレビューはGit blobハッシュで限定し、後続変更や統合後の巻き戻しを検出します。

検証: pytest全67件、Python構文51ファイル、旧カメラ168条件比較、GPU処理本体のAST一致。実FFmpeg・モックAPI・合成映像/音声で、逆順2クリップ＋モンタージュ、キー・個別FX、従来の隣接キル結合を1080p/約60fps/カラー/AAC音声で確認しました。Windows・実LoL・実GPU・Native録音は未検証です。旧総合runnerの既知失敗は別途記録を維持しています。

追跡済み144ファイルと全11ブランチのGit bundleを同梱し、復元後のコミット・ソース一致を確認しました。個人設定・診断ログ・録画・音声・.venvは含めていません。詳細は `LoL_AutoCine/docs/CODEX_INTEGRATION_RESULTS_v5.9.2_JA.md`、取得手順とGit状態は `handoff/` にあります。

比較先は既存の `codex/lol-autocine-v590-handoff` です。そのブランチに追加されていた変更と前回bundleを保持します。mainへのマージは行いません。受領UIのウィンドウタイトルはv5.9.0のままで、実際のバージョンはVERSION.txtのv5.9.2です。
