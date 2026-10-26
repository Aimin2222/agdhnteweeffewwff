/* Fixed, synthetic DOM-event integration fixtures for the research app only. */
function integrationChecks(){
 const before=store.serialize(),cases=[];
 const test=(id,fn)=>{try{if(fn()===false)throw Error('assertion false');cases.push({id,status:'PASS'});}catch(e){cases.push({id,status:'FAIL',reason:e.message});}};
 const click=s=>{const e=$(s);if(!e)throw Error('missing '+s);e.click();};
 const input=(s,v,event='input')=>{const e=$(s);if(!e)throw Error('missing '+s);e.value=v;e.dispatchEvent(new Event(event,{bubbles:true}));};
 try {
  store=new M.Store();render();
  test('control.camera-tab',()=>{click('[data-view="camera"]');return store.data.view==='camera'&&!!$('#r-fov');});
  test('control.slider-and-number-preview',()=>{input('#r-fov',72);return store.scene.camera.fov===72&&$('[aria-label="FOV 数値"]').value==='72'&&$('.demo-fov').textContent.includes('72.0');});
  test('control.dark-theme-keeps-camera',()=>{input('#theme','dark','change');return document.body.classList.contains('dark')&&store.scene.camera.fov===72;});
  test('control.variant-retains-state',()=>{const sc=JSON.stringify(store.data.scenes);click('[data-variant="LN"]');return store.data.variant==='LN'&&JSON.stringify(store.data.scenes)===sc&&getComputedStyle($('.rail')).display!=='none';});
  test('control.side-radio',()=>{click('[data-setting="camera.side"][data-value="RED"]');return store.scene.camera.side==='RED';});
  test('control.timeline-scrub',()=>{input('#scrubber',3.2);return Math.abs(store.data.time-3.2)<1e-4&&$('#clock').textContent==='00:03.20';});
  test('control.key-add',()=>{click('[data-view="curve"]');click('#timelineAdd');return store.scene.keys.some(k=>Math.abs(k.t-3.2)<1e-6&&k.value===72)&&store.data.useKeys;});
  test('control.key-numeric',()=>{input('#keyValue',81,'change');return store.scene.keys.find(k=>k.id===store.data.selectedKey).value===81&&$('.demo-fov').textContent.includes('81.0');});
  test('control.key-easing',()=>{input('#keyEase','hold','change');return store.scene.keys.find(k=>k.id===store.data.selectedKey).ease==='hold';});
  test('control.undo',()=>{click('#undo');return store.scene.keys.find(k=>k.id===store.data.selectedKey).ease==='smooth';});
  test('control.redo',()=>{click('#redo');return store.scene.keys.find(k=>k.id===store.data.selectedKey).ease==='hold';});
  test('control.scene-focus-checks-independent',()=>{const checks=store.data.scenes.map(s=>s.checked).join();click('[data-scene="s1"]');return store.data.selected==='s1'&&store.scene.camera.fov===48&&store.data.scenes.map(s=>s.checked).join()===checks;});
  test('control.return-scene-preserves-FOV',()=>{click('[data-scene="s2"]');return store.scene.camera.fov===72;});
  test('control.grade-preset-preview',()=>{click('[data-view="color"]');click('[data-preset="warm"]');return store.scene.grade.temperature===30&&$('.graded').style.filter.includes('sepia');});
  test('control.split-compare',()=>{if(!store.data.compare)click('#splitToggle');input('#split',25);return store.data.compare&&store.data.split===25&&$('.graded').style.clipPath.includes('25%');});
  test('control.material-motion',()=>{click('[data-view="material"]');click('[data-setting="assets.motion"][data-value="slide_left"]');return store.scene.assets.motion==='slide_left'&&Math.abs(store.data.time-store.scene.event-.1)<1e-6;});
  test('control.output-not-real-encode',()=>{click('[data-view="export"]');input('[data-output="encoder"]','NVENC','change');return store.data.settings.encoder==='NVENC'&&[...document.querySelectorAll('button')].some(b=>b.disabled&&b.textContent.includes('実際の動画'))&&!store.data.capabilities.gpu;});
  test('control.modal-close-focus',()=>{$('#settings').focus();click('#settings');if(!$('#dialog').open)return false;click('#closeDialog');return !$('#dialog').open&&document.activeElement===$('#settings');});
  test('control.70-feature-search',()=>{click('#capabilities');input('#featureSearch','NVENC');const ok=$('#featureRows').textContent.includes('NVENC')&&$('#featureRows').querySelectorAll('.feature-row').length>0;click('#closeDialog');return ok;});
 } finally {store=new M.Store(JSON.parse(before));render();}
 const report={cases,count:cases.length,passed:cases.filter(x=>x.status==='PASS').length,failed:cases.filter(x=>x.status==='FAIL').length,scope:'Actual HTML controls and their handlers driven by synthetic DOM events in isolated WebView2 fixture. Not native pointer/keyboard/IME, file dialogs, or live AutoCine backend.',nativePointer:'NOT_RUN',nativeKeyboard:'NOT_RUN',backend:'NOT_RUN'};
 native('integration-report',{report});return report;
}
