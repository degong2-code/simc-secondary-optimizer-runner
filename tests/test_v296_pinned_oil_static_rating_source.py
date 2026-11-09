"""v296: stat values come from same-build unbuffed SimC DBC, not class buffs."""
import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v296_pinned_oil_static_rating_source as oil

REV="c20e2ad52e4c33711f74272309a5748125175fe8"
BUILD="12.1.5.70783"
FIXTURE=(
  "// Spell item enchantments, wow build "+BUILD+"\n"
  '{ 8052, 0, 0, 0, 0, 0, 0, 0, 0, '
  '{ 5, 5, 0 }, { 16, 16, 0 }, { 32, 36, 0 }, '
  '{ 0, 0, 0 }, 1237006, "Thalassian Phoenix Oil" },\n'
)
def selected(ident=8052):
    return {"kind":"temporary_enchant","physical_item_id":243734,
            "selected_hand":"main_hand","simc_input_token":
                "main_hand:thalassian_phoenix_oil",
            "simc_enchant_id":ident,"crafting_quality":2,
            "source_candidate_sha256":"a"*64,
            "source_stage_receipt_sha256":"b"*64}
class SeasonOilStaticSource(unittest.TestCase):
    def test_original_simc_raw_16_16_ignores_buffed_16_17(self):
        src=oil.extract(generated_text=FIXTURE,
                        game_build=BUILD,simc_revision=REV,
                        enchant_ids={8052})
        self.assertEqual(src["items"][0]["static_CHMV_vector"],{
            "crit_rating":16,"haste_rating":16,
            "mastery_rating":0,"versatility_rating":0})
        older={**selected(),"physical_item_source_stage_sha256":"b"*64,
               "physical_item_source_candidate_sha256":"a"*64,
               "buffed_CHMV_observation_unadmitted":{
                   "crit_rating":16,"haste_rating":17,
                   "mastery_rating":0,"versatility_rating":0}}
        joined=oil.project_source_oils(source=src,worklist={"oil":[selected()]},
               native_numeric={"status":
                  "PHYSICAL_ITEM_SIMC_F_O_CANDIDATES_UNADMITTED",
                  "flask":[],"oil":[older]})
        row=joined["oil"][0]
        self.assertEqual(row["rating_candidate_unadmitted"],{
            "crit_rating":16,"haste_rating":16,
            "mastery_rating":0,"versatility_rating":0})
        self.assertEqual(row["status"],"SIMC_RAW_STATIC_NUMBER_SOURCE_ONLY")
        self.assertTrue(row["buffed_snapshot_disagrees_with_raw_source"])
        self.assertFalse(row["source_admitted"])
        self.assertFalse(row["weapon_and_hand_applicability_verified"])
        self.assertIsNone(joined["O"])

    def test_unsupported_dynamic_or_scaling_never_becomes_O(self):
        modified=FIXTURE.replace("{ 5, 5, 0 }","{ 5, 3, 0 }")
        doc=oil.extract(generated_text=modified,game_build=BUILD,
                        simc_revision=REV,enchant_ids=[8052])
        self.assertIsNone(doc["items"][0]["static_CHMV_vector"])
        self.assertEqual(doc["items"][0]["status"],oil.PENDING)
        scaled=FIXTURE.replace("{ 0, 0, 0 }, 1237006",
                               "{ 1, 0, 0 }, 1237006")
        doc=oil.extract(generated_text=scaled,game_build=BUILD,
                        simc_revision=REV,enchant_ids=[8052])
        self.assertIsNone(doc["items"][0]["static_CHMV_vector"])

    def test_build_change_and_missing_8052_fail(self):
        with self.assertRaises(oil.OilSourceBlocked):
            oil.extract(generated_text=FIXTURE,game_build="12.2.0.71000",
                        simc_revision=REV,enchant_ids=[8052])
        with self.assertRaises(oil.OilSourceBlocked):
            oil.extract(generated_text=FIXTURE,game_build=BUILD,
                        simc_revision=REV,enchant_ids=[8053])

    def test_sealed_worklist_binding_does_not_allow_other_item(self):
        src=oil.extract(generated_text=FIXTURE,
                        game_build=BUILD,simc_revision=REV,
                        enchant_ids={8052})
        wrong=selected()
        wrong["simc_enchant_id"]=8051
        with self.assertRaises(oil.OilSourceBlocked):
            oil.project_source_oils(source=src,
                worklist={"oil":[wrong]},
                native_numeric={"status":
                  "PHYSICAL_ITEM_SIMC_F_O_CANDIDATES_UNADMITTED",
                  "flask":[],"oil":[]})
if __name__=="__main__":unittest.main()
