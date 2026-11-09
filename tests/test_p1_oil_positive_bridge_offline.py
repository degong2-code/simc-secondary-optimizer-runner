"""Conditional installed O>0 physical oil input, offline only; no real proof."""
import copy,hashlib,pathlib,sys,tempfile,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v091_weapon_oil_external_adapter as oil_mod
import v096_unified_product_entry as entry
import v212_environment_manifest as installed
import v216_environment_build_coordinator as coordinator
from test_p3_ho_fresh_v212_user_bridge import FreshInstalledV096Bridge

class PositiveInstalledOil(unittest.TestCase):
    def case(self,root):
        path,doc,cfg,flask,profile,selection,attested=(
            FreshInstalledV096Bridge().make_case(root))
        old_sha=doc["manifest_sha256"]
        fixed={"crit_rating":16,"haste_rating":17,
               "mastery_rating":0,"versatility_rating":0}
        source={"source_verification":"VALID_SAME_SEASON_SOURCE",
            "source_sha256":doc["trusted_budget_component_source_identities"][
                "O"]["source_sha256"],
            "weapon_applicability_verified":True,
            "applied_hands":["main_hand"],
            "selected_oil_item_ids_by_hand":{"main_hand":243734},
            "oil_by_hand":{"main_hand":{
                "physical_item_id":243734,
                "simc_input_token":"main_hand:thalassian_phoenix_oil_2",
                "static_CHMV_vector":fixed}}}
        physical=installed._selected_verified_O_source(source,fixed)
        payload={k:v for k,v in doc.items() if k!="manifest_sha256"}
        payload["official_O"]=dict(fixed)
        payload["official_T"]=doc["official_B"]+sum(fixed.values())
        payload["official_O_physical_source"]=physical
        doc={**payload,"manifest_sha256":installed.sha(
            installed.canonical(payload).encode("utf8"))}
        self.assertNotEqual(doc["manifest_sha256"],old_sha)
        self.assertTrue(installed.verify_fresh_installed_environment(doc))
        newpath=path.with_name(
            "v212_installed_"+doc["manifest_sha256"][:20]+".json")
        newpath.write_text(installed.canonical(doc)+"\n",encoding="utf8")
        selection["installed_environment_path"]=str(newpath)
        selection["installed_manifest_sha256"]=doc["manifest_sha256"]
        selection["oil_by_hand"]=physical["oil_by_hand"]
        attested["installed_manifest_sha256"]=doc["manifest_sha256"]
        cfg["source"]["profile_sha256"]=hashlib.sha256(
            profile.encode("utf8")).hexdigest()
        converted=oil_mod.configure(
            profile,cfg,"one_hand_frill",["main_hand"],
            season_oil_by_hand=selection["oil_by_hand"])
        self.assertEqual(converted["declared_O"],fixed)
        return doc,converted["scenario"],converted["profile"],flask,selection,attested

    def test_positive_requires_source_id_hand_and_exact_vector(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            doc,cfg,profile,flask,selection,attested=self.case(root)
            self.assertEqual(doc["official_O_physical_source"][
                "selected_oil_item_ids_by_hand"],{"main_hand":243734})
            with mock.patch.object(coordinator,
                    "find_verified_installed_season_environment",
                    return_value=attested):
                admitted=entry._admitted_fresh_season_source(
                    manifest_path=root/"manifest.json",season=selection,
                    revision="runtime-changed",user_scenario=cfg,
                    flask_F=flask,oil_hands=["main_hand"],profile=profile)
                self.assertEqual(admitted["season_budget"]["fixed_O"],
                                 doc["official_O"])
                self.assertEqual(admitted["season_budget"]["base_B"],3150)
                self.assertEqual(admitted["season_budget"]["final_T"],3183)
                self.assertEqual(admitted["oil_by_hand"],
                                 selection["oil_by_hand"])
                altered=copy.deepcopy(selection)
                altered["oil_by_hand"]["main_hand"]["physical_item_id"]=999
                with self.assertRaisesRegex(entry.EntryBlocked,
                       "FRESH_SEASON_POSITIVE_O_VERIFIED_PHYSICAL_SOURCE_DRIFT"):
                    entry._admitted_fresh_season_source(
                        manifest_path=root/"manifest.json",season=altered,
                        revision="runtime-changed",user_scenario=cfg,
                        flask_F=flask,oil_hands=["main_hand"],profile=profile)
                with self.assertRaisesRegex(entry.EntryBlocked,
                       "FRESH_SEASON_POSITIVE_O_SIMC_PROFILE_DRIFT"):
                    entry._admitted_fresh_season_source(
                        manifest_path=root/"manifest.json",season=selection,
                        revision="runtime-changed",user_scenario=cfg,
                        flask_F=flask,oil_hands=["main_hand"],
                        profile=profile.replace("thalassian_phoenix_oil_2",
                                                "unverified_oil"))

    def test_tampered_positive_metadata_cannot_verify_even_rehashed(self):
        with tempfile.TemporaryDirectory() as td:
            doc,*_=self.case(pathlib.Path(td))
            payload={k:v for k,v in doc.items() if k!="manifest_sha256"}
            del payload["official_O_physical_source"]
            corrupted={**payload,"manifest_sha256":installed.sha(
                installed.canonical(payload).encode("utf8"))}
            with self.assertRaisesRegex(installed.EnvironmentBlocked,
                                         "FRESH_INSTALL_READY_OR_BUDGET"):
                installed.verify_fresh_installed_environment(corrupted)
            payload={k:v for k,v in doc.items() if k!="manifest_sha256"}
            payload["official_O_physical_source"]=copy.deepcopy(
                payload["official_O_physical_source"])
            payload["official_O_physical_source"]["oil_by_hand"][
                "main_hand"]["static_CHMV_vector"]["haste_rating"]=18
            corrupted={**payload,"manifest_sha256":installed.sha(
                installed.canonical(payload).encode("utf8"))}
            with self.assertRaisesRegex(installed.EnvironmentBlocked,
                                         "FRESH_INSTALL_READY_OR_BUDGET"):
                installed.verify_fresh_installed_environment(corrupted)
if __name__=="__main__":unittest.main()
