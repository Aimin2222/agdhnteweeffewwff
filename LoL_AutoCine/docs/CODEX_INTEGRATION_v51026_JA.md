# v5.10.26-test 実イベントQA・版識別・構図調査用候補

受領ZIP CRC/パス/リンク/README/全patch/添付5新規+旧3テスト・実装文書を読み、指定0e8e8f6へ独立apply --check/適用。単体とpatch内byte一致。前回受領v25から7パスだけレビュー統合。実機仕様で指定されたGitHub bec275d4655c09ce674260efe7cadc755d370de6をfetchし、camera/camera_tuning/qa_visual/camera_qaは受領原本とbyte一致、fingerprint 9e8b67454cb10e33を確認。原本archive/received-ui-v51026、code/READMEはhistory、原ZIPはGit外。受領資料の実機/画像/JSON/CI・Release評価はCodex実測と区別。

ユーザー指定の2026-10-13実機results/part001〜003/診断/画像はこの環境にない。ユーザー返信ではPC内にある。既存診断添付は10月9〜10日の旧版で代用しない。実機MP4未解析、BLUE9/10の空・遠景占有/stale原因は未確定。BLUE9/10→6→8、RED1/3保護、RED2/4/5・BLUE7良好維持。BLUE6 X=-2を維持し別枝X=-4を採用しない。カメラ角度/位置/FOVの推測修正なし。同一実機シーンの修正前後合格は未達。

versionは実VERSIONを読む従来仕様を保持。qa_build_version=5.10.26-testを別記しinstalled_versionとの差をversion_mismatchへ。camera.py+camera_tuning.pyのSHA256全64桁と16桁fingerprint。読込失敗はunknown/null/identity_errors、録画を無効にせず警告する。受領の固定versionで新しい版だと誤認させない。QA_Support.collectに任意keyword build_identityを追加、旧呼出しは互換。生成時に版/コードID/不一致を説明文へ含め、既存rawtail/書込失敗保護/中止/最終JSON一致を維持。

上部約55%を48×32へ縮小・RGB16段quantizeで単色割合を測る。黒/白極端色除外。旧2/3時点>0.5のsuspected_sky_or_empty_frameは維持し、中央KILL相当1時点>0.5だけでもkill_frame_needs_human_review/framing_needs_human_reviewを追加。0.538単独の漏れを検証。平坦地形も検知しうる補助で、空/戦闘不在の自動失敗判定ではない。

旧比較のKILLラベルは実キルでなく動画50%だった。QA録画だけ既存playback観測を利用し_replay_event_observerでmonotonic録画時計へ補間。ClipTake末尾qa_event_times任意field、通常effectsのeffect_eventsとは分離しFXをONにしない。CAMERA_QA_TIMING→current.recording_timing→visual_qa。有効event_video_secondsがあればevent±1秒/PRE・KILL・POST、未観測/範囲外/非有限は旧時間割合へ戻しMID表示・duration_fraction_fallback/event_mapping_verified=falseを明記。録画時刻・60fps正規化/音声同期の処理は維持。

既存Replay APIのtop/fps/検証readをCAMERA_QA_BASELINEへ記録（観測position/rotation/mode/selection・対象基準・予定offsetとexpectedworldposition）。追加POST/角度変更なし。ケースbaseline_reads最大12、POSEのfell_back/note/FOVを追加しRED4 topフォールバックを調査可能に。読込フェーズ間でcached/stale座標が混ざる可能性は実ログで確認する。stale防止の既存mode/team cache・normal thirdの4500閾値対策は保持。

全22GPUFX/OpenCL/NVENC/60fps・LoL専用Native Loopback/Helper/WGC/encoderpolicyとFX診断分離・CPUfallback/LatestPreview/Tk所有/ミラー/oneclickQA/cache・partial/二重押し・stop/7ログ各1MB/1MBstream・500MB直接ZIP/最終JSON/参照ZIP・Unicode/CRC/上限/cleanup/37PNG/UIを保持。core/camera.py/jobs.pyはQAの観測・ログだけ追加、カメラの位置/向き式は同一。GPU/音声/録画本体byte不変。

GPU feature/gpu-cameraqa-v51026、UI feature/ui-cameraqa-v51026、integration/v5.10.26、旧127先端・旧配布物保持、全131refs bundle・共有8blobレビュー。

```sh
python tools/check_parallel_integration.py --gpu feature/gpu-cameraqa-v51026 --ui feature/ui-cameraqa-v51026 --integration integration/v5.10.26 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.26.json
python tools/check_text_encoding.py
```

ガードはcommit先端なのでstatusも確認。結果handoff/VERIFICATION_v5.10.26.json。過去native139/132原因未確定。Windows CIスモークは実LoL/NVIDIA構図確認と別。実機改善の完成条件は証拠受領と同一シーン比較待ち。main/PR29マージなし。
