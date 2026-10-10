# -*- coding: utf-8 -*-
from core.camera import CameraPlan, RigInfo

def rig():
    return RigInfo(mode='fps', third=True, P=(0,60,0), v=(0,1800,-1300),
                   rot={'x':0.0,'y':-54.0,'z':0.0}, pitch_axis='y', pitch_sign=1.0,
                   h=(0.0,-1.0))

def test_zero_degree_keeps_base_view():
    p=CameraPlan(style='third', third_yaw=0, third_dist=950, rig=rig())
    off,_=p.third_pose_at(0)
    r=p.rotation_at(0)
    assert abs(off[0]) < 1e-6 and off[2] < 0
    assert r['x'] == 0

def test_positive_90_keeps_target_lock():
    p=CameraPlan(style='third', third_yaw=90, third_dist=950, rig=rig())
    off,_=p.third_pose_at(0)
    r=p.rotation_at(0)
    assert off[0] > 0 and abs(off[2]) < 1e-6
    assert r['x'] == -90

def test_negative_90_keeps_target_lock():
    p=CameraPlan(style='third', third_yaw=-90, third_dist=950, rig=rig())
    off,_=p.third_pose_at(0)
    r=p.rotation_at(0)
    assert off[0] < 0 and abs(off[2]) < 1e-6
    assert r['x'] == 90
