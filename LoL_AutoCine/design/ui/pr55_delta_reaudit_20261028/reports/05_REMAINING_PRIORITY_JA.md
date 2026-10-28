# 残る差分の優先順位

1. **P0 / R2-01の小画面**：1366×768のプレビューと下段が重なります。`.timeline`の170px指定より後に強いln固有270pxがあり、上下領域が収まりません。サイズ別に下段高・左余白・grid rowを定義して再撮影。根拠：[CSS](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/reference_views.css#L29)。
2. **P1 / R-04のYaw結線**：画面はv.third_yを読む一方、snapshotはthird_yawを返します。undefinedがnumberControlで0になるため、回転角が0へ戻る構造です。v.third_yawへ合わせ、32°などの非ゼロでタブ/再描画/状態を検査。根拠：[LoL_AutoCine/ui/reference_views_v2.js:41](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/reference_views_v2.js#L41)、[LoL_AutoCine/ui/audit29_runtime.py:159](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/audit29_runtime.py#L159)。これはソース上の結線不一致で、Workの実操作再現はNOT_RUN。
3. **P0 / R-01**：追加した既存キー編集を維持し、同じ評価式から曲線/値目盛/選択点を描きます。絶対値へ勝手に変換しません。
4. **P0 / R-02・R2-02**：比較は未実装と明示継続。対象チェックは実シーンで独立性を試験。空のダイアログ開閉だけで合格にしない。
5. **P1 / R-05・R-07・R-03**：既存露出/LUTの接続と保存スコープを決め、原画の色ルック/簡単カード/出力情報階層へ戻す。異なる能力を同名にしません。
6. **P1 / C3-02・05・04・03**：3タブ展開・カードの説明/画像・原画の字形/余白を差分修正。4スライダーが無いという古い修正指示は繰り返しません。
7. **R-09・R-11・R-12**：時刻/倍率を実データへ接続。入力ガードとfps/encoder修正は残し、IMEや長時間・非ゼロ値で独立操作を確認。

これは前回26IDの下位残件です。R2-01/COMPACT、R-04/YAWを付随させ、別の26件へ作り直していません。今後の修正はUI3表示層/必要なアダプターに限定し、本体のカメラ計算・正式素材・承認状態をこの監査中に変更するものではありません。
