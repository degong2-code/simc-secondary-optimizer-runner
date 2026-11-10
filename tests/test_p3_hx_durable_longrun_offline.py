"""v291 long-run control and source binding, offline only.

Native and oil acceptance are synthetic fakes; they are not SimC evidence.
"""
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v291_durable_multiscale_native_runner as runner
from test_v094_durable_inclusive_adaptive_runner import V094Durable

F={"crit_rating":0,"haste_rating":165,"mastery_rating":0,"versatility_rating":0}


def fake_native(req,calibration,binary,folder,progress,*,
                cache_only=False,cancel_file=None,
                recover_verified_partial=False):
    folder=pathlib.Path(folder)
    source=folder/"input.simc"
    native=folder/"result.json"
    receipt=folder/"native_receipt.json"
    if receipt.exists():
        assert source.read_bytes()==req["input"].encode()
        doc=json.loads(native.read_bytes())
        assert doc["case_key"]==req["case_key"]
        return {"case_key":req["case_key"],
                "native_json_sha256":hashlib.sha256(native.read_bytes()).hexdigest(),
                "source":"CACHED_VERIFIED_NATIVE"}
    if cache_only:
        raise ValueError("CACHE_ONLY_REFUSES_NEW_NATIVE")
    if progress["native_attempts"]:
        raise ValueError("PARTIAL_NATIVE_MUST_NOT_RETRY")
    folder.mkdir(parents=True,exist_ok=True)
    source.write_bytes(req["input"].encode())
    target=req["v092_base_target"]
    dps=185000.0-0.0009*sum((v-800)**2 for v in target.values())
    raw=json.dumps({"case_key":req["case_key"],"dps":dps},sort_keys=True).encode()
    native.write_bytes(raw)
    receipt.write_text(json.dumps({"case_key":req["case_key"]}))
    runner.atomic(folder.parent/"V065_PROGRESS.json",
                  {"native_attempts":1,"status":"RUNNING_NATIVE"})
    return {"case_key":req["case_key"],
            "native_json_sha256":hashlib.sha256(raw).hexdigest(),
            "source":"NEW_NATIVE"}


def fake_ingest(req,doc,raw):
    assert doc["case_key"]==req["case_key"]
    return {"case_key":req["case_key"],"native_json_sha256":hashlib.sha256(raw).hexdigest(),
            "dps_mean":doc["dps"],"dps_sem":300.0,
            "dps_samples":req["iterations"],
            "simc_seed":12345,"status":"PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT"}


class V291LongRun(unittest.TestCase):
    def fixture(self,folder,cap=6):
        from test_v091_weapon_oil_external_adapter import fury, REV
        import v091_weapon_oil_external_adapter as adapter
        import v093_inclusive_adaptive_scheduler_bridge as adaptive
        import v046_static_item_cache as static_cache
        p,c,f=fury(folder)
        c["runtime"]["max_native_calls"]=cap
        prepared=adapter.prepare(
            p,c,f,static_cache.empty_cache(),
            "dual_two_hand",["main_hand","off_hand"])
        binary=pathlib.Path(folder)/"dummy-simc"
        binary.write_bytes(b"synthetic test-only executable SHA")
        ctx=adaptive.prepare(
            prepared,hashlib.sha256(binary.read_bytes()).hexdigest(),REV,35,80)
        return ctx,binary,pathlib.Path(folder)/"longrun"

    def test_three_native_resume_exact_replay_zero_new_and_cancel(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=self.fixture(folder)
            with mock.patch.object(runner.engine,"execute_one",side_effect=fake_native), \
                 mock.patch.object(runner.oil,"ingest_native",side_effect=fake_ingest):
                first=runner.run(ctx,F,binary,out,max_native_calls=6,
                    max_new_native_this_invocation=3)
                self.assertEqual(first["completed_cases"],3)
                self.assertEqual(first["native_attempts_cumulative"],3)
                self.assertEqual(first["status"],"PAUSED_INVOCATION_NATIVE_BUDGET")
                self.assertEqual(first["new_native_this_invocation"],3)
                replay=runner.run(ctx,F,binary,out,max_native_calls=6,
                    max_new_native_this_invocation=0)
                self.assertEqual(replay["new_native_this_invocation"],0)
                self.assertEqual(replay["completed_cases"],3)
                stop=pathlib.Path(folder)/"CANCEL"
                stop.write_text("x")
                canceled=runner.run(ctx,F,binary,out,max_native_calls=6,cancel_file=stop)
                self.assertEqual(canceled["status"],"PAUSED_USER_CANCEL")
                stop.unlink()
                done=runner.run(ctx,F,binary,out,max_native_calls=6)
                self.assertEqual(done["status"],"BUDGET_EXHAUSTED")
                self.assertEqual(done["completed_cases"],6)
                self.assertEqual(done["native_attempts_cumulative"],6)
                again=runner.run(ctx,F,binary,out,max_native_calls=6)
                self.assertEqual(again["new_native_this_invocation"],0)
                self.assertEqual(again["completed_cases"],6)

    def test_experimental_percent_grid_opt_in_seal_and_resume(self):
        # Pure fake executor only; NO real SimC or new DPS evidence.
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=self.fixture(folder,cap=12)
            with mock.patch.object(runner.engine,"execute_one",
                                   side_effect=fake_native), \
                 mock.patch.object(runner.oil,"ingest_native",
                                   side_effect=fake_ingest):
                first=runner.run(ctx,F,binary,out,max_native_calls=12,
                    percentage_grid_points=11,max_new_native_this_invocation=4)
                self.assertEqual(first["completed_cases"],4)
                self.assertEqual(first["policy"],runner.percent_grid.SCHEMA)
                seal=runner.read_json(out/"V291_SESSION.json")
                self.assertEqual(seal["experimental_percent_grid"]["resolution"],11)
                self.assertTrue((out/"V298_NATIVE_TIMINGS.json").is_file())
                second=runner.run(ctx,F,binary,out,max_native_calls=12,
                    percentage_grid_points=11,max_new_native_this_invocation=0)
                self.assertEqual(second["new_native_this_invocation"],0)
                self.assertEqual(second["completed_cases"],4)
                with self.assertRaisesRegex(
                        runner.LongRunBlocked,"SEALED_SESSION_IDENTITY_DRIFT"):
                    runner.run(ctx,F,binary,out,max_native_calls=12,
                               percentage_grid_points=None,
                               max_new_native_this_invocation=0)
                with self.assertRaisesRegex(
                        runner.LongRunBlocked,"SEALED_SESSION_IDENTITY_DRIFT"):
                    runner.run(ctx,F,binary,out,max_native_calls=12,
                               percentage_grid_points=9,
                               max_new_native_this_invocation=0)
        # "auto" uses only actual NEW_NATIVE scouting durations; this
        # synthetic fake tests the plumbing, not real throughput thresholds.
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=self.fixture(folder,cap=12)
            with mock.patch.object(runner.engine,"execute_one",
                                   side_effect=fake_native), \
                 mock.patch.object(runner.oil,"ingest_native",
                                   side_effect=fake_ingest):
                first=runner.run(ctx,F,binary,out,max_native_calls=12,
                                 percentage_grid_points="auto",
                                 max_elapsed_seconds=300,
                                 max_new_native_this_invocation=5)
                self.assertEqual(first["completed_cases"],5)
                self.assertEqual(first["policy"],runner.percent_grid.SCHEMA)
                again=runner.run(ctx,F,binary,out,max_native_calls=12,
                                 percentage_grid_points="auto",
                                 max_elapsed_seconds=300,
                                 max_new_native_this_invocation=0)
                self.assertEqual(again["new_native_this_invocation"],0)

    def test_above_six_native_cases_with_typed_runtime_and_replay(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=self.fixture(folder,cap=12)
            with mock.patch.object(runner.engine,"execute_one",side_effect=fake_native), \
                 mock.patch.object(runner.oil,"ingest_native",side_effect=fake_ingest):
                result=runner.run(
                    ctx,F,binary,out,max_native_calls=12,
                    max_new_native_this_invocation=9)
                self.assertEqual(result["completed_cases"],9)
                self.assertEqual(result["native_attempts_cumulative"],9)
                self.assertEqual(result["status"],
                                 "PAUSED_INVOCATION_NATIVE_BUDGET")
                replay=runner.run(ctx,F,binary,out,
                                  max_native_calls=12,cache_only=True)
                self.assertEqual(replay["new_native_this_invocation"],0)
                self.assertEqual(replay["completed_cases"],9)
                self.assertEqual(replay["native_attempts_cumulative"],9)

    def test_short_typed_twelve_reaches_confirmed_pair_and_replays(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=self.fixture(folder,cap=12)
            with mock.patch.object(runner.engine,"execute_one",side_effect=fake_native), \
                 mock.patch.object(runner.oil,"ingest_native",side_effect=fake_ingest):
                first=runner.run(ctx,F,binary,out,max_native_calls=12,
                                 max_new_native_this_invocation=4)
                self.assertEqual(first["completed_cases"],4)
                second=runner.run(ctx,F,binary,out,max_native_calls=12,
                                  max_new_native_this_invocation=6)
                self.assertEqual(second["completed_cases"],10)
                rows=runner._load_journal(out/"V291_JOURNAL.jsonl")
                self.assertEqual([r["phase"] for r in rows[:8]],["scout"]*8)
                self.assertEqual([r["phase"] for r in rows[8:10]],
                                 ["precision"]*2)
                self.assertTrue(all(r["iterations"]==80 for r in rows[8:10]))
                pair=second["confirmed_selected_pair_95"]
                self.assertEqual(pair["comparison_scope"],
                                 "SELECTED_CONFIRMED_PAIR_ONLY")
                self.assertFalse(pair["distinct_simc_seeds_observed"])
                self.assertFalse(pair["pairwise_direction_supported"])
                replay=runner.run(ctx,F,binary,out,max_native_calls=12,
                                  max_new_native_this_invocation=0,
                                  cache_only=True)
                self.assertEqual(replay["new_native_this_invocation"],0)
                self.assertEqual(replay["confirmed_selected_pair_95"],pair)

    def test_exact_simc_seed_source_must_match_native_receipt(self):
        actual={"sim":{"options":{"seed":987654321}}}
        self.assertEqual(runner._source_seed(
            actual,{"simc_seed":987654321}),987654321)
        self.assertEqual(runner._source_seed(
            actual,{}),987654321)
        self.assertIsNone(runner._source_seed({},{}))
        with self.assertRaisesRegex(runner.LongRunBlocked,
                                    "SIMC_SEED_NATIVE_JSON_RECEIPT_DRIFT"):
            runner._source_seed(actual,{"simc_seed":123})
        with self.assertRaisesRegex(runner.LongRunBlocked,
                                    "SIMC_SEED_NATIVE_JSON_RECEIPT_DRIFT"):
            runner._source_seed({},{"simc_seed":987654321})

    def test_null_seed_legacy_journal_replays_only_after_exact_native_check(self):
        def seeded_native(req,calibration,binary,folder,progress,**kw):
            receipt=fake_native(req,calibration,binary,folder,progress,**kw)
            path=pathlib.Path(folder)/"result.json"
            doc=json.loads(path.read_bytes())
            if receipt["source"]=="NEW_NATIVE":
                doc["sim"]={"options":{"seed":int(req["case_key"][:12],16)}}
                raw=json.dumps(doc,sort_keys=True).encode()
                path.write_bytes(raw)
                receipt["native_json_sha256"]=hashlib.sha256(raw).hexdigest()
            receipt["simc_seed"]=doc["sim"]["options"]["seed"]
            return receipt
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=self.fixture(folder,cap=12)
            with mock.patch.object(runner.engine,"execute_one",
                                   side_effect=seeded_native), \
                 mock.patch.object(runner.oil,"ingest_native",
                                   side_effect=fake_ingest):
                first=runner.run(ctx,F,binary,out,max_native_calls=12,
                                 max_new_native_this_invocation=10)
                self.assertEqual(first["completed_cases"],10)
                self.assertTrue(first["confirmed_selected_pair_95"][
                    "distinct_simc_seeds_observed"])
                journal=out/"V291_JOURNAL.jsonl"
                # Simulate the earlier real v291 null-seed journal, retaining
                # every other exact Native target/iteration/SHA/source byte.
                old=[json.loads(x) for x in journal.read_text().splitlines()]
                for row in old:
                    row["simc_seed"]=None
                old_bytes=("".join(json.dumps(x,sort_keys=True,
                    separators=(",",":"),allow_nan=False)+"\n"
                    for x in old)).encode("utf8")
                journal.write_bytes(old_bytes)
                replay=runner.run(ctx,F,binary,out,max_native_calls=12,
                                  max_new_native_this_invocation=0,
                                  cache_only=True)
                self.assertEqual(replay["new_native_this_invocation"],0)
                self.assertTrue(replay["confirmed_selected_pair_95"][
                    "distinct_simc_seeds_observed"])
                self.assertEqual(journal.read_bytes(),old_bytes)
                # Metadata compatibility does not allow any other drift.
                old[0]["dps_mean"]=1.0
                journal.write_bytes(("".join(json.dumps(x,sort_keys=True,
                    separators=(",",":"),allow_nan=False)+"\n"
                    for x in old)).encode("utf8"))
                with self.assertRaisesRegex(runner.LongRunBlocked,
                                            "RECORDED_NATIVE_CASE_BYTES_OR_SUMMARY_DRIFT"):
                    runner.run(ctx,F,binary,out,max_native_calls=12,
                               cache_only=True)

    def test_selected_pair_95_checks_real_distinct_seeds(self):
        def make(target,dps,sem,seed,case):
            return {"phase":"precision","target":target,"iterations":320,
                    "dps_mean":dps,"dps_sem":sem,"simc_seed":seed,
                    "case_key":case}
        a=make({"crit_rating":1,"haste_rating":1552,
                "mastery_rating":1553,"versatility_rating":1},
               186000.,120.,11,"one")
        b=make({"crit_rating":736,"haste_rating":900,
                "mastery_rating":736,"versatility_rating":735},
               182000.,160.,22,"two")
        pair=runner.confirmed_selected_pair_95([a,b],320)
        self.assertTrue(pair["pairwise_direction_supported"])
        self.assertTrue(pair["multiplicity_and_winner_bias_not_corrected"])
        self.assertFalse(pair["global_optimum_proven"])

    def test_fail_closed_on_tampered_real_case_and_session(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=self.fixture(folder)
            with mock.patch.object(runner.engine,"execute_one",side_effect=fake_native), \
                 mock.patch.object(runner.oil,"ingest_native",side_effect=fake_ingest):
                runner.run(ctx,F,binary,out,max_native_calls=6,
                           max_new_native_this_invocation=2)
                with self.assertRaisesRegex(runner.LongRunBlocked,
                                             "SEALED_SESSION_IDENTITY_DRIFT"):
                    runner.run(ctx,F,binary,out,max_native_calls=5)
                path=runner.case_folder(out,0)/"result.json"
                doc=json.loads(path.read_text())
                doc["dps"]=1.0
                path.write_text(json.dumps(doc))
                with self.assertRaisesRegex(runner.LongRunBlocked,
                                             "RECORDED_NATIVE_CASE_BYTES_OR_SUMMARY_DRIFT"):
                    runner.run(ctx,F,binary,out,max_native_calls=6)

    def test_extended_source_budget_stages_separate_exact_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder)
            base=root/"original"
            base.mkdir()
            (base/"profile.simc").write_text("shaman=test\\n",encoding="utf8")
            (base/"fillers.json").write_text("[]",encoding="utf8")
            raw={"runtime":{"max_native_calls":6,"scout_iterations":35,
                            "confirm_iterations":320}}
            (base/"scenario.json").write_text(json.dumps(raw),encoding="utf8")
            (base/"manifest.json").write_text("{}",encoding="utf8")
            binary=root/"simc_fake";binary.write_bytes(b"test")
            paths={key:base/name for key,name in (
                ("profile_simc","profile.simc"),
                ("scenario_json","scenario.json"),
                ("fillers_json","fillers.json"))}
            paths.update({"native_binary":binary,"static_cache_json":None})
            plan={"base_B":3107,"fixed_O":{"crit_rating":0,"haste_rating":0,
                 "mastery_rating":0,"versatility_rating":0},
                 "final_T":3107,"source_profile_sha256":"a"*64,
                 "budget_source":"test_fixture","binary_sha256":"b"*64,
                 "scenario_digest":"1"*64}
            original={"paths":paths,"plan":plan,
                      "manifest":{"native_limit":6,"schema":"test"}}
            def admitted(path):
                candidate=json.loads(path.read_text())
                data=json.loads(path.with_name("scenario.json").read_text())
                self.assertEqual(candidate["native_binary"],str(binary))
                self.assertEqual(data["runtime"]["max_native_calls"],2000)
                return {"paths":{**paths,"output_dir":path.parent/"simc_results"},
                        "plan":{**plan,"scenario_digest":"2"*64},
                        "context":{"bundle":{"prepared":{"scenario":{
                            "scenario":{"runtime":data["runtime"]}}}}}}
            ready,path=runner.stage_extended_manifest(
                original,base/"manifest.json",2000,source_loader=admitted)
            self.assertTrue(path.is_file())
            self.assertEqual(ready["plan"]["scenario_digest"],"2"*64)
            self.assertEqual((base/"scenario.json").read_text(),json.dumps(raw))
            runner.stage_extended_manifest(
                original,base/"manifest.json",2000,source_loader=admitted)
            with self.assertRaisesRegex(runner.LongRunBlocked,
                                         "LONGRUN_STAGED_SESSION_SOURCE_DRIFT"):
                (path.parent/"profile.simc").write_text("tampered")
                runner.stage_extended_manifest(
                    original,base/"manifest.json",2000,source_loader=admitted)

    def test_cache_only_no_native_and_partial_attempt_refuses_repeat(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=self.fixture(folder)
            with mock.patch.object(runner.engine,"execute_one",side_effect=fake_native), \
                 mock.patch.object(runner.oil,"ingest_native",side_effect=fake_ingest):
                first=runner.run(ctx,F,binary,out,max_native_calls=6,
                                 cache_only=True)
                self.assertEqual(first["status"],"PAUSED_CACHE_ONLY")
                self.assertEqual(first["native_attempts_cumulative"],0)
                parent=runner.case_folder(out,0).parent
                runner.atomic(parent/"V065_PROGRESS.json",
                              {"native_attempts":1,"status":"RUNNING_NATIVE"})
                with self.assertRaisesRegex(runner.LongRunBlocked,
                                            "PARTIAL_NATIVE_NEEDS_EXPLICIT_RECOVERY"):
                    runner.run(ctx,F,binary,out,max_native_calls=6)
if __name__=="__main__":
    unittest.main()
