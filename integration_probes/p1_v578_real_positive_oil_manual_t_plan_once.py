#!/usr/bin/env python3
"""v578: one original same-build source-owned physical-oil O-positive
v113/v216/v222/v212 Build -> v217 exact installed SHA -> v113 user
manual-T plan. NO DPS worker and NO automatic 64-case optimizer. Distinguish
original source truth from historical O synthetic fixtures.

Actual Native: original v216 internal G / selected F / selected scaled-O
only, bounded to a single build. Auth credentials consumed in memory only.
"""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib,re,subprocess,sys,tempfile
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v113_local_web_api as web
import v212_environment_manifest as installed
import v216_environment_build_coordinator as coordinator
import v289_retail_live_build_source as retail
from integration_probes import p3_haj_real_local_web_native_e2e as owner

BUILD="12.1.5.70783"
REV="de11f57df75dda668bae6ac7043a43b98831fa96"
EXE_SHA="1fc927d2be7f1b6064c75f004b5b22245b064a6b3e56e572af4048ba822a986d"
OIL_ITEM=243734
FLASK_ITEM=241324
MANUAL_T=3500
MAX_ENV_NATIVE=12
SCHEMA="p1_v578_one_actual_70783_selected_physical_oil_installed_manual_T_plan_v1"
FILE="V578_ACTUAL_POSITIVE_O_INSTALLED_TO_MANUAL_T_PLAN_COMPACT.json"
KEYS=("BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET","WCL_CLIENT_ID","WCL_CLIENT_SECRET")

class Credentials:
    def load(self):
        data={k:os.environ.get(k,"") for k in KEYS}
        return data if all(data.values()) else None

def digest(path):
    sha=hashlib.sha256()
    with pathlib.Path(path).open("rb") as stream:
        for blob in iter(lambda:stream.read(1<<20),b""):
            sha.update(blob)
    return sha.hexdigest()

def need(ok,reason):
    if not ok:raise RuntimeError("V578_"+reason)

def code(exc):
    text=str(exc).split(":",1)[0].split("\n",1)[0]
    if re.fullmatch("[A-Z][A-Z0-9_]{4,110}",text):return text
    return type(exc).__name__

def run(binary,out):
    binary=pathlib.Path(binary).resolve(strict=True)
    out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    receipt=out/FILE
    report={
      "schema":SCHEMA,"status":"STARTED","build":BUILD,"revision":REV,
      "binary_sha256":EXE_SHA,"target_ilevel":334,
      "selected_flask_item_id":FLASK_ITEM,
      "selected_oil_item_ids_by_hand":{"main_hand":OIL_ITEM},
      "manual_final_T":MANUAL_T,
      "actual_environment_native":None,"actual_user_dps_native":0,
      "actual_environment_ready":False,"installed_manifest_sha256":None,
      "user_plan_ready":False,"result_95_or_dps_measured":False,
      "global_optimum_proven":False,"source_approval_synthetic":False,
      "credentials_written_to_receipt":False,"official_full_product_e2e":"PENDING"}
    def save():
        receipt.write_text(json.dumps(report,ensure_ascii=False,
            sort_keys=True,indent=2,allow_nan=False,default=str)+"\n",
            encoding="utf8")
    save()
    try:
        need(sys.platform=="win32" and binary.name.lower()=="simc.exe" and
             digest(binary)==EXE_SHA,
             "PINNED_WINDOWS_SAME_BUILD_BINARY_REQUIRED")
        need(os.environ.get("SIMC_PINNED_SOURCE_COMMIT")==REV and
             os.environ.get("SIMC_PINNED_GAME_BUILD")==BUILD,
             "SAME_BUILD_REVISION_REQUIRED")
        need(Credentials().load() is not None,
             "BLIZZARD_WCL_SOURCE_CREDENTIALS_MISSING")
        banner=subprocess.run([str(binary)],input="",
            capture_output=True,text=True,errors="replace",
            cwd=binary.parent,timeout=30)
        need(banner.returncode==0 and
             BUILD in (banner.stdout+"\n"+banner.stderr),
             "ORIGINAL_SIMC_BINARY_GAME_BUILD_DRIFT")
        live=retail.discover(region="KR")
        report["live_build"]=live.get("game_build")
        report["live_source_sha256"]=live.get("source_sha256")
        if live.get("game_build")!=BUILD:
            report["status"]="PENDING_LIVE_RETAIL_BUILD_CHANGED"
            report["first_blocker"]="ACTIVE_RETAIL_BUILD_NOT_PINNED_SIMC"
            save()
            return 2
        with tempfile.TemporaryDirectory(prefix="v578-once-oil-",dir=out) as temp:
            root=pathlib.Path(temp)/"runs";root.mkdir()
            jobs=web.LocalJobs(root,source_credential_store=Credentials())
            # No M1 discovery/Native repeat: user intentionally entered
            # verified same-build manual target level 334.
            result=jobs.build_season_environment(
                game_build=BUILD,target_ilevel=334,
                native_G_binary=str(binary),
                consumable_native_binary=str(binary),
                auto_native_F_requested=True,
                auto_native_O_requested=True,
                selected_flask_item_id=FLASK_ITEM,
                selected_oil_item_ids_by_hand={"main_hand":OIL_ITEM},
                source_target_socket_count=4,
                existing_special_gem_id=None,
                simc_revision_hint=REV)
            report["actual_environment_native"]=result.get("native_calls")
            report["build_stage_status"]=(result.get("source_compilation") or {}).get("status")
            report["build_first_requires"]=(result.get("zero_history_build") or {}).get("requires",[])[:7]
            report["reported_original_budget"]={
                k:result.get(k) for k in ("G","J","F","O","B","T")}
            report["actual_environment_ready"]=result.get("environment_ready") is True
            report["environment_installed"]=result.get("environment_installed") is True
            install=(result.get("source_compilation") or {}).get(
                "verified_environment_install") or {}
            report["installed_manifest_sha256"]=install.get("manifest_sha256")
            save()
            need(type(report["actual_environment_native"]) is int and
                 0<=report["actual_environment_native"]<=MAX_ENV_NATIVE,
                 "SINGLE_SELECTED_ENV_NATIVE_BOUND_EXCEEDED")
            if not (report["actual_environment_ready"] and
                    report["environment_installed"]):
                report["status"]="PENDING_ORIGINAL_SELECTED_PHYSICAL_OIL_INSTALL"
                report["first_blocker"]=(
                    report["build_first_requires"][0]
                    if report["build_first_requires"] else
                    report["build_stage_status"] or
                    "ORIGINAL_BUILD_DID_NOT_VERIFY_SELECTED_OIL")
                save()
                return 2
            manifest=report["installed_manifest_sha256"]
            need(re.fullmatch(r"[a-f0-9]{64}",manifest or "") is not None,
                 "ACTUAL_ORIGINAL_V212_SHA_REQUIRED")
            path=pathlib.Path(install["stage_output_path"])
            doc,_=installed.read_json(path)
            installed.verify_fresh_installed_environment(doc)
            oil=doc.get("official_O_physical_source")
            need(type(oil) is dict and
                 oil.get("selected_oil_item_ids_by_hand")==
                     {"main_hand":OIL_ITEM} and
                 sum(doc["official_O"].values())>0 and
                 doc["official_T"]==doc["official_B"]+
                     sum(doc["official_O"].values()) and
                 manifest==doc["manifest_sha256"],
                 "EXACT_INSTALLED_SELECTED_OIL_BUDGET_SOURCE_DRIFT")
            verified=coordinator.find_verified_installed_season_environment(
                root,334,expected_game_build=BUILD,
                expected_installed_manifest_sha256=manifest,
                selected_oil_item_ids_by_hand={"main_hand":OIL_ITEM})
            report["original_v217_exact_oil_reverified"]=(type(verified) is dict
                and verified.get("installed_manifest_sha256")==manifest)
            report["official_O"]=doc["official_O"]
            report["installed_B"]=doc["official_B"]
            report["installed_T"]=doc["official_T"]
            save()
            need(report["original_v217_exact_oil_reverified"],
                 "EXACT_SELECTED_OIL_V217_NOT_REVERIFIED")
            # Existing per-user source consumer, not an invented worker.
            with owner.verified_current_catalog(
                result["source_compilation"]["source_catalog_path"],BUILD):
                app=web.create_app(root=root,token="v578-local-only-token",
                                   source_credential_store=Credentials())
                app.state.jobs.remember_verified_fresh_environment(result)
                user=web.sessions.standard_controls(("paladin","retribution"))
                user["race"]="dwarf"
                user["oil_hands"]=["main_hand"]
                user["final_T"]=MANUAL_T
                request={
                  "controls":user,"binary":str(binary),"revision":REV,
                  "current_season_product":True,
                  "selected_oil_item_ids_by_hand":{"main_hand":OIL_ITEM},
                  "selected_flask_item_id":FLASK_ITEM,
                  "user_socket_total":4,
                  "installed_season_game_build":BUILD,
                  "installed_manifest_sha256":manifest}
                with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                    response=client.post("/api/v1/sessions/plan",json=request,
                        headers={"x-simc-local-token":"v578-local-only-token",
                                 "origin":"http://127.0.0.1:8765"})
                    if response.status_code!=200:
                        data=response.json()
                        detail=data.get("detail") or {}
                        report["user_plan_http_status"]=response.status_code
                        report["first_blocker"]=str(
                          detail.get("code","UNKNOWN")
                          if type(detail) is dict else detail)[:130]
                        report["status"]="PENDING_ACTUAL_OIL_USER_PLAN"
                        save()
                        return 2
                    data=response.json()
                    report["user_plan_http_status"]=200
                    report["user_plan_ready"]=data.get("status")=="READY_ZERO_NATIVE"
                    plan=data.get("plan") or {}
                    report["user_budget"]={
                       k:plan.get(k) for k in ("base_B","final_T","fixed_O")}
                    report["user_plan_native_calls"]=data.get("native_calls")
                    report["user_plan_session_id_hash"]=hashlib.sha256(
                         data["session_id"].encode()).hexdigest()
                    generated=(root/data["session_id"]/"generated")
                    source=generated/"profile.simc"
                    need(source.is_file(),"ORIGINAL_PREPARED_SIMC_PROFILE_MISSING")
                    profile=source.read_text(encoding="utf8")
                    report["user_profile_sha256"]=digest(source)
                    report["profile_oil_token_once"]=sum(
                        s.startswith("temporary_enchant=") and
                        "thalassian_phoenix_oil" in s for s in
                        profile.splitlines())==1
                    save()
                    need(report["user_plan_ready"] and
                         plan.get("final_T")==MANUAL_T and
                         plan.get("base_B")==MANUAL_T-
                             sum(doc["official_O"].values()) and
                         plan.get("fixed_O")==doc["official_O"] and
                         data.get("native_calls")==0 and
                         report["profile_oil_token_once"],
                         "ACTUAL_MANUAL_T_POSITIVE_OIL_PROFILE_PLAN_DRIFT")
            report["status"]="PASS_REAL_SELECTED_PHYSICAL_OIL_V212_V217_USER_MANUAL_T_PLAN_NATIVE_BOUNDED"
            save()
            print("V578_REAL_SELECTED_OIL "+json.dumps({
              k:report.get(k) for k in (
                "status","actual_environment_native","reported_original_budget",
                "original_v217_exact_oil_reverified","user_budget",
                "user_plan_native_calls","actual_user_dps_native")},
                sort_keys=True,ensure_ascii=True),flush=True)
            return 0
    except Exception as exc:
        report["status"]="BLOCKED_REAL_SELECTED_OIL_"+type(exc).__name__
        report["first_blocker"]=code(exc)
        save()
        print("V578_SELECTED_OIL_BLOCKER "+json.dumps({
            k:report.get(k) for k in(
                "status","first_blocker","actual_environment_native",
                "reported_original_budget","original_v217_exact_oil_reverified")},
                sort_keys=True,ensure_ascii=True),flush=True)
        return 2

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--simc",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    raise SystemExit(run(a.simc,a.out))
