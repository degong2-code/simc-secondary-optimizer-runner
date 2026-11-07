"""P3-GW: declared SimC full sockets are independent of intrinsic counts."""
import copy,json,pathlib,sys,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"runner"))
import v271_user_socket_gem_layout as gems
import v216_environment_build_coordinator as env

class DeclaredFullSockets(unittest.TestCase):
    @staticmethod
    def need(ok,code):
        if not ok: raise ValueError(code)
    def setUp(self):
        self.ids={s:310000+i for i,s in enumerate(
            ("head","neck","finger1","finger2","wrists","waist",
             "feet","hands","legs","shoulders","chest","back"))}
        self.observed={stat:{"item_id":311001+i,"raw_nominal_points":40}
                       for i,stat in enumerate(gems.ORDINARY_FOUR_STATS)}
    def source_counts(self,n):
        return gems.declared_full_socket_counts(
            available_slots=list(self.ids),socket_total=n,need=self.need)
    def test_fixed_four_types_and_extra_rotation_for_5_7_8(self):
        for n in (5,7,8):
            with self.subTest(n=n):
                ids=gems.ordinary_four_stat_default(
                    observed_by_stat=self.observed,socket_total=n,
                    special_gem_id=311200,need=self.need)
                self.assertEqual(ids,[311001+(i%4) for i in range(n-1)])
                self.assertEqual(len(set(ids[:4])),4)
                layout=self.source_counts(n)
                self.assertEqual(sum(layout.values()),n)
                self.assertEqual(layout,gems.declared_full_socket_counts(
                    available_slots=list(reversed(list(self.ids))),
                    socket_total=n,need=self.need))
    def test_all_slots_filled_j_counts_only_ordinary_once(self):
        values={}
        for n in (5,7):
            ordinary=gems.ordinary_four_stat_default(
                observed_by_stat=self.observed,socket_total=n,
                special_gem_id=311200,need=self.need)
            plan=gems.intrinsic_source_plan(
                intrinsic_socket_counts=self.source_counts(n),
                special_gem_id=311200,ordinary_gem_ids=ordinary,
                source_observed_gem_item_ids=sorted(set(ordinary)|{311200}),
                need=self.need)
            original={s:{"slot":s,"item_id":id,"ilevel":334,"options":{}}
                      for s,id in self.ids.items()}
            rows,receipt=gems.arrange(original,plan,self.need)
            j=gems.reconcile_observed_J(
                receipt,{str(id):40 for id in set(ordinary)},self.need)
            self.assertEqual(receipt["ordinary_count"],n-1)
            self.assertEqual(receipt["socket_total"],n)
            self.assertEqual(sum(len(r["options"]["gem_id"].split("/"))
                for r in rows.values() if "gem_id" in r["options"]),n)
            self.assertEqual(j["J_candidate_unadmitted"],40*(n-1))
            self.assertIsNone(j.get("gear_rating_injected"))
            self.assertFalse(j["environment_ready"])
            values[n]=j["J_candidate_unadmitted"]
        self.assertEqual(values[7]-values[5],80)
    def test_zero_original_intrinsic_still_stages_seven_gems_no_new_native(self):
        original={s:0 for s in self.ids}
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp);(root/"source").mkdir()
            candidate={"schema":env.simc_representative.SCHEMA,
                       "game_build":"12.1.5.70783","target_ilevel":334,
                       "selected_G_slot_ids":self.ids,
                       "selected_intrinsic_socket_count_by_slot_source_only":original,
                       "environment_ready":False}
            candidate["receipt_sha256"]=env.simc_source.digest(
                env.simc_source.canonical(candidate).encode("utf8"))
            path=root/"source"/"v232.json"
            path.write_text(json.dumps(candidate),encoding="utf8")
            collected={"expected_game_build":"12.1.5.70783",
                "fresh_one_spec_simc_representative":{
                    "status":"FRESH_ONE_SPEC_SIMC_G_SOURCE_CANDIDATE_PENDING_NATIVE",
                    "candidate_path":str(path),
                    "source_stage":{"status":"EXECUTED_AND_SEALED",
                        "receipt_sha256":"f"*64,
                        "output_paths":{"candidate":"source/v232.json"}},
                    "selected_slot_count":len(original),
                    "intrinsic_socket_total_source_only":0,
                    "intrinsic_socket_counts_by_selected_slot_source_only":original,
                    "added_socket_bonus_and_game_permission_not_proven":True}}
            before=copy.deepcopy(collected)
            declared=self.source_counts(7)
            layout=env._fresh_default_intrinsic_gem_layout_from_source(
                collected=collected,
                selected_roles={"special_gem_id":311200,
                                "ordinary_gem_ids":[311001,311002,311003,
                                                    311004,311001,311002]},
                target_ilevel=334,simc_declared_socket_counts=declared)
            self.assertEqual(collected,before)
            self.assertEqual(layout["socket_total"],7)
            self.assertEqual(layout["ordinary_count"],6)
            self.assertEqual(layout["simc_declared_full_socket_policy"],
                             "FULL_GEM_ID_PROFILE_SIMC_OWNS")
            preflight={"schema":env.FRESH_SOURCE_PREFLIGHT_SCHEMA,
                       "game_build":"12.1.5.70783",
                       "simc_revision":"abc1234","environment_ready":False,
                       "physical_gem_layout_unadmitted":layout}
            linked=env._fresh_selected_J_intrinsic_socket_source(
                collected=collected,preflight=preflight,
                compilation={"simc_revision":"abc1234"})
            self.assertEqual(linked["status"],
                             "J_SIMC_DECLARED_FULL_GEM_PROFILE_SOURCE_ONLY")
            self.assertTrue(linked["additional_socket_proof_required_by_slot"])
            self.assertFalse(linked["J_approved"])
            self.assertEqual(linked["new_native_calls"],0)
    def test_unsupported_count_or_slot_does_not_get_fake_bonuses(self):
        for n in (0,4,65,True):
            with self.subTest(n=n),self.assertRaises(ValueError):
                self.source_counts(n)
        with self.assertRaises(ValueError):
            gems.declared_full_socket_counts(
                available_slots=["unknown"],socket_total=7,need=self.need)
if __name__=="__main__":
    unittest.main()
