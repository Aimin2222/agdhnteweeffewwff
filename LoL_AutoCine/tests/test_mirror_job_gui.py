"""Real Tk display test using synthetic frames, not live LoL quality approval."""
import tkinter as tk
from types import SimpleNamespace
import numpy as np
import legacy_app


def test_recording_source_is_presented_even_without_manual_mirror():
    root=tk.Tk();root.withdraw()
    errors=[];observed=[]
    root.report_callback_exception=lambda *e:errors.append(e)
    app=legacy_app.App(root)
    frame=np.zeros((180,320,4),np.uint8);frame[:,:,1]=150
    source=SimpleNamespace(running=True,latest=lambda:frame)
    app.busy=True
    app.q.put(('capture_preview_ready',source))
    def finish():
        observed.append(app._preview_presented is not None and app.source is None)
        app.busy=False
        app.on_close()
    root.after(1800,finish)
    root.mainloop()
    assert not errors
    assert observed==[True]
