"""v220 generic auto-admission policy: exact evidence only; no Native."""
import copy
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v220_catalog_auto_admission as policy


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

    def test_invalid_scope_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"CANDIDATE_IDENTITY_INVALID"):
            policy.decide({**self.item,"simc_revision":"wrong"})
        with self.assertRaisesRegex(ValueError,"UNKNOWN_PROOF_FAMILY"):
            policy.decide(self.item,{"made_up":{}})


if __name__=="__main__":
    unittest.main()
