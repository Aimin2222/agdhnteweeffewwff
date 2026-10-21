# モンタージュ映像調査台帳と確認範囲

> 調査日：2026-10-22 JST。コード基準：`fb03e0390805125fc063f4599af6c2541a653abf`。今回の作業は調査・設計のみ。実装、LoL実機操作、録画、既存テストの再実行は行っていません。提案値は未実測です。

## 重要：20本の分析は完了していない

候補20本のURL・題名・作者・検索時の公開時期を記録した。本編画面を点で確認したのは2本、キル前→瞬間→後を連続して分析完了した本数は0。残り18本はメタデータのみ。広告、シーク後の未更新フレーム、終了まで流れた再生を視聴実績に数えない。公開時期が「○年前」の候補は正確な日付未検証。題名由来の分類と実際の画面観測を区別する。

ブラウザー上で広告・シーク・更新遅延があり、時刻と本編が一致して確認できた画面のみ採用した。音声は聴取しておらず、拍合わせ・音ハメの評価はしていない。映像はダウンロード・再配布していない。

## 実際の確認内容

|動画|確認できた本編時刻|画面で確認した事実|未確認／推測|
|---|---|---|---|
|[LOLNAM Cinematic Montage #16](https://www.youtube.com/watch?v=d-r2kgeFfus)|約00:25.34、00:54.45、04:10.43の点観測|斜め俯瞰の戦闘、最初のsampleに選手名lower-third、04:10では暗めの戦闘画面|連続軌道、速度曲線、kill前後の全time、制作ソフト、正確なgrade値は未確認|
|[Yone - League of Legends Montage](https://www.youtube.com/watch?v=Y1MGS-wlxrM)|冒頭00:00、約01:32.47の点観測|冒頭Yoneタイトルと2人物、上下letterbox、01:32にTRIPLE KILL表示・戦闘・淡い粒子|粒子のゲーム由来/追加合成、連続camera/retime、音楽同期は未確認|

点観測の間の全区間を見たという意味ではない。YouTubeの画面内時間表示が古い場合があり、HTML video時刻と更新後の画面を併用した。時刻は秒小数を含む概数。

## AutoCineへの応用（観測と分けた設計上の推論）

選手名plateは既存kill badgeと目的が違うため、新設する場合は別overlayとして検討。title/letterboxは低負荷候補だが、LoL HUDや人物を覆わないsafe areaが必要。画角は常に狭めず、複数killでは既存cinema_top/topを比較基準にする。正確な他者camera pathやLUTの逆算は行えない。負荷見込みは2D title低、単純grade低〜中、粒子layer中、追跡や光学flow高で、実測ではない。

## 候補一覧（分析済み一覧ではない）

| ID | 題名・リンク | 作者 | 公開時期（未確定を含む） | 本編確認 |
| --- | --- | --- | --- | --- |
| V01 | [史上最強。全米が震えた神プレイ TOP 30](https://www.youtube.com/watch?v=NolHvXjZA4A) | 롤읽남 LOLNAM | 3年前 | 未視聴 |
| V02 | ['Don't you just have to avoid it?' ／ LOLNAM Cinematic Montage #16](https://www.youtube.com/watch?v=d-r2kgeFfus) | 근육쩌는응애 ᆞ LOLNAM | 2023-08-02 | 点観測のみ |
| V03 | [Mind-blowing plays that take it all the way to the grave ／ LOLNAM Cinematic Montage #15](https://www.youtube.com/watch?v=CDzfUgZHdME) | 근육쩌는응애 ᆞ LOLNAM | 3年前 | 未視聴 |
| V04 | [ジャーヴァンIVモンタージュ2025 - パーフェクト](https://www.youtube.com/watch?v=eYopd5Ynq8o) | LOL TIME | 1年前 | 未視聴 |
| V05 | [OUTPLAYS WORLDWIDE that will HYPE you up for SEASON 13 ／ League of Legends Cinematic Montage](https://www.youtube.com/watch?v=vvjTv5VJzQQ) | GMYugi | 3年前 | 未視聴 |
| V06 | [Yone - League of Legends Montage](https://www.youtube.com/watch?v=Y1MGS-wlxrM) | diyyo | 2020-08-16 | 点観測のみ |
| V07 | [SHEN MONTAGE 2026 - BEST PLAYS](https://www.youtube.com/watch?v=U_E00b3jKbg) | LOL TIME | 7か月前 | 未視聴 |
| V08 | ["Defiant" - Challenger Irelia Montage ft. Rate](https://www.youtube.com/watch?v=FgqHOT9YeSo) | Luviana | 7年前 | 未視聴 |
| V09 | [YASUO-WIND NEVER DIES ／ CINEMATIC MONTAGE](https://www.youtube.com/watch?v=p6J1CkhYt3M) | Markeloffs | 2か月前 | 未視聴 |
| V10 | [Against The Sun - League Of Legends Cinematic Montage](https://www.youtube.com/watch?v=g1DxiJqctkI) | ThePeacePigeon | 11年前 | 未視聴 |
| V11 | [LEE SIN MONTAGE 2025 - GOD PLAYS](https://www.youtube.com/watch?v=aFks00ErSDA) | LOL TIME | 1年前 | 未視聴 |
| V12 | [LOLプレイヤーがとてつもなく頭脳明晰…IQ200のプレイモンタージュ（リーグ・オブ・レジェンド）](https://www.youtube.com/watch?v=0m3O1TYzJE0) | Protatomonster | 1年前 | 未視聴 |
| V13 | [50 ULTRA SATISFYING MOMENTS IN LEAGUE OF LEGENDS](https://www.youtube.com/watch?v=_JWJgS00hfk) | Protatomonster | 2年前 | 未視聴 |
| V14 | [Frame of Mind - Cinematic League Montage](https://www.youtube.com/watch?v=lsiWSeWySMU) | ThePeacePigeon | 12年前 | 未視聴 |
| V15 | [Skills of an expert you don't want to miss ／ LOLNAM Cinematic Montage #24](https://www.youtube.com/watch?v=Vv6ykcYJXrE) | 근육쩌는응애 ᆞ LOLNAM | 2年前 | 未視聴 |
| V16 | ['a thin line, a fine line' ／ LOLNAM Cinematic Montage #23](https://www.youtube.com/watch?v=53CXTEC17oU) | 근육쩌는응애 ᆞ LOLNAM | 2年前 | 未視聴 |
| V17 | [► League of Legends cinematic montage - my demons } full video](https://www.youtube.com/watch?v=l7-ArPoCKn4) | Lunaris | 12年前 | 未視聴 |
| V18 | [League of Legends Cinematic Montage Trailer](https://www.youtube.com/watch?v=a43uvdm22_I) | BestOutplays Ever | 10年前 | 未視聴 |
| V19 | [League of Legends ／ It's Just A Game](https://www.youtube.com/watch?v=YHstBNb5_7g) | Silvxs | 6年前 | 未視聴 |
| V20 | [ADC MONTAGE 2026 - INSANE PLAYS](https://www.youtube.com/watch?v=3c_AK62eY8k) | LOL TIME | 9か月前 | 未視聴 |

## 残っている審査

20候補には公式cinematic再編集・trailerと思われるものもある。まずReplay操作を使う実モンタージュかを本編で選別し、対象外は理由を記録して代替する。作者・champion・強弱・古い/新しい作品が偏らないよう追加する。各採用動画で最低2つのkill区間（前3秒→kill→後3秒）とtransition区間を実際に連続確認し、URL時刻・観測した効果・推測した方法・既存機能との対応・負荷を記録する。速度は音/画とtimecodeを見て推定と明記する。

この未了分を残したまま「最新モンタージュ20本研究済み」と報告しない。現段階のレシピはコード監査と公式制作手法に基づく設計案であり、20本分析から実証した結果ではない。
