"""v449 B10: existing v280 ItemID→on-use SpellID source to v216 J PENDING.

All fixtures synthetic. Do not certify item use/slots or run HTTP/Native.
"""
import copy
import json
import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v216_environment_build_coordinator as v216


BUILD="12.1.5.70783"
STAGE_ID="fresh-consumable-item-use-spell-source-other"
STAGE_VERSION="v280-real-other-consumables-v2"
OUTPUTS={
    "item_effect":"source/v283_ItemEffect.csv",
    "candidate":"source/v283_consumable_use_spell_candidates.json"}


def item(iid,name,spells,*,kind="item_enhancement",
         on_use=True,selectable=False):
    return {
        "item_id":iid,"name_enUS":name,"kind":kind,
        "ui_selectable":selectable,"expansion_id":11,
        "item_effect_source":{
            "status":("EXACT_DB2_ITEM_TO_ON_USE_SPELL_SOURCE_ONLY"
                      if on_use else "ITEM_USE_SPELL_RELATION_PENDING"),
            "on_use_spell_ids":list(spells)}}


class V449ExistingItemUseOwner(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root=pathlib.Path(self.folder.name)
        self.source=[
            item(275707,"Miasmic Jewelbinder",[1309820]),
            item(263897,"Radiant Jewelbinder",[1270804]),
            item(276187,"Venomous Jeweler's Setting",[1309139]),
            item(244001,"Ordinary Elixir",[121000]),
            item(244002,"Unresolved Jewelbinder",[],on_use=False)]

    def seal(self,*,items=None,build=BUILD):
        row={
            "schema":v216.consumable_item_candidates.SCHEMA,
            "source":{"wago_snapshot_build":build},
            "item_use_spell_join":{
                "schema":v216.item_spell_bridge.SCHEMA,
                "game_build":build,"source_only":True},
            "automatic_ui_promotion":False,
            "items":self.source if items is None else items}
        payload=json.dumps(row,sort_keys=True)
        def execute():
            for file in OUTPUTS.values():
                target=self.root/file
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text(
                    payload if file==OUTPUTS["candidate"] else "ID,SpellID\n",
                    encoding="utf8")
        result=v216.stage_engine.execute_stage(
            root=self.root,stage_id=STAGE_ID,
            stage_version=STAGE_VERSION,
            inputs={"build":build,"synthetic":"v449"},
            outputs=OUTPUTS,execute=execute)
        return {
            "expected_game_build":build,
            "fresh_consumable_item_spell_source":{
                "status":"ITEM_USE_SPELL_SOURCE_JOINED_UNADMITTED",
                "candidate_path":str((self.root/OUTPUTS["candidate"]).resolve()),
                "source_stage":{k:v for k,v in result.items() if k!="result"}}}

    def compilation(self):
        return {"stage_root":str(self.root),
                "status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED"}

    def test_original_sealed_same_build_candidates_are_hints_not_approval(self):
        collected=self.seal()
        source=v216._existing_v280_season_socket_item_source(
            collected,self.compilation())
        self.assertEqual(source["status"],
                         "SAME_BUILD_SOCKET_ITEM_USE_CANDIDATES_UNADMITTED")
        self.assertEqual(source["candidate_count"],3)
        self.assertEqual([x["physical_item_id"] for x in
                          source["physical_candidates_unadmitted"]],
                         [263897,275707,276187])
        m=next(x for x in source["physical_candidates_unadmitted"]
               if x["physical_item_id"]==275707)
        self.assertEqual(m["observed_on_use_spell_ids"],[1309820])
        self.assertFalse(m["same_season_item_applicability_verified"])
        self.assertFalse(m["game_socket_legal_verified"])
        self.assertFalse(source["slot_application_verified"])
        self.assertFalse(source["j_budget_admitted"])
        self.assertTrue(source["same_build_source"])
        self.assertEqual(source["new_native_calls"],0)
        self.assertEqual(source["network_calls"],0)

    def test_selected_extra_stages_in_existing_v216_build_without_j_grant(self):
        collected=self.seal()
        progress={}
        comp=self.compilation()
        attached=v216._fresh_attach_existing_v280_socket_preview(
            collected=collected,compilation=comp,progress=progress,
            selected_roles={"special_gem_id":None,
                            "ordinary_gem_ids":None},socket_total=5)
        self.assertEqual(
            attached,progress["existing_v280_socket_item_source_unadmitted"])
        self.assertEqual(
            attached,comp["existing_v280_socket_item_source_unadmitted"])
        self.assertFalse(attached["j_budget_admitted"])
        self.assertFalse(attached["slot_application_verified"])

    def test_base_four_does_not_read_or_mutate_optional_socket_source(self):
        collected=self.seal()
        progress={}
        comp=self.compilation()
        for roles,total in [(None,5),({"special_gem_id":None},4)]:
            self.assertIsNone(v216._fresh_attach_existing_v280_socket_preview(
                collected=collected,compilation=comp,progress=progress,
                selected_roles=roles,socket_total=total))
        self.assertEqual(progress,{})
        self.assertNotIn("existing_v280_socket_item_source_unadmitted",comp)

    def test_missing_v280_stage_stays_pending_and_does_not_forge_id(self):
        collected=self.seal()
        collected["fresh_consumable_item_spell_source"]={
            "status":"ITEM_USE_SPELL_SOURCE_PENDING"}
        comp=self.compilation()
        result=v216._fresh_attach_existing_v280_socket_preview(
            collected=collected,compilation=comp,progress={},
            selected_roles={"special_gem_id":None},socket_total=5)
        self.assertEqual(result["status"],
                         "SAME_BUILD_SOCKET_ITEM_SOURCE_PENDING")
        self.assertEqual(result["physical_candidates_unadmitted"],[])
        self.assertFalse(result["same_build_source"])

    def test_same_build_source_is_not_the_active_season_gear_permission(self):
        collected=self.seal()
        result=v216._existing_v280_season_socket_item_source(
            collected,self.compilation())
        # Two different season labels are present in one exact-build source;
        # name and on-use ID never establish the target gear's season/PvP.
        self.assertEqual(result["candidate_count"],3)
        for row in result["physical_candidates_unadmitted"]:
            self.assertFalse(row["same_season_item_applicability_verified"])
            self.assertTrue(row["pvp_or_pve_not_inferred_from_name"])

    def test_receipt_output_mutation_fails_closed(self):
        collected=self.seal()
        file=self.root/OUTPUTS["candidate"]
        file.write_text(file.read_text()+" ",encoding="utf8")
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                   "V216_SOCKET_V280_ORIGINAL_OUTPUT_SHA_DRIFT"):
            v216._existing_v280_season_socket_item_source(
                collected,self.compilation())

    def test_tampered_stage_summary_cannot_alias_receipt(self):
        collected=self.seal()
        copied=copy.deepcopy(collected)
        copied["fresh_consumable_item_spell_source"]["source_stage"][
            "receipt_sha256"]="f"*64
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                   "V216_SOCKET_V280_ORIGINAL_RECEIPT_DRIFT"):
            v216._existing_v280_season_socket_item_source(
                copied,self.compilation())

    def test_wrong_build_join_cannot_supply_socket_candidate(self):
        collected=self.seal()
        collected["expected_game_build"]="12.2.0.99999"
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                   "V216_SOCKET_V280_SAME_BUILD_ITEM_JOIN_DRIFT"):
            v216._existing_v280_season_socket_item_source(
                collected,self.compilation())

    def test_non_on_use_or_not_enhancement_or_ui_selected_not_admitted(self):
        collected=self.seal(items=[
            item(275707,"Miasmic Jewelbinder",[1309820],
                 kind="potion"),
            item(263897,"Radiant Jewelbinder",[1270804],
                 selectable=True),
            item(276187,"Venomous Jeweler's Setting",[],on_use=False)])
        result=v216._existing_v280_season_socket_item_source(
            collected,self.compilation())
        self.assertEqual(result["status"],
                         "NO_MATCH_IN_EXISTING_V280_CONSUMABLE_SCOPE")
        self.assertEqual(result["candidate_count"],0)
        self.assertFalse(result["j_budget_admitted"])

    def test_user_selected_j_owner_still_pending_with_source_hints(self):
        from tests.test_v447_b10_v232_intrinsic_socket_owner_boundaries import (
            B10OriginalSocketSourceBoundaries)
        f=B10OriginalSocketSourceBoundaries()
        collected,pre,comp=f.prepare(
            plan_counts={"head":1,"neck":1,"finger1":1,
                         "finger2":1,"wrists":1})
        preview=v216._existing_v280_season_socket_item_source(
            self.seal(),self.compilation())
        comp["existing_v280_socket_item_source_unadmitted"]=preview
        j=v216._fresh_selected_J_intrinsic_socket_source(
            collected=collected,preflight=pre,compilation=comp)
        self.assertEqual(j["status"],
                         "J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING")
        self.assertEqual(
            j["socket_item_source_only_for_unverified_additions"]["candidate_count"],
            3)
        self.assertFalse(j[
            "socket_item_source_only_for_unverified_additions"][
                "game_socket_legal_verified"])
        self.assertFalse(j["J_approved"])


if __name__=="__main__":
    unittest.main()
