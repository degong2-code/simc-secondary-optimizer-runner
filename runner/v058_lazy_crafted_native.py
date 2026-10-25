#!/usr/bin/env python3
"""v058 targeted Native stat hydration for selected crafted equipment, not effects.

Only cache-missing *nontrinket* variants trigger a 1-iteration SimC local
item-lookup. Trinket ID/stat reporting is never a selection or DPS gate.
No blanket refresh after SimC version changes. No WEQUIP runtime dependency.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,subprocess,sys

import v046_static_item_cache as cache
import v055_simc_item_selection as selector

BINARY_SHA="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"
CLASSES={"cloth":("mage","arcane","spell"),
         "leather":("druid","balance","spell"),
         "mail":("hunter","marksmanship","attack"),
         "plate":("warrior","arms","attack"),
         "shared":("mage","arcane","spell"),
         "jewelry":("mage","arcane","spell"),
         "shield":("warrior","protection","attack")}
ACCEPTED={"mage","druid","hunter","warrior","deathknight","paladin",
          "shaman","monk","demonhunter","evoker","priest","rogue","warlock"}
MAX_SECONDS=45

def require(ok,reason):
    if not ok:raise cache.CacheBlocked(reason)

def get_class(request):
    override=request.get("compatible_profile")
    if override is not None:
        require(type(override) is dict and set(override)=={"class","spec","role"},
                "COMPATIBLE_PROFILE_FIELDS")
        require(override["class"] in ACCEPTED and
             all(type(override[k]) is str and override[k].isidentifier()
                 for k in ("spec","role")),"COMPATIBLE_PROFILE_VALUES")
        return (override["class"],override["spec"],override["role"])
    catalog=selector.load_advisory_catalog()
    item=catalog.get(request["item_id"])
    require(item is not None,"UNCATALOGUED_ITEM_REQUIRES_COMPATIBLE_PROFILE")
    family=item["category"]
    require(family in CLASSES,"WEAPON_REQUIRES_COMPATIBLE_PROFILE")
    return CLASSES[family]

def validate_request(request):
    require(type(request) is dict and
            set(request)=={"item_id","slot","ilevel","options","compatible_profile"},
            "ON_DEMAND_REQUEST_SHAPE")
    selector.checked_id(request["item_id"])
    selector.checked_level(request["ilevel"])
    require(request["slot"] in selector.SLOTS,"REQUEST_SLOT_INVALID")
    selector.checked_options(request["options"])
    return request

def identity(request):
    return {"season":cache.SEASON,"item_id":request["item_id"],
            "ilevel":request["ilevel"],
            "slot":cache.normalize_slot(request["slot"]),
            "options":selector.checked_options(request["options"])}

def native_source(request,path):
    player,spec,role=get_class(request)
    slot=request["slot"]
    require(not slot.startswith("trinket"),"TRINKET_QUERY_NOT_REQUIRED")
    line=selector.equipment_line(slot,request["item_id"],
                                  request["ilevel"],request["options"])
    lines=[player+'="V058_Static_Only"','spec='+spec,'level=90',
           'race=dwarf','role='+role,
           'item_db_source=local','fight_style=Patchwerk',
           'iterations=1','threads=1','fixed_time=1','max_time=2',
           'vary_combat_length=0','optimal_raid=0','calculate_scale_factors=0',
           'actions=wait,sec=1']
    # A compatible 1H main-hand baseline for offhand-only lookup. SimC
    # validates actual weapon and class conditions; neither our code nor
    # the catalog implements weapon effects.
    if slot=="off_hand" and player in ("mage","priest","warlock"):
        lines.append("main_hand=v058_anchor,id=268205,ilevel=331,source=local")
    elif slot=="off_hand" and player not in ("mage","priest","warlock"):
        lines.append("main_hand=v058_anchor,id=268209,ilevel=331,source=local")
    lines.extend([line,"json2="+str(path.resolve())])
    return "\n".join(lines)+"\n"

def hydrate(request,initial_cache_path,bin_path,out):
    validate_request(request)
    out.mkdir(parents=True,exist_ok=True)
    report={"schema":"v058_lazy_native_stat_v1","status":"BLOCKED",
        "selected_item_id":request["item_id"],"native_attempts":0,
        "max_native_attempts":1,
        "effect_mechanics_by_simc_not_an_admission_gate":True,
        "simc_revision_not_cache_key":True,
        "product_code_integrated":False,"official_policy_promoted":False}
    try:
        current=cache.load(initial_cache_path)
        ident=identity(request);key=cache.digest(ident)
        if request["slot"].startswith("trinket"):
            report["status"]="PASS_TRINKET_NO_STATIC_LOOKUP_REQUIRED"
            report["G_contribution"]=0
            report["reported_native_static"]=current["variants"].get(key,{}).get("static")
            report["static_undetected_is_not_zero_proof"]=key not in current["variants"]
        elif key in current["variants"]:
            report["status"]="PASS_REUSED_EXACT_NATIVE_STATIC_VARIANT"
            report["G_contribution"]=sum(current["variants"][key]["static"]["secondary"].values())
        else:
            require(bin_path is not None and bin_path.is_file() and
                hashlib.sha256(bin_path.read_bytes()).hexdigest()==BINARY_SHA,
                "BINARY_SHA_CHANGED")
            path=out/"result.json"
            inp=out/"input.simc"
            inp.write_text(native_source(request,path),encoding="utf8")
            report["input_sha256"]=hashlib.sha256(inp.read_bytes()).hexdigest()
            report["native_attempts"]=1
            p=subprocess.run([str(bin_path),str(inp)],cwd=bin_path.parent,
                 stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE,timeout=MAX_SECONDS)
            (out/"stdout.txt").write_bytes(p.stdout)
            (out/"stderr.txt").write_bytes(p.stderr)
            require(p.returncode==0 and path.is_file(),
                    "NATIVE_ITEM_QUERY_FAILED")
            raw=path.read_bytes()
            records=cache.native_records(raw,artifact_id="V058_LAZY_CRAFTED_STATIC")
            matches=[x for x in records
                     if x["identity"]==ident and x["observed_slot"]==request["slot"]]
            require(len(matches)==1,"NATIVE_ITEM_LEVEL_OPTIONS_OR_SLOT_NOT_EXACT")
            outcome=cache.merge_native(current,matches)
            require(outcome["added_variants"]==1,"NATIVE_MERGE_NOT_NEW")
            report["native_json_sha256"]=hashlib.sha256(raw).hexdigest()
            report["G_contribution"]=sum(matches[0]["static"]["secondary"].values())
            report["status"]="PASS_ONE_MISSING_NONTRINKET_NATIVE_VARIANT_ADDED"
        cache.write_atomic(out/"static_cache_with_selected_variant.json",current)
    except Exception as exc:
        report["error"]=type(exc).__name__+":"+str(exc)
    (out/"V058_RECEIPT.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("V058",report["status"],"calls",report["native_attempts"],flush=True)
    return 0 if report["status"].startswith("PASS") else 3

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--request",type=pathlib.Path,required=True)
    p.add_argument("--seed",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    p.add_argument("--binary",type=pathlib.Path)
    a=p.parse_args(argv)
    req=json.loads(a.request.read_text())
    return hydrate(req,a.seed.resolve(),a.binary.resolve() if a.binary else None,
                   a.out.resolve())
if __name__=="__main__":sys.exit(main())
