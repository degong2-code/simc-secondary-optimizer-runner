"""P3-CT: no Native/HTTP; reuse sealed v167/v232/v285 and original v274."""
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner")]
import v217_stage_execution_engine as stages
import v281_consumable_simc_relation as v281
import v285_consumable_weapon_source as v285
import v286_representative_oil_source_binding as binding
import v274_zero_history_source_compiler_wiring as wiring
from tests.test_v281_consumable_simc_relation import SOURCE,TMP,FLASK,CSV,BUILD

WEAPON_MASK_ROW={
    "row_id":254979,"spell_id":211,"equipped_item_class":2,
    "inventory_type_mask":73572352,"weapon_subclass_mask":983039
}

class RepresentativeOilSource(unittest.TestCase):
    def setUp(self):
        td=tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.root=pathlib.Path(td.name)
        (self.root/"wago").mkdir()
        (self.root/"wago"/"receipt.json").write_text("{}")
        effect=self.root/"effect.csv"
        effect.write_bytes(CSV)
        relation=v281.correlate(
           SOURCE,v281.scan_spell_effects(effect,{111,211,212}),
           TMP,build=BUILD,flask_dbc_rows=FLASK)
        oil=v285.attach(relation,[WEAPON_MASK_ROW],BUILD)
        self.gear={
            "schema":"v167_product_season_gear_db_v1",
            "season_build":BUILD,
            "items":[{"item_id":9101,"class_id":2,"subclass_id":7,
                      "inventory_type":13}],
            "internal_conditional_mplus_plain_candidates":[]}
        self.rep={
            "schema":"v232_simc_only_one_dps_representative_source_candidate_v1",
            "game_build":BUILD,"simc_revision":"a"*40,
            "selected_G_source_candidate_not_approved":True,
            "selected_weapons":{"main_hand":9101},
            "selected_G_slot_ids":{"main_hand":9101},
            "character":{"class":"mage","spec":"frost"}}
        self.docs={"OIL":oil,"GEAR":self.gear,
                   "REPRESENTATIVE":self.rep}
        self.set_up_sources()
    def seal(self,name,filename,document):
        rel="source/"+filename
        path=self.root/rel
        def write():
            path.parent.mkdir(exist_ok=True)
            path.write_text(json.dumps(document,sort_keys=True)+"\n",
                            encoding="utf8")
        stage=stages.execute_stage(root=self.root,stage_id=name,
             stage_version="test-source-v1",inputs={"build":BUILD},
             outputs={"candidate":rel},execute=write)
        return {"candidate_path":str(path.resolve()),
                "source_stage":{k:v for k,v in stage.items() if k!="result"}}
    def set_up_sources(self):
        self.source={
            "schema":"v216_fresh_source_stage_v1",
            "expected_game_build":BUILD,
            "snapshot_receipt_path":str(self.root/"wago"/"receipt.json"),
            "fresh_consumable_weapon_source":
                self.seal("fresh-consumable-weapon-inventory-source",
                          "v285_masks.json",self.docs["OIL"]),
            "fresh_ordinary_gear":
                self.seal("fresh-ordinary-gear-source-candidates",
                          "v167_gear.json",self.docs["GEAR"]),
            "fresh_one_spec_simc_representative":
                self.seal("fresh-one-spec-generic-G-representative-test",
                          "v232_one_spec.json",self.docs["REPRESENTATIVE"]),
        }
    def test_selected_representative_weapon_matches_oil_mask(self):
        data=binding.match_collected(self.source)
        self.assertEqual(data["status"],"REPRESENTATIVE_OIL_MASK_MATCH_SOURCE_ONLY")
        self.assertEqual(data["source_mask_matches"],1)
        case=data["candidate_options"][0]
        self.assertEqual(case["oil_item_id"],601)
        self.assertEqual(case["hand"],"main_hand")
        self.assertEqual(case["representative_weapon_id"],9101)
        self.assertEqual(case["quality_rank"],2)
        self.assertTrue(case["matched_same_build_spell_equipped_masks"])
        self.assertFalse(case["game_weapon_ilevel_and_use_requirements_verified"])
        self.assertFalse(case["quality_effect_equivalence_verified"])
        self.assertFalse(data["environment_ready"])
        self.assertFalse(data["user_selectable"])
        self.assertIsNone(data["F"])
        self.assertIsNone(data["O"])
        self.assertIsNone(data["B"])
        self.assertEqual(data["network_calls"],0)
        self.assertEqual(data["new_native_calls"],0)
    def test_dual_weapon_vs_offhand_shield_with_same_item_id_source(self):
        shield=dict(self.rep,selected_weapons={
            "main_hand":9101,"off_hand":9102})
        armor=dict(self.gear,items=self.gear["items"]+[
            {"item_id":9102,"class_id":4,"subclass_id":4,
             "inventory_type":14}])
        source=dict(self.source,
            fresh_one_spec_simc_representative=self.seal(
                "fresh-one-spec-generic-G-representative-shield",
                "v232_shield.json",shield),
            fresh_ordinary_gear=self.seal(
                "fresh-ordinary-gear-source-shield",
                "v167_shield.json",armor))
        only_main=binding.match_collected(source)
        self.assertEqual([x["hand"] for x in only_main["candidate_options"]],
                         ["main_hand"])
        # With a physically selected second WEAPON the exact offhand mask
        # is applicable; no game minimum-ilvl or same-effect UI approval.
        dual=dict(armor,items=self.gear["items"]+[
            {"item_id":9102,"class_id":2,"subclass_id":7,
             "inventory_type":22}])
        source["fresh_ordinary_gear"]=self.seal(
            "fresh-ordinary-gear-source-dual","v167_dual.json",dual)
        two=binding.match_collected(source)
        self.assertEqual({x["hand"] for x in two["candidate_options"]},
                         {"main_hand","off_hand"})
        self.assertTrue(all(x["user_selectable"] is False
                            for x in two["candidate_options"]))
    def test_missing_representative_remains_pending_without_source_scan(self):
        doc=dict(self.source)
        doc["fresh_one_spec_simc_representative"]={}
        result=binding.match_collected(doc)
        self.assertEqual(result["status"],"REPRESENTATIVE_OIL_SOURCE_PENDING")
        self.assertEqual(result["candidate_options"],[])
        self.assertEqual(result["network_calls"],0)
        self.assertFalse(result["environment_ready"])
    def test_byte_drift_or_wrong_build_never_becomes_user_option(self):
        p=pathlib.Path(self.source["fresh_consumable_weapon_source"][
            "candidate_path"])
        p.write_text("tampered",encoding="utf8")
        with self.assertRaisesRegex(binding.OilRepresentativeSourceBlocked,
                                     "CANDIDATE_SIZE_DRIFT|CANDIDATE_SHA_DRIFT"):
            binding.match_collected(self.source)
    def test_existing_compiler_receives_source_only_representative_match(self):
        stub={"schema":wiring.SCHEMA,
              "status":"COLLECTED_COMPILER_INPUTS_COMPLETE",
              "inputs":{"ready":True,"stage_root":self.root,
                        "expected_simc_revision":"a"*40},"missing":[]}
        compiler_result={
            "source_catalog_path":str(self.root/"catalog.json"),
            "v191_stage":{"status":"EXECUTED_AND_SEALED"},
            "v211_stage":{"status":"EXECUTED_AND_SEALED"},
            "v213_stage":{"status":"EXECUTED_AND_SEALED"}}
        with mock.patch.object(wiring,"discover",return_value=stub):
            done=wiring.compile_collected(
                self.source,compiler=lambda **_:compiler_result)
        matched=done["representative_oil_source_options_unadmitted"]
        self.assertEqual(matched["source_mask_matches"],1)
        self.assertFalse(done["environment_ready"])
        self.assertFalse(matched["user_selectable"])
    def test_no_compiler_inputs_still_keeps_source_only_diagnostic(self):
        with mock.patch.object(wiring,"discover",return_value={
            "status":"COLLECTED_COMPILER_INPUTS_PENDING",
            "schema":wiring.SCHEMA,"missing":["GENERATED_GEM"],
            "inputs":None}):
            done=wiring.compile_collected(
                self.source,compiler=mock.Mock(
                    side_effect=AssertionError("COMPILER_UNEXPECTED")))
        self.assertEqual(done["status"],"COLLECTED_COMPILER_INPUTS_PENDING")
        self.assertEqual(done["representative_oil_source_options_unadmitted"][
            "source_mask_matches"],1)

if __name__=="__main__":
    unittest.main()
