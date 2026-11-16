"""v535: one verified user ring-enchant UI bridge, no Native or network.

Checks fail-closed browser contract. General season candidates stay blocked.
"""
from __future__ import annotations
import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v531_current_season_positive_E_bridge as exact
import v529_current_season_eagle_E0_bridge as e0

class ExactEnchantUiScope(unittest.TestCase):
    def test_source_native_proof_stays_exact(self):
        self.assertEqual(e0.CHOICE,{"finger1":7967})
        self.assertEqual(set(exact.ENCHANTS),{7965,8025})
        self.assertEqual(exact.check_choice({"finger1":8025})[1]["haste_rating"],30)
        self.assertEqual(exact.check_choice({"finger1":7965})[1]["mastery_rating"],26)
        for bad in ({"finger2":8025},{"finger1":7964},
                    {"finger1":8025,"finger2":7965}):
            with self.assertRaises(exact.PositiveEnchantBlocked):
                exact.check_choice(bad)

    def test_backend_publishes_separate_exact_only_not_catalog_approval(self):
        api=(ROOT/"runner/v113_local_web_api.py").read_text("utf8")
        self.assertIn('"verified_exact_user_enchant_runtime":exact_runtime',api)
        self.assertIn('"general_selectable":False',api)
        self.assertIn('exact_positive_enchant.project(',api)
        self.assertIn('exact_positive_enchant.source(',api)
        self.assertIn('exact_e0_enchant.source(',api)
        self.assertIn('"installed_manifest_sha256":',api)
        self.assertIn('"runtime_selectable":False',api)
        self.assertIn('"new_approval_granted":False',api)

    def test_browser_rejects_other_class_race_items_or_unsupported_id(self):
        js=(ROOT/"runner/webui/app.js").read_text("utf8")
        self.assertIn('function exactUserEnchantInputsMatch()',js)
        self.assertIn('state.exactUserEnchantIds.has(eid)',js)
        self.assertIn('exactUserEnchantInputsMatch();',js)
        self.assertIn('exact.scope.trinket_ids.join(",")==="270175,270173"',js)
        self.assertIn('exact.scope?.finger1_item_id===268266',js)
        self.assertIn('Number(field("ilevel"))===334',js)
        self.assertIn('oils.length===0 && specials.length===0 && crafted.length===0',js)
        self.assertIn('exact.general_selectable===false',js)
        self.assertIn('UNVERIFIED_ENCHANT_SELECTION_BLOCKED',js)
        self.assertIn('selector.disabled=true',js)
        self.assertIn('selector.disabled=false',js)
        self.assertIn('catalog.enchant_candidates?.selectable_count===0',js)

if __name__=="__main__":unittest.main()
