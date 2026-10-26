# テーマ・検査記録
ライト/ダークでP1/P2の配置は共通。配色はCOLOR_TOKENS_AND_CONTRAST.json、実寸はMEASURED_LAYOUT.json。純白/純黒を広い背景に使わず、オフホワイト/ブルーグレーを採用。映像imgはobject-fit:contain、filterなし。

通常文字4.5:1、操作識別に必要な境界/選択は3:1を目安に計算。検査14組の全てが閾値以上。装飾panel境界は対象外で、全画素のWCAG認証ではない。[W3C文字コントラスト](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)、[非文字コントラスト](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)を参照。

実施：24画像の解像度一致、全assetロード、全体水平overflowなし、通常最小preview>=480×270、P1/P2のtheme前後panel寸法一致。全24画像をoverviewで目視し、main/小画面/設定/警告を実寸でも確認。スクロールして初めて見える操作は消失ではなくpanel内の到達として別検証。1366版timeline3行が切れないよう高さを調整。
実操作：fresh-open output dialogの初期focus=見出し、Escで閉じて「動画を作成」へ戻る。camera距離1000入力→dark切替後も1000。slider/numberは相互更新。これらは試作HTMLの限定検証。実App接続・systemテーマ追従・全keyboard/全reader/highcontrast/125%DPI・全機能到達の実機合格ではない。

試作の制約：動作しない配置例のボタンがある。素材全件検索・checker切替・出力picker・処理開始・template適用は見本。ページ遷移をまたぐ全編集状態保持は実装前契約。6登場の視覚的な動きのサムネイルは将来製品で実素材から生成し、文言/矢印とともに表示する。現在は文字ボタンで6種を表示。
