#!/usr/bin/env python3
"""v052: bounded 13 one-iteration Native item-only 331 crafted lookup samples.

No combat DPS, no external item API, and no auto gear selection. The results
are per-variant *static stat* evidence; no claim that all ilvls are obtainable.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,subprocess,sys
import v046_static_item_cache as cache
import v051_crafted_embellishment_bridge as bridge

BIN_SHA="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"
CLASS={"cloth":("mage","arcane"),"leather":("druid","balance"),
       "mail":("hunter","marksmanship"),"plate":("warrior","arms")}
ITEM_CASES=[
  (239648,"49/36"),(239649,"49/36"),(239656,"49/36"),
  (244576,"49/36"),(244569,"49/36"),(244584,"49/36"),
  (244581,"49/36"),(237834,"49/36"),(237840,"49/36"),
  (237850,"49/36"),(245769,"49/36"),(245770,"49/36"),
  (239648,"32/49"),
]
def build_sample(item,token,output):
    role=item["armor_family"]
    item_id=item["item_id"]
    if role in CLASS: player,spec=CLASS[role]
    else:
        lookup={237840:("demonhunter","havoc"),
                237850:("shaman","enhancement"),
                245769:("mage","arcane"),
                245770:("mage","arcane")}
        player,spec=lookup[item_id]
    slot=item["slot"]
    lines=[
      player+'="V052CraftedStatic"', "spec="+spec,"level=90","race=dwarf",
      "role=attack","item_db_source=local","fight_style=Patchwerk",
      "iterations=1","threads=1","fixed_time=1","max_time=2",
      "vary_combat_length=0","optimal_raid=0","calculate_scale_factors=0",
      "actions=wait,sec=1"
    ]
    if item_id==237840:
        lines.append("main_hand=v052_main_warglaive,id=237840,ilevel=331,source=local,crafted_stats="+token)
    elif item_id==237850:
        lines.append("main_hand=v052_anchor,id=268209,ilevel=331,source=local")
    elif item_id==245769:
        lines.append("main_hand=v052_anchor,id=268205,ilevel=331,source=local")
    if item_id==237840:
        # Test same physical crafted warglaive in an offhand slot.
        # Avoid the duplicate same-ID two-hand configuration: the first
        # main-hand record may be sufficient, and the chosen report slot
        # is kept explicit.
        pass
    lines.append(f"{slot}=v052_crafted_{item_id},id={item_id},ilevel=331,source=local,crafted_stats={token}")
    lines.append("json2="+str(output.resolve()))
    return "\n".join(lines)+"\n"

def inspect(raw,item,token):
    rows=cache.native_records(raw,artifact_id="V052_CRAFTED_ILVL331")
    matches=[r for r in rows if r["identity"]["item_id"]==item["item_id"]
             and r["identity"]["ilevel"]==331
             and r["identity"]["options"].get("crafted_stats")==token
             and r["observed_slot"]==item["slot"]]
    if len(matches)!=1:raise cache.CacheBlocked("CRAFTED_NATIVE_VARIANT_ABSENT")
    row=matches[0];sec=row["static"]["secondary"]
    vals=[v for v in sec.values() if v>0]
    if len(vals)!=2 or abs(vals[0]-vals[1])>1:
        raise cache.CacheBlocked("CRAFTED_FIFTY_FIFTY_INVARIANT_UNVERIFIED")
    return row

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--binary",type=pathlib.Path,required=True)
    ap.add_argument("--catalog",type=pathlib.Path,required=True)
    ap.add_argument("--output",type=pathlib.Path,required=True)
    args=ap.parse_args(argv)
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"v052_crafted_native_331_stat_sampling_v1",
             "status":"SETUP_BLOCKED","native_calls":0,"max_native_calls":13,
             "results":[],"product_code_integrated":False,
             "official_policy_promoted":False,
             "dps_optimization":False,"game_reachability_attested":False}
    try:
        binary=args.binary.resolve()
        if not binary.is_file() or hashlib.sha256(binary.read_bytes()).hexdigest()!=BIN_SHA:
            raise cache.CacheBlocked("BINARY_SHA_MISMATCH")
        _,ids=bridge.load_reference(args.catalog)
        assert len(ITEM_CASES)==13 and len({i for i,_ in ITEM_CASES})==12
        variants=[]
        for i,(item_id,token) in enumerate(ITEM_CASES):
            item=ids[item_id];entry={"item_id":item_id,"token":token,"slot":item["slot"],
                                  "itemlevel":331,"status":"BLOCKED"}
            receipt["results"].append(entry)
            src=out/"sample.simc";result=out/"sample.json"
            src.write_text(build_sample(item,token,result),encoding="utf8")
            result.unlink(missing_ok=True)
            try:
                receipt["native_calls"]+=1
                p=subprocess.run([str(binary),str(src)],cwd=binary.parent,
                    stdin=subprocess.DEVNULL,capture_output=True,timeout=35)
                entry["simc_exit"]=p.returncode
                entry["stderr_excerpt"]=p.stderr.decode("utf8","replace")[:400]
                if p.returncode!=0 or not result.is_file():
                    raise cache.CacheBlocked("NATIVE_FAILED")
                raw=result.read_bytes()
                row=inspect(raw,item,token)
                entry["status"]="PASS_331_NATIVE_STATIC"
                entry["static_secondary"]=row["static"]["secondary"]
                entry["native_sha256"]=hashlib.sha256(raw).hexdigest()
                variants.append(row)
            except Exception as exc:
                entry["failure"]=type(exc).__name__+":"+str(exc)
            finally:
                (out/"V052_PROGRESS.json").write_text(json.dumps(receipt,indent=2)+"\n")
                for pth in (src,result):pth.unlink(missing_ok=True)
        native_cache=cache.empty_cache()
        cache.merge_native(native_cache,variants)
        cache.write_atomic(out/"v052_crafted_331_native_variants.json",native_cache)
        receipt["status"]="COMPLETE_WITH_ITEM_GAPS" if any(
            x["status"]!="PASS_331_NATIVE_STATIC" for x in receipt["results"]) else "PASS_ALL_13"
        receipt["success"]=sum(x["status"]=="PASS_331_NATIVE_STATIC" for x in receipt["results"])
        receipt["missing"]=len(ITEM_CASES)-receipt["success"]
    except Exception as exc:
        receipt["setup_error"]=type(exc).__name__+":"+str(exc)
    (out/"V052_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("V052",receipt["status"],"success",receipt.get("success",0),
          "native",receipt["native_calls"])
    return 0 if receipt["status"]!="SETUP_BLOCKED" else 3
if __name__=="__main__":sys.exit(main())
