#!/usr/bin/env python3
"""Exact v221 gem-item enchant IDs -> same-build Wago raw CHMV effect points.

A SOURCE join, NOT a new stat effect interpreter, highest-quality selector,
socket verifier or J approval engine. SimC remains responsible for actual
effect application; raw points and scaled/conditional cases stay pending.
"""
from __future__ import annotations

import csv
import hashlib
import io
import math
import re

SCHEMA = "v266_gem_enchant_raw_chmv_source_v1"
GEM_SOURCE_SCHEMA = "v221_verified_gem_property_item_source_join_v1"
GEM_SOURCE_STATUS = "SOURCE_ITEM_PROPERTY_LINKS_ONLY_NOT_USER_ADMITTED"
# SimulationCraft engine/dbc/data_enums.hh :: item_mod_type at the pinned
# SimC version. IDs for crit/haste/vers/mastery are stable source enum keys.
CHMV = {32:"crit_rating",36:"haste_rating",
        49:"mastery_rating",40:"versatility_rating"}
STAT_ENCHANT_EFFECT = 5
MAX_CSV = 32_000_000
MAX_GEM_LINKS = 5000
MAX_RELEVANT_ENCHANTS = 5000
INT = re.compile(r"-?[0-9]+\Z")
COLUMNS = (
    "ID",
    *(f"{name}_{index}" for index in range(3)
      for name in ("Effect", "EffectArg", "EffectPointsMin",
                   "EffectScalingPoints")),
)

class EnchantSourceBlocked(ValueError):
    pass


def need(test, code):
    if not test:
        raise EnchantSourceBlocked(code)


def integer(value, label):
    need(type(value) is str and INT.fullmatch(value.strip()) is not None,
         "V266_" + label + "_INTEGER_REQUIRED")
    return int(value)


def floating(value, label):
    try:
        num = float(value)
    except (ValueError, TypeError) as exc:
        raise EnchantSourceBlocked(
            "V266_" + label + "_NUMBER_REQUIRED") from exc
    need(math.isfinite(num), "V266_" + label + "_FINITE_REQUIRED")
    return num


def preview(*, gem_join, raw_enchant_csv, expected_game_build):
    """One pass over an independently sealed, same-build enchant CSV."""
    need(type(gem_join) is dict and
         gem_join.get("schema") == GEM_SOURCE_SCHEMA and
         gem_join.get("status") == GEM_SOURCE_STATUS and
         type(expected_game_build) is str and bool(expected_game_build) and
         gem_join.get("game_build") == expected_game_build and
         gem_join.get("simc_generated_gem_source_build") ==
            expected_game_build,
         "V266_EXACT_SAME_BUILD_V221_GEM_JOIN_REQUIRED")
    joins=gem_join.get("joins")
    need(type(joins) is list and len(joins)<=MAX_GEM_LINKS and
         len(joins)==gem_join.get("exact_link_count"),
         "V266_V221_GEM_LINK_COUNT_INVALID")
    ids=set()
    for join in joins:
        need(type(join) is dict and
             type(join.get("item_id")) is int and join["item_id"]>0 and
             join["item_id"] not in ids and
             type(join.get("enchant_id")) is int and
             join["enchant_id"]>=0 and
             join.get("status")=="EXACT_DB2_ITEMSPARSE_GEM_PROPERTY_RELATION" and
             join.get("ui_selectable") is False,
             "V266_GEM_LINK_OR_ENCHANT_ID_INVALID")
        ids.add(join["item_id"])
    need(type(raw_enchant_csv) is bytes and
         0<len(raw_enchant_csv)<=MAX_CSV,
         "V266_ENCHANT_SOURCE_SIZE_INVALID")
    try:
        reader=csv.DictReader(io.StringIO(raw_enchant_csv.decode("utf8"),
                                         newline=""))
        need(reader.fieldnames is not None and
             set(COLUMNS)<=set(reader.fieldnames),
             "V266_WAGO_ENCHANT_STATIC_COLUMNS_MISSING")
        wanted={row["enchant_id"] for row in joins if row["enchant_id"]>0}
        need(len(wanted)<=MAX_RELEVANT_ENCHANTS,
             "V266_ENCHANT_SOURCE_ID_SET_TOO_LARGE")
        found={}
        for row in reader:
            if row is None or row.get("ID") is None:
                raise EnchantSourceBlocked("V266_ENCHANT_ROW_INVALID")
            key=integer(row["ID"],"ENCHANT_ID")
            if key not in wanted:
                continue
            need(key not in found, "V266_DUPLICATE_RELEVANT_ENCHANT_ID")
            found[key]=row
    except (UnicodeError,csv.Error) as exc:
        raise EnchantSourceBlocked(
            "V266_ENCHANT_SOURCE_CSV_UNREADABLE") from exc
    records=[]
    for join in joins:
        enchant_id=join["enchant_id"]
        row=found.get(enchant_id)
        vector={name:0 for name in CHMV.values()}
        unknown=False
        applicable=0
        if row is None:
            verdict="ENCHANT_ID_MISSING_FROM_SAME_BUILD_CSV"
        else:
            for idx in range(3):
                kind=integer(row[f"Effect_{idx}"],"EFFECT_KIND")
                if kind==0:
                    continue
                applicable+=1
                arg=integer(row[f"EffectArg_{idx}"],"EFFECT_ARG")
                points=integer(row[f"EffectPointsMin_{idx}"],"POINTS")
                scaling=floating(row[f"EffectScalingPoints_{idx}"],
                                 "SCALING")
                if (kind!=STAT_ENCHANT_EFFECT or arg not in CHMV or
                        points<=0 or scaling!=0):
                    unknown=True
                    continue
                vector[CHMV[arg]]+=points
            verdict=("RAW_STATIC_CHMV_POINTS_CANDIDATE_ONLY"
                     if applicable and not unknown and any(vector.values())
                     else "NONSTATIC_SCALED_OR_NON_CHMV_EFFECT_PENDING")
        records.append({
            "item_id":join["item_id"],"gem_property_id":join["gem_property_id"],
            "enchant_id":enchant_id,
            "effect_classification":verdict,
            "raw_static_points_candidate":(
                vector if verdict=="RAW_STATIC_CHMV_POINTS_CANDIDATE_ONLY"
                else None),
            "crafting_quality_rank":"NOT_PROVEN_BY_DB2_LINK",
            "native_gem_stat_acceptance":"NOT_MEASURED",
            "exact_socket_applicability":"NOT_ESTABLISHED",
            "J_rating_verified":False,"ui_selectable":False,
        })
    return {
        "schema":SCHEMA,"status":"ENCHANT_RAW_POINTS_SOURCE_ONLY_J_NOT_APPROVED",
        "game_build":expected_game_build,
        "simc_revision":gem_join["simc_revision"],
        "v221_manifest_sha256":gem_join["v213_manifest_sha256"],
        "gem_item_link_count":len(joins),
        "enchant_source_sha256":hashlib.sha256(raw_enchant_csv).hexdigest(),
        "raw_static_candidate_count":sum(
            x["raw_static_points_candidate"] is not None for x in records),
        "unresolved_count":sum(
            x["raw_static_points_candidate"] is None for x in records),
        "records":records,
        "highest_quality_selection_verified":False,
        "J":None,"environment_ready":False,
        "source_only_no_effect_reimplementation":True,
        "network_calls":0,"native_calls":0,"cache_mutations":0,
    }
