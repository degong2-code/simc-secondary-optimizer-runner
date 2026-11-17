#!/usr/bin/env python3
"""v574: simulated absence of Python and winget decision boundaries of the
exact extracted Windows ZIP BAT. Windows command stubs are confined to a
temporary PATH. No real winget install is attempted or claimed. Native 0.
"""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib,re,shutil,subprocess,tempfile,zipfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
PREFIX="SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA"
NAME="V574_WINDOWS_PYTHON_ABSENT_WINGET_CONSENT_DRYRUN.json"
SCHEMA="p1_v574_windows_no_python_winget_dry_run_only_v1"

def need(ok,reason):
    if not ok:raise RuntimeError("V574_"+reason)

def run(zip_file,out):
    need(os.name=="nt","WINDOWS_ONLY")
    zip_file=pathlib.Path(zip_file).resolve(strict=True)
    out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    receipt=out/NAME
    report={
        "schema":SCHEMA,"status":"STARTED","native_calls":0,
        "actual_winget_invocations":0,"real_python_installation_attempted":False,
        "real_python_absent_on_ci_runner":False,
        "simulated_python_absence_only":True,
        "simulated_winget_only":True,
        "no_consent_no_winget":False,
        "consent_winget_once_then_manual_when_no_python_visible":False,
        "winget_unavailable_returns_manual":False,
        "no_user_venv_or_sessions_created":False,
        "personal_pc_tested":False}
    def save():
        receipt.write_text(json.dumps(report,ensure_ascii=False,
             sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf8")
    save()
    root=None
    try:
        with tempfile.TemporaryDirectory(prefix="v574-windows-no-python-",dir=out) as dirname:
            temp=pathlib.Path(dirname)
            root=temp/PREFIX
            with zipfile.ZipFile(zip_file) as z:
                entries=z.namelist()
                need(len(entries)==len(set(entries)) and all(
                    n.startswith(PREFIX+"/") and
                    ".." not in pathlib.PurePosixPath(n).parts
                    for n in entries),"EXTRACTED_ZIP_PATH_POLICY")
                doc=json.loads(z.read(PREFIX+"/V181_PACKAGE_MANIFEST.json"))
                rec=doc["files"]
                need(len(rec)==doc["file_count"] and len(rec)>=75 and
                     not doc["native_executable_bundled"] and
                     not doc["sessions_bundled"] and
                     not doc["historical_native_json2_bundled"],
                     "ZIP_NOT_SOURCE_ONLY")
                for obj in rec:
                    raw=z.read(PREFIX+"/"+obj["path"])
                    need(hashlib.sha256(raw).hexdigest()==obj["sha256"] and
                         len(raw)==obj["size"],"ZIP_SHA_MISMATCH")
                need(hashlib.sha256(z.read(
                    PREFIX+"/START_HERE_AUTO_SETUP_AND_RUN.bat")).digest()==
                    hashlib.sha256((ROOT/"START_HERE_AUTO_SETUP_AND_RUN.bat")
                                   .read_bytes()).digest(),
                    "EXACT_PACKAGED_INSTALLER_BYTES_CHANGED")
                z.extractall(temp)
            fake=temp/"fixture-bin";fake.mkdir()
            # Windows batch invokes WHERE without CALL. A .cmd shim would
            # *replace* execution of the parent .bat, not return to it.
            # Instead copy a harmless built-in Windows command EXE under
            # the names py/python/winget. WHERE finds them, their version/
            # install arguments fail, and no real OS Python/winget executes.
            system_where=pathlib.Path(os.environ.get(
                "SystemRoot","C:\\Windows"))/"System32"/"where.exe"
            need(system_where.is_file(),"WINDOWS_WHERE_EXE_MISSING")
            for name in ("py.exe","python.exe","winget.exe"):
                shutil.copy2(system_where,fake/name)
            appdata=temp/"isolated-appdata";appdata.mkdir()
            home=temp/"isolated-home";home.mkdir()
            sysroot=pathlib.Path(os.environ.get("SystemRoot","C:\\Windows"))
            env={**os.environ,
                "PATH":str(fake)+";"+str(sysroot/"System32"),
                "LOCALAPPDATA":str(appdata),"USERPROFILE":str(home),
                "HOME":str(home),
                "PYTHONIOENCODING":"utf-8"}
            def invoke(winget_present,keyboard):
                target=fake/"winget.exe"
                # Simulate winget absent by removing only the temporary
                # harmless dummy command, never a system executable.
                if not winget_present:
                    target.unlink(missing_ok=True)
                elif not target.exists():
                    shutil.copy2(system_where,target)
                return subprocess.run(["cmd","/d","/c",
                      str(root/"START_HERE_AUTO_SETUP_AND_RUN.bat")],
                    cwd=root,env=env,input=keyboard,
                    stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                    encoding="utf8",errors="replace",timeout=20)
            # Simulated 'py/python' missing, winget available, user declines
            # both winget and opening a browser. No winget command invocation.
            refuse=invoke(True,"N\nN\nx\n")
            report["no_consent_diagnostic"]={
                "exit":refuse.returncode,
                "where_found_dummy_winget":(fake/"winget.exe").exists(),
                "python_missing_text":"Python 3.12 or newer was not found." in refuse.stdout,
                "manual_text":"Please install Python 3.12+" in refuse.stdout,
                "tail":refuse.stdout[-450:]}
            save()
            need(refuse.returncode==1 and
                 "Python 3.12 or newer was not found." in refuse.stdout and
                 "Please install Python 3.12+" in refuse.stdout,
                 "WINGET_NO_CONSENT_SHOULD_NOT_CALL")
            report["no_consent_no_winget"]=True
            # User consents to a harmless dummy EXE. It can report a zero
            # exit code while NOT installing Python. The original BAT must
            # recheck, find no Python, and offer manual setup, never READY.
            agreed=invoke(True,"Y\nN\nx\n")
            report["stub_winget_failure_diagnostic"]={
                "exit":agreed.returncode,
                "offered_manual_python":
                    "Please install Python 3.12+" in agreed.stdout,
                "install_attempted_success_text":
                    "Installation attempted. Rechecking" in agreed.stdout}
            save()
            need(agreed.returncode==1 and
                 "Please install Python 3.12+" in agreed.stdout and
                 "Installation attempted. Rechecking" in agreed.stdout and
                 "[READY]" not in agreed.stdout,
                 "DUMMY_WINGET_SUCCESS_NOT_MISLABELLED_PYTHON_READY")
            report["consent_winget_once_then_manual_when_no_python_visible"]=True
            # winget itself not found, so only a manual Python link is
            # suggested, never an automatic alternative source.
            missing=invoke(False,"N\nx\n")
            need(missing.returncode==1 and
                 "Please install Python 3.12+" in missing.stdout,
                 "NO_WINGET_MUST_STAY_MANUAL")
            report["winget_unavailable_returns_manual"]=True
            need(not (appdata/"SIMC_Secondary_Optimizer").exists() and
                 not (home/"SIMC_Secondary_Optimizer").exists(),
                 "MOCK_MISSING_PYTHON_CREATED_SESSION_OR_VENV")
            report["no_user_venv_or_sessions_created"]=True
            report["packaged_files"]=len(rec)
            report["status"]="PASS_WINDOWS_ZIP_PYTHON_ABSENT_WINGET_OPT_IN_DRY_RUN_NO_NATIVE"
            save()
            print("V574_WINDOWS_NO_PYTHON_DRYRUN "+
                json.dumps({k:report[k] for k in (
                    "status","no_consent_no_winget",
                    "consent_winget_once_then_manual_when_no_python_visible",
                    "winget_unavailable_returns_manual","native_calls")},
                    sort_keys=True),flush=True)
            return 0
    except Exception as exc:
        report["status"]="BLOCKED_OR_PARTIAL_"+type(exc).__name__
        code=str(exc).split(":",1)[0]
        report["first_blocker"]=code if re.fullmatch(
            r"V574_[A-Z_]{4,100}",code) else type(exc).__name__
        save()
        print("V574_WINDOWS_NO_PYTHON_VERDICT "+
              json.dumps({k:report.get(k) for k in (
                  "status","first_blocker","native_calls")},
                  sort_keys=True),flush=True)
        return 2

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--zip",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    args=p.parse_args()
    raise SystemExit(run(args.zip,args.out))
