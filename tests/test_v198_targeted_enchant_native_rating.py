"""v198: exact one-slot base/enchant profile and JSON2 stat deltas, zero Native."""
import json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v198_targeted_enchant_native_rating as p

SAMPLE="""mage=target_frost
race=dwarf
default_actions=1
finger1=selected_158366,id=158366,ilevel=334,source=local,gem_id=240900,enchant_id=8021
finger2=selected_159459,id=159459,ilevel=334,source=local
gear_crit_rating=700
gear_haste_rating=700
gear_mastery_rating=700
gear_versatility_rating=700
json2={{json2}}
iterations=35
"""
def native(rating,with_enchant=True,revision="710c2408bf"):
    item="selected_158366,id=158366,ilevel=334,source=local,gem_id=240900"
    if with_enchant:item+=",enchant_id=8025"
    return json.dumps({
        "report_version":"2.0.0","git_revision":revision,
        "sim":{"players":[{"gear":{
          "finger1":{"encoded_item":item,"crit_rating":0,
                     "haste_rating":rating},
          "finger2":{"encoded_item":
             "selected_159459,id=159459,ilevel=334,source=local",
             "haste_rating":7},
          "head":{"encoded_item":
             "selected_271564,id=271564,ilevel=334,source=local",
             "mastery_rating":11}
        }}]}}).encode("utf8")

class MatchedEnchantProbe(unittest.TestCase):
    def test_only_one_real_slot_diff_preserves_gem_item_and_no_other_gear(self):
        original=SAMPLE.replace("{{json2}}","__JSON2_PATH__")
        base,new=p.swap_slot_enchant(original,"finger1",8025)
        self.assertEqual(len([i for i,(a,b) in enumerate(zip(
            base.splitlines(),new.splitlines())) if a!=b]),1)
        self.assertIn("gem_id=240900",base)
        self.assertIn("gem_id=240900",new)
        self.assertNotIn("enchant_id=",base)
        self.assertIn("enchant_id=8025",new)
        self.assertEqual(p.compare_native(native(40,False),native(69),
                        "finger1",8025,"710c240")["static_secondary"],
                        {"crit_rating":0,"haste_rating":29,
                         "mastery_rating":0,"versatility_rating":0})
    def test_wrong_enchant_revision_item_and_negative_static_fail_closed(self):
        with self.assertRaisesRegex(p.ProbeBlocked,"ENCHANT_NOT_OBSERVED"):
            p.compare_native(native(40,False),native(40,False),
                             "finger1",8025,"710c240")
        with self.assertRaisesRegex(p.ProbeBlocked,"REVISION"):
            p.compare_native(native(40,False),native(69,revision="bad_hash"),
                             "finger1",8025,"710c240")
        with self.assertRaisesRegex(p.ProbeBlocked,"NEGATIVE"):
            p.compare_native(native(40,False),native(39),"finger1",8025,"710c240")
        with self.assertRaisesRegex(p.ProbeBlocked,"PROBE_SLOT_NOT_APPROVED"):
            p.swap_slot_enchant(SAMPLE,"off_hand",8025)
    def test_extra_gear_difference_cannot_generate_static_receipt(self):
        a=json.loads(native(69))
        a["sim"]["players"][0]["gear"]["finger2"]["haste_rating"]=8
        with self.assertRaisesRegex(p.ProbeBlocked,"OTHER_NATIVE_GEAR_CHANGED"):
            p.compare_native(native(40,False),json.dumps(a).encode(),
                             "finger1",8025,"710c240")

if __name__=="__main__":unittest.main()
