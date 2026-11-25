"""P3-GL: highest-quality source F worklist, no new Native."""
import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"runner"))
import v216_environment_build_coordinator as v

class FPriority(unittest.TestCase):
    def row(self,id,name,quality):
        return {"physical_item_id":id,"simc_input_token":name,
                "crafting_quality":quality}
    def test_highest_quality_each_distinct_effect(self):
        src=[self.row(11,"haste_flask_1",1),
             self.row(21,"mastery_flask_2",2),
             self.row(12,"haste_flask_2",2),
             self.row(22,"mastery_flask_1",1),
             self.row(31,"crit_flask_2",2)]
        r=v._prioritize_highest_source_quality_F(src)
        self.assertEqual([x["physical_item_id"] for x in r["selected"]],[21,12,31])
        self.assertEqual(r["all_source_candidates"],5)
        self.assertEqual(r["deferred_lower_source_qualities"],2)
        self.assertEqual(r["distinct_source_token_families"],3)
        self.assertFalse(r["effect_equivalence_verified"])
        self.assertFalse(r["quality_and_use_admitted"])
        self.assertEqual(r["new_native_calls"],0)
    def test_ambiguous_names_and_ties_remain(self):
        src=[self.row(1,"unknown",0),self.row(2,"unknown",0),
             self.row(3,"token_2",2),self.row(4,"token_2",2)]
        r=v._prioritize_highest_source_quality_F(src)
        self.assertEqual([x["physical_item_id"] for x in r["selected"]],[1,2,3,4])
    def test_v758_observed_distinct_use_ids_do_not_merge(self):
        stats=v.season_budget_contract.STATS
        def row(i,rank,spell,rating):
            return {**self.row(i,"same_name_"+str(rank),rank),
                "flask_use_source_scope":{"on_use_spell_ids":[spell]},
                "status":"SIMC_NATIVE_STATIC_NUMBER_SOURCE_ONLY",
                "static_CHMV_vector_unadmitted":{
                    s:rating if s==stats[0] else 0 for s in stats},
                "rating_candidate_unadmitted":rating}
        a=row(1,1,123,100);b=row(2,2,456,150)
        def groups(rows):
            return v._zero_history_quality_weapon_candidate_join(
                numeric={"status":"PHYSICAL_ITEM_SIMC_F_O_CANDIDATES_UNADMITTED",
                         "flask":rows,"oil":[]},weapon_source=None,
                game_build="12.2.0.99999",simc_revision="a"*40
                )["flask_quality_groups_observed_unadmitted"]
        separate=groups([a,b])
        self.assertEqual(len(separate),2)
        self.assertEqual({g["highest_observed_quality_item_id_unadmitted"]
                          for g in separate},{1,2})
        same=groups([a,{**b,"flask_use_source_scope":a["flask_use_source_scope"]}])
        self.assertEqual(len(same),1)
        self.assertEqual(same[0]["highest_observed_quality_item_id_unadmitted"],2)
        self.assertFalse(same[0]["user_selectable"])

    def test_invalid_quality_fails(self):
        with self.assertRaisesRegex(v.EnvironmentBuildBlocked,
                                    "V216_F_SOURCE_QUALITY_ROW_INVALID"):
            v._prioritize_highest_source_quality_F([self.row(1,"bad",None)])

if __name__=="__main__":
    unittest.main()
