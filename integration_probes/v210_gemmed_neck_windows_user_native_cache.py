#!/usr/bin/env python3
"""v210 one real Windows selected special -> static L1 -> DPS6 -> cache6.

Exact source-listed, internally gem-decorated neck on one current-season Ele Shaman at
ilvl331. No new optimizer, no complete 26-specialization certification.
"""
from __future__ import annotations
import argparse,hashlib,json,math,pathlib,sys,tempfile
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as sessions
import v113_local_web_api as web
import v208_internal_exact_special_L_hydrator as exact_L
import v046_static_item_cache as static
import v062_static_budget_bridge as budget
import v098_target_user_scenario_bootstrap as bootstrap

def check(ok,why):
    if not ok:raise RuntimeError("V210_"+why)

def okay(response,phase):
    check(response.status_code==200,
          phase+"_HTTP_"+str(response.status_code)+"_"+str(response.json().get("detail")))
    return response.json()

def run(binary,out):
    check(sys.platform=="win32","WINDOWS_ONLY")
    binary=binary.resolve()
    check(binary.is_file() and binary.name.lower()=="simc.exe" and
          exact_L.sha_file(binary)=="0ad16368cd1effb19c793dbce63518ccb72fec89c72f6ef75d9afca239a039e8",
          "OFFICIAL_PINNED_EXE_REQUIRED")
    out=out.resolve();out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="v210-one-user-",dir=out) as tmp:
        root=pathlib.Path(tmp)
        app=web.create_app(root=root/"runs",token="v210-local-only")
        client=TestClient(app,base_url="http://127.0.0.1:8765")
        headers={"x-simc-local-token":"v210-local-only",
                 "origin":"http://127.0.0.1:8765"}
        c=sessions.standard_controls(("shaman","elemental"))
        c["ilevel"]=331
        c["special_items"]=[{"slot":"neck","item_id":268250,"options":{}}]
        staged=bootstrap.build(sessions.user_scenario(c),
            root/"prebudget-source",binary,"710c2408bf",
            current_season_product=True,static_special_probe_only=True)
        check(len(staged["special_rows"])==1 and
              staged["special_rows"][0]["slot"]=="neck" and
              staged["special_rows"][0]["item_id"]==268250 and
              "gem_id" in staged["special_rows"][0]["options"],
              "SOURCE_NECK_GEM_MUST_BE_PRESENT")
        actual=staged["special_rows"][0]
        bare=budget.undecorated_special(actual)
        check("gem_id" not in bare["options"] and
              bare["item_id"]==actual["item_id"] and
              bare["ilevel"]==actual["ilevel"],
              "BARE_STATIC_IDENTITY_MUST_PRESERVE_ID_AND_LEVEL")
        params={"controls":c,"binary":str(binary),"revision":"710c2408bf",
                "current_season_product":True,"static_cache":None}
        # Plan stays Native zero; user has not authorized static Native yet.
        unprepared=client.post("/api/v1/sessions/plan",headers=headers,json=params)
        check(unprepared.status_code==422 and
              unprepared.json()["detail"]["code"]==
                 "V106_SPECIAL_EQUIPMENT_REQUIRES_EXACT_STATIC_CACHE",
              "ZERO_NATIVE_PREVIEW_MUST_FAIL_WITH_EXACT_L_REQUIRED")
        started=okay(client.post("/api/v1/sessions/start",
                         headers=headers,json=params),"START_WITH_STATIC")
        check(started["status"]=="WORKER_STARTED" and
              started["static_L_native_calls_this_start"]==1 and
              started["native_attempt_ceiling_cumulative"]==6,
              "ONE_STATIC_L_AND_SIX_DPS_BOUNDS_REQUIRED")
        sid=started["session_id"]
        session=root/"runs"/sid
        manifest=json.loads((session/"generated"/"manifest.json").read_text("utf8"))
        selected_cache=pathlib.Path(manifest["static_cache_json"])
        records=static.load(selected_cache)
        ident=budget.exact_identity(bare)
        selected=records["variants"].get(static.digest(ident))
        check(selected is not None and
              selected["source_kind"]=="NATIVE_JSON2_RESOLVED_VARIANT" and
              sum(selected["static"]["secondary"].values())>0 and
              static.digest(budget.exact_identity(actual)) not in records["variants"],
              "BARE_NATIVE_L_ONLY_NO_DECORATED_STATS_CACHED")
        L=selected["static"]["secondary"]
        complete_profile=(session/"generated"/"profile.simc").read_text("utf8")
        necklace=next(x for x in complete_profile.splitlines() if x.startswith("neck="))
        check("gem_id=" in necklace and "id=268250" in necklace,
              "COMPLETE_GEMMED_DPS_PROFILE_MUST_BE_PRESERVED")
        original_cache_sha=exact_L.sha_file(selected_cache)
        worker=app.state.jobs.children[sid]
        check(worker.wait(timeout=600)==0,
              "REAL_WINDOWS_SELECTED_SPECIAL_DPS_WORKER_FAILED")
        status=okay(client.get("/api/v1/sessions/"+sid+"/status",
                               headers=headers),"STATUS")
        check(status["active"] is False and status["result_ready"] is True,
              "DPS_RESULT_NOT_READY")
        result=okay(client.get("/api/v1/sessions/"+sid+"/result",
                               headers=headers),"RESULT")
        user=result["user_result"];best=user["observed_first_choice"]
        check(result["native_calls_cumulative"]==6 and
              result["base_B"]==3110 and result["final_T"]==3142 and
              user["confidence_level"]==0.95 and
              user["global_optimum_proven"] is False,
              "DPS_SIX_OR_INCLUSIVE_T_OR_95")
        check(math.isfinite(best["observed_dps_mean"]) and best["observed_dps_mean"]>0
              and math.isfinite(best["simc_sem"]) and best["simc_sem"]>=0,
              "NATIVE_DPS_AND_SEM_REQUIRED")
        rated=best["absolute_rating_T"]
        check(sum(rated.values())==3142 and
              all(rated[k]>=L[k] for k in L),
              "BARE_FIXED_L_FLOOR_OR_ABSOLUTE_T_MISMATCH")
        cache_request=okay(client.post("/api/v1/sessions/"+sid+"/cache-only",
                              headers=headers,json={}),"CACHE_START")
        check(cache_request["new_native_execution_permitted"] is False,
              "CACHE_ONLY_NO_NEW_NATIVE")
        repeat_worker=app.state.jobs.children[sid]
        check(repeat_worker.wait(timeout=180)==0,
              "CACHE_ONLY_WORKER_FAILED")
        replay=okay(client.get("/api/v1/sessions/"+sid+"/result",
                               headers=headers),"CACHE_RESULT")
        check(replay["native_calls_cumulative"]==6 and
              replay["cache_hits_this_run"]==6 and
              replay["user_result"]==user and
              exact_L.sha_file(selected_cache)==original_cache_sha,
              "CACHED_DPS_OR_STATIC_L_CHANGED")
        proof=json.loads((session/"V112_CACHE_REPLAY_RECEIPT.json")
                         .read_text("utf8"))
        check(proof["additional_native_calls"]==0 and
              proof["cache_hits_this_run"]==6 and
              len(proof["native_json2_sha256"])==6,
              "SIX_JSON2_HASH_REPLAY")
        static_repeat=exact_L.hydrate(
            sessions.user_scenario(c),root/"runs",binary,"710c2408bf",
            existing=selected_cache)
        check(static_repeat["native_new_calls"]==0,
              "SECOND_STATIC_NATIVE_FORBIDDEN")
        record={
         "schema":"v210_one_gemmed_special_bare_L_windows_real_native_v1",
         "status":"PASS_GEMMED_SPECIAL_BARE_L1_DPS6_CACHE6_WINDOWS_REAL_NATIVE",
         "scope":"shaman/elemental ilvl331 neck item268250 source gemmed",
         "selected_full_item_identity":budget.exact_identity(actual),
         "measured_bare_item_identity":ident,
         "full_dps_neck_preserved_with_gem":True,
         "binary_sha256":exact_L.sha_file(binary),
         "source_profile_sha256":hashlib.sha256(
             (session/"generated"/"profile.simc").read_bytes()).hexdigest(),
         "static_L_native_new_calls":1,"static_L_new_on_replay":0,
         "static_L_native_json2_sha256":selected["metadata"]["native_json_sha256"],
         "static_L":dict(L),
         "static_cache_snapshot_sha256":original_cache_sha,
         "base_B":3110,"final_T":3142,
         "dps_new_native_calls":6,"dps_cache_hits":6,
         "new_native_calls_on_dps_replay":0,
         "six_native_json2_sha256":proof["native_json2_sha256"],
         "observed_dps":best["observed_dps_mean"],"observed_sem":best["simc_sem"],
         "confidence_level":0.95,"global_optimum_proven":False,
         "not_26_specs_or_all_decorated_specials_proven":True}
        (out/"V210_GEMMED_NECK_BARE_L1_DPS6_CACHE6_RECEIPT.json").write_text(
            json.dumps(record,sort_keys=True,indent=2)+"\n",encoding="utf8")
        print("V210_GEMMED_NECK_BARE_L1_DPS6_CACHE6_PASS",json.dumps(
            {k:record[k] for k in ("static_L","base_B","final_T",
             "observed_dps","observed_sem")},sort_keys=True),flush=True)
        return 0

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--simc",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    a=p.parse_args();raise SystemExit(run(a.simc,a.out))
