# Codex向け既存問題の修正準備
まずUI29完成→ユーザーUI選択→既存70接続→Windows/LoL検証の順序を守る。以下は今すぐ製品変更する指示ではなく、採用後の独立PR仕様です。

## 1 CPU Flash
入力はFLASH_REVISION_RESULTSとflash_compat_revision.py。旧単発をbit保持、各後続eventで同じpulse、empty無害化。ただしhelper例外の通常到達性を先に調べる。window/丸め/速度mapを保護。旧revision欠落時legacy。single3強度+複数間隔+端+empty+retime全回帰。後続pulse欠落/旧single差分が出たら新revision無効化。

v3は短い重複窓で次event前のpulse項を漏らすことが追加再現できたため、そのまま採用しない。flash_gated_revision.pyのevent開始gate候補も比較する。単発bit一致だけでは複数eventの安全性を保証しない。

## 2 Zoom Blur
入力testsrc2/1.2秒30fps、元graph、tmix_only、without_tmix、constant_scale比較。scale4乗算で飽和する原因候補。研究候補auto0/quarter.25を評価するが、見た目変更なので新processing revisionで明示。真のradialblur追加とは別PR。明度/色/寸法/フレーム数を比較し、旧project goldenと一致するlegacyを保持。実job再現前にLoL不良確定と呼ばない。

## 3 mirror/export座標と固定解像度
PREVIEW_EXPORT_PARITYの3実描画を再現。非1080pで固定384exportに対しmirrorは384×width/1920。どの座標系を正式にするかは採用判断。レイヤのframe/peak/portraitを同じ変換へ、HUD safe areaも同じ空間へ。旧resolutionを無条件rewriteしない。FXの1920固定graphも最終chainで検査。

## 4 肖像枠・素材状態
651fallbackをapprovedにしない。元PNGやカタログstatusを上書きせず、検証済みgeometry/maskを別の明示更新として審査。killer/victim左右、hole、native alpha、最終寸法、3段/HUDを全件審査。19制約は元資料待ち。

## 共通回帰
旧37/原本89/Work687hash、70設定の型/単位/既定/未知field、manual camera/TargetLock、LoLプロセス音声required、GPUFXとencoder別、previewとexportの別command、job cancel/retry、保存/復元、theme状態保持。テスト失敗や例外原文は圧縮せず確認。RTK自動hookを入れず、本研究からクレジット削減を主張しない。
