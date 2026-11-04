"""v096 unified single-manifest entry cross-archetype offline integration tests.

No SimC execution. Existing earlier Rogue/Shaman/Hunter/Fury/Paladin/Mage
Native evidence is historical and is NOT recast as new Native coverage.
"""
import copy,hashlib,json,pathlib,sys,tempfile,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v096_unified_product_entry as entry
import v216_environment_build_coordinator as env
import v082_fury_plate_dual_twohand_native as fury_module
import v084_frost_cloth_1h_frill_native as frost_module
from test_v091_weapon_oil_external_adapter import (
    fury,frost,FURY_TARGET,FROST_TARGET,REV)

class V096Unified(unittest.TestCase):
    def fixture(self,td,kind="fury"):
        p,c,fill=(fury(td) if kind=="fury" else frost(td))
        root=pathlib.Path(td)
        (root/"profile.simc").write_text(p,encoding="utf8")
        (root/"scenario.json").write_text(json.dumps(c),encoding="utf8")
        (root/"fillers.json").write_text(json.dumps(fill),encoding="utf8")
        fake=root/"dummy-no-native"
        fake.write_bytes(b"NO_SIMC_EXECUTION_PLAN_ONLY")
        target=FURY_TARGET if kind=="fury" else FROST_TARGET
        other=dict(target)
        other["crit_rating"]+=100
        other["haste_rating"]-=100
        document={"schema":entry.SCHEMA,
            "profile_simc":"profile.simc","scenario_json":"scenario.json",
            "fillers_json":"fillers.json","static_cache_json":None,
            "weapon_layout":"dual_two_hand" if kind=="fury" else "one_hand_frill",
            "oil_hands":["main_hand","off_hand"] if kind=="fury" else ["main_hand"],
            "flask_F":fury_module.DECLARED_F if kind=="fury" else frost_module.F_DECLARED,
            "seed_targets_B":[target,other],
            "native_binary":str(fake),"native_revision":REV,"output_dir":"output",
            "scouts":0,"material_scouts":0,"native_limit":4,"step":100,
            "cancel_file":None}
        manifest=root/"manifest.json"
        manifest.write_text(json.dumps(document),encoding="utf8")
        return manifest,document

    def seasonal_fixture(self, td):
        path,raw=self.fixture(td,"frost")
        source=path.parent/"scenario.json"
        cfg=json.loads(source.read_text("utf8"))
        cfg["target"]={
            "mode":"manual_total","ilevel":334,"manual_total":3150,
            "manual_total_scope":"INCLUDES_G_J_F"}
        import v061_scenario_contract as contract
        cfg["target"]["manual_total_scope"]=contract.MANUAL_TOTAL_SCOPE
        source.write_text(json.dumps(cfg),encoding="utf8")
        F=sum(raw["flask_F"].values())
        J=contract.normalize(cfg)["budget"]["J"]
        O={"crit_rating":16,"haste_rating":17,
           "mastery_rating":0,"versatility_rating":0}
        game_build="12.1.5.70575"
        source_manifest_sha="b"*64
        source_artifact_sha="c"*64
        season={
            "game_build":game_build,
            "simc_revision":raw["native_revision"],
            "source_catalog_manifest_sha256":source_manifest_sha,
            "source_catalog_artifact_sha256":source_artifact_sha,
            "target_ilevel":334,"base_B":3150,"final_T":3183,
            "fixed_O":dict(O),"fixed_L":{k:0 for k in O},
            "fixed_E":{k:0 for k in O},
            "J":J,"F":F,
            "source_links_verified_by_v223":True,
            "source_authentication_performed_here":False,
            "source_input_sha256":{
                "gear":"1"*64,"tier":"2"*64,
                "budget":"3"*64,"reference":"4"*64}}
        receipt={"schema":env.SCHEMA,"session_id":"a"*20,
                 "season_budget":season,
                 "source":{"game_build":game_build,
                           "simc_revision":raw["native_revision"],
                           "manifest_sha256":source_manifest_sha,
                           "artifact_sha256":source_artifact_sha},
                 "environment_manifest_sha256":"5"*64,
                 "native_calls":0,"network_calls":0,"cache_mutations":0,
                 "historical_sessions_preserved":True}
        receipt["receipt_sha256"]=env.digest(
            env.canonical(receipt).encode("utf8"))
        rp=path.parent/"environment_build_receipt.json"
        rp.write_text(json.dumps(receipt),encoding="utf8")
        raw[entry.SEASON_FIELD]={
            "schema":entry.SEASON_SCHEMA,
            "environment_receipt_path":rp.name,
            "environment_receipt_sha256":receipt["receipt_sha256"],
            "oil_by_hand":{"main_hand":{
                "physical_item_id":243734,
                "simc_input_token":
                    "main_hand:thalassian_phoenix_oil_2",
                "static_CHMV_vector":O}}}
        path.write_text(json.dumps(raw),encoding="utf8")
        return path,raw,receipt

    def test_same_build_v216_source_binds_seasonal_v096_v093_without_native(self):
        with tempfile.TemporaryDirectory() as td:
            path,raw,receipt=self.seasonal_fixture(td)
            ready=entry.source(path)
            plan=ready["plan"]
            self.assertEqual(plan["base_B"],3150)
            self.assertEqual(plan["final_T"],3183)
            self.assertEqual(plan["fixed_O"]["haste_rating"],17)
            self.assertEqual(plan["budget_source"],
                             "ADMITTED_SEASON_GJFO_V216_V223")
            self.assertEqual(plan["season_source_receipt_sha256"],
                             receipt["receipt_sha256"])
            self.assertEqual(plan["source_links_verified_by_v223"],True)
            self.assertTrue(plan["season_gjfo_source_is_NOT_policy_A_coverage"])
            self.assertFalse(plan["native_called"])
            self.assertEqual(ready["context"]["identity"][
                "admitted_season_environment_identity"][
                    "environment_build_receipt_sha256"],
                receipt["receipt_sha256"])
            self.assertIn(
                "temporary_enchant=main_hand:thalassian_phoenix_oil_2",
                ready["context"]["bundle"]["oil"]["profile"])
            self.assertEqual(ready["context"]["bundle"][
                "prepared"]["reference_source"],"user_manual_total")
            self.assertFalse((path.parent/"output").exists())
            self.assertEqual(entry.run_manifest(path,plan_only=True),plan)

    def test_seasonal_source_requires_v223_links_and_exact_rating(self):
        with tempfile.TemporaryDirectory() as td:
            path,raw,receipt=self.seasonal_fixture(td)
            def replace_receipt(change):
                doc=copy.deepcopy(receipt)
                change(doc)
                doc["receipt_sha256"]=env.digest(
                    env.canonical({k:v for k,v in doc.items()
                                   if k!="receipt_sha256"}).encode("utf8"))
                (path.parent/"environment_build_receipt.json").write_text(
                    json.dumps(doc),encoding="utf8")
                raw[entry.SEASON_FIELD][
                    "environment_receipt_sha256"]=doc["receipt_sha256"]
                path.write_text(json.dumps(raw),encoding="utf8")
            replace_receipt(lambda doc:doc["season_budget"].update({
                "source_links_verified_by_v223":False}))
            with self.assertRaisesRegex(entry.EntryBlocked,
                             "SEASON_V223_ACTUAL_SOURCE_LINKS_NOT_VERIFIED"):
                entry.run_manifest(path,plan_only=True)
            replace_receipt(lambda doc:doc["season_budget"].update({
                "source_links_verified_by_v223":True,
                "fixed_O":{"crit_rating":16,"haste_rating":16,
                           "mastery_rating":0,"versatility_rating":0}}))
            with self.assertRaisesRegex(entry.EntryBlocked,
                             "SEASON_V222_TYPED_GJFO_B_T_F_O_DRIFT"):
                entry.run_manifest(path,plan_only=True)
            self.assertFalse((path.parent/"output").exists())

    def test_seasonal_source_receipt_sha_drift_blocks_and_legacy_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            path,raw,receipt=self.seasonal_fixture(td)
            raw[entry.SEASON_FIELD]["environment_receipt_sha256"]="0"*64
            path.write_text(json.dumps(raw),encoding="utf8")
            with self.assertRaisesRegex(entry.EntryBlocked,
                            "SEASON_ENVIRONMENT_RECEIPT_IDENTITY_MISMATCH"):
                entry.run_manifest(path,plan_only=True)
            raw.pop(entry.SEASON_FIELD)
            path.write_text(json.dumps(raw),encoding="utf8")
            # No seasonal overlay: unchanged v096 legacy route still runs.
            cfg=path.parent/"scenario.json"
            obj=json.loads(cfg.read_text("utf8"))
            obj["target"]["mode"]="derived_ilevel"
            obj["target"].pop("manual_total",None)
            obj["target"].pop("manual_total_scope",None)
            cfg.write_text(json.dumps(obj),encoding="utf8")
            p=entry.run_manifest(path,plan_only=True)
            self.assertEqual(p["budget_source"],"OPT_IN_ILVL_REFERENCE_BASE_B")
            self.assertEqual(p["fixed_O"]["haste_rating"],16)
            self.assertFalse((path.parent/"output").exists())

    def test_fury_dual_twohand_source_bound_common_entry(self):
        with tempfile.TemporaryDirectory() as td:
            path,_=self.fixture(td)
            plan=entry.run_manifest(path,plan_only=True)
            self.assertEqual((plan["base_B"],plan["final_T"]),(3350,3414))
            self.assertEqual((plan["class"],plan["spec"]),("warrior","fury"))
            self.assertEqual(plan["fixed_O"]["crit_rating"],32)
            self.assertEqual(plan["item_slots"],16)
            self.assertFalse((pathlib.Path(td)/"output").exists())
            self.assertFalse(plan["native_called"])
    def test_frost_frill_source_bound_common_entry(self):
        with tempfile.TemporaryDirectory() as td:
            path,_=self.fixture(td,"frost")
            plan=entry.run_manifest(path,plan_only=True)
            self.assertEqual((plan["base_B"],plan["final_T"]),(3150,3182))
            self.assertEqual((plan["class"],plan["spec"]),("mage","frost"))
            self.assertEqual(plan["fixed_O"]["crit_rating"],16)
            self.assertEqual(plan["item_slots"],16)
            self.assertFalse(plan["native_called"])
    def test_native_call_budget_refuses_extra_scout_without_side_effects(self):
        with tempfile.TemporaryDirectory() as td:
            path,raw=self.fixture(td)
            raw["scouts"]=1
            path.write_text(json.dumps(raw),encoding="utf8")
            with self.assertRaisesRegex(entry.EntryBlocked,
                                        "SCENARIO_NATIVE_LIMIT_PRECHECK"):
                entry.run_manifest(path,plan_only=True)
            self.assertFalse((pathlib.Path(td)/"output").exists())
    def test_original_profile_sha_guard_rejects_modifications(self):
        with tempfile.TemporaryDirectory() as td:
            path,_=self.fixture(td)
            p=pathlib.Path(td)/"profile.simc"
            p.write_text(p.read_text()+"\n# changed\n",encoding="utf8")
            with self.assertRaisesRegex(Exception,"USER_SOURCE_PROFILE_SHA_MISMATCH"):
                entry.run_manifest(path,plan_only=True)
    def test_bad_fields_fail_before_file_or_native_access(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/"bad.json"
            p.write_text(json.dumps({"schema":entry.SCHEMA,"extra":True}))
            with self.assertRaisesRegex(entry.EntryBlocked,"ENTRY_SCHEMA_OR_FIELDS"):
                entry.run_manifest(p,plan_only=True)
if __name__=="__main__":unittest.main()
