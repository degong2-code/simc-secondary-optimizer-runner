"""v455 B10: source-only original v281 spell rows follow sealed v280 items.

Synthetic v217 fixtures verify identity, missing stages, and no J approval.
The real 70783 four-spell observation is stored separately by v454.
"""
from __future__ import annotations
import copy
import json
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v216_environment_build_coordinator as v216
from tests.test_v449_b10_existing_v280_socket_item_owner import (
    V449ExistingItemUseOwner)
from tests.test_v447_b10_v232_intrinsic_socket_owner_boundaries import (
    B10OriginalSocketSourceBoundaries)

STAGE="fresh-consumable-simc-spell-effect-source-other"
VERSION="v281-real-other-consumables-v2"
OUTPUTS={
    "spell_effect":"source/v284_SpellEffect.csv",
    "candidate":"source/v284_simc_consumable_relations.json"}
EFFECTS={
    1270804:[(314,5523,0),(3,0,1)],
    1309820:[(359,181,0),(359,184,1),(3,0,2)],
    1309139:[(359,180,0),(3,0,1)]}


class SealedExistingV281SocketOwner(unittest.TestCase):
    def setUp(self):
        self.fixture=V449ExistingItemUseOwner()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root=self.fixture.root
        self.collected=self.fixture.seal()

    def compilation(self):
        return self.fixture.compilation()

    def seal_v281(self,*,item_mutation=None,build="12.1.5.70783"):
        path=self.root/"source"/"v283_consumable_use_spell_candidates.json"
        source=json.loads(path.read_text(encoding="utf8"))
        for item in source["items"]:
            ids=item["item_effect_source"]["on_use_spell_ids"]
            rows=[{
                "spell_id":sid,"effect":e,"enchant_id":misc,
                "effect_index":idx,"difficulty_id":0}
                for sid in ids for e,misc,idx in EFFECTS.get(sid,[])]
            item["spell_effect_source"]={
                "on_use_spell_ids":list(ids),
                "status":("SAME_BUILD_SPELL_EFFECT_SOURCE_ONLY"
                          if rows else "SPELL_EFFECT_SOURCE_PENDING"),
                "observed_spell_effects":rows}
        if item_mutation is not None:
            item_mutation(source)
        source["simc_relation_source"]={
            "schema":v216.consumable_simc_relation.SCHEMA,
            "game_build":build}
        payload=json.dumps(source,sort_keys=True)
        def execute():
            for name,rel in OUTPUTS.items():
                dst=self.root/rel
                dst.parent.mkdir(parents=True,exist_ok=True)
                dst.write_text(payload if name=="candidate"
                               else "SpellID,Effect,EffectIndex\n",
                               encoding="utf8")
        stage=v216.stage_engine.execute_stage(
            root=self.root,stage_id=STAGE,stage_version=VERSION,
            inputs={"build":build,"synthetic":"v455"},
            outputs=OUTPUTS,execute=execute)
        self.collected["fresh_consumable_simc_effect_relation"]={
            "status":"SIMC_CONSUMABLE_RELATIONS_SOURCE_ONLY",
            "candidate_path":str((self.root/OUTPUTS["candidate"]).resolve()),
            "source_stage":{k:v for k,v in stage.items() if k!="result"}}
        return stage

    def previews(self):
        comp=self.compilation()
        v280=v216._existing_v280_season_socket_item_source(
            self.collected,comp)
        v281=v216._existing_v281_season_socket_spell_effect_source(
            self.collected,comp,v280)
        return v280,v281

    def test_original_v281_three_candidate_effects_exact_and_unadmitted(self):
        self.seal_v281()
        v280,v281=self.previews()
        self.assertEqual(v281["status"],
                         "SAME_BUILD_V281_SOCKET_SPELL_EFFECTS_UNADMITTED")
        self.assertEqual(v281["candidate_count"],v280["candidate_count"])
        by_id={r["physical_item_id"]:r for r in
               v281["spell_effect_candidates_unadmitted"]}
        self.assertEqual(sorted(by_id),[263897,275707,276187])
        self.assertEqual([r["effect"] for r in by_id[275707][
            "observed_source_effect_rows"]],[359,359,3])
        self.assertEqual(by_id[275707]["on_use_spell_ids"],[1309820])
        self.assertTrue(v281["same_build_source"])
        self.assertFalse(v281["effect_chain_verified"])
        self.assertFalse(v281["j_budget_admitted"])
        self.assertFalse(v281["slot_application_verified"])
        self.assertEqual(v281["new_native_calls"],0)
        self.assertEqual(v281["network_calls"],0)

    def test_source_only_v281_missing_stays_pending(self):
        v280,v281=self.previews()
        self.assertTrue(v280["same_build_source"])
        self.assertEqual(v281["status"],
                         "SAME_BUILD_SOCKET_SPELL_EFFECT_SOURCE_PENDING")
        self.assertIsNone(v281["v281_stage_receipt_sha256"])

    def test_real_v280_item_spell_rows_do_not_approve_J(self):
        self.seal_v281()
        comp=self.compilation()
        progress={}
        preview=v216._fresh_attach_existing_v280_socket_preview(
            collected=self.collected,compilation=comp,progress=progress,
            selected_roles={"special_gem_id":None},socket_total=5)
        self.assertEqual(preview["candidate_count"],3)
        rows=comp["existing_v281_socket_spell_source_unadmitted"]
        self.assertEqual(rows["candidate_count"],3)
        self.assertIs(rows,progress["existing_v281_socket_spell_source_unadmitted"])
        self.assertFalse(rows["j_budget_admitted"])
        self.assertFalse(rows["effect_chain_verified"])

    def test_four_base_gems_do_not_read_v281_or_v280(self):
        self.seal_v281()
        comp=self.compilation()
        progress={}
        self.assertIsNone(v216._fresh_attach_existing_v280_socket_preview(
            collected=self.collected,compilation=comp,progress=progress,
            selected_roles={"special_gem_id":None},socket_total=4))
        self.assertEqual(comp, self.compilation())
        self.assertEqual(progress,{})

    def test_selected_j_owner_summary_never_promotes_actual_effect(self):
        self.seal_v281()
        comp=self.compilation()
        v216._fresh_attach_existing_v280_socket_preview(
            collected=self.collected,compilation=comp,progress={},
            selected_roles={"special_gem_id":None},socket_total=5)
        parts=B10OriginalSocketSourceBoundaries().prepare(
            plan_counts={"head":1,"neck":1,"finger1":1,
                         "finger2":1,"wrists":1})
        parts[2].update({k:v for k,v in comp.items()
                         if k.endswith("_unadmitted")})
        j=v216._fresh_selected_J_intrinsic_socket_source(
            collected=parts[0],preflight=parts[1],compilation=parts[2])
        self.assertEqual(j["status"],
                         "J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING")
        self.assertEqual(j[
            "socket_spell_effect_source_only_for_unverified_additions"][
                "candidate_count"],3)
        self.assertFalse(j["J_approved"])
        self.assertFalse(j["game_socket_legal_verified"])

    def test_tampered_spell_effect_candidate_sha_fails_closed(self):
        self.seal_v281()
        file=self.root/OUTPUTS["candidate"]
        file.write_text(file.read_text()+" ",encoding="utf8")
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                   "V216_SOCKET_V281_ORIGINAL_OUTPUT_SHA_DRIFT"):
            self.previews()

    def test_forged_v281_stage_sha_fails_closed(self):
        self.seal_v281()
        self.collected["fresh_consumable_simc_effect_relation"][
            "source_stage"]["receipt_sha256"]="f"*64
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                   "V216_SOCKET_V281_ORIGINAL_RECEIPT_DRIFT"):
            self.previews()

    def test_v281_build_drift_fails_closed(self):
        self.seal_v281(build="12.2.0.99999")
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                   "V216_SOCKET_V281_SAME_BUILD_RELATION_DRIFT"):
            self.previews()

    def test_v281_item_changed_but_v280_item_unchanged_fails_closed(self):
        def change(doc):
            next(r for r in doc["items"] if r["item_id"]==275707)[
                "item_effect_source"]["on_use_spell_ids"]=[1297709]
        self.seal_v281(item_mutation=change)
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                   "V216_SOCKET_V281_V280_ITEM_USE_DRIFT"):
            self.previews()

    def test_separate_effect_spell_cannot_masquerade_as_use_spell(self):
        def change(doc):
            row=next(r for r in doc["items"] if r["item_id"]==275707)
            row["spell_effect_source"]["observed_spell_effects"].append({
                "spell_id":1297709,"effect":314,"enchant_id":6007,
                "effect_index":3,"difficulty_id":0})
        self.seal_v281(item_mutation=change)
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                   "V216_SOCKET_V281_SPELL_EFFECT_ROWS_DRIFT"):
            self.previews()

    def test_v281_missing_original_item_is_rejected(self):
        def change(doc):
            doc["items"]=[r for r in doc["items"]
                          if r["item_id"]!=275707]
        self.seal_v281(item_mutation=change)
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                   "V216_SOCKET_V281_V280_ITEM_USE_DRIFT"):
            self.previews()


if __name__=="__main__":
    unittest.main()
