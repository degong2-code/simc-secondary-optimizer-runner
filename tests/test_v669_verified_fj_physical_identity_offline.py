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
                    "simc_revision": "synthetic-" + letter,
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
                                   return_value={}), \
                 mock.patch.object(web,
                                   "_verified_saved_profile_snapshot",
                                   side_effect=lambda docs, doc, snapshot:
                                       json.loads(snapshot.read_text("utf8"))):
                result = jobs.installed_oil_loadouts(334, game_build=build)
            rows = result["verified_base_flask_installs"]
            self.assertEqual(len(rows), 2)
            self.assertEqual([row["ordinary_gem_item_ids"] for row in rows],
                             list(gem_sets))
            self.assertEqual([row["flask_quality"] for row in rows], [2, 2])
            self.assertEqual([row["J"] for row in rows], [92, 92])
            self.assertEqual([row["F"] for row in rows], [165, 165])
            self.assertTrue(all(row["individually_verified"] for row in rows))
            self.assertEqual(set(row["simc_revision"] for row in rows),
                             {"synthetic-a","synthetic-b"})
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
 value:'',textContent:'',hidden:true,disabled:false,options:[],
 replaceChildren(...xs){this.options=[...xs];this.value=xs[0]?.value||'';},
 appendChild(x){if(x.tag==='optgroup')this.options.push(...x.children);else this.options.push(x);}
});
const field=id=>String($(id).value||'');
const option=(value,label)=>({value:String(value),textContent:String(label),disabled:false});
const document={getElementById:id=>$(id),createElement:tag=>{
 assert.equal(tag,"optgroup");
 return {tag,children:[],appendChild(x){this.children.push(x)}};
}};
const state={verifiedInstalledBuildFromThisPage:null,seasonGear:null};
$('season-game-build').value='12.1.5.70961';
$('ilevel').value='334';
const api=Function('state','field','$','document','option',
  'refreshDefaultConsumableSummaries',
  raw.slice(a,b)+'\nreturn {renderInstalledFlaskChoices};')(
  state,field,$,document,option,()=>{});
const base={
 flask_item_id:241324,flask_quality:2,J:92,F:165,socket_total:4,
 ordinary_gem_item_ids:[240001,240002,240003,240004]
};
const A='a'.repeat(64),B='b'.repeat(64);
const mk=(sha,verified=true)=>({...base,
  installed_manifest_sha256:sha,individually_verified:verified,
  simc_revision:sha===A?'revision-A':'revision-B'});
const payload=rows=>({schema:'v113_verified_installed_oil_loadouts_v1',
  game_build:'12.1.5.70961',target_ilevel:334,
  verified_base_flask_installs:rows,verified_flasks:[],
  verified_base_fj_collision_diagnostics:[]});
api.renderInstalledFlaskChoices(payload([mk(A),mk(B)]));
const sel=$('season-verified-budget');
assert.equal(state.verifiedBaseFlaskInstalls.length,2);
assert.strictEqual($('season-verified-budget-group').hidden,false);
assert.equal(sel.options.length,3);
assert.equal(sel.options[1].disabled,false);
assert.equal(sel.options[2].disabled,false);
assert(sel.options[1].textContent.includes('구성 1'));
assert(sel.options[2].textContent.includes('구성 1'));
assert(sel.options[1].textContent.includes('저장본 1'));
assert(sel.options[2].textContent.includes('저장본 2'));
assert.deepEqual(sel.options.slice(1).map(x=>x.value),[A,B]);
assert(sel.options[1].title.includes('revision-A'));
assert(!sel.options[1].textContent.includes(A));
assert(!sel.options[2].textContent.includes(B));
assert($('season-verified-budget-status').textContent.includes('구성 1종 · 저장본 2개'));
assert.equal($('season-verified-budget-diagnostic-detail').hidden,true);
assert.equal($('season-verified-fj-diagnostic-copy').hidden,true);
// Each original v212+v113 source must be admitted on its own exact receipt.
// A fabricated or not-yet-verified row must not enter the selector.
api.renderInstalledFlaskChoices(payload([mk(A),mk(B,false)]));
assert.equal(state.verifiedBaseFlaskInstalls.length,1);
assert.equal(sel.options.length,2);
assert.equal($('season-verified-budget-group').hidden,true);
sel.value=A;
api.renderInstalledFlaskChoices(payload([mk(A),mk(B)]));
assert.equal(sel.value,A,'prior exact selected SHA retained');
$('season-game-build').value='12.1.5.70575';
api.renderInstalledFlaskChoices(payload([mk(A),mk(B)]));
assert.equal(state.verifiedBaseFlaskInstalls.length,0);
console.log('V676_INDEPENDENT_EXACT_SHA_FJ_CHOICES_PASS');
"""
        p = subprocess.run([node, "-e", harness,
                            str(ROOT / "runner/webui/app.js")],
                           cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("V676_INDEPENDENT_EXACT_SHA_FJ_CHOICES_PASS", p.stdout)


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
                 mock.patch.object(web,"_verified_saved_profile_snapshot",
                                   side_effect=lambda docs,document,snapshot:
                                       json.loads(snapshot.read_text("utf8"))), \
                 mock.patch.object(web.subprocess,"Popen",
                                   side_effect=AssertionError("NO_NATIVE")):
                data=jobs.installed_oil_loadouts(334,game_build=build)
            self.assertEqual(len(data["verified_base_flask_installs"]),2)
            # Independent original receipts need no cross-source equality;
            # avoid any response with raw source SHA/provenance comparisons.
            self.assertEqual(data["verified_base_fj_collision_diagnostics"],[])
            self.assertTrue(all(
                item["individually_verified"]
                for item in data["verified_base_flask_installs"]))
            self.assertEqual({item["simc_revision"]
                              for item in data["verified_base_flask_installs"]},
                             {"revision-A","revision-B"})
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
const fs=require('fs'),assert=require('assert');
const raw=fs.readFileSync(process.argv[1],'utf8');
const a=raw.indexOf('function installedConsumableScopeMatches(data) {');
const b=raw.indexOf('async function chooseInstalledFlask()',a);
const nodes=Object.create(null),copies=[];
const $=id=>(nodes[id]??={
 value:'',hidden:true,disabled:false,textContent:'',options:[],
 replaceChildren(...items){this.options=items;this.value=items[0]?.value||'';},
 appendChild(item){if(item.tag==='optgroup')this.options.push(...item.children);else this.options.push(item)}
});
const field=id=>String($(id).value||'');
const valueInt=id=>Number(field(id));
const document={getElementById:id=>$(id),createElement:tag=>{
 assert.equal(tag,"optgroup");
 return {tag,children:[],appendChild(x){this.children.push(x)}};
}};
const option=(value,label)=>({value:String(value),textContent:String(label),
 disabled:false});
const navigator={clipboard:{writeText:async x=>copies.push(x)}};
const state={seasonGear:null,verifiedInstalledBuildFromThisPage:null};
$('season-game-build').value='12.1.5.70961';
$('ilevel').value='334';
const funcs=Function('state','field','valueInt','$','document','option',
  'refreshDefaultConsumableSummaries','navigator','setNotice',
  raw.slice(a,b)+'\nreturn {renderInstalledFlaskChoices,copyVerifiedFjCollisionDiagnostic};')(
  state,field,valueInt,$,document,option,()=>{},navigator,()=>{});
const A='a'.repeat(64),B='b'.repeat(64);
const mk=sha=>({
  flask_item_id:241324,flask_quality:2,J:92,F:165,socket_total:4,
  ordinary_gem_item_ids:[240001,240002,240003,240004],
  installed_manifest_sha256:sha,individually_verified:true
});
const payload={
 schema:'v113_verified_installed_oil_loadouts_v1',
 game_build:'12.1.5.70961',target_ilevel:334,
 verified_base_flask_installs:[mk(A),mk(B)],
 verified_flasks:[],
 verified_base_fj_collision_diagnostics:[{
  flask_item_id:241324,flask_quality:2,F:165,J:92,socket_total:4,
  ordinary_gem_item_ids:[240001,240002,240003,240004],
  installed_count:2,difference_codes:['SIMC_REVISION','J_SOURCE']}]
};
state.oilCatalog=payload;
(async()=>{
  funcs.renderInstalledFlaskChoices(payload);
  const sel=$('season-verified-budget');
  assert.equal(sel.options[1].disabled,false);
  assert.equal(sel.options[2].disabled,false);
  assert.equal($('season-verified-fj-diagnostic-copy').hidden,true);
  assert.equal($('season-verified-budget-diagnostic-detail').hidden,true);
  assert.equal(state.verifiedFjCollisionReport.length,0);
  await funcs.copyVerifiedFjCollisionDiagnostic();
  assert.equal(copies.length,0,'retired debug report must not leak through basic flow');
  assert($('season-verified-budget-status').textContent.length<110);
  console.log('V676_RETIRED_CROSS_INSTALL_DIAGNOSTIC_PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
"""
        result=subprocess.run([node,"-e",harness,
                str(ROOT/"runner/webui/app.js")],cwd=ROOT,
                text=True,capture_output=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("V676_RETIRED_CROSS_INSTALL_DIAGNOSTIC_PASS",
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
                                 {"installed","source_stage","runtime_snapshot","runtime_fields"})
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
        self.assertIn("item.individually_verified===true",js)
        self.assertIn("candidate=option(item.installed_manifest_sha256,savedLabel)",js)
        self.assertNotIn("candidate.disabled=duplicate",js)




class V675FieldLevelAndOptionDedupe(unittest.TestCase):
    def test_field_digests_only_known_codes_unknown_fails_closed(self):
        source={"schema":"v113_verified_v212_profile_source_snapshot_v1",
                "source_catalog_artifact_sha256":"a"*64,
                "environment_result":{
                    "normal_build_entry":True,"verified_target_ilevel":334,
                    "source_compilation":{
                        "v098_source_only_profile_inputs_unadmitted":{
                            "flask":{"physical_item_id":241320,
                                     "simc_input_token":"flask_2"}},
                        "physical_gem_layout_unadmitted":{
                            "ordinary_gem_ids":[240890,240898,240906,240914]}}}}
        baseline=web._v675_runtime_input_field_digests(source)
        self.assertIsNotNone(baseline)
        self.assertEqual(len(baseline),24)
        other=json.loads(json.dumps(source))
        other["environment_result"]["source_compilation"][
            "v098_source_only_profile_inputs_unadmitted"]["flask"][
                "simc_input_token"]="changed_simc_token"
        differences=web._v675_runtime_input_field_digests(other)
        self.assertEqual([name for name in baseline
                          if baseline[name]!=differences[name]],
                         ["COMPILATION_V098_PROFILE"])
        # Unknown additions never disappear or become an implicit approved
        # default; the OTHER_COMPILATION_FIELDS bucket changes.
        other=json.loads(json.dumps(source))
        other["environment_result"]["source_compilation"][
            "new_unrecognized_effect"]="non-default"
        differences=web._v675_runtime_input_field_digests(other)
        self.assertEqual([name for name in baseline
                          if baseline[name]!=differences[name]],
                         ["OTHER_COMPILATION_FIELDS"])
        # A missing value must differ from an explicitly present null.
        other=json.loads(json.dumps(source))
        other["environment_result"]["fresh_ordinary_gear"]=None
        differences=web._v675_runtime_input_field_digests(other)
        self.assertNotEqual(baseline["RUNTIME_ORDINARY_GEAR"],
                            differences["RUNTIME_ORDINARY_GEAR"])
        self.assertNotIn("changed_simc_token",json.dumps(differences))
        self.assertNotIn("241320",json.dumps(differences))

    def test_real_js_only_dedupes_identical_option_values(self):
        node=shutil.which("node")
        if node is None:
            self.skipTest("Node needed for actual JS guard")
        harness=r"""
const fs=require('fs'),assert=require('assert');
const raw=fs.readFileSync(process.argv[1],'utf8');
const a=raw.indexOf('function populateSelect(id, values, labeler) {');
const b=raw.indexOf('function field(id) {',a);
assert(a>=0 && b>a);
const nodes={};
const $=id=>(nodes[id]??={
 options:[],
 replaceChildren(){this.options=[]},
 appendChild(o){this.options.push(o)}
});
const option=(v,label)=>({value:String(v),textContent:String(label)});
const populateSelect=Function('$','option',raw.slice(a,b)+
 '\nreturn populateSelect;')($,option);
populateSelect('food',['source_default','source_default',
 'flask_same','flask_same','different_effect'],v=>v);
assert.deepEqual($('food').options.map(o=>o.value),
 ['source_default','flask_same','different_effect']);
populateSelect('potion',[0,'0',1,'1'],v=>String(v));
assert.deepEqual($('potion').options.map(o=>o.value),['0','1']);
console.log('V675_EXACT_OPTION_VALUES_ONLY_PASS');
"""
        completed=subprocess.run([node,"-e",harness,
            str(ROOT/"runner/webui/app.js")],cwd=ROOT,
            text=True,capture_output=True,timeout=20)
        self.assertEqual(completed.returncode,0,completed.stderr)
        self.assertIn("V675_EXACT_OPTION_VALUES_ONLY_PASS",completed.stdout)

    def test_detail_markup_unbroken_and_hidden_until_evidence(self):
        html=(ROOT/"runner/webui/index.html").read_text(encoding="utf8")
        css=(ROOT/"runner/webui/styles.css").read_text(encoding="utf8")
        self.assertEqual(html.count('id="season-verified-budget-diagnostic-detail"'),1)
        self.assertIn('<summary>원본 차이 자세히</summary>',html)
        self.assertIn('id="season-verified-budget-diagnostic-detail-text"',html)
        self.assertIn('#season-verified-budget-diagnostic-detail[hidden]',css)
        self.assertIn('white-space:normal',css.split('/* v675: long F/J reasons',1)[1])



if __name__ == "__main__":
    unittest.main()
