"""Fresh user profile selection contract; no source API, no Native."""
import unittest
from integration_probes import p2_new_profile_product_e2e_once as e2e


class FreshProductScenarioOffline(unittest.TestCase):
    def test_three_unique_profiles_not_old_hae_or_ret(self):
        fingerprints=[]
        for name in e2e.CASES:
            item,controls=e2e.selected_case(name)
            self.assertEqual(item["sockets"],4)
            self.assertIsNone(item["special_gem"])
            self.assertEqual(controls["consumable_choices"]["diamond_id"],0)
            self.assertEqual(controls["final_T"],item["final_T"])
            self.assertEqual(controls["special_items"],[])
            self.assertEqual(controls["embellishments"],[])
            self.assertIn((item["character_class"],item["character_spec"]),
                          e2e.users.SUPPORTED)
            fingerprints.append((
                item["character_class"],item["character_spec"],
                item["final_T"]))
        self.assertEqual(len(set(fingerprints)),len(e2e.CASES))
        self.assertNotIn(("shaman","enhancement"),set(
            (x[0],x[1]) for x in fingerprints))

    def test_unknown_case_fail_closed(self):
        with self.assertRaisesRegex(
                e2e.ProductCaseBlocked,
                "EXPLICIT_DIFFERENT_PROFILE_CASE_REQUIRED"):
            e2e.selected_case("old_enhancement_70783")
        with self.assertRaisesRegex(
                e2e.ProductCaseBlocked,
                "EXPLICIT_DIFFERENT_PROFILE_CASE_REQUIRED"):
            e2e.selected_case("")

    def test_binary_and_explicit_native_opt_in_required(self):
        with self.assertRaisesRegex(
                e2e.ProductCaseBlocked,
                "EXPLICIT_FRESH_PRODUCT_NATIVE_OPT_IN_REQUIRED"):
            e2e.run()


if __name__=="__main__":
    unittest.main()
