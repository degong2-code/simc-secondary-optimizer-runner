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
        self.assertEqual(results["missing_exact_fifth_tier"],0)
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
    def test_full_five_tier_identity_for_all_eleven_source_classes(self):
        for key in source.NEW:
            with self.subTest(key=key):
                data,_=preview.draft(key)
                self.assertEqual(data["missing_fifth_tier_id"],[])
                cls=key.split("/")[0]
                self.assertEqual(len(preview.FIVE_TIER[cls]),5)
                self.assertTrue(all(type(id_) is int and id_>0
                                    for id_ in preview.FIVE_TIER[cls]))
        self.assertEqual(preview.FIVE_TIER["monk"][3],271520)
        self.assertEqual(preview.FIVE_TIER["priest"][1],271553)
        self.assertEqual(preview.FIVE_TIER["warlock"][0],271546)
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
    def test_original_diamond_retained_only_on_source_supported_head(self):
        cases={"mage/arcane":("240983",271874),
               "mage/fire":("240967",271874),
               "hunter/marksmanship":("240967",249317),
               "hunter/survival":("240983",249317),
               "warlock/affliction":("240967",271874)}
        for key,(gem,id_) in cases.items():
            with self.subTest(key=key):
                data,profile=preview.draft(key)
                head=next(line for line in profile.splitlines()
                          if line.startswith("head="))
                self.assertIn("id="+str(id_),head)
                self.assertIn("gem_id="+gem,head)
                self.assertEqual(data["diamond_id"],gem)

    def test_staged_feral_six_ordinary_gems_and_head_diamond_are_source_witnessed(self):
        feral=source.validate_source("druid/feral")["source"]
        monk=source.validate_source("monk/windwalker")["source"]
        self.assertIn("head=enigmatic_dreamwatchers_somnolent_stare,id=271528",feral)
        self.assertIn("neck=aqirbane_reliquary,id=268265",feral)
        self.assertIn("gem_id=240983",feral)
        self.assertIn("neck=aqirbane_reliquary,id=268265",monk)
        self.assertIn("gem_id=240914/240890",monk)
        self.assertIn("wrists=silvermoon_agents_deflectors,id=244576",monk)
        self.assertIn("waist=sash_of_the_forlorn_vessel,id=268256",monk)
        self.assertIn("gem_id=240908",monk)
        data,profile=preview.draft("druid/feral",334)
        self.assertEqual(data["diamond_id"],"240983")
        self.assertEqual(data["ordinary_gem_count"],6)
        self.assertNotIn("REPRESENTATIVE_HEAD_DIAMOND_NOT_READY",
                         data["open_product_conditions"])
        self.assertNotIn("SIX_PHYSICAL_ORDINARY_GEMS_NOT_READY",
                         data["open_product_conditions"])
        self.assertIn("NON_TIER_SOURCE_GEAR_NOT_ALL_STANDARDIZED",
                      data["open_product_conditions"])
        self.assertIn("FERAL_TARGET_CHMV_NATIVE_NOT_YET_VERIFIED",
                      data["open_product_conditions"])
        self.assertFalse(data["ready_for_user_optimizer"])
        self.assertEqual(data["native_calls"],0)
        for slot,(id_,gems) in preview.FERAL_SOCKET_ROWS.items():
            row=next(line for line in profile.splitlines()
                     if line.startswith(slot+"="))
            self.assertIn("id="+str(id_),row)
            self.assertIn("gem_id="+gems,row)
        # The preview must not rewrite its SHA-pinned original source/APl.
        self.assertEqual(fields.matching_lines(profile,"actions"),
                         fields.matching_lines(feral,"actions"))
        self.assertNotIn("gem_id=240983",next(
            line for line in profile.splitlines() if line.startswith("neck=")))

    def test_feral_candidate_fails_if_source_item_or_socket_layout_drifts(self):
        feral=source.validate_source("druid/feral")["source"]
        ids,mods=fields.equipment(feral,preview.item.SLOTS,
                                  need=preview.need,include_gem_enchant=True,
                                  duplicate_prefix="V133_SOURCE_DUPLICATE_SLOT:",
                                  missing_id_prefix="V133_SOURCE_ITEM_ID_MISSING:")
        with self.assertRaisesRegex(preview.PreviewBlocked,
                                    "V133_FERAL_SOCKET_REFERENCE_ITEM_DRIFT"):
            preview.feral_candidate_sockets("druid/feral",
                                            dict(ids,neck=1),mods)
        ids,mods=fields.equipment(feral,preview.item.SLOTS,
                                  need=preview.need,include_gem_enchant=True,
                                  duplicate_prefix="V133_SOURCE_DUPLICATE_SLOT:",
                                  missing_id_prefix="V133_SOURCE_ITEM_ID_MISSING:")
        with self.assertRaisesRegex(preview.PreviewBlocked,
                                    "V133_FERAL_ORIGINAL_SOCKET_LAYOUT_DRIFT"):
            mods["head"]["gem_id"]="240967"
            preview.feral_candidate_sockets("druid/feral",ids,mods)

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
