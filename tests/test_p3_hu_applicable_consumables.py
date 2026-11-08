"""P3-HU source-pinned full applicable test; offline and no new Native."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from integration_probes import p3_fr_zero_base_t1_acceptance as p
from runner import v108_native_consumable_inputs as source
class FullApplicable(unittest.TestCase):
    cases={"P3_T1_FULL_CONSUMABLES_ONCE":"1",
         "P3_T1_FULL_FOOD":"harandar_celebration",
         "P3_T1_FULL_POTION":"potion_of_recklessness_2",
         "P3_T1_FULL_AUGMENTATION":"void_touched",
         "P3_T1_FULL_OMNIUM":"136822:1/136823:1/136817:1/136821:1/136814:1"}
    character={"class":"shaman","spec":"enhancement","race":"dwarf"}
    def test_settings_from_existing_pinned_simc_source(self):
        selected=p.optional_full_consumables(self.cases,dps_once=True,character=self.character)
        self.assertEqual(selected["food"],"harandar_celebration")
        self.assertEqual(selected["potion"],"potion_of_recklessness_2")
        self.assertIn(selected["augmentation"],source.SUPPORTED["augmentation"])
        self.assertIn(selected["omnium_talents"],source.OMNIUM_PRESETS)
        self.assertIsNone(p.optional_full_consumables({},dps_once=True,character=self.character))
    def test_scope_and_invalid_options_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"ONE_SHAMAN"):
            p.optional_full_consumables(self.cases,dps_once=False,character=self.character)
        with self.assertRaisesRegex(ValueError,"ONE_SHAMAN"):
            p.optional_full_consumables(self.cases,dps_once=True,character={"class":"paladin","spec":"retribution"})
        with self.assertRaisesRegex(ValueError,"SOURCE_PINNED"):
            p.optional_full_consumables({**self.cases,"P3_T1_FULL_FOOD":"invented"},dps_once=True,character=self.character)
    def test_one_shot_workflow_opt_in(self):
        root=pathlib.Path(__file__).resolve().parents[1]
        yaml=(root/".github/workflows/p3_fz_reuse_exact_simc_live_t1.yml").read_text("utf8")
        self.assertIn("[p3-hu-full-nonenchant-dps-once]",yaml)
        self.assertIn("p3_hu_full_no_enchants_20261108.json",yaml)
        self.assertIn("P3_T1_FULL_CONSUMABLES_ONCE",yaml)
        self.assertIn("p3_ht_dps_native_audit.zip",yaml)
if __name__=="__main__": unittest.main()
