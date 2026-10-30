"""v203 offline: E evidence cannot break user API, season list or B/T/O/L."""
import copy,json,pathlib,sys,tempfile,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v202_one_enchant_admission as evidence
import v196_current_season_user_catalog as catalog
import v106_user_session_controller as sessions
import v197_verified_effect_budget as finance
import v065_v015_scheduler_adapter as scheduler

def v(c=0,h=0,m=0,s=0):
    return dict(zip(finance.STATS,(c,h,m,s)))
def required(ok,code):
    if not ok:raise ValueError(code)

class EnchantCrossFeatureContract(unittest.TestCase):
    def test_existing_normal_user_fields_do_not_admit_developer_enchant(self):
        c=sessions.standard_controls(("mage","frost"))
        safe=sessions.user_scenario(c)
        self.assertNotIn("verified_enchant",safe)
        self.assertNotIn("v202_verified_enchant_choice",safe)
        c["verified_enchant"]={"finger1":8025}
        with self.assertRaisesRegex(sessions.SessionBlocked,"USER_INPUT_FIELDS"):
            sessions.user_scenario(c)

    def test_separate_static_receipt_failure_does_not_blank_38_season_options(self):
        with patch.object(catalog.observed_enchant,"read",
                          side_effect=evidence.EnchantAdmissionBlocked("INVALID_EVIDENCE")):
            result=catalog.public_options()
        self.assertEqual(result["one_enchant_native_evidence_status"],
                         "OPTIONAL_EVIDENCE_UNAVAILABLE_ALL_ENCHANT_CHOICES_LOCKED")
        self.assertEqual(result["enchant_candidates"]["total"],38)
        self.assertEqual(result["enchant_candidates"]["selectable_count"],0)
        self.assertEqual(len(result["existing_allowed_input_choices"]["food"]),6)
        self.assertFalse(any("measured_E_in_one_simc_native_scope" in x
                             for x in result["enchant_candidates"]["items"]))

    def test_exact_native_evidence_sha_and_artifact_are_immutable(self):
        source,_=evidence.read()
        tampered=copy.deepcopy(source)
        tampered["v201_after_native_sha256"]="a"*64
        with tempfile.TemporaryDirectory() as td:
            dest=pathlib.Path(td)/"evidence.json"
            dest.write_text(json.dumps(tampered),encoding="utf8")
            with patch.object(evidence,"DEFAULT",dest):
                with self.assertRaisesRegex(evidence.EnchantAdmissionBlocked,
                                            "PINNED_NATIVE_EVIDENCE_BYTES_OR_ARTIFACT_DRIFT"):
                    evidence.read()

    def test_selected_special_or_crafted_same_ring_blocks_before_build(self):
        for field in ("special_items","embellishments"):
            u={field:[{"slot":"finger1","item_id":158366,"options":{}}]}
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError,"OVERLAPS_SELECTED_L"):
                    evidence.reject_selected_L_overlap(u,required)
        evidence.reject_selected_L_overlap({
            "special_items":[{"slot":"chest"}],
            "embellishments":[{"slot":"shoulders"}]},required)

    def test_fixed_E_is_nonfree_inside_existing_G_oil_is_once(self):
        ref,_=evidence.read()
        proof={"enchant_id":8025,"slot":"finger1",
            "static_secondary":dict(ref["static_enchant_E"]),
            "proof_kind":"MATCHED_SIMC_NATIVE_JSON2_STATIC_SECONDARY_DELTA_VERIFIED",
            "profile_before_sha256":"a"*64,"profile_after_sha256":"b"*64,
            "native_before_sha256":ref["v200_before_native_sha256"],
            "native_after_sha256":ref["v200_after_native_sha256"],
            "verified_receipt_sha256":"c"*64}
        fin=finance.plan_locked_fixed_enchant_T(
            3182,v(h=138),v(c=165),v(c=16,h=16),v(),[proof])
        self.assertEqual(fin["gear_G_including_enchant_E"],2847)
        self.assertEqual(fin["remaining_freely_distributable_gear_G"],2817)
        self.assertEqual(fin["minimum_final_per_stat"],v(c=181,h=184))
        self.assertEqual(fin["official_total_T"],3182)
        self.assertFalse(fin["new_enchant_added_to_total_T"])

if __name__=="__main__":unittest.main()
