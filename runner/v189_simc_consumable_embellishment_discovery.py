#!/usr/bin/env python3
"""v189: on-demand, PINNED SimC-source effect discovery (no Native, no UI promotion).

Input is the exact unique_gear_midnight.cpp bytes at the selected SimC commit.
Only extracts *registered handlers*. Not every DBC-backed consumable, actual
crafted reagent compatibility, valid SimC text token or working Native proc.
Those require separate DBC item/enchant/recipe joins and scoped validation.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from urllib.request import Request,urlopen

SCHEMA="v189_pinned_simc_effect_registration_candidates_v1"
SOURCE="engine/player/unique_gear_midnight.cpp"
URL_PREFIX="https://raw.githubusercontent.com/simulationcraft/simc/"
MAX_SOURCE=2_000_000
MAX_HANDLERS=1000
RE_COMMIT=re.compile(r"[0-9a-f]{40}\Z")
REGISTER=re.compile(r"(?:unique_gear::)?register_special_effect\s*\(\s*(\{[^}]+\}|[0-9]+)\s*,\s*((?:consumables|embellishments|darkmoon)::[a-zA-Z0-9_]+|DISABLED_EFFECT)")
MIN_VERSION=re.compile(r"set_min_version\s*\(\s*wowv_t\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)\s*\)")
RESET_VERSION=re.compile(r"reset_version_check\s*\(\s*\)")
NORM=re.compile(r"[^a-z0-9]+")
class DiscoveryBlocked(ValueError):pass
def need(ok,code):
    if not ok:raise DiscoveryBlocked(code)
def sha(data):
    return hashlib.sha256(data).hexdigest()
def bounds(s,start,end):
    need(s.count(start)==1 and s.count(end)==1,"SOURCE_SECTION_MARKER_MISMATCH")
    a=s.index(start)+len(start);b=s.index(end,a)
    need(a<b,"SOURCE_SECTION_ORDER_INVALID")
    return s[a:b]
def read_source(path=None,commit=None,transport=urlopen):
    if path is not None:
        p=Path(path)
        need(p.is_file() and 0<p.stat().st_size<=MAX_SOURCE,"SOURCE_PATH_INVALID")
        return p.read_bytes()
    need(type(commit) is str and RE_COMMIT.fullmatch(commit) is not None,
         "EXACT_SIMC_COMMIT_REQUIRED")
    url=URL_PREFIX+commit+"/"+SOURCE
    with transport(Request(url,headers={"User-Agent":"SIMC-Secondary-v189-source-discovery/1.0",
                                         "Accept":"text/plain"}),timeout=30) as response:
        need(response.status==200,"SIMC_PINNED_SOURCE_HTTP_NON200")
        data=response.read(MAX_SOURCE+1)
    need(0<len(data)<=MAX_SOURCE,"SIMC_PINNED_SOURCE_TOO_LARGE")
    return data

def extract_region(section,kind):
    candidates=[];version=[12,0,0]
    # Parsing each registration line is intentionally conservative. Unsupported
    # layouts BLOCK rather than silently miss registrations on future versions.
    for line in section.splitlines():
        stripped=line.strip()
        if not stripped or stripped.startswith("//"):continue
        m=MIN_VERSION.search(line)
        if m:
            version=[int(m.group(i)) for i in (1,2,3)]
            continue
        if "set_min_version(" in line:raise DiscoveryBlocked("UNKNOWN_VERSION_EXPRESSION")
        if RESET_VERSION.search(line):
            version=[12,0,0]
            continue
        if "reset_version_check(" in line:raise DiscoveryBlocked("UNKNOWN_VERSION_RESET")
        if "register_special_effect" not in line:continue
        found=REGISTER.search(line)
        need(found is not None,"UNPARSED_REGISTRATION_IN_"+kind)
        raw_ids=found.group(1)
        if raw_ids.startswith("{"):
            ids=[int(v) for v in re.findall(r"\d+",raw_ids)]
            need(re.sub(r"[\d,{}\s]","",raw_ids)=="","REGISTRATION_ID_EXPRESSION_NOT_SIMPLE")
        else:ids=[int(raw_ids)]
        need(ids and len(set(ids))==len(ids) and all(x>0 for x in ids),
             "REGISTRATION_IDS_INVALID")
        handler=found.group(2)
        comment=line.split("//",1)[1].strip() if "//" in line else ""
        candidates.append({"kind":kind,"spell_ids":ids,"handler":handler,
           "minimum_game_version":version.copy(),"source_comment":comment,
           "implemented":handler!="DISABLED_EFFECT",
           "evidence_level":"SIMC_HANDLER_REGISTERED_ONLY",
           "native_acceptance":"NOT_CHECKED",
           "actual_item_id":"UNRESOLVED",
           "ui_selectable":False})
        need(len(candidates)<=MAX_HANDLERS,"TOO_MANY_REGISTRATIONS")
    need(candidates,"NO_HANDLERS_"+kind)
    return candidates

def discover(data,commit):
    need(type(commit) is str and RE_COMMIT.fullmatch(commit) is not None,
         "EXACT_SIMC_COMMIT_REQUIRED")
    need(type(data) is bytes and 0<len(data)<=MAX_SOURCE,
         "SOURCE_BYTES_INVALID")
    try:s=data.decode("utf8")
    except UnicodeError as exc:raise DiscoveryBlocked("SOURCE_NOT_UTF8") from exc
    need(s.count("void register_special_effects()")==1,
         "SOURCE_REGISTRY_FUNCTION_MISSING_OR_AMBIGUOUS")
    root=s[s.index("void register_special_effects()"):]
    # Anchors define unambiguous, mutually disjoint registrations in pinned
    # Midnight C++. If any move or disappear, require explicit parser review.
    food=extract_region(bounds(root,"  // Food\n","  // Flasks\n"),"food")
    potion=extract_region(bounds(root,"  // Potions\n","  // Oils\n"),"potion")
    embellished=extract_region(bounds(root,"  // Embellishments & Tinkers\n",
                                     "  // Trinkets\n"),"embellishment_or_darkmoon")
    need(all(x["handler"].startswith("consumables::") for x in food+potion),
         "SOURCE_CONSUMABLE_KIND_DRIFT")
    need(all(x["handler"].startswith(("embellishments::","darkmoon::")) or
             not x["implemented"] for x in embellished),
         "SOURCE_EMBELLISHMENT_KIND_DRIFT")
    distinct_ids=[i for candidates in (food,potion,embellished)
                    for x in candidates for i in x["spell_ids"]]
    need(len(set(distinct_ids))==len(distinct_ids),
         "DUPLICATE_REGISTRATION_SPELL_IDS")
    return {
      "schema":SCHEMA,"status":"DISCOVERED_EFFECT_HANDLERS_NOT_PUBLISHED",
      "source":{"repository":"simulationcraft/simc","commit":commit,
        "path":SOURCE,"sha256":sha(data),"bytes":len(data)},
      "counts":{"food_handler_registrations":len(food),
          "potion_handler_registrations":len(potion),
          "embellishment_and_darkmoon_registrations":len(embellished),
          "disabled_embellishment_registrations":sum(not v["implemented"] for v in embellished)},
      "candidates":{"food":food,"potion":potion,
                    "embellishment_or_darkmoon":embellished},
      "unresolved_requirements":[
         "FOOD_AND_POTION_ITEM_LIST_FROM_SAME_BUILD_SIMC_DBC",
         "ITEM_NAME_CRAFT_QUALITY_CLASS_SUBCLASS_AND_SOURCE_TOKEN",
         "EMBELLISHMENT_OPTION_REAGENT_OR_ITEM_SLOT_RESTRICTIONS",
         "EMBELLISHMENT_EFFECT_SPELL_TO_REAL_ITEM_OR_ENCHANT_ID",
         "PINNED_SIMC_NATIVE_ACCEPTANCE_FOR_NEW_OPTIONS",
         "KOREAN_DISPLAY_NAME_AND_TOOLTIP_PROVENANCE"],
      "source_only_not_native":True,"new_native_calls":0,
      "auto_promote_to_user_ui":False,
      "historical_sessions_and_cache_mutated":False}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--simc-commit",required=True)
    p.add_argument("--source",type=Path,help="Already pinned local source, else fetch exact GitHub commit")
    p.add_argument("--source-sha256",help="Optional required source-byte sha256")
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args(argv)
    need(a.source is None or a.source_sha256 is not None,
         "LOCAL_SOURCE_REQUIRES_EXACT_SOURCE_SHA")
    raw=read_source(a.source,a.simc_commit)
    if a.source_sha256:
        need(a.source_sha256==sha(raw),"SOURCE_SHA_MISMATCH")
    data=discover(raw,a.simc_commit)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+"\n",
                     encoding="utf8")
    print("V189_SIMC_DISCOVERY",json.dumps(data["counts"],sort_keys=True),
          "NATIVE_0","NOT_PROMOTED",flush=True)
    return 0
if __name__=="__main__":raise SystemExit(main())
