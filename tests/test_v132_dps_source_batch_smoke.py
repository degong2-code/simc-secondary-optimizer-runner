"""P1 v132 bounded 17-source acceptance smoke, entirely OFFLINE tests (Native0)."""
from __future__ import annotations
import json,pathlib,sys,tempfile,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v132_dps_source_batch_smoke as batch

class SourceBatchSmoke(unittest.TestCase):
    def test_exact_17_source_blobs_and_dps_only_class_apl_and_full_gear(self):
        info=batch.scan()
        self.assertEqual(info["status"],"PASS_OFFLINE_SOURCE_INSPECTION")
        self.assertEqual(len(info["new_sources"]),17)
        self.assertEqual(info["new_source_count"]+len(info["already_source_connected"]),24)
        self.assertEqual(info["missing_mid2"],
            ["druid/balance","evoker/devastation","evoker/augmentation"])
        for item in info["new_sources"]:
            with self.subTest(spec=item["key"]):
                self.assertIn(item["slot_count"],(15,16))
                self.assertGreaterEqual(item["apl_lines"],10)
                self.assertTrue(item["git_blob"])
                self.assertTrue(item["race"])
                self.assertIn(item["role"],("attack","spell"))
        self.assertEqual(info["native_calls"],0)
        self.assertFalse(info["all_27_executable"])

    def test_input_serializer_preserves_apl_and_gear_and_sets_one_json2(self):
        rec=batch.validate_source("shaman/enhancement")
        with tempfile.TemporaryDirectory() as td:
            profile=batch.smoke_input(rec["source"],pathlib.Path(td)/"r.json",35)
            self.assertEqual([x for x in profile.splitlines()
                             if x.startswith("json2=")].__len__(),1)
            self.assertEqual(sum(x.startswith("iterations=")
                                 for x in profile.splitlines()),1)
            self.assertEqual(len(batch.scan()["new_sources"]),17)
            self.assertEqual([x for x in rec["source"].splitlines()
                              if x.startswith("actions")],
                             [x for x in profile.splitlines()
                              if x.startswith("actions")])
            for slot in rec["weapon_slots"]:
                self.assertEqual(
                    next(x for x in profile.splitlines() if x.startswith(slot+"=")),
                    next(x for x in rec["source"].splitlines() if x.startswith(slot+"=")))

    def test_mock_native_one_call_cache_digest_replay_and_deferred_resume(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td);bin=root/"fake_simc.exe"
            bin.write_bytes(b"NOT_A_REAL_SIMC")
            out=root/"output"
            launched=[]
            def fake_run(argv,**kw):
                path=pathlib.Path(argv[1])
                src=path.read_text("utf8")
                target=pathlib.Path(next(x.partition("=")[2] for x in
                                         src.splitlines() if x.startswith("json2=")))
                target.write_text(json.dumps(
                    {"sim":{"players":[{"name":"fake_offline_only"}]}}),encoding="utf8")
                launched.append(path)
                class Result:
                    returncode=0
                    stdout=b"synthetic test only"
                return Result()
            with mock.patch.object(batch.subprocess,"run",side_effect=fake_run):
                first=batch.run(bin,out,max_new=1)
                self.assertEqual(first["native_calls_this_run"],1)
                self.assertEqual(first["cases"][0]["status"],"PASS_NATIVE_SMOKE")
                self.assertEqual(first["cases"][1]["status"],"NOT_RUN_LIMIT")
                self.assertFalse((out/"deathknight__unholy"/"input.simc").exists())
                second=batch.run(bin,out,max_new=0)
                self.assertEqual(second["native_calls_this_run"],0)
                self.assertEqual(second["cases"][0]["status"],"CACHED_VERIFIED_NATIVE")
                self.assertEqual(len(launched),1)
                with self.assertRaisesRegex(batch.SmokeBlocked,"EXISTING_NATIVE_RESULT_DRIFT"):
                    (out/"deathknight__frost"/"result.json").write_text("{}")
                    batch.run(bin,out,max_new=0)

    def test_no_native_requires_a_real_binary_and_caps(self):
        with tempfile.TemporaryDirectory() as td:
            b=pathlib.Path(td)/"fake"
            with self.assertRaisesRegex(batch.SmokeBlocked,"SIMC_BINARY_NOT_FOUND"):
                batch.run(b,pathlib.Path(td)/"out")
            b.write_bytes(b"fake")
            with self.assertRaisesRegex(batch.SmokeBlocked,"INVALID_MAX_NEW"):
                batch.run(b,pathlib.Path(td)/"out",max_new=27)
            with self.assertRaisesRegex(batch.SmokeBlocked,"SMOKE_ITERATIONS_OUTSIDE_BOUNDS"):
                batch.smoke_input("druid=test",pathlib.Path(td)/"out.json",5000)

if __name__=="__main__":unittest.main()
