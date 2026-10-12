#!/usr/bin/env bash
set -euo pipefail
autocine_root=${AUTOCINE_SETUP_ROOT:-/workspace/LoL_AutoCine}
# Restore the preserved source and all one hundred three branches only when the target is absent.
# Fetch changes Git objects/remote refs only; never switch/reset the website checkout.
if [ ! -e "$autocine_root" ]; then
  mkdir -p /workspace/scratch
  restore_bundle=/workspace/scratch/LoL_AutoCine_v5.10.19_CameraUI_SpatialQA_GPUFull_github_restore.bundle
  git -C /workspace/agdhnteweeffewwff fetch origin \
    refs/heads/codex/lol-autocine-v51019-camera-ui-qa-handoff:refs/remotes/origin/codex/lol-autocine-v51019-camera-ui-qa-handoff
  git -C /workspace/agdhnteweeffewwff show \
    43baa43f379daba81315489dd5a230119e2c1aed:handoff/LoL_AutoCine_v5.10.19_CameraUI_SpatialQA_GPUFull_all_branches.bundle > "$restore_bundle"
  printf '%s  %s\n' 689160c7adfe225e6167f1d941e70182b5b8d6c63b5b6801001ebf39cf5cd2b1 "$restore_bundle" | sha256sum -c -
  git clone --branch integration/v5.10.19 "$restore_bundle" "$autocine_root"
  while read -r branch_sha branch_ref; do
    case "$branch_ref" in
      refs/heads/*)
        if ! git -C "$autocine_root" show-ref --verify --quiet "$branch_ref"; then
          git -C "$autocine_root" branch "${branch_ref#refs/heads/}" "$branch_sha"
        fi
        ;;
    esac
  done < <(git bundle list-heads "$restore_bundle")
fi
cd "$autocine_root"
test -f AGENTS.md
test -f requirements.txt
export PIP_CACHE_DIR=/workspace/.onboarding-tools/pip-cache
mkdir -p "$PIP_CACHE_DIR"
python3 -m venv .venv
# The stable releases currently do not satisfy yt-dlp>=2026.09.01.
# Pin the official PyPI prerelease already validated in this environment.
.venv/bin/python -m pip install --disable-pip-version-check \
  numpy==2.5.3 pillow==12.3.0 imageio-ffmpeg==0.6.0 psutil==7.2.2 \
  yt-dlp==2026.9.27.232945.dev0 pytest==9.1.1 -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python - <<'PY'
from pathlib import Path
import subprocess
exclude=Path(subprocess.check_output(['git','rev-parse','--git-path','info/exclude'],text=True).strip())
exclude.parent.mkdir(parents=True,exist_ok=True)
contents=exclude.read_text() if exclude.exists() else ''
for line in ('/dist/','/projects/','/settings.json','/diagnostics/test_report.txt','/diagnostics/last_error.txt','/AutoCine_Diagnostics.zip'):
    if line not in contents.splitlines(): contents=contents.rstrip()+'\n'+line+'\n'
exclude.write_text(contents)
PY
compile_targets=(app.py legacy_app.py ui_phase1_prototype.py core tests tools)
if [ -d ui ]; then compile_targets+=(ui); fi
.venv/bin/python -m compileall -q "${compile_targets[@]}"

# Install Xvfb only under /workspace; keep Debian signature and package hash verification.
xvfb_root=/workspace/.onboarding-tools/xvfb/root
if [ ! -x "$xvfb_root/usr/bin/Xvfb" ]; then
  . /etc/os-release
  if [ "${ID:-}" != debian ] || [ "${VERSION_ID:-}" != 13 ]; then
    echo 'This Xvfb setup expects Debian 13; adapt to the current distribution.' >&2
    exit 2
  fi
  apt_root=/workspace/.onboarding-tools/apt
  mkdir -p "$apt_root/lists/partial" "$apt_root/cache/archives/partial" \
    /workspace/.onboarding-tools/xvfb/packages
  cat > "$apt_root/sources.list" <<'EOF'
deb [signed-by=/usr/share/keyrings/debian-archive-keyring.gpg] https://deb.debian.org/debian trixie main
EOF
  cat > "$apt_root/local.conf" <<'EOF'
#clear APT::Update::Post-Invoke;
#clear APT::Update::Post-Invoke-Success;
#clear DPkg::Post-Invoke;
EOF
  apt_options=(-c "$apt_root/local.conf" -o Dir::Etc::parts=- -o Dir::Etc::main=-
    -o "Dir::Etc::sourcelist=$apt_root/sources.list" -o Dir::Etc::sourceparts=-
    -o "Dir::State::lists=$apt_root/lists" -o "Dir::Cache=$apt_root/cache")
  apt-get "${apt_options[@]}" -o APT::Update::Error-Mode=any update
  (
    cd /workspace/.onboarding-tools/xvfb/packages
    apt-get "${apt_options[@]}" download xvfb libxfont2 xserver-common xauth
    for package in *.deb; do dpkg-deb -x "$package" "$xvfb_root"; done
  )
fi
mkdir -p /workspace/.onboarding-tools/autocine
cat > /workspace/.onboarding-tools/autocine/with-xvfb.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
xvfb_root=/workspace/.onboarding-tools/xvfb/root
export PATH="$xvfb_root/usr/bin:$PATH"
export LD_LIBRARY_PATH="$xvfb_root/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec "$xvfb_root/usr/bin/xvfb-run" -a "$@"
EOF
chmod +x /workspace/.onboarding-tools/autocine/with-xvfb.sh
/workspace/.onboarding-tools/autocine/with-xvfb.sh .venv/bin/python -c \
  'import tkinter as tk; r=tk.Tk(); print("Tk/Xvfb ready"); r.destroy()'
git diff --exit-code -- app.py legacy_app.py ui_phase1_prototype.py core tests requirements.txt

