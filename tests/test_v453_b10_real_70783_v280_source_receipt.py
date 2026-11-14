"""v453 B10: protect observed 70783 v280 on-use IDs against synthetic drift.

REAL source was collected by v452 one-shot Actions. This is a compact
research receipt, NOT an immutable v217 runtime source or game applicability.
"""
from __future__ import annotations

import json,pathlib,re,unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
RECEIPT=ROOT/"docs/development/research_receipts"/(
    "p1_v452_b10_real_70783_v280_socket_item_use_source.json")


class Real70783V280SocketSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads(RECEIPT.read_text("utf8"))

    def test_build_revision_and_exact_research_identity_are_pinned(self):
        d=self.doc
        self.assertEqual(d["game_build"],"12.1.5.70783")
        self.assertEqual(d["pinned_simc_revision"],
                         "c20e2ad52e4c33711f74272309a5748125175fe8")
        self.assertEqual(d["original_workflow_run_id"],43566234553)
        self.assertEqual(d["original_workflow_artifact_id"],14102746031)
        self.assertEqual(d["original_workflow_receipt_sha256"],
            "36f068bf4043e3c5dd40e3e511534091d1ac5dcfc42943556d4887c62bc43753")
        self.assertEqual(d["status"],
                         "REAL_SAME_BUILD_V280_SOURCE_HINTS_UNADMITTED")

    def test_same_build_sources_carry_raw_hashes_without_native(self):
        d=self.doc
        self.assertEqual(set(d["source_table_sha256"]),{
            "Item","ItemSparse","ItemXItemEffect","ItemEffect",
            "simc_pinned_unique_gear"})
        self.assertTrue(all(re.fullmatch("[0-9a-f]{64}",v) for v in
                            d["source_table_sha256"].values()))
        self.assertRegex(d["original_v280_join_sha256"],"^[0-9a-f]{64}$")
        self.assertEqual(d["native_calls"],0)
        self.assertEqual(d["dps_calls"],0)

    def test_original_join_observed_exact_item_to_use_spell_ids(self):
        rows=self.doc["physical_item_use_candidates_unadmitted"]
        self.assertEqual([
            (r["item_id"],r["name_enUS"],r["on_use_spell_ids"])
            for r in rows],[
            (263897,"Radiant Jewelbinder",[1270804]),
            (275707,"Miasmic Jewelbinder",[1309820]),
            (276187,"Venomous Jeweler's Setting",[1309139])])
        self.assertEqual(self.doc["v280_total_considered"],561)
        self.assertTrue(all(r["expansion_id"]==11
                            and r["item_class"]==0
                            and r["item_subclass"]==8 for r in rows))

    def test_miasmic_effect_spell_must_not_replace_real_on_use_spell(self):
        observed={
            x["item_id"]:x["on_use_spell_ids"] for x in
            self.doc["physical_item_use_candidates_unadmitted"]}
        self.assertEqual(observed[275707],[1309820])
        self.assertNotIn(1297709,observed[275707])

    def test_source_is_not_socket_use_permission_or_j_admission(self):
        doc=self.doc
        for key in ("user_item_applicability_verified",
                    "pvp_exclusion_verified",
                    "added_socket_spell_effect_verified",
                    "actual_bonus_socket_count_verified",
                    "J_approved","ui_selectable",
                    "environment_ready","installed_environment"):
            self.assertIs(doc[key],False,key)
        self.assertTrue(doc["source_only"])
        for candidate in doc["physical_item_use_candidates_unadmitted"]:
            self.assertIs(candidate["same_season_use_applicability_verified"],
                          False)
            self.assertIs(candidate["ui_selectable"],False)

    def test_research_evidence_is_not_original_v217_runtime_stage(self):
        self.assertNotIn("v280_stage_receipt_sha256",self.doc)
        self.assertNotIn("source_stage",self.doc)
        self.assertNotIn("environment_manifest_sha256",self.doc)

    def test_existing_v449_fixture_reuses_real_ids_but_not_proof(self):
        from tests.test_v449_b10_existing_v280_socket_item_owner import (
            V449ExistingItemUseOwner)
        x=V449ExistingItemUseOwner()
        x.setUp()
        try:
            fixture={
                r["item_id"]:r["item_effect_source"]["on_use_spell_ids"]
                for r in x.source
                if r["item_id"] in (263897,275707,276187)}
            observed={
                r["item_id"]:r["on_use_spell_ids"]
                for r in self.doc["physical_item_use_candidates_unadmitted"]}
            self.assertEqual(fixture,observed)
            self.assertTrue(all(r["ui_selectable"] is False
                                for r in x.source))
        finally:
            x.doCleanups()


if __name__=="__main__":
    unittest.main()
