#!/usr/bin/env python3
"""Reusable exact SimC precombat gear delta for one selected weapon oil.

Uses the ORIGINAL v278 content-addressed two-case Native runner and SimC's
own player_t::init_initial_stats debug 'total gear stats'. Unlike v269's
buffed_stats, this reports item statistics before combat/talent multipliers.
This is an internal, source-only number; it never certifies physical item
applicability or admits an item into the user catalog.
"""
from __future__ import annotations

import hashlib
import pathlib
import re

import v278_sealed_simc_consumable_native_pair as native_pair

SCHEMA="v297_sealed_simc_oil_precombat_gear_delta_v1"
STATS={"Crit":"crit_rating","Haste":"haste_rating",
       "Mastery":"mastery_rating","Vers":"versatility_rating"}
CHMV=("crit_rating","haste_rating","mastery_rating","versatility_rating")
NUMBERS=re.compile(r"\b([A-Za-z][A-Za-z0-9]*)=(-?\d+(?:\.\d+)?)")
OIL=re.compile(r"(?:main_hand:[a-z0-9_]+|main_hand:disabled/off_hand:[a-z0-9_]+)\Z")
REV=re.compile(r"[0-9a-f]{40}\Z")
MAX_PROFILE=4_000_000
MAX_LOG=18_000_000

class OilGearBlocked(ValueError):
    pass

def need(ok,code):
    if not ok:raise OilGearBlocked(code)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def parse_total_gear(log,actor):
    """Extract one SimC initial-gear line; reject buffed-only JSON/logs."""
    need(type(log) is str and type(actor) is str and
         re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,90}",actor) is not None,
         "V297_TOTAL_GEAR_LOG_OR_ACTOR_INVALID")
    key="Player '"+actor+"' total gear stats:"
    lines=[row for row in log.splitlines() if key in row]
    need(len(lines)==1,"V297_EXPECTED_EXACT_ONE_SIMC_TOTAL_GEAR_LINE")
    fields={stat:float(value) for stat,value in NUMBERS.findall(
        lines[0].split(key,1)[1])}
    need(set(STATS)<=set(fields) and
         all(abs(v)<=1e8 and v==v for v in fields.values()),
         "V297_SIMC_PRECOMBAT_STAT_FIELDS_INVALID")
    return {"line":lines[0],"all_stats":fields}

def compare(*,off,on):
    need(type(off) is dict and type(on) is dict and
         type(off.get("all_stats")) is dict and
         type(on.get("all_stats")) is dict and
         set(off["all_stats"])==set(on["all_stats"]) and
         set(STATS)<=set(off["all_stats"]),
         "V297_SIMC_GEAR_STAT_IDENTITY_MISMATCH")
    difference={k:on["all_stats"][k]-v
                for k,v in off["all_stats"].items()}
    need(all(abs(v)<1e-7 for k,v in difference.items() if k not in STATS),
         "V297_NON_CHMV_GEAR_CHANGED")
    vector={}
    for abbrev,stat in STATS.items():
        value=difference[abbrev]
        need(value>=0 and abs(value-round(value))<1e-7,
             "V297_SIMC_STATIC_O_NONINTEGER_OR_NEGATIVE")
        vector[stat]=int(round(value))
    need(sum(vector.values())>0,"V297_SIMC_NO_POSITIVE_STATIC_O")
    return {stat:vector[stat] for stat in CHMV}

def _actor_from_v233(source):
    # The sealed G probe includes a single class=actor header, no copy.
    names=[line.split("=",1)[1] for line in source.splitlines()
           if re.match(r"^(?:death_knight|demon_hunter|druid|evoker|hunter|mage|monk|paladin|priest|rogue|shaman|warlock|warrior)=",line)]
    need(len(names)==1 and
         re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,90}",names[0]) is not None,
         "V297_ONE_ORIGINAL_SIMC_ACTOR_REQUIRED")
    return names[0]

def measure(*,stage_root,source_profile_path,binary,simc_revision,
            game_build,target_ilevel,oil_token,enchant_id,
            timeout_seconds=180):
    """Measure only a selected upstream v281 exact hand token, at most 2 Native.

    run_case() owns the old v278 cache/attempt receipts, so repeated
    identical binary/profile/season/token invocations consume 0 new Native.
    Missing binary or original source stays PENDING without an O=0 claim.
    """
    pending={"schema":SCHEMA,
             "status":"SIMC_PRECOMBAT_OIL_GEAR_SOURCE_OR_BINARY_PENDING",
             "static_CHMV_vector_unadmitted":None,
             "new_native_calls":0,"environment_ready":False,
             "weapon_and_hand_applicability_verified":False}
    if source_profile_path is None or binary is None:
        return pending
    need(type(simc_revision) is str and REV.fullmatch(simc_revision)
         and type(game_build) is str and bool(game_build)
         and type(target_ilevel) is int and 1<=target_ilevel<=1000
         and type(enchant_id) is int and enchant_id>0
         and type(oil_token) is str and OIL.fullmatch(oil_token)
         and type(timeout_seconds) is int and 1<=timeout_seconds<=900,
         "V297_OIL_MEASUREMENT_IDENTITY_INVALID")
    root=pathlib.Path(stage_root).resolve(strict=True)
    profile=pathlib.Path(source_profile_path).resolve(strict=True)
    exe=pathlib.Path(binary).expanduser().resolve(strict=True)
    need(root.is_dir() and not root.is_symlink()
         and profile.is_file() and not profile.is_symlink()
         and profile.is_relative_to(root)
         and 0<profile.stat().st_size<=MAX_PROFILE
         and exe.is_file() and not exe.is_symlink(),
         "V297_ORIGINAL_PROFILE_OR_BINARY_NOT_SEALED")
    source=profile.read_text(encoding="utf8")
    actor=_actor_from_v233(source)
    lines=source.splitlines()
    hand=("off_hand" if "/off_hand:" in oil_token else "main_hand")
    weapon_lines=[x for x in lines if x.startswith(hand+"=")]
    need(len(weapon_lines)==1,
         "V297_SELECTED_WEAPON_NOT_IN_ORIGINAL_PROFILE")
    weapon_id=re.search(r"(?:^|,)id=(\d+)(?:,|$)",
                        weapon_lines[0])
    weapon_ilvl=re.search(r"(?:^|,)ilevel=(\d+)(?:,|$)",
                          weapon_lines[0])
    need(weapon_id is not None and weapon_ilvl is not None
         and int(weapon_id.group(1))>0
         and int(weapon_ilvl.group(1))==target_ilevel,
         "V297_SELECTED_ORIGINAL_WEAPON_ID_OR_ILEVEL_DRIFT")
    need(any(line.startswith("main_hand=") for line in lines)
         and ("/off_hand:" not in oil_token or
              any(line.startswith("off_hand=") for line in lines))
         and not any(line.startswith(("temporary_enchant=",
             "flask=","food=","potion=","augmentation=",
             "gear_crit_rating=","gear_haste_rating=",
             "gear_mastery_rating=","gear_versatility_rating=",
             "json2=","iterations=","threads=","debug=",
             "profileset.","copy=")) for line in lines),
         "V297_ORIGINAL_PHYSICAL_GEAR_REQUIRED")
    source_sha=digest(profile.read_bytes())
    binary_sha=native_pair.file_sha(exe)
    options=source.rstrip()+"\n"+"".join(
        name+"=disabled\n" for name in
        ("flask","food","potion","augmentation"))
    inputs={
        "baseline":options+"temporary_enchant=disabled\ndebug=1\n",
        "active":options+"temporary_enchant="+oil_token+"\ndebug=1\n"}
    outcomes=[]
    new_calls=0
    for variant in ("baseline","active"):
        case=native_pair.run_case(
            stage_root=root,profile=inputs[variant],
            source_identity=source_sha,
            binary=exe,binary_sha256=binary_sha,
            revision=simc_revision,variant=variant,
            timeout_seconds=timeout_seconds)
        new_calls+=case["new_native_calls"]
        outcomes.append(case)
        if case["receipt"]["status"]!="NATIVE_JSON2_CAPTURED":
            return {**pending,"status":"SIMC_PRECOMBAT_NATIVE_FAILED_NO_RETRY",
                    "failed_variant":variant,
                    "native_status":case["receipt"]["status"],
                    "native_log_excerpt":native_pair.log_excerpt(
                        case["folder"]),
                    "new_native_calls":new_calls}
    reports=[]
    for case in outcomes:
        path=case["folder"]/"simc.log"
        need(path.is_file() and path.stat().st_size<=MAX_LOG,
             "V297_SIMC_GEAR_DEBUG_LOG_MISSING_OR_TOO_LARGE")
        log=path.read_text("utf8",errors="replace")
        need("invalid temporary enchant" not in log.lower(),
             "V297_SIMC_OIL_TOKEN_IGNORED")
        reports.append(parse_total_gear(log,actor))
    vector=compare(off=reports[0],on=reports[1])
    receipt_shas=[native_pair.file_sha(x["folder"]/"receipt.json")
                  for x in outcomes]
    return {**pending,
        "status":"SIMC_PRECOMBAT_TOTAL_GEAR_STATIC_NUMBER_SOURCE_ONLY",
        "simc_revision":simc_revision,"game_build":game_build,
        "target_ilevel":target_ilevel,
        "selected_hand":hand,
        "representative_weapon_id":int(weapon_id.group(1)),
        "enchant_id":enchant_id,"simc_input_token":oil_token,
        "binary_sha256":binary_sha,
        "source_profile_sha256":source_sha,
        "static_CHMV_vector_unadmitted":vector,
        "native_case_receipt_sha256":receipt_shas,
        "precombat_total_gear_lines":[x["line"] for x in reports],
        "talent_buffed_stats_not_used":True,
        "new_native_calls":new_calls}
