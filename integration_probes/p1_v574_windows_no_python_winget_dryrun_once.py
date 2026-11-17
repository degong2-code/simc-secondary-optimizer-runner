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
            (fake/"where.cmd").write_text(
                '@echo off\n'
                'if /I "%~1"=="py" exit /b 1\n'
                'if /I "%~1"=="python" exit /b 1\n'
                'if /I "%~1"=="winget" (\n'
                '  if "%V574_WINGET_PRESENT%"=="1" exit /b 0\n'
                '  exit /b 1\n'
                ')\n'
                '"%SystemRoot%\\System32\\where.exe" %*\n',
                encoding="ascii")
            (fake/"winget.cmd").write_text(
                '@echo off\n'
                'echo V574_WINGET_STUB_CALLED>>"%V574_WINGET_LOG%"\n'
                'exit /b 0\n',encoding="ascii")
            appdata=temp/"isolated-appdata";appdata.mkdir()
            home=temp/"isolated-home";home.mkdir()
            winget_log=temp/"mock-winget.log"
            sysroot=pathlib.Path(os.environ.get("SystemRoot","C:\\Windows"))
            env={**os.environ,
                "PATH":str(fake)+";"+str(sysroot/"System32"),
                "LOCALAPPDATA":str(appdata),"USERPROFILE":str(home),
                "HOME":str(home),"V574_WINGET_LOG":str(winget_log),
                "PYTHONIOENCODING":"utf-8"}
            def invoke(winget_present,keyboard):
                env["V574_WINGET_PRESENT"]="1" if winget_present else "0"
                return subprocess.run(["cmd","/d","/c",
                      str(root/"START_HERE_AUTO_SETUP_AND_RUN.bat")],
                    cwd=root,env=env,input=keyboard,
                    stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                    encoding="utf8",errors="replace",timeout=20)
            # Simulated 'py/python' missing, winget available, user declines
            # both winget and opening a browser. No winget command invocation.
            refuse=invoke(True,"N\nN\nx\n")
            need(refuse.returncode==1 and
                 "Python 3.12 or newer was not found." in refuse.stdout and
                 "Please install Python 3.12+" in refuse.stdout and
                 not winget_log.exists(),"WINGET_NO_CONSENT_SHOULD_NOT_CALL")
            report["no_consent_no_winget"]=True
            # If user opted in to winget but it did not actually install
            # Python, a success code from winget alone must NEVER be
            # mistaken for an installed runtime/ready local server.
            agreed=invoke(True,"Y\nN\nx\n")
            calls=(winget_log.read_text("ascii").splitlines()
                    if winget_log.exists() else [])
            need(agreed.returncode==1 and len(calls)==1 and
                 "Installation attempted. Rechecking" in agreed.stdout and
                 "Please install Python 3.12+" in agreed.stdout,
                 "WINGET_NOOP_STUB_NOT_HANDLED_AS_MISSING_PYTHON")
            report["consent_winget_once_then_manual_when_no_python_visible"]=True
            # winget itself not found, so only a manual Python link is
            # suggested, never an automatic alternative source.
            winget_log.unlink(missing_ok=True)
            missing=invoke(False,"N\nx\n")
            need(missing.returncode==1 and not winget_log.exists() and
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
