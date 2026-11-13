"""Structural policy gate regression: do not promote sources into generic READY.

No SimC, Wago, Blizzard, WCL, Native or network access is required.
"""
from __future__ import annotations
import copy
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"integration_probes"))
import v401_completion_contract_gate as gate

class CompletionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=json.loads((ROOT/gate.REGISTRY).read_text(encoding="utf8"))
    def scenario(self):
        return copy.deepcopy(self.original)
    def row(self,doc,eid):
        return doc["elements"][gate.ALL_IDS.index(eid)]

    def test_exact_current_contract_and_generated_view(self):
        rows=gate.validate(self.scenario())
        self.assertEqual(len(rows),78)
        self.assertEqual([x["id"] for x in rows],list(gate.ALL_IDS))
        self.assertTrue(gate.check_tracker(self.scenario()))
        self.assertEqual(gate.render(self.scenario()),
                         (ROOT/gate.GENERATED).read_text(encoding="utf8"))
        self.assertEqual(gate.run(["--check"]),0)
        # A1~A10 are a proven source/generic prefix; avoid frozen totals.
        self.assertTrue(all(
            row["generic"]["state"]=="PASS" and
            row["current_source"]["state"]=="PASS"
            for row in rows[:10]))
        historical={x["id"] for x in rows
                    if x["historical"]["state"]=="PASS"}
        # New scope-backed history is additive, not a fixed count forever.
        self.assertTrue({"A8","A10","A11","G2"}.issubset(historical))
        self.assertTrue({"A8","A9","A10"}.issubset({
            x["id"] for x in rows if gate.complete(x)}))

    def test_a4_a6_generic_pass_is_scoped_and_product_unverified(self):
        data=self.scenario()
        for eid in ("A4","A5","A6"):
            row=self.row(data,eid)
            self.assertEqual(row["generic"]["state"],"PASS")
            self.assertEqual(row["current_source"]["state"],"PASS")
            self.assertEqual(row["product_integration"]["state"],"PENDING")
            self.assertFalse(gate.complete(row))
            self.assertEqual(gate.legacy_badge(row),
                             "ENGINE_GENERALIZATION_PASS")
            kinds={data["evidence"][key]["kind"]
                   for key in row["generic"]["evidence"]}
            self.assertIn("CURRENT_SOURCE_REAL",kinds)
            self.assertIn("GENERALIZATION_REGRESSION",kinds)
        self.assertNotIn(data["policy"]["next_review"],("A4","A5","A6","A7"))

    def test_a7_scoped_source_and_generic_complete_without_product_e2e(self):
        data=self.scenario()
        row=self.row(data,"A7")
        self.assertEqual(row["generic"]["state"],"PASS")
        self.assertEqual(row["current_source"]["state"],"PASS")
        self.assertEqual(row["product_integration"]["state"],"PENDING")
        self.assertFalse(gate.complete(row))
        self.assertEqual(gate.legacy_badge(row),"ENGINE_GENERALIZATION_PASS")
        self.assertNotIn(data["policy"]["next_review"],("A4","A5","A6","A7"))

    def test_cannot_advance_a8_until_a7_generic_and_current_proven(self):
        for axis in ("generic","current_source"):
            with self.subTest(axis=axis):
                data=self.scenario()
                self.row(data,"A7")[axis]={"state":"PENDING","evidence":[]}
                if axis=="current_source":
                    self.row(data,"A7")["generic"]={
                        "state":"PENDING","evidence":[]}
                with self.assertRaisesRegex(
                      gate.ContractInvalid,
                      "NEXT_REVIEW_SKIPPED_GENERIC_VALIDATION:A7"):
                    gate.validate(data)

    def test_a4_cannot_claim_generic_pass_from_current_only_source(self):
        doc=self.scenario()
        row=self.row(doc,"A4")
        row["generic"]={"state":"PASS","evidence":["a4_source"]}
        with self.assertRaisesRegex(gate.ContractInvalid,
                                    "PASS_MISSING_REQUIRED_EVIDENCE_KIND:A4:generic"):
            gate.validate(doc)

    def test_a4_cannot_claim_generic_pass_without_any_evidence(self):
        doc=self.scenario()
        self.row(doc,"A4")["generic"]={"state":"PASS","evidence":[]}
        with self.assertRaisesRegex(gate.ContractInvalid,
                                    "PASS_WITHOUT_EVIDENCE:A4:generic"):
            gate.validate(doc)

    def test_a7_may_not_be_next_when_a4_a6_generic_pending(self):
        doc=self.scenario()
        self.row(doc,"A4")["generic"]={"state":"PENDING","evidence":[]}
        doc["policy"]["next_review"]="A7"
        with self.assertRaisesRegex(gate.ContractInvalid,
                                    "NEXT_REVIEW_SKIPPED_GENERIC_VALIDATION:A4"):
            gate.validate(doc)

    def test_next_generic_unreviewed_element_must_be_selected(self):
        doc=self.scenario()
        self.row(doc,"A5")["generic"]={"state":"PENDING","evidence":[]}
        with self.assertRaisesRegex(gate.ContractInvalid,
                                    "NEXT_REVIEW_SKIPPED_GENERIC_VALIDATION:A5"):
            gate.validate(doc)

    def test_unrelated_evidence_cannot_be_borrowed_to_promote_a4(self):
        doc=self.scenario()
        self.row(doc,"A4")["generic"]={
            "state":"PASS","evidence":["a1_source","a1_generic"]}
        with self.assertRaisesRegex(gate.ContractInvalid,
                                    "EVIDENCE_NOT_SCOPED_TO_ELEMENT:A4:generic"):
            gate.validate(doc)

    def test_a7_cannot_be_marked_current_ready_while_a4_unreviewed(self):
        doc=self.scenario()
        self.row(doc,"A4")["generic"]={"state":"PENDING","evidence":[]}
        doc["policy"]["next_review"]="A4"
        self.row(doc,"A7")["current_source"]={
            "state":"PASS","evidence":["a1_source"]}
        # Even if the external ref has been incorrectly attached to A7,
        # completion must not leapfrog the A4-A6 generic review.
        doc["evidence"]["a1_source"]["supports"].append("A7")
        with self.assertRaisesRegex(gate.ContractInvalid,
                "A7_PREMATURE_VERIFIED_CLAIM_BEFORE_A4_A6_GENERIC"):
            gate.validate(doc)

    def test_a8_scoped_three_axes_are_complete_but_final_e2e_is_pending(self):
        doc=self.scenario()
        row=self.row(doc,"A8")
        self.assertTrue(gate.complete(row))
        self.assertNotEqual(doc["policy"]["next_review"],"A8")
        self.assertEqual(doc["policy"]["full_product_e2e"],"PENDING")
        self.assertEqual({doc["evidence"][key]["kind"]
            for key in row["generic"]["evidence"]},
            {"CURRENT_SOURCE_REAL","GENERALIZATION_REGRESSION"})

    def test_a9_cannot_skip_a8_generic_or_current_source(self):
        for axis in ("generic","current_source"):
            with self.subTest(axis=axis):
                doc=self.scenario()
                self.row(doc,"A8")["generic"]={"state":"PENDING","evidence":[]}
                if axis=="current_source":
                    self.row(doc,"A8")["current_source"]={
                        "state":"PENDING","evidence":[]}
                self.row(doc,"A8")["product_integration"]={
                    "state":"PENDING","evidence":[]}
                with self.assertRaisesRegex(gate.ContractInvalid,
                    "NEXT_REVIEW_SKIPPED_GENERIC_VALIDATION:A8"):
                    gate.validate(doc)

    def test_a10_compiler_completion_has_independent_proofs(self):
        doc=self.scenario()
        row=self.row(doc,"A10")
        self.assertTrue(gate.complete(row))
        self.assertEqual({doc["evidence"][k]["kind"]
            for k in row["generic"]["evidence"]},
            {"CURRENT_SOURCE_REAL","GENERALIZATION_REGRESSION"})
        self.assertEqual({doc["evidence"][k]["kind"]
            for k in row["product_integration"]["evidence"]},
            {"PRODUCT_INTEGRATION_REAL"})
        self.assertEqual(doc["policy"]["full_product_e2e"],"PENDING")

    def test_a11_receipt_proofs_preserve_history_and_separate_axes(self):
        doc=self.scenario()
        row=self.row(doc,"A11")
        self.assertTrue(gate.complete(row))
        self.assertEqual({doc["evidence"][key]["kind"]
            for key in row["generic"]["evidence"]},
            {"CURRENT_SOURCE_REAL","GENERALIZATION_REGRESSION"})
        self.assertEqual({doc["evidence"][key]["kind"]
            for key in row["product_integration"]["evidence"]},
            {"PRODUCT_INTEGRATION_REAL"})
        self.assertEqual(row["historical"]["state"],"PASS")
        self.assertEqual(doc["policy"]["full_product_e2e"],"PENDING")

    def test_b1_source_and_generic_scope_do_not_promote_26_product_e2e(self):
        doc=self.scenario()
        row=self.row(doc,"B1")
        self.assertEqual(row["generic"]["state"],"PASS")
        self.assertEqual(row["current_source"]["state"],"PASS")
        self.assertEqual(row["historical"]["state"],"PASS")
        self.assertEqual(row["product_integration"]["state"],"PENDING")
        self.assertFalse(gate.complete(row))
        self.assertNotEqual(doc["policy"]["next_review"],"B1")
        self.assertEqual(doc["policy"]["full_product_e2e"],"PENDING")

    def test_b2_ilvl_scoped_full_axes_and_legacy_non334_receipt(self):
        doc=self.scenario()
        row=self.row(doc,"B2")
        self.assertTrue(gate.complete(row))
        self.assertEqual({doc["evidence"][key]["kind"]
            for key in row["generic"]["evidence"]},
            {"CURRENT_SOURCE_REAL","GENERALIZATION_REGRESSION"})
        self.assertEqual({doc["evidence"][key]["kind"]
            for key in row["product_integration"]["evidence"]},
            {"PRODUCT_INTEGRATION_REAL"})
        self.assertEqual(row["historical"]["state"],"PASS")
        self.assertFalse(gate.complete(self.row(doc,"B1")))
        self.assertEqual(doc["policy"]["full_product_e2e"],"PENDING")
        self.assertNotEqual(doc["policy"]["next_review"],"B2")

    def test_b3_ordinary_equipment_has_scoped_real_json2_and_regression_proof(self):
        doc=self.scenario()
        row=self.row(doc,"B3")
        self.assertTrue(gate.complete(row))
        self.assertEqual({doc["evidence"][key]["kind"]
            for key in row["generic"]["evidence"]},
            {"CURRENT_SOURCE_REAL","GENERALIZATION_REGRESSION"})
        self.assertEqual({doc["evidence"][key]["kind"]
            for key in row["product_integration"]["evidence"]},
            {"PRODUCT_INTEGRATION_REAL"})
        self.assertEqual(row["historical"]["state"],"PASS")
        self.assertFalse(gate.complete(self.row(doc,"B1")))
        self.assertEqual(doc["policy"]["full_product_e2e"],"PENDING")
        self.assertNotEqual(doc["policy"]["next_review"],"B3")

    def test_a10_cannot_skip_a9_generic_source(self):
        doc=self.scenario()
        self.row(doc,"A9")["generic"]={"state":"PENDING","evidence":[]}
        self.row(doc,"A9")["product_integration"]={"state":"PENDING","evidence":[]}
        with self.assertRaisesRegex(gate.ContractInvalid,
             "NEXT_REVIEW_SKIPPED_GENERIC_VALIDATION:A9"):
            gate.validate(doc)

    def test_historical_receipt_cannot_replace_current_or_generic_proof(self):
        doc=self.scenario()
        self.row(doc,"A10")["current_source"]={
            "state":"PASS","evidence":["legacy_v344"]}
        with self.assertRaisesRegex(gate.ContractInvalid,
                                    "PASS_MISSING_REQUIRED_EVIDENCE_KIND:A10:current_source"):
            gate.validate(doc)

    def test_a8_history_cannot_prove_current_source_or_generic(self):
        data=self.scenario()
        key="a8_historical_v342_v344"
        row=self.row(data,"A8")
        self.assertEqual(row["historical"]["state"],"PASS")
        self.assertEqual(data["evidence"][key]["supports"],["A8"])
        row["current_source"]={"state":"PASS","evidence":[key]}
        with self.assertRaisesRegex(gate.ContractInvalid,
                 "PASS_MISSING_REQUIRED_EVIDENCE_KIND:A8:current_source"):
            gate.validate(data)

    def test_not_applicable_requires_specific_policy_evidence(self):
        doc=self.scenario()
        self.row(doc,"B1")["generic"]={"state":"NOT_APPLICABLE",
                                         "evidence":[],"reason":"not needed"}
        with self.assertRaisesRegex(gate.ContractInvalid,
                                    "NA_REQUIRES_CONCRETE_REASON:B1:generic"):
            gate.validate(doc)

    def test_product_and_final_e2e_cannot_be_marked_without_proof(self):
        doc=self.scenario()
        self.row(doc,"A4")["product_integration"]={
            "state":"PASS","evidence":["a4_source"]}
        with self.assertRaisesRegex(gate.ContractInvalid,
                                    "PASS_MISSING_REQUIRED_EVIDENCE_KIND:A4:product_integration"):
            gate.validate(doc)
        doc=self.scenario()
        doc["policy"]["full_product_e2e"]="PASS"
        with self.assertRaisesRegex(gate.ContractInvalid,
                                    "FINAL_E2E_CANNOT_PASS_WHILE_ELEMENTS_INCOMPLETE"):
            gate.validate(doc)

    def test_tracker_drift_cannot_silently_change_scope(self):
        data=self.scenario()
        original=(ROOT/gate.TRACKER).read_text(encoding="utf8")
        changed=original.replace(
            "| **A4 Blizzard 원본** | BASE |",
            "| **A4 Blizzard 원본** | USER |",1)
        self.assertNotEqual(original,changed)
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp)
            target=root/gate.TRACKER
            target.parent.mkdir(parents=True)
            target.write_text(changed,encoding="utf8")
            with self.assertRaisesRegex(gate.ContractInvalid,
                                        "TRACKER_IDENTITIES_OR_ACCEPTANCE_DRIFT:A4"):
                gate.check_tracker(data,root)
            changed=original.replace(
                "ENGINE_GENERALIZATION_PASS — CURRENT_KR_70783_BLIZZARD_INDEX_SOURCE_SCOPE",
                "READY_SCOPED — CURRENT_KR_70783_BLIZZARD_INDEX_BASE_ONLY",1)
            target.write_text(changed,encoding="utf8")
            with self.assertRaisesRegex(gate.ContractInvalid,
                                        "TRACKER_STATUS_CONTRADICTS_CONTRACT:A4"):
                gate.check_tracker(data,root)

    def test_document_is_not_allowed_to_drift_from_json(self):
        with tempfile.TemporaryDirectory() as temp:
            fake=pathlib.Path(temp)/"generated.md"
            fake.write_text("STALE STATUS",encoding="utf8")
            with mock.patch.object(gate,"GENERATED",fake):
                with self.assertRaisesRegex(gate.ContractInvalid,
                                            "GENERATED_STATUS_DOCUMENT_STALE"):
                    gate.run(["--check"])

    def test_exact_element_set_and_evidence_note_must_exist(self):
        doc=self.scenario()
        del doc["elements"][-1]
        with self.assertRaisesRegex(gate.ContractInvalid,
                                    "EXACTLY_78_CONTRACTS_REQUIRED"):
            gate.validate(doc)
        doc=self.scenario()
        doc["evidence"]["a1_source"]["note"] = (
            "docs/development/notes/does-not-exist.md")
        with self.assertRaisesRegex(gate.ContractInvalid,
                                    "EVIDENCE_NOTE_NOT_FOUND:a1_source"):
            gate.validate(doc)

if __name__=="__main__":
    unittest.main()
