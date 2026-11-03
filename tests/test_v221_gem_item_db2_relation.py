"""v221: pinned DB2 Item/ItemSparse to SimC gem property keys, zero Native."""
import copy
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v213_source_to_catalog as source_bridge
import v221_gem_item_db2_relation as joiner
import v220_catalog_auto_admission as admission
from tests.test_v213_source_to_catalog import SourceToCatalogTests


class GemPropertyRelationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_builder=SourceToCatalogTests()
        cls.source_builder.setUpClass()

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder=pathlib.Path(self.tmp.name)
        season,classification=self.source_builder.build_inputs()
        season["gem_properties"]["source_records"]=[
            {"gem_property_id":12000+i,
             "enchant_id":20000+i,
             "color_mask":2,"minimum_ilevel":0}
            for i in range(2409)]
        self.catalog=source_bridge.compile_catalog(
            season,"a"*64,classification,"b"*64)
        self.files={
            "Item":"ID,ClassID,SubclassID\n240001,3,0\n240002,3,0\n240003,4,0\n240004,3,0\n",
            "ItemSparse":
                "ID,ExpansionID,Display_lang,Gem_properties\n"
                "240001,11,Gem One,12000\n"
                "240002,11,Gem Two,12000\n"
                "240003,11,Armor Not Gem,12001\n"
                "240004,10,Old Expansion,12002\n",
        }
        self.write_snapshot()

    def write_snapshot(self):
        tables={}
        for name,content in self.files.items():
            raw=content.encode("utf8")
            (self.folder/(name+".csv")).write_bytes(raw)
            tables[name]={"bytes":len(raw),
                          "sha256":hashlib.sha256(raw).hexdigest()}
        self.receipt={
            "schema":"v161_wago_zero_seed_csv_snapshot_v1",
            "status":"ALL_CSV_DOWNLOADED_NOT_YET_INTERPRETED",
            "build":"12.1.5.70575","locale":"enUS",
            "source":"wago.tools/db2","tables":tables}
        (self.folder/"receipt.json").write_text(
            json.dumps(self.receipt),encoding="utf8")

    def test_exact_two_items_may_share_one_gem_property_no_admission(self):
        out=joiner.join(self.catalog,self.folder)
        self.assertEqual(out["status"],
                         "SOURCE_ITEM_PROPERTY_LINKS_ONLY_NOT_USER_ADMITTED")
        self.assertEqual(out["exact_link_count"],2)
        self.assertEqual([r["item_id"] for r in out["joins"]],
                         [240001,240002])
        self.assertEqual([r["gem_property_id"] for r in out["joins"]],
                         [12000,12000])
        self.assertEqual(out["joins"][0]["enchant_id"],20000)
        self.assertEqual(out["joins"][0]["socket_eligibility"],
                         "NOT_YET_VERIFIED")
        self.assertFalse(out["automatic_ui_promotion"])
        self.assertFalse(out["historical_cache_modified"])
        self.assertEqual(out["simc_native_calls"],0)
        self.assertEqual(out["network_calls"],0)
        self.assertFalse(any(r["ui_selectable"] for r in out["joins"]))
        candidate={
            "kind":"gem","exact_id":out["joins"][0]["item_id"],
            "simc_token":"not_yet_verified",
            "slot":"socket1","slot_status":"PENDING_EXACT_SOCKET",
            "game_build":out["game_build"],
            "simc_revision":out["simc_revision"],
            "catalog_sha256":out["v213_manifest_sha256"],
        }
        decision=admission.decide(candidate)
        self.assertFalse(decision["eligible"])
        self.assertIn("EXACT_PHYSICAL_SLOT_OR_HAND_RELATION_NOT_VERIFIED",
                      decision["missing"])

    def test_reuse_verified_snapshot_pair_without_duplicate_hash(self):
        proof=joiner._verify_db2(self.folder,self.catalog["game_build"])
        with mock.patch.object(joiner,"_sha_file",
                               side_effect=AssertionError("duplicate SHA")):
            result=joiner.join(self.catalog,self.folder,verified_tables=proof)
        self.assertEqual(result["exact_link_count"],2)
        self.assertFalse(result["automatic_ui_promotion"])
        bad=copy.deepcopy(proof)
        bad["ItemSparse"]["sha256"]="0"*64
        with self.assertRaisesRegex(joiner.GemJoinBlocked,
                                    "V217_VERIFIED_TABLE_PROVENANCE_MISMATCH"):
            joiner.join(self.catalog,self.folder,verified_tables=bad)

    def test_simc_generated_build_difference_is_pending_not_false_join(self):
        changed=copy.deepcopy(self.catalog)
        changed["source_provenance"]["v191"]["simc_generated_sources"][
            "gem_property"]["source_build"]="12.1.5.70448"
        body={k:v for k,v in changed.items() if k!="manifest_sha256"}
        changed["manifest_sha256"]=source_bridge.sha(
            source_bridge.canonical(body).encode("utf8"))
        out=joiner.join(changed,self.folder)
        self.assertEqual(out["exact_link_count"],0)
        self.assertEqual(out["joins"],[])
        self.assertEqual(out["status"],
                         "PENDING_GENERATED_SIMC_DBC_AND_DB2_BUILD_MISMATCH")

    def test_receipt_hash_and_build_drift_fail_closed(self):
        path=self.folder/"ItemSparse.csv"
        path.write_bytes(path.read_bytes()+b"\n")
        with self.assertRaisesRegex(joiner.GemJoinBlocked,"DB2_TABLE_SHA"):
            joiner.join(self.catalog,self.folder)
        self.write_snapshot()
        self.receipt["build"]="12.1.5.70448"
        (self.folder/"receipt.json").write_text(json.dumps(self.receipt))
        with self.assertRaisesRegex(joiner.GemJoinBlocked,"DB2_SNAPSHOT_BUILD"):
            joiner.join(self.catalog,self.folder)

    def test_missing_foreign_key_column_or_duplicate_item_fails_closed(self):
        self.files["ItemSparse"]=self.files["ItemSparse"].replace(
            "Gem_properties","UnknownColumn")
        self.write_snapshot()
        with self.assertRaisesRegex(joiner.GemJoinBlocked,"DB2_REQUIRED_COLUMNS"):
            joiner.join(self.catalog,self.folder)
        self.files["ItemSparse"]=self.files["ItemSparse"].replace(
            "UnknownColumn","Gem_properties")
        self.files["Item"]+="240001,3,0\n"
        self.write_snapshot()
        with self.assertRaisesRegex(joiner.GemJoinBlocked,
                                    "DB2_DUPLICATE_GEM_ITEM_ID"):
            joiner.join(self.catalog,self.folder)

    def test_conflicting_source_key_blocks_without_partial_publication(self):
        changed=copy.deepcopy(self.catalog)
        records=changed["catalog"]["gem_properties"]["source_records"]
        records[1]={**records[0],"enchant_id":33000}
        body={k:v for k,v in changed.items() if k!="manifest_sha256"}
        changed["manifest_sha256"]=source_bridge.sha(
            source_bridge.canonical(body).encode("utf8"))
        with self.assertRaisesRegex(joiner.GemJoinBlocked,
                                    "V213_SOURCE_CATALOG_INVALID|V213_GEM_PROPERTY_KEY_CONFLICT"):
            joiner.join(changed,self.folder)

    def test_missing_retained_source_keys_never_inferred(self):
        old=copy.deepcopy(self.catalog)
        old["catalog"]["gem_properties"].pop("source_records")
        old["source_join_audit"]=source_bridge._source_join_audit(old["catalog"])
        body={k:v for k,v in old.items() if k!="manifest_sha256"}
        old["manifest_sha256"]=source_bridge.sha(
            source_bridge.canonical(body).encode("utf8"))
        with self.assertRaisesRegex(joiner.GemJoinBlocked,
                                    "V213_GEM_SOURCE_KEYS_NOT_RETAINED"):
            joiner.join(old,self.folder)


if __name__=="__main__":
    unittest.main()
