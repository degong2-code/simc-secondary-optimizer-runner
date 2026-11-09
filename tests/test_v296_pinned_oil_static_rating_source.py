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
        scaled=FIXTURE.replace("{ 8052, 0, 0, 0, 0, 0, 0, 0, 0, ",
                               "{ 8052, 0, -7, 0, 80, 120, 0, 0, 0, ")
        doc=oil.extract(generated_text=scaled,game_build=BUILD,
                        simc_revision=REV,enchant_ids=[8052])
        self.assertIsNone(doc["items"][0]["static_CHMV_vector"])

    def test_real_70783_scaled_source_stays_pending_not_12_or_16_or_17(self):
        # Simplified verbatim field-shape from 70783 generated DBC. The
        # -7 scaling ID and 0.4757 coefficients are SimC-owned operations.
        scaled=(
          "// spell item enchantments, wow build "+BUILD+"\n"
          '{ 8052, 0, -7, 0, 80, 120, 0, 0, 0, '
          '{ 5, 5, 0 }, { 12, 0, 0 }, { 32, 36, 0 }, '
          '{ 0.4757, 0.4757, 0 }, 0, "Thalassian Phoenix Oil" },\n'
        )
        doc=oil.extract(generated_text=scaled,game_build=BUILD,
                        simc_revision=REV,enchant_ids={8052})
        row=doc["items"][0]
        self.assertIsNone(row["static_CHMV_vector"])
        self.assertEqual(row["status"],oil.PENDING)
        self.assertIn("SIMC_ITEM_ENCHANT_SCALING_REQUIRED",
                      row["source_reason_codes"])
        self.assertEqual(set(row["unresolved_simc_scaled_static_stats"]),
                         {"crit_rating","haste_rating"})
        self.assertEqual(row["unresolved_simc_scaled_static_stats"][
                         "haste_rating"]["simc_coefficient"],0.4757)

    def test_scaled_simc_precombat_gear_measurement_reuses_source_without_buffed_delta(self):
        # Synthetic receipt: only the actual Native run confirms 70783 16/16.
        scaled=(
          "// spell item enchantments, wow build "+BUILD+"\n"
          '{ 8052, 0, -7, 0, 80, 120, 0, 0, 0, '
          '{ 5, 5, 0 }, { 12, 0, 0 }, { 32, 36, 0 }, '
          '{ 0.4757, 0.4757, 0 }, 0, "Thalassian Phoenix Oil" },\n'
        )
        src=oil.extract(generated_text=scaled,game_build=BUILD,
                        simc_revision=REV,enchant_ids={8052})
        self.assertIsNone(src["items"][0]["static_CHMV_vector"])
        choice=selected()
        measured={"schema":"v297_sealed_simc_oil_precombat_gear_delta_v1",
                  "status":"SIMC_PRECOMBAT_TOTAL_GEAR_STATIC_NUMBER_SOURCE_ONLY",
                  "game_build":BUILD,"simc_revision":REV,
                  "enchant_id":8052,
                  "simc_input_token":choice["simc_input_token"],
                  "talent_buffed_stats_not_used":True,
                  "binary_sha256":"c"*64,
                  "source_profile_sha256":"d"*64,
                  "native_case_receipt_sha256":["e"*64,"f"*64],
                  "static_CHMV_vector_unadmitted":{
                      "crit_rating":16,"haste_rating":16,
                      "mastery_rating":0,"versatility_rating":0}}
        numeric={"status":"PHYSICAL_ITEM_SIMC_F_O_CANDIDATES_UNADMITTED",
                 "flask":[],"oil":[]}
        def join(row):
            return oil.project_source_oils(
                source=src,worklist={"oil":[choice]},native_numeric=numeric,
                scaled_simc_gear_measurements=[{
                    "physical_item_id":243734,"selected_hand":"main_hand",
                    "measurement":row}])
        linked=join(measured)
        out=linked["oil"][0]
        self.assertEqual(out["status"],
                         "SIMC_PRECOMBAT_GEAR_NUMBER_SOURCE_ONLY")
        self.assertEqual(out["rating_candidate_unadmitted"],
                         measured["static_CHMV_vector_unadmitted"])
        self.assertEqual(out["simc_native_receipt_sha256"],
                         ["e"*64,"f"*64])
        self.assertFalse(out["source_admitted"])
        self.assertIsNone(linked["O"])
        with self.assertRaisesRegex(oil.OilSourceBlocked,"STAT_KIND"):
            join({**measured,"static_CHMV_vector_unadmitted":{
                "crit_rating":16,"haste_rating":16,"mastery_rating":1,
                "versatility_rating":0}})
        with self.assertRaisesRegex(oil.OilSourceBlocked,"IDENTITY_DRIFT"):
            join({**measured,"simc_revision":"a"*40})

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
