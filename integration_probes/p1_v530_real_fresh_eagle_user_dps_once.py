#!/usr/bin/env python3
"""v530: one real v212 fresh USER six-case SimC session wearing 7967 E0.

Reuses v529 exact v528 source/native proof; v113/v098/v096/v106/v094.
Runs NO AI, NO proc emulator, NO new optimizer, and does not generalize
7967 to other item builds/profiles or approve positive-E enchants.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,re,sys,tempfile,zipfile
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v113_local_web_api as web
import v529_current_season_eagle_E0_bridge as eagle
import p1_v524_m1_m2_source_owner_once as original
import p1_v525_real_option_matrix_once as fixed
from integration_probes import p3_haj_real_local_web_native_e2e as owner

SCHEMA="p1_v530_actual_70783_original_E0_enchant_user_dps_v1"
def check(ok,reason):
    if not ok:raise RuntimeError("V530_"+reason)
def digest(path):
    with pathlib.Path(path).open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()
def http(client,method,uri,payload=None):
    headers={"x-simc-local-token":"v530-one-user-native-token",
             "origin":"http://127.0.0.1:8765"}
    response=client.get(uri,headers=headers) if method=="GET" else client.post(
        uri,json=payload if payload is not None else {},headers=headers)
    if response.status_code!=200:
        detail=response.json().get("detail") or {}
        code=detail.get("code") if type(detail) is dict else str(detail)
        raise RuntimeError("V530_HTTP_"+str(response.status_code)+"_"+
                           str(code)[:100])
    return response.json()
def save(p,doc):
    p.write_text(json.dumps(doc,ensure_ascii=False,sort_keys=True,
        indent=2,allow_nan=False)+"\n",encoding="utf8")
def error(exc):
    return {"error_type":type(exc).__name__,
        "stable_error_codes":re.findall(r"[A-Z][A-Z0-9_]{5,120}",str(exc))[:6]}

def run(binary,out):
    binary=pathlib.Path(binary).resolve()
    out=pathlib.Path(out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    path=out/"V530_ACTUAL_FRESH_E0_USER_DPS.json"
    r={"schema":SCHEMA,"status":"NOT_RUN","game_build":original.BUILD,
       "revision":original.REV,"simc_binary_sha256":original.EXE_SHA,
       "runtime_AI_calls":0,"simc_effect_and_APL_owner":True,
       "new_environment_native":None,"new_DPS_native":0,
       "user_selected_enchant_id":7967,
       "fixed_E":{"crit_rating":0,"haste_rating":0,
                  "mastery_rating":0,"versatility_rating":0},
       "full_product_e2e":"PENDING",
       "global_optimum_proven":False}
    def checkpoint():save(path,r)
    checkpoint()
    try:
        check(sys.platform=="win32","ONLY_OFFICIAL_WINDOWS_SIMC")
        check(binary.is_file() and binary.name.lower()=="simc.exe"
            and digest(binary)==original.EXE_SHA,
            "ORIGINAL_BINARY_SHA_MISMATCH")
        check(original.EphemeralActionsCredentials().load() is not None,
              "ORIGINAL_SOURCE_CREDENTIALS_MISSING")
        eagle.evidence()
        with tempfile.TemporaryDirectory(prefix="v530-real-eagle-",dir=out) as t:
            root=pathlib.Path(t)/"runs";root.mkdir()
            jobs=web.LocalJobs(root,source_credential_store=
                original.EphemeralActionsCredentials())
            myth=jobs.discover_season_myth_target(original.BUILD)
            check(myth.get("target_ilevel")==334 and
                  myth.get("status")==
                  "MYTH_TARGET_CANDIDATE_FROM_MATCHED_WAGO_V163_SOURCE",
                  "ACTUAL_M1_SOURCE_NOT_VERIFIED")
            env=jobs.build_season_environment(
                game_build=original.BUILD,target_ilevel=334,
                auto_initial_core_build=True,
                auto_initial_core_simc_binary=str(binary),
                simc_revision_hint=original.REV,
                existing_special_gem_id=None,source_target_socket_count=4,
                auto_myth_target_source_build=original.BUILD,
                auto_myth_target_source_sha256=myth["currency_csv_sha256"])
            r["new_environment_native"]=env.get("native_calls")
            check(env.get("environment_installed") is True and
                  env.get("environment_ready") is True and
                  env.get("G")==2850 and env.get("J")==92
                  and env.get("F")==165 and env.get("B")==3107
                  and env.get("T")==3107 and sum(env["O"].values())==0,
                  "REAL_M2_70783_BASE_BUDGET_DRIFT")
            installed=env["source_compilation"][
                "verified_environment_install"]["manifest_sha256"]
            r["installed_v212_manifest_sha256"]=installed;checkpoint()
            with owner.verified_current_catalog(
                env["source_compilation"]["source_catalog_path"],
                original.BUILD):
                app=web.create_app(root=root,token="v530-one-user-native-token")
                app.state.jobs.remember_verified_fresh_environment(env)
                base=fixed.controls(fixed.TRINKETS[0])
                enchanted=fixed.controls(fixed.TRINKETS[0],
                                         enchant=7967)
                def payload(controls):
                    return {"controls":controls,"binary":str(binary),
                        "revision":original.REV,"current_season_product":True,
                        "installed_season_game_build":original.BUILD,
                        "installed_manifest_sha256":installed,
                        "user_socket_total":4}
                with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                    ordinary=http(client,"POST","/api/v1/sessions/plan",
                                  payload(base))
                    check(ordinary.get("status")=="READY_ZERO_NATIVE",
                          "BASE_PROFILE_PLAN_NOT_READY")
                    r["base_session_id"]=ordinary["session_id"]
                    original_source=(root/ordinary["session_id"]/
                                     "generated"/"profile.simc")
                    r["original_unenchanted_profile_sha256"]=digest(
                        original_source)
                    check(r["original_unenchanted_profile_sha256"]==
                          eagle.BASE_SHA,
                          "UNENCHANTED_REAL_V528_PROFILE_NOT_IDENTICAL")
                    chosen=http(client,"POST","/api/v1/sessions/plan",
                                payload(enchanted))
                    check(chosen.get("status")=="READY_ZERO_NATIVE" and
                          chosen["session_id"]!=ordinary["session_id"] and
                          chosen["plan"]["base_B"]==
                          chosen["plan"]["final_T"]==3107,
                          "ENCHANTED_PLAN_IDENTITY_OR_E0_BUDGET_INVALID")
                    sid=chosen["session_id"]
                    r["enchant_session_id"]=sid
                    actual_input=(root/sid/"generated"/"profile.simc")
                    raw=actual_input.read_text(encoding="utf8")
                    ring=[x for x in raw.splitlines() if
                          x.startswith("finger1=")]
                    check(len(ring)==1 and
                          ring[0].count("enchant_id=7967")==1 and
                          "id=268266" in ring[0],
                          "FINGER1_ENCHANT_NOT_EXACTLY_SERIALIZED")
                    r["actual_enchanted_source_sha256"]=digest(actual_input)
                    # The public v113 plan intentionally projects only
                    # user-safe class/spec/B/T. Read the already source-sealed
                    # v218/v098 output and original v096 plan on disk.
                    original_stage=root/sid/"generated"/"v098_bootstrap_result.json"
                    check(original_stage.is_file() and
                          not original_stage.is_symlink(),
                          "ORIGINAL_V098_SESSION_PROOF_MISSING")
                    stage=json.loads(original_stage.read_text("utf8"))
                    internal=stage.get("plan") or {}
                    r["observed_nonchmv_plan"]=internal.get(
                        "selected_nonchmv_enchant")
                    original_manifest=json.loads(
                        (root/sid/"generated"/"manifest.json").read_text("utf8"))
                    check(original_manifest.get(
                          "v206_source_classified_nonchmv_enchant_choice")==
                          eagle.CHOICE,
                          "ORIGINAL_V096_ENCHANT_MANIFEST_OPTION_MISSING")
                    check(r["observed_nonchmv_plan"] is not None and
                          r["observed_nonchmv_plan"]["static_CHMV_E"]==
                            eagle.ZERO,"PROVEN_E_ZERO_NOT_IN_ORIGINAL_V096_PLAN")
                    checkpoint()
                    started=http(client,"POST","/api/v1/sessions/start",
                                 payload(enchanted))
                    check(started.get("status")=="WORKER_STARTED" and
                          started.get("session_id")==sid and
                          started.get("static_L_native_calls_this_start",0)==0,
                          "ENCHANTED_USER_WORKER_NOT_STARTED")
                    exit_code=app.state.jobs.children[sid].wait(timeout=660)
                    r["worker_exit"]=exit_code
                    if exit_code!=0:
                        state=web.sessions.paths(root/sid)["state"]
                        if state.is_file():
                            d=json.loads(state.read_text(encoding="utf8"))
                            r["worker_error_codes"]=re.findall(
                                r"[A-Z][A-Z0-9_]{4,120}",
                                d.get("reason",""))[:6]
                        r["status"]="ACTUAL_ENCHANTED_DPS_WORKER_BLOCKED"
                        checkpoint()
                        return 2
                    observed=http(client,"GET",
                                  "/api/v1/sessions/"+sid+"/result")
                    result=observed["user_result"]
                    best=result["observed_first_choice"]
                    check(observed["native_calls_cumulative"]==6 and
                          observed["base_B"]==observed["final_T"]==3107
                          and result["confidence_level"]==0.95
                          and result["global_optimum_proven"] is False
                          and best["observed_dps_mean"]>0
                          and best["simc_sem"]>=0
                          and sum(best["absolute_rating_T"].values())==3107,
                          "EAGLE_NATIVE_DPS_SEM_95_BUDGET_DRIFT")
                    r["new_DPS_native"]=6
                    r["observed_first_dps"]=best["observed_dps_mean"]
                    r["observed_first_sem"]=best["simc_sem"]
                    r["observed_final_T"]=best["absolute_rating_T"]
                    r["confidence_level"]=result["confidence_level"]
                    result_root=root/sid/"generated"/"simc_results"
                    rows=sorted(result_root.rglob("input.simc"))
                    raws=sorted(result_root.rglob("result.json"))
                    proofs=sorted(result_root.rglob("native_receipt.json"))
                    check(len(rows)==len(raws)==len(proofs)==6,
                          "ORIGINAL_SIX_NATIVE_INPUT_JSON2_RECEIPTS_NOT_FOUND")
                    for p in rows:
                        text=p.read_text(encoding="utf8")
                        rings=[x for x in text.splitlines()
                               if x.startswith("finger1=")]
                        check(len(rings)==1 and
                              rings[0].count("enchant_id=7967")==1,
                              "ONE_ENCHANT_MISSING_ON_NATIVE_INPUT")
                    r["native_input_sha256"]=[digest(p) for p in rows]
                    r["native_JSON2_sha256"]=[digest(p) for p in raws]
                    r["native_receipt_sha256"]=[digest(p) for p in proofs]
                    with zipfile.ZipFile(out/"V530_ACTUAL_EAGLE_SIX_ORIGINAL_SIMC.zip",
                       "w",compression=zipfile.ZIP_DEFLATED,
                       compresslevel=6) as z:
                        for p in rows+raws+proofs:
                            z.write(p,p.relative_to(result_root))
                    r["original_native_zip_sha256"]=digest(
                        out/"V530_ACTUAL_EAGLE_SIX_ORIGINAL_SIMC.zip")
                    replay=http(client,"POST",
                                "/api/v1/sessions/"+sid+"/cache-only",{})
                    check(replay["new_native_execution_permitted"] is False
                          and app.state.jobs.children[sid].wait(timeout=180)==0,
                          "ENCHANTED_CACHE_REPLAY_ATTEMPTED_NATIVE")
                    replay_result=http(client,"GET",
                                       "/api/v1/sessions/"+sid+"/result")
                    check(replay_result["cache_hits_this_run"]==6
                          and replay_result["user_result"]==result,
                          "ENCHANTED_CACHE_REPLAY_STATISTICAL_DRIFT")
                    r["cache_only_hits"]=6
                    r["cache_only_new_native"]=0
                    r["status"]="PASS_ONE_REAL_SOURCE_LOCKED_E0_ENCHANT_6_DPS"
                    checkpoint()
                    return 0
    except Exception as exc:
        r["status"]="BLOCKED_SCOPE_OR_REAL_ENCHANT_EXECUTION"
        r["error"]=error(exc)
        checkpoint()
        return 3
    finally:
        print("V530_REAL_USER_E0 "+json.dumps({
           "status":r["status"],
           "worker_exit":r.get("worker_exit"),
           "observed_dps":r.get("observed_first_dps"),
           "new_DPS_native":r.get("new_DPS_native",0),
           "environment_native":r.get("new_environment_native"),
           "error":r.get("error"),
           "worker_error_codes":r.get("worker_error_codes") },
           ensure_ascii=False,sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--simc",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args()
    sys.exit(run(a.simc,a.out))
