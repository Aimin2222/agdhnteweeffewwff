# 検証結果と限界
- Node共有モデル：85/85 PASS。6外観組合せ×8viewの保存roundtrip、scene独立、Undo/Redo、clamp、キー、style/motion等。GUIやLoL試験ではない。
- WebView2のDOMイベント：19/19 PASS。実HTMLコントロールのhandlerへ合成eventを与え、FOV/数値/表示、theme/variant保持、side/seek、キー/補間、Undo/Redo、scene独立、grade/split、素材、出力無効、modal焦点、70検索を確認。native pointer/keyboard/IME試験ではない。
- WebView2自己テスト：10/10 PASS。8モデルassertion＋2 DOM確認。上記モデル試験と重複があるため合算独立件数にしない。
- 自作画面：20/20実寸PASS（18枚1920×1080、2枚1366×768）。CapturePreviewで取得。画像を後から引き伸ばして解像度を偽装していない。DPR1/本文横overflowなし/16:9 previewを実測。
- 機械PNG decode/hash/JSON整合/70ID一意/外部第三者画像なし/ZIP展開は納品QAで別記録。

現在環境はNATIVE_ENVIRONMENTを参照。参照2アプリ起動、実LoL、録画/音声/GPU、native入力の網羅、ファイルdialog、再起動永続化の実process間完全比較、別PC、複数DPI、全既存機能の実行はNOT_RUN。前工程のP2残523等は未完のまま。

native UIは起動/表示を確認したが、ウィンドウ状態変化等でpointer入力の自動試験を完了できなかった。IABのfile URL表示はポリシーで拒否され未実施。撮影/DOM検証は元々設計した独立オフラインWebView2ホストのQA機能で行った。IABの拒否を回避するproxyやbrowser設定変更は行っていない。

初回撮影の1920幅はWindows枠制約で高さ1061だったため不合格とし、描画controlのサイズを明示して1920×1080を再取得した。旧画像を成功数へ含めない。現在の20枚だけを配布する。実製品DPI問題が解消したという意味ではない。
