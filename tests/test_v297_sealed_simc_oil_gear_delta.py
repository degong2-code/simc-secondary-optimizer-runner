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

    def test_original_v278_cached_cases_feed_internal_unbuffed_owner(self):
        import tempfile
        from unittest import mock
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            profile=root/"original.simc"
            profile.write_text(
                "paladin=source_actor\nrace=dwarf\nspec=retribution\n"
                "main_hand=simc_source_9010,id=9010,ilevel=334,source=local\n")
            binary=root/"simc"
            binary.write_bytes(b"test binary placeholder, never executed")
            folders={}
            for variant,line in (("baseline",OFF),("active",ON)):
                folder=root/variant
                folder.mkdir()
                (folder/"simc.log").write_text(line+"\n")
                (folder/"receipt.json").write_text('{"synthetic":true}')
                folders[variant]=folder
            used=[]
            def cached(**kwargs):
                variant=kwargs["variant"]
                used.append(kwargs)
                return {"receipt":{"status":"NATIVE_JSON2_CAPTURED"},
                        "folder":folders[variant],
                        "new_native_calls":0,"cache_reused":True}
            with mock.patch.object(simc.native_pair,"run_case",
                                   side_effect=cached):
                got=simc.measure(
                    stage_root=root,source_profile_path=profile,
                    binary=binary,simc_revision="c"*40,
                    game_build="12.1.5.70783",target_ilevel=334,
                    oil_token="main_hand:thalassian_phoenix_oil_2",
                    enchant_id=8052)
            self.assertEqual(got["status"],
                "SIMC_PRECOMBAT_TOTAL_GEAR_STATIC_NUMBER_SOURCE_ONLY")
            self.assertEqual(got["new_native_calls"],0)
            self.assertEqual(got["static_CHMV_vector_unadmitted"],{
                "crit_rating":16,"haste_rating":16,
                "mastery_rating":0,"versatility_rating":0})
            self.assertTrue(all("debug=1" in r["profile"] for r in used))
            self.assertTrue(all("flask=disabled" in r["profile"]
                                for r in used))
            self.assertFalse(got["weapon_and_hand_applicability_verified"])
    def test_v216_original_oil_mask_accepts_only_numeric_source_candidate(self):
        import v216_environment_build_coordinator as build
        vector={"crit_rating":16,"haste_rating":16,
                "mastery_rating":0,"versatility_rating":0}
        candidate={
            "physical_item_id":243734,"crafting_quality":2,
            "simc_input_token":"main_hand:thalassian_phoenix_oil_2",
            "simc_enchant_id":8052,"selected_hand":"main_hand",
            "status":"SIMC_PRECOMBAT_GEAR_NUMBER_SOURCE_ONLY",
            "rating_candidate_unadmitted":vector}
        compat={
            "schema":"v286_representative_oil_source_compatibility_v1",
            "status":"REPRESENTATIVE_OIL_MASK_MATCH_SOURCE_ONLY",
            "same_build_source_only":True,"game_build":"12.1.5.70783",
            "simc_revision":"c"*40,"environment_ready":False,
            "candidate_options":[{
                "oil_item_id":243734,"quality_rank":2,
                "simc_enchant_id":8052,"simc_token":"thalassian_phoenix_oil",
                "hand":"main_hand","matched_same_build_spell_equipped_masks":True,
                "user_selectable":False,"representative_weapon_id":9010}]}
        joined=build._zero_history_quality_weapon_candidate_join(
            numeric={"status":"PHYSICAL_ITEM_SIMC_F_O_CANDIDATES_UNADMITTED",
                     "flask":[],"oil":[candidate]},
            weapon_source=compat,game_build="12.1.5.70783",
            simc_revision="c"*40)
        self.assertEqual(joined[
            "oil_representative_weapon_matches_unadmitted"][0][
                "static_O_for_hand_unadmitted"],vector)
        self.assertFalse(joined["environment_ready"])
        self.assertFalse(joined["user_selectable"])

    def test_engine_source_owned_selected_O_updates_shared_v222_B_T_once(self):
        # Generic source/Native owner wiring, NOT a fresh proof about a
        # particular game's oil. Original source + hand mask + same gear
        # must match before the existing budget calculator can use O.
        import v216_environment_build_coordinator as build
        import v222_season_budget_contract as budget
        game="12.9.0.99999"
        rev="d"*40
        manifest="a"*64
        vec={"crit_rating":3,"haste_rating":5,
             "mastery_rating":0,"versatility_rating":0}
        selected={"flask_item_id":101,
                  "oil_item_ids_by_hand":{"main_hand":209}}
        token="main_hand:sample_engine_oil_3"
        source={"schema":"v296_pinned_simc_raw_oil_static_rating_v1",
                "source_unbuffed":True,"game_build":game,
                "simc_revision":rev,"source_sha256":"b"*64,
                "items":[{"enchant_id":309,
                          "static_CHMV_vector":None}]}
        row={"physical_item_id":209,"selected_hand":"main_hand",
             "simc_enchant_id":309,"simc_input_token":token,
             "crafting_quality":3,
             "status":"SIMC_PRECOMBAT_GEAR_NUMBER_SOURCE_ONLY",
             "static_CHMV_vector_unadmitted":vec,
             "source_min_ilevel":10,"source_max_ilevel":0,
             "static_O_unbuffed_source_sha256":"b"*64,
             "game_build":game,"simc_revision":rev,
             "physical_item_source_candidate_sha256":"c"*64,
             "simc_native_receipt_sha256":["1"*64,"2"*64]}
        numeric={"oil":[row]}
        match={"physical_item_id":209,"hand":"main_hand",
               "status":"SAME_BUILD_REPRESENTATIVE_WEAPON_MASK_MATCH_SOURCE_ONLY",
               "static_O_for_hand_unadmitted":vec,
               "selected_representative_weapon_id_unadmitted":409}
        masks={"game_build":game,"simc_revision":rev,
               "oil_representative_weapon_matches_unadmitted":[match],
               "oil_source_stage_identities":{"OIL":{"stage_receipt_sha256":"3"*64}}}
        measurement={"status":"SIMC_PRECOMBAT_TOTAL_GEAR_STATIC_NUMBER_SOURCE_ONLY",
                     "simc_input_token":token,"enchant_id":309,
                     "game_build":game,"simc_revision":rev,
                     "selected_hand":"main_hand",
                     "representative_weapon_id":409,"target_ilevel":334,
                     "talent_buffed_stats_not_used":True,
                     "static_CHMV_vector_unadmitted":vec}
        call=dict(preflight={"game_build":game,"simc_revision":rev,
                              "source_catalog_manifest_sha256":manifest},
                  staged={"status":"FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED"},
                  compilation={"simc_revision":rev},
                  selected=selected,original_oil=source,numeric=numeric,
                  choices=masks,
                  scaled_native_gear=[{"physical_item_id":209,
                                      "selected_hand":"main_hand",
                                      "measurement":measurement}],
                  target_ilevel=334)
        owner=build._fresh_source_owner_selected_O_component(**call)
        self.assertEqual(owner["rating"],vec)
        self.assertTrue(owner["weapon_applicability_verified"])
        self.assertEqual(owner["selected_oil_item_ids_by_hand"],
                         selected["oil_item_ids_by_hand"])
        self.assertEqual(owner["oil_by_hand"]["main_hand"][
            "simc_input_token"],token)
        def component(amount,kind):
            return {"rating":amount,"game_build":game,
                    "source_catalog_manifest_sha256":manifest,
                    "source_sha256":"e"*64,"source_verification":kind}
        evidence={"schema":budget.SCHEMA,
                  "game_build":game,"simc_revision":rev,
                  "source_catalog_manifest_sha256":manifest,
                  "source_catalog_artifact_sha256":"f"*64,
                  "target_ilevel":334,"components":{
                    "G":component(1000,"EXACT_NATIVE"),
                    "J":component(100,"VALID_SAME_SEASON_SOURCE"),
                    "F":component(100,"EXACT_NATIVE"),
                    "O":owner},
                  "fixed_L":{x:0 for x in budget.STATS},
                  "fixed_E":{x:0 for x in budget.STATS},
                  "G_reference_excludes_selected_E":True}
        common=dict(source_catalog={"game_build":game,
                     "simc_revision":rev,"manifest_sha256":manifest},
                    source_artifact_sha256="f"*64,
                    evidence=evidence,target_ilevel=334)
        automatic=budget.preprofile_budget(**common)
        self.assertEqual((automatic["base_B"],automatic["final_T"]),
                         (1200,1208))
        manual=budget.preprofile_budget(**common,manual_final_T=1300)
        self.assertEqual((manual["base_B"],manual["final_T"]),
                         (1292,1300))
        # Wrong actual representative weapon or missing source must not
        # turn a source-only mask into a verified product selection.
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                    "SIMC_WEAPON_PROFILE"):
            build._fresh_source_owner_selected_O_component(
                **{**call,"scaled_native_gear":[{
                    "physical_item_id":209,"selected_hand":"main_hand",
                    "measurement":{**measurement,
                                   "representative_weapon_id":410}}]})
        self.assertIsNone(build._fresh_source_owner_selected_O_component(
            **{**call,"numeric":{"oil":[]}}))

if __name__=="__main__":unittest.main()
