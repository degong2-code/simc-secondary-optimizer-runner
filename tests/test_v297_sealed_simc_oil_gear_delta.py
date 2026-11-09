"""v297 parser contracts only; no new Native or hardcoded seasonal budget."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"runner"))
import v297_sealed_simc_oil_gear_delta as simc

OFF="0.000 Player 'source_actor' total gear stats: Str=1913 Crit=1217 Haste=820 Mastery=533 Vers=358 Wdps=0"
ON="0.000 Player 'source_actor' total gear stats: Str=1913 Crit=1233 Haste=836 Mastery=533 Vers=358 Wdps=0"

class GearStatOwner(unittest.TestCase):
    def test_simc_precombat_owner_exact(self):
        self.assertEqual(simc.compare(
            off=simc.parse_total_gear(OFF,"source_actor"),
            on=simc.parse_total_gear(ON,"source_actor")),
            {"crit_rating":16,"haste_rating":16,
             "mastery_rating":0,"versatility_rating":0})
    def test_buffed_json_cannot_substitute(self):
        with self.assertRaisesRegex(simc.OilGearBlocked,"EXACT_ONE"):
            simc.parse_total_gear(
                "buffed_stats: Crit=1233 Haste=837 Mastery=533 Vers=358",
                "source_actor")
    def test_changed_non_chmv_gear_blocks(self):
        with self.assertRaisesRegex(simc.OilGearBlocked,"NON_CHMV"):
            simc.compare(off=simc.parse_total_gear(OFF,"source_actor"),
                on=simc.parse_total_gear(ON.replace("Wdps=0","Wdps=1"),
                                         "source_actor"))
    def test_negative_or_fractional_delta_blocks(self):
        for val in ("Haste=819","Haste=836.5"):
            with self.subTest(val=val):
                with self.assertRaises(simc.OilGearBlocked):
                    simc.compare(
                        off=simc.parse_total_gear(OFF,"source_actor"),
                        on=simc.parse_total_gear(
                            ON.replace("Haste=836",val),"source_actor"))
    def test_absent_or_duplicate_source_blocks(self):
        for log in (OFF+"\n"+OFF,
                    "Player 'source_actor' buffed_stats: Crit=0"):
            with self.assertRaisesRegex(simc.OilGearBlocked,"EXACT_ONE"):
                simc.parse_total_gear(log,"source_actor")
    def test_no_binary_means_no_native(self):
        self.assertEqual(simc.measure(
            stage_root="/does/not/exist",source_profile_path=None,binary=None,
            simc_revision="x",game_build="",target_ilevel=0,
            oil_token="not_an_oil",enchant_id=0)["new_native_calls"],0)
if __name__=="__main__":unittest.main()
