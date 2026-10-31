import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v212_environment_manifest as v212
import v216_environment_build_coordinator as v216


def sealed_manifest(*,dependency=None):
    payload={
        "schema":v212.SCHEMA,
        "status":"READY_WITH_LIMITATIONS",
        "source_catalog":{
            "artifact_sha256":"a"*64,
            "manifest_sha256":"b"*64,
            "game_build":"12.1.5.70575",
            "simc_revision":"c"*40,
            "v191":{"sha256":"d"*64,"sha256_by_input":{
                "gear":"1"*64,"tier":"2"*64,"budget":"3"*64}},
            "v211":{"sha256":"e"*64},
        },
        "approved_ui_catalog":{"normalized_sha256":"f"*64},
        "target_profile":{
            "normalized_result_sha256":"4"*64,
            "profile_files":{"profile.simc":{"sha256":"5"*64}},
            "static_cache":None,
            "profile_supplier_coverage_sha256":"6"*64,
        },
        "product_scope":{"profile_supplier_coverage":{
            "current_season_profile_supplier_count":26,
            "contract_count":26,
            "adaptive_native_evidence_complete":False}},
        "dependency_change":dependency or {
            "status":"INITIAL_ENVIRONMENT","changed_inputs":["v213_source_catalog"],
            "invalidated_components":["v098_profile","environment_manifest"],
            "cache_mutations":0,"native_calls":0},
        "readiness_limitations":["ALL_26_ADAPTIVE_PROFILE_NATIVE_ACCEPTANCE_NOT_COMPLETE"],
        "unresolved_dependencies":["ALL_26_ADAPTIVE_PROFILE_NATIVE_ACCEPTANCE"],
        "native_calls":0,"network_calls":0,
    }
    return {**payload,"manifest_sha256":
            v216.digest(v216.canonical(payload).encode("utf8"))}


def source_document(path):
    doc={"schema":"v213_current_season_source_to_catalog_v1",
         "manifest_sha256":"b"*64,"game_build":"12.1.5.70575",
         "simc_revision":"c"*40}
    path.write_text(json.dumps(doc),encoding="utf8")
    return doc


def make_receipt(session_id,scope,manifest_sha):
    payload={"schema":v216.SCHEMA,"session_id":session_id,
             "environment_scope_sha256":scope,
             "environment_manifest_sha256":manifest_sha,
             "native_calls":0,"network_calls":0,"cache_mutations":0,
             "historical_sessions_preserved":True}
    return {**payload,"receipt_sha256":
            v216.digest(v216.canonical(payload).encode("utf8"))}


class EnvironmentBuildCoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.binary=self.root/"simc.exe"
        self.binary.write_bytes(b"fake-binary-no-native")
        self.cache=self.root/"static-cache.json"
        self.cache.write_text("{}",encoding="utf8")
        self.user={"character":{"class":"paladin","spec":"retribution"},
                   "target":{"ilevel":334,"final_T":None}}
        self.revision="c"*40

    def test_scope_identity_groups_same_user_across_dependency_versions(self):
        first=v216.environment_scope_identity(self.user)
        same=v216.environment_scope_identity(dict(self.user))
        changed_user=v216.environment_scope_identity(
            self.user|{"combat":{"targets":2}})
        self.assertEqual(first["scope_sha256"],same["scope_sha256"])
        self.assertNotEqual(first["scope_sha256"],changed_user["scope_sha256"])

    def test_previous_environment_lookup_requires_valid_receipt_and_manifest(self):
        scope="a"*64
        prior=self.root/("1"*20)
        generated=prior/"generated"
        generated.mkdir(parents=True)
        manifest=sealed_manifest()
        (generated/"environment_manifest.json").write_text(
            json.dumps(manifest),encoding="utf8")
        receipt=make_receipt(prior.name,scope,manifest["manifest_sha256"])
        (generated/"environment_build_receipt.json").write_text(
            json.dumps(receipt),encoding="utf8")
        current=self.root/("2"*20)
        current.mkdir()
        found=v216.find_previous_environment(self.root,current,scope)
        self.assertEqual(found["session_id"],prior.name)
        self.assertEqual(found["manifest"]["manifest_sha256"],
                         manifest["manifest_sha256"])
        receipt["native_calls"]=1
        (generated/"environment_build_receipt.json").write_text(
            json.dumps(receipt),encoding="utf8")
        self.assertIsNone(v216.find_previous_environment(
            self.root,current,scope))

    def test_receipt_digest_and_side_effect_contract_fail_closed(self):
        receipt=make_receipt("1"*20,"a"*64,"b"*64)
        self.assertTrue(v216.verify_receipt(receipt))
        corrupted=dict(receipt,native_calls=1)
        with self.assertRaises(v216.EnvironmentBuildBlocked):
            v216.verify_receipt(corrupted)

    def test_build_is_incremental_reuses_same_manifest_and_preserves_cache(self):
        source=self.root/"source.json"
        source_document(source)
        session=self.root/("3"*20)
        session.mkdir()
        first=sealed_manifest()
        calls=[]
        def compile_paths(*args,**kwargs):
            calls.append(args[5] if len(args)>5 else None)
            return first
        with mock.patch.object(v216.environment_manifest,
                               "compile_from_paths",side_effect=compile_paths):
            result1=v216.build_environment(
                sessions_root=self.root,session_folder=session,user=self.user,
                binary=self.binary,revision=self.revision,static_cache=self.cache,
                source_catalog_path=source,bootstrap_result={"schema":"v098"},
            )
            result2=v216.build_environment(
                sessions_root=self.root,session_folder=session,user=self.user,
                binary=self.binary,revision=self.revision,static_cache=self.cache,
                source_catalog_path=source,bootstrap_result={"schema":"v098"},
            )
            result3=v216.build_environment(
                sessions_root=self.root,session_folder=session,user=self.user,
                binary=self.binary,revision=self.revision,static_cache=self.cache,
                source_catalog_path=source,bootstrap_result={"schema":"v098"},
            )
        self.assertFalse(result1["manifest_reused"])
        self.assertTrue(result2["manifest_reused"])
        self.assertTrue(result3["manifest_reused"])
        self.assertEqual(calls[0],None)
        self.assertIsNone(calls[1])
        self.assertEqual(result3["receipt"]["native_calls"],0)
        self.assertEqual(result3["receipt"]["network_calls"],0)
        self.assertEqual(result3["receipt"]["cache_mutations"],0)
        self.assertTrue(result3["receipt"]["historical_sessions_preserved"])
        self.assertTrue(result3["receipt"]["cache_reuse"]["static_item_cache_preserved"])
        self.assertTrue(v216.verify_receipt(json.loads(
            (session/"generated"/"environment_build_receipt.json")
            .read_text(encoding="utf8"))))


if __name__=="__main__":
    unittest.main()
