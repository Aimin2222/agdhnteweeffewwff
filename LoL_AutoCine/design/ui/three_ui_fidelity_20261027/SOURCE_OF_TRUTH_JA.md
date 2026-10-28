# 3UIの正本を探すための入口

| ユーザーの呼び名 | Work名 | 画像ファイルの接頭辞 | 基準 |
|---|---|---|---|
| 候補3 | testA / T-A-M / 旧テストA 現行整理 | A_main.png（legacy_test） | ユーザー指定の原画像そのもの |
| League Director参考版 | R1 Track Desk | **LD_** | Work自作の参考UI。第三者アプリそのものではない |
| Lolnam参考版 | R2 Shot Canvas | **LN_** | Work自作の参考UI。第三者アプリそのものではない |

正本を確認した保存コミット：`3fdda5405f5acac1188ea7be70a07239df06e08b`。R1/R2の最初の画像保存コミットは `85111bef81005aa4a8beb413fcbe9bcb90a10876`。ファイル名だけではLolnamという単語が出ないため、LN_で探してください。

R1/R2原画像の保存フォルダー：`LoL_AutoCine/design/ui/ld_lolnam_reference_20261027/screenshots/`。
配置・寸法：同じフォルダー直上の `specs/LAYOUT_TOKENS.json`。
全70の過去監査：`specs/FEATURE_COMPARISON_70.json`。
操作能力の当時の範囲：`specs/CONTROL_CAPABILITIES.json`。過去のデモ操作報告は現在の本体接続成功を意味しません。

| 正本メイン | 固定リンク |
|---|---|
| 候補3 | [A_main.png](https://github.com/Aimin2222/agdhnteweeffewwff/blob/3fdda5405f5acac1188ea7be70a07239df06e08b/LoL_AutoCine/design/ui/implementation_audit_29_20261021/references/legacy_test/A_main.png) |
| League Director参考版 | [LD_main_light_1920x1080.png](https://github.com/Aimin2222/agdhnteweeffewwff/blob/3fdda5405f5acac1188ea7be70a07239df06e08b/LoL_AutoCine/design/ui/ld_lolnam_reference_20261027/screenshots/LD_main_light_1920x1080.png) |
| Lolnam参考版 | [LN_main_light_1920x1080.png](https://github.com/Aimin2222/agdhnteweeffewwff/blob/3fdda5405f5acac1188ea7be70a07239df06e08b/LoL_AutoCine/design/ui/ld_lolnam_reference_20261027/screenshots/LN_main_light_1920x1080.png) |

各参考UIにはmain/easy/detail/camera/curve/color/material/exportの8画面、main dark、main1366版があり、合計20枚です。全パス・コミット・SHA256・Git blobを `specs/SOURCE_INDEX.json` に記載し、GitHubの20ファイルとローカルPNGのGit blob一致を確認しました。

以前の `demo/app.js` や `index.html`、EXE、起動BATを探して復元する必要はありません。配布停止は継続し、今回のPNG・寸法・機能契約を基準に信頼できる現行コードで実装してください。旧Windows実装仕様の「デモコードを正本にする」という箇所より、この資料の画像優先・配布停止の扱いを優先します。原本資料自体は変更していません。
