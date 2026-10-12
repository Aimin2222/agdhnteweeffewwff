新規カラー既定を無補正へ変更し、テンプレート選択/旧保存IDを維持。図鑑のopen/close/destroyを追跡して背後パネルwheelを抑制し、従来非同期preview/worker終了を保持する。

ユーザー開始QAにデータ専用JSON計画を追加。既知camera/transition/motionと100〜500MBを検証し、64KB/3秒制限、通信失敗時は付属計画へ戻す。付属計画ではRED/BLUE各5視点（従来4＋geo_aim実験）を実行し、plan未指定APIは従来8本。geoは相対offsetから視線を計算する選択時だけの機能で、既存カメラ式/TargetLock/RED184度/手動向きを保持。数値と実フレーム比較表は参考で、主役・水平線・地形の自動合格判定ではない。

QA結果を500MB以下の直接ZIPに保存。ZIP入れ子なし、大きなMP4は1MBずつstreamして番号partへ分割し復元手順付き。原動画/元JSON/既存ZIPを保持、repeatは新しい名前。出力名を先に計画して最終JSONをZIPにも保存。symlink/外部パスを含めない。前回GPU確認動画/60fps/元音声copy/encoder_policy/素材再利用を維持し、色・DOFを二重適用しない。中止は現在の1本を終えて残り停止、追加比較表/ZIPを開始しない。

受領指定基準へのapply --check/適用と受領v17からの差分13パスをレビューし、現行Codex v17へ機能別統合。GPU/UI/共有8blobを固定レビュー、旧95refと過去配布物/37PNG/GPUエンジン/音声/録画を保持し全99refs bundle保存。

検証: Linux/Xvfb全635成功82.14秒（失敗/skip/除外なし）、分割再結合/元データ保持/再出力/最終JSON一致、データplan拒否/通信fallback、geometry offset整合、短い動画の実フレーム比較/直接ZIP/CRC。Windows/LoL/物理NVIDIA速度とgeo画角は未確認。前回Linux native終了の原因は未確定、今回全件で再発なし。完全ZIPと差分適用の全ソース一致・個人ファイル除外を確認。

前回v5.10.17を比較先とするDraft PR、mainへマージしません。完全ZIP→Download raw file、またはCode→Download ZIP。別フォルダでSTART_GPU.bat、実機手順はdocs/WINDOWS_TEST_v51018_JA.md。

GitHub復元で463ソース/99refs/配布物hash一致。代表126テスト成功12.66秒（強制GCなし・GC有効）。再setupでも463ソース/99refs/3個人設定相当ファイルを保持/status clean。実URLのデータ専用QA計画も取得・検証成功。同じ実行環境の別フォルダ検証でPublish/新タスク/Windows実機とは区別します。
