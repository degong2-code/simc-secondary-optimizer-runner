"""v220 generic auto-admission policy: exact evidence only; no Native."""
import copy
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v220_catalog_auto_admission as policy
import v196_current_season_user_catalog as catalog


class AutoAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.item={"kind":"permanent_enchant","exact_id":8019,
                   "simc_token":"enchant_boots__farstriders_hunt",
                   "slot":"feet","slot_status":"SOURCE_MASK_RESOLVED",
                   "game_build":"12.1.5.70575",
                   "simc_revision":"a"*40,"catalog_sha256":"b"*64}
        identity=policy._identity(self.item)
        self.receipts={
            family:{"identity":dict(identity),"status":status,
                    "evidence_sha256":str(index)*64}
            for index,(family,status) in enumerate(policy.PROOF_STATUSES.items(),1)
        }
        self.receipts["chmv_budget"]["no_double_count"]=True
        self.receipts["chmv_budget"]["unknown_static_chmv"]=False

    def test_missing_proofs_pending_no_manual_approval_or_ui_mutation(self):
        out=policy.decide(self.item)
        self.assertFalse(out["eligible"])
        self.assertEqual(out["status"],"PENDING_EXACT_EVIDENCE")
        self.assertEqual(len(out["missing"]),4)
        self.assertFalse(out["requires_separate_manual_approval"])
        self.assertFalse(out["ui_selection_mutated"])
        self.assertEqual(out["native_calls"],0)

    def test_all_matching_internal_proofs_make_item_eligible(self):
        out=policy.decide(self.item,self.receipts)
        self.assertTrue(out["eligible"])
        self.assertEqual(out["status"],"ELIGIBLE_FOR_ATOMIC_PUBLICATION")
        self.assertEqual(out["missing"],[])
        self.assertEqual(out["conflicts"],[])
        self.assertEqual(out["effect_proc_dps_owner"],"SimC")

    def test_exact_revision_slot_and_source_identity_drift_rejects(self):
        for key,value in (("slot","hands"),
                          ("simc_revision","c"*40),
                          ("catalog_sha256","d"*64),
                          ("exact_id",8020)):
            changed={**self.item,key:value}
            with self.subTest(key=key):
                out=policy.decide(changed,self.receipts)
                self.assertFalse(out["eligible"])
                self.assertTrue(any("EVIDENCE_SCOPE_MISMATCH:" in x
                                    for x in out["conflicts"]))

    def test_no_weapon_hand_inference_even_with_four_receipts(self):
        out=policy.decide({**self.item,
                           "slot_status":"PENDING_EXACT_HAND"},self.receipts)
        self.assertFalse(out["eligible"])
        self.assertIn("EXACT_PHYSICAL_SLOT_OR_HAND_RELATION_NOT_VERIFIED",
                      out["missing"])

    def test_unknown_static_and_double_count_are_not_eligible(self):
        for key,value in (("no_double_count",False),
                          ("unknown_static_chmv",True)):
            receipts=copy.deepcopy(self.receipts)
            receipts["chmv_budget"][key]=value
            with self.subTest(key=key):
                self.assertFalse(policy.decide(self.item,receipts)["eligible"])

    def test_malformed_proof_or_effect_ownership_violation_blocks(self):
        receipts=copy.deepcopy(self.receipts)
        receipts["source_relation"]["evidence_sha256"]="invalid"
        self.assertEqual(policy.decide(self.item,receipts)["status"],
                         "BLOCKED_EVIDENCE_CONFLICT")
        receipts=copy.deepcopy(self.receipts)
        receipts["simc_input"]["effect_mechanism_reimplemented"]=True
        out=policy.decide(self.item,receipts)
        self.assertIn("SIMC_EFFECT_OWNERSHIP_VIOLATION",out["conflicts"])

    def test_temporary_enchant_not_user_auto_admitted_even_with_receipts(self):
        """Oil is its own fixed-O product input; not a generic enchant choice."""
        temporary={**self.item,"kind":"temporary_enchant",
                   "simc_token":"temporary_oil_example"}
        with self.assertRaisesRegex(ValueError,
                                    "AUTO_ADMISSION_CANDIDATE_IDENTITY_INVALID"):
            policy.decide(temporary,self.receipts)

    def test_generic_not_hardcoded_to_7967_or_enchant(self):
        gem={**self.item,"kind":"gem","exact_id":244444,
             "simc_token":"gem_foo","slot":"socket1"}
        identity=policy._identity(gem)
        receipts=copy.deepcopy(self.receipts)
        for proof in receipts.values():
            proof["identity"]=identity
        self.assertTrue(policy.decide(gem,receipts)["eligible"])

    def test_slotless_consumables_use_existing_four_exact_proofs(self):
        """Synthetic receipts exercise the generic policy, NOT real item admission."""
        for item_id,token in ((311001,"food_example"),
                              (311002,"potion_example"),
                              (311003,"augmentation_example")):
            candidate={**self.item,"kind":"consumable","exact_id":item_id,
                       "simc_token":token,"slot":"NO_EQUIPMENT_SLOT",
                       "slot_status":"CONSUMABLE_USE_SCOPE_NOT_EQUIPMENT"}
            identity=policy._identity(candidate)
            receipts=copy.deepcopy(self.receipts)
            for proof in receipts.values():
                proof["identity"]=dict(identity)
            with self.subTest(token=token):
                approved=policy.decide(candidate,receipts)
                self.assertTrue(approved["eligible"])
                self.assertEqual(approved["missing"],[])
                self.assertFalse(approved["ui_selection_mutated"])
                self.assertEqual(approved["native_calls"],0)
                # A slotless item still requires the original exact item/use
                # and CHMV ownership proofs. There is no extra effect Gate.
                lacking=copy.deepcopy(receipts)
                lacking.pop("product_input")
                blocked=policy.decide(candidate,lacking)
                self.assertFalse(blocked["eligible"])
                self.assertIn("EVIDENCE_MISSING:product_input",blocked["missing"])
                unknown=copy.deepcopy(receipts)
                unknown["chmv_budget"]["unknown_static_chmv"]=True
                self.assertIn("CHMV_BUDGET_OWNERSHIP_NOT_SETTLED",
                              policy.decide(candidate,unknown)["missing"])
                changed={**candidate,"exact_id":item_id+100}
                self.assertIn("EVIDENCE_SCOPE_MISMATCH:source_relation",
                              policy.decide(changed,receipts)["conflicts"])

    def test_consumable_cannot_forge_equipment_slot_scope(self):
        """Even matching receipts cannot turn a non-equipped item into gear."""
        candidate={**self.item,"kind":"consumable","exact_id":311001,
                   "simc_token":"food_example","slot":"NO_EQUIPMENT_SLOT",
                   "slot_status":"CONSUMABLE_USE_SCOPE_NOT_EQUIPMENT"}
        identity=policy._identity(candidate)
        receipts=copy.deepcopy(self.receipts)
        for proof in receipts.values():
            proof["identity"]=dict(identity)
        for slot,status in (
                ("NO_EQUIPMENT_SLOT","SOURCE_MASK_RESOLVED"),
                ("main_hand","SOURCE_MASK_RESOLVED"),
                ("NO_EQUIPMENT_SLOT","PENDING_USE_CONDITIONS")):
            with self.subTest(slot=slot,status=status):
                forged={**candidate,"slot":slot,"slot_status":status}
                result=policy.decide(forged,receipts)
                self.assertFalse(result["eligible"])
                self.assertIn("CONSUMABLE_NO_EQUIPMENT_SLOT_SCOPE_INVALID",
                              result["missing"])
        # No source, SimC token or game-use condition may be inferred from
        # a candidate with the correct syntactic slot marker alone.
        result=policy.decide(candidate)
        self.assertFalse(result["eligible"])
        self.assertEqual(len(result["missing"]),4)

    def test_same_build_gem_property_uses_original_v220_source_family_only(self):
        src={"game_build":"12.1.5.70575",
             "simc_revision":"a"*40,
             "manifest_sha256":"b"*64}
        prop={"item_id":311001,"gem_property_id":11001,
              "enchant_id":9801,"color_mask":2,
              "minimum_ilevel":300,"expansion_id":12}
        gem=policy.candidate_from_source_gem(src,prop)
        self.assertEqual(gem["exact_id"],311001)
        self.assertEqual(gem["simc_token"],"gem_id=311001")
        self.assertEqual(gem["kind"],"gem")
        self.assertEqual(gem["slot"],"ANY_EXISTING_SOCKET")
        self.assertEqual(gem["slot_status"],
                         "GEM_SOCKET_TYPE_NOT_APPLICABLE")
        ident=policy._identity(gem)
        proof={"source_relation":{"identity":ident,
                "status":"EXACT_SOURCE_RELATION_VERIFIED",
                "evidence_sha256":"c"*64}}
        decision=policy.decide(gem,proof)
        self.assertFalse(decision["eligible"])
        self.assertNotIn("EVIDENCE_MISSING:source_relation",
                         decision["missing"])
        for field in ("simc_input","product_input","chmv_budget"):
            self.assertIn("EVIDENCE_MISSING:"+field,decision["missing"])
        self.assertNotIn("EXACT_PHYSICAL_SLOT_OR_HAND_RELATION_NOT_VERIFIED",
                         decision["missing"])
        # Source-only is still NOT an accepted gem. All three remaining
        # original proof families must be real and internally scoped.
        self.assertEqual(decision["status"],"PENDING_EXACT_EVIDENCE")
        receipts={family:{"identity":dict(ident),"status":status,
                          "evidence_sha256":str(i)*64}
                  for i,(family,status) in enumerate(
                      policy.PROOF_STATUSES.items(),1)}
        receipts["chmv_budget"].update(
            no_double_count=True,unknown_static_chmv=False)
        self.assertTrue(policy.decide(gem,receipts)["eligible"])
        # Changing only the DB2 source color is not socket rejection.
        other_color=policy.candidate_from_source_gem(
            src,{**prop,"color_mask":1})
        self.assertEqual(other_color["slot"],"ANY_EXISTING_SOCKET")
        self.assertEqual(other_color["slot_status"],
                         "GEM_SOCKET_TYPE_NOT_APPLICABLE")
        self.assertFalse(policy.decide(other_color)["eligible"])
        forged={**gem,"slot_status":"PENDING_GAME_SOCKET_APPLICABILITY"}
        self.assertIn("EXACT_PHYSICAL_SLOT_OR_HAND_RELATION_NOT_VERIFIED",
                      policy.decide(forged)["missing"])
        for bad in ({**prop,"gem_property_id":0},
                    {**prop,"item_id":-1}):
            with self.assertRaisesRegex(ValueError,
                                        "GEM_PROPERTY_FIELDS_INVALID"):
                policy.candidate_from_source_gem(src,bad)

    def test_preview_source_catalog_never_auto_promotes_without_proofs(self):
        src={"game_build":"12.1.5.70575","simc_revision":"a"*40,
             "manifest_sha256":"b"*64}
        result=policy.preview_enchant_catalog(src,[{
            "enchant_id":8019,"token":self.item["simc_token"],
            "source_slots":["feet"]}])
        self.assertEqual(result["automatically_eligible"],0)
        self.assertEqual(result["pending"],1)
        self.assertFalse(result["selection_mutated"])
        self.assertIn("8019",result["per_item_missing_reasons"])

    def test_multi_slot_and_grouped_ring_preview_only_pending(self):
        src={"game_build":"12.1.5.70575","simc_revision":"a"*40,
             "manifest_sha256":"b"*64}
        rows=[
            {"enchant_id":8019,"token":"enchant_boots__farstriders_hunt",
             "source_slots":["feet","hands"]},
            {"enchant_id":8018,"token":"enchant_ring__example",
             "source_slots":["finger1/finger2"]},
            {"enchant_id":8017,"token":"enchant_weapon__example",
             "source_slots":["WEAPON_SUBCLASS_NOT_YET_USER_SLOT_CERTIFIED"]},
        ]
        out=policy.preview_enchant_catalog(src,rows)
        self.assertEqual(out["pending"],3)
        self.assertEqual(out["automatically_eligible"],0)
        self.assertFalse(out["selection_mutated"])
        for id_ in (8019,8018,8017):
            self.assertIn(
                "EXACT_PHYSICAL_SLOT_OR_HAND_RELATION_NOT_VERIFIED",
                out["per_item_missing_reasons"][str(id_)])
        # A missing/ill-formed source-slot structure is NOT a valid
        # candidate silently promoted through diagnostics.
        with self.assertRaisesRegex(ValueError,
                "AUTO_ADMISSION_SLOT_SCOPE_INVALID"):
            policy.preview_enchant_catalog(src,[
                {"enchant_id":8016,"token":"enchant_ring__bad",
                 "source_slots":[None]}])

    def test_trusted_internal_receipts_project_eligible_not_published(self):
        source={"game_build":"12.1.5.70575","simc_revision":"a"*40,
                "manifest_sha256":"b"*64}
        rows=[{"enchant_id":8019,"token":self.item["simc_token"],
               "source_slots":["feet"]},
              {"enchant_id":8018,"token":"enchant_boots__other",
               "source_slots":["feet"]}]
        projected=policy.preview_enchant_catalog(
            source,rows,trusted_internal_receipts_by_id={
                8019:copy.deepcopy(self.receipts)})
        self.assertEqual(projected["status"],
            "PREVIEW_ONLY_ELIGIBLE_NEEDS_ATOMIC_PUBLICATION")
        self.assertEqual(projected["automatically_eligible"],1)
        self.assertEqual(projected["pending"],1)
        self.assertEqual([r["exact_id"] for r in projected[
            "eligible_for_atomic_publication"]],[8019])
        self.assertEqual(len(projected["per_item_missing_reasons"]["8018"]),4)
        self.assertFalse(projected["selection_mutated"])
        self.assertFalse(projected.get("approved_count",0))
        # The same receipts on another revision or source SHA do not match.
        another={**source,"simc_revision":"c"*40}
        shifted=policy.preview_enchant_catalog(
            another,rows,trusted_internal_receipts_by_id={
                8019:copy.deepcopy(self.receipts)})
        self.assertEqual(shifted["automatically_eligible"],0)
        self.assertIn("EVIDENCE_SCOPE_MISMATCH:source_relation",
                      shifted["per_item_conflict_reasons"]["8019"])
        self.assertEqual(shifted["pending"],2)
        with self.assertRaisesRegex(ValueError,
                    "AUTO_ADMISSION_RECEIPT_FOR_NONCANDIDATE"):
            policy.preview_enchant_catalog(
                source,rows,trusted_internal_receipts_by_id={
                    999999:copy.deepcopy(self.receipts)})
        with self.assertRaisesRegex(ValueError,
                    "AUTO_ADMISSION_INTERNAL_RECEIPT_MAP_INVALID"):
            policy.preview_enchant_catalog(
                source,rows,trusted_internal_receipts_by_id={
                    "8019":copy.deepcopy(self.receipts)})

    def test_invalid_scope_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"CANDIDATE_IDENTITY_INVALID"):
            policy.decide({**self.item,"simc_revision":"wrong"})
        with self.assertRaisesRegex(ValueError,"UNKNOWN_PROOF_FAMILY"):
            policy.decide(self.item,{"made_up":{}})


    def test_real_selected_armor_and_subclass_masks_are_source_only(self):
        source={"item_class":4,"inventory_type_mask":1<<7,
                "item_subclass_mask":0x1e}
        legs={"item_id":248161,"class_id":4,"subclass_id":4,"inventory_type":7}
        result=policy.selected_equipment_source_mask_match(
            permanent_source=source,item_metadata=legs,selected_slot="legs")
        self.assertTrue(result["matched"],result)
        self.assertFalse(result["policy_A_product_input_verified"])
        self.assertFalse(result["ui_selectable"])
        self.assertEqual(result["native_calls"],0)
        self.assertTrue(result["fixed_E_or_no_E_not_attested"])
        self.assertFalse(policy.selected_equipment_source_mask_match(
            permanent_source=source,item_metadata=legs,
            selected_slot="head")["matched"])
        wrong={**legs,"subclass_id":0}
        self.assertIn("SOURCE_SUBCLASS_MASK_NOT_MATCHED",
            policy.selected_equipment_source_mask_match(
                permanent_source=source,item_metadata=wrong,
                selected_slot="legs")["missing_or_conflicting_conditions"])

    def test_ranged_source_weapons_match_bow_gun_crossbow_only_main_hand(self):
        source={"item_class":2,"inventory_type_mask":0,
                "item_subclass_mask":0x4000c}
        for subclass in (2,3,18):
            equipped={"item_id":268207+subclass,"class_id":2,
                      "subclass_id":subclass,"inventory_type":26}
            with self.subTest(subclass=subclass):
                self.assertTrue(policy.selected_equipment_source_mask_match(
                    permanent_source=source,item_metadata=equipped,
                    selected_slot="main_hand")["matched"])
                self.assertFalse(policy.selected_equipment_source_mask_match(
                    permanent_source=source,item_metadata=equipped,
                    selected_slot="off_hand")["matched"])
        wrong={"item_id":268207,"class_id":2,"subclass_id":0,
               "inventory_type":13}
        result=policy.selected_equipment_source_mask_match(
            permanent_source=source,item_metadata=wrong,
            selected_slot="main_hand")
        self.assertIn("SOURCE_SUBCLASS_MASK_NOT_MATCHED",
                      result["missing_or_conflicting_conditions"])

    def test_exact_ring_slot_is_a_source_relation_not_both_slots_approval(self):
        source={"item_class":4,"inventory_type_mask":1<<11,
                "item_subclass_mask":0}
        ring={"item_id":268266,"class_id":4,"subclass_id":0,
              "inventory_type":11}
        first=policy.selected_equipment_source_mask_match(
            permanent_source=source,item_metadata=ring,
            selected_slot="finger1")
        self.assertEqual(first["selected_slot"],"finger1")
        self.assertTrue(first["matched"])
        self.assertFalse(first["policy_A_product_input_verified"])
        other=policy.selected_equipment_source_mask_match(
            permanent_source=source,item_metadata={**ring,"item_id":268267},
            selected_slot="finger2")
        self.assertNotEqual(first["selected_item_id"],other["selected_item_id"])

    def test_unknown_equipment_metadata_never_approves_a_mask(self):
        source={"item_class":2,"inventory_type_mask":0,
                "item_subclass_mask":0x4000c}
        with self.assertRaisesRegex(ValueError,
                                    "PERMANENT_SELECTED_ITEM_EXACT_METADATA_INVALID"):
            policy.selected_equipment_source_mask_match(
                permanent_source=source,item_metadata={
                    "item_id":268207,"class_id":2,"inventory_type":26},
                selected_slot="main_hand")
        with self.assertRaisesRegex(ValueError,
                                    "PERMANENT_SELECTED_ITEM_SOURCE_FIELDS_INVALID"):
            policy.selected_equipment_source_mask_match(
                permanent_source=source,item_metadata={},
                selected_slot="bogus_hand")


class SealedRepresentativeConsumerTests(unittest.TestCase):
    """v216 source ownership can reach v196/v220 without user enrollment."""

    def setUp(self):
        self.source={
            "game_build":"12.1.5.70783",
            "simc_revision":"d"*40,"manifest_sha256":"a"*64,
            "v196_enchant_source":{"rows":[{
                "enchant_id":8025,"item_class":4,
                "inventory_type_mask":1<<11,"item_subclass_mask":0}]}}
        self.scope={
            "game_build":"12.1.5.70783","simc_revision":"d"*40,
            "enchant_id":8025,"selected_slot":"finger1",
            "item_metadata":{"item_id":268266,"class_id":4,
                             "subclass_id":0,"inventory_type":11},
            "wago_item_id":244444,
            "v232_receipt_sha256":"b"*64,
            "v583_receipt_sha256":"c"*64,
            "v230_item_data_sha256":"e"*64}

    def test_consumer_reads_one_exact_item_but_never_approves_it(self):
        with mock.patch.object(catalog.source_bridge,"verify_catalog"):
            out=catalog.preview_sealed_representative_enchant_mask(
                source_catalog=self.source,scope=self.scope)
        self.assertEqual(out["selected_representative_item_id"],268266)
        self.assertEqual(out["enchant_id"],8025)
        self.assertEqual(out["selected_slot"],"finger1")
        self.assertTrue(out["matched"])
        self.assertTrue(out["reference_representative_not_user_equipment"])
        self.assertFalse(out["ui_selectable"])
        self.assertFalse(out["policy_A_product_input_verified"])
        self.assertFalse(out["same_effect_and_highest_quality_verified"])
        self.assertFalse(out["fixed_E_or_no_E_verified"])
        self.assertEqual((out["network_calls"],out["native_calls"]),(0,0))

    def test_sealed_supplemental_gear_family_stays_source_only(self):
        # New source family is absent from old v213 enchant_ catalog.
        supplemental={
            "enchant_id":7939,"simc_token":"bright_linen_spellthread",
            "quality_rank_simc":2,
            "source_class_and_masks":{
                "item_class":4,"inventory_type_mask":1<<7,
                "item_subclass_mask":0x1e},
            "physical_item_ids":[240133],
            "source_slot":{"status":"SOURCE_MASK_RESOLVED"},
            "selection_status":"SUPPLEMENTAL_SOURCE_ONLY_NOT_USER_PUBLISHED",
            "ui_selectable":False,
            "static_E_source_status":"NO_STATIC_CHMV_COMPONENT_IN_SIMC_DBC",
            "raw_rank_component_evidence":{
                "same_effect_and_use_conditions_verified":False,
                "quality_noninferiority_runtime_verified":False}}
        scope={**self.scope,"enchant_id":7939,"wago_item_id":240133,
               "selected_slot":"legs",
               "item_metadata":{"item_id":268268,"class_id":4,
                                "subclass_id":4,"inventory_type":7}}
        with mock.patch.object(catalog.source_bridge,"verify_catalog"):
            out=catalog.preview_sealed_representative_enchant_mask(
                source_catalog=self.source,scope=scope,
                supplemental_source=supplemental)
            self.assertTrue(out["matched"])
            self.assertTrue(out["supplemental_v583_v584_source_only"])
            self.assertEqual(out["source_observed_static_E_status"],
                             "NO_STATIC_CHMV_COMPONENT_IN_SIMC_DBC")
            self.assertFalse(out["fixed_E_or_no_E_verified"])
            self.assertFalse(out["same_effect_and_highest_quality_verified"])
            self.assertFalse(out["ui_selectable"])
            with self.assertRaisesRegex(
                    catalog.CatalogBlocked,"EXACT_SOURCE_CATALOG"):
                catalog.preview_sealed_representative_enchant_mask(
                    source_catalog=self.source,scope=scope)
            with self.assertRaisesRegex(
                    catalog.CatalogBlocked,"SUPPLEMENTAL_SEALED"):
                catalog.preview_sealed_representative_enchant_mask(
                    source_catalog=self.source,
                    scope={**scope,"wago_item_id":999999},
                    supplemental_source=supplemental)
            # A physical applicability check must not independently
            # certify or block SimC spell effects or quality dominance.
            # Even inconsistent optional effect observations cannot grant
            # UI/Policy A/E status; product-quality dedup owns that later.
            untrusted_quality=catalog.preview_sealed_representative_enchant_mask(
                source_catalog=self.source,scope=scope,
                supplemental_source={**supplemental,
                    "raw_rank_component_evidence":{
                      "same_effect_and_use_conditions_verified":True,
                      "quality_noninferiority_runtime_verified":True}})
            self.assertTrue(untrusted_quality["matched"])
            self.assertFalse(untrusted_quality["same_effect_and_highest_quality_verified"])
            self.assertFalse(untrusted_quality["policy_A_product_input_verified"])
            self.assertFalse(untrusted_quality["ui_selectable"])


    def test_wrong_equipment_or_build_cannot_become_a_choice(self):
        with mock.patch.object(catalog.source_bridge,"verify_catalog"):
            wrong=catalog.preview_sealed_representative_enchant_mask(
                source_catalog=self.source,
                scope={**self.scope,"selected_slot":"feet"})
            self.assertFalse(wrong["matched"])
            self.assertFalse(wrong["ui_selectable"])
            with self.assertRaisesRegex(
                    catalog.CatalogBlocked,"ORIGINAL_SOURCE_SCOPE_REQUIRED"):
                catalog.preview_sealed_representative_enchant_mask(
                    source_catalog=self.source,
                    scope={**self.scope,"game_build":"12.1.5.99999"})
            with self.assertRaisesRegex(
                    catalog.CatalogBlocked,"EXACT_SOURCE_CATALOG"):
                catalog.preview_sealed_representative_enchant_mask(
                    source_catalog=self.source,
                    scope={**self.scope,"enchant_id":999999})


if __name__=="__main__":
    unittest.main()
