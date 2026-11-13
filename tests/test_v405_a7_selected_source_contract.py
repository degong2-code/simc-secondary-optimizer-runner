"""A7 consumer origin contract, synthetic across different season/build IDs.

v405 reads v163 and v167 evidence: no product seed, token, native, or HTTP.
"""
from __future__ import annotations

import copy
import hashlib
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v405_a7_selected_source_contract as audit
import v167_product_season_gear_adapter as adapter
from tests.test_v167_product_season_gear_adapter import source as make_compact

BUILD="13.0.0.88888"
SEASON=83

def journal(kind="raid_journal",season=SEASON,wse=719):
    return {"source":kind,"season_evidence":(
        "DB2_DISPLAY_SEASON_MATCH" if season==SEASON
        else "UNKNOWN_OTHER_DISPLAY_SEASON"),
        "display_season_id":season,"world_state_expression_id":wse,
        "journal_encounter_id":114,"journal_instance_id":115,
        **({"challenge_mode_id":116} if kind=="mplus_journal" else {})}

def case():
    original=make_compact()
    original["season_build"]=BUILD
    original["expansion_id"]=27
    original["display_season_id"]=SEASON
    origins={}
    for row in original["current_candidates"]:
        if row["item_id"]==105:
            provenance={"source":"selectable_stat_craft","expansion_id":27,
                "classification":"PROVISIONAL_SIMC_BATCH_REVIEW",
                "stat_placeholders":[24,25]}
        else:
            provenance=journal("mplus_journal" if row["item_id"]==104
                               else "raid_journal",wse=row["item_id"])
        origins[row["item_id"]]=provenance
        row["source_kinds"]=[provenance["source"]]
        # v166 preserves just the consumer-relevant fields, not WCL names
        # or craft/bonus text; WSE is retained but never controls admission.
        row["source_evidence"]=[{
            k:v for k,v in provenance.items() if k in (
                "source","season_evidence","display_season_id",
                "world_state_expression_id","journal_encounter_id",
                "journal_instance_id","challenge_mode_id","expansion_id")}]
    product=adapter.from_v166(original)
    source={
        "schema":"v163_zero_seed_db2_join_v1",
        "source_provider":"WAGO_TOOLS_PINNED_DB2_WCL_LIVE",
        "old_item_catalog_imported":False,
        "full_season_completeness_confirmed":False,
        "build":BUILD,
        "db2_expansion_id":27,
        "db2_display_season_id":SEASON,
        "items":[{"item_id":i,"acquisition_sources":[o]}
                 for i,o in origins.items()]
    }
    return source,product

def verify(source,product):
    return audit.assess(
        source=source,catalog=product,expected_game_build=BUILD,
        source_report_sha256=hashlib.sha256(b"source").hexdigest(),
        candidate_sha256=hashlib.sha256(b"candidate").hexdigest())

class A7AutoConsumerProofs(unittest.TestCase):
    def test_no_manual_item_selection_and_reused_provenance(self):
        source,product=case()
        result=verify(source,product)
        self.assertEqual(result["status"],
            "A7_PUBLIC_CANDIDATE_ORIGINS_AUTO_RECONCILED_SOURCE_ONLY")
        self.assertEqual(result["public_candidate_count"],2)
        self.assertEqual(result["public_role_counts"]["trinket"],1)
        self.assertEqual(result["public_role_counts"]["selectable_stat_craft"],1)
        self.assertFalse(result["item_eligibility_requires_wse"])
        self.assertTrue(result["wse_diagnostics_preserved_not_evaluated"])
        self.assertFalse(result["effect_or_simc_certification"])
        self.assertFalse(result["final_product_e2e"])
        self.assertFalse(result["manually_selected_item_ids"])
        self.assertEqual(result["additional_api_calls"],0)
        self.assertEqual(result["native_calls"],0)
        self.assertEqual(result["public_item_ids_sha256"],
                         audit.sha([104,105]))

    def test_wse_positive_none_or_malformed_never_gates_season(self):
        for wse in (0,905, None, "bad-observed-value"):
            with self.subTest(wse=wse):
                source,product=case()
                for row in source["items"]:
                    if row["item_id"]==104:
                        row["acquisition_sources"][0][
                            "world_state_expression_id"]=wse
                for row in product["items"]:
                    if row["item_id"]==104:
                        row["source_evidence"][0][
                            "world_state_expression_id"]=wse
                self.assertEqual(verify(source,product)["public_candidate_count"],2)

    def test_forged_current_choice_without_original_source_rejected(self):
        source,product=case()
        source["items"]=[r for r in source["items"] if r["item_id"]!=104]
        with self.assertRaisesRegex(
             audit.SourceContractBlocked,
             "A7_PUBLIC_ITEM_WITHOUT_AUTHENTICATED_SOURCE"):
            verify(source,product)

    def test_other_season_raid_or_mplus_rejected_even_with_wse_zero(self):
        for kind in ("raid_journal","mplus_journal"):
            with self.subTest(kind=kind):
                source,product=case()
                for row in source["items"]:
                    if row["item_id"]==104:
                        row["acquisition_sources"]=[journal(kind,SEASON+1,0)]
                for row in product["items"]:
                    if row["item_id"]==104:
                        row["source_evidence"]=[journal(kind,SEASON+1,0)]
                        row["source_kinds"]=[kind]
                with self.assertRaisesRegex(
                    audit.SourceContractBlocked,
                    "A7_NO_CURRENT_JOURNAL_OR_CRAFT_ORIGIN"):
                    verify(source,product)

    def test_changed_item_source_provenance_rejected(self):
        source,product=case()
        for row in product["items"]:
            if row["item_id"]==104:
                row["source_evidence"][0]["journal_encounter_id"]=999999
        with self.assertRaisesRegex(
            audit.SourceContractBlocked,"A7_PUBLIC_ITEM_SOURCE_EVIDENCE_DRIFT"):
            verify(source,product)

    def test_wrong_build_and_display_season_rejected(self):
        source,product=case()
        product["db2_display_season_id"]=SEASON+1
        with self.assertRaisesRegex(
            audit.SourceContractBlocked,"A7_SEASON_AND_EXPANSION_MISMATCH"):
            verify(source,product)
        source,product=case()
        source["build"]="13.0.0.99999"
        with self.assertRaisesRegex(
            audit.SourceContractBlocked,"A7_AUTHENTICATED_CURRENT_DB2_SOURCE_REQUIRED"):
            verify(source,product)

if __name__=="__main__":
    unittest.main()
