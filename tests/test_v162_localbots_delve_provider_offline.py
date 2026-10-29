"""Localbots source is an external 2026+ provider, not a seeded historic DB."""
import json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v162_localbots_delve_provider as provider

class LocalbotsDelveImport(unittest.TestCase):
    def samples(self):
        source={"_comment":"New expansion from external publisher","items":[
            {"id":900010,"name":"Sunscale Shield"},
            {"name":"Shimmering Crest"},
            {"name":"Lost Trinket"}]}
        csv="ID,Display_lang,OverallQualityID,InventoryType,ExpansionID\n"
        csv+="900010,Sunscale Shield,4,14,15\n"
        csv+="900020,Shimmering Crest,3,12,15\n"
        csv+="900021,Shimmering Crest,4,12,15\n"
        csv+="900022,Shimmering Crest,4,12,15\n"
        return json.dumps(source).encode(),csv.encode()
    def test_another_expansion_no_79_gate(self):
        s,d=self.samples()
        o=provider.assemble(s,d,build="15.0.0.90000",expansion_id=15)
        self.assertEqual(o["names_in_source"],3)
        self.assertEqual(o["resolved_count"],2)
        self.assertEqual(o["unresolved_count"],1)
        self.assertEqual(o["items"][1]["item_id"],900022)
        self.assertFalse(o["prior_wequip_or_past_item_db_used"])
        self.assertEqual(o["simc_native_calls"],0)
    def test_id_name_mismatch_not_silently_mapped(self):
        s,d=self.samples()
        bad=d.replace(b"Sunscale Shield",b"Wrong Item Name")
        o=provider.assemble(s,bad,build="x",expansion_id=15)
        self.assertEqual(o["unresolved_count"],2)
        self.assertEqual(o["unresolved"][0]["reason"],
                         "DB2_ID_NAME_OR_EXPANSION_MISMATCH")
    def test_missing_source_and_duplicates_are_blocked(self):
        s,d=self.samples()
        v=json.loads(s)
        v["items"].append(dict(v["items"][0]))
        with self.assertRaises(provider.SourceBlocked):
            provider.assemble(json.dumps(v).encode(),d,build="x")
    def test_expansion_filter_and_provenance(self):
        s,d=self.samples()
        o=provider.assemble(s,d,build="15.0.0.90000",expansion_id=11)
        self.assertEqual(o["resolved_count"],0)
        self.assertEqual(o["unresolved_count"],3)
        self.assertEqual(o["source_provider"],
                         "Localbots / balovich-matje/localbots")
    def test_csv_required_fields(self):
        s,d=self.samples()
        with self.assertRaises(provider.SourceBlocked):
            provider.assemble(s,b"ID,Name\n1,X\n",build="test")
if __name__=="__main__":unittest.main()
