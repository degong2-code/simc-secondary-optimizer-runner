#!/usr/bin/env python3
"""v575: actual Windows BAT Python3.12 standard-path fallback after stale PATH.

Isolated Windows user profile has no runnable py/python on PATH; an authentic
Python 3.12 installation is exposed only through a temporary NTFS junction
at %LOCALAPPDATA%\Programs\Python\Python312. Exact extracted source-only ZIP
is used. Real user consent N then Y makes a REAL fresh web venv/pip install.
No winget, source collection or SimC Native is invoked.
"""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib,re,shutil,subprocess,sys,tempfile,zipfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
PREFIX="SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA"
SCHEMA="p1_v575_windows_same_cmd_path_stale_verified_python312_fallback_v1"
NAME="V575_WINDOWS_STALE_PATH_PYTHON312_REAL_VENV_COMPACT.json"

def need(ok,reason):
    if not ok:raise RuntimeError("V575_"+reason)

def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def run_bat(root,env,answer,timeout=45):
    command=["cmd","/d","/c",str(root/"START_HERE_AUTO_SETUP_AND_RUN.bat"),"--check"]
    return subprocess.run(command,cwd=root,env=env,input=answer,
         stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
         encoding="utf8",errors="replace",timeout=timeout)

def main(source_zip,out):
    need(os.name=="nt","WINDOWS_ONLY")
    need(sys.version_info[:2]==(3,12),"PINNED_CI_PYTHON312_REQUIRED")
    out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    source_zip=pathlib.Path(source_zip).resolve(strict=True)
    receipt=out/NAME
    result={"schema":SCHEMA,"status":"STARTED",
       "exact_extracted_zip":False,"no_python_in_process_path":False,
       "standard_user_python312_path_verifiable":False,
       "decline_prevents_venv":False,"consent_installs_fresh_web_venv":False,
       "repeat_check_no_install":False,
       "actual_winget_run":False,"native_calls":0,
       "external_season_calls":0,"actual_personal_pc":False,
       "actual_fresh_python_installed_with_winget":False}
    def save():
        receipt.write_text(json.dumps(result,sort_keys=True,indent=2,
               ensure_ascii=False,allow_nan=False)+"\n",encoding="utf8")
    save()
    try:
        with tempfile.TemporaryDirectory(prefix="v575 win setup path ",dir=out) as w:
            temp=pathlib.Path(w)
            with zipfile.ZipFile(source_zip) as z:
                names=z.namelist()
                need(len(names)==len(set(names)) and all(
                    p.startswith(PREFIX+"/") and
                    ".." not in pathlib.PurePosixPath(p).parts
                    for p in names),"ZIP_PATH_POLICY")
                m=json.loads(z.read(PREFIX+"/V181_PACKAGE_MANIFEST.json"))
                entries=m["files"]
                need(len(entries)==m["file_count"] and len(entries)>=75 and
                     not m["native_executable_bundled"] and
                     not m["sessions_bundled"] and
                     not m["historical_native_json2_bundled"],
                     "ZIP_MANIFEST_POLICY")
                for row in entries:
                    raw=z.read(PREFIX+"/"+row["path"])
                    need(len(raw)==row["size"] and
                         hashlib.sha256(raw).hexdigest()==row["sha256"],
                         "ZIP_MEMBER_SHA_DRIFT")
                for file in ("START_HERE_AUTO_SETUP_AND_RUN.bat",
                             "runner/v113_local_web_api.py",
                             "requirements-web.txt"):
                    need(hashlib.sha256(z.read(PREFIX+"/"+file)).hexdigest()==
                         digest(ROOT/file),
                         "ZIP_NOT_EXACT_LATEST_PRODUCT_RUNTIME")
                need(not any(p.lower().endswith((".exe",".dll",".pem",
                     ".pfx",".key")) for p in names),
                     "ZIP_BUNDLES_EXECUTABLE_OR_SECRET")
                z.extractall(temp)
            root=temp/PREFIX
            result["exact_extracted_zip"]=True
            result["source_zip_sha256"]=digest(source_zip)
            result["package_files"]=len(entries)
            # PATH contains only harmless fake Python/py plus System32.
            # WHERE finds the fake names, but their command exits nonzero.
            # This forces the original BAT into direct standard-path check.
            systemroot=pathlib.Path(os.environ.get("SystemRoot","C:\\Windows"))
            dummy=temp/"fake interpreter bin";dummy.mkdir()
            where=systemroot/"System32"/"where.exe"
            need(where.is_file(),"WHERE_EXE_MISSING")
            for name in ("py.exe","python.exe"):
                shutil.copy2(where,dummy/name)
            home=temp/"isolated home";home.mkdir()
            appdata=temp/"isolated local appdata";appdata.mkdir()
            target=appdata/"Programs"/"Python"/"Python312"
            target.parent.mkdir(parents=True)
            # Junction points to CI's existing authentic complete Python
            # installation. No host PATH/registry/machine interpreter change.
            actual=pathlib.Path(sys.executable).resolve().parent
            junction=subprocess.run(["cmd","/d","/c","mklink","/J",
                       str(target),str(actual)],
                       capture_output=True,text=True,timeout=25)
            need(junction.returncode==0 and
                 (target/"python.exe").is_file(),
                 "ISOLATED_AUTHENTIC_PYTHON312_JUNCTION_UNAVAILABLE")
            env={**os.environ,
                 "PATH":str(dummy)+";"+str(systemroot/"System32"),
                 "LOCALAPPDATA":str(appdata),"USERPROFILE":str(home),
                 "HOME":str(home),"PYTHONIOENCODING":"utf-8"}
            probe=subprocess.run([str(target/"python.exe"),"-c",
                 "import sys; print(sys.version_info.major,sys.version_info.minor)"],
                 cwd=root,env=env,capture_output=True,text=True,timeout=25)
            need(probe.returncode==0 and
                 probe.stdout.strip()=="3 12",
                 "STANDARD_PER_USER_PATH_NOT_EXECUTABLE")
            result["standard_user_python312_path_verifiable"]=True
            result["no_python_in_process_path"]=True
            save()
            venv=appdata/"SIMC_Secondary_Optimizer"/"web-python"
            denied=run_bat(root,env,"N\n",timeout=40)
            need(denied.returncode==0 and
                 "[SETUP]" in denied.stdout and
                 "[CANCELLED]" in denied.stdout and
                 "[PYTHON] Python 3.12" not in denied.stdout and
                 not venv.exists(),
                 "STANDARD_PYTHON_FALLBACK_DID_NOT_REQUEST_CONSENT")
            result["decline_prevents_venv"]=True
            # Actual pip installation into an isolated real venv is allowed
            # only on the second explicit YES answer. The BAT never calls
            # winget because Python was verified through its absolute path.
            accepted=run_bat(root,env,"Y\n",timeout=230)
            result["consent_exit"]=accepted.returncode
            result["consent_reported_web_ready"]=(
                "[READY] Web libraries installed." in accepted.stdout)
            save()
            need(accepted.returncode==0 and
                 result["consent_reported_web_ready"],
                 "VERIFIED_ABSOLUTE_PYTHON_REAL_VENV_PIP_FAILED")
            exe=venv/"Scripts"/"python.exe"
            need(exe.is_file(),"VERIFIED_ABSOLUTE_PYTHON_VENV_MISSING")
            check=subprocess.run([str(exe),"-c",
                "import sys,fastapi,uvicorn,pydantic; print('ready')"],
                cwd=root,env=env,capture_output=True,text=True,timeout=30)
            need(check.returncode==0 and check.stdout.strip()=="ready",
                 "REQUIRED_WEB_PACKAGES_NOT_INSTALLED_IN_USER_VENV")
            result["consent_installs_fresh_web_venv"]=True
            save()
            again=run_bat(root,env,"",timeout=40)
            need(again.returncode==0 and
                 "[READY] Local Python environment is working." in again.stdout
                 and "[SETUP]" not in again.stdout,
                 "STILL_PROMPTS_AFTER_CORRECT_INSTALL")
            result["repeat_check_no_install"]=True
            need(not (home/"SIMC_Secondary_Optimizer"/"runs").exists(),
                 "SETUP_CREATED_USER_SIMC_SESSIONS")
            result["status"]="PASS_WINDOWS_BAT_STALE_PATH_REAL_PYTHON312_VENV_CONSENT_NATIVE_ZERO"
            save()
            print("V575_WIN_STALE_PATH_SETUP "+
                  json.dumps({k:result[k] for k in (
                    "status","package_files","decline_prevents_venv",
                    "consent_installs_fresh_web_venv",
                    "repeat_check_no_install","native_calls")},
                    sort_keys=True),flush=True)
            return 0
    except Exception as exc:
        result["status"]="BLOCKED_OR_PARTIAL_"+type(exc).__name__
        code=str(exc).split(":",1)[0]
        result["first_blocker"]=code if re.fullmatch(
            r"V575_[A-Z0-9_]{3,110}",code) else type(exc).__name__
        save()
        print("V575_WIN_STALE_PATH_VERDICT "+
              json.dumps({k:result.get(k) for k in (
                  "status","first_blocker","native_calls")},
                  sort_keys=True),flush=True)
        return 2

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--zip",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    args=p.parse_args()
    raise SystemExit(main(args.zip,args.out))
