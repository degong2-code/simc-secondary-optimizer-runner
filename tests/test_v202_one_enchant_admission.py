"""v202: exact Native-evidence developer-only ring check; zero Native."""
import hashlib,pathlib,sys,unittest
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"runner"))
import v202_one_enchant_admission as v
def need(cond,why):
    if not cond: raise ValueError(why)
class OneExactRing(unittest.TestCase):
    def test_exact_item_bin_and_source_receipt(self):
        proof,_=v.read()
        rings={"finger1":{"item_id":158366,"ilevel":334,"options":{"gem_id":"240900"}}}
        fixed=v.apply_verified_ring(rings,{"finger1":8025},("mage","frost"),334,need)
        self.assertEqual(fixed["haste_rating"],30)
        self.assertEqual(rings["finger1"]["options"]["enchant_id"],"8025")
        profile="finger1=selected_158366,id=158366,ilevel=334,source=local,gem_id=240900,enchant_id=8025\n"
        norm={"scenario":{"character":{"class":"mage","spec":"frost"},"target":{"ilevel":334},"equipment":{"special":[],"crafted":[]}}}
        # Synthetic unit fixture explicitly patches the independent exact
        # profile seal. Production is separately checked against actual v203.
        with patch.object(v,"EXACT_SOURCE_PROFILE_SHA256",
                          hashlib.sha256(profile.encode("utf8")).hexdigest()):
            x=v.admit({"finger1":8025},profile,norm,proof["linux_binary_sha256"],"710c2408bf")
        self.assertEqual(x["fixed_E"],fixed)
        with patch.object(v,"EXACT_SOURCE_PROFILE_SHA256",
                          hashlib.sha256(profile.encode("utf8")).hexdigest()):
            conflicting={"scenario":{**norm["scenario"],
                "equipment":{"special":[{"slot":"finger1","item_id":158366}],
                             "crafted":[]}}}
            with self.assertRaisesRegex(v.EnchantAdmissionBlocked,
                                       "OVERLAPS_NATIVE_L"):
                v.admit({"finger1":8025},profile,conflicting,
                        proof["linux_binary_sha256"],"710c2408bf")
        with self.assertRaisesRegex(v.EnchantAdmissionBlocked,
                                    "FULL_PROFILE_TALENTS_CONSUMABLES"):
            v.admit({"finger1":8025},profile,norm,proof["linux_binary_sha256"],"710c2408bf")
        for wrong in (profile.replace("id=158366","id=111111"),
                      profile.replace("ilevel=334","ilevel=335"),
                      profile.replace("enchant_id=8025","enchant_id=8021")):
            with self.assertRaises(v.EnchantAdmissionBlocked):
                v.admit({"finger1":8025},wrong,norm,proof["linux_binary_sha256"],"710c2408bf")
        with self.assertRaises(v.EnchantAdmissionBlocked):
            v.admit({"finger1":8021},profile,norm,proof["linux_binary_sha256"],"710c2408bf")
        with self.assertRaises(v.EnchantAdmissionBlocked):
            v.admit({"finger1":8025},profile,norm,"0"*64,"710c2408bf")
    def test_existing_enchant_not_overwritten(self):
        rows={"finger1":{"item_id":158366,"ilevel":334,"options":{"enchant_id":"8021"}}}
        with self.assertRaises(ValueError):
            v.apply_verified_ring(rows,{"finger1":8025},("mage","frost"),334,need)
if __name__=="__main__":unittest.main()
