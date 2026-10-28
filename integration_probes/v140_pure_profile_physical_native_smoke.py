#!/usr/bin/env python3
"""Bounded local SimC physical acceptance for the source-independent P1 stage.

This is NOT the adaptive 6-candidate DPS optimizer, nor an independent
APL/gear-effects certification. Uses v098(pure_stage=True) for the actual
source-free user -> gear -> B/T/manifest profile, then ONLY strips numeric
gear_* overrides to inspect the physical sample's natural JSON2 rating.
The sealed v096 Native gate remains unchanged. Two cases max, one fresh
SimC execution each; verified identical receipts are reused, no repeat.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v098_target_user_scenario_bootstrap as bootstrap
import v122_common_profile_format as profile_format

SCHEMA="v140_pure_profile_physical_smoke_v1"
# Test inputs ONLY: commented upstream Midnight S2 generator draft talent
# selections (ilvl289 original equipment is NOT imported). This file is NOT
# an executable product dependency on a complete official MID2 profile.
ACTORS={
 "druid/balance":("night_elf",
  "CYGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWoMbNjxMDwsYmZmZhBjZZmlZYmZswyMLzMGzshhBYstMzgxsNCMBAAAYxMzMzgNDjxAAwMDMA"),
 "evoker/devastation":("dracthyr",
  "CsbBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzMDMDzgBmZGjZaYmpZMWmxMzMz8AzMzAmxMGzMLzMDMwYwCsMGN2GQmBBbYGMzghB")}
TRINKETS=(
 {"slot":"trinket1","item_id":250215,"options":{}},
 {"slot":"trinket2","item_id":281215,"options":{}})
DEFAULT_OUT=pathlib.Path.home()/"SIMC_Secondary_Optimizer"/"v140_pure_physical_smoke"
REMOVABLE=("gear_crit_rating=","gear_haste_rating=",
           "gear_mastery_rating=","gear_versatility_rating=")

class PhysicalSmokeBlocked(ValueError):
    pass

def need(condition,why):
    if not condition:
        raise PhysicalSmokeBlocked(why)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def canonical(doc):
    return json.dumps(doc,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False)+"\n"

def user_for(key):
    need(key in ACTORS,"SPEC_NOT_PILOTED")
    cl,spec=key.split("/")
    race,talents=ACTORS[key]
    return {"schema":bootstrap.SCHEMA,
            "character":{"class":cl,"spec":spec,"race":race,
                         "talents":talents},
            "target":{"ilevel":334,"final_T":None},
            "trinkets":[dict(x) for x in TRINKETS],
            "special_items":[],"embellishments":[],"oil_hands":[],
            "combat":{"targets":1,"duration_seconds":300,"raid_buffs":True}}

def physical_input(planned,json2_path,iterations):
    """Only remove the 4 free CHMV overrides, not real physical gear lines."""
    need(type(iterations) is int and 1<=iterations<=35,
         "PHYSICAL_PILOT_ITERATIONS")
    lines=planned.splitlines()
    for prefix in REMOVABLE:
        need(sum(x.startswith(prefix) for x in lines)==1,
             "EXPECTED_ONE_GEAR_OVERRIDE:"+prefix)
    need(sum(x.startswith("json2=") for x in lines)==1,
         "EXPECTED_ONE_JSON2_PLACEHOLDER")
    need("json2="+profile_format.JSON2_PLACEHOLDER in lines,
         "STAGED_PLAN_JSON2_PLACEHOLDER_REQUIRED")
    need(sum(x.startswith("iterations=") for x in lines)==1,
         "EXPECTED_ONE_ITERATIONS_SETTING")
    output=[]
    for line in lines:
        if any(line.startswith(prefix) for prefix in REMOVABLE):
            continue
        if line.startswith("json2="):
            output.append("json2="+str(json2_path.resolve()))
        elif line.startswith("iterations="):
            output.append("iterations="+str(iterations))
        else:
            output.append(line)
    rendered="\n".join(output)+"\n"
    need("default_actions=1" in output and
         not any(line.startswith("load_default_gear=") for line in output),
         "PHYSICAL_SOURCE_FREE_APL_OR_GEAR_CONTRACT")
    return rendered

def json2_summary(raw):
    data=json.loads(raw)
    players=(data.get("sim") or {}).get("players") or []
    need(len(players)==1,"JSON2_EXPECTED_ONE_PLAYER")
    player=players[0]
    need(isinstance(player,dict),"JSON2_PLAYER_OBJECT")
    return {"player_count":1,"report_version":data.get("report_version"),
            "player_name":player.get("name"),
            "specialization":player.get("specialization"),
            "dps_mean":(player.get("collected_data") or {}).get("dps",{}).get("mean")}

def put_once(path,data):
    raw=data.encode("utf8") if isinstance(data,str) else data
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        need(path.read_bytes()==raw,"EXISTING_INPUT_BYTES_DRIFT:"+path.name)
    else:
        path.write_bytes(raw)

def run(binary,out,*,revision,iterations=1,timeout_seconds=180,
        max_new=2,retry_failed=False):
    binary=pathlib.Path(binary).resolve()
    out=pathlib.Path(out).resolve()
    need(binary.is_file(),"SIMC_BINARY_NOT_FOUND")
    need(type(revision) is str and len(revision)>=7,"SIMC_REVISION_REQUIRED")
    need(type(timeout_seconds) is int and 1<=timeout_seconds<=900,
         "TIMEOUT_INVALID")
    need(type(max_new) is int and 0<=max_new<=2,"MAX_NEW_OUT_OF_RANGE")
    binary_sha=digest(binary.read_bytes())
    new_calls=0
    cases=[]
    for key in ACTORS:
        folder=out/key.replace("/","__")
        stage=folder/"stage"
        stage.mkdir(parents=True,exist_ok=True)
        user=user_for(key)
        put_once(folder/"user.json",canonical(user))
        # This is plan-only, with a non-executable seal on v096.
        prepared=bootstrap.build(user,stage,binary,revision,pure_stage=True)
        need(prepared["status"]=="STAGED_INTERNAL_MANIFEST_NATIVE_NOT_AUTHORIZED",
             "PURE_STAGE_NOT_SEALED")
        json2_path=folder/"physical.json"
        input_path=folder/"physical.simc"
        receipt_path=folder/"receipt.json"
        text=physical_input((stage/"profile.simc").read_text(encoding="utf8"),
                            json2_path,iterations)
        identity={"binary_sha256":binary_sha,"simc_revision":revision,
                  "input_sha256":digest(text.encode("utf8")),
                  "iterations":iterations,"scenario_spec":key,
                  "source_free_composer":True,"gear_rating_override_removed":True}
        prior=json.loads(receipt_path.read_text(encoding="utf8")) if receipt_path.is_file() else None
        if prior is not None:
            need(prior.get("identity")==identity,"PREVIOUS_NATIVE_IDENTITY_DRIFT:"+key)
            need(input_path.read_bytes()==text.encode("utf8"),
                 "PREVIOUS_PHYSICAL_INPUT_DRIFT:"+key)
            if prior.get("status")=="PASS_PHYSICAL_SIMC":
                need(json2_path.is_file() and
                     digest(json2_path.read_bytes())==prior.get("json2_sha256"),
                     "CACHED_JSON2_DRIFT:"+key)
                json2_summary(json2_path.read_bytes())
                cases.append({"spec":key,"status":"CACHED_VERIFIED_PHYSICAL_SIMC"})
                continue
            if not retry_failed:
                cases.append({"spec":key,"status":"PRIOR_FAILURE_RETAINED"})
                continue
        else:
            need(not input_path.exists() and not json2_path.exists(),
                 "PREEXISTING_UNRECEIPTED_NATIVE_FILES:"+key)
        if new_calls>=max_new:
            # Dry-run/call-cap must not create an unreceipted physical input:
            # a later actual smoke needs to be able to start immediately.
            cases.append({"spec":key,"status":"NOT_RUN_NEW_CALL_LIMIT"})
            continue
        if prior is None:
            put_once(input_path,text)
        if prior is not None and json2_path.exists():
            # Explicit retry is the only permitted replacement of a failed JSON2.
            json2_path.unlink()
        new_calls+=1
        status="FAIL_NATIVE_NOT_RETURNED"
        err=None
        summary=None
        try:
            result=subprocess.run([str(binary),str(input_path.resolve())],
                cwd=str(folder),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                timeout=timeout_seconds,check=False)
            (folder/"simc.log").write_text(
                result.stdout.decode("utf8",errors="replace")[-100000:],
                encoding="utf8")
            if result.returncode!=0:
                status="FAIL_NATIVE_EXIT"
                err="returncode="+str(result.returncode)
            elif not json2_path.is_file():
                status="FAIL_NATIVE_MISSING_JSON2"
                err="SimC did not write physical.json"
            else:
                summary=json2_summary(json2_path.read_bytes())
                status="PASS_PHYSICAL_SIMC"
        except subprocess.TimeoutExpired as e:
            status="FAIL_NATIVE_TIMEOUT"
            err="timeout_seconds="+str(timeout_seconds)
            (folder/"simc.log").write_text(
                "timeout; captured output="+str(e.stdout)[:2000],encoding="utf8")
        except (OSError,ValueError,KeyError,json.JSONDecodeError) as e:
            status="FAIL_NATIVE_JSON2_OR_EXEC"
            err=type(e).__name__+":"+str(e)
        receipt={"schema":SCHEMA,"identity":identity,"status":status,
                 "spec":key,"new_native_calls":1,"error":err,
                 "physical_profile_only":True,"chmv_optimization_completed":False,
                 "four_tier_effect_certified":False,
                 "global_optimum_proven":False}
        if status=="PASS_PHYSICAL_SIMC":
            receipt["json2_sha256"]=digest(json2_path.read_bytes())
            receipt["observed_json2"]=summary
        receipt_path.write_text(canonical(receipt),encoding="utf8")
        cases.append({"spec":key,"status":status,"error":err})
    result={"schema":SCHEMA,"binary_sha256":binary_sha,
            "new_native_calls":new_calls,"cases":cases,
            "all_pass":all(x["status"] in ("PASS_PHYSICAL_SIMC",
                    "CACHED_VERIFIED_PHYSICAL_SIMC") for x in cases),
            "user_optimizer_ready":False}
    out.mkdir(parents=True,exist_ok=True)
    (out/"SUMMARY.json").write_text(canonical(result),encoding="utf8")
    return result

def main(argv=None):
    p=argparse.ArgumentParser(description="Max two bounded source-independent physical SimC smokes")
    p.add_argument("--simc",required=True,type=pathlib.Path)
    p.add_argument("--revision",required=True)
    p.add_argument("--out",type=pathlib.Path,default=DEFAULT_OUT)
    p.add_argument("--iterations",type=int,default=1)
    p.add_argument("--timeout-seconds",type=int,default=180)
    p.add_argument("--max-new",type=int,default=2)
    p.add_argument("--retry-failed",action="store_true")
    a=p.parse_args(argv)
    try:
        result=run(a.simc,a.out,revision=a.revision,
                   iterations=a.iterations,
                   timeout_seconds=a.timeout_seconds,max_new=a.max_new,
                   retry_failed=a.retry_failed)
        print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True))
        print("OUTPUT_DIR:",str(a.out.resolve()))
        if os.name=="nt":
            try:
                os.startfile(str(a.out.resolve()))
            except OSError:
                pass
        return 0 if result["all_pass"] else 3
    except Exception as e:
        print("V140_BLOCKED:",type(e).__name__,str(e),file=sys.stderr)
        return 3

if __name__=="__main__":
    sys.exit(main())
