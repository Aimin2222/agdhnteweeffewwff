# QA30MB保存状況

ソース /workspace/LoL_AutoCine、integration/v5.10.26-qa30mb、HEAD c0d26f192b054dad8eb89fbd829dffe0e33a9d91、remoteなし。取得用 /workspace/agdhnteweeffewwff、codex/lol-autocine-v51026-qa30mb-handoff、origin https://github.com/Aimin2222/agdhnteweeffewwff.git。全551ソースと全134ローカルbranchesをbundleへ保存。

## git log -3 --oneline
```text
c0d26f1 Keep remote QA data plan on the new handoff branch
299ef62 Point developer QA data plan at the bounded upload handoff branch
647234b Preserve original QA timing without frame insertion
```
## 前回v5.10.25からの追加・変更
```text
A	MAKE_CAMERAQA_UPLOAD.bat
M	VERSION.txt
M	core/camera.py
M	core/camera_qa.py
M	core/jobs.py
M	core/qa_package.py
M	core/qa_plan.py
M	core/qa_support.py
A	core/qa_upload.py
M	core/qa_visual.py
M	docs/APP_PACKAGING_PLAN_JA.md
A	docs/CAMERAQA_30MB_DEV_JA.md
A	docs/CODEX_INTEGRATION_v51026_JA.md
A	docs/CODEX_SHARED_API_REVIEW_v5.10.26.json
A	docs/RECEIVED_IMPLEMENTATION_v51026_JA.md
A	docs/WINDOWS_TEST_v51026_JA.md
A	patches/history/v5.10.26/RECEIVED_CODE.patch
A	patches/history/v5.10.26/RECEIVED_README_JA.txt
M	qa/test_plan.json
A	tests/test_gpu_event_visual_identity_v51026.py
A	tests/test_gpu_qa_upload_30mb.py
M	tests/test_v51018_release_qa.py
A	tests/test_v51026_video_framing_and_version.py
M	tools/check_parallel_integration.py
A	tools/make_cameraqa_upload.py
A	tools/package_v51026.py
```
個人録画/設定/診断の追加コミットなし。sourceの最終statusは空、未保存の作業変更なし。main/PR29をマージしない。
