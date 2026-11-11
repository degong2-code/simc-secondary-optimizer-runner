#!/usr/bin/env python3
"""v347: retail-70783 empty-profile Windows G/J/F/O without private API keys.

One original v113 -> v216 -> v212 Environment Build; never starts user DPS.
Pinned official SimC Windows binary and season, max G1+F2 native calls. It
does NOT infer "READY" merely because credential-free Wago source responded.
"""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib,re,subprocess,sys,tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner")]
import v113_local_web_api as web
import v242_authenticated_season_source_stage as auth
import v289_retail_live_build_source as retail

BUILD="12.1.5.70783"
REV="de11f57df75dda668bae6ac7043a43b98831fa96"
EXE_SHA="1fc927d2be7f1b6064c75f004b5b22245b064a6b3e56e572af4048ba822a986d"
SCHEMA="p1_v347_windows_70783_no_blizzard_wcl_github_credentials_core_v1"

def need(ok,label):
    if not ok:raise RuntimeError("V347_"+label)

def sha(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for buf in iter(lambda:f.read(1024*1024),b""):h.update(buf)
    return h.hexdigest()

def probe(binary,out):
    need(sys.platform=="win32","REAL_WINDOWS_REQUIRED")
    # This CI runs the *same* source path a local user without developer
    # credentials will take. No copies of masked secrets or token fallback.
    for k in (*auth.FIELDS,"SIMC_SOURCE_GITHUB_API_TOKEN"):
        need(not os.environ.get(k),"PRIVATE_SOURCE_CREDENTIAL_PRESENT")
        os.environ.pop(k,None)
    binary=pathlib.Path(binary).resolve(strict=True)
    need(binary.name.lower()=="simc.exe" and sha(binary)==EXE_SHA,
         "PINNED_OFFICIAL_EXE_SHA_MISMATCH")
    need(os.environ.get("SIMC_PINNED_SOURCE_COMMIT")==REV and
         os.environ.get("SIMC_PINNED_GAME_BUILD")==BUILD,
         "CI_PINNED_SOURCE_IDENTITY_MISMATCH")
    out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    state={
        "schema":SCHEMA,"status":"NOT_RUN",
        "private_blizzard_wcl_keys_configured":False,
        "public_github_api_token_configured":False,
        "simc_binary_sha256":EXE_SHA,
        "simc_revision":REV,"target_game_build":BUILD,
        "target_ilevel":334,"character":"paladin/retribution",
        "actual_new_dps_native_calls":0,
        "environment_native_calls_observed":None,
        "environment_ready":False,"environment_installed":False,
        "global_optimum_proven":False,
        "package_70575_catalog_used":False,
        "user_personal_pc_proven":False}
    receipt=out/"V347_WINDOWS_NO_PRIVATE_KEYS_ENVIRONMENT.json"
    def save():
        receipt.write_text(json.dumps(state,sort_keys=True,ensure_ascii=False,
             indent=2,allow_nan=False)+"\n",encoding="utf8")
    save()
    run=subprocess.run([str(binary)],input="",capture_output=True,
                       text=True,errors="replace",timeout=25,cwd=binary.parent)
    need(run.returncode==0 and BUILD in (run.stdout+"\n"+run.stderr),
         "OFFICIAL_BINARY_RETAIL_BUILD_NOT_REPORTED")
    live=retail.discover(region="KR")
    state["observed_public_KR_game_build"]=live["game_build"]
    save()
    need(live["game_build"]==BUILD,
         "KR_PUBLIC_RETAIL_BUILD_CHANGED_REFUSE_OLD_SOURCE")
    with tempfile.TemporaryDirectory(prefix="v347-no-private-keys-",dir=out) as t:
        root=pathlib.Path(t)/"runs";root.mkdir()
        jobs=web.LocalJobs(root)
        try:
            result=jobs.build_season_environment(
                game_build=None,target_ilevel=334,
                auto_initial_core_build=True,
                auto_initial_core_simc_binary=str(binary),
                simc_revision_hint=REV,
                existing_special_gem_id=None,
                source_target_socket_count=4)
            state["environment_status"]=result.get("status")
            state["environment_ready"]=result.get("environment_ready") is True
            state["environment_installed"]=result.get("environment_installed") is True
            state["environment_native_calls_observed"]=result.get("native_calls")
            scope=result.get("web_environment_scope") or {}
            state["web_scope_build"]=scope.get("game_build")
            state["web_scope_discovery"]=scope.get("game_build_source")
            state["web_scope_ready"]=scope.get("environment_ready")
            state["stage_statuses"]={
                k:v.get("status") for k,v in result.items()
                if type(v) is dict and type(v.get("status")) is str}
            source=result.get("source_compilation") or {}
            install=source.get("verified_environment_install") or {}
            state["installed_manifest_sha256"]=install.get("manifest_sha256")
            if state["environment_ready"] and state["environment_installed"]:
                state["budget"]={k:result.get(k) for k in
                                 ("G","J","F","O","B","T")}
                need(type(state["environment_native_calls_observed"]) is int
                     and 0<=state["environment_native_calls_observed"]<=3,
                     "INITIAL_BUILD_EXCEEDS_THREE_NATIVE")
                need(all(result[k]==v for k,v in (
                        ("G",2850),("J",92),("F",165),("B",3107),("T",3107)))
                     and type(result.get("O")) is dict
                     and sum(result["O"].values())==0,
                     "CURRENT_70783_BUDGET_MISMATCH")
                need(scope.get("game_build")==BUILD and
                     install.get("environment_ready") is True and
                     install.get("environment_installed") is True,
                     "WRONG_SOURCE_INSTALLED_OR_NOT_SEALED")
                state["status"]="PASS_WIN_NO_PRIVATE_KEYS_GJFO_INSTALLED"
            else:
                state["status"]="PENDING_WIN_NO_PRIVATE_KEYS_GJFO_NOT_READY"
            save()
            need(state["status"]=="PASS_WIN_NO_PRIVATE_KEYS_GJFO_INSTALLED",
                 "NO_PRIVATE_CREDENTIALS_GJFO_REMAINS_PENDING")
        except Exception as exc:
            state["status"]="BLOCKED_OR_PARTIAL_"+type(exc).__name__
            text=str(exc)
            state["error_code"]=(text if re.fullmatch(
                r"[A-Z][A-Z0-9_]{4,130}",text) else type(exc).__name__)
            # Original v217 stage states stay on the temp worker while
            # working; a failed run never publishes an invented READY.
            stages=root/"_fresh_season_sources"/("wago_"+BUILD)/".stage_receipts"
            state["partial_stage_receipt_count"]=(
                len(list(stages.glob("*.json"))) if stages.is_dir() else 0)
            save()
            raise
    print("V347_NO_PRIVATE_SOURCE_KEYS "+json.dumps({
        k:state[k] for k in ("status","environment_native_calls_observed",
            "environment_ready","environment_installed","budget")},
        ensure_ascii=False,sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--simc",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args()
    probe(a.simc,a.out)
