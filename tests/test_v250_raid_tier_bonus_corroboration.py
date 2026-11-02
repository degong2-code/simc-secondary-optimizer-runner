"""v250 candidate-only active raid/tier DB2 bonus group proof, no network/Native."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
import tempfile
import unittest

from runner import v245_db2_first_tier_discovery as tierdb
from runner import v250_raid_tier_bonus_corroboration as v250
from tests.test_v245_db2_first_tier_discovery import arrange, BUILD

def source_rows(dual_raid=False):
    records=[];nodes=[]
    for wave in (0,1):
        for n in range(13):
            for pos in range(5):
                iid=910000+100*n+pos if wave==0 else 820000+100*n+pos
                records.append({"ID":len(records)+1,"ItemID":iid,
                                "ItemBonusTreeID":900+wave})
        for g in range(5):
            nodes.append({"ID":len(nodes)+1,"ParentItemBonusTreeID":900+wave,
                          "ChildItemBonusTreeID":0,
                          "ChildItemBonusListGroupID":(608 if wave==0 else 614)+g})
    for iid in (7001,7002):
        records.append({"ID":len(records)+1,"ItemID":iid,"ItemBonusTreeID":901})
    if dual_raid:
        records.append({"ID":len(records)+1,"ItemID":7001,"ItemBonusTreeID":900})
    def make(rows):
        buf=io.StringIO()
        w=csv.DictWriter(buf,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
        return buf.getvalue().encode("utf8")
    return {"ItemXBonusTree":make(records),"ItemBonusTreeNode":make(nodes)}

def raid_scope(valid=True):
    return {"schema":"v163_zero_seed_db2_join_v1",
        "source_provider":"WAGO_TOOLS_PINNED_DB2_WCL_LIVE",
        "build":BUILD,"db2_expansion_id":11,
        "auto_source_scope":{"raid_zone":"Synthetic Current Raid",
             "source_basis":("LIVE_WCL_ACTIVE_ZONES_AND_SAME_BUILD_DB2"
                             if valid else "UNKNOWN")},
        "full_season_completeness_confirmed":False,
        "items":[{"item_id":7001,"acquisition_sources":[{
            "source":"raid_journal","journal_encounter_id":1}]}],
        "raid_non_equipment_loot_candidates":[{
            "item_id":7002,"observed_base_item_level":219,
            "acquisition_sources":[{"source":"raid_journal",
                                    "journal_encounter_id":1}]}]}

def inputs(tmp):
    root=Path(tmp);folder=root/"wago";folder.mkdir()
    sources=arrange(folder)
    tier=tierdb.discover(wago_folder=folder,build=BUILD,
                         expansion_id=11,source_bytes=sources)
    return tier,raid_scope()

class RaidBonusCorroboration(unittest.TestCase):
    def test_raid_shared_bonus_groups_select_observed_candidate_not_season(self):
        with tempfile.TemporaryDirectory() as td:
            tier,raid=inputs(td)
            result=v250.correlate(tier=tier,raid=raid,
                                  source_bytes=source_rows())
            self.assertEqual(result["candidate_cohort_count"],2)
            self.assertEqual(result["raid_journal_item_count"],2)
            self.assertEqual(result["status"],
                "UNIQUE_RAID_BONUS_CORRELATED_TIER_COHORT_SEASON_PENDING")
            best=result["observed_leading_cohort"]
            self.assertEqual(best["observed_base_item_level"],219)
            self.assertEqual(best["physical_items"],65)
            self.assertEqual(best["bonus_list_group_ids"],[614,615,616,617,618])
            self.assertEqual(best["raid_loot_overlap_item_count"],2)
            self.assertEqual(best["raid_non_equipment_same_base_ilvl_count"],1)
            prior=result["cohort_comparisons"][1]
            self.assertEqual(prior["observed_base_item_level"],44)
            self.assertEqual(prior["raid_loot_overlap_item_count"],0)
            self.assertIs(result["source_season_verified"],False)
            self.assertIs(result["environment_ready"],False)
            self.assertIs(result["observed_leading_cohort_is_certified_current_season"],False)

    def test_tied_overlap_is_unresolved(self):
        with tempfile.TemporaryDirectory() as td:
            tier,raid=inputs(td)
            records=source_rows(dual_raid=True)
            # Both cohorts share one current-raid item, but older cohort
            # has not been independently ruled out.
            raid["raid_non_equipment_loot_candidates"]=[]
            result=v250.correlate(tier=tier,raid=raid,source_bytes=records)
            self.assertEqual(result["status"],
                             "RAID_BONUS_TIER_COHORT_AMBIGUOUS_PENDING")
            self.assertIsNone(result["observed_leading_cohort"])

    def test_non_authenticated_or_mismatched_build_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as td:
            tier,raid=inputs(td)
            with self.assertRaisesRegex(v250.BonusSourceBlocked,
                                         "V250_AUTHENTICATED_SAME_BUILD_RAID_REQUIRED"):
                v250.correlate(tier=tier,raid=raid_scope(False),
                               source_bytes=source_rows())
            raid["build"]="12.3.0.99999"
            with self.assertRaisesRegex(v250.BonusSourceBlocked,
                                         "V250_AUTHENTICATED_SAME_BUILD_RAID_REQUIRED"):
                v250.correlate(tier=tier,raid=raid,
                               source_bytes=source_rows())

    def test_stage_sealed_reuse_requests_exact_two_tables_once(self):
        class Response(io.BytesIO):
            status=200
            def __enter__(self):return self
            def __exit__(self,*a):self.close()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);tier,raid=inputs(td)
            t=root/"tier.json";r=root/"raid.json"
            t.write_text(json.dumps(tier),encoding="utf8")
            r.write_text(json.dumps(raid),encoding="utf8")
            folder=root/"stage";folder.mkdir()
            data=source_rows()
            calls=[]
            def fetch(req,timeout):
                name=req.full_url.split("/db2/")[1].split("/")[0]
                calls.append(name)
                return Response(data[name])
            args={"stage_root":folder,"build":BUILD,
                  "tier_candidate_path":t,"raid_candidate_path":r,
                  "tier_stage_receipt":"a"*64,"raid_stage_receipt":"b"*64,
                  "transport":fetch}
            first=v250.build_stage(**args)
            second=v250.build_stage(**args)
            self.assertEqual(calls,list(v250.TABLES))
            self.assertEqual(first["network_calls_by_stage"],2)
            self.assertEqual(second["network_calls_by_stage"],0)
            self.assertEqual(first["source_stage"]["status"],"EXECUTED_AND_SEALED")
            self.assertEqual(second["source_stage"]["status"],"REUSED_VERIFIED")
            self.assertEqual(first["observed_leading_cohort"]["observed_base_item_level"],219)
            self.assertFalse(first["source_season_verified"])

if __name__=="__main__":
    unittest.main()
