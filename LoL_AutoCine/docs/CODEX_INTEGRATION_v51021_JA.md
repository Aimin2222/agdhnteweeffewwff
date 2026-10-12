# v5.10.21-test FPS対象座標・モード別小補正・ディレクター強さ・単体参照動画

受領ZIPのCRC/パス/リンクを確認し全README/差分/7追加テストを読む。指定GitHub0e8e8f65362fd10a3ab9509c3fcbb4580b72691dへ独立checkoutでapply --check/適用。単体テストはpatch内とバイト一致。受領v20からの差分12パスだけ現行Codex v20 d76c0d78c82db9f0c278d83878113b5bc7757aeeへ機能別統合。添付のresults/画像比較・良好カメラ・Windows/Release記述は受領側の説明で、Codex実機確認・Release作成ではない。原ZIPはGit外、原コードはarchive/received-ui-v51021とhistoryへ保存。

カメラ補正辞書core/camera_tuning.pyでチーム/モード別。距離0.87〜1.15、角度±8度以内と有限値を検証（受領が許したNaNをCodexで拒否）。RED通常third0.94/シネマ0.96距離、RED Lolnam X/Y-3度/geo X-3度、BLUE third X+3度/Lolnam・geo X+2.5度、BLUEシネマ追加補正なし。ライブsetupだけ反映、直接CameraPlanの旧式は保持。実構図改善と軸の正しさは未確認。RED2/BLUE7の悪化を実機回帰条件にする。

FPSは古いTopベクトルを縮める処理から、既存third poseによる対象相対オフセットへ変更。RED自動192度を位置と向きへ使用。Codexで手動blue0/red180をprofileから同じく位置と回転へ反映し、FPS高さ入力も保持。キャッシュ分離(selection/team/style)とstable rotation分離(selection/team/style/axis)、安全俯瞰・forced Y/+1/通常pitch・reset/seek/TargetLockは保持。画面内の主役やキル自動認識ではない。

UIは色微調整とディレクターの変数traceでON/OFF時すぐ直下を展開、OFFで共有値保持。自動ディレクターの強さ0〜1.5を回り込み/接近パラメータへ。受領の0が既定Orbit再生成へ戻る問題を補正し、UIスレッドでTemplate末尾の任意auto_director_strength（既定None）へsnapshot、jobsがCameraPlan私有値へ接続。CameraPlanのフィールド・末尾team・各呼出署名は不変。旧Template位置引数・JSON・Noneの動作を保持、replaceでも値を保持。指定0は追加自動Orbitと接近を抑制、0.5は実接近を中間へ、1.0は従来量。スタイル固有FOV/スロー/ローアングル/手動keyframeは残る。非数値/NaNは開始前にUIエラー。GPU rendererはこの任意カメラ値を描画処理へ使わず全22FXを維持。

参照BATはフォルダ/単体MP4・MOV・MKV・WEBMを受け、入力別出力先、TEMPのAutoCine_ReferenceReview_latest.log、失敗コード/pause。Python helperも単体入力の基準パスを調整、前回の空フォルダJSON/ZIPとPath正規化を保持（受領パッチはこのCodex補正に競合、個別解決）。実60fps MP4から6時点JPEG/JSON/ZIPと元動画不変を検証。BAT自体のWindows実行は未確認。任意のCPU静止画比較で通常GPU加工経路外、AI判定/自動アップロードなし。

GPU feature/gpu-cameraqa-v51021、UI feature/ui-cameraqa-v51021、統合 integration/v5.10.21、受領 archive/received-ui-v51021。旧107先端/193過去配布物/37PNGを保持、全111refs bundle、共有8blobレビュー。

```sh
python tools/check_parallel_integration.py --gpu feature/gpu-cameraqa-v51021 --ui feature/ui-cameraqa-v51021 --integration integration/v5.10.21 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.21.json
```

ガードはコミット先端だけ、statusも確認。GPU Full/OpenCL/NVENC/実FXとencoder診断/60fps時刻・フレーム数/LoL Native Loopback/WGC/Native Helper/ミラー応答/CPU安全fallback/6空間・6キルQA/3切替QAと通常10演出/1MBstream 500MB直接ZIP/最終JSON一致/元動画・既存ZIP保持/データJSON64KB・3秒を維持。GPU効果とNVENCを混同せずCPUゼロを主張しない。前回capture終了テスト同期も維持。過去Linux native139/132は原因未確定。今回実機/NVIDIA性能・LoL構図は未確認、結果はhandoff/VERIFICATION_v5.10.21.json。mainへマージしない。
