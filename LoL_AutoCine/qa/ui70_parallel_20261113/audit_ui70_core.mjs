// AutoCine UI70 independent offline contracts. Does not start app/GPU/LoL.
export function auditUi70(d, trackedPaths) {
  const problems=[], item=(code,info)=>{if(problems.length<150)problems.push({code,info:String(info??"")})};
  const array=(x)=>Array.isArray(x)?x:[];
  const count=(xs,key)=>xs.reduce((m,x)=>{const k=String(x?.[key]);m[k]=(m[k]||0)+1;return m},{});
  const unique=(xs,code)=>{const values=xs.map(x=>String(x));const set=new Set(values);if(set.size!==values.length)item(code,`duplicates=${values.length-set.size}`);return set};
  const eq=(a,b)=>JSON.stringify([...a].sort())===JSON.stringify([...b].sort());
  const exactKeys=(o,keys)=>o&&typeof o==="object"&&eq(Object.keys(o),keys);
  const legalPath=(s)=>typeof s==="string"&&s.startsWith("LoL_AutoCine/")&&!s.includes("\\")&&!s.split("/").some(p=>p===".."||p==="."||p===""||p.includes("\0"));
  const files=new Set(trackedPaths||[]);
  const checkPath=(p,id)=>{if(!legalPath(p))item("PATH_UNSAFE",id);else if(!files.has(p))item("SOURCE_NOT_TRACKED",id)};
  const ledger=array(d.ledger?.rows), sections=array(d.sections?.sections), placements=array(d.placements?.items), bindings=array(d.bindings?.items);
  const screens=array(d.screens?.screens), controls=array(d.controls?.controls), tests=array(d.tests?.cases);
  const ids=ledger.map(x=>x.id), sourceIds=unique(ids,"FEATURE_ID_DUPLICATE");
  for(const [key,arr,field] of [["ledger",ledger,"id"],["sections",sections,"feature"],["placements",placements,"id"],["bindings",bindings,"id"]]) {
    if(arr.length!==70)item("COUNT_70_INVALID",key+":"+arr.length);
    const ids2=unique(arr.map(x=>x[field]),"ID_DUPLICATE_"+key);
    if(!eq(sourceIds,ids2))item("FEATURE_ID_SET_MISMATCH",key);
  }
  if(d.ledger?.count!==70||d.placements?.total!==70||d.ledger?.no_deletions!==true)item("LEDGER_CLAIM_INVALID","count/total/no_deletions");
  const sMap=new Map(sections.map(x=>[x.feature,x])),pMap=new Map(placements.map(x=>[x.id,x])),bMap=new Map(bindings.map(x=>[x.id,x]));
  const allowed=new Set(["C3","R1","R2"]);
  if(screens.length!==36||d.screens?.count!==36)item("SCREEN_COUNT_INVALID",screens.length);
  const screenIds=unique(screens.map(x=>x.id),"SCREEN_ID_DUPLICATE");
  for(const fam of allowed){const sub=screens.filter(x=>x.id?.startsWith(fam+"."));if(sub.length!==12)item("FAMILY_12_INVALID",fam+":"+sub.length)}
  if(controls.length!==86||d.controls?.count!==86)item("CONTROL_COUNT_INVALID",controls.length);
  const controlIds=unique(controls.map(x=>x.id),"CONTROL_ID_DUPLICATE");
  for(const screen of screens) for(const c of array(screen.controls))if(!controlIds.has(c))item("SCREEN_CONTROL_MISSING",screen.id+":"+c);
  if(tests.length!==239||d.tests?.count!==239)item("TEST_CASE_COUNT_INVALID",tests.length);
  const testIds=unique(tests.map(x=>x.id),"TEST_ID_DUPLICATE");
  for(const t of tests)if(t.status!=="NOT_RUN")item("UNVERIFIED_PRODUCT_TEST_STATUS",t.id+":"+t.status);
  const categories=count(placements,"primary_category"),access=count(ledger,"baseline_access");
  for(const [cat,expected] of Object.entries({MAIN:8,EASY:4,DETAIL:2,SETTINGS:12,SPECIAL:39,LIBRARY:5}))if(categories[cat]!==expected)item("CATEGORY_TOTAL_MISMATCH",cat);
  for(const [cat,expected] of Object.entries({DIRECT_UI3:29,NATIVE_EDITOR:35,BACKEND_AUTOMATIC:4,UNIMPLEMENTED:2}))if(access[cat]!==expected)item("ACCESS_TOTAL_MISMATCH",cat);
  if(d.fidelity?.identity?.candidate_number!==3||d.fidelity?.identity?.family!=="testA"||d.fidelity?.identity?.screen_id!=="T-A-M"||d.fidelity?.C3PS_are_not_replacements!==true)item("C3_FIDELITY_IDENTITY", "must keep testA T-A-M not C3-P/C3-S");
  let edges=0;
  for(const row of ledger){
    const id=row.id,sect=sMap.get(id),place=pMap.get(id),binding=bMap.get(id);
    if(!sect||!place||!binding)continue;
    if(row.name!==place.name||row.name!==binding.name)item("FEATURE_NAME_MISMATCH",id);
    if(place.entry_test_id!=="FN-"+id||row.test_id!=="FN-"+id)item("FEATURE_TEST_ID_MISMATCH",id);
    if(row.unit_test?.id!=="UT-"+id||row.windows_test?.id!=="WIN-"+id||!testIds.has("UT-"+id)||!testIds.has("WIN-"+id))item("FEATURE_TEST_LINK_MISSING",id);
    if(row.unit_test?.status!=="NOT_RUN"||row.windows_test?.status!=="NOT_RUN"||place.runtime_status!=="NOT_RUN")item("FEATURE_RUNTIME_FALSE_PASS",id);
    if(sect.id!=="feature-"+id)item("SECTION_ID_BAD",id);
    if(!exactKeys(row.entrances,["C3","R1","R2"]))item("ENTRANCE_SET_INVALID",id);
    for(const f of allowed){
      const route=row.entrances?.[f];
      if(!route||!screenIds.has(route.screen)||!String(route.screen).startsWith(f+".")||route.section_id!=="feature-"+id||!array(sect.screen_ids).includes(route.screen))item("ROUTE_NOT_RESOLVED",id+"/"+f);
      else edges++;
    }
    if(!eq(array(sect.screen_ids).map(v=>v.split(".")[0]),["C3","R1","R2"]))item("SECTION_3UI_INVALID",id);
    checkPath(row.existing_location?.path,id);
    checkPath(sect.current_backend?.path,id);
  }
  if(edges!==210)item("ROUTE_EDGE_COUNT_INVALID",edges);
  for(const c of controls)if(c.current_source?.path)checkPath(c.current_source.path,"control:"+c.id);
  const counts={features:ledger.length,sections:sections.length,placements:placements.length,bindings:bindings.length,screens:screens.length,controls:controls.length,product_test_specs:tests.length,valid_route_edges:edges,access,categories};
  return {schema:"AC_UI70_STATIC_AUDIT_V1",static_contract:problems.length?"BLOCKED":"PASS",runtime_app:"NOT_RUN",windows_gpu_audio_lol:"NOT_RUN",product_tests:"NOT_RUN",formal_app_acceptance:false,counts,problems};
}
