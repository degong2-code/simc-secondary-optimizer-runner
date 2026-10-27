"""v134 single 17-spec input producer: original APL/tier/weapon, Native0."""
from __future__ import annotations
import pathlib,sys,tempfile,hashlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v132_dps_source_batch_smoke as pins
import v133_mid2_target_representative_preview as drafts
import v134_shared_mid2_profile_adapter as adapter
import v129_common_source_fields as sourcefields

class SharedTargetAdapter(unittest.TestCase):
    def test_one_adapter_covers_all_source_complete_normal_gem_profiles(self):
        good=[]
        held={}
        for key in pins.NEW:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as td:
                original=pins.validate_source(key)
                target=tuple(key.split("/"))
                try:
                    profile,cfg,fillers,meta=adapter.producer(target)(
                        original["source"],pathlib.Path(td))
                except adapter.SharedAdapterBlocked as e:
                    held[key]=str(e)
                    continue
                good.append(key)
                self.assertEqual(cfg["character"]["spec"],target[1])
                self.assertEqual(cfg["character"]["class"],target[0])
                self.assertEqual(len(cfg["equipment"]["tier"]),4)
                self.assertEqual(cfg["consumables"]["flask_budget_F"],165)
                self.assertEqual(cfg["consumables"]["gem_budget_J"],138)
                self.assertEqual(sum(adapter.flask_for(original["source"])[1].values()),165)
                self.assertEqual(cfg["source"]["profile_sha256"],
                                 hashlib.sha256(profile.encode("utf8")).hexdigest())
                self.assertEqual(sourcefields.matching_lines(profile,"actions"),
                                 sourcefields.matching_lines(original["source"],"actions"))
                self.assertEqual(meta["new_native_calls"],0)
                self.assertEqual(len(cfg["equipment"]["tier"])+
                                 len(cfg["equipment"]["trinkets"])+
                                 len(fillers),original["slot_count"])
                self.assertFalse((pathlib.Path(td)/"simc_results").exists())
        # Feral now has a staged candidate with the witnessed six physical
        # ordinary gems and head diamond. A physical-only preview Native
        # passed on Windows, but the v098 CHMV target full run is unverified.
        self.assertEqual(held,{})
        self.assertEqual(len(good),17)
        import v101_common_representative_equipment as representative
        self.assertIn(("druid","feral"),representative.GENERIC_PENDING)

    def test_new_adapter_source_integrity_fail_closed(self):
        key=("warlock","destruction")
        original=pins.validate_source("/".join(key))
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(adapter.SharedAdapterBlocked,
                      "V134_SOURCE_BYTES_DIFFER_FROM_OFFICIAL_FIXTURE"):
                adapter.build(original["source"]+"\n# unsealed",td,key)
        with self.assertRaisesRegex(adapter.SharedAdapterBlocked,
                      "V134_NOT_A_NEW_PINNED_SOURCE"):
            adapter.producer(("evoker","augmentation"))

    def test_reference_flask_is_fixed_rating_not_an_unverified_guess(self):
        for key in pins.NEW:
            with self.subTest(key=key):
                source=pins.validate_source(key)["source"]
                flask,F,old=adapter.flask_for(source)
                self.assertIn(flask,adapter.FLASK_F)
                self.assertEqual(sum(F.values()),165)
                if old not in adapter.FLASK_F:
                    self.assertEqual(flask,adapter.DEFAULT_FLASK)
                else:
                    self.assertEqual(flask,old)

if __name__=="__main__":
    unittest.main()
