# -*- coding: utf-8 -*-
"""自動テスト (LoL実機なしでパイプライン全体を検証)。  python tests/run_tests.py"""
from __future__ import annotations
import json
import re
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import paths                                   # noqa: E402
from core.camera import CameraPlan, INTENSITY, smoothstep  # noqa: E402
from core.capture import SyntheticSource, CaptureError, find_lol_hwnd  # noqa: E402
from core.effects import (Template, one_click_templates, apply_effects, FFMPEG,   # noqa: E402
                          GRADES, find_jp_font)
from core.jobs import run_auto_edit, StallError, record_one_clip     # noqa: E402
from core.players import parse_players, is_player_name   # noqa: E402
from core.replay_api import ReplayAPI                    # noqa: E402
from core.audio import SyntheticAudio, PaddedWavWriter   # noqa: E402
from core.hud import hide_values                         # noqa: E402
import core.preview as PV                                # noqa: E402
from core.scanner import scan_kills, group_clips         # noqa: E402
from tests.mock_replay_server import start_mock          # noqa: E402

RESULTS = []


def probe(path: Path) -> dict:
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", str(path)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    s = r.stderr
    d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", s)
    dur = int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3)) if d else -1
    fps = re.search(r"([\d.]+) fps", s)
    return {"dur": dur, "fps": float(fps.group(1)) if fps else -1, "text": s}


def test(fn):
    def w():
        t0 = time.time()
        try:
            fn()
            RESULTS.append((fn.__name__, True, f"{time.time() - t0:.1f}s", ""))
        except Exception as e:
            RESULTS.append((fn.__name__, False, f"{time.time() - t0:.1f}s", traceback.format_exc()[-900:]))
    w.__name__ = fn.__name__
    return w


@test
def t01_game_cfg_patch():
    with tempfile.TemporaryDirectory() as d:
        cfg = Path(d) / "Config" / "game.cfg"
        assert not paths.replay_api_enabled(cfg)
        paths.enable_replay_api(cfg)                 # 新規作成 (Configフォルダも作る = 「パスが見つかりません」対策)
        assert paths.replay_api_enabled(cfg)
        cfg.write_text("[General]\nWidth=1920\n[Performance]\nShadows=1\n", encoding="utf-8")
        paths.enable_replay_api(cfg)
        txt = cfg.read_text(encoding="utf-8")
        assert txt.index("EnableReplayApi=1") < txt.index("[Performance]"), txt
        assert list(cfg.parent.glob("game.cfg.bak_*")), "バックアップが無い"
        paths.enable_replay_api(cfg)                 # 冪等
        assert txt.count("EnableReplayApi") == 1


@test
def t02_players_ten():
    st, base, down = start_mock()
    try:
        ps = parse_players(ReplayAPI(base).playerlist())
        assert len(ps) == 10, len(ps)
        assert [p.team for p in ps[:5]] == ["ORDER"] * 5 and [p.team for p in ps[5:]] == ["CHAOS"] * 5
        assert is_player_name("Taki#JP0", ps[0]) and is_player_name("Taki", ps[0]) and not is_player_name("Bob#JP1", ps[0])
    finally:
        down()


@test
def t03_scan_only_selected_player():
    st, base, down = start_mock(length=60)
    try:
        api = ReplayAPI(base)
        ps = parse_players(api.playerlist())
        prog = []
        res = scan_kills(api, ps[0], progress=lambda *a: prog.append(a), diag_dir=ROOT / "diagnostics")
        assert res.complete
        ts = [k.time for k in res.kills]
        assert ts == [10.0, 13.0, 30.0, 50.0], ts           # 他人のキルは混ざらない / 表記ゆれも拾う
        assert [k.multikill for k in res.kills] == [1, 2, 1, 1]
        assert prog and prog[-1][0] == 100.0 and prog[-1][3] >= 7 and prog[-1][4] == 4
        j = json.loads((ROOT / "diagnostics" / "last_scan_events.json").read_text(encoding="utf-8"))
        assert j["target_kills"] == 4 and j["total_events"] >= 7
        # 別プレイヤーを選べばそのキルだけ
        st.time = 0.0
        res2 = scan_kills(api, ps[1])
        assert [k.time for k in res2.kills] == [20.0]
    finally:
        down()


@test
def t04_group_clips():
    from core.scanner import Kill
    ks = [Kill(1, 10, "a", "b", []), Kill(2, 13, "a", "c", []), Kill(3, 30, "a", "d", [])]
    g = group_clips(ks, 2, 2, True)
    assert [(s, e, len(k)) for s, e, k in g] == [(8, 15, 2), (28, 32, 1)], g
    assert len(group_clips(ks, 2, 2, False)) == 3


@test
def t05_camera_curves_smooth():
    for style in ("cinema", "cinema_top", "follow", "top"):
        for amp in INTENSITY.values():
            p = CameraPlan(style=style, intensity=amp, kill_time=10.0)
            prev_s, prev_f, prev_d = p.speed_at(0), p.fov_at(0), p.scale_at(0)
            mn_s, mn_f, mn_d = 9, 99, 9
            t = 0.0
            while t < 20:
                s_, f, d = p.speed_at(t), p.fov_at(t), p.scale_at(t)
                assert abs(s_ - prev_s) < 0.03 and abs(f - prev_f) < 0.35 and abs(d - prev_d) < 0.012, (style, amp, t)
                prev_s, prev_f, prev_d = s_, f, d
                mn_s, mn_f, mn_d = min(mn_s, s_), min(mn_f, f), min(mn_d, d)
                t += 0.02
            if style in ("cinema", "cinema_top"):
                assert mn_s <= 0.71, (style, amp, mn_s)
            if style == "cinema_top":
                assert mn_f < p.base_fov - 3
            if style == "cinema":
                assert mn_d < p.dist_scale * 0.8, (amp, mn_d)         # ドリーインで寄る
                assert mn_d >= 0.22                                    # 寄りすぎない(地面に近づきすぎない)
            if style in ("follow", "top"):
                assert mn_s == 1.0 and mn_f == p.base_fov
    a_, b_ = CameraPlan("cinema", 0.6, 10).speed_at(10), CameraPlan("cinema", 1.4, 10).speed_at(10)
    assert b_ <= a_
    assert CameraPlan("cinema", 1.0, 10).speed_at(0) == 1.0 and CameraPlan("cinema", 1.0, 10).speed_at(30) == 1.0


@test
def t06_effects_all_templates_and_grades():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        src = d / "src.mp4"
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=60:duration=3",
                        "-pix_fmt", "yuv420p", str(src)], check=True)
        from core.scanner import Kill
        ks = [Kill(1, 1, "a", "b", [])] * 2
        # 全テンプレ + 全グレード
        for name, tpl in one_click_templates().items():
            out = d / f"o_{abs(hash(name))}.mp4"
            apply_effects(src, out, tpl, 3.0, ks)
            p = probe(out)
            assert out.exists() and abs(p["dur"] - 3.0) < 0.3 and abs(p["fps"] - 60) < 1, (name, p["dur"], p["fps"])
        for g in GRADES:
            tpl = Template(grade=g, grade_strength=1.0, temperature=0.5, bpm=120, bars=0.5, transition="flash",
                           title_text="日本語タイトル テスト")
            out = d / f"g_{g}.mp4"
            apply_effects(src, out, tpl, 3.0, ks)
            assert out.exists() and out.stat().st_size > 1000, g
        assert find_jp_font() is not None or sys.platform == "win32"


@test
def t07_no_desktop_fallback():
    assert find_lol_hwnd() is None               # 非Windows/LoL無し -> None
    from core.capture import WGCWindowSource
    try:
        WGCWindowSource().start()
        raise AssertionError("例外が出るべき")
    except CaptureError as e:
        assert "フォールバックは行いません" in str(e)


@test
def t08_end_to_end_auto_edit():
    st, base, down = start_mock(length=60)
    try:
        api = ReplayAPI(base)
        ps = parse_players(api.playerlist())
        player = ps[0]
        scan = scan_kills(api, player)
        assert len(scan.kills) == 4
        src = SyntheticSource(time_fn=lambda: st.time)
        src.start()
        tpl = one_click_templates()["ジャネット風シネマ"]
        tpl.pre, tpl.post = 2.0, 2.0
        events = []
        with tempfile.TemporaryDirectory() as d:
            res = run_auto_edit(api, src, player, scan.kills, tpl, Path(d), make_montage=True,
                                progress=lambda *a: events.append(a), log=print,
                                audio_factory=lambda p: SyntheticAudio(p))
            src.stop()
            assert not res.failed, res.failed
            names = [p.name for p in res.outputs]
            assert names == ["kill_001.mp4", "kill_002.mp4", "kill_003.mp4"], names   # 10&13は1本にまとまる
            for p in res.outputs:
                pr = probe(p)
                assert abs(pr["fps"] - 60) < 1, pr["fps"]
                assert pr["dur"] > 2.5, (p.name, pr["dur"])
            assert res.montage and probe(res.montage)["dur"] > 10
            assert events[-1][0] == 3 and events[-1][2] == 100.0
            # 毎クリップ同じプレイヤーがカメラ対象
            sel = [r["selectionName"] for r in st.render_log if "selectionName" in r]
            assert len(sel) >= 3 and set(sel) == {player.selection_name}, sel
            # 地面に埋まらない: 録画中に送ったFPS風カメラのオフセット高さは常に十分上
            offs = [r["selectionOffset"]["y"] for r in st.render_log
                    if "selectionOffset" in r and r["selectionOffset"]["y"] > 0]
            assert len(offs) > 10 and min(offs) >= 350, (len(offs), min(offs) if offs else None)
            # ゲーム音が入っている (音声ストリームあり・長さが映像と一致)
            for p in res.outputs:
                pr = probe(p)
                assert "Audio:" in pr["text"], p.name
            # FOV/速度が実際に動かされた (シネマ)
            fovs = [r["fieldOfView"] for r in st.render_log if "fieldOfView" in r]
            assert min(fovs) < 58.5, min(fovs)
            assert min(st.speed_log) < 0.7, min(st.speed_log)
            assert (Path(d) / "Taki_Ahri" / "raw" / "raw_001.mp4").exists()
    finally:
        down()


@test
def t09_stall_guard_no_same_frame_recording():
    st, base, down = start_mock(length=60, stuck=True)    # 再生が一切進まない環境
    try:
        api = ReplayAPI(base)
        ps = parse_players(api.playerlist())
        src = SyntheticSource(time_fn=lambda: st.time)
        src.start()
        from core import jobs
        import core.jobs as J
        from core.scanner import Kill
        orig = time.time
        tpl = Template(style="follow", pre=1, post=1)
        with tempfile.TemporaryDirectory() as d:
            t0 = time.time()
            try:
                record_one_clip(api, src, ps[0], tpl, 8.0, 12.0, [Kill(1, 10, "Taki", "x", [])], Path(d) / "r.mp4")
                raise AssertionError("StallError になるべき")
            except StallError:
                pass
            assert time.time() - t0 < 14, "検知が遅すぎる"
        src.stop()
    finally:
        down()


@test
def t10_utf8_paths_and_names():
    with tempfile.TemporaryDirectory() as d:
        from core.jobs import safe_name
        assert safe_name('たき: 田中/Ahri*?') == "たき_田中_Ahri"
        out = Path(d) / "出力 フォルダ" / "日本語"
        out.mkdir(parents=True)
        src = out / "元.mp4"
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=blue:s=320x180:r=60:d=1",
                        "-pix_fmt", "yuv420p", str(src)], check=True)
        dst = out / "結果.mp4"
        apply_effects(src, dst, Template(title_text="ペンタキル！"), 1.0, [])
        assert dst.exists()


@test
def t11_hud_safe_mode_does_not_touch_replay():
    st, base, down = start_mock(length=60)
    try:
        api = ReplayAPI(base)
        player = parse_players(api.playerlist())[0]
        from core.scanner import Kill
        src = SyntheticSource(time_fn=lambda: st.time)
        src.start()
        tpl = Template(style="top", pre=1, post=1, hide_hud=True)
        with tempfile.TemporaryDirectory() as d:
            res = run_auto_edit(api, src, player, [Kill(1, 10, "Taki", "x", [])], tpl, Path(d), make_montage=False)
            src.stop()
            assert not res.failed, res.failed
        assert not st.hud_log, "安全モードなのにReplay HUDを変更した"
        assert all(st.render[k] for k in hide_values()), "安全モードでHUD状態が変化した"
        # HPバーだけ残す設定値の生成自体は維持
        # HPバーだけ残すオプション
        vals = hide_values(keep_champion_bars=True)
        assert vals["healthBarChampions"] is True and vals["interfaceAll"] is False and vals["floatingText"] is False
    finally:
        down()


@test
def t12_fps_camera_falls_back_to_top_instead_of_underground():
    from core.camera import attach_to_player, MIN_CLEARANCE
    from tests.mock_replay_server import champ_pos
    # 正常な環境: FPS風カメラが地面より十分上に置かれる
    st, base, down = start_mock()
    try:
        api = ReplayAPI(base)
        p = parse_players(api.playerlist())[0]
        rig = attach_to_player(api, p, "cinema", settle=0.0)
        assert rig.mode == "fps" and not rig.fell_back, rig
        pos = api.render()["cameraPosition"]
        assert pos["y"] - champ_pos(p.selection_name)[1] >= MIN_CLEARANCE
        assert api.render()["cameraRotation"] == {"x": 0.0, "y": -54.0, "z": 0.0}    # 標準の視線をそのまま使う
    finally:
        down()
    # オフセットが効かず足元(地面)に置かれてしまう環境 -> 俯瞰へ自動フォールバック
    st, base, down = start_mock(fps_broken=True)
    try:
        api = ReplayAPI(base)
        p = parse_players(api.playerlist())[0]
        logs = []
        rig = attach_to_player(api, p, "cinema", settle=0.0, log=logs.append)
        assert rig.mode == "top" and rig.fell_back and logs, (rig, logs)
        assert api.render()["cameraMode"] == "top"
        # その状態で録画しても fps オフセットは送られない
        src = SyntheticSource(time_fn=lambda: st.time)
        src.start()
        with tempfile.TemporaryDirectory() as d:
            from core.scanner import Kill
            take = record_one_clip(api, src, p, Template(style="cinema", pre=1, post=1), 8.0, 12.0,
                                   [Kill(1, 10, "Taki", "x", [])], Path(d) / "r.mp4")
            assert take.rig.mode == "top"
        src.stop()
        # 試し置き(検証用)の後に俯瞰へ戻した時点から、録画中に FPS オフセットは一切送られない
        last_top = max(i for i, r in enumerate(st.render_log) if r.get("cameraMode") == "top" and r.get("cameraAttached"))
        after = st.render_log[last_top + 1:]
        assert after and not [r for r in after if r.get("selectionOffset", {}).get("y", 0) > 0]
    finally:
        down()


@test
def t13_audio_mix_and_sync():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        src = d / "src.mp4"
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=60:duration=4",
                        "-pix_fmt", "yuv420p", str(src)], check=True)
        wav = d / "game.wav"
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=330:d=4.5", str(wav)], check=True)
        bgm = d / "bgm.wav"
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=110:d=2", str(bgm)], check=True)
        # ゲーム音のみ / ゲーム音+BGM(BGMは短くてもループ) / BGMのみ / 音声なし
        for name, game, b, gflag in (("g", wav, "", True), ("gb", wav, str(bgm), True), ("b", None, str(bgm), True),
                                      ("n", None, "", True), ("off", wav, "", False)):
            out = d / f"o_{name}.mp4"
            apply_effects(src, out, Template(bgm_path=b, game_audio=gflag, title_text="T"), 4.0, [],
                          game_audio=game, audio_offset=0.3)
            pr = probe(out)
            has_a = "Audio:" in pr["text"]
            assert has_a == (name in ("g", "gb", "b")), (name, has_a)
            assert abs(pr["dur"] - 4.0) < 0.3, (name, pr["dur"])
            if has_a:
                # 音声が無音ではない
                r = subprocess.run([FFMPEG, "-i", str(out), "-af", "volumedetect", "-vn", "-f", "null", "-"],
                                   capture_output=True, text=True, encoding="utf-8", errors="replace")
                m = re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr)
                assert m and float(m.group(1)) > -60, (name, r.stderr[-200:])


@test
def t14_padded_wav_fills_silence_gaps():
    import wave
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "a.wav"
        w = PaddedWavWriter(p, rate=1000, channels=1, t0=0.0)
        w.write(b"\x01\x00" * 100, now=0.1)           # 最初の100フレーム
        w.write(b"\x01\x00" * 100, now=1.2)           # WASAPI は無音中データを送らない -> 約1000フレーム欠落
        dur = w.finish(now=2.0)
        assert abs(dur - 2.0) < 0.01, dur
        with wave.open(str(p)) as r:
            assert r.getnframes() == 2000


@test
def t15_vignette_strength_is_monotonic():
    from core.effects import vignette_angle, build_graph
    angs = [vignette_angle(v / 10) for v in range(11)]
    assert all(b > a for a, b in zip(angs, angs[1:])), angs      # 強度を上げるほど四隅が暗くなる(v1.0では逆だった)
    g0 = build_graph(Template(vignette=0.0), 3.0, False)
    assert "vignette" not in g0


@test
def t16_template_preview():
    import numpy as np
    from PIL import Image
    img = PV.sample_scene(480, 270)
    base = Template(grade="standard", grade_strength=0, contrast=1.0, vignette=0, grain=0, bloom=0, bars=0,
                    temperature=0, transition="cut")
    same = PV.grade_rgb(img, base)
    assert np.abs(same.astype(int) - img.astype(int)).mean() < 2          # 何も効かせない設定なら不変
    noir = PV.grade_rgb(img, Template(grade="noir", grade_strength=1.0, vignette=0, grain=0, bloom=0, bars=0))
    sat = lambda a: (a.max(-1).astype(int) - a.min(-1).astype(int)).mean()
    assert sat(noir) < sat(img) * 0.5                                      # ノワールは彩度が落ちる
    vig = PV.grade_rgb(img, Template(grade="standard", grade_strength=0, vignette=1.0, grain=0, bloom=0, bars=0))
    assert vig[:30, :30].mean() < img[:30, :30].mean() * 0.8 and abs(int(vig[135, 240].mean()) - int(img[135, 240].mean())) < 6
    bars = PV.grade_rgb(img, Template(grade="standard", grade_strength=0, vignette=0, grain=0, bloom=0, bars=1.0))
    assert bars[:10].max() == 0 and bars[-10:].max() == 0 and bars[135].max() > 0   # シネマ枠
    cmp_ = PV.compose_compare(img, Template(grade="noir", grade_strength=1.0), "", split=0.5)
    assert np.array_equal(cmp_[:, :200], img[:, :200]) and not np.array_equal(cmp_[:, 300:], img[:, 300:])  # 左=適用前
    with tempfile.TemporaryDirectory() as d:
        out = PV.render_exact_still(img, one_click_templates()["ジャネット風シネマ"], Path(d) / "x.png")
        assert Image.open(out).size == (480, 270)
    # 近似プレビューが ffmpeg の最終出力と大きくズレない (平均誤差 < 12/255)
    for name, tpl in one_click_templates().items():
        t2 = Template(**{**tpl.to_dict(), "grain": 0.0, "transition": "cut", "bpm": 0.0})
        with tempfile.TemporaryDirectory() as d:
            ex = np.asarray(Image.open(PV.render_exact_still(img, t2, Path(d) / "e.png")).convert("RGB")).astype(float)
        pv = PV.grade_rgb(img, t2).astype(float)
        assert np.abs(ex - pv).mean() < 12, (name, np.abs(ex - pv).mean())


if __name__ == "__main__":
    from tests.test_feature_preservation import test_preserved_effect_fields, test_preserved_templates, test_camera_controls_all_modes, test_output_fps_split, test_fog_presets
    for _f in (test_preserved_effect_fields, test_preserved_templates, test_camera_controls_all_modes, test_output_fps_split, test_fog_presets):
        _f()
    for f in [t01_game_cfg_patch, t02_players_ten, t03_scan_only_selected_player, t04_group_clips,
              t05_camera_curves_smooth, t06_effects_all_templates_and_grades, t07_no_desktop_fallback,
              t08_end_to_end_auto_edit, t09_stall_guard_no_same_frame_recording, t10_utf8_paths_and_names,
              t11_hud_safe_mode_does_not_touch_replay, t12_fps_camera_falls_back_to_top_instead_of_underground,
              t13_audio_mix_and_sync, t14_padded_wav_fills_silence_gaps, t15_vignette_strength_is_monotonic,
              t16_template_preview]:
        f()
    ok = True
    lines = []
    for name, passed, dt, err in RESULTS:
        lines.append(f"{'PASS' if passed else 'FAIL'}  {name}  ({dt})")
        if not passed:
            ok = False
            lines.append(err)
    rep = "\n".join(lines)
    print("\n" + rep)
    (ROOT / "diagnostics" / "test_report.txt").write_text(rep + "\n", encoding="utf-8")
    sys.exit(0 if ok else 1)
