"""v106 user UI backend regression, all tests OFFLINE (never SimC Native)."""
import copy,json,pathlib,sys,tempfile,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as ux

def fake_native(hits=0):
    return {"schema":"v096_user_scenario_unified_entry_v1",
            "status":"PASS_BOUNDED_GENERIC_NATIVE_SEARCH_AND_CACHE",
            "result_path":"synthetic_not_a_native_receipt",
            "base_B":3150,"final_T":3182,
            "cache_hits_this_run":hits,"native_calls_cumulative":6,
            "user_result":{
                "confidence_level":0.95,"official_formula":"T=G+J+F+O",
                "base_B":3150,
                "fixed_O":{"crit_rating":16,"haste_rating":16,
                           "mastery_rating":0,"versatility_rating":0},
                "final_T":3182,
                "observed_first_choice":{
                    "absolute_rating_T":{"crit_rating":704,"haste_rating":804,
                                          "mastery_rating":787,"versatility_rating":887},
                    "base_rating_B":{"crit_rating":688,"haste_rating":788,
                                     "mastery_rating":787,"versatility_rating":887},
                    "percent_of_final_T":{"crit_rating":22.12,"haste_rating":25.27,
                                          "mastery_rating":24.73,"versatility_rating":27.88},
                    "observed_dps_mean":179171.785,
                    "simc_sem":275.80,
                    "rank_basis":"HIGHEST_OBSERVED_MEAN_NOT_GLOBAL_OPTIMUM"},
                "material_near_alternatives":[],
                "confirmation_pair_direction_supported_at_95":True,
                "global_optimum_proven":False}}

def synthetic_completed_cache(folder):
    """Offline-only six fake files; NOT observed SimC Native evidence."""
    p=ux.paths(folder);p["progress"].parent.mkdir(parents=True,exist_ok=True)
    p["progress"].write_text(json.dumps({
        "status":"PASS_BOUNDED_GENERIC_NATIVE_SEARCH_AND_CACHE",
        "completed_jobs":6,"planned_jobs":6,
        "new_native_attempts":6,"cache_verified_hits":0}))
    p["native_result"].write_text(json.dumps({
        "status":"PASS_BOUNDED_GENERIC_NATIVE_SEARCH_AND_CACHE"}))
    for k in range(6):
        sub=(p["native_result"].parent/
             ("confirmations" if k>=4 else "search")/("case_%02d"%k))
        sub.mkdir(parents=True)
        (sub/"result.json").write_text(json.dumps({"fake_case":k}))
        (sub/"native_receipt.json").write_text(json.dumps({"fake_case":k}))

class UserSessionControls(unittest.TestCase):
    def setUp(self):
        # The real Windows worker opens a successful result folder for users.
        # Offline fixtures live under TemporaryDirectory and disappear at
        # tearDown: letting Explorer open them races with cleanup and raises
        # "Location is not available" dialogs despite an OK unittest run.
        # Mock only the external GUI side effect; exercise the real worker,
        # result, cache, state and failure branches without a Native call.
        self.mock_folder_open=None
        if ux.os.name=="nt":
            patch=mock.patch.object(ux.os,"startfile")
            self.mock_folder_open=patch.start()
            self.addCleanup(patch.stop)

    def fixture(self):
        td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup)
        root=pathlib.Path(td.name);binary=root/"simc.fake"
        binary.write_bytes(b"FAKE_ONLY_NOT_SIMC")
        user=ux.user_scenario(ux.standard_controls())
        return root,binary,user

    def test_v596_generic_user_E0_syntax_not_authorization(self):
        source=ux.standard_controls(("hunter","survival"))
        for slot in ("finger1","finger2","head","chest","legs","feet"):
            with self.subTest(slot=slot):
                controls={**source,"enchant_choices":{slot:89999}}
                user=ux.user_scenario(controls)
                self.assertEqual(user["selected_season_enchants"],
                                 {slot:89999})
                self.assertNotIn("fixed_E",user)
        for bad in ({"finger3":7967},{"main_hand":89999},
                    {"off_hand":89999},{"trinket1":89999},{"finger1":0},
                    {"finger1":True},{"finger1":"7967"},
                    {"finger1":7967,"finger2":7967}):
            with self.subTest(bad=bad):
                with self.assertRaises(ux.SessionBlocked):
                    ux.user_scenario({**source,"enchant_choices":bad})
        # An apparently valid numeric ID is NOT a product approval;
        # without a verified v212 physical item it fails later in v098.
        self.assertFalse(ux.standard_controls().get("enchant_choices"))


    def test_all_26_dps_user_defaults_require_no_full_gear(self):
        self.assertEqual(len(ux.SUPPORTED),26)
        self.assertEqual(len(ux.bootstrap.ARCHETYPES),24)
        self.assertEqual(set(ux.SUPPORTED)-set(ux.bootstrap.ARCHETYPES),
                         ux.bootstrap.PURE_PRODUCT_SPECS)
        for key in ux.SUPPORTED:
            with self.subTest(key=key):
                c=ux.standard_controls(key)
                u=ux.user_scenario(c)
                self.assertEqual((u["character"]["class"],
                                  u["character"]["spec"]),key)
                self.assertEqual(len(u["trinkets"]),2)
                self.assertEqual(u["target"],{"ilevel":334,"final_T":None})
                self.assertNotIn("fillers",u)
                self.assertNotIn("seed",u)
                self.assertEqual(u["embellishments"],[])
                self.assertEqual(u["special_items"],[])

    def test_optional_race_and_talents_default_without_gear_import(self):
        controls=self.fixture()[2]
        self.assertEqual(controls["character"]["class"],"paladin")
        sample=ux.standard_controls(("paladin","retribution"))
        sample.pop("race");sample.pop("talents")
        resolved=ux.user_scenario(sample)
        self.assertEqual(resolved["character"]["race"],"dwarf")
        self.assertEqual(resolved["character"]["talents"],
                         ux.source_defaults(("paladin","retribution"))["talents"])
        self.assertEqual(resolved["trinkets"][0]["item_id"],
                         sample["trinket_ids"][0])
        self.assertEqual(resolved["special_items"],[])
        self.assertEqual(resolved["embellishments"],[])
        self.assertNotIn("fillers",resolved)
        self.assertNotIn("simc_gear",resolved)
        blank=ux.standard_controls(("paladin","retribution"))
        blank["race"]="   ";blank["talents"]=""
        self.assertEqual(ux.user_scenario(blank),resolved)
        custom=ux.standard_controls(("paladin","retribution"))
        custom["race"]="human";custom["talents"]="CUSTOM_TALENTS_V1"
        result=ux.user_scenario(custom)
        self.assertEqual(result["character"]["race"],"human")
        self.assertEqual(result["character"]["talents"],"CUSTOM_TALENTS_V1")

    def test_dwarf_default_requires_explicit_race_for_unsupported_classes(self):
        for key in (("druid","balance"),("druid","feral"),
                    ("demonhunter","havoc"),("demonhunter","devourer"),
                    ("evoker","devastation")):
            with self.subTest(key=key):
                controls=ux.standard_controls(key)
                controls.pop("race")
                with self.assertRaisesRegex(
                        ux.SessionBlocked,
                        "DWARF_NOT_AVAILABLE_FOR_CLASS_SELECT_RACE"):
                    ux.user_scenario(controls)
                controls["race"]="dwarf"
                with self.assertRaisesRegex(
                        ux.SessionBlocked,
                        "DWARF_NOT_AVAILABLE_FOR_CLASS_SELECT_RACE"):
                    ux.user_scenario(controls)
                controls["race"]=ux.source_defaults(key)["race"]
                self.assertEqual(ux.user_scenario(controls)["character"]["race"],
                                 controls["race"])

    def test_24_compact_starter_examples_exactly_reproduce_legacy_defaults(self):
        # Pinned complete source profiles are ONLY offline comparison fixtures.
        # Runtime starter lookup cannot require those full .simc files.
        import re
        records=ux.starter_examples()
        self.assertEqual(set(records),
                         {"/".join(key) for key in ux.bootstrap.ARCHETYPES})
        for key in sorted(ux.bootstrap.ARCHETYPES):
            with self.subTest(key=key):
                compact=ux.source_defaults(key)
                original=ux.legacy_fixture_path(key).read_text(encoding="utf8")
                lines=original.splitlines()
                for field in ("race","talents"):
                    vals=[line.split("=",1)[1] for line in lines
                          if line.startswith(field+"=")]
                    self.assertEqual(vals,[compact[field]])
                ids=[]
                for slot in ("trinket1","trinket2"):
                    vals=[line for line in lines if line.startswith(slot+"=")]
                    self.assertEqual(len(vals),1)
                    m=re.search(r"(?:^|,)id=(\d+)(?:,|$)",vals[0])
                    self.assertIsNotNone(m)
                    ids.append(int(m.group(1)))
                self.assertEqual(ids,compact["trinket_ids"])
                self.assertEqual(
                    compact["weapon_form"],ux.bootstrap.ARCHETYPES[key][2])

    def test_two_pure_dps_default_sessions_preserve_existing_identity_contract(self):
        root,binary,_=self.fixture()
        for key in sorted(ux.bootstrap.PURE_PRODUCT_SPECS):
            with self.subTest(spec=key):
                source=ux.standard_controls(key)
                self.assertEqual(source["oil_hands"],[])
                user=ux.user_scenario(source)
                self.assertEqual(len(user["trinkets"]),2)
                folder=ux.store_session(user,root/"runs",binary,"7bc10711b5")
                self.assertEqual(ux.store_session(user,root/"runs",binary,
                                                  "7bc10711b5"),folder)
                self.assertNotIn("ordinary_variant",
                      json.loads((folder/"V106_SESSION_IDENTITY.json").read_text()))
        self.assertEqual(len(list((root/"runs").iterdir())),2)

    def test_v596_E0_item_and_finger_change_distinguishes_v106_user_key(self):
        root,binary,_=self.fixture()
        controls=ux.standard_controls(("hunter","survival"))
        controls["enchant_choices"]={"finger1":89999}
        first=ux.user_scenario(controls)
        controls["enchant_choices"]={"finger2":89999}
        second=ux.user_scenario(controls)
        controls["enchant_choices"]={"finger1":89998}
        third=ux.user_scenario(controls)
        cases=[ux.session_key(u,binary,"7bc10711b5")
               for u in (first,second,third)]
        self.assertEqual(len(set(k for k,_ in cases)),3)
        # This is the underlying user-key distinction only. Runnable
        # authority still requires signed v212 + v098/v096 source replay.
        for user,(_,identity) in zip((first,second,third),cases):
            self.assertEqual(identity["user"],user)


    def test_session_binary_and_cache_sha_preserve_identity_without_full_reads(self):
        # The original SHA-256 values and v106 key must remain byte-identical.
        # Session lookup need not copy large SimC or static-cache files to RAM.
        import hashlib
        root,binary,user=self.fixture()
        cache=root/"selected-static-cache.json"
        cache.write_bytes(b"TEST_CACHE_ONLY_NOT_REAL_ITEM_DATA")
        binary_sha=hashlib.sha256(binary.read_bytes()).hexdigest()
        cache_sha=hashlib.sha256(cache.read_bytes()).hexdigest()
        original=pathlib.Path.read_bytes
        def no_full_large_file_read(path):
            if path in (binary,cache):
                raise AssertionError("FULL_BINARY_OR_CACHE_READ_FOR_SHA")
            return original(path)
        with mock.patch.object(pathlib.Path,"read_bytes",no_full_large_file_read):
            key,identity=ux.session_key(
                user,binary,"7bc10711b5",static_cache=cache)
        self.assertEqual(identity["simc_binary_sha256"],binary_sha)
        self.assertEqual(identity["static_cache_sha256"],cache_sha)
        self.assertEqual(
            key,ux.sha(ux.canonical(identity).encode("utf8"))[:20])
        binary.write_bytes(b"CHANGED_BINARY_BYTES")
        changed_key,changed=ux.session_key(
            user,binary,"7bc10711b5",static_cache=cache)
        self.assertNotEqual(changed["simc_binary_sha256"],binary_sha)
        self.assertEqual(changed["static_cache_sha256"],cache_sha)
        self.assertNotEqual(changed_key,key)
        cache.write_bytes(b"CHANGED_CACHE_BYTES")
        cache_key,cache_changed=ux.session_key(
            user,binary,"7bc10711b5",static_cache=cache)
        self.assertNotEqual(cache_changed["static_cache_sha256"],cache_sha)
        self.assertNotEqual(cache_key,changed_key)

    def test_profile_stage_contract_is_sealed_into_new_session_identity(self):
        root,binary,user=self.fixture()
        key,identity=ux.session_key(user,binary,"7bc10711b5")
        self.assertEqual(key,ux.sha(ux.canonical(identity).encode("utf8"))[:20])
        self.assertEqual(identity["profile_stage"]["stage_id"],
                         "v098_target_profile")
        self.assertEqual(identity["profile_stage"]["stage_version"],
                         "v098_profile_stage_v1")
        self.assertEqual(len(identity["profile_stage"]["code_sha256"]),64)
        self.assertTrue(identity["profile_stage"]["data_fingerprints"])

    def test_deterministic_session_resume_and_binary_revision_identity(self):
        root,binary,user=self.fixture()
        folder=ux.store_session(user,root/"sessions",binary,"7bc10711b5")
        again=ux.store_session(user,root/"sessions",binary,"7bc10711b5")
        self.assertEqual(folder,again)
        self.assertEqual(json.loads((folder/"user.json").read_text()),user)
        changed=copy.deepcopy(user)
        changed["target"]["ilevel"]=321
        self.assertNotEqual(ux.store_session(changed,root/"sessions",
                       binary,"7bc10711b5"),folder)
        self.assertNotEqual(ux.store_session(user,root/"sessions",
                       binary,"7bc10711b6"),folder)
        other=root/"another.fake";other.write_bytes(b"DIFFERENT_SIMC_BINARY")
        self.assertNotEqual(ux.store_session(user,root/"sessions",
                       other,"7bc10711b5"),folder)
        with self.assertRaisesRegex(ux.SessionBlocked,"SIMC_REVISION"):
            ux.store_session(user,root,binary,"not-a-known-revision")

    def test_v564_fresh_v191_26_supplier_uses_new_bundle_not_old_package(self):
        """No old-season inventory JSON is needed for fresh 26 spec coverage."""
        bootstrap=ux.bootstrap
        source=bootstrap.source_first
        key="mage/frost"
        bundle={
            "gear":{"season_build":"12.2.0.99999"},
            "tier":{"retail_build":"12.2.0.99999"},
            "budget":{"schema":"unit-test-source-not-numeric-authority"},
        }
        bad=pathlib.Path(self.fixture()[0])/"old-season-missing"
        with (mock.patch.object(source.gear,"DEFAULT",bad/"gear.json"),
              mock.patch.object(source,"TIER_PATH",bad/"tier.json"),
              mock.patch.object(source,"BUDGET_PATH",bad/"budget.json"),
              mock.patch.object(bootstrap,
                                "_profile_supplier_registry",
                                side_effect=AssertionError(
                                    "HISTORICAL_PACKAGE_NOT_ALLOWED"))):
            coverage=bootstrap._current_season_profile_supplier_coverage(
                {"specializations":{key:{}}},key,one_spec_only=True,
                original_source_bundle=bundle)
        self.assertEqual(coverage["selected_specialization"],key)
        self.assertEqual(coverage["season_build"],"12.2.0.99999")
        self.assertEqual(coverage["current_season_profile_supplier_count"],1)
        self.assertEqual(coverage["contract_count"],26)
        self.assertFalse(coverage["all_specs_ready"])
        self.assertFalse(coverage["adaptive_native_evidence_complete"])

    def test_v562_fresh_installed_v212_session_uses_exact_source_without_old_json(self):
        """A zero-source season must not load historical 511/65/F seasons."""
        root,binary,_=self.fixture()
        user=ux.user_scenario(ux.standard_controls(("mage","frost")))
        current=root/"actual_new_season_v213.json"
        current.write_bytes(b"source-supplied-exact-v213-original-test-only")
        bad=root/"not-present"
        rev="a"*40
        digest="c"*64
        with (mock.patch.object(ux.bootstrap.source_first.gear,
                                "DEFAULT",bad/"old_gear.json"),
              mock.patch.object(ux.bootstrap.source_first,
                                "TIER_PATH",bad/"old_tier.json"),
              mock.patch.object(ux.bootstrap.source_first,
                                "BUDGET_PATH",bad/"old_budget.json"),
              mock.patch.object(ux,"source_catalog_identity",
                                return_value={"source":"test-only-v213"})):
            key,identity=ux.session_key(
                user,binary,rev,current_season_product=True,
                source_catalog_path=current,
                fresh_installed_manifest_sha256=digest)
            self.assertEqual(identity["fresh_v212_installed_manifest_sha256"],
                             digest)
            self.assertNotIn("current_season_gear_sha256",identity)
            self.assertNotIn("current_season_tier_sha256",identity)
            self.assertNotIn("current_season_budget_sha256",identity)
            self.assertEqual(identity["current_season_source_authority"],
                "EXACT_V212_INSTALLED_SOURCE_NOT_LEGACY_SEASON_JSON")
            fingerprints=identity["profile_stage"]["data_fingerprints"]
            self.assertNotIn("season_gear",fingerprints)
            self.assertNotIn("season_tier",fingerprints)
            self.assertNotIn("season_budget",fingerprints)
            self.assertIn("v213_source_catalog",fingerprints)
            other,_=ux.session_key(user,binary,rev,
                current_season_product=True,source_catalog_path=current,
                fresh_installed_manifest_sha256="d"*64)
            self.assertNotEqual(key,other)
        # Packaged users preserve their original source dependency behavior.
        self.assertTrue(ux.bootstrap.source_first.gear.DEFAULT.is_file())

    def test_v184_weapon_policy_rekeys_current_season_without_touching_legacy(self):
        root,binary,_=self.fixture()
        user=ux.user_scenario(ux.standard_controls(("mage","frost")))
        rev="7bc10711b5"
        fresh=ux.store_session(user,root/"runs",binary,rev,
                               current_season_product=True)
        key,identity=ux.session_key(user,binary,rev,
                                    current_season_product=True)
        policy=ux.bootstrap.source_first.WEAPON_SELECTION_POLICY
        self.assertEqual(fresh.name,key)
        self.assertEqual(identity["current_season_weapon_selection_policy"],policy)
        self.assertEqual(ux.store_session(user,root/"runs",binary,rev,
                                         current_season_product=True),fresh)
        # Reconstruct the immutable pre-v184 identity without rewriting
        # any actual user cache or inventing a different item DB snapshot.
        historical=dict(identity)
        historical.pop("current_season_weapon_selection_policy")
        old_key=ux.sha(ux.canonical(historical).encode("utf8"))[:20]
        self.assertNotEqual(old_key,key)
        old=root/"runs"/old_key
        old.mkdir()
        (old/"user.json").write_text(ux.canonical(user)+"\n",encoding="utf8")
        (old/"V106_SESSION_IDENTITY.json").write_text(
            ux.canonical(historical)+"\n",encoding="utf8")
        # Prior results are inspectable, but must not be resumed with new
        # gear IDs or admitted as the new corrected Native result.
        with mock.patch.object(ux.bootstrap,"run",
                               side_effect=AssertionError("NATIVE_NOT_AUTHORIZED")):
            self.assertEqual(ux.worker(old,binary,rev),3)
        self.assertFalse((old/"generated").exists())
        standard_key,standard_identity=ux.session_key(user,binary,rev)
        self.assertNotIn("current_season_weapon_selection_policy",
                         standard_identity)
        self.assertNotEqual(standard_key,key)

    def test_v187_tier_slot_only_rekeys_affected_season_sessions(self):
        root,binary,_=self.fixture()
        revision="7bc10711b5"
        base=ux.user_scenario(ux.standard_controls(("mage","frost")))
        baseline_key,baseline=ux.session_key(
            base,binary,revision,current_season_product=True)
        self.assertNotIn("current_season_tier_layout_policy",baseline)
        # A crafted cloak does not displace any of the 4 original tier
        # slots. Do not invalidate its valid historical DPS cache.
        outside=copy.deepcopy(base)
        outside["embellishments"]=[{
            "slot":"back","item_id":239656,
            "options":{"crafted_stats":"32/36",
                       "embellishment":"arcanoweave_lining"}}]
        _,identity_out=ux.session_key(
            outside,binary,revision,current_season_product=True)
        self.assertNotIn("current_season_tier_layout_policy",identity_out)
        selected=copy.deepcopy(base)
        selected["embellishments"]=[{
            "slot":"head","item_id":239652,
            "options":{"crafted_stats":"32/36",
                       "embellishment":"arcanoweave_lining"}}]
        key,identity=ux.session_key(
            selected,binary,revision,current_season_product=True)
        self.assertNotEqual(key,baseline_key)
        self.assertEqual(identity["current_season_tier_layout_policy"],
                         ux.bootstrap.common.CURRENT_SEASON_TIER_LAYOUT_POLICY)
        prior=dict(identity)
        prior.pop("current_season_tier_layout_policy")
        old_key=ux.sha(ux.canonical(prior).encode("utf8"))[:20]
        self.assertNotEqual(key,old_key)
        old=root/"sessions"/old_key
        old.mkdir(parents=True)
        (old/"user.json").write_text(
            ux.canonical(selected)+"\n",encoding="utf8")
        (old/"V106_SESSION_IDENTITY.json").write_text(
            ux.canonical(prior)+"\n",encoding="utf8")
        with mock.patch.object(ux.bootstrap,"run",
                               side_effect=AssertionError("NO_NATIVE_ALLOWED")):
            self.assertEqual(ux.worker(old,binary,revision),3)
        self.assertFalse((old/"generated").exists())
        fresh=ux.store_session(
            selected,root/"sessions",binary,revision,
            current_season_product=True)
        self.assertEqual(fresh.name,key)
        self.assertNotEqual(fresh,old)
        self.assertEqual(ux.store_session(
            selected,root/"sessions",binary,revision,
            current_season_product=True),fresh)

    def test_internal_ordinary_variant_gets_new_session_without_default_identity_drift(self):
        root,binary,_=self.fixture()
        user=ux.user_scenario(ux.standard_controls(("demonhunter","havoc")))
        ordinary=ux.store_session(user,root/"sessions",binary,"7bc10711b5")
        variant=ux.store_session(user,root/"sessions",binary,"7bc10711b5",
              ordinary_variant="mid2_havoc_leather_feet_v1")
        self.assertNotEqual(ordinary,variant)
        self.assertEqual((ordinary/"user.json").read_bytes(),
                         (variant/"user.json").read_bytes())
        original=json.loads((ordinary/"V106_SESSION_IDENTITY.json").read_text())
        selected=json.loads((variant/"V106_SESSION_IDENTITY.json").read_text())
        self.assertNotIn("ordinary_variant",original)
        self.assertEqual(selected["ordinary_variant"],"mid2_havoc_leather_feet_v1")
        self.assertEqual({k:v for k,v in selected.items()
                          if k!="ordinary_variant"},original)
        self.assertEqual(ux.sha(ux.canonical(original).encode("utf8"))[:20],
                         ordinary.name)
        self.assertEqual(ux.sha(ux.canonical(selected).encode("utf8"))[:20],
                         variant.name)
        self.assertEqual(ux.store_session(user,root/"sessions",binary,
              "7bc10711b5",ordinary_variant="mid2_havoc_leather_feet_v1"),
              variant)

    def test_variant_rejects_unverified_level_spec_and_user_foot_conflict(self):
        root,binary,_=self.fixture()
        user=ux.user_scenario(ux.standard_controls(("demonhunter","havoc")))
        for key,changed,error in [
            ("wrong-level",{"ilevel":321},"ORDINARY_VARIANT_CHARACTER_OR_LEVEL"),
            ("wrong-spec",{"class":"druid","spec":"feral"},
             "ORDINARY_VARIANT_CHARACTER_OR_LEVEL")]:
            with self.subTest(key=key):
                item=copy.deepcopy(user)
                item["target"]["ilevel"]=changed.get("ilevel",334)
                item["character"]["class"]=changed.get("class","demonhunter")
                item["character"]["spec"]=changed.get("spec","havoc")
                with self.assertRaisesRegex(ux.SessionBlocked,error):
                    ux.store_session(item,root/"sessions",binary,"7bc10711b5",
                        ordinary_variant="mid2_havoc_leather_feet_v1")
        special=copy.deepcopy(user)
        special["special_items"]=[{"slot":"feet","item_id":268261,"options":{}}]
        # The existing v106 special-L policy requires a static-cache file
        # before the internal ordinary-variant collision check is reachable.
        # This is an offline identity fixture, NOT a measured Native cache.
        static=root/"synthetic_static_cache.json"
        static.write_bytes(b"OFFLINE_NOT_NATIVE_STATIC_DATA")
        with self.assertRaisesRegex(ux.SessionBlocked,
                                    "ORDINARY_VARIANT_CONFLICTS_WITH_SELECTED_GEAR"):
            ux.store_session(special,root/"sessions",binary,"7bc10711b5",
                 static_cache=static,
                 ordinary_variant="mid2_havoc_leather_feet_v1")
        with self.assertRaisesRegex(ux.SessionBlocked,"ORDINARY_VARIANT_NOT_PINNED"):
            ux.store_session(user,root/"sessions",binary,"7bc10711b5",
                 ordinary_variant="unknown")
        self.assertFalse((root/"sessions").exists())

    def test_variant_worker_routes_to_existing_bootstrap_and_refuses_tampered_identity(self):
        root,binary,_=self.fixture()
        user=ux.user_scenario(ux.standard_controls(("demonhunter","havoc")))
        ordinary=ux.store_session(user,root/"sessions",binary,"7bc10711b5")
        variant=ux.store_session(user,root/"sessions",binary,"7bc10711b5",
              ordinary_variant="mid2_havoc_leather_feet_v1")
        with mock.patch.object(ux.bootstrap,"run",
             return_value={"native_result":fake_native(0)}) as run:
            self.assertEqual(ux.worker(variant,binary,"7bc10711b5"),0)
            self.assertEqual(run.call_args.kwargs["ordinary_variant"],
                             "mid2_havoc_leather_feet_v1")
            self.assertEqual(run.call_count,1)
            self.assertEqual(ux.worker(ordinary,binary,"7bc10711b5"),0)
            self.assertNotIn("ordinary_variant",run.call_args.kwargs)
            self.assertEqual(run.call_count,2)
        self.assertNotEqual(ux.paths(variant)["final"],ux.paths(ordinary)["final"])
        identity_path=variant/"V106_SESSION_IDENTITY.json"
        seal=json.loads(identity_path.read_text())
        seal["ordinary_variant"]="invalid_candidate"
        identity_path.write_text(ux.canonical(seal)+"\\n",encoding="utf8")
        with mock.patch.object(ux.bootstrap,"run") as run:
            self.assertEqual(ux.worker(variant,binary,"7bc10711b5"),3)
            run.assert_not_called()

    def test_cancel_flag_and_progress_expose_existing_durable_runner(self):
        root,binary,user=self.fixture()
        folder=ux.store_session(user,root,binary,"7bc10711b5")
        self.assertEqual(ux.progress(folder)["status"],"NOT_STARTED")
        flag=ux.request_cancel(folder)
        self.assertTrue(flag.is_file())
        ux.clear_cancel(folder)
        self.assertFalse(flag.exists())
        trace=ux.paths(folder)
        trace["progress"].parent.mkdir(parents=True)
        trace["progress"].write_text(json.dumps({
          "status":"SCOUT_00_VERIFIED","progress_percent":50.0,
          "completed_jobs":3,"planned_jobs":6,"cache_verified_hits":1,
          "new_native_attempts":3}))
        p=ux.progress(folder)
        self.assertEqual((p["completed_jobs"],p["planned_jobs"]),(3,6))
        self.assertEqual((p["native_attempts"],p["cache_hits"]),(3,1))
        self.assertEqual(p["progress_percent"],50.0)

    def test_intentional_cancel_is_distinct_from_actual_failure(self):
        # No Native: exercise real sealed worker and its exact exception
        # boundary, not a mocked application status response.
        root,binary,user=self.fixture()
        folder=ux.store_session(user,root,binary,"7bc10711b5")
        state=ux.paths(folder)["state"]
        cancel=ux.request_cancel(folder)
        variants=(ux.bootstrap.entry.durable.DurableBlocked,
                  ux.bootstrap.entry.durable.engine.PipelineBlocked)
        for kind in variants:
            with self.subTest(cancel_type=kind.__name__):
                with mock.patch.object(ux.bootstrap,"run",
                        side_effect=kind("USER_CANCEL_FILE_PRESENT")) as run:
                    self.assertEqual(ux.worker(folder,binary,"7bc10711b5"),3)
                    run.assert_called_once()
                self.assertEqual(json.loads(state.read_text())["status"],
                                 "CANCELLED_PARTIAL")
                self.assertFalse(ux.paths(folder)["final"].exists())
        # Same marker in an unexpected exception type must NOT be relabeled.
        with mock.patch.object(ux.bootstrap,"run",
                side_effect=RuntimeError("USER_CANCEL_FILE_PRESENT")):
            self.assertEqual(ux.worker(folder,binary,"7bc10711b5"),3)
        self.assertEqual(json.loads(state.read_text())["status"],
                         "BLOCKED_OR_PARTIAL")
        # Without the cancel file, even the expected class is a real error.
        cancel.unlink()
        with mock.patch.object(ux.bootstrap,"run",
                side_effect=variants[0]("USER_CANCEL_FILE_PRESENT")):
            self.assertEqual(ux.worker(folder,binary,"7bc10711b5"),3)
        self.assertEqual(json.loads(state.read_text())["status"],
                         "BLOCKED_OR_PARTIAL")

    def test_wrong_oil_hand_rejected_and_tank_not_enabled(self):
        c=ux.standard_controls(("paladin","retribution"))
        c["oil_hands"]=["main_hand","off_hand"]
        with self.assertRaisesRegex(ux.SessionBlocked,"OIL_HANDS"):
            ux.user_scenario(c)
        c=ux.standard_controls()
        c["class"]="warrior";c["spec"]="protection"
        with self.assertRaisesRegex(ux.SessionBlocked,"DPS_ARCHETYPE_NOT_READY"):
            ux.user_scenario(c)

    def test_user_stat_cap_default_custom_and_invalid(self):
        controls=ux.standard_controls()
        self.assertEqual(controls["max_single_stat_percent"],60)
        user=ux.user_scenario(controls)
        self.assertEqual(user["max_single_stat_percent"],60)
        controls["max_single_stat_percent"]=50
        self.assertEqual(ux.user_scenario(controls)["max_single_stat_percent"],50)
        controls["max_single_stat_percent"]=100
        self.assertEqual(ux.user_scenario(controls)["max_single_stat_percent"],100)
        for invalid in (24,101,60.5,True):
            controls["max_single_stat_percent"]=invalid
            with self.assertRaisesRegex(ux.SessionBlocked,
                                        "USER_MAX_SINGLE_STAT_PERCENT"):
                ux.user_scenario(controls)
        # Previously sealed controls with no new field retain their original
        # implicit <50% semantics rather than being silently reinterpreted.
        del controls["max_single_stat_percent"]
        self.assertNotIn("max_single_stat_percent",
                         ux.user_scenario(controls))

    def test_format_only_proven_95_result_never_claim_global(self):
        msg=ux.format_result(fake_native())
        self.assertIn("179,171.8",msg)
        self.assertIn("치명 704 (22.12%)",msg)
        self.assertIn("특화 787",msg)
        self.assertIn("전역 최적해 입증 아님",msg)
        bad=fake_native();bad["user_result"]["confidence_level"]=0.97
        with self.assertRaisesRegex(ux.SessionBlocked,"ONLY_95_ALLOWED"):
            ux.format_result(bad)

    def test_os_worker_lock_serial_and_released_for_resume(self):
        root,_,_=self.fixture()
        with ux.worker_lock(root):
            with self.assertRaisesRegex(ux.SessionBlocked,
                                        "SAME_SESSION_ALREADY_RUNNING"):
                with ux.worker_lock(root):pass
        self.assertEqual((root/"V106_WORKER.lock").stat().st_size,1)
        with ux.worker_lock(root):pass

    def test_offline_mock_native_result_resume_changes_hit_count_only(self):
        root,binary,user=self.fixture()
        folder=ux.store_session(user,root/"sessions",binary,"7bc10711b5")
        fake1={"native_result":fake_native(0)}
        fake2={"native_result":fake_native(6)}
        with mock.patch.object(ux.bootstrap,"run",
                               side_effect=[fake1,fake2]) as mocked:
            self.assertEqual(ux.worker(folder,binary,"7bc10711b5"),0)
            synthetic_completed_cache(folder)
            self.assertEqual(ux.worker(folder,binary,"7bc10711b5",
                                       cache_only=True),0)
            self.assertEqual(mocked.call_count,2)
        if self.mock_folder_open is not None:
            self.assertEqual(self.mock_folder_open.call_count,2)
            self.mock_folder_open.assert_any_call(str(folder))
        p=ux.paths(folder)
        self.assertEqual(json.loads(p["final"].read_text())
                         ["cache_hits_this_run"],6)
        self.assertEqual(json.loads(p["state"].read_text())["status"],"PASS_CACHE_ONLY")
        self.assertEqual(json.loads((folder/"V112_CACHE_REPLAY_RECEIPT.json")
                                   .read_text())["cache_hits_this_run"],6)
        self.assertNotIn("result.json",list(x.name for x in folder.glob("*.json")))
        self.assertTrue((folder/"generated"/"simc_results"/"V094_RESULT.json").exists())

    def test_cache_only_missing_six_results_refuses_runner_before_any_native(self):
        root,binary,user=self.fixture()
        folder=ux.store_session(user,root/"sessions",binary,"7bc10711b5")
        with mock.patch.object(ux.bootstrap,"run") as mocked:
            self.assertEqual(ux.worker(folder,binary,"7bc10711b5",
                                       cache_only=True),3)
            mocked.assert_not_called()
        self.assertFalse((folder/"V112_CACHE_REPLAY_RECEIPT.json").exists())
        self.assertFalse(ux.paths(folder)["progress"].exists())

    def test_cache_only_rejects_modified_native_json2_even_with_fake_runner_pass(self):
        root,binary,user=self.fixture()
        folder=ux.store_session(user,root/"sessions",binary,"7bc10711b5")
        with mock.patch.object(ux.bootstrap,"run",
                               return_value={"native_result":fake_native(0)}):
            self.assertEqual(ux.worker(folder,binary,"7bc10711b5"),0)
        synthetic_completed_cache(folder)
        case=(ux.paths(folder)["native_result"].parent/
              "search"/"case_00"/"result.json")
        def fake_replay(*_args,**_kwargs):
            case.write_text(json.dumps({"fake_case":0,"tampered":True}))
            return {"native_result":fake_native(6)}
        with mock.patch.object(ux.bootstrap,"run",side_effect=fake_replay):
            self.assertEqual(ux.worker(folder,binary,"7bc10711b5",
                                       cache_only=True),3)
        self.assertIn("CACHE_ONLY_NATIVE_BYTES_OR_ATTEMPTS_DRIFT",
                      json.loads(ux.paths(folder)["state"].read_text())["reason"])
        self.assertFalse((folder/"V112_CACHE_REPLAY_RECEIPT.json").exists())

    def test_replay_semantic_drift_blocks_even_if_worker_is_mocked(self):
        root,binary,user=self.fixture()
        folder=ux.store_session(user,root,binary,"7bc10711b5")
        changed=fake_native(6)
        changed["user_result"]["observed_first_choice"]["observed_dps_mean"]+=1000
        with mock.patch.object(ux.bootstrap,"run",side_effect=[
                {"native_result":fake_native(0)},{"native_result":changed}]):
            self.assertEqual(ux.worker(folder,binary,"7bc10711b5"),0)
            synthetic_completed_cache(folder)
            self.assertEqual(ux.worker(folder,binary,"7bc10711b5",
                                       cache_only=True),3)
        self.assertIn("CACHE_ONLY_DPS_SEM_OR_95_RESULT_DRIFT",
                      json.loads(ux.paths(folder)["state"].read_text())["reason"])

if __name__=="__main__":unittest.main()
