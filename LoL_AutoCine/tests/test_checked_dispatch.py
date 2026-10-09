"""Run under Xvfb: xvfb-run -a python tests/test_checked_dispatch.py"""
import os, sys, tempfile, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import tkinter as tk
import legacy_app
from core.players import Player
from core.scanner import Kill

root=tk.Tk()
app=legacy_app.App(root)
app.locked=Player(1,'Aimin','Aimin#1','Aimin','Lee Sin','ORDER')
app.kills=[Kill(1,100,'Aimin','Enemy',[]), Kill(2,200,'Aimin','Enemy2',[])]
app.checked_kills={0,1}
app.var_gaudio.set(False)
app._fill_kills()
app._need_lock=lambda: True
captured=[]
orig_bg=app._run_bg
app._run_bg=lambda fn,*args: captured.append((fn,args))
app.on_make_checked()
assert len(captured)==1, 'checked click did not dispatch'
fn,args=captured[0]
assert fn.__name__=='_make_list' and len(args[0])==2
assert args[1].game_audio is False

class FakeSource:
    def stop(self): pass
fake=FakeSource()
app._ensure_source=lambda: (fake,True)
from types import SimpleNamespace
original_render=legacy_app.run_auto_edit
legacy_app.run_auto_edit=lambda *a,**k: SimpleNamespace(outputs=['clip1.mp4','clip2.mp4'],failed=[])
app._make_list(*args)
legacy_app.run_auto_edit=original_render
log=(ROOT/'diagnostics'/'runtime.log').read_text(encoding='utf-8')
for token in ('CHECKED_STAGE click_enter','CHECKED_STAGE template_begin','CHECKED_STAGE template_ready','CHECKED_STAGE enqueue_worker','CHECKED_STAGE capture_start','CHECKED_STAGE capture_ready','CHECKED_STAGE render_begin','CHECKED_STAGE render_complete'):
    assert token in log, f'missing {token}'
# The threaded path must update busy immediately (double clicks are prevented)
app._run_bg=orig_bg
app._make_list=lambda *a: time.sleep(0.02)
app.on_make_checked()
assert app.busy is True
for i in range(120):
    root.update()
    if not app.busy: break
    time.sleep(0.01)
assert not app.busy
root.destroy()
print('CHECKED DISPATCH TEST PASS: UI callback, stubbed render, worker busy state')
