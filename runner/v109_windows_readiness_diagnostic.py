#!/usr/bin/env python3
"""v109 Windows user readiness: zero-Native plan, private-safe receipt ZIP.

Only the existing v106 user controls and v098 plan-only builder are invoked.
Does not execute, discover, or assert the real SimC revision, nor prove DPS.
Keep raw binary path, talents, player settings and profile out of the export.
"""
from __future__ import annotations
import hashlib,json,os,pathlib,platform,sys,uuid,zipfile
import v098_target_user_scenario_bootstrap as bootstrap
import v106_user_session_controller as sessions

SCHEMA="v109_windows_p1_readiness_no_native_v1"
ROOT=pathlib.Path.home()/"SIMC_Secondary_Optimizer"/"diagnostics"

def _filename(reason):
    return str(reason).split(":",1)[0].split("\n",1)[0][:100]

def safe_receipt(user,binary,revision,static_cache=None,*,root=None):
    """Prepare a normal session without invoking SimC; return sanitized receipt.

    The zip excludes uploaded gear profile, full user JSON, raw logs,
    executable bytes and machine-specific paths.
    """
    data={"schema":SCHEMA,"status":"BLOCKED",
          "new_native_calls":0,"revision_binary_match_verified":False,
          "Windows_GUI_clicked":False,"Windows_real_SimC_executed":False,
          "cancel_during_native_tested":False,
          "resume_after_cancel_tested":False,
          "os_family":platform.system(),"python_version":
             ".".join(map(str,sys.version_info[:3]))}
    try:
        # UI user info stays in private session folder; no original text in zip.
        need_user=isinstance(user,dict)
        if not need_user:raise ValueError("V109_USER_JSON_REQUIRED")
        file=pathlib.Path(binary).expanduser().resolve()
        if os.name=="nt":
            if file.suffix.lower()!=".exe":
                raise ValueError("V109_WINDOWS_EXECUTABLE_EXE_REQUIRED")
            with file.open("rb") as fh:
                if fh.read(2)!=b"MZ":
                    raise ValueError("V109_WINDOWS_PE_HEADER_NOT_PRESENT")
        scope=root if root is not None else sessions.DEFAULT_ROOT
        folder=sessions.store_session(user,scope,file,revision,static_cache)
        prepared=bootstrap.build(user,folder/"generated",file,revision,
                                 static_cache_path=static_cache)
        plan=prepared["plan"]
        if plan["native_called"] or prepared["native_calls"]!=0:
            raise ValueError("V109_UNEXPECTED_NATIVE_IN_PREFLIGHT")
        if (plan["native_min_calls"],plan["native_limit"])!=(6,6):
            raise ValueError("V109_UNEXPECTED_NATIVE_CALL_LIMIT")
        if not plan["class"] or not plan["spec"]:
            raise ValueError("V109_SPEC_MISSING")
        if (plan["base_B"]+sum(plan["fixed_O"].values())!=
            plan["final_T"]):
            raise ValueError("V109_B_O_T_DRIFT")
        data.update({
            "status":"PASS_ZERO_NATIVE_PLAN_ONLY",
            "spec":plan["class"]+"/"+plan["spec"],
            "target_ilevel":prepared["target_ilevel"],
            "base_B":plan["base_B"],"oil_O_total":sum(plan["fixed_O"].values()),
            "final_T":plan["final_T"],"physical_item_slots":plan["item_slots"],
            "tier_slots":prepared["effective_four_tier_slots"],
            "minimum_native_calls_if_started":plan["native_min_calls"],
            "maximum_native_calls_if_started":plan["native_limit"],
            "session_key":folder.name,
            "binary_sha256":sessions.sha(file.read_bytes()),
            "binary_suffix":file.suffix.lower(),
            "source_provenance_present":True,
            "simc_executable_functionality_tested":False,
            "caution":"Executable hash exists but binary revision and SimC behavior not verified"})
        # Do not open an executable or import untrusted output from it.
    except Exception as exc:
        data.update({"status":"BLOCKED_NO_NATIVE",
                    "blocker_class":type(exc).__name__,
                    "blocker_code":_filename(str(exc))})
    return data

def archive_receipt(receipt,out=None,open_folder=False):
    dest=pathlib.Path(out).expanduser().resolve() if out else ROOT
    dest.mkdir(parents=True,exist_ok=True)
    path=dest/("V109_READINESS_"+uuid.uuid4().hex[:10]+".zip")
    clean=json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    with zipfile.ZipFile(path,"w",compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("V109_READINESS_RECEIPT.json",clean)
        z.writestr("READ_ME_FIRST.txt",
                   "SIMC SECONDARY OPTIMIZER — Windows readiness receipt\n"
                   "This ZIP does not contain player talents, entire equipment,"
                   " file paths, the executable, profile or Native JSON.\n"
                   "PASS_ZERO_NATIVE_PLAN_ONLY only verifies the internal"
                   " six-call input plan; real SimC revision/GUI/cancel/resume"
                   " require a later actual Windows test.\n")
    if open_folder and os.name=="nt":
        try:os.startfile(str(dest))
        except Exception:pass
    return path
