#!/usr/bin/env python3
"""v068 controlled 2× real SimC probe, no DPS optimizer yet.

The exact user-selected Rogue 334 SimC profile is composed from a pinned
upstream APL and only OUR source fields; output JSON2 and stderr are preserved.
Native is sole authority on item/embellishment/Omnium/APL effects. Non-trinket
static G/L only when Native records demonstrate exact variants.
"""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib,subprocess,sys,time
import v046_static_item_cache as static
import v063_numeric_injection as numeric
import v068_rogue_user_profile as profile

BIN_SHA="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"
SCHEMA="v068_user_rogue_two_native_probe_v1"
class ProbeBlocked(ValueError):pass
def need(ok,msg):
    if not ok:raise ProbeBlocked(msg)
def write(path,obj):
    path=pathlib.Path(path)
    tmp=path.with_suffix(path.suffix+".tmp")
    with tmp.open("w",encoding="utf8") as f:
        json.dump(obj,f,sort_keys=True,ensure_ascii=False,indent=2)
        f.write("\n");f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)
def execute(binary,out,reference=None,iterations=35,cache_only=False):
    binary=pathlib.Path(binary);out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
    ref=(pathlib.Path(reference) if reference else profile.REFERENCE)
    receipt={"schema":SCHEMA,"status":"BLOCKED","native_calls_attempted":0,
             "native_max":2,"user_scenario":"void_elf_rogue_subtlety_334",
             "selected_gear_effects_owned_by":"SimC",
             "official_T":None,"special_static_L":None,"native_cases":[],
             "cross_spec_acceptance":False,"global_optimum_proven":False,
             "original_v015_v016_not_modified":True}
    progress=out/"V068_PROBE_RECEIPT.json"
    try:
        need(binary.is_file() and hashlib.sha256(binary.read_bytes()).hexdigest()==BIN_SHA,
             "EXACT_PINNED_SIMC_BINARY_MISMATCH")
        source=ref.read_text(encoding="utf8")
        # Original Git blob is checked in workflow; a pinned reference is
        # mandatory to avoid undetected APL changes.
        need(len(source)>5000 and "rogue=" in source,
             "UPSTREAM_ROGUE_PROFILE_NOT_FOUND")
        evidence=[]
        for i,choice in enumerate(("A","B")):
            case=out/("case_%02d"%i);case.mkdir(exist_ok=True)
            inputfile=case/"input.simc";nativefile=case/"result.json"
            text,meta=profile.assemble(source,nativefile,iterations,choice)
            if inputfile.exists():
                need(hashlib.sha256(inputfile.read_bytes()).hexdigest()==meta["input_sha256"],
                     "EXISTING_CASE_INPUT_CHANGED")
            else:
                inputfile.write_text(text,encoding="utf8")
            entry={"candidate":choice,"input_sha256":meta["input_sha256"],
                   "target_is_ONLY_raw_probe_not_official_T":True,
                   "status":"PENDING"}
            if nativefile.exists():
                need((case/"stdout.txt").is_file() and
                     (case/"stderr.txt").is_file(),
                     "PARTIAL_NATIVE_RECEIPT_NOT_A_CACHE")
                entry["source"]="EXISTING_NATIVE_BYTES_UNTAMPERED_UNATTESTED"
            else:
                need(not cache_only,"CACHE_ONLY_NO_NATIVE_RESULT")
                need(receipt["native_calls_attempted"]<2,"NATIVE_TWO_CALL_CAP")
                receipt["native_calls_attempted"]+=1
                entry["source"]="NEW_NATIVE"
                write(progress,receipt)
                start=time.monotonic()
                p=subprocess.run([str(binary.resolve()),str(inputfile.resolve())],
                   cwd=binary.resolve().parent,stdin=subprocess.DEVNULL,
                   stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=210)
                (case/"stdout.txt").write_bytes(p.stdout)
                (case/"stderr.txt").write_bytes(p.stderr)
                entry["wall_seconds"]=round(time.monotonic()-start,3)
                entry["returncode"]=p.returncode
                if p.returncode!=0:
                    entry["status"]="SIMC_NATIVE_EXIT_FAIL_SEE_RAW_STDERR"
                    receipt["native_cases"].append(entry)
                    raise ProbeBlocked("SIMC_NATIVE_EXIT_"+str(p.returncode))
            need(nativefile.is_file() and nativefile.stat().st_size>0,
                 "JSON2_NOT_WRITTEN")
            native_raw=nativefile.read_bytes()
            native_doc=json.loads(native_raw)
            need(native_doc.get("report_version")=="2.0.0","JSON2_REPORT_VERSION_NOT_2")
            need(native_doc.get("git_revision") is not None,"JSON2_REVISION_MISSING")
            player=(native_doc.get("sim") or {}).get("players") or []
            need(len(player)==1,"JSON2_SINGLE_PLAYER_REQUIRED")
            stats=numeric.read_rating(player[0])
            mean=((player[0].get("collected_data") or {}).get("dps") or {})
            need(type(mean.get("mean")) in (float,int) and
                 type(mean.get("mean_std_dev")) in (float,int) and
                 type(mean.get("count")) is int and mean["count"]>=20,
                 "JSON2_DPS_SEM_NOT_AVAILABLE")
            entry.update({"status":"PASS_NATIVE_JSON2_INPUT",
                "json2_sha256":hashlib.sha256(native_raw).hexdigest(),
                "native_revision":native_doc["git_revision"],
                "actual_buffed_stats_rating":stats,
                "dps_mean":mean["mean"],
                "dps_sem":mean["mean_std_dev"],
                "samples":mean["count"]})
            # Native static table records are collected only as a source
            # of G/L and only after JSON2 exists. Missing trinket gear rows
            # are not treated as failed selection or interpreted as zero.
            records=static.native_records(native_raw,
                         artifact_id="V068_USER_ROGUE_REAL_NATIVE_INPUT")
            entry["native_static_rows_observed"]=len(records)
            evidence.append({"input":text,"native":native_doc})
            receipt["native_cases"].append(entry)
            write(progress,receipt)
        # Numeric offset must agree for the exact same profile; if it
        # does not, report calibration blocked without rejecting SimC effects.
        calibrated=numeric.calibrate(evidence)
        receipt["numeric_calibration"]={
            "status":calibrated["status"],
            "profile_sha256":calibrated["stable_profile_sha256"],
            "offset":calibrated["net_input_to_json2_rating_offset"],
            "native_revision":calibrated["native_revision"]}
        receipt["status"]="PASS_TWO_REAL_ROGUE_NATIVE_JSON2_NUMERIC_WITNESSES"
    except Exception as e:
        receipt["error"]=type(e).__name__+":"+str(e)
        receipt["status"]="BLOCKED_OR_PARTIAL"
    write(progress,receipt)
    print("V068",receipt["status"],"Native calls",receipt["native_calls_attempted"])
    return 0 if receipt["status"].startswith("PASS") else 3
def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--binary",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    p.add_argument("--reference",type=pathlib.Path)
    p.add_argument("--iterations",type=int,default=35)
    p.add_argument("--cache-only",action="store_true")
    a=p.parse_args(argv)
    return execute(a.binary,a.out,a.reference,a.iterations,a.cache_only)
if __name__=="__main__":
    sys.exit(main())
