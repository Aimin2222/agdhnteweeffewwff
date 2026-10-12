# LoL AutoCine v5.10.25 — BLUE #6 上下構図の限定テスト版

## 資料と検証上の注意
- 開発基準は v5.10.24-test / コミット `49d8093974ef0f34a73399e2db8516bd4893d44d`。
- ユーザーのWindows v5.10.24実機テスト：`results(9).json`、`camera_comparison(8).jpg`、`RED_camera_3frames(7).jpg`、`BLUE_camera_3frames(7).jpg`、`transition_comparison(6).jpg`、`transition_3frames(5).jpg` など。利用者の個人名やローカル診断ZIPの中身はリポジトリへコミットしない。
- `results(9).json`ではRED/BLUE計10本（failures空）、既存切替3種、空間切替6種、キルフレーム登場6種の生成が記録。**生成成功と、被写体が正確に映ることや音声が正常であることは別**。
- RED #1/#3は比較画像上で以前の端寄りから改善した可能性があり、幾何学的中央向きフラグがON（X約-160.67°/ -162.66°）と記録されている。実際に全フレームで中央かは未確定。
- BLUE #6はPRE/KILL/POSTの3枚画像で主役・戦闘が上寄りに見える。v5.10.24には既に距離1.10倍と追加の後退1.26倍があり、単なる追加後退よりピッチ方向の限定変更を試す。
- **重大な制約：本チャットでPythonとコンテナがClientErrorのため、受領した生MP4／CameraQA 3つの分割ZIP／x_media_all_merged(3).zip／診断ZIPを直接解凍、ffprobe、音声解析できていない。動画を解析したとは主張しない。原因も断定しない。** スクリーンショットとJSON、現行GitHubソースだけに基づく暫定調整。

## v5.10.25で行った変更（動画合格を保証しない）
1. `core/camera_tuning.py`の `SHOT_TUNING[("BLUE","third")]` の角度補正を **X +3° → X -4°** とし、BLUE通常三人称に限り視線を7度浅くする。キル前/瞬間/後で主役を画面の上端から中央寄りへ動かす意図。確定ではなく実機で結果を測るためのテスト版。
2. BLUE #6の既存距離1.10倍、追加後退1.26倍、FOV/補正方式、ターゲット追従を変更しない。
3. **RED #1〜#5、BLUE #7〜#10のパラメータは変更しない。** Replay API、共通CameraPlan/CameraDirector、GPU/OpenCL、NVENC、ネイティブLoL専用音声、HUD、ミラー、キルフレーム37素材と6種類の登場動作、テンプレートA/B、詳細編集は変更しない。
4. `VERSION.txt`、CameraQA `results.json`の`version`、`qa/test_plan.json`をv5.10.25のテスト目的に合わせ更新。ワンクリックテストの10本・演出・500MB分割ZIPは維持。
5. `tests/test_v51025_blue6_vertical_frame.py`でBLUE #6のみの補正、他9モードの構図設定、RED/BLUE FPS後方距離、Zロールゼロ、位置・FOV維持を回帰検査。

## ユーザーのWindowsでの確認（旧版と同じリプレイ推奨）
1. v5.10.25 Windows_Test_Full.zipを**v5.10.24とは別フォルダーへ展開**。
2. 開発用ワンクリックQAを一度だけ実行。**BLUE #6のPRE/KILL/POST**をv5.10.24の`BLUE_camera_3frames(7).jpg`と比較。主役の縦位置、キル相手の視認性、地形の遮り、天地反転/過度の水平線を確認。
3. RED #1/#3の幾何補正結果、保護中のRED #2/#4/#5、BLUE #7/#8/#9/#10に退行がないことを比較画像と動画で検証。
4. CameraQAの10本、RED/BLUE各レビュー動画、従来切替3種、空間切替6種、キルフレーム登場6種が揃うか。JSONの`outputs[].failed`、ZIPの500MB制限を確認。
5. 1920×1080 / 60fps、LoL音声のみ、NVENC/GPU、ミラー停止復帰、HUD・キルフレーム・テンプレートは継続して実機確認。
6. `MAKE_REFERENCE_SHEETS.bat`で動画単体・フォルダー・動画ZIPの読み込みと保存先表示も確認（この版はBAT変更なし）。
7. 問題があれば`results.json`、`RED_camera_3frames.jpg`、`BLUE_camera_3frames.jpg`、実MP4、診断ZIPを共有。過去動画の大量再送は避けてよい。

## 参考映像（変更の候補であり今回すべてを実装した意味ではない）
別途渡されたxMediaコンタクトシート（29本と報告）や静止画、およびユーザー提供の参考分析文章から、以下を確認対象とする。
- `Aegis Lee Sin`: 放射状Zoom Blurを交戦導入のアクセントにする案
- `Ahri vs Fizz`: モノクロ背景＋一部のスキル色を強調する案
- `Yasuo 1vs4`: 低角度・接近したシネマカメラの案
- 別のサミーラ戦闘シーン: 近距離カメラと発光タイミングを統合する案

これらの演出は静止画像・文章からの**方向性の整理**であり、元動画のモーション曲線・時間関係を実測した成果ではない。既存の良好なカメラを置き換えたり、旧FX・音声・GPUを削除したりせず、今後実動画にアクセスできるときに評価する。

## 配布／統合
- v5.10.24の指定コミットから専用開発ブランチ`autocine/v5.10.25-blue6-vertical-frame-qa`を作成。
- main、Codexの`codex/lol-autocine-v51015-ui-scan-camera-handoff`、Draft PR #29を**変更・マージしない**。
- Linuxのpytest、WindowsのBAT/有効動画ZIP・不正ZIPテストをGitHub Actionsで実行。成功ログとZIP CRC検査が確認できるまで自動テスト合格・配布完了とは書かない。
- 差分ZIPはCodex v5.10.15を起点にした**レビュー用パッチ**。既存Codex GPU/音声/録画ファイルへ無検証で上書きしない。
