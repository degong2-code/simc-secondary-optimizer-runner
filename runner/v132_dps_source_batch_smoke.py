#!/usr/bin/env python3
"""v132: ONE bounded raw-SimC smoke per NEW source-backed MID2 DPS spec.

This is a source-profile acceptance smoke, NOT a target-ilvl representative
CHMV optimization, gear recommendation or proc model. Seven earlier profile
specializations are not redundantly rerun. Missing three MID2 sources are
reported honestly. Source, SimC binary, iterations and combat are cache identity.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
FIXTURES=ROOT/"integration_probes"/"fixtures"
SCHEMA="v132_official_mid2_dps_source_smoke_v1"
UPSTREAM_COMMIT="426ad85ecb1c5d9a1af166931478dabf29b42fdd"
NEW={
 "deathknight/frost":("Death_Knight_Frost","1d300486e23eeab2628915eb9bb99a79425529a6"),
 "deathknight/unholy":("Death_Knight_Unholy","3a94484f15b5fb8b454c05dbdfd78b799979560e"),
 "demonhunter/devourer":("Demon_Hunter_Devourer","2392cdeb7da267d1f46b96b12fac31b12cf229bc"),
 "demonhunter/havoc":("Demon_Hunter_Havoc","9cab6566a655df9cf1d73bb92e7173ed1e708a25"),
 "druid/feral":("Druid_Feral","29c4bd2329114bbdcbf36f4bc330d52e39349e72"),
 "hunter/marksmanship":("Hunter_Marksmanship","87582489548939934be9bb2c5e74709ea74363b3"),
 "hunter/survival":("Hunter_Survival","506e65416789716d5139a2217549b765f07e78e4"),
 "mage/arcane":("Mage_Arcane","8d06eda4f69374dd1ed2e2d1eb8076b82cbbaf7f"),
 "mage/fire":("Mage_Fire","9fae08d2f1c49f3a964f9415540929723384e6fe"),
 "monk/windwalker":("Monk_Windwalker","235bf8bbce49bada7cad1d5660c044581a3f60d3"),
 "priest/shadow":("Priest_Shadow","b613a34fa10e42cd454e08c253a5742acf79f41a"),
 "rogue/assassination":("Rogue_Assassination","795a7bb03d8806d9d41f04c5e9b3b97a244b6f34"),
 "shaman/enhancement":("Shaman_Enhancement","2f2c951ae07489d124db36c464ab66d1efd262ce"),
 "warlock/affliction":("Warlock_Affliction","20f77c7900923ceebbaf698888dd04d6b185ca44"),
 "warlock/demonology":("Warlock_Demonology","6649192a2b983ed8b0637d27f0903bf5c78c556b"),
 "warlock/destruction":("Warlock_Destruction","541a593f18b7f1200516282f300dad0691d3814d"),
 "warrior/arms":("Warrior_Arms","2b7f8b1a3297b1447f80d9f05272c7f45337f809"),
}
ALREADY_SOURCE_CONNECTED=("warrior/fury","paladin/retribution","mage/frost",
 "hunter/beast_mastery","rogue/subtlety","shaman/elemental","rogue/outlaw")
MISSING_MID2=("druid/balance","evoker/devastation","evoker/augmentation")
# Current official SimulationCraft midnight branch evidence, reviewed
# 2026-10-28. These are upstream *readiness facts*, not copied profiles.
# Balance/Devastation have active CI default actors but their seasonal MID2
# profile entries remain commented and only ilvl289 generator drafts exist.
# Augmentation remains commented in CI and has no MID2 generator profile.
UPSTREAM_MISSING_EVIDENCE={
 "simulationcraft_ci_blob":"5abef61dacb12f079617fcf1865bea32a35d2b01",
 "mid2_raid_blob":"a02b49a05c484948ce632b3fd2ee27a6f200078a",
 "druid_generator_blob":"99fec56a6c139f0e5cdeedc14a3e677ead965add",
 "evoker_generator_blob":"70dac232a9b7d65a5ca17438471c9ffbcee8645f"}
MISSING_SOURCE_READINESS={
 "druid/balance":{
   "ci_default_actor":True,"mid2_profile_enabled":False,
   "generator_draft_present":True,"generator_draft_ilevel":289,
   "reason":"NO_CURRENT_ENABLED_MID2_SOURCE_PROFILE"},
 "evoker/devastation":{
   "ci_default_actor":True,"mid2_profile_enabled":False,
   "generator_draft_present":True,"generator_draft_ilevel":289,
   "reason":"NO_CURRENT_ENABLED_MID2_SOURCE_PROFILE"},
 "evoker/augmentation":{
   "ci_default_actor":False,"mid2_profile_enabled":False,
   "generator_draft_present":False,"generator_draft_ilevel":None,
   "reason":"NO_CURRENT_SIMC_SOURCE_PROFILE"}}
SLOTS=("head","neck","shoulders","back","chest","wrists","hands","waist",
       "legs","feet","finger1","finger2","trinket1","trinket2","main_hand","off_hand")
RUNTIME=("iterations","json2","threads")
class SmokeBlocked(ValueError):pass
def need(ok,why):
    if not ok:raise SmokeBlocked(why)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def atomic_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".part")
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
                   encoding="utf8")
    tmp.replace(path)
def validate_source(key):
    name,sha=NEW[key]
    file=FIXTURES/("v132_MID2_"+name+".simc")
    raw=file.read_bytes()
    need(git_blob(raw)==sha,"PINNED_GIT_BLOB_CHANGED:"+key)
    source=raw.decode("utf8")
    settings={}
    slots={}
    actions=0
    primary=0
    for line in source.splitlines():
        if line.startswith("# Gear Summary"):break
        k,sep,value=line.partition("=")
        if not sep or line.startswith("#"):continue
        if k=="actions":primary+=1
        if k.startswith("actions"):actions+=1
        if k in SLOTS:
            need(k not in slots,"DUPLICATE_GEAR:"+key+":"+k)
            matches=re.findall(r"(?:^|,)id=([1-9][0-9]*)(?:,|$)",value)
            need(len(matches)==1,"INVALID_GEAR_ID:"+key+":"+k)
            slots[k]=int(matches[0])
        if k in ("spec","race","role","talents","omnium_talents"):
            need(k not in settings,"DUPLICATE_SETTING:"+key+":"+k)
            settings[k]=value
    cl,sp=key.split("/")
    need(source.count(cl+'="')==1 and settings.get("spec")==sp,
         "SOURCE_CLASS_SPEC_MISMATCH:"+key)
    need(settings.get("race") and settings.get("role") and settings.get("talents"),
         "SOURCE_CHARACTER_INCOMPLETE:"+key)
    need(primary==1 and actions>=10,"APL_ABSENT:"+key)
    need(set(slots)==set(SLOTS)-({"off_hand"} if "off_hand" not in slots else set()),
         "SOURCE_GEAR_SLOTS_INCOMPLETE:"+key)
    need("main_hand" in slots and all(x in slots for x in ("trinket1","trinket2")),
         "SOURCE_WEAPON_OR_TRINKET_ABSENT:"+key)
    return {"key":key,"path":str(file.relative_to(ROOT)),
            "git_blob":sha,"sha256":digest(raw),"source":source,
            "slot_count":len(slots),"apl_lines":actions,
            "race":settings["race"],"role":settings["role"],
            "has_omnium":"omnium_talents" in settings,
            "weapon_slots":[s for s in ("main_hand","off_hand") if s in slots]}
def scan():
    found=[validate_source(key) for key in NEW]
    return {"schema":SCHEMA,"status":"PASS_OFFLINE_SOURCE_INSPECTION",
            "upstream_commit":UPSTREAM_COMMIT,
            "new_source_count":len(found),"already_source_connected":list(ALREADY_SOURCE_CONNECTED),
            "missing_mid2":list(MISSING_MID2),
            "missing_source_readiness":MISSING_SOURCE_READINESS,
            "upstream_missing_evidence":UPSTREAM_MISSING_EVIDENCE,
            "new_sources":[{k:v for k,v in item.items() if k!="source"} for item in found],
            "native_calls":0,"all_27_executable":False,
            "source_readiness_not_target_profile_readiness":True}
def smoke_input(source,json2,iterations):
    need(1<=iterations<=200,"SMOKE_ITERATIONS_OUTSIDE_BOUNDS")
    lines=[]
    for line in source.splitlines():
        if line.partition("=")[0] not in RUNTIME:
            lines.append(line)
    lines+=["iterations="+str(iterations),"threads=1","json2="+str(json2.resolve())]
    return "\n".join(lines).rstrip()+"\n"
def check_native_result(raw):
    obj=json.loads(raw.decode("utf8"))
    sim=obj.get("sim")
    need(isinstance(sim,dict) and isinstance(sim.get("players"),list)
         and len(sim["players"])>0,"NATIVE_JSON2_NO_SIM_PLAYERS")
    return len(sim["players"])
def run(binary,out,iterations=35,timeout_seconds=180,max_new=17,retry_failed=False):
    need(binary.is_file(),"SIMC_BINARY_NOT_FOUND")
    need(0<=max_new<=len(NEW),"INVALID_MAX_NEW")
    need(1<=timeout_seconds<=900,"INVALID_SMOKE_TIMEOUT")
    checked=scan()
    binary_sha=digest(binary.read_bytes())
    cases=[]
    native=0
    for key in NEW:
        record=validate_source(key)
        root=out/key.replace("/","__")
        json2=root/"result.json"
        profile=root/"input.simc"
        receipt=root/"receipt.json"
        lines=smoke_input(record["source"],json2,iterations)
        input_sha=digest(lines.encode("utf8"))
        identity={"source_sha256":record["sha256"],"binary_sha256":binary_sha,
                  "iterations":iterations,"input_sha256":input_sha}
        root.mkdir(parents=True,exist_ok=True)
        current=json.loads(receipt.read_text("utf8")) if receipt.exists() else None
        if current is not None:
            need(current.get("identity")==identity,
                 "EXISTING_SMOKE_IDENTITY_DRIFT:"+key)
            need(profile.read_bytes()==lines.encode("utf8"),
                 "EXISTING_SMOKE_INPUT_DRIFT:"+key)
            if current["status"]=="PASS_NATIVE_SMOKE":
                need(json2.is_file() and digest(json2.read_bytes())==
                     current["json2_sha256"],"EXISTING_NATIVE_RESULT_DRIFT:"+key)
                check_native_result(json2.read_bytes())
                cases.append({"key":key,"status":"CACHED_VERIFIED_NATIVE"})
                continue
            if not retry_failed:
                cases.append({"key":key,"status":"PRIOR_FAILED_NOT_RETRIED"})
                continue
        elif profile.exists() or json2.exists():
            raise SmokeBlocked("PREEXISTING_UNRECEIPTED_NATIVE_FILES:"+key)
        if native>=max_new:
            cases.append({"key":key,"status":"NOT_RUN_LIMIT"})
            continue
        if current is not None and json2.exists():
            # A failed attempt may have emitted an incomplete JSON2 file.
            # Only explicit --retry-failed permits discarding it.
            json2.unlink()
        if current is None:
            profile.write_text(lines,encoding="utf8",newline="\n")
        native+=1
        try:
            cmd=subprocess.run([str(binary.resolve()),str(profile.resolve())],
                               cwd=str(root),stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,timeout=timeout_seconds,
                               check=False)
            log=cmd.stdout.decode("utf8",errors="replace")
            (root/"simc.log").write_text(log[-100000:],encoding="utf8")
            if cmd.returncode!=0:
                status="FAIL_NATIVE_EXIT";error="returncode="+str(cmd.returncode)
            elif not json2.is_file():
                status="FAIL_NATIVE_MISSING_JSON2";error="No result.json emitted"
            else:
                players=check_native_result(json2.read_bytes())
                status="PASS_NATIVE_SMOKE";error=None
        except subprocess.TimeoutExpired:
            status="FAIL_NATIVE_TIMEOUT";error="timeout_seconds="+str(timeout_seconds)
        except (OSError,ValueError,KeyError,json.JSONDecodeError) as e:
            status="FAIL_NATIVE_JSON2_OR_INPUT";error=type(e).__name__+":"+str(e)
        receipt_doc={"schema":SCHEMA,"key":key,"identity":identity,
                     "status":status,"new_native_calls":1,"error":error}
        if status=="PASS_NATIVE_SMOKE":
            receipt_doc["json2_sha256"]=digest(json2.read_bytes())
            receipt_doc["sim_player_count"]=players
        atomic_json(receipt,receipt_doc)
        cases.append({"key":key,"status":status,"error":error})
        print(key,status,flush=True)
    summary={k:v for k,v in checked.items() if k not in ("new_sources",)}
    summary.update({"status":"PASS_ALL_ATTEMPTED" if all(
                  x["status"] in ("CACHED_VERIFIED_NATIVE","PASS_NATIVE_SMOKE","NOT_RUN_LIMIT")
                  for x in cases) else "INCOMPLETE_OR_FAILED",
                  "native_calls_this_run":native,"binary_sha256":binary_sha,
                  "cases":cases,"source_readiness_not_target_profile_readiness":True})
    atomic_json(out/"V132_BATCH_SMOKE_SUMMARY.json",summary)
    return summary
def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--audit",action="store_true",help="Only 17 SHA/slot/APL scans; Native 0")
    p.add_argument("--simc",type=pathlib.Path,help="Local real SimC executable for Native 1/spec")
    p.add_argument("--out",type=pathlib.Path,
                   default=pathlib.Path.home()/"SIMC_Secondary_Optimizer"/"batch_smoke_v132")
    p.add_argument("--iterations",type=int,default=35)
    p.add_argument("--timeout-seconds",type=int,default=180)
    p.add_argument("--max-new",type=int,default=17)
    p.add_argument("--retry-failed",action="store_true")
    a=p.parse_args(argv)
    try:
        if a.audit:
            result=scan()
            atomic_json(a.out/"V132_SOURCE_AUDIT.json",result)
            print(result["status"],"new",result["new_source_count"],"Native 0")
            ret=0
        else:
            need(a.simc is not None,"SIMC_BINARY_REQUIRED_FOR_NATIVE")
            result=run(a.simc,a.out,a.iterations,a.timeout_seconds,
                       a.max_new,a.retry_failed)
            ret=0 if result["status"]=="PASS_ALL_ATTEMPTED" else 3
    except Exception as e:
        print("V132_BLOCKED",type(e).__name__,str(e),file=sys.stderr)
        ret=3
    print("RESULT_DIR:",a.out.resolve(),flush=True)
    if os.name=="nt" and a.out.exists():
        try:os.startfile(str(a.out.resolve()))
        except OSError:pass
    return ret
if __name__=="__main__":
    sys.exit(main())
