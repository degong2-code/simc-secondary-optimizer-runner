#!/usr/bin/env python3
"""v049: recover the exact 32 class-incompatible v047 items at 14 levels.

Bare one-item SimC Native lookup, 1 iteration, no DPS comparison, no item
optimization, and no race/class-specific derived stat inference.
Items without valid JSON2 static gear remain blocked.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,subprocess,sys
import v046_static_item_cache as cache
import v047_full_scope_collector as base

BIN_SHA=base.BASELINE_SHA
LEVELS=[292,295,298,302,305,308,311,315,318,321,324,328,331,334]
MAX_CASES=160
CLASSES={"Plate":("warrior","arms"),"Leather":("druid","balance"),"Mail":("hunter","marksmanship")}
BAD_IDS={
 251138,251152,251159,268207,268216,268219,268220,268222,268223,
 268224,268225,268227,268229,268230,268231,268234,268235,268237,
 268239,268240,268245,268246,268258,268259,268261,271875,271876,
 271878,273775,281236,281238,281239
} # 31 armor + one bow; two trinkets 250224/250244 excluded

def need(ok,name):
    if not ok:raise cache.CacheBlocked(name)

def classify(x):
    armor=x.get("armor_type")
    slot=x["slot"]
    if slot.endswith("_PLATE"):armor="Plate"
    if slot.endswith("_LEATHER"):armor="Leather"
    if slot.endswith("_MAIL"):armor="Mail"
    if x["item_id"]==268207:
        return ("hunter","marksmanship","main_hand")
    need(armor in CLASSES,"CLASS_NOT_VALIDATED:"+str(x["item_id"]))
    player,spec=CLASSES[armor]
    return player,spec,base.SLOT[slot]

def expected_cases(manifest):
    selected=[x for x in manifest["items"] if x["item_id"] in BAD_IDS]
    need(len(selected)==32 and set(x["item_id"] for x in selected)==BAD_IDS,
         "EXACT_FAILED_ITEM_SET_CHANGED")
    return [(it,lev) for it in selected for lev in LEVELS]

def profile(item,ilevel,result):
    player,spec,slot=classify(item)
    parts=[player+'="V049StaticProbe"', 'spec='+spec,'level=90','race=dwarf',
       'role=attack', f"{slot}=v049_probe_{item['item_id']},id={item['item_id']},ilevel={ilevel},source=local",
       'item_db_source=local','fight_style=Patchwerk','iterations=1','threads=1',
       'fixed_time=1','max_time=2','vary_combat_length=0',
       'optimal_raid=0','calculate_scale_factors=0',
       'actions=wait,sec=1','json2='+str(result.resolve())]
    return "\n".join(parts)+"\n"

def run(binary,manifest_path,seed,out,start,max_cases):
    out.mkdir(parents=True,exist_ok=True)
    report={"schema":"v049_recovered_class_native_static_v1",
       "status":"SETUP_BLOCKED","start":start,"max_cases":max_cases,
       "native_attempts":0,"saved":0,"blocked":0,"items":[],
       "possible_pairs":448,"trinkets_in_this_batch":0,
       "product_code_integrated":False,"official_policy_promoted":False}
    try:
        manifest=base.parse_manifest(manifest_path)
        full=expected_cases(manifest)
        need(type(max_cases) is int and 1<=max_cases<=MAX_CASES,"CALLS_OUT_OF_BOUND")
        need(type(start) is int and start>=0 and start<=len(full),"BAD_START")
        pairs=full[start:start+max_cases]
        need(binary.is_file() and hashlib.sha256(binary.read_bytes()).hexdigest()==BIN_SHA,
             "BINARY_IDENTITY_DRIFT")
        c=cache.load(seed)
        for i,(item,ilevel) in enumerate(pairs):
            record={"index":start+i,"item_id":item["item_id"],
                    "requested_level":ilevel,"slot":item["slot"],"status":"BLOCKED"}
            report["items"].append(record)
            try:
                _,_,slot=classify(item)
                identity={"season":cache.SEASON,"item_id":item["item_id"],
                     "ilevel":ilevel,"slot":cache.normalize_slot(slot),"options":{}}
                key=cache.digest(identity)
                if key in c["variants"]:
                    record["status"]="CACHED_EXACT_VARIANT";continue
                inp=out/"probe.simc";result=out/"probe.json"
                inp.write_text(profile(item,ilevel,result),encoding="utf8")
                result.unlink(missing_ok=True)
                report["native_attempts"]+=1
                p=subprocess.run([str(binary),str(inp)],cwd=binary.parent,
                   stdin=subprocess.DEVNULL,capture_output=True,timeout=35)
                record["exit_code"]=p.returncode
                if p.returncode!=0 or not result.is_file():
                    record["error_type"]="NATIVE_FAILURE"
                    record["stderr_excerpt"]=p.stderr.decode("utf8","replace")[:500]
                    raise cache.CacheBlocked("NATIVE_FAILURE")
                blob=result.read_bytes()
                records=cache.native_records(blob,artifact_id="V049_NATIVE_1_ITERATION")
                matches=[r for r in records if r["observed_slot"]==slot and
                    r["identity"]["item_id"]==item["item_id"] and
                    r["identity"]["ilevel"]==ilevel]
                need(len(matches)==1,"NATIVE_ITEM_NOT_IN_CORRECT_SLOT")
                row=matches[0]
                need(row["identity"]["options"]=={},"UNEXPECTED_OPTION")
                cache.merge_native(c,[row])
                record["status"]="NATIVE_STATIC_SAVED"
                record["secondary"]=row["static"]["secondary"]
                record["native_json_sha256"]=cache.digest(blob)
                record["game_reachability_verified"]=False
                report["saved"]+=1
            except Exception as exc:
                report["blocked"]+=1
                record["error"]=type(exc).__name__+":"+str(exc)
            finally:
                cache.write_atomic(out/"midnight_s2_static_cache_v049.json",c)
                (out/"V049_LEDGER.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
                (out/"probe.simc").unlink(missing_ok=True)
                (out/"probe.json").unlink(missing_ok=True)
        report["status"]="BATCH_PARTIAL" if report["blocked"] else "BATCH_COMPLETE"
    except Exception as exc:
        report["setup_error"]=type(exc).__name__+":"+str(exc)
    (out/"V049_LEDGER.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("V049",report["status"],"calls",report["native_attempts"],
          "saved",report["saved"],"blocked",report["blocked"])
    return 0 if report["status"]!="SETUP_BLOCKED" else 3

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    for name in ("binary","manifest","seed","out"):ap.add_argument("--"+name,required=True,type=pathlib.Path)
    ap.add_argument("--start",type=int,default=0)
    ap.add_argument("--max-cases",type=int,default=10)
    a=ap.parse_args()
    sys.exit(run(a.binary.resolve(),a.manifest.resolve(),a.seed.resolve(),a.out.resolve(),a.start,a.max_cases))
