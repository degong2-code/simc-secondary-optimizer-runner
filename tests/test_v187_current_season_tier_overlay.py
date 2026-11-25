"""v187: selected items + current-season 4 of 5 tier slot reconciliation.

Offline-only real season DB and fake selected item overlays. Not SimC Native,
not an independent proc/catalyst eligibility certification.
"""
from __future__ import annotations
import copy,pathlib,sys,tempfile,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v101_common_representative_equipment as common
import v139_pure_target_profile_composer as pure
import v169_source_first_representative_stage as season
import v106_user_session_controller as sessions

class CurrentSeasonTierReconciliation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.map=season.load_tier()["classes"]["mage"]["pieces"]
    def setup_rows(self):
        user=sessions.user_scenario(sessions.standard_controls(("mage","frost")))
        scope=season.season_scope()
        _,_,rows,groups,*_=pure.v098_inputs(
            user["character"],user["trinkets"],target_ilevel=334,
            combat=user["combat"],season_override=scope)
        return user,rows,groups
    def apply(self,user,rows,groups):
        return common.apply_user_equipment(
            ("mage","frost"),rows,groups,user,334,
            lambda v,code:self.fail(code) if not v else None,
            tier_override=self.map,
            fifth_override=("chest",self.map["chest"],159257),
            flexible_current_tier=True)
    def assert_four(self,rows,groups):
        tier={slot for slot in common.TIER_FIVE if groups.get(slot)=="tier"}
        self.assertEqual(len(tier),4)
        self.assertTrue(all(rows[s]["item_id"]==self.map[s] for s in tier))
        self.assertEqual(len(set(x["item_id"] for x in rows.values())),
                         len(rows))

    def test_new_build_source_injection_accepts_only_its_own_selected_id(self):
        import v167_product_season_gear_adapter as product_gear
        gear=copy.deepcopy(product_gear.read())
        tier=copy.deepcopy(season.load_tier())
        # Synthetic alternative build, not a claim of fresh game evidence.
        gear["season_build"]="12.1.5.79999"
        tier["retail_build"]="12.1.5.79999"
        row=next(x for x in gear["items"] if x["item_id"]==239652)
        row["item_id"]=939652
        user,rows,groups=self.setup_rows()
        user["embellishments"]=[{
            "slot":"head","item_id":939652,
            "options":{"crafted_stats":"32/36",
                       "embellishment":"arcanoweave_lining"}}]
        require=lambda valid,why:self.fail(why) if not valid else None
        # Legacy packaged IDs must not accept the new source item.
        with self.assertRaisesRegex(AssertionError,
                      "CURRENT_SEASON_SELECTED_ITEM_NOT_IN_APPROVED_ROLE"):
            common.apply_user_equipment(
                ("mage","frost"),copy.deepcopy(rows),dict(groups),
                user,334,require,tier_override=self.map,
                fifth_override=("chest",self.map["chest"],159257),
                flexible_current_tier=True)
        with mock.patch.object(product_gear,"read",
                               side_effect=AssertionError("LEGACY_GEAR_READ")), \
             mock.patch.object(season,"load_tier",
                               side_effect=AssertionError("LEGACY_TIER_READ")):
            restored,origin=common.apply_user_equipment(
                ("mage","frost"),rows,groups,user,334,require,
                tier_override=tier["classes"]["mage"]["pieces"],
                fifth_override=("chest",self.map["chest"],159257),
                flexible_current_tier=True,season_source_gear=gear,
                season_source_tier=tier)
        self.assertEqual(restored,["chest"])
        self.assertEqual(origin,[])
        self.assertEqual(rows["head"]["item_id"],939652)
        self.assert_four(rows,groups)

    def test_refresh_special_validation_only_does_not_change_original_four_tier(self):
        import v167_product_season_gear_adapter as product_gear
        gear=product_gear.read()
        tier=season.load_tier()
        snapshot=copy.deepcopy(gear)
        u,rows,groups=self.setup_rows()
        original=copy.deepcopy(rows)
        new_id=999991
        extra={"item_id":new_id,"category":"special_effect_gear_candidate",
               "inventory_type":11,"class_id":4,"subclass_id":0,
               "allowed_class_mask":None}
        u["special_items"]=[{"slot":"finger1","item_id":new_id,"options":{}}]
        require=lambda valid,why:self.fail(why) if not valid else None
        args=dict(tier_override=self.map,
            fifth_override=("chest",self.map["chest"],159257),
            flexible_current_tier=True,season_source_gear=gear,
            season_source_tier=tier)
        with self.assertRaisesRegex(AssertionError,"CURRENT_SEASON_SELECTED_ITEM_NOT_IN_APPROVED_ROLE"):
            common.apply_user_equipment(("mage","frost"),copy.deepcopy(rows),
                dict(groups),u,334,require,**args)
        with self.assertRaisesRegex(AssertionError,"CURRENT_SEASON_SELECTED_ITEM_WRONG_PHYSICAL_SLOT"):
            common.apply_user_equipment(("mage","frost"),copy.deepcopy(rows),
                dict(groups),u,334,require,**args,
                selected_refresh_rows=[{**extra,"inventory_type":2}])
        common.apply_user_equipment(("mage","frost"),rows,groups,u,334,require,
                                    **args,selected_refresh_rows=[extra])
        self.assertEqual(rows["finger1"]["item_id"],new_id)
        self.assertEqual(gear,snapshot)
        self.assertEqual({s:r for s,r in rows.items() if s!="finger1"},
                         {s:r for s,r in original.items() if s!="finger1"})
        self.assert_four(rows,groups)

    def test_exact_effect_option_applies_from_base_or_refresh_and_preserves_four_tier(self):
        import v167_product_season_gear_adapter as product_gear
        base=product_gear.read()
        tier=season.load_tier()
        # Synthetic fixture: an unused ID and a typed source option, not
        # evidence of any actual new effect, budget or item.
        row={"item_id":999991,"name":"Synthetic option ring",
             "category":"special_effect_gear_candidate","inventory_type":11,
             "class_id":4,"subclass_id":0,"allowed_class_mask":-1,
             "stat_modifier_codes":[32],"item_set_id":0,"slot_hint":None,
             "source_kinds":["raid_journal"],
             "season_list_basis":"SEALED_CONTEXT_FREE_EFFECT_OPTION",
             "required_options":{"bonus_id":"987654"}}
        merged=product_gear.merge_effect_option_rows(base,[row])
        args=dict(tier_override=self.map,
            fifth_override=("chest",self.map["chest"],159257),
            flexible_current_tier=True,season_source_tier=tier)
        require=lambda valid,why:self.fail(why) if not valid else None
        for source,refresh in ((merged,None),(base,[row])):
            user,rows,groups=self.setup_rows()
            user["special_items"]=[{"slot":"finger1","item_id":row["item_id"],"options":{}}]
            common.apply_user_equipment(("mage","frost"),rows,groups,user,334,require,
                season_source_gear=source,selected_refresh_rows=refresh,**args)
            self.assertEqual(rows["finger1"]["options"]["bonus_id"],"987654")
            self.assert_four(rows,groups)
            user,rows,groups=self.setup_rows()
            user["special_items"]=[{"slot":"finger1","item_id":row["item_id"],
                                    "options":{"bonus_id":"987655"}}]
            with self.assertRaisesRegex(AssertionError,"SELECTED_EFFECT_BONUS_OPTION_CONFLICT"):
                common.apply_user_equipment(("mage","frost"),rows,groups,user,334,require,
                    season_source_gear=source,selected_refresh_rows=refresh,**args)

    def test_fixed_special_primary_consistency_in_base_and_refresh(self):
        import v167_product_season_gear_adapter as product_gear
        base=product_gear.read()
        tier=season.load_tier()
        require=lambda valid,why:self.fail(why) if not valid else None
        args=dict(tier_override=self.map,
            fifth_override=("chest",self.map["chest"],159257),
            flexible_current_tier=True,season_source_tier=tier)
        # Synthetic cloak: compare existing public eligibility to profile
        # assembly, not a claim about a live item.
        for codes,allowed in (([3],False),([4],False),([5],True),
                              ([71],True),([73],True),([32],True),([],True)):
            row={"item_id":999991,"name":"Synthetic fixed cloak",
                 "category":"special_effect_gear_candidate","inventory_type":16,
                 "class_id":4,"subclass_id":1,"allowed_class_mask":-1,
                 "stat_modifier_codes":codes,"item_set_id":0,"slot_hint":"back",
                 "source_kinds":["raid_journal"],
                 "season_list_basis":"SEALED_CONTEXT_FREE_EFFECT_OPTION",
                 "required_options":{"bonus_id":"987654"}}
            merged=product_gear.merge_effect_option_rows(base,[row])
            public=product_gear.public_options(merged)["choices"]["special_effect_gear_candidate"]
            item=next(x for x in public if x["item_id"]==row["item_id"])
            self.assertEqual("mage/frost" in item["compatible_dps_specs"],allowed)
            for source,refresh in ((merged,None),(base,[row])):
                with self.subTest(codes=codes,refresh=refresh is not None):
                    user,rows,groups=self.setup_rows()
                    user["special_items"]=[{"slot":"back","item_id":row["item_id"],"options":{}}]
                    before=copy.deepcopy(rows)
                    if not allowed:
                        with self.assertRaisesRegex(AssertionError,
                                "CURRENT_SEASON_SPECIAL_ITEM_WRONG_PRIMARY:back"):
                            common.apply_user_equipment(("mage","frost"),rows,groups,
                                user,334,require,season_source_gear=source,
                                selected_refresh_rows=refresh,**args)
                        self.assertEqual(rows,before)
                    else:
                        common.apply_user_equipment(("mage","frost"),rows,groups,
                            user,334,require,season_source_gear=source,
                            selected_refresh_rows=refresh,**args)
                        self.assertEqual(rows["back"]["item_id"],row["item_id"])
                        self.assertEqual(rows["back"]["options"]["bonus_id"],"987654")
                        self.assert_four(rows,groups)

    def test_new_build_source_pair_and_build_mismatch_fail_closed(self):
        import v167_product_season_gear_adapter as product_gear
        gear=copy.deepcopy(product_gear.read())
        tier=copy.deepcopy(season.load_tier())
        gear["season_build"]="12.1.5.79999"
        user,rows,groups=self.setup_rows()
        user["embellishments"]=[{
            "slot":"head","item_id":239652,
            "options":{"crafted_stats":"32/36",
                       "embellishment":"arcanoweave_lining"}}]
        require=lambda valid,why:self.fail(why) if not valid else None
        opts={"tier_override":self.map,
              "fifth_override":("chest",self.map["chest"],159257),
              "flexible_current_tier":True,"season_source_gear":gear}
        with self.assertRaisesRegex(AssertionError,
                          "CURRENT_SEASON_SELECTED_SOURCE_PAIR_REQUIRED"):
            common.apply_user_equipment(
                ("mage","frost"),rows,groups,user,334,require,**opts)
        opts["season_source_tier"]=tier
        with self.assertRaisesRegex(AssertionError,
                     "CURRENT_SEASON_SELECTED_SOURCE_BUILD_OR_TIER_DRIFT"):
            common.apply_user_equipment(
                ("mage","frost"),rows,groups,user,334,require,**opts)

    def test_new_build_source_catalyst_overflow_avoids_packaged_read(self):
        import v167_product_season_gear_adapter as product_gear
        gear=copy.deepcopy(product_gear.read())
        tier=copy.deepcopy(season.load_tier())
        gear["season_build"]="12.1.5.79999"
        tier["retail_build"]="12.1.5.79999"
        user,rows,groups=self.setup_rows()
        user["special_items"]=[{
            "slot":"chest","item_id":self.map["chest"],
            "options":{"redirected_base_stats":"159257"}}]
        require=lambda valid,why:self.fail(why) if not valid else None
        with mock.patch.object(product_gear,"read",
                               side_effect=AssertionError("LEGACY_GEAR_READ")), \
             mock.patch.object(season,"load_tier",
                               side_effect=AssertionError("LEGACY_TIER_READ")):
            restored,origin=common.apply_user_equipment(
                ("mage","frost"),rows,groups,user,334,require,
                tier_override=tier["classes"]["mage"]["pieces"],
                fifth_override=("chest",self.map["chest"],159257),
                flexible_current_tier=True,season_source_gear=gear,
                season_source_tier=tier)
        self.assertEqual(restored,[])
        self.assertEqual(origin[0]["slot"],"chest")
        self.assert_four(rows,groups)

    def test_alternate_fifth_catalyst_reuses_one_validated_source_pair(self):
        import v167_product_season_gear_adapter as product_gear
        gear=product_gear.read()
        tier=season.load_tier()
        user,rows,groups=self.setup_rows()
        # Starting with ordinary legs, exact class chest tier.
        leg=season.available_plain(gear,slot="legs",family="cloth",
            class_mask=tier["classes"]["mage"]["allowed_class_mask"],
            primary="intellect")[0]
        rows["legs"]["item_id"]=leg
        rows["chest"]["item_id"]=self.map["chest"]
        del groups["legs"];groups["chest"]="tier"
        user["special_items"]=[{"slot":"legs","item_id":self.map["legs"],
            "options":{"redirected_base_stats":str(leg)}}]
        require=lambda valid,why:self.fail(why) if not valid else None
        with mock.patch.object(common,"_selected_current_season_sources",
                wraps=common._selected_current_season_sources) as sources:
            restored,origin=common.apply_user_equipment(
                ("mage","frost"),rows,groups,user,334,require,
                tier_override=self.map,fifth_override=("legs",self.map["legs"],leg),
                flexible_current_tier=True,season_source_gear=gear,
                season_source_tier=tier)
            self.assertEqual(sources.call_count,1)
        self.assertEqual(restored,[])
        self.assertEqual(origin,[{"slot":"legs","tier_item_id":self.map["legs"],
                                  "source_item_id":leg}])
        self.assertEqual(groups["legs"],"tier")
        self.assertNotIn("hands",groups)
        self.assert_four(rows,groups)
        equipment,fillers=common.physical_gear_groups(rows,groups,origin)
        self.assertEqual(equipment["catalyst_special_tier_slots"],["legs"])
        self.assertEqual(len(equipment["tier"]),4)
        self.assertEqual(len([r for r in fillers if r["slot"]=="hands"]),1)

    def test_unselected_baseline_four_and_both_crafted_non_tier(self):
        u,rows,groups=self.setup_rows()
        u["embellishments"]=[
            {"slot":"back","item_id":239656,
             "options":{"crafted_stats":"32/36","embellishment":"arcanoweave_lining"}},
            {"slot":"feet","item_id":239654,
             "options":{"crafted_stats":"32/36","embellishment":"arcanoweave_lining"}}]
        # These two user-visible slots are outside five tier positions.
        self.apply(u,rows,groups)
        self.assert_four(rows,groups)
        self.assertEqual(set(s for s in common.TIER_FIVE if groups.get(s)=="tier"),
                         {"head","shoulders","hands","legs"})

    def test_one_crafted_head_restores_exact_fifth_chest(self):
        u,rows,groups=self.setup_rows()
        diamond=rows["head"]["options"].get("gem_id")
        u["embellishments"]=[{"slot":"head","item_id":239652,
          "options":{"crafted_stats":"32/36","embellishment":"arcanoweave_lining"}}]
        restored,catalyst=self.apply(u,rows,groups)
        self.assertEqual(restored,["chest"])
        self.assertEqual(catalyst,[])
        self.assertEqual(groups["head"],"crafted")
        self.assertEqual(groups["chest"],"tier")
        self.assertEqual(rows["head"]["item_id"],239652)
        self.assertEqual(rows["head"]["options"]["gem_id"],diamond)
        self.assert_four(rows,groups)

    def test_two_crafted_inside_five_are_explicitly_impossible(self):
        for slots in (("head","shoulders"),("head","chest"),
                      ("hands","legs")):
            with self.subTest(slots=slots):
                u,rows,groups=self.setup_rows()
                source={"head":239652,"shoulders":239650,"chest":239655,
                        "hands":239653,"legs":239651}
                u["embellishments"]=[{"slot":slot,"item_id":source[slot],
                    "options":{"crafted_stats":"32/36",
                               "embellishment":"arcanoweave_lining"}}
                                  for slot in slots]
                with self.assertRaisesRegex(AssertionError,
                        "FOUR_TIER_IMPOSSIBLE_USER_OCCUPIES_TOO_MANY_SLOTS"):
                    self.apply(u,rows,groups)

    def test_selected_catalyst_fifth_demotes_one_internal_tier(self):
        u,rows,groups=self.setup_rows()
        u["special_items"]=[{"slot":"chest","item_id":self.map["chest"],
                             "options":{"redirected_base_stats":"159257"}}]
        restored,catalyst=self.apply(u,rows,groups)
        self.assertEqual(restored,[])
        self.assertEqual(groups["chest"],"tier")
        self.assertEqual(rows["chest"]["item_id"],self.map["chest"])
        self.assertEqual(catalyst,[{"slot":"chest",
                  "tier_item_id":self.map["chest"],"source_item_id":159257}])
        self.assertNotIn("legs",groups)
        self.assertIn("legs",rows)
        self.assertNotEqual(rows["legs"]["item_id"],self.map["legs"])
        self.assert_four(rows,groups)
        equipment,fillers=common.physical_gear_groups(rows,groups,catalyst)
        self.assertEqual(len(equipment["tier"]),4)
        self.assertEqual(equipment["catalyst_special_tier_slots"],["chest"])
        self.assertEqual(len([x for x in fillers if x["slot"]=="legs"]),1)

    def test_catalyst_redirect_requires_exact_current_source_slot_family_and_primary(self):
        import v167_product_season_gear_adapter as product_gear
        source=product_gear.read()
        self.assertEqual(source["season_build"],season.load_tier()["retail_build"])
        u,rows,groups=self.setup_rows()
        u["special_items"]=[{"slot":"head","item_id":self.map["head"],
            "options":{"redirected_base_stats":"271874"}}]
        restored,catalyst=self.apply(u,rows,groups)
        self.assertEqual(catalyst,[{"slot":"head","tier_item_id":self.map["head"],
                                    "source_item_id":271874}])
        # 271876 is a current-season mail chest, not a cloth head.
        for origin,reason in (
            ("999999","CURRENT_SEASON_CATALYST_SOURCE_NOT_IN_APPROVED_ROLE:head"),
            ("271876","CURRENT_SEASON_CATALYST_SOURCE_WRONG_PHYSICAL_SLOT:head"),
            ("271875","CURRENT_SEASON_CATALYST_SOURCE_WRONG_ARMOR_FAMILY:head"),
        ):
            with self.subTest(origin=origin):
                u,rows,groups=self.setup_rows()
                u["special_items"]=[{"slot":"head","item_id":self.map["head"],
                    "options":{"redirected_base_stats":origin}}]
                with self.assertRaisesRegex(AssertionError,reason):
                    self.apply(u,rows,groups)

    def test_actual_v098_product_catalyst_profile_binds_current_source_and_blocks_missing_L(self):
        import v098_target_user_scenario_bootstrap as bootstrap
        import v090_reference_total_native_candidate as reference
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            fake=root/"simc-not-executed"
            fake.write_bytes(b"NO_SIMC_EXECUTION")
            user,_,_=self.setup_rows()
            user["special_items"]=[{"slot":"head","item_id":self.map["head"],
                "options":{"redirected_base_stats":"271874"}}]
            result=bootstrap.build(user,root/"probe",fake,"7bc10711b5",
                current_season_product=True,static_special_probe_only=True)
            self.assertEqual(result["schema"],
                             "v208_exact_current_special_static_source_v1")
            self.assertEqual(result["native_calls"],0)
            self.assertTrue(result["no_optimization_or_budget_produced"])
            self.assertEqual(len(result["special_rows"]),1)
            self.assertEqual(result["special_rows"][0]["item_id"],self.map["head"])
            self.assertEqual(
                result["special_rows"][0]["options"]["redirected_base_stats"],
                "271874")
            self.assertEqual(len(result["source_profile_sha256"]),64)
            head=next(x for x in result["profile"].splitlines()
                      if x.startswith("head="))
            self.assertIn("id="+str(self.map["head"]),head)
            self.assertIn("redirected_base_stats=271874",head)
            # Full budget/profile execution remains blocked until this exact
            # redirected tier variant has an original Native JSON2 static L.
            with self.assertRaisesRegex(
                    reference.ReferenceNativeBlocked,
                    "SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT"):
                bootstrap.build(user,root/"blocked",fake,"7bc10711b5",
                                current_season_product=True)
    def test_catalyst_source_identity_generalizes_across_all_26_dps_specs(self):
        import v143_specialization_contracts as contracts
        import v167_product_season_gear_adapter as product_gear
        db=product_gear.read()
        tier_source=season.load_tier()
        self.assertEqual(len(contracts.CONTRACTS),26)
        inv={"head":(1,),"shoulders":(3,),"chest":(5,20),
             "hands":(10,),"legs":(7,)}
        for key,contract in sorted(contracts.CONTRACTS.items()):
            cls,sp=key.split("/")
            with self.subTest(spec=key):
                user=sessions.user_scenario(sessions.standard_controls((cls,sp)))
                scope=season.season_scope()
                _,_,rows,groups,form,F,tier_map,fifth=pure.v098_inputs(
                    user["character"],user["trinkets"],target_ilevel=334,
                    combat=user["combat"],season_override=scope)
                slot=next(s for s in common.TIER_FIVE if groups.get(s)=="tier")
                mask=tier_source["classes"][cls]["allowed_class_mask"]
                family=product_gear.ARMOR_SUBCLASS[contract["family"]]
                primary=season.PRIMARY_STAT_CODES[contract["primary"]]
                candidates=sorted((x for x in db["items"]
                    if x["category"]=="plain_representative_candidate"
                    and x["class_id"]==4 and x["subclass_id"]==family
                    and x["inventory_type"] in inv[slot]
                    and "raid_journal" in x.get("source_kinds",[])
                    and any(code in primary for code in
                            x.get("stat_modifier_codes",[]))
                    and (x.get("allowed_class_mask") is None or
                         (type(x.get("allowed_class_mask")) is int and
                          (x["allowed_class_mask"]&mask)==mask))),
                    key=lambda x:x["item_id"])
                self.assertTrue(candidates,"NO_SAME_BUILD_ORIGIN:"+key+":"+slot)
                origin=candidates[0]["item_id"]
                user["special_items"]=[{"slot":slot,"item_id":tier_map[slot],
                    "options":{"redirected_base_stats":str(origin)}}]
                def require(ok,reason):
                    if not ok:raise AssertionError(reason)
                restored,catalyst=common.apply_user_equipment(
                    (cls,sp),rows,groups,user,334,require,
                    tier_override=tier_map,fifth_override=fifth,
                    flexible_current_tier=True,season_source_gear=db,
                    season_source_tier=tier_source)
                self.assertEqual(catalyst,[{"slot":slot,
                    "tier_item_id":tier_map[slot],"source_item_id":origin}])
                self.assertEqual(sum(groups.get(s)=="tier"
                                     for s in common.TIER_FIVE),4)
                equipment,_=common.physical_gear_groups(rows,groups,catalyst)
                self.assertEqual(len(equipment["tier"]),4)
                self.assertEqual(equipment["catalyst_special_tier_slots"],[slot])

    def test_duplicate_catalyst_and_special_slot_is_rejected(self):
        u,rows,groups=self.setup_rows()
        catalyst={"slot":"head","item_id":self.map["head"],
                  "options":{"redirected_base_stats":"271874"}}
        u["special_items"]=[copy.deepcopy(catalyst),copy.deepcopy(catalyst)]
        with self.assertRaisesRegex(AssertionError,
                                    "SELECTED_SLOT_INVALID_OR_DUPLICATE"):
            self.apply(u,rows,groups)

    def test_catalyst_head_and_crafted_chest_still_four(self):
        u,rows,groups=self.setup_rows()
        u["special_items"]=[{"slot":"head","item_id":self.map["head"],
                             "options":{"redirected_base_stats":"159236"}}]
        u["embellishments"]=[{"slot":"chest","item_id":239655,
          "options":{"crafted_stats":"32/36","embellishment":"arcanoweave_lining"}}]
        restored,catalyst=self.apply(u,rows,groups)
        self.assertEqual(restored,[])
        self.assertEqual(catalyst[0]["slot"],"head")
        self.assertEqual(groups["chest"],"crafted")
        self.assert_four(rows,groups)

    def test_wrong_class_tier_catalyst_id_rejected(self):
        u,rows,groups=self.setup_rows()
        u["special_items"]=[{"slot":"head","item_id":271555,
                             "options":{"redirected_base_stats":"159236"}}]
        with self.assertRaisesRegex(AssertionError,
                             "CURRENT_SEASON_SELECTED_ITEM_NOT_IN_APPROVED_ROLE:head"):
            self.apply(u,rows,groups)

    def test_all_26_specs_crafted_head_reassigns_fifth_tier_without_native(self):
        import v143_specialization_contracts as contracts
        import v167_product_season_gear_adapter as catalog
        items=catalog.read()["items"]
        source=season.season_scope()
        sets=season.load_tier()["classes"]
        self.assertEqual(len(contracts.CONTRACTS),26)
        for key,contract in sorted(contracts.CONTRACTS.items()):
            with self.subTest(spec=key):
                cls,sp=key.split("/")
                control=sessions.standard_controls((cls,sp))
                user=sessions.user_scenario(control)
                _,_,rows,groups,form,F,tier_map,fifth=pure.v098_inputs(
                    user["character"],user["trinkets"],
                    target_ilevel=334,combat=user["combat"],
                    season_override=source)
                family=catalog.ARMOR_SUBCLASS[contract["family"]]
                head_craft=sorted(x["item_id"] for x in items
                   if x["category"]=="selectable_stat_craft"
                   and x["class_id"]==4 and x["subclass_id"]==family
                   and x["inventory_type"]==1)
                self.assertTrue(head_craft)
                chosen=head_craft[0]
                user["embellishments"]=[{"slot":"head","item_id":chosen,
                     "options":{"crafted_stats":"32/36",
                                "embellishment":"arcanoweave_lining"}}]
                def require(ok,code):
                    if not ok:raise AssertionError(code)
                restored,catalyst=common.apply_user_equipment(
                    (cls,sp),rows,groups,user,334,require,
                    tier_override=tier_map,fifth_override=fifth,
                    flexible_current_tier=True)
                self.assertEqual(restored,["chest"])
                self.assertEqual(catalyst,[])
                self.assertEqual(groups["head"],"crafted")
                self.assertEqual(rows["head"]["item_id"],chosen)
                actual_tiers={slot for slot in common.TIER_FIVE
                              if groups.get(slot)=="tier"}
                self.assertEqual(actual_tiers,
                                 {"shoulders","chest","hands","legs"})
                self.assertEqual(tier_map,sets[cls]["pieces"])
                self.assertEqual(len({v["item_id"] for v in rows.values()}),
                                 len(rows))
                equipment,fillers=common.physical_gear_groups(
                    rows,groups,catalyst)
                self.assertEqual(len(equipment["tier"]),4)
                self.assertEqual(len(equipment["crafted"]),1)

    def test_actual_v098_product_head_craft_rebuilds_four_tier_zero_native(self):
        import v098_target_user_scenario_bootstrap as bootstrap
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            fake=root/"simc-not-executed"
            fake.write_bytes(b"NO_SIMC_EXECUTION")
            u,_,_=self.setup_rows()
            u["embellishments"]=[{"slot":"head","item_id":239652,
                "options":{"crafted_stats":"32/36",
                           "embellishment":"arcanoweave_lining"}}]
            result=bootstrap.build(u,root/"valid",fake,"7bc10711b5",
                                   current_season_product=True)
            self.assertEqual(result["native_calls"],0)
            self.assertEqual(result["restored_tier_slots"],["chest"])
            self.assertEqual(set(result["effective_four_tier_slots"]),
                             {"shoulders","chest","hands","legs"})
            scenario=__import__("json").loads(
                     (root/"valid"/"scenario.json").read_text("utf8"))
            self.assertEqual(len(scenario["equipment"]["tier"]),4)
            self.assertEqual(len(scenario["equipment"]["crafted"]),1)
            profile=(root/"valid"/"profile.simc").read_text("utf8")
            self.assertIn("head=selected_239652,id=239652",profile)
            self.assertIn("chest=selected_"+str(self.map["chest"])+
                          ",id="+str(self.map["chest"]),profile)

    def test_actual_v098_product_two_tier_crafts_block_before_simc(self):
        import v098_target_user_scenario_bootstrap as bootstrap
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            fake=root/"simc-not-executed"
            fake.write_bytes(b"NO_SIMC_EXECUTION")
            u,_,_=self.setup_rows()
            u["embellishments"]=[
                {"slot":"head","item_id":239652,
                 "options":{"crafted_stats":"32/36",
                            "embellishment":"arcanoweave_lining"}},
                {"slot":"shoulders","item_id":239650,
                 "options":{"crafted_stats":"32/36",
                            "embellishment":"arcanoweave_lining"}}]
            with self.assertRaisesRegex(
                ValueError,"FOUR_TIER_IMPOSSIBLE_USER_OCCUPIES_TOO_MANY_SLOTS"):
                bootstrap.build(u,root/"invalid",fake,"7bc10711b5",
                                current_season_product=True)
            self.assertFalse((root/"invalid"/"manifest.json").exists())

    def test_only_real_season_special_role_can_overlay_tier(self):
        u,rows,groups=self.setup_rows()
        # 159236 is plain cloth head, NOT user-selectable special effect.
        u["special_items"]=[{"slot":"head","item_id":159236,"options":{}}]
        with self.assertRaisesRegex(AssertionError,
                  "CURRENT_SEASON_SELECTED_ITEM_NOT_IN_APPROVED_ROLE:head"):
            self.apply(u,rows,groups)

    def test_special_item_wrong_slot_and_wrong_primary_rejected(self):
        u,rows,groups=self.setup_rows()
        # Current-season special cloak 159288 must not be slotted as head.
        u["special_items"]=[{"slot":"head","item_id":159288,"options":{}}]
        with self.assertRaisesRegex(AssertionError,
                  "CURRENT_SEASON_SELECTED_ITEM_WRONG_PHYSICAL_SLOT:head"):
            self.apply(u,rows,groups)
        u,rows,groups=self.setup_rows()
        # Agility dagger 271093 is not a mage intellect weapon.
        u["special_items"]=[{"slot":"main_hand","item_id":271093,"options":{}}]
        with self.assertRaisesRegex(AssertionError,
                  "CURRENT_SEASON_SPECIAL_WEAPON_WRONG_PRIMARY:main_hand"):
            self.apply(u,rows,groups)

    def test_source_weapon_subclass_matches_public_and_overlay(self):
        import v167_product_season_gear_adapter as product_gear
        base=product_gear.read()
        tier=season.load_tier()
        require=lambda valid,why:self.fail(why) if not valid else None
        # Same inventory and primary, different subclass. Synthetic IDs
        # isolate physical rules; no live item or effect certification.
        for key,inv,cases in (
                ("rogue/assassination",13,((13,False),(15,True))),
                ("hunter/beast_mastery",26,((19,False),(18,True))),
                ("hunter/marksmanship",26,((19,False),(3,True)))):
            cls,sp=key.split("/")
            tier_map=tier["classes"][cls]["pieces"]
            for sub,allowed in cases:
                row={"item_id":999991,"name":"Synthetic fixed weapon",
                     "category":"special_effect_gear_candidate",
                     "inventory_type":inv,"class_id":2,"subclass_id":sub,
                     "allowed_class_mask":-1,"stat_modifier_codes":[3],
                     "item_set_id":0,"slot_hint":None,
                     "source_kinds":["raid_journal"],
                     "season_list_basis":"SEALED_CONTEXT_FREE_EFFECT_OPTION",
                     "required_options":{"bonus_id":"987654"}}
                self.assertEqual(key in product_gear.equipment_primary_armor_compatibility(
                    row)["compatible_dps_specs"],allowed)
                craft={**row,"category":"selectable_stat_craft"}
                self.assertEqual(key in product_gear.equipment_primary_armor_compatibility(
                    craft)["compatible_dps_specs"],allowed)
                merged=product_gear.merge_effect_option_rows(base,[row])
                hands=("main_hand","off_hand") if cls=="rogue" else ("main_hand",)
                for source,refresh in ((merged,None),(base,[row])):
                    for hand in hands:
                        with self.subTest(spec=key,sub=sub,hand=hand,refresh=refresh is not None):
                            user=sessions.user_scenario(sessions.standard_controls((cls,sp)))
                            _,_,rows,groups,_,_,_,fifth=pure.v098_inputs(
                                user["character"],user["trinkets"],target_ilevel=334,
                                combat=user["combat"],season_override=season.season_scope())
                            user["special_items"]=[{"slot":hand,"item_id":row["item_id"],"options":{}}]
                            args=dict(tier_override=tier_map,fifth_override=fifth,
                                flexible_current_tier=True,season_source_tier=tier,
                                season_source_gear=source,selected_refresh_rows=refresh)
                            if not allowed:
                                with self.assertRaisesRegex(AssertionError,
                                        "CURRENT_SEASON_SELECTED_WEAPON_WRONG_SUBCLASS:"+hand):
                                    common.apply_user_equipment((cls,sp),rows,groups,user,334,require,**args)
                            else:
                                common.apply_user_equipment((cls,sp),rows,groups,user,334,require,**args)
                                self.assertEqual(rows[hand]["item_id"],row["item_id"])
                                self.assertEqual(sum(groups.get(s)=="tier" for s in common.TIER_FIVE),4)

    def test_v188_armor_lining_rejected_on_real_ring_neck_and_weapon_crafts(self):
        # SimC's embellishment parser is intentionally permissive; our
        # product must respect optional-reagent recipe slot restrictions.
        for slot,item_id in (("finger1",240947),("neck",240948),
                             ("main_hand",237838)):
            with self.subTest(slot=slot):
                u,rows,groups=self.setup_rows()
                u["embellishments"]=[{"slot":slot,"item_id":item_id,
                    "options":{"crafted_stats":"32/36",
                               "embellishment":"arcanoweave_lining"}}]
                with self.assertRaisesRegex(AssertionError,
                      "CURRENT_SEASON_EMBELLISHMENT_WRONG_EQUIPMENT_CATEGORY:"+slot):
                    self.apply(u,rows,groups)

    def test_selected_crafted_wrong_family_and_slot_rejected(self):
        u,rows,groups=self.setup_rows()
        u["embellishments"]=[{"slot":"head","item_id":237832,
           "options":{"crafted_stats":"32/36",
                      "embellishment":"arcanoweave_lining"}}]
        # 237832 is plate head; mage requires cloth.
        with self.assertRaisesRegex(AssertionError,
                  "CURRENT_SEASON_SELECTED_ITEM_WRONG_ARMOR_FAMILY:head"):
            self.apply(u,rows,groups)
        u,rows,groups=self.setup_rows()
        u["embellishments"]=[{"slot":"legs","item_id":239652,
           "options":{"crafted_stats":"32/36",
                      "embellishment":"arcanoweave_lining"}}]
        with self.assertRaisesRegex(AssertionError,
                  "CURRENT_SEASON_SELECTED_ITEM_WRONG_PHYSICAL_SLOT:legs"):
            self.apply(u,rows,groups)

if __name__=="__main__":unittest.main()
