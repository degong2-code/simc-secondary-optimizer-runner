"""v047 bounded full-source collector scope and safety regression."""
import copy,json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runner'))
import v047_full_scope_collector as v
import v046_static_item_cache as c

MANIFEST=ROOT/"integration_probes/requests/v047_full_scope_manifest.json"

class V047Scope(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=v.parse_manifest(MANIFEST)
    def test_census_all_cases_and_scope(self):
        m=self.manifest
        self.assertEqual(len(m["items"]),126)
        self.assertEqual(m["selected_unique_count"],126)
        self.assertEqual(len(m["target_level_candidates"]),14)
        self.assertEqual(m["possible_variant_pairs"],1764)
        self.assertFalse(m["complete_season_catalog_attested"])
        self.assertFalse(m["all_crafted_ids_attested"])
    def test_bounded_slicing(self):
        cases,size=v.candidates(self.manifest,[334],0,7)
        self.assertEqual(size,126)
        self.assertEqual(len(cases),7)
        self.assertTrue(all(level==334 for item,level in cases))
        with self.assertRaisesRegex(c.CacheBlocked,"BOUNDED_CALLS_REQUIRED"):
            v.candidates(self.manifest,[334],0,1000)
    def test_selected_roles(self):
        observed={k:sum(k in x["category_roles"] for x in self.manifest["items"])
            for k in ["ALL_MASTER_TRINKETS","SPELL_BEARING_CANDIDATE_REQUIRES_SIMC_CHECK",
                      "PROVISIONAL_ARMOR_REPRESENTATIVE","PATCH_1215_DELTA","CRAFTED_KNOWN_ONLY"]}
        self.assertEqual(observed,{
            "ALL_MASTER_TRINKETS":60,
            "SPELL_BEARING_CANDIDATE_REQUIRES_SIMC_CHECK":80,
            "PROVISIONAL_ARMOR_REPRESENTATIVE":34,
            "PATCH_1215_DELTA":10,
            "CRAFTED_KNOWN_ONLY":2})
    def test_profile_preserves_unrelated_equipment(self):
        import pilot
        base,_=pilot.source()
        cand=next(x for x in self.manifest["items"] if x["slot"]=="HEAD")
        path=pathlib.Path("/tmp/sample.json")
        new=v.make_native_profile(base,cand,334,path)
        self.assertEqual(sum(x.startswith("json2=") for x in new.splitlines()),1)
        self.assertEqual(sum(x.startswith("head=") for x in new.splitlines()),1)
        self.assertIn("head=v047_stat_probe_",new)
        self.assertNotIn("gear_crit_rating=",new)
        self.assertIn("item_db_source=local",new)
        self.assertIn("iterations=1",new)
        self.assertIn("max_time=2",new)
        self.assertEqual([x for x in new.splitlines() if x.startswith("trinket2=")],
                         [x for x in base.splitlines() if x.startswith("trinket2=")])
    def test_unsupported_slot_fail_closed(self):
        import pilot
        base,_=pilot.source()
        bad={"item_id":22,"slot":"SHIELD","name":"Test"}
        with self.assertRaisesRegex(c.CacheBlocked,"SLOT_HAS_NO_VALIDATED_SIMC_MAPPING"):
            v.make_native_profile(base,bad,334,pathlib.Path('/tmp/e.json'))
    def test_crafted_option_explicit(self):
        import pilot
        base,_=pilot.source()
        craft=next(x for x in self.manifest["items"] if x["item_id"]==239648)
        raw=v.make_native_profile(base,craft,334,pathlib.Path('/tmp/e.json'))
        self.assertIn("wrists=v047_stat_probe_239648,id=239648,ilevel=334,source=local,crafted_stats=49/36",raw)
    def test_native_audit_rejects_wrong_id(self):
        data={"report_version":"2.0.0","git_revision":"7bc10711b5",
              "sim":{"players":[{"gear":{"head":{"encoded_item":"bad,id=90,ilevel=334,source=local",
                       "ilevel":334}}}]}}
        with self.assertRaisesRegex(c.CacheBlocked,"NATIVE_ITEM_ID_OR_ILVL_DRIFT"):
            v.audit_variant(json.dumps(data).encode(),{"item_id":91,"slot":"HEAD"},334)
    def test_import_existing_catalog_schema(self):
        obj=json.loads((ROOT/"integration_probes/catalog/v047_catalog_import_407_rows.json").read_text())
        self.assertEqual(len(obj["items"]),407)
        rows=c.catalog_rows(json.dumps(obj).encode())
        self.assertEqual(len(rows),407)
        ca=c.empty_cache();r=c.merge_catalog(ca,rows)
        self.assertEqual(r["source_rows"],407)
        self.assertEqual(r["stats_populated_by_catalog"],0)
        self.assertEqual(len(ca["variants"]),0)
    def test_no_silent_g_catalog(self):
        self.assertFalse(self.manifest["complete_season_catalog_attested"])
        self.assertEqual(self.manifest["lookup_policy"]["wequip_scaled_stats"],"NOT_USED_FOR_CACHE")

if __name__=="__main__":unittest.main()
