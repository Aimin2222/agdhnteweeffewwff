const characters = [
  {
    name: "アムム",
    items:
      "ガーゴイル ストーンプレート, ワーモグアーマー, リデンプション, プロテクターの誓い, アイオニックスパーク or イーブンシュラウド, サンファイアケープ, ドラゴンクロウ, ブランブルベスト",
    anomalies:
      "ドラマチックな登場, 超特大サイズ, 要塞化, ブルワーク, 深い根, 石の皮膚"
  },
   {
    name: "イレリア",
    items:
      "ヒーロー:, インフィニティエッジ, ブラッドサースター, 巨人の誓い, ハンド オブ ジャスティス  , タンク:, ガーゴイル ストーンプレート, ワーモグアーマー, リデンプション, プロテクターの誓い, アイオニックスパーク or イーブンシュラウド, サンファイアケープ, ブランブルベスト",
    anomalies: "究極のヒーロー, ブリー, ノックアウト, 最後のチャンス, シュリーマの遺産"
  },
    {
    name: "ヴァイオレット",
    items:
      "ブラッドサースター or ハンド オブ ジャスティス, 巨人の誓い, ステラックの篭手, ナイトエッジ, クイックシルバー, インフィニティエッジ, 伏兵の紋章",
    anomalies: "究極のヒーロー, ブリー, 最後のチャンス, 友情の力"
  },
    {
    name: "ヴェックス",
    items:
      "ショウジンの矛, ジュエルガントレット, ナッシャートゥース, ラバドンデスキャップ, アークエンジェルスタッフ, ジャイアントスレイヤー",
    anomalies:
      "ブリー, 無駄なし, 連続キル, 逆転劇, フィニッシャー, 魔法の訓練, フリースタイル"
  },
   {
    name: "ザイラ",
    items: "ショウジンの矛, ジュエルガントレット, ナッシャートゥース, ラバドンデスキャップ, アークエンジェルスタッフ",
    anomalies:
      "ブリー, 無駄なし, 連続キル, 逆転劇, フィニッシャー, 魔法の訓練, フリースタイル"
  },
  {
    name: "シンジド(ヒーロー)",
    items:
      ", タンク: ガーゴイル ストーンプレート, リデンプション, ドラゴンクロウ, ワーモグアーマー, アイオニックスパーク ... , ヒーロー:, ブラッドサースター or ヘクステックガンブレード, アークエンジェルスタッフ, モレロノミコン, ジュエルガントレット, アイオニックスパーク",
    anomalies:
      "ヒーロー:, 究極のヒーロー, ブリー ... SINGED IN RENATA COMP: 超特大サイズ, 要塞化, ブルワーク, 深い根, 石の皮膚, 防御の達人"
  },
 {
    name: "ステブ(ヒーロー)",
    items: "ヒーロー:, ブラッドサースター, アークエンジェルスタッフ, 巨人の誓い, ジュエルガントレット",
    anomalies: "究極のヒーロー, ブリー"
  },
    {
    name: "ダリウス",
    items: "ブラッドサースター or ハンド オブ ジャスティス, 巨人の誓い, ステラックの篭手, ナイトエッジ",
    anomalies: "究極のヒーロー, ブリー, 最後のチャンス"
  },
    {
    name: "トランドル (ヒーロー)",
    items: "ヒーロー:, ブラッドサースター, 巨人の誓い, ハンド オブ ジャスティス, クイックシルバー",
    anomalies: "究極のヒーロー, ブリー, シュリーマの遺産"
  },
    {
    name: "ドレイブン",
    items:
      "グインソーレイジブレード, ラストウィスパー, デスブレード, ジャイアントスレイヤー, インフィニティエッジ, ルナーンハリケーン",
    anomalies: "究極のヒーロー, ブリー, 巨人の攻撃, 腕力の訓練"
  },
    {
    name: "パウダー",
    items:
      "ショウジンの矛, アークエンジェルスタッフ, ナッシャートゥース, ジュエルガントレット, ラバドンデスキャップ, ジャイアントスレイヤー",
    anomalies: "ブリー, 究極のヒーロー"
  },
   {
    name: "マディー",
    items:
      " インフィニティエッジ, ショウジンの矛, ラストウィスパー, デスブレード, ルナーンハリケーン, グインソーレイジブレード",
    anomalies: "ブリー"
  },
   {
    name: "モルガナ",
    items: "ブルーバフ or ショウジンの矛, モレロノミコン, スタティック シヴ",
    anomalies:
      "ブリー, 無駄なし, 連続キル, 逆転劇, フィニッシャー, 魔法の訓練, フリースタイル"
  },
    {
    name: "ラックス",
    items:
      "アークエンジェルスタッフ, グインソーレイジブレード, ヘクステックガンブレード, ショウジンの矛 or ブルーバフ, ラバドンデスキャップ, ナッシャートゥース",
    anomalies: "メイジの鎧, 究極のヒーロー, シュリーマの遺産"
  },
   {
    name: "アーゴット",
    items: "ブラッドサースター or ハンド オブ ジャスティス, 巨人の誓い, ステラックの篭手, インフィニティエッジ",
    anomalies:
      "要塞化, ブルワーク, 超特大サイズ, 攻撃の達人, フリースタイル, 巨人の攻撃, 逆転劇, 力への飢え (Urgot+Sett Comp), ブリー"
  },
  { 
    name: "アカリ",
    items:
      "ハンド オブ ジャスティス or ブラッドサースター, ジュエルガントレット, アイオニックスパーク, ナイトエッジ, クラウンガード, ラバドンデスキャップ",
    anomalies: "ブリー, 最後のチャンス, インビジブル"
  },
  {
    name: "ヴァンダ(ヒーロー)",
    items:
      "ヒーロー:, ブラッドサースター, 巨人の誓い, ハンド オブ ジャスティス, ステラックの篭手 ... , タンク: ガーゴイル ストーンプレート, ワーモグアーマー, リデンプション, プロテクターの誓い",
    anomalies: "ヒーロー:, ブリー, 友情の力, 破竹の勢い"
  },
     {
    name: "カミール",
    items:
      "ブラッドサースター or ハンド オブ ジャスティス, 巨人の誓い, ステラックの篭手, ナイトエッジ, クイックシルバー",
    anomalies:
      "ノックアウト, 最後のチャンス, シュリーマの遺産, ブリー, インビジブル, 強欲の化身"
  },
   {
    name: "ジグス",
    items:
      "ショウジンの矛, ジュエルガントレット, ナッシャートゥース, ラバドンデスキャップ, アークエンジェルスタッフ, モレロノミコン or レッドバフ",
    anomalies:
      "ブリー, 無駄なし, 連続キル, 逆転劇, フィニッシャー, 魔法の訓練, フリースタイル, 魔法の達人"
  },
   {
    name: "セト",
    items:
      "ガーゴイル ストーンプレート, ワーモグアーマー, リデンプション, プロテクターの誓い, アイオニックスパーク or イーブンシュラウド, サンファイアケープ, ドラゴンクロウ, ブランブルベスト",
    anomalies: "超特大サイズ, 要塞化, ブルワーク, 深い根, 石の皮膚"
  },
     {
    name: "ゼリ",
    items:
      "グインソーレイジブレード, インフィニティエッジ, ラストウィスパー, レッドバフ, デスブレード, ジャイアントスレイヤー, フィッシュボーン",
    anomalies:
      "ブリー, 巨人の攻撃, 腕力の訓練, フィニッシャー, 逆転劇"
  },
   {
    name: "トリスターナ",
    items: "グインソーレイジブレード, インフィニティエッジ, ジャイアントスレイヤー, デスブレード, ラストウィスパー",
    anomalies:
      "ブリー, 鷹の目, 巨人の攻撃, 腕力の訓練, 逆転劇"
  },
   {
    name: "ノクターン",
    items:
      "フィッシュボーン, ラピッド ファイアキャノン, スナイパー フォーカス or Emblem, インフィニティエッジ, クイックシルバー, ブラッドサースター or ハンド オブ ジャスティス,ナイトエッジ, 巨人の誓い, ラストウィスパー, ジャイアントスレイヤー",
    anomalies:
      "ブリー, 腕力の訓練, 最後のチャンス, インビジブル, シュリーマの遺産, 鷹の目"
  },
    {
    name: "ブラッドミア(ヒーロー)",
    items: "ヒーロー:, グインソーレイジブレード, アークエンジェルスタッフ, ジュエルガントレット",
    anomalies:
      "ブリー, 無駄なし, 連続キル, 逆転劇, 魔法の達人"
  },
   {
    name: "レオナ",
    items:
      "ガーゴイル ストーンプレート, ワーモグアーマー, リデンプション, プロテクターの誓い, アイオニックスパーク or イーブンシュラウド, サンファイアケープ, ドラゴンクロウ, ブランブルベスト",
    anomalies:
      "超特大サイズ, 要塞化, ブルワーク, 深い根, 石の皮膚, ドラマチックな登場"
  },
   {
    name: "レナータ",
    items: "アークエンジェルスタッフ, ショウジンの矛, ナッシャートゥース, ラバドンデスキャップ, レッドバフ, モレロノミコン, スタティック シヴ",
    anomalies:
      "友情の力, 連続キル, 逆転劇, 魔法の訓練, ブリー, 魔法の達人"
  },
 {
    name: "レル",
    items:
      "ガーゴイル ストーンプレート, ワーモグアーマー, リデンプション, プロテクターの誓い, アイオニックスパーク or イーブンシュラウド, サンファイアケープ, ドラゴンクロウ, ブランブルベスト",
    anomalies:
      "超特大サイズ, 要塞化, ブルワーク, 深い根, 石の皮膚, ドラマチックな登場"
  },
     {
    name: "エズリアル",
    items:
      " インフィニティエッジ, ラストウィスパー, ジャイアントスレイヤー, レッドバフ, デスブレード, ガードブレーカー, レッドバフ, ルナーンハリケーン",
    anomalies: "ブリー, 逆転劇, 巨人の攻撃, 腕力の訓練"
  },
  {
    name: "カシオペア",
    items:
      "ブルーバフ or ショウジンの矛, ナッシャートゥース, ジュエルガントレット, ラバドンデスキャップ, ヘクステックガンブレード, ジャイアントスレイヤー",
    anomalies:
      "無駄なし, 連続キル, 逆転劇, フィニッシャー, 魔法の訓練, フリースタイル"
  },
   {
    name: "ガンクプランク",
    items:
      " インフィニティエッジ, ショウジンの矛, ラストウィスパー, ジャイアントスレイヤー, デスブレード, レッドバフ",
    anomalies: "ブリー, 逆転劇, 巨人の攻撃, 腕力の訓練"
  },
  {
    name: "コグマウ",
    items:
      "ブルーバフ or ショウジンの矛 or グインソーレイジブレード, アークエンジェルスタッフ, ヘクステックガンブレード,ナッシャートゥース, ギャンブラーの剣, ウィッツ エンド, リッチ ベイン",
    anomalies: "ブリー, 超高速, 千の切り傷, 魔法の訓練"
  },
   {
    name: "スウェイン",
    items:
      "CARRY: ショウジンの矛, ガードブレーカー, ジュエルガントレット ... , タンク: ガーゴイル ストーンプレート, ワーモグアーマー, リデンプション, プロテクターの誓い, アイオニックスパーク or イーブンシュラウド, サンファイアケープ, DC, ブランブルベスト",
    anomalies:
      "ブリー, 無駄なし, 連続キル, 逆転劇, フィニッシャー, 魔法の訓練, フリースタイル"
  },
   {
    name: "スカー",
    items:
      "ガーゴイル ストーンプレート, ワーモグアーマー, リデンプション, プロテクターの誓い, アイオニックスパーク or イーブンシュラウド, サンファイアケープ, ドラゴンクロウ, ブランブルベスト",
    anomalies: "超特大サイズ, 要塞化, ブルワーク, 深い根, 石の皮膚"
  },
  {
    name: "スミーチ",
    items:
      "ブラッドサースター or ハンド オブ ジャスティス, 巨人の誓い, ステラックの篭手, ナイトエッジ, インフィニティエッジ, ピットファイターの紋章",
    anomalies: "ブリー, ノックアウト, 最後のチャンス, シュリーマの遺産"
  },
     {
    name: "ツイステッド・フェイト",
    items:
      "ショウジンの矛,ナッシャートゥース, ジュエルガントレット, アークエンジェルスタッフ, モレロノミコン, ラバドンデスキャップ, ジャイアントスレイヤー",
    anomalies: "ブリー, 超高速, 逆転劇, ドラゴンソウル"
  },
  {
    name: "ナミ",
    items:
      "ショウジンの矛 or ブルーバフ,ナッシャートゥース, ラバドンデスキャップ, ジュエルガントレット, モレロノミコン, アークエンジェルスタッフ",
    anomalies:
      "ブリー, 無駄なし, 連続キル, 逆転劇, フィニッシャー, 魔法の訓練, フリースタイル"
  },
   {
    name: "ヌヌ",
    items:
      "ガーゴイル ストーンプレート, ワーモグアーマー, リデンプション, プロテクターの誓い, アイオニックスパーク or イーブンシュラウド, サンファイアケープ, ドラゴンクロウ, ブランブルベスト",
    anomalies:
      "超特大サイズ, スロウクッカー, 要塞化, ブルワーク, 深い根, 石の皮膚, 防護シールド, スカトルの使い魔, ドラマチックな登場"
  },
  {
    name: "ブリッツクランク",
    items:
      "ガーゴイル ストーンプレート, ワーモグアーマー, リデンプション, プロテクターの誓い, アイオニックスパーク or イーブンシュラウド, サンファイアケープ, ドラゴンクロウ, ブランブルベスト",
    anomalies:
      "超特大サイズ, 要塞化, ブルワーク, 深い根, 石の皮膚, 防護シールド, ドラマチックな登場"
  },
  {
    name: "レニー(ヒーロー)",
    items:
      "ヒーロー:, ブラッドサースター, ステラックの篭手, 巨人の誓い ...  , タンク:, ガーゴイル ストーンプレート, ワーモグアーマー, リデンプション, プロテクターの誓い, アイオニックスパーク or イーブンシュラウド, サンファイアケープ",
    anomalies:
      "ヒーロー:, ブリー, シュリーマの遺産 ... , タンク: 超特大サイズ, 要塞化, ブルワーク, 深い根, 石の皮膚"
  },
   {
    name: "ロリス",
    items:
      "ガーゴイル ストーンプレート, ワーモグアーマー, リデンプション, プロテクターの誓い, アイオニックスパーク or イーブンシュラウド, サンファイアケープ,ドラゴンクロウ, ブランブルベスト",
    anomalies:
      "超特大サイズ, 要塞化, ブルワーク, 深い根, 石の皮膚, ドラマチックな登場"
  },
   {
    name: "アンベッサ",
    items:
      "ブラッドサースター or ハンド オブ ジャスティス, 巨人の誓い, ステラックの篭手, ナイトエッジ,  インフィニティエッジ, 執行官の紋章",
    anomalies: "フリースタイル, 巨人の攻撃, 逆転劇"
  },
  {
    name: "イラオイ",
    items:
      "ドラゴンクロウ, ワーモグアーマー, アイオニックスパーク or イーブンシュラウド, サンファイアケープ,リデンプション, プロテクターの誓い, ガーゴイル ストーンプレート, ブランブルベスト",
    anomalies:
      "超特大サイズ, 要塞化, ブルワーク, 深い根, 石の皮膚, ドラマチックな登場"
  },
  {
    name: "ヴァイ",
    items:
      "ブラッドサースター or ハンド オブ ジャスティス, 巨人の誓い, ステラックの篭手, ナイトエッジ, クイックシルバー, インフィニティエッジ",
    anomalies: "逆転劇, 最後のチャンス"
  },
   {
    name: "エコー",
    items:
      "ハンド オブ ジャスティス or ブラッドサースター, アイオニックスパーク, ジュエルガントレット, ラバドンデスキャップ, クラウンガード",
    anomalies: "ブルワーク, 茨の皮膚, 石の皮膚, アルカナの圧倒"
  },
  {
    name: "エリス",
    items:
      "DMG:, ショウジンの矛, ナッシャートゥース, アークエンジェルスタッフ, ジュエルガントレット, ラバドンデスキャップ , タンク:, ガーゴイル ストーンプレート, ワーモグアーマー, リデンプション, プロテクターの誓い, アイオニックスパーク or イーブンシュラウド, サンファイアケープ",
    anomalies:
      "超特大サイズ, 要塞化, ブルワーク, 深い根, 石の皮膚, スカトルの使い魔, ドラマチックな登場"
  },
    {
    name: "ガレン",
    items:
      "ガーゴイル ストーンプレート, ワーモグアーマー, リデンプション, プロテクターの誓い, アイオニックスパーク or イーブンシュラウド, サンファイアケープ, ドラゴンクロウ, ブランブルベスト",
    anomalies:
      "超特大サイズ, 要塞化, ブルワーク, 深い根, 石の皮膚, 防護シールド, 元気の共有 (ワーモグアーマー stack), ドラマチックな登場, スカトルの使い魔"
  },
   {
    name: "コーキ",
    items:
      " インフィニティエッジ, ラストウィスパー, ジャイアントスレイヤー, レッドバフ, デスブレード, ガードブレーカー",
    anomalies:
      "連続キル, 逆転劇, フリースタイル, フィニッシャー, 巨人の攻撃, 攻撃の達人"
  },
  {
    name: "シルコ",
    items: "ショウジンの矛,ナッシャートゥース, ジュエルガントレット, モレロノミコン, ラバドンデスキャップ, アークエンジェルスタッフ",
    anomalies:
      "無駄なし, 連続キル, 逆転劇, フィニッシャー, 魔法の訓練, フリースタイル, 魔法の達人"
  },
  {
    name: "ゾーイ",
    items:
      "ショウジンの矛, ジュエルガントレット, ナッシャートゥース, ラバドンデスキャップ, アークエンジェルスタッフ, モレロノミコン or レッドバフ, ジャイアントスレイヤー, ガードブレーカー",
    anomalies:
      "無駄なし, 連続キル, 逆転劇, フィニッシャー, 魔法の訓練, フリースタイル, エネルギー吸収"
  },
     {
    name: "トゥイッチ",
    items:
      "グインソーレイジブレード, インフィニティエッジ, レッドバフ, ラストウィスパー, ルナーンハリケーン, デスブレード, ジャイアントスレイヤー, ガードブレーカー",
    anomalies:
      "ドラゴンソウル, 鷹の目, 巨人の攻撃, 腕力の訓練, 逆転劇, ミニ・ミー, 狼の使い魔"
  },
   {
    name: "ムンド",
    items:
      "ガーゴイル ストーンプレート, ワーモグアーマー, リデンプション, プロテクターの誓い, アイオニックスパーク or イーブンシュラウド, サンファイアケープ, ドラゴンクロウ, ブランブルベスト",
    anomalies:
      "超特大サイズ, スロウクッカー (ブルーザー紋章), 要塞化, ブルワーク, 深い根, 石の皮膚, 防護シールド, ドラマチックな登場"
  },
  {
    name: "ハイマーディンガー",
    items:
      "ブルーバフ or ショウジンの矛, アークエンジェルスタッフ, ヘクステックガンブレード, ラバドンデスキャップ, ジュエルガントレット, ジャイアントスレイヤー, ガードブレーカー",
    anomalies:
      "無駄なし, 連続キル, 逆転劇, フィニッシャー, 魔法の訓練, フリースタイル"
  },
   {
    name: "ケイトリン",
    items:
      "ブルーバフ,  インフィニティエッジ, ラストウィスパー, デスブレード, ジャイアントスレイヤー, レッドバフ, ガードブレーカー",
    anomalies:
      "逆転劇, 鷹の目, 巨人の攻撃, 腕力の訓練, 無駄なし"
  },
     {
    name: "ジェイス",
    items:
      " インフィニティエッジ, ショウジンの矛, ラストウィスパー, ジャイアントスレイヤー, レッドバフ, デスブレード",
    anomalies: "無駄なし"
  },
  {
    name: "ジンクス",
    items:
      " インフィニティエッジ, ショウジンの矛, ラストウィスパー, ジャイアントスレイヤー, レッドバフ, デスブレード",
    anomalies: "無駄なし, 連続キル, パワー吸収"
  },
  {
    name: "セヴィカ",
    items:
      "ブラッドサースター or ハンド オブ ジャスティス, 巨人の誓い, ステラックの篭手, ナイトエッジ, インフィニティエッジ, 執行官の紋章",
    anomalies: "逆転劇, インビシブル"
  },
   {
    name: "マルザハール",
    items:
      "ショウジンの矛, モレロノミコン or レッドバフ, ナッシャートゥース, ジュエルガントレット, ラバドンデスキャップ, ヘクステックガンブレード",
    anomalies:
      "無駄なし, 連続キル, 逆転劇, フィニッシャー, 魔法の訓練, フリースタイル"
  },
   {
    name: "モルデカイザー",
    items:
      "ブラッドサースター or ハンド オブ ジャスティス, ジュエルガントレット, クイックシルバー, クラウンガード, アイオニックスパーク, ナッシャートゥース",
    anomalies: "シュリーマの遺産"
  },
    {
    name: "ランブル",
    items:
      "ブラッドサースター or ハンド オブ ジャスティス, ジュエルガントレット, ラバドンデスキャップ, クラウンガード, アイオニックスパーク",
    anomalies:
      "深い根 (put Rumble bottom right corner), 最後のチャンス, ダイブイン"
  },
  {
    name: "ルブラン",
    items:
      "ショウジンの矛, ジュエルガントレット,モレロノミコン, ナッシャートゥース, ラバドンデスキャップ, ジャイアントスレイヤー, アークエンジェルスタッフ",
    anomalies:
      "無駄なし, 連続キル, 逆転劇, フィニッシャー, 魔法の訓練, フリースタイル"
  },
    {
    name: "ビクター",
    items:
      "Thief's Gloves, レッドバフ or モレロノミコンs, ラバドンデスキャップ, ジャイアントスレイヤー, デスブレード, ジュエルガントレット, ホライゾン フォーカス",
    anomalies: "逆転劇, 魔法の達人"
  },
  {
    name: "メル",
    items:
      "オートマタの紋章, ブルーバフ or ショウジンの矛 or アダプティブ ヘルム, モレロノミコン or レッドバフ, アークエンジェルスタッフ, スタティック シヴ",
    anomalies: "無駄なし, フィニッシャー"
  },
  {
    name: "ワーウィック",
    items:
      "アートマターの紋章, ナイトエッジ, ブラッドサースター or ハンド オブ ジャスティス, ステラックの篭手, 巨人の誓い",
    anomalies: "腕力の訓練, 逆転劇, 巨人の攻撃"
  }
    
];

const buttonsContainer = document.getElementById("character-buttons");
const characterName = document.getElementById("character-name");
const characterItems = document.getElementById("character-items");
const characterAnomalies = document.getElementById("character-anomalies");

characters.forEach(character => {
    const button = document.createElement("button");
    button.className = "button";
    button.textContent = character.name;
    button.onclick = () => {
        characterName.textContent = character.name;
        
        // アイテム部分に改行を追加
        characterItems.innerHTML = `<strong>アノマリー:</strong><br>${character.items
            .split(', ')  // アノマリーをカンマで分割
            .map(items => `・ ${items}`)  // それぞれのアノマリーに「・」をつける
            .join('<br>')}`;  // 改行でつなげる
        // アノマリー部分に「・」と改行を追加
        characterAnomalies.innerHTML = `<strong>アノマリー:</strong><br>${character.anomalies
            .split(', ')  // アノマリーをカンマで分割
            .map(anomaly => `・ ${anomaly}`)  // それぞれのアノマリーに「・」をつける
            .join('<br>')}`;  // 改行でつなげる
    };
    buttonsContainer.appendChild(button);
});
