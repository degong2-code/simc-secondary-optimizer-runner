#!/usr/bin/env python3
"""Two exact previously published source ZIPs; real Windows HTTP, no Native.

Old product creates a historical plan. Existing offline result fixture and
managed SimC/settings/season/cache sentinels are explicitly synthetic.
No fake fixture is used to claim a READY season or a real DPS cache hit.
"""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import json
import os
import pathlib
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import venv
import zipfile

from v181_windows_beta_live_http import http
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tests.test_v106_user_session_controller import fake_native

PREFIX="SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA"
OLD_SHA="50e7723c5c389e87598b7507d1b1fb926b099c38f660d765ce509dfe4bac6f24"

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def need(ok,stage,detail=None):
    if not ok:
        raise RuntimeError("V860 "+stage+" "+str(detail)[:1000])

def unpack(path,dest,expected=None):
    sha=digest(path.read_bytes())
    need(expected is None or sha==expected,"ARCHIVE_SHA",{"expected":expected,"actual":sha})
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        manifest=json.loads(z.read(PREFIX+"/V181_PACKAGE_MANIFEST.json"))
        rows=manifest["files"]
        need(len(names)==len(set(names))==len(rows)+1 and
             set(names)=={PREFIX+"/"+r["path"] for r in rows}|{PREFIX+"/V181_PACKAGE_MANIFEST.json"},
             "ARCHIVE_MEMBERS")
        need(manifest.get("source_catalog") is None and
             manifest.get("historical_season_sources_bundled") is False,
             "EXPECTED_COLD_SOURCE_PACKAGE")
        for row in rows:
            name=PREFIX+"/"+row["path"]
            need(".." not in pathlib.PurePosixPath(name).parts and
                 not pathlib.PurePosixPath(name).is_absolute(),"ARCHIVE_PATH",name)
            raw=z.read(name)
            need(len(raw)==row["size"] and digest(raw)==row["sha256"],
                 "ARCHIVE_FILE_SHA",name)
        z.extractall(dest)
    return dest/PREFIX,{"sha256":sha,"bytes":path.stat().st_size,"verified_files":len(rows)}

def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes((json.dumps(value,sort_keys=True)+"\n").encode("utf8"))

def inventory(root):
    return {p.relative_to(root).as_posix():digest(p.read_bytes())
            for p in root.rglob("*") if p.is_file()}

@contextlib.contextmanager
def server(root,python,env,log):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1",0))
        port=sock.getsockname()[1]
    base="http://127.0.0.1:"+str(port)
    with log.open("w",encoding="utf8") as output:
        proc=subprocess.Popen([str(python),"-u",str(root/"runner/v113_local_web_api.py"),
                              "--port",str(port)],cwd=root,env=env,
                              stdin=subprocess.DEVNULL,stdout=output,stderr=subprocess.STDOUT)
        try:
            deadline=time.monotonic()+35
            while time.monotonic()<deadline:
                need(proc.poll() is None,"SERVER_EARLY_EXIT",root.name)
                try:
                    code,payload=http(base,"/api/v1/bootstrap")
                    if code==200:
                        need(len(payload["supported"])==26,"DPS_SCOPE")
                        break
                except (urllib.error.URLError,ConnectionError,TimeoutError):
                    time.sleep(.2)
            else:raise RuntimeError("V860 SERVER_TIMEOUT")
            token=payload["session_token"]
            def call(path,body=None,expected=200):
                code,data=http(base,path,token=token,payload=body,extra={"Origin":base})
                need(code==expected,"HTTP "+path,{"expected":expected,"actual":code,"response":data})
                return data
            yield call
        finally:
            proc.terminate()
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill();proc.wait(timeout=5)

def run(args):
    need(os.name=="nt","WINDOWS_ONLY")
    args.out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"p1_v860_exact_zip_upgrade_fixture_restore_v1",
             "status":"RUNNING","native_environment_calls":0,"native_dps_calls":0,
             "new_game_source_calls":0,"synthetic_saved_result":True,
             "real_native_cache_replay_verified":False,
             "verified_installed_season_restore":False,
             "personal_pc_upgrade_verified":False,"stages":[]}
    def save():
        put(args.out/"V860_RECEIPT.json",receipt)
    def stage(name):
        receipt["stages"].append(name);save()
        print("V860_STAGE "+name,flush=True)
    save()
    try:
        with tempfile.TemporaryDirectory(prefix="v860-upgrade-") as temp:
            # Windows TEMP can contain an 8.3 alias (RUNNER~1). The
            # product resolves its runs root and managed binary path.
            # Establish the same physical root before writing any fixture.
            work=pathlib.Path(temp).resolve(strict=True)
            old,receipt["old_archive"]=unpack(args.old,work/"old",OLD_SHA)
            new,receipt["new_archive"]=unpack(args.new,work/"new")
            need(receipt["old_archive"]["sha256"]!=receipt["new_archive"]["sha256"],
                 "DISTINCT_VERSIONS")
            stage("EXACT_TWO_PACKAGE_MANIFESTS")
            home=work/"home";local=work/"local"
            app=home/"SIMC_Secondary_Optimizer";runs=app/"runs"
            envpath=local/"SIMC_Secondary_Optimizer"/"web-python"
            venv.create(str(envpath),system_site_packages=True,with_pip=False)
            python=envpath/"Scripts"/"python.exe"
            env={**os.environ,"HOME":str(home),"USERPROFILE":str(home),
                 "LOCALAPPDATA":str(local),"PYTHONIOENCODING":"utf8",
                 "PYTHONDONTWRITEBYTECODE":"1"}
            # Same external user state; never execute this sentinel binary.
            raw=b"V860_SYNTHETIC_SIMC_DO_NOT_RUN"
            sha=digest(raw)
            binary=app/"simc-managed"/"versions"/sha[:24]/"simc.exe"
            binary.parent.mkdir(parents=True);binary.write_bytes(raw)
            revision="710c240"
            entry={"sha256":sha,"filename":"simc-1215-01-win64-"+revision+".7z",
                   "revision_short":revision,"archive_source":"LOCAL_FIXTURE_ONLY"}
            put(app/"simc-managed"/"installed.json",{
                "schema":"v193_explicit_local_simc_nightly_manager_v1",
                "active":entry,"previous":None})
            put(app/"simc-user-connection.json",{
                "schema":"v645_user_confirmed_simc_connection_v1",
                "binary":str(binary),"revision":revision,"static_cache":"",
                "binary_sha256":sha,"observed_game_build":None,
                "revision_identity":"SYNTHETIC_FIXTURE_NOT_ATTESTED"})
            # An incomplete season receipt must remain unavailable, not
            # become READY merely because a new package opens the old home.
            build="12.1.5.70961";install_sha="b"*64
            put(runs/"_fresh_season_sources"/("wago_"+build)/"fresh_source"/
                ("v212_installed_"+install_sha[:20]+".json"),
                {"manifest_sha256":install_sha,"fixture":"NOT_VERIFIED"})
            gear="/api/v1/season-gear?game_build="+build+"&target_ilevel=334&installed_manifest_sha256="+install_sha
            def read_settings(call):
                m=call("/api/v1/simc-updates/status")
                p=call("/api/v1/simc-connection/status")
                expected={"active_binary":str(binary),"sha256":sha,"native_calls_now":0}
                actual={"active_binary":m.get("active_binary"),
                        "sha256":(m.get("installed") or {}).get("sha256"),
                        "native_calls_now":m.get("native_calls_now")}
                need(actual==expected,"MANAGED_POINTER",{"expected":expected,"actual":actual})
                expected={"binary":str(binary),"revision":revision,
                          "verified_now":False,"native_calls_now":0}
                saved=p.get("saved") or {}
                actual={"binary":saved.get("binary"),"revision":saved.get("revision"),
                        "verified_now":p.get("verified_now"),
                        "native_calls_now":p.get("native_calls_now")}
                need(actual==expected,"CONNECTION",{"expected":expected,"actual":actual})
                g=call(gear)
                need(g["count"]==0 and g["status"]=="SEASON_GEAR_INSTALLED_SOURCE_UNAVAILABLE",
                     "UNVERIFIED_SEASON_MUST_NOT_PROMOTE",g)
                return m["installed"],p["saved"]
            with server(old,python,env,args.out/"old-server.log") as call:
                settings=read_settings(call)
                stage("OLD_PACKAGE_MANAGED_CONNECTION_AND_PENDING_SEASON")
                defaults=call("/api/v1/defaults")
                controls=dict(next(x for x in defaults["archetypes"]
                                   if x["class"]=="paladin" and x["spec"]=="retribution"))
                controls.pop("representative_scope",None)
                controls["oil_hands"]=["main_hand"]
                request={"controls":controls,"binary":str(binary),"revision":revision,
                         "current_season_product":False}
                plan=call("/api/v1/sessions/plan",request)
                sid=plan["session_id"]
                need(re.fullmatch(r"[a-f0-9]{20}",sid) and plan["native_calls"]==0
                     and plan["plan"]["final_T"]==3182,"OLD_HISTORICAL_PLAN",plan)
                folder=runs/sid
                initial=call("/api/v1/sessions/"+sid+"/status")
                need(not initial["active"] and initial["progress"]["native_attempts"]==0,
                     "OLD_PLAN_NO_NATIVE")
                stage("OLD_PACKAGE_REAL_HTTP_PLAN")
                # Reuse existing synthetic result fixture, not a real receipt.
                put(folder/"V106_USER_RESULT.json",fake_native(hits=6))
                put(folder/"generated"/"simc_results"/"fixture-not-native.json",
                    {"fixture":"CACHE_BYTES_ONLY_NOT_NATIVE_EVIDENCE"})
                inputs=call("/api/v1/sessions/"+sid+"/inputs")
                result=call("/api/v1/sessions/"+sid+"/result")
                need(result["final_T"]==3182 and result["user_result"]["confidence_level"]==.95,
                     "OLD_RESULT_FIXTURE")
            before=inventory(app)
            cfg=(envpath/"pyvenv.cfg").read_bytes()
            stage("OLD_STATE_SNAPSHOT")
            checked=subprocess.run(["cmd","/d","/c",
                str(new/"START_HERE_AUTO_SETUP_AND_RUN.bat"),"--check"],
                cwd=new,env=env,stdin=subprocess.DEVNULL,capture_output=True,
                text=True,encoding="utf8",errors="replace",timeout=35)
            need(checked.returncode==0 and "[READY]" in checked.stdout and
                 "[SETUP]" not in checked.stdout,"NEW_EASY_START",checked.stdout[-800:])
            stage("NEW_EXTRACTED_LAUNCHER_REUSED_RUNTIME")
            with server(new,python,env,args.out/"new-server.log") as call:
                need(read_settings(call)==settings,"NEW_SAVED_SETTINGS_CHANGED")
                listed=call("/api/v1/sessions")
                need(any(x["session_id"]==sid for x in listed["sessions"]),
                     "NEW_SESSION_INDEX",listed)
                need(call("/api/v1/sessions/"+sid+"/inputs")==inputs,
                     "NEW_SAVED_INPUTS_CHANGED")
                need(call("/api/v1/sessions/"+sid+"/result")==result,
                     "NEW_SAVED_RESULT_CHANGED")
                status=call("/api/v1/sessions/"+sid+"/status")
                need(not status["active"] and status["progress"]["native_attempts"]==0,
                     "NEW_READ_ONLY_NO_NATIVE")
                blocked=call("/api/v1/sessions/"+sid+"/cache-only",{},expected=422)
                need(blocked.get("detail",{}).get("code")=="CACHE_ONLY_REQUIRES_COMPLETED_REAL_SESSION",
                     "UNVERIFIED_CACHE_MUST_NOT_RUN",blocked)
            after=inventory(app)
            need(before==after and (envpath/"pyvenv.cfg").read_bytes()==cfg,
                 "PERSISTED_BYTES_DRIFT",sorted(set(before)^set(after))+
                     [k for k in before.keys()&after.keys() if before[k]!=after[k]])
            receipt["preserved_file_count"]=len(before)
            receipt["old_plan_session_id_sha256"]=digest(sid.encode())
            stage("NEW_PACKAGE_RESTORED_AND_BYTES_UNCHANGED")
            receipt["status"]="PASS_EXACT_TWO_ZIP_FIXTURE_UPGRADE_RESTORE"
            save()
            print("V860_RECEIPT "+json.dumps(receipt,sort_keys=True),flush=True)
    except BaseException as exc:
        receipt["status"]="FAIL";receipt["first_error"]=str(exc)[:1500];save()
        raise

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--old",type=pathlib.Path,required=True)
    p.add_argument("--new",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    run(p.parse_args())
