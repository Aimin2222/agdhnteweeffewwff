import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
const req=createRequire('C:/Users/saoan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const sharp=req('sharp');
const root='C:/Users/saoan/Documents/Codex/2026-10-19/files-pasted-by-the-user-lol/work/autocine_quiet_pass_20261025/private_screens';
export function makeQuietObserver(tab,out){
 const state=()=>tab.playwright.evaluate(()=>({time:document.querySelector('video')?.currentTime,duration:document.querySelector('video')?.duration,paused:document.querySelector('video')?.paused,muted:document.querySelector('video')?.muted,volume:document.querySelector('video')?.volume,rate:document.querySelector('video')?.playbackRate,ready:document.querySelector('video')?.readyState,seeking:document.querySelector('video')?.seeking,fullscreen:!!document.fullscreenElement,ad:document.querySelector('#movie_player')?.classList.contains('ad-showing'),rect:document.querySelector('#movie_player')?.getBoundingClientRect().toJSON(),url:location.href}));
 async function pause(){let s=await state();if(!s.paused)await tab.playwright.locator('#movie_player').press('k');}
 async function prepare(){
  for(let i=0;i<40;i++){
   let s=await state();if(s.fullscreen)throw Error('Fullscreen forbidden; manually leave through verified UI before continuing');
   if(s.ready>=1&&!s.muted)await tab.playwright.locator('#movie_player').press('m');
   s=await state();if(s.ready>=1&&!s.muted){await pause();throw Error('Unable to verify muted state');}
   if(s.ad){let sk=tab.playwright.getByRole('button',{name:'スキップ',exact:true});if(await sk.isVisible())await sk.click();else if(s.paused)await tab.playwright.locator('#movie_player').press('k');}
   else if(s.duration>5&&s.ready>=2){await pause();out.write(await state());return;}
   await new Promise(r=>setTimeout(r,500));
  }
  await pause();throw Error('Main video unavailable after bounded muted ad handling');
 }
 async function open(id){await tab.goto('https://www.youtube.com/watch?v='+id);await prepare();await tab.playwright.locator('#movie_player').press('0');out.write(await state());}
 async function observe(label,count=32){
  let before=await state();if(before.fullscreen||!before.muted||before.ad||before.ready<2)throw Error('Quiet viewing preconditions failed');
  let records=[],frames=[];if(before.paused)await tab.playwright.locator('#movie_player').press('k');
  try{
  for(let i=0;i<count;i++){
   let pre=await state();if(pre.ad||!pre.muted||pre.fullscreen||pre.paused||pre.duration!==before.duration){records.push({pre,excluded:true,reason:'state_guard'});break;}
   let bytes=await tab.getScreenshot({emit:false});let post=await state();
   if(post.ad||post.duration!==pre.duration||post.url!==pre.url||post.time<pre.time){records.push({pre,post,excluded:true,reason:'screenshot_race_or_postroll'});break;}
   let meta=await sharp(Buffer.from(bytes)).metadata(),x=Math.max(0,Math.round(pre.rect.x)),y=Math.max(0,Math.round(pre.rect.y)),w=Math.min(meta.width-x,Math.round(pre.rect.width)),h=Math.min(meta.height-y,Math.round(pre.rect.height));
   let jpg=await sharp(Buffer.from(bytes)).extract({left:x,top:y,width:w,height:h}).resize(480,270,{fit:'contain',background:'#000'}).extend({bottom:24,background:'#102030'}).composite([{input:Buffer.from('<svg width="480" height="24"><text x="6" y="17" fill="white" font-size="15">'+pre.time.toFixed(2)+'–'+post.time.toFixed(2)+' s / '+pre.rate+'x</text></svg>'),left:0,top:270}]).jpeg({quality:92}).toBuffer();
   frames.push(jpg);records.push({pre,post,excluded:false});if(i<count-1)await new Promise(r=>setTimeout(r,1000));
  }
  } finally { await pause(); }
  let end=await state();
  await fs.writeFile(root+'/'+label+'.json',JSON.stringify({before,end,records,nominal_wait_ms:1000,audio_observed:false,fullscreen_allowed:false,scope:'muted accelerated whole-structure survey; not frame-exact motion or audio analysis'},null,2));
  if(frames.length){let sheet=await sharp({create:{width:1440,height:Math.ceil(frames.length/3)*294,channels:3,background:'#102030'}}).composite(frames.map((input,i)=>({input,left:i%3*480,top:Math.floor(i/3)*294}))).jpeg({quality:94}).toBuffer();await fs.writeFile(root+'/'+label+'.jpg',sheet);out.write({label,samples:frames.length,first:records.find(x=>!x.excluded)?.pre.time,last:[...records].reverse().find(x=>!x.excluded)?.post.time,duration:before.duration,muted:true,fullscreen:false});await out.emitImage({bytes:sheet,mimeType:'image/jpeg'});}
 }
 return {state,prepare,open,observe,pause};
}
