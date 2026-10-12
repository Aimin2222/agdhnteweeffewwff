# -*- coding: utf-8 -*-
"""Source-derived reference image sampling, no fabricated 3D camera claims."""
from pathlib import Path
import json

from PIL import Image


def test_reference_contact_samples_three_times_each(monkeypatch,tmp_path):
    from core import reference_contact
    clips=[tmp_path/"one.mp4",tmp_path/"two.mp4"]
    for clip in clips:
        clip.write_bytes(b"dummy")
    calls=[]
    monkeypatch.setattr(reference_contact,"get_duration",lambda path:10.0)
    def fake_frame(path, seconds):
        calls.append((Path(path).name,seconds))
        tone=int(round(seconds*16))
        return Image.new("RGB",(320,180),(tone,tone,tone))
    monkeypatch.setattr(reference_contact,"frame_at",fake_frame)
    report=reference_contact.extract_reference_contact(clips,tmp_path/"xmedia")
    data=json.loads(report.read_text(encoding="utf-8"))
    assert len(data["videos"])==2
    assert len(calls)==6
    assert [x[1] for x in calls[:3]]==[1.5,5.0,8.5]
    assert (report.parent/"xmedia_reference_contact.jpg").is_file()
    assert data["videos"][0]["mean_visual_difference"]>0
    assert "cannot be recovered" in data["limitations"]


def test_reference_contact_reports_invalid_file_without_losing_others(monkeypatch,tmp_path):
    from core import reference_contact
    good=tmp_path/"good.mp4"
    bad=tmp_path/"bad.mp4"
    good.write_bytes(b"x")
    bad.write_bytes(b"x")
    def probe(p):
        if Path(p)==bad:
            raise RuntimeError("bad mp4")
        return 10.0
    monkeypatch.setattr(reference_contact,"get_duration",probe)
    monkeypatch.setattr(reference_contact,"frame_at",lambda *a,**kw:Image.new("RGB",(320,180),"black"))
    report=reference_contact.extract_reference_contact([good,bad],tmp_path/"qa")
    data=json.loads(report.read_text(encoding="utf-8"))
    assert len(data["videos"])==2
    assert not data["videos"][0]["errors"]
    assert data["videos"][1]["errors"]
