#!/usr/bin/env python3
"""v232: SimC-only ordinary/weapon representative *candidate*, one DPS request.

Reads exactly v229's pinned SimC generated item source and a v231 physical
tier candidate. Reuses v230's single-pass metadata parser and v169's existing
ordinary/weapon physical selection functions (not a new item recommender).
The selected physical IDs are provisional until their actual Native static G
is observed. Active-season acquisition is NOT a numeric G prerequisite when
slot/material/primary/plain item-effect conditions are checked. This source
candidate alone is not the final product G/B/T or item-list admission.
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



def _source_scope_diagnostic(provider, display_season_id):
    """Grade observed DB2 source relations, NOT actual season membership.

    WCL-active zone and DB2 display season relation are useful *candidate*
    provenance, not a guarantee that the particular difficulty/item variant
    is obtainable this week. Unknown world-state, Localbots and crafts
    must not silently become current-season obtainable USER equipment.
    They may still be physically suitable for a generic G reference.
    """
    sources = provider.get("source_evidence", []) if provider else []
    kind = provider.get("source_kinds", []) if provider else []
    explicit = [s for s in sources if
                s.get("source") in ("mplus_journal","raid_journal")
                and type(display_season_id) is int
                and display_season_id > 0
                and s.get("season_evidence") == "DB2_DISPLAY_SEASON_MATCH"
                and s.get("display_season_id") == display_season_id
                and s.get("world_state_expression_id") == 0
                and type(s.get("journal_encounter_id")) is int
                and s["journal_encounter_id"] > 0
                and type(s.get("journal_instance_id")) is int
                and s["journal_instance_id"] > 0]
    same_world = any(
        type(display_season_id) is int and display_season_id>0
        and s.get("source")=="mplus_journal"
        and s.get("display_season_id")==display_season_id
        and type(s.get("world_state_expression_id")) is int
        and s["world_state_expression_id"]>0 for s in sources)
    if explicit:
        state = "DB2_DISPLAY_SEASON_EXPLICIT_WSE_ZERO_CANDIDATE"
        blockers = ["INDEPENDENT_ACTIVE_ITEM_VARIANT_AND_TIER_SEASON_PROOF"]
    else:
        unresolved_world = any(
            s.get("season_evidence") == "UNKNOWN_WORLD_STATE_EXPRESSION"
            or type(s.get("world_state_expression_id")) is int
            and s["world_state_expression_id"] > 0 for s in sources)
        if unresolved_world:
            state = "WORLD_STATE_EXPRESSION_PENDING"
        elif "raid_journal" in kind:
            state = "RAID_JOURNAL_SEASON_UNSCOPED_OR_UNKNOWN"
        elif "mplus_journal" in kind:
            state = "MPLUS_DISPLAY_SEASON_NOT_INDEPENDENTLY_MATCHED"
        elif "selectable_stat_craft" in kind:
            state = "EXPANSION_CRAFT_NOT_SEASON_AUTHENTICATED"
        elif "localbots_delve_pool" in kind:
            state = "LOCALBOTS_SUPPLEMENTARY_NOT_SEASON_AUTHENTICATED"
        else:
            state = "SOURCE_CONDITIONS_NOT_RETAINED_OR_NOT_FOUND"
        blockers = [state]
    return {
        "status":state,
        "explicit_db2_match_no_world_state":bool(explicit),
        "same_display_season_worldstate_pending":same_world,
        "world_state_expression_ids":sorted({
            s["world_state_expression_id"] for s in sources
            if type(s.get("world_state_expression_id")) is int
            and s["world_state_expression_id"]>0}),
        "season_membership_authenticated":False,
        "G_source_approved":False,
        "source_kinds":list(kind),
        "matched_journal_encounter_ids":sorted({
            s["journal_encounter_id"] for s in explicit}),
        "unresolved_requirements":blockers,
    }


def find_candidate(*, seed_directory, tier_candidate, target_ilevel,
                   max_source_distance=MAX_DISTANCE, season_gear_db=None):
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

    # Normal product mode: opt into same-build Wago DB2 candidates already
    # collected by v167/v171. Omitted by default for strict SimC-only trials.
    season_ids=None
    provider_by_id={}
    if season_gear_db is not None:
        try:
            verified=chooser.gear.validate(season_gear_db)
        except (chooser.gear.GearBlocked,KeyError,TypeError) as exc:
            raise SourceRepresentativeBlocked(
                "V232_OPTIONAL_SEASON_GEAR_SOURCE_INVALID") from exc
        need(verified["season_build"]==receipt["simc_generated_build"]
             and verified.get("no_old_catalog_seed") is True,
             "V232_OPTIONAL_SEASON_GEAR_BUILD_OR_PROVENANCE_MISMATCH")
        provider_by_id={
            x["item_id"]:x for x in (
                verified["items"]+
                verified.get("internal_conditional_mplus_plain_candidates",[])+
                verified.get("internal_source_only_plain_neck_candidates",[])+
                verified.get("internal_source_only_plain_ring_candidates",[]))
            if x["category"]=="plain_representative_candidate"
            and x.get("source_kinds")
        }
        season_ids=set(provider_by_id)
        need(bool(season_ids),
             "V232_OPTIONAL_SEASON_GEAR_HAS_NO_PLAIN_CANDIDATES")
    # P3-GB: zero extra source reads/Native. For a failed neck selection,
    # record only bounded drop-off counts from the SAME v230 streaming pass.
    # Do not assume a missing source ID is an unusable real-world necklace.
    ring_source_ids={iid for iid,row in provider_by_id.items()
                     if row["inventory_type"]==11}
    ring_coverage={
        "db2_plain_ring_count":len(ring_source_ids),
        "simc_exact_id_seen":0,
        "simc_class_mask_rejected":0,
        "simc_item_set_rejected":0,
        "simc_plain_ring_accepted":0,
        "selected_ring_count":0,
        "upstream_ring_total":sum(
            verified.get("source_ring_role_scope_counts",{}).values()
            ) if season_ids is not None else 0,
        "upstream_plain_conditional":sum(
            v for k,v in verified.get(
                "source_ring_role_scope_counts",{}).items()
            if k=="plain_representative_candidate:CONDITIONAL_SEASON_NOT_ESTABLISHED"
            ) if season_ids is not None else 0,
    }
    neck_source_ids={iid for iid,row in provider_by_id.items()
                     if row["inventory_type"]==2}
    neck_coverage={
        "db2_plain_neck_count":len(neck_source_ids),
        "simc_exact_id_seen":0,
        "simc_inventory_mismatch":0,
        "simc_class_or_subclass_rejected":0,
        "simc_class_mask_rejected":0,
        "simc_item_set_rejected":0,
        "simc_plain_neck_accepted":0,
        "upstream_neck_total":sum(
            verified.get("source_neck_role_scope_counts",{}).values()
            ) if season_ids is not None else 0,
        "upstream_plain_conditional":sum(
            v for k,v in verified.get(
                "source_neck_role_scope_counts",{}).items()
            if k=="plain_representative_candidate:CONDITIONAL_SEASON_NOT_ESTABLISHED"
            ) if season_ids is not None else 0,
    }
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
        neck=iid in neck_source_ids
        ring=iid in ring_source_ids
        if ring:
            ring_coverage["simc_exact_id_seen"]+=1
        if neck:
            neck_coverage["simc_exact_id_seen"]+=1
        if iid in tier_ids:return True
        if season_ids is not None and iid not in season_ids:return False
        inv=metadata.number(fields[10],"V232_INVENTORY_TYPE_INVALID")
        if inv not in VALID_INVENTORY:
            if neck: neck_coverage["simc_inventory_mismatch"]+=1
            return False
        if neck and inv!=2:
            neck_coverage["simc_inventory_mismatch"]+=1
        kind=metadata.number(fields[11],"V232_ITEM_CLASS_INVALID")
        if kind not in (2,4):
            if neck:neck_coverage["simc_class_or_subclass_rejected"]+=1
            return False
        source_level=metadata.number(fields[5],"V232_ITEM_LEVEL_INVALID")
        # Optional DB2 candidates may have different historical base ilvl
        # or quality despite being in the *current rotation* (returning M+).
        if season_ids is None:
            if abs(source_level-ref_ilevel)>max_source_distance:return False
            if metadata.number(fields[9],"V232_ITEM_QUALITY_INVALID")!=quality:
                return False
        if metadata.number(fields[24],"V232_ITEM_SET_INVALID")!=0:
            if neck:neck_coverage["simc_item_set_rejected"]+=1
            if ring:ring_coverage["simc_item_set_rejected"]+=1
            return False
        if (metadata.number(fields[19],"V232_CLASS_MASK_INVALID")
                & class_mask)!=class_mask:
            if neck:neck_coverage["simc_class_mask_rejected"]+=1
            if ring:ring_coverage["simc_class_mask_rejected"]+=1
            return False
        sub=metadata.number(fields[12],"V232_SUBCLASS_INVALID")
        if inv in (5,20,9,6,8):
            return kind==4 and sub==chooser.gear.ARMOR_SUBCLASS[
                contract["family"]]
        if inv in (2,16,11):
            if ring and kind==4 and inv==11:
                ring_coverage["simc_plain_ring_accepted"]+=1
            if neck:
                if kind==4 and inv==2:
                    neck_coverage["simc_plain_neck_accepted"]+=1
                else:
                    neck_coverage["simc_class_or_subclass_rejected"]+=1
            return kind==4
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
    primary_allowed=chooser.PRIMARY_STAT_CODES[contract["primary"]]
    all_primary=frozenset().union(*chooser.PRIMARY_STAT_CODES.values())
    def matching_primary(iid,slot):
        # WoW neck/rings may carry no primary rating. When a primary code
        # exists, it must still be usable by this specialization.
        codes=set(items[iid]["stat_modifier_codes"])
        if slot in chooser.COMMON:
            return not (codes & all_primary) or bool(codes & primary_allowed)
        return bool(codes & primary_allowed)

    options=[]
    for r in items.values():
        if r["item_id"] in tier_ids:continue
        provider=provider_by_id.get(r["item_id"])
        if season_ids is not None:
            need(provider is not None and
                 provider["inventory_type"]==r["inventory_type"] and
                 provider["class_id"]==r["class_id"] and
                 provider["subclass_id"]==r["subclass_id"] and
                 provider["item_set_id"]==0,
                 "V232_SAME_BUILD_DB2_SIMC_ITEM_METADATA_DISAGREES")
        options.append({
            "category":"plain_representative_candidate",
            "item_id":r["item_id"],"name":r["name"],
            "inventory_type":r["inventory_type"],
            "class_id":r["class_id"],"subclass_id":r["subclass_id"],
            "stat_modifier_codes":r["stat_modifier_codes"],
            "allowed_class_mask":r["allowed_class_mask"],
            "item_set_id":0,
            "season_candidate_source_kinds":(
                provider.get("source_kinds",[]) if provider else []),
        })
    # Reuse v169 pure selectors, preferring explicit same-display-season
    # DB2 candidates to lower-ID Localbots / unscoped historical candidates
    # for a clean SimC profile. This preference is not a G-budget Gate:
    # same-ilevel plain physical gear can also provide numeric G after Native.
    season_display=(verified.get("db2_display_season_id")
                    if season_ids is not None else None)
    evidence_by_id={
        r["item_id"]:_source_scope_diagnostic(
            provider_by_id.get(r["item_id"]),season_display)
        for r in options}
    def source_rank(iid):
        # A representative G-only physical neck is never promoted to an
        # obtainable season item. It is the last eligible source option.
        if provider_by_id.get(iid,{}).get("internal_generic_G_only") is True:
            return 5
        e=evidence_by_id[iid]
        if e["explicit_db2_match_no_world_state"]:return 0
        if (e["status"]=="WORLD_STATE_EXPRESSION_PENDING"
            and e["same_display_season_worldstate_pending"]):return 1
        if "raid_journal" in e["source_kinds"]:return 2
        if "mplus_journal" in e["source_kinds"]:return 3
        return 4
    def explicit_id(iid):
        return source_rank(iid)==0
    scratch={"items":options}
    used=set(tier_ids)
    ordinary={}
    for slot in chooser.ORDINARY:
        matches=chooser.available_plain(scratch,slot=slot,
            family=contract["family"],class_mask=class_mask,used=used)
        need(bool(matches),"V232_ORDINARY_SLOT_WITHOUT_SIMC_CANDIDATE:"+slot)
        matches=[iid for iid in matches if matching_primary(iid,slot)]
        need(bool(matches),"V232_ORDINARY_PRIMARY_STAT_NOT_COMPATIBLE:"+slot)
        matches.sort(key=lambda iid:(source_rank(iid),iid))
        ordinary[slot]=matches[0];used.add(matches[0])
    common={}
    common_socket_source_candidates={}
    for slot in chooser.COMMON:
        matches=chooser.available_plain(scratch,slot=slot,
                class_mask=class_mask,used=used)
        if not matches and slot=="neck" and season_ids is not None:
            # This diagnostic is NOT a bypass or a season catalog. Values
            # contain no item IDs, profile, raw source path or credentials.
            raise SourceRepresentativeBlocked(
                "V232_COMMON_SLOT_WITHOUT_SIMC_CANDIDATE:neck|"
                +json.dumps(neck_coverage,sort_keys=True,separators=(",",":")))
        if not matches and slot in ("finger1","finger2") and season_ids is not None:
            ring_coverage["selected_ring_count"]=sum(
                key in common for key in ("finger1","finger2"))
            raise SourceRepresentativeBlocked(
                "V232_COMMON_SLOT_WITHOUT_SIMC_CANDIDATE:"+slot+"|"
                +json.dumps(ring_coverage,sort_keys=True,separators=(",",":")))
        need(bool(matches),"V232_COMMON_SLOT_WITHOUT_SIMC_CANDIDATE:"+slot)
        matches=[iid for iid in matches if matching_primary(iid,slot)]
        need(bool(matches),"V232_COMMON_PRIMARY_STAT_NOT_COMPATIBLE:"+slot)
        # Future-target defaults need real gem locations. On neck/rings,
        # prefer a physically socketed source candidate if one exists.
        # Source-season provenance remains the first priority. Socket
        # preference only breaks ties inside the SAME provenance rank;
        # do not promote an unresolved/off-season candidate over an
        # explicitly observed active-season plain item.
        jewelry=slot in ("neck","finger1","finger2")
        if jewelry:
            common_socket_source_candidates[slot]={
                "eligible_count":len(matches),
                "intrinsic_socketed_count":sum(
                    items[iid]["intrinsic_socket_count_from_simc_source"]>0
                    for iid in matches),
                "best_socket_count":max(
                    items[iid]["intrinsic_socket_count_from_simc_source"]
                    for iid in matches),
                "non_generic_socketed_count":sum(
                    items[iid]["intrinsic_socket_count_from_simc_source"]>0
                    and source_rank(iid)<5 for iid in matches)}
            matches.sort(key=lambda iid:(
                source_rank(iid),
                items[iid]["intrinsic_socket_count_from_simc_source"]==0,
                iid))
        else:
            matches.sort(key=lambda iid:(source_rank(iid),iid))
        common[slot]=matches[0];used.add(matches[0])
    try:
        # Reuse v169 exact weapon-form selection; WSE candidates are
        # second-tier internal source fallback, never public eligibility.
        explicit_weapons={"items":[r for r in options if explicit_id(
            r["item_id"])]}
        try:
            weapons=chooser.shape_weapons(
                explicit_weapons,contract["weapon_form"],class_mask,
                spec_key=cl+"/"+sp)
        except chooser.RepresentativeBlocked:
            conditional_weapons={"items":[r for r in options
                if source_rank(r["item_id"])<=1]}
            try:
                weapons=chooser.shape_weapons(
                    conditional_weapons,contract["weapon_form"],class_mask,
                    spec_key=cl+"/"+sp)
            except chooser.RepresentativeBlocked:
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
    # v165/v166's original ItemXItemEffect classification (via v167
    # 'plain_representative_candidate') and v169's existing weapon shape
    # establish generic G *physical* suitability. Neither condition depends
    # on the item's active-season acquisition/WorldStateExpression status.
    # SimC-only fallback lacks the DB2 effect record and remains a probe.
    selected_plain_catalog_effect_free=(
        season_ids is not None and all(
            provider_by_id.get(iid,{}).get("category")==
                "plain_representative_candidate"
            and provider_by_id[iid].get("item_set_id")==0
            for slot,iid in selected.items() if iid not in tier_ids))
    selected_primary_compatible=all(
        matching_primary(iid,slot) for slot,iid in selected.items())
    need(selected_primary_compatible,
         "V232_SELECTED_G_PRIMARY_STAT_OR_WEAPON_INCOMPATIBLE")
    generic_G_physical_conditions_verified=bool(
        selected_plain_catalog_effect_free and selected_primary_compatible
        and len(selected) in (13,14))
    non_tier_sources={slot:evidence_by_id[iid]
        for slot,iid in sorted(selected.items()) if iid not in tier_ids}
    unresolved_slots=sorted(
        slot for slot,details in non_tier_sources.items()
        if not details["explicit_db2_match_no_world_state"])
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
        "season_candidate_provider":(
            "EXPLICIT_SAME_BUILD_WAGO_DB2_V167_CANDIDATES"
            if season_ids is not None else "SIMC_ONLY_NO_SEASON_PROOF"),
        "season_gear_db_digest_sha256":(
            seed.digest(seed.canonical(verified).encode("utf8"))
            if season_ids is not None else None),
        "season_gear_db_mplus_worldstate_pending":(
            verified.get("mplus_season_candidate_inclusion",{}).get(
                "world_state_effectively_resolved") is False
            if season_ids is not None else None),
        "selected_gear_season_source_kinds":{
            slot:provider_by_id.get(iid,{}).get("source_kinds",[])
            for slot,iid in sorted(selected.items())
            if iid not in tier_ids},
        "selected_ordinary_source_provenance":non_tier_sources,
        "selected_non_tier_season_condition_pending_slots":unresolved_slots,
        "selected_non_tier_explicit_db2_match_count":
            len(non_tier_sources)-len(unresolved_slots),
        "tier_active_season_membership_not_authenticated":True,
        "selected_G_source_candidate_not_approved":True,
        "selected_ordinary":ordinary,
        "selected_common":common,
        "selected_common_socket_source_coverage":{
            slot:{**info,"selected_item_id":common[slot],
                  "selected_intrinsic_count":
                    items[common[slot]][
                        "intrinsic_socket_count_from_simc_source"]}
            for slot,info in sorted(common_socket_source_candidates.items())},
        "selected_weapons":weapons,
        "selected_G_slot_ids":{k:selected[k] for k in sorted(selected)},
        # Same v230 streaming source; not game-side socket bonus permission.
        "selected_intrinsic_socket_colors_by_slot_source_only":{
            slot:list(items[iid]["intrinsic_socket_colors_from_simc_source"])
            for slot,iid in sorted(selected.items())},
        "selected_intrinsic_socket_count_by_slot_source_only":{
            slot:items[iid]["intrinsic_socket_count_from_simc_source"]
            for slot,iid in sorted(selected.items())},
        "selected_intrinsic_socket_total_source_only":sum(
            items[iid]["intrinsic_socket_count_from_simc_source"]
            for iid in selected.values()),
        "added_socket_bonus_and_game_permission_not_proven":True,
        "selected_item_unscaled_source_ilevel":{
            slot:items[iid]["ilevel_unscaled"] for slot,iid
            in sorted(selected.items())},
        "native_physical_and_static_G_still_required":True,
        "generic_G_physical_conditions_verified":
            generic_G_physical_conditions_verified,
        "generic_G_current_season_membership_required":False,
        "generic_G_plain_item_effect_relation_checked":
            selected_plain_catalog_effect_free,
        # Tier 2/4pc effects and arbitrary non-DB2 SimC effects are NOT
        # independently certified here; SimC remains their owner.
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
    p.add_argument("--season-gear-db",type=Path,
                   help="Optional v167/v171 same-build Wago candidates; omit for SimC-only trials")
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args(argv)
    source=json.loads(a.tier_candidate.read_text(encoding="utf8"))
    db=json.loads(a.season_gear_db.read_text(encoding="utf8")) if a.season_gear_db else None
    data=find_candidate(seed_directory=a.seed_dir,tier_candidate=source,
                       target_ilevel=a.target_ilevel,season_gear_db=db)
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
