# -*- coding: utf-8 -*-
"""GUIの通し試験 (xvfb + モックAPI + 疑似キャプチャ/疑似音声)。  xvfb-run -a python tests/gui_smoke.py"""
import os, re, subprocess, sys, threading, time, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tests.mock_replay_server import start_mock, HUD_KEYS
st, base, down = start_mock(length=60)
os.environ["AUTOCINE_API_BASE"] = base
os.environ["AUTOCINE_FAKE_CAPTURE"] = "1"
import tkinter as tk
import app as A
from core.effects import FFMPEG

root = tk.Tk()
ap = A.App(root)
out = Path(tempfile.mkdtemp())
ap.out_root = out
ap.apply_template("ジャネット風シネマ")
ap.var_pre.set(2.0); ap.var_post.set(2.0)
TPL = ap.current_template()
assert TPL.hide_hud and TPL.game_audio and TPL.style == "cinema"
done = {"ok": False, "err": None}

# 1) ミラー未開始時はサンプル画像を表示しない。案内表示のみ。
for _ in range(15):
    root.update(); time.sleep(0.02)
assert ap.canvas.find_all(), "ミラー待機中の案内が描画されていない"
sample_preview = False
# 比較スライダ/テンプレ切替でも例外なく描画できる
ap.var_split.set(0.5)
for name in ap.templates:
    ap.var_tpl.set(name); ap.apply_template(name)
    for _ in range(3):
        root.update(); time.sleep(0.05)
ap.apply_template("ジャネット風シネマ"); ap.var_split.set(0.0)
ap.var_pre.set(2.0); ap.var_post.set(2.0)

def work():
    try:
        ap._connect()
        assert len(ap.players) == 10
        ap.locked = ap.players[0]
        ap.on_mirror_start()
        time.sleep(0.5)
        # 2) LoL上でのカメラ演出プレビュー再生 (録画なし)。HUDは終了後に元へ戻る
        st.time = 0.0
        ap._preview_play(TPL, None)
        assert all(st.render[k] for k in HUD_KEYS), "プレビュー後にHUDが戻っていない"
        assert any(not any(h.values()) for h in st.hud_log), "プレビュー中にHUDが隠れていない"
        # 3) ワンクリック全自動
        st.hud_log.clear()
        ap._make(True, TPL, True, "キル")
        assert all(st.render[k] for k in HUD_KEYS), "ジョブ後にHUDが戻っていない"
        assert any(not any(h.values()) for h in st.hud_log), "録画中にHUDが隠れていない"
        done["ok"] = True
    except Exception:
        import traceback; done["err"] = traceback.format_exc()
    done["fin"] = True

threading.Thread(target=work, daemon=True).start()
t0 = time.time(); mirror_drawn = False
while not done.get("fin") and time.time() - t0 < 240:
    root.update()
    if ap.source is not None and ap.canvas.find_all():
        mirror_drawn = True
    time.sleep(0.03)
for _ in range(20):
    root.update(); time.sleep(0.02)
ap.on_exact_still()
print("tree rows:", len(ap.tree.get_children()), "| kills listed:", ap.lb_kills.size(), "| mirror drawn:", mirror_drawn)
print("log:\n" + ap.txt.get("1.0", "end")[-1100:])
files = sorted(p.relative_to(out).as_posix() for p in out.rglob("*.mp4") if "raw" not in p.parts)
print("outputs:", files)
has_audio = []
for f in files:
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", str(out / f)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    has_audio.append("Audio:" in r.stderr)
print("audio in outputs:", has_audio, "| exact still:", (out / "preview_exact.png").exists())
ap.on_mirror_stop(); down()
assert done["ok"], done["err"]
assert files == ["Taki_Ahri/kill_001.mp4", "Taki_Ahri/kill_002.mp4", "Taki_Ahri/kill_003.mp4", "Taki_Ahri/montage.mp4"], files
assert all(has_audio), has_audio
assert mirror_drawn and ap.lb_kills.size() == 4 and (out / "preview_exact.png").exists()
print("GUI SMOKE: PASS")
