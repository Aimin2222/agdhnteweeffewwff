# B4 混合UIの機能接続整理（新UI制作ではない）
公開候補番号をPR51のcomparison_labels原文に照合。候補7=L05-M（旧ウィザード）、候補4=L06-L/L06-E（旧ライブラリ/編集）。内部layout_variantsの番号を転用しない。ユーザー保持の候補7メイン＋4詳細・素材・枠、比較3/5/8を維持。簡単画面は未決定。採点・順位付け・採用変更は行わない。

70機能はFEATURE_MAP_70.json/CSV、既存25契約はEXISTING_BINDING_CONTRACTS_25.json。各機能の導線を残し、実接続がないものを成功表示しない。ENGAGE/BESTSHOTなどの既存監査上の不足は解消したと扱わない。PR52候補8〜10の文書には実LoL・録画・音声・GPU・MP4接続が無いことが明記されている（今回は文書の確認のみ）。

遷移: 候補7の準備→対象選手→スキャン→シーン選択→既存プリセット→演出確認→出力。途中で候補4詳細へ入り、トリム/キーフレーム/色/カメラを調整→素材図鑑→同じシーンへ戻る。画面遷移はジョブやReplay接続の再生成理由にしない。メインの再表示でテンプレートを自動適用しない。

共通状態: projectId, stableSceneId, focusedSceneId, outputCheckedIds, perSceneOverrides, cameraMode/style/side, TargetLock対象ID, previewPTS, assetIdとcatalog承認状態, encoderPolicy, actualEncoder, audioSource, outputPath, jobState。焦点と出力チェックは独立。Undoは場面設定変更を一操作として記録。出力開始時は不変スナップショットを取り、処理中のUI変更と混在させない。テーマlight/dark/systemと候補/viewIdは外観状態として別保存し、映像色やカメラ値を変更しない。

不足導線の提案: 接続/FFmpeg/音声helper/WebView2診断、スキャン中断、失敗クリップ再試行、出力進捗/中止/残存ファイル、実エンコーダ、正式/確認用/ユーザー不採用フィルター。既存機能のショートカットを足す提案であり、製品に実装済みではない。モーダル内スクロールと背景スクロールを分離し、Esc/閉じる/フォーカス復帰を同じ契約にする。

検証: 70ID重複/欠落0。5候補×3テーマの独立状態契約15件PASS（モデル不変の限定試験）。実GUI遷移、スクロール、DPI、実バックエンド70機能の押下試験はNOT_RUN。Codex側で元画面と照合し、数値変更→プレビュー更新→保存→再起動→出力値の一致を各機能で検証する。
