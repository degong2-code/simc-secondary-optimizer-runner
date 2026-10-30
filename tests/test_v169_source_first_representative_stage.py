"""v169: no legacy gear seeding; 26 DPS source-first 4pc preview only."""
import copy
import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v169_source_first_representative_stage as stage
import v167_product_season_gear_adapter as gear

class SourceFirstRepresentative(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=gear.read()
        cls.tier=stage.load_tier()

    def test_all_26_classes_four_real_tier_without_source_profile_copy(self):
        plan=stage.build_all(self.db,self.tier)
        # Returning dungeons enlarge the INTERNAL plain gear pool only.
        # They never add user-selectable ordinary equipment controls.
        self.assertEqual(self.db["item_count"],511)
        self.assertEqual(self.db["role_counts"]["plain_representative_candidate"],328)
        self.assertEqual(plan["dps_specs"],26)
        self.assertEqual(plan["tier_classes"],13)
        self.assertEqual(plan["simc_native_calls"],0)
        self.assertFalse(plan["old_profile_item_ids_copied"])
        self.assertFalse(plan["profile_activated_in_v098"])
        self.assertFalse(plan["all_items_physical_simc_accepted"])
        source_ids={x["item_id"] for x in self.db["items"]}
        for name,spec in plan["specializations"].items():
            with self.subTest(spec=name):
                cl=name.split("/")[0]
                self.assertEqual(spec["tier_ids"],self.tier["classes"][cl]["pieces"])
                self.assertEqual(set(spec["four_tier_slots"]),set(stage.FOUR))
                self.assertEqual(set(spec["ordinary"]),set(stage.ORDINARY))
                self.assertEqual(set(spec["weapons"]),set(
                    stage.contracts.WEAPON_FORMS[spec["weapon_form"]]))
                self.assertEqual(len(set(spec["weapons"].values())),
                                 len(spec["weapons"]))
                self.assertTrue(set(spec["ordinary"].values())<=source_ids)
                self.assertTrue(set(spec["weapons"].values())<=source_ids)
        self.assertTrue(set(plan["common_gear"].values())<=source_ids)

    def test_new_source_profile_text_only_uses_new_item_ids(self):
        sample={"class":"paladin","spec":"retribution",
                "race":"human","talents":"abc123456789"}
        trinkets=[{"slot":slot,"item_id":iid,"options":{}}
                  for slot,iid in zip(("trinket1","trinket2"),
                   [r["item_id"] for r in self.db["items"]
                    if r["category"]=="trinket"][:2])]
        proof=stage.compose_stage(sample,trinkets,db=self.db,tier=self.tier)
        self.assertEqual(proof["status"],"PROFILE_TEXT_PREVIEW_ONLY_NOT_NATIVE_ACCEPTED")
        self.assertEqual(proof["profile_receipt"]["status"],"STAGED_NOT_USER_READY")
        self.assertIn("default_actions=1",proof["profile_text"])
        self.assertEqual(proof["native_calls"],0)
        self.assertFalse(proof["full_profile_native_accepted"])
        self.assertTrue(proof["new_current_season_equipment_only"])

    def test_all_26_stage_as_v139_profile_text_without_old_item_ids(self):
        from v143_specialization_contracts import CONTRACTS
        trinkets=[{"slot":slot,"item_id":iid,"options":{}}
                  for slot,iid in zip(("trinket1","trinket2"),
                   [r["item_id"] for r in self.db["items"]
                    if r["category"]=="trinket"][:2])]
        for name,contract in sorted(CONTRACTS.items()):
            with self.subTest(spec=name):
                cls,spec=name.split("/")
                races=contract["allowed_races"]
                character={"class":cls,"spec":spec,
                           "race":races[0] if races else "human",
                           "talents":"abc123456789"}
                proof=stage.compose_stage(character,trinkets,
                                          db=self.db,tier=self.tier)
                self.assertEqual(proof["profile_receipt"]["spec"],name)
                self.assertEqual(proof["profile_receipt"]["physical_slots"],
                                 15 if contract["weapon_form"] in (
                                     "single_one_hand","single_two_hand","ranged") else 16)
                self.assertEqual(len(proof["profile_receipt"]["four_tier_item_ids"]),4)
                self.assertFalse(proof["full_profile_native_accepted"])
                self.assertIn("default_actions=1",proof["profile_text"])
                self.assertEqual(proof["native_calls"],0)

    def test_build_mismatch_rejected_not_implicit_repair(self):
        snapshot=copy.deepcopy(self.db)
        snapshot["season_build"]="12.1.5.70576"
        with self.assertRaises(stage.RepresentativeBlocked):
            stage.build_all(snapshot,self.tier)
        scope=copy.deepcopy(self.tier)
        scope["classes"].pop("evoker")
        with self.assertRaises(stage.RepresentativeBlocked):
            stage.build_all(self.db,scope)

    def test_all_26_weapon_and_offhand_primary_stats_are_compatible(self):
        # Prevent regression to v176: Native may execute successfully while
        # the selected dagger/staff/sword has the WRONG primary stat.
        plan=stage.build_all(self.db,self.tier)
        by_id={x["item_id"]:x for x in self.db["items"]}
        expected={"strength":{4,71,72,74},
                  "agility":{3,71,72,73},
                  "intellect":{5,71,73,74}}
        self.assertEqual(len(plan["specializations"]),26)
        checked=0
        for key,info in plan["specializations"].items():
            contract=stage.contracts.CONTRACTS[key]
            cls=key.split("/")[0]
            class_mask=self.tier["classes"][cls]["allowed_class_mask"]
            primary=expected[contract["primary"]]
            for slot,item_id in info["weapons"].items():
                with self.subTest(spec=key,slot=slot,item_id=item_id):
                    item=by_id[item_id]
                    self.assertEqual(item["category"],"plain_representative_candidate")
                    self.assertIs(type(item.get("stat_modifier_codes")),list)
                    self.assertTrue(primary.intersection(item["stat_modifier_codes"]))
                    mask=item.get("allowed_class_mask")
                    if mask is not None:
                        self.assertEqual(mask&class_mask,class_mask)
                    if item["class_id"]==4:
                        self.assertEqual(slot,"off_hand")
                        self.assertIn(item["inventory_type"],(14,23))
                    else:
                        self.assertEqual(item["class_id"],2)
                        self.assertIn(item["subclass_id"],
                          stage.SPEC_SUBCLASS_PREFS.get(
                            key,stage.FORM_SUBCLASS_PREFS[contract["weapon_form"]]))
                        if contract["weapon_form"]=="ranged":
                            self.assertIn(item["inventory_type"],(15,26))
                        elif contract["weapon_form"] in ("dual_two_hand","single_two_hand"):
                            self.assertEqual(item["inventory_type"],17)
                        else:
                            self.assertEqual(item["inventory_type"],13)
                    checked+=1
            self.assertEqual(
                set(info["weapons"]),set(
                    stage.contracts.WEAPON_FORMS[contract["weapon_form"]]))
            self.assertEqual(
                info["tier_ids"],self.tier["classes"][cls]["pieces"])
        self.assertEqual(checked,44)

    def test_historical_wrong_primary_choices_are_not_reused(self):
        plan=stage.build_all(self.db,self.tier)["specializations"]
        wrong={("mage/frost","main_hand"):159136,
               ("druid/feral","main_hand"):159636,
               ("deathknight/frost","off_hand"):158714,
               ("rogue/assassination","off_hand"):159137,
               ("shaman/enhancement","main_hand"):158369,
               ("rogue/outlaw","main_hand"):158373}
        for (key,slot),id in wrong.items():
            with self.subTest(spec=key,slot=slot):
                self.assertNotEqual(plan[key]["weapons"][slot],id)
        self.assertEqual(plan["mage/frost"]["weapons"]["main_hand"],159137)

    def test_missing_primary_or_malformed_codes_fail_closed(self):
        broken=copy.deepcopy(self.db)
        # There ARE many one-handed daggers, but none may be accepted as
        # a mage weapon after their explicit INT code is removed.
        for x in broken["items"]:
            if x["category"]=="plain_representative_candidate" and (
                x["class_id"]==2 and x["inventory_type"]==13):
                x["stat_modifier_codes"]=[3]
        mage_mask=self.tier["classes"]["mage"]["allowed_class_mask"]
        with self.assertRaisesRegex(stage.RepresentativeBlocked,
                                    "NO_COMPATIBLE_ONE_HAND_PRIMARY_WEAPON_PAIR"):
            stage.shape_weapons(broken,"one_hand_frill",mage_mask,
                                spec_key="mage/frost")
        broken=copy.deepcopy(self.db)
        for x in broken["items"]:
            if x["category"]=="plain_representative_candidate" and (
                x["class_id"]==4 and x["inventory_type"]==23):
                x["stat_modifier_codes"]=[3]
        with self.assertRaisesRegex(stage.RepresentativeBlocked,
                                    "NO_COMPATIBLE_PRIMARY_OFFHAND_FRILL"):
            stage.shape_weapons(broken,"one_hand_frill",mage_mask,
                                spec_key="mage/frost")
        # Code 73 is AGI/INT, so only an unknown code must fail closed.
        broken=copy.deepcopy(self.db)
        for x in broken["items"]:
            if x["category"]=="plain_representative_candidate" and (
                x["class_id"]==2 and x["inventory_type"]==13):
                x["stat_modifier_codes"]=[75]
        with self.assertRaises(stage.RepresentativeBlocked):
            stage.shape_weapons(broken,"one_hand_frill",mage_mask,
                                spec_key="mage/frost")

    def test_hybrid_primary_codes_preserve_valid_demonhunter_glaives(self):
        # ITEM_MOD_AGI_INT=73 is shared by AGI Havoc and INT Devourer.
        # Filtering only 3/4/5 would silently replace legitimate glaives.
        expected={"strength":frozenset((4,71,72,74)),
                  "agility":frozenset((3,71,72,73)),
                  "intellect":frozenset((5,71,73,74))}
        self.assertEqual(stage.PRIMARY_STAT_CODES,expected)
        plan=stage.build_all(self.db,self.tier)["specializations"]
        for key in ("demonhunter/havoc","demonhunter/devourer"):
            with self.subTest(spec=key):
                self.assertEqual(
                    plan[key]["weapons"],
                    {"main_hand":249677,"off_hand":251231})
        by_id={x["item_id"]:x for x in self.db["items"]}
        self.assertIn(73,by_id[249677]["stat_modifier_codes"])
        self.assertIn(73,by_id[251231]["stat_modifier_codes"])

    def test_profile_serializes_corrected_mage_primary_weapon(self):
        import v139_pure_target_profile_composer as pure
        preset=pure.catalog()
        ch={"class":"mage","spec":"frost",
            "race":"human","talents":"abc123456789"}
        trinkets=[{"slot":slot,"item_id":iid,"options":{}}
                  for slot,iid in zip(("trinket1","trinket2"),
                   [r["item_id"] for r in self.db["items"]
                    if r["category"]=="trinket"][:2])]
        result=stage.compose_stage(ch,trinkets,db=self.db,tier=self.tier,
                                   settings=preset)
        line=next(x for x in result["profile_text"].splitlines()
                  if x.startswith("main_hand="))
        self.assertIn("id=159137",line)
        self.assertNotIn("id=159136",line)
        self.assertEqual(result["profile_receipt"]["four_tier_item_ids"],
              {k:self.tier["classes"]["mage"]["pieces"][k]
               for k in stage.FOUR})

    def test_weapon_inventory_form_only_not_class_proficiency(self):
        plan=stage.build_all(self.db,self.tier)["specializations"]
        self.assertEqual(len(plan["warrior/fury"]["weapons"]),2)
        self.assertEqual(len(plan["hunter/marksmanship"]["weapons"]),1)
        self.assertEqual(len(plan["shaman/elemental"]["weapons"]),2)
        self.assertEqual(len(plan["mage/arcane"]["weapons"]),2)
        self.assertTrue(all(item["weapon_subclass_proficiency_native_unverified"]
                            for item in plan.values()))

if __name__=="__main__":unittest.main()
