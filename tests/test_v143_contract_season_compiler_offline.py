"""P1 stable contracts / replaceable season compiler, ZERO Native SimC."""
from __future__ import annotations
import copy
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v139_pure_target_profile_composer as pure
import v098_target_user_scenario_bootstrap as bootstrap
import v143_specialization_contracts as specs
from integration_probes.v140_pure_profile_physical_native_smoke import user_for

# Actual prior user Windows v140 physical receipt 'profile_sha256' values.
# These hash the final v098 profile.simc bytes (NOT V094 session source SHA).
# Both v140 physical trials PASS and their same inputs fed v141 adaptive Native.
# Evidence fingerprints are only test constants, never runtime templates.
VERIFIED_SOURCE_SHA={
    "druid/balance":"4dca36b5aad03e3cb8f7d0a3c2368c5c194e54c053224ca0c251de9ab8bfb5bc",
    "evoker/devastation":"14d951bd1b423a20dbf8e75cf5e8fd5e2ac654bd22aa5a7eb445dc1a583c192c",
}

class IndependentSeasonCompiler(unittest.TestCase):
    def test_contract_is_stable_and_season_records_contain_only_items(self):
        self.assertTrue(specs.validate_contracts())
        season=pure.catalog()
        self.assertEqual(set(season["specializations"]),set(specs.CONTRACTS))
        self.assertEqual(season["schema"],"v144_representative_season_items_v1")
        self.assertEqual(season["target_ilevel"],334)
        for key,item in season["specializations"].items():
            expected={"tier_ids","four_tier_slots","ordinary","weapons"}
            self.assertIn(set(item),(expected,expected|{"item_options"}))
            cl,sp=key.split("/")
            contract=specs.lookup(cl,sp)
            self.assertEqual(contract["simc_class"],cl)
            self.assertEqual(contract["simc_spec"],sp)
            self.assertNotIn("tier_ids",contract)
            self.assertNotIn("main_hand",contract)
        self.assertIsNone(specs.lookup("evoker","augmentation"))

    def test_import_and_two_pure_plans_without_any_legacy_full_profile_files(self):
        # Execute in a CLEAN Python process: tests in this main process
        # may already have memoized legacy registries. Block all attempted
        # reads of old complete .simc fixtures before importing the runner.
        script=textwrap.dedent(r"""
            import pathlib,sys,tempfile
            root=pathlib.Path(sys.argv[1])
            sys.path.insert(0,str(root/"runner"))
            original_text=pathlib.Path.read_text
            original_bytes=pathlib.Path.read_bytes
            attempted=[]
            def blocked(path):
                loc=str(path).replace(chr(92),"/")
                if "/integration_probes/fixtures/" in loc and loc.endswith(".simc"):
                    attempted.append(loc)
                    raise RuntimeError("LEGACY_COMPLETE_SIMC_PROFILE_REQUIRED:"+loc)
            def read_text(self,*args,**kwargs):
                blocked(self)
                return original_text(self,*args,**kwargs)
            def read_bytes(self,*args,**kwargs):
                blocked(self)
                return original_bytes(self,*args,**kwargs)
            pathlib.Path.read_text=read_text
            pathlib.Path.read_bytes=read_bytes
            import v098_target_user_scenario_bootstrap as boot
            import v101_common_representative_equipment as common
            from integration_probes.v140_pure_profile_physical_native_smoke import user_for
            assert len(boot.ARCHETYPES)==24
            assert len(common.FIFTH_TIER)==24
            assert not attempted
            with tempfile.TemporaryDirectory() as t:
                directory=pathlib.Path(t)
                binary=directory/"fake_simc"
                binary.write_bytes(b"NO_NATIVE")
                for key in ("druid/balance","evoker/devastation"):
                    user=user_for(key)
                    result=boot.build(user,directory/key.replace("/","_"),
                                      binary,"7bc10711b5")
                    assert result["status"]=="READY_INTERNAL_MANIFEST_ZERO_NATIVE"
                    assert result["native_calls"]==0
                    assert result["plan"]["item_slots"]==16
            assert not attempted, attempted
            # The other four are preview-only, but their common compiler
            # must likewise generate from character + catalog with zero
            # complete source-profile access. No legacy UI defaults here.
            import v139_pure_target_profile_composer as pure
            season_specs=pure.catalog()["specializations"]
            assert len(season_specs)==26
            preview_keys=set(season_specs)-{"druid/balance","evoker/devastation"}
            assert len(preview_keys)==24
            races={"deathknight":"human","demonhunter":"void_elf",
                   "druid":"night_elf","hunter":"dwarf",
                   "mage":"human","monk":"troll","paladin":"blood_elf",
                   "priest":"void_elf","rogue":"dwarf",
                   "shaman":"tauren","warlock":"orc","warrior":"dwarf"}
            for key in sorted(preview_keys):
                cl,sp=key.split("/")
                contract=pure.contracts.lookup(cl,sp)
                race=races[cl]
                slots=14+len(pure.contracts.WEAPON_FORMS[contract["weapon_form"]])
                user={"class":cl,"spec":sp,"race":race,
                      "talents":"CAAAABBB11122"}
                trinkets=[{"slot":slot,"item_id":item,"options":{}}
                          for slot,item in
                          (("trinket1",270175),("trinket2",270173))]
                profile,meta,rows,tier=pure.compose(user,trinkets)
                assert len(rows)==slots and len(tier)==4
                assert "default_actions=1" in profile
                assert meta["native_calls"]==0 and not meta["source_profile_read"]
            assert not attempted, attempted
            # Existing legacy source-backed path MUST still require its
            # checked fixture when actually selected.
            try:
                common.ARCHETYPES[("druid","feral")]
            except RuntimeError as exc:
                assert "LEGACY_COMPLETE_SIMC_PROFILE_REQUIRED" in str(exc)
            else:
                raise AssertionError("LEGACY_SOURCE_CHECK_BYPASSED")
            assert len(attempted)==1
            print("PURE_NO_FULL_SIMC_FIXTURE_IMPORT_OR_PLAN_PASS")
        """)
        result=subprocess.run([sys.executable,"-c",script,str(ROOT)],
                              capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn("PURE_NO_FULL_SIMC_FIXTURE_IMPORT_OR_PLAN_PASS",
                      result.stdout)

    def test_frost_mage_legacy_evidence_is_preview_only(self):
        # Existing source-backed default stays source-backed: no re-keying
        # of the 24 established Native/95% cache identities.
        import v106_user_session_controller as sessions
        controls=sessions.standard_controls(("mage","frost"))
        user=sessions.user_scenario(controls)
        self.assertIn(("mage","frost"),bootstrap.ARCHETYPES)
        self.assertNotIn(("mage","frost"),bootstrap.PURE_PRODUCT_SPECS)
        self.assertEqual(set(sessions.SUPPORTED),
                         set(bootstrap.ARCHETYPES)|bootstrap.PURE_PRODUCT_SPECS)
        # Source fixture may verify provenance, but the NEW pure generator
        # never opens the old completed source profile at runtime.
        from v102_ordinary_armor_seed_pool import FAMILY_ROWS
        cloth=FAMILY_ROWS["cloth"]
        cat=pure.catalog()["specializations"]["mage/frost"]
        for slot in ("wrists","waist","feet"):
            self.assertEqual(cat["ordinary"][slot],cloth[slot][1])
        self.assertEqual(cat["weapons"],
                         {"main_hand":271092,"off_hand":245769})
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            binary=root/"simc.mock"
            binary.write_bytes(b"OFFLINE_NO_SIMC_EXECUTABLE")
            folder=root/"frost_pure_stage"
            result=bootstrap.build(user,folder,binary,"7bc10711b5",
                                   pure_stage=True)
            self.assertEqual(result["status"],
                "STAGED_INTERNAL_MANIFEST_NATIVE_NOT_AUTHORIZED")
            self.assertEqual(result["native_calls"],0)
            self.assertFalse(result["user_optimizer_ready"])
            self.assertEqual(result["plan"]["item_slots"],16)
            self.assertEqual(result["plan"]["base_B"],3150)
            self.assertEqual(set(result["effective_four_tier_slots"]),
                             {"shoulders","chest","hands","legs"})
            rendered=(folder/"profile.simc").read_text()
            self.assertIn("default_actions=1\n",rendered)
            self.assertNotIn("actions.",rendered)
            with mock.patch.object(
                bootstrap.entry,"run_manifest") as native:
                with self.assertRaisesRegex(bootstrap.UserScenarioBlocked,
                                            "PURE_STAGE_NATIVE_NOT_AUTHORIZED"):
                    input_file=root/"user.json"
                    input_file.write_text(bootstrap.canonical(user)+"\n")
                    bootstrap.run(input_file,root/"no_native",
                                  binary,"7bc10711b5",execute=True,
                                  pure_stage=True)
                native.assert_not_called()

    def test_retribution_legacy_2h_stays_default_source_backed(self):
        import v106_user_session_controller as sessions
        controls=sessions.standard_controls(("paladin","retribution"))
        user=sessions.user_scenario(controls)
        self.assertIn(("paladin","retribution"),bootstrap.ARCHETYPES)
        self.assertNotIn(("paladin","retribution"),
                         bootstrap.PURE_PRODUCT_SPECS)
        self.assertEqual(controls["oil_hands"],["main_hand"])
        self.assertEqual(specs.lookup("paladin","retribution")["primary"],
                         "strength")
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            binary=root/"simc.mock"
            binary.write_bytes(b"OFFLINE_NO_NATIVE_SIMC")
            path=root/"ret_stage"
            result=bootstrap.build(user,path,binary,"7bc10711b5",
                                   pure_stage=True)
            self.assertEqual(result["status"],
                             "STAGED_INTERNAL_MANIFEST_NATIVE_NOT_AUTHORIZED")
            self.assertEqual(result["native_calls"],0)
            self.assertEqual(result["plan"]["item_slots"],15)
            self.assertEqual(len(result["effective_four_tier_slots"]),4)
            text=(path/"profile.simc").read_text()
            self.assertIn("role=attack\n",text)
            self.assertNotIn("off_hand=",text)
            self.assertIn("default_actions=1\n",text)
            self.assertNotIn("actions.",text)
            with mock.patch.object(bootstrap.entry,"run_manifest") as native:
                with self.assertRaisesRegex(bootstrap.UserScenarioBlocked,
                                            "PURE_STAGE_NATIVE_NOT_AUTHORIZED"):
                    input_file=root/"user.json"
                    input_file.write_text(bootstrap.canonical(user)+"\n")
                    bootstrap.run(input_file,root/"blocked",
                                  binary,"7bc10711b5",execute=True,
                                  pure_stage=True)
                native.assert_not_called()

    def test_fury_and_bm_pure_stage_preview_only_keep_legacy_default(self):
        import v106_user_session_controller as sessions
        trials=[
            (("warrior","fury"),16,"dual_two_hand",3350),
            (("hunter","beast_mastery"),15,"ranged",3150),
        ]
        for key,expected_slots,form,expected_B in trials:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as td:
                self.assertIn(key,bootstrap.ARCHETYPES)
                self.assertNotIn(key,bootstrap.PURE_PRODUCT_SPECS)
                controls=sessions.standard_controls(key)
                user=sessions.user_scenario(controls)
                binary=pathlib.Path(td)/"fake_simc"
                binary.write_bytes(b"NO_NATIVE")
                stage=pathlib.Path(td)/"only_preview"
                plan=bootstrap.build(user,stage,binary,"7bc10711b5",
                                     pure_stage=True)
                self.assertEqual(plan["status"],
                    "STAGED_INTERNAL_MANIFEST_NATIVE_NOT_AUTHORIZED")
                self.assertEqual(plan["native_calls"],0)
                self.assertFalse(plan["user_optimizer_ready"])
                self.assertEqual(plan["plan"]["item_slots"],expected_slots)
                self.assertEqual(plan["plan"]["base_B"],expected_B)
                self.assertEqual(plan["weapon_form"],form)
                profile=(stage/"profile.simc").read_text()
                self.assertIn("default_actions=1\n",profile)
                self.assertNotIn("actions.",profile)
                self.assertEqual(profile.count("main_hand="),1)
                self.assertEqual(profile.count("off_hand="),
                                 1 if expected_slots==16 else 0)
                self.assertEqual(len(plan["effective_four_tier_slots"]),4)
                with mock.patch.object(bootstrap.entry,"run_manifest") as native:
                    with self.assertRaisesRegex(bootstrap.UserScenarioBlocked,
                                                "PURE_STAGE_NATIVE_NOT_AUTHORIZED"):
                        input_file=pathlib.Path(td)/"user.json"
                        input_file.write_text(bootstrap.canonical(user)+"\n")
                        bootstrap.run(input_file,pathlib.Path(td)/"blocked",
                                      binary,"7bc10711b5",
                                      execute=True,pure_stage=True)
                    native.assert_not_called()

    def test_three_legacy_v104_shapes_have_source_free_stage_only(self):
        import v106_user_session_controller as sessions
        cases=(
            (("rogue","outlaw"),"dual_one_hand"),
            (("rogue","subtlety"),"dual_one_hand"),
            (("shaman","elemental"),"one_hand_shield"),
        )
        for key,form in cases:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as td:
                self.assertIn(key,bootstrap.ARCHETYPES)
                self.assertNotIn(key,bootstrap.PURE_PRODUCT_SPECS)
                controls=sessions.standard_controls(key)
                user=sessions.user_scenario(controls)
                binary=pathlib.Path(td)/"fake_simc"
                binary.write_bytes(b"NOT_NATIVE")
                folder=pathlib.Path(td)/"preview"
                report=bootstrap.build(user,folder,binary,"7bc10711b5",
                                       pure_stage=True)
                self.assertEqual(report["status"],
                                 "STAGED_INTERNAL_MANIFEST_NATIVE_NOT_AUTHORIZED")
                self.assertEqual(report["native_calls"],0)
                self.assertFalse(report["user_optimizer_ready"])
                self.assertEqual(report["weapon_form"],form)
                self.assertEqual(report["plan"]["item_slots"],16)
                self.assertEqual(report["plan"]["base_B"],3150)
                self.assertEqual(len(report["effective_four_tier_slots"]),4)
                rendered=(folder/"profile.simc").read_text()
                self.assertEqual(rendered.count("main_hand="),1)
                self.assertEqual(rendered.count("off_hand="),1)
                self.assertIn("default_actions=1\n",rendered)
                self.assertNotIn("actions.",rendered)
                with mock.patch.object(bootstrap.entry,"run_manifest") as native:
                    with self.assertRaisesRegex(bootstrap.UserScenarioBlocked,
                                               "PURE_STAGE_NATIVE_NOT_AUTHORIZED"):
                        inp=pathlib.Path(td)/"user.json"
                        inp.write_text(bootstrap.canonical(user)+"\n")
                        bootstrap.run(inp,pathlib.Path(td)/"blocked",
                                      binary,"7bc10711b5",execute=True,
                                      pure_stage=True)
                    native.assert_not_called()

    def test_six_cloth_source_backed_defaults_stay_legacy_and_pure_stage_zero_native(self):
        import v106_user_session_controller as sessions
        specs=(
            ("mage","arcane"),("mage","fire"),("priest","shadow"),
            ("warlock","affliction"),("warlock","demonology"),
            ("warlock","destruction"),
        )
        for key in specs:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as td:
                self.assertIn(key,bootstrap.ARCHETYPES)
                self.assertNotIn(key,bootstrap.PURE_PRODUCT_SPECS)
                controls=sessions.standard_controls(key)
                user=sessions.user_scenario(controls)
                binary=pathlib.Path(td)/"fake_simc"
                binary.write_bytes(b"NO_NATIVE")
                folder=pathlib.Path(td)/"preview"
                result=bootstrap.build(user,folder,binary,"7bc10711b5",
                                       pure_stage=True)
                self.assertEqual(result["status"],
                    "STAGED_INTERNAL_MANIFEST_NATIVE_NOT_AUTHORIZED")
                self.assertEqual(result["native_calls"],0)
                self.assertFalse(result["user_optimizer_ready"])
                self.assertEqual(result["plan"]["item_slots"],16)
                self.assertEqual(result["plan"]["base_B"],3150)
                self.assertEqual(result["weapon_form"],"one_hand_frill")
                self.assertEqual(len(result["effective_four_tier_slots"]),4)
                profile=(folder/"profile.simc").read_text()
                self.assertIn("default_actions=1\n",profile)
                self.assertNotIn("actions.",profile)
                self.assertEqual(profile.count("main_hand="),1)
                self.assertEqual(profile.count("off_hand="),1)

    def test_last_eleven_catalog_ids_match_pinned_source_witnesses(self):
        # Focused provenance comparison of the newly migrated 11 records.
        # This is a TEST-ONLY read of historical exact Git-pinned fixtures.
        # No fixture becomes a production profile-generator dependency.
        import v132_dps_source_batch_smoke as witness
        import v133_mid2_target_representative_preview as reference
        import v102_ordinary_armor_seed_pool as ordinary
        from v086_hunter_fixed_mail_representative import REPLACEMENTS
        migrated={
            "deathknight/frost","deathknight/unholy",
            "demonhunter/devourer","demonhunter/havoc",
            "druid/feral","hunter/marksmanship","hunter/survival",
            "monk/windwalker","rogue/assassination",
            "shaman/enhancement","warrior/arms"}
        self.assertEqual(len(migrated),11)
        season=pure.catalog()
        self.assertEqual(set(season["specializations"]),
                         set(witness.NEW)|{
                           "druid/balance","evoker/devastation",
                           "warrior/fury","paladin/retribution",
                           "mage/frost","hunter/beast_mastery",
                           "rogue/outlaw","rogue/subtlety",
                           "shaman/elemental"})
        for key in sorted(migrated):
            with self.subTest(key=key):
                cl,sp=key.split("/")
                record=witness.validate_source(key)
                source=record["source"]
                data=season["specializations"][key]
                contract=specs.lookup(cl,sp)
                expected_tiers=dict(zip(reference.FIVE,
                                         reference.FIVE_TIER[cl]))
                self.assertEqual(data["tier_ids"],expected_tiers)
                for name in ("spec","role","position"):
                    match=re.findall(r"^"+name+r"=(.+)$",source,re.M)
                    self.assertEqual(len(match),1)
                    self.assertEqual(match[0],contract[
                        "simc_spec" if name=="spec" else name])
                source_weapons={}
                offhand_crafted=None
                for line in source.splitlines():
                    slot,sep,val=line.partition("=")
                    if not sep or slot not in ("main_hand","off_hand"):
                        continue
                    id_match=re.search(r"(?:^|,)id=(\\d+)(?:,|$)",val)
                    self.assertIsNotNone(id_match)
                    source_weapons[slot]=int(id_match.group(1))
                    if slot=="off_hand":
                        crafted=re.search(
                            r"(?:^|,)crafted_stats=(\\d+/\\d+)(?:,|$)",val)
                        if crafted:offhand_crafted=crafted.group(1)
                self.assertEqual(data["weapons"],source_weapons)
                self.assertEqual(set(data["weapons"]),
                                 set(specs.WEAPON_FORMS[contract["weapon_form"]]))
                opts=data.get("item_options",{}).get("off_hand",{})
                self.assertEqual(opts.get("crafted_stats"),offhand_crafted)
                family=contract["family"]
                fifth={"plate":"legs","leather":"chest","mail":"head"}[family]
                self.assertEqual(set(data["four_tier_slots"]),
                                 set(specs.TIER_SLOTS)-{fifth})
                if fifth=="legs":self.assertEqual(
                    data["ordinary"]["legs"],271878)
                if fifth=="chest":self.assertEqual(
                    data["ordinary"]["chest"],
                    ordinary.FAMILY_ROWS["leather"]["chest"][1])
                if fifth=="head":self.assertEqual(
                    data["ordinary"]["head"],REPLACEMENTS["head"][1])
                for slot in ("wrists","waist","feet"):
                    expected=(REPLACEMENTS["feet"][1]
                        if family=="mail" and slot=="feet"
                        else ordinary.FAMILY_ROWS[family][slot][1])
                    self.assertEqual(data["ordinary"][slot],expected)

    def test_last_eleven_native_blocked_legacy_runs_still_selected(self):
        import v106_user_session_controller as sessions
        cases={
            ("deathknight","frost"),("deathknight","unholy"),
            ("demonhunter","devourer"),("demonhunter","havoc"),
            ("druid","feral"),("hunter","marksmanship"),
            ("hunter","survival"),("monk","windwalker"),
            ("rogue","assassination"),("shaman","enhancement"),
            ("warrior","arms")}
        self.assertEqual(len(cases),11)
        for key in sorted(cases):
            with self.subTest(key=key),tempfile.TemporaryDirectory() as td:
                self.assertIn(key,bootstrap.ARCHETYPES)
                self.assertNotIn(key,bootstrap.PURE_PRODUCT_SPECS)
                controls=sessions.standard_controls(key)
                user=sessions.user_scenario(controls)
                binary=pathlib.Path(td)/"simc_placeholder"
                binary.write_bytes(b"NO_SIMC_NATIVE")
                folder=pathlib.Path(td)/"stage"
                report=bootstrap.build(user,folder,binary,"7bc10711b5",
                                       pure_stage=True)
                self.assertEqual(report["status"],
                    "STAGED_INTERNAL_MANIFEST_NATIVE_NOT_AUTHORIZED")
                self.assertEqual(report["native_calls"],0)
                self.assertFalse(report["user_optimizer_ready"])
                self.assertEqual(report["plan"]["base_B"],3150)
                self.assertEqual(len(report["effective_four_tier_slots"]),4)
                form=pure.contracts.lookup(*key)["weapon_form"]
                self.assertEqual(report["weapon_form"],form)
                self.assertEqual(report["plan"]["item_slots"],
                    14+len(pure.contracts.WEAPON_FORMS[form]))
                profile=(folder/"profile.simc").read_text()
                self.assertIn("default_actions=1\n",profile)
                self.assertNotIn("actions.",profile)
                self.assertEqual(profile.count("main_hand="),1)
                self.assertEqual(profile.count("off_hand="),
                    1 if "off_hand" in pure.contracts.WEAPON_FORMS[form] else 0)
                with mock.patch.object(bootstrap.entry,"run_manifest") as run:
                    with self.assertRaisesRegex(bootstrap.UserScenarioBlocked,
                                                "PURE_STAGE_NATIVE_NOT_AUTHORIZED"):
                        user_file=pathlib.Path(td)/"user.json"
                        user_file.write_text(bootstrap.canonical(user)+"\n")
                        bootstrap.run(user_file,pathlib.Path(td)/"blocked",
                                      binary,"7bc10711b5",execute=True,
                                      pure_stage=True)
                    run.assert_not_called()

    def test_season_item_option_can_not_override_existing_gem(self):
        actor={"class":"warrior","spec":"fury","race":"dwarf",
               "talents":"CAAAABBB11122"}
        trinkets=[{"slot":s,"item_id":i,"options":{}}
                  for s,i in (("trinket1",270175),("trinket2",270173))]
        broken=copy.deepcopy(pure.catalog())
        broken["specializations"]["warrior/fury"]["item_options"]["head"]={
            "gem_id":"240900"}
        with self.assertRaisesRegex(pure.ProfileStageBlocked,
                                    "SEASON_ITEM_OPTIONS_INVALID_OR_DUPLICATED"):
            pure.compose(actor,trinkets,season=broken)

    def test_no_rewrite_of_native_proven_source_profile_bytes(self):
        for key,sha in VERIFIED_SOURCE_SHA.items():
            with self.subTest(key=key):
                user=user_for(key)
                text,meta,rows,tier=pure.compose(
                    user["character"],user["trinkets"],
                    target_ilevel=334,combat=user["combat"])
                self.assertEqual(meta["native_calls"],0)
                self.assertFalse(meta["source_profile_read"])
                self.assertEqual(len(tier),4)
                self.assertEqual(len(rows),16)
                # The real Native identity hashes the FINAL v098 emitter
                # output (including validated selected gear/consumables),
                # not v139's intermediate string.
                with tempfile.TemporaryDirectory() as td:
                    root=pathlib.Path(td)
                    binary=root/"simc.mock"
                    binary.write_bytes(b"OFFLINE_NO_NATIVE_SIMC")
                    folder=root/"stage"
                    result=bootstrap.build(user,folder,binary,"7bc10711b5",
                                           pure_stage=True)
                    self.assertEqual(result["native_calls"],0)
                    profile=(folder/"profile.simc").read_bytes()
                    self.assertEqual(hashlib.sha256(profile).hexdigest(),sha)
                    cfg=json.loads((folder/"scenario.json").read_text())
                    self.assertEqual(cfg["source"]["profile_sha256"],sha)

    def test_only_season_data_changes_for_future_season_mock(self):
        user=user_for("druid/balance")
        base=pure.catalog()
        future=copy.deepcopy(base)
        future["season"]="future_mock_not_real_items"
        future["target_ilevel"]=345
        future["character_level"]=91
        future["specializations"]["druid/balance"]["ordinary"]["feet"]=123456
        future["default_consumables"]["food"]="disabled"
        before=copy.deepcopy(specs.CONTRACTS)
        text,meta,rows,_=pure.compose(
            user["character"],user["trinkets"],
            target_ilevel=345,combat=user["combat"],season=future)
        self.assertEqual(specs.CONTRACTS,before)
        self.assertEqual(meta["season"],"future_mock_not_real_items")
        self.assertEqual(rows["feet"]["item_id"],123456)
        self.assertEqual(rows["feet"]["ilevel"],345)
        self.assertIn("food=disabled\n",text)
        self.assertIn("level=91\n",text)
        self.assertIn("default_actions=1\n",text)
        # A synthetic future item is not evidence of accepted real SimC IDs.
        self.assertFalse(meta["user_optimizer_ready"])

    def test_bad_contract_in_season_cannot_silently_become_runtime_code(self):
        season=pure.catalog()
        user=user_for("druid/balance")
        for bad in ("family","role","primary","weapon_form","simc_class"):
            with self.subTest(field=bad):
                changed=copy.deepcopy(season)
                changed["specializations"]["druid/balance"][bad]="incorrect"
                with self.assertRaisesRegex(pure.ProfileStageBlocked,
                       "SEASON_CONTAINS_STABLE_CONTRACT_FIELDS"):
                    pure.compose(user["character"],user["trinkets"],
                                 season=changed,combat=user["combat"])
        missing=copy.deepcopy(season)
        missing["specializations"]["evoker/augmentation"]={
            "tier_ids":{},"four_tier_slots":[],
            "ordinary":{},"weapons":{}}
        with self.assertRaisesRegex(pure.ProfileStageBlocked,
                                   "SEASON_SPEC_HAS_NO_STABLE_CONTRACT"):
            pure.compose(user["character"],user["trinkets"],season=missing)

if __name__=="__main__":
    unittest.main()
