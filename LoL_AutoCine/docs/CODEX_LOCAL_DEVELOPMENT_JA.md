# ローカル開発の引き継ぎ手順

ユーザーの希望に合わせて、GitHubへの公開/pushは行っていない。選択済みの`Aimin2222/agdhnteweeffewwff`は別の静的Webアプリであり、LoL AutoCineのソースで置き換えていない。

## 今回のGit管理

- ZIPを`/workspace/LoL_AutoCine`へ新規展開。ZIPには既存Git履歴がなかった。
- `baseline/v5.8.5`の基準コミット`96b928a`で、同梱ソース・既存テスト・資料107ファイルを保持。
- 調査は`codex/initial-audit`ブランチで実施。追加変更は監査Markdownのみ。
- コミットのローカル識別子は`Codex Local <codex@localhost>`。ユーザー自身の名前/メールは設定していない。
- 診断ログ、JSON/CSV、録画、音声、.venv、exeは基準コミットへ追加していない。診断ZIP、テストレポート等も`.git/info/exclude`でローカル除外。
- Git remoteは設定していない。実機v5.8.4のソース/履歴はZIPにないので、手元の比較基準を別途保持する。

元ZIPのSHA256:

```text
e9f789eb2f63270f07f56efbcc1d8291a68cf9628359dd2bd6ecf17326bf7e68
```

## 手元Windowsへの移行

作業後の配布ZIPにはGitで管理するソースと監査資料、`LoL_AutoCine.bundle`を含める。診断ログ、録画、音声、クラウド仮想環境、Windows exeは含めない。付属bundleから以下のように新しいフォルダへ履歴ごと復元できる。

```powershell
git clone --branch codex/initial-audit .\LoL_AutoCine.bundle .\LoL_AutoCine_local
Set-Location .\LoL_AutoCine_local
git branch baseline/v5.8.5 origin/baseline/v5.8.5
git status
git log --oneline --all
```

cloneで作られる`origin`はローカルbundleのパスでありGitHubではない。不要なら`git remote remove origin`で外せる。自身のコミットに使う識別子は、そのリポジトリ内で`git config user.name`と`git config user.email`を設定する。

ZIPのソースフォルダを直接使う場合には、bundle cloneと別々のコピーになる。開発はどちらか一方に統一する。元v5.8.5、実機比較用v5.8.4は別フォルダに残す。

## Windowsの依存関係・起動

```powershell
py -3 -m venv .venv
# requirementsの下限を満たす安定版がないため、今回使った公式開発版を明示。
& .\.venv\Scripts\python.exe -m pip install 'yt-dlp==2026.9.27.232945.dev0'
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt pytest
& .\.venv\Scripts\python.exe -m pip check
cmd /c BUILD_AUDIO_HELPER.bat
& .\.venv\Scripts\python.exe app.py
```

このWindows手順はクラウドで実行していない。MSVC/Windows SDKの自動準備、UAC、Native Process LoopbackはWindows実機で確認する。既存`START.bat`とHelper構築フローはそのまま保持。`START.bat`は現在`py -3 app.py`で起動し、`.venv`を作成する処理はないため、上記では仮想環境のPythonを明示している。`RUN_TESTS.bat`は`.venv\Scripts\python.exe`を使う。

LoLなしのチェック:

```powershell
& .\.venv\Scripts\python.exe -m compileall -q app.py legacy_app.py ui_phase1_prototype.py core tests tools
& .\.venv\Scripts\python.exe -m pytest -q tests/test_allkill_safety.py tests/test_feature_preservation.py tests/test_orbit_target_lock.py tests/test_v31_regressions.py
& .\.venv\Scripts\python.exe tests/test_v585_diagnostics.py
& .\.venv\Scripts\python.exe tests/test_v585_filters.py
& .\.venv\Scripts\python.exe tests/test_checked_dispatch.py
& .\.venv\Scripts\python.exe tests/run_tests.py
```

総合テストの既知の失敗は`CODEX_AUDIT_RESULTS_JA.md`を参照。GUI通し試験`tests/gui_smoke.py`はXvfbを使うLinux向けのモック試験であり、Windows本番起動試験ではない。未対応のテストを通すためにLoL全体音声録音へ切り替えたり、チェックを無効化したりしない。

## クラウドで再開する場合

このタスクの環境は隔離済みなので、既存checkoutを使用し、要求がなければworktreeは作らない。開始時に必ず`AGENTS.md`と引き継ぎ文書を読む。

```bash
cd /workspace/LoL_AutoCine
/workspace/.onboarding-tools/autocine/install.sh
.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_allkill_safety.py tests/test_feature_preservation.py tests/test_orbit_target_lock.py tests/test_v31_regressions.py
.venv/bin/python tests/test_v585_diagnostics.py
.venv/bin/python tests/test_v585_filters.py
/workspace/.onboarding-tools/autocine/with-xvfb.sh .venv/bin/python tests/test_checked_dispatch.py
.venv/bin/python tests/run_tests.py
/workspace/.onboarding-tools/autocine/with-xvfb.sh .venv/bin/python tests/gui_smoke.py
```

仮想ディスプレイのプロセスは再開時に再生成する。GPUがないクラウドで`IMAGEIO_FFMPEG_EXE=/usr/bin/ffmpeg`を常用しない。このシステムFFmpegはNVENCを搭載しているがGPU不在で使えず、現行の搭載判定がNVENCを選んで失敗する。検証したデフォルトはimageio-ffmpeg付属のCPU版。

クラウド環境設定の保存は実行や公開とは別。LoL AutoCineはローカルコミット/ZIP由来でGitHub登録されたcheckoutではない。手元への移行は検証したbundleを使えるが、クラウドの新規タスクへの復元は未検証。元ZIPとbundleをローカル保存し、クラウド公開だけを唯一のバックアップにしない。

## 今後のGit運用

機能ごとに`git switch -c fix/説明`で短いブランチを作り、変更前に対象テストを確認する。差分とテスト結果を記録してレビューし、統合する。回帰時には新しいブランチで基準コミットを参照するか修正コミットを`git revert`し、未保存の変更がある作業場所を強制resetしない。

`git add .`を常用せず、ソース/テスト/資料を明示指定する。`settings.json`、ユーザー参考テンプレート、診断ログ/ZIPにはパスやユーザー情報が入り得るため、追加前に必ず確認する。`.git/info/exclude`はbundleに含まれないので、復元後の自動テスト成果物は同じローカル除外を追加する。
