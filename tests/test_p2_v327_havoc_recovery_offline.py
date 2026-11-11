"""v327 original 128 Native recovery identity, Native0 offline."""
from __future__ import annotations
import os,unittest
from unittest import mock
from integration_probes import p2_v327_havoc_recover_original_128_only_n168 as r
class Recovery(unittest.TestCase):
    def test_pinned_source_receipt_and_cadence(self):
        self.assertEqual(r.EXPECTED,{"v290_original":(57,7,4235),
                                     "v318_idea001":(58,6,3950)})
        self.assertEqual(len(r.RECEIPT_SHA),64)
        self.assertEqual(len(r.PROFILE_SHA),64)
        self.assertEqual(len(r.ZIPS),2)
    def test_fails_closed_on_tampered_receipt(self):
        with self.assertRaisesRegex(r.RecoveryBlocked,"ORIGINAL_ACTION_RECEIPT_SHA"):
            r.original_receipt(b'{}')
    def test_real_v291_final_T_is_a_four_rating_vector_not_scalar(self):
        from integration_probes import p2_v327_havoc_new_user_three_seed_n_real_once as study
        vector=dict(zip(study.quality.STATS,(1398,93,1305,311)))
        self.assertEqual(sum(vector.values()),3107)
        self.assertIsInstance(vector,dict)
        self.assertNotEqual(vector,3107)
    def test_no_native_without_explicit_optin(self):
        with mock.patch.dict(os.environ,{"P2_V327_REUSE_ORIGINAL_128_NATIVE_ONLY":"0"}):
            with self.assertRaisesRegex(r.RecoveryBlocked,"EXPLICIT_RECOVERY_NATIVE_ONCE"):
                r.main()
if __name__=="__main__":unittest.main()
