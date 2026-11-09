"""P3-HAJ one-source local web HTTP -> v293 -> actual SimC, tightly bounded.

This is NOT a real click in the user's Windows browser. It exercises the
actual FastAPI endpoints/worker with original same-build v216 native source.
No private user profile or effect-engine checks; Ret default public fixture.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import pathlib
import shutil
import time
import zipfile

from fastapi.testclient import TestClient

import v106_user_session_controller as users
import v113_local_web_api as web
import v213_source_to_catalog as catalog


class WebLiveBlocked(RuntimeError):
    pass


def need(ok,reason):
    if not ok:raise WebLiveBlocked(reason)


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def response(client,method,path,*,payload=None):
    headers={"x-simc-local-token":"p3-haj-one-test-token",
             "origin":"http://127.0.0.1:8765"}
    if method=="GET":
        r=client.get(path,headers=headers)
    else:
        r=client.post(path,headers=headers,json=payload if payload is not None else {})
    if r.status_code!=200:
        try:
            error=r.json().get("detail",{})
            error_code=error.get("code") if isinstance(error,dict) else str(error)
        except (ValueError,TypeError):
            error_code="INVALID_HTTP_ERROR_BODY"
        raise WebLiveBlocked("HTTP_%d_%s_%s"%(r.status_code,path,error_code))
    return r.json()


def finish(client,session,timeout=360):
    url="/api/v1/sessions/%s/longrun/status"%session
    stop=time.monotonic()+timeout
    while time.monotonic()<stop:
        progress=response(client,"GET",url)
        if not progress.get("active"):
            state=progress["progress"]["worker"]["status"]
            need(state not in ("BLOCKED_OR_PARTIAL","QUEUED","RUNNING"),
                 "LONGRUN_WORKER_DID_NOT_COMPLETE_SUCCESSFULLY:"+str(state))
            return progress
        time.sleep(0.25)
    raise WebLiveBlocked("LONGRUN_WORKER_TIMEOUT")


def save_cases(root,session,output_file):
    import v293_local_longrun_session as longrun
    saved=longrun.config(root/session)
    need(saved is not None,"MISSING_SEALED_LONGRUN_CONFIG")
    output=longrun.stage_path(root/session,saved["native_budget"])/"simc_results"
    files=["V291_SESSION.json","V291_JOURNAL.jsonl",
           "V291_RESULT.json","V291_PROGRESS.json"]
    cases=sorted(output.glob("cases/case_*/*"))
    for name in files:
        need((output/name).is_file(),"MISSING_NATIVE_EVIDENCE:"+name)
    allowed={"input.simc","result.json","native_receipt.json"}
    cases=[p for p in cases if p.is_file() and p.name in allowed]
    need(len(cases)>=6,"LESS_THAN_TWO_VERIFIABLE_NATIVE_CASES")
    b=0
    with zipfile.ZipFile(output_file,"x",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in [output/name for name in files]+cases:
            length=p.stat().st_size
            b+=length
            need(length<=20_000_000 and b<=50_000_000,
                 "BOUNDED_NATIVE_EVIDENCE_SIZE_EXCEEDED")
            z.write(p,p.relative_to(output).as_posix())
    return {"name":str(output_file),"sha256":digest(output_file),
            "native_case_files":len(cases),"uncompressed_bytes":b}


@contextlib.contextmanager
def verified_current_catalog(original,game_build):
    path=pathlib.Path(__file__).resolve().parents[1]/"data"/"current_season_source_to_catalog.json"
    source=pathlib.Path(original).resolve(strict=True)
    need(source.is_file() and not source.is_symlink(),
         "VERIFIED_V216_CURRENT_SOURCE_CATALOG_REQUIRED")
    source_raw=source.read_bytes()
    doc=json.loads(source_raw)
    catalog.verify_catalog(doc)
    need(doc.get("game_build")==game_build,
         "NO_CROSS_BUILD_SEASON_CATALOG_REUSE")
    need(not path.exists(),"WEB_PACKAGE_SOURCE_ALREADY_PRESENT")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(source_raw)
    try:
        yield {"game_build":game_build,
               "source_catalog_sha256":hashlib.sha256(source_raw).hexdigest(),
               "source_from":"VERIFIED_ORIGINAL_V216_NEW_SEASON_BUILD"}
    finally:
        if path.exists() and path.read_bytes()==source_raw:
            path.unlink()


def execute(root,binary,revision,game_build,environment_result,*,receipt_file):
    root=pathlib.Path(root).resolve()
    compilation=environment_result.get("source_compilation") or {}
    candidate=compilation.get("source_catalog_path")
    need(type(candidate) is str and candidate,
         "V216_COMPILED_SOURCE_CATALOG_MISSING")
    record={"schema":"p3_haj_real_local_web_native_e2e_v1",
            "status":"NOT_STARTED","native_ceiling":4,
            "real_browser_click_tested":False,
            "web_layer":"FASTAPI_LOCAL_TESTCLIENT_AND_REAL_SUBPROCESS",
            "new_native_dps_calls":0,
            "existing_environment_native_calls_excluded":True}
    receipt_file=pathlib.Path(receipt_file)
    try:
        with verified_current_catalog(candidate,game_build) as source:
            record["catalog"]=source
            app=web.create_app(root=root,token="p3-haj-one-test-token")
            # Match the real season Build -> same-process local web flow.
            # Recheck the pre-existing v217/v212 install before profile admission.
            app.state.jobs.remember_verified_fresh_environment(environment_result)
            controls=users.standard_controls(("paladin","retribution"))
            controls["race"]="dwarf"
            args={"controls":controls,"binary":str(pathlib.Path(binary).resolve()),
                  "revision":revision,"current_season_product":True,
                  "max_native_calls":12,
                  "max_new_native_this_invocation":1,
                  "max_elapsed_seconds":360}
            with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                prepared=response(client,"POST","/api/v1/longrun/prepare",
                                  payload=args)
                need(prepared["status"]=="LONGRUN_SOURCE_PREPARED_NO_DPS_NATIVE",
                     "WEB_PREPARE_NO_DPS_NATIVE_NOT_OBSERVED")
                session=prepared["session_id"]
                record["session_id"]=session
                record["prepare_status"]=prepared["status"]
                record["static_L_native_calls"]=prepared.get(
                    "static_L_native_calls_this_start",0)
                need(record["static_L_native_calls"]==0,
                     "UNEXPECTED_SPECIAL_L_NATIVE")
                started=response(client,"POST","/api/v1/sessions/"+session+
                                 "/longrun/resume",
                                 payload={"max_new_native_this_invocation":1,
                                          "max_elapsed_seconds":360})
                need(started["max_new_native_this_invocation"]==1,
                     "WEB_START_BUDGET_DRIFT")
                record["started_status"]=started["status"]
                after_first=finish(client,session)
                need(after_first["progress"]["completed_jobs"]==1 and
                     after_first["progress"]["native_attempts"]==1,
                     "WEB_FIRST_NATIVE_NOT_CHECKPOINTED")
                first_result=response(client,"GET",
                    "/api/v1/sessions/"+session+"/longrun/result")
                need(first_result["native_calls_cumulative"]==1,
                     "WEB_FIRST_RESULT_NATIVE_COUNT_DRIFT")
                record["first_case_new_native"]=1
                resumed=response(client,"POST",
                    "/api/v1/sessions/"+session+"/longrun/resume",
                    payload={"max_new_native_this_invocation":2,
                             "max_elapsed_seconds":360})
                record["resume_request_status"]=resumed["status"]
                # Cancellation may race with a very fast 35-iteration SimC.
                try:
                    cancelled=response(client,"POST",
                        "/api/v1/sessions/"+session+"/longrun/cancel")
                    record["cancel_observed"]=cancelled["status"]
                except WebLiveBlocked as exc:
                    if "HTTP_409_" not in str(exc):
                        raise
                    record["cancel_observed"]="NOT_OBSERVED_ALREADY_EXITED"
                after_resume=finish(client,session)
                count=after_resume["progress"]["completed_jobs"]
                need(1<=count<=3,"WEB_RESUME_CASE_CEILING_DRIFT")
                if count<2:
                    record["cancel_before_second_native"]=True
                    response(client,"POST",
                        "/api/v1/sessions/"+session+"/longrun/resume",
                        payload={"max_new_native_this_invocation":1,
                                 "max_elapsed_seconds":360})
                    after_resume=finish(client,session)
                    count=after_resume["progress"]["completed_jobs"]
                need(2<=count<=4,"WEB_RESUME_NOT_VERIFIED")
                record["case_count_after_resume"]=count
                record["new_native_dps_calls"]=count
                before_cache=count
                cache=response(client,"POST",
                    "/api/v1/sessions/"+session+"/longrun/cache-only")
                need(cache["max_new_native_this_invocation"]==0,
                     "WEB_CACHE_ONLY_ALLOWED_NEW_NATIVE")
                final_status=finish(client,session)
                need(final_status["progress"]["completed_jobs"]==before_cache
                     and final_status["progress"]["native_attempts"]==before_cache,
                     "WEB_CACHE_ONLY_MUTATED_NATIVE_HISTORY")
                final=response(client,"GET",
                    "/api/v1/sessions/"+session+"/longrun/result")
                user_result=final["user_result"]
                top=user_result["observed_first_choice"]
                total=user_result["final_T"]
                vector=top["absolute_rating_T"]
                need(user_result["confidence_level"]==0.95
                     and user_result["global_optimum_proven"] is False
                     and sum(vector.values())==total
                     and all(v*2<total for v in vector.values())
                     and final["native_calls_cumulative"]==count,
                     "WEB_RESULT_STATISTICS_OR_CHMV_DRIFT")
                record["reported"]={
                    "native_calls_cumulative":count,
                    "cache_only_new_native":0,
                    "observed_chmv":vector,
                    "final_T":total,
                    "dps_mean":top["observed_dps_mean"],
                    "sem":top["simc_sem"],
                    "confidence_level":user_result["confidence_level"],
                    "global_optimum_proven":False,
                    "selected_pair_direction_supported_95":
                        user_result["confirmation_pair_direction_supported_at_95"]}
                record["native_evidence"]=save_cases(
                    root,session,pathlib.Path("p3_haj_web_native_evidence.zip"))
                record["status"]="PASS_REAL_FASTAPI_LONGRUN_PREPARE_RUN_RESUME_CACHE"
    except Exception as exc:
        record["status"]="BLOCKED_OR_PARTIAL"
        record["error_type"]=type(exc).__name__
        record["error_code"]=str(exc)[:300]
        raise
    finally:
        receipt_file.write_text(json.dumps(record,sort_keys=True,indent=2,
                             ensure_ascii=False,allow_nan=False)+"\n",encoding="utf8")
    return record
