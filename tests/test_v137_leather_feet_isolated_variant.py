"""P1 isolated leather-feet physical variant: deterministic, zero Native."""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))

import v102_ordinary_armor_seed_pool as pool
import v132_dps_source_batch_smoke as pins
import v133_mid2_target_representative_preview as preview
import v137_leather_feet_isolated_variant as stage


class IsolatedLeatherFeetVariant(unittest.TestCase):
    def test_only_havoc_feet_id_changes_while_all_other_rows_and_apl_match(self):
        report,baseline,variant=stage.stage()
        self.assertEqual(report["spec"],"demonhunter/havoc")
        self.assertEqual(report["changed_slots"],["feet"])
        self.assertEqual(report["old_item_id"],159327)
        self.assertEqual(report["new_item_id"],268261)
        self.assertEqual(report["native_calls"],0)
        self.assertFalse(report["user_default_profile_changed"])
        self.assertFalse(report["historical_dps_cache_changed"])
        self.assertFalse(report["target_variant_native_verified"])
        self.assertFalse(report["exact_target_static_rating_verified"])
        b=baseline.splitlines()
        v=variant.splitlines()
        self.assertEqual(len(b),len(v))
        changed=[(x,y) for x,y in zip(b,v) if x!=y]
        self.assertEqual(len(changed),1)
        old,new=changed[0]
        self.assertTrue(old.startswith("feet="))
        self.assertEqual(
            old.replace("selected_159327","selected_268261")
               .replace(",id=159327",",id=268261"),
            new)
        self.assertIn("enchant_id=7963",new)
        self.assertEqual(report["baseline_sha256"],
                         hashlib.sha256(baseline.encode()).hexdigest())
        self.assertEqual(report["variant_sha256"],
                         hashlib.sha256(variant.encode()).hexdigest())

    def test_existing_v133_baseline_and_source_bytes_remain_unchanged(self):
        report,baseline,variant=stage.stage()
        original,expected=preview.draft("demonhunter/havoc",334)
        self.assertEqual(baseline,expected)
        self.assertEqual(report["baseline_sha256"],original["profile_sha256"])
        self.assertEqual(pins.validate_source("demonhunter/havoc")["source"]
                         .count("feet=sandshined_snakeskin_sandals"),1)
        self.assertEqual(pins.validate_source("druid/feral")["source"]
                         .count("feet=bespittled_slitherslippers"),1)
        self.assertEqual(pool.provenance("leather","feet")["item_id"],268261)
        self.assertNotEqual(variant,baseline)

    def test_source_seed_id_drift_fails_closed_without_native(self):
        with mock.patch.object(pool,"row",return_value={
             "slot":"feet","item_id":159304,"ilevel":334,"options":{}}):
            with self.assertRaisesRegex(stage.VariantBlocked,
                                        "V137_LEATHER_FEET_SEED_CHANGED"):
                stage.stage()
        self.assertEqual(stage.stage()[0]["native_calls"],0)

    def test_unexpected_existing_feet_option_changes_are_refused(self):
        real=preview.draft
        def modified(key,ilevel):
            result,profile=real(key,ilevel)
            return result,profile.replace("enchant_id=7963",
                                         "enchant_id=9999",1)
        with mock.patch.object(preview,"draft",side_effect=modified):
            with self.assertRaisesRegex(stage.VariantBlocked,
                                        "V137_BASELINE_FEET_OPTIONS_CHANGED"):
                stage.stage()

    def test_output_files_are_immutable_idempotent_and_not_user_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=pathlib.Path(tmp)
            report=stage.write_stage(folder)
            self.assertEqual(stage.write_stage(folder),report)
            profiles=folder/"profiles"
            self.assertEqual(set(x.name for x in profiles.iterdir()),
                 {"demonhunter__havoc__baseline.simc",
                  "demonhunter__havoc__leather_feet_268261.simc"})
            saved=json.loads((folder/"V137_LEATHER_FEET_VARIANT.json")
                             .read_text(encoding="utf8"))
            self.assertEqual(saved,report)
            self.assertFalse((folder/"V094_RESULT.json").exists())
            self.assertFalse((folder/"runs").exists())
            candidate=profiles/"demonhunter__havoc__leather_feet_268261.simc"
            candidate.write_text("tampered\n",encoding="utf8")
            with self.assertRaisesRegex(stage.VariantBlocked,
                                        "V137_OUTPUT_IDENTITY_DRIFT"):
                stage.write_stage(folder)
            self.assertEqual(candidate.read_text(),"tampered\n")

    def test_rejects_profile_filename_or_missing_seed_without_fabrication(self):
        with mock.patch.object(pool,"provenance",return_value={
                "source_kind":"legacy_reference"}):
            with self.assertRaisesRegex(stage.VariantBlocked,
                                        "V137_NOT_SAME_SEASON_ORDINARY"):
                stage.stage()


if __name__=="__main__":
    unittest.main()
