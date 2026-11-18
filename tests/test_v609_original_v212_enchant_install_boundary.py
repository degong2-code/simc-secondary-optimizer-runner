"""v609: original sealed v212 installer consumes v220 Policy A enchant receipts.

Fixtures and budget amounts here are SYNTHETIC and are never a season source,
a user-executable Native acceptance, or an authorization to publish IDs.
No new source fetch, Native call, or optimizer implementation.
"""
import copy
import json
import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
sys.path.insert(0,str(ROOT))

from runner import v211_enchant_source_effect_classification as classify
from runner import v213_source_to_catalog as join
from runner import v216_environment_build_coordinator as build
from runner import v220_catalog_auto_admission as policy
from runner import v096_unified_product_entry as product
from runner import v196_current_season_user_catalog as ui
from runner import v212_environment_manifest as install
from runner import v222_season_budget_contract as budget
from tests.test_v240_v211_v213_fresh_catalog_handoff import SameFreshCatalogChain
from tests.test_v239_v211_fresh_season_dynamic_classifier import (
    fixture_source, put_sources)


class OriginalInstallerOneVerifiedE0Choice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SameFreshCatalogChain.setUpClass()

    def test_signed_internal_E0_ordinary_enchant_installed_and_budget_preview(self):
        # Take the existing new-season synthetic fixture, convert only one
        # ordinary gear source row to a SimC-owned spell enchant. No actual
        # physical season or native behavior is asserted by this test.
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            season,_=SameFreshCatalogChain().inputs(root)
            _,sources=fixture_source()
            row=next(r for r in season["enchants"]["current_season"][
                "highest_rank_candidates"] if r["enchant_id"]==91001)
            row["simc_token"]="enchant_boots__future_spell"
            row["inventory_type_mask"]=1<<8
            row["inventory_type_options"]=[8]
            sources["permanent_enchant.inc"]=(
                sources["permanent_enchant.inc"]
                    .replace("enchant_ring__new_haste","enchant_boots__future_spell")
                    .replace("0x800","0x100"))
            # The previous synthetic haste enchant has a STATIC CHMV item
            # modifier; a new source spell cannot inherit an imagined E0.
            # Replace its actual generated DBC row with an equip spell path.
            rows=[]
            for line in sources["spell_item_enchantment.inc"].splitlines():
                if line.startswith("{ 91001,"):
                    line=line.replace("{ 5, 0, 0 }","{ 3, 0, 0 }").replace(
                        "{ 36, 0, 0 }","{ 1234567, 0, 0 }")
                rows.append(line)
            sources["spell_item_enchantment.inc"]="\n".join(rows)+"\n"
            manifest=put_sources(root,sources)
            classified=classify.compile_fresh_season(season,root,manifest)
            actual=next(r for r in classified["rows"]
                        if r["enchant_id"]==91001)
            self.assertFalse(actual["static_chmv_rating_present_in_dbc"])
            self.assertEqual(actual["effect_family"],"simc_spell_effect")
            self.assertEqual(len(actual["spell_effects"]),1)
            source=join.compile_catalog(
                season,"a"*64,classified,"b"*64)
            self.assertTrue(join.verify_catalog(source))
            artifact_sha=install.sha(install.canonical(source).encode("utf8"))
            stage_root=root/"_fresh_season_sources"/(
                "wago_"+source["game_build"])
            stage_root.mkdir(parents=True)
            source_path=stage_root/"fresh_source"/"v213_candidate_catalog.json"
            source_path.parent.mkdir()
            source_path.write_text(install.canonical(source),encoding="utf8")
            preflight={
                "schema":"v216_new_season_source_preflight_v1",
                "status":"FRESH_SOURCE_CANDIDATES_VALID_GJFO_PENDING_NOT_INSTALLED",
                "game_build":source["game_build"],
                "simc_revision":source["simc_revision"],
                "source_artifact_sha256":artifact_sha,
                "source_catalog_manifest_sha256":source["manifest_sha256"],
                "environment_ready":False,"approved_new_choices":0,
                "G":None,"J":None,"F":None,"O":None,"B":None,"T":None,
                "requires":["G/J/F/O_VERIFIED_SOURCE_RECEIPTS"]}
            preflight["preflight_sha256"]=install.sha(
                install.canonical(preflight).encode("utf8"))
            compilation={
                "status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                "simc_revision":source["simc_revision"],
                "preflight_sha256":preflight["preflight_sha256"],
                "environment_ready":False,"stage_root":str(stage_root),
                "source_catalog_path":str(source_path),
                **{key:{"status":"REUSED_VERIFIED",
                        "receipt_sha256":str(i)*64}
                   for i,key in enumerate(
                       ("v191_stage","v211_stage","v213_stage"),1)}}
            staged=build._stage_source_environment_only(
                compilation=compilation,preflight=preflight,
                target_ilevel=334)
            staged_doc=json.loads(pathlib.Path(
                staged["stage_output_path"]).read_text("utf8"))
            zero=dict.fromkeys(budget.STATS,0)
            def component(value,seed):
                return {"rating":value,"game_build":source["game_build"],
                    "source_catalog_manifest_sha256":source["manifest_sha256"],
                    "source_sha256":seed*64,
                    "source_verification":"VALID_SAME_SEASON_SOURCE"}
            trusted_budget={
                "schema":budget.SCHEMA,"game_build":source["game_build"],
                "simc_revision":source["simc_revision"],
                "source_catalog_manifest_sha256":source["manifest_sha256"],
                "source_catalog_artifact_sha256":artifact_sha,
                "target_ilevel":334,
                "components":{"G":component(2800,"4"),
                              "J":component(140,"5"),
                              "F":component(170,"6"),
                              "O":budget.explicit_no_oil_component(
                                  game_build=source["game_build"],
                                  source_catalog_manifest_sha256=
                                      source["manifest_sha256"],
                                  selected_oil_item_ids_by_hand={})},
                "fixed_L":dict(zero),"fixed_E":dict(zero),
                "G_reference_excludes_selected_E":True}
            public=ui.public_options(source_path)
            row_ui=next(r for r in public["enchant_candidates"]["items"]
                        if r["enchant_id"]==91001)
            original=next(r for r in source["catalog"]["enchants"]["items"]
                          if r["enchant_id"]==91001)
            context={"game_build":source["game_build"],
                     "simc_revision":source["simc_revision"],
                     "manifest_sha256":source["manifest_sha256"]}
            identity=policy._identity(policy.candidate_from_source_enchant(
                context,row_ui,original_source_row=original))
            # v607 source-producing boundary has its own SHA/tamper tests.
            # These synthetic proof values test consumer wiring ONLY.
            receipts={kind:{"identity":dict(identity),"status":status,
                            "evidence_sha256":str(i)*64}
                      for i,(kind,status) in enumerate(
                          policy.PROOF_STATUSES.items(),1)}
            receipts["product_input"].update({
                "exact_application_scope_verified":True,
                "source_quality_family_verified":True,
                "same_build_physical_join_verified":True,
                "quality_source_sha256":"f"*64,
                "verified_quality_rank":row_ui["highest_source_quality_rank"]})
            receipts["chmv_budget"].update({
                "no_double_count":True,"unknown_static_chmv":False,
                "fixed_E":dict(zero)})
            choice=policy.decide(policy.candidate_from_source_enchant(
                context,row_ui,original_source_row=original),receipts)
            self.assertTrue(choice["eligible"])
            installed=install.compile_fresh_installed_environment(
                source_catalog=source,
                source_artifact_sha256=artifact_sha,
                staged_source_environment=staged_doc,
                trusted_budget_evidence=trusted_budget,
                source_ui=public,
                trusted_policy_A_receipts_by_id={91001:receipts},
                target_ilevel=334)
            self.assertTrue(install.verify_fresh_installed_environment(installed))
            published=installed["published_verified_options"]
            self.assertEqual(len(published),1)
            self.assertEqual(published[0]["enchant_id"],91001)
            self.assertEqual(published[0]["slot"],"feet")
            self.assertEqual(published[0]["verified_fixed_E"],zero)
            self.assertEqual(installed["published_verified_option_count"],1)
            self.assertEqual((installed["official_B"],installed["official_T"]),
                             (3110,3110))
            preview=install.preview_installed_selected_enchant_budget(
                document=installed,slot="feet",item_id=987654,
                enchant_id=91001)
            self.assertTrue(preview["fixed_E_zero_is_valid"])
            self.assertEqual((preview["base_B"],preview["final_T"]),(3110,3110))
            self.assertTrue(preview["user_physical_item_and_simc_profile_binding_pending"])
            manual=install.preview_installed_selected_enchant_budget(
                document=installed,slot="feet",item_id=987654,
                enchant_id=91001,manual_final_T=3500)
            self.assertEqual((manual["base_B"],manual["final_T"]),(3500,3500))
            self.assertTrue(manual["manual_final_T_authoritative"])
            # The original v096 consumer must observe the EXACT final
            # physical item and enchant ID once; spell DPS belongs to SimC.
            selected={"identity_sha256":preview["selected_identity_sha256"],
                      "slot":"feet","item_id":987654,"enchant_id":91001}
            base_profile="finger1=id=111\nfinger2=id=222\n"
            actual_profile=base_profile+"feet=id=987654,enchant_id=91001\n"
            consumed=product._signed_installed_user_E0_profile(
                doc=installed,selected=selected,
                profile=actual_profile,user_final_T=None)
            self.assertEqual(consumed["selected_identity_sha256"],
                             preview["selected_identity_sha256"])
            self.assertEqual(consumed["fixed_E"],zero)
            with self.assertRaisesRegex(
                    product.EntryBlocked,
                    "FRESH_SELECTED_E0_EXACT_ONCE_SIMC_INPUT_REQUIRED"):
                product._signed_installed_user_E0_profile(
                    doc=installed,selected=selected,
                    profile=actual_profile+
                        "chest=id=333,enchant_id=91001\n",
                    user_final_T=None)
            with self.assertRaisesRegex(
                    install.EnvironmentBlocked,"FRESH_SELECTED_ENCHANT_USER_SLOT_OUTSIDE_ORIGINAL_MASK"):
                install.preview_installed_selected_enchant_budget(
                    document=installed,slot="finger1",item_id=987654,
                    enchant_id=91001)
            # The same core budget must install normally when no optional
            # enchant is verified; a candidate is NOT a base G/J/F/O gate.
            baseline=install.compile_fresh_installed_environment(
                source_catalog=source,source_artifact_sha256=artifact_sha,
                staged_source_environment=staged_doc,
                trusted_budget_evidence=trusted_budget,source_ui=public,
                trusted_policy_A_receipts_by_id={},target_ilevel=334)
            self.assertEqual(baseline["published_verified_options"],[])
            self.assertEqual(baseline["official_T"],installed["official_T"])
            self.assertNotEqual(baseline["manifest_sha256"],
                                installed["manifest_sha256"])


if __name__=="__main__":
    unittest.main()
