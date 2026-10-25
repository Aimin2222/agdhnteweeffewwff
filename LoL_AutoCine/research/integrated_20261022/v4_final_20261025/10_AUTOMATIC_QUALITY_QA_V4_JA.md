# 自動画質QA拡充
14分類×正常/異常×30/60fps=56期待値一致。黒画面、静止、上下反転候補、frame落ち、音声欠落、AV差、過剰Flash、HUD/人物遮蔽、素材見切れ、死亡後gray、低体力赤、teleport、意図的暗転、正常cameraを含みます。

黒/静止は人工画像列、反転/遮蔽/ゲーム状態などの多くはfixtureのsemantic metadataを使用。映像認識器の精度56/56ではありません。警告が期待ラベルどおりかというルール検証です。実LoLのFP/FNは未測定。gray=死亡、red=低体力、white=FXを機械的に断定しない。意図した暗転/teleport区間や手動カメラも自動削除しない。

将来は警告中心、理由・区間・信頼度・既知ゲーム状態・ユーザーdismissを保存。自動再撮影/切捨ては既定off。比較fixtureに正常長回し、map切替、死亡、teleport、薄暗いskin、連続Flash、実遮蔽を追加し、人手annotationとのFP/FN/confusionを出すまで品質合格へ昇格禁止。
