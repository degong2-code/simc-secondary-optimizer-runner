#!/usr/bin/env python3
"""v345: exact extracted Windows beta ZIP + genuine CMD + Chrome persistence.

No SimulationCraft Native calls: a real HTTP /sessions/plan saves the
browser's valid user inputs; restart the extracted CMD and restore via visible
Chrome UI. The old v344 complete Native64 receipt covers actual DPS workflow.
The official Windows SimC exe is external to the ZIP and only its banner is
inspected (empty profile).
"""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib,re,subprocess,sys,tempfile,time,zipfile
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait,Select

ROOT=pathlib.Path(__file__).resolve().parents[1]
PREFIX="SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA"
URL="http://127.0.0.1:8765"
SCHEMA="p1_v345_real_extracted_windows_zip_cmd_chrome_restore_zero_native_v1"
SIMC_SHA="1fc927d2be7f1b6064c75f004b5b22245b064a6b3e56e572af4048ba822a986d"
REV="de11f57df75dda668bae6ac7043a43b98831fa96"
BUILD="12.1.5.70783"

def need(condition,code):
    if not condition:raise RuntimeError("V345_"+code)

def digest(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def wait_for_http(proc):
    for _ in range(180):
        need(proc.poll() is None,"PACKAGED_CMD_EXITED_BEFORE_HTTP")
        try:
            with urlopen(URL+"/api/v1/health",timeout=1.5) as response:
                data=json.load(response)
                if response.status==200 and data.get("mode")=="LOCAL_ONLY":
                    return data
        except (OSError,ValueError):pass
        time.sleep(.14)
    raise RuntimeError("V345_PACKAGED_CMD_HTTP_TIMEOUT")

def start_cmd(root,home,log):
    env={**os.environ,"HOME":str(home),"USERPROFILE":str(home),
         "PYTHONIOENCODING":"utf-8","PYTHONDONTWRITEBYTECODE":"1"}
    proc=subprocess.Popen(["cmd","/d","/c",
           str(root/"START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd")],
           cwd=root,stdin=subprocess.DEVNULL,
           stdout=log,stderr=subprocess.STDOUT,env=env)
    wait_for_http(proc)
    return proc

def stop_cmd(proc):
    if proc is None:return
    if proc.poll() is None:
        subprocess.run(["taskkill","/PID",str(proc.pid),"/T","/F"],
                       stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                       timeout=20)
    try:proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill();proc.wait(timeout=5)
    # We only inspect one Windows machine's loopback port. Never assume that
    # terminating the outer CMD automatically terminates its Python child.
    for _ in range(80):
        try:
            with urlopen(URL+"/api/v1/health",timeout=.2):
                time.sleep(.1)
        except OSError:return
    raise RuntimeError("V345_PACKAGED_CMD_CHILD_SERVER_NOT_STOPPED")

def actual_chrome():
    opt=Options()
    for arg in ("--headless=new","--no-sandbox","--disable-dev-shm-usage",
                "--window-size=1440,950"):
        opt.add_argument(arg)
    driver=webdriver.Chrome(options=opt)
    driver.get(URL+"/")
    # defaults.length and token become visible *before* initialize()
    # populates default class/spec/gear and calls buttonState(). Wait for
    # the exact fully initialized primary user flow as the v344 browser did.
    WebDriverWait(driver,45).until(
       lambda d:d.execute_script(
          "return state.defaults.length===26 && !!state.token && "+
          "!state.busy && !!field('spec') && !!field('race') && "+
          "!document.getElementById('start-btn').disabled"))
    return driver

def http_json(path,token=None,body=None):
    headers={"Accept":"application/json"}
    if token:headers["x-simc-local-token"]=token
    if body is not None:
        headers["Content-Type"]="application/json"
        headers["Origin"]=URL
    req=Request(URL+path,method="POST" if body is not None else "GET",
        headers=headers,data=(json.dumps(body,ensure_ascii=False).encode("utf8")
                              if body is not None else None))
    try:
        with urlopen(req,timeout=35) as reply:
            return reply.status,json.load(reply)
    except HTTPError as exc:
        return exc.code,json.loads(exc.read().decode("utf8"))

def run(zip_path,exe,out):
    need(os.name=="nt","WINDOWS_ONLY")
    exe=pathlib.Path(exe).resolve(strict=True)
    need(exe.name.lower()=="simc.exe" and digest(exe)==SIMC_SHA,
         "EXTERNAL_OFFICIAL_SIMC_SHA_DRIFT")
    check=subprocess.run([str(exe)],input="",text=True,errors="replace",
                         capture_output=True,timeout=25,cwd=exe.parent)
    need(check.returncode==0 and BUILD in (check.stdout+"\n"+check.stderr),
         "EXTERNAL_OFFICIAL_SIMC_BUILD_BANNER_MISMATCH")
    zip_path=pathlib.Path(zip_path).resolve(strict=True)
    out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    report={
      "schema":SCHEMA,"status":"NOT_RUN","new_dps_native_calls":0,
      "new_environment_native_calls":0,"used_synthetic_http":False,
      "used_actual_chrome":False,"launched_extracted_cmd":False,
      "source_zip_sha256":digest(zip_path),
      "official_simc_exe_sha256":SIMC_SHA,"official_simc_revision":REV,
      "official_simc_banner_build":BUILD,
      "v344_64_native_proof_reused_historically":True,
      "v344_native_cases_replayed_in_this_probe":False,
      "personally_installed_user_pc_proven":False}
    def save():
        (out/"V345_WINDOWS_PACKAGE_CMD_BROWSER_RECEIPT.json").write_text(
          json.dumps(report,ensure_ascii=False,sort_keys=True,
                     indent=2,allow_nan=False)+"\n",encoding="utf8")
    save()
    driver=None;proc=None;log_file=None
    with tempfile.TemporaryDirectory(prefix="v345-extracted-beta-",dir=out) as tmp:
        work=pathlib.Path(tmp);home=work/"isolated-home";home.mkdir()
        try:
            with zipfile.ZipFile(zip_path) as z:
                members=z.namelist()
                need(len(members)==len(set(members)) and
                     all(x.startswith(PREFIX+"/") and
                         ".." not in pathlib.PurePosixPath(x).parts
                         for x in members),"ARCHIVE_PATH_POLICY_VIOLATED")
                m=json.loads(z.read(PREFIX+"/V181_PACKAGE_MANIFEST.json"))
                records=m["files"]
                need(m["archive_root"]==PREFIX and
                     m["file_count"]==len(records) and len(records)>=75 and
                     not m["native_executable_bundled"] and
                     not m["sessions_bundled"] and
                     not m["historical_native_json2_bundled"],
                     "BETA_PACKAGE_MANIFEST_POLICY_FAILED")
                for p in records:
                    raw=z.read(PREFIX+"/"+p["path"])
                    need(hashlib.sha256(raw).hexdigest()==p["sha256"] and
                         len(raw)==p["size"],"SOURCE_MEMBER_SHA_MISMATCH")
                live_paths=("runner/webui/app.js",
                            "runner/v113_local_web_api.py",
                            "runner/v216_environment_build_coordinator.py",
                            "runner/v293_local_longrun_session.py",
                            "runner/v281_consumable_simc_relation.py",
                            "START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd")
                need(all((PREFIX+"/"+p) in members for p in live_paths),
                     "LATEST_P1_RUNTIME_MISSING_FROM_PACKAGE")
                for p in live_paths:
                    need(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==
                         hashlib.sha256(z.read(PREFIX+"/"+p)).hexdigest(),
                         "CURRENT_HEAD_RUNTIME_BYTES_CHANGED_IN_ZIP")
                need(not any(x.lower().endswith((".exe",".dll",".pfx",".pem",".key"))
                             for x in members),"EXECUTABLE_OR_SECRET_BUNDLED")
                z.extractall(work)
            root=work/PREFIX
            report["package_files"]=len(records)
            report["verified_source_catalog_sha256"]=m["source_catalog"]["artifact_sha256"]
            report["latest_runtime_source_bytes_unchanged"]=True
            # No local native, server, network or user session on preflight.
            env={**os.environ,"HOME":str(home),"USERPROFILE":str(home)}
            check=subprocess.run(["cmd","/d","/c",
                str(root/"START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd"),"--check"],
                cwd=root,capture_output=True,stdin=subprocess.DEVNULL,
                text=True,encoding="utf8",errors="replace",env=env,timeout=25)
            need(check.returncode==0 and
                 "READY:" in check.stdout,
                 "EXTRACTED_LAUNCHER_DEPENDENCY_CHECK_FAILED")
            report["extracted_cmd_check_pass"]=True
            session_home=home/"SIMC_Secondary_Optimizer"/"runs"
            need(not session_home.exists(),"CHECK_MUST_NOT_CREATE_SESSIONS")
            log_file=(out/"V345_WINDOWS_PACKAGED_LAUNCHER.log").open(
                "w",encoding="utf8")
            proc=start_cmd(root,home,log_file)
            report["launched_extracted_cmd"]=True
            driver=actual_chrome()
            report["used_actual_chrome"]=True
            ui=driver.execute_script("""
              return {
                supported:state.defaults.length,
                token:state.token,
                assets:!!document.getElementById("start-btn"),
                sourceCode:buildRequest.toString().includes("current_season_product"),
                sourceHash:state.session
              };
            """)
            need(ui["supported"]==26 and ui["assets"] and ui["sourceCode"] and
                 not ui["sourceHash"],"PACKAGED_CHROME_INIT_INVALID")
            # This is a *user scenario preflight*, not a simulation start.
            # The product intentionally hides the 0-Native plan button.
            # Send its unmodified actual browser form to the same real HTTP
            # route v181 already verified, then inspect persisted receipt.
            driver.execute_script("""
              document.getElementById("simc-technical-panel").open=true;
              document.getElementById("binary").value=arguments[0];
              document.getElementById("revision").value=arguments[1];
            """,str(exe),REV)
            invalid=driver.execute_script("""
              return Array.from(document.querySelectorAll(
                '#optimizer-form input, #optimizer-form select'))
                .filter(e=>e.willValidate && !e.validity.valid)
                .map(e=>({id:e.id||e.dataset.field||"unknown",
                          flags:{missing:e.validity.valueMissing,
                            mismatch:e.validity.patternMismatch,
                            range:e.validity.rangeOverflow||
                                  e.validity.rangeUnderflow}}));
            """)
            report["browser_invalid_input_fields"]=invalid
            need(not invalid,"READY_BROWSER_FORM_INVALID_BEFORE_PLAN")
            payload=driver.execute_script("return buildRequest();")
            need(payload["current_season_product"] is True and
                 payload["binary"]==str(exe) and payload["revision"]==REV and
                 payload["controls"]["ilevel"]==334 and
                 len(payload["controls"]["trinket_ids"])==2 and
                 payload["controls"]["final_T"] is None,
                 "ORIGINAL_VISIBLE_USER_CONTROLS_INVALID")
            st,plan=http_json("/api/v1/sessions/plan",token=ui["token"],body=payload)
            need(st==200 and plan.get("native_calls")==0 and
                 plan.get("session_id") and
                 re.fullmatch(r"[0-9a-f]{20}",plan["session_id"]),
                 "PACKAGED_REAL_HTTP_SOURCE_PLAN_INVALID")
            sid=plan["session_id"]
            report["saved_session_id_sha256"]=hashlib.sha256(sid.encode()).hexdigest()
            report["plan_native_calls"]=plan["native_calls"]
            report["initial_user_spec"]=(payload["controls"]["class"]+"/"+
                                         payload["controls"]["spec"])
            st,snapshot=http_json("/api/v1/sessions/"+sid+"/inputs",
                                  token=ui["token"])
            need(st==200 and snapshot["user"]["target"]["ilevel"]==334,
                 "PLAN_INPUTS_NOT_PERSISTED")
            st,sessions=http_json("/api/v1/sessions",token=ui["token"])
            need(st==200 and sessions.get("read_only") is True and
                 sessions.get("native_calls_now")==0 and
                 any(s["session_id"]==sid for s in sessions.get("sessions",[])),
                 "PLAN_MISSING_FROM_READ_ONLY_SESSION_INDEX")
            report["verified_saved_user_inputs"]=True
            need(session_home.exists(),"USERPROFILE_SESSION_NOT_STORED_OUTSIDE_ZIP")
            driver.quit();driver=None
            stop_cmd(proc);proc=None
            # Same extracted application, new operating-system CMD/Python
            # process, same isolated home; no cached process or mock API.
            proc=start_cmd(root,home,log_file)
            driver=actual_chrome()
            WebDriverWait(driver,30).until(
                lambda d: d.find_element(By.ID,"recent-session-id").
                          find_elements(By.TAG_NAME,"option") and
                          any(x.get_attribute("value")==sid for x in
                          d.find_element(By.ID,"recent-session-id").
                          find_elements(By.TAG_NAME,"option")))
            driver.find_element(By.CSS_SELECTOR,"details.restore > summary").click()
            Select(driver.find_element(By.ID,"recent-session-id")).select_by_value(sid)
            driver.find_element(By.ID,"recent-open-btn").click()
            WebDriverWait(driver,35).until(
                lambda d: d.execute_script(
                    "return state.session===arguments[0] && !state.busy && "+
                    "document.getElementById('notice').textContent.includes("+
                    "'기존 세션·입력 복원 성공')",sid))
            final=driver.execute_script("""
               return {
                 sid:state.session, restored:field("spec"),
                 level:Number(field("ilevel")),
                 binary:field("binary"),revision:field("revision"),
                 running:state.running,sessionLabel:document.getElementById(
                   "run-label").textContent
               };
            """)
            need(final["sid"]==sid and
                 final["restored"]==payload["controls"]["class"]+"/"+
                                    payload["controls"]["spec"] and
                 final["level"]==334 and
                 final["binary"]==str(exe) and
                 final["revision"]==REV and not final["running"],
                 "ACTUAL_RESTART_AND_CHROME_SESSION_RESTORE_MISMATCH")
            st,progress=http_json("/api/v1/sessions/"+sid+"/status",
                                  token=driver.execute_script("return state.token"))
            need(st==200 and not progress["active"] and
                 progress["progress"]["native_attempts"]==0,
                 "PACKAGE_RESTORE_ACCIDENTALLY_RAN_SIMC")
            report["restart_new_cmd_process"]=True
            report["restored_saved_inputs_from_visible_list"]=True
            report["restored_session_native_attempts"]=0
            report["simc_binary_outside_package"]=True
            report["status"]="PASS_EXTRACTED_WIN_CMD_REAL_CHROME_SAVED_SESSION_ZERO_NATIVE"
            save()
            print("V345_PACKAGE_USER_PATH "+json.dumps({
                k:report[k] for k in ("status","package_files",
                    "latest_runtime_source_bytes_unchanged",
                    "restored_saved_inputs_from_visible_list",
                    "new_dps_native_calls","new_environment_native_calls")},
                ensure_ascii=False),flush=True)
        except BaseException as exc:
            report["status"]="BLOCKED_OR_PARTIAL_"+type(exc).__name__
            message=str(exc)
            report["error_code"]=message if re.fullmatch(
                r"V345_[A-Z_0-9]{3,120}",message) else type(exc).__name__
            save()
            raise
        finally:
            if driver:
                try:driver.quit()
                except Exception:pass
            if proc:stop_cmd(proc)
            if log_file:log_file.close()

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--zip",type=pathlib.Path,required=True)
    ap.add_argument("--simc",type=pathlib.Path,required=True)
    ap.add_argument("--out",type=pathlib.Path,required=True)
    args=ap.parse_args()
    run(args.zip,args.simc,args.out)
