# v5.9.7 共有API・GPU担当レビュー

受領したUI差分を丸ごとGPU担当ファイルへ上書きせず、次の接続変更だけを個別に採用する。

- `core.effects.Template` の `montage_fx` は既定cutで末尾へ追加。v5.8.5の全位置引数とv5.9.6のscene_keyframesの位置を維持する。添付フルファイルはscene_keyframesを途中へ戻していたため使用しない。描画・GPU・音声・色補正関数は変更しない。
- `core/jobs.py` はモンタージュ作成箇所のみ変更。cutは従来のconcat_clipsを直接使用、flash/darkのみ独立したrender_montageへ渡す。run_auto_editの署名、音声工場、録画、TargetLock、時計、HUDの復元、v5.9.6診断を維持。
- `core/montage_fx.py` はGPU担当として保管。CPU eqによる短い明るさ演出とNVENC/CPUエンコードを区別して診断。NVENC失敗時だけCPU再試行、エンコード失敗・タイムアウト・小さすぎる出力では音声入り元連結へ戻す。全音声をstream copy、強制fpsを除去。
- `ui/scene_batch.py` の既定cutは従来concat。追加演出だけ同じアダプターを呼ぶ。ワーカーへ渡す設定はTemplateのプレーン値でありTk変数を読み取らない。
- 既存camera/clockの承認blobをそのまま維持し、新しいjobsの正確なblobだけ更新。旧レビューでjobsが阻止されること、担当違反と巻き戻しが阻止されることを検証する。

位置引数互換性、CPU/NVENC失敗の区別、fps/audio指定、元映像復旧、ffprobeなしのWindowsバイナリ経路を回帰テストで確認。実FFmpeg出力とUI回帰の結果は統合結果資料へ記録する。Windows・実LoL・Native録音・実NVENC成功はLinuxで代替検証できない。
