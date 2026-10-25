from lab_common import *
import urllib.request,urllib.parse,hashlib,socket,os,collections
def get(u):
 with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'AutoCine-V4-readonly-research'}),timeout=90) as r:return r.read()
repo='https://api.github.com/repos/Aimin2222/agdhnteweeffewwff';sha='b32513ada0a5ada7585972e06716ff84829bcb23'
c=json.loads(get(repo+'/git/commits/'+sha));tree=json.loads(get(c['tree']['url']+'?recursive=1'));assert not tree['truncated'];(W/'latest_tree.json').write_text(json.dumps(tree),'utf-8')
a={x['path']:x['sha'] for x in load(OLD/'latest_tree_final_v3.json')['tree'] if x['type']=='blob'};b={x['path']:x['sha'] for x in tree['tree'] if x['type']=='blob'}
changes=[{'path':p,'old':a.get(p),'new':b.get(p)} for p in sorted(a.keys()|b.keys()) if a.get(p)!=b.get(p)]
save('LATEST_UI_DELTA_V4.json',{'v3_observed_ui_head':'9bb15e15d8057237515cc9bcf7e061a6d15d3369','v4_observed_ui_head':sha,'full_tree':True,'changed':changes,'core':[x for x in changes if x['path'].startswith('LoL_AutoCine/core/')],'assets':[x for x in changes if x['path'].startswith('LoL_AutoCine/assets/')]})
# Official static icons are research inputs, not downloads of reference videos.
iconrows=[];iconroot=W/'official_icons';iconroot.mkdir(exist_ok=True)
for champ in ['Yasuo','Jinx','Ahri','Zed']:
 url='https://ddragon.leagueoflegends.com/cdn/16.18.1/img/champion/'+champ+'.png';bb=get(url);(iconroot/(champ+'.png')).write_bytes(bb);iconrows.append({'champion':champ,'url':url,'sha256':hashlib.sha256(bb).hexdigest(),'bytes':len(bb),'purpose':'static official portrait research composition, not actual LoL gameplay validation'})
save('OFFICIAL_ICON_PROVENANCE_V4.json',{'version':'16.18.1','official_documentation':'https://developer.riotgames.com/docs/lol#data-dragon','items':iconrows})
save('NATIVE_ENVIRONMENT_V4.json',{'platform':os.name,'replay_port_2999_open':socket.socket().connect_ex(('127.0.0.1',2999))==0,'ffmpeg_version':subprocess.run([FF,'-version'],capture_output=True,text=True).stdout.splitlines()[0],'no_replay_camera_POST':True,'no_product_launch':True})
print(json.dumps({'ui_changed':len(changes),'core':sum(x['path'].startswith('LoL_AutoCine/core/') for x in changes),'assets':sum(x['path'].startswith('LoL_AutoCine/assets/') for x in changes),'icons':len(iconrows)}))
