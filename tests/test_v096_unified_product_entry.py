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


class InstalledE0NativeProfileInputTests(unittest.TestCase):
    """Original v212 CHMV E0 + actual SimC item fields, zero Native/effect probes."""

    def test_admitted_fresh_source_rebinds_signed_e0_into_native_identity(self):
        """Original v096 signed installed source path; no SimC subprocess."""
        from tests.test_v212_environment_manifest import (
            SelectedPermanentEnchantE0BudgetTests)
        import v212_environment_manifest as installed
        zero=dict.fromkeys(installed.season_budget.STATS,0)
        doc=SelectedPermanentEnchantE0BudgetTests().installed([{
            "enchant_id":89999,"simc_token":"enchant_ring__synthetic_e0",
            "slot":"finger1/finger2","ui_selectable":True,
            "verified_fixed_E":zero,
            "chmv_budget_receipt_sha256":"d"*64}])
        # Synthetic v212 helper omits the revision field because its
        # original budget-only unit test does not need a SimC revision.
        # The FULL v096 installed source replay does.
        doc["simc_revision"]="d"*40
        doc["trusted_budget_component_source_identities"]={
            k:{"source_sha256":str(i)*64}
            for i,k in enumerate(("G","J","F","O"),1)}
        F={**zero,"versatility_rating":165}
        doc["official_F_physical_source"]={
            "static_CHMV_vector":F,"F_rating":165,
            "simc_input_token":"test_flask"}
        profile="\n".join((
            "hunter=Selected","flask=test_flask",
            "finger1=id=268266,ilevel=334,enchant_id=89999",
            "finger2=id=268268,ilevel=334",""))
        normalized={
            "scenario":{"target":{"mode":"manual_total",
                "ilevel":334,"manual_total":3107}},
            "budget":{"T":3107,"J":92,"F":165,
                      "external_temporary_rating":zero}}
        with mock.patch.object(installed,
                "verify_fresh_installed_environment",return_value=True):
            preview=installed.preview_installed_selected_enchant_budget(
                document=doc,slot="finger1",item_id=268266,
                enchant_id=89999)
            selection={"identity_sha256":preview["selected_identity_sha256"],
                       "slot":"finger1","item_id":268266,
                       "enchant_id":89999}
            original_load={"stage_receipt_sha256":"f"*64}
            season={"schema":entry.FRESH_SEASON_SCHEMA,
                    "installed_environment_path":"/fake/v212.json",
                    "installed_manifest_sha256":doc["manifest_sha256"],
                    "oil_by_hand":{},"selected_user_installed_E0":selection}
            with (mock.patch.object(entry,
                    "_verified_installed_fresh_v217",
                    return_value=(doc,original_load)),
                  mock.patch.object(entry.contract,"normalize",
                    return_value=normalized)):
                result=entry._admitted_fresh_season_source(
                    manifest_path=pathlib.Path("/fake/manifest.json"),
                    season=season,revision="d"*40,user_scenario={},
                    flask_F=F,oil_hands=[],profile=profile)
            self.assertEqual(result["season_budget"]["base_B"],3107)
            self.assertEqual(result["season_budget"]["final_T"],3107)
            self.assertEqual(result["selected_user_installed_E0"]["choice"],
                             {"finger1":89999})
            self.assertEqual(result["selected_user_installed_E0"]["fixed_E"],
                             zero)
            self.assertEqual(len(result["season_source_identity"][
                "source_input_sha256"]),64)
            # Modified options may not replay under the same signed identity.
            changed={**season,"selected_user_installed_E0":{
                **selection,"enchant_id":89998}}
            with (mock.patch.object(entry,
                    "_verified_installed_fresh_v217",
                    return_value=(doc,original_load)),
                  mock.patch.object(entry.contract,"normalize",
                    return_value=normalized)):
                with self.assertRaisesRegex(
                        installed.EnvironmentBlocked,
                        "EXACT_INSTALLED_REGISTRATION_REQUIRED"):
                    entry._admitted_fresh_season_source(
                        manifest_path=pathlib.Path("/fake/manifest.json"),
                        season=changed,revision="d"*40,user_scenario={},
                        flask_F=F,oil_hands=[],profile=profile)


    def test_v625_two_signed_armor_e0_profile_and_unchanged_B_T(self):
        """Two real-slot source assertions, synthetic v212; zero Native."""
        from tests.test_v212_environment_manifest import (
            SelectedPermanentEnchantE0BudgetTests)
        import v212_environment_manifest as installed
        zero=dict.fromkeys(installed.season_budget.STATS,0)
        doc=SelectedPermanentEnchantE0BudgetTests().installed([
            {"enchant_id":7957,"simc_token":"enchant_chest__synthetic_e0",
             "slot":"chest","ui_selectable":True,
             "verified_fixed_E":zero,"chmv_budget_receipt_sha256":"d"*64},
            {"enchant_id":7951,"simc_token":"enchant_head__synthetic_e0",
             "slot":"head","ui_selectable":True,
             "verified_fixed_E":zero,"chmv_budget_receipt_sha256":"e"*64}])
        doc["simc_revision"]="d"*40
        doc["trusted_budget_component_source_identities"]={
            k:{"source_sha256":str(i)*64}
            for i,k in enumerate(("G","J","F","O"),1)}
        F={**zero,"versatility_rating":165}
        doc["official_F_physical_source"]={
            "static_CHMV_vector":F,"F_rating":165,
            "simc_input_token":"test_flask"}
        profile="\n".join((
            "hunter=Selected","flask=test_flask",
            "finger1=id=268266,ilevel=334",
            "finger2=id=268268,ilevel=334",
            "head=id=260001,ilevel=334,enchant_id=7951",
            "chest=id=260002,ilevel=334,enchant_id=7957",""))
        normalized={"scenario":{"target":{"mode":"manual_total",
                       "ilevel":334,"manual_total":3107}},
                    "budget":{"T":3107,"J":92,"F":165,
                              "external_temporary_rating":zero}}
        with mock.patch.object(installed,
              "verify_fresh_installed_environment",return_value=True):
            selections=[]
            for slot,eid,item in (("chest",7957,260002),
                                  ("head",7951,260001)):
                preview=installed.preview_installed_selected_enchant_budget(
                    document=doc,slot=slot,item_id=item,enchant_id=eid)
                selections.append({
                    "identity_sha256":preview["selected_identity_sha256"],
                    "slot":slot,"item_id":item,"enchant_id":eid})
            season={"schema":entry.FRESH_SEASON_SCHEMA,
                    "installed_environment_path":"/fake/v212.json",
                    "installed_manifest_sha256":doc["manifest_sha256"],
                    "oil_by_hand":{},
                    "selected_user_installed_E0_multi":selections}
            with (mock.patch.object(entry,
                    "_verified_installed_fresh_v217",
                    return_value=(doc,{"stage_receipt_sha256":"f"*64})),
                  mock.patch.object(entry.contract,"normalize",
                    return_value=normalized)):
                kwargs=dict(manifest_path=pathlib.Path("/fake/manifest.json"),
                            season=season,revision="d"*40,user_scenario={},
                            flask_F=F,oil_hands=[])
                accepted=entry._admitted_fresh_season_source(
                    **kwargs,profile=profile)
                bound=accepted["selected_user_installed_E0_multi"]
                self.assertEqual(bound["choice"],
                                 {"chest":7957,"head":7951})
                self.assertEqual(bound["fixed_E"],zero)
                self.assertEqual((accepted["season_budget"]["base_B"],
                                  accepted["season_budget"]["final_T"]),
                                 (3107,3107))
                self.assertEqual(len(accepted["season_source_identity"]
                    ["source_input_sha256"]),64)
                self.assertEqual(len(bound["selected_identity_sha256"]),2)
                with self.assertRaisesRegex(entry.EntryBlocked,
                        "FRESH_SELECTED_E0_EXACT_ONCE_SIMC_INPUT_REQUIRED"):
                    entry._admitted_fresh_season_source(
                        **kwargs,profile=profile.replace(
                            "head=id=260001,ilevel=334,enchant_id=7951",
                            "head=id=260001,ilevel=334"))
                with self.assertRaises(entry.EntryBlocked):
                    entry._admitted_fresh_season_source(
                        **kwargs,profile=profile.replace(
                            "head=id=260001,ilevel=334,enchant_id=7951",
                            "head=id=260001,ilevel=334,enchant_id=7957"))

    def test_v626_repeated_ring_enchant_id_counts_one_per_physical_ring(self):
        """The ring family is reusable, but each selected slot has one ID."""
        from tests.test_v212_environment_manifest import (
            SelectedPermanentEnchantE0BudgetTests)
        import v212_environment_manifest as installed
        zero=dict.fromkeys(installed.season_budget.STATS,0)
        doc=SelectedPermanentEnchantE0BudgetTests().installed([{
            "enchant_id":89999,"simc_token":"enchant_ring__synthetic_e0",
            "slot":"finger1/finger2","ui_selectable":True,
            "verified_fixed_E":zero,"chmv_budget_receipt_sha256":"d"*64}])
        profile=("hunter=Player\n"
                 "finger1=id=268266,ilevel=334,enchant_id=89999\n"
                 "finger2=id=268268,ilevel=334,enchant_id=89999\n")
        with mock.patch.object(installed,
              "verify_fresh_installed_environment",return_value=True):
            for slot,item in (("finger1",268266),("finger2",268268)):
                scope=installed.preview_installed_selected_enchant_budget(
                    document=doc,slot=slot,item_id=item,
                    enchant_id=89999)
                selected={"identity_sha256":scope["selected_identity_sha256"],
                          "slot":slot,"item_id":item,"enchant_id":89999}
                bound=entry._signed_installed_user_E0_profile(
                    doc=doc,selected=selected,profile=profile,
                    user_final_T=None,expected_same_id_count=2)
                self.assertEqual(bound["fixed_E"],zero)
                with self.assertRaisesRegex(entry.EntryBlocked,
                      "FRESH_SELECTED_E0_EXACT_ONCE_SIMC_INPUT_REQUIRED"):
                    entry._signed_installed_user_E0_profile(
                        doc=doc,selected=selected,profile=profile,
                        user_final_T=None,expected_same_id_count=1)
                with self.assertRaises(entry.EntryBlocked):
                    entry._signed_installed_user_E0_profile(
                        doc=doc,selected=selected,
                        profile=profile.replace("id="+str(item),
                                               "id=999999"),
                        user_final_T=None,expected_same_id_count=2)

    def test_v604_signed_e0_final_feet_profile_and_exact_once(self):
        """One v212 registered ordinary E0; the final SimC item still owns it."""
        from tests.test_v212_environment_manifest import (
            SelectedPermanentEnchantE0BudgetTests)
        import v212_environment_manifest as installed
        E=dict.fromkeys(installed.season_budget.STATS,0)
        doc=SelectedPermanentEnchantE0BudgetTests().installed([{
            "enchant_id":89999,"simc_token":"enchant_boots__synthetic_e0",
            "slot":"feet","ui_selectable":True,
            "verified_fixed_E":E,"chmv_budget_receipt_sha256":"d"*64}])
        with mock.patch.object(installed,
                "verify_fresh_installed_environment",return_value=True):
            source=installed.preview_installed_selected_enchant_budget(
                document=doc,slot="feet",item_id=260001,enchant_id=89999)
            selected={"identity_sha256":source["selected_identity_sha256"],
                      "slot":"feet","item_id":260001,"enchant_id":89999}
            profile=("hunter=Profile\n"
                     "finger1=id=268266,ilevel=334\n"
                     "finger2=id=268268,ilevel=334\n"
                     "feet=id=260001,ilevel=334,enchant_id=89999\n")
            accepted=entry._signed_installed_user_E0_profile(
                doc=doc,selected=selected,profile=profile,user_final_T=None)
            self.assertEqual(accepted["fixed_E"],E)
            self.assertEqual((accepted["base_B"],accepted["final_T"]),(3107,3107))
            for broken in (
                    profile.replace("id=260001","id=260002"),
                    profile.replace("enchant_id=89999","enchant_id=89998"),
                    profile.replace("finger2=id=268268,ilevel=334\n",""),
                    profile.replace("feet=id=260001,ilevel=334,enchant_id=89999",
                                    "feet=id=260001,ilevel=334"),
                    profile.replace("finger1=id=268266,ilevel=334",
                                    "finger1=id=268266,ilevel=334,enchant_id=89999")):
                with self.subTest(broken=broken):
                    with self.assertRaises(entry.EntryBlocked):
                        entry._signed_installed_user_E0_profile(
                            doc=doc,selected=selected,profile=broken,
                            user_final_T=None)
            # The user may select a weapon hand, but a boots enchant
            # is rejected by the original signed v212 slot/hand mask.
            with self.assertRaises(installed.EnvironmentBlocked):
                entry._signed_installed_user_E0_profile(
                    doc=doc,selected={**selected,"slot":"main_hand"},
                    profile=profile,user_final_T=None)


    def test_signed_v212_e0_option_matches_exact_finger_profile_once(self):
        from tests.test_v212_environment_manifest import (
            SelectedPermanentEnchantE0BudgetTests)
        import v212_environment_manifest as installed
        zero=dict.fromkeys(installed.season_budget.STATS,0)
        doc=SelectedPermanentEnchantE0BudgetTests().installed([{
            "enchant_id":7967,
            "simc_token":"enchant_ring__eyes_of_the_eagle",
            "slot":"finger1/finger2","ui_selectable":True,
            "verified_fixed_E":zero,
            "chmv_budget_receipt_sha256":"d"*64}])
        with mock.patch.object(installed,"verify_fresh_installed_environment",
                               return_value=True):
            bound=installed.preview_installed_selected_enchant_budget(
                document=doc,slot="finger1",item_id=268266,
                enchant_id=7967)
            selected={"identity_sha256":bound["selected_identity_sha256"],
                      "slot":"finger1","item_id":268266,
                      "enchant_id":7967}
            profile=("hunter=Profile\nfinger1=id=268266,ilevel=334,"
                     "enchant_id=7967\nfinger2=id=268268,ilevel=334\n")
            actual=entry._signed_installed_user_E0_profile(
                doc=doc,selected=selected,profile=profile,user_final_T=None)
            self.assertEqual(actual["fixed_E"],zero)
            self.assertEqual((actual["base_B"],actual["final_T"]),(3107,3107))
            self.assertEqual(actual["selected_identity_sha256"],
                             bound["selected_identity_sha256"])
            # No independent spell-effect activation check, never E>0 here.
            failures=(
                ({**selected,"identity_sha256":"0"*64},profile),
                (selected,profile.replace("id=268266","id=268269")),
                (selected,profile.replace("enchant_id=7967","enchant_id=999")),
                (selected,profile.replace("finger2=id=268268,ilevel=334\n","")),
                (selected,profile.replace(
                    "finger2=id=268268,ilevel=334",
                    "finger2=id=268268,ilevel=334,enchant_id=7967"))
            )
            for changed,profile_text in failures:
                with self.subTest(changed=changed,profile=profile_text):
                    with self.assertRaises(entry.EntryBlocked):
                        entry._signed_installed_user_E0_profile(
                            doc=doc,selected=changed,profile=profile_text,
                            user_final_T=None)
            positive={**doc,"published_verified_options":[{
                **doc["published_verified_options"][0],
                "verified_fixed_E":{**zero,"haste_rating":30}}]}
            with self.assertRaisesRegex(
                    entry.EntryBlocked,"SIGN.*SOURCE_OR_BUDGET"):
                entry._signed_installed_user_E0_profile(
                    doc=positive,selected=selected,profile=profile,
                    user_final_T=None)



    def test_v635_signed_positive_rings_and_e0_chest_auto_manual_T(self):
        """Signed new-season multi-slot E can leave the old one-profile gate."""
        from tests.test_v212_environment_manifest import (
            SelectedPermanentEnchantE0BudgetTests)
        import v212_environment_manifest as installed
        zero=dict.fromkeys(installed.season_budget.STATS,0)
        doc=SelectedPermanentEnchantE0BudgetTests().installed([
            {"enchant_id":8025,"simc_token":"enchant_ring__haste",
             "slot":"finger1/finger2","ui_selectable":True,
             "verified_fixed_E":{**zero,"haste_rating":29},
             "chmv_budget_receipt_sha256":"d"*64},
            {"enchant_id":7997,"simc_token":"enchant_ring__crit",
             "slot":"finger1/finger2","ui_selectable":True,
             "verified_fixed_E":{**zero,"crit_rating":29},
             "chmv_budget_receipt_sha256":"e"*64},
            {"enchant_id":7957,"simc_token":"enchant_chest__e0",
             "slot":"chest","ui_selectable":True,
             "verified_fixed_E":zero,
             "chmv_budget_receipt_sha256":"a"*64}])
        doc["simc_revision"]="d"*40
        doc["trusted_budget_component_source_identities"]={
            k:{"source_sha256":str(i)*64}
            for i,k in enumerate(("G","J","F","O"),1)}
        F={**zero,"versatility_rating":165}
        doc["official_F_physical_source"]={
            "static_CHMV_vector":F,"F_rating":165,
            "simc_input_token":"test_flask"}
        profile="\n".join((
            "hunter=Selected","flask=test_flask",
            "finger1=id=268266,ilevel=334,enchant_id=8025",
            "finger2=id=268268,ilevel=334,enchant_id=7997",
            "chest=id=260002,ilevel=334,enchant_id=7957",""))
        def bind(manual):
            with mock.patch.object(installed,
                    "verify_fresh_installed_environment",return_value=True):
                selection=[]
                for slot,item_id,eid in (
                        ("finger1",268266,8025),
                        ("finger2",268268,7997),
                        ("chest",260002,7957)):
                    proof=installed.preview_installed_selected_enchant_budget(
                        document=doc,slot=slot,item_id=item_id,
                        enchant_id=eid,manual_final_T=manual)
                    selection.append({
                        "identity_sha256":proof["selected_identity_sha256"],
                        "slot":slot,"item_id":item_id,"enchant_id":eid})
            season={"schema":entry.FRESH_SEASON_SCHEMA,
                    "installed_environment_path":"/fake/v212.json",
                    "installed_manifest_sha256":doc["manifest_sha256"],
                    "oil_by_hand":{},
                    "selected_user_installed_E0_multi":sorted(
                        selection,key=lambda x:x["slot"]),
                    **({"user_final_T":manual} if manual is not None else {})}
            normalized={
                "scenario":{"target":{"mode":"manual_total",
                    "ilevel":334,"manual_total":manual or 3165}},
                "budget":{"T":manual or 3165,"J":92,"F":165,
                          "external_temporary_rating":zero}}
            with (mock.patch.object(installed,
                    "verify_fresh_installed_environment",return_value=True),
                  mock.patch.object(entry,
                    "_verified_installed_fresh_v217",
                    return_value=(doc,{"stage_receipt_sha256":"f"*64})),
                  mock.patch.object(entry.contract,"normalize",
                    return_value=normalized)):
                return entry._admitted_fresh_season_source(
                    manifest_path=pathlib.Path("/fake/manifest.json"),
                    season=season,revision="d"*40,user_scenario={},
                    flask_F=F,oil_hands=[],profile=profile)
        auto=bind(None)
        manual=bind(3500)
        expected={**zero,"crit_rating":29,"haste_rating":29}
        for proof,B in ((auto,3165),(manual,3500)):
            self.assertEqual(proof["signed_installed_E"],expected)
            self.assertEqual(proof["selected_user_installed_E0_multi"][
                "fixed_E"],expected)
            self.assertEqual(proof["season_budget"]["base_B"],B)
            self.assertEqual(proof["season_budget"]["final_T"],B)
            self.assertTrue(proof["season_source_identity"][
                "source_input_sha256"])
        self.assertNotEqual(auto["signed_installed_E_identity_sha256"],
                            manual["signed_installed_E_identity_sha256"])
        self.assertNotEqual(auto["season_source_identity"][
            "source_input_sha256"],manual["season_source_identity"][
            "source_input_sha256"])


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

    def test_optional_search_policy_accepts_new_only_and_rejects_unknown(self):
        # Source and verified static budget remain identical; no SimC calls.
        with tempfile.TemporaryDirectory() as td:
            path,raw=self.fixture(td)
            legacy=entry.source(path)
            self.assertNotIn(entry.EXPLORATION_FIELD,legacy["manifest"])
            raw[entry.EXPLORATION_FIELD]="axis_coverage_v1"
            path.write_text(json.dumps(raw),encoding="utf8")
            selected=entry.source(path)
            self.assertEqual(selected["manifest"][entry.EXPLORATION_FIELD],
                             "axis_coverage_v1")
            self.assertEqual(selected["plan"]["base_B"],
                             legacy["plan"]["base_B"])
            self.assertEqual(selected["plan"]["source_profile_sha256"],
                             legacy["plan"]["source_profile_sha256"])
            raw[entry.EXPLORATION_FIELD]="invalid_nonexistent_policy"
            path.write_text(json.dumps(raw),encoding="utf8")
            with self.assertRaisesRegex(entry.EntryBlocked,
                                         "UNKNOWN_ADAPTIVE_EXPLORATION_POLICY"):
                entry.source(path)

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

    def test_simc_runtime_revision_changes_without_invalidating_season_source(self):
        with tempfile.TemporaryDirectory() as td:
            path,raw,receipt=self.seasonal_fixture(td)
            old=entry.source(path)
            source_bytes=(path.parent/"environment_build_receipt.json").read_bytes()
            runtime="d"*40
            self.assertNotEqual(runtime,receipt["source"]["simc_revision"])
            raw["native_revision"]=runtime
            path.write_text(json.dumps(raw),encoding="utf8")
            new=entry.source(path)
            self.assertEqual(new["plan"]["season_source_receipt_sha256"],
                             old["plan"]["season_source_receipt_sha256"])
            self.assertEqual(new["plan"]["base_B"],old["plan"]["base_B"])
            self.assertEqual(new["plan"]["final_T"],old["plan"]["final_T"])
            self.assertNotEqual(new["context"]["identity"],
                                old["context"]["identity"])
            self.assertEqual(source_bytes,(path.parent/
                             "environment_build_receipt.json").read_bytes())
            self.assertFalse((path.parent/"output").exists())

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
            obj["target"]["manual_total"]=None
            obj["target"]["manual_total_scope"]=None
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
