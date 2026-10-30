"""v190 deterministic snapshot join without network, Native or UI changes."""
import hashlib,json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v190_consumable_item_snapshot_join as join

SOURCE={"schema":"v189_pinned_simc_effect_registration_candidates_v1",
 "source":{"commit":"7bc10711b5a4514066fa402ca0a71c9ba4b7c9dd",
           "sha256":"ab"*32},
 "counts":{"food_handler_registrations":37,
           "potion_handler_registrations":5},
 "auto_promote_to_user_ui":False}
ITEMS="""ID,ClassID,SubclassID,InventoryType
101,0,5,0
102,0,1,0
103,4,1,1
104,0,1,0
"""
SPARSE="""ID,ExpansionID,Display_lang
101,11,Fresh Feast
102,11,New Potion
103,11,Normal Armor
104,10,Legacy Potion
"""
def prepare(root):
    table={}
    for name,data in (("Item",ITEMS),("ItemSparse",SPARSE)):
        p=root/(name+".csv");p.write_text(data,encoding="utf8")
        table[name]={"bytes":p.stat().st_size,
                     "sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
    receipt={"schema":"v161_wago_zero_seed_csv_snapshot_v1",
             "status":"ALL_CSV_DOWNLOADED_NOT_YET_INTERPRETED",
             "locale":"enUS","build":"12.1.5.70575",
             "tables":table}
    (root/"receipt.json").write_text(json.dumps(receipt))
class ConsumableDb2Join(unittest.TestCase):
    def test_real_class_subclass_and_expansion_filter_without_simc_claims(self):
        with tempfile.TemporaryDirectory() as td:
            out=join.build(SOURCE,pathlib.Path(td) if False else self.create(td),
               expected_build="12.1.5.70575",expansion_id=11)
            self.assertEqual(out["counts"],{
               "food_items":1,"potion_items":1,
               "simc_effect_food_registrations":37,
               "simc_effect_potion_registrations":5})
            self.assertEqual({x["item_id"] for x in out["items"]},{101,102})
            self.assertEqual({x["kind"] for x in out["items"]},{"food","potion"})
            self.assertTrue(all(x["ui_selectable"] is False for x in out["items"]))
            self.assertTrue(all(x["simc_dbc_presence"]=="NOT_CHECKED" for x in out["items"]))
            self.assertFalse(out["automatic_ui_promotion"])
            self.assertTrue(out["preserve_old_runtime_whitelist"])
            self.assertEqual(out["simc_native_calls"],0)
    def create(self,dirname):
        root=pathlib.Path(dirname);prepare(root);return root
    def test_tamper_or_version_mismatch_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root=self.create(td)
            with self.assertRaisesRegex(join.ConsumableJoinBlocked,
                                        "BUILD_OR_LOCALE_MISMATCH"):
                join.build(SOURCE,root,expected_build="12.1.5.99999",
                           expansion_id=11)
            (root/"Item.csv").write_text(ITEMS+"105,0,1,0\n")
            with self.assertRaisesRegex(join.ConsumableJoinBlocked,"TABLE_SHA_MISMATCH"):
                join.build(SOURCE,root,expected_build="12.1.5.70575",
                           expansion_id=11)
    def test_no_unverified_source_or_missing_columns_can_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root=self.create(td)
            invalid=dict(SOURCE,auto_promote_to_user_ui=True)
            with self.assertRaisesRegex(join.ConsumableJoinBlocked,"V189_SOURCE"):
                join.build(invalid,root,expected_build="12.1.5.70575",
                           expansion_id=11)
            (root/"Item.csv").write_text(ITEMS.replace("ClassID","BadClass"))
            table=json.loads((root/"receipt.json").read_text())
            table["tables"]["Item"]["sha256"]=join.sha_file(root/"Item.csv")
            table["tables"]["Item"]["bytes"]=(root/"Item.csv").stat().st_size
            (root/"receipt.json").write_text(json.dumps(table))
            with self.assertRaisesRegex(join.ConsumableJoinBlocked,"DB2_COLUMNS_MISSING"):
                join.build(SOURCE,root,expected_build="12.1.5.70575",
                           expansion_id=11)
if __name__=="__main__":unittest.main()
