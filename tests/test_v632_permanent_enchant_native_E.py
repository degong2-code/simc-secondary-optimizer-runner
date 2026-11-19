"""v632 exact permanent-enchant SimC initial-gear E; offline mock Native only."""
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v632_permanent_enchant_native_E as enchant

REV="a"*40
BASE=("paladin=simc_source_g_probe\n"
      "race=human\nspec=retribution\n"
      "finger1=simc_source_240111,id=240111,ilevel=334,source=local\n"
      "finger2=simc_source_240112,id=240112,ilevel=334,source=local\n")
GEAR={"finger1":{"encoded_item":"simc_source_240111,id=240111,ilevel=334"},
      "finger2":{"encoded_item":"simc_source_240112,id=240112,ilevel=334"}}


def report(active):
    data={key:dict(value) for key,value in GEAR.items()}
    if active:
        data["finger1"]["encoded_item"]+=",enchant_id=8025"
    return json.dumps({"report_version":"2.0.0","git_revision":REV,
        "sim":{"players":[{"gear":data}]}},sort_keys=True).encode("utf8")


class PermanentEProbeTests(unittest.TestCase):
    def test_one_selected_line_and_unbuffed_source_only(self):
        planned=enchant.prepare(BASE,slot="finger1",item_id=240111,
                                enchant_id=8025,target_ilevel=334)
        self.assertIn(",enchant_id=8025",planned["active"])
        self.assertNotIn("enchant_id=",planned["baseline"])
        self.assertEqual(
            sum(a!=b for a,b in zip(planned["baseline"].splitlines(),
                                   planned["active"].splitlines())),1)
        for invalid in (
            BASE+"gear_haste_rating=500\n",
            BASE+"temporary_enchant=disabled\n",
            BASE.replace("ilevel=334","ilevel=335",1),
            BASE.replace("finger1=simc_source_","finger1=simc_source_"
                         "333,enchant_id=8011,",1),
        ):
            with self.subTest(invalid=invalid):
                with self.assertRaises(enchant.EnchantEBlocked):
                    enchant.prepare(invalid,slot="finger1",
                                    item_id=240111,enchant_id=8025,
                                    target_ilevel=334)
        self.assertTrue(enchant.verify_only_target_changed(
            report(False),report(True),slot="finger1",item_id=240111,
            enchant_id=8025,simc_revision=REV))
        corrupted=json.loads(report(True))
        corrupted["sim"]["players"][0]["gear"]["finger2"]["encoded_item"]+=",id=4"
        with self.assertRaisesRegex(enchant.EnchantEBlocked,
                                    "OTHER_PHYSICAL_ITEMS_CHANGED"):
            enchant.verify_only_target_changed(
                report(False),json.dumps(corrupted).encode(),
                slot="finger1",item_id=240111,enchant_id=8025,
                simc_revision=REV)

    def test_v278_case_reuse_and_v297_unbuffed_gear_positive_delta(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            source=root/"source"/"v233.simc"
            source.parent.mkdir()
            source.write_text(BASE,encoding="utf8")
            exe=root/"simc.exe"
            exe.write_bytes(b"fake binary verified by runner only")
            fake=[]
            for i,kind in enumerate(("baseline","active")):
                folder=root/"source"/kind
                folder.mkdir()
                (folder/"receipt.json").write_text(
                    json.dumps({"status":"NATIVE_JSON2_CAPTURED"}))
                (folder/"native.json").write_bytes(report(i==1))
                haste=1000+(30 if i else 0)
                (folder/"simc.log").write_text(
                    "Player 'simc_source_g_probe' total gear stats:"
                    f" Crit=900 Haste={haste} Mastery=800 Vers=700\n")
                fake.append({"folder":folder,
                    "receipt":{"status":"NATIVE_JSON2_CAPTURED"},
                    "new_native_calls":1-i,"cache_reused":bool(i)})
            with mock.patch.object(enchant.native_cases,"run_case",
                                   side_effect=fake) as calls:
                actual=enchant.measure(
                    stage_root=root,source_profile_path=source,binary=exe,
                    simc_revision=REV,game_build="12.1.5.70961",
                    target_ilevel=334,slot="finger1",
                    item_id=240111,enchant_id=8025)
            self.assertEqual(calls.call_count,2)
            self.assertEqual(actual["status"],
                "SIMC_PERMANENT_ENCHANT_EXACT_INITIAL_GEAR_E_UNADMITTED")
            self.assertEqual(actual["new_native_calls"],1)
            self.assertEqual(actual["fixed_E_unadmitted"],{
                "crit_rating":0,"haste_rating":30,
                "mastery_rating":0,"versatility_rating":0})
            self.assertFalse(actual["user_selectable"])
            self.assertFalse(actual["budget_owner_approved"])
            self.assertFalse(actual["gameplay_effect_certified"])

    def test_scaled_unknown_zero_or_proc_drift_does_not_forge_E(self):
        # No gear delta: cannot convert an unknown static-scaled source to E0.
        zeros={"line":"same","all_stats":{"Crit":900,"Haste":1000,
               "Mastery":800,"Vers":700}}
        with self.assertRaises(enchant.initial_gear.OilGearBlocked):
            enchant.initial_gear.compare(off=zeros,on=zeros)
        changed=json.loads(report(True))
        changed["sim"]["players"][0]["gear"]["finger1"]["encoded_item"]=(
            "simc_source_240111,id=240113,ilevel=334,enchant_id=8025")
        with self.assertRaisesRegex(enchant.EnchantEBlocked,
                                    "PHYSICAL_ITEM_DRIFT"):
            enchant.verify_only_target_changed(
                report(False),json.dumps(changed).encode(),
                slot="finger1",item_id=240111,enchant_id=8025,
                simc_revision=REV)


if __name__=="__main__":
    unittest.main()
