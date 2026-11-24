#!/usr/bin/env python3
"""v165: small CURRENT-season candidate catalog, from v163/v162 + same-build Retail DB2 ItemXItemEffect.

No old item seed, SimC process, DPS query, or effect emulation.
Effect presence comes from Retail DB2 ItemXItemEffect; absence only proves
NO_DIRECT_ITEM_EFFECT_RECORD, not absence of bonus-option or SimC effects.
Only WCL-matched raid/current-expansion, explicit M+ display season, accepted
Localbots, and current-expansion crafts are user-list eligible.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter
from pathlib import Path

SCHEMA="v165_current_season_gear_pool_v1"
TRINKET=12
# Exactly the inventory types of class tier pieces (v168).
TIER_INVENTORY_TYPES=frozenset((1,3,5,20,10,7))
MAX_SOURCE_BYTES=5_000_000
MAX_CSV_BYTES=210_000_000
MAX_ROWS=1_000_000
# Separate CHMV accounting facts: one quality-two (highest) example and 4
# top-tier flask item IDs verified from public item pages. Not effect code.
ROOT=Path(__file__).resolve().parents[1]
# Legacy installed-season budget is a compatibility source, never imported
# at module load. Fresh-season Build must supply new J/F evidence or None.
INSTALLED_BUDGET=ROOT/"data/current_season_chmv_consumables.json"
_INSTALLED=object()

class CatalogBlocked(ValueError):pass
def need(test,code):
    if not test:raise CatalogBlocked(code)
def integer(value,default=None):
    try:return int(value)
    except (ValueError,TypeError):return default
def read_json(path):
    p=Path(path)
    need(p.is_file() and 0<p.stat().st_size<=MAX_SOURCE_BYTES,
         "SOURCE_JSON_MISSING_OR_OVERSIZE")
    return json.loads(p.read_text(encoding="utf8"))
def read_csv(path, columns):
    p=Path(path)
    need(p.is_file() and 0<p.stat().st_size<=MAX_CSV_BYTES,
         "DB2_CSV_MISSING_OR_OVERSIZE")
    with p.open(encoding="utf-8-sig",newline="") as source:
        reader=csv.DictReader(source)
        need(set(columns)<=set(reader.fieldnames or ()),"DB2_COLUMNS_MISSING")
        for idx,row in enumerate(reader):
            need(idx<MAX_ROWS,"DB2_ROW_LIMIT")
            yield row
def effects(path,ids):
    if path is None:return None,None
    # RETAIL: ItemXItemEffect(ItemID, ItemEffectID) is the relation.
    # ItemEffect.ParentItemID is Classic-only and cannot classify Retail gear.
    observed=set()
    for row in read_csv(path,("ItemID","ItemEffectID")):
        iid=integer(row["ItemID"])
        if iid in ids and integer(row["ItemEffectID"],0)>0:
            observed.add(iid)
    digest=hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda:source.read(1024*1024),b""):
            digest.update(chunk)
    return observed,digest.hexdigest()
def _budget_source(source,build):
    if source is _INSTALLED:
        source=read_json(INSTALLED_BUDGET)
        mode="INSTALLED_SAME_SEASON_REFERENCE_COMPATIBILITY"
    elif source is None:
        return None,"NEW_SEASON_J_F_BUDGET_EVIDENCE_PENDING"
    else:
        need(type(source) is dict,
             "EXPLICIT_NEW_SEASON_BUDGET_SOURCE_OBJECT_REQUIRED")
        mode="EXPLICIT_SAME_BUILD_NEW_SEASON_BUDGET_CANDIDATE"
    need(source.get("retail_build")==build,
         "CONSUMABLE_BUDGET_BUILD_MISMATCH")
    gem=source.get("ordinary_gem",{})
    flask=source.get("flasks",{})
    need(type(gem) is dict and type(flask) is dict
         and type(gem.get("slots")) is int
         and type(gem.get("highest_quality_bonus")) is list
         and all(type(x) is int and x>=0
                 for x in gem["highest_quality_bonus"])
         and type(gem.get("total_J")) is int
         and gem["slots"]*sum(gem["highest_quality_bonus"])==gem["total_J"]
         and type(flask.get("total_F")) is int
         and flask.get("total_F")==flask.get(
             "single_secondary_highest_quality_rating")
         and type(flask.get("by_stat")) is dict
         and len(flask["by_stat"])==4
         and all(type(x) is dict and x.get("rating")==flask["total_F"]
                 for x in flask["by_stat"].values()),
         "CONSUMABLE_BUDGET_DATA_INCONSISTENT")
    return source,mode


def _journal_origin_current(row, display_season, *, raid):
    """Use actual active raid/M+ provenance, never opaque WSE eligibility.

    v163 has already matched the raid to the active WCL zone and same-build
    journal, and M+ to the active DB2 DisplaySeasonID. Preserve WSE in the
    source record for diagnostics, but do not evaluate, require, or filter it.
    An unscoped M+ source is not proof of current-season membership.
    """
    if type(row) is not dict or type(display_season) is not int or display_season<=0:
        return False
    if row.get("source") != ("raid_journal" if raid else "mplus_journal"):
        return False
    if type(row.get("display_season_id")) is not int:
        return False
    if any(type(row.get(key)) is not int or row[key]<=0
           for key in ("journal_encounter_id","journal_instance_id")):
        return False
    season=row["display_season_id"]
    evidence=row.get("season_evidence")
    # Old sealed v163 reports encoded WSE>0 as UNKNOWN_WORLD_STATE_EXPRESSION.
    # The underlying same-season/raid occurrence remains a valid source.
    # New v163 reports classify DisplaySeasonID regardless of optional WSE.
    if season==display_season:
        return evidence in ("DB2_DISPLAY_SEASON_MATCH",
                            "UNKNOWN_WORLD_STATE_EXPRESSION")
    return (raid and season==0
            and evidence in ("UNKNOWN_UNSCOPED_JOURNAL",
                             "UNKNOWN_WORLD_STATE_EXPRESSION"))


def expand_selectable_source(original, folder, effect_path):
    """Supplement the known raid and craft sources; preserve original v163/G."""
    import copy
    folder=Path(folder)
    raw=(folder/"receipt.json").read_bytes()
    receipt=json.loads(raw)
    need(hashlib.sha256(raw).hexdigest()==original.get("snapshot_receipt_sha256")
         and receipt.get("build")==original["build"]
         and receipt.get("locale")=="enUS","SELECTABLE_SOURCE_SNAPSHOT_DRIFT")
    for table in ("JournalEncounter","JournalEncounterItem","CraftingData",
                  "Item","ItemSparse"):
        path=folder/(table+".csv")
        meta=receipt.get("tables",{}).get(table,{})
        need(path.is_file() and not path.is_symlink() and
             path.stat().st_size==meta.get("bytes") and
             path.stat().st_size<=MAX_CSV_BYTES,
             "SELECTABLE_SOURCE_TABLE_SIZE:"+table)
        h=hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda:stream.read(1024*1024),b""):
                h.update(chunk)
        need(h.hexdigest()==meta.get("sha256"),
             "SELECTABLE_SOURCE_TABLE_SHA:"+table)
    result=copy.deepcopy(original)
    indexed={x["item_id"]:x for x in result["items"]}
    sid=original["db2_display_season_id"]
    instances={src["journal_instance_id"] for row in original["items"]
        for src in row["acquisition_sources"] if src.get("source")=="raid_journal"
        and _journal_origin_current(src,sid,raid=True)}
    encounters={integer(x["ID"]):x for x in read_csv(
        folder/"JournalEncounter.csv",("ID","JournalInstanceID","Name_lang"))
        if integer(x["JournalInstanceID"]) in instances}
    origins={}
    for row in read_csv(folder/"JournalEncounterItem.csv",(
            "ID","JournalEncounterID","ItemID","DisplaySeasonID")):
        eid=integer(row["JournalEncounterID"]);iid=integer(row["ItemID"],0)
        if eid not in encounters or iid<=0 or iid in indexed:continue
        season=integer(row["DisplaySeasonID"])
        if season not in (0,sid):continue
        encounter=encounters[eid]
        origins.setdefault(iid,[]).append({
            "source":"raid_journal","name":encounter["Name_lang"],
            "journal_encounter_id":eid,
            "journal_instance_id":integer(encounter["JournalInstanceID"]),
            "display_season_id":season,
            "world_state_expression_id":integer(row.get("WorldStateExpressionID")),
            "season_evidence":("DB2_DISPLAY_SEASON_MATCH" if season==sid
                               else "UNKNOWN_UNSCOPED_JOURNAL")})
    for row in read_csv(folder/"CraftingData.csv",("ID","CraftedItemID")):
        iid=integer(row["CraftedItemID"],0)
        if iid>0 and iid not in indexed:
            origins.setdefault(iid,[]).append({
                "source":"crafted_fixed_gear",
                "expansion_id":original["db2_expansion_id"],
                "classification":"SAME_EXPANSION_CRAFTED_PHYSICAL_CANDIDATE"})
    ids=set(origins)
    item={integer(x["ID"]):x for x in read_csv(
        folder/"Item.csv",("ID","ClassID","InventoryType"))
        if integer(x["ID"]) in ids}
    equipment={i for i,x in item.items() if integer(x["ClassID"]) in (2,4)}
    wanted=equipment|(ids-set(item))
    sparse={integer(x["ID"]):x for x in read_csv(folder/"ItemSparse.csv",
        ("ID","Display_lang","InventoryType","ExpansionID"))
        if integer(x["ID"]) in wanted}
    linked,_=effects(effect_path,equipment)
    pending=[];added=[];indirect_review=[]
    for iid in sorted(wanted):
        src=origins[iid]
        it=item.get(iid);sp=sparse.get(iid)
        if it is None or sp is None:
            pending.append({"item_id":iid,"reason":"ITEM_OR_ITEMSPARSE_MISSING",
                            "source_kinds":sorted({x["source"] for x in src})})
            continue
        slot=integer(it["InventoryType"],0)
        if slot<=0 or slot!=integer(sp["InventoryType"]):
            pending.append({"item_id":iid,"reason":"EQUIPMENT_SLOT_UNRESOLVED"})
            continue
        if integer(sp["ExpansionID"])!=original["db2_expansion_id"]:continue
        if slot!=TRINKET and iid not in linked:
            # Preserve the source-scoped ID for bonus-effect discovery.
            # It is not an ordinary representative or a public choice.
            indirect_review.append(iid)
            continue
        unique={json.dumps(x,sort_keys=True):x for x in src}
        added.append({"item_id":iid,"name":sp["Display_lang"],"slot":slot,
                      "acquisition_sources":[unique[k] for k in sorted(unique)]})
    result["items"]=sorted([*result["items"],*added],key=lambda x:x["item_id"])
    result["selectable_source_extension"]={
        "source_basis":"PINNED_MATCHED_RAID_INSTANCES_AND_CRAFTINGDATA",
        "additional_candidate_ids":[x["item_id"] for x in added],
        "indirect_review_item_ids":indirect_review,
        "unresolved_join_rows":pending,
        "ordinary_G_candidates_added":False,
        "full_season_completeness_confirmed":False}
    return result


def compile_pool(db2,delve,sparse_path,effect_path=None,*,budget_source=_INSTALLED,
                 delve_selectable_only=False):
    need(db2.get("schema")=="v163_zero_seed_db2_join_v1"
         and db2.get("source_provider")=="WAGO_TOOLS_PINNED_DB2_WCL_LIVE",
         "SOURCE_DB2_REPORT_INVALID")
    # Localbots is supplementary. An authenticated v163 raid/M+ source
    # must remain usable when Localbots is unavailable on a fresh install.
    # No synthetic Localbots receipt or old-season seed may be substituted.
    need(type(db2.get("db2_expansion_id")) is int,
         "SEASON_BUILD_EXPANSION_MISMATCH")
    if delve is None:
        delve_rows=[]
        delve_status="OPTIONAL_SOURCE_NOT_COLLECTED"
    else:
        need(delve.get("schema")=="v162_localbots_delve_source_v1"
             and delve.get("source_provider")=="Localbots / balovich-matje/localbots",
             "SOURCE_LOCALBOTS_REPORT_INVALID")
        need(db2.get("build")==delve.get("db2_build")
             and db2.get("db2_expansion_id")==delve.get("db2_expansion_id"),
             "SEASON_BUILD_EXPANSION_MISMATCH")
        delve_rows=delve.get("items")
        delve_status="SAME_BUILD_SUPPLEMENTARY_SOURCE"
    budget, budget_mode=_budget_source(budget_source,db2["build"])
    originals={}
    for src,rows in (("wago",db2.get("items")),("localbots",delve_rows)):
        need(type(rows) is list and len(rows)<=30000,"SOURCE_ROWS_INVALID")
        seen=set()
        for row in rows:
            iid=row.get("item_id")
            need(type(iid) is int and iid>0 and iid not in seen,"SOURCE_DUPLICATE_OR_INVALID_ID")
            seen.add(iid)
            record=originals.setdefault(iid,{"item_id":iid,"sources":[]})
            if src=="wago":
                need(type(row.get("slot")) is int and
                     type(row.get("acquisition_sources")) is list,
                     "DB2_ITEM_FIELDS_INVALID")
                record["sources"].extend(row["acquisition_sources"])
                record["item_slot"]=row["slot"]
                record["name"]=row["name"]
            else:
                need(type(row.get("inventory_type")) is int,
                     "LOCALBOTS_ITEM_FIELDS_INVALID")
                record["sources"].append({"source":"localbots_delve_pool",
                    "season_evidence":"TRUSTED_SOURCE_ITEMSPARSE_ID",
                    "resolution":row["resolution"]})
                record["item_slot"]=row["inventory_type"]
                record["name"]=row["name"]
    ids=set(originals);sparse={}
    for row in read_csv(sparse_path,("ID","Display_lang","InventoryType",
                                      "ExpansionID","ItemSet","OverallQualityID")):
        iid=integer(row["ID"])
        if iid in ids:
            need(iid not in sparse,"SPARSE_DUPLICATE_ID")
            sparse[iid]={"name":row["Display_lang"],
              "slot":integer(row["InventoryType"]),"expansion":integer(row["ExpansionID"]),
              "set_id":integer(row["ItemSet"],0),
              "quality":integer(row["OverallQualityID"])}
    need(ids<=set(sparse),"ITEMSPARSE_ID_MISSING")
    linked,fx_sha=effects(effect_path,ids)
    output=[]
    pending_public=[]
    for iid,row in sorted(originals.items()):
        meta=sparse[iid]
        need(meta["slot"]==row["item_slot"] and
             meta["slot"] is not None and meta["slot"]>0,
             "SLOT_MISMATCH_OR_NOT_EQUIPMENT")
        source_names={x["source"] for x in row["sources"]}
        craft="selectable_stat_craft" in source_names
        fixed_craft="crafted_fixed_gear" in source_names
        raid=any(_journal_origin_current(
                 x,db2["db2_display_season_id"],raid=True)
                 for x in row["sources"])
        delve_ok="localbots_delve_pool" in source_names
        mplus_ok=any(_journal_origin_current(
                     x,db2["db2_display_season_id"],raid=False)
                     for x in row["sources"])
        direct=(iid in linked) if linked is not None else None
        if meta["slot"]==TRINKET:role="trinket"
        elif craft:role="selectable_stat_craft"
        # Non-tier inventory types cannot be one of v168's five class
        # pieces. A set ID alone must not hide their direct item effects.
        elif meta["set_id"]>0 and (
                meta["slot"] in TIER_INVENTORY_TYPES or direct is not True):
            role="set_piece_unclassified"
        elif direct is True:role="special_effect_gear_candidate"
        elif direct is False:role="plain_representative_candidate"
        else:role="effect_classification_pending"
        # Active-season M+ can rotate in older expansion instances. A
        # verified current DisplaySeasonID + Journal occurrence is the
        # user-facing item membership proof, not the item's original era.
        # Scope this change to requested selectable loot; keep internal
        # representative equipment and crafting/tier policy unchanged.
        public_loot=role in ("trinket","special_effect_gear_candidate")
        # Supplemental Delve loot must not change ordinary G composition.
        if (delve_selectable_only and source_names=={"localbots_delve_pool"}
                and not public_loot):
            if direct is True and role=="set_piece_unclassified":
                pending_public.append({"item_id":iid,
                    "reason":"DIRECT_EFFECT_SET_ROLE_UNRESOLVED"})
            continue
        season_eligible=((meta["expansion"]==db2["db2_expansion_id"] and
                         (craft or raid or mplus_ok or
                          (fixed_craft and public_loot) or
                          (delve_ok and (not delve_selectable_only or public_loot))))
                         or (mplus_ok and role in
                             ("trinket","special_effect_gear_candidate")))
        # No hidden effect mechanism certification; exact SimC item variant
        # remains authoritative when this candidate is used in a session.
        item={"item_id":iid,"name":meta["name"],
              "inventory_type":meta["slot"],"expansion_id":meta["expansion"],
              "item_set_id":meta["set_id"],"quality":meta["quality"],
              "category":role,"direct_item_effect_record":direct,
              "season_selection":"CURRENT_CANDIDATE" if season_eligible else
                 "CONDITIONAL_SEASON_NOT_ESTABLISHED",
              "user_selectable_candidate":season_eligible and role not in
                ("effect_classification_pending","set_piece_unclassified"),
              "acquisition_sources":row["sources"]}
        output.append(item)
        if public_loot and not season_eligible:
            pending_public.append({"item_id":iid,
                "reason":"SEASON_MEMBERSHIP_UNRESOLVED"})
        elif direct is True and role=="set_piece_unclassified":
            pending_public.append({"item_id":iid,
                "reason":"DIRECT_EFFECT_SET_ROLE_UNRESOLVED"})
    count=Counter(x["category"] for x in output)
    selection=Counter(x["season_selection"] for x in output)
    return {"schema":SCHEMA,"status":("EFFECT_TABLE_OBSERVED_CANDIDATES"
                         if linked is not None else "EFFECT_TABLE_PENDING"),
       "build":db2["build"],"expansion_id":db2["db2_expansion_id"],
       "db2_display_season_id":db2["db2_display_season_id"],
       "items":output,"item_count":len(output),
       "counts_by_category":dict(sorted(count.items())),
       "counts_by_season_status":dict(sorted(selection.items())),
       "item_x_item_effect_csv_sha256":fx_sha,
       "effect_classification_meaning":"RETAIL_ITEMXITEMEFFECT_RELATION_ONLY_NOT_SIMC_PROC_CERTIFICATION",
       "supplementary_localbots_status":delve_status,
       # Diagnostics from the same scan, not a completeness gate.
       "selectable_loot_coverage":{
           "known_source_item_count":len(originals),
           "current_trinket_count":sum(x["category"]=="trinket" and
               x["user_selectable_candidate"] for x in output),
           "current_direct_special_count":sum(
               x["category"]=="special_effect_gear_candidate" and
               x["user_selectable_candidate"] for x in output),
           "pending_known_ids":pending_public,
           "delve_unresolved_count":(
               delve.get("unresolved_count") if delve is not None else None),
           "indirect_effect_routes_reviewed":False,
           "full_season_completeness_confirmed":False},
       "usable_four_piece_roster_certified":False,
       "fully_implemented_special_item_list_certified":False,
       "full_season_completeness_confirmed":False,
       "consumable_budget_reference":budget,
        "consumable_budget_source_mode":budget_mode,
        "G":None,"B":None,"T":None,
       "no_legacy_catalog_seed":True,"new_native_calls":0}
def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--db2",type=Path,required=True)
    p.add_argument("--delve",type=Path,required=True)
    p.add_argument("--item-sparse",type=Path,required=True)
    p.add_argument("--item-effect",type=Path)
    sources=p.add_mutually_exclusive_group()
    sources.add_argument("--budget-source",type=Path,
                         help="Explicit same-build newly collected J/F source file")
    sources.add_argument("--fresh-source-only",action="store_true",
                         help="Discover gear with J/F unknown; NEVER read installed budget")
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args(argv)
    try:
        budget=(None if a.fresh_source_only else
                read_json(a.budget_source) if a.budget_source else _INSTALLED)
        result=compile_pool(read_json(a.db2),read_json(a.delve),
                            a.item_sparse,a.item_effect,budget_source=budget)
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,
                                   separators=(",",":"))+"\n",encoding="utf8")
        print(json.dumps({"status":result["status"],
            "item_count":result["item_count"],"roles":result["counts_by_category"],
            "native":0},sort_keys=True))
        return 0
    except (CatalogBlocked,KeyError,TypeError,ValueError,OSError) as e:
        print(json.dumps({"status":"BLOCKED","code":str(e) if isinstance(e,CatalogBlocked)
                          else type(e).__name__}))
        return 3
if __name__=="__main__":raise SystemExit(main())
