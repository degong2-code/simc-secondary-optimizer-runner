"""Versioned season data change planning; 0 Native, no runtime promotion."""
import contextlib
import copy
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v139_pure_target_profile_composer as composer
import v151_season_catalog_impact as updater

class SeasonCatalogUpdatePlanOffline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=composer.catalog()
        cls.specs=sorted(cls.old["specializations"])
        assert len(cls.specs)==26

    def diff(self,change):
        after=copy.deepcopy(self.old)
        change(after)
        return updater.compare(self.old,after)

    def test_identical_and_metadata_only_never_require_native(self):
        same=updater.compare(self.old,copy.deepcopy(self.old))
        self.assertEqual(same["native_calls_performed"],0)
        self.assertEqual(same["needs_physical_acceptance_review"],[])
        self.assertEqual(same["needs_adaptive_dps_review"],[])
        self.assertFalse(same["metadata_only_change"])
        changed=self.diff(lambda d:d.update(status="NEW_REVIEW_LABEL"))
        self.assertTrue(changed["metadata_only_change"])
        self.assertFalse(changed["actual_profile_or_dps_inputs_changed"])
        self.assertEqual(changed["next_action"],
                         "NO_NATIVE_FOR_METADATA_OR_IDENTICAL_CATALOG")
        self.assertFalse(changed["product_support_for_new_level_or_season_granted"])

    def test_one_specialization_item_or_tier_change_impacts_only_that_spec(self):
        spec="demonhunter/havoc"
        def edit(d):
            d["specializations"][spec]["ordinary"]["feet"]=283431
        result=self.diff(edit)
        self.assertEqual(result["needs_physical_acceptance_review"],[spec])
        self.assertEqual(result["needs_adaptive_dps_review"],[spec])
        self.assertEqual(result["changed_specialization_fields"],{spec:["ordinary"]})
        self.assertEqual(result["physical_reasons"][spec],["ordinary"])
        self.assertTrue(result["may_reuse_unchanged_static_cache_records"])
        self.assertFalse(result["same_season_static_records_always_invalidated"])
        self.assertFalse(result["dps_cache_reuse_of_affected_scenarios_without_identity_recheck"])
        self.assertEqual(result["native_calls_auto_authorized"],0)

    def test_global_item_or_gem_change_requires_scoped_all_specs_review(self):
        def edit(d):
            d["gems"]["head"]="new_gem_test"
        changed=self.diff(edit)
        self.assertEqual(changed["needs_physical_acceptance_review"],self.specs)
        self.assertEqual(changed["needs_adaptive_dps_review"],self.specs)
        self.assertFalse(changed["budget_policy_review_required"])
        self.assertEqual(changed["native_calls_auto_authorized"],0)

    def test_consumable_effect_change_alone_does_not_force_extra_physical_native(self):
        def edit(d):
            d["default_consumables"]["potion"]="new_potion_for_diff_test"
        changed=self.diff(edit)
        self.assertEqual(changed["needs_physical_acceptance_review"],[])
        self.assertEqual(changed["needs_adaptive_dps_review"],self.specs)
        self.assertFalse(changed["budget_policy_review_required"])
        self.assertEqual(changed["native_calls_performed"],0)

    def test_chmv_f_and_j_budget_changes_get_explicit_budget_review(self):
        def edit(d):
            d["default_consumables"]["flask_budget_F"]=170
            d["default_consumables"]["gem_budget_J"]=140
        changed=self.diff(edit)
        self.assertTrue(changed["budget_policy_review_required"])
        self.assertEqual(changed["changed_consumable_budget_fields"],
                         ["flask_budget_F","gem_budget_J"])
        self.assertEqual(changed["needs_adaptive_dps_review"],self.specs)

    def test_level_and_season_swap_use_same_compiler_but_no_auto_promotion(self):
        def edit(d):
            d["season"]="future_season_candidate"
            d["target_ilevel"]=321
        changed=self.diff(edit)
        self.assertEqual(changed["needs_physical_acceptance_review"],self.specs)
        self.assertTrue(changed["budget_policy_review_required"])
        self.assertFalse(changed["product_support_for_new_level_or_season_granted"])
        actor={"class":"druid","spec":"balance","race":"night_elf",
               "talents":"CYGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWoMbNjxMDwsYmZmZhBjZZmlZYmZswyMLzMGzshhBYstMzgxsNCMBAAAYxMzMzgNDjxAAwMDMA"}
        trinkets=[{"slot":x,"item_id":y,"options":{}}
                  for x,y in [("trinket1",250215),("trinket2",281215)]]
        with mock.patch("subprocess.run") as external_simc:
            new=copy.deepcopy(self.old);edit(new)
            profile,meta,rows,_=composer.compose(actor,trinkets,
                           target_ilevel=321,season=new)
            external_simc.assert_not_called()
        self.assertIn("ilevel=321",profile)
        self.assertEqual(meta["status"],"STAGED_NOT_USER_READY")
        self.assertEqual(rows["main_hand"]["ilevel"],321)

    def test_future_catalog_can_use_simc_local_item_db_without_second_source(self):
        # Existing v144's profile is left unchanged (hash/cache compatible).
        actor={"class":"druid","spec":"balance","race":"night_elf",
               "talents":"CYGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWoMbNjxMDwsYmZmZhBjZZmlZYmZswyMLzMGzshhBYstMzgxsNCMBAAAYxMzMzgNDjxAAwMDMA"}
        trinkets=[{"slot":x,"item_id":y,"options":{}}
                  for x,y in [("trinket1",250215),("trinket2",281215)]]
        original,_,_,_=composer.compose(actor,trinkets,season=self.old)
        self.assertNotIn("item_db_source=",original)
        selected=copy.deepcopy(self.old)
        selected["simc_item_db_source"]="local"
        with mock.patch("subprocess.run") as external_simc:
            profile,meta,_,_=composer.compose(actor,trinkets,season=selected)
            external_simc.assert_not_called()
        self.assertTrue(profile.startswith("item_db_source=local\\n"))
        self.assertEqual(profile.count("item_db_source=local"),1)
        self.assertIn("default_actions=1",profile)
        self.assertIn("ilevel=334",profile)
        self.assertEqual(meta["status"],"STAGED_NOT_USER_READY")
        changed=updater.compare(self.old,selected)
        self.assertEqual(changed["needs_physical_acceptance_review"],self.specs)
        self.assertEqual(changed["needs_adaptive_dps_review"],self.specs)
        self.assertEqual(changed["bundled_simc_item_source_policy"],"local")
        self.assertFalse(changed["automatic_item_roster_discovery_implemented"])
        self.assertFalse(changed["product_support_for_new_level_or_season_granted"])
        self.assertEqual(changed["native_calls_performed"],0)

    def test_simc_item_source_does_not_silently_allow_network_fallback(self):
        candidate=copy.deepcopy(self.old)
        candidate["simc_item_db_source"]="local|wowhead"
        with self.assertRaisesRegex(composer.ProfileStageBlocked,
                                     "ONLY_SIMC_LOCAL_ITEM_DATA_SOURCE_SUPPORTED"):
            composer.validate_season(candidate)
        candidate["simc_item_db_source"]="wowhead"
        with self.assertRaisesRegex(composer.ProfileStageBlocked,
                                     "ONLY_SIMC_LOCAL_ITEM_DATA_SOURCE_SUPPORTED"):
            updater.compare(self.old,candidate)

    def test_unknown_new_field_requires_human_review_not_silent_acceptance(self):
        changed=self.diff(lambda d:d.update(new_damage_formula={"x":1}))
        self.assertEqual(changed["needs_physical_acceptance_review"],self.specs)
        self.assertIn("new_damage_formula",
                      changed["unclassified_changes_require_human_review"])
        self.assertEqual(changed["next_action"],
                         "REVIEW_UNCLASSIFIED_FIELDS_BEFORE_RELEASE")

    def test_data_import_cli_only_reads_two_files_and_outputs_plan(self):
        with tempfile.TemporaryDirectory() as temp:
            before=pathlib.Path(temp)/"before.json"
            after=pathlib.Path(temp)/"after.json"
            before.write_text(json.dumps(self.old),encoding="utf8")
            updated=copy.deepcopy(self.old)
            updated["specializations"]["mage/frost"]["tier_ids"]["head"]=282481
            after.write_text(json.dumps(updated),encoding="utf8")
            out=io.StringIO()
            with contextlib.redirect_stdout(out), \
                 mock.patch("subprocess.run") as simc:
                status=updater.main(["--before",str(before),
                                     "--after",str(after)])
                simc.assert_not_called()
            self.assertEqual(status,0)
            plan=json.loads(out.getvalue())
            self.assertEqual(plan["needs_physical_acceptance_review"],["mage/frost"])
            self.assertEqual(plan["native_calls_performed"],0)
            self.assertNotIn("C:\\Users\\",out.getvalue())

if __name__=="__main__":unittest.main()
