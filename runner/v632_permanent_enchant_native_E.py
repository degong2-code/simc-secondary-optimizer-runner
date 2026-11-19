#!/usr/bin/env python3
"""One source-bound permanent-enchant E measurement, no independent engine.

Use the existing v278 two-case immutable Native cache and v297 SimC
initial total-gear-stat parser. This is a single physical *reference item*
comparison: it never certifies proc mechanics, all hand/slot combinations,
quality, or other IDs with similar scaling coefficients. No gear_* overrides.
Only v216's already sealed v213/v230/v583 source owner can authorize the
measurement's eventual Policy A consumption.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re

import v278_sealed_simc_consumable_native_pair as native_cases
import v297_sealed_simc_oil_gear_delta as initial_gear

SCHEMA="v632_original_simc_permanent_enchant_static_E_pair_v1"
REV=re.compile(r"[0-9a-f]{40}\Z")
SLOTS=frozenset(("head","neck","shoulders","back","chest","wrist",
                 "hands","waist","legs","feet","finger1","finger2",
                 "main_hand","off_hand"))
GEAR_OVERRIDE=("gear_crit_rating=","gear_haste_rating=",
               "gear_mastery_rating=","gear_versatility_rating=")
EXCLUDE=("flask=","food=","potion=","augmentation=",
         "temporary_enchant=","json2=","iterations=","threads=",
         "debug=","profileset.","copy=")
ITEM_ID=re.compile(r"(?:^|,)id=(\d+)(?:,|$)")
ILEVEL=re.compile(r"(?:^|,)ilevel=(\d+)(?:,|$)")
MAX_PROFILE=4_000_000
MAX_LOG=18_000_000


class EnchantEBlocked(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise EnchantEBlocked(code)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def prepare(source, *, slot, item_id, enchant_id, target_ilevel):
    """Only the selected physical row changes; all other equipment remains."""
    need(type(source) is str and 0<len(source.encode("utf8"))<=MAX_PROFILE
         and type(slot) is str and slot in SLOTS
         and type(item_id) is int and item_id>0
         and type(enchant_id) is int and enchant_id>0
         and type(target_ilevel) is int and 1<=target_ilevel<=1000,
         "V632_SOURCE_OR_SELECTED_SCOPE_INVALID")
    lines=source.splitlines()
    need(not any(line.startswith(GEAR_OVERRIDE+EXCLUDE)
                 for line in lines),
         "V632_UNBUFFED_SOURCE_WITHOUT_OVERRIDES_REQUIRED")
    chosen=[i for i,line in enumerate(lines)
            if line.startswith(slot+"=")]
    need(len(chosen)==1 and
         sum(line.startswith(slot+"=") for line in lines)==1,
         "V632_SINGLE_EXACT_SLOT_REQUIRED")
    index=chosen[0]
    physical=lines[index]
    actual_id=ITEM_ID.search(physical)
    level=ILEVEL.search(physical)
    need("source=local" in physical
         and actual_id is not None and int(actual_id.group(1))==item_id
         and level is not None and int(level.group(1))==target_ilevel
         and not any(piece.startswith(("enchant=","enchant_id="))
                     for piece in physical.split(",")),
         "V632_EXACT_UNENCHANTED_PHYSICAL_ITEM_REQUIRED")
    base=source.rstrip()+"\n"
    active_lines=list(lines)
    active_lines[index]=physical+",enchant_id="+str(enchant_id)
    on="\n".join(active_lines)+"\n"
    need(len(on.splitlines())==len(base.splitlines())
         and sum(a!=b for a,b in zip(base.splitlines(),on.splitlines()))==1,
         "V632_ONLY_ONE_ENCHANT_FIELD_MAY_CHANGE")
    # SimC owns actual gear effects. Buffs/oils are absent from this
    # v233 stage; debug=1 exposes its own unbuffed initial gear rating.
    return {"baseline":base+"debug=1\n",
            "active":on+"debug=1\n",
            "profile_sha256":digest(source.encode("utf8")),
            "base_profile_sha256":digest(base.encode("utf8")),
            "selected_row_sha256":digest(physical.encode("utf8"))}


def _player_gear(raw,revision):
    try:
        obj=json.loads(raw)
        need(obj.get("report_version")=="2.0.0" and
             str(obj.get("git_revision","")).startswith(revision[:7]),
             "V632_SIMC_JSON2_REVISION_DRIFT")
        players=(obj.get("sim") or {}).get("players") or []
        need(len(players)==1,"V632_SIMC_ONE_PLAYER_REQUIRED")
        return players[0].get("gear") or {}
    except (ValueError,KeyError,TypeError,AttributeError) as exc:
        raise EnchantEBlocked("V632_SIMC_JSON2_GEAR_INVALID") from exc


def verify_only_target_changed(off,on,*,slot,item_id,enchant_id,
                               simc_revision):
    before=_player_gear(off,simc_revision)
    after=_player_gear(on,simc_revision)
    need(set(before)==set(after) and slot in before,
         "V632_SIMC_PHYSICAL_GEAR_SET_DRIFT")
    need(all(before[key]==after[key] for key in before if key!=slot),
         "V632_SIMC_OTHER_PHYSICAL_ITEMS_CHANGED")
    b=before[slot].get("encoded_item","")
    a=after[slot].get("encoded_item","")
    need(("enchant_id="+str(enchant_id)) in a.split(",")
         and ("enchant_id="+str(enchant_id)) not in b.split(","),
         "V632_SELECTED_ENCHANT_NOT_APPLIED_IN_JSON2")
    for pattern,expected in ((ITEM_ID,item_id),(ILEVEL,None)):
        x=pattern.search(b);y=pattern.search(a)
        need(x is not None and y is not None
             and x.group(1)==y.group(1)
             and (expected is None or int(x.group(1))==expected),
             "V632_SELECTED_PHYSICAL_ITEM_DRIFT")
    return True


def measure(*,stage_root,source_profile_path,binary,simc_revision,
            game_build,target_ilevel,slot,item_id,enchant_id,
            timeout_seconds=180):
    """At most two source-bound Native cases; cache hits need zero calls."""
    pending={"schema":SCHEMA,
             "status":"SIMC_PERMANENT_ENCHANT_PROFILE_OR_BINARY_PENDING",
             "fixed_E_unadmitted":None,"new_native_calls":0,
             "user_selectable":False,"budget_owner_approved":False,
             "gameplay_effect_certified":False}
    if binary is None or source_profile_path is None:
        return pending
    need(type(simc_revision) is str and REV.fullmatch(simc_revision)
         and type(game_build) is str and bool(game_build)
         and type(timeout_seconds) is int and 1<=timeout_seconds<=900,
         "V632_SIMC_SOURCE_IDENTITY_INVALID")
    root=pathlib.Path(stage_root).resolve(strict=True)
    path=pathlib.Path(source_profile_path).resolve(strict=True)
    exe=pathlib.Path(binary).resolve(strict=True)
    need(root.is_dir() and not root.is_symlink()
         and path.is_file() and not path.is_symlink()
         and path.is_relative_to(root)
         and 0<path.stat().st_size<=MAX_PROFILE
         and exe.is_file() and not exe.is_symlink(),
         "V632_ORIGINAL_V233_PROFILE_OR_BINARY_REQUIRED")
    raw=path.read_bytes()
    try:
        source=raw.decode("utf8")
    except UnicodeError as exc:
        raise EnchantEBlocked("V632_SIMC_SOURCE_PROFILE_UTF8_INVALID") from exc
    inputs=prepare(source,slot=slot,item_id=item_id,
                   enchant_id=enchant_id,target_ilevel=target_ilevel)
    actor=initial_gear._actor_from_v233(source)
    binary_sha=native_cases.file_sha(exe)
    results=[]
    new_calls=0
    for variant in ("baseline","active"):
        case=native_cases.run_case(
            stage_root=root,profile=inputs[variant],
            source_identity=inputs["profile_sha256"],
            binary=exe,binary_sha256=binary_sha,
            revision=simc_revision,variant=variant,
            timeout_seconds=timeout_seconds)
        results.append(case)
        new_calls+=case["new_native_calls"]
        if case["receipt"]["status"]!="NATIVE_JSON2_CAPTURED":
            return {**pending,"status":"SIMC_ENCHANT_NATIVE_CASE_FAILED_NO_AUTO_RETRY",
                    "failed_variant":variant,
                    "native_status":case["receipt"]["status"],
                    "native_log_excerpt":native_cases.log_excerpt(case["folder"]),
                    "new_native_calls":new_calls}
    try:
        verify_only_target_changed(
            (results[0]["folder"]/"native.json").read_bytes(),
            (results[1]["folder"]/"native.json").read_bytes(),
            slot=slot,item_id=item_id,enchant_id=enchant_id,
            simc_revision=simc_revision)
        parsed=[]
        for case in results:
            log=case["folder"]/"simc.log"
            need(log.is_file() and not log.is_symlink()
                 and 0<log.stat().st_size<=MAX_LOG,
                 "V632_SIMC_INITIAL_GEAR_LOG_MISSING")
            parsed.append(initial_gear.parse_total_gear(
                log.read_text("utf8",errors="replace"),actor))
        E=initial_gear.compare(off=parsed[0],on=parsed[1])
    except (EnchantEBlocked,initial_gear.OilGearBlocked,
            ValueError,KeyError,TypeError,UnicodeError,OSError) as exc:
        # A malformed/impossible observation must never turn into E=0.
        # Count actual already-spent Native cases and preserve cached
        # before/after receipts; do not trigger a retry or item admission.
        return {**pending,
            "status":"SIMC_ENCHANT_STATIC_E_MEASUREMENT_PENDING",
            "reason":str(exc).split(":",1)[0],
            "native_case_receipt_sha256":[
                native_cases.file_sha(case["folder"]/"receipt.json")
                for case in results],
            "new_native_calls":new_calls}
    need(set(E)==set(initial_gear.CHMV) and
         all(type(n) is int and 0<=n<=100000 for n in E.values()),
         "V632_EXACT_E_VECTOR_REQUIRED")
    return {**pending,
        "status":"SIMC_PERMANENT_ENCHANT_EXACT_INITIAL_GEAR_E_UNADMITTED",
        "game_build":game_build,"simc_revision":simc_revision,
        "binary_sha256":binary_sha,
        "source_profile_sha256":inputs["profile_sha256"],
        "selected_profile_slot_sha256":inputs["selected_row_sha256"],
        "slot":slot,"item_id":item_id,"enchant_id":enchant_id,
        "target_ilevel":target_ilevel,
        "fixed_E_unadmitted":E,
        "native_case_receipt_sha256":[
            native_cases.file_sha(case["folder"]/"receipt.json")
            for case in results],
        "unbuffed_initial_gear_stats_from_simc":True,
        "gear_override_used":False,
        "only_selected_item_enchant_changed":True,
        "new_native_calls":new_calls}
