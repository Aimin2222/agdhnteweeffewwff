# Codex向け 安全な修正・実装の引継ぎ
これは実装提案。AutoCine本体に研究コードをコピーして完了扱いしない。参照固定commitはSOURCE_REFERENCES。PR49 queried7ファイルは旧snapshotとAST一致だが、PR44など他ブランチを上書きする根拠にしない。

1. Flash: source/replay/event/timeline/encode PTSの写像を先に固定。CFRはceil(event×fps)の因果gate、VFRはactualPTS>=event。丸めは開始前へずらさず同時別victimを保持。max合成と残光上限を独立設定。通常/slow/seek/pause/長尺を別回帰にする。明るさ修正は因果性修正と別PR/別revision。
2. Zoom: tmix自動正規化を小さい独立修正候補にする。cut/seek/clip切替のcontinuity IDが変わったら履歴破棄。真の空間radialは新しいeffect IDで対象中心座標/weight正規化/端サンプル/alpha/color空間を定義し、時間blur修正と混ぜない。CPU/GPU同一PTS比較後に採用判断。
3. Overlay: 共有OverlayPlanでrowと時刻とtransformを一元化。先に準備RGBAの合成器一致を確認し、次に独立plannerの入力/出力同値を検証。画面上のDPI/letterboxは最後。旧84FAILを基準に全frame比較。missingbboxは失敗理由/画面外/非表示のどれかを記録する。
4. 素材: catalog formalStatusは不変。research geometry/AI review/userExcludedを別領域に保存。原本/37badge/89masterのhash照合、推薦から除外5件を落とす。alpha-dHash/MAEの低さだけで削除・統合・再承認しない。P2残523と19原本制約を明示する。
5. Camera: 採用済み斜め後ろを保持した別モードで研究。manual優先、BLUE/RED実軸、TargetLock対象IDを固定。速度/加速度/lag/cutの4基準をログ化し、対象画角・遮蔽confidenceを実機で確認。図の研究unitをそのままゲームunitへ代入しない。
6. Oneclick: 既存smart_montageへ全自動置換せず、score順と同戦闘groupの選択理由を保存。event重複IDだけ除去し別victim同時刻を残す。手動overrideは候補更新でも保持。ゲーム音のみを既定にし、成功通知は実出力QAの後。
7. AV: helper対象PID treeを検証し、無音時の全デスクトップfallbackは禁止。actual PTSとsample countからdrift/concat境界を測る。durationだけPASSにしない。合成testは録画機能の成功証明ではない。
8. UI/配布: ユーザー保持の7main＋4detail/material/frame、比較3/5/8維持。70機能導線・テーマstate不変の契約を接続。新しいUI採用判断なし。日本語path/標準ユーザー/FFmpeg/helper/runtime/CPU fallback/再開を隔離PCでE2E実施。Windows設定を変更して試験を通さない。

推奨修正順は時刻因果性→tmix正規化/履歴→Overlay共通化→実AV/復元→新しいcamera/素材整理。これは不具合修正の依存順で、UI順位や素材の正式採用順位ではない。各修正で旧状態へ戻せるrevisionとdiff、入力hash、raw比較frame、実エンコーダ、NOT_RUNを記録する。
