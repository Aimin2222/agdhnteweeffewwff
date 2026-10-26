(function(root){'use strict';
const clone=x=>JSON.parse(JSON.stringify(x));
const clamp=(x,a,b)=>Math.max(a,Math.min(b,Number.isFinite(+x)?+x:a));
const styles=['third_cinema','third','geo_aim','cinema','fps','orbit','lolnam_cinema','follow','cinema_top','top'];
const motions=['instant','slide_left','slide_right','slide_up','slide_down','pop'];
function scene(id,label,event,role){return {id,label,event,role,checked:true,camera:{fov:48,yaw:32,distance:850,height:350,side:'BLUE',mode:'fixed_auto',style:'third'},grade:{exposure:0,saturation:100,temperature:0},assets:{frame:'line',fx:'none',motion:'instant',strength:25},keys:[{id:'k1',t:1,value:40,ease:'smooth'},{id:'k2',t:5,value:64,ease:'smooth'},{id:'k3',t:10,value:48,ease:'linear'}]};}
function fresh(){return {schema:1,projectName:'Mid Lane • シネマティック研究',variant:'LD',view:'main',theme:'light',timelineMode:'keys',time:5,rate:1,selected:'s2',selectedKey:'k2',split:50,compare:false,scenes:[scene('s1','開戦の一瞬',2.3,'kill'),scene('s2','連続キル • 余韻まで',5.4,'multi'),scene('s3','味方と連携',7.2,'assist'),scene('s4','集団戦の見せ場',9.1,'multi'),scene('s5','ロングショット',10.8,'kill')],settings:{encoder:'auto',gameAudio:true,hideHUD:true,fps:'60',resolution:'1920x1080'},capabilities:{replay:false,scan:false,camera:false,record:false,audio:false,gpu:false,exportVideo:false}};}
function validate(raw){
 if(!raw||raw.schema!==1||!Array.isArray(raw.scenes)||raw.scenes.length<1||raw.scenes.length>100)throw Error('対応する研究プロジェクト（schema 1）が必要です。');
 const base=fresh(); const ids=new Set();
 base.projectName=typeof raw.projectName==='string'?raw.projectName.slice(0,120):base.projectName;
 base.scenes=raw.scenes.map((r,i)=>{if(!r||typeof r.id!=='string'||!/^[A-Za-z0-9_-]{1,64}$/.test(r.id)||ids.has(r.id))throw Error('シーンIDが不正・重複しています。');ids.add(r.id);const s=scene(r.id,String(r.label||'シーン').slice(0,80),clamp(r.event,0,12),['kill','multi','assist'].includes(r.role)?r.role:'kill');s.checked=!!r.checked;
  for(const [k,a,b] of [['fov',20,110],['yaw',-180,180],['distance',500,1400],['height',0,900]])s.camera[k]=clamp(r.camera?.[k]??s.camera[k],a,b);
  for(const [k,allowed] of [['side',['AUTO','BLUE','RED']],['mode',['manual','fixed_auto','full_auto']],['style',styles]])if(allowed.includes(r.camera?.[k]))s.camera[k]=r.camera[k];
  for(const [k,a,b] of [['exposure',-2,2],['saturation',0,180],['temperature',-50,50]])s.grade[k]=clamp(r.grade?.[k]??s.grade[k],a,b);
  for(const [k,allowed] of [['frame',['line','halo','split']],['fx',['none','pulse','rays']],['motion',motions]])if(allowed.includes(r.assets?.[k]))s.assets[k]=r.assets[k];s.assets.strength=clamp(r.assets?.strength??25,0,100);
  if(Array.isArray(r.keys)&&r.keys.length<=200){const ks=new Set();s.keys=r.keys.map((q,j)=>{const id=String(q.id||'key'+j);if(!/^[A-Za-z0-9_-]{1,64}$/.test(id)||ks.has(id))throw Error('キーフレームIDが不正です。');ks.add(id);return {id,t:clamp(q.t,0,12),value:clamp(q.value,20,110),ease:['linear','smooth','hold'].includes(q.ease)?q.ease:'linear'};}).sort((a,b)=>a.t-b.t);}
  return s;});
 base.selected=ids.has(raw.selected)?raw.selected:base.scenes[0].id;base.selectedKey=typeof raw.selectedKey==='string'?raw.selectedKey:'';
 for(const k of ['variant','view','theme','timelineMode']){const options={variant:['LD','LN'],view:['main','easy','detail','camera','curve','color','material','export'],theme:['light','dark','system'],timelineMode:['keys','curve']};if(options[k].includes(raw[k]))base[k]=raw[k];}
 base.time=clamp(raw.time??5,0,12);base.rate=[.5,1,2].includes(+raw.rate)?+raw.rate:1;base.split=clamp(raw.split??50,0,100);base.compare=!!raw.compare;base.useKeys=!!raw.useKeys;
 if(raw.settings){base.settings.gameAudio=raw.settings.gameAudio!==false;base.settings.hideHUD=raw.settings.hideHUD!==false;if(['auto','CPU','NVENC'].includes(raw.settings.encoder))base.settings.encoder=raw.settings.encoder;if(['30','60','60000/1001'].includes(raw.settings.fps))base.settings.fps=raw.settings.fps;if(['1920x1080','1366x768','1280x720'].includes(raw.settings.resolution))base.settings.resolution=raw.settings.resolution;}
 // No imported capability can connect this research demo to an application or device.
 return base;
}
function interpolate(keys,t){if(!keys.length)return 48;const ks=[...keys].sort((a,b)=>a.t-b.t);if(t<=ks[0].t)return ks[0].value;for(let i=1;i<ks.length;i++){const a=ks[i-1],b=ks[i];if(t<=b.t){let u=b.t===a.t?1:(t-a.t)/(b.t-a.t);if(a.ease==='hold')u=0;if(a.ease==='smooth')u=u*u*(3-2*u);return a.value+(b.value-a.value)*u;}}return ks.at(-1).value;}
class Store{
 constructor(data){this.data=validate(data||fresh());this.undoStack=[];this.redoStack=[];}
 get scene(){return this.data.scenes.find(x=>x.id===this.data.selected)||this.data.scenes[0];}
 transact(fn,remember=true){if(remember){this.undoStack.push(clone(this.data));if(this.undoStack.length>50)this.undoStack.shift();this.redoStack=[];}fn(this.data,this.scene);}
 set(group,key,value){const limits={fov:[20,110],yaw:[-180,180],distance:[500,1400],height:[0,900],exposure:[-2,2],saturation:[0,180],temperature:[-50,50],strength:[0,100]};this.transact((d,s)=>{s[group][key]=limits[key]?clamp(value,...limits[key]):value;});}
 key(t,value){this.transact((d,s)=>{t=clamp(Math.round(+t*30)/30,0,12);let key=s.keys.find(x=>Math.abs(x.t-t)<1/60);if(key){key.value=clamp(value,20,110);}else{key={id:'k'+Date.now().toString(36)+s.keys.length,t,value:clamp(value,20,110),ease:'smooth'};s.keys.push(key);}s.keys.sort((a,b)=>a.t-b.t);d.selectedKey=key.id;});}
 undo(){if(!this.undoStack.length)return false;this.redoStack.push(clone(this.data));this.data=this.undoStack.pop();return true;}
 redo(){if(!this.redoStack.length)return false;this.undoStack.push(clone(this.data));this.data=this.redoStack.pop();return true;}
 serialize(){return JSON.stringify(this.data,null,2);}
}
const api={fresh,validate,Store,interpolate,clamp,clone,styles,motions};if(typeof module!=='undefined')module.exports=api;root.AutoCineModel=api;
})(typeof window!=='undefined'?window:globalThis);
