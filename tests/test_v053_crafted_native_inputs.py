"""v053: regression for all 12 crafted equipment reference profiles."""
import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v051_crafted_embellishment_bridge as bridge
import v052_crafted_native_sample as probe

class CraftedNativeInputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat=bridge.load_reference(ROOT/"integration_probes/catalog/v051_crafted_armor_weapon_reference.json")[1]
    def test_all_native_sample_items_have_compatible_source(self):
        self.assertEqual(len(probe.ITEM_CASES),13)
        for item_id,token in probe.ITEM_CASES:
            case=probe.build_sample(self.cat[item_id],token,pathlib.Path('/tmp/v053.json'))
            self.assertIn(f"id={item_id},ilevel=331,source=local,crafted_stats={token}",case)
            self.assertIn("iterations=1",case)
            self.assertIn("actions=wait,sec=1",case)
    def test_generic_cloak_allowed_without_weapon_lookup(self):
        x=probe.build_sample(self.cat[239656],"49/36",pathlib.Path('/tmp/v053.json'))
        self.assertIn('mage="V052CraftedStatic"',x)
        self.assertIn("back=v052_crafted_239656",x)
    def test_armor_class_mapping(self):
        for item_id,token in probe.ITEM_CASES:
            item=self.cat[item_id]
            if item["armor_family"] in probe.CLASS:
                case=probe.build_sample(item,token,pathlib.Path('/tmp/x.json'))
                self.assertTrue(case.startswith(probe.CLASS[item["armor_family"]][0]+'="V052CraftedStatic"'))
    def test_offhand_have_anchor(self):
        for id in (237840,237850,245769):
            x=probe.build_sample(self.cat[id],"49/36",pathlib.Path('/tmp/v053.json'))
            self.assertIn("main_hand=v052_anchor",x)
            self.assertIn("off_hand=v052_crafted_",x)

if __name__=="__main__":unittest.main()
