"""v182: user-friendly controls, source-first gear, no SimC Native."""
import json,pathlib,sys,tempfile,unittest
from unittest import mock
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v108_native_consumable_inputs as consumables
import v106_user_session_controller as sessions
import v098_target_user_scenario_bootstrap as bootstrap
import v167_product_season_gear_adapter as seasons
import v113_local_web_api as web

class SimpleUserInputs(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=pathlib.Path(tmp.name)
        self.binary=self.root/"NO_NATIVE";self.binary.write_bytes(b"NO_ACTUAL_SIMC")
        self.revision="7bc10711b5"

    def test_all_26_weapon_forms_disable_incompatible_offhand(self):
        doc=seasons.public_options(seasons.read())
        self.assertEqual(len(doc["weapon_forms"]),26)
        self.assertEqual(doc["weapon_forms"]["mage/frost"],"one_hand_frill")
        self.assertEqual(doc["weapon_forms"]["warrior/fury"],"dual_two_hand")
        for key,form in doc["weapon_forms"].items():
            cl,sp=key.split("/")
            controls=sessions.standard_controls((cl,sp))
            controls["oil_hands"]=["main_hand","off_hand"]
            if form in sessions.DUAL_FORMS:
                self.assertEqual(len(sessions.user_scenario(controls)["oil_hands"]),2)
            else:
                with self.assertRaisesRegex(sessions.SessionBlocked,
                    "OIL_HANDS_INCOMPATIBLE_WITH_SOURCE_WEAPON_FORM"):
                    sessions.user_scenario(controls)

    def test_four_stat_runes_leave_source_rows_except_fourth(self):
        for base in (
          "136822:1/136816:1/136817:1/136815:1/136814:1",
          "136822:1/136817:1/136821:1/136814:1",
          "rune_of_unleashed_fire/rune_of_lynxlike_reflexes/rune_of_lingering/rune_of_burning_haste/rune_of_overload",
        ):
            for stat in consumables.OMNIUM_ROW4_BY_STAT:
                with self.subTest(base=base,stat=stat):
                    updated=consumables.change_row_four(base,stat)
                    self.assertEqual(len(base.split("/")),len(updated.split("/")))
                    self.assertEqual(sum(a!=b for a,b in zip(base.split("/"),updated.split("/"))),int(consumables.OMNIUM_ROW4_BY_STAT[stat] not in base.split("/")))
                    self.assertIn(consumables.OMNIUM_ROW4_BY_STAT[stat],updated)
        with self.assertRaisesRegex(consumables.ConsumableBlocked,
                                    "OMNIUM_SOURCE_ROW4_AMBIGUOUS"):
            consumables.change_row_four("bad:1/invalid:1","row4_crit")

    def test_real_334_season_profile_four_stats_and_distinct_session_ids(self):
        keys=[]
        for stat in consumables.OMNIUM_ROW4_BY_STAT:
            controls=sessions.standard_controls(("mage","frost"))
            controls["consumable_choices"]["omnium_talents"]=stat
            user=sessions.user_scenario(controls)
            sid,_=sessions.session_key(user,self.binary,self.revision,
                                       current_season_product=True)
            keys.append(sid)
            with mock.patch.object(bootstrap.entry.durable,"run") as native:
                prepared=bootstrap.build(user,self.root/stat,self.binary,
                                          self.revision,current_season_product=True)
                native.assert_not_called()
            profile=(self.root/stat/"profile.simc").read_text("utf8")
            self.assertIn(consumables.OMNIUM_ROW4_BY_STAT[stat],profile)
            self.assertEqual(prepared["plan"]["native_limit"],6)
        self.assertEqual(len(set(keys)),4)

    def test_current_season_craft_base_is_source_derived_and_gui_hides_advanced_fields(self):
        options=seasons.public_options(seasons.read())["choices"]
        crafts=options["selectable_stat_craft"]
        self.assertEqual(len(crafts),106)
        self.assertTrue(all("class_id" in x and "subclass_id" in x for x in crafts))
        for family in (1,2,3,4):
            self.assertTrue(any(x["class_id"]==4 and
                      x["subclass_id"]==family and x["slot_hint"]=="wrists"
                      for x in crafts))
        self.assertTrue(any(x["item_id"]==239656 for x in crafts))
        controls=sessions.standard_controls(("mage","frost"))
        controls["embellishments"]=[{"slot":"back","item_id":239656,
              "options":{"crafted_stats":"32/36","embellishment":"arcanoweave_lining"}}]
        scenario=sessions.user_scenario(controls)
        self.assertEqual(scenario["embellishments"][0]["item_id"],239656)
        with mock.patch.object(bootstrap.entry.durable,"run") as native:
            prepared=bootstrap.build(scenario,self.root/"craft",
                            self.binary,self.revision,current_season_product=True)
            native.assert_not_called()
        profile=(self.root/"craft"/"profile.simc").read_text("utf8")
        self.assertIn("embellishment=arcanoweave_lining",profile)
        self.assertIn("crafted_stats=32/36",profile)
        js=(ROOT/"runner/webui/app.js").read_text("utf8")
        html=(ROOT/"runner/webui/index.html").read_text("utf8")
        for marker in ('function oilCompatibility()','function chosenCraft(slot)',
            'function selectedGear(nodeId, group)','row4_crit','row4_vers',
            '["arcanoweave_lining","비전직조 안감"]',
            '["sunfire_silk_lining","태양불꽃 비단 안감"]'):
            self.assertIn(marker,js)
        self.assertIn("label.hidden=isPrivate",js)
        self.assertIn("장식은 부위·종류·제작 스탯만 선택",html)
        self.assertIn("Omnium Folio · 4열 스탯",html)

if __name__=="__main__":unittest.main()
