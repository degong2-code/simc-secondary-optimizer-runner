#!/usr/bin/env python3
"""v573: real extracted Windows beta ZIP easy-start bootstrap, cold user-local
web venv with actual user-decision branch and real pip install of requirements.

Zero SimC Native or season Build. Windows CI's Python 3.12 is already
installed; this is NOT proof of winget installing Python on a personal PC.
"""
from __future__ import annotations

import argparse,hashlib,json,os,pathlib,re,shutil,subprocess,sys,tempfile,time,zipfile
from urllib.request import urlopen
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"integration_probes"))
from p1_v571_windows_extracted_easy_start_restore_no_native import (
    PREFIX,wait_for_http,stop_cmd,actual_chrome)
from p1_v345_windows_extracted_zip_cmd_browser_restore import digest

SCHEMA="p1_v573_real_windows_zip_cold_web_dependencies_explicit_consent_v1"
NAME="V573_WINDOWS_COLD_SETUP_EXPLICIT_CONSENT_COMPACT.json"

def need(value,reason):
    if not value:raise RuntimeError("V573_"+reason)

def run_bat(root,env,argument,keyboard,timeout=40):
    invocation=["cmd","/d","/c",str(root/"START_HERE_AUTO_SETUP_AND_RUN.bat")]
    if argument:invocation.append(argument)
    command=subprocess.run(invocation,cwd=root,env=env,
        input=keyboard,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
        encoding="utf8",errors="replace",timeout=timeout)
    return command.returncode,command.stdout

def start_server(root,env,log):
    p=subprocess.Popen(["cmd","/d","/c",
        str(root/"START_HERE_AUTO_SETUP_AND_RUN.bat")],
        cwd=root,env=env,stdin=subprocess.DEVNULL,
        stdout=log,stderr=subprocess.STDOUT)
    wait_for_http(p)
    return p

def check_browser():
    browser=actual_chrome()
    try:
        info=browser.execute_script("""
          return {
            supported:state.defaults.length, token:!!state.token,
            session:state.session,
            start_label:document.getElementById("start-btn").textContent,
            setupCalls:performance.getEntriesByType("resource").map(e=>e.name)
              .filter(n=>n.includes("/season-build")||
                         n.includes("/longrun/start")||
                         n.includes("/sessions/plan"))
          };
        """)
        need(info["supported"]==26 and info["token"] and
             not info["session"] and
             info["start_label"]=="시즌 환경 준비 · 장신구 목록 불러오기" and
             not info["setupCalls"],"FRESH_USER_CHROME_TRIGGERED_NATIVE_OR_BUILD")
        return {"visible_26_dps":True,
                "first_user_environment_button":True,
                "no_implicit_source_or_dps_request":True}
    finally:
        browser.quit()

def run(zip_file,out,*,before_first_server=None,continue_after_cold_browser=None):
    need(os.name=="nt","WINDOWS_ONLY")
    zip_file=pathlib.Path(zip_file).resolve(strict=True)
    out=pathlib.Path(out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    receipt=out/NAME
    evidence={"schema":SCHEMA,"status":"STARTED",
       "native_calls":0,"season_build_calls":0,
       "real_windows_extracted_zip":False,
       "existing_system_python_3_12_plus":False,
       "user_local_venv_preexisted":False,
       "user_consent_no_prevents_dependency_install":False,
       "user_consent_yes_performed_real_pip_install":False,
       "pip_installed_packages_only_in_isolated_user_appdata":False,
       "preexisting_user_session_modified":False,
       "real_cold_chrome_no_native":False,
       "first_python_install_via_winget_tested":False,
       "personal_windows_pc_tested":False}
    def save():
        receipt.write_text(json.dumps(evidence,sort_keys=True,indent=2,
                          ensure_ascii=False,allow_nan=False)+"\n","utf8")
    save()
    proc=None;log=None;work=None
    try:
        work=pathlib.Path(tempfile.mkdtemp(prefix="v573-windows-first-web-",dir=out))
        home=work/"user-home";home.mkdir()
        appdata=work/"local-appdata";appdata.mkdir()
        root=work/PREFIX
        with zipfile.ZipFile(zip_file) as z:
            names=z.namelist()
            need(len(names)==len(set(names)) and all(
                n.startswith(PREFIX+"/") and
                ".." not in pathlib.PurePosixPath(n).parts for n in names),
                "ZIP_PATH_POLICY_INVALID")
            manifest=json.loads(z.read(PREFIX+"/V181_PACKAGE_MANIFEST.json"))
            records=manifest["files"]
            need(len(records)==manifest["file_count"] and len(records)>=75 and
                 not manifest["native_executable_bundled"] and
                 not manifest["sessions_bundled"] and
                 not manifest["historical_native_json2_bundled"],
                 "ZIP_PAYLOAD_POLICY_DRIFT")
            for record in records:
                raw=z.read(PREFIX+"/"+record["path"])
                need(len(raw)==record["size"] and
                     hashlib.sha256(raw).hexdigest()==record["sha256"],
                     "ZIP_SOURCE_MEMBER_SHA_DRIFT")
            for p in ("START_HERE_AUTO_SETUP_AND_RUN.bat",
                      "requirements-web.txt","runner/v113_local_web_api.py",
                      "runner/webui/app.js"):
                need(hashlib.sha256(z.read(PREFIX+"/"+p)).hexdigest()==
                     digest(ROOT/p),"PACKAGED_BOOTSTRAP_OR_WEB_BYTES_NOT_CURRENT")
            need(not any(n.lower().endswith((".exe",".dll",".pfx",".pem",
                  ".key")) for n in names),"EXE_OR_SECRET_BUNDLED")
            z.extractall(work)
        evidence["real_windows_extracted_zip"]=True
        evidence["source_zip_sha256"]=digest(zip_file)
        evidence["package_files"]=len(records)
        need(not (appdata/"SIMC_Secondary_Optimizer").exists(),
             "USER_APPDATA_NOT_EMPTY_BEFORE_SETUP")
        env={**os.environ,"HOME":str(home),"USERPROFILE":str(home),
             "LOCALAPPDATA":str(appdata),"PYTHONIOENCODING":"utf-8",
             "PYTHONDONTWRITEBYTECODE":"1"}
        # Avoid quoting a nested 'cmd /c ... && python -c' expression:
        # subprocess/Win32 quoting is not the semantics of the BAT's WHERE.
        # Verify the same PATH-exposed candidates directly, with each actual
        # interpreter's Python version and no accidental SimC execution.
        found={}
        selected=None
        for name,base_args in (("py",["-3"]),("python",[])):
            executable=shutil.which(name)
            record={"on_path":bool(executable),"supported":False}
            if executable:
                checked=subprocess.run([executable,*base_args,"-c",
                     "import sys; print(sys.version_info.major, sys.version_info.minor)"],
                     cwd=root,env=env,capture_output=True,text=True,timeout=20)
                match=re.fullmatch(r"3\s+(\d+)\s*",checked.stdout)
                record["version_minor"]=(int(match.group(1)) if match else None)
                record["supported"]=bool(checked.returncode==0 and match and
                                         int(match.group(1))>=12)
                if record["supported"]:
                    selected=name
                    found[name]=record
                    break
            found[name]=record
        evidence["windows_python_detection"]=found
        save()
        need(selected is not None,"WINDOWS_RUNNER_PYTHON_312_REQUIRED")
        evidence["existing_system_python_3_12_plus"]=True
        # Run --check on a freshly extracted ZIP. With no venv this is not
        # permitted to trigger pip without explicit interactive Y consent.
        code,output=run_bat(root,env,"--check","N\n",timeout=35)
        evidence["no_consent_exit"]=code
        evidence["no_consent_label"]="[CANCELLED]" in output
        evidence["venv_created_after_no"]=(
            appdata/"SIMC_Secondary_Optimizer"/"web-python").exists()
        need(code==0 and evidence["no_consent_label"] and
             not evidence["venv_created_after_no"],
             "FIRST_USER_CANCEL_IS_NOT_NO_WRITE_EXIT")
        evidence["user_consent_no_prevents_dependency_install"]=True
        # User explicitly chooses yes. The packaged BAT creates an entirely
        # fresh normal venv, uses its own pip with the exact packaged
        # requirements-web.txt and exits --check without starting a server.
        code,output=run_bat(root,env,"--check","Y\n",timeout=245)
        evidence["yes_consent_exit"]=code
        evidence["yes_consent_message"]=("[READY] Web libraries installed." in output)
        need(code==0 and evidence["yes_consent_message"],
             "REAL_USER_CONSENT_PIP_INSTALL_FAILED")
        venvpath=appdata/"SIMC_Secondary_Optimizer"/"web-python"
        python=venvpath/"Scripts"/"python.exe"
        need(python.is_file(),"ISOLATED_NORMAL_VENV_NOT_CREATED")
        check=subprocess.run([str(python),"-c",
           "import fastapi,uvicorn,pydantic,sys; print('WEB_READY')"],
           cwd=root,env=env,capture_output=True,text=True,timeout=35)
        need(check.returncode==0 and "WEB_READY" in check.stdout,
             "WEB_PACKAGES_NOT_IN_FRESH_VENV")
        evidence["user_consent_yes_performed_real_pip_install"]=True
        evidence["pip_installed_packages_only_in_isolated_user_appdata"]=True
        # Repeat check is idempotent and cannot reinstall requirements,
        # launch a server, or touch a user's saved SimC results.
        code,output=run_bat(root,env,"--check","",timeout=35)
        need(code==0 and "[READY] Local Python environment" in output and
             "[SETUP]" not in output and "[START]" not in output,
             "SECOND_CHECK_PROMPTED_TO_REINSTALL")
        evidence["already_ready_check_is_readonly"]=True
        session_root=home/"SIMC_Secondary_Optimizer"/"runs"
        need(not session_root.exists(),
             "INSTALL_OR_CHECK_CREATED_NATIVE_USER_SESSIONS")
        log=(out/"V573_WINDOWS_EXTRACTED_EASY_START_LOG.txt").open("w",encoding="utf8")
        # Optional one-shot CURRENT product acceptance hooks. Historical
        # v573 run() remains byte-for-byte equivalent without these. The
        # hook never authorizes old source files or disables genuine HTTPS.
        if before_first_server is not None:
            before_first_server(root,env,work)
        proc=start_server(root,env,log)
        evidence["real_cold_chrome_no_native"]=True
        evidence["browser"]=check_browser()
        save()
        if continue_after_cold_browser is not None:
            extra=continue_after_cold_browser(root,env,work)
            evidence["one_contiguous_first_user_check"]=extra
            if extra.get("status")!="PASS_REAL_FIRST_USER_SOURCE_AND_DPS":
                evidence["status"]="PENDING_FIRST_USER_"+str(
                    extra.get("first_blocker") or extra.get("status"))
                save()
                return 2
        evidence["status"]=(
            "PASS_REAL_WINDOWS_ZIP_COLD_SETUP_THROUGH_USER_DPS"
            if continue_after_cold_browser is not None else
            "PASS_REAL_WINDOWS_ZIP_COLD_WEB_DEPENDENCY_CONSENT_AND_FIRST_CHROME_NATIVE_ZERO")
        save()
        print("V573_WINDOWS_USER_SETUP "+json.dumps({
             k:evidence[k] for k in (
               "status","package_files",
               "user_consent_no_prevents_dependency_install",
               "user_consent_yes_performed_real_pip_install",
               "already_ready_check_is_readonly",
               "real_cold_chrome_no_native","native_calls")},
             sort_keys=True,ensure_ascii=True),flush=True)
        return 0
    except Exception as exc:
        evidence["status"]="BLOCKED_OR_PARTIAL_"+type(exc).__name__
        label=str(exc).split(":",1)[0]
        evidence["first_blocker"]=(
            label if re.fullmatch(r"V573_[A-Z0-9_]{3,90}",label)
            else type(exc).__name__)
        save()
        return 2
    finally:
        if proc:
            try:stop_cmd(proc)
            except Exception:pass
        if log:log.close()
        if work and work.is_dir():
            try:shutil.rmtree(work)
            except OSError:evidence["temporary_cleanup"]="WINDOWS_LIVE_HANDLE_PENDING";save()
        print("V573_SETUP_VERDICT "+json.dumps({
            k:evidence.get(k) for k in (
              "status","first_blocker",
              "no_consent_exit","yes_consent_exit",
              "real_cold_chrome_no_native","native_calls")},
            sort_keys=True,ensure_ascii=True),flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--zip",type=pathlib.Path,required=True)
    parser.add_argument("--out",type=pathlib.Path,required=True)
    args=parser.parse_args()
    raise SystemExit(run(args.zip,args.out))
