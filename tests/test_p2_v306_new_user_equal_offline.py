"""New destruction-warlock equal-resource cohort: deterministic offline only."""
from __future__ import annotations

import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]

from integration_probes import p2_v306_new_user_equal_native_once as study
import v290_multiscale_adaptive_policy as v290
import v304_v303_durable_adapter as v304
import v306_seed_retained_coarse_escape_regions as v306


class P2NewWarlockEqualOffline(unittest.TestCase):
    def test_new_product_class_spec_and_manual_user_T(self):
        case,controls=study.fresh.selected_case(study.CASE_ID)
        self.assertEqual((case["character_class"],case["character_spec"],
                          case["final_T"],case["special_gem"]),
                         ("warlock","destruction",3400,None))
        self.assertEqual(controls["final_T"],3400)
        self.assertEqual(controls["consumable_choices"]["diamond_id"],0)
        self.assertEqual(study.GLOBAL,20)
        self.assertEqual(study.POST,20)
        self.assertEqual(study.CONFIRM,4)
        self.assertEqual(study.PLAN_CAP,44)
        self.assertEqual(study.MAX_TOTAL_NEW_DPS_NATIVE,68)

    def test_equal_iter_contract_and_selection_caveat(self):
        for scout,confirm in ((35,320),(64,320),(72,640)):
            b=study.equal_budget(scout,confirm)
            self.assertEqual(b["requested_iterations_per_arm"],
                             40*scout+4*confirm)
            self.assertTrue(b["same_binary_profile_combat_target_initial_candidates"])
            self.assertIn("NOT_PRODUCT_DEFAULT",b["v290_comparator"])
        a={"dps_mean":186200.,"dps_sem":200.}
        b={"dps_mean":187000.,"dps_sem":220.}
        c=study.compare_selected(a,b)
        self.assertEqual(c["v306_minus_v290_normalized_dps"],-800)
        self.assertFalse(c["multiple_selection_familywise_95_proven"])
        self.assertFalse(c["global_optimum_proven"])

    def test_20_global_both_policies_equal_44_requests_no_fabricated_native(self):
        B,lower,upper=3400,(0,165,0,0),(2040,)*4
        scout,confirm=35,320
        initial=[]
        hist=[]
        order=v304._global_order(B,lower,upper,study.GLOBAL)
        for i,vec in enumerate(order):
            p=study.plan_v306(hist,B=B,lower=lower,upper=upper,
                              scout=scout,confirm=confirm)
            req=p["next_request"]
            self.assertEqual(tuple(v290.legacy.key(req["target"])),vec)
            row=dict(vector=list(vec),iterations=scout,
                     dps_mean=193000+(i%17)*30,
                     dps_sem=750.)
            initial.append(row)
            hist.append(study.history_row(row,req))
        arms={key:[] for key in study.ARMS}
        for i in range(study.POST):
            for arm in study.ARMS:
                if arm=="v306_seed_retained":
                    proposal=study.plan_v306(hist,B=B,lower=lower,
                        upper=upper,scout=scout,confirm=confirm)
                    req=proposal["next_request"]
                    self.assertEqual(req["phase"],"scout")
                    vec=tuple(v290.legacy.key(req["target"]))
                else:
                    req=None
                    vec,reason,forced=study.normalized_v290_candidate(
                        initial+arms[arm],B=B,lower=lower,upper=upper,
                        scout=scout,confirm=confirm)
                    self.assertIsInstance(forced,bool)
                self.assertTrue(v290.legacy.eligible(vec,B,lower,upper))
                self.assertNotIn(vec,{tuple(r["vector"]) for r in
                                    initial+arms[arm]})
                row=dict(vector=list(vec),iterations=scout,
                         dps_mean=192000+(i%7)*31, dps_sem=750.)
                arms[arm].append(row)
                if req is not None:
                    hist.append(study.history_row(row,req))
        for rank in range(study.CONFIRM):
            for arm in study.ARMS:
                if arm=="v306_seed_retained":
                    req=study.plan_v306(hist,B=B,lower=lower,
                                         upper=upper,scout=scout,
                                         confirm=confirm)["next_request"]
                    self.assertEqual(req["adaptive_stage"],"confirmation")
                    vec=tuple(v290.legacy.key(req["target"]))
                else:
                    req=None
                    by_vec={tuple(r["vector"]):r for r in
                            initial+[r for r in arms[arm]
                                     if r["iterations"]==scout]}
                    rank_order=sorted(by_vec,key=lambda v:
                                      (-study.regional.score(by_vec[v]),v))
                    observed={tuple(r["vector"]) for r in arms[arm]
                              if r["iterations"]==confirm}
                    vec=next(v for v in rank_order if v not in observed)
                row=dict(vector=list(vec),iterations=confirm,
                         dps_mean=192000+rank*16,dps_sem=220.)
                arms[arm].append(row)
                if req is not None:
                    hist.append(study.history_row(row,req))
        self.assertIsNone(study.plan_v306(
            hist,B=B,lower=lower,upper=upper,
            scout=scout,confirm=confirm)["next_request"])
        for arm in study.ARMS:
            rows=initial+arms[arm]
            self.assertEqual(len(rows),study.PLAN_CAP)
            self.assertEqual(sum(r["iterations"] for r in rows),
                study.equal_budget(scout,confirm)["requested_iterations_per_arm"])
            self.assertEqual(len({(tuple(r["vector"]),r["iterations"])
                                  for r in rows}),study.PLAN_CAP)


if __name__=="__main__":
    unittest.main()
