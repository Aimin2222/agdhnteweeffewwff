# v5.10.20-test CameraIsolation / GPUFull

完全版 **handoff/LoL_AutoCine_v5.10.20_CameraIsolation_GPUFull_Windows_Full.zip** をGitHubで開き **Download raw file**。または **codex/lol-autocine-v51020-camera-isolation-handoff** の **Code → Download ZIP**。旧版と別フォルダへ展開してLoL_AutoCine/START_GPU.bat。Windowsへの取得にmainマージ/環境Publishは不要。

校正と安定回転のキャッシュをチーム/カメラモード別に分離。同じモードの再校正安定化を保持。ライブBLUE通常thirdの引き構図・BLUEシネマ/Lolnamのgeo look・FPS距離/向き・auto RED通常thirdの+8度を受領補正候補として統合。REDシネマ/BLUE geoの計算式と手動/keyframe/TargetLockは保持。構図改善はWindows未確認。

かんたん色微調整をチェック直下に表示、OFFでも共有設定を保持。QA比較は従来cut/flash/darkの3種＋6 GPU空間切替＋6 GPUキル登場。全10種の通常演出を削除しない。任意のMAKE_REFERENCE_SHEETS.batで参照動画の6時点JPEG/JSONをローカルZIP化。空フォルダも有効ZIP、元動画不変・外部送信なし。静止比較ツールはCPU抽出、通常GPUエンコードとは別。

GPU全22FX/60fps時刻/LoL専用音声/NVENC/選択policy/CPU fallback診断/500MB直接ZIP/1MBstream/既存ミラー応答修正/前回capture終了テスト同期を保持。Linux/Xvfb全675成功、失敗/skip/除外なし、54.082秒。実GPU/Windows/LoL画角と性能は未確認。過去Linux native139/132は原因未確定、今回の成功を恒久修正とは扱わない。

完全ZIP484ファイル、差分適用後486ソース一致、全107refs bundle（Windows改行変換をbinary属性で防止）。差分基準は前回Codex v5.10.19-test。実機手順はLoL_AutoCine/docs/WINDOWS_TEST_v51020_JA.md。

## ローカルGit復元
```sh
git clone --single-branch --branch codex/lol-autocine-v51020-camera-isolation-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v51020_Handoff
git clone --branch integration/v5.10.20 LoL_AutoCine_v51020_Handoff/handoff/LoL_AutoCine_v5.10.20_CameraIsolation_GPUFull_all_branches.bundle LoL_AutoCine_v51020_Dev
cd LoL_AutoCine_v51020_Dev
git branch feature/gpu-cameraqa-v51020 origin/feature/gpu-cameraqa-v51020
git branch feature/ui-cameraqa-v51020 origin/feature/ui-cameraqa-v51020
git status --short
```

全refsはorigin/*へ復元。originはローカルbundle。設定/録画/プロジェクトを保管。担当ガードはdocs/CODEX_INTEGRATION_v51020_JA.md。

GitHubから別checkout/bundle復元で全486ソース/107refs/ZIP・bundle hashes一致。復元先代表166成功13.00秒、失敗/skip/除外なし、GC有効・強制GCなし。再setupで486ソース/107refs/3個人設定相当のバイト保持/status clean。これは同一クラウド内の別フォルダ検証で新しいcloud task/Windows/Publish検証とは別。環境install_script/start_skillをrevision38へ保存してreadback確認、他の既知設定保持、Publishは未実行。次回環境へ反映する場合だけ環境設定で確認・保存後Publish。
