#!/usr/bin/env python3
"""Source-identity bridge: DB2 observed tier cohort -> first-party SimC set option.

No publisher tier-name lookup, hardcoded season/set IDs or duplicate item DB.
The current raid's observed leading cohort remains a CANDIDATE.  The bridge
only prepares 13x5 physical IDs + optional one-spec exact SimC item-set check
for the existing v231 -> v232 preview pathway; it cannot activate production.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

try:
    from . import v143_specialization_contracts as specs
    from . import v168_current_season_tier_discovery as physical
    from . import v231_simc_tier_item_join as simc_tier
    from . import v217_stage_execution_engine as stages
except ImportError:
    import v143_specialization_contracts as specs
    import v168_current_season_tier_discovery as physical
    import v231_simc_tier_item_join as simc_tier
    import v217_stage_execution_engine as stages

SCHEMA="v251_db2_raid_tier_to_simc_source_candidate_bridge_v1"
SLOTS=("head","shoulders","chest","hands","legs")
FOUR=("head","shoulders","hands","legs")
MAX_JSON=4_000_000

class BridgeBlocked(ValueError):pass

def need(ok,code):
    if not ok:raise BridgeBlocked(code)

def digest(raw):return hashlib.sha256(raw).hexdigest()

def raw_report(path):
    p=Path(path)
    need(p.is_file() and not p.is_symlink()
         and 0<p.stat().st_size<=MAX_JSON,
         "V251_SOURCE_REPORT_MISSING_OR_UNSAFE")
    raw=p.read_bytes()
    need(0<len(raw)<=MAX_JSON,"V251_SOURCE_CHANGED_WHILE_READING")
    return raw

def load(path):
    return json.loads(raw_report(path))

def preview(*,db2,corroboration):
    need(db2.get("schema")=="v245_db2_first_class_tier_candidates_v1"
         and db2.get("current_season_selection") is None
         and db2.get("source_season_verified") is False
         and db2.get("environment_ready") is False
         and db2.get("native_calls")==0
         and type(db2.get("candidates")) is list,
         "V251_DB2_PENDING_CANDIDATES_REQUIRED")
    need(corroboration.get("schema")==
             "v250_active_raid_bonus_tier_corroboration_v1"
         and corroboration.get("status")==
             "UNIQUE_RAID_BONUS_CORRELATED_TIER_COHORT_SEASON_PENDING"
         and corroboration.get("game_build")==db2.get("game_build")
         and corroboration.get("observed_leading_cohort_is_certified_current_season")
             is False
         and corroboration.get("source_season_verified") is False
         and corroboration.get("environment_ready") is False
         and corroboration.get("native_calls")==0,
         "V251_UNPROMOTED_SAME_BUILD_CORROBORATION_REQUIRED")
    lead=corroboration.get("observed_leading_cohort")
    need(type(lead) is dict and
         lead in corroboration.get("cohort_comparisons",[]) and
         lead.get("uniform_65_item_bonus_fingerprint") is True and
         lead.get("raid_loot_overlap_item_count",0)>0 and
         lead.get("physical_items")==65 and
         lead.get("source_season_verified") is False,
         "V251_UNIQUE_OBSERVED_RAID_COHORT_REQUIRED")
    groups=lead.get("item_set_ids_by_class")
    need(type(groups) is dict and set(groups)==set(physical.FAMILY)
         and all(type(v) is list and len(v)==1 and
                 type(v[0]) is int and v[0]>0 for v in groups.values()),
         "V251_13_CLASS_SET_ROSTER_REQUIRED")
    matches=corroboration.get("cohort_comparisons",[])
    need(sum(x.get("raid_loot_overlap_item_count",0)>=
             lead["raid_loot_overlap_item_count"] for x in matches)==1,
         "V251_RAID_CORROBORATION_NOT_UNIQUELY_LEADING")
    candidates={x["item_set_id"]:x for x in db2["candidates"]}
    need(len(candidates)==len(db2["candidates"]),
         "V251_DUPLICATE_ITEMSET_CANDIDATES")
    classes={}
    all_ids=set()
    for cls,ids in sorted(groups.items()):
        item=candidates.get(ids[0])
        need(type(item) is dict and item.get("class")==cls
             and item.get("observed_expansion_id")==
                 lead["observed_expansion_id"]
             and item.get("observed_base_item_level_min")==
                 lead["observed_base_item_level"]
             and item.get("observed_base_item_level_max")==
                 lead["observed_base_item_level"]
             and item.get("base_item_level_evidence")==
                 "SOURCE_OBSERVED_ALL_FIVE"
             and item.get("season_membership_verified") is False
             and set(item.get("tier_piece_ids",{}))==set(SLOTS)
             and set(item.get("spec_bonus_spells",{})),
             "V251_DB2_SOURCE_SET_CLASS_SLOT_OR_ILVL_DRIFT")
        slots=item["tier_piece_ids"]
        need(all(type(slots[s]) is int and slots[s]>0 for s in SLOTS)
             and len(set(slots.values()))==5,
             "V251_NOT_FIVE_DISTINCT_PHYSICAL_ITEMS")
        need(not (all_ids&set(slots.values())),
             "V251_PHYSICAL_ITEM_SHARED_BETWEEN_CLASSES")
        all_ids.update(slots.values())
        classes[cls]={
            "item_set_id":ids[0],
            "observed_base_item_level":lead["observed_base_item_level"],
            "tier_piece_ids":{s:slots[s] for s in SLOTS},
            "four_piece_slots":list(FOUR),
            "simc_set_option":None,
            "simc_source_verified":False,
            "season_membership_verified":False}
    need(len(classes)==13 and len(all_ids)==65,
         "V251_13X5_ROSTER_INCOMPLETE")
    return {
        "schema":SCHEMA,
        "status":"OBSERVED_CURRENT_RAID_CORRELATED_65_PIECE_TIER_CANDIDATE",
        "game_build":db2["game_build"],
        "expansion_id":lead["observed_expansion_id"],
        "observed_base_item_level":lead["observed_base_item_level"],
        "observed_raid_bonus_group_ids":lead["bonus_list_group_ids"],
        "raid_bonus_overlap_count":lead["raid_loot_overlap_item_count"],
        "class_count":len(classes),"piece_count":len(all_ids),
        "classes":classes,
        "source_identity":{"db2_candidate_schema":db2["schema"],
                           "bonus_relation_schema":corroboration["schema"],
                           "source_only":True},
        "used_tier_name_matching":False,
        "used_previous_season_item_id_seed":False,
        "season_membership_verified":False,
        "simc_source_verified":False,
        "production_profile_promoted":False,
        "G":None,"J":None,"F":None,"O":None,"B":None,"T":None,
        "environment_ready":False,"native_calls":0,"network_calls":0}

def select_for_simc(*,candidate,seed_directory,cls,spec):
    """Only an EXACT 5-item/class/ItemSet match may discover set_option.

    Then delegate the authoritative physical SimC item validation to existing
    v231.select, once for the requested DPS specialization. This neither
    imports another season roster nor chooses an option by its text/name.
    """
    need(type(candidate) is dict and candidate.get("schema")==SCHEMA
         and candidate.get("status")==
             "OBSERVED_CURRENT_RAID_CORRELATED_65_PIECE_TIER_CANDIDATE"
         and candidate.get("class_count")==13
         and candidate.get("piece_count")==65
         and candidate.get("season_membership_verified") is False
         and candidate.get("production_profile_promoted") is False
         and candidate.get("environment_ready") is False,
         "V251_UNPROMOTED_CLASS_ROSTER_REQUIRED")
    entry=candidate.get("classes",{}).get(cls)
    need(entry is not None and specs.lookup(cls,spec) is not None,
         "V251_SUPPORTED_26_DPS_SPEC_REQUIRED")
    receipt,source=simc_tier.read_receipt(seed_directory)
    need(receipt["simc_generated_build"]==candidate["game_build"],
         "V251_SAME_BUILD_SIMC_SOURCE_REQUIRED")
    clsid=simc_tier.CLASS_ID[cls]
    itemids=set(entry["tier_piece_ids"].values())
    exact=[g for g in source["candidate_groups"]
           if g["class_id"]==clsid
           and g["set_id"]==entry["item_set_id"]
           and set(g["item_ids"])==itemids
           and g["observed_bonus_sizes"]==[2,4]]
    need(len(exact)==1,
         "V251_SOURCE_ITEMSET_EXACT_ID_OPTION_NOT_UNIQUE_OR_MISSING")
    result=simc_tier.select(seed_directory=seed_directory,
                            cls=cls,spec=spec,set_option=exact[0]["set_opt"])
    need(result["set_id"]==entry["item_set_id"]
         and result["tier_piece_ids"]==entry["tier_piece_ids"]
         and result["game_build"]==candidate["game_build"]
         and result["environment_ready"] is False,
         "V251_SIMC_PHYSICAL_MATCH_CHANGED")
    return {"schema":SCHEMA,
            "status":"EXACT_FIRST_PARTY_SIMC_TIER_MATCH_SEASON_PENDING",
            "class":cls,"spec":spec,
            "simc_set_option_discovered":exact[0]["set_opt"],
            "simc_set_id":result["set_id"],
            "tier_piece_ids":result["tier_piece_ids"],
            "v231_candidate":result,
            "season_membership_verified":False,
            "production_profile_promoted":False,
            "environment_ready":False,"native_calls":0,"network_calls":0}

def match_first_party_roster(*,candidate,simc_receipt,simc_set_groups):
    """One-pass exact 13-class SimC set ID + 65 physical-ID join.

    Caller MUST source simc_receipt and simc_set_groups from v231.read_receipt
    (the pinned v229 source verifier). This pure function is not an independent
    authentication of external dicts. Does not require item_data.inc or Native;
    per-spec physical metadata remains owned by v231.select.
    """
    need(type(candidate) is dict and candidate.get("schema")==SCHEMA
         and candidate.get("status")==
             "OBSERVED_CURRENT_RAID_CORRELATED_65_PIECE_TIER_CANDIDATE"
         and candidate.get("class_count")==13 and
             candidate.get("piece_count")==65
         and candidate.get("season_membership_verified") is False
         and candidate.get("environment_ready") is False
         and candidate.get("production_profile_promoted") is False
         and candidate.get("simc_source_verified") is False
         and candidate.get("used_tier_name_matching") is False
         and set(candidate.get("classes",{}))==set(physical.FAMILY),
         "V251_PHYSICAL_CANDIDATE_SOURCE_REQUIRED")
    need(type(simc_receipt) is dict and
         simc_receipt.get("simc_generated_build")==candidate["game_build"]
         and simc_receipt.get("provenance_tree_blob_authenticated") is True
         and type(simc_receipt.get("receipt_sha256")) is str
         and len(simc_receipt["receipt_sha256"])==64
         and type(simc_set_groups) is dict
         and type(simc_set_groups.get("candidate_groups")) is list,
         "V251_FIRST_PARTY_SIMC_SOURCE_BUILD_OR_RECEIPT_REQUIRED")
    index={}
    for r in simc_set_groups["candidate_groups"]:
        if (type(r.get("class_id")) is not int or
            type(r.get("set_id")) is not int or
            type(r.get("item_ids")) is not list or
            r.get("observed_bonus_sizes")!=[2,4]):
            continue
        key=(r["class_id"],r["set_id"],tuple(sorted(r["item_ids"])))
        index.setdefault(key,[]).append(r["set_opt"])
    rows={}
    options=set()
    for cls,entry in sorted(candidate["classes"].items()):
        ids=entry["tier_piece_ids"]
        need(set(ids)==set(SLOTS) and all(type(x) is int and x>0
             for x in ids.values()) and len(set(ids.values()))==5
             and entry.get("season_membership_verified") is False,
             "V251_SIMC_ROSTER_CLASS_PHYSICAL_INVALID")
        key=(simc_tier.CLASS_ID[cls],entry["item_set_id"],
             tuple(sorted(ids.values())))
        exact=index.get(key,[])
        need(len(exact)==1 and isinstance(exact[0],str)
             and simc_tier.TOKEN.fullmatch(exact[0]),
             "V251_SIMC_13_CLASS_EXACT_SET_OPTION_MISSING_OR_AMBIGUOUS")
        options.add(exact[0])
        rows[cls]={"item_set_id":entry["item_set_id"],
                   "simc_set_option":exact[0],
                   "tier_piece_ids":{k:ids[k] for k in SLOTS},
                   "observed_base_item_level":
                       entry["observed_base_item_level"],
                   "source_set_bonus_sizes":[2,4]}
    need(len(rows)==13 and
         len({x for r in rows.values()
              for x in r["tier_piece_ids"].values()})==65,
         "V251_SIMC_ROSTER_INCOMPLETE")
    return {
        "schema":SCHEMA,
        "status":"EXACT_13_CLASS_SIMC_SET_OPTIONS_MATCHED_SEASON_PENDING",
        "game_build":candidate["game_build"],
        "simc_revision":simc_receipt["simc_revision"],
        "simc_seed_receipt_sha256":simc_receipt["receipt_sha256"],
        "observed_simc_options":sorted(options),
        "class_count":13,"piece_count":65,
        "classes":rows,
        "simc_set_option_verified_by_exact_physical_ids":True,
        "simc_item_data_metadata_fully_verified":False,
        "season_membership_verified":False,
        "production_profile_promoted":False,
        "environment_ready":False,"native_calls":0,
        "G":None,"J":None,"F":None,"O":None,"B":None,"T":None}

def build_first_party_match_stage(*,stage_root,physical_candidate_path,
                                  physical_stage_receipt,seed_directory):
    """Optional stage only when the normal environment owns a v229 seed.

    No source collection/Native. Read the first-party set file once using
    v231 verification, then seal one 13-class exact physical source join.
    """
    root=Path(stage_root)
    need(root.is_dir() and not root.is_symlink(),
         "V251_FIRST_PARTY_STAGE_ROOT_INVALID")
    physical_raw=raw_report(physical_candidate_path)
    candidate=json.loads(physical_raw)
    receipt,groups=simc_tier.read_receipt(seed_directory)
    result=match_first_party_roster(candidate=candidate,
                                    simc_receipt=receipt,
                                    simc_set_groups=groups)
    need(type(physical_stage_receipt) is str
         and len(physical_stage_receipt)==64,
         "V251_PHYSICAL_STAGE_RECEIPT_REQUIRED")
    code=stages.module_dependency_fingerprint(
        [Path(__file__),Path(stages.__file__),
         Path(simc_tier.__file__)])
    rel="source/v251_exact_first_party_13_class_simc_options.json"
    output=root/rel
    def execute():
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(
            result,indent=2,sort_keys=True,ensure_ascii=False)+"\n",
            encoding="utf8")
    def validate(paths):
        d=json.loads(paths["result"].read_text("utf8"))
        return (d==result and
                d["simc_set_option_verified_by_exact_physical_ids"] is True
                and d["season_membership_verified"] is False
                and d["environment_ready"] is False)
    try:
        stage=stages.execute_stage(
            root=root,stage_id="fresh-v251-exact-first-party-simc-options",
            stage_version="same-build-exact-class-65-source-1",
            inputs={"physical_sha256":digest(physical_raw),
                    "physical_stage_receipt":physical_stage_receipt,
                    "simc_seed_receipt_sha256":receipt["receipt_sha256"],
                    "simc_source_set_sha256":
                        receipt["source_files"]["item_set_bonus.inc"]["sha256"],
                    "code_sha256":code["sha256"]},
            outputs={"result":rel},execute=execute,validate=validate)
    except stages.StageExecutionBlocked as exc:
        raise BridgeBlocked("V251_FIRST_PARTY_STAGE_BLOCKED:"+str(exc)) from exc
    return {"schema":SCHEMA,"status":result["status"],
            "candidate_path":str(output.resolve()),
            "simc_seed_receipt_sha256":receipt["receipt_sha256"],
            "class_count":13,"piece_count":65,
            "season_membership_verified":False,
            "environment_ready":False,
            "native_calls":0,"network_calls_by_stage":0,
            "source_stage":{k:v for k,v in stage.items() if k!="result"}}

def build_stage(*,stage_root,db2_candidate_path,bonus_candidate_path,
                db2_receipt,bonus_receipt):
    root=Path(stage_root)
    need(root.is_dir() and not root.is_symlink(),
         "V251_STAGE_ROOT_REQUIRED")
    db2path=Path(db2_candidate_path);bonuspath=Path(bonus_candidate_path)
    db2raw=raw_report(db2path);bonusraw=raw_report(bonuspath)
    db2=json.loads(db2raw);bonus=json.loads(bonusraw)
    need(type(db2_receipt) is str and len(db2_receipt)==64
         and type(bonus_receipt) is str and len(bonus_receipt)==64,
         "V251_UPSTREAM_STAGE_RECEIPTS_REQUIRED")
    code=stages.module_dependency_fingerprint(
        [Path(__file__),Path(stages.__file__)])
    rel="source/v251_raid_correlated_tier_65_piece_candidate.json"
    path=root/rel
    def execute():
        doc=preview(db2=db2,corroboration=bonus)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(doc,indent=2,sort_keys=True,
                                  ensure_ascii=False)+"\n",encoding="utf8")
    def validate(paths):
        doc=json.loads(paths["candidate"].read_text("utf8"))
        return (doc.get("schema")==SCHEMA
                and doc.get("game_build")==db2["game_build"]
                and doc.get("class_count")==13
                and doc.get("piece_count")==65
                and doc.get("production_profile_promoted") is False
                and doc.get("season_membership_verified") is False
                and doc.get("environment_ready") is False
                and doc.get("native_calls")==0
                and doc.get("used_tier_name_matching") is False)
    try:
        stage=stages.execute_stage(
            root=root,stage_id="fresh-v251-db2-raid-tier-candidate",
            stage_version="exact-13x5-no-season-promotion-1",
            inputs={"db2_sha256":digest(db2raw),
                    "bonus_sha256":digest(bonusraw),
                    "db2_receipt":db2_receipt,
                    "bonus_receipt":bonus_receipt,
                    "code_sha256":code["sha256"]},
            outputs={"candidate":rel},execute=execute,validate=validate)
    except (stages.StageExecutionBlocked,BridgeBlocked) as exc:
        raise BridgeBlocked("V251_CANDIDATE_STAGE_PENDING:"+str(exc)) from exc
    doc=load(path)
    return {"schema":SCHEMA,"status":doc["status"],
            "candidate_path":str(path.resolve()),
            "class_count":13,"piece_count":65,
            "season_membership_verified":False,
            "simc_source_verified":False,
            "environment_ready":False,"native_calls":0,
            "network_calls_by_stage":0,
            "source_stage":{k:v for k,v in stage.items() if k!="result"}}
