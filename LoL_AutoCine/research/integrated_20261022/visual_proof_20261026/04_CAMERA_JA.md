# 自動カメラのテストデータ検証 / R01–R05
既存採用third（三人称斜め後ろ）とthird_cinemaを保護。core.camera.CameraPlan、side_yaw_for、limit_camera_postを読取コピーから呼ぶ。BLUE/RED × 2style × yaw0/90/180 × mode未指定/fixed_auto/full_auto=36条件、各90sample@30fps。テストRigInfoのh=(0,-1)、pitch axis=x/sign=-1、初期rotation x=-32を明示。LoLの実機校正値ではない。

36/36でfinite、入力rigは不変。BLUE0/RED180という既存関数の結果と、XZ平面のoffset/高さ/rotation/FOV/speedを保存した。4動画は各side/styleの3yaw比較。default arc0などで固定になる/線が重なる条件もあり、動きが大きいと誇張しない。この図はエンジンの投影や地形可視率ではない。

90/180°stepを既存slow-API limiterへ通し、selectionName/attachedが維持されることを確認。これはpacketフィールド保持であって、ゲーム内の物理TargetLock成功ではない。180°の最短経路は負方向を取る場合がある。軸の意味は実機校正待ち。

新規候補は別の2D fixture。4参加者と発射者(-350+50sin(t),-260)、着弾(800,220)、宣言した矩形壁を使い、1秒で発射者中心から集団＋着弾の平均へ切替。rawの最大中心跳躍=571.997320単位/frameでFAIL。単純な平均中心をそのままcameraへ適用しない。

追加比較はこの中心をテストpacketのoffsetとして既存limit_camera_postへ通す。強制slow_api=True、dt=1/30。最大offsetstep=14.000000000、yawstep=1.400000000°で上限14/1.4に1e-9許容で適合。6本目switch_raw_vs_bounded.mp4と4frame sheetでbefore/afterを示す。これは速度上限だけで、加速度・衝突・実機投影・最適構図を保証しない。通常API速度時はこのguardがbypassされるため、恒常的な新plannerの平滑化として無条件流用しない。

遮蔽は既知の2D線分×矩形2例を確認しただけ。地形メッシュ、キャラクター遮蔽、画面内包含率、長射程の発射/命中イベントの検出、実Replay targetはNOT_RUN。遮蔽不明なら既存採用カメラを保持する設計を継続。既存三人称を新候補に置換していない。LoL Replayを操作/録画していない。
