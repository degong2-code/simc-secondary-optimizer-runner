"""Season runeforges are discovered from pinned SimC module IDs; no Native."""
import copy,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v295_season_runeforge_source as source
import v212_environment_manifest as installed
import v294_dk_runeforge_selection as dk
import v055_simc_item_selection as items

REV="7bc10711b5"+"a"*30
BUILD="12.1.5.70783"
SOURCE=b"""
enum runeforges_e {
    RUNEFORGE_NONE = -1,
    RUNEFORGE_RAZORICE,
    RUNEFORGE_ID_RAZORICE = 3370,
    RUNEFORGE_ID_FALLEN_CRUSADER = 3368,
};
"""

class PinnedDeathKnightRunes(unittest.TestCase):
    def test_next_season_new_ids_observed_from_simc_not_fixed_list(self):
        doc=source.compile_source(SOURCE,game_build=BUILD,simc_revision=REV)
        self.assertTrue(source.verify(doc,game_build=BUILD,simc_revision=REV))
        self.assertEqual([x["enchant_id"] for x in doc["items"]],[3368,3370])
        self.assertFalse(doc["source_profile_gear_copied"])
        changed=SOURCE.replace(b"= 3370",b"= 993370")
        later=source.compile_source(changed,game_build="12.2.0.71000",
                                    simc_revision=REV)
        self.assertEqual([x["enchant_id"] for x in later["items"]],
                         [3368,993370])
        self.assertNotEqual(later["manifest_sha256"],doc["manifest_sha256"])
        rows={"main_hand":{"slot":"main_hand","item_id":268209,
                           "ilevel":334,"options":{}}}
        def need(ok,why):
            if not ok:raise ValueError(why)
        # Source-listed future ID is usable even though it is not part of
        # the previous-season RUNE_IDS constant.
        dk.apply(rows=rows,selection={"main_hand":993370},
                 class_name="deathknight",weapon_form="dual_one_hand",
                 need=need,admitted_ids={x["enchant_id"] for x in later["items"]})
        self.assertIn("enchant_id=993370",
                      items.equipment_line(**rows["main_hand"]))

    def test_install_projection_requires_same_build_and_stage_receipt(self):
        original=source.compile_source(SOURCE,game_build=BUILD,
                                       simc_revision=REV)
        signed={**original,"source_stage_receipt_sha256":"f"*64}
        self.assertEqual(installed._project_season_dk_runes(
            signed,game_build=BUILD,simc_revision=REV),signed)
        with self.assertRaisesRegex(installed.EnvironmentBlocked,
                                     "FRESH_DK_PINNED_SOURCE_DRIFT"):
            installed._project_season_dk_runes(
                signed,game_build="12.2.0.71000",simc_revision=REV)
        forged=copy.deepcopy(signed)
        forged["items"][0]["enchant_id"]=999999
        with self.assertRaisesRegex(installed.EnvironmentBlocked,
                                     "FRESH_DK_PINNED_SOURCE_DRIFT"):
            installed._project_season_dk_runes(
                forged,game_build=BUILD,simc_revision=REV)
        self.assertIsNone(installed._project_season_dk_runes(
            None,game_build=BUILD,simc_revision=REV))

    def test_v217_cached_collector_reuses_pinned_source_without_repeat_http(self):
        import v229_simc_only_source_seed as seed
        import v275_pinned_simc_compiler_inputs as pinned
        class Resp:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,n):return SOURCE
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            folder=root/"source"/"v275_pinned_simc_compiler_inputs"
            folder.mkdir(parents=True)
            origin={"status":"PINNED_V211_AND_GENERATED_SOURCES_SEALED",
                    "simc_revision":REV,"source_dir":str(folder),
                    "source_stage":{"status":"REUSED_VERIFIED",
                                    "receipt_sha256":"a"*64}}
            meta={"dk":{"size":len(SOURCE),"sha":seed.git_blob(SOURCE)}}
            used=[]
            def transport(req,timeout):
                used.append(req.full_url)
                return Resp()
            with mock.patch.object(pinned,"pinned_git_blobs",
                                   return_value=meta):
                first=source.collect(stage_root=root,game_build=BUILD,
                    pinned_source=origin,transport=transport)
                self.assertEqual(first["status"],
                                 "PINNED_SIMC_DK_RUNEFORGE_OPTIONS_SEALED")
                self.assertEqual(first["network_calls"],1)
                self.assertEqual(len(used),1)
                second=source.collect(stage_root=root,game_build=BUILD,
                    pinned_source=origin,transport=transport)
                self.assertEqual(second["network_calls"],0)
                self.assertEqual(first["manifest_sha256"],
                                 second["manifest_sha256"])
                self.assertEqual(len(used),1)

    def test_source_missing_or_ambiguous_does_not_unlock_any(self):
        for data in (b"",b"int other=0;",
                     SOURCE+SOURCE,
                     SOURCE.replace(b"= 3370",b"= 3368")):
            with self.subTest(value=data[:30]),self.assertRaises(
                    source.RuneforgeSourceBlocked):
                source.compile_source(data,game_build=BUILD,simc_revision=REV)
if __name__=="__main__":unittest.main()
