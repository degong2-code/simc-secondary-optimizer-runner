"""v093 B-valued v015 search with final native T=B+fixed O evidence.

Offline tests construct explicitly FAKE observations to exercise policy math.
These do not count as Native acceptance. Actual JSON2 acceptance must pass
v091.ingest_native and strict v064 disk-cache revalidation separately.
"""
from __future__ import annotations
import copy,hashlib,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v046_static_item_cache as cache
import v065_v015_scheduler_adapter as v065
import v091_weapon_oil_external_adapter as oil
import v093_inclusive_adaptive_scheduler_bridge as v93
import v082_fury_plate_dual_twohand_native as warrior
from test_v091_weapon_oil_external_adapter import fury,BIN,REV,FURY_TARGET

OTHER={"crit_rating":938,"haste_rating":738,
       "mastery_rating":837,"versatility_rating":837}

def simulated_result(req,dps,sem,seed=None):
    """SYNTHETIC OFFLINE FIXTURE ONLY; never shown as a real SimC receipt."""
    return {"status":"PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT",
         "schema":"v064_adaptive_evaluator_port_v1",
         "rating_semantics":"STATIC_CHMV_C_V1",
         "case_key":req["case_key"],"target":copy.deepcopy(req["target"]),
         "iterations":req["iterations"],"input_sha256":req["input_sha256"],
         "simc_binary_sha256":req["simc_binary_sha256"],
         "scenario_digest":req["scenario_digest"],
         "native_revision":req["native_revision"],
         "static_rating_verified":copy.deepcopy(req["target"]),
         "native_json_sha256":"a"*64,
         "oil_reported_by_native":req["v091_expected_temporary_enchant"],
         "dps_mean":float(dps),"dps_sem":float(sem),
         "dps_samples":req["iterations"]-1,"simc_seed":seed,
         "_synthetic_offline_only":True}

class V093InclusiveAdaptive(unittest.TestCase):
    def make(self,folder,hands=None,scout=35,confirm=80):
        profile,cfg,fill=fury(folder)
        prepared=oil.prepare(profile,cfg,fill,cache.empty_cache(),
                             "dual_two_hand",hands if hands is not None
                             else ["main_hand","off_hand"])
        context=v93.prepare(prepared,BIN,REV,scout,confirm)
        return context

    def test_original_v065_selects_B_and_simc_receives_T(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx=self.make(folder)
            self.assertEqual(ctx["identity"]["base_B"],3350)
            self.assertEqual(ctx["identity"]["approved_final_T"],3414)
            self.assertEqual(ctx["identity"]["oil_vector"]["crit_rating"],32)
            reqs=[v93.request(ctx,base,warrior.DECLARED_F,
                 pathlib.Path(folder)/("a" if i==0 else "b")/"result.json",
                 phase="seed") for i,base in enumerate((FURY_TARGET,OTHER))]
            obs=[v93.project_native_for_v065(r,simulated_result(r,201000+i*1000,650))
                 for i,r in enumerate(reqs)]
            self.assertEqual([sum(x["target"].values()) for x in obs],
                             [3350,3350])
            self.assertEqual([sum(x["v093_native_final_T_target"].values())
                              for x in obs],[3414,3414])
            state=v93.start_scout(ctx,obs,step=100,scout_max=1)
            self.assertEqual(state["official_total"],3350)
            plan=v93.next_scout(ctx,state,warrior.DECLARED_F,
                         pathlib.Path(folder)/"scout"/"result.json")
            self.assertEqual(sum(plan["candidate_B"].values()),3350)
            self.assertEqual(sum(plan["candidate_final_T"].values()),3414)
            self.assertEqual(plan["policy"],"v065_original_v015_choose_next")
            self.assertNotIn(plan["candidate_B"],[FURY_TARGET,OTHER])
            new_obs=simulated_result(plan["request"],202000,500)
            next_state=v93.accept_scout(ctx,state,plan["request"],new_obs)
            self.assertEqual(next_state["completed_new_scouts"],1)
            self.assertEqual(len(next_state["observations"]),3)
            confirm=v93.confirmation_plan(ctx,next_state,
                          warrior.DECLARED_F,pathlib.Path(folder)/"confirmation")
            self.assertEqual(len(confirm["cases"]),2)
            self.assertTrue(all(sum(x.values())==3414 for x in confirm["final_pair"]))
            self.assertEqual(confirm["policy"],"v065_original_v015_confirmation_pair")
            self.assertFalse(confirm["global_optimum_proven"])

    def test_original_v065_stat_judgment_reuses_native_static_sem(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx=self.make(folder)
            a=v93.request(ctx,FURY_TARGET,warrior.DECLARED_F,
                    pathlib.Path(folder)/"a"/"result.json",phase="confirm")
            b=v93.request(ctx,OTHER,warrior.DECLARED_F,
                    pathlib.Path(folder)/"b"/"result.json",phase="confirm")
            x=v93.fresh_judgment((a,b),(
                   simulated_result(a,201000,200,seed=1),
                   simulated_result(b,202000,200,seed=2)))
            self.assertTrue(x["pairwise_direction_supported"])
            self.assertFalse(x["global_optimum_proven"])
            self.assertEqual(x["official_final_T"],3414)
            self.assertEqual(x["underlying_free_allocation_B"],3350)
            y=v93.fresh_judgment((a,b),(
                   simulated_result(a,201000,200,seed=1),
                   simulated_result(b,202000,200,seed=1)))
            self.assertFalse(y["pairwise_direction_supported"])

    def test_native_evidence_tamper_rejected_but_full_T_kept(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx=self.make(folder)
            req=v93.request(ctx,FURY_TARGET,warrior.DECLARED_F,
                     pathlib.Path(folder)/"result.json",phase="seed")
            valid=simulated_result(req,200000,700)
            self.assertEqual(v93.project_native_for_v065(req,valid)
                             ["v093_native_final_T_target"],req["target"])
            for key,wrong in [
                ("static_rating_verified",dict(req["target"],crit_rating=999)),
                ("target",dict(req["target"],crit_rating=999)),
                ("case_key","other"),("input_sha256","0"*64),
                ("native_revision","bad"),
                ("oil_reported_by_native","disabled")]:
                with self.subTest(key=key):
                    changed=copy.deepcopy(valid);changed[key]=wrong
                    with self.assertRaisesRegex(v93.AdaptiveBridgeBlocked,
                                                "NATIVE_T_NOT_VERIFIED|NATIVE_OIL_INPUT"):
                        v93.project_native_for_v065(req,changed)

    def test_oil_and_binary_and_iterations_identity_separate(self):
        with tempfile.TemporaryDirectory() as folder:
            dual=self.make(folder,["main_hand","off_hand"])
            single=self.make(folder,["main_hand"])
            self.assertNotEqual(dual["identity"]["oil_vector"],
                                single["identity"]["oil_vector"])
            a=v93.request(dual,FURY_TARGET,warrior.DECLARED_F,
                   pathlib.Path(folder)/"a"/"result.json",phase="seed")
            b=v93.request(single,FURY_TARGET,warrior.DECLARED_F,
                   pathlib.Path(folder)/"b"/"result.json",phase="seed")
            c=v93.request(dual,FURY_TARGET,warrior.DECLARED_F,
                   pathlib.Path(folder)/"c"/"result.json",phase="confirm")
            self.assertEqual(a["v092_final_T"],3414)
            self.assertEqual(b["v092_final_T"],3382)
            self.assertNotEqual(a["case_key"],b["case_key"])
            self.assertNotEqual(a["case_key"],c["case_key"])
            self.assertEqual(a["v093_session_digest"],
                             v93.request(dual,FURY_TARGET,warrior.DECLARED_F,
                             pathlib.Path(folder)/"d"/"result.json",
                             phase="seed")["v093_session_digest"])

    def test_bad_anchors_and_wrong_session_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx=self.make(folder)
            req=v93.request(ctx,FURY_TARGET,warrior.DECLARED_F,
                             pathlib.Path(folder)/"r.json",phase="seed")
            obs=simulated_result(req,200000,700)
            projected=v93.project_native_for_v065(req,obs)
            with self.assertRaisesRegex(v93.AdaptiveBridgeBlocked,
                                        "NATIVE_ANCHORS_REQUIRED"):
                v93.start_scout(ctx,[],scout_max=1)
            with self.assertRaises(v065.SchedulerBlocked):
                v93.start_scout(ctx,[dict(projected,target=req["target"])],
                                scout_max=1)
            state=v93.start_scout(ctx,[projected],scout_max=1)
            plan=v93.next_scout(ctx,state,warrior.DECLARED_F,
                                 pathlib.Path(folder)/"scout"/"result.json")
            altered=copy.deepcopy(plan["request"])
            altered["v093_session_digest"]="wrong"
            with self.assertRaisesRegex(v93.AdaptiveBridgeBlocked,
                                        "SCOUT_ANOTHER_SESSION"):
                v93.accept_scout(ctx,state,altered,
                          simulated_result(plan["request"],201000,600))

if __name__=="__main__":unittest.main()
