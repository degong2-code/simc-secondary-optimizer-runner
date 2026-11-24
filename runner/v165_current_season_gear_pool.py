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
# Same physical inventory types supported by the selected-special runtime.
SPECIAL_INVENTORY_TYPES=frozenset((1,2,3,5,6,7,8,9,10,11,13,14,15,16,17,20,23,26))
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


ROTATION_TRINKET_EVIDENCE="DB2_ACTIVE_ROTATION_UNSCOPED_TRINKET"
ROTATION_SPECIAL_EVIDENCE="DB2_ACTIVE_ROTATION_UNSCOPED_DIRECT_SPECIAL"

def _rotation_origin_current(row, display_season, evidence):
    """Only the derived, pinned active rotation may certify unscoped loot.
    
    The raw item DisplaySeasonID remains zero. Do not reinterpret arbitrary
    season-0 rows or allow these role-scoped relations into ordinary G.
    """
    return (type(row) is dict and type(display_season) is int
            and display_season>0 and row.get("source")=="mplus_journal"
            and type(row.get("display_season_id")) is int
            and row["display_season_id"]==0
            and row.get("season_evidence")==evidence
            and type(row.get("active_rotation_display_season_id")) is int
            and row["active_rotation_display_season_id"]==display_season
            and all(type(row.get(k)) is int and row[k]>0 for k in
                ("journal_encounter_id","journal_instance_id","challenge_mode_id")))


def _rotation_trinket_origin_current(row, display_season):
    return _rotation_origin_current(row,display_season,ROTATION_TRINKET_EVIDENCE)


def _rotation_special_origin_current(row, display_season):
    return _rotation_origin_current(row,display_season,ROTATION_SPECIAL_EVIDENCE)


def expand_selectable_source(original, folder, effect_path, *, wcl_report=None):
    """Supplement only authenticated seasonal sources; preserve original v163/G."""
    import copy
    import v163_zero_seed_db2_join as join
    from collections import defaultdict
    folder=Path(folder)
    raw=(folder/"receipt.json").read_bytes()
    receipt=json.loads(raw)
    need(hashlib.sha256(raw).hexdigest()==original.get("snapshot_receipt_sha256")
         and receipt.get("build")==original["build"]
         and receipt.get("locale")=="enUS","SELECTABLE_SOURCE_SNAPSHOT_DRIFT")
    # Old minimal fixture/exports do not assert a full rotation. Actual
    # authenticated v163 reports always carry the exact auto_source_scope.
    rotation=bool(original.get("auto_source_scope"))
    tables=["JournalEncounter","JournalEncounterItem","CraftingData",
            "Item","ItemSparse"]
    if rotation:tables+=["JournalInstance","MapChallengeMode","MythicPlusSeasonTrackedMap"]
    for table in tables:
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
    journal=list(read_csv(folder/"JournalEncounter.csv",
                          ("ID","JournalInstanceID","Name_lang")))
    encounters={integer(x["ID"]):x for x in journal}
    # Resolve every active challenge from the exact previously authenticated
    # DisplaySeasonID. Prefer existing WCL/DB2 match, then unique map ID;
    # name mismatch alone must not erase a dungeon.
    dungeon_by_instance={}
    dungeon_rows={}
    if rotation:
        active={integer(x["MapChallengeModeID"]) for x in read_csv(
            folder/"MythicPlusSeasonTrackedMap.csv",("DisplaySeasonID","MapChallengeModeID"))
            if join.exact_display_season_id(x["DisplaySeasonID"])==sid}
        modes={integer(x["ID"]):x for x in read_csv(folder/"MapChallengeMode.csv",
            ("ID","Name_lang","MapID")) if integer(x["ID"]) in active}
        instance_rows=list(read_csv(folder/"JournalInstance.csv",
                                    ("ID","MapID","Name_lang")))
        prior=defaultdict(set)
        for row in original["items"]:
            for origin in row["acquisition_sources"]:
                if origin.get("source")=="mplus_journal":
                    prior[origin.get("challenge_mode_id")].add(origin["journal_instance_id"])
        for cid in sorted(active):
            mode=modes.get(cid)
            report={"challenge_mode_id":cid,"name":mode["Name_lang"] if mode else None,
                    "journal_instance_id":None,"status":"DUNGEON_JOURNAL_UNRESOLVED",
                    "current_trinket_ids":[],"unscoped_trinket_ids":[],
                    "other_season_trinket_ids":[],"unresolved_loot_ids":[],
                    "rotation_unscoped_admitted_trinket_ids":[],
                    "unscoped_direct_special_ids":[],
                    "rotation_unscoped_admitted_special_ids":[]}
            dungeon_rows[cid]=report
            if mode is None:continue
            options=[x for x in instance_rows if integer(x["MapID"])==
                     integer(mode["MapID"])]
            exact=[x for x in options if integer(x["ID"]) in prior[cid]]
            if len(exact)!=1:
                exact=[x for x in options if join.norm(x["Name_lang"])==
                       join.norm(mode["Name_lang"])]
            chosen=(exact[0] if len(exact)==1 else
                    options[0] if len(options)==1 else None)
            if chosen is None:continue
            instance=integer(chosen["ID"])
            if instance in dungeon_by_instance:
                previous=dungeon_by_instance.pop(instance)
                dungeon_rows[previous]["status"]="DUNGEON_SHARED_INSTANCE_UNRESOLVED"
                dungeon_rows[previous]["journal_instance_id"]=None
                report["status"]="DUNGEON_SHARED_INSTANCE_UNRESOLVED"
                continue
            dungeon_by_instance[instance]=cid
            report.update(journal_instance_id=instance,status="DUNGEON_JOURNAL_OBSERVED")
    # Supplement only exact WCL-registered bosses from other active zones
    # in the same WCL expansion. A non-frozen zone alone is not season proof.
    # No field boss enumeration or sibling encounter expansion.
    registered={}
    unmatched=[]
    if wcl_report is not None:
        scope=original.get("auto_source_scope") or {}
        zone_ids=original.get("wcl_zone_ids") or {}
        zones=join.wcl_zone_sources(wcl_report)
        exp=scope.get("wcl_expansion_id")
        if type(exp) is int:
            for zone in zones:
                if (zone.get("wcl_frozen") is not False or
                    zone.get("expansion_id")!=exp or
                    zone.get("zone_id") in zone_ids.values()):continue
                for boss in zone.get("encounters",[]):
                    match=join.uniquely_match(boss["name"],journal,"Name_lang")
                    if match is None:
                        unmatched.append({"zone_id":zone["zone_id"],"name":boss["name"]})
                        continue
                    eid=integer(match["ID"])
                    instance=integer(match["JournalInstanceID"])
                    if instance in instances or instance in dungeon_by_instance:continue
                    registered[eid]={"wcl_zone_id":zone["zone_id"],
                                     "wcl_boss_name":boss["name"]}
    origins={}
    dungeon_loot=defaultdict(set)
    unscoped_origins=defaultdict(list)
    world_pending=[]
    registered_unscoped=defaultdict(list)
    registered_seasons=defaultdict(set)
    for row in read_csv(folder/"JournalEncounterItem.csv",(
            "ID","JournalEncounterID","ItemID","DisplaySeasonID")):
        eid=integer(row["JournalEncounterID"]);iid=integer(row["ItemID"],0)
        encounter=encounters.get(eid)
        if encounter is None or iid<=0:continue
        instance=integer(encounter["JournalInstanceID"])
        cid=dungeon_by_instance.get(instance)
        if instance not in instances and cid is None and eid not in registered:continue
        season=join.exact_display_season_id(row["DisplaySeasonID"])
        base={"name":encounter["Name_lang"],"journal_encounter_id":eid,
            "journal_instance_id":instance,"display_season_id":season,
            "world_state_expression_id":join.exact_world_state_expression_id(
                row.get("WorldStateExpressionID")),
            "season_evidence":join.classify_era(season,None,sid)}
        if cid is not None:
            dungeon_loot[iid].add((cid,season))
            if season==sid:
                origins.setdefault(iid,[]).append({
                    **base,"source":"mplus_journal","challenge_mode_id":cid})
            elif season==0:
                unscoped_origins[iid].append({
                    **base,"source":"mplus_journal","challenge_mode_id":cid})
        if instance in instances and iid not in indexed and season in (0,sid):
            origins.setdefault(iid,[]).append({**base,"source":"raid_journal"})
        if eid in registered:
            registered_seasons[(eid,iid)].add(season)
            if season==sid:
                origins.setdefault(iid,[]).append({
                    **base,"source":"raid_journal",**registered[eid]})
            elif season==0:
                world_pending.append({"item_id":iid,"journal_encounter_id":eid})
                registered_unscoped[iid].append({
                    **base,"source":"raid_journal",**registered[eid]})

    for row in read_csv(folder/"CraftingData.csv",("ID","CraftedItemID")):
        iid=integer(row["CraftedItemID"],0)
        if iid>0 and iid not in indexed:
            origins.setdefault(iid,[]).append({
                "source":"crafted_fixed_gear",
                "expansion_id":original["db2_expansion_id"],
                "classification":"SAME_EXPANSION_CRAFTED_PHYSICAL_CANDIDATE"})
    ids=set(origins)|set(dungeon_loot)|set(registered_unscoped)
    item={integer(x["ID"]):x for x in read_csv(
        folder/"Item.csv",("ID","ClassID","InventoryType"))
        if integer(x["ID"]) in ids}
    equipment={i for i,x in item.items() if integer(x["ClassID"]) in (2,4)}
    wanted=equipment|(ids-set(item))
    sparse={integer(x["ID"]):x for x in read_csv(folder/"ItemSparse.csv",
        ("ID","Display_lang","InventoryType","ExpansionID"))
        if integer(x["ID"]) in wanted}
    linked,_=effects(effect_path,equipment)
    pending=[];added=[];indirect_review=[];effect_review_rows=[]
    for iid in sorted(wanted):
        src=origins.get(iid,[])
        it=item.get(iid);sp=sparse.get(iid)
        if it is None or sp is None:
            for cid,_ in dungeon_loot.get(iid,()):
                dungeon_rows[cid]["unresolved_loot_ids"].append(iid)
            pending.append({"item_id":iid,"reason":"ITEM_OR_ITEMSPARSE_MISSING",
                            "source_kinds":sorted({x["source"] for x in src})})
            continue
        slot=integer(it["InventoryType"],0)
        if slot<=0 or slot!=integer(sp["InventoryType"]):
            for cid,_ in dungeon_loot.get(iid,()):
                dungeon_rows[cid]["unresolved_loot_ids"].append(iid)
            pending.append({"item_id":iid,"reason":"EQUIPMENT_SLOT_UNRESOLVED"})
            continue
        if slot==TRINKET:
            for cid,season in dungeon_loot.get(iid,()):
                key=("current_trinket_ids" if season==sid else
                     "unscoped_trinket_ids" if season==0 else "other_season_trinket_ids")
                dungeon_rows[cid][key].append(iid)
        if slot==TRINKET:
            # The authenticated rotation, exact map/instance/encounter and
            # physical trinket slot establish candidate membership. Season
            # 0 is unscoped, not "old season". Explicit other-season-only
            # occurrences stay withheld, including contradictory zero rows.
            for origin in unscoped_origins.get(iid,()):
                cid=origin["challenge_mode_id"]
                seasons={s for c,s in dungeon_loot[iid] if c==cid}
                if any(s not in (0,sid) for s in seasons) and sid not in seasons:
                    continue
                src.append({**origin,"season_evidence":ROTATION_TRINKET_EVIDENCE,
                    "active_rotation_display_season_id":sid})
                dungeon_rows[cid]["rotation_unscoped_admitted_trinket_ids"].append(iid)
        # Same exact active rotation proof, but only direct-effect physical
        # special equipment. No ordinary gear, ambiguous class tier, recipe
        # or unsupported inventory type enters the public special source.
        if (slot in SPECIAL_INVENTORY_TYPES and iid in linked
                and not (integer(sp.get("ItemSet"),0)>0 and
                         slot in TIER_INVENTORY_TYPES)):
            for origin in unscoped_origins.get(iid,()):
                cid=origin["challenge_mode_id"]
                dungeon_rows[cid]["unscoped_direct_special_ids"].append(iid)
                seasons={s for c,s in dungeon_loot[iid] if c==cid}
                if any(s not in (0,sid) for s in seasons) and sid not in seasons:
                    continue
                src.append({**origin,"season_evidence":ROTATION_SPECIAL_EVIDENCE,
                    "active_rotation_display_season_id":sid})
                dungeon_rows[cid]["rotation_unscoped_admitted_special_ids"].append(iid)
        # Discovery must not depend on direct effects or explicit item
        # DisplaySeasonID. Preserve scoped zero-season occurrences separately
        # from admission. This cannot add a representative G candidate or
        # promote unverified variants. Explicit other-season conflicts are
        # retained as pending reasons, never treated as current eligibility.
        if slot in SPECIAL_INVENTORY_TYPES:
            review_origins=list(src)
            conflicts=[]
            for origin in unscoped_origins.get(iid,()):
                cid=origin["challenge_mode_id"]
                seasons={s for c,s in dungeon_loot[iid] if c==cid}
                if any(s not in (0,sid) for s in seasons) and sid not in seasons:
                    conflicts.append(origin)
                else:
                    review_origins.append(origin)
            for origin in registered_unscoped.get(iid,()):
                seasons=registered_seasons[(origin["journal_encounter_id"],iid)]
                if any(s not in (0,sid) for s in seasons) and sid not in seasons:
                    conflicts.append(origin)
                else:
                    review_origins.append(origin)
            in_scope=(integer(sp["ExpansionID"])==original["db2_expansion_id"]
                      or any(x["source"]=="mplus_journal" for x in review_origins))
            if in_scope and (review_origins or conflicts):
                if iid not in linked and review_origins:
                    indirect_review.append(iid)
                # Preserve only missing/ambiguous public candidates, not an
                # extra full ordinary catalog. Exact origins are needed later.
                if iid not in linked or not src or conflicts:
                    unique={json.dumps(x,sort_keys=True):x for x in review_origins}
                    effect_review_rows.append({
                        "item_id":iid,"name":sp["Display_lang"],"slot":slot,
                        "direct_item_effect_record":iid in linked,
                        "acquisition_sources":[unique[k] for k in sorted(unique)],
                        "conflicting_source_occurrences":conflicts,
                        "variant_applicability_verified":False,
                        "source_review_only":True})
        if not src:continue
        is_current_mplus=any(x["source"]=="mplus_journal" for x in src)
        if (integer(sp["ExpansionID"])!=original["db2_expansion_id"]
                and not is_current_mplus):continue
        if slot!=TRINKET and iid not in linked:
            continue
        # Update existing public IDs only, never add new representative G.
        old=indexed.get(iid)
        if old is not None:
            known={(x.get("source"),x.get("journal_encounter_id"),
                    x.get("display_season_id"),x.get("challenge_mode_id"),
                    x.get("season_evidence"))
                   for x in old["acquisition_sources"]}
            for origin in src:
                key=(origin.get("source"),origin.get("journal_encounter_id"),
                     origin.get("display_season_id"),origin.get("challenge_mode_id"),
                     origin.get("season_evidence"))
                if key not in known:
                    old["acquisition_sources"].append(origin);known.add(key)
            continue
        unique={json.dumps(x,sort_keys=True):x for x in src}
        added.append({"item_id":iid,"name":sp["Display_lang"],"slot":slot,
                      "acquisition_sources":[unique[k] for k in sorted(unique)]})
    for report in dungeon_rows.values():
        for key in ("current_trinket_ids","unscoped_trinket_ids",
                    "other_season_trinket_ids","unresolved_loot_ids",
                    "rotation_unscoped_admitted_trinket_ids",
                    "unscoped_direct_special_ids",
                    "rotation_unscoped_admitted_special_ids"):
            report[key]=sorted(set(report[key]))
    result["items"]=sorted([*result["items"],*added],key=lambda x:x["item_id"])
    result["selectable_source_extension"]={
        "source_basis":"PINNED_MATCHED_RAID_INSTANCES_AND_CRAFTINGDATA",
        "additional_candidate_ids":[x["item_id"] for x in added],
        "indirect_review_item_ids":sorted(set(indirect_review)),
        "effect_review_rows":effect_review_rows,
        "effect_review_is_source_only":True,
        "unresolved_join_rows":pending,
        "mplus_dungeon_review":list(dungeon_rows.values()),
        "mplus_rotation_reviewed":rotation,
        "supplementary_wcl_boss_review":{
            "status":"WCL_REGISTERED_ONLY" if wcl_report is not None else "WCL_SOURCE_NOT_AVAILABLE",
            "registered_extra_encounters":len(registered),
            "unmatched_registered_bosses":unmatched,
            "unscoped_loot_pending":world_pending,
            "unregistered_field_boss_search":False},
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
                     or (meta["slot"]==TRINKET and
                         _rotation_trinket_origin_current(x,db2["db2_display_season_id"]))
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
        if role=="special_effect_gear_candidate" and meta["slot"] in SPECIAL_INVENTORY_TYPES:
            mplus_ok=mplus_ok or any(_rotation_special_origin_current(
                x,db2["db2_display_season_id"]) for x in row["sources"])
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
