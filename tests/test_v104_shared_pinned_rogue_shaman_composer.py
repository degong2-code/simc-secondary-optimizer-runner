"""v104 shared Rogue/Shaman source-bound target equipment; OFFLINE ONLY."""
import copy,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v061_scenario_contract as scenario
import v102_ordinary_armor_seed_pool as future_pool
import v104_shared_pinned_rogue_shaman_composer as target

class SourceBackedTwoSpecComposer(unittest.TestCase):
    def source(self,key):
        return (target.FIXTURES/target.PROFILES[key]["filename"]).read_text("utf8")

    def test_two_source_profiles_have_exact_original_APL_and_four_class_tiers(self):
        for key in target.PROFILES:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as td:
                original=self.source(key)
                profile,cfg,fillers,receipt=target.create_from_source(
                    original,pathlib.Path(td),key)
                self.assertEqual([l for l in original.splitlines()
                                  if l.startswith("actions")],
                                 [l for l in profile.splitlines()
                                  if l.startswith("actions")])
                self.assertGreaterEqual(receipt["original_apl_line_count"],15)
                self.assertEqual(len(cfg["equipment"]["tier"]),4)
                self.assertEqual(len(cfg["equipment"]["trinkets"]),2)
                self.assertEqual(len(fillers),10)
                self.assertEqual(cfg["equipment"]["special"],[])
                self.assertEqual(cfg["equipment"]["crafted"],[])
                self.assertEqual(sum(int(l.startswith("main_hand=")) for l in
                                     profile.splitlines()),1)
                self.assertEqual(sum(int(l.startswith("off_hand=")) for l in
                                     profile.splitlines()),1)
                self.assertEqual(receipt["new_native_calls"],0)
                self.assertFalse(receipt["new_exact_static_variant_verified"])
                self.assertEqual(scenario.normalize(cfg)["status"],
                                 "VALID_SCENARIO_INPUT_NO_SIMC_EFFECT_GATE")
                self.assertNotIn("temporary_enchant=",profile)

    def test_rogue_source_is_not_used_as_equipped_special_head_or_cloak(self):
        key=("rogue","subtlety")
        profile,cfg,fill,meta=target.create_from_source(
            self.source(key),pathlib.Path("."),key)
        source={r["slot"]:r for r in cfg["equipment"]["tier"]+fill}
        self.assertEqual(source["head"]["item_id"],271510)
        self.assertEqual(source["chest"]["item_id"],251159)
        self.assertEqual(source["back"]["item_id"],268253)
        self.assertEqual(source["wrists"]["item_id"],268240)
        self.assertNotIn("redirected_base_stats",
                         source["head"]["options"])
        self.assertNotIn("bonus_id",source["head"]["options"])
        self.assertEqual(source["off_hand"]["item_id"],237837)
        self.assertEqual(source["off_hand"]["options"]["crafted_stats"],"36/49")

    def test_shaman_fixed_mail_head_and_ordinary_wrists_replace_legacy_random_gear(self):
        key=("shaman","elemental")
        profile,cfg,fill,meta=target.create_from_source(
            self.source(key),pathlib.Path("."),key)
        source={r["slot"]:r for r in cfg["equipment"]["tier"]+fill}
        self.assertEqual(source["head"]["item_id"],249317)
        self.assertEqual(source["head"]["options"]["gem_id"],"240983")
        self.assertEqual(source["wrists"]["item_id"],273775)
        self.assertEqual(source["feet"]["item_id"],249320)
        self.assertNotIn("crafted_stats",source["head"]["options"])
        self.assertNotIn("crafted_stats",source["wrists"]["options"])
        self.assertEqual(len(cfg["equipment"]["tier"]),4)
        self.assertEqual(source["off_hand"]["item_id"],268262)

    def test_historical_shaman_baseline_is_decoupled_from_future_mail_seed_pool(self):
        self.assertEqual(target.HISTORICAL_ORDINARY[("mail","head")],249317)
        self.assertEqual(target.HISTORICAL_ORDINARY[("mail","feet")],249320)
        self.assertEqual(future_pool.row("mail","head",334)["item_id"],271441)
        self.assertEqual(future_pool.row("mail","feet",334)["item_id"],271440)
        profile,cfg,fill,_=target.create_from_source(
            self.source(("shaman","elemental")),pathlib.Path("."),
            ("shaman","elemental"))
        rows={r["slot"]:r for r in cfg["equipment"]["tier"]+fill}
        self.assertEqual(rows["head"]["item_id"],249317)
        self.assertEqual(rows["feet"]["item_id"],249320)
        self.assertNotIn("selected_271441,id=271441",profile)
        self.assertNotIn("selected_271440,id=271440",profile)

    def test_source_tampering_rejected_and_all_other_specs_not_enabled(self):
        for key in target.PROFILES:
            source=self.source(key)
            with self.subTest(key=key):
                with self.assertRaisesRegex(target.SourceBlocked,
                          "SOURCE_PROFILE_GIT_BLOB_MISMATCH"):
                    target.create_from_source(source+"\n# modified\n",
                                              pathlib.Path("."),key)
        with self.assertRaisesRegex(target.SourceBlocked,
                                   "NEW_SOURCE_SPEC_UNSUPPORTED"):
            target.create_from_source("test",pathlib.Path("."),
                                      ("druid","balance"))

    def test_original_source_catalyst_redirect_not_accidentally_injected_into_baseline(self):
        for key in target.PROFILES:
            source=self.source(key)
            profile,cfg,fill,receipt=target.create_from_source(
                source,pathlib.Path("."),key)
            for part in profile.splitlines():
                if part.startswith(tuple(target.ALL_SLOTS)):
                    self.assertNotIn("redirected_base_stats=",part)
            self.assertNotIn("selected_271441,id=271441",profile)
            self.assertNotIn("selected_271440,id=271440",profile)

if __name__=="__main__":unittest.main()
