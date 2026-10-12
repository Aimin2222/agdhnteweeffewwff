# -*- coding: utf-8 -*-
"""v5.10.26: skyline rejection hints, artifact build identity, approved camera safety."""
from pathlib import Path

from PIL import Image

from core.qa_visual import flat_upper_background_ratio
from core.camera_tuning import shot_tuning


def test_flat_green_out_of_map_frame_is_flagged_as_suspicious():
    frame = Image.new("RGB", (320, 180), (84, 115, 95))
    # Bottom 45% contains active map texture, but the top 55% is empty sky.
    for y in range(107, 180):
        for x in range(320):
            frame.putpixel((x, y), ((x*13)%160+50, (y*3)%90+60, (x+y)%125+30))
    assert flat_upper_background_ratio(frame) > .90


def test_detailed_map_not_marked_flat_sky():
    frame = Image.new("RGB", (320, 180))
    for y in range(180):
        for x in range(320):
            frame.putpixel((x,y), ((x*17+y*7)%200+20,
                                         (x*11+y*23)%200+20,
                                         (x*29+y*3)%200+20))
    assert flat_upper_background_ratio(frame) < .50  # below the actual sky warning threshold


def test_dark_or_white_flash_does_not_count_as_green_sky():
    assert flat_upper_background_ratio(Image.new("RGB",(320,180),(0,0,0)))==0
    assert flat_upper_background_ratio(Image.new("RGB",(320,180),(255,255,255)))==0


def test_camera_qa_embeds_version_and_code_fingerprint():
    root = Path(__file__).resolve().parents[1]
    version=(root/"VERSION.txt").read_text(encoding="utf-8").strip()
    camera_qa=(root/"core"/"camera_qa.py").read_text(encoding="utf-8")
    assert version=="5.10.26-test"
    assert '"version": "5.10.26-test"' in camera_qa
    assert '"installed_version": installed_version' in camera_qa
    assert '"camera_code_fingerprint": camera_fingerprint' in camera_qa
    assert '"version_mismatch": installed_version != "5.10.26-test"' in camera_qa


def test_approved_camera_settings_not_changed_on_stale_visual_evidence():
    red = {
      "third":(1.13,{}), "third_cinema":(.96,{}),
      "fps":(1.0,{}), "lolnam_cinema":(1.0,{"x":-3.0,"y":-3.0}),
      "geo_aim":(1.12,{"x":-4.0}),
    }
    blue = {
      "third":(1.10,{"x":-2.0}),
      "third_cinema":(1.08,{}),"fps":(1.0,{}),
      "lolnam_cinema":(1.08,{"x":2.5}),
      "geo_aim":(1.08,{"x":2.5}),
    }
    for side,modes in (("RED",red),("BLUE",blue)):
        for mode,(distance,angles) in modes.items():
            cfg=shot_tuning(side,mode)
            assert cfg["distance"]==distance
            assert cfg["angles"]==angles
