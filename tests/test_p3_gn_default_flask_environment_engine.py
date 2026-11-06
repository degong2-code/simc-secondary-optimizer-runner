"""P3-GN: season F automatic source selection, zero Native/source requests."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"runner"))
import v216_environment_build_coordinator as v

class FAutomaticSourceChoice(unittest.TestCase):
    def row(self,i,token,rank):
        return {"physical_item_id":i,"simc_input_token":token,
                "crafting_quality":rank}
    def plan(self,rows):
        return {"status":"MEASURABLE_PHYSICAL_F_O_CANDIDATES_UNADMITTED",
                "flask":rows,"oil":[]}
    def test_multifamily_chooses_one_highest_source_quality_before_native(self):
        raw=[self.row(1001,"flask_zenith_1",1),
             self.row(2002,"flask_wind_2",2),
             self.row(1003,"flask_zenith_3",3),
             self.row(2001,"flask_wind_1",1)]
        before=list(raw)
        v1=v._auto_default_F_from_sealed_v281_worklist(self.plan(raw))
        v2=v._auto_default_F_from_sealed_v281_worklist(
            self.plan(list(reversed(raw))))
        self.assertEqual(v1["selected_physical_items_unadmitted"],
                         {"flask_item_id":2002,"oil_item_ids_by_hand":{}})
        self.assertEqual(v1["selected_physical_items_unadmitted"],
                         v2["selected_physical_items_unadmitted"])
        self.assertEqual(raw,before)
        self.assertFalse(v1["environment_ready"])
        self.assertTrue(v1["not_spec_default_or_stat_optimization"])
        self.assertEqual(v1["new_native_calls"],0)
    def test_tie_only_family_does_not_guess_physical_id(self):
        selected=v._auto_default_F_from_sealed_v281_worklist(self.plan([
            self.row(1,"flask_same_3",3),self.row(2,"flask_same_3",3)]))
        self.assertIsNone(selected["selected_physical_items_unadmitted"])
        self.assertIn("AUTO_F_HIGHEST_SOURCE_QUALITY_UNAMBIGUOUS_ITEM_PENDING",
                      selected["requires"])
    def test_unknown_family_name_does_not_get_assumed_quality(self):
        selected=v._auto_default_F_from_sealed_v281_worklist(self.plan([
            self.row(1,"unlabelled",3)]))
        self.assertIsNone(selected["selected_physical_items_unadmitted"])
    def test_empty_source_is_pending_not_zero_F(self):
        p=v._auto_default_F_from_sealed_v281_worklist(self.plan([]))
        self.assertIn("AUTO_F_SEALED_PHYSICAL_WORKLIST_PENDING",p["requires"])
        self.assertIsNone(p["selected_physical_items_unadmitted"])
if __name__=="__main__":
    unittest.main()
