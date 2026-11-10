"""Offline planning sanity for bounded real SimC comparison; no Native."""
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"integration_probes"), str(ROOT/"runner")]
import p2_real_equal_v304_once as pilot


class EqualBudgetPilotOffline(unittest.TestCase):
    def fake(self, vec, iterations=35, mean=190000, sem=300):
        return {
            "vector": list(vec), "iterations": iterations,
            "dps_mean": float(mean), "dps_sem": float(sem),
        }

    def global_rows(self):
        return [
            self.fake(v, mean=190000 - i*5)
            for i, v in enumerate(pilot.v304._global_order(
                pilot.B, tuple(pilot.LOWER), tuple(pilot.UPPER), pilot.GLOBAL))
        ]

    def test_exact_same_requested_iterations_and_three_arms(self):
        budget = pilot.equal_resource_contract()
        self.assertEqual(budget["requested_iterations_per_arm"], 4520)
        self.assertEqual(budget["logical_requests_per_arm"], 69)
        self.assertEqual(pilot.ARMS, (
            "fixed_local6", "adaptive_v304", "v290_proposal_normalized"))
        self.assertTrue(budget["global_optimum_proven"] is False)
        self.assertIn("NOT unmodified", budget[
            "candidate_policy_v290_caveat"])

    def test_fixed_local6_unique_and_feasible_and_global_distinct(self):
        global_rows = self.global_rows()
        fixed = pilot.fixed_local_candidates(global_rows, count=32)
        observed = {tuple(x["vector"]) for x in global_rows}
        self.assertEqual(len(fixed), 32)
        self.assertEqual(len(set(fixed)), 32)
        self.assertTrue(all(v not in observed for v in fixed))
        self.assertTrue(all(pilot.v290.legacy.eligible(
            v, pilot.B, pilot.LOWER, pilot.UPPER) for v in fixed))

    def test_normalized_v290_proposes_unmeasured_scout(self):
        rows = self.global_rows()
        vec, decision, forced = pilot.normalized_v290_candidate(rows)
        self.assertNotIn(vec, {tuple(x["vector"]) for x in rows})
        self.assertTrue(pilot.v290.legacy.eligible(
            vec, pilot.B, pilot.LOWER, pilot.UPPER))
        self.assertIsInstance(decision, str)
        self.assertIsInstance(forced, bool)

    def test_v304_full_32_post_plus_4_confirm_without_native(self):
        history=[]
        for i, vec in enumerate(pilot.v304._global_order(
                pilot.B, tuple(pilot.LOWER), tuple(pilot.UPPER), pilot.GLOBAL)):
            p=pilot.v304.next_plan(
                history, total=pilot.B, lower=pilot.LOWER, upper=pilot.UPPER,
                max_native_calls=pilot.GLOBAL+pilot.POST+pilot.CONFIRM,
                scout_iterations=pilot.SCOUT_ITERS,
                confirmation_iterations=pilot.CONFIRM_ITERS,
                initial_global_calls=pilot.GLOBAL,
                confirmation_calls=pilot.CONFIRM)
            r=p["next_request"]
            history.append(pilot.to_v304_row(
                self.fake(vec, mean=190000+i*4),r))
        stages=[]
        for step in range(pilot.POST):
            p=pilot.v304.next_plan(
                history, total=pilot.B, lower=pilot.LOWER, upper=pilot.UPPER,
                max_native_calls=pilot.GLOBAL+pilot.POST+pilot.CONFIRM,
                scout_iterations=pilot.SCOUT_ITERS,
                confirmation_iterations=pilot.CONFIRM_ITERS,
                initial_global_calls=pilot.GLOBAL,
                confirmation_calls=pilot.CONFIRM)
            r=p["next_request"]
            self.assertEqual(r["phase"],"scout")
            stages.append(r["adaptive_stage"])
            vec=tuple(pilot.v290.legacy.key(r["target"]))
            history.append(pilot.to_v304_row(
                self.fake(vec, mean=190100+step*6),r))
        # v304 reserves ceil(15%) for SMALL sessions (5 of 32);
        # its 160-post main study reserves 24. Do not hardcode 8 here.
        regional_options=pilot.v304.options(
            pilot.GLOBAL+pilot.POST+pilot.CONFIRM,
            pilot.GLOBAL,pilot.CONFIRM)
        self.assertEqual(stages.count("global_reserve"),
                         regional_options["global_reserve_calls"])
        self.assertEqual(stages.count("regional"),
                         regional_options["regional_calls"])
        for step in range(pilot.CONFIRM):
            p=pilot.v304.next_plan(
                history, total=pilot.B, lower=pilot.LOWER, upper=pilot.UPPER,
                max_native_calls=pilot.GLOBAL+pilot.POST+pilot.CONFIRM,
                scout_iterations=pilot.SCOUT_ITERS,
                confirmation_iterations=pilot.CONFIRM_ITERS,
                initial_global_calls=pilot.GLOBAL,
                confirmation_calls=pilot.CONFIRM)
            r=p["next_request"]
            self.assertEqual(r["adaptive_stage"],"confirmation")
            vec=tuple(pilot.v290.legacy.key(r["target"]))
            history.append(pilot.to_v304_row(
                self.fake(vec, iterations=pilot.CONFIRM_ITERS,
                          mean=190200+step*2),r))
        self.assertEqual(len(history),68)
        self.assertIsNone(pilot.v304.next_plan(
            history, total=pilot.B, lower=pilot.LOWER, upper=pilot.UPPER,
            max_native_calls=pilot.GLOBAL+pilot.POST+pilot.CONFIRM,
            scout_iterations=pilot.SCOUT_ITERS,
            confirmation_iterations=pilot.CONFIRM_ITERS,
            initial_global_calls=pilot.GLOBAL,
            confirmation_calls=pilot.CONFIRM)["next_request"])

    def test_real_history_reuse_requires_same_proven_source(self):
        one = self.fake((800,800,800,707), mean=190000.0)
        one["json2_sha256"] = "a"*64
        good = {
            "schema": "p2_nested_real_simc_11_21_comparison_v1",
            "status": "PASS_REAL_NATIVE_EXPLORATORY_NO_GLOBAL_PROOF",
            "binary_sha256": pilot.prior.BINARY_SHA,
            "source_archive_sha256": pilot.prior.INNER_SHA,
            "source_commit": pilot.KNOWN_SOURCE_COMMIT,
            "stable_input_profile_sha256": "b"*64,
            "observations": {"arm1":[one], "arm2":[one]},
        }
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/"receipt.json"
            p.write_text(json.dumps(good))
            recovered=pilot.historical_cache(p,"b"*64)
            self.assertEqual(len(recovered),1)
            self.assertEqual(
                recovered[((800,800,800,707),35)]["dps_mean"],
                190000.0)
            with self.assertRaisesRegex(RuntimeError,"IDENTITY_MISMATCH"):
                pilot.historical_cache(p,"c"*64)

    def test_v304_32_global_history_and_region_candidate(self):
        rows=self.global_rows()
        history=[]
        for row in rows:
            action=pilot.v304.next_plan(
                history,total=pilot.B,lower=pilot.LOWER,upper=pilot.UPPER,
                max_native_calls=pilot.GLOBAL+pilot.POST+pilot.CONFIRM,
                scout_iterations=pilot.SCOUT_ITERS,
                confirmation_iterations=pilot.CONFIRM_ITERS,
                initial_global_calls=pilot.GLOBAL,
                confirmation_calls=pilot.CONFIRM)
            req=action["next_request"]
            self.assertEqual(req["adaptive_stage"],"global_initial")
            self.assertEqual(tuple(pilot.v290.legacy.key(req["target"])),
                             tuple(row["vector"]))
            history.append(pilot.to_v304_row(row,req))
        after=pilot.v304.next_plan(
            history,total=pilot.B,lower=pilot.LOWER,upper=pilot.UPPER,
            max_native_calls=pilot.GLOBAL+pilot.POST+pilot.CONFIRM,
            scout_iterations=pilot.SCOUT_ITERS,
            confirmation_iterations=pilot.CONFIRM_ITERS,
            initial_global_calls=pilot.GLOBAL,
            confirmation_calls=pilot.CONFIRM)
        self.assertEqual(after["next_request"]["phase"],"scout")
        self.assertIn(after["next_request"]["adaptive_stage"],
                      ("regional","global_reserve"))

if __name__=="__main__":
    unittest.main()
