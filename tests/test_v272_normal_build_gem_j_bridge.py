"""P3-CA existing v216 + v222 J physical link; synthetic offline only."""
import copy,pathlib,sys,tempfile,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v216_environment_build_coordinator as build
import v271_user_socket_gem_layout as gems
from tests.test_v264_environment_standard_budget_integration import prepared


def stage():
    rows={s:{"slot":s,"item_id":12345,"ilevel":334,"options":{}}
          for s in ("head","wrists","waist","feet","shoulders")}
    plan={"socket_counts":{"head":1,"wrists":2,"waist":1,"feet":1},
          "special_gem_id":240967,"special_slot":"head",
          "ordinary_gem_ids":[240908]*4}
    _,receipt=gems.arrange(rows,plan,build.need)
    assert len(set(receipt["ordinary_gem_ids"]))==4
    return receipt,{str(i):23 for i in receipt["ordinary_gem_ids"]}


class NormalBuildGemJ(unittest.TestCase):
    def preflight(self,*,table=None,layout=None,ratings=None,manual=None):
        catalog,_,ui=prepared()
        with tempfile.TemporaryDirectory() as tmp:
            path=pathlib.Path(tmp)/"source.json"
            path.write_text("{}",encoding="utf8")
            with mock.patch.object(build.environment_manifest,"read_json",
                                   return_value=(catalog,"a"*64)), \
                 mock.patch.object(build.source_to_catalog,"verify_catalog"), \
                 mock.patch.object(build.user_catalog,"public_options",
                                   return_value=ui):
                return build.preflight_new_season_source(
                    source_catalog_path=path,
                    expected_game_build=catalog["game_build"],
                    expected_simc_revision=catalog["simc_revision"],
                    target_ilevel=334 if table is not None else None,
                    standard_budget_evidence_by_ilevel=table,
                    standard_budget_reference_track=(
                        "ordinary_two_hand" if table is not None else None),
                    manual_final_T=manual,gem_layout_receipt=layout,
                    gem_rating_by_id=ratings)

    def test_season_nominal_j_bypasses_unresolved_v266_but_not_source_gate(self):
        """Existing source-bounded v216 J connection needs no new SimC run."""
        catalog,_,ui=prepared()
        by_stat={stat:{"item_id":311100+i,"rating":23}
                 for i,stat in enumerate(gems.ORDINARY_FOUR_STATS)}
        nominal={"game_build":catalog["game_build"],
                 "source_sha256":"9"*64,"by_stat":by_stat}
        selected=gems.nominal_four_stat_from_season_source(
            source=nominal,game_build=catalog["game_build"],
            socket_total=5,special_gem_id=311200,need=build.need)
        rows={slot:{"slot":slot,"item_id":12345,
                    "ilevel":334,"options":{}}
              for slot in ("head","wrists","waist","feet","shoulders")}
        plan={"socket_counts":{"head":1,"wrists":2,"waist":1,"feet":1},
              "special_gem_id":311200,"special_slot":"head",
              "ordinary_gem_ids":selected["ordinary_gem_ids"],
              gems.SOURCE_IDS_FIELD:sorted({311200,*selected["ordinary_gem_ids"]})}
        _,layout=gems.arrange(rows,plan,build.need)
        v268={"selected_gem_v221_same_build_items_all_present":True,
              "selected_gem_v221_item_ids_unadmitted":
                  sorted({311200,*selected["ordinary_gem_ids"]}),
              "selected_gem_v221_source_properties_complete":False,
              "selected_ordinary_gem_two_stat_budget_eligible_unadmitted":False,
              "selected_gem_all_raw_points_known":False,
              "enchant_source_sha256":"e"*64}
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            source=root/"v213.json"
            source.write_text("{}",encoding="utf8")
            with mock.patch.object(build.environment_manifest,"read_json",
                                   return_value=(catalog,"a"*64)), \
                 mock.patch.object(build.source_to_catalog,"verify_catalog"), \
                 mock.patch.object(build.user_catalog,"public_options",
                                   return_value=ui), \
                 mock.patch.object(build,"_fresh_gem_item_source_stage",
                     return_value={"candidate_path":str(root/"source.json"),
                                   "source_stage":{"receipt_sha256":"b"*64}}), \
                 mock.patch.object(build.gem_enchant_stage,"view",
                                   return_value=v268):
                kwargs=dict(
                    source_catalog_path=source,
                    expected_game_build=catalog["game_build"],
                    expected_simc_revision=catalog["simc_revision"],
                    source_snapshot_folder=root,
                    source_stage_root=root,
                    gem_layout_receipt=layout,
                    gem_rating_by_id=selected["rating_by_id"])
                pending=build.preflight_new_season_source(**kwargs)
                self.assertNotIn("physical_gem_J_arithmetic_unadmitted",
                                 pending)
                result=build.preflight_new_season_source(
                    **kwargs,nominal_gem_source=nominal)
                j=result["physical_gem_J_arithmetic_unadmitted"]
                self.assertEqual(j["J_candidate_unadmitted"],92)
                self.assertEqual(j["rating_origin"],
                                 "SEASON_NOMINAL_PER_ITEM_TOTAL_SOURCE")
                self.assertEqual(j["nominal_source_sha256"],"9"*64)
                self.assertFalse(j["v266_effect_points_numeric_required"])
                self.assertFalse(j["quality_and_official_admission_verified"])
                self.assertIsNone(result["J"])
                self.assertFalse(result["environment_ready"])
                self.assertEqual((result["native_calls"],
                                  result["network_calls"]),(0,0))
                bad=dict(nominal,game_build="12.1.5.NOT_THIS_BUILD")
                with self.assertRaisesRegex(
                        build.EnvironmentBuildBlocked,
                        "SOCKET_NOMINAL_J_SAME_BUILD_SOURCE_IDENTITY_REQUIRED"):
                    build.preflight_new_season_source(
                        **kwargs,nominal_gem_source=bad)

    def test_p3_hk_quality_scope_nominal_pinned_rank_not_simc_effect_gate(self):
        import v216_environment_build_coordinator as engine
        from tests.test_v264_environment_standard_budget_integration import prepared
        catalog,_,_=prepared()
        # Reuse the same source shape rather than manufacture an effect
        # certificate or a new simulated season budget.
        build="12.1.5.70783"
        nominal=__import__("v271_user_socket_gem_layout").load_packaged_season_nominal_source(
            game_build=build,need=engine.need)
        selected=__import__("v271_user_socket_gem_layout").nominal_four_stat_from_season_source(
            source=nominal,game_build=build,
            socket_total=5,special_gem_id=240967,need=engine.need)
        ids=selected["ordinary_gem_ids"]
        all_ids=sorted(set(ids+[240967]))
        quality={"quality_source_authenticated":True,
                 "v230_stage_receipt_sha256":"c"*64,
                 "game_build":build,
                 "simc_revision":catalog["simc_revision"],
                 "selected_item_ids":all_ids,
                 "selected_item_quality_unadmitted":[
                    {"item_id":i,"crafting_quality":2} for i in all_ids]}
        comparison={
            "schema":"v216_selected_gem_quality_policy_A_preview_v1",
            "game_build":build,"simc_revision":catalog["simc_revision"],
            "quality_source_groups_unadmitted":[]}
        pre={"game_build":build,
             "simc_revision":catalog["simc_revision"],
             "selected_v221_gem_item_relation_unadmitted":{
                 "selected_item_ids":all_ids,
                 "v221_stage_receipt_sha256":"b"*64,
                 "selected_simc_gem_quality_source_unadmitted":quality,
                 "gem_policy_A_source_and_quality_unadmitted":comparison}}
        j={"ordinary_gem_item_ids":ids,
           "observed_quality_rank_by_id":
               nominal["observed_quality_rank_by_id"],
           "season_nominal_source_sha256":nominal["source_sha256"],
           "numeric_source_owner":"PACKAGED_SEASON_NOMINAL_PER_ITEM"}
        owner={"J":j,"F":None}
        q=engine._fresh_source_owner_observed_J_F_quality(
            preflight=pre,compilation={"simc_revision":catalog["simc_revision"]},
            owner_numeric=owner)
        self.assertTrue(q["J"]["selected_nominal_quality_matches_v230"])
        self.assertFalse(q["environment_ready"])
        low=copy.deepcopy(pre)
        low["selected_v221_gem_item_relation_unadmitted"][
            "selected_simc_gem_quality_source_unadmitted"][
                "selected_item_quality_unadmitted"][1]["crafting_quality"]=1
        q2=engine._fresh_source_owner_observed_J_F_quality(
            preflight=low,
            compilation={"simc_revision":catalog["simc_revision"]},
            owner_numeric=owner)
        self.assertFalse(q2["J"]["selected_nominal_quality_matches_v230"])
    def test_physical_four_colors_reconcile_existing_J_B_T(self):
        layout,ratings=stage()
        _,table,_=prepared()
        for row in table.values():
            row["components"]["J"]["rating"]=92
        result=self.preflight(table=table,layout=layout,ratings=ratings)
        j=result["physical_gem_J_arithmetic_unadmitted"]
        self.assertEqual(j["physical_gem_item_ids"],layout["ordinary_gem_ids"])
        self.assertEqual(j["J_candidate_unadmitted"],92)
        b=result["proposed_budget_arithmetic_unadmitted"]
        self.assertEqual((b["J"],b["base_B"],b["final_T"]),(92,3107,3139))
        self.assertIsNone(result["J"])
        self.assertFalse(result["environment_ready"])
        self.assertFalse(j["source_quality_and_applicability_authenticated_here"])
        self.assertEqual((result["native_calls"],result["network_calls"]),(0,0))
        manual=self.preflight(table=table,layout=layout,ratings=ratings,manual=3300)
        self.assertEqual(manual["proposed_budget_arithmetic_unadmitted"]["base_B"],3268)
        self.assertEqual(manual["proposed_budget_arithmetic_unadmitted"]["final_T"],3300)

    def test_layout_only_remains_pending(self):
        layout,_=stage()
        result=self.preflight(layout=layout)
        self.assertIn("PHYSICAL_GEM_ITEM_BY_ID_CHMV_RATING_SOURCE_PENDING",
                      result["requires"])
        self.assertNotIn("physical_gem_J_arithmetic_unadmitted",result)
        self.assertNotIn("proposed_budget_arithmetic_unadmitted",result)

    def test_missing_per_id_proof_mismatch_and_layout_drift_block(self):
        layout,ratings=stage()
        _,table,_=prepared()
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                    "DISAGREES_WITH_PHYSICAL_GEM_IDS"):
            self.preflight(table=table,layout=layout,ratings=ratings)
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                    "EXACT_PHYSICAL_ITEM_RATINGS_REQUIRED"):
            self.preflight(layout=layout,ratings={"240908":23})
        altered=copy.deepcopy(layout)
        altered["ordinary_count"]=5
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                    "LAYOUT_COUNTS_OR_IDS_DRIFT"):
            self.preflight(layout=altered,ratings=ratings)
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                    "LAYOUT_REQUIRED_BEFORE_RATING"):
            self.preflight(ratings=ratings)
        for row in table.values():
            row["components"]["J"]["rating"]=92
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                    "PHYSICAL_ID_RATING_LINK_MISSING"):
            self.preflight(table=table,layout=layout)

    def test_normal_build_uses_profile_receipt_and_existing_preflight(self):
        layout,ratings=stage()
        catalog,table,_=prepared()
        proof=copy.deepcopy(table[334])
        proof["components"]["J"]["rating"]=92
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            source=root/"v213.json"
            source.write_text("{}",encoding="utf8")
            user={"target":{"ilevel":334,"final_T":3300}}
            with mock.patch.object(build.environment_manifest,"read_json",
                                   return_value=(catalog,"a"*64)), \
                 mock.patch.object(build,"preflight_new_season_source",
                                   return_value={"preflight_sha256":"9"*64}) as pf:
                with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                            "GJFO_NOT_READY"):
                    build.build_environment(
                        sessions_root=root/"sessions",
                        session_folder=root/"sessions"/("0"*20),
                        user=user,binary=root/"simc",revision=catalog["simc_revision"],
                        static_cache=None,source_catalog_path=source,
                        bootstrap_result={},expected_new_season_build=catalog["game_build"],
                        profile_stage_receipt={"socket_layout":layout},
                        fresh_gem_rating_by_id=ratings,fresh_gjfo_evidence=proof)
            args=pf.call_args.kwargs
            self.assertIs(args["gem_layout_receipt"],layout)
            self.assertIs(args["gem_rating_by_id"],ratings)
            self.assertIs(args["budget_evidence"],proof)
            self.assertEqual(args["target_ilevel"],334)
            self.assertEqual(args["manual_final_T"],3300)
            self.assertFalse((root/"sessions").exists())


if __name__=="__main__":
    unittest.main()
