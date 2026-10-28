"""v102 bounded, four-family real-item ordinary seed inputs; ZERO Native."""
import copy,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v046_static_item_cache as cache
import v062_static_budget_bridge as budget
import v101_common_representative_equipment as common
import v102_ordinary_armor_seed_pool as pool

class SourceBoundArmorSeeds(unittest.TestCase):
    def test_four_materials_have_exact_source_id_slots_without_full_catalog_claim(self):
        x=pool.verify_pool()
        self.assertEqual(x["status"],"FOUR_FAMILY_PARTIAL_ORDINARY_POOL")
        self.assertEqual(x["source_backed_item_ids"],14)
        self.assertEqual(x["family_slot_counts"],
                         {"cloth":3,"leather":4,"mail":4,"plate":3})
        self.assertEqual(x["fully_equipped_profiles"],0)
        self.assertFalse(x["new_variant_stats_native_verified"])
        self.assertTrue(x["not_a_full_armor_pool"])
        self.assertEqual(x["native_calls"],0)

    def test_all_registered_item_slots_are_anchored_to_pinned_simc_fixture_or_v086(self):
        for family,slots in pool.FAMILY_ROWS.items():
            with self.subTest(family=family):
                self.assertEqual(family in common.ARMOR_CLASSES,True)
                for slot,(source,item_id,kind,name) in slots.items():
                    got=pool.row(family,slot,334)
                    self.assertEqual(got,{"slot":slot,"item_id":item_id,
                                         "ilevel":334,"options":{}})
                    meta=pool.provenance(family,slot)
                    self.assertEqual(meta["item_id"],item_id)
                    self.assertEqual(meta["slot"],slot)
                    self.assertEqual(meta["armor_family"],family)
                    self.assertTrue(meta["item_reference"].endswith(str(item_id)))
                    self.assertTrue(meta["not_verified_native_exact_target_variant"])
                    self.assertTrue(meta["not_an_item_acquisition_recommendation"])

    def test_new_wrist_rows_are_real_fixed_secondary_live_season_not_crafted(self):
        expected={"leather":(268240,"crit/haste"),
                  "mail":(273775,"vers/mastery"),
                  "plate":(268239,"crit/mastery")}
        for family,(item_id,stats) in expected.items():
            with self.subTest(family=family):
                row=pool.row(family,"wrists",334)
                self.assertEqual(row["item_id"],item_id)
                self.assertEqual(row["options"],{})
                self.assertEqual(pool.provenance(family,"wrists")
                                 ["source_file"],"LIVE_WOWHEAD_12_1_ITEM_ID_AND_MATERIAL")
                self.assertEqual(pool.WEB_SOURCE_DETAILS[item_id][2],stats)
        self.assertNotIn("web_live",pool.SOURCE)

    def test_mail_head_and_feet_use_same_season_target334_mid2_hunter_ids(self):
        # These are ordinary S2 mail drops with random secondaries. The seed
        # deliberately carries no crafted_stats/gems: exact target variant
        # static rating remains a later Native/static-cache identity.
        self.assertEqual(pool.row("mail","head",334),
                         {"slot":"head","item_id":271441,
                          "ilevel":334,"options":{}})
        self.assertEqual(pool.row("mail","feet",334),
                         {"slot":"feet","item_id":271440,
                          "ilevel":334,"options":{}})
        for slot,item_id in (("head",271441),("feet",271440)):
            meta=pool.provenance("mail",slot)
            self.assertEqual(meta["source_kind"],"ordinary")
            self.assertEqual(meta["item_id"],item_id)
            self.assertEqual(meta["source_file"],
                "integration_probes/fixtures/v132_MID2_Hunter_Marksmanship.simc")
            self.assertTrue(meta["not_verified_native_exact_target_variant"])
        source=pool.source_ids("marksman_mid2")
        self.assertEqual((source["head"],source["feet"]),(271441,271440))
        ids=[r[1] for r in pool.FAMILY_ROWS["mail"].values()]
        self.assertNotIn(249317,ids)
        self.assertNotIn(249320,ids)

    def test_leather_feet_now_use_same_season_pinned_ordinary_item_only_in_seed_pool(self):
        # Previously the seed pool used legacy Goldfeather Boots 159304.
        # 268261 is source-observed Feral feet in official MID2 fixture,
        # corroborated externally as a plain leather crit/haste foot item.
        row=pool.row("leather","feet",334)
        self.assertEqual(row,{"slot":"feet","item_id":268261,
                              "ilevel":334,"options":{}})
        meta=pool.provenance("leather","feet")
        self.assertEqual(meta["source_kind"],"ordinary")
        self.assertEqual(meta["source_file"],
                         "integration_probes/fixtures/v132_MID2_Druid_Feral.simc")
        self.assertTrue(meta["not_verified_native_exact_target_variant"])
        self.assertEqual(pool.source_ids("feral_mid2")["feet"],268261)
        self.assertNotIn(159304,[r[1] for r in pool.FAMILY_ROWS["leather"].values()])
        self.assertEqual(pool.row("leather","waist",334)["item_id"],268256)
        self.assertEqual(pool.row("cloth","waist",334)["item_id"],268257)

    def test_new_ordinary_seed_does_not_rewrite_existing_havoc_native_profile(self):
        # Source-backed candidate metadata is separate from the v133 builder.
        import v133_mid2_target_representative_preview as preview
        data,profile=preview.draft("demonhunter/havoc",334)
        feet=next(line for line in profile.splitlines()
                  if line.startswith("feet="))
        self.assertIn("id=159327",feet)
        self.assertNotIn("id=268261",feet)
        self.assertEqual(pool.row("leather","feet",334)["item_id"],268261)
        self.assertEqual(data["native_calls"],0)

    def test_material_and_unverified_slot_cannot_cross_fill(self):
        for family,slot in (("leather","head"),("plate","head"),
                            ("mail","chest"),("cloth","legs"),
                            ("unknown","feet")):
            with self.subTest(family=family,slot=slot):
                with self.assertRaisesRegex(pool.PoolBlocked,
                          "ORDINARY_SLOT_NOT_SOURCE_READY|ARMOR_FAMILY_UNSUPPORTED"):
                    common.ordinary_armor_seed(family,slot,334)
        with self.assertRaisesRegex(pool.PoolBlocked,
                                    "ORDINARY_ILVL_OUTSIDE_APPROVED_REFERENCE"):
            pool.row("plate","feet",345)
        with self.assertRaisesRegex(pool.PoolBlocked,
                                    "ORDINARY_ILVL_OUTSIDE_APPROVED_REFERENCE"):
            pool.row("plate","feet",334.5)

    def test_exact_static_variant_cache_key_is_distinct_when_target_level_changes(self):
        a=common.ordinary_armor_seed("plate","feet",334)
        b=common.ordinary_armor_seed("plate","feet",321)
        self.assertEqual(a["item_id"],b["item_id"])
        self.assertNotEqual(cache.digest(budget.exact_identity(a)),
                            cache.digest(budget.exact_identity(b)))
        self.assertEqual(a["options"],{})
        self.assertEqual(b["options"],{})

    def test_fixture_checksum_drift_is_refused_without_new_network_or_native(self):
        source_key="frost"
        old=pool.SOURCE[source_key]
        try:
            pool.SOURCE[source_key]=(old[0],"0"*40)
            with self.assertRaisesRegex(pool.PoolBlocked,
                                        "ORDINARY_SOURCE_GIT_BLOB_DRIFT"):
                pool.source_ids(source_key)
        finally:
            pool.SOURCE[source_key]=old
        self.assertTrue(pool.source_ids(source_key)["feet"]==268255)

    def test_partial_seed_does_not_rewrite_existing_profile(self):
        self.assertEqual(common.available_ordinary_seed_slots("cloth"),
                         ("feet","waist","wrists"))
        self.assertEqual(common.available_ordinary_seed_slots("plate"),
                         ("feet","waist","wrists"))
        self.assertEqual(common.available_ordinary_seed_slots("missing"),())
        self.assertEqual(common.ordinary_armor_seed("leather","chest",321),
                         {"slot":"chest","item_id":251159,"ilevel":321,"options":{}})

if __name__=="__main__":unittest.main()
