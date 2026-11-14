"""v448 B10: source-bound four ordinary BASE != optional socket admission.

Synthetic, offline-only J owner regression. No new item, effect or Native gate.
"""
from __future__ import annotations

import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v216_environment_build_coordinator as engine
from tests.test_v447_b10_v232_intrinsic_socket_owner_boundaries import (
    B10OriginalSocketSourceBoundaries as SocketFixture)


class DeclaredJOwnerScope(unittest.TestCase):
    def setUp(self):
        self.fixture=SocketFixture()

    def case(self,*,slots=None,intrinsic=None,declared=True,
             mutate_layout=None):
        kwargs={"declared":declared}
        if slots is not None:
            kwargs["plan_counts"]=slots
        if intrinsic is not None:
            kwargs["intrinsic"]=intrinsic
        collected,pre,comp=self.fixture.prepare(**kwargs)
        layout=pre["physical_gem_layout_unadmitted"]
        if mutate_layout is not None:
            mutate_layout(layout)
            pre["physical_gem_J_arithmetic_unadmitted"][
                "physical_gem_item_ids"]=list(layout["ordinary_gem_ids"])
        socket=engine._fresh_selected_J_intrinsic_socket_source(
            collected=collected,preflight=pre,compilation=comp)
        return pre,layout,socket

    @staticmethod
    def official(pre,layout,socket):
        ids=layout["ordinary_gem_ids"]
        unique={str(i):23 for i in ids}
        owner={
            "ordinary_gem_item_ids":list(ids),
            "rating":sum(unique[str(i)] for i in ids),
            "v221_stage_receipt_sha256":"b"*64,
            "per_item_nominal_rating":unique,
            "numeric_source_owner":"PACKAGED_SEASON_NOMINAL_PER_ITEM",
            "season_nominal_source_sha256":"e"*64,
            "source_identity_sha256":"f"*64}
        quality={
            "ordinary_gem_item_ids":list(ids),
            "same_enchant_quality_groups_source_only":[],
            "v230_stage_receipt_sha256":"a"*64,
            "v221_stage_receipt_sha256":"b"*64,
            "real_socket_proof_required":True,
            "selected_nominal_quality_matches_v230":True,
            "season_nominal_source_sha256":"e"*64}
        stage={
            "status":"FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED",
            "stage_status":"EXECUTED_AND_SEALED",
            "stage_receipt_sha256":"d"*64}
        checked_pre={
            **pre,"source_catalog_manifest_sha256":"c"*64}
        compilation={
            "simc_revision":pre["simc_revision"],
            "physical_gem_layout_unadmitted":layout,
            "selected_J_intrinsic_socket_origin_unadmitted":socket}
        return engine._fresh_source_owner_original_J_F_components(
            preflight=checked_pre,compilation=compilation,
            staged=stage,owner_numeric={"J":owner},
            quality_scope={"J":quality},effect_observations=[])

    def test_four_ordinary_default_preserves_70783_compatibility(self):
        pre,layout,socket=self.case()
        self.assertEqual(socket["observed_J_unadmitted"],92)
        self.assertEqual(socket["additional_socket_proof_required_by_slot"],
                         {"head":1})
        self.assertEqual(socket["status"],
                         "J_SIMC_DECLARED_FULL_GEM_PROFILE_SOURCE_ONLY")
        result=self.official(pre,layout,socket)
        self.assertEqual(result["J"]["rating"],92)
        self.assertEqual(result["J"]["budget_policy"],
                         "NOMINAL_ORDINARY_GEMS_ONLY")
        self.assertFalse(socket["game_socket_legal_verified"])

    def test_fifth_ordinary_declared_without_real_source_cannot_admit_J(self):
        desired={"head":1,"neck":1,"finger1":1,"finger2":1,"wrists":1}
        pre,layout,socket=self.case(slots=desired)
        self.assertEqual(socket["status"],
                         "J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING")
        self.assertEqual(socket["additional_socket_proof_required_by_slot"],
                         {"head":1,"wrists":1})
        self.assertNotIn("J",self.official(pre,layout,socket))

    def test_seven_declared_without_physical_source_remains_pending(self):
        desired={"head":1,"neck":2,"finger1":2,"finger2":2}
        pre,layout,socket=self.case(slots=desired)
        self.assertEqual(layout["socket_total"],7)
        self.assertEqual(socket["status"],
                         "J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING")
        self.assertNotIn("J",self.official(pre,layout,socket))

    def test_four_with_repeated_gem_does_not_impersonate_base_four(self):
        def change(layout):
            layout["ordinary_gem_ids"]=[311101]*4
            layout["ordinary_count"]=4
        pre,layout,socket=self.case(mutate_layout=change)
        # The independent original J source checks exact selected IDs before
        # a public decision. This helper must not grant BASE compatibility.
        self.assertFalse(engine._fresh_declared_four_ordinary_base_compatibility(
            layout=layout,extra={"head":1}))
        self.assertEqual(socket["status"],
                         "J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING")
        self.assertNotIn("J",self.official(pre,layout,socket))

    def test_four_with_original_intrinsic_all_verified_no_exception_needed(self):
        counts={"head":1,"neck":1,"finger1":1,
                "finger2":1,"wrists":0,"feet":0}
        pre,layout,socket=self.case(intrinsic=counts,declared=False)
        self.assertEqual(socket["additional_socket_proof_required_by_slot"],{})
        self.assertEqual(socket["status"],
                         "J_INTRINSIC_COUNTS_BOUND_SOURCE_ONLY")
        self.assertEqual(self.official(pre,layout,socket)["J"]["rating"],92)

    def test_unselected_source_without_declared_is_pending_not_base(self):
        pre,layout,socket=self.case(declared=False)
        self.assertEqual(socket["status"],
                         "J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING")
        self.assertNotIn("J",self.official(pre,layout,socket))

    def test_selected_special_gem_is_not_five_ordinary_base(self):
        desired={"head":1,"neck":1,"finger1":1,"finger2":1,"wrists":1}
        pre,layout,socket=self.case(slots=desired)
        self.assertFalse(engine._fresh_declared_four_ordinary_base_compatibility(
            layout={**layout,"special_gem_id":311200,
                    "ordinary_count":4,"ordinary_gem_ids":
                        layout["ordinary_gem_ids"][:4]},
            extra={"head":1,"wrists":1}))
        self.assertNotIn("J",self.official(pre,layout,socket))


if __name__=="__main__":
    unittest.main()
