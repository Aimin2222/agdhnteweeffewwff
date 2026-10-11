"""Portrait/comparison work is bounded, off Tk and guarded against stale results."""
import threading
from types import SimpleNamespace
from PIL import Image, ImageTk
from tkinter import ttk
from core.players import Player
from tests.test_v5107_mirror_controls import app
from tests.test_v51010_gallery_responsiveness import pump


def kill(name):return SimpleNamespace(killer=name)


def roster():
    return [Player(0,'Alpha','Alpha#JP1','Alpha','Ahri','ORDER',selection_name='Ahri'),
            Player(5,'Beta','Beta#JP1','Beta','Lee Sin','CHAOS',selection_name='LeeSin')]


def test_portrait_lookup_and_resize_are_off_tk_and_latest_selection_wins(app,monkeypatch,tmp_path):
    from ui import scene_champion
    paths={}
    for name,color in [('Ahri','red'),('LeeSin','blue')]:
        paths[name]=tmp_path/(name+'.png');Image.new('RGB',(120,120),color).save(paths[name])
    entered,release=threading.Event(),threading.Event()
    main=threading.get_ident()
    def lookup(player,**kwargs):
        assert threading.get_ident()!=main
        assert isinstance(player,dict)
        if player['selection_name']=='Ahri':
            entered.set();assert release.wait(3)
        return paths[player['selection_name']]
    monkeypatch.setattr(scene_champion,'champion_icon',lookup)
    resize=Image.Image.resize
    def checked_resize(*args,**kw):
        assert threading.get_ident()!=main
        return resize(*args,**kw)
    monkeypatch.setattr(Image.Image,'resize',checked_resize)
    app.players=roster()
    app._show_scene_champion(kill('alpha'))  # normalized real event alias
    helper=app._scene_champion_preview
    try:
        pump(app.root,entered.is_set)
        beats=[];app.root.after(1,lambda:beats.append(True))
        pump(app.root,lambda:bool(beats),timeout=.5)
        app._show_scene_champion(kill('Beta#JP1'))
        assert app.scene_champion_icon.cget('text')=='キラー: Lee Sin'
        assert helper.photo is None
        release.set()
        pump(app.root,lambda:helper.photo is not None)
        assert ImageTk.getimage(helper.photo).convert('RGB').getpixel((25,25))==(0,0,255)
        assert helper.photo.width()==72
    finally:release.set();helper.close()
    assert helper.worker._closed and helper.after is None


def test_portrait_result_from_old_replay_is_rejected(app,monkeypatch):
    from ui import scene_champion
    entered,release=threading.Event(),threading.Event()
    def slow(player):
        entered.set();assert release.wait(3)
        return Image.new('RGB',(72,72),'red')
    monkeypatch.setattr(scene_champion,'render_champion',slow)
    app.players=roster();app._show_scene_champion(kill('Alpha'))
    helper=app._scene_champion_preview
    try:
        pump(app.root,entered.is_set)
        app._replay_generation+=1
        release.set()
        pump(app.root,lambda:helper.after is None)
        assert helper.photo is None and app.scene_champion_icon.cget('text')=='キラー: 未選択'
    finally:release.set();helper.close()


def test_missing_portrait_finishes_with_champion_name_and_destroy_closes_worker(app,monkeypatch):
    from ui import scene_champion
    monkeypatch.setattr(scene_champion,'champion_icon',lambda *a,**k:None)
    app.players=roster();app._show_scene_champion(kill('Alpha'))
    helper=app._scene_champion_preview
    pump(app.root,lambda:helper.after is None)
    assert helper.photo is None and app.scene_champion_icon.cget('text')=='キラー: Ahri'
    app._show_scene_champion(None)
    assert app.scene_champion_icon.cget('text')=='キラー: 未選択'
    app.root.destroy()
    assert helper.worker._closed and helper.after is None
    # Existing shared fixture owns root destruction; make its cleanup idempotent.
    app.root.destroy=lambda:None


def test_large_comparison_keeps_tk_responsive_and_latest_preset_without_applying(app,monkeypatch):
    from ui import frame_comparison
    entered,release=threading.Event(),threading.Event()
    main=threading.get_ident();requests=[]
    def slow(request):
        assert threading.get_ident()!=main
        requests.append(request)
        entered.set();assert release.wait(3)
        return Image.new('RGB',(960,270),'blue'),''
    monkeypatch.setattr(frame_comparison,'render_comparison',slow)
    before=app.current_template().to_dict()
    win=app._open_easy_preset_comparison()
    try:
        pump(app.root,entered.is_set)
        beats=[];app.root.after(1,lambda:beats.append(True))
        pump(app.root,lambda:bool(beats),timeout=.5)
        buttons=[child for frame in win.winfo_children() for child in frame.winfo_children() if isinstance(child,ttk.Button)]
        assert len(buttons)==3
        buttons[1].invoke();buttons[2].invoke()
        release.set()
        pump(app.root,lambda:hasattr(win,'_photo'))
        assert requests[-1][1]==app.templates['Lolnam風ダイナミック'].to_dict()
        assert win._photo.width()==960 and app.current_template().to_dict()==before
    finally:release.set();win.destroy()
    assert win._comparison_worker._closed


def test_popup_detection_does_not_construct_unopened_native_menus(app):
    def existing():
        return {str(cb) for cb in app._autocine_comboboxes if int(app.root.tk.call('winfo','exists',str(cb)+'.popdown'))}
    before=existing()
    assert app.root._autocine_combobox_popup_open() is False
    assert existing()==before


def test_legacy_color_and_badge_labels_still_resolve_and_persist(app):
    from core.effects import GRADE_JP
    from core.kill_icons import STYLES
    app.var_grade.set('ティール&オレンジ')
    app.var_kill_icon_style.set('追加素材 13')
    template=app.current_template()
    assert template.grade=='tealorange' and template.kill_icon_style=='user_frame_13'
    app.templates['__LEGACY_LABELS__']=template
    app.apply_template('__LEGACY_LABELS__')
    assert app.var_grade.get()==GRADE_JP['tealorange']
    assert app.var_kill_icon_style.get()==STYLES['user_frame_13']
    app._save_settings()
    app.var_kill_icon_style.set(STYLES['off'])
    app._load_settings()
    assert app.current_template().kill_icon_style=='user_frame_13'
