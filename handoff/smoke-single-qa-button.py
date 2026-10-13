from pathlib import Path
import sys,json,tkinter as tk
sys.path.insert(0,str(Path.cwd()))
import legacy_app
root=tk.Tk();root.geometry('1450x900')
try:
 app=legacy_app.App(root);root.update()
 def walk(widget):
  yield widget
  for child in widget.winfo_children():yield from walk(child)
 buttons=[w for w in walk(root) if w.winfo_class() in ('TButton','Button')]
 dev=[w for w in buttons if str(w.cget('text')).startswith('開発用：')]
 assert len(dev)==1,[w.cget('text') for w in dev]
 assert dev[0].cget('text')=='開発用：全カメラテスト・30MB ZIP'
 assert str(dev[0].cget('command')).endswith('on_dev_camera_qa')
 assert any(w.cget('text')=='▶ 全検出シーンを一括作成' for w in buttons)
 assert any(w.cget('text')=='✓ チェックしたシーンだけ作成' for w in buttons)
 print(json.dumps({'development_buttons':len(dev),'text':dev[0].cget('text'),'callback':'on_dev_camera_qa','ordinary_export_buttons_present':True},ensure_ascii=False))
finally:root.destroy()
