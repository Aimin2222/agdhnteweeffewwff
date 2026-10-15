# -*- coding: utf-8 -*-
"""Plot the existing CameraPlan's actual time samples; preview only, no native API calls.

The graph samples normalized orbit, lens FOV and camera distance from the same
CameraPlan math used by the renderer, with a synthetic target rig.
"""
from __future__ import annotations
import tkinter as tk
import math
from core.camera import CameraPlan, RigInfo
from .scene_project import Shot


def sample_motion(shot: Shot, samples=81, base_distance=950):
    amp={'natural':0.6, 'standard':1.0,'strong':1.4}.get(shot.intensity,1.0)
    plan=CameraPlan(style='lolnam_cinema',intensity=amp,kill_time=0,
                    kill_times=(0,),third_dist=base_distance,third_yaw=shot.yaw,
                    motion_arc=shot.arc,motion_dolly=shot.dolly,motion_profile=shot.profile,
                    scene_keyframes=tuple(shot.keyframes),
                    rig=RigInfo(mode='fps',third=True,h=(0.0,-1.0)))
    points=[]
    for i in range(samples):
        t=-shot.pre+(shot.pre+shot.post)*i/max(1,samples-1)
        offset,_=plan.third_pose_at(t)
        distance=math.sqrt(sum(v*v for v in offset))
        fov=plan.fov_at(t)
        # True orbit position changes with yaw; direction of horizontal vector is measured in x-z plane
        angle=math.degrees(math.atan2(offset[0],-offset[2]))
        orbit=angle-shot.yaw
        points.append((t,fov,distance,orbit))
    return points


class ShotMotionGraph(tk.Canvas):
    def __init__(self, master, get_shot, **kw):
        opts={'background':'#F8FAFC','height':130,'highlightbackground':'#CBD5E1','highlightthickness':1}
        opts.update(kw)
        super().__init__(master,**opts)
        self.get_shot=get_shot
        self.bind('<Configure>',lambda _:self.redraw())

    def redraw(self):
        self.delete('all')
        w=max(320,self.winfo_width());h=max(115,self.winfo_height())
        left,right,top,bottom=26,w-18,22,h-25
        self.create_text(9,8,text='カメラ軌道プレビュー（実際のCameraPlanをサンプリング）',
                         fill='#475569',anchor='nw',font=('Meiryo UI',8))
        try:
            shot=self.get_shot()
            data=sample_motion(shot)
        except Exception:
            return
        self.create_rectangle(left,top,right,bottom,outline='#CBD5E1')
        kill_x=left+(right-left)*shot.pre/(shot.pre+shot.post)
        self.create_line(kill_x,top,kill_x,bottom,fill='#F97316',dash=(3,3))
        self.create_text(kill_x,13,text='KILL',fill='#C2410C',font=('Meiryo UI',8))
        for frame in shot.keyframes:
            rel = frame['time'] + shot.pre
            if 0 <= rel <= (shot.pre + shot.post):
                x = left + (right-left) * rel / (shot.pre + shot.post)
                self.create_line(x, top, x, bottom, fill='#94A3B8', dash=(2, 3))
                self.create_oval(x-3, top+2, x+3, top+8, fill='#334155', outline='')
        self.create_text(left,h-8,text=f'-{shot.pre:g}s' ,fill='#64748B',font=('Meiryo UI',8))
        self.create_text(right,h-8,text=f'+{shot.post:g}s',fill='#64748B',anchor='e',font=('Meiryo UI',8))
        metrics=[('FOV',1,'#2563EB'),('距離',2,'#16A34A'),('Orbit',3,'#9A49C5')]
        for m,col,color in metrics:
            vals=[row[col] for row in data]
            minimum,maximum=min(vals),max(vals)
            size=max(0.001,maximum-minimum)
            coords=[]
            for i,val in enumerate(vals):
                coords.extend((left+(right-left)*i/(len(vals)-1),bottom-4-(bottom-top-8)*(val-minimum)/size))
            self.create_line(*coords,fill=color,width=2,smooth=True)
        # three short legends
        for i,(m,_,color) in enumerate(metrics):
            self.create_text(left+12+i*85,top+8,text=m,anchor='w',fill=color,font=('Meiryo UI',8,'bold'))
