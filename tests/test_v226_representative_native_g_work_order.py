"""v226: one request-specific representative G input; no Native and no fake rating."""
from __future__ import annotations
import copy
import json
import pathlib
import tempfile
import unittest

from runner import v226_representative_native_g_work_order as planner
from runner import v225_season_source_bundle_intake as bundle
from tests.test_v225_season_source_bundle_intake import BundleIntakeTests


class RepresentativeGWorkOrderTests(unittest.TestCase):
    def setUp(self):
        self.provider = BundleIntakeTests()
        self.provider.setUp()
        self.addCleanup(self.provider.tmp.cleanup)
        self.root = self.provider.root

    def plan(self, cls="paladin", spec="retribution", ilevel=335):
        return planner.make_work_order(
            bundle_dir=self.root, event="season_change",
            previous_game_build="12.1.5.70575", target_ilevel=ilevel,
            character_class=cls, specialization=spec)

    def test_retribution_13_actual_source_slots_no_numeric_G(self):
        out=self.plan()
        self.assertEqual(out["status"],
                         "WAIT_EXACT_SOURCE_PROFILE_AND_NATIVE_STATIC_G")
        self.assertEqual(out["weapon_form"],"single_two_hand")
        self.assertEqual(out["weapon_count"],1)
        self.assertEqual(len(out["selected_source_slots"]),13)
        self.assertIn("main_hand",out["selected_source_slots"])
        self.assertNotIn("off_hand",out["selected_source_slots"])
        self.assertNotIn("chest",out["tier_piece_ids"])
        self.assertIsNone(out["G"])
        self.assertIsNone(out["B"])
        self.assertIsNone(out["T"])
        self.assertFalse(out["verified_G"])
        self.assertFalse(out["environment_ready"])
        self.assertFalse(out["measurement_request"]["execute_native_now"])
        self.assertEqual(out["new_native_calls"],0)
        self.assertEqual(out["scope"],"ONE_REQUESTED_SPEC_AND_ITEM_LEVEL")

    def test_fury_2h_two_weapons_and_14_slots(self):
        out=self.plan(cls="warrior",spec="fury")
        self.assertEqual(out["weapon_form"],"dual_two_hand")
        self.assertEqual(out["weapon_count"],2)
        self.assertEqual(len(out["selected_source_slots"]),14)
        self.assertNotEqual(out["selected_source_slots"]["main_hand"],
                            out["selected_source_slots"]["off_hand"])
        self.assertEqual(out["measurement_request"]["native_input"][
            "excluded_slot_rules"],[
            "TRINKET_FIXED_STATS_OUTSIDE_G",
            "NO_J_F_OR_TEMPORARY_OIL_IN_G",
            "NO_USER_CURRENT_EQUIPMENT"])

    def test_source_sha_stable_and_request_is_deterministic(self):
        left=self.plan()
        right=self.plan()
        self.assertEqual(left,right)
        self.assertEqual(left["work_identity_sha256"],
                         left["measurement_request"]["work_identity_sha256"])
        self.assertEqual(left["work_identity_sha256"],
                         planner.digest(left["measurement_request"][
                             "native_input"]))
        self.assertEqual(left["receipt_sha256"],
                         planner.digest({k:v for k,v in left.items()
                                         if k!="receipt_sha256"}))

    def test_ilvl_changes_work_identity_and_never_fills_G(self):
        first=self.plan(ilevel=335)
        second=self.plan(ilevel=336)
        self.assertNotEqual(first["work_identity_sha256"],
                            second["work_identity_sha256"])
        self.assertEqual(first["selected_source_slots"],
                         second["selected_source_slots"])
        self.assertIsNone(second["G"])

    def test_unrelated_budget_source_sha_not_forcing_G_remeasurement(self):
        first=self.plan()
        path=self.root/"budget.json"
        budget=json.loads(path.read_text("utf8"))
        budget["new_candidate_information_only"]="NOT_MEASURED"
        path.write_text(json.dumps(budget,sort_keys=True)+"\n",encoding="utf8")
        self.provider.manifest["sources"]["budget"]["sha256"]=bundle.sha(
            path.read_bytes())
        self.provider.write_manifest()
        second=self.plan()
        self.assertNotEqual(first["source_bundle_receipt_sha256"],
                            second["source_bundle_receipt_sha256"])
        self.assertEqual(first["work_identity_sha256"],
                         second["work_identity_sha256"])
        self.assertIsNone(second["G"])

    def test_stale_gear_sha_fails_before_work_order(self):
        path=self.root/"gear.json"
        path.write_bytes(path.read_bytes()+b" ")
        with self.assertRaisesRegex(bundle.SourceBundleBlocked,
                                    "SOURCE_BYTES_CHANGED"):
            self.plan()

    def test_invalid_spec_fails_no_native_or_fallback(self):
        with self.assertRaisesRegex(planner.GWorkOrderBlocked,
                                    "REPRESENTATIVE_GEAR_NOT_READY"):
            self.plan("evoker","augmentation")
        with self.assertRaisesRegex(planner.GWorkOrderBlocked,
                                    "REPRESENTATIVE_GEAR_NOT_READY"):
            self.plan("warrior","protection")

    def test_cli_writes_only_one_request_and_no_native(self):
        with tempfile.TemporaryDirectory() as td:
            file=pathlib.Path(td)/"work.json"
            self.assertEqual(planner.main([
                "--bundle-dir",str(self.root),"--event","season_change",
                "--previous-game-build","12.1.5.70575",
                "--target-ilevel","335",
                "--class","paladin","--spec","retribution",
                "--out",str(file)]),0)
            data=json.loads(file.read_text(encoding="utf8"))
            self.assertEqual(data["new_native_calls"],0)
            self.assertEqual(data["target_ilevel"],335)
            self.assertFalse(data["profile_native_accepted"])


if __name__=="__main__":
    unittest.main()
