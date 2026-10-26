# AutoCine UI/UX全面再調査
調査日：2026-10-21。対象はWindowsデスクトップ。以下の「採用」「注意点」「評価」はAutoCineの用途に対する制作側の判断であり、他社製品の総合的な優劣やユーザーテスト結果ではない。

## 調査方法と不足
公式の製品画面、ヘルプ内のスクリーンショット、操作手順を中心に確認。Resolve・CapCutの公式画像、Lolnamの公式チュートリアル入口もブラウザーで目視した。10製品をインストールして同じ課題を操作した実験ではない。ログイン後限定の機能、すべての最新バージョン・プラン・テーマ設定は確認できていない。公式資料にないテーマ対応は推測で補っていない。Blenderの一部公式マニュアル本文は取得制限があり、公式検索結果と取得できたワークスペース資料を使用した。

他社画像は参考リンクとして記録し、本納品に画像原本を再配布しない。今回のゲームプレビューは生成イメージ。他社アプリを撮影した画像や実機のLoL映像ではない。

## 10アプリの操作設計
| アプリ | 公式画面・操作で確認した流れ | AutoCineで参考にする点 | AutoCineに持ち込む際の注意 |
|---|---|---|---|
| DaVinci Resolve | Cutの高速編集とEditの通常編集を行き来。全体と局所を扱う時間軸、クイック操作 | 簡単作成とStudioを別の仕事場にし、同じプロジェクトを共有 | 多数の制作ページ・専門用語を初回画面へ並べない |
| Adobe Premiere | 作業別ワークスペース、パネル配置の保存とリセット、素材からタイムライン編集へ | 位置を安定させる。選択中の対象に設定パネルを連動 | ドックを自由に動かす仕組みは初期実装を重くする。最初は固定配置 |
| CapCut | プロジェクト作成、素材読込、時間軸配置、調整、出力。テンプレート・素材の画像選択 | 仕上がりを画像で探す入口、主要操作を少数にする | テンプレート名だけでカメラ・FXの変更内容を隠さない。WebとDesktopの画面を混同しない |
| Filmora | メディア・プレイヤー・時間軸・プロパティ、目的別配置とパネル寸法変更 | 数値を使う詳細と画像カードを使う簡単操作の共存 | 初心者に多数のレイアウトやAIメニューを初回選択させない |
| OBS Studio | シーン／ソース／音声／操作をドックに分ける。Studio Modeは編集側と配信側を区別 | ミラー表示、演出確認、録画を別の状態・操作として表示 | AutoCineで2画面プレビューを常用すると映像が小さくなる。ソース管理は本用途と異なる |
| Blender | 作業ごとのWorkspaceと用途別Editor。初期設定でテーマ等を選ぶ | キーフレーム等の上級操作を目的別ページへまとめる | どの領域でもエディター種別を変更する自由度は初心者に重い |
| Medal | ライブラリーでクリップを選び、編集・結合・端をドラッグしてトリム | 見どころ一覧から編集に入る。出力チェックとプレビュー対象を分ける | 既録画クリップを扱う設計を、リプレイ内のカメラ撮影へそのまま移植しない |
| Outplayed | ゲームイベントを契機にハイライト、試合・セッションを整理し、クリップを編集 | キル・アシスト・選手を入口にする。全試合の文脈を残す | 録画済み動画の収集とAutoCineのカメラ再演出は違う。検出結果を画質合格にしない |
| Adobe Lightroom Classic | Libraryで選別→Developで調整。共通Filmstrip、パネルのSolo表示・Lights Out | シーン集合を維持して仕事場を切り替える。必要な設定だけ開く | 写真用の多数のモジュールは不要。Lights Outを「ライト／ダーク切替」と同一視しない |
| Lolnam Editor | リプレイ管理からカメラ時間軸・キーフレーム・曲線・色調整を経て出力する公式紹介 | キル時刻を基準にカメラの動きと演出を整理する | 上級カメラ編集を初回入口にしない。自由な世界座標カメラなど未実装機能を流用しない |

### 公式参照先
- Resolve：[Cut](https://www.blackmagicdesign.com/products/davinciresolve/cut)／[Edit](https://www.blackmagicdesign.com/products/davinciresolve/edit)。
- Premiere：[Workspaceの切替・保存・リセット](https://helpx.adobe.com/ca/premiere/desktop/get-started/tour-the-workspace/change-create-reset-workspaces.html)／[配色設定](https://helpx.adobe.com/premiere/desktop/get-started/preferences-and-settings/appearance-preferences.html)。
- CapCut：[PCでの基本操作](https://www.capcut.com/resource/how-to-use-capcut-on-pc)／[操作例](https://www.capcut.com/resource/how-to-use-capcut)。
- Filmora：[Windowsのパネル配置・設定](https://filmora.wondershare.com/guide/panel-layout.html)。
- OBS：[公式概要・設定・Studio Mode](https://obsproject.com/kb/OBS-Studio-Overview)。
- Blender：[Workspaces](https://docs.blender.org/manual/en/latest/interface/window_system/workspaces.html)／[初期設定のテーマ選択](https://docs.blender.org/manual/en/dev/getting_started/configuration/defaults.html)。
- Medal：[Montage Editor](https://support.medal.tv/support/solutions/articles/48001185258/)／[Windows入門](https://support.medal.tv/support/solutions/articles/48000959661-getting-started-with-medal-on-windows)。
- Outplayed：[公式の使い方](https://support.overwolf.com/support/solutions/articles/9000284659-how-to-use-outplayed)。
- Lightroom Classic：[ワークスペースの基本](https://helpx.adobe.com/lightroom-classic/desktop/workspace/workspace-basics.html)。
- Lolnam：[公式画面とワークフロー](https://lolnam.gg/)／[開発者のOverwolf紹介](https://www.overwolf.com/app/lolnam-lolnameditor)。

## 配色の比較
| アプリ | 今回確認できた配色・変更 | AutoCineへ応用する点 |
|---|---|---|
| Resolve | 公式紹介画面は暗いニュートラル系。今回資料から現在の全テーマ選択肢は確定できず | 暗い編集環境と中立的な映像周囲。小さい低コントラスト文字は模倣しない |
| Premiere | Darkest / Dark / Lightとコントラスト設定が公式手順にある | 明暗と視認性を分けて設計し、暗い背景でも選択・境界を明瞭に |
| CapCut | 公式PC紹介に暗いUI。今回、Desktop版の正式なライト切替手順は確認できず | 素材カードの見やすさを採用。対応テーマ数は断定しない |
| Filmora | Windows設定のUser InterfaceでLight / Darkを選択する手順 | 同一の仕事場を配色だけ変える |
| OBS | 公式概要にライト／ダークテーマの変更 | ドックごとに文字・境界・無効表示をテーマ対応 |
| Blender | 公式初期設定にライト／ダーク選択。カスタムテーマの公式資料もある | 形状・余白を変えず、色トークンで一括変更 |
| Lightroom Classic | 公式画面はグレーの作業面。Lights Outは周囲を暗くする機能 | 映像の周囲を中立に保ち、テーマで画像そのものを加工しない |
| Medal / Outplayed | 公式手順の画像はクリップ中心の暗い構成。完全なテーマ切替仕様は未確認 | 暗いサムネイルでも枠とラベルが見える中間色のマットを設ける |
| Lolnam | 公式チュートリアル入口は暗いUIと色分けしたキー。全テーマ仕様は未確認 | キー・選択・未確認に形と文言を加え、色だけに頼らない |

## 目に優しい配色の判断
初期案は「ソフトライト」と「ソフトダーク」の2つ。Windowsに合わせる選択を既定候補とする。純白／純黒の大面積使用は避け、見やすさを確保した本文と操作境界を組み合わせる。Microsoftも環境や利用者の好みに合わせたテーマと、純白・純黒を避ける方向を示している。[Windowsの配色](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/color)、[Windowsアプリの設計指針](https://learn.microsoft.com/en-us/windows/apps/get-started/best-practices)。

明るい背景上の暗い文字に校正課題の成績上の利点を示した研究がある。ただし、これはAutoCineを長時間使用した際の疲労軽減を証明したものではない。暗いモードを万人に優れたものと扱わず、好みと環境で切り替えられる設計にする。[Piepenbrockらの原著抄録](https://pubmed.ncbi.nlm.nih.gov/25135324/)。

ニュートラル案は中間グレーの映像周囲を両モードで固定する方式として採用。独自配色は「青を主操作に限定したSlate Blue」。暖色は注意、赤はエラー等に用途を絞る。追加の色テーマを増やすより、ライト／ダーク／Windows追従の3つを分かりやすくする。

通常文字4.5:1、主要部品3:1を参考目標にした。装飾線まで一律3:1にするのではなく、操作境界・選択・フォーカス等の意味のある情報を検査する。無効部品は基準の対象外になる場合があるが、本案では理由文と破線を付け、文字も読みやすくする。[WCAG文字](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)、[非テキスト](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)。

60組の指定色を計算し、基準未満だった暗色モードの境界色と無効文字色を調整した。最終値と全計算結果はCOLOR_TOKENS.json、CONTRAST_AUDIT.csvに記載。これは指定色の検査であり、全画面・全状態・全実装のWCAG適合認証ではない。

