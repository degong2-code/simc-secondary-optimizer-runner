"""v066: generic boundary synthetic class variation and real Native replay elsewhere.

Synthetic results in this module are explicitly NOT second-class SimC PASS.
No inherited v015 71/71 or v016 104/104 are reexecuted here.
"""
import copy,hashlib,json,pathlib,sys,tempfile,unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v046_static_item_cache as native
import v061_scenario_contract as contract
import v062_static_budget_bridge as budget
import v063_numeric_injection as numeric
import v066_profile_neutral_preflight as p
import v065_v015_scheduler_adapter as policy
from test_v064_adaptive_evaluator_port import make_fixture,SIMC_SHA
from test_v062_static_budget_bridge import record
from test_v063_numeric_injection import fake_doc

def fixture(character="mage",spec="arcane",role="spell"):
    normalized,compiled,cal,profile=make_fixture()
    fillers=[]
    selected={r["slot"] for group in normalized["scenario"]["equipment"].values()
              for r in group}
    for slot,row in compiled["native_gear_stats"].items():
        if slot not in selected:
            identity=row["identity"]
            fillers.append({"slot":slot,"item_id":identity["item_id"],
                            "ilevel":identity["ilevel"],
                            "options":identity["options"]})
    cache=native.empty_cache()
    for slot,row in compiled["native_gear_stats"].items():
        ident=row["identity"]
        raw={"slot":slot,"item_id":ident["item_id"],
             "ilevel":ident["ilevel"],"options":ident["options"]}
        record(cache,raw,row["secondary"])
    cfg=copy.deepcopy(normalized["scenario"])
    cfg["character"]["class"]=character
    cfg["character"]["spec"]=spec
    cfg["character"]["role"]=role
    if character!="mage":
        profile=profile.replace('mage="V031R3','warrior="V031R3',1)
        # Exact profile line is intentionally a synthetic harness;
        # this is NOT item compatibility evidence for warrior.
        if 'mage="' in profile:
            profile=profile.replace('mage="','warrior="',1)
        profile=profile.replace("spec=arcane","spec="+spec,1)
        profile=profile.replace("role=spell","role="+role,1)
    rows=[]
    for crit,haste in [(400,235),(430,205)]:
        source=profile
        for stat,value in (("crit",crit),("haste",haste),
                           ("mastery",400),("versatility",403)):
            import re
            source=re.sub(r"(?m)^gear_"+stat+r"_rating=[0-9]+$",
                          "gear_"+stat+"_rating="+str(value),source)
        rows.append({"input":source,"native":fake_doc(source)})
    return cfg,fillers,cache,profile,rows

class GenericNumericBoundary(unittest.TestCase):
    def test_mage_offline_synthetic_model_binds_without_hardcoding_334(self):
        cfg,fill,static,source,witnesses=fixture()
        ready=p.prepare(cfg,fill,static,source,witnesses,SIMC_SHA)
        s=ready["summary"]
        self.assertEqual(s["T_official"],1603)
        self.assertEqual(s["G_native"],1300)
        self.assertEqual(s["J"],138)
        self.assertEqual(s["F"],165)
        self.assertEqual(s["simc_binary_sha256"],SIMC_SHA)
        self.assertEqual(s["new_simc_calls"],0)
        self.assertTrue(s["profile_binding"]["two_trinkets_bound"])
        self.assertFalse(s["cross_class_native_acceptance_claimed"])
    def test_another_class_warrior_structure_without_simc_effect_proof(self):
        cfg,fill,static,source,witnesses=fixture("warrior","arms","attack")
        plan=p.prepare(cfg,fill,static,source,witnesses,SIMC_SHA)
        self.assertEqual(plan["summary"]["class"],"warrior")
        self.assertEqual(plan["summary"]["spec"],"arms")
        self.assertEqual(plan["summary"]["role"],"attack")
        self.assertEqual(plan["summary"]["G_native"],1300)
        self.assertFalse(plan["summary"]["cross_class_native_acceptance_claimed"])
        self.assertEqual(plan["summary"]["measured_net_gear_to_rating_offset"]["haste_rating"],165)
        # The +165 here comes only from synthetic test data; NEVER a warrior
        # calibration claim from actual Native SimC.
    def test_changing_profile_class_without_witness_recalibration_fails(self):
        cfg,fill,static,source,witnesses=fixture("warrior","arms","attack")
        wrong=source.replace("role=attack","role=spell",1)
        with self.assertRaisesRegex(p.numeric.InjectionError,
                                    "NATIVE_NUMERIC_WITNESSES_FOR_OTHER_PROFILE"):
            p.prepare(cfg,fill,static,wrong,witnesses,SIMC_SHA)
    def test_item_identity_mismatch_not_a_proc_gate(self):
        cfg,fill,static,source,witnesses=fixture()
        altered=source.replace("id=250224","id=250244")
        changed=[]
        for w in witnesses:
            text=w["input"].replace("id=250224","id=250244")
            changed.append({"input":text,"native":fake_doc(text)})
        with self.assertRaisesRegex(p.port.PortBlocked,
                                    "PROFILE_GEAR_ID_LEVEL_OPTIONS_DRIFT"):
            p.prepare(cfg,fill,static,altered,changed,SIMC_SHA)
    def test_missing_nontrinket_exact_static_not_guessed_zero(self):
        cfg,fill,static,source,witnesses=fixture()
        key=next(iter(static["variants"]))
        del static["variants"][key]
        with self.assertRaisesRegex(p.PreflightBlocked,
                                    "MISSING_EXACT_NONTRINKET_STATIC_VARIANTS"):
            p.prepare(cfg,fill,static,source,witnesses,SIMC_SHA)
    def test_manual_T_and_ilevel_independent_of_334_reference(self):
        cfg,fill,static,source,witnesses=fixture()
        cfg["target"].update(mode="manual_total",ilevel=320,manual_total=1603,
                             manual_total_scope=contract.MANUAL_TOTAL_SCOPE)
        # The test exercises user override, not a 320-ilvl physical-gem proof.
        p0=p.prepare(cfg,fill,static,source,witnesses,SIMC_SHA)
        self.assertEqual(p0["summary"]["target_ilevel"],320)
        self.assertEqual(p0["summary"]["T_official"],1603)
    def test_missing_witnesses_not_silently_filled(self):
        cfg,fill,static,source,witnesses=fixture()
        with self.assertRaisesRegex(p.PreflightBlocked,
                                    "TWO_PROFILE_SCOPED_NATIVE_WITNESSES_REQUIRED"):
            p.prepare(cfg,fill,static,source,witnesses[:1],SIMC_SHA)
    def test_measured_calibration_mismatch_strict(self):
        cfg,fill,static,source,witnesses=fixture()
        wrong=copy.deepcopy(witnesses)
        wrong[1]["native"]["sim"]["players"][0]["collected_data"]["buffed_stats"]["stats"]["haste_rating"]+=4
        with self.assertRaisesRegex(p.numeric.InjectionError,"NONCONSTANT_NUMERIC"):
            p.prepare(cfg,fill,static,source,wrong,SIMC_SHA)
    def test_native_json_raw_bytes_parity(self):
        cfg,fill,static,source,witnesses=fixture()
        wrong=copy.deepcopy(witnesses)
        wrong[0]["raw_native_json"]=b'{"report_version":"2.0.0"}'
        with self.assertRaisesRegex(p.PreflightBlocked,"WITNESS_NATIVE_JSON_BYTES_MISMATCH"):
            p.prepare(cfg,fill,static,source,wrong,SIMC_SHA)
    def test_native_result_is_not_a_gear_recommendation(self):
        cfg,fill,static,source,witnesses=fixture()
        p0=p.prepare(cfg,fill,static,source,witnesses,SIMC_SHA)
        with tempfile.TemporaryDirectory() as path:
            next0=p.propose_next(p0,60,pathlib.Path(path)/"result.json",step=100)
            self.assertEqual(next0["status"],"PROPOSED_SCOUT_NOT_RUN")
            self.assertEqual(sum(next0["case"]["target"].values()),1603)
            self.assertNotIn(next0["case"]["target"],[
                row["target"] for row in p0["prior_observations"]])
            self.assertTrue(next0["decision"]["derived_new_module_not_original_v015"])
            self.assertEqual(next0["decision"]["method"],
                             "V015_LOCAL_MIRROR_FOR_SCOUT_ORDER_ONLY")
    def test_invalid_binary_hash(self):
        cfg,fill,static,source,witnesses=fixture()
        with self.assertRaisesRegex(p.PreflightBlocked,"BINARY_SHA256_REQUIRED"):
            p.prepare(cfg,fill,static,source,witnesses,"a")
    def test_user_profile_input_hash_protection(self):
        cfg,fill,static,source,witnesses=fixture()
        cfg["source"]={"kind":"user_supplied","profile_sha256":"b"*64}
        with self.assertRaisesRegex(p.PreflightBlocked,"USER_PROFILE_EXACT_INPUT_HASH_CHANGED"):
            p.prepare(cfg,fill,static,source,witnesses,SIMC_SHA)
        cfg["source"]["profile_sha256"]=hashlib.sha256(source.encode()).hexdigest()
        result=p.prepare(cfg,fill,static,source,witnesses,SIMC_SHA)
        self.assertEqual(result["summary"]["class"],"mage")

if __name__=="__main__":
    unittest.main()
