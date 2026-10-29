"""v169: no legacy gear seeding; 26 DPS source-first 4pc preview only."""
import copy
import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v169_source_first_representative_stage as stage
import v167_product_season_gear_adapter as gear

class SourceFirstRepresentative(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=gear.read()
        cls.tier=stage.load_tier()

    def test_all_26_classes_four_real_tier_without_source_profile_copy(self):
        plan=stage.build_all(self.db,self.tier)
        self.assertEqual(plan["dps_specs"],26)
        self.assertEqual(plan["tier_classes"],13)
        self.assertEqual(plan["simc_native_calls"],0)
        self.assertFalse(plan["old_profile_item_ids_copied"])
        self.assertFalse(plan["profile_activated_in_v098"])
        self.assertFalse(plan["all_items_physical_simc_accepted"])
        source_ids={x["item_id"] for x in self.db["items"]}
        for name,spec in plan["specializations"].items():
            with self.subTest(spec=name):
                cl=name.split("/")[0]
                self.assertEqual(spec["tier_ids"],self.tier["classes"][cl]["pieces"])
                self.assertEqual(set(spec["four_tier_slots"]),set(stage.FOUR))
                self.assertEqual(set(spec["ordinary"]),set(stage.ORDINARY))
                self.assertEqual(set(spec["weapons"]),set(
                    stage.contracts.WEAPON_FORMS[spec["weapon_form"]]))
                self.assertEqual(len(set(spec["weapons"].values())),
                                 len(spec["weapons"]))
                self.assertTrue(set(spec["ordinary"].values())<=source_ids)
                self.assertTrue(set(spec["weapons"].values())<=source_ids)
        self.assertTrue(set(plan["common_gear"].values())<=source_ids)

    def test_new_source_profile_text_only_uses_new_item_ids(self):
        sample={"class":"paladin","spec":"retribution",
                "race":"human","talents":"abc123456789"}
        trinkets=[{"slot":slot,"item_id":iid,"options":{}}
                  for slot,iid in zip(("trinket1","trinket2"),
                   [r["item_id"] for r in self.db["items"]
                    if r["category"]=="trinket"][:2])]
        proof=stage.compose_stage(sample,trinkets,db=self.db,tier=self.tier)
        self.assertEqual(proof["status"],"PROFILE_TEXT_PREVIEW_ONLY_NOT_NATIVE_ACCEPTED")
        self.assertEqual(proof["profile_receipt"]["status"],"STAGED_NOT_USER_READY")
        self.assertIn("default_actions=1",proof["profile_text"])
        self.assertEqual(proof["native_calls"],0)
        self.assertFalse(proof["full_profile_native_accepted"])
        self.assertTrue(proof["new_current_season_equipment_only"])

    def test_build_mismatch_rejected_not_implicit_repair(self):
        snapshot=copy.deepcopy(self.db)
        snapshot["season_build"]="12.1.5.70576"
        with self.assertRaises(stage.RepresentativeBlocked):
            stage.build_all(snapshot,self.tier)
        scope=copy.deepcopy(self.tier)
        scope["classes"].pop("evoker")
        with self.assertRaises(stage.RepresentativeBlocked):
            stage.build_all(self.db,scope)

    def test_weapon_inventory_form_only_not_class_proficiency(self):
        plan=stage.build_all(self.db,self.tier)["specializations"]
        self.assertEqual(len(plan["warrior/fury"]["weapons"]),2)
        self.assertEqual(len(plan["hunter/marksmanship"]["weapons"]),1)
        self.assertEqual(len(plan["shaman/elemental"]["weapons"]),2)
        self.assertEqual(len(plan["mage/arcane"]["weapons"]),2)
        self.assertTrue(all(item["weapon_subclass_proficiency_native_unverified"]
                            for item in plan.values()))

if __name__=="__main__":unittest.main()
