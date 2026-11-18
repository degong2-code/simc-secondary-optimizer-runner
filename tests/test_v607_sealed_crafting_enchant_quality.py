"""v607: same-crafting-family highest quality, NOT SimC effect dominance."""
import copy
import pathlib
import sys
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v216_environment_build_coordinator as build
import v196_current_season_user_catalog as catalog
import v220_catalog_auto_admission as admission


class SealedCraftingQualityTests(unittest.TestCase):
    def setUp(self):
        self.build="12.1.5.70783"
        self.rev="d"*40
        self.token="enchant_boots__family"
        self.mask=1<<8
        self.rows=[
            {"enchant_id":99011,"quality_rank":1,
             "simc_token":self.token,"item_class":4,
             "inventory_type_mask":self.mask,"item_subclass_mask":0},
            {"enchant_id":99012,"quality_rank":2,
             "simc_token":self.token,"item_class":4,
             "inventory_type_mask":self.mask,"item_subclass_mask":0}
        ]
        self.catalog={"game_build":self.build,"simc_revision":self.rev,
            "manifest_sha256":"e"*64,
            "v196_enchant_source":{"rows":[
                {"enchant_id":99012,"token":self.token,"quality_rank":2,
                 "inventory_type_mask":self.mask}]}}
        self.v191={"game_build":self.build,"simc_revision":self.rev,
            "enchants":{"permanent":{"source_records":copy.deepcopy(self.rows)}}}
        self.v583={"status":"PERMANENT_ENCHANT_EXACT_WAGO_SIMC_SOURCE_ONLY",
            "game_build":self.build,"simc_revision":self.rev,
            "expansion_id":11,"source_only":True,
            "automatic_ui_promotion":False,"matches":[]}
        for rank,src in enumerate(self.rows,13):
            self.v583["matches"].append({
                "enchant_id":src["enchant_id"],"simc_rank_rows":[dict(src)],
                "physical_items":[{
                    "item_id":240000+rank,"expansion_id":11,
                    "exact_join":"WAGO_301_CRAFTDATA_QUALITY_TO_SIMC_ID",
                    "crafting_data_id":90001,
                    "quality_rank_wago":rank,
                    "wago_quality_row_id":81000+rank}]})

    def eligible(self, doc=None, v191=None, v583=None):
        return build._v607_sealed_highest_crafting_quality(
            catalog=self.catalog if doc is None else doc,
            original_v191=self.v191 if v191 is None else v191,
            physical_v583=self.v583 if v583 is None else v583,
            v191_sha="a"*64,v583_sha="b"*64)

    def test_exact_family_top_rank_accepts_without_effect_numbers(self):
        good=self.eligible()
        self.assertEqual(list(good),[99012])
        row=good[99012]
        self.assertTrue(row["source_quality_family_verified"])
        self.assertTrue(row["same_build_physical_join_verified"])
        self.assertEqual(row["verified_quality_rank"],2)
        self.assertEqual(len(row["quality_source_sha256"]),64)
        self.assertNotIn("no_inferior_effect_components_verified",row)
        self.assertNotIn("same_effect_and_use_conditions_verified",row)

    def test_different_crafting_data_not_same_quality_family(self):
        altered=copy.deepcopy(self.v583)
        altered["matches"][0]["physical_items"][0]["crafting_data_id"]=90002
        self.assertEqual(self.eligible(v583=altered),{})

    def test_wago_rank_order_not_equal_simc_rank_but_must_increase(self):
        altered=copy.deepcopy(self.v583)
        altered["matches"][0]["physical_items"][0]["quality_rank_wago"]=15
        self.assertEqual(self.eligible(v583=altered),{})
        # A rank-13/14 source order is valid even though SimC ranks are 1/2.
        self.assertIn(99012,self.eligible())

    def test_missing_lower_rank_and_conflicting_token_pending(self):
        altered=copy.deepcopy(self.v583)
        altered["matches"].pop(0)
        self.assertEqual(self.eligible(v583=altered),{})
        altered=copy.deepcopy(self.v583)
        altered["matches"][0]["simc_rank_rows"][0]["simc_token"]="other_enchant"
        self.assertEqual(self.eligible(v583=altered),{})

    def test_build_revision_and_source_masks_fail_closed(self):
        altered=copy.deepcopy(self.v583)
        altered["simc_revision"]="c"*40
        self.assertEqual(self.eligible(v583=altered),{})
        altered=copy.deepcopy(self.v191)
        altered["enchants"]["permanent"]["source_records"][0][
            "item_subclass_mask"]=1
        self.assertEqual(self.eligible(v191=altered),{})
        altered=copy.deepcopy(self.v583)
        altered["automatic_ui_promotion"]=True
        self.assertEqual(self.eligible(v583=altered),{})

    def test_original_v196_policy_A_uses_quality_without_effect_dominance(self):
        source_row={"enchant_id":99012,"token":self.token,"quality_rank":2,
                    "item_class":4,"inventory_type_mask":self.mask,
                    "item_subclass_mask":0,"slot_group":"feet",
                    "slot_resolution_status":"SOURCE_MASK_RESOLVED"}
        source={**self.catalog,
            "v196_enchant_source":{"rows":[source_row]}}
        public_row={"enchant_id":99012,"token":self.token,
                    "highest_source_quality_rank":2,
                    "source_slots":["feet"],"ui_selectable":False}
        ui={"schema":catalog.SCHEMA,
            "status":"FRESH_SEASON_CANDIDATES_UNAPPROVED_NOT_ENVIRONMENT_READY",
            "environment_ready":False,"season_build":self.build,
            "simc_revision":self.rev,
            "source_catalog":{"manifest_sha256":source["manifest_sha256"]},
            "enchant_candidates":{"selectable_count":0,"items":[public_row]}}
        identity=admission._identity(admission.candidate_from_source_enchant(
            source,public_row,original_source_row=source_row))
        receipts={name:{"identity":dict(identity),"status":status,
                        "evidence_sha256":str(i)*64}
                  for i,(name,status) in enumerate(
                      admission.PROOF_STATUSES.items(),1)}
        receipts["product_input"].update(self.eligible()[99012])
        receipts["product_input"]["same_effect_and_use_conditions_verified"]=False
        receipts["product_input"]["no_inferior_effect_components_verified"]=False
        receipts["chmv_budget"].update({
            "no_double_count":True,"unknown_static_chmv":False,
            "fixed_E":dict.fromkeys(admission.CHMV_STATS,0)})
        def prepare(data):
            with mock.patch.object(catalog.source_bridge,"verify_catalog"):
                return catalog.prepare_verified_fresh_choices(
                    source,ui,{99012:data})
        good=prepare(receipts)
        self.assertEqual(len(good["verified_option_inputs_unpublished"]),1)
        self.assertEqual(good["verified_option_inputs_unpublished"][0][
            "highest_verified_quality_rank"],2)
        for field in ("source_quality_family_verified",
                      "same_build_physical_join_verified"):
            bad=copy.deepcopy(receipts)
            bad["product_input"].pop(field)
            self.assertEqual(prepare(bad)["verified_option_inputs_unpublished"],[])
        no_E=copy.deepcopy(receipts)
        no_E["chmv_budget"].pop("fixed_E")
        self.assertEqual(prepare(no_E)["verified_option_inputs_unpublished"],[])


    def test_original_v216_stage_receipts_publish_product_input_only_from_sealed_join(self):
        """Actual v216 producer consumes v191/v583 stage SHA, not client flags."""
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            (root/"fresh_source").mkdir()
            (root/"source").mkdir()
            v191path=root/"fresh_source"/"v191_candidate.json"
            v191path.write_text(json.dumps(self.v191,sort_keys=True),encoding="utf8")
            original_sha=build.digest(v191path.read_bytes())
            joinpath=root/"source"/"v583_join.json"
            joinpath.write_text(json.dumps(self.v583,sort_keys=True),encoding="utf8")
            join_sha=build.digest(joinpath.read_bytes())
            v583stage="fresh-v583-enchant-join-test"
            stage_map={
                "v191":("candidate","fresh_source/v191_candidate.json",original_sha),
                "v211":("classification","fresh_source/v211_classification.json","b"*64),
                "v213":("candidate","fresh_source/v213_candidate_catalog.json","c"*64)}
            att={"stage_root":str(root)}
            receipts={}
            for stage,(key,rel,checksum) in stage_map.items():
                name="fresh-"+stage
                stamp=(str(1+len(att))*64)[:64]
                att[stage+"_stage"]={"status":"REUSED_VERIFIED",
                    "stage_id":name,"receipt_sha256":stamp}
                receipts[name]={"stage_id":name,"stage_version":"1",
                    "status":"COMPLETE","receipt_sha256":stamp,
                    "output_paths":{key:rel},
                    "outputs":{key:{"sha256":checksum,"path":rel}}}
            receipts[v583stage]={"receipt_sha256":"9"*64,
                "output_paths":{"candidate":"source/v583_join.json"},
                "outputs":{"candidate":{"sha256":join_sha}}}
            v583_ref={"status":
                "PERMANENT_ENCHANT_EXACT_WAGO_SIMC_SOURCE_ONLY",
                "candidate_path":str(joinpath),
                "source_stage":{"stage_id":v583stage,
                    "receipt_sha256":"9"*64,
                    "output_paths":{"candidate":"source/v583_join.json"}}}
            original={"enchant_id":99012,"token":self.token,
                "quality_rank":2,"slot_group":"feet",
                "slot_resolution_status":"SOURCE_MASK_RESOLVED",
                "item_class":4,"inventory_type_mask":self.mask,
                "item_subclass_mask":0}
            static={"component_index":0,"item_mod_id":7,
                    "category":"NON_CHMV_STAT",
                    "dbc_amount":100,"coefficient":0.0}
            category={**{k:original[k] for k in
                        ("enchant_id","token","quality_rank","item_class",
                         "inventory_type_mask","item_subclass_mask")},
                "simc_effect_owner":"SIMC",
                "simc_effect_reimplemented":False,
                "effect_family":"static_nonchmv_item_mod",
                "effect_source_status":"DBC_STAT_AND_SPELLTEXT_SOURCE_CLASSIFIED",
                "budget_policy":
                    "NO_STATIC_CHMV_COMPONENT_IN_DBC_ROW; DYNAMIC_EFFECTS_STAY_WITH_SIMC",
                "static_components":[static],"static_chmv_rating_present_in_dbc":False,
                "static_chmv_stats":[],"spell_effects":[],
                "unknown_components":[],
                "dynamic_chmv_proc_present_in_spell_text":False,
                "dynamic_chmv_proc_roles":[],"simc_custom_handlers":[],
                "simc_generic_or_unregistered_spell_count":0,
                "native_E_evidence":{"status":"NOT_MEASURED_NEW_BUILD",
                    "static_E":None,"ui_selectable":False,"source_file":None},
                "selection_status":"LOCKED_PENDING_CURRENT_SEASON_ITEM_EFFECT_PROOF"}
            category_item={**original,"classification":category}
            data={**self.catalog,
                "source_provenance":{
                    "v191":{"sha256":original_sha},
                    "v211":{"sha256":"b"*64,
                        "simc_item_enchant_pipeline":{
                            "owner":"SIMC","source_file":"engine/item/enchants.cpp",
                            "static_stat_path":"ITEM_ENCHANTMENT_STAT",
                            "spell_effect_path":"ITEM_ENCHANTMENT_EQUIP_SPELL",
                            "passive_spell_path":"passive_enchant"}}},
                "enchant_classification":{
                    "status":
                        "SOURCE_CLASSIFIED_NOT_GENERAL_NATIVE_ACCEPTANCE_OR_UI_PROMOTION",
                    "source_manifest_sha256":"f"*64,
                    "rows":[category]},
                "catalog":{"enchants":{"items":[category_item]}},
                "v196_enchant_source":{"rows":[
                    {"enchant_id":99012,"token":self.token,
                     "inventory_type_mask":self.mask}]}}
            public={"enchant_id":99012,"token":self.token,
                    "highest_source_quality_rank":2,"source_slots":["feet"]}
            def produce():
                with mock.patch.object(build.stage_engine,"_read_receipt",
                    side_effect=lambda path:receipts[path.stem]):
                    return build._v217_policy_A_source_relation_receipts(
                        catalog=data,artifact_sha256="c"*64,
                        catalog_path=root/"fresh_source"/"v213_candidate_catalog.json",
                        stage_attestations=att,public_rows=[public],
                        physical_enchant_source=v583_ref)[99012]
            good=produce()
            self.assertEqual(set(good),{
                "source_relation","simc_input","product_input","chmv_budget"})
            self.assertTrue(good["product_input"]["source_quality_family_verified"])
            self.assertFalse(good["chmv_budget"]["gameplay_or_native_effect_attested"])
            candidate=admission.candidate_from_source_enchant(
                data,public,original_source_row=original)
            self.assertTrue(admission.decide(candidate,good)["eligible"])
            joinpath.write_text(joinpath.read_text("utf8")+" ",encoding="utf8")
            # Tampered optional v583 source leaves G/J/F/O and original
            # source relation alone, without a forged quality certificate.
            pending=produce()
            self.assertNotIn("product_input",pending)
            self.assertEqual(set(pending),
                {"source_relation","simc_input","chmv_budget"})


if __name__=="__main__":
    unittest.main()
