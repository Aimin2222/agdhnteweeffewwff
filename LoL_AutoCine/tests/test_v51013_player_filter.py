"""Player filtering must keep target/cache/session state consistent and responsive."""
import threading
from types import SimpleNamespace
import pytest
from core.players import Player
from tests.test_v5107_mirror_controls import app

EVENTS=[dict(event_id=1,time=12.,killer='Blue',victim='Red',assisters=[]),
        dict(event_id=2,time=24.,killer='Red',victim='Blue',assisters=['Blue'])]

@pytest.fixture
def roster(app):
    app.players=[Player(0,'Blue','Blue#JP1','Blue','Ahri','ORDER'),
                 Player(5,'Red','Red#JP1','Red','Lee Sin','CHAOS')]
    app._match_scan_cache=SimpleNamespace(complete=True,events=EVENTS)
    app._fill_players()
    return app


def test_selector_filters_cache_and_sets_real_target_without_api(roster,monkeypatch):
    def forbidden(*a,**k):raise AssertionError('must reuse completed whole-match cache')
    monkeypatch.setattr(roster,'_run_bg',forbidden)
    roster.api=SimpleNamespace(events=forbidden)
    roster.var_scene_player_filter.set(roster.players[1].label())
    roster._on_scene_player_filter_changed()
    assert roster.locked is roster.players[1]
    assert [k.event_id for k in roster.kills]==[2]
    assert roster.checked_kills=={0}
    assert roster.tree.selection()==('5',)
    roster.var_event_mode.set('キル＋アシスト')
    roster.var_scene_player_filter.set(roster.players[0].label())
    roster._on_scene_player_filter_changed()
    assert [k.role for k in roster.kills]==['kill','assist']
    assert roster.var_scene_player_filter.get()==roster.locked.label()


def test_busy_selector_restores_actual_target_and_keeps_scenes(roster):
    roster._set_locked_player(roster.players[0])
    old=list(roster.kills)
    roster.busy=True
    roster.var_scene_player_filter.set(roster.players[1].label())
    roster._on_scene_player_filter_changed()
    assert roster.locked is roster.players[0] and roster.kills==old
    assert roster.var_scene_player_filter.get()==roster.locked.label()


def test_reset_discards_previous_match_and_selector(roster):
    roster._set_locked_player(roster.players[0])
    old=roster._replay_generation
    roster._reset_match_state()
    roster._pump()
    assert roster._replay_generation==old+1 and roster._match_scan_cache is None
    assert not roster.players and not roster.kills and roster.locked is None
    assert roster.var_scene_player_filter.get()==''
    assert not roster.cb_scene_player_filter.cget('values')

@pytest.mark.parametrize('complete,cancelled',[(False,False),(True,True)])
def test_partial_or_cancelled_scan_is_never_cached(roster,monkeypatch,complete,cancelled):
    import legacy_app
    roster._match_scan_cache=None
    roster.stop_ev.set() if cancelled else roster.stop_ev.clear()
    result=SimpleNamespace(complete=complete,events=EVENTS,kills=[],notes=[],total_events=len(EVENTS))
    monkeypatch.setattr(legacy_app,'scan_kills',lambda *a,**k:result)
    roster._scan('キル')
    assert roster._match_scan_cache is None


def test_stale_scan_after_reconnect_is_discarded(roster,monkeypatch):
    import legacy_app
    roster._match_scan_cache=None
    def stale(*a,**k):
        roster._reset_match_state()
        return SimpleNamespace(complete=True,events=EVENTS,kills=[],notes=[],total_events=len(EVENTS))
    monkeypatch.setattr(legacy_app,'scan_kills',stale)
    roster._scan('キル')
    assert roster._match_scan_cache is None and not roster.kills


def test_qa_single_worker_survives_error(app,monkeypatch):
    import core.auto_qa
    started,release=threading.Event(),threading.Event()
    calls=[]
    def failing(*a,**k):
        calls.append(True);started.set();assert release.wait(3)
        raise OSError('test write failure')
    monkeypatch.setattr(core.auto_qa,'run_checks',failing)
    try:
        app.on_automatic_qa();assert started.wait(1)
        app.on_automatic_qa();assert len(calls)==1 and app._auto_qa_pending
    finally:release.set()
    from tests.test_v51010_gallery_responsiveness import pump
    pump(app.root,lambda:not app._auto_qa_pending)
    assert len(calls)==1


def test_zoom_comparison_does_pixels_off_tk(app,tmp_path,monkeypatch):
    from ui import template_gallery as gallery
    from core.effects import Template
    from PIL import Image
    from tests.test_v51010_gallery_responsiveness import pump
    path=tmp_path/'scene.png';Image.new('RGB',(960,540),'slateblue').save(path)
    entered,release=threading.Event(),threading.Event()
    main=threading.get_ident();comparison=gallery.render_scene_comparison
    def slow(*a,**k):
        assert threading.get_ident()!=main
        entered.set();assert release.wait(3)
        return comparison(*a,**k)
    monkeypatch.setattr(gallery,'render_scene_comparison',slow)
    win=gallery._open_scene_zoom(app.root,str(path),Template(grade='default'))
    try:
        pump(app.root,entered.is_set)
        heartbeat=[];app.root.after(1,lambda:heartbeat.append(True))
        pump(app.root,lambda:bool(heartbeat),timeout=.5)
        assert not win._photos
        release.set();pump(app.root,lambda:bool(win._photos))
        assert win._photos[0].width()==1263
    finally:
        release.set();win.destroy()
    assert win._comparison_worker._closed
