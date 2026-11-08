#!/usr/bin/env python3
"""Read SimC's own before/after precombat CHMV rating, not DB2 effect points.

One controlled option at a time. This is a numeric observation adapter, never
an independent consumable proc interpreter, item-eligibility Gate, or J/F/O
production approval. Callers must bind paired JSON2 bytes to the actual
same-binary Native executions; a supplied hash is not independent attestation.
"""
from __future__ import annotations

import hashlib
import json
import math
import re

SCHEMA = "v269_simc_native_precombat_chmv_delta_v1"
STATS = ("crit_rating", "haste_rating", "mastery_rating", "versatility_rating")
CONSUMABLES = ("flask", "food", "potion", "augmentation", "temporary_enchant")
MEASURABLE = ("flask", "food", "temporary_enchant")
TOKEN = re.compile(r"[a-z0-9_]+\Z")
OIL = re.compile(r"main_hand:[a-z0-9_]+(?:/off_hand:[a-z0-9_]+)?\Z")
REV = re.compile(r"[0-9a-f]{40}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
MAX_JSON = 32_000_000


class SnapshotBlocked(ValueError):
    pass


def need(value, reason):
    if not value:
        raise SnapshotBlocked(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))


def prepare(*, profile, kind, token):
    """Preserve identical source gear/APL and neutralize other consumables."""
    need(type(profile) is str and bool(profile.strip()) and
         len(profile.encode("utf8")) <= 4_000_000,
         "V269_SOURCE_PROFILE_INVALID")
    need(kind in MEASURABLE and type(token) is str and
         (OIL.fullmatch(token) if kind == "temporary_enchant"
          else TOKEN.fullmatch(token)) is not None and token != "disabled",
         "V269_SINGLE_SIMC_OPTION_REQUIRED")
    lines = profile.splitlines()
    need(not any(x.strip().startswith(("profileset.", "copy=", "json2=",
                                          "iterations=", "output=", "html="))
                 for x in lines), "V269_NO_MULTI_PROFILE_OR_REPORT_OVERRIDES")
    names = {}
    for line in lines:
        key, sep, _ = line.partition("=")
        if sep and key.strip() in CONSUMABLES:
            need(key.strip() not in names, "V269_DUPLICATE_CONSUMABLE_SETTING")
            names[key.strip()] = True
    precombat = []
    for line in lines:
        m = re.match(r"^actions\.precombat(?:\+)?=/?([a-z_]+)", line.strip())
        if m:
            precombat.append(m.group(1))
    need(precombat.count("snapshot_stats") == 1,
         "V269_SINGLE_PRECOMBAT_SNAPSHOT_REQUIRED")
    snap = precombat.index("snapshot_stats")
    if kind in ("flask", "food"):
        need(kind in precombat[:snap],
             "V269_SELECTED_CONSUMABLE_MUST_PRECEDE_SNAPSHOT")
    if kind == "temporary_enchant":
        need(not any(re.match(r"^gear_(?:crit|haste|mastery|versatility)_rating=",
                              l.strip()) for l in lines),
             "V269_OIL_BASELINE_CANNOT_USE_GEAR_RATING_OVERRIDE")
        need(any(l.startswith("main_hand=") for l in lines),
             "V269_OIL_MAIN_HAND_ITEM_REQUIRED")
        if "/off_hand:" in token:
            need(any(l.startswith("off_hand=") for l in lines),
                 "V269_OIL_OFF_HAND_ITEM_REQUIRED")
    stable = [l for l in lines if l.partition("=")[0].strip() not in CONSUMABLES]
    # The five explicit options suppress class-specific defaults. No dynamic
    # potion/augmentation/food/flask/oil can contaminate either snapshot.
    def render(value):
        return "\n".join(stable + [f"{key}={value if key == kind else 'disabled'}"
                                    for key in CONSUMABLES]).rstrip() + "\n"
    base, active = render("disabled"), render(token)
    need(base != active, "V269_EFFECT_PROFILE_NOT_DISTINCT")
    return {
        "schema": SCHEMA, "kind": kind, "token": token,
        "source_profile_sha256": digest(profile.encode("utf8")),
        "baseline_profile_sha256": digest(base.encode("utf8")),
        "active_profile_sha256": digest(active.encode("utf8")),
        "baseline_profile": base, "active_profile": active,
        "other_consumables_explicitly_disabled": True,
        "native_calls": 0,
    }


def _player(raw, revision, kind, expected):
    need(type(raw) is bytes and 0 < len(raw) <= MAX_JSON,
         "V269_JSON2_SIZE_INVALID")
    try:
        doc = json.loads(raw)
    except (UnicodeError, ValueError) as exc:
        raise SnapshotBlocked("V269_NATIVE_JSON2_DECODE_ERROR") from exc
    need(type(doc) is dict and type(doc.get("git_revision")) is str and
         revision.startswith(doc["git_revision"]) and
         re.fullmatch(r"[0-9a-f]{7,40}", doc["git_revision"]) is not None,
         "V269_NATIVE_SOURCE_REVISION_DRIFT")
    sim = doc.get("sim")
    players = sim.get("players") if type(sim) is dict else None
    need(type(players) is list and len(players) == 1 and
         type(players[0]) is dict, "V269_ONE_PLAYER_JSON2_REQUIRED")
    player = players[0]
    need(player.get(kind) == expected, "V269_ACTUAL_SIMC_OPTION_DRIFT")
    cd = player.get("collected_data")
    bs = cd.get("buffed_stats") if type(cd) is dict else None
    stats = bs.get("stats") if type(bs) is dict else None
    need(type(stats) is dict, "V269_BUFFED_STATS_SNAPSHOT_MISSING")
    ratings = {}
    for stat in STATS:
        val = stats.get(stat, 0)
        need(type(val) in (int, float) and math.isfinite(val) and val >= 0,
             "V269_BUFFED_CHMV_NUMERIC_INVALID")
        ratings[stat] = float(val)
    # Zero CHMV values are valid. Only missing rating fields are invalid.
    need(any(stat in stats for stat in STATS),
         "V269_BUFFED_CHMV_SNAPSHOT_EMPTY")
    return player.get("name"), ratings


def compare(*, baseline_json2, active_json2, prepared,
            binary_sha256, simc_revision):
    """Attribute only the precombat numeric difference to ONE changed option."""
    need(type(prepared) is dict and prepared.get("schema") == SCHEMA and
         prepared.get("kind") in MEASURABLE and
         type(prepared.get("token")) is str and
         prepared.get("other_consumables_explicitly_disabled") is True and
         type(prepared.get("baseline_profile")) is str and
         type(prepared.get("active_profile")) is str and
         prepared.get("baseline_profile_sha256") == digest(
             prepared["baseline_profile"].encode("utf8")) and
         prepared.get("active_profile_sha256") == digest(
             prepared["active_profile"].encode("utf8")) and
         type(binary_sha256) is str and SHA.fullmatch(binary_sha256) is not None and
         type(simc_revision) is str and REV.fullmatch(simc_revision) is not None,
         "V269_PAIRED_NATIVE_INPUT_IDENTITY_REQUIRED")
    kind, token = prepared["kind"], prepared["token"]
    a, left = _player(baseline_json2, simc_revision, kind, "disabled")
    b, right = _player(active_json2, simc_revision, kind, token)
    need(type(a) is str and a == b, "V269_SAME_SIMC_PLAYER_REQUIRED")
    observed = {key: round(right[key] - left[key], 6) for key in STATS}
    rounded = {key: int(round(val)) for key, val in observed.items()}
    static = (any(x > 0.05 for x in observed.values()) and
              all(value >= -0.05 and abs(value - rounded[key]) <= 0.05
                  for key, value in observed.items()))
    status = ("OBSERVED_INTEGER_STATIC_CHMV_SNAPSHOT_DELTA"
              if static else "NO_CLEAN_STATIC_CHMV_DELTA_CONDITIONAL_EFFECT_PENDING")
    return {
        "schema": SCHEMA, "status": status,
        "kind": kind, "token": token, "player": a,
        "source_profile_sha256": prepared["source_profile_sha256"],
        "baseline_profile_sha256": prepared["baseline_profile_sha256"],
        "active_profile_sha256": prepared["active_profile_sha256"],
        "simc_revision": simc_revision, "binary_sha256": binary_sha256,
        "baseline_json2_sha256": digest(baseline_json2),
        "active_json2_sha256": digest(active_json2),
        "baseline_rating": left, "active_rating": right,
        "observed_rating_delta": observed,
        "static_CHMV_candidate": rounded if static else None,
        "source": "SIMC_JSON2_COLLECTED_DATA_BUFFED_STATS_SNAPSHOT",
        "condition_or_proc_effect_ignored": False,
        "J": None, "F": None, "O": None, "E": None,
        "source_option_verified": False,
        "budget_ownership_not_assigned_here": True,
        "environment_ready": False, "network_calls": 0,
    }

# P3-HE: read only SimC's actual two-stat result for ONE ordinary physical gem.
# This supplements (never relaxes) v266 raw-source and highest-quality owners.
GEM_SLOT_NAMES = frozenset((
    "head","neck","shoulders","back","chest","wrists","hands","waist",
    "legs","feet","finger1","finger2","main_hand","off_hand",
))


def prepare_ordinary_gem(*, profile, slot, ordinary_gem_id):
    """One difference: a single ordinary gem_id on an unchanged SimC item."""
    need(type(profile) is str and bool(profile.strip()) and
         len(profile.encode("utf8")) <= 4_000_000 and
         type(slot) is str and slot in GEM_SLOT_NAMES and
         type(ordinary_gem_id) is int and 0<ordinary_gem_id<=999999999 and
         ordinary_gem_id not in (240967,240983),
         "V269_GEM_PHYSICAL_INPUT_REQUIRED")
    need(not re.search(r"(?:^|,)gem_id=",profile,re.MULTILINE) and
         not re.search(r"(?m)^\\s*gear_(?:crit|haste|mastery|versatility)_rating=",profile) and
         not re.search(r"(?m)^\\s*(?:copy|profileset\\.|json2|output|html)=",profile),
         "V269_GEM_UNCONFOUNDED_NATIVE_INPUT_REQUIRED")
    lines=profile.splitlines(keepends=True)
    located=[(i,line) for i,line in enumerate(lines)
             if line.startswith(slot+"=")]
    need(len(located)==1 and re.search(r",id=[1-9][0-9]*",located[0][1])
         is not None, "V269_GEM_SOURCE_PHYSICAL_SLOT_REQUIRED")
    index,row=located[0]
    stable=row.rstrip("\r\n")
    ending=row[len(stable):]
    marker=",gem_id="+str(ordinary_gem_id)
    lines[index]=stable+marker+ending
    active="".join(lines)
    need(active.replace(marker,"",1)==profile,
         "V269_GEM_ONLY_ONE_PHYSICAL_CHANGE_REQUIRED")
    return {
        "schema":"v269_one_physical_ordinary_gem_native_pair_v1",
        "slot":slot,"ordinary_gem_id":ordinary_gem_id,
        "source_profile_sha256":digest(profile.encode("utf8")),
        "baseline_profile":profile,
        "active_profile":active,
        "baseline_profile_sha256":digest(profile.encode("utf8")),
        "active_profile_sha256":digest(active.encode("utf8")),
        "only_changed_option":"ONE_PHYSICAL_GEM_ID",
        "native_calls":0,"environment_ready":False,
    }


def _gem_native_player(raw, revision):
    need(type(raw) is bytes and 0<len(raw)<=MAX_JSON,
         "V269_GEM_JSON2_SIZE_REQUIRED")
    try:
        doc=json.loads(raw)
    except (UnicodeError,ValueError) as exc:
        raise SnapshotBlocked("V269_GEM_JSON2_DECODE_ERROR") from exc
    need(type(doc) is dict and type(doc.get("git_revision")) is str and
         re.fullmatch(r"[a-f0-9]{7,40}",doc["git_revision"]) is not None and
         revision.startswith(doc["git_revision"]),
         "V269_GEM_EXACT_SIMC_REVISION_REQUIRED")
    sim=doc.get("sim")
    players=sim.get("players") if type(sim) is dict else None
    need(type(players) is list and len(players)==1 and
         type(players[0]) is dict,
         "V269_GEM_SINGLE_PLAYER_JSON2_REQUIRED")
    player=players[0]
    gear=player.get("gear")
    cd=player.get("collected_data")
    bs=cd.get("buffed_stats") if type(cd) is dict else None
    stats=bs.get("stats") if type(bs) is dict else None
    need(type(gear) is dict and type(stats) is dict and
         all(key in stats and type(stats[key]) in (int,float)
             and math.isfinite(stats[key]) and stats[key]>=0
             for key in STATS),
         "V269_GEM_COMPLETE_BUFFED_CHMV_REQUIRED")
    ratings={key:float(stats[key]) for key in STATS}
    return player.get("name"),gear,ratings


def compare_ordinary_gem(*, prepared, baseline_json2, active_json2,
                         simc_revision, binary_sha256):
    """Source-only SimC delta. Caller still owns exact quality and official J."""
    need(type(prepared) is dict and prepared.get("schema")==
         "v269_one_physical_ordinary_gem_native_pair_v1" and
         prepared.get("only_changed_option")=="ONE_PHYSICAL_GEM_ID" and
         type(simc_revision) is str and REV.fullmatch(simc_revision) is not None and
         type(binary_sha256) is str and SHA.fullmatch(binary_sha256) is not None,
         "V269_GEM_PAIR_IDENTITY_REQUIRED")
    base=prepared.get("baseline_profile")
    active=prepared.get("active_profile")
    slot=prepared.get("slot")
    item=prepared.get("ordinary_gem_id")
    need(type(base) is str and type(active) is str and
         prepared.get("baseline_profile_sha256")==digest(base.encode("utf8")) and
         prepared.get("active_profile_sha256")==digest(active.encode("utf8")) and
         active.replace(",gem_id="+str(item),"",1)==base,
         "V269_GEM_INPUT_HASH_OR_SINGLE_DIFF_DRIFT")
    # Do not assume the CLI applied a written gem_id: inspect actual JSON2 gear.
    left,base_gear,base_stats=_gem_native_player(baseline_json2,simc_revision)
    right,active_gear,active_stats=_gem_native_player(active_json2,simc_revision)
    need(type(left) is str and left==right and
         set(base_gear)==set(active_gear) and slot in base_gear and
         all(type(base_gear[k]) is dict and
             type(active_gear[k]) is dict and
             type(base_gear[k].get("encoded_item")) is str and
             type(active_gear[k].get("encoded_item")) is str
             for k in base_gear),
         "V269_GEM_PLAYER_GEAR_IDENTITY_REQUIRED")
    marker=",gem_id="+str(item)
    for key in base_gear:
        b=base_gear[key]["encoded_item"]
        a=active_gear[key]["encoded_item"]
        need(not re.search(r"(?:^|,)gem_id=",b) and
             (a.replace(marker,"",1)==b if key==slot else a==b) and
             (a.count(marker)==1 if key==slot else marker not in a),
             "V269_GEM_ACTUAL_SIMC_GEAR_ITEM_DRIFT")
    delta={stat:round(active_stats[stat]-base_stats[stat],6)
           for stat in STATS}
    rounded={stat:int(round(value)) for stat,value in delta.items()}
    positives=[stat for stat in STATS if delta[stat]>0.05]
    clean=(len(positives)==2 and
           all(value>=-0.05 and abs(value-rounded[stat])<=0.05
               for stat,value in delta.items()) and
           all(rounded[stat]==0 for stat in STATS if stat not in positives))
    return {
        "schema":"v269_one_physical_ordinary_gem_native_delta_v1",
        "status":("SIMC_ORDINARY_GEM_TWO_STAT_OBSERVED_UNADMITTED" if clean
                  else "SIMC_ORDINARY_GEM_EFFECTIVE_RATING_PENDING"),
        "ordinary_gem_id":item,"physical_slot":slot,
        "baseline_profile_sha256":prepared["baseline_profile_sha256"],
        "active_profile_sha256":prepared["active_profile_sha256"],
        "baseline_json2_sha256":digest(baseline_json2),
        "active_json2_sha256":digest(active_json2),
        "binary_sha256":binary_sha256,"simc_revision":simc_revision,
        "observed_delta":delta,
        "simc_effective_two_stat_rating_unadmitted":(
            sum(rounded.values()) if clean else None),
        "simc_effective_two_stat_vector_unadmitted":(
            rounded if clean else None),
        "source":"SIMC_JSON2_ACTUAL_GEM_ID_AND_BUFFED_STATS",
        "native_case_attestation_by_caller_required":True,
        "same_effect_highest_quality_verified_here":False,
        "official_J":None,"environment_ready":False,
        "new_native_calls":0,"network_calls":0,
    }

