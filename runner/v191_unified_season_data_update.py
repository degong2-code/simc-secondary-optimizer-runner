#!/usr/bin/env python3
"""v191: one request-scoped, source-pinned *candidate* season update.

Assembles existing source-first gear/tier/CHMV, v189 SimC effect handlers,
v190 same-build consumable items and exact SimC generated enchant/gem tables.
SimC owns effects. This code owns IDs, options, slot masks, version evidence
and deterministic high-quality reduction. No Native, API fetch or UI promotion.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re
from pathlib import Path

SCHEMA="v191_unified_patch_season_expansion_data_candidates_v1"
MAX_FILE=5_000_000
HEX40=re.compile(r"[a-f0-9]{40}\Z")
GENERATED={
  "permanent_enchant":"permanent_enchant.inc",
  "temporary_enchant":"temporary_enchant.inc",
  "gem_property":"gem_data.inc"}
PAT_PERM=re.compile(r'^\s*\{\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(0x[0-9a-fA-F]+)\s*,\s*(0x[0-9a-fA-F]+)\s*,\s*"([^"]+)"\s*\},?\s*$')
PAT_TEMP=re.compile(r'^\s*\{\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*"([^"]+)"\s*\},?\s*$')
PAT_GEM=re.compile(r'^\s*\{\s*(\d+)\s*,\s*(\d+)\s*,\s*(0x[0-9a-fA-F]+)\s*,\s*(\d+)\s*\},?\s*(?://.*)?$')
COUNTER=re.compile(r'std::array<\w+,\s*(\d+)>')
BUILD=re.compile(r'wow build (\d+\.\d+\.\d+\.\d+)')
class CatalogBlocked(ValueError):pass
def need(value,reason):
    if not value:raise CatalogBlocked(reason)
def canonical(obj):
    return json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":"))
def digest(data):
    return hashlib.sha256(data).hexdigest()
def read_small(path):
    p=Path(path)
    need(p.is_file() and 0<p.stat().st_size<=MAX_FILE,
         "SMALL_INPUT_MISSING_OR_TOO_LARGE:"+p.name)
    return p.read_bytes()
def load_json(path):
    data=read_small(path)
    try:return json.loads(data.decode("utf8")),digest(data)
    except (UnicodeError,ValueError) as e:
        raise CatalogBlocked("INVALID_JSON:"+Path(path).name) from e
def parse_generated(name,data):
    need(name in GENERATED,"UNSUPPORTED_SIMC_GENERATED_DATA")
    try:s=data.decode("utf8")
    except UnicodeError as e:raise CatalogBlocked("SIMC_GENERATED_NON_UTF8") from e
    header=s.splitlines()[:5]
    m=BUILD.search("\n".join(header));n=COUNTER.search("\n".join(header))
    need(m is not None and n is not None,"SIMC_GENERATED_HEADER_MISSING:"+name)
    total=int(n.group(1));need(total>0,"SIMC_GENERATED_EMPTY:"+name)
    pat={"permanent_enchant":PAT_PERM,
         "temporary_enchant":PAT_TEMP,
         "gem_property":PAT_GEM}[name]
    parsed=[]
    for line in s.splitlines():
        if not line.lstrip().startswith("{"):continue
        found=pat.fullmatch(line)
        need(found is not None,"UNPARSED_SIMC_GENERATED_ROW:"+name)
        vals=found.groups()
        if name=="permanent_enchant":
            eid,rank,item_class,inventory_mask,subclass_mask,token=vals
            entry={"enchant_id":int(eid),"quality_rank":int(rank),
                   "item_class":int(item_class),
                   "inventory_type_mask":int(inventory_mask,16),
                   "item_subclass_mask":int(subclass_mask,16),
                   "simc_token":token,
                   "input_form":"enchant=token_or_enchant_id",
                   "effect_magnitude":"UNRESOLVED"}
        elif name=="temporary_enchant":
            eid,rank,spell,token=vals
            entry={"enchant_id":int(eid),"quality_rank":int(rank),
                   "effect_spell_id":int(spell),"simc_token":token,
                   "input_form":"temporary_enchant=weapon_slot:token",
                   "effect_magnitude":"UNRESOLVED"}
        else:
            property_id,enchant_id,color_mask,min_ilevel=vals
            entry={"gem_property_id":int(property_id),
                   "enchant_id":int(enchant_id),
                   "color_mask":int(color_mask,16),
                   "minimum_ilevel":int(min_ilevel),
                   "gem_item_id":"UNRESOLVED"}
        parsed.append(entry)
    need(len(parsed)==total,"SIMC_GENERATED_ROW_COUNT_MISMATCH:"+name)
    return {"source_build":m.group(1),"declared_rows":total,
            "sha256":digest(data),"rows":parsed}

def highest_known_quality(rows,name):
    """Collapse only exact same SimC token+physical applicability.
    
    Never mix distinct effects, item-slot masks or armor/weapon subclasses.
    Rank 0 (not tiered) is legitimate. Rank alone does not certify potency
    against different effects, and unknown spell magnitude is not guessed.
    """
    groups=collections.defaultdict(list)
    for x in rows:
        if name=="permanent_enchant":
            key=(x["simc_token"],x["item_class"],
                 x["inventory_type_mask"],x["item_subclass_mask"])
        else:key=(x["simc_token"],)
        groups[key].append(x)
    winners=[]
    for family in groups.values():
        rank=max(x["quality_rank"] for x in family)
        best=[x for x in family if x["quality_rank"]==rank]
        # Multiple records at the highest rank can be distinct enchant
        # variants. Do not choose an arbitrary 'strongest' without stats.
        distinct={canonical(v):v for v in best}
        winners.extend(distinct.values())
    return sorted(winners,key=lambda x:(x["simc_token"],x["quality_rank"],
                 x["enchant_id"]))

def highest_effect_variants(rows):
    """Only comparable, verified SAME-effect + SAME-slot numeric variants.

    Unknown strength? Preserve all ambiguous variants, never falsely infer
    higher item level, quality or a generic primary stat is more DPS.
    """
    families=collections.defaultdict(list)
    for row in rows:
        need(all(k in row for k in ("kind","effect_fingerprint","allowed_slots",
                                    "quality_rank","effect_strength")),
             "EFFECT_COMPARISON_SCHEMA_MISSING")
        key=(row["kind"],row["effect_fingerprint"],
             tuple(sorted(row["allowed_slots"])))
        families[key].append(row)
    kept=[]
    for group in families.values():
        if len(group)==1:kept.extend(group);continue
        comparable=all(type(x["quality_rank"]) is int and
                       type(x["effect_strength"]) in (int,float)
                       for x in group)
        if not comparable:
            kept.extend(group)
            continue
        best=max((v["quality_rank"],v["effect_strength"]) for v in group)
        kept.extend(v for v in group
                    if (v["quality_rank"],v["effect_strength"])==best)
    return kept

def current_season_enchant_candidates(generated_permanent):
    """Source-observed Midnight enchant_ names, not historical 772 entries.

    These new-enchant tokens are tied to a real built-in SimC slot mask and
    each exact token retains only highest quality; profession tools (class19)
    are excluded. No game item ID, DPS strength, Native acceptance or UI
    publication is inferred from these generated tables alone.
    """
    observed=[x for x in generated_permanent["rows"]
              if x["simc_token"].startswith("enchant_")
              and x["item_class"] in (2,4)]
    winners=highest_known_quality(observed,"permanent_enchant")
    need(len({x["simc_token"] for x in winners})==len(winners),
         "SAME_ENCHANT_TOKEN_CONFLICTING_EQUIPMENT_CLASS")
    for row in winners:
        row["inventory_type_options"]=inventory_options(row)
        need(row["inventory_type_options"] or row["item_class"]==2,
             "CURRENT_SEASON_ENCHANT_SLOT_MASK_UNRESOLVED")
        row["user_selectable"]=False
        row["season_basis"]="SIMC_MIDNIGHT_ENCHANT_TOKEN_PREFIX_NOT_ITEM_RECIPE_CERTIFIED"
    return winners

def inventory_options(entry):
    mask=entry["inventory_type_mask"]
    # SimC find() evaluates (1 << inventory_type), not a human-readable
    # enchant slot enum. Unrestricted 0 means we CANNOT infer a slot list.
    return [i for i in range(1,31) if mask&(1<<i)] if mask else []

def compile_catalog(gear,tier,budget,effects,consumables,generated,*,event):
    need(event in ("mid_patch","season_change","expansion_change"),
         "UPDATE_EVENT_NOT_EXPLICIT")
    need(gear.get("schema")=="v167_product_season_gear_db_v1"
         and tier.get("schema")=="v168_source_first_class_tier_5pc_v1"
         and budget.get("schema")=="v165_current_season_chmv_consumables_v1",
         "SOURCE_FIRST_CORE_CATALOG_SCHEMA_MISMATCH")
    build=gear["season_build"]
    need(tier["retail_build"]==budget["retail_build"]==build
         and tier["expansion_id"]==gear["expansion_id"]
         and len(tier["classes"])==13 and
         len(gear["items"])==gear["item_count"],
         "CORE_BUILD_OR_COUNTS_MISMATCH")
    need(effects.get("schema")=="v189_pinned_simc_effect_registration_candidates_v1"
         and effects.get("auto_promote_to_user_ui") is False
         and consumables.get("schema")=="v190_same_build_consumable_item_candidates_v1"
         and consumables.get("automatic_ui_promotion") is False
         and consumables["source"]["wago_snapshot_build"]==build
         and consumables["source"]["simc_revision"]==effects["source"]["commit"]
         and consumables["source"]["simc_registration_sha256"]==
             effects["source"]["sha256"],
         "SIMC_AND_DB2_PROVENANCE_MISMATCH")
    need(all(k in generated for k in GENERATED),"SIMC_GENERATED_FILES_MISSING")
    builds={k:v["source_build"] for k,v in generated.items()}
    # Independent native DBC snapshot is often a different *build* from
    # current Wago CSV; this is material and must remain in the receipt.
    counts=collections.Counter(x["category"] for x in gear["items"])
    need(len(set(x["item_id"] for x in gear["items"]))==len(gear["items"]),
         "GEAR_DUPLICATE_ITEM_IDS")
    tiers={cl:{slot:entry["item_id"] if type(entry) is dict else entry
               for slot,entry in data["pieces"].items()}
           for cl,data in tier["classes"].items()}
    need(all(len(v)==5 for v in tiers.values())
         and len({v for record in tiers.values() for v in record.values()})==65,
         "SIXTY_FIVE_UNIQUE_TIER_IDS_REQUIRED")
    permanent=highest_known_quality(
        generated["permanent_enchant"]["rows"],"permanent_enchant")
    temporary=highest_known_quality(
        generated["temporary_enchant"]["rows"],"temporary_enchant")
    season_enchants=current_season_enchant_candidates(
        generated["permanent_enchant"])
    for item in permanent:
        item["inventory_type_options"]=inventory_options(item)
        item["user_selectable"]=False
    for item in temporary:item["user_selectable"]=False
    warnings=["PUBLISHED_CATALOG_NOT_READY_SIMC_ITEM_EFFECT_AND_CRAFT_QUALITY",
        "SIMC_EFFECT_IMPLEMENTED_IS_DISCOVERY_AUTHORITY_NOT_PHYSICAL_SLOT_MASK"]
    if set(builds.values())!={build}:
        warnings.append("SIMC_COMPILED_DBC_AND_GAME_DB2_BUILDS_DIFFER_REVIEW")
    gear_candidates=[
      {k:x.get(k) for k in (
        "item_id","name","category","class_id","subclass_id","inventory_type",
        "allowed_class_mask","item_set_id","slot_hint","source_kinds",
        "season_list_basis","stat_modifier_codes")}
      for x in sorted(gear["items"],key=lambda row:row["item_id"])
    ]
    tier_classes={
      cl:{
        "allowed_class_mask":data["allowed_class_mask"],
        "item_set_id":data["item_set_id"],
        "names":dict(sorted(data["names"].items())),
        "pieces":dict(sorted(tiers[cl].items()))
      }
      for cl,data in sorted(tier["classes"].items())
    }
    related_source_counts={
      "gear_item_candidates":len(gear_candidates),
      "tier_piece_ids":sum(len(x["pieces"]) for x in tier_classes.values()),
      "food_raw_item_candidates":sum(x["kind"]=="food" for x in consumables["items"]),
      "potion_raw_item_candidates":sum(x["kind"]=="potion" for x in consumables["items"]),
      "food_handler_registrations":len(effects["candidates"].get("food",[])),
      "potion_handler_registrations":len(effects["candidates"].get("potion",[])),
      "embellishment_darkmoon_registrations":len(
          effects["candidates"].get("embellishment_or_darkmoon",[])),
      "temporary_enchant_entries":generated["temporary_enchant"]["declared_rows"],
      "gem_property_records":generated["gem_property"]["declared_rows"]
    }
    return {
      "schema":SCHEMA,"status":"SOURCE_COMBINED_NOT_YET_USER_SELECTABLE",
      "update_event":event,"game_build":build,"expansion_id":gear["expansion_id"],
      "simc_revision":effects["source"]["commit"],"simc_generated_builds":builds,
      "warnings":warnings,"native_calls":0,"network_calls_by_compiler":0,
      "source_first":True,"automatic_ui_promotion":False,
      "source_artifacts":{
        "v189":{"schema":effects["schema"],"simc_commit":effects["source"]["commit"],
                "source_sha256":effects["source"]["sha256"]},
        "v190":{"schema":consumables["schema"],
                "game_build":consumables["source"]["wago_snapshot_build"],
                "simc_revision":consumables["source"]["simc_revision"],
                "simc_registration_sha256":consumables["source"]["simc_registration_sha256"]}
      },
      "related_source_counts":related_source_counts,
      "gear":{"count":len(gear_candidates),"role_counts":dict(sorted(counts.items())),
              "item_ids_by_role":{kind:sorted(x["item_id"] for x in gear["items"]
                                    if x["category"]==kind) for kind in sorted(counts)},
              "candidates":gear_candidates},
      "tier":{"class_count":13,"piece_count":65,"item_ids":tiers,
              "classes":tier_classes},
      "consumables":{
         "food":{"candidates":[x for x in consumables["items"]
                                if x["kind"]=="food"],"stage":"DB2_ID_ONLY"},
         "potion":{"candidates":[x for x in consumables["items"]
                                  if x["kind"]=="potion"],"stage":"DB2_ID_ONLY"},
         "flask":{"reference":budget["flasks"],
                   "stage":"CHMV_F_REFERENCE_NOT_ALL_SIMC_VALIDATED"},
         "augmentation_rune":{"stage":"SIMC_DBC_ITEM_MATCH_PENDING"},
         "weapon_oils":{"stage":"SIMC_TEMPORARY_ENCHANT_MATCH_PENDING"},
         "general_gems":{"reference":budget["ordinary_gem"],
                         "stage":"CHMV_J_REFERENCE_NOT_FULL_GEM_CATALOG"},
         "special_diamonds":{"stage":"ITEM_GEM_EFFECT_ID_JOIN_PENDING"}},
      "embellishments":{"registered_effects":
            effects["candidates"]["embellishment_or_darkmoon"],
            "stage":"SIMC_IMPLEMENTED_EFFECT_DISCOVERY_RECIPE_TYPE_AND_SLOT_LINK_PENDING"},
      "enchants":{"current_season_midnight":{"highest_rank_candidates":season_enchants,
                    "count":len(season_enchants),
                    "stage":"SIMC_MIDNIGHT_TOKEN_AND_SLOT_MASK_CANDIDATE_NOT_NATIVE_UI"},
                  "permanent":{"source_rows":generated["permanent_enchant"]["declared_rows"],
                    "highest_rank_candidates":permanent,
                    "stage":"SIMC_ENCHANT_SLOT_MASK_KNOWN_SEASON_EFFECT_UNVERIFIED"},
                  "temporary":{"source_rows":generated["temporary_enchant"]["declared_rows"],
                    "highest_rank_candidates":temporary,
                    "stage":"SIMC_TEMPORARY_EFFECT_SPELL_KNOWN_SEASON_UNVERIFIED"}},
      "gem_properties":{"source_count":generated["gem_property"]["declared_rows"],
                        "stage":"SIMC_ENCHANT_PROPERTIES_NOT_GEM_ITEM_IDS"},
      "pending":["SAME_BUILD_SIMC_COMPILED_DBC_ITEM_AND_EFFECT_LINK",
                 "SOURCE_VERIFIED_HIGHEST_QUALITY_AND_STRONGEST_EQUIVALENT_EFFECT",
                 "SLOT_CONSTRAINED_GEM_ENCHANT_EMBELLISHMENT_VALIDITY",
                 "KOKR_NAMES_AND_TOOLTIPS",
                 "NEW_CHOICES_SELECTED_NATIVE_ONLY",
                 "VERSIONED_UI_CATALOG_AND_SESSION_IDENTITY"],
      "historical_cache_modified":False,
      "no_optimizer_changes":True}
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    for x in ("gear","tier","budget","v189","v190","simc-generated-folder","out"):
        p.add_argument("--"+x,required=True,type=Path)
    p.add_argument("--event",choices=("mid_patch","season_change","expansion_change"),
                   required=True)
    args=p.parse_args(argv)
    inputs={}
    for key in ("gear","tier","budget","v189","v190"):
        inputs[key]=load_json(getattr(args,key))[0]
    src={}
    for key,filename in GENERATED.items():
        src[key]=parse_generated(key,read_small(args.simc_generated_folder/filename))
    out=compile_catalog(inputs["gear"],inputs["tier"],inputs["budget"],
                        inputs["v189"],inputs["v190"],src,event=args.event)
    out["sha256_by_input"]={key:load_json(getattr(args,key))[1]
                             for key in ("gear","tier","budget","v189","v190")}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,sort_keys=True,
                                  ensure_ascii=False)+"\n",encoding="utf8")
    print("V191_UNIFIED",out["status"],"gear",out["gear"]["count"],
          "tier",out["tier"]["piece_count"],"enchant_candidates",
          len(out["enchants"]["permanent"]["highest_rank_candidates"]),
          "NATIVE_0","NO_UI_PROMOTION",flush=True)
    return 0
if __name__=="__main__":raise SystemExit(main())
