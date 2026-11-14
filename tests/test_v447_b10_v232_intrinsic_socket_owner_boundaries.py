"""v447 B10: distinguish sealed intrinsic slots, SimC declarations and J.

No HTTP, SimC Native or fresh season item certification. All fixtures synthetic.
"""
from __future__ import annotations

import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v216_environment_build_coordinator as engine
import v271_user_socket_gem_layout as sockets


class B10OriginalSocketSourceBoundaries(unittest.TestCase):
    @staticmethod
    def rows():
        return {
            slot:{"slot":slot,"item_id":270000+i,
                  "ilevel":334,"options":{}}
            for i,slot in enumerate(
                ("head","neck","finger1","finger2","wrists","feet"))}

    @staticmethod
    def base_counts():
        # Three jewelry sockets are original; head is only SimC-declared.
        return {"head":0,"neck":1,"finger1":1,
                "finger2":1,"wrists":0,"feet":0}

    def prepare(self,*,declared=True,game_build="12.1.5.70783",
                intrinsic=None,plan_counts=None,stage_status="EXECUTED_AND_SEALED"):
        counts=self.base_counts() if intrinsic is None else intrinsic
        desired=({"head":1,"neck":1,"finger1":1,"finger2":1}
                 if plan_counts is None else plan_counts)
        total=sum(desired.values())
        ids=[311101,311102,311103,311104]+[311101]*(total-4)
        plan={"socket_counts":desired,"special_gem_id":None,
              "special_slot":None,"ordinary_gem_ids":ids,
              "source_observed_gem_item_ids":sorted(set(ids))}
        _,layout=sockets.arrange(self.rows(),plan,engine.need)
        if declared:
            layout["simc_declared_full_socket_policy"]=(
                "FULL_GEM_ID_PROFILE_SIMC_OWNS")
        revision="c"*40
        collected={"expected_game_build":game_build,
                   "fresh_one_spec_simc_representative":{
                       "status":"FRESH_ONE_SPEC_SIMC_G_SOURCE_CANDIDATE_PENDING_NATIVE",
                       "source_stage":{"status":stage_status,
                                       "receipt_sha256":"a"*64},
                       "intrinsic_socket_counts_by_selected_slot_source_only":
                           counts,
                       "selected_slot_count":len(counts),
                       "intrinsic_socket_total_source_only":sum(counts.values()),
                       "added_socket_bonus_and_game_permission_not_proven":True}}
        preflight={
            "schema":engine.FRESH_SOURCE_PREFLIGHT_SCHEMA,
            "game_build":game_build,"simc_revision":revision,
            "environment_ready":False,
            "physical_gem_layout_unadmitted":layout,
            "physical_gem_J_arithmetic_unadmitted":{
                "status":"PHYSICAL_GEM_J_ARITHMETIC_UNADMITTED",
                "physical_gem_item_ids":ids,
                "J_candidate_unadmitted":23*len(ids),
                "environment_ready":False}}
        compilation={"simc_revision":revision}
        return collected,preflight,compilation

    def read(self,parts):
        collected,preflight,compilation=parts
        return engine._fresh_selected_J_intrinsic_socket_source(
            collected=collected,preflight=preflight,compilation=compilation)

    def test_sealed_intrinsic_jewelry_and_declared_head_are_separated(self):
        result=self.read(self.prepare())
        self.assertEqual(result["intrinsic_socket_counts_by_slot"],
                         self.base_counts())
        self.assertEqual(result["additional_socket_proof_required_by_slot"],
                         {"head":1})
        self.assertEqual(result["observed_J_unadmitted"],92)
        self.assertEqual(result["status"],
                         "J_SIMC_DECLARED_FULL_GEM_PROFILE_SOURCE_ONLY")
        self.assertFalse(result["game_socket_legal_verified"])
        self.assertFalse(result["J_approved"])
        self.assertFalse(result["environment_ready"])

    def test_no_declared_approval_addition_is_explicitly_pending(self):
        result=self.read(self.prepare(declared=False))
        self.assertEqual(result["status"],
                         "J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING")
        self.assertEqual(result["additional_socket_proof_required_by_slot"],
                         {"head":1})
        self.assertFalse(result["game_socket_legal_verified"])

    def test_real_intrinsic_four_needs_no_bonus_socket_proof(self):
        intrinsic={**self.base_counts(),"head":1}
        result=self.read(self.prepare(declared=False,intrinsic=intrinsic))
        self.assertEqual(result["status"],
                         "J_INTRINSIC_COUNTS_BOUND_SOURCE_ONLY")
        self.assertEqual(result["additional_socket_proof_required_by_slot"],{})
        self.assertFalse(result["J_approved"])

    def test_declared_extra_on_existing_slot_remains_unverified(self):
        desired={"head":1,"neck":1,"finger1":1,"finger2":1,"wrists":1}
        result=self.read(self.prepare(plan_counts=desired))
        self.assertEqual(result["additional_socket_proof_required_by_slot"],
                         {"head":1,"wrists":1})
        self.assertEqual(result["observed_J_unadmitted"],115)
        self.assertFalse(result["game_socket_legal_verified"])

    def test_phantom_slot_outside_original_sealed_item_set_rejected(self):
        original=self.base_counts()
        original.pop("feet")
        desired={"head":1,"neck":1,"finger1":1,"finger2":1,"feet":1}
        parts=self.prepare(intrinsic=original,plan_counts=desired)
        with self.assertRaisesRegex(engine.EnvironmentBuildBlocked,
                                    "V216_J_V232_SELECTED_SOCKET_SLOT_OUTSIDE_ORIGINAL"):
            self.read(parts)

    def test_changed_build_cannot_claim_original_game_legality(self):
        result=self.read(self.prepare(game_build="12.2.0.99999"))
        self.assertEqual(result["additional_socket_proof_required_by_slot"],
                         {"head":1})
        self.assertFalse(result["game_socket_legal_verified"])
        self.assertFalse(result["J_approved"])

    def test_wrong_season_source_or_stage_receipt_rejected(self):
        parts=self.prepare()
        parts[0]["expected_game_build"]="12.2.0.99999"
        with self.assertRaises(engine.EnvironmentBuildBlocked):
            self.read(parts)
        parts=self.prepare()
        parts[0]["fresh_one_spec_simc_representative"][
            "source_stage"]["receipt_sha256"]="not-a-sha"
        with self.assertRaises(engine.EnvironmentBuildBlocked):
            self.read(parts)

    def test_unsealed_source_does_not_become_ready(self):
        pending=self.read(self.prepare(stage_status="PENDING"))
        self.assertEqual(pending["status"],"J_V232_INTRINSIC_SOURCE_PENDING")
        self.assertIsNone(pending["intrinsic_socket_counts_by_slot"])
        self.assertFalse(pending["environment_ready"])
        self.assertFalse(pending["J_approved"])


if __name__=="__main__":
    unittest.main()
