#!/usr/bin/env python3
"""P1: stage ONE source-grounded ordinary leather-feet variant (Native 0).

This is a side-by-side physical target334 SimC input, NOT a new equipment
optimizer or a modification to existing v098/v106 user plans and receipts.
Only Havoc feet changes: source 159327 -> same-season ordinary 268261.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import sys

import v055_simc_item_selection as selected
import v102_ordinary_armor_seed_pool as pool
import v132_dps_source_batch_smoke as pins
import v133_mid2_target_representative_preview as preview

SCHEMA="v137_isolated_same_season_leather_feet_variant_v1"
KEY="demonhunter/havoc"
LEVEL=334
OLD_ID=159327
NEW_ID=268261
ENCHANT="7963"


class VariantBlocked(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise VariantBlocked(reason)


def unique_slot_line(profile, slot):
    found=[line for line in profile.splitlines() if line.startswith(slot+"=")]
    need(len(found)==1,"V137_SLOT_NOT_UNIQUE:"+slot)
    return found[0]


def sha(data):
    return hashlib.sha256(data.encode("utf8")).hexdigest()


def stage():
    # v102 verifies exact Git blob and item/slot, not target-334 exact stats.
    pool.verify_pool()
    seed=pool.row("leather","feet",LEVEL)
    need(seed=={"slot":"feet","item_id":NEW_ID,
                "ilevel":LEVEL,"options":{}},
         "V137_LEATHER_FEET_SEED_CHANGED")
    need(pool.provenance("leather","feet")["source_kind"]=="ordinary",
         "V137_NOT_SAME_SEASON_ORDINARY")
    source_havoc=pins.validate_source(KEY)["source"]
    source_feral=pins.validate_source("druid/feral")["source"]
    need("id="+str(OLD_ID) in unique_slot_line(source_havoc,"feet")
         and "enchant_id="+ENCHANT in unique_slot_line(source_havoc,"feet"),
         "V137_HAVOC_SOURCE_FEET_CHANGED")
    need("id="+str(NEW_ID) in unique_slot_line(source_feral,"feet")
         and "enchant_id="+ENCHANT in unique_slot_line(source_feral,"feet"),
         "V137_FERAL_WITNESS_CHANGED")
    baseline_info,baseline=preview.draft(KEY,LEVEL)
    need(baseline_info["native_calls"]==0
         and len(baseline_info["four_tier_slots"])==4,
         "V137_BASE_PREVIEW_CONTRACT_CHANGED")
    old=selected.equipment_line("feet",OLD_ID,LEVEL,
                                {"enchant_id":ENCHANT})
    need(unique_slot_line(baseline,"feet")==old,
         "V137_BASELINE_FEET_OPTIONS_CHANGED")
    new=selected.equipment_line("feet",NEW_ID,LEVEL,
                                {"enchant_id":ENCHANT})
    lines=baseline.splitlines()
    need(lines.count(old)==1,"V137_BASELINE_FEET_NOT_EXACT")
    variant="\n".join(new if line==old else line for line in lines)+"\n"
    need(variant.replace(new,old)==baseline and variant!=baseline,
         "V137_MORE_THAN_FEET_CHANGED")
    need(unique_slot_line(variant,"feet")==new,
         "V137_VARIANT_FEET_NOT_EXACT")
    report={
        "schema":SCHEMA,
        "status":"STAGED_SINGLE_FEET_VARIANT_NATIVE_NOT_RUN",
        "spec":KEY,
        "ilevel":LEVEL,
        "changed_slots":["feet"],
        "old_item_id":OLD_ID,
        "new_item_id":NEW_ID,
        "target_slot_enchant_id":ENCHANT,
        "source_witnesses":["demonhunter/havoc","druid/feral"],
        "baseline_sha256":sha(baseline),
        "variant_sha256":sha(variant),
        "native_calls":0,
        "target_variant_native_verified":False,
        "exact_target_static_rating_verified":False,
        "user_default_profile_changed":False,
        "historical_dps_cache_changed":False,
        "APL_and_all_other_gear_rows_unchanged":True,
    }
    need(report["baseline_sha256"]==baseline_info["profile_sha256"],
         "V137_BASELINE_HASH_CHANGED")
    return report,baseline,variant


def put_once(path, data):
    # An existing output file is immutable and never silently overwritten.
    if path.exists():
        need(path.read_bytes()==data,
             "V137_OUTPUT_IDENTITY_DRIFT:"+path.name)
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)


def write_stage(folder):
    report,baseline,variant=stage()
    files={
        folder/"profiles"/"demonhunter__havoc__baseline.simc":
            baseline.encode("utf8"),
        folder/"profiles"/"demonhunter__havoc__leather_feet_268261.simc":
            variant.encode("utf8"),
        folder/"V137_LEATHER_FEET_VARIANT.json":
            (json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)
             +"\n").encode("utf8"),
    }
    # Preflight all outputs before writing a single new file.
    for path,data in files.items():
        if path.exists():
            need(path.read_bytes()==data,
                 "V137_OUTPUT_IDENTITY_DRIFT:"+path.name)
    for path,data in files.items():
        put_once(path,data)
    return report


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=pathlib.Path,
        default=pathlib.Path.home()/"SIMC_Secondary_Optimizer"/"ordinary_feet_v137")
    args=parser.parse_args(argv)
    try:
        report=write_stage(args.out)
        print(report["status"],"spec",report["spec"],
              "changed",report["changed_slots"],"Native",report["native_calls"])
        code=0
    except (VariantBlocked,ValueError,OSError) as exc:
        print("V137_BLOCKED",type(exc).__name__,str(exc),file=sys.stderr)
        code=3
    print("RESULT_DIR:",args.out.resolve())
    if os.name=="nt" and args.out.exists():
        try:os.startfile(str(args.out.resolve()))
        except OSError:pass
    return code


if __name__=="__main__":
    raise SystemExit(main())
