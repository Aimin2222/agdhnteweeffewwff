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
    """Readable normalized view of actual CameraPlan samples (not a pixel preview)."""
    def __init__(self, master, get_shot, **kw):
        opts={'background':'#F8FAFC','height':180,'highlightbackground':'#CBD5E1','highlightthickness':1}
        opts.update(kw)
        super().__init__(master,**opts)
        self.get_shot=get_shot
        self._data=[]
        self._chart=(32,0,0,0)
        self.bind('<Configure>',lambda _:self.redraw())
        self.bind('<Motion>',self._show_cursor)
        self.bind('<Leave>',lambda _:self.delete('cursor'))

    def redraw(self):
        self.delete('all')
        w=max(330,self.winfo_width());h=max(165,self.winfo_height())
        left,right,top,bottom=35,w-18,36,h-56
        self._chart=(left,right,top,bottom)
        self.create_text(left,11,text='カメラの動き：キル前 → キル瞬間 → キル後',
                         fill='#475569',anchor='w',font=('Meiryo UI',9,'bold'))
        try:
            shot=self.get_shot()
            data=sample_motion(shot)
        except Exception:
            self._data=[]
            return
        self._data=data
        self.create_rectangle(left,top,right,bottom,outline='#CBD5E1')
        for frac in (0.25,0.5,0.75):
            x=left+(right-left)*frac
            self.create_line(x,top,x,bottom,fill='#E2E8F0',dash=(2,4))
        kill_x=left+(right-left)*shot.pre/max(.1,shot.pre+shot.post)
        self.create_line(kill_x,top,kill_x,bottom,fill='#EA580C',width=2,dash=(4,3))
        self.create_text(kill_x,top-8,text='キル瞬間',fill='#C2410C',font=('Meiryo UI',8),anchor='s')
        for frame in shot.keyframes:
            rel=frame['time']+shot.pre
            if 0<=rel<=shot.pre+shot.post:
                x=left+(right-left)*rel/(shot.pre+shot.post)
                self.create_line(x,top,x,bottom,fill='#94A3B8',dash=(2,4))
                self.create_oval(x-4,top+1,x+4,top+9,fill='#475569',outline='')
        self.create_text(left,bottom+15,text=f'キル {shot.pre:g} 秒前',fill='#64748B',anchor='w',font=('Meiryo UI',8))
        self.create_text(right,bottom+15,text=f'キル {shot.post:g} 秒後',fill='#64748B',anchor='e',font=('Meiryo UI',8))
        metrics=[('画角 FOV',1,'#2563EB','°'),('カメラ距離',2,'#059669',''),('回り込み',3,'#9333EA','°')]
        for idx,(label,col,color,unit) in enumerate(metrics):
            vals=[row[col] for row in data]
            mn,mx=min(vals),max(vals)
            delta=max(0.001,mx-mn)
            coords=[]
            for i,val in enumerate(vals):
                coords.extend((left+(right-left)*i/max(1,len(vals)-1),
                               bottom-3-(bottom-top-6)*(val-mn)/delta))
            self.create_line(*coords,fill=color,width=2,smooth=True)
            width=max(90,(right-left)/3)
            self.create_text(left+idx*width,bottom+36,anchor='w',
                             text=f'{label}: {mn:.0f}〜{mx:.0f}{unit}',fill=color,font=('Meiryo UI',8,'bold'))

    def _show_cursor(self,event):
        self.delete('cursor')
        if not self._data:
            return
        left,right,top,bottom=self._chart
        if not left<=event.x<=right or not top<=event.y<=bottom:
            return
        idx=max(0,min(len(self._data)-1,round((event.x-left)/(right-left)*(len(self._data)-1))))
        t,fov,dist,orbit=self._data[idx]
        self.create_line(event.x,top,event.x,bottom,fill='#64748B',dash=(2,2),tags='cursor')
        label=f'{t:+.1f}秒   画角{fov:.0f}° / 距離{dist:.0f} / 回り込み{orbit:+.1f}°'
        self.create_text(right,26,text=label,anchor='e',fill='#334155',font=('Meiryo UI',8),tags='cursor')
