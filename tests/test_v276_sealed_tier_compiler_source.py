"""P3-CF: no old tier IDs, original sealed v251 + same-build 65 DB2 rows.

This uses existing 13x5 v251/SimC fixture, real v217 stage, and the original
v191 compiler contract. No actual game HTTP, native execution or prior build.
"""
from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v168_current_season_tier_discovery as physical
import v191_unified_season_data_update as compiler
import v251_db2_raid_tier_simc_bridge as bridge
import v261_tier_source_evidence_reuse as reuse
import v274_zero_history_source_compiler_wiring as wiring
import v276_sealed_tier_compiler_source as stage
from tests.test_v251_db2_raid_tier_simc_bridge import (
    fixture,pinned_thirteen_class_source)
from tests.test_v250_raid_tier_bonus_corroboration import BUILD

class V251PhysicalTierCompiler(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=pathlib.Path(tmp.name)/"source_build"
        self.root.mkdir()
        self.wago=self.root/"wago"
        # The existing v250 fixture creates its own Wago workspace.
        t,b=fixture(self.root)
        self.physical=bridge.preview(db2=t,corroboration=b)
        seed_root=self.root/"simc";seed_root.mkdir()
        pinned_thirteen_class_source(seed_root,self.physical)
        rec,group=bridge.simc_tier.read_receipt(seed_root)
        self.exact=bridge.match_first_party_roster(
            candidate=self.physical,simc_receipt=rec,simc_set_groups=group)
        pair=(("physical","fresh-v251-db2-raid-tier-candidate",
               "v251_raid_correlated_tier_65_piece_candidate.json","a"*64),
              ("exact","fresh-v251-exact-first-party-simc-options",
               "v251_exact_first_party_13_class_simc_options.json","b"*64))
        for field,id,name,sha in pair:
            file=self.root/"source"/name
            file.parent.mkdir(exist_ok=True)
            file.write_text(json.dumps(getattr(self,field)),encoding="utf8")
            setattr(self,field+"_source",{
                "candidate_path":str(file),
                "source_stage":{
                    "stage_id":id,"status":"EXECUTED_AND_SEALED",
                    "receipt_sha256":sha}})
        self.selected=reuse.reuse_existing_tier_source(
            physical_candidate=self.physical,exact_match=self.exact)
        self.selected["source_stage_receipts"]={
            "raid_correlated_physical":"a"*64,
            "simc_exact_13_class":"b"*64}
        self._write_db2()

    def _write_csv(self,name,rows):
        file=self.wago/(name+".csv")
        with file.open("w",encoding="utf8",newline="") as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
            writer.writeheader();writer.writerows(rows)
        return file

    def _write_db2(self,*,changed=None):
        sparse=[];items=[]
        inventory={"head":1,"shoulders":3,"chest":20,
                   "hands":10,"legs":7}
        for cls,entry in sorted(self.physical["classes"].items()):
            for slot,iid in entry["tier_piece_ids"].items():
                row={"ID":iid,
                     "Display_lang":"Observed "+cls+" "+slot,
                     "InventoryType":inventory[slot],
                     "ExpansionID":self.physical["expansion_id"],
                     "ItemSet":entry["item_set_id"],
                     "AllowableClass":1<<(bridge.simc_tier.CLASS_ID[cls]-1)}
                if changed is not None and (cls,slot)==("paladin","head"):
                    row[changed[0]]=changed[1]
                sparse.append(row)
                items.append({"ID":iid,"ClassID":4,
                              "SubclassID":physical.FAMILY[cls],
                              "InventoryType":inventory[slot]})
        self._write_csv("ItemSparse",sparse)
        self._write_csv("Item",items)
        self.verified={}
        for name in ("Item","ItemSparse"):
            content=(self.wago/(name+".csv")).read_bytes()
            self.verified[name]={
                "sha256":hashlib.sha256(content).hexdigest(),
                "bytes":len(content)}
        (self.wago/"receipt.json").write_text(json.dumps({
            "build":BUILD,"locale":"enUS",
            "tables":{name:{**record,
                "source_url":"https://wago.tools/db2/"+name+"/csv?build="+
                    BUILD+"&locale=enUS"}
                for name,record in self.verified.items()}}),encoding="utf8")

    def collect(self):
        return stage.collect(
            stage_root=self.root,wago_folder=self.wago,build=BUILD,
            tier_bridge=self.physical_source,first_party=self.exact_source,
            selected_tier=self.selected,
            verified_wago_tables=self.verified)

    def test_original_v191_tier_compiles_from_actual_65_physical_rows(self):
        one=self.collect()
        self.assertEqual(one["source_stage"]["status"],"EXECUTED_AND_SEALED")
        self.assertEqual(one["status"],stage.CANDIDATE_STATUS)
        self.assertFalse(one["season_membership_verified"])
        doc=json.loads(pathlib.Path(one["candidate_path"]).read_text("utf8"))
        self.assertEqual(doc["schema"],physical.SCHEMA)
        self.assertEqual(doc["item_count"],65)
        self.assertEqual(len(doc["classes"]),13)
        self.assertEqual(doc["evidence"]["publisher_tier_names_verified"],False)
        self.assertFalse(doc["season_membership_verified"])
        self.assertFalse(doc["environment_ready"])
        self.assertEqual(doc["classes"]["paladin"]["names"]["head"],
                         "Observed paladin head")
        # Original v191 (not copied optimizer) accepts the source fields.
        gear={"schema":"v167_product_season_gear_db_v1",
              "season_build":BUILD,
              "expansion_id":self.physical["expansion_id"],
              "item_count":0,"items":[]}
        rev="e"*40
        effects={"schema":"v189_pinned_simc_effect_registration_candidates_v1",
                 "auto_promote_to_user_ui":False,
                 "source":{"commit":rev,"sha256":"f"*64},
                 "candidates":{"food":[],"potion":[],
                               "embellishment_or_darkmoon":[]}}
        consum={"schema":"v190_same_build_consumable_item_candidates_v1",
                "automatic_ui_promotion":False,
                "source":{"wago_snapshot_build":BUILD,
                          "simc_revision":rev,
                          "simc_registration_sha256":"f"*64},
                "items":[]}
        generated={name:{"source_build":BUILD,"declared_rows":0,
                         "rows":[],"sha256":"0"*64}
                   for name in compiler.GENERATED}
        combined=compiler.compile_catalog(
            gear,doc,None,effects,consum,generated,event="season_change")
        self.assertEqual(combined["tier"]["piece_count"],65)
        self.assertEqual(combined["tier"]["item_ids"]["paladin"]["head"],
                         doc["classes"]["paladin"]["pieces"]["head"])
        self.assertFalse(combined["environment_ready"])
        self.assertIsNone(combined["B"])

    def test_v217_reuses_exact_same_source_with_no_db2_scan(self):
        first=self.collect()
        with mock.patch.object(stage.tier,"rows",
                               side_effect=AssertionError("CSV_RESCAN_FORBIDDEN")):
            again=self.collect()
        self.assertEqual(first["source_stage"]["status"],"EXECUTED_AND_SEALED")
        self.assertEqual(again["source_stage"]["status"],"REUSED_VERIFIED")
        self.assertEqual(again["source_stage"]["receipt_writes"],0)
        self.assertEqual(again["network_calls_by_stage"],0)
        self.assertFalse(again["environment_ready"])

    def test_v274_reads_new_sealed_tier_instead_of_raw_v251(self):
        row=self.collect()
        source={"schema":"v216_fresh_source_stage_v1",
                "expected_game_build":BUILD,
                "snapshot_receipt_path":str(self.wago/"receipt.json"),
                "fresh_compiler_tier_source":row,
                "fresh_tier":self.physical_source}
        result=wiring.discover(source)
        self.assertIn("TIER_V168",result["available"])
        self.assertNotIn("TIER_V168",result["missing"])
        self.assertIn("GEAR_V167",result["missing"])
        self.assertFalse(result["environment_ready"])

    def test_v161_url_metadata_does_not_break_real_v217_sha_and_size_reuse(self):
        # The mock Wago v161 record has a source_url, while original v217
        # verifies only bytes+sha. Live source reuse must accept that exact
        # original contract, without rehashing large CSV bytes.
        self.assertEqual(self.collect()["status"],stage.CANDIDATE_STATUS)
        receipt_path=self.wago/"receipt.json"
        receipt=json.loads(receipt_path.read_text("utf8"))
        receipt["tables"]["Item"]["sha256"]="0"*64
        receipt_path.write_text(json.dumps(receipt),encoding="utf8")
        bad=self.collect()
        # Already sealed v217 candidate may reuse unchanged results even
        # if external receipt is edited afterward. Require clean stage for
        # testing the underlying physical_roster source identity directly.
        with self.assertRaisesRegex(
            stage.TierCompilerSourceBlocked,
            "V276_WAGO_ALREADY_SEALED_SOURCE_IDENTITY_REQUIRED"):
            stage.physical_roster(
                physical=self.physical,matched=self.exact,
                selected=self.selected,build=BUILD,wago_folder=self.wago,
                verified_wago_tables=self.verified)

    def test_sparse_wrong_set_or_simc_drift_retains_pending_not_ready(self):
        self._write_db2(changed=("ItemSet",999999))
        result=self.collect()
        self.assertEqual(result["status"],"COMPILER_TIER_PHYSICAL_SOURCE_PENDING")
        self.assertIn("V276_SPARSE_SLOT_SET_CLASS_OR_EXPANSION_DRIFT",
                      result["reason"])
        self.assertFalse(result["environment_ready"])
        self.assertIsNone(result["candidate_path"])

    def test_incomplete_proof_never_scans_or_triggers_fetch(self):
        with mock.patch.object(stage.tier,"rows",
                               side_effect=AssertionError("NO_SOURCE_NO_SCAN")):
            pending=stage.collect(
                stage_root=self.root,wago_folder=self.wago,build=BUILD,
                tier_bridge={},first_party=self.exact_source,
                selected_tier=self.selected,
                verified_wago_tables=self.verified)
        self.assertEqual(pending["status"],"COMPILER_TIER_PHYSICAL_SOURCE_PENDING")
        self.assertEqual(pending["network_calls_by_stage"],0)
        self.assertFalse(pending["environment_ready"])

if __name__=="__main__":
    unittest.main()
