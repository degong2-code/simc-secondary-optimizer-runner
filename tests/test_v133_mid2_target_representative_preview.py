"""v133: 17 target-level draft profiles share one generator, Native0.

NO claim that source's other armor IDs are fully standard-ordinary, or
that generated profiles have passed real Native gear/CHMV/95% validation.
"""
from __future__ import annotations
import hashlib,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v133_mid2_target_representative_preview as preview
import v132_dps_source_batch_smoke as source
import v129_common_source_fields as fields
class Mid2TargetDraft(unittest.TestCase):
    def test_all_seventeen_share_target_ilvl_four_tier_and_original_apl(self):
        results=preview.preview_all(334)
        self.assertEqual(results["status"],
                         "PASS_17_PROFILES_STAGED_NOT_EXECUTABLE")
        self.assertEqual(results["source_count"],17)
        self.assertEqual(results["native_calls"],0)
        self.assertEqual(results["ready_for_user_optimizer"],0)
        self.assertEqual(len(results["specs"]),17)
        self.assertEqual(results["missing_exact_fifth_tier"],5)
        for key in source.NEW:
            with self.subTest(key=key):
                data,profile=preview.draft(key,334)
                old=source.validate_source(key)
                self.assertEqual(fields.matching_lines(profile,"actions"),
                                 fields.matching_lines(old["source"],"actions"))
                self.assertEqual(data["four_tier_slots"].__len__(),4)
                self.assertEqual(data["physical_items"],old["slot_count"])
                self.assertTrue(data["open_product_conditions"])
                self.assertFalse(data["ready_for_user_optimizer"])
                self.assertEqual(data["native_calls"],0)
                self.assertEqual(
                    hashlib.sha256(profile.encode()).hexdigest(),
                    data["profile_sha256"])
                self.assertEqual(sum(line.startswith("iterations=")
                                     for line in profile.splitlines()),1)
                self.assertEqual(sum(line.startswith("main_hand=")
                                     for line in profile.splitlines()),1)
                self.assertEqual(sum(line.startswith("trinket1=")
                                     for line in profile.splitlines()),1)
                self.assertEqual(sum(line.startswith("trinket2=")
                                     for line in profile.splitlines()),1)
                self.assertEqual(sum(",ilevel=334" in line
                                     for line in profile.splitlines()),
                                 old["slot_count"])
    def test_tiers_are_unambiguously_source_observed_not_guessed(self):
        expected={"monk/windwalker":"hands","priest/shadow":"shoulders",
                  "warlock/affliction":"head",
                  "warlock/demonology":"head",
                  "warlock/destruction":"head"}
        for key in source.NEW:
            with self.subTest(key=key):
                data,_=preview.draft(key)
                missing=data["missing_fifth_tier_id"]
                if key in expected:
                    self.assertEqual(missing,[expected[key]])
                else:
                    self.assertEqual(missing,[])
    def test_target_ilvl_is_only_a_physical_preview_not_source_native_input(self):
        before=source.validate_source("deathknight/frost")["source"]
        at334,profile334=preview.draft("deathknight/frost",334)
        at321,profile321=preview.draft("deathknight/frost",321)
        self.assertNotEqual(profile334,profile321)
        self.assertEqual(at321["level"],321)
        self.assertIn("ilevel=334",profile334)
        self.assertIn("ilevel=321",profile321)
        self.assertNotIn("gear_crit_rating=700",profile334)
        self.assertEqual(before,source.validate_source("deathknight/frost")["source"])
    def test_no_17_native_or_product_ui_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            result=preview.preview_all(334,root)
            self.assertEqual(len(list(root.glob("*.simc"))),17)
            self.assertEqual(result["native_calls"],0)
            self.assertFalse((root/"simc_results").exists())
            self.assertEqual(sum(x["ready_for_user_optimizer"]
                                 for x in result["specs"]),0)
        with self.assertRaisesRegex(preview.PreviewBlocked,"V133_LEVEL_INVALID"):
            preview.draft("mage/fire",999)
        with self.assertRaisesRegex(preview.PreviewBlocked,"V133_SOURCE_KEY_NOT_PINNED"):
            preview.draft("evoker/augmentation")
if __name__=="__main__":unittest.main()
