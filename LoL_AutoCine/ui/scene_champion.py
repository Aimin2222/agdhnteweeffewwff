"""One portrait worker, UI-side polling, replay generation and selection guards."""
from PIL import Image, ImageTk
from core.kill_icons import champion_icon
from ui.live_preview import LatestPreview
from core.players import norm


def render_champion(player):
    try:
        path=champion_icon(player,download=True)
        if path is None:return None
        with Image.open(path) as picture:
            return picture.convert('RGB').resize((72,72),Image.Resampling.LANCZOS)
    except Exception:
        return None


def render_result(player):
    # An unavailable portrait is a finished result, never an endless poll.
    return (render_champion(player),)


class SceneChampionPreview:
    def __init__(self,root,label,current_generation):
        self.root,self.label,self.current_generation=root,label,current_generation
        self.worker=LatestPreview(render_result)
        self.generation=0
        self.after=None
        self.closed=False
        self.photo=None
        root.bind('<Destroy>',lambda event:self.close() if event.widget is root else None,add='+')

    def show(self,kill,players,replay_generation):
        if self.closed:return
        self.generation+=1
        key=self.generation
        if self.after is not None:self.root.after_cancel(self.after)
        self.after=None
        self.photo=None
        name=getattr(kill,'killer','')
        player=next((p for p in players if name and norm(name) in {
            norm(alias) for field in ('name','riot_id','summoner','champion','selection_name')
            for alias in (getattr(p,field,''),str(getattr(p,field,'') or '').split('#')[0]) if alias}),None)
        self.label.configure(image='',text='キラー: '+(getattr(player,'champion',name) or '未選択'))
        if player is None:return
        snapshot={field:getattr(player,field,'') for field in
                  ('name','riot_id','summoner','champion','selection_name','raw_champion')}
        self.worker.submit(key,snapshot)
        def poll():
            self.after=None
            if self.closed or self.generation!=key:return
            if self.current_generation()!=replay_generation:
                self.photo=None
                self.label.configure(image='',text='キラー: 未選択')
                return
            result=self.worker.result(key)
            if result is None:
                self.after=self.root.after(40,poll)
                return
            picture=result[1][0]
            if picture is not None:
                self.photo=ImageTk.PhotoImage(picture,master=self.root)
                self.label.configure(image=self.photo,text='')
        self.after=self.root.after(40,poll)

    def close(self):
        if self.closed:return
        self.closed=True
        self.worker.close()
        if self.after is not None:self.root.after_cancel(self.after)
        self.after=None
