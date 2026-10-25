"""v067: exact profile-neutral injection into reused v065 execution loop.

The non-Mage profile here is synthetic-only for data-flow tests, NOT proof of
equipment, item effects, APL compatibility or Native cross-class DPS.
"""
import copy,json,pathlib,sys,tempfile,unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v046_static_item_cache as native
import v065_original_scheduler_native_bridge as engine
import v066_profile_neutral_preflight as adapter
import v067_generic_adaptive_native_route as route
from test_v066_profile_neutral_preflight import fixture, SIMC_SHA

def serialized(root,cls="mage",spec="arcane",role="spell"):
    scenario,fill,stat,profile,witnesses=fixture(cls,spec,role)
    root=pathlib.Path(root)
    root.mkdir(parents=True,exist_ok=True)
    inputs={}
    for name,obj in (("scenario.json",scenario),("filler.json",fill),
                     ("static_cache.json",stat)):
        path=root/name
        path.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf8")
        inputs[name]=path
    src=root/"reference.simc";src.write_text(profile,encoding="utf8")
    refs=root/"witnesses";refs.mkdir(exist_ok=True)
    for i,w in enumerate(witnesses):
        folder=refs/("case_%02d"%i);folder.mkdir(exist_ok=True)
        (folder/"input.simc").write_text(w["input"],encoding="utf8")
        (folder/"result.json").write_text(json.dumps(w["native"]),encoding="utf8")
    return inputs["scenario.json"],inputs["filler.json"],inputs["static_cache.json"],src,refs

class GenericNativePipeline(unittest.TestCase):
    def test_existing_scheduler_reused_not_reimplemented(self):
        with tempfile.TemporaryDirectory() as d:
            path=pathlib.Path(d)
            files=serialized(path/"input")
            out=path/"out"
            self.assertEqual(route.route(*files,SIMC_SHA,out),0)
            report=json.loads((out/"V065_RECEIPT.json").read_text())
            self.assertEqual(report["status"],"PASS_OFFLINE_SCOUT_PLAN_ONLY")
            self.assertEqual(report["native_attempts"],0)
            self.assertEqual(report["official_T"],1603)
            self.assertEqual(report["scoped_simc_binary_sha256"],SIMC_SHA)
            self.assertEqual(len(report["scouts"]),1)
            self.assertFalse(report["product_v015_v016_original_directly_merged"])
    def test_structural_other_class_uses_same_scheduler_no_native(self):
        with tempfile.TemporaryDirectory() as d:
            path=pathlib.Path(d)
            files=serialized(path/"input","warrior","arms","attack")
            out=path/"out"
            self.assertEqual(route.route(*files,SIMC_SHA,out),0)
            prep=json.loads((out/"V067_PROFILE_PREFLIGHT.json").read_text())
            self.assertEqual(prep["class"],"warrior")
            self.assertEqual(prep["spec"],"arms")
            self.assertFalse(prep["cross_class_native_acceptance_claimed"])
            self.assertEqual(json.loads((out/"V065_RECEIPT.json").read_text())
                                 ["native_attempts"],0)
    def test_no_missing_profile_hash_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            files=serialized(root/"input")
            source=files[3];source.write_text(source.read_text().replace(
                "race=dwarf","race=human"),encoding="utf8")
            self.assertEqual(route.main([
                "--scenario",str(files[0]),"--filler",str(files[1]),
                "--static-cache",str(files[2]),"--profile",str(files[3]),
                "--witness-root",str(files[4]),
                "--binary-sha256",SIMC_SHA,"--output",str(root/"out")]),3)
            result=json.loads((root/"out"/"V067_BLOCKED.json").read_text())
            self.assertEqual(result["status"],"BLOCKED_NO_SILENT_GUESS")
            self.assertIn("NATIVE_NUMERIC_WITNESSES_FOR_OTHER_PROFILE",result["error"])
    def test_binding_wrong_binary_not_reused_as_cached(self):
        with tempfile.TemporaryDirectory() as d:
            path=pathlib.Path(d)
            files=serialized(path/"in")
            out=path/"out"
            self.assertEqual(route.route(*files,SIMC_SHA,out),0)
            self.assertEqual(route.route(*files,"b"*64,out),3)
            blocked=json.loads((out/"V065_RECEIPT.json").read_text())
            self.assertIn("DURABLE_PROGRESS_IDENTITY_OR_BUDGET_CONFLICT",blocked["error"])
    def test_prepared_bundle_immutability_before_scheduling(self):
        cfg,fill,static,src,witnesses=fixture()
        prepared=adapter.prepare(cfg,fill,static,src,witnesses,SIMC_SHA)
        mutated=copy.deepcopy(prepared)
        mutated["summary"]["T_official"]+=1
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(engine.start(None,d,prepared=mutated),3)
            failure=json.loads((pathlib.Path(d)/"V065_RECEIPT.json").read_text())
            self.assertIn("GENERIC_PREPARED_BINDING_MISMATCH",failure["error"])
    def test_cross_class_simc_effects_remain_simc_owned(self):
        cfg,fill,static,src,witnesses=fixture("warrior","arms","attack")
        prepared=adapter.prepare(cfg,fill,static,src,witnesses,SIMC_SHA)
        self.assertEqual(prepared["summary"]["item_effects_and_APL_owned_by"],"SimC")
        self.assertEqual(prepared["summary"]["new_simc_calls"],0)
        self.assertFalse(prepared["summary"]["original_product_v016_integrated"])

if __name__=="__main__":
    unittest.main()
