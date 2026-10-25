"""v076 offline source-boundary and coverage checks; no Native inference."""
import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v076_generic_dps_scope_audit as audit

class V076GenericEngineAudit(unittest.TestCase):
    def test_six_factor_cover_without_unverified_native_claim(self):
        r=audit.audit()
        self.assertEqual(r["matrix_cover"]["cases"],6)
        self.assertEqual(len(r["matrix_cover"]["armors"]),4)
        self.assertEqual(len(r["matrix_cover"]["weapon_forms"]),6)
        self.assertEqual(len(r["matrix_cover"]["primary_stats"]),3)
        self.assertEqual(r["matrix_cover"]["unique_races"],6)
        self.assertEqual(r["new_native_calls"],0)
        self.assertEqual(r["matrix_cover"]["new_profile_native_tests_completed"],0)
        self.assertTrue(all(not x["race_class_pair_native_verified_in_this_stage"]
                            for x in r["matrix"]))

    def test_gaps_are_explicit_and_no_role_promotion(self):
        r=audit.audit()
        ids={x["id"] for x in r["open_gaps"]}
        for required in ("NUMERIC_CALIBRATION_BOOTSTRAP_REQUIRES_TWO_REAL_WITNESSES",
                         "EXACT_ITEM_VARIANTS_REQUIRED_PER_PROFILE",
                         "GENERIC_PROFILE_PRODUCER_NOT_IN_V067",
                         "WEAPON_FORM_NOT_EXPLICIT_IN_V061_OR_V062",
                         "DPS_ONLY_USER_REQUEST_CONFLICTS_WITH_APPROVED_ROLE_SCOPE"):
            self.assertIn(required,ids)
        self.assertEqual(r["test_scope"],
              "DPS representative scenarios only; existing approved role set unchanged")
        self.assertFalse(r["oil_added_to_T"])

    def test_zero_fixture_imports_in_generic_boundary(self):
        r=audit.read_asts(audit.ROOT)
        for name in audit.GENERIC_BOUNDARY_MODULES:
            self.assertFalse(r[name]["imports"] & audit.ISOLATED_FIXTURES,name)

    def test_matrix_rejects_missing_armor_category(self):
        old=audit.SIX_CASES
        try:
            audit.SIX_CASES=tuple(tuple(
                list(row[:3])+["cloth"]+list(row[4:]))
                for row in old)
            with self.assertRaisesRegex(ValueError,"ARMOR_MISSING"):
                audit.assert_matrix()
        finally:
            audit.SIX_CASES=old

    def test_compilation_and_source_integrity(self):
        seen=set()
        for row in audit.audit()["source_snapshots"]:
            self.assertNotIn(row["path"],seen)
            seen.add(row["path"])
            self.assertEqual(len(row["sha256"]),64)
        self.assertEqual(len(seen),9)

if __name__=="__main__":
    unittest.main()
