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

    def test_v671_stage_provenance_is_split_into_exact_existing_receipts(self):
        # All source and numeric owners are unchanged. Compare the exact
        # original v216/v217 stage identity fields without admitting either.
        a={
            "simc_revision":"same",
            "staged_source_environment_sha256":"a"*64,
            "original_v216_preflight_sha256":"1"*64,
            "original_v217_stage_receipts":{
                "v191_stage":"9"*64,"v211_stage":"2"*64,
                "v213_stage":"3"*64},
        }
        b={
            **a,
            "staged_source_environment_sha256":"b"*64,
            "original_v216_preflight_sha256":"4"*64,
            "original_v217_stage_receipts":{
                "v191_stage":"9"*64,"v211_stage":"5"*64,
                "v213_stage":"3"*64},
        }
        key=(241320,2,165,92,4,(240890,240898,240906,240914))
        reports=web._v670_colliding_fj_diagnostics([
            (key,web._v670_sealed_fj_difference_proofs(a,{})),
            (key,web._v670_sealed_fj_difference_proofs(b,{}))])
        self.assertEqual(reports[0]["difference_codes"],[
            "SOURCE_STAGES","STAGED_SOURCE_MANIFEST",
            "V216_PREFLIGHT_SEAL","V217_V211_RECEIPT"])
        serialized=json.dumps(reports)
        self.assertNotIn("a"*64,serialized)
        self.assertNotIn("b"*64,serialized)
        self.assertNotIn("5"*64,serialized)
        self.assertEqual(reports[0]["installed_count"],2)

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
  payload.verified_base_flask_installs=[
    {...base,installed_manifest_sha256:A,
     verified_runtime_equivalence_blocker_codes:['DIFFERENT_SOURCE_STAGE']},
    {...base,installed_manifest_sha256:B,
     verified_runtime_equivalence_blocker_codes:['DIFFERENT_SOURCE_STAGE']}
  ];
  funcs.renderInstalledFlaskChoices(payload);
  assert.equal(sel.options[1].disabled,true);
  assert($('season-verified-budget-status').textContent.includes('v212 단계'));
  // Two originally verified and *runnable-input-equal* receipts:
  // only the server-marked representative becomes selectable, never both.
  payload.verified_base_flask_installs=[
    {...base,installed_manifest_sha256:A,
     verified_runtime_equivalent_representative:true},
    {...base,installed_manifest_sha256:B,
     verified_runtime_equivalent_representative:false}
  ];
  funcs.renderInstalledFlaskChoices(payload);
  assert.equal(sel.options[1].disabled,false);
  assert.equal(sel.options[2].disabled,true);
  assert(sel.options[1].textContent.includes('동일 실행 입력'));
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



class VerifiedRuntimeInputEquivalence(unittest.TestCase):
    """Bounded original v212/v113 source projection; no new admission."""

    def test_only_preflight_link_diff_allows_same_runtime_fingerprint(self):
        with tempfile.TemporaryDirectory() as td:
            docs=pathlib.Path(td)/"wago_12.1.5.70961"/"fresh_source"
            docs.mkdir(parents=True)
            details=[]
            for installed_sha,stage_sha,preflight_sha in (
                    ("a"*64,"c"*64,"1"*64),("b"*64,"d"*64,"2"*64)):
                installed={
                    "manifest_sha256":installed_sha,
                    "staged_source_environment_sha256":stage_sha,
                    "original_v216_preflight_sha256":preflight_sha,
                    "original_v217_stage_receipts":{"v191_stage":"3"*64},
                    "source_catalog_artifact_sha256":"4"*64,
                    "game_build":"12.1.5.70961","target_ilevel":334,
                    "official_G":2850,"official_J":92,"official_F":165,
                    "official_B":3107,"official_T":3107,
                    "published_verified_options":[]}
                staged={
                    "manifest_sha256":stage_sha,
                    "original_v216_preflight_sha256":preflight_sha,
                    "original_v217_stage_receipts":{"v191_stage":"3"*64},
                    "source_catalog_artifact_sha256":"4"*64,
                    "game_build":"12.1.5.70961","target_ilevel":334,
                    "pending_core_requirements":["G/J/F/O"]}
                stage_path=docs/("v212_environment_"+stage_sha[:20]+".json")
                stage_path.write_text(json.dumps(staged),encoding="utf8")
                profile={
                    "schema":"v113_verified_v212_profile_source_snapshot_v1",
                    "installed_manifest_sha256":installed_sha,
                    "source_catalog_artifact_sha256":"4"*64,
                    "environment_result":{
                        "normal_build_entry":True,
                        "source_compilation":{
                            "preflight_sha256":preflight_sha,
                            "verified_environment_install":{
                                "manifest_sha256":installed_sha,
                                "stage_output_path":"different-original-path"},
                            "v098_source_only_profile_inputs_unadmitted":{
                                "flask":{"physical_item_id":241320,
                                         "simc_input_token":"flask_2"}},
                            "physical_gem_layout_unadmitted":{
                                "ordinary_gem_ids":[240890,240898,240906,240914]
                            }},
                        "verified_target_ilevel":334}}
                snapshot=docs/("v113_profile_"+installed_sha[:20]+".json")
                snapshot.write_bytes(
                    (web.stage_engine.canonical(profile)+"\n").encode("utf8"))
                details.append((installed,stage_path,snapshot))
            def read(path,*unused):
                return json.loads(path.read_text("utf8")), "trusted-original"
            with mock.patch.object(web.environment_manifest,"read_json",
                                   side_effect=read), \
                 mock.patch.object(web.environment_manifest,
                                   "verify_fresh_source_environment"), \
                 mock.patch.object(web.stage_engine,"verify_stage",
                                   return_value={"status":"REUSED_VERIFIED"}):
                first=web._v672_verified_runtime_inputs_digest(
                    docs,details[0][0],details[0][2])
                second=web._v672_verified_runtime_inputs_digest(
                    docs,details[1][0],details[1][2])
                self.assertIsNotNone(first)
                self.assertEqual(first,second)
                parts_a=web._v672_verified_runtime_inputs_digest(
                    docs,details[0][0],details[0][2],
                    return_component_digests=True)
                parts_b=web._v672_verified_runtime_inputs_digest(
                    docs,details[1][0],details[1][2],
                    return_component_digests=True)
                self.assertEqual(set(parts_a),
                                 {"installed","source_stage","runtime_snapshot"})
                self.assertEqual(parts_a,parts_b)
                # v673: original v216 preflight may vary in two
                # non-executable diagnostic collections. Both original
                # installed+stage receipts must STILL have been verified.
                altered=json.loads(details[1][1].read_text("utf8"))
                altered["pending_core_requirements"].append("OPTIONAL_DIFFERENT")
                altered["optional_item_missing"]={"999":"OPTIONAL_PROOF_PENDING"}
                details[1][1].write_text(json.dumps(altered),encoding="utf8")
                self.assertEqual(first,
                    web._v672_verified_runtime_inputs_digest(
                        docs,details[1][0],details[1][2]))
                # A different numeric/source-owner stage field is material,
                # even when ItemIDs, F/J and all optional labels match.
                altered["numeric_budget_preview_unadmitted"]={"J":999}
                details[1][1].write_text(json.dumps(altered),encoding="utf8")
                changed=web._v672_verified_runtime_inputs_digest(
                    docs,details[1][0],details[1][2])
                self.assertNotEqual(first,changed)
                changed_parts=web._v672_verified_runtime_inputs_digest(
                    docs,details[1][0],details[1][2],
                    return_component_digests=True)
                self.assertNotEqual(parts_a["source_stage"],
                                    changed_parts["source_stage"])
                self.assertEqual(parts_a["installed"],
                                 changed_parts["installed"])
                self.assertEqual(parts_a["runtime_snapshot"],
                                 changed_parts["runtime_snapshot"])
                altered.pop("numeric_budget_preview_unadmitted")
                details[1][1].write_text(json.dumps(altered),encoding="utf8")
                # A different saved SimC source input must not be merged.
                altered_profile=json.loads(details[1][2].read_text("utf8"))
                altered_profile["environment_result"]["source_compilation"][
                    "v098_source_only_profile_inputs_unadmitted"]["flask"][
                    "simc_input_token"]="different_input"
                details[1][2].write_bytes(
                    (web.stage_engine.canonical(altered_profile)+"\n").encode("utf8"))
                self.assertNotEqual(first,
                    web._v672_verified_runtime_inputs_digest(
                        docs,details[1][0],details[1][2]))
            # No receipt check, no runtime-equivalence proof.
            self.assertIsNone(web._v672_verified_runtime_inputs_digest(
                docs,details[0][0],details[0][2]))
            self.assertIsNone(web._v672_verified_runtime_inputs_digest(
                docs,details[0][0],docs/"missing_v113_profile.json"))



class CraftedEmbellishmentTwoColumnLayout(unittest.TestCase):
    def test_css_grids_real_generated_sibling_rows_not_outer_single_wrapper(self):
        css=(ROOT/"runner/webui/styles.css").read_text(encoding="utf8")
        js=(ROOT/"runner/webui/app.js").read_text(encoding="utf8")
        self.assertIn('parent.appendChild(group);',js)
        self.assertIn('row.className="gear-row"',js)
        self.assertIn('row.appendChild(grid);',js)
        # Both generated .gear-row siblings live under ONE .gear-group.
        # A grid on #crafted-rows alone cannot put them next to each other.
        section=css.split("/* v673: the generated crafted rows",1)[1]
        self.assertIn('#crafted-rows > .gear-group{',section)
        self.assertIn('display:grid;grid-template-columns:repeat(2,minmax(0,1fr))',section)
        self.assertIn('#crafted-rows .gear-fields{',section)
        self.assertIn('#crafted-rows .gear-fields label:has([data-field="item_id"])',section)
        self.assertIn('grid-column:1/-1',section)
        self.assertIn('#crafted-rows .gear-fields label[hidden]',section)
        self.assertIn('display:none!important',section)
        self.assertIn('@media(max-width:680px)',section)
        self.assertIn('grid-template-columns:1fr',section)
        self.assertIn('box-sizing:border-box',section)
        self.assertEqual(js.count('const limit=isSpecial?8:2;'),1)



class ConsumableDropdownLayoutRegression(unittest.TestCase):
    def test_v674_verified_fj_is_direct_full_width_grid_sibling(self):
        from html.parser import HTMLParser
        html=(ROOT/"runner/webui/index.html").read_text(encoding="utf8")
        class GridNesting(HTMLParser):
            def __init__(self):
                super().__init__(convert_charrefs=True)
                self.divs=[]
                self.parent=None
            def handle_starttag(self,tag,attrs):
                if tag!="div":
                    return
                data=dict(attrs)
                if data.get("id")=="season-verified-budget-group":
                    self.parent=self.divs[-1] if self.divs else {}
                self.divs.append(data)
            def handle_endtag(self,tag):
                if tag=="div" and self.divs:
                    self.divs.pop()
        structure=GridNesting()
        structure.feed(html)
        self.assertEqual(structure.parent.get("class"),"env-input-grid")
        segment=html.split('<div class="env-input-grid"',1)[1].split(
            '<div class="env-bottom-row">',1)[0]
        self.assertLess(segment.index('for="food"'),
                        segment.index('for="season-verified-flask"'))
        self.assertLess(segment.index('for="season-verified-flask"'),
                        segment.index('for="potion"'))
        self.assertLess(segment.index('for="potion"'),
                        segment.index('for="augmentation"'))
        self.assertLess(segment.index('for="augmentation"'),
                        segment.index('id="season-verified-budget-group"'))
        self.assertLess(segment.index('id="season-verified-budget-group"'),
                        segment.index('env-grid-cell env-omnium'))
        self.assertEqual(segment.count('id="season-verified-budget-group"'),1)

    def test_v674_consumables_are_readable_and_options_never_wrap(self):
        css=(ROOT/"runner/webui/styles.css").read_text(encoding="utf8")
        js=(ROOT/"runner/webui/app.js").read_text(encoding="utf8")
        section=css.split("/* v674: scoped consumable layout.",1)[1]
        self.assertIn("nth-child(n+5):nth-child(-n+8)",section)
        self.assertIn("grid-column:span 2!important",section)
        self.assertIn("#season-verified-budget-group[hidden]",section)
        self.assertIn("grid-template-columns:minmax(0,1fr)",section)
        self.assertIn("overflow-wrap:anywhere;white-space:normal",section)
        self.assertIn("max-width:100%",section)
        self.assertIn(".choice-results .choice-result",section)
        self.assertIn("white-space:nowrap;overflow:hidden;text-overflow:ellipsis",section)
        self.assertIn("@media(max-width:880px)",section)
        self.assertIn("@media(max-width:540px)",section)
        self.assertIn("b.title=opt.textContent;",js)
        self.assertIn('input.title=selected?.textContent||"";',js)
        # Avoid changing stored SimC identity, verified install selection or
        # option IDs just to improve a narrow dropdown's presentation.
        self.assertIn("candidate.disabled=duplicate&&!equivalentRepresentative",js)
        self.assertIn("candidate=option(item.installed_manifest_sha256,text)",js)



if __name__ == "__main__":
    unittest.main()
