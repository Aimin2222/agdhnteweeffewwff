(() => {
 const root=document.documentElement, selector=document.querySelector('#theme');
 const params=new URLSearchParams(location.search);
 const initial=root.dataset.theme;
 let preference=params.get('theme')||localStorage.getItem('autocine-design-theme')||'system';
 const media=matchMedia('(prefers-color-scheme: dark)');
 function apply(){root.dataset.theme=preference==='system'?(media.matches?'dark':'light'):preference;if(selector)selector.value=preference;}
 apply();
 if(selector)selector.addEventListener('change',()=>{preference=selector.value;localStorage.setItem('autocine-design-theme',preference);apply();});
 media.addEventListener('change',()=>{if(preference==='system')apply();});
 for(const input of document.querySelectorAll('[data-setting]')){
  const saved=sessionStorage.getItem('autocine-design-'+input.dataset.setting);
  if(saved!==null&&!params.has('capture'))input.value=saved;
  input.addEventListener('input',()=>sessionStorage.setItem('autocine-design-'+input.dataset.setting,input.value));
 }
 const note=document.createElement('div');note.setAttribute('role','status');note.className='notice';note.style.cssText='position:fixed;bottom:42px;left:50%;transform:translateX(-50%);background:var(--panel);color:var(--ink);border:1px solid var(--line);z-index:30;display:none;box-shadow:var(--shadow);max-width:700px';
 note.textContent='設計用モックです。LoL接続・設定適用・録画は行いません。実装対応表で接続先を確認できます。';
 document.body.append(note);let timer;
 document.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{note.style.display='block';clearTimeout(timer);timer=setTimeout(()=>note.style.display='none',4500);}));
 window.designState=()=>({plan:document.body.dataset.plan,mode:document.body.dataset.mode,themePreference:preference,effectiveTheme:root.dataset.theme,settings:Object.fromEntries([...document.querySelectorAll('[data-setting]')].map(e=>[e.dataset.setting,e.value])),preview:'static-generated-image',runtime:'not-connected'});
})();

