"""P3-GR: future socket proposal must never grant source admission."""
import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"runner"))
import v216_environment_build_coordinator as v

class FutureFiveSockets(unittest.TestCase):
    def test_three_intrinsic_plus_two_candidates(self):
        original={"neck":1,"finger1":1,"finger2":1,
                  "head":0,"wrists":0,"waist":0}
        result=v._future_target_five_socket_plan(original)
        self.assertTrue(result["can_place_four"])
        self.assertEqual(result["original_intrinsic_total"],3)
        self.assertEqual(result["planned_socket_total"],5)
        self.assertEqual(result["provisional_added_by_slot"],{
            "wrists":1,"waist":1})
        self.assertFalse(result["additional_source_verified"])
        self.assertEqual(original["wrists"],0)
        self.assertEqual(result["new_native_calls"],0)
    def test_five_intrinsic_requires_no_bonus(self):
        r=v._future_target_five_socket_plan({
            "neck":1,"finger1":1,"finger2":1,"head":1,"waist":1})
        self.assertTrue(r["can_place_four"])
        self.assertTrue(r["additional_source_verified"])
        self.assertEqual(r["provisional_added_by_slot"],{})
    def test_not_enough_eligible_slots_stays_pending(self):
        r=v._future_target_five_socket_plan({"neck":1,"head":0,"finger1":1})
        self.assertFalse(r["can_place_four"])
        self.assertIsNone(r["planned_socket_counts"])
    def test_missing_original_source_stays_pending(self):
        for raw in (None,{},{"neck":-1},{"neck":1.1}):
            with self.subTest(raw=raw):
                r=v._future_target_five_socket_plan(raw)
                self.assertIsNone(r["planned_socket_counts"])
                self.assertFalse(r["can_place_four"])
    def test_determinism_and_no_intrinsic_mutation(self):
        original={"neck":1,"head":0,"finger1":1,
                  "waist":0,"finger2":1,"wrists":0}
        p=v._future_target_five_socket_plan(original)
        q=v._future_target_five_socket_plan(dict(reversed(
            list(original.items()))))
        self.assertEqual(p["planned_socket_counts"],q["planned_socket_counts"])
        self.assertEqual(original["head"],0)
if __name__=="__main__":
    unittest.main()
