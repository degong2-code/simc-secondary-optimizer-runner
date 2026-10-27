"""v122 common profile output for ALL connected DPS archetypes; offline."""
from __future__ import annotations
import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v063_numeric_injection as numeric
import v122_common_profile_format as common

SAMPLE="""rogue=\"Test\"
spec=subtlety
race=dwarf
iterations=35
gear_crit_rating=700
gear_haste_rating=700
gear_mastery_rating=700
gear_versatility_rating=700
actions=some_action
"""

class CommonProfileFormat(unittest.TestCase):
    def test_new_and_sealed_legacy_runtime_profiles(self):
        old=SAMPLE
        self.assertIs(common.finalize(old,legacy=True),old)
        with self.assertRaisesRegex(numeric.InjectionError,
                                    "MISSING_OR_DUPLICATE_INPUT:json2="):
            numeric.input_parts(old)
        modern=common.finalize(old,legacy=False)
        self.assertEqual(modern.count("json2="),1)
        self.assertIn("json2="+common.JSON2_PLACEHOLDER,modern)
        numeric.input_parts(modern)
        self.assertEqual(common.finalize(modern,legacy=False),modern)
        self.assertEqual(common.finalize(old,legacy=True),old)

    def test_sorts_equipment_by_same_slot_order_for_any_specialization(self):
        rows={slot:{"slot":slot,"item_id":i,"ilevel":334,"options":{}}
              for i,slot in enumerate(("waist","head","main_hand"),1)}
        self.assertEqual(list(common.order_rows(rows,legacy=False)),
                         ["head","main_hand","waist"])
        self.assertEqual(list(common.order_rows(rows,legacy=True)),
                         ["waist","head","main_hand"])
        with self.assertRaisesRegex(common.ProfileFormatBlocked,
                                    "INVALID_PROFILE_EQUIPMENT_ROWS"):
            common.order_rows({"head":dict(rows["waist"])},legacy=False)

    def test_duplicates_and_missing_iterations_never_normalized_away(self):
        for bad in (SAMPLE+"json2=a\\njson2=b\\n",
                    SAMPLE.replace("iterations=35\\n","")):
            with self.subTest(bad=bad[-25:]):
                for legacy in (False,True):
                    with self.assertRaises(
                            (common.ProfileFormatBlocked,numeric.InjectionError)):
                        common.finalize(bad,legacy=legacy)

if __name__=="__main__":
    unittest.main()
