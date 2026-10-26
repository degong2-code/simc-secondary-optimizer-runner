"""v091 per-weapon oil policy and native-input identity (offline, no SimC)."""
import copy,hashlib,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v046_static_item_cache as cache
import v063_numeric_injection as numeric
import v091_weapon_oil_external_adapter as tested
import v082_fury_plate_dual_twohand_native as warrior
import v084_frost_cloth_1h_frill_native as mage

FROST=ROOT/"integration_probes/fixtures/v084_upstream_mid2_mage_frost_reference.simc"
FURY=ROOT/"integration_probes/fixtures/v082_upstream_mid2_warrior_fury_reference.simc"
BIN="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"
REV="7bc10711b5"
FROST_TARGET={"crit_rating":900,"haste_rating":800,"mastery_rating":800,
              "versatility_rating":650}
FURY_TARGET={"crit_rating":838,"haste_rating":838,"mastery_rating":837,
             "versatility_rating":837}

def frost(folder):
    profile,cfg,fillers,_=mage.source_profile(FROST.read_text("utf8"),folder)
    return profile,cfg,fillers
def fury(folder):
    profile,cfg,fillers,_=warrior.source_profile(FURY.read_text("utf8"),folder)
    return profile,cfg,fillers

class V091OilInputs(unittest.TestCase):
    def test_frost_none_explicit_disabled_and_no_O(self):
        with tempfile.TemporaryDirectory() as d:
            profile,cfg,fillers=frost(d)
            z=tested.prepare(profile,cfg,fillers,cache.empty_cache(),
                             "one_hand_frill",[])
            oil=z["oil"]
            self.assertEqual(z["prepared"]["T"],3150)
            self.assertEqual(oil["expected_simc_temporary_enchant"],"disabled")
            self.assertIn("\ntemporary_enchant=disabled\n",oil["profile"])
            self.assertEqual(sum(oil["declared_O"].values()),0)
            self.assertEqual(z["prepared"]["missing_ordinary_G_observed_not_zero"],14)
            req=tested.propose(z,FROST_TARGET,mage.F_DECLARED,BIN,REV,35,
                                pathlib.Path(d)/"none"/"result.json")
            self.assertEqual(req["raw_gear_override"]["crit_rating"],735)
            self.assertEqual(req["v091_expected_temporary_enchant"],"disabled")
            self.assertEqual(req["official_total"],3150)
            self.assertTrue(req["v091_stat_effect_simc_owned"])

    def test_frost_one_main_oil_only_and_no_double_rating(self):
        with tempfile.TemporaryDirectory() as d:
            p,c,f=frost(d)
            x=tested.prepare(p,c,f,cache.empty_cache(),"one_hand_frill",["main_hand"])
            z=tested.propose(x,FROST_TARGET,mage.F_DECLARED,BIN,REV,35,
                              pathlib.Path(d)/"one"/"result.json")
            self.assertEqual(z["raw_gear_override"]["crit_rating"],751)
            self.assertEqual(z["v091_declaration_O"]["crit_rating"],16)
            self.assertEqual(z["v091_declaration_O"]["haste_rating"],16)
            self.assertEqual(z["official_total"],3182)
            self.assertEqual(z["v091_expected_temporary_enchant"],
                             "main_hand:thalassian_phoenix_oil_2")

    def test_fury_none_one_offhand_and_two_all_keep_same_static_target(self):
        with tempfile.TemporaryDirectory() as d:
            p,c,f=fury(d)
            ref=[]
            for hands in ([],["main_hand"],["off_hand"],
                          ["main_hand","off_hand"]):
                x=tested.prepare(p,c,f,cache.empty_cache(),
                                 "dual_two_hand",hands)
                req=tested.propose(x,FURY_TARGET,warrior.DECLARED_F,
                                   BIN,REV,35,pathlib.Path(d)/str(len(hands))/
                                   ("x_"+("_".join(hands) or "none")+".json"))
                ref.append(req)
                self.assertEqual(req["official_total"],3350+32*len(hands))
                self.assertEqual(sum(req["raw_gear_override"].values()),3185+32*len(hands))
                self.assertEqual(req["raw_gear_override"]["haste_rating"],673+16*len(hands))
                self.assertEqual(req["v091_declaration_O"]["crit_rating"],
                                 16*len(hands))
                self.assertEqual(req["v091_declaration_O"]["haste_rating"],
                                 16*len(hands))
                self.assertEqual(req["profile_binding"]["slots_bound"],16)
                self.assertEqual(sum(req["target"].values()),3350+32*len(hands))
                self.assertEqual(req["v092_base_B"],3350)
                self.assertEqual(req["v092_formula"],"T=G+J+F+O")
            self.assertEqual(len({r["case_key"] for r in ref}),4)
            self.assertEqual(ref[0]["v091_expected_temporary_enchant"],"disabled")
            self.assertEqual(ref[2]["v091_expected_temporary_enchant"],
                 "off_hand:thalassian_phoenix_oil_2")
            self.assertEqual(ref[-1]["v091_expected_temporary_enchant"],
                 "main_hand:thalassian_phoenix_oil_2/off_hand:thalassian_phoenix_oil_2")

    def test_nonweapon_frill_rejects_offhand_even_if_item_slot_present(self):
        with tempfile.TemporaryDirectory() as d:
            p,c,_=frost(d)
            for hands in (["off_hand"],["main_hand","off_hand"]):
                with self.subTest(hands=hands):
                    with self.assertRaisesRegex(tested.OilInputBlocked,
                            "NONWEAPON_OFFHAND_CANNOT_RECEIVE_OIL"):
                        tested.configure(p,c,"one_hand_frill",hands)

    def test_duplicated_hands_duplicate_profile_setting_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p,c,_=fury(d)
            with self.assertRaisesRegex(tested.OilInputBlocked,
                         "OIL_HAND_SET_INVALID"):
                tested.configure(p,c,"dual_two_hand",["main_hand","main_hand"])
            mutated=p+"temporary_enchant=disabled\n"+"temporary_enchant=disabled\n"
            intentional=copy.deepcopy(c)
            intentional["source"]["profile_sha256"]=hashlib.sha256(
                 mutated.encode("utf8")).hexdigest()
            with self.assertRaisesRegex(tested.OilInputBlocked,
                         "MULTIPLE_TEMPORARY_ENCHANT_ASSIGNMENTS"):
                tested.configure(mutated,intentional,
                                 "dual_two_hand",["main_hand"])

    def test_profile_source_sha_protected_and_no_talent_apl_changes(self):
        with tempfile.TemporaryDirectory() as d:
            p,c,_=fury(d)
            base=[l for l in p.splitlines() if l.startswith("actions")]
            x=tested.configure(p,c,"dual_two_hand",["main_hand","off_hand"])
            self.assertEqual(base,[l for l in x["profile"].splitlines()
                                   if l.startswith("actions")])
            self.assertEqual(x["scenario"]["character"],c["character"])
            self.assertEqual(x["scenario"]["equipment"],c["equipment"])
            self.assertEqual(x["scenario"]["target"],c["target"])
            self.assertEqual(x["scenario"]["source"]["profile_sha256"],
                             hashlib.sha256(x["profile"].encode()).hexdigest())
            with self.assertRaisesRegex(tested.OilInputBlocked,
                                "USER_SOURCE_PROFILE_SHA_MISMATCH"):
                tested.configure(p.replace("race=dwarf","race=orc"),c,
                                 "dual_two_hand",["main_hand"])

    def test_default_missing_is_not_equivalent_to_disabled(self):
        with tempfile.TemporaryDirectory() as d:
            p,c,_=fury(d)
            self.assertNotIn("temporary_enchant=",p)
            q=tested.configure(p,c,"dual_two_hand",[])
            self.assertIn("temporary_enchant=disabled",q["profile"])
            self.assertNotEqual(q["profile_sha256"],q["original_sha256"])
            self.assertEqual(q["declared_O"],dict.fromkeys(tested.PER_WEAPON,0))

    def test_native_reported_enchant_selection_guard(self):
        req={"v091_expected_temporary_enchant":"disabled"}
        fake={"report_version":"2.0.0",
              "sim":{"players":[{"temporary_enchant":
                     "main_hand:thalassian_phoenix_oil_2"}]}}
        with self.assertRaisesRegex(tested.OilInputBlocked,
                   "NATIVE_OIL_SETTING_DIFFERENT_FROM_USER_CHOICE"):
            tested.ingest_native(req,fake)

if __name__=="__main__":unittest.main()
