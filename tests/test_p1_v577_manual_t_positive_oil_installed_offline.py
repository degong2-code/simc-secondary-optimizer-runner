"""v577: manual inclusive T + sealed selected physical oil O>0 bridge.

Reuses existing synthetic installed-v212 fixture ONLY, not proof of a live
season, source quality admission, real oil stat rating or SimC execution.
Executes the original verified-install retarget and v096 physical-oil bridge:
T is authoritative, B=T-O, cache identity distinct, selection & profile
tampering fail closed, and impossible minima fail before Native.
"""
from __future__ import annotations
import copy
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v096_unified_product_entry as entry
import v216_environment_build_coordinator as coordinator
import v212_environment_manifest as installed
import v222_season_budget_contract as accounting
from test_p1_oil_positive_bridge_offline import PositiveInstalledOil

# This is deliberately NOT a new-season O=16/16 physical observation.
# Existing v577 fixture contains synthetic 16+17 for boundary testing only.
MANUAL_T=3300
SYNTHETIC_O=33

class ManualPositiveOilInstalledBridge(unittest.TestCase):
    def case(self,root):
        doc,cfg,profile,flask,selection,attested=(
            PositiveInstalledOil().case(root))
        # The historical positive-O fixture tests source-id/hand binding
        # but intentionally uses an empty v222 receipt. Construct an
        # internally consistent synthetic v222 arithmetic receipt so the
        # real retarget_verified_install can exercise its strong checks.
        original=doc["v222_reconciled_budget"]
        self.assertEqual(original,{})
        zero={s:0 for s in accounting.STATS}
        typed={
            "game_build":doc["game_build"],
            "simc_revision":doc["simc_revision"],
            "target_ilevel":doc["target_ilevel"],
            "source_catalog_manifest_sha256":
                doc["source_catalog_manifest_sha256"],
            "source_catalog_artifact_sha256":
                doc["source_catalog_artifact_sha256"],
            "reference_G":doc["official_G"],
            "effective_G":doc["official_effective_G"],
            "J":doc["official_J"],"F":doc["official_F"],
            "fixed_O":dict(doc["official_O"]),
            "fixed_L":dict(zero),"fixed_E":dict(zero),
            "reference_B":(doc["official_effective_G"]+
                           doc["official_J"]+doc["official_F"]),
            "base_B":doc["official_B"],"final_T":doc["official_T"],
            "manual_final_T_authoritative":False}
        payload={k:v for k,v in doc.items() if k!="manifest_sha256"}
        payload["v222_reconciled_budget"]=typed
        doc={**payload,"manifest_sha256":installed.sha(
            installed.canonical(payload).encode("utf8"))}
        self.assertTrue(installed.verify_fresh_installed_environment(doc))
        newpath=pathlib.Path(selection["installed_environment_path"]).with_name(
            "v212_installed_"+doc["manifest_sha256"][:20]+".json")
        newpath.write_text(installed.canonical(doc)+"\n",encoding="utf8")
        selection["installed_environment_path"]=str(newpath)
        selection["installed_manifest_sha256"]=doc["manifest_sha256"]
        attested["installed_manifest_sha256"]=doc["manifest_sha256"]
        self.assertEqual(sum(doc["official_O"].values()),SYNTHETIC_O)
        self.assertEqual((doc["official_B"],doc["official_T"]),(3150,3183))
        self.assertEqual(
            doc["official_O_physical_source"][
                "selected_oil_item_ids_by_hand"],{"main_hand":243734})
        return doc,cfg,profile,flask,selection,attested

    def bridge(self,root,cfg,profile,flask,selection,attested):
        with mock.patch.object(coordinator,
                "find_verified_installed_season_environment",
                return_value=attested) as found:
            result=entry._admitted_fresh_season_source(
                manifest_path=root/"manifest.json",season=selection,
                revision="new-simc-revision-must-not-rewrite-static-O",
                user_scenario=cfg,flask_F=flask,
                oil_hands=["main_hand"],profile=profile)
            found.assert_called_once_with(
                root.resolve(),334,expected_game_build="12.1.5.70783",
                expected_installed_manifest_sha256=
                    selection["installed_manifest_sha256"],
                selected_oil_item_ids_by_hand={"main_hand":243734})
        return result

    def test_manual_T_retarget_and_original_profile_owner_exactly_once(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            doc,cfg,profile,flask,selection,attested=self.case(root)
            original=self.bridge(root,cfg,profile,flask,selection,attested)
            self.assertEqual(
                (original["season_budget"]["base_B"],
                 original["season_budget"]["final_T"]),(3150,3183))
            self.assertIsNone(original["user_manual_final_T"])
            self.assertEqual(
                original["season_budget"]["fixed_O"],doc["official_O"])
            adjusted=accounting.retarget_verified_install(
                document=doc,manual_final_T=MANUAL_T)
            self.assertEqual((adjusted["base_B"],adjusted["final_T"]),
                             (MANUAL_T-SYNTHETIC_O,MANUAL_T))
            self.assertTrue(adjusted["manual_final_T_authoritative"])
            self.assertEqual(adjusted["fixed_O"],doc["official_O"])
            self.assertEqual(adjusted["installed_reference_T"],3183)
            self.assertEqual(adjusted["user_budget_source_installed_manifest_sha256"],
                             doc["manifest_sha256"])
            manual=copy.deepcopy(selection)
            manual["user_final_T"]=MANUAL_T
            scenario=copy.deepcopy(cfg)
            scenario["target"]["manual_total"]=MANUAL_T-SYNTHETIC_O
            verified=self.bridge(root,scenario,profile,flask,manual,attested)
            self.assertEqual(
                (verified["season_budget"]["base_B"],
                 verified["season_budget"]["final_T"],
                 verified["user_manual_final_T"]),
                (MANUAL_T-SYNTHETIC_O,MANUAL_T,MANUAL_T))
            self.assertEqual(
                verified["season_budget"]["fixed_O"],doc["official_O"])
            self.assertEqual(verified["oil_by_hand"],
                             selection["oil_by_hand"])
            self.assertEqual(
                verified["season_source_identity"]["environment_build_receipt_sha256"],
                doc["manifest_sha256"])
            self.assertNotEqual(
                verified["season_source_identity"]["source_input_sha256"],
                original["season_source_identity"]["source_input_sha256"])
            self.assertEqual(profile.count(
                "temporary_enchant=main_hand:thalassian_phoenix_oil_2"),1)
            # Same final T still has explicit manual identity, not auto T.
            equal=copy.deepcopy(selection)
            equal["user_final_T"]=3183
            same=self.bridge(root,cfg,profile,flask,equal,attested)
            self.assertEqual(same["season_budget"]["final_T"],3183)
            self.assertNotEqual(
                same["season_source_identity"]["source_input_sha256"],
                original["season_source_identity"]["source_input_sha256"])
            self.assertEqual(doc["official_T"],3183,
                             "signed installed source must remain immutable")
            self.assertFalse((root/"manifest.json").exists(),
                             "preflight must not start/seed Native or write manifests")

    def test_t_below_fixed_floor_and_unknown_physical_oil_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            doc,cfg,profile,flask,selection,attested=self.case(root)
            with self.assertRaisesRegex(
                 accounting.SeasonBudgetBlocked,
                 "GJFO_FIXED_MINIMA_EXCEED_TOTAL"):
                accounting.retarget_verified_install(
                    document=doc,manual_final_T=SYNTHETIC_O)
            bad=copy.deepcopy(selection)
            # Legacy v061 requires positive internal B; give it B=1,
            # which is validly typed but still far below fixed J/F minima.
            bad["user_final_T"]=SYNTHETIC_O+1
            cfg_bad=copy.deepcopy(cfg)
            cfg_bad["target"]["manual_total"]=1
            # The existing v061 candidate feasibility check correctly
            # blocks this before the later v222 retarget can be reached.
            # The direct v222 retarget above independently confirms the
            # J/F/L/E floor on the signed installed accounting source.
            with self.assertRaisesRegex(
                Exception,"UNFEASIBLE_MANUAL_TOTAL_BOUNDS"):
                self.bridge(root,cfg_bad,profile,flask,bad,attested)
            manual=copy.deepcopy(selection)
            manual["user_final_T"]=MANUAL_T
            cfg_manual=copy.deepcopy(cfg)
            cfg_manual["target"]["manual_total"]=MANUAL_T-SYNTHETIC_O
            broken=copy.deepcopy(manual)
            broken["oil_by_hand"]["main_hand"]["physical_item_id"]=999
            with self.assertRaisesRegex(
                  entry.EntryBlocked,
                  "FRESH_SEASON_POSITIVE_O_VERIFIED_PHYSICAL_SOURCE_DRIFT"):
                self.bridge(root,cfg_manual,profile,flask,broken,attested)
            with self.assertRaisesRegex(
                  entry.EntryBlocked,
                  "FRESH_SEASON_POSITIVE_O_SIMC_PROFILE_DRIFT"):
                self.bridge(root,cfg_manual,
                    profile.replace("thalassian_phoenix_oil_2",
                                    "unverified_oil_token"),
                    flask,manual,attested)
            self.assertFalse((root/"manifest.json").exists())
if __name__=="__main__":
    unittest.main()
