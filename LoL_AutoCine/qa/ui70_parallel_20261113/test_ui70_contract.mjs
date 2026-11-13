// AutoCine UI70 negative mutation tests. Read-only, no app/LoL/GPU run.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {auditUi70} from './audit_ui70_core.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const base='LoL_AutoCine/design/ui/final_implementation_spec_20261028/';
const paths={
 ledger:base+'specs/FEATURE_IMPLEMENTATION_LEDGER_70.json',
 sections:base+'specs/FEATURE_SECTIONS_70.json',
 screens:base+'specs/SCREEN_SPECIFICATIONS.json',
 controls:base+'specs/CONTROL_CONTRACTS.json',
 tests:base+'specs/TEST_CASES.json',
 placements:'LoL_AutoCine/design/ui/c3_acceptance_20261027/specs/FUNCTION_PLACEMENT_70.json',
 bindings:'LoL_AutoCine/design/ui/c3_refinement_20261027/specs/FEATURE_BINDINGS_70.json',
 fidelity:base+'references/C3_FIDELITY_CONTRACT.json'
};
const docs=Object.fromEntries(Object.entries(paths).map(([k,p])=>[k,JSON.parse(fs.readFileSync(path.join(root,p),'utf8'))]));
const tracked=new Set([
 ...docs.ledger.rows.map(x=>x.existing_location?.path),
 ...docs.sections.sections.map(x=>x.current_backend?.path),
 ...docs.controls.controls.map(x=>x.current_source?.path).filter(Boolean)
]);
const mutation=[
 ['drop_feature',d=>d.ledger.rows.pop()],
 ['duplicate_feature_id',d=>d.ledger.rows[1].id=d.ledger.rows[0].id],
 ['extra_feature',d=>d.ledger.rows.push({...d.ledger.rows[0],id:'EXTRA'})],
 ['missing_section',d=>d.sections.sections.pop()],
 ['missing_binding',d=>d.bindings.items.pop()],
 ['missing_placement',d=>d.placements.items.pop()],
 ['duplicate_section',d=>d.sections.sections[1].feature=d.sections.sections[0].feature],
 ['wrong_route_family',d=>d.ledger.rows[0].entrances.C3.screen='R1.main'],
 ['missing_route_screen',d=>d.ledger.rows[0].entrances.R1.screen='R1.MISSING'],
 ['wrong_route_section',d=>d.ledger.rows[0].entrances.R2.section_id='feature-FAKE'],
 ['route_removed',d=>delete d.ledger.rows[0].entrances.R2],
 ['false_product_test_pass',d=>d.tests.cases[0].status='PASS'],
 ['false_runtime_pass',d=>d.placements.items[0].runtime_status='PASS'],
 ['false_unit_pass',d=>d.ledger.rows[0].unit_test.status='PASS'],
 ['false_windows_pass',d=>d.ledger.rows[0].windows_test.status='PASS'],
 ['missing_test_link',d=>d.ledger.rows[0].unit_test.id='UT-BOGUS'],
 ['missing_screen',d=>d.screens.screens.pop()],
 ['duplicate_screen',d=>d.screens.screens[1].id=d.screens.screens[0].id],
 ['missing_control',d=>d.controls.controls.pop()],
 ['dangling_control',d=>d.screens.screens[0].controls.push('missing.control')],
 ['wrong_category',d=>d.placements.items[0].primary_category='FAKE'],
 ['wrong_access',d=>d.ledger.rows[0].baseline_access='FAKE'],
 ['wrong_identity',d=>d.fidelity.identity.screen_id='C3-P'],
 ['swap_c3_ps',d=>d.fidelity.C3PS_are_not_replacements=false],
 ['missing_source',d=>d.ledger.rows[0].existing_location.path='LoL_AutoCine/core/UNKNOWN.py'],
 ['unsafe_source',d=>d.ledger.rows[0].existing_location.path='../secrets'],
 ['wrong_feature_name',d=>d.bindings.items[0].name='tampered'],
 ['duplicate_test',d=>d.tests.cases[1].id=d.tests.cases[0].id],
 ['missing_test_case',d=>d.tests.cases.pop()],
 ['route_extra',d=>d.ledger.rows[0].entrances.EXTRA=d.ledger.rows[0].entrances.C3]
];
const errors=[],baseResult=auditUi70(docs,tracked);
if(baseResult.static_contract!=='PASS')errors.push('BASELINE_NOT_PASS');
for(const [id,mutate] of mutation){
 const changed=JSON.parse(JSON.stringify(docs));
 mutate(changed);
 if(auditUi70(changed,tracked).static_contract!=='BLOCKED')errors.push(id);
}
console.log(JSON.stringify({
 schema:'AC_UI70_NEGATIVE_QA_V1',
 status:errors.length?'BLOCKED':'OFFLINE_CONTRACT_TEST_PASS_NOT_APP_PASS',
 baseline_contract:baseResult.static_contract,
 negative_mutation_cases:mutation.length,
 mutation_rejections:mutation.length-errors.filter(x=>x!=='BASELINE_NOT_PASS').length,
 errors,
 windows:'NOT_RUN',app:'NOT_RUN',product_tests:'NOT_RUN',
 formal_acceptance:false
},null,2));
if(errors.length)process.exitCode=2;
