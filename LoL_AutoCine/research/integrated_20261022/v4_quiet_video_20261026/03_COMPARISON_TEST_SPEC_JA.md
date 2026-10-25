# 将来のAutoCine出力比較手順（未実行）
## 撮影入力
同じReplayのイベントID・対象participant・team・gameTimeを固定。kill前4秒〜最後のkill後2秒を最低範囲とし、次のengageがある場合はその開始まで残す。秒数は試験条件で正式既定値ではない。BLUE/REDそれぞれ、手動/旧camera/fixed-auto/new candidateを同じ条件で収録する。参照YouTubeは別試合のためピクセル一致を求めない。
## 追加した比較ケース
1. Q-WIDE：V05 259–278相当。複数kill後に残敵がいる入力。旧wideをbaselineに、kill直後の寄りで残敵/攻撃者が画面外に出ないか全フレーム点検。
2. Q-AFTER：V22 155–174相当。最後のkill後に低い寄り、次のengage前に戻る。group誤り/対象死亡/遮蔽で安全wideへ戻す。正確な閾値はユーザー実機比較まで未決。
3. Q-EDGE：V24 100/204/430相当の低角度/傾斜。地形裏・空白・人物欠落率を時間付きで保存。参照映像の演出を製品不具合として自動ラベル化しない。
4. Q-NOTIFY：V04 68 turret/471 elder、V05 273 feed、V24 481縦光を分離。縦光だけでkill確定にしない。Replayイベントで正解を確定。
5. Q-GRAY：V09 121–138。死亡グレー/編集モノクロ/正常カラーを別入力にし、警告をユーザー確認付き候補として記録。
6. Q-OCCLUDE：V22左肖像列、V05右4段feedに似た研究条件。AutoCine最大3段の素材表示とHUD/名前/HPの衝突を各解像度/テーマで測る。原動画の4段を製品要件へ自動追加しない。
## 保存と判定
入力Replayハッシュ、build SHA、設定JSON、ShotPlan、カメラ座標/FOV/TargetLock、イベント時刻、映像PTS、音声PTS、frame drop、encode経路を保存。比較は連続動画+contact sheet+評価票。各被写体可視率/切れ/地形外露出/HUD遮蔽/次engageへの食込み/AV差を記録。許容値は暫定と明示し、無条件PASSを作らない。
既存projectの再出力が変わらないこと、テーマ切替で再生/選択状態が維持されること、旧37/原本89/候補652のhashと承認状態が維持されることも別項目で確認。人工映像テストやNVENC成功を実LoL/GPU FX合格に昇格しない。
