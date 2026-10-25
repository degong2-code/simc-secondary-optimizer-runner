#!/usr/bin/env python3
"""v047 full-scope *bounded* Native static collector.

This is NOT a combat DPS optimization, item optimizer, reachability validator,
or a WEQUIP runtime dependency. SimC Native JSON2 supplies static stats.
Partial/unsupported variants get a durable ledger instead of fabricated values.
Resume is append-only and does not replace previously verified static entries.
"""
from __future__ import annotations

import argparse,hashlib,json,pathlib,re,subprocess,sys,time
from datetime import datetime,timezone

import pilot
import v046_static_item_cache as cache

SLOT={
    "HEAD":"head","SHOULDER":"shoulders","CHEST":"chest","ROBE":"chest",
    "HAND":"hands","WRIST":"wrists","WAIST":"waist","LEGS":"legs","FEET":"feet",
    "CLOAK":"back","NECK":"neck","FINGER":"finger1","TRINKET":"trinket1",
    "WEAPON":"main_hand","TWOHWEAPON":"main_hand","WEAPONMAINHAND":"main_hand",
    "ONE_HAND_SWORD":"main_hand","TWO_HAND_SWORD":"main_hand",
    "LEGS_CLOTH":"legs","CHEST_LEATHER":"chest","HANDS_MAIL":"hands",
    "HEAD_PLATE":"head"
}
UNSUPPORTED_SLOTS={"HOLDABLE","SHIELD","RANGEDRIGHT","RANGED"}
BASELINE_SHA="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"
MAX_CASES_PER_RUN=200
MAX_SECONDS_PER_NATIVE=35
MIN_ITERATIONS=1
STATS=cache.STATS

def need(ok,code):
    if not ok: raise cache.CacheBlocked(code)

def parse_manifest(p):
    manifest=json.loads(p.read_text(encoding="utf8"))
    need(manifest.get("schema")=="v047_bounded_collection_scope_v1","MANIFEST_SCHEMA")
    need(manifest.get("season")==cache.SEASON,"MANIFEST_SEASON")
    need(manifest.get("selected_unique_count")==126,"MANIFEST_SCOPE_CHANGED")
    items=manifest["items"]
    need(type(items) is list and len(items)==126 and
         len({x["item_id"] for x in items})==126,"ITEM_LIST_CHANGED")
    levels=manifest.get("target_level_candidates")
    need(levels==[292,295,298,302,305,308,311,315,318,321,324,328,331,334],
         "UNAPPROVED_LEVEL_CANDIDATES")
    for x in items:
        need(type(x["item_id"]) is int and x["item_id"]>0 and
             type(x["name"]) is str and len(x["name"])>1 and
             x["slot"] in SLOT or x["slot"] in UNSUPPORTED_SLOTS,
             "ITEM_INVALID_OR_UNKNOWN_SLOT")
    return manifest

def candidates(manifest,levels=None,start=0,max_cases=MAX_CASES_PER_RUN):
    levels=levels or manifest["target_level_candidates"]
    need(all(x in manifest["target_level_candidates"] for x in levels),"LEVEL_NOT_IN_SCOPE")
    need(type(start) is int and start>=0,"CURSOR_INVALID")
    need(type(max_cases) is int and 1<=max_cases<=MAX_CASES_PER_RUN,"BOUNDED_CALLS_REQUIRED")
    full=[(it,level) for it in manifest["items"] for level in levels]
    need(start<=len(full),"CURSOR_OUTSIDE_SCOPE")
    return full[start:start+max_cases],len(full)

def make_native_profile(reference,item,level,path):
    need(item["slot"] in SLOT,"SLOT_HAS_NO_VALIDATED_SIMC_MAPPING:"+item["slot"])
    slot=SLOT[item["slot"]]
    ident=item["item_id"]
    # Bare static by default, except explicitly known crafted stats that must
    # be provided for a meaningful baseline. These are variant-specific, not
    # free/lock eligibility decisions.
    extra=",crafted_stats=49/36" if ident in (239648,239656) else ""
    line=f"{slot}=v047_stat_probe_{ident},id={ident},ilevel={level},source=local{extra}"
    lines=[];seen=0;json2seen=0
    for old in reference.splitlines():
        if old.startswith(slot+"="):
            lines.append(line);seen+=1
        elif old.startswith("iterations="):
            lines.append("iterations=1")
        elif old.startswith("max_time="):
            lines.append("max_time=2")
        elif old.startswith("json2="):
            json2seen+=1
        elif old.startswith("gear_") and old.split("=",1)[0].endswith("_rating"):
            # No gear overrides: extract actual Native item stats while
            # keeping all other equipment and buffs unchanged.
            continue
        else:
            lines.append(old)
    need(seen==1 and json2seen==0,"BASELINE_PROFILE_NOT_SAFE")
    lines.append("json2="+str(path.resolve()))
    return "\n".join(lines)+"\n"

def audit_variant(payload,item,level):
    records=cache.native_records(payload,cache.SEASON,"V047_GEAR_QUERY")
    slot=SLOT[item["slot"]]
    matched=[x for x in records if x["observed_slot"]==slot]
    need(len(matched)==1,"NATIVE_SLOT_ABSENT")
    r=matched[0]
    need(r["identity"]["item_id"]==item["item_id"] and
         r["identity"]["ilevel"]==level,"NATIVE_ITEM_ID_OR_ILVL_DRIFT")
    if item["item_id"] in (239648,239656):
        need(r["identity"]["options"].get("crafted_stats")=="49/36",
             "CRAFTED_STAT_OPTION_MISSING")
    else:
        need(not any(k in r["identity"]["options"] for k in
          ("gem_id","enchant_id","enchant","crafted_stats","embellishment")),
          "PROBE_UNWANTED_MODIFIER")
    # Item stats (including zeros) are valid ONLY for a resolved Native ID.
    need(all(type(r["static"]["secondary"][k]) is int for k in STATS),
         "SECONDARY_STAT_SHAPE")
    return r

def run(binary,manifest_path,seed_path,out,start,levels,max_cases):
    out.mkdir(parents=True,exist_ok=True)
    ledger_path=out/"V047_LEDGER.json"
    result={
      "schema":"v047_native_static_full_collection_ledger_v1",
      "status":"STARTED","requested_max_native":max_cases,
      "attempted":0,"saved":0,"cache_reused":0,"blocked":0,
      "source":"NATIVE_LOCAL_DB_ONLY","new_game_acquisition_verified":False,
      "crafted_catalog_complete":False,"product_code_integrated":False,
      "official_policy_promoted":False,"results":[]}
    try:
        manifest=parse_manifest(manifest_path)
        full,possible=candidates(manifest,levels,start,max_cases)
        result["total_possible_for_requested_levels"]=possible
        result["start_cursor"]=start
        result["next_cursor"]=start+len(full)
        need(binary.is_file() and cache.digest(binary.read_bytes())==BASELINE_SHA,
             "BIN_SHA_CHANGED")
        existing=cache.load(seed_path)
        reference,_=pilot.source()
        result["seed_cache_sha256"]=cache.digest(seed_path.read_bytes())
        cache_path=out/"midnight_s2_static_cache_v047.json"
        for offset,(item,level) in enumerate(full):
            step={"index":start+offset,"item_id":item["item_id"],
                  "item_name":item["name"],"source_slot":item["slot"],
                  "requested_level":level,"status":"BLOCKED"}
            result["results"].append(step)
            try:
                slot=SLOT.get(item["slot"])
                need(bool(slot),"SLOT_UNSUPPORTED:"+item["slot"])
                extra={"crafted_stats":"49/36"} if item["item_id"] in (239648,239656) else {}
                identity={"season":cache.SEASON,"item_id":item["item_id"],
                          "ilevel":level,"slot":cache.normalize_slot(slot),
                          "options":extra}
                key=cache.digest(identity)
                if key in existing["variants"]:
                    step["status"]="CACHED_EXACT_VARIANT";result["cache_reused"]+=1
                    continue
                inp=out/"tmp_input.simc"
                native=out/"tmp_result.json"
                src=make_native_profile(reference,item,level,native)
                inp.write_text(src,encoding="utf8")
                if native.exists():native.unlink()
                result["attempted"]+=1
                p=subprocess.run([str(binary),str(inp)],cwd=binary.parent,
                    stdin=subprocess.DEVNULL,capture_output=True,timeout=MAX_SECONDS_PER_NATIVE)
                step["simc_exit"]=p.returncode
                step["native_stdout_digest"]=cache.digest(p.stdout)
                step["native_stderr_digest"]=cache.digest(p.stderr)
                need(p.returncode==0 and native.is_file(),
                     "SIMC_PROCESS_OR_JSON2_ERROR")
                raw=native.read_bytes()
                row=audit_variant(raw,item,level)
                cache.merge_native(existing,[row])
                step["status"]="NATIVE_STATIC_SAVED"
                step["native_json_digest"]=cache.digest(raw)
                step["native_static"]=row["static"]
                step["resolved_item_options"]=row["identity"]["options"]
                step["item_level_reachability_confirmed"]=False
                step["special_effect_native_supported"]=False
                result["saved"]+=1
            except Exception as exc:
                result["blocked"]+=1
                step["error"]=type(exc).__name__+":"+str(exc)
            finally:
                result["status"]="PARTIAL_IN_PROGRESS"
                cache.write_atomic(cache_path,existing)
                ledger_path.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
                for name in ("tmp_input.simc","tmp_result.json"):
                    (out/name).unlink(missing_ok=True)
        result["status"]="BATCH_COMPLETE_WITH_BLOCKERS" if result["blocked"] else "BATCH_COMPLETE"
    except Exception as exc:
        result["status"]="FAILED_SETUP"
        result["setup_error"]=type(exc).__name__+":"+str(exc)
    ledger_path.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("V047",result["status"],"attempted",result["attempted"],
          "saved",result["saved"],"reused",result["cache_reused"],
          "blocked",result["blocked"],flush=True)
    return 0 if result["status"]!="FAILED_SETUP" else 3

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--binary",type=pathlib.Path,required=True)
    parser.add_argument("--manifest",type=pathlib.Path,required=True)
    parser.add_argument("--seed-cache",type=pathlib.Path,required=True)
    parser.add_argument("--out",type=pathlib.Path,required=True)
    parser.add_argument("--start",type=int,default=0)
    parser.add_argument("--max-cases",type=int,default=6)
    parser.add_argument("--levels",type=int,nargs="+",default=[334])
    args=parser.parse_args()
    raise SystemExit(run(args.binary.resolve(),args.manifest.resolve(),
                         args.seed_cache.resolve(),args.out.resolve(),
                         args.start,args.levels,args.max_cases))
