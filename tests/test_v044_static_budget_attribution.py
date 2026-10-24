"""v044: mock-negative attribution gates, no Native calls and no policy changes."""
import copy
import hashlib
import json
import pathlib
import sys
import unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v044_static_budget_attribution as v

SLOT_DATA = {
  "head":(0,0,201,0),
  "neck":(0,127,278,0),
  "shoulders":(102,48,0,0),
  "chest":(130,71,0,0),
  "waist":(0,102,49,0),
  "legs":(62,0,0,139),
  "feet":(104,0,46,0),
  "wrists":(0,57,57,0),
  "hands":(45,106,0,0),
  "finger1":(232,0,174,0),
  "finger2":(0,266,0,139),
  "trinket1":(0,0,0,0),
  "trinket2":(0,0,0,0),
  "back":(0,57,57,0),
  "main_hand":(0,63,138,0),
}
FLASK="flask_of_the_blood_knights_2"
OIL="main_hand:thalassian_phoenix_oil_2"
INPUT="\n".join([
  "gear_crit_rating=600","gear_haste_rating=975",
  "gear_mastery_rating=1115","gear_versatility_rating=329",
  "flask="+FLASK,"temporary_enchant="+OIL])+"\n"
GEM={"head":"240967","neck":"240908","wrists":"240892","waist":"240918",
     "finger1":"240900/240908","finger2":"240892"}

def fixture():
    gear={}
    for i,slot in enumerate(v.SLOTS):
        base=(f"tier,id=271564,bonus_id=13846,ilevel=334,gem_id=240967,"
              f"redirected_base_stats=271874" if slot=="head" else
              f"test_{slot},id={210000+i},ilevel=334")
        if slot!="head" and slot in GEM: base+=",gem_id="+GEM[slot]
        gear[slot]={"encoded_item":base,"ilevel":334,
                    **dict(zip(v.STATS,SLOT_DATA[slot]))}
    return {"report_version":"2.0.0","git_revision":"7bc10711b5",
       "sim":{"players":[{"gear":gear,"flask":FLASK,"temporary_enchant":OIL,
       "collected_data":{"buffed_stats":{"stats":dict(zip(v.STATS,(600.0,1140.0,1115.0,329.0)))}}}]}}

def check(document,src=INPUT):
    x=src.encode();y=json.dumps(document,sort_keys=True).encode()
    with patch.object(v,"INPUT_SHA",hashlib.sha256(x).hexdigest()),patch.object(
          v,"NATIVE_SHA",hashlib.sha256(y).hexdigest()):
        return v.analyze(x,y)

class V044Attribution(unittest.TestCase):
    def test_positive_only_observations(self):
        proof=check(fixture())
        self.assertEqual(proof["static_nontrinket_gear_sum_all_stats"],2850)
        self.assertEqual(proof["final_minus_gear_override"], dict(zip(v.STATS,(0,165,0,0))))
        self.assertEqual(len(proof["gem_ids"]["other_six"]),6)
        self.assertEqual(proof["hypothetical_v1_0_arithmetic_if_observed_slots_equal_G"]["conditional_T"],3153)
        self.assertFalse(proof["known_mismatches_not_reconciled"]["simc_flask_plus165_causality_proven"])
        self.assertFalse(proof["actual_334_G_verified_for_product"])
        self.assertFalse(proof["actual_334_T_verified_for_product"])
        self.assertFalse(proof["product_code_integrated"])
        self.assertFalse(proof["official_policy_promoted"])
        self.assertEqual(proof["native_simc_calls"],0)
        self.assertEqual(proof["product_admission"],"BLOCKED_PROVENANCE_AND_ATTRIBUTION")

    def test_missing_gem_blocked(self):
        x=fixture()
        x["sim"]["players"][0]["gear"]["finger2"]["encoded_item"]=x["sim"]["players"][0]["gear"]["finger2"]["encoded_item"].replace(",gem_id=240892","")
        with self.assertRaisesRegex(v.Blocked,"SIX_OTHER_GEMS_NOT_RETAINED"):check(x)

    def test_changed_head_fixed_stat_blocked(self):
        x=fixture()
        x["sim"]["players"][0]["gear"]["head"]["mastery_rating"]=402
        with self.assertRaisesRegex(v.Blocked,"HEAD_FIXED_STAT_CHANGED"):check(x)

    def test_changed_head_identity_blocked(self):
        x=fixture()
        x["sim"]["players"][0]["gear"]["head"]["encoded_item"]=x["sim"]["players"][0]["gear"]["head"]["encoded_item"].replace("bonus_id=13846","bonus_id=13848")
        with self.assertRaisesRegex(v.Blocked,"PINNED_HEAD_IDENTITY_MISMATCH"):check(x)

    def test_changed_ilevel_blocked(self):
        x=fixture()
        x["sim"]["players"][0]["gear"]["neck"]["ilevel"]=335
        with self.assertRaisesRegex(v.Blocked,"UNEXPECTED_ITEM_LEVEL"):check(x)

    def test_extra_gear_blocked(self):
        x=fixture()
        x["sim"]["players"][0]["gear"]["unapproved_slot"]={"ilevel":334}
        with self.assertRaisesRegex(v.Blocked,"GEAR_SLOT_SET_CHANGED"):check(x)

    def test_duplicate_input_stat_rejected(self):
        with self.assertRaisesRegex(v.Blocked,"DUPLICATE_INPUT_SETTING"):
            check(fixture(),INPUT+"gear_haste_rating=12\n")

    def test_consumable_drift_rejected(self):
        x=fixture()
        x["sim"]["players"][0]["flask"]="other_flask"
        with self.assertRaisesRegex(v.Blocked,"CONSUMABLE_IDENTITY_CHANGED"):check(x)

    def test_nonintegral_native_final_rejected(self):
        x=fixture()
        x["sim"]["players"][0]["collected_data"]["buffed_stats"]["stats"]["haste_rating"]=1140.5
        with self.assertRaisesRegex(v.Blocked,"INVALID_FINAL_RATING"):check(x)

    def test_extra_external_trinket_is_not_G(self):
        x=fixture()
        x["sim"]["players"][0]["gear"]["trinket1"]["crit_rating"]=200
        proof=check(x)
        self.assertEqual(proof["static_nontrinket_gear_sum_all_stats"],2850)
        self.assertEqual(proof["trinket_gear_secondary_external"]["crit_rating"],200)

    def test_corrupted_zip_is_refused(self):
        with self.assertRaisesRegex(v.Blocked,"ARCHIVE_SHA_MISMATCH"):v.inspect_archive(b"not the pinned archive")

    def test_reject_raw_bytes_without_pinning(self):
        with self.assertRaisesRegex(v.Blocked,"NATIVE_PAIR_SHA_MISMATCH"):
            v.analyze(INPUT.encode(),json.dumps(fixture()).encode())

if __name__=="__main__":unittest.main()
