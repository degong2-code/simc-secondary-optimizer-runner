"""v197 fixed enchant rating is an L-like floor *inside* official G budget."""
import copy,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v197_verified_effect_budget as e

S=e.STATS
def vec(c=0,h=0,m=0,v=0):
    return dict(zip(S,(c,h,m,v)))
def evidence(slot="finger1",enchant_id=8025,delta=None):
    return {
      "slot":slot,"enchant_id":enchant_id,
      "static_secondary":delta or vec(h=29),
      "proof_kind":"MATCHED_SIMC_NATIVE_JSON2_STATIC_SECONDARY_DELTA_VERIFIED",
      "profile_before_sha256":"a"*64,"profile_after_sha256":"b"*64,
      "native_before_sha256":"c"*64,"native_after_sha256":"d"*64,
      "verified_receipt_sha256":"e"*64}

class NativeEnchantmentLockedBudget(unittest.TestCase):
    def test_fixed_enchant_is_inside_gear_budget_with_no_T_growth(self):
        # T=3182, J=138, F=165, oil=32, fixed special L=40, rings 29+29.
        out=e.plan_locked_fixed_enchant_T(
            3182,vec(h=138),vec(c=165),vec(h=32),vec(m=40),
            [evidence(),evidence("finger2",8025)])
        self.assertEqual(out["official_total_T"],3182)
        self.assertEqual(out["gear_G_including_enchant_E"],2847)
        self.assertEqual(out["fixed_enchant_E"],vec(h=58))
        self.assertEqual(out["remaining_freely_distributable_gear_G"],2749)
        self.assertEqual(out["minimum_final_per_stat"],
                         vec(c=165,h=228,m=40))
        self.assertFalse(out["new_enchant_added_to_total_T"])
        self.assertFalse(out["can_emit_native_candidate_without_profile_receipt"])
        self.assertTrue(e.check_candidate(out,vec(c=286,h=1396,m=750,v=750)))
        with self.assertRaisesRegex(e.RatingEvidenceBlocked,"TOTAL_T_CHANGED"):
            e.check_candidate(out,vec(c=286,h=1454,m=750,v=750))

    def test_unverified_enchant_never_changes_user_budget(self):
        untrusted=evidence()
        untrusted["proof_kind"]="WOWHEAD_TOOLTIP_ESTIMATED"
        with self.assertRaisesRegex(e.RatingEvidenceBlocked,
                                    "ENCHANT_STATIC_NOT_NATIVE_VERIFIED"):
            e.plan_locked_fixed_enchant_T(
                3182,vec(h=138),vec(c=165),vec(h=32),vec(),[untrusted])
        untrusted=evidence()
        untrusted["native_after_sha256"]=""
        with self.assertRaisesRegex(e.RatingEvidenceBlocked,
                                    "NATIVE_ENCHANT_PROVENANCE_SHA_MISSING"):
            e.plan_locked_fixed_enchant_T(
                3182,vec(h=138),vec(c=165),vec(h=32),vec(),[untrusted])

    def test_fixed_budget_excess_and_per_stat_floor_blocked(self):
        with self.assertRaisesRegex(e.RatingEvidenceBlocked,
                                    "FIXED_L_AND_ENCHANT_E_EXCEED"):
            e.plan_locked_fixed_enchant_T(
                3182,vec(h=138),vec(c=165),vec(h=32),vec(h=2810),
                [evidence()])
        with self.assertRaisesRegex(e.RatingEvidenceBlocked,"UNDER_NATIVELY"):
            p=e.plan_locked_fixed_enchant_T(
                3182,vec(h=138),vec(c=165),vec(h=32),vec(),
                [evidence()])
            e.check_candidate(p,vec(c=3000,h=10,m=100,v=72))

    def test_duplicate_equipped_enchant_slot_and_unbalanced_vector_fail(self):
        with self.assertRaisesRegex(e.RatingEvidenceBlocked,"ENCHANT_SLOT_DUPLICATE"):
            e.plan_locked_fixed_enchant_T(
                3182,vec(),vec(),vec(),vec(),
                [evidence(),evidence()])
        for invalid in ({"crit_rating":0},vec(h=-1),{"crit_rating":True,
              "haste_rating":0,"mastery_rating":0,"versatility_rating":0}):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(e.RatingEvidenceBlocked,
                                            "INVALID_NONNEGATIVE_VECTOR"):
                    e.plan_locked_fixed_enchant_T(
                        3182,invalid,vec(),vec(),vec(),[])

if __name__=="__main__":unittest.main()
