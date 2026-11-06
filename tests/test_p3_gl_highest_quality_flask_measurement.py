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
    def test_invalid_quality_fails(self):
        with self.assertRaisesRegex(v.EnvironmentBuildBlocked,
                                    "V216_F_SOURCE_QUALITY_ROW_INVALID"):
            v._prioritize_highest_source_quality_F([self.row(1,"bad",None)])

if __name__=="__main__":
    unittest.main()
