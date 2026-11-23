"""v669: same numeric F/J is selectable only with distinct sealed physical input.
Synthetic local receipts + actual browser JS. No DB2, HTTP, Native or cache writes.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
import v113_local_web_api as web


class VerifiedPhysicalFJIdentity(unittest.TestCase):
    def test_local_existing_v212_and_saved_v113_projection_is_read_only(self):
        build = "12.1.5.70961"
        gem_sets = ([240001, 240002, 240003, 240004],
                    [240005, 240006, 240007, 240008])
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td) / "runs"
            docs = root / "_fresh_season_sources" / ("wago_" + build) / "fresh_source"
            docs.mkdir(parents=True)
            for letter, gem_ids in zip(("a", "b"), gem_sets):
                digest = letter * 64
                sealed = {
                    "manifest_sha256": digest,
                    "game_build": build,
                    "target_ilevel": 334,
                    "official_J": 92,
                    "official_F": 165,
                    "official_O_physical_source": None,
                    "official_F_physical_source": {
                        "physical_item_id": 241324,
                        "crafting_quality": 2,
                        "F_rating": 165,
                        "simc_input_token": "flask_of_thalassian_resistance_2"
                    }
                }
                snapshot = {
                    "environment_result": {
                        "source_compilation": {
                            "physical_gem_layout_unadmitted": {
                                "schema": "v271_user_socket_gem_layout_stage_v1",
                                "status": "PHYSICAL_GEMS_STAGED_SOURCE_AND_SOCKET_PROOFS_PENDING",
                                "ordinary_gem_ids": list(gem_ids),
                                "special_gem_id": None,
                                "socket_total": 4
                            }
                        }
                    }
                }
                (docs / ("v212_installed_" + digest[:20] + ".json")).write_text(
                    json.dumps(sealed), encoding="utf8")
                (docs / ("v113_profile_" + digest[:20] + ".json")).write_text(
                    json.dumps(snapshot), encoding="utf8")
            def read_json(path, max_bytes=None):
                return json.loads(path.read_text("utf8")), b""
            def verified_find(*args, **kwargs):
                return {"installed_manifest_sha256":
                        kwargs["expected_installed_manifest_sha256"]}
            jobs = web.LocalJobs(root, source_credential_store=object())
            with mock.patch.object(web.environment_manifest, "read_json",
                                   side_effect=read_json), \
                 mock.patch.object(web.environment_manifest,
                                   "verify_fresh_installed_environment"), \
                 mock.patch.object(web.environment_build,
                                   "find_verified_installed_season_environment",
                                   side_effect=verified_find), \
                 mock.patch.object(web.official_ko_env, "read_names",
                                   return_value={}):
                result = jobs.installed_oil_loadouts(334, game_build=build)
            rows = result["verified_base_flask_installs"]
            self.assertEqual(len(rows), 2)
            self.assertEqual([row["ordinary_gem_item_ids"] for row in rows],
                             list(gem_sets))
            self.assertEqual([row["flask_quality"] for row in rows], [2, 2])
            self.assertEqual([row["J"] for row in rows], [92, 92])
            self.assertEqual([row["F"] for row in rows], [165, 165])
            self.assertNotEqual(rows[0]["installed_manifest_sha256"],
                                rows[1]["installed_manifest_sha256"])
            self.assertEqual(result["native_calls"], 0)
            self.assertEqual(result["network_calls"], 0)

    def test_real_ui_only_enables_distinct_physical_inputs(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node is needed for actual JS regression")
        harness = r"""
const fs=require('fs'), assert=require('assert');
const raw=fs.readFileSync(process.argv[1],'utf8');
const a=raw.indexOf('function installedConsumableScopeMatches(data) {');
const b=raw.indexOf('async function chooseInstalledFlask() {',a);
assert(a>=0&&b>a);
const nodes=Object.create(null);
const $=id=>(nodes[id]??={
 value:'',textContent:'',hidden:true,options:[],
 replaceChildren(...xs){this.options=[...xs];this.value=xs[0]?.value||'';},
 appendChild(x){this.options.push(x);}
});
const field=id=>String($(id).value||'');
const option=(value,label)=>({value:String(value),textContent:String(label),
                             disabled:false});
const document={getElementById:id=>$(id)};
const state={verifiedInstalledBuildFromThisPage:null,seasonGear:null};
$('season-game-build').value='12.1.5.70961';
$('ilevel').value='334';
const api=Function('state','field','$','document','option',
                   'refreshDefaultConsumableSummaries',
                   raw.slice(a,b)+'\nreturn {renderInstalledFlaskChoices};')(
 state,field,$,document,option,()=>{});
const base={
 flask_item_id:241324,flask_quality:2,J:92,F:165,socket_total:4
};
const A='a'.repeat(64),B='b'.repeat(64);
const gemA=[240001,240002,240003,240004];
const gemB=[240005,240006,240007,240008];
const mk=(sha,gems)=>({...base,installed_manifest_sha256:sha,
                         ordinary_gem_item_ids:gems});
const payload=(rows)=>({
 schema:'v113_verified_installed_oil_loadouts_v1',
 game_build:'12.1.5.70961',target_ilevel:334,
 verified_base_flask_installs:rows,verified_flasks:[]
});
api.renderInstalledFlaskChoices(payload([mk(A,gemA),mk(B,gemB)]));
const sel=$('season-verified-budget');
assert.equal(state.verifiedBaseFlaskInstalls.length,2);
assert.strictEqual($('season-verified-budget-group').hidden,false);
assert.equal(sel.options.length,3);
assert.equal(sel.options[1].disabled,false);
assert.equal(sel.options[2].disabled,false);
assert(sel.options[1].textContent.includes('#240001'));
assert(sel.options[2].textContent.includes('#240005'));
assert(!sel.options[1].textContent.includes(A));
assert(!sel.options[2].textContent.includes(B));
// Exact duplicate physical F/J profiles are NOT distinguished by arbitrary SHA.
api.renderInstalledFlaskChoices(payload([mk(A,gemA),mk(B,gemA)]));
assert.equal(sel.options[1].disabled,true);
assert.equal(sel.options[2].disabled,true);
assert($('season-verified-budget-status').textContent.includes('원본'));
// A fake/missing physical gem identity never becomes selectable.
api.renderInstalledFlaskChoices(payload([mk(A,gemA),mk(B,[])]));
assert.equal(state.verifiedBaseFlaskInstalls.length,1);
// The same installed data for a different build cannot be reused.
$('season-game-build').value='12.1.5.70575';
api.renderInstalledFlaskChoices(payload([mk(A,gemA),mk(B,gemB)]));
assert.equal(state.verifiedBaseFlaskInstalls.length,0);
console.log('V669_PHYSICAL_FJ_UI_EXACT_CHOICES_PASS');
"""
        p = subprocess.run([node, "-e", harness,
                            str(ROOT / "runner/webui/app.js")],
                           cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("V669_PHYSICAL_FJ_UI_EXACT_CHOICES_PASS", p.stdout)


class SealedFJCollisionReceipt(unittest.TestCase):
    def test_existing_v212_diff_categories_only_not_auto_approved(self):
        build="12.1.5.70961"
        sha_a,sha_b="a"*64,"b"*64
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)/"runs"
            folder=root/"_fresh_season_sources"/("wago_"+build)/"fresh_source"
            folder.mkdir(parents=True)
            for sha,rev,proof in (
                    (sha_a,"revision-A","j-evidence-A"),
                    (sha_b,"revision-B","j-evidence-B")):
                doc={
                    "manifest_sha256":sha,"game_build":build,
                    "target_ilevel":334,"official_G":2850,
                    "official_J":92,"official_F":165,"official_B":3107,
                    "official_T":3107,"manual_final_T_authoritative":False,
                    "simc_revision":rev,"trusted_budget_component_source_identities":{
                        "G":{"source_sha256":"same"},
                        "J":{"source_sha256":proof},
                        "F":{"source_sha256":"same"},
                        "O":{"source_sha256":"same"}},
                    "official_F_physical_source":{
                        "physical_item_id":241324,"crafting_quality":2,
                        "F_rating":165,"simc_input_token":"flask_2"},
                    "official_O_physical_source":None}
                profile={"environment_result":{"source_compilation":{
                    "physical_gem_layout_unadmitted":{
                        "schema":"v271_user_socket_gem_layout_stage_v1",
                        "status":"PHYSICAL_GEMS_STAGED_SOURCE_AND_SOCKET_PROOFS_PENDING",
                        "ordinary_gem_ids":[240001,240002,240003,240004],
                        "special_gem_id":None,"socket_total":4}}}}
                (folder/("v212_installed_"+sha[:20]+".json")).write_text(
                    json.dumps(doc),encoding="utf8")
                (folder/("v113_profile_"+sha[:20]+".json")).write_text(
                    json.dumps(profile),encoding="utf8")
            before={p.name:p.read_bytes() for p in folder.iterdir()}
            def exact(*args,**kwargs):
                return {"installed_manifest_sha256":
                        kwargs["expected_installed_manifest_sha256"]}
            def read(path,*args):
                return json.loads(path.read_text("utf8")), "synthetic"
            jobs=web.LocalJobs(root,source_credential_store=object())
            with mock.patch.object(web.environment_manifest,"read_json",
                                   side_effect=read), \
                 mock.patch.object(web.environment_manifest,
                                   "verify_fresh_installed_environment"), \
                 mock.patch.object(web.environment_build,
                                   "find_verified_installed_season_environment",
                                   side_effect=exact), \
                 mock.patch.object(web.official_ko_env,"read_names",
                                   return_value={}), \
                 mock.patch.object(web.subprocess,"Popen",
                                   side_effect=AssertionError("NO_NATIVE")):
                data=jobs.installed_oil_loadouts(334,game_build=build)
            self.assertEqual(len(data["verified_base_flask_installs"]),2)
            diag=data["verified_base_fj_collision_diagnostics"]
            self.assertEqual(len(diag),1)
            self.assertEqual(diag[0]["installed_count"],2)
            self.assertEqual(diag[0]["difference_codes"],
                             ["J_SOURCE","SIMC_REVISION"])
            serialized=json.dumps(diag)
            for secret in (sha_a,sha_b,str(folder),"revision-A",
                           "j-evidence-A","source_sha256"):
                self.assertNotIn(secret,serialized)
            self.assertEqual(data["native_calls"],0)
            self.assertEqual(data["network_calls"],0)
            self.assertEqual(before,
                {p.name:p.read_bytes() for p in folder.iterdir()},
                "read-only collision comparison cannot edit saved receipts")

    def test_identical_known_fields_do_not_make_multiple_sha_selectable(self):
        vals={"simc_revision":"same",
              "trusted_budget_component_source_identities":{}}
        a=web._v670_sealed_fj_difference_proofs(vals,{})
        b=web._v670_sealed_fj_difference_proofs(dict(vals),{})
        key=(241324,2,165,92,4,(240001,240002,240003,240004))
        result=web._v670_colliding_fj_diagnostics([(key,a),(key,b)])
        self.assertEqual(result[0]["difference_codes"],
                         ["OTHER_SEALED_IDENTITY"])

    def test_real_ui_safe_copy_only_after_exact_local_scope(self):
        node=shutil.which("node")
        if node is None:self.skipTest("Node needed")
        harness=r"""
const fs=require('fs'), assert=require('assert');
const raw=fs.readFileSync(process.argv[1],'utf8');
const a=raw.indexOf('function installedConsumableScopeMatches(data) {');
const b=raw.indexOf('async function chooseInstalledFlask()',a);
assert(a>=0&&b>a);
const nodes=Object.create(null),copies=[],notices=[];
const $=id=>(nodes[id]??={
 value:'',hidden:true,disabled:false,textContent:'',options:[],
 replaceChildren(...items){this.options=items;this.value=items[0]?.value||'';},
 appendChild(item){this.options.push(item)}
});
const field=id=>String($(id).value||'');
const valueInt=id=>Number(field(id));
const document={getElementById:id=>$(id)};
const option=(value,label)=>({value:String(value),textContent:String(label),
 disabled:false});
const navigator={clipboard:{writeText:async text=>copies.push(text)}};
const setNotice=message=>notices.push(message);
const state={seasonGear:null,verifiedInstalledBuildFromThisPage:null};
$('season-game-build').value='12.1.5.70961';
$('ilevel').value='334';
const funcs=Function('state','field','valueInt','$','document','option',
  'refreshDefaultConsumableSummaries','navigator','setNotice',
  raw.slice(a,b)+'\nreturn {renderInstalledFlaskChoices,copyVerifiedFjCollisionDiagnostic};')(
  state,field,valueInt,$,document,option,()=>{},navigator,setNotice);
const A='a'.repeat(64),B='b'.repeat(64);
const base={flask_item_id:241324,flask_quality:2,J:92,F:165,
 socket_total:4,ordinary_gem_item_ids:[240001,240002,240003,240004]};
const payload={
 schema:'v113_verified_installed_oil_loadouts_v1',
 game_build:'12.1.5.70961',target_ilevel:334,
 verified_base_flask_installs:[
   {...base,installed_manifest_sha256:A},
   {...base,installed_manifest_sha256:B}],
 verified_flasks:[],
 verified_base_fj_collision_diagnostics:[{
   flask_item_id:241324,flask_quality:2,
   F:165,J:92,socket_total:4,
   ordinary_gem_item_ids:[240001,240002,240003,240004],
   installed_count:2,difference_codes:['SIMC_REVISION','J_SOURCE']}]
};
state.oilCatalog=payload;
(async()=>{
  funcs.renderInstalledFlaskChoices(payload);
  const sel=$('season-verified-budget');
  assert.equal(sel.options[1].disabled,true);
  assert.equal(sel.options[2].disabled,true);
  assert.equal($('season-verified-fj-diagnostic-copy').hidden,false);
  assert($('season-verified-budget-status').textContent.includes('SimC revision'));
  await funcs.copyVerifiedFjCollisionDiagnostic();
  assert.equal(copies.length,1);
  const receipt=JSON.parse(copies[0]);
  assert.equal(receipt.groups[0].installed_count,2);
  assert.deepEqual(receipt.groups[0].difference_codes,
    ['SIMC_REVISION','J_SOURCE']);
  assert.equal(receipt.environment_ready,false);
  assert(!copies[0].includes(A));
  assert(!copies[0].includes(B));
  assert(!copies[0].includes('C:\\Users'));
  $('season-game-build').value='12.1.5.70575';
  funcs.renderInstalledFlaskChoices(payload);
  assert.equal($('season-verified-fj-diagnostic-copy').hidden,true);
  await funcs.copyVerifiedFjCollisionDiagnostic();
  assert.equal(copies.length,1,'Old build cannot copy as present evidence');
  console.log('V670_SEALED_FJ_COLLISION_SAFE_DIAGNOSTIC_PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
"""
        result=subprocess.run([node,"-e",harness,
                str(ROOT/"runner/webui/app.js")],cwd=ROOT,
                text=True,capture_output=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("V670_SEALED_FJ_COLLISION_SAFE_DIAGNOSTIC_PASS",
                      result.stdout)



if __name__ == "__main__":
    unittest.main()
