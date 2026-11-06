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
    def test_public_season_ui_distinguishes_source_F_from_official_F(self):
        root=pathlib.Path(__file__).resolve().parents[1]/"runner"/"webui"
        html=(root/"index.html").read_text(encoding="utf8")
        js=(root/"app.js").read_text(encoding="utf8")
        self.assertIn("시즌 기본 영약 F 자동 선정",html)
        self.assertIn("전문화별 최적 영약 아님",html)
        self.assertIn("source.automatic_default_F_source_selection_unadmitted",js)
        self.assertIn("original_J_F_verified_components_not_full_environment?.F",js)
        self.assertIn("환경 정식 등록 전",js)
        self.assertIn("최대 2회 측정",js)

    def test_empty_source_is_pending_not_zero_F(self):
        p=v._auto_default_F_from_sealed_v281_worklist(self.plan([]))
        self.assertIn("AUTO_F_SEALED_PHYSICAL_WORKLIST_PENDING",p["requires"])
        self.assertIsNone(p["selected_physical_items_unadmitted"])
if __name__=="__main__":
    unittest.main()
