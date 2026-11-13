#!/usr/bin/env python3
"""A7: bounded read-only provenance contract for automatically discovered choices.

v163 is the already-authenticated same-build WCL/DB2 join. v167 is the
candidate compiled from it by v165/v166. This module does not choose items,
evaluate WorldStateExpressionID, authenticate effects, run SimC, fetch data,
or turn candidate options into approved in-game effects.
"""
from __future__ import annotations

import hashlib
import json

import v163_zero_seed_db2_join as season
import v165_current_season_gear_pool as pool
import v167_product_season_gear_adapter as adapter

SCHEMA="v405_a7_selected_source_contract_v1"
PUBLIC_ROLES=("trinket","special_effect_gear_candidate","selectable_stat_craft")
MAX_SOURCE_ITEMS=30000
MAX_PRODUCT_ITEMS=2000

class SourceContractBlocked(ValueError):
    pass

def need(value,code):
    if not value:
        raise SourceContractBlocked(code)

def canonical(obj):
    return json.dumps(obj,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False).encode("utf8")

def sha(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

def _eligible(source,season_id):
    if type(source) is not dict:
        return False
    kind=source.get("source")
    if kind=="raid_journal":
        return pool._journal_origin_current(source,season_id,raid=True)
    if kind=="mplus_journal":
        return pool._journal_origin_current(source,season_id,raid=False)
    if kind=="selectable_stat_craft":
        return (source.get("classification")=="PROVISIONAL_SIMC_BATCH_REVIEW"
                and type(source.get("expansion_id")) is int
                and source["expansion_id"]>0)
    return False

def assess(*, source, catalog, expected_game_build, source_report_sha256,
           candidate_sha256):
    """Proof for every *visible* item without preselected IDs or external calls.

    Ensure a WCL/DB2 original admitted the ID, an exact acquisition source
    survives into the final product row, and one of that item's actual
    journal/craft origins satisfies the independent season relation. Ignore
    opaque WSE value for eligibility (preserve it in unchanged provenance).
    """
    need(type(source) is dict and source.get("schema")==season.SCHEMA
         and source.get("source_provider")=="WAGO_TOOLS_PINNED_DB2_WCL_LIVE"
         and source.get("old_item_catalog_imported") is False
         and source.get("full_season_completeness_confirmed") is False
         and source.get("build")==expected_game_build,
         "A7_AUTHENTICATED_CURRENT_DB2_SOURCE_REQUIRED")
    need(type(catalog) is dict and catalog.get("schema")==adapter.SCHEMA
         and catalog.get("season_build")==expected_game_build
         and catalog.get("no_old_catalog_seed") is True
         and catalog.get("status")=="CURRENT_SEASON_CANDIDATE_SELECTION_ONLY",
         "A7_CURRENT_PRODUCT_CANDIDATE_SOURCE_REQUIRED")
    need(type(source_report_sha256) is str and len(source_report_sha256)==64
         and type(candidate_sha256) is str and len(candidate_sha256)==64
         and all(c in "0123456789abcdef" for c in
                 source_report_sha256+candidate_sha256),
         "A7_SEALED_SOURCE_HASHES_REQUIRED")
    season_id=source.get("db2_display_season_id")
    expansion=source.get("db2_expansion_id")
    need(type(season_id) is int and season_id>0
         and type(expansion) is int and expansion>0
         and catalog.get("db2_display_season_id")==season_id
         and catalog.get("expansion_id")==expansion,
         "A7_SEASON_AND_EXPANSION_MISMATCH")
    raw=source.get("items")
    need(type(raw) is list and len(raw)<=MAX_SOURCE_ITEMS
         and all(type(x) is dict and type(x.get("item_id")) is int
                 and x["item_id"]>0 for x in raw),
         "A7_SOURCE_ITEMS_INVALID")
    by_id={x["item_id"]:x for x in raw}
    need(len(by_id)==len(raw),"A7_DUPLICATE_SOURCE_ITEM_ID")
    items=catalog.get("items")
    need(type(items) is list and len(items)<=MAX_PRODUCT_ITEMS,
         "A7_PRODUCT_ITEMS_INVALID")
    need(adapter.validate(catalog) is catalog,
         "A7_CANDIDATE_SHAPE_INVALID")
    visible=adapter.public_options(catalog)
    choices=visible["choices"]
    need(set(choices)==set(PUBLIC_ROLES),"A7_PUBLIC_ROLES_CHANGED")
    indexed={x["item_id"]:x for x in items}
    need(len(indexed)==len(items),"A7_DUPLICATE_CANDIDATE_ITEM_ID")
    # Every v167 current candidate, including internal ordinary equipment,
    # must trace back to an admitted source row. User options are then an
    # exact subset; no item IDs are selected or supplied by GPT.
    verified_ids=set()
    for candidate in items:
        item_id=candidate["item_id"]
        original=by_id.get(item_id)
        need(original is not None,"A7_PUBLIC_ITEM_WITHOUT_AUTHENTICATED_SOURCE")
        raw_sources=original.get("acquisition_sources")
        known_sources=candidate.get("source_evidence")
        # v166 intentionally retains only a small projection of v163
        # (without WCL names or raw WSE diagnostics).
        need(type(raw_sources) is list and type(known_sources) is list
             and all(type(s) is dict for s in raw_sources+known_sources)
             and all(any(all(k in src and src[k]==v for k,v in obs.items())
                         for src in raw_sources) for obs in known_sources),
             "A7_PUBLIC_ITEM_SOURCE_EVIDENCE_DRIFT")
        eligible=False
        for src in raw_sources:
            if not _eligible(src,season_id):
                continue
            if src["source"]=="selectable_stat_craft":
                if src["expansion_id"]!=expansion:
                    continue
            eligible=True
            break
        need(eligible,"A7_NO_CURRENT_JOURNAL_OR_CRAFT_ORIGIN")
        verified_ids.add(item_id)
    public_ids=[]
    counts={}
    for role in PUBLIC_ROLES:
        rows=choices[role]
        need(type(rows) is list,"A7_PUBLIC_ROLE_ROWS_INVALID")
        counts[role]=len(rows)
        for row in rows:
            item_id=row["item_id"]
            need(item_id not in public_ids,"A7_DUPLICATE_PUBLIC_ITEM_ID")
            public_ids.append(item_id)
            candidate=indexed.get(item_id)
            need(candidate is not None and candidate["category"]==role
                 and item_id in verified_ids,
                 "A7_PUBLIC_ITEM_WITHOUT_AUTHENTICATED_SOURCE")
    expected_visible={x["item_id"] for x in items
                      if x["category"] in PUBLIC_ROLES}
    need(set(public_ids)==expected_visible,
         "A7_PUBLIC_OPTIONS_DO_NOT_MATCH_CURRENT_CANDIDATES")
    visible_counts=visible.get("count")
    need(type(visible_counts) is int and
         visible_counts==len(items),"A7_PUBLIC_CANDIDATE_COUNT_DRIFT")
    return {
        "schema":SCHEMA,
        "status":"A7_PUBLIC_CANDIDATE_ORIGINS_AUTO_RECONCILED_SOURCE_ONLY",
        "game_build":expected_game_build,
        "db2_expansion_id":expansion,
        "db2_display_season_id":season_id,
        "original_v163_sha256":source_report_sha256,
        "v167_candidate_sha256":candidate_sha256,
        "source_reconciled_candidate_count":len(verified_ids),
        "source_reconciled_candidate_ids_sha256":sha(sorted(verified_ids)),
        "public_candidate_count":len(public_ids),
        "public_role_counts":counts,
        "public_item_ids_sha256":sha(sorted(public_ids)),
        "wse_diagnostics_preserved_not_evaluated":True,
        "item_eligibility_requires_wse":False,
        "manually_selected_item_ids":False,
        "effect_or_simc_certification":False,
        "whole_season_coverage_certified":False,
        "final_product_e2e":False,
        "additional_api_calls":0,
        "native_calls":0
    }
