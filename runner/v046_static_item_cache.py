#!/usr/bin/env python3
"""v046 lightweight *static item variant* cache, independent of SimC revision.

No SimC invocation, DPS computation, or gear optimization.
New SimC revisions are provenance only; same-season static entries stay cached.
Catalog identity is not stat authority; only actual Native JSON2 populates stats.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import zipfile

SCHEMA = "simc_static_item_cache_v046"
SEASON = "midnight_s2"
STATS = ("crit_rating", "haste_rating", "mastery_rating", "versatility_rating")
PRIMARY = ("strength", "agility", "intellect", "stragiint", "stamina", "armor")
MAX_VARIANTS = 10000
MAX_NATIVE_BYTES = 25_000_000
MAX_CATALOG_ROWS = 4000
ALLOWED_OPTION = re.compile(r"^[a-z][a-z0-9_]*$")
SLOT_ALIASES = {"finger1":"finger", "finger2":"finger", "trinket1":"trinket",
                "trinket2":"trinket", "shoulder":"shoulders",
                "wrist":"wrists", "hand":"hands", "ring1":"finger",
                "ring2":"finger"}

class CacheBlocked(ValueError):
    pass

def need(condition, code):
    if not condition:
        raise CacheBlocked(code)

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",",":"), allow_nan=False)

def digest(value):
    data=value if isinstance(value,bytes) else canonical(value).encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def empty_cache(season=SEASON):
    need(type(season) is str and bool(re.fullmatch("[a-z][a-z0-9_]{2,50}",season)),
         "INVALID_SEASON")
    return {"schema":SCHEMA,"season":season,"catalog":{},"variants":{},
            "correction_history":[]}

def check_cache(cache):
    need(type(cache) is dict and set(cache)=={"schema","season","catalog","variants","correction_history"},
         "CACHE_SCHEMA")
    need(cache["schema"]==SCHEMA,"CACHE_SCHEMA_VERSION")
    need(type(cache["catalog"]) is dict and len(cache["catalog"])<=MAX_CATALOG_ROWS,
         "CATALOG_TOO_LARGE")
    need(type(cache["variants"]) is dict and len(cache["variants"])<=MAX_VARIANTS,
         "VARIANTS_TOO_LARGE")
    need(type(cache["correction_history"]) is list,"HISTORY_INVALID")
    empty_cache(cache["season"])
    for key,record in cache["variants"].items():
        need(key==digest(record.get("identity")),"CACHE_KEY_CORRUPT")
        need(record.get("source_kind")=="NATIVE_JSON2_RESOLVED_VARIANT"
             or record.get("source_kind")=="USER_REQUESTED_MANUAL_CORRECTION",
             "CACHE_SOURCE_INVALID")
        need(record.get("static_digest")==digest(record.get("static")),
             "CACHE_STATIC_TAMPER")
    return cache

def load(path,season=SEASON):
    if not path.is_file():
        return empty_cache(season)
    cache=check_cache(json.loads(path.read_text(encoding="utf-8")))
    need(cache["season"]==season,"SEASON_MISMATCH")
    return cache

def write_atomic(path,cache):
    check_cache(cache)
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix=".static-cache-",suffix=".tmp")
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as out:
            out.write(json.dumps(cache,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def parse_encoded(raw):
    need(type(raw) is str and len(raw)<=4096,"ENCODED_ITEM_INVALID")
    tokens=raw.split(",")
    need(tokens[0]!="","ITEM_NAME_EMPTY")
    options={}
    for token in tokens[1:]:
        need("=" in token,"BAD_ITEM_OPTION")
        key,value=token.split("=",1)
        need(ALLOWED_OPTION.fullmatch(key) is not None and value
             and key not in options,"DUPLICATE_OR_BAD_ITEM_OPTION")
        options[key]=value
    need(re.fullmatch(r"[1-9][0-9]*",options.get("id","")) is not None,"ITEM_ID_MISSING")
    need(re.fullmatch(r"[1-9][0-9]*",options.get("ilevel","")) is not None,
         "ILEVEL_OPTION_MISSING")
    return tokens[0],options

def normalize_slot(slot):
    need(type(slot) is str and bool(re.fullmatch(r"[a-z][a-z0-9_]{1,30}",slot)),
         "INVALID_SLOT")
    return SLOT_ALIASES.get(slot,slot)

def read_number(item,k):
    v=item.get(k,0)
    need(type(v) is int and 0<=v<=100000,"BAD_STATIC_NUMERIC:"+k)
    return v

def native_records(payload,season=SEASON,artifact_id=None):
    need(type(payload) is bytes and len(payload)<=MAX_NATIVE_BYTES,"NATIVE_PAYLOAD_SIZE")
    doc=json.loads(payload)
    need(type(doc) is dict and doc.get("report_version")=="2.0.0",
         "NOT_NATIVE_JSON2")
    people=(doc.get("sim") or {}).get("players")
    need(type(people) is list and len(people)==1,"NATIVE_PLAYER_COUNT")
    gear=people[0].get("gear")
    need(type(gear) is dict and 1<=len(gear)<=25,"NATIVE_GEAR_COUNT")
    revision=str(doc.get("git_revision",""))
    need(re.fullmatch(r"[0-9a-f]{7,40}",revision) is not None,"NATIVE_REVISION_MISSING")
    records=[]
    for slot,item in sorted(gear.items()):
        need(type(item) is dict,"INVALID_GEAR_SLOT")
        name,options=parse_encoded(item.get("encoded_item"))
        need(item.get("ilevel")==int(options["ilevel"]),"NATIVE_ILEVEL_CONFLICT")
        # Variants include ALL relevant item modifiers, including gemstones,
        # enchant, crafted stats, redirect and bonus IDs. Source and display
        # alias are intentionally not part of the static-stats identity.
        variant_options={k:v for k,v in options.items()
                         if k not in ("id","ilevel","source")}
        ident={"season":season,"item_id":int(options["id"]),
               "ilevel":int(options["ilevel"]),
               "slot":normalize_slot(slot),"options":variant_options}
        static={"secondary":{s:read_number(item,s) for s in STATS},
                "primary_other":{s:read_number(item,s) for s in PRIMARY}}
        # Store weapon-related native fields only if the JSON2 actually exposes
        # numeric values; never fabricate weapon dps from item id or itemlevel.
        additional={}
        for k in ("weapon_dps","weapon_speed","min_damage","max_damage"):
            if k in item:
                val=item[k]
                need(type(val) in (float,int) and val>=0,"BAD_WEAPON_FIELD:"+k)
                additional[k]=val
        static["weapon_if_native"]=additional
        decorated=bool(set(variant_options) &
                       {"gem_id","enchant","enchant_id","embellishment",
                        "crafted_stats","socket"})
        records.append({
            "identity":ident,"static":static,
            "static_digest":digest(static),
            "source_kind":"NATIVE_JSON2_RESOLVED_VARIANT",
            "item_name_observed":name,
            "observed_slot":slot,
            "modifiers_present":decorated,
            "bare_item_stats_independently_attested":False,
            "metadata":{"native_revision":revision,
                        "native_json_sha256":digest(payload),
                        "artifact":artifact_id or "UNSPECIFIED",
                        "item_db_source":options.get("source","not_reported")},
            "not_user_selection":True,
            "dynamic_effect_values_cached":False,
            "eligible_for_gear_sum_only_in_exact_same_variant":True
        })
    return records

def merge_native(cache,records):
    """Append only. No silent stat changes, even if SimC version changes."""
    check_cache(cache)
    staged=dict(cache["variants"])
    changed=0;reused=0
    for item in records:
        need(item["identity"]["season"]==cache["season"],"ITEM_SEASON_MISMATCH")
        key=digest(item["identity"])
        if key in staged:
            need(staged[key]["static_digest"]==item["static_digest"],
                 "STATIC_CONFLICT_MANUAL_REVIEW_REQUIRED:"+str(item["identity"]["item_id"]))
            reused+=1
            continue
        staged[key]=item
        changed+=1
    need(len(staged)<=MAX_VARIANTS,"CACHE_FULL")
    cache["variants"]=staged
    return {"added_variants":changed,"reused_variants":reused,
            "total_variants":len(staged),"native_simc_calls":0}

def catalog_rows(payload,season=SEASON):
    doc=json.loads(payload)
    need(type(doc) is dict and type(doc.get("items")) in (dict,list),"CATALOG_SHAPE")
    stated=doc.get("season")
    if stated is not None and season==SEASON:
        need(stated=="Midnight Season 2","CATALOG_SEASON_CONFLICT")
    source=doc["items"]
    if isinstance(source,dict):
        entries=list(source.items());source_type="WEQUIP_MASTER_METADATA_ONLY"
    else:
        entries=[(str(i),item) for i,item in enumerate(source)]
        source_type="PATCH_DELTA_METADATA_ONLY"
    need(len(entries)<=MAX_CATALOG_ROWS,"CATALOG_SOURCE_EXCESSIVE")
    result=[]
    for record_id,entry in entries:
        need(type(entry) is dict,"CATALOG_ITEM_INVALID")
        id_=entry.get("item_id")
        need(type(id_) is int and id_>0,"CATALOG_ITEM_ID_INVALID")
        name=entry.get("name_en") or entry.get("name")
        need(type(name) is str and bool(name.strip()),"CATALOG_NAME_INVALID")
        slot=entry.get("slot")
        need(type(slot) is str and bool(slot),"CATALOG_SLOT_INVALID")
        result.append({"item_id":id_,"name":name,"slot":slot,
            "armor_type":entry.get("item_subclass_name"),
            "category_hint":entry.get("category","UNCLASSIFIED"),
            "source_class":source_type,
            "source_reference":str(record_id),
            "status":"CATALOG_ONLY_STATS_NOT_SIMC_VERIFIED"})
    return result

def merge_catalog(cache,rows):
    """Same physical ID may occur at multiple loot sources; keep references."""
    check_cache(cache)
    staged=json.loads(json.dumps(cache["catalog"]))
    created=0
    for row in rows:
        key=str(row["item_id"])
        if key not in staged:
            staged[key]={"item_id":row["item_id"],
                "names":[row["name"]],
                "slots":[row["slot"]],
                "armor_types":([row["armor_type"]] if row["armor_type"] else []),
                "category_hints":([row["category_hint"]] if row["category_hint"] else []),
                "provenance":[],"stats_verified":False}
            created+=1
        record=staged[key]
        for prop,value in (("names",row["name"]),("slots",row["slot"]),
                            ("armor_types",row["armor_type"]),
                            ("category_hints",row["category_hint"])):
            if value and value not in record[prop]:
                record[prop].append(value)
        origin={"source_class":row["source_class"],
                "source_reference":row["source_reference"]}
        if origin not in record["provenance"]:
            record["provenance"].append(origin)
    need(len(staged)<=MAX_CATALOG_ROWS,"CATALOG_FULL")
    cache["catalog"]=staged
    return {"source_rows":len(rows),"new_ids":created,"total_ids":len(staged),
            "stats_populated_by_catalog":0}

def request_correction(cache,request):
    """Explicit human-requested replacement, never a SimC-version refresh."""
    need(type(request) is dict and set(request)==
         {"identity","new_static","expected_static_digest","reason",
          "user_requested"},"CORRECTION_SHAPE")
    need(request["user_requested"] is True and type(request["reason"]) is str
         and len(request["reason"].strip())>=12,"EXPLICIT_CORRECTION_REQUIRED")
    need(type(request["expected_static_digest"]) is str and
         re.fullmatch("[0-9a-f]{64}",request["expected_static_digest"]),
         "CORRECTION_EXPECTED_HASH")
    key=digest(request["identity"])
    entry=cache["variants"].get(key)
    need(entry is not None,"CORRECTION_UNKNOWN_VARIANT")
    need(entry["static_digest"]==request["expected_static_digest"],
         "CORRECTION_STALE_EXPECTED_DIGEST")
    proposed=request["new_static"]
    need(type(proposed) is dict and set(proposed)==set(entry["static"]),
         "CORRECTION_FIELDS")
    for bucket in ("secondary","primary_other"):
        need(type(proposed[bucket]) is dict and set(proposed[bucket])==
             set(entry["static"][bucket]),"CORRECTION_STAT_FIELDS")
        for n in proposed[bucket].values():
            need(type(n) is int and 0<=n<=100000,"CORRECTION_STAT_RANGE")
    need(type(proposed["weapon_if_native"]) is dict,"CORRECTION_WEAPON_SHAPE")
    for n in proposed["weapon_if_native"].values():
        need(type(n) in (int,float) and n>=0,"CORRECTION_WEAPON_VALUE")
    need(digest(proposed)!=entry["static_digest"],"NO_CORRECTION_DIFFERENCE")
    prior_digest=entry["static_digest"]
    cache["correction_history"].append({"identity":request["identity"],
       "prior_static_digest":prior_digest,"new_static_digest":digest(proposed),
       "reason":request["reason"],"user_requested":True})
    entry["static"]=proposed
    entry["static_digest"]=digest(proposed)
    entry["source_kind"]="USER_REQUESTED_MANUAL_CORRECTION"
    return {"status":"EXPLICIT_CORRECTION_APPLIED",
            "previous_digest":prior_digest,"new_digest":entry["static_digest"]}

def selected_gear_sum(cache,identities):
    """Add only exact same resolved variants; trinket stat outside G."""
    need(type(identities) is list and len(identities)>0,"NO_SELECTED_GEAR")
    total=dict.fromkeys(STATS,0);external=dict.fromkeys(STATS,0)
    seen=set()
    for identity in identities:
        need(type(identity) is dict,"GEAR_IDENTITY_INVALID")
        key=digest(identity);item=cache["variants"].get(key)
        need(item is not None,"CACHE_MISS_NOT_ZERO:"+str(identity.get("item_id")))
        # Duplicate ring/trinket slot identities are permitted only when
        # callers explicitly supply distinct slot keys; otherwise fail.
        slot=identity.get("slot")
        need(slot not in seen or slot in ("finger","trinket"),
             "DUPLICATE_SLOT_SUM")
        seen.add(slot)
        bucket=external if slot=="trinket" else total
        for s in STATS:
            bucket[s]+=item["static"]["secondary"][s]
    return {"G_native_static_including_selected_modifiers":sum(total.values()),
            "G_vector":total,"trinket_external_vector":external,
            "J_policy":138,"F_policy":165,
            "T_v1_policy_arithmetic":sum(total.values())+138+165,
            "J_F_NOT_PROVED_CAUSALLY_BY_CACHE":True,
            "requires_reconciliation_if_gems_oils_present":True,
            "not_a_user_ready_budget":True}

def get_native_input(path,member):
    if path.suffix.lower()!=".zip":
        payload=path.read_bytes()
    else:
        need(member is not None,"ZIP_MEMBER_REQUIRED")
        with zipfile.ZipFile(path) as z:
            need(z.testzip() is None,"ZIP_CRC")
            need(len(z.namelist())<=300,"ZIP_TOO_MANY_FILES")
            need(member in z.namelist() and not member.startswith("/")
                 and ".." not in Path(member).parts,"ZIP_MEMBER_INVALID")
            need(z.getinfo(member).file_size<=MAX_NATIVE_BYTES,"ZIP_NATIVE_TOO_BIG")
            payload=z.read(member)
    need(len(payload)<=MAX_NATIVE_BYTES,"INPUT_TOO_LARGE")
    return payload

def main(argv=None):
    p=argparse.ArgumentParser(description="Offline lightweight Native static item cache")
    p.add_argument("--cache",type=Path,required=True)
    p.add_argument("--season",default=SEASON)
    subs=p.add_subparsers(dest="action",required=True)
    n=subs.add_parser("import-native")
    n.add_argument("--input",type=Path,required=True)
    n.add_argument("--zip-member")
    n.add_argument("--artifact-id")
    c=subs.add_parser("import-catalog")
    c.add_argument("--input",type=Path,required=True)
    r=subs.add_parser("correct")
    r.add_argument("--request",type=Path,required=True)
    subs.add_parser("summary")
    args=p.parse_args(argv)
    try:
        cache=load(args.cache,args.season)
        if args.action=="import-native":
            records=native_records(get_native_input(args.input,args.zip_member),
                                   args.season,args.artifact_id)
            result=merge_native(cache,records)
        elif args.action=="import-catalog":
            result=merge_catalog(cache,catalog_rows(args.input.read_bytes(),args.season))
        elif args.action=="correct":
            result=request_correction(cache,json.loads(args.request.read_text()))
        else:
            result={"catalog_ids":len(cache["catalog"]),
                    "cached_item_variants":len(cache["variants"]),
                    "manual_corrections":len(cache["correction_history"])}
        if args.action!="summary":
            write_atomic(args.cache,cache)
        print(json.dumps({"status":"PASS","action":args.action,"result":result,
                         "simc_revisions_not_cache_keys":True,
                         "simc_exec_calls":0},ensure_ascii=False,sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status":"BLOCKED","reason":str(exc),
                          "type":type(exc).__name__},ensure_ascii=False),file=sys.stderr)
        return 3

if __name__=="__main__":
    sys.exit(main())
