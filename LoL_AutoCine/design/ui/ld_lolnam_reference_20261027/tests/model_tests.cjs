const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const root=fs.existsSync(path.resolve(__dirname,'../demo/model.js'))?path.resolve(__dirname,'..'):path.resolve(__dirname,'../../outputs/ld_lolnam_ui_20261027');
const M=require(path.join(root,'demo/model.js'));const cases=[];
function test(id,fn){try{fn();cases.push({id,status:'PASS'});}catch(e){cases.push({id,status:'FAIL',reason:e.message});}}
test('project.valid-roundtrip',()=>{const s=new M.Store();assert.equal(new M.Store(JSON.parse(s.serialize())).serialize(),s.serialize());});
test('project.bad-schema',()=>assert.throws(()=>M.validate({schema:2,scenes:[]})));
test('project.duplicate-scene',()=>{let r=M.fresh();r.scenes[1].id=r.scenes[0].id;assert.throws(()=>M.validate(r));});
test('project.duplicate-key',()=>{let r=M.fresh();r.scenes[1].keys[1].id='k1';assert.throws(()=>M.validate(r));});
test('project.max-scenes',()=>{let r=M.fresh();r.scenes=Array(101).fill(r.scenes[0]);assert.throws(()=>M.validate(r));});
test('capability.cannot-import-live',()=>{let r=M.fresh();for(const k in r.capabilities)r.capabilities[k]=true;assert(Object.values(M.validate(r).capabilities).every(x=>x===false));});
test('project.unknown-fields-removed',()=>{let r=M.fresh();r.backendCommand='connect';assert(!('backendCommand' in M.validate(r)));});
test('scene.focus-is-not-output-selection',()=>{const s=new M.Store();const before=s.data.scenes.map(x=>x.checked);s.data.selected='s3';assert.deepEqual(s.data.scenes.map(x=>x.checked),before);});
test('scene.per-scene-overrides',()=>{const s=new M.Store();s.set('camera','fov',77);s.data.selected='s1';assert.equal(s.scene.camera.fov,48);s.data.selected='s2';assert.equal(s.scene.camera.fov,77);});
for(const variant of ['LD','LN'])for(const theme of ['light','dark','system'])for(const view of ['main','easy','detail','camera','curve','color','material','export']){
 test(`state-preservation.${variant}.${theme}.${view}`,()=>{const s=new M.Store();s.set('camera','fov',73);s.set('grade','exposure',.6);s.key(3.2,81);s.data.time=7.25;const scenes=JSON.stringify(s.data.scenes);s.data.variant=variant;s.data.theme=theme;s.data.view=view;const after=new M.Store(JSON.parse(s.serialize()));assert.equal(JSON.stringify(after.data.scenes),scenes);assert.equal(after.data.time,7.25);});
}
for(const [key,min,max] of [['fov',20,110],['yaw',-180,180],['distance',500,1400],['height',0,900]])test('camera.clamp.'+key,()=>{const s=new M.Store();s.set('camera',key,max+1e6);assert.equal(s.scene.camera[key],max);s.set('camera',key,min-1e6);assert.equal(s.scene.camera[key],min);});
test('history.undo-redo',()=>{const s=new M.Store();s.set('camera','fov',73);s.undo();assert.equal(s.scene.camera.fov,48);s.redo();assert.equal(s.scene.camera.fov,73);});
test('history.new-change-clears-redo',()=>{const s=new M.Store();s.set('camera','fov',73);s.undo();s.set('camera','fov',60);assert.equal(s.redo(),false);});
test('key.quantized',()=>{const s=new M.Store();s.key(3.127,80);assert(s.scene.keys.some(x=>Math.abs(x.t-94/30)<1e-9));});
test('key.same-time-updates-not-duplicates',()=>{const s=new M.Store();s.key(5,81);assert.equal(s.scene.keys.length,3);assert.equal(s.scene.keys.find(k=>k.t===5).value,81);});
test('curve.linear',()=>assert.equal(M.interpolate([{t:0,value:40,ease:'linear'},{t:10,value:80}],2.5),50));
test('curve.hold',()=>assert.equal(M.interpolate([{t:0,value:40,ease:'hold'},{t:10,value:80}],2.5),40));
test('curve.smooth-endpoints',()=>{const k=[{t:0,value:40,ease:'smooth'},{t:10,value:80}];assert.equal(M.interpolate(k,0),40);assert.equal(M.interpolate(k,10),80);assert.equal(M.interpolate(k,5),60);});
test('curve.empty',()=>assert.equal(M.interpolate([],3),48));
for(const motion of M.motions)test('motion.persist.'+motion,()=>{const s=new M.Store();s.set('assets','motion',motion);assert.equal(new M.Store(JSON.parse(s.serialize())).scene.assets.motion,motion);});
for(const style of M.styles)test('style.persist.'+style,()=>{const s=new M.Store();s.set('camera','style',style);assert.equal(new M.Store(JSON.parse(s.serialize())).scene.camera.style,style);});
const result={cases,count:cases.length,passed:cases.filter(x=>x.status==='PASS').length,failed:cases.filter(x=>x.status==='FAIL').length,scope:'Node.js isolated shared-model tests; no browser or Windows input; not LoL/GPU/audio/recording/UI E2E',node:process.version};
fs.mkdirSync(path.join(root,'tests'),{recursive:true});fs.writeFileSync(path.join(root,'tests/MODEL_TEST_RESULTS.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({count:result.count,passed:result.passed,failed:result.failed}));if(result.failed)process.exitCode=1;
