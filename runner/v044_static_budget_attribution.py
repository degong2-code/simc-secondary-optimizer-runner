#!/usr/bin/env python3
"""v044: offline native-evidence attribution for *static* CHMV budget only.

Reads a previously completed pinned v042 SimC artifact. Never runs SimC, never
treats JSON2 gear stats as a universally calibrated G, and does not decide
the v1.0 vs oil-inclusive budget-policy question.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re
import sys
import zipfile
from io import BytesIO

SCHEMA = "v044_static_gear_budget_attribution_v1"
REV = "7bc10711b5"
STATS = ("crit_rating", "haste_rating", "mastery_rating", "versatility_rating")
TRINKETS = ("trinket1", "trinket2")
SOURCE = "v042/native/input.simc"
NATIVE = "v042/native/result.json"
ARCHIVE_SHA = "eea36762a1d21db5e9ad5bcf72c6c94bff4d122fee28f3ea83cd700120b9dc7f"
INPUT_SHA = "02f45fb88772ed8fd26b2044866a2d3a7c3417e0ca928ffe460b608cf541f56e"
NATIVE_SHA = "4367cfa9e911190af8e8441f44378cb0efab4d018fd059677e01fa054636ed55"
EXPECTED_HEAD = ("id=271564", "redirected_base_stats=271874", "bonus_id=13846", "gem_id=240967")
SLOTS = ("head","neck","shoulders","chest","waist","legs","feet","wrists",
         "hands","finger1","finger2","trinket1","trinket2","back","main_hand")

class Blocked(ValueError):
    pass

def need(ok, why):
    if not ok: raise Blocked(why)

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def _settings(source: str) -> dict:
    keys = ("gear_crit_rating","gear_haste_rating","gear_mastery_rating",
            "gear_versatility_rating","flask","temporary_enchant")
    found = {}
    for line in source.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        key, val = line.split("=", 1)
        if key in keys:
            need(key not in found, "DUPLICATE_INPUT_SETTING:" + key)
            found[key] = val
    need(set(found) == set(keys), "MISSING_INPUT_SETTINGS")
    out={}
    for name in keys[:4]:
        need(re.fullmatch(r"[0-9]+",found[name]) is not None,"INPUT_RATING_NOT_INTEGER")
        out[name.replace("gear_","")] = int(found[name])
    return {"gear_override":out,"flask":found["flask"],"temporary_enchant":found["temporary_enchant"]}

def analyze(input_bytes: bytes, native_bytes: bytes) -> dict:
    need(type(input_bytes) is bytes and type(native_bytes) is bytes, "INPUT_BYTES_REQUIRED")
    need(sha(input_bytes)==INPUT_SHA and sha(native_bytes)==NATIVE_SHA, "NATIVE_PAIR_SHA_MISMATCH")
    src = input_bytes.decode("utf-8")
    opts = _settings(src)
    raw = json.loads(native_bytes)
    need(raw.get("report_version")=="2.0.0" and
         str(raw.get("git_revision","")).startswith(REV), "NATIVE_VERSION_INVALID")
    players = raw["sim"]["players"]
    need(type(players) is list and len(players)==1, "PLAYER_COUNT_INVALID")
    player=players[0]
    gear=player["gear"]
    need(type(gear) is dict and set(gear)==set(SLOTS), "GEAR_SLOT_SET_CHANGED")
    item_vectors={}; totals={s:0 for s in STATS}; trinkets={s:0 for s in STATS}
    gems={}
    for slot in SLOTS:
        item=gear[slot]
        need(item.get("ilevel")==334,"UNEXPECTED_ITEM_LEVEL:"+slot)
        encoded=item.get("encoded_item","")
        need(isinstance(encoded,str) and encoded,"MISSING_ENCODED_ITEM:"+slot)
        vec={}
        for stat in STATS:
            n=item.get(stat,0)
            need(type(n) is int and 0<=n<=100000,"INVALID_ITEM_STAT:"+slot+":"+stat)
            vec[stat]=n
            if slot in TRINKETS: trinkets[stat]+=n
            else: totals[stat]+=n
        item_vectors[slot]=vec
        matches=re.findall(r"(?:^|,)gem_id=([0-9/]+)(?=,|$)",encoded)
        need(len(matches)<=1,"AMBIGUOUS_GEM_ENTRY:"+slot)
        gems[slot] = matches[0].split("/") if matches else []
    head=gear["head"]["encoded_item"]
    need(all(head.count(k)==1 for k in EXPECTED_HEAD), "PINNED_HEAD_IDENTITY_MISMATCH")
    need(item_vectors["head"]==dict(zip(STATS,(0,0,201,0))),
         "HEAD_FIXED_STAT_CHANGED")
    need(gems["head"]==["240967"],"SPECIAL_GEM_CHANGED")
    other_gems=[id_ for slot,gem_ids in gems.items() if slot!="head" for id_ in gem_ids]
    need(len(other_gems)==6,"SIX_OTHER_GEMS_NOT_RETAINED")
    need(all(not gems[t] for t in TRINKETS),"TRINKET_GEM_OUT_OF_SCOPE")
    observed=player["collected_data"]["buffed_stats"]["stats"]
    applied={}
    for stat in STATS:
        val=observed.get(stat)
        need(type(val) in (float,int) and abs(val-round(val))<1e-8,
             "INVALID_FINAL_RATING:"+stat)
        applied[stat]=int(round(val))
    offsets={s:applied[s]-opts["gear_override"][s] for s in STATS}
    need(opts["flask"]==player.get("flask") and
         opts["temporary_enchant"]==player.get("temporary_enchant"),
         "CONSUMABLE_IDENTITY_CHANGED")
    return {
        "schema":SCHEMA,
        "status":"PASS_OFFLINE_NATIVE_OBSERVATION_ONLY_NOT_CALIBRATED_BUDGET",
        "test_success":True, "product_code_integrated":False,
        "official_policy_promoted":False,
        "source_sha256":{"input":sha(input_bytes),"native_json2":sha(native_bytes)},
        "scope":"PINNED_V042_ONE_PROFILE_334_NOT_ALL_ITEMS",
        "static_nontrinket_gear_slots":{s:item_vectors[s] for s in SLOTS if s not in TRINKETS},
        "static_nontrinket_gear_sum":totals,
        "static_nontrinket_gear_sum_all_stats":sum(totals.values()),
        "trinket_gear_secondary_external":trinkets,
        "gem_ids":{"special_head":gems["head"],"other_six":other_gems},
        "simc_input_gear_override_rating":opts["gear_override"],
        "simc_final_observed_rating":applied,
        "final_minus_gear_override":offsets,
        "flask_name":opts["flask"],"temporary_enchant_name":opts["temporary_enchant"],
        "hypothetical_v1_0_arithmetic_if_observed_slots_equal_G":{
            "J_from_policy_not_native_verified":138,
            "F_from_policy_not_causal_verified":165,
            "conditional_T":sum(totals.values())+138+165,
            "not_product_budget":True},
        "known_mismatches_not_reconciled":{
            "reported_v020_G":2847,
            "observed_v042_gear_slots_minus_reported_v020_G":sum(totals.values())-2847,
            "reported_reference_T":3184,
            "reported_other_T":3182,
            "v1_0_vs_oil_candidate_formula":"UNRESOLVED",
            "relative_scenario_provenance_identical":False,
            "simc_flask_plus165_causality_proven":False},
        "manual_total_3284_is_itemlevel_verified":False,
        "actual_334_G_verified_for_product":False,
        "actual_334_T_verified_for_product":False,
        "v016_to_github_code_lineage_verified":False,
        "product_admission":"BLOCKED_PROVENANCE_AND_ATTRIBUTION",
        "native_simc_calls":0
    }

def inspect_archive(blob:bytes):
    need(type(blob) is bytes and sha(blob)==ARCHIVE_SHA, "ARCHIVE_SHA_MISMATCH")
    with zipfile.ZipFile(BytesIO(blob)) as f:
        names=f.namelist()
        need(len(names)==len(set(names)) and len(names)<=15, "ZIP_ENTRIES_INVALID")
        need(all(not n.startswith("/") and ".." not in pathlib.PurePosixPath(n).parts for n in names),
             "ZIP_UNSAFE_PATH")
        need(SOURCE in names and NATIVE in names, "REQUIRED_EVIDENCE_MISSING")
        need(f.getinfo(SOURCE).file_size<10000 and f.getinfo(NATIVE).file_size<2000000,
             "EVIDENCE_TOO_LARGE")
        need(f.testzip() is None,"ZIP_CRC_FAILURE")
        proof=analyze(f.read(SOURCE),f.read(NATIVE))
    proof["source_sha256"]["artifact_zip"]=sha(blob)
    return proof

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--artifact",type=pathlib.Path,required=True)
    p.add_argument("--output",type=pathlib.Path,required=True)
    args=p.parse_args(argv)
    try:
        proof=inspect_archive(args.artifact.read_bytes())
    except Exception as exc:
        proof={"schema":SCHEMA,"status":"BLOCKED","error":type(exc).__name__+":"+str(exc),
            "test_success":False,"product_code_integrated":False,"official_policy_promoted":False,
            "native_simc_calls":0}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(proof,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("V044",proof["status"],"native_calls",0)
    return 0 if proof["test_success"] else 3

if __name__=="__main__":
    sys.exit(main())
