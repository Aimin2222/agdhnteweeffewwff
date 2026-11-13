// AutoCine UI70 standalone read-only CLI. Node.js standard library only.
// Usage: node LoL_AutoCine/qa/ui70_parallel_20261113/run_offline_audit.mjs
// Does not launch AutoCine, LoL, GPU/audio, create output files or change settings.
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {auditUi70} from './audit_ui70_core.mjs';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const SOURCES=Object.freeze({
 ledger:['LoL_AutoCine/design/ui/final_implementation_spec_20261028/specs/FEATURE_IMPLEMENTATION_LEDGER_70.json','3815395f03c94681565da07e33fcc7d2408e0600'],
 sections:['LoL_AutoCine/design/ui/final_implementation_spec_20261028/specs/FEATURE_SECTIONS_70.json','af824c4c5d42c09ca621efc9ba783cf6560f125f'],
 screens:['LoL_AutoCine/design/ui/final_implementation_spec_20261028/specs/SCREEN_SPECIFICATIONS.json','3b1d5b36670a6e84c9131ec2b70022de613c78e4'],
 controls:['LoL_AutoCine/design/ui/final_implementation_spec_20261028/specs/CONTROL_CONTRACTS.json','aa9b7f04e35fe83eb22e159806a46264bd7b8a84'],
 tests:['LoL_AutoCine/design/ui/final_implementation_spec_20261028/specs/TEST_CASES.json','27c9db1ecf2c95c302cd2f1d5f67c65c09c44a09'],
 placements:['LoL_AutoCine/design/ui/c3_acceptance_20261027/specs/FUNCTION_PLACEMENT_70.json','bb74402c70956111c172d2303dc28c65b99b5db9'],
 bindings:['LoL_AutoCine/design/ui/c3_refinement_20261027/specs/FEATURE_BINDINGS_70.json','97faab8f713b9f66cd3ff7901cd5c63dac9c94a5'],
 fidelity:['LoL_AutoCine/design/ui/final_implementation_spec_20261028/references/C3_FIDELITY_CONTRACT.json','8760ed0fd11f1750d7e476cf0015272585eaa69e']
});
function safeFile(relative){
 if(typeof relative!=='string'||!relative.startsWith('LoL_AutoCine/')||
    relative.includes('\\')||relative.split('/').some(s=>!s||s==='.'||s==='..'))
   throw new Error('AC_UI70_PATH_UNSAFE');
 const full=path.resolve(ROOT,relative);
 if(!full.startsWith(ROOT+path.sep))throw new Error('AC_UI70_PATH_ESCAPES_REPO');
 let dir=ROOT;
 for(const p of relative.split('/')){
   dir=path.join(dir,p);
   const stat=fs.lstatSync(dir);
   if(stat.isSymbolicLink())throw new Error('AC_UI70_SYMLINK_BLOCKED');
 }
 if(!fs.statSync(full).isFile())throw new Error('AC_UI70_NOT_A_FILE');
 return full;
}
function gitBlobSha(raw){
 const header=Buffer.from('blob '+raw.length+'\0','ascii');
 return createHash('sha1').update(header).update(raw).digest('hex');
}
function fail(reason){
 console.log(JSON.stringify({
  schema:'AC_UI70_LOCAL_CLI_V1',status:'BLOCKED',reason:String(reason).slice(0,170),
  runtime_app:'NOT_RUN',product_tests:'NOT_RUN',formal_app_accepted:false
 },null,2));
 process.exitCode=2;
}
if(process.argv.length!==2){
 fail('AC_UI70_ARGUMENTS_NOT_ALLOWED');
}else{
 try{
  const d={},pins={};
  for(const [key,[relative,sha]] of Object.entries(SOURCES)){
   const bytes=fs.readFileSync(safeFile(relative));
   const actual=gitBlobSha(bytes);
   if(actual!==sha)throw new Error('AC_UI70_SOURCE_PIN_MISMATCH:'+key);
   d[key]=JSON.parse(bytes.toString('utf8'));
   pins[key]=actual;
  }
  const paths=new Set();
  // Source-reference availability is checked only, not runtime readiness.
  for(const row of d.ledger.rows)paths.add(row.existing_location?.path);
  for(const row of d.sections.sections)paths.add(row.current_backend?.path);
  for(const row of d.controls.controls)if(row.current_source?.path)paths.add(row.current_source.path);
  const present=[];
  for(const relative of paths){safeFile(relative);present.push(relative)}
  const audit=auditUi70(d,present);
  console.log(JSON.stringify({
   schema:'AC_UI70_LOCAL_CLI_V1',status:audit.static_contract==='PASS'?'CONTRACT_PASS_NOT_APP_PASS':'BLOCKED',
   baseline:'PR56 head b4f8b0af7633da5f362ab84b901b5cde69c8adc0',
   code_changed:false,window_settings_changed:false,app_launched:false,
   runtime_app:'NOT_RUN',product_tests:'NOT_RUN',formal_app_accepted:false,
   pinned_input_blobs:pins,source_paths_checked:present.length,
   counts:audit.counts,problems:audit.problems
  },null,2));
  if(audit.static_contract!=='PASS')process.exitCode=2;
 }catch(e){fail(e?.message||'AC_UI70_UNKNOWN_ERROR')}
}
