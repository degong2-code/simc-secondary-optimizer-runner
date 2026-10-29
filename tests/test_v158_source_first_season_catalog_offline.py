"""Fresh season catalog construction with ZERO existing item DB."""
import json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v158_source_first_season_catalog as catalog

class EmptySeasonAssembly(unittest.TestCase):
    def samples(self):
        return [
            {"schema":"v155_season_discovery_provider_probe_v1",
             "blizzard":{"endpoints":{"keystone_season_index":{
                 "data":{"current_season_id":987}}}}},
            {"schema":"v154_source_first_blizzard_encounter_loot_v2",
             "source_authority":"BLIZZARD_API_RESPONSE",
             "encounter_sources":[
                 {"encounter_id":41,"instance_id":7,"kind":"raid",
                  "observed_item_ids":[900001,900002]},
                 {"encounter_id":42,"instance_id":8,"kind":"mplus",
                  "observed_item_ids":[900002]},
                 {"encounter_id":43,"instance_id":9,"kind":"delve",
                  "observed_item_ids":None}]},
            {"schema":"v157_source_first_blizzard_profession_recipes_v2",
             "profession_id":197,"skill_tier_id":2918,
             "discovered_recipe_references":[
                 {"id":801,"name":"First Recipe"},
                 {"id":802,"name":"Second Recipe"}],
             "sampled_recipe_details":[
                 {"recipe_id":801,"crafted_output_item_ids":[900002,900003]},
                 {"recipe_id":802,"crafted_output_item_ids":None}]}
        ]

    def test_zero_seed_catalog_deduplicates_only_provider_item_ids(self):
        result=catalog.ingest(self.samples())
        self.assertEqual(result["season_data"]["blizzard_keystone_season_id"],987)
        self.assertEqual(result["item_ids"],[900001,900002,900003])
        self.assertEqual(result["observed_unique_item_ids"],3)
        self.assertEqual(len(result["items"][1]["acquisition_sources"]),3)
        self.assertEqual(len(result["unresolved_provider_fields"]),2)
        self.assertFalse(result["legacy_comparison_performed"])
        self.assertFalse(result["old_item_catalog_imported"])
        self.assertFalse(result["full_season_completeness_confirmed"])
        self.assertFalse(result["special_effects_classified"])

    def test_historical_db_is_not_needed_for_cli(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            files=[]
            for i,report in enumerate(self.samples()):
                f=root/("source%d.json"%i)
                f.write_text(json.dumps(report))
                files.extend(["--report",str(f)])
            output=root/"new-season.json"
            code=catalog.main(files+["--out",str(output)])
            self.assertEqual(code,0)
            report=json.loads(output.read_text())
            self.assertEqual(report["item_ids"],[900001,900002,900003])
            self.assertNotIn("matched_existing",output.read_text())
            self.assertEqual(report["simc_native_calls"],0)

    def test_same_inputs_produce_same_catalog_and_unknowns_are_not_empty(self):
        self.assertEqual(catalog.ingest(self.samples()),
                         catalog.ingest(self.samples()))
        self.assertNotEqual(catalog.ingest(self.samples())
                            ["unresolved_provider_fields"],[])
        data=self.samples()
        data[1]["encounter_sources"][2]["observed_item_ids"]=[]
        newer=catalog.ingest(data)
        self.assertEqual(len(newer["unresolved_provider_fields"]),1)

    def test_invalid_recipe_id_and_unsupported_report_fail_closed(self):
        data=self.samples()
        data[-1]["sampled_recipe_details"][0]["recipe_id"]=999
        with self.assertRaises(catalog.CatalogBlocked):
            catalog.ingest(data)
        with self.assertRaises(catalog.CatalogBlocked):
            catalog.ingest([{"schema":"v047_wequip_snapshot_identity_census_v1"}])

    def test_real_v156_shape_is_ingested_without_reference_data(self):
        record={"schema":"v156_one_blizzard_journal_raid_loot_smoke_v1",
                "status":"BOUNDED_JOURNAL_SMOKE_COMPLETE",
                "raid":{"journal_instance_id":10},
                "boss":{"journal_encounter_id":11},
                "loot":{"status":"EXPLICIT_JOURNAL_LOOT_ITEMS",
                        "observed_item_ids":[910000,910001]}}
        result=catalog.ingest([record])
        self.assertEqual(result["item_ids"],[910000,910001])
        self.assertEqual(result["items"][0]["acquisition_sources"][0]
                         ["encounter_id"],11)

if __name__=="__main__":
    unittest.main()
