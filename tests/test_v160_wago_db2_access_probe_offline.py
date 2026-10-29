"""No HTTP: verify strict schema, no old item input, fail-closed parsing."""
import json
import pathlib
import sys
import unittest
from urllib.error import HTTPError
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v160_wago_db2_access_probe as p

class WagoDB2Probe(unittest.TestCase):
    def test_valid_csv_header_is_required(self):
        raw=b"ID,CraftedItemID,Extra\n3,239001,stuff\n"
        r=p.csv_preview(raw,("CraftedItemID",))
        self.assertEqual(r["status"],"CSV_COLUMNS_CONFIRMED")
        self.assertEqual(r["preview_rows"],1)
        self.assertEqual(p.csv_preview(b"<html>Oops</html>",("ID",))
                         ["status"],"REQUIRED_COLUMNS_MISSING")
    def test_missing_mandatory_fields(self):
        self.assertEqual(p.csv_preview(b"ID,Name_lang\n42,Test\n",
                                      ("JournalEncounterID","ItemID"))
                         ["missing_columns"],
                         ["JournalEncounterID","ItemID"])
    def test_no_prior_id_or_implicit_loot_catalog(self):
        self.assertEqual(len(p.TABLES),9)
        self.assertIn("CraftingData",p.TABLES)
        self.assertIn("JournalEncounterItem",p.TABLES)
        self.assertNotIn("delve-loot.json",json.dumps(p.TABLES))
    def test_transport_validates_origin_and_limits(self):
        class R:
            status=200
            headers={"Content-Type":"text/csv; charset=utf-8"}
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):
                assert n<=32768
                return b"ID,CraftedItemID\n1,239656\n"
        u=[]
        def transport(req,timeout):
            u.append(req.full_url)
            return R()
        r=p.fetch_header("CraftingData",("ID","CraftedItemID"),
                         transport=transport)
        self.assertEqual(r["status"],"CSV_COLUMNS_CONFIRMED")
        self.assertIn("12.1.5.70575",u[0])
        with self.assertRaises(ValueError):
            p.fetch_header("../else",("ID",),transport=transport)
    def test_all_requests_result_no_fake_success(self):
        class R:
            status=403
            headers={}
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return b"Forbidden"
        d=p.run(transport=lambda req,timeout:R())
        self.assertEqual(d["confirmed_csv_tables"],0)
        self.assertFalse(d["full_tables_downloaded"])
        self.assertFalse(d["delve_loot_pool_extracted"])
        self.assertEqual(d["simc_native_calls"],0)
if __name__=="__main__":unittest.main()
