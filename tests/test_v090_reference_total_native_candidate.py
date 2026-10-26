"""v090 source-backed Frost Native input; reference T without ordinary G cache."""
import copy,hashlib,json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v046_static_item_cache as cache
import v061_scenario_contract as scenario
import v062_static_budget_bridge as bridge
import v063_numeric_injection as numeric
import v064_adaptive_evaluator_port as port
import v089_ilvl_chmv_budget_selector as choices
import v090_reference_total_native_candidate as tested
import v084_frost_cloth_1h_frill_native as mage
from test_v062_static_budget_bridge import record

UPSTREAM=(ROOT/"integration_probes/fixtures/v084_upstream_mid2_mage_frost_reference.simc")
BIN="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"
REV="7bc10711b5"
FLASK={"crit_rating":165,"haste_rating":0,"mastery_rating":0,
       "versatility_rating":0}
A={"crit_rating":900,"haste_rating":800,"mastery_rating":800,
   "versatility_rating":650}
B={"crit_rating":800,"haste_rating":900,"mastery_rating":800,
   "versatility_rating":650}

def fixture(folder):
    original=UPSTREAM.read_text("utf8")
    profile,cfg,fillers,_=mage.source_profile(original,folder)
    choice=choices.resolve(cfg,mode=choices.REFERENCE_MODE,
                           weapon_layout="one_hand_frill")
    return profile,cfg,fillers,choice

class V090ReferenceToStaticNative(unittest.TestCase):
    def test_no_ordinary_stat_cache_required_all_16_exact_items_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            profile,cfg,fillers,selection=fixture(directory)
            plan=tested.prepare(selection,fillers,cache.empty_cache(),profile)
            self.assertEqual(plan["T"],3150)
            self.assertIsNone(plan["static_budget"]["G_if_complete"])
            self.assertEqual(plan["missing_ordinary_G_observed_not_zero"],14)
            self.assertEqual(plan["items_bound"],16)
            self.assertEqual(sum(plan["floor_L"].values()),0)
            self.assertEqual(len(plan["static_budget"]["native_gear_stats"]),0)
            self.assertEqual(len(plan["static_budget"]["selected_trinkets"]),2)
            self.assertEqual(plan["static_budget"]["selected_trinkets"][0]
                             ["native_static_status"],"UNREPORTED_UNKNOWN_NOT_ZERO")
            q=tested.propose(plan,profile,A,FLASK,BIN,REV,35,
                             pathlib.Path(directory)/"a"/"result.json")
            p=numeric.input_parts(q["input"])
            self.assertEqual(q["target"],A)
            self.assertEqual(q["official_total"],3150)
            self.assertEqual(q["raw_gear_override"]["crit_rating"],735)
            self.assertEqual(q["raw_gear_override"]["haste_rating"],800)
            self.assertEqual(p["gear_override"],q["raw_gear_override"])
            self.assertEqual(q["profile_binding"]["slots_bound"],16)
            self.assertFalse(q["G_was_required_for_candidate"])
            self.assertFalse(q["global_optimum_proven"])
            self.assertNotEqual(q["input_sha256"],hashlib.sha256(profile.encode()).hexdigest())
            self.assertEqual(q["profile_stable_sha256"],
                             numeric.input_parts(profile)["stable_sha256"])

    def test_candidates_have_distinct_cache_identity_and_same_exact_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            profile,cfg,fillers,selection=fixture(directory)
            plan=tested.prepare(selection,fillers,cache.empty_cache(),profile)
            q=tested.propose(plan,profile,A,FLASK,BIN,REV,35,
                             pathlib.Path(directory)/"a"/"result.json")
            r=tested.propose(plan,profile,B,FLASK,BIN,REV,35,
                             pathlib.Path(directory)/"b"/"result.json")
            self.assertNotEqual(q["case_key"],r["case_key"])
            self.assertEqual(q["profile_stable_sha256"],
                             r["profile_stable_sha256"])
            with self.assertRaisesRegex(tested.ReferenceNativeBlocked,
                    "REFERENCE_CANDIDATE_T_OR_LOCKED_L_CONSTRAINT"):
                tested.propose(plan,profile,dict(A,crit_rating=901),
                               FLASK,BIN,REV,35,
                               pathlib.Path(directory)/"bad"/"result.json")
            self.assertEqual(q["external_oil_only"],
                             dict.fromkeys(scenario.STATS,0))

    def test_profile_gear_tamper_blocks_even_with_ordinary_G_unobserved(self):
        with tempfile.TemporaryDirectory() as directory:
            profile,cfg,fillers,selection=fixture(directory)
            changed=profile.replace(
                "head=selected_271874,id=271874",
                "head=selected_271874,id=271999",1)
            with self.assertRaisesRegex(port.PortBlocked,
                    "PROFILE_GEAR_ID_LEVEL_OPTIONS_DRIFT"):
                tested.prepare(selection,fillers,cache.empty_cache(),changed)

    def test_source_sha_protects_user_supplied_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            profile,cfg,fillers,selection=fixture(directory)
            changed=profile.replace("potion=potion_of_recklessness_2",
                                    "potion=potion_of_recklessness_1",1)
            with self.assertRaisesRegex(tested.ReferenceNativeBlocked,
                    "USER_SOURCE_PROFILE_SHA_DRIFT"):
                tested.prepare(selection,fillers,cache.empty_cache(),changed)

    def test_selected_special_L_requires_actual_Native_static(self):
        with tempfile.TemporaryDirectory() as directory:
            profile,cfg,fillers,selection=fixture(directory)
            special=next(x for x in fillers if x["slot"]=="back")
            cfg2=copy.deepcopy(cfg)
            cfg2["equipment"]["special"]=[special]
            filler=[x for x in fillers if x["slot"]!="back"]
            select=choices.resolve(cfg2,mode=choices.REFERENCE_MODE,
                                   weapon_layout="one_hand_frill")
            with self.assertRaisesRegex(tested.ReferenceNativeBlocked,
                    "SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT"):
                tested.prepare(select,filler,cache.empty_cache(),profile)
            native=cache.empty_cache()
            observed={"crit_rating":0,"haste_rating":0,
                      "mastery_rating":170,"versatility_rating":0}
            record(native,special,observed)
            plan=tested.prepare(select,filler,native,profile)
            self.assertEqual(plan["floor_L"],observed)
            self.assertEqual(plan["T"],3150)
            self.assertEqual(plan["static_budget"]["native_gear_stats"]["back"]
                             ["secondary"],observed)
            with self.assertRaisesRegex(tested.ReferenceNativeBlocked,
                    "REFERENCE_CANDIDATE_T_OR_LOCKED_L_CONSTRAINT"):
                tested.propose(plan,profile,{"crit_rating":1500,"haste_rating":1400,
                    "mastery_rating":100,"versatility_rating":150},
                    FLASK,BIN,REV,35,pathlib.Path(directory)/"bad.json")
            q=tested.propose(plan,profile,A,FLASK,BIN,REV,35,
                             pathlib.Path(directory)/"good.json")
            self.assertTrue(q["locked_L_not_double_added"])
            self.assertEqual(sum(q["target"].values()),3150)

    def test_mismatch_reference_and_exact_path_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            profile,cfg,fillers,selection=fixture(directory)
            wrong=copy.deepcopy(selection);wrong["reference_sha256"]="f"*64
            with self.assertRaisesRegex(tested.ReferenceNativeBlocked,
                    "REFERENCE_PROVENANCE_TAMPERED"):
                tested.prepare(wrong,fillers,cache.empty_cache(),profile)
            exact=choices.resolve(cfg,mode=choices.NATIVE_MODE,
                                  weapon_layout="one_hand_frill")
            with self.assertRaisesRegex(tested.ReferenceNativeBlocked,
                    "REFERENCE_SELECTION_REQUIRED"):
                tested.prepare(exact,fillers,cache.empty_cache(),profile)

if __name__=="__main__":unittest.main()
