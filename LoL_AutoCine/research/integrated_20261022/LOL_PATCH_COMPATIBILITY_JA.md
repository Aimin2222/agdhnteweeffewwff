# LoLパッチ互換性とAPI依存の監査

> 調査日：2026-10-22 JST。コード基準：`fb03e0390805125fc063f4599af6c2541a653abf`。今回の作業は調査・設計のみ。実装、LoL実機操作、録画、既存テストの再実行は行っていません。提案値は未実測です。

## 何を保証できるか

今回LoLクライアントへの接続は行っていない。現行パッチ番号もローカル実機から取得しておらず、互換済みパッチ一覧は作れない。[Riot Replay FAQ](https://support.riotgames.com/en-us/league-of-legends/gameplay/replays-faq-pro-tips)はリプレイがpatch cycleで失効すると説明する。古いroflを新patchで必ず再生できる設計にはしない。

## 依存点と予防策

|依存|起き得る変化|事前検査・代替案|
|---|---|---|
|ROFL/ゲーム版|リプレイ起動不能|版不一致を区別し原因表示。ゲームファイルを自動改変しない|
|Replay API playback/render|field型・意味・対応範囲|read-only schema probe→制限値付き最小操作を別実機試験|
|Live Client events/playerlist|イベント欠落・識別名|eventID/時刻/killer/victim/assistを保存し欠落はunknown|
|camera axes/FOV/attach|対象が空や地面へ|side/style/patch別承認。旧承認の無条件再利用なし|
|HUD/DOF/Fog|設定無効・復元不能|対応fieldを個別probe、復元失敗をログに残す|
|LoLプロセス・ウィンドウ|PID切替、最小化、権限差|実LoL process treeを検証、WGC freshと別にチェック|
|音声|出力デバイス・OS API対応|プロセス音声helperの実行試験。全体録音へ代替しない|
|champion icon/skin|Data Dragon版差・欠落|既存キャッシュ＋欠落用プレースホルダ、別人iconにしない|

[core/replay_api.py:1](https://github.com/Aimin2222/agdhnteweeffewwff/blob/fb03e0390805125fc063f4599af6c2541a653abf/LoL_AutoCine/core/replay_api.py#L1)はlocalhost HTTPS2999へのserial access。公開Web APIとローカルReplay APIを同一扱いしない。[Riot LoL developer docs](https://developer.riotgames.com/docs/lol)を仕様の入口とし、欲しい敵3D位置やdepth mapが存在すると推測しない。POSTのタイムアウトは「未適用」と限らないのでreadbackしてから再送を決める。

## サポート台帳と試験

OS build/LoL patch/Replay patch/GPU driver/FFmpeg hash/AutoCine SHAを1行へ保存。patch更新時は起動→player→scan→BLUE/REDロック→FXoff→音声あり10秒→復元の順。未試験patchは「未検証」であり「非対応確定」ではない。実機試験はユーザーの開発・自動テストが走っていない時に別途実施する。

## Riot方針の確認

[General Policies](https://developer.riotgames.com/policies/general)は製品登録・審査、対応サービスの利用、不公正な優位を避けること等を要求する。今回それらへの登録状況は確認していない。[Legal Jibber Jabber](https://www.riotgames.com/en/legal)もファン制作物と素材利用の条件を定める。Replay APIを使えることだけで配布・収益化・他者映像/BGMの利用許諾まで確定しない。公開・配布段階に適用条件を再確認するための確認項目であり、今回の研究を止める承認フローではない。
