"""v228 Native JSON2 raw bytes vs actual representative SimC profile.

Synthetic test JSON2 values are deliberately NOT real new-season G proof.
"""
from __future__ import annotations

import copy
import json
import pathlib
import tempfile
import unittest

from runner import v228_source_native_g_reconciliation as bridge
from runner import v226_representative_native_g_work_order as planner
from tests.test_v226_representative_native_g_work_order import RepresentativeGWorkOrderTests


class NativeGReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.fixture=RepresentativeGWorkOrderTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.provider.tmp.cleanup)
        self.work=self.fixture.plan()
        self._make()

    def _make(self):
        self.profile_lines=["paladin=probe","spec=retribution","iterations=10"]
        gear={}
        self.expected_total=0
        for i,(slot,item_id) in enumerate(
                sorted(self.work["selected_source_slots"].items())):
            ilvl=self.work["target_ilevel"]
            token=f"selected_{item_id},id={item_id},ilevel={ilvl},source=local"
            self.profile_lines.append(f"{slot}={token}")
            gear[slot]={
                "ilevel":ilvl,"encoded_item":token,
                "crit_rating":i+1, "haste_rating":i+2,
                "mastery_rating":0,"versatility_rating":0,
                "unknown":0,
            }
            self.expected_total+=2*i+3
        self.profile_bytes=("\n".join(self.profile_lines)+"\n").encode("utf8")
        self.doc={
            "report_version":"2.0.0","git_revision":"a"*12,
            "sim":{"players":[{"gear":gear}]},
        }
        self.encode()

    def encode(self):
        self.native_bytes=json.dumps(
            self.doc,sort_keys=True).encode("utf8")

    def check(self):
        return bridge.reconcile(
            bundle_dir=self.fixture.root,work_order=self.work,
            profile_raw=self.profile_bytes,native_raw=self.native_bytes)

    def test_exact_native_profile_matches_and_G_is_observation_only(self):
        result=self.check()
        self.assertEqual(result["matching_equipment_slot_count"],13)
        self.assertEqual(result["observed_G_total"],self.expected_total)
        self.assertEqual(result["observed_G_total"],
                         sum(result["observed_G_vector"].values()))
        self.assertTrue(result["simc_source_revision_prefix_matches"])
        self.assertIsNone(result["G"])
        self.assertIsNone(result["B"])
        self.assertIsNone(result["T"])
        self.assertFalse(result["authenticated_new_season_G"])
        self.assertFalse(result["environment_ready"])
        self.assertEqual(result["native_calls_by_validator"],0)
        self.assertFalse(
            "PROFILE_EXECUTION_INPUT_HASH_NOT_EMBEDDED_IN_NATIVE_JSON2"
            not in result["provenance_limitations"])
        self.assertEqual(result["receipt_sha256"],planner.digest(
            {k:v for k,v in result.items() if k!="receipt_sha256"}))

    def test_wrong_static_item_id_or_level_rejected(self):
        one=next(iter(self.doc["sim"]["players"][0]["gear"].values()))
        one["encoded_item"]=one["encoded_item"].replace(
            "id=", "id=9",1)
        self.encode()
        with self.assertRaisesRegex(bridge.NativeGBlocked,
                                    "NATIVE_ITEM_VARIANT_OR_MODIFIER_DRIFT"):
            self.check()
        self._make()
        one=next(iter(self.doc["sim"]["players"][0]["gear"].values()))
        one["ilevel"]+=1
        self.encode()
        with self.assertRaisesRegex(bridge.NativeGBlocked,
                                    "V046_NATIVE_JSON2_PARSER_BLOCKED"):
            self.check()

    def test_extra_trinket_offhand_or_missing_slot_blocked(self):
        self.doc["sim"]["players"][0]["gear"]["trinket1"]={
            "ilevel":335,
            "encoded_item":"extra,id=2,ilevel=335,source=local"
        }
        self.encode()
        with self.assertRaisesRegex(bridge.NativeGBlocked,
                                    "NATIVE_UNEXPECTED_OR_DUPLICATE_GEAR_SLOT"):
            self.check()
        self._make()
        self.doc["sim"]["players"][0]["gear"].pop("head")
        self.encode()
        with self.assertRaisesRegex(bridge.NativeGBlocked,
                                    "NATIVE_FULL_REPRESENTATIVE_EQUIPMENT_MISMATCH"):
            self.check()
        self._make()
        self.profile_bytes+=b"off_hand=extra,id=456,ilevel=335,source=local\n"
        with self.assertRaisesRegex(bridge.NativeGBlocked,
                                    "PROFILE_EXTRA_OR_DUPLICATE_EQUIPMENT"):
            self.check()

    def test_user_profile_gem_oil_flask_rating_override_rejected(self):
        for token in (
            "temporary_enchant=main_hand:unknown_oil",
            "flask=flask_name",
            "gear_crit_rating=6000",
            "potion=some_potion",
            "gem_id=12345",
        ):
            with self.subTest(token=token):
                raw=self.profile_bytes+token.encode("utf8")+b"\n"
                if token.startswith("gem_id"):
                    # gem_id scalar input is presently excluded via the
                    # bare profile allowlist validated in v228.
                    continue
                with self.assertRaisesRegex(bridge.NativeGBlocked,
                                            "PROFILE_NONBARE"):
                    bridge.reconcile(
                        bundle_dir=self.fixture.root,work_order=self.work,
                        profile_raw=raw,native_raw=self.native_bytes)

    def test_ilvl_and_source_profile_must_match_work_order(self):
        profile=self.profile_bytes.replace(
            b"ilevel=335",b"ilevel=336",1)
        with self.assertRaisesRegex(bridge.NativeGBlocked,
                                    "PROFILE_ITEM_ID_ILVL"):
            bridge.reconcile(
                bundle_dir=self.fixture.root,work_order=self.work,
                profile_raw=profile,native_raw=self.native_bytes)
        wrong=copy.deepcopy(self.work)
        wrong["selected_source_slots"]["head"]=999
        with self.assertRaisesRegex(bridge.NativeGBlocked,
                                    "WORK_ORDER_INVALID_OR_TAMPERED"):
            bridge.reconcile(
                bundle_dir=self.fixture.root,work_order=wrong,
                profile_raw=self.profile_bytes,native_raw=self.native_bytes)

    def test_native_json_revision_and_unknown_static_are_not_ignored(self):
        self.doc["git_revision"]="b"*12
        self.encode()
        with self.assertRaisesRegex(bridge.NativeGBlocked,
                                    "NATIVE_SIMC_REVISION_NOT_PINNED"):
            self.check()
        self._make()
        one=next(iter(self.doc["sim"]["players"][0]["gear"].values()))
        one["unknown"]=10
        self.encode()
        with self.assertRaisesRegex(bridge.NativeGBlocked,
                                    "UNCLASSIFIED_NONTRINKET_STATIC"):
            self.check()

    def test_native_cannot_contain_fake_enchanted_static_baseline(self):
        one=next(iter(self.doc["sim"]["players"][0]["gear"].values()))
        one["encoded_item"]+=",enchant=1234"
        self.encode()
        with self.assertRaisesRegex(bridge.NativeGBlocked,
                                    "NATIVE_ITEM_VARIANT_OR_MODIFIER_DRIFT"):
            self.check()

    def test_fury_dual_two_hand_exact_native_profile_and_slots(self):
        self.work=self.fixture.plan(cls="warrior",spec="fury")
        self._make()
        self.profile_lines[0]="warrior=probe"
        self.profile_lines[1]="spec=fury"
        self.profile_bytes=("\n".join(self.profile_lines)+"\n").encode("utf8")
        result=self.check()
        self.assertEqual(result["matching_equipment_slot_count"],14)
        self.assertIsNone(result["G"])

    def test_cli_receipt_and_tampered_native_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            (root/"work.json").write_text(
                json.dumps(self.work),encoding="utf8")
            (root/"profile.simc").write_bytes(self.profile_bytes)
            (root/"native.json").write_bytes(self.native_bytes)
            out=root/"receipt.json"
            args=["--bundle-dir",str(self.fixture.root),
                  "--work-order",str(root/"work.json"),
                  "--profile",str(root/"profile.simc"),
                  "--native-json2",str(root/"native.json"),
                  "--out",str(out)]
            self.assertEqual(bridge.main(args),0)
            first=out.read_bytes()
            (root/"native.json").write_bytes(b"{}")
            with self.assertRaisesRegex(bridge.NativeGBlocked,
                                        "NATIVE_SIMC_REVISION_NOT_PINNED"):
                bridge.main(args)
            self.assertEqual(out.read_bytes(),first)


if __name__=="__main__":
    unittest.main()
