#!/usr/bin/env python3
"""v233: deterministic SimC-only representative G probe input.

One requested DPS class/spec, no current equipment, trinkets, gems, flask,
oils, gear-rating injection, or old seasonal source. Rebuild v232 from pinned
v229/v231 data rather than trusting arbitrary candidate JSON edits.
Result is a *physical measurement probe*, not a new-season budget or profile
guaranteed accepted by the actual SimC binary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re

try:
    from . import v229_simc_only_source_seed as seed
    from . import v231_simc_tier_item_join as tier_join
    from . import v232_simc_only_ordinary_representative as ordinary
    from . import v143_specialization_contracts as contracts
except ImportError:
    import v229_simc_only_source_seed as seed
    import v231_simc_tier_item_join as tier_join
    import v232_simc_only_ordinary_representative as ordinary
    import v143_specialization_contracts as contracts

SCHEMA="v233_simc_source_only_native_G_probe_input_v1"
RACE=re.compile(r"[a-z][a-z_]{2,39}\Z")
TALENTS=re.compile(r"[A-Za-z0-9_/:.,+\\-]{1,4096}\Z")
NAME="simc_source_g_probe"


class ProbeBlocked(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise ProbeBlocked(reason)


def build(*, source_directory, tier_candidate, representative_candidate,
          race, level, talents=None):
    need(type(representative_candidate) is dict and
         representative_candidate.get("schema")==ordinary.SCHEMA and
         representative_candidate.get("status")==
             "SIMC_SOURCE_PHYSICAL_CANDIDATE_NOT_ACTUAL_SEASON_PROOF" and
         representative_candidate.get("receipt_sha256")==seed.digest(
             seed.canonical({k:v for k,v in representative_candidate.items()
                             if k!="receipt_sha256"}).encode("utf8")),
         "V233_SOURCE_CANDIDATE_INVALID_OR_CHANGED")
    window=representative_candidate.get("source_item_level_window")
    need(type(window) is dict and
         type(window.get("distance")) is int,
         "V233_CANDIDATE_SOURCE_SEARCH_WINDOW_MISSING")
    try:
        rebuilt=ordinary.find_candidate(
            seed_directory=source_directory,
            tier_candidate=tier_candidate,
            target_ilevel=representative_candidate["target_ilevel"],
            max_source_distance=window["distance"])
    except (ordinary.SourceRepresentativeBlocked,ValueError,KeyError,
            TypeError,OSError) as exc:
        raise ProbeBlocked("V233_REGENERATED_SIMC_SOURCE_REJECTED") from exc
    need(rebuilt==representative_candidate,
         "V233_REPRESENTATIVE_SOURCE_CANDIDATE_REPLAY_DRIFT")
    character=rebuilt["character"]
    class_name=character["class"]
    spec_name=character["spec"]
    contract=contracts.lookup(class_name,spec_name)
    need(contract is not None and len(contracts.CONTRACTS)==26,
         "V233_26_DPS_CONTRACT_REQUIRED")
    need(type(race) is str and RACE.fullmatch(race) is not None and
         (contract["allowed_races"] is None or
          race in contract["allowed_races"]),
         "V233_RACE_INVALID_OR_UNSUPPORTED")
    need(type(level) is int and 1<=level<=100,
         "V233_CHARACTER_LEVEL_INVALID")
    need(talents is None or
         (type(talents) is str and TALENTS.fullmatch(talents) is not None),
         "V233_TALENTS_FORMAT_INVALID")
    slots=rebuilt["selected_G_slot_ids"]
    need(type(slots) is dict and len(slots) in (13,14) and
         all(type(i) is int and i>0 for i in slots.values()) and
         len(slots)==len(set(slots.values())) and
         set(slots)<=set(contracts.SLOT_ORDER) and
         not set(slots)&{"trinket1","trinket2"},
         "V233_REPRESENTATIVE_G_SLOTS_INVALID")
    ilvl=rebuilt["target_ilevel"]
    lines=["# v233 generated, SimC-only physical G measurement candidate",
           class_name+"="+NAME,
           "level="+str(level),"race="+race,"spec="+spec_name,
           "position="+contract["position"]]
    if talents is not None:
        lines.append("talents="+talents)
    for slot in contracts.SLOT_ORDER:
        if slot not in slots:continue
        iid=slots[slot]
        lines.append(f"{slot}=simc_source_{iid},id={iid},ilevel={ilvl},source=local")
    profile="\n".join(lines)+"\n"
    raw=profile.encode("utf8")
    output={
        "schema":SCHEMA,
        "status":"EXACT_SIMC_SOURCE_PROFILE_PREPARED_NOT_EXECUTED",
        "source_candidate_receipt_sha256":rebuilt["receipt_sha256"],
        "source_tier_receipt_sha256":rebuilt["source_tier_receipt_sha256"],
        "source_seed_receipt_sha256":rebuilt["source_seed_receipt_sha256"],
        "simc_revision":rebuilt["simc_revision"],
        "game_build_declared_by_simc_source":rebuilt["game_build"],
        "class":class_name,"spec":spec_name,"race":race,
        "level":level,"talents_supplied":talents is not None,
        "target_ilevel":ilvl,
        "selected_G_slot_ids":{k:slots[k] for k in sorted(slots)},
        "physical_profile_sha256":hashlib.sha256(raw).hexdigest(),
        "physical_profile_bytes":len(raw),
        "native_calls":0,"G":None,"J":None,"F":None,"O":None,
        "B":None,"T":None,"environment_ready":False,
        "current_season_membership_certified":False,
    }
    return profile,{**output,"receipt_sha256":seed.digest(
        seed.canonical(output).encode("utf8"))}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed-dir",type=pathlib.Path,required=True)
    p.add_argument("--tier-candidate",type=pathlib.Path,required=True)
    p.add_argument("--representative-candidate",type=pathlib.Path,required=True)
    p.add_argument("--race",required=True)
    p.add_argument("--level",type=int,required=True)
    p.add_argument("--talents",default=None)
    p.add_argument("--output-dir",type=pathlib.Path,required=True)
    a=p.parse_args(argv)
    tier=json.loads(a.tier_candidate.read_text("utf8"))
    candidate=json.loads(a.representative_candidate.read_text("utf8"))
    profile,receipt=build(
        source_directory=a.seed_dir,tier_candidate=tier,
        representative_candidate=candidate,race=a.race,
        level=a.level,talents=a.talents)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    outputs=((a.output_dir/"source_G_probe.simc",profile.encode("utf8")),
             (a.output_dir/"v233_receipt.json",
              (json.dumps(receipt,ensure_ascii=False,sort_keys=True,
                         indent=2)+"\n").encode("utf8")))
    for path,payload in outputs:
        need(not path.exists() or path.read_bytes()==payload,
             "V233_EXISTING_PROFILE_OR_RECEIPT_IMMUTABLE_DRIFT")
    for path,payload in outputs:
        if not path.exists():path.write_bytes(payload)
    print("V233_SOURCE_ONLY_PROFILE_PREPARED",receipt["class"],
          receipt["spec"],len(receipt["selected_G_slot_ids"]),
          "NATIVE_NOT_EXECUTED")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
