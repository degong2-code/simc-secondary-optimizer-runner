#!/usr/bin/env python3
"""v181: real Windows Python/HTTP process launched FROM the extracted beta ZIP.

No mocked server, no GUI clicks and NO SimC Native. Exercises 3 current
season user plans and restored identities over actual loopback port.
"""
from __future__ import annotations
import argparse
import json
import os
import pathlib
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile

def need(ok,why):
    if not ok:raise RuntimeError("V181_"+why)

def http(base,path,*,token=None,payload=None,extra=None):
    headers={"Accept":"application/json"}
    if token:headers["x-simc-local-token"]=token
    if payload is not None:
        headers["Content-Type"]="application/json"
        body=json.dumps(payload,ensure_ascii=False).encode("utf8")
    else:body=None
    headers.update(extra or {})
    request=urllib.request.Request(base+path,data=body,headers=headers,
                                   method="POST" if payload is not None else "GET")
    try:
        with urllib.request.urlopen(request,timeout=7) as response:
            raw=response.read()
            return response.status,(json.loads(raw) if path.startswith("/api/") else raw)
    except urllib.error.HTTPError as exc:
        raw=exc.read()
        try:content=json.loads(raw)
        except ValueError:content=raw.decode("utf8","replace")
        return exc.code,content

def run(archive_path):
    with tempfile.TemporaryDirectory(prefix="v181_windows_beta_") as tmp:
        work=pathlib.Path(tmp)
        with zipfile.ZipFile(archive_path) as archive:
            # The packager is trusted only after tests validate its exact roots.
            names=archive.namelist()
            need(all(n.startswith("SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA/")
                     and ".." not in pathlib.PurePosixPath(n).parts
                     for n in names),"INVALID_ZIP_MEMBER")
            archive.extractall(work)
        root=work/"SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA"
        need((root/"START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd").is_file(),
             "EXTRACTED_LAUNCHER_MISSING")
        need((root/"runner/v113_local_web_api.py").is_file(),
             "EXTRACTED_SERVER_MISSING")
        check=subprocess.run(["cmd","/d","/c",str(root/"START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd"),
                              "--check"],cwd=root,stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                             timeout=25,text=True,encoding="utf8",errors="replace")
        need(check.returncode==0 and "READY:" in check.stdout,
             "ONE_CLICK_WINDOWS_DEPENDENCY_CHECK_FAILED:"+check.stdout[-600:])
        print("V181_WINDOWS_EXTRACTED_LAUNCHER_CHECK_PASS",flush=True)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1",0))
            port=sock.getsockname()[1]
        base="http://127.0.0.1:"+str(port)
        fake=work/"NOT_REAL_SIMC_DO_NOT_RUN.exe"
        fake.write_bytes(b"V181_CHECKS_PLAN_ONLY_NATIVE_ZERO")
        server_log=work/"server.log"
        with server_log.open("w",encoding="utf8") as handle:
            server=subprocess.Popen(
                [sys.executable,"-u",str(root/"runner/v113_local_web_api.py"),
                 "--port",str(port)],
                 cwd=root,stdin=subprocess.DEVNULL,stdout=handle,
                 stderr=subprocess.STDOUT,
                 env={**os.environ,"PYTHONIOENCODING":"utf-8",
                      "PYTHONDONTWRITEBYTECODE":"1"})
            try:
                deadline=time.monotonic()+22
                while time.monotonic()<deadline:
                    need(server.poll() is None,"WEB_SERVER_EARLY_EXIT")
                    try:
                        status,health=http(base,"/api/v1/health")
                        if status==200:break
                    except (urllib.error.URLError,ConnectionError,TimeoutError):
                        time.sleep(.16)
                else:raise RuntimeError("V181_LIVE_LOOPBACK_DID_NOT_START")
                need(health["mode"]=="LOCAL_ONLY" and
                     health["native_called_by_health"] is False and
                     health["supported_dps"]==26,
                     "REAL_SERVER_HEALTH_INVALID")
                status,html=http(base,"/")
                need(status==200 and
                     b'id="current_season_product"' not in html and
                     b"simc-import-file" in html and
                     b"craft-compatibility-note" in html,
                     "BROWSER_UI_NOT_SERVED")
                status,js=http(base,"/assets/app.js")
                need(status==200 and b"current_season_product" in js,
                     "JS_NOT_SERVED")
                status,auth=http(base,"/api/v1/bootstrap")
                need(status==200 and len(auth["supported"])==26,
                     "BOOTSTRAP_26_DPS_FAILED")
                token=auth["session_token"]
                status,defaults=http(base,"/api/v1/defaults",token=token)
                need(status==200 and len(defaults["archetypes"])==26,
                     "USER_DEFAULTS_26_DPS_FAILED")
                status,gear=http(base,"/api/v1/season-gear",token=token)
                need(status==200 and gear.get("status")==
                     "CURRENT_SEASON_CANDIDATE_SELECTION_ONLY",
                     "CURRENT_SEASON_GEAR_LIST_UNAVAILABLE")
                from_map={(c["class"],c["spec"]):c for c in defaults["archetypes"]}
                seen=set()
                for cls,spec,level in (("paladin","retribution",334),
                                        ("warrior","fury",321),
                                        ("mage","frost",344)):
                    controls={k:v for k,v in from_map[(cls,spec)].items()
                              if k not in ("representative_scope",)}
                    controls["ilevel"]=level
                    # Defaults include fields class/spec and user inputs; no
                    # unknown HTTP keys are introduced.
                    payload={"controls":controls,"binary":str(fake),
                             "revision":"7bc10711b5",
                             "current_season_product":True}
                    st,result=http(base,"/api/v1/sessions/plan",
                                   token=token,payload=payload)
                    need(st==200,"CURRENT_SEASON_REAL_HTTP_PLAN_FAILED:"
                         +str((cls,spec,level,st,result))[:450])
                    sid=result["session_id"]
                    need(sid not in seen,"USER_SCENARIOS_CACHE_COLLIDED")
                    seen.add(sid)
                    need(result["native_calls"]==0 and
                         result["plan"]["native_limit"]==6 and
                         result["plan"]["current_season_product"] is True,
                         "WRONG_PLAN_OR_SIMC_WAS_CALLED")
                    st,restore=http(base,"/api/v1/sessions/"+sid+"/inputs",
                                     token=token)
                    need(st==200 and restore["current_season_product"] is True
                         and restore["user"]["target"]["ilevel"]==level,
                         "USER_SESSION_RESTORE_NOT_ROUNDTRIP")
                    st,progress=http(base,"/api/v1/sessions/"+sid+"/status",
                                      token=token)
                    need(st==200 and not progress["active"] and
                         progress["progress"]["native_attempts"]==0,
                         "PLAN_ACCIDENTALLY_LAUNCHED_NATIVE")
                    print("V181_WINDOWS_HTTP_PLAN_PASS",cls+"/"+spec,level,
                          "native 0",flush=True)
                # Security: foreign Host rejected, missing token refused.
                st,_=http(base,"/api/v1/defaults")
                need(st==403,"UNAUTHORIZED_DEFAULTS_NOT_DENIED")
                st,_=http(base,"/api/v1/bootstrap",
                           extra={"Host":"evil.example:"+str(port)})
                need(st==403,"DNS_REBINDING_NOT_BLOCKED")
                st,_=http(base,"/api/v1/defaults",token=token,
                           extra={"Origin":"http://evil.example"})
                need(st==403,"FOREIGN_ORIGIN_NOT_BLOCKED")
                print("V181_WINDOWS_LIVE_HTTP_SECURITY_PASS",flush=True)
                return 0
            finally:
                server.terminate()
                try:server.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait(timeout=5)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--zip",type=pathlib.Path,required=True)
    args=parser.parse_args()
    need(os.name=="nt","WINDOWS_ONLY_REAL_PLATFORM_SMOKE")
    code=run(args.zip)
    print("V181_WINDOWS_BETA_LIVE_3_PLANS_RESTORE_ZERO_NATIVE_PASS",flush=True)
    return code

if __name__=="__main__":raise SystemExit(main())
