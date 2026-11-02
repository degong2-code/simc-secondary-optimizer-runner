#!/usr/bin/env python3
"""v232: SimC-only ordinary/weapon representative *candidate*, one DPS request.

Reads exactly v229's pinned SimC generated item source and a v231 physical
tier candidate. Reuses v230's single-pass metadata parser and v169's existing
ordinary/weapon physical selection functions (not a new item recommender).
The selected source IDs are provisional until active-season membership and
the real Native static profile are independently verified; NEVER feed this
candidate directly to production G/B/T or v167 verified-season admission.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from . import v229_simc_only_source_seed as seed
    from . import v230_simc_item_metadata as metadata
    from . import v231_simc_tier_item_join as tier_join
    from . import v169_source_first_representative_stage as chooser
except ImportError:
    import v229_simc_only_source_seed as seed
    import v230_simc_item_metadata as metadata
    import v231_simc_tier_item_join as tier_join
    import v169_source_first_representative_stage as chooser

SCHEMA="v232_simc_only_one_dps_representative_source_candidate_v1"
VALID_INVENTORY=frozenset((2,5,20,9,6,8,16,11,13,17,15,26,14,23))
GEAR_LIMIT=4500
MAX_DISTANCE=20


class SourceRepresentativeBlocked(ValueError):pass


def need(ok, code):
    if not ok:raise SourceRepresentativeBlocked(code)


def find_candidate(*, seed_directory, tier_candidate, target_ilevel,
                   max_source_distance=MAX_DISTANCE):
    """Source-only deterministic G-work precursor, Native0 and cache0.

    The distance of ordinary item's *unscaled source level* from the tier's
    unscaled source level is a candidate search window only, NOT an item
    scaling formula or evidence of same-season status.
    """
    need(type(target_ilevel) is int and 1<=target_ilevel<=1000 and
         type(max_source_distance) is int and
         0<=max_source_distance<=100,
         "V232_TARGET_LEVEL_OR_SEARCH_WINDOW_INVALID")
    need(type(tier_candidate) is dict and
         tier_candidate.get("schema")==tier_join.SCHEMA and
         tier_candidate.get("status")==
             "SIMC_FIRST_PARTY_CLASS_TIER_CANDIDATE_NOT_SEASON_CERTIFIED" and
         tier_candidate.get("season_set_option_source_authentication")==
             "NOT_PROVED_BY_SIMC_TABLE_ALONE" and
         tier_candidate.get("environment_ready") is False and
         tier_candidate.get("G") is None and
         tier_candidate.get("receipt_sha256")==seed.digest(
             seed.canonical({k:v for k,v in tier_candidate.items()
                             if k!="receipt_sha256"}).encode("utf8")),
         "V232_UNPROMOTED_V231_SOURCE_TIER_REQUIRED")
    cl=tier_candidate["class"]
    sp=tier_candidate["spec"]
    contract=chooser.contracts.lookup(cl,sp)
    need(contract is not None, "V232_DPS_SPEC_REQUIRED")
    receipt,groups=tier_join.read_receipt(seed_directory)
    need(receipt["receipt_sha256"]==tier_candidate[
             "seed_receipt_sha256"] and
         receipt["simc_revision"]==tier_candidate["simc_revision"] and
         receipt["simc_generated_build"]==tier_candidate["game_build"],
         "V232_TIER_SEED_IDENTITY_CHANGED")
    matching=[g for g in groups["candidate_groups"]
              if g["set_opt"]==tier_candidate["season_set_option_declared"]
              and g["class_id"]==tier_candidate["class_id"]
              and g["set_id"]==tier_candidate["set_id"]]
    need(len(matching)==1 and
         set(matching[0]["item_ids"])==
             set(tier_candidate["tier_piece_ids"].values()) and
         matching[0]["observed_bonus_sizes"]==[2,4],
         "V232_SIMC_SET_SOURCE_TIER_IDS_DRIFT")

    tier_ids=set(tier_candidate["tier_piece_ids"].values())
    levels=tier_candidate.get("tier_unscaled_ilevel_by_slot")
    qualities=tier_candidate.get("tier_quality_by_slot")
    need(type(levels) is dict and type(qualities) is dict and
         set(levels)==set(chooser.contracts.TIER_SLOTS) and
         set(qualities)==set(levels) and
         all(type(v) is int and 1<=v<=1000 for v in levels.values()) and
         len(set(qualities.values()))==1 and
         all(type(q) is int and 1<=q<=7 for q in qualities.values()),
         "V232_TIER_LEVEL_OR_QUALITY_NOT_SOURCE_BOUND")
    ref_ilevel=sorted(levels.values())[2]
    quality=next(iter(qualities.values()))
    class_mask=tier_candidate["class_mask"]
    need(type(class_mask) is int and
         class_mask==(1<<(tier_candidate["class_id"]-1)) and
         chooser.gear.ARMOR_SUBCLASS[contract["family"]] > 0,
         "V232_CLASS_MASK_OR_ARMOR_FAMILY_INVALID")

    raw=seed.bounded_read(Path(seed_directory)/"item_data.inc",
                          seed.MAX_ITEM_FILE)
    item_source=receipt.get("source_files",{}).get("item_data.inc",{})
    need(seed.digest(raw)==item_source.get("sha256")==
             tier_candidate["item_data_sha256"] and
         seed.git_blob(raw)==item_source.get("git_blob_sha1"),
         "V232_ITEM_DATA_SOURCE_BYTES_DRIFT")

    def match(fields):
        # Every requested tier item is also scanned; binds v231's detailed
        # unscaled source-level/quality/slots to actual physical bytes.
        iid=metadata.number(fields[1],"V232_ITEM_ID_INVALID")
        if iid in tier_ids:return True
        inv=metadata.number(fields[10],"V232_INVENTORY_TYPE_INVALID")
        if inv not in VALID_INVENTORY:return False
        kind=metadata.number(fields[11],"V232_ITEM_CLASS_INVALID")
        if kind not in (2,4):return False
        source_level=metadata.number(fields[5],"V232_ITEM_LEVEL_INVALID")
        if abs(source_level-ref_ilevel)>max_source_distance:return False
        if metadata.number(fields[9],"V232_ITEM_QUALITY_INVALID")!=quality:
            return False
        if metadata.number(fields[24],"V232_ITEM_SET_INVALID")!=0:
            return False
        if (metadata.number(fields[19],"V232_CLASS_MASK_INVALID")
                & class_mask)!=class_mask:
            return False
        sub=metadata.number(fields[12],"V232_SUBCLASS_INVALID")
        if inv in (5,20,9,6,8):
            return kind==4 and sub==chooser.gear.ARMOR_SUBCLASS[
                contract["family"]]
        if inv in (2,16,11):return kind==4
        if inv in (13,17,15,26):return kind==2
        if inv==14:return kind==4 and sub==6
        if inv==23:return kind==4 and sub==0
        return False

    parsed=metadata.parse_exact(raw,build=receipt["simc_generated_build"],
        candidate_filter=match,candidate_limit=GEAR_LIMIT)
    items={r["item_id"]:r for r in parsed["items"]}
    need(tier_ids<=set(items),"V232_NATIVE_SOURCE_TIER_IDS_NOT_FOUND")
    for slot,iid in tier_candidate["tier_piece_ids"].items():
        row=items[iid]
        need(row["ilevel_unscaled"]==levels[slot] and
             row["quality"]==qualities[slot] and
             row["class_id"]==4 and
             row["subclass_id"]==chooser.gear.ARMOR_SUBCLASS[
                 contract["family"]] and
             row["item_set_id"]==tier_candidate["set_id"] and
             row["allowed_class_mask"]==class_mask and
             tier_join.INV_SLOT.get(row["inventory_type"])==slot,
             "V232_TIER_PHYSICAL_SOURCE_ROW_CHANGED")
    options=[]
    for r in items.values():
        if r["item_id"] in tier_ids:continue
        options.append({
            "category":"plain_representative_candidate",
            "item_id":r["item_id"],"name":r["name"],
            "inventory_type":r["inventory_type"],
            "class_id":r["class_id"],"subclass_id":r["subclass_id"],
            "stat_modifier_codes":r["stat_modifier_codes"],
            "allowed_class_mask":r["allowed_class_mask"],
            "item_set_id":0,
        })
    # Reuse v169 pure physical selectors only. Do not call
    # v169.select_class_spec/v167.validate with a fake CURRENT_SEASON flag.
    scratch={"items":options}
    used=set(tier_ids)
    ordinary={}
    for slot in chooser.ORDINARY:
        matches=chooser.available_plain(scratch,slot=slot,
            family=contract["family"],class_mask=class_mask,used=used)
        need(bool(matches),"V232_ORDINARY_SLOT_WITHOUT_SIMC_CANDIDATE:"+slot)
        ordinary[slot]=matches[0];used.add(matches[0])
    common={}
    for slot in chooser.COMMON:
        matches=chooser.available_plain(scratch,slot=slot,
                class_mask=class_mask,used=used)
        need(bool(matches),"V232_COMMON_SLOT_WITHOUT_SIMC_CANDIDATE:"+slot)
        common[slot]=matches[0];used.add(matches[0])
    try:
        weapons=chooser.shape_weapons(
            scratch,contract["weapon_form"],class_mask,
            spec_key=cl+"/"+sp)
    except chooser.RepresentativeBlocked as exc:
        raise SourceRepresentativeBlocked(
            "V232_WEAPON_FORM_SOURCE_CANDIDATE_MISSING:"+str(exc)) from exc
    selected={
        **{s:tier_candidate["tier_piece_ids"][s]
           for s in chooser.FOUR},
        **ordinary,**common,**weapons
    }
    need(len(selected) in (13,14) and
         len(set(selected.values()))==len(selected) and
         set(selected)<=set(chooser.contracts.SLOT_ORDER),
         "V232_DUPLICATE_OR_MISSING_G_ITEM")
    result={
        "schema":SCHEMA,
        "status":"SIMC_SOURCE_PHYSICAL_CANDIDATE_NOT_ACTUAL_SEASON_PROOF",
        "character":{"class":cl,"spec":sp,
                     "primary":contract["primary"],
                     "armor_family":contract["family"],
                     "weapon_form":contract["weapon_form"]},
        "game_build":receipt["simc_generated_build"],
        "simc_revision":receipt["simc_revision"],
        "target_ilevel":target_ilevel,
        "tier_set_option":tier_candidate["season_set_option_declared"],
        "tier_set_current_season_authenticated":False,
        "tier_set_id":tier_candidate["set_id"],
        "source_tier_receipt_sha256":tier_candidate["receipt_sha256"],
        "source_seed_receipt_sha256":receipt["receipt_sha256"],
        "item_data_sha256":parsed["source_sha256"],
        "source_item_level_window":{"tier_median_base":ref_ilevel,
                 "distance":max_source_distance,"tier_quality":quality,
                 "not_an_ilevel_scaling_rule":True},
        "physical_gear_candidates_seen":len(options),
        "selected_ordinary":ordinary,
        "selected_common":common,
        "selected_weapons":weapons,
        "selected_G_slot_ids":{k:selected[k] for k in sorted(selected)},
        "selected_item_unscaled_source_ilevel":{
            slot:items[iid]["ilevel_unscaled"] for slot,iid
            in sorted(selected.items())},
        "native_physical_and_static_G_still_required":True,
        "item_effects_absence_not_proven":True,
        "same_season_membership_not_proven":True,
        "G":None,"J":None,"F":None,"O":None,"B":None,"T":None,
        "environment_ready":False,
        "native_calls":0,"cache_mutations":0,
    }
    return {**result,"receipt_sha256":seed.digest(
        seed.canonical(result).encode("utf8"))}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed-dir",type=Path,required=True)
    p.add_argument("--tier-candidate",type=Path,required=True)
    p.add_argument("--target-ilevel",type=int,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args(argv)
    source=json.loads(a.tier_candidate.read_text(encoding="utf8"))
    data=find_candidate(seed_directory=a.seed_dir,tier_candidate=source,
                       target_ilevel=a.target_ilevel)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(
        data,sort_keys=True,ensure_ascii=False,indent=2)+"\n",
        encoding="utf8")
    print("V232_ONE_DPS_SOURCE_PHYSICAL_CANDIDATE",
          data["character"]["class"],data["character"]["spec"],
          len(data["selected_G_slot_ids"]),"G_UNKNOWN_NATIVE0")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
