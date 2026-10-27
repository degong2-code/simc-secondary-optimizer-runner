"""v124 P1: universal per-stat candidate floor B+O>=F, beyond locked L.

All Native-shaped observations in this file are synthetic OFFLINE fixtures.
They do NOT attest SimC acceptance, DPS, or any item effect.
"""
from __future__ import annotations
import copy,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v065_v015_scheduler_adapter as policy
import v093_inclusive_adaptive_scheduler_bridge as adaptive
import v095_material_precision_policy as extended
import v082_fury_plate_dual_twohand_native as warrior
import v098_target_user_scenario_bootstrap as bootstrap
import v096_unified_product_entry as entry
from test_v098_target_user_scenario_bootstrap import case
from test_v093_inclusive_adaptive_scheduler_bridge import V093InclusiveAdaptive

STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")

class FixedComponentsFeasibility(unittest.TestCase):
    def setup_context(self,folder):
        return V093InclusiveAdaptive().make(folder)

    def test_actual_rogue_240967_preflight_applies_same_crit_floor(self):
        # The user's blocked Rogue path has Fcrit165 and two oils Ocrit32.
        # Exercise its real v098->v096->v093 plan using a non-executable fake
        # binary; no SimC JSON2 or new Native evidence is manufactured.
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            fake=root/"simc.exe"
            fake.write_bytes(b"NO_NATIVE_EXECUTION")
            user=case("subtlety")
            user["consumable_choices"]={
                "flask":"source_default","food":"source_default",
                "potion":"source_default","augmentation":"source_default",
                "diamond_id":240967,"omnium_talents":"source_default"}
            folder=root/"generated"
            bootstrap.build(user,folder,fake,"7bc1071")
            sealed=entry.source(folder/"manifest.json")
            ctx=sealed["context"]
            F=sealed["flask"]
            O=ctx["identity"]["oil_vector"]
            self.assertEqual((F["crit_rating"],O["crit_rating"]),(165,32))
            adjusted=adaptive.feasible_budget(ctx,F)
            _,lo,hi=policy.bounds(ctx["bundle"]["prepared"]["scenario"],
                                  adjusted)
            self.assertGreaterEqual(lo[0],133)
            for seed in sealed["seeds"]:
                self.assertGreaterEqual(seed["crit_rating"],lo[0])
            # 132 crit is feasible under old L-only bounds, but cannot be
            # a physically valid candidate after the fixed flask subtraction.
            impossible=dict(zip(STATS,(132,1000,1009,1009)))
            self.assertEqual(sum(impossible.values()),3150)
            with self.assertRaisesRegex(adaptive.AdaptiveBridgeBlocked,
                                        "BASE_TARGET_BELOW_FIXED_COMPONENT_FLOOR"):
                adaptive.request(ctx,impossible,F,root/"no.json","scout")
            self.assertFalse((root/"no.json").exists())
            self.assertFalse((folder/"simc_results").exists())

    def test_fixed_F_and_O_raise_common_floor_without_changing_budget_or_identity(self):
        with tempfile.TemporaryDirectory() as td:
            ctx=self.setup_context(td)
            normalized=ctx["bundle"]["prepared"]["scenario"]
            budget=ctx["bundle"]["prepared"]["static_budget"]
            original=copy.deepcopy(budget)
            identity=copy.deepcopy(ctx["identity"])
            f=warrior.DECLARED_F
            self.assertEqual(f["haste_rating"],165)
            self.assertEqual(identity["oil_vector"]["haste_rating"],32)
            feasible=adaptive.feasible_budget(ctx,f)
            total,lo,hi=policy.bounds(normalized,feasible)
            self.assertEqual(total,3350)
            self.assertEqual(lo[STATS.index("haste_rating")],
                             max(original["effective_floor_if_possible"]["haste_rating"],133))
            self.assertEqual(budget,original)
            self.assertEqual(ctx["identity"],identity)
            # A per-stat locked L higher than F-O stays authoritative.
            locked=copy.deepcopy(budget)
            locked["effective_floor_if_possible"]["haste_rating"]=200
            again=policy.budget_with_fixed_components(
                normalized,locked,f,identity["oil_vector"])
            self.assertEqual(policy.bounds(normalized,again)[1][1],200)
            bad_F=dict(f);bad_F["haste_rating"]=164
            with self.assertRaisesRegex(policy.SchedulerBlocked,
                                        "FIXED_F_NOT_SCENARIO_BUDGET"):
                adaptive.feasible_budget(ctx,bad_F)
            bad_O=dict(identity["oil_vector"]);bad_O["haste_rating"]=31
            with self.assertRaisesRegex(policy.SchedulerBlocked,
                                        "FIXED_O_NOT_SCENARIO_BUDGET"):
                policy.budget_with_fixed_components(normalized,budget,f,bad_O)

    def test_exact_feasible_boundary_and_lower_target_refusal_before_any_native(self):
        with tempfile.TemporaryDirectory() as td:
            ctx=self.setup_context(td)
            f=warrior.DECLARED_F
            valid=dict(zip(STATS,(970,133,1124,1123)))
            invalid=dict(zip(STATS,(971,132,1124,1123)))
            self.assertEqual(sum(valid.values()),3350)
            with self.assertRaisesRegex(adaptive.AdaptiveBridgeBlocked,
                                        "BASE_TARGET_BELOW_FIXED_COMPONENT_FLOOR"):
                adaptive.request(ctx,invalid,f,pathlib.Path(td)/"bad.json","seed")
            req=adaptive.request(ctx,valid,f,pathlib.Path(td)/"good.json","seed")
            self.assertEqual(req["raw_gear_override"]["haste_rating"],0)
            self.assertEqual(req["target"]["haste_rating"],165)
            self.assertEqual(req["v092_base_B"],3350)
            self.assertEqual(req["v092_final_T"],3414)
            self.assertFalse((pathlib.Path(td)/"good.json").exists())

    def test_material_scout_excludes_observed_leader_unfeasible_transfer(self):
        with tempfile.TemporaryDirectory() as td:
            ctx=self.setup_context(td)
            prepared=ctx["bundle"]["prepared"]
            anchor=dict(zip(STATS,(100,400,1400,1450)))
            self.assertEqual(sum(anchor.values()),3350)
            synthetic={"status":"PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT",
                       "rating_semantics":"STATIC_CHMV_C_V1",
                       "target":anchor,"static_rating_verified":anchor,
                       "dps_mean":200000.0,"dps_sem":500.0}
            # Prior policy ignored F and considered this 10% CHMV move valid.
            old=extended.material_neighbor(prepared["scenario"],
                 prepared["static_budget"],[synthetic],fraction=0.10)
            self.assertLess(old["candidate_B"]["haste_rating"],133)
            # v094 now supplies the exact SAME F/O/L view for this stage.
            adjusted=adaptive.feasible_budget(ctx,warrior.DECLARED_F)
            proposal=extended.material_neighbor(prepared["scenario"],
                 adjusted,[synthetic],fraction=0.10)
            B,lo,hi=policy.bounds(prepared["scenario"],adjusted)
            self.assertTrue(policy.eligible(policy.key(proposal["candidate_B"]),
                                            B,lo,hi))
            self.assertGreaterEqual(proposal["candidate_B"]["haste_rating"],133)
            req=adaptive.request(ctx,proposal["candidate_B"],
                 warrior.DECLARED_F,pathlib.Path(td)/"material.json","scout")
            self.assertTrue(all(req["raw_gear_override"][k]>=0 for k in STATS))
            self.assertFalse((pathlib.Path(td)/"material.json").exists())

if __name__=="__main__":
    unittest.main()
