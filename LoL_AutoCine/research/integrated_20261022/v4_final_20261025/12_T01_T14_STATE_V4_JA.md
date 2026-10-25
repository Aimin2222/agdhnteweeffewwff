# T01–T14状態

製品全体PASS 0/14。PARTIAL/REPRODUCEDは研究証拠であって製品合格ではありません。各行の元V3入力/期待/手順/log要件をJSONに保持。

| ID | 試験 | 状態 | 今回の証拠 | 残件 |
| --- | --- | --- | --- | --- |
| T01 | BLUE/REDと旧10camera | PARTIAL | CAMERA_SOURCE_MATH_V4.json 48/48; CAMERA_RECIPE_RULE_RESULTS_V4.json 133/133 | real BLUE/RED target, occlusion, TargetLock and3D camera not observed |
| T02 | eventとscene anchor | PARTIAL | independent event grouping/dedup/assist rules and time-map V3 fixtures | real match scan/seek/capture anchors absent |
| T03 | 連続kill/FX重複 | PARTIAL | 23472 geometry scenarios,144 mirror renders,35 moving-FX composites; Flash reproduced | real short/long multi-kill and actual HUD absent |
| T04 | dash/壁/遮蔽/姿勢 | PARTIAL | camera finite-value48 checks; QA semantic fixtures only | no actual wall/dash/target images or engine collision oracle |
| T05 | ゲーム状態QA誤検出 | PARTIAL | WARNING_QA_EXPANDED_V4.json 56/56 declared fixture labels | metadata-based exclusions not video recognition; actual LoL false-positive rate unmeasured |
| T06 | 全687素材 | PARTIAL | 687 preserved hashes;652 original-detail views and3backgrounds;35FX composition | 651 portrait geometries,19 source limitations, actual LoL presentation not approved |
| T07 | 6motionの全過程 | PARTIAL | 144 actual mirror videos decoded;652x6x3x2 numeric cases;24 four-phase sheets viewed | GPU parity and actual LoL/HUD not executed |
| T08 | preview/exact/final | REPRODUCED | PREVIEW_EXPORT_PARITY_V4.json same083 matches1080p bbox, differs1366/1280 | isolated original CPU renderer; live final job parity not executed |
| T09 | multi flash/retime時刻 | REPRODUCED | 48 legacy/v2 +24 v3 +24 causal-gate Flash cases;single event3/3 bit equal in both candidates | v3 future pulse overlap exposed; causal-gate candidate tested; no product fix or live job pass |
| T10 | CPU/GPU FXとencode | PARTIAL | 4 CPU/NVENC encode tests decode120/300; OpenCL failed twice incl alternative | GPU FX BLOCKED OpenCL device creation -12; NVENC is not GPU FX |
| T11 | LoL専用音声/retime | PARTIAL | 12 artificial AV cases;10 within50ms,2 around-58.7ms need review | LoL process audio not captured; no heard-audio quality claim |
| T12 | 同一takeのrecipe比較 | PARTIAL | 6 recipe roundtrip/manual guards,133 independent rules | no adopted recipe / real same-take six outputs |
| T13 | 素材・project互換/保護 | PARTIAL | 1251 protected local files unchanged;70 rows retain IDs/settings contracts; actual Template/SceneProject119/119 independent roundtrip/undo/redo/version/keyframe tests | old project GUI roundtrip and all selected UI connections not executed |
| T14 | job resume/長尺/配布 | PARTIAL | V3 checkpoint/static contract and new handoff acceptance package | long-run resume, clean-PC distribution, cancelled live record NOT_RUN |
