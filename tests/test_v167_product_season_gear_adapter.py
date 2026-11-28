"""v167 read-only catalog into UI and ordinary armor-compatible previews."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

# Standalone unittest discovery does not add runner/ to sys.path;
# v167's display-only v332 dependency is intentionally runner-local.
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runner"))
from runner import v167_product_season_gear_adapter as adapter


def source():
    def row(i, name, category, slot, cl, sub):
        return {"item_id":i,"name":name,"category":category,"slot":slot,
                "class_id":cl,"subclass_id":sub,"allowed_class_mask":-1,
                "stat_modifier_codes":[5,24],"item_set_id":0,
                "source_kinds":["raid_journal"],
                "selection_evidence":"CURRENT_CANDIDATE"}
    return {
        "schema":"v166_current_season_product_gear_db_v1",
        "status":"COMPACT_CANDIDATE_DB_WITH_PENDING_GAPS",
        "season_build":"12.1.5.70575","expansion_id":11,"display_season_id":37,
        "current_candidate_count":5,"conditional_count":2,
        "no_old_catalog_seed":True,"native_calls":0,
        "current_candidates":[
            row(101,"Plate Wrist","plain_representative_candidate",9,4,4),
            row(102,"Cloth Wrist","plain_representative_candidate",9,4,1),
            row(103,"Everyone Cloak","plain_representative_candidate",16,4,1),
            row(104,"Delve Trinket","trinket",12,4,0),
            row(105,"Craftable Boots","selectable_stat_craft",8,4,4)]}


class ProductAdapterTests(unittest.TestCase):
    def test_only_user_effect_choices_and_craft_id_exception(self):
        c=adapter.from_v166(source())
        options=adapter.public_options(c)
        self.assertEqual(c["item_count"],5)
        self.assertFalse(options["manual_exact_id_allowed"])
        self.assertEqual(options["manual_exact_id_exception"],"CRAFTED_EQUIPMENT_VARIANTS_ONLY")
        self.assertEqual(len(options["choices"]["trinket"]),1)
        self.assertEqual(options["choices"]["trinket"][0]["name"],"Delve Trinket")
        self.assertNotIn("plain_representative_candidate",options["choices"])
        self.assertFalse(options["ordinary_equipment_user_selectable"])
        self.assertEqual(c["conditional_ids_excluded"],2)
        self.assertEqual(c["new_native_calls"],0)

    def test_optional_loot_spec_metadata_never_filters_or_changes_catalog(self):
        from v737_trinket_loot_spec_source import classify
        c=adapter.from_v166(source())
        snapshot=copy.deepcopy(c)
        specs=b"ID,ClassID,Role,Name_lang\n1,1,0,Protection\n2,8,2,Fire\n3,5,1,Holy\n"
        overrides=b"ID,ItemID,SpecID\n1,104,1\n2,105,2\n3,106,1\n4,106,2\n5,107,999\n6,108,3\n"
        raw={"ChrSpecialization":specs,"ItemSpecOverride":overrides}
        rows=classify({i:str(i) for i in range(104,110)},raw)
        self.assertEqual([r["status"] for r in rows],[
            "EXPLICIT_NON_DPS_ROLES_ONLY","EXPLICIT_DPS_ROLE_ONLY",
            "EXPLICIT_SHARED_WITH_DPS","OVERRIDE_REFERENCE_OR_ROLE_PENDING",
            "EXPLICIT_NON_DPS_ROLES_ONLY","NO_EXPLICIT_OVERRIDE_UNKNOWN"])
        default=adapter.public_options(c)
        enriched=adapter.public_options(c,loot_spec_sources={
            "game_build":c["season_build"],"tables":raw})
        self.assertEqual(c,snapshot)
        self.assertEqual(enriched["count"],default["count"])
        row=enriched["choices"]["trinket"][0]
        metadata=row.pop("loot_spec_metadata")
        self.assertEqual(metadata["roles"],["TANK"])
        self.assertFalse(metadata["equipment_eligibility_proven"])
        self.assertFalse(metadata["dps_effect_usefulness_proven"])
        self.assertEqual(enriched,default)
        with self.assertRaisesRegex(ValueError,"ROLE_SOURCE_BUILD_DRIFT"):
            adapter.public_options(c,loot_spec_sources={
                "game_build":"99.1.1.12345","tables":raw})

    def test_reuse_sealed_tier_specialization_and_only_fetch_override_once(self):
        import io
        import v216_environment_build_coordinator as env
        import v217_stage_execution_engine as stages
        import v737_trinket_loot_spec_source as role
        build="12.2.0.99999"
        spec=b"ID,ClassID,Role,Name_lang\n1,1,0,Protection\n2,8,2,Fire\n"
        overrides=b"ID,ItemID,SpecID\n1,104,1\n2,105,2\n"
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            calls=[]
            class Response(io.BytesIO):
                status=200
                def __enter__(self):return self
                def __exit__(self,*args):self.close()
            def transport(req,timeout):
                calls.append(req.full_url)
                return Response(overrides)
            pending=env.refresh_trinket_loot_spec_sources(
                stage_root=root,build=build,transport=transport)
            self.assertEqual(pending["network_calls_by_stage"],0)
            self.assertIsNone(role.read_sources(root,build))
            outputs={"ChrSpecialization":"source/db2_tier_ilvl_ChrSpecialization.csv",
                     "candidates":"source/v245_db2_tier_candidates_ilvl.json"}
            def seal_tier():
                for key,relative in outputs.items():
                    p=root/relative;p.parent.mkdir(exist_ok=True)
                    p.write_bytes(spec if key=="ChrSpecialization" else json.dumps({
                        "schema":"v245_db2_first_class_tier_candidates_v1",
                        "game_build":build,
                        "evidence":{"chr_specialization_sha256":role.sha(spec)}
                    }).encode("utf8"))
            original=stages.execute_stage(root=root,stage_id=role.TIER_STAGE_ID,
                stage_version=role.TIER_STAGE_VERSION,inputs={"game_build":build},
                outputs=outputs,execute=seal_tier)
            first=env.refresh_trinket_loot_spec_sources(
                stage_root=root,build=build,transport=transport)
            second=env.refresh_trinket_loot_spec_sources(
                stage_root=root,build=build,transport=transport)
            self.assertEqual(first["status"],"TRINKET_LOOT_SPEC_SOURCE_OBSERVED")
            self.assertEqual((first["network_calls_by_stage"],second["network_calls_by_stage"]),(1,0))
            self.assertEqual(calls,[role.source_url("ItemSpecOverride",build)])
            self.assertEqual(role.read_sources(root,build),{"game_build":build,
                "tables":{"ChrSpecialization":spec,"ItemSpecOverride":overrides}})
            self.assertEqual(stages.verify_stage(root=root,stage_id=role.TIER_STAGE_ID,
                stage_version=role.TIER_STAGE_VERSION,inputs={"game_build":build},
                outputs=outputs)["receipt_sha256"],original["receipt_sha256"])
            with self.assertRaisesRegex(ValueError,"ROLE_SEALED_SOURCE_IDENTITY_DRIFT"):
                role.read_sources(root,"12.3.0.99999")
            (root/outputs["ChrSpecialization"]).write_bytes(spec.replace(b"Fire",b"Frost"))
            with self.assertRaisesRegex(ValueError,"ROLE_SEALED_SOURCE_SIZE_DRIFT"):
                role.read_sources(root,build)

    def test_plain_representative_is_nonmutating_and_class_family_filtered(self):
        c=adapter.from_v166(source())
        plate=adapter.ordinary_candidates(c,"plate")
        cloth=adapter.ordinary_candidates(c,"cloth")
        self.assertEqual([x["item_id"] for x in plate["candidate_slots"]["wrists"]],[101])
        self.assertEqual([x["item_id"] for x in cloth["candidate_slots"]["wrists"]],[102])
        self.assertEqual([x["item_id"] for x in plate["candidate_slots"]["back"]],[103])
        self.assertFalse(plate["tier_four_piece_id_confirmed"])
        self.assertFalse(plate["weapon_profile_confirmed"])
        self.assertEqual(plate["status"],"PREVIEW_ONLY_NOT_A_PROFILE")

    def test_fresh_j_f_unknown_is_preserved_without_making_it_ready(self):
        inp=source()
        inp["consumable_budget_source_mode"]="NEW_SEASON_J_F_BUDGET_EVIDENCE_PENDING"
        inp["consumable_budget_reference"]=None
        result=adapter.from_v166(inp)
        self.assertEqual(result["consumable_budget_source_mode"],
                         "NEW_SEASON_J_F_BUDGET_EVIDENCE_PENDING")
        self.assertTrue(result["J_F_NUMERIC_AUTHENTICATION_NOT_IN_GEAR_COLLECTOR"])
        self.assertEqual(result["item_count"],5)
        self.assertTrue(result["not_certified"]["tier_four_set"])

    def test_reject_conditional_or_uncertified_as_current(self):
        a=source();a["current_candidates"][0]["selection_evidence"]="CONDITIONAL_SEASON_NOT_ESTABLISHED"
        with self.assertRaises(adapter.GearBlocked):
            adapter.from_v166(a)
        b=source();b["current_candidates"][3]["slot"]=5
        with self.assertRaises(adapter.GearBlocked):
            adapter.from_v166(b)

    def test_conditional_worldstate_plain_is_internal_only(self):
        source_doc=source()
        source_doc["internal_conditional_mplus_plain_candidates"]=[{
            "item_id":200,"name":"Conditional M+ Wrist","slot":9,
            "class_id":4,"subclass_id":4,
            "allowed_class_mask":2,"stat_modifier_codes":[4],
            "item_set_id":0,"direct_item_effect_record":False,
            "category":"plain_representative_candidate",
            "selection_evidence":"CONDITIONAL_SEASON_NOT_ESTABLISHED",
            "source_kinds":["mplus_journal"],
            "source_evidence":[{
                "source":"mplus_journal",
                "season_evidence":"UNKNOWN_WORLD_STATE_EXPRESSION",
                "display_season_id":37,"world_state_expression_id":441,
                "journal_encounter_id":10,"journal_instance_id":20}]}]
        source_doc["internal_conditional_mplus_plain_count"]=1
        c=adapter.from_v166(source_doc)
        without_wse=copy.deepcopy(source_doc)
        without_wse["internal_conditional_mplus_plain_candidates"][0][
            "source_evidence"][0]["world_state_expression_id"]=None
        # WSE is no longer an admission or internal-fallback requirement.
        self.assertEqual(adapter.from_v166(without_wse)[
            "internal_conditional_mplus_plain_count"],1)
        self.assertEqual(c["internal_conditional_mplus_plain_count"],1)
        self.assertNotIn(200,{x["item_id"] for x in c["items"]})
        self.assertFalse(c["internal_conditional_mplus_plain_candidates"][0][
            "ui_selectable"])
        self.assertNotIn("plain_representative_candidate",
                         adapter.public_options(c)["choices"])
        # A new season may expose no approved current choices yet while
        # the sole WSE-pending same-display-season plain item is available
        # for INTERNAL physical source discovery.
        source_doc["current_candidates"]=[]
        source_doc["current_candidate_count"]=0
        only_pending=adapter.from_v166(source_doc)
        self.assertEqual(only_pending["item_count"],0)
        self.assertEqual(only_pending[
            "internal_conditional_mplus_plain_count"],1)
        self.assertEqual(adapter.public_options(only_pending)["choices"][
            "trinket"],[])
        c["internal_conditional_mplus_plain_candidates"][0]["ui_selectable"]=True
        with self.assertRaisesRegex(adapter.GearBlocked,
                                    "INTERNAL_MPLUS_SOURCE_NOT_PENDING"):
            adapter.validate(c)

    def test_internal_plain_neck_is_not_user_selectable(self):
        src=source()
        src["internal_source_only_plain_neck_candidates"]=[{
            "item_id":200,"name":"Generic neck","slot":2,
            "class_id":4,"subclass_id":0,"allowed_class_mask":-1,
            "stat_modifier_codes":[5],"item_set_id":0,
            "direct_item_effect_record":False,
            "category":"plain_representative_candidate",
            "selection_evidence":"CONDITIONAL_SEASON_NOT_ESTABLISHED",
            "source_expansion_id":11,"internal_generic_G_only":True,
            "user_selectable_candidate":False,
            "source_kinds":["raid_journal"],
            "source_evidence":[{"source":"raid_journal"}]}]
        src["internal_source_only_plain_neck_count"]=1
        row=adapter.from_v166(src)
        self.assertEqual(row["internal_source_only_plain_neck_count"],1)
        self.assertNotIn(200,{x["item_id"] for x in row["items"]})
        visible=adapter.public_options(row)["choices"]
        self.assertNotIn(200,{x["item_id"] for v in visible.values() for x in v})
        tampered=copy.deepcopy(row)
        tampered["internal_source_only_plain_neck_candidates"][0][
            "ui_selectable"]=True
        with self.assertRaisesRegex(adapter.GearBlocked,
                                     "PRODUCT_INTERNAL_SOURCE_NECK_NOT_JUSTIFIED"):
            adapter.validate(tampered)

    def test_internal_plain_ring_not_ui_and_tampering_blocked(self):
        src=source()
        src["internal_source_only_plain_ring_candidates"]=[{
            "item_id":201,"name":"Generic ring","slot":11,
            "class_id":4,"subclass_id":0,"allowed_class_mask":-1,
            "stat_modifier_codes":[5],"item_set_id":0,
            "direct_item_effect_record":False,
            "category":"plain_representative_candidate",
            "selection_evidence":"CONDITIONAL_SEASON_NOT_ESTABLISHED",
            "source_expansion_id":11,"internal_generic_G_only":True,
            "user_selectable_candidate":False,
            "source_kinds":["raid_journal"],
            "source_evidence":[{"source":"raid_journal"}]}]
        src["internal_source_only_plain_ring_count"]=1
        row=adapter.from_v166(src)
        self.assertEqual(row["internal_source_only_plain_ring_count"],1)
        self.assertNotIn(201,{x["item_id"] for x in row["items"]})
        visible=adapter.public_options(row)["choices"]
        self.assertNotIn(201,{x["item_id"] for v in visible.values() for x in v})
        tampered=copy.deepcopy(row)
        tampered["internal_source_only_plain_ring_candidates"][0][
            "ui_selectable"]=True
        with self.assertRaisesRegex(adapter.GearBlocked,
                                     "PRODUCT_INTERNAL_SOURCE_RING_NOT_JUSTIFIED"):
            adapter.validate(tampered)

    def test_unknown_roles_counts_and_tier_fail_closed(self):
        doc=adapter.from_v166(source())
        doc["role_counts"]["trinket"]=20
        with self.assertRaises(adapter.GearBlocked):
            adapter.public_options(doc)
        doc=adapter.from_v166(source())
        doc["not_certified"]["tier_four_set"]=False
        with self.assertRaises(adapter.GearBlocked):
            adapter.validate(doc)
        with self.assertRaises(adapter.GearBlocked):
            adapter.ordinary_candidates(adapter.from_v166(source()),"mail",
                                        slots=("main_hand",))

    def test_determinism_and_round_trip(self):
        d=adapter.from_v166(source())
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"season.json"
            p.write_text(json.dumps(d))
            self.assertEqual(adapter.read(p),d)
        self.assertEqual(adapter.from_v166(source()),d)

    def test_real_saved_v166_when_provided(self):
        p=os.environ.get("SIMC_V166_PRODUCT_GEAR_DB")
        if not p:
            self.skipTest("real v166 artifact not supplied to offline test")
        doc=adapter.from_v166(json.loads(Path(p).read_text()))
        self.assertEqual(doc["item_count"],288)
        self.assertEqual(doc["role_counts"],{
            "plain_representative_candidate":136,
            "selectable_stat_craft":106,
            "special_effect_gear_candidate":10,
            "trinket":36})
        self.assertEqual(doc["conditional_ids_excluded"],225)
        self.assertEqual(doc["new_native_calls"],0)


class EquipmentSpecCompatibility(unittest.TestCase):
    def test_v869_all_26_primary_armor_and_supported_special_slot_matrix(self):
        # Independent expected spec sets, not inferred from the production
        # contract being tested. No season-specific IDs or Native calls.
        cloth={"mage/arcane","mage/fire","mage/frost","priest/shadow",
               "warlock/affliction","warlock/demonology","warlock/destruction"}
        leather={"demonhunter/devourer","demonhunter/havoc","druid/balance","druid/feral",
                 "monk/windwalker","rogue/assassination","rogue/outlaw","rogue/subtlety"}
        mail={"evoker/devastation","hunter/beast_mastery","hunter/marksmanship",
              "hunter/survival","shaman/elemental","shaman/enhancement"}
        plate={"deathknight/frost","deathknight/unholy","paladin/retribution",
               "warrior/arms","warrior/fury"}
        all_specs=cloth|leather|mail|plate
        intelligence=cloth|{"demonhunter/devourer","druid/balance","evoker/devastation","shaman/elemental"}
        strength=plate
        agility=all_specs-intelligence-strength
        self.assertEqual(len(all_specs),26)
        def eligible(**changes):
            row={"category":"trinket","inventory_type":12,"class_id":4,
                 "subclass_id":0,"allowed_class_mask":-1,"stat_modifier_codes":[]}
            row.update(changes)
            original=copy.deepcopy(row)
            actual=set(adapter.equipment_primary_armor_compatibility(row)["compatible_dps_specs"])
            self.assertEqual(row,original)
            return actual
        for codes,expected in [([3],agility),([4],strength),([5],intelligence),
                ([71],all_specs),([72],strength|agility),([73],agility|intelligence),
                ([74],strength|intelligence),([3,5],agility|intelligence),
                ([-1,32,36,49],all_specs),([],all_specs),(None,all_specs)]:
            with self.subTest(codes=codes):
                self.assertEqual(eligible(stat_modifier_codes=codes),expected)
        for sub,family in enumerate((cloth,leather,mail,plate),1):
            for slot in (1,3,5,6,7,8,9,10,20):
                for codes,primary in [([3],agility),([4],strength),([5],intelligence),
                                      ([71],all_specs),([],all_specs)]:
                    with self.subTest(sub=sub,slot=slot,codes=codes):
                        self.assertEqual(eligible(category="special_effect_gear_candidate",
                            inventory_type=slot,subclass_id=sub,stat_modifier_codes=codes),family&primary)
            for slot in (2,11,16):
                self.assertEqual(eligible(category="special_effect_gear_candidate",
                    inventory_type=slot,subclass_id=sub,stat_modifier_codes=[71]),all_specs)
        two_hand={"deathknight/unholy","warrior/fury","warrior/arms",
                  "paladin/retribution","druid/feral","hunter/survival","monk/windwalker"}
        frill=cloth|{"druid/balance","evoker/devastation"}
        ranged={"hunter/beast_mastery","hunter/marksmanship"}
        for slot,cl,sub,expected in (
            (17,2,8,two_hand),(23,4,0,frill),(14,4,6,{"shaman/elemental"}),
            (15,2,2,ranged),(26,2,19,set()),(13,2,15,all_specs-two_hand-ranged),
            (12,4,0,set())):
            with self.subTest(slot=slot,cl=cl,sub=sub):
                self.assertEqual(eligible(category="special_effect_gear_candidate",
                    inventory_type=slot,class_id=cl,subclass_id=sub,
                    stat_modifier_codes=[71]),expected)
        self.assertEqual(eligible(allowed_class_mask=128,stat_modifier_codes=[5]),
                         {"mage/arcane","mage/fire","mage/frost"})
        self.assertEqual(eligible(allowed_class_mask=128,stat_modifier_codes=[3]),set())
        # Provisional craft stat distribution is not a fixed primary filter.
        self.assertEqual(eligible(category="selectable_stat_craft",inventory_type=5,
                                  subclass_id=2,stat_modifier_codes=[4]),leather)
        # Loot source role alone cannot forbid a physically compatible trinket.
        self.assertEqual(eligible(loot_spec_metadata={"roles":["TANK"]}),all_specs)

    def test_fixed_primary_armor_class_and_unknown(self):
        def eligible(**changes):
            row={"category":"trinket","inventory_type":12,"class_id":4,
                 "subclass_id":0,"allowed_class_mask":-1,
                 "stat_modifier_codes":[]}
            row.update(changes)
            return set(adapter.equipment_primary_armor_compatibility(row)["compatible_dps_specs"])
        intellect=eligible(stat_modifier_codes=[5,32])
        self.assertIn("mage/fire",intellect)
        self.assertIn("shaman/elemental",intellect)
        self.assertNotIn("shaman/enhancement",intellect)
        self.assertNotIn("warrior/fury",intellect)
        self.assertNotIn("rogue/outlaw",intellect)
        strength=eligible(stat_modifier_codes=[4])
        self.assertIn("warrior/fury",strength)
        self.assertNotIn("mage/fire",strength)
        multi=eligible(stat_modifier_codes=[71])
        self.assertEqual(len(multi),26)
        self.assertEqual(eligible(stat_modifier_codes=[32]),multi)
        self.assertEqual(eligible(stat_modifier_codes=None),multi)
        cloth=eligible(category="special_effect_gear_candidate",inventory_type=5,subclass_id=1,stat_modifier_codes=[5])
        self.assertIn("mage/fire",cloth)
        self.assertNotIn("shaman/elemental",cloth)
        self.assertNotIn("druid/balance",cloth)
        self.assertEqual(eligible(allowed_class_mask=128),{"mage/arcane","mage/fire","mage/frost"})
        self.assertIn("mage/fire",eligible(category="selectable_stat_craft",inventory_type=5,subclass_id=1,stat_modifier_codes=[4]))
        self.assertFalse(adapter.equipment_primary_armor_compatibility({})["spec_role_source_verified"])

if __name__=="__main__":
    unittest.main()
