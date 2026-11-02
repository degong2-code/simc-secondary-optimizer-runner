"""v233/v234 controlled single physical SimC input and native JSON2 replay.

Tests use a fake process and synthetic SimC item data. They run ZERO real
SimulationCraft Native processes and cannot certify any season rating.
"""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from runner import v229_simc_only_source_seed as seed
from runner import v233_source_only_G_probe_profile as profile
from runner import v234_source_only_one_native_G as native
from tests.test_v232_simc_only_ordinary_representative import (
    SourceOnlyRepresentativeTests,make_fixture)


class SinglePhysicalNativeTests(unittest.TestCase):
    def setUp(self):
        self.fixture=SourceOnlyRepresentativeTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.temp.cleanup)
        self.folder=self.fixture.folder
        self.tier=self.fixture.tier
        self.representative=self.fixture.plan()
        self.race="human"
        self._profile()

    def _profile(self):
        self.text,self.prepared=profile.build(
            source_directory=self.folder,tier_candidate=self.tier,
            representative_candidate=self.representative,
            race=self.race,level=90,talents=None)

    def _fake_json2(self):
        gear={}
        for i,(slot,item_id) in enumerate(sorted(
                self.prepared["selected_G_slot_ids"].items())):
            value=f"simc_source_{item_id},id={item_id},ilevel="+str(
                self.prepared["target_ilevel"])+",source=local"
            gear[slot]={
                "encoded_item":value,
                "ilevel":self.prepared["target_ilevel"],
                "crit_rating":10+i,"haste_rating":3,
                "mastery_rating":2,"versatility_rating":1,
                "unknown":0}
        return {"report_version":"2.0.0",
                "git_revision":self.prepared["simc_revision"][:12],
                "sim":{"players":[{"gear":gear}]}}

    def _observe(self,doc):
        return native.observe(
            native_raw=json.dumps(doc).encode("utf8"),
            profile_receipt=self.prepared,
            native_binary_sha256="f"*64,
            executed_profile_sha256="e"*64)

    def test_generate_exact_bare_profile_in_source_order(self):
        self.assertTrue(self.text.startswith(
            "# v233 generated, SimC-only physical G measurement candidate\n"
            "paladin=simc_source_g_probe\n"
            "level=90\nrace=human\nspec=retribution\n"))
        self.assertIn(
            "head=simc_source_9001,id=9001,ilevel=335,source=local",
            self.text)
        self.assertEqual(self.text.count("source=local"),13)
        self.assertNotIn("gear_crit_rating",self.text)
        self.assertNotIn("flask=",self.text)
        self.assertNotIn("trinket",self.text)
        self.assertNotIn("temporary_enchant",self.text)
        self.assertEqual(self.prepared["native_calls"],0)
        self.assertIsNone(self.prepared["G"])
        self.assertFalse(self.prepared["environment_ready"])
        self.assertEqual(self.prepared["physical_profile_sha256"],
                         hashlib.sha256(self.text.encode()).hexdigest())

    def test_native_json2_exact_static_G_v046_reused(self):
        result=self._observe(self._fake_json2())
        self.assertEqual(result["matching_nontrinket_G_slots"],13)
        self.assertEqual(result["observed_G_total"],
                         sum(result["observed_G_vector"].values()))
        self.assertGreater(result["observed_G_total"],0)
        self.assertIsNone(result["G"])
        self.assertIsNone(result["B"])
        self.assertIsNone(result["T"])
        self.assertFalse(result["source_current_season_membership_verified"])
        self.assertFalse(result["native_compiled_game_build_independently_verified"])
        self.assertFalse(result["environment_ready"])
        self.assertTrue(result["existing_static_cache_modified"] is False)
        self.assertEqual(result["new_native_calls_by_observer"],0)

    def test_wrong_native_id_level_modifier_and_unknown_are_rejected(self):
        for variant in ("id","ilevel","modifier","unknown"):
            with self.subTest(variant=variant):
                doc=self._fake_json2()
                item=doc["sim"]["players"][0]["gear"]["head"]
                if variant=="id":
                    item["encoded_item"]=item["encoded_item"].replace(
                        "id=9001", "id=3333")
                elif variant=="ilevel":
                    item["ilevel"]=777
                elif variant=="modifier":
                    item["encoded_item"]+=",gem_id=22"
                else:item["unknown"]=99
                with self.assertRaises(native.PhysicalNativeBlocked):
                    self._observe(doc)

    def test_missing_extra_and_ambiguous_rings_blocked(self):
        for variant in ("missing","extra","ambiguous"):
            with self.subTest(variant=variant):
                doc=self._fake_json2()
                gear=doc["sim"]["players"][0]["gear"]
                if variant=="missing":gear.pop("head")
                elif variant=="extra":
                    gear["trinket1"]={
                        "encoded_item":"extra,id=4,ilevel=335,source=local",
                        "ilevel":335}
                else:gear["finger"]=gear.pop("finger1")
                with self.assertRaises(native.PhysicalNativeBlocked):
                    self._observe(doc)

    def test_simc_revision_must_be_same_pinned_source(self):
        doc=self._fake_json2()
        doc["git_revision"]="aabbccddeeff"
        with self.assertRaisesRegex(native.PhysicalNativeBlocked,
                                    "NATIVE_REVISION_NOT_SOURCE_PINNED"):
            self._observe(doc)

    def test_only_one_race_specialization_and_source_identity(self):
        with self.assertRaisesRegex(profile.ProbeBlocked,
                                    "RACE_INVALID_OR_UNSUPPORTED"):
            profile.build(source_directory=self.folder,
                tier_candidate=self.tier,
                representative_candidate=self.representative,
                race="human\ntrinket1=foo",level=90)
        edited=copy.deepcopy(self.representative)
        edited["selected_G_slot_ids"]["head"]=999
        with self.assertRaisesRegex(profile.ProbeBlocked,
                                    "SOURCE_CANDIDATE_INVALID_OR_CHANGED"):
            profile.build(source_directory=self.folder,
                tier_candidate=self.tier,
                representative_candidate=edited,race="human",level=90)
        edited["receipt_sha256"]=seed.digest(
            seed.canonical({k:v for k,v in edited.items()
                            if k!="receipt_sha256"}).encode())
        with self.assertRaisesRegex(profile.ProbeBlocked,
                                    "REPRESENTATIVE_SOURCE_CANDIDATE_REPLAY_DRIFT"):
            profile.build(source_directory=self.folder,
                tier_candidate=self.tier,
                representative_candidate=edited,race="human",level=90)

    def test_fury_two_2h_items_produce_14_native_profile_lines(self):
        self.fixture.seed_files(make_fixture(warrior=True),
                                cls="warrior",spec="fury")
        self.tier=self.fixture.tier
        self.representative=self.fixture.plan()
        self._profile()
        self.assertEqual(self.text.count("source=local"),14)
        self.assertIn("warrior=simc_source_g_probe",self.text)
        self.assertIn("off_hand=simc_source_9031,id=9031",self.text)
        self.assertEqual(self._observe(self._fake_json2())[
                         "matching_nontrinket_G_slots"],14)

    def test_plan_only_hash_binds_binary_and_input_without_native(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            binpath=root/"simc_dummy"
            binpath.write_bytes(b"fake binary never invoked")
            binarysha=hashlib.sha256(binpath.read_bytes()).hexdigest()
            out=root/"one_run"
            response=native.execute(
                source_directory=self.folder,tier_candidate=self.tier,
                representative_candidate=self.representative,
                race="human",level=90,talents=None,binary=binpath,
                expected_binary_sha256=binarysha,output_dir=out,
                max_new=0)
            self.assertEqual(response["status"],"PREPARED_NATIVE_NOT_EXECUTED")
            self.assertEqual(response["new_native_calls"],0)
            self.assertTrue((out/"native.simc").is_file())
            self.assertFalse((out/"native.json").exists())
            with self.assertRaisesRegex(native.PhysicalNativeBlocked,
                                        "ONE_RUN_OUTPUT_MUST_BE_NEW"):
                native.execute(
                    source_directory=self.folder,tier_candidate=self.tier,
                    representative_candidate=self.representative,
                    race="human",level=90,talents=None,binary=binpath,
                    expected_binary_sha256=binarysha,output_dir=out)
            with self.assertRaisesRegex(native.PhysicalNativeBlocked,
                                        "BINARY_BYTES_NOT_PINNED"):
                native.execute(
                    source_directory=self.folder,tier_candidate=self.tier,
                    representative_candidate=self.representative,
                    race="human",level=90,talents=None,binary=binpath,
                    expected_binary_sha256="0"*64,
                    output_dir=root/"bad_hash")

    def test_one_fake_process_invocation_preserves_exact_profile_and_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            binpath=root/"simc_dummy"
            binpath.write_bytes(b"fake runner")
            binarysha=hashlib.sha256(binpath.read_bytes()).hexdigest()
            calls=[]
            def fake_run(cmd,*,cwd,stdout,stderr,timeout,check):
                calls.append(cmd)
                physical=pathlib.Path(cmd[1]).read_text("utf8")
                self.assertIn("iterations=1",physical)
                self.assertIn("json2=",physical)
                self.assertEqual(len(cmd),2)
                (pathlib.Path(cwd)/"native.json").write_text(
                    json.dumps(self._fake_json2()))
                return SimpleNamespace(returncode=0)
            with patch.object(native.subprocess,"run",side_effect=fake_run):
                output=native.execute(
                    source_directory=self.folder,tier_candidate=self.tier,
                    representative_candidate=self.representative,
                    race="human",level=90,talents=None,binary=binpath,
                    expected_binary_sha256=binarysha,
                    output_dir=root/"run",max_new=1)
            self.assertEqual(len(calls),1)
            self.assertEqual(output["new_native_calls"],1)
            self.assertEqual(output["status"],
                "PASS_NATIVE_PHYSICAL_G_OBSERVED_NOT_SEASON_APPROVED")
            self.assertIsNone(output["G"])
            self.assertFalse(output["environment_ready"])
            self.assertEqual(json.loads((root/"run"/"receipt.json").read_text())[
                "identity"]["binary_sha256"],binarysha)

    def test_fake_nonzero_native_preserves_log_without_approval(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            exe=root/"simc_dummy"
            exe.write_bytes(b"fake runner")
            def fake_fail(cmd,*,cwd,stdout,stderr,timeout,check):
                stdout.write(b"ERROR SimC unsupported item id\n")
                return SimpleNamespace(returncode=42)
            with patch.object(native.subprocess,"run",side_effect=fake_fail):
                result=native.execute(
                    source_directory=self.folder,tier_candidate=self.tier,
                    representative_candidate=self.representative,
                    race="human",level=90,talents=None,binary=exe,
                    expected_binary_sha256=hashlib.sha256(
                        exe.read_bytes()).hexdigest(),
                    output_dir=root/"run",max_new=1)
            self.assertEqual(result["status"],"FAIL_NATIVE_EXIT")
            self.assertEqual(result["native_returncode"],42)
            self.assertEqual((root/"run"/"simc.log").read_text(),
                             "ERROR SimC unsupported item id\n")
            self.assertIsNone(result["observed_G"])
            self.assertIsNone(result["G"])


if __name__=="__main__":
    unittest.main()
