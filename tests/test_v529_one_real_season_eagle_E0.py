"""v529 focused fail-closed contract for ONE real v528 70783 E=0 selection.

This unit test never emulates SimC effects or invents an approved user session.
The real source/Native connection is tested by the bounded Windows v530 job.
"""
from __future__ import annotations
import copy,json,pathlib,sys,tempfile,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as sessions
import v529_current_season_eagle_E0_bridge as owner
import v098_target_user_scenario_bootstrap as bootstrap

class OneSourceBoundEagle(unittest.TestCase):
    def user(self):
        controls=sessions.standard_controls(("hunter","survival"))
        controls.update(race="human",oil_hands=[],trinket_ids=[270175,270173])
        return sessions.user_scenario(controls)
    def test_existing_native_receipt_metadata_exact(self):
        proof=owner.evidence()
        self.assertEqual(proof["game_build"],owner.BUILD)
        self.assertEqual(proof["enchant_scope"]["physical_enchant_Native_calls"],6)
        self.assertEqual(owner.ZERO,dict.fromkeys(owner.ZERO,0))
        self.assertFalse(proof["enchant_scope"]["scoped_results"][0]["source_ui_selectable"])
    def test_only_original_334_user_loadout_and_2_trinkets(self):
        good=self.user()
        owner.user_scope(good)
        changes=[
            ("target",{"ilevel":335,"final_T":None}),
            ("target",{"ilevel":334,"final_T":3107}),
            ("oil_hands",["main_hand"]),
            ("trinkets",[{"slot":"trinket1","item_id":270169,"options":{}},
                          {"slot":"trinket2","item_id":270174,"options":{}}]),
            ("embellishments",[{"slot":"head","item_id":244579,
                                 "options":{"embellishment":"arcanoweave_lining"}}])
        ]
        for key,val in changes:
            with self.subTest(key=key,val=val):
                changed=copy.deepcopy(good)
                changed[key]=val
                with self.assertRaisesRegex(owner.SourceBlocked,
                                            "SINGLE_NATIVE_WITNESSED"):
                    owner.user_scope(changed)
    def test_original_proof_change_does_not_authorize(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad=pathlib.Path(tmp)/"tampered.json"
            src=owner.evidence()
            src["enchant_scope"]["scoped_results"][0]["per_profile_E"]={
                **owner.ZERO,"haste_rating":30}
            bad.write_text(json.dumps(src),encoding="utf8")
            with patch.object(owner,"PROOF",bad):
                with self.assertRaisesRegex(owner.SourceBlocked,
                                            "PINNED_REAL_WINDOWS_NATIVE_STATIC_PROOF_DRIFT"):
                    owner.evidence()
    def test_enchant_choice_and_fresh_catalog_required(self):
        with self.assertRaisesRegex(owner.SourceBlocked,
                                    "ONLY_ONE_EXACT_FINGER1_7967"):
            owner.source({"finger1":8025},None)
        with self.assertRaisesRegex(owner.SourceBlocked,
                                    "FRESH_V213_CATALOG_REQUIRED"):
            owner.source(owner.CHOICE,None)
    def test_admit_needs_actual_simc_profile_and_binary(self):
        with self.assertRaisesRegex(owner.SourceBlocked,
                                    "EXACT_WINDOWS_BINARY_OR_REVISION_REQUIRED"):
            owner.admit(owner.CHOICE,
                        "finger1=selected_268266,id=268266,ilevel=334,source=local,enchant_id=7967\n",
                        {"scenario":{"character":{"class":"hunter","spec":"survival"},
                                     "equipment":{"special":[],"crafted":[]}}},
                        "incorrect",owner.REVISION)
        with self.assertRaisesRegex(owner.SourceBlocked,
                                    "ORIGINAL_UNENCHANTED_V528_PROFILE_SHA_MISMATCH"):
            owner.admit(owner.CHOICE,
                        "finger1=selected_268266,id=268266,ilevel=334,source=local,enchant_id=7967\n",
                        {"scenario":{"character":{"class":"hunter","spec":"survival"},
                                     "equipment":{"special":[],"crafted":[]}}},
                        owner.BIN_SHA,owner.REVISION)
    def test_scope_does_not_change_existing_numeric_budget(self):
        self.assertEqual(sum(owner.ZERO.values()),0)
        self.assertEqual(owner.CHOICE,{"finger1":7967})
        self.assertEqual(bootstrap.SEASON_ENCHANT_FIELD,
                         "selected_season_enchants")

if __name__=="__main__": unittest.main()
