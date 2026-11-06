"""P3-GM: exact native F T1 selection is source-only until original v281/v278."""
import sys
import pathlib
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from integration_probes import p3_fr_zero_base_t1_acceptance as p


class TargetedFlaskT1Inputs(unittest.TestCase):
    def test_unchanged_default_opt_in_remains_broad(self):
        self.assertIsNone(p.optional_exact_item_id({},"P3_T1_EXACT_FLASK_ITEM_ID"))
        self.assertEqual(p.selected_t1_source_inputs(
            exact_flask_item_id=None,existing_special_gem_id=None),{})
        self.assertIsNone(p.original_verified_F_only_uninstalled({},None))

    def test_selected_exact_F_is_not_rating_or_unverified_admission(self):
        f=p.optional_exact_item_id({"EXACT":"241326"},"EXACT")
        self.assertEqual(f,241326)
        self.assertEqual(p.selected_t1_source_inputs(
            exact_flask_item_id=f,existing_special_gem_id=None),
            {"selected_budget_items":{
                "flask_item_id":241326,"oil_item_ids_by_hand":{}}})
        self.assertIsNone(p.original_verified_F_only_uninstalled({},f))

    def test_existing_gem_role_reuses_source_without_mechanics(self):
        self.assertEqual(p.selected_t1_source_inputs(
            exact_flask_item_id=241326,existing_special_gem_id=240983)[
            "source_selected_gem_roles"],
            {"special_gem_id":240983,"ordinary_gem_ids":None})

    def test_user_cannot_supply_F_rating_or_untrusted_ID(self):
        for raw in ("0","-1"," 241326","1.2","foo","1234567890",241326):
            with self.subTest(raw=raw),self.assertRaisesRegex(
                    ValueError,"P3_GM_EXACT_PHYSICAL_ITEM_ID_INVALID"):
                p.optional_exact_item_id({"EXACT":raw},"EXACT")

    def test_original_full_source_owner_F_is_exposed_only_uninstalled(self):
        selected=241326
        proof={"F":{"selected_flask_item_id":selected,
                    "source_verification":"EXACT_NATIVE",
                    "rating":188,"source_sha256":"a"*64,
                    "native_pair_receipt_sha256":["b"*64,"c"*64]}}
        out=p.original_verified_F_only_uninstalled(
            {"original_J_F_verified_components_not_full_environment":proof},
            selected)
        self.assertEqual(out["F_rating"],188)
        self.assertIsNone(out["official_environment_F"])
        self.assertFalse(out["environment_ready"])
        with self.assertRaisesRegex(ValueError,
                                    "P3_GM_ORIGINAL_F_SOURCE_OWNER_IDENTITY_DRIFT"):
            p.original_verified_F_only_uninstalled(
                {"original_J_F_verified_components_not_full_environment":proof},
                selected+1)

if __name__=="__main__":
    unittest.main()
