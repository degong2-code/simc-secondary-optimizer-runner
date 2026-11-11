#!/usr/bin/env python3
"""v343: one true Retail-70783 Windows fresh GJFO -> v113 N56 DPS12.

Reuse exact official Windows SimC binary de11f57 from 2026-11-11 nightly;
reuse existing v216/v212/v098/v293 and v334 source-first one-spec probe.
No full 64, no Windows browser automation, no optimizer changes.
"""
from __future__ import annotations
import hashlib,json,os,pathlib,re,sys,tempfile,zipfile,subprocess,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
from runner import v113_local_web_api as web
from runner import v289_retail_live_build_source as retail
from integration_probes import p3_haj_real_local_web_native_e2e as native_web

BUILD="12.1.5.70783"
REVISION="de11f57df75dda668bae6ac7043a43b98831fa96"
EXE_SHA="1fc927d2be7f1b6064c75f004b5b22245b064a6b3e56e572af4048ba822a986d"
SCHEMA="p1_v343_current_70783_windows_real_user_N56_native_once_v1"

def need(ok,reason):
    if not ok:raise RuntimeError("V343_"+reason)

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for part in iter(lambda:f.read(1024*1024),b""):
            h.update(part)
    return h.hexdigest()

def run(binary,out):
    need(sys.platform=="win32","ONLY_REAL_WINDOWS")
    binary=pathlib.Path(binary).resolve(strict=True)
    need(binary.name.lower()=="simc.exe" and sha(binary)==EXE_SHA,
         "CURRENT_OFFICIAL_WIN_BINARY_SHA_DRIFT")
    need(os.environ.get("SIMC_PINNED_SOURCE_COMMIT")==REVISION and
         os.environ.get("SIMC_PINNED_GAME_BUILD")==BUILD,
         "PINNED_RETAIL_BUILD_SOURCE_MISMATCH")
    for secret in ("BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
                   "WCL_CLIENT_ID","WCL_CLIENT_SECRET"):
        need(bool(os.environ.get(secret)),"SOURCE_CREDENTIAL_MISSING")
    out=pathlib.Path(out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    result={"schema":SCHEMA,"status":"NOT_STARTED",
            "binary_sha256":EXE_SHA,"simc_source_revision":REVISION,
            "target_game_build":BUILD,"character":"hunter/survival",
            "target_ilevel":334,"manual_final_T":None,
            "new_environment_native":0,"new_dps_native":0,
            "global_optimum_proven":False,"user_browser_actual":False}
    def save():
        (out/"V343_WINDOWS_70783_COMPACT.json").write_text(
            json.dumps(result,ensure_ascii=False,sort_keys=True,
                       indent=2,allow_nan=False)+"\n",encoding="utf8")
    save()
    try:
        # No user profile or full simulation. This checks the binary's stated
        # game build as a guard, not a standalone season admission.
        banner=subprocess.run([str(binary)],input="",capture_output=True,
                              text=True,errors="replace",cwd=binary.parent,
                              timeout=25)
        need("12.1.5.70783" in (banner.stdout+"\n"+banner.stderr),
             "CURRENT_RETAIL_CLI_BUILD_NOT_REPORTED")
        live=retail.discover(region="KR")
        result["observed_live_KR_build"]=live["game_build"]
        need(live["game_build"]==BUILD,
             "LIVE_RETAIL_KR_BUILD_CHANGED_FROM_PIN")
        with tempfile.TemporaryDirectory(prefix="v343-one-windows-",dir=out) as tmp:
            root=pathlib.Path(tmp)
            need(not list(root.iterdir()),"NOT_FRESH_EMPTY_INSTALL_ROOT")
            local=web.LocalJobs(root)
            environment=local.build_season_environment(
                game_build=BUILD,target_ilevel=334,
                auto_initial_core_build=True,
                auto_initial_core_simc_binary=str(binary),
                simc_revision_hint=REVISION,
                existing_special_gem_id=None,
                source_target_socket_count=4)
            source=environment.get("source_compilation") or {}
            gems=source.get("physical_gem_layout_unadmitted") or {}
            result["new_environment_native"]=environment.get("native_calls",0)
            result["environment_budget"]={key:environment.get(key) for key in
                                          ("G","J","F","O","B","T")}
            result["environment_ready"]=environment.get("environment_ready")
            result["environment_installed"]=environment.get("environment_installed")
            result["installed_manifest_sha256"]=(source.get(
                    "verified_environment_install") or {}).get("manifest_sha256")
            need(result["environment_ready"] is True and
                 result["environment_installed"] is True and
                 type(result["new_environment_native"]) is int and
                 0<=result["new_environment_native"]<=3,
                 "NEW_GJFO_INSTALL_NOT_READY_OR_EXCEEDS_NATIVE_BOUND")
            need(environment["B"]==environment["G"]+environment["J"]+
                 environment["F"] and
                 environment["T"]==environment["B"] and
                 sum(environment["O"].values())==0,
                 "BUDGET_70783_CHMV_DRIFT")
            need(environment["G"]==2850 and environment["J"]==92 and
                 environment["F"]==165 and environment["T"]==3107,
                 "SAME_SEASON_BUDGET_DIFFERS_FROM_VERIFIED_70783")
            need(gems.get("socket_total")==4 and
                 gems.get("special_gem_id") is None and
                 len(gems.get("ordinary_gem_ids") or [])==4,
                 "FOUR_ORDINARY_GEMS_SOURCE_DRIFT")
            save()
            # The existing real FastAPI+subprocess P1 path owns all SimC
            # effects/APL, JSON2 validation, N56 and 95% statistics.
            receipt_file=out/"V343_WEB_NATIVE_RESULT.json"
            evidence_file=pathlib.Path("p3_haj_web_native_evidence.zip")
            need(not evidence_file.exists(),"NATIVE_EVIDENCE_ALREADY_PRESENT")
            completed=native_web.execute(
                root,binary,REVISION,BUILD,environment,
                receipt_file=receipt_file,
                manual_final_T=None,
                selected_oil_item_ids_by_hand={},
                character_class="hunter",
                character_spec="survival",
                character_race="human",
                expected_socket_count=4,
                primary_continuous=True)
            result["new_dps_native"]=completed["new_native_dps_calls"]
            result["web_status"]=completed["status"]
            result["observed"]=completed.get("reported")
            need(completed["status"]=="PASS_REAL_FASTAPI_PRIMARY_CONTINUOUS_N56"
                 and result["new_dps_native"]==12 and
                 result["observed"]["scout_N"]==56 and
                 result["observed"]["final_T"]==3107 and
                 result["observed"]["confidence_level"]==0.95 and
                 result["observed"]["global_optimum_proven"] is False,
                 "CURRENT_WINDOWS_PRIMARY_DPS_AND_95_INVALID")
            need(evidence_file.is_file(),"MISSING_ORIGINAL_NATIVE_ZIP")
            with zipfile.ZipFile(evidence_file) as z:
                file_names=z.namelist()
                simc_input=[x for x in file_names if x.endswith("/input.simc")]
                json2=[x for x in file_names if x.endswith("/result.json")]
                receipts=[x for x in file_names
                          if x.endswith("/native_receipt.json")]
                need(len(simc_input)==len(json2)==len(receipts)==12,
                     "TWELVE_ORIGINAL_NATIVE_JSON2_RECEIPTS_MISSING")
                sample=z.read(simc_input[0])
                need(b"spec=survival" in sample and
                     re.search(rb"(?m)^hunter=",sample) is not None,
                     "SOURCES_MUST_BE_NEW_SURVIVAL_PROFILE")
                result["first_native_input_sha256"]=hashlib.sha256(
                    sample).hexdigest()
                result["native_json2_sha256"]=[hashlib.sha256(
                    z.read(p)).hexdigest() for p in json2]
            result["raw_evidence_sha256"]=sha(evidence_file)
            result["status"]="PASS_REAL_WINDOWS_70783_FRESH_GJFO_N56_12"
            save()
            shutil.move(str(evidence_file),
                        str(out/"V343_NATIVE_INPUT_JSON2_RECEIPT.zip"))
        print("V343_WINDOWS_70783_NATIVE "+json.dumps({
            k:result[k] for k in ("status","environment_budget",
                 "new_environment_native","new_dps_native","observed")},
            ensure_ascii=False,sort_keys=True),flush=True)
    except Exception as e:
        result["status"]="BLOCKED_OR_PARTIAL_"+type(e).__name__
        message=str(e)
        result["error_code"]=(message if re.fullmatch(
            r"(?:V343_)?[A-Z][A-Z0-9_]{3,100}",message)
            else type(e).__name__)
        save()
        raise

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--simc",type=pathlib.Path,required=True)
    parser.add_argument("--out",type=pathlib.Path,required=True)
    args=parser.parse_args()
    run(args.simc,args.out)
