"""One real selected special-gem install -> existing HTTP menu, DPS and cache.
No separate repeated v829 comparison job; this is the actual integrated flow."""
import argparse,json,pathlib,tempfile,time
from fastapi.testclient import TestClient
from p1_v769_incremental_environment_once import BUILD,REV,EphemeralActionsCredentials,digest
from p1_v802_selected_mixed_oil_once import observe_real_boundary,_safe_failure
import v113_local_web_api as web
import v293_local_longrun_session as longrun

TOKEN="v830-local-only"
SPECIAL=240983
FLASK=241324
def main():
    ap=argparse.ArgumentParser()
    for n in ("simc","identity","out"):ap.add_argument("--"+n,type=pathlib.Path,required=True)
    args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    report={"schema":"p1_v830_actual_selected_special_gem_product_once_v1",
            "status":"STARTED","game_build":BUILD,"revision":REV,
            "special_gem_id":SPECIAL,"socket_total":5,"target_ilevel":334,
            "full_product_e2e":"PENDING","global_optimum_proven":False,
            "dps_native":0,"environment_installed":False}
    def save(stage=None):
        if stage:report["stage"]=stage
        raw=json.dumps(report,sort_keys=True,ensure_ascii=True,allow_nan=False)
        (out/"V830_SELECTED_SPECIAL_GEM.json").write_text(raw+"\n","utf8")
        print("V830_RECEIPT "+raw,flush=True)
    def check(code,actual,expected):
        if actual!=expected:
            report["failed_comparison"]={"code":code,"actual":actual,"expected":expected}
            save()
            raise RuntimeError(code)
    def call(client,method,url,**kw):
        response=client.request(method,url,headers={"x-simc-local-token":TOKEN,
                  "origin":"http://127.0.0.1:8765"},**kw)
        if response.status_code!=200:
            detail=response.json().get("detail",{})
            report["http_blocker"]={"status":response.status_code,
                "code":detail.get("code") if isinstance(detail,dict) else None}
            save()
            raise RuntimeError("V830_ORIGINAL_HTTP_BLOCKED")
        return response.json()
    def wait(client,url):
        limit=time.monotonic()+420
        while time.monotonic()<limit:
            status=call(client,"GET",url+"/longrun/status")
            if not status.get("active"):
                p=status.get("progress") or {}
                worker=p.get("worker") or {}
                report["worker_status"]={"status":worker.get("status"),
                    "native_attempts":p.get("native_attempts"),
                    "completed_jobs":p.get("completed_jobs")}
                save()
                return p
            time.sleep(.5)
        raise RuntimeError("V830_NATIVE_TIMEOUT")
    try:
        binary=args.simc.resolve(strict=True)
        identity=json.loads(args.identity.read_text("utf-8-sig"))
        check("V830_BINARY_BUILD",identity["game_build"],BUILD)
        check("V830_BINARY_REV",identity["source_commit"],REV)
        check("V830_BINARY_SHA",digest(binary),identity["binary_sha256"])
        credentials=EphemeralActionsCredentials()
        if credentials.load() is None:raise RuntimeError("V830_CREDENTIALS_MISSING")
        with tempfile.TemporaryDirectory(prefix="v830-") as tmp:
            root=pathlib.Path(tmp)/"runs";root.mkdir()
            app=web.create_app(root=root,token=TOKEN,source_credential_store=credentials)
            jobs=app.state.jobs
            save("ONE_SELECTED_ACTUAL_BUILD")
            env=jobs.build_season_environment(game_build=BUILD,target_ilevel=334,
                native_G_binary=str(binary),consumable_native_binary=str(binary),
                auto_native_F_requested=True,selected_flask_item_id=FLASK,
                selected_oil_item_ids_by_hand={},existing_special_gem_id=SPECIAL,
                source_target_socket_count=5,simc_revision_hint=REV)
            comp=env.get("source_compilation") or {}
            progress=env.get("zero_history_build") or {}
            report.update(environment_native=env.get("native_calls"),
                environment_installed=env.get("environment_installed") is True,
                selected_socket_bonus_native=comp.get("selected_socket_bonus_native"),
                J_owner=(comp.get("original_J_F_verified_components_not_full_environment") or {}).get("J"),
                requires=progress.get("requires"))
            save()
            check("V830_INSTALL_READY",env.get("environment_ready"),True)
            check("V830_INSTALL_J",env.get("J"),92)
            check("V830_INSTALL_T",env.get("T"),3107)
            installed=comp["verified_environment_install"]
            sha=installed["manifest_sha256"]
            path=pathlib.Path(installed["stage_output_path"])
            before=digest(path)
            doc=json.loads(path.read_text("utf8"))
            scope=doc["official_J_physical_socket_source"]
            report["installed_sha256"]=sha
            report["installed_scope"]=scope
            save("VERIFIED_MENU_AND_RESTORE")
            with observe_real_boundary(report,root),TestClient(app,base_url="http://127.0.0.1:8765") as client:
                menu=call(client,"GET","/api/v1/verified-oil-loadouts",
                          params={"game_build":BUILD,"ilevel":334})
                matched=[x for x in menu["verified_gem_installs"]
                         if x["installed_manifest_sha256"]==sha and
                         x["special_gem_id"]==SPECIAL and x["socket_total"]==5]
                check("V830_AUTO_GEM_MENU",len(matched),1)
                report["menu_registered"]=True
                controls=web.sessions.standard_controls(("paladin","retribution"))
                controls.update(race="dwarf",oil_hands=[],final_T=None)
                request={"controls":controls,"binary":str(binary),"revision":REV,
                    "current_season_product":True,"installed_season_game_build":BUILD,
                    "installed_manifest_sha256":sha,"selected_flask_item_id":FLASK,
                    "user_socket_total":5,"user_special_gem_id":SPECIAL}
                req={**request,"max_native_calls":12,
                     "max_new_native_this_invocation":1,"max_elapsed_seconds":360}
                save("FIRST_USER_PREPARE")
                first=call(client,"POST","/api/v1/longrun/prepare",json=req)
                check("V830_PREPARE_STATUS",first.get("status"),"LONGRUN_SOURCE_PREPARED_NO_DPS_NATIVE")
                check("V830_PREPARE_DPS",first.get("new_dps_native_calls"),0)
                sid=first["session_id"]
                plan=call(client,"POST","/api/v1/sessions/plan",json=request)
                check("V830_PLAN_READY",plan.get("status"),"READY_ZERO_NATIVE")
                check("V830_PLAN_T",plan["plan"]["final_T"],3107)
                check("V830_PLAN_SESSION",plan["session_id"],sid)
                replay=call(client,"POST","/api/v1/longrun/prepare",json=req)
                check("V830_REPREPARE_SESSION",replay["session_id"],sid)
                url="/api/v1/sessions/"+sid
                def hashes():
                    folder=root/sid;cfg=longrun.config(folder)
                    cases=longrun.stage_path(folder,cfg["native_budget"])/"simc_results"/"cases"
                    return sorted(digest(p) for p in cases.glob("case_*/native/native_receipt.json"))
                for n in (1,2):
                    save("DPS_NATIVE_"+str(n))
                    call(client,"POST",url+"/longrun/resume",
                         json={"max_new_native_this_invocation":1,"max_elapsed_seconds":360})
                    p=wait(client,url)
                    report["dps_native"]=p["native_attempts"]
                    check("V830_DPS_ATTEMPTS",p["native_attempts"],n)
                    check("V830_DPS_COMPLETED",p["completed_jobs"],n)
                original=hashes()
                check("V830_TWO_RECEIPTS",len(original),2)
                call(client,"POST",url+"/longrun/cache-only",json={})
                p=wait(client,url)
                check("V830_CACHE_NATIVE",p["native_attempts"],2)
                check("V830_CACHE_BYTES",hashes(),original)
                check("V830_INSTALL_BYTES",digest(path),before)
                result=call(client,"GET",url+"/longrun/result")["user_result"]
                best=result["observed_first_choice"]
                check("V830_RESULT_CONFIDENCE",result["confidence_level"],.95)
                check("V830_RESULT_T",sum(best["absolute_rating_T"].values()),3107)
                if not best["observed_dps_mean"]>0 or not best["simc_sem"]>=0:
                    raise RuntimeError("V830_RESULT_DPS_SEM")
                report.update(status="PASS_ACTUAL_SPECIAL_GEM_INSTALL_TWO_DPS_CACHE",
                    dps=best["observed_dps_mean"],sem=best["simc_sem"],
                    rating=best["absolute_rating_T"],cache_only_new_native=0)
                save()
        return 0
    except Exception as exc:
        report["status"]="BLOCKED_ACTUAL_SPECIAL_GEM_PRODUCT"
        report["failure"]=_safe_failure(exc)
        save()
        return 2

if __name__=="__main__":
    raise SystemExit(main())
