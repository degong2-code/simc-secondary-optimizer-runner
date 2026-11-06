"""P3-GK compact real source-derived F wave/J layout diagnosis, offline."""
import unittest
from integration_probes import p3_fr_zero_base_t1_acceptance as probe


class ExistingFJDiagnostic(unittest.TestCase):
    def test_observed_partial_F_wave_missing_special_J_stays_pending(self):
        progress={
            "requires":["AUTO_F_NEXT_MEASUREMENT_BATCH_PENDING"],
            "automatic_F_native_measurements_unadmitted":{
                "status":"AUTO_F_NATIVE_MEASURED_SOURCE_ONLY",
                "attempted":4,"remaining":12,"new_native_calls":8,
                "per_item":[
                    {"physical_item_id":123,"status":"SIMC_STATIC_CHMV_EFFECT_OBSERVED_NOT_ADMITTED",
                     "new_native_calls":2,"cache_hit":False,
                     "native_log_excerpt":"ignored"},
                ]}}
        compiled={"automatic_F_O_measurement_candidates_unadmitted":{
            "flask":[{"physical_item_id":n} for n in range(16)]}}
        d=probe.summarize_existing_f_and_j(
            progress,compiled,special_gem_id=None)
        self.assertEqual(d["F"]["source_candidate_count"],16)
        self.assertTrue(d["F"]["next_batch_pending"])
        self.assertEqual(d["F"]["attempted"],4)
        self.assertEqual(d["F"]["remaining"],12)
        self.assertEqual(d["F"]["items"][0]["physical_item_id"],123)
        self.assertNotIn("native_log_excerpt",str(d))
        self.assertTrue(d["J"]["missing_required_existing_special_gem_id"])
        self.assertEqual(d["native_calls"],0)
        self.assertEqual(d["source_http_calls"],0)

    def test_supplied_special_id_no_extra_source_confirmation(self):
        d=probe.summarize_existing_f_and_j(
            {"requires":[],"default_intrinsic_gem_layout_unadmitted":{
                "special_gem_id":999}},
            {"automatic_F_native_measurements_unadmitted":{
                "status":"AUTO_F_NATIVE_MEASURED_SOURCE_ONLY",
                "attempted":1,"remaining":0,"new_native_calls":0,
                "per_item":[]}},special_gem_id=999)
        self.assertFalse(d["J"]["missing_required_existing_special_gem_id"])
        self.assertTrue(d["J"]["physical_layout_observed"])
        self.assertFalse(d["F"]["next_batch_pending"])
        self.assertEqual(d["F"]["new_native_calls"],0)

    def test_no_F_source_keeps_values_unknown(self):
        d=probe.summarize_existing_f_and_j({},{},special_gem_id=None)
        self.assertIsNone(d["F"]["attempted"])
        self.assertIsNone(d["F"]["source_candidate_count"])
        self.assertTrue(d["J"]["missing_required_existing_special_gem_id"])

    def test_f_wave_rows_not_unbounded(self):
        with self.assertRaisesRegex(ValueError,"P3_GK_F_MEASUREMENT_RECEIPT_COUNT"):
            probe.summarize_existing_f_and_j(
                {},{"automatic_F_native_measurements_unadmitted":{
                    "per_item":[{}]*9}},special_gem_id=None)


if __name__=="__main__":
    unittest.main()
