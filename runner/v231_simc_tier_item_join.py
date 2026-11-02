#!/usr/bin/env python3
"""v231: one spec's five SimC tier item IDs, joined to exact item_data rows.

Use only v229's immutable SimC-generated source receipt, v230's exact item
metadata, and existing season-independent specialization/armor contracts.
This does not infer which set option is the current season from names/IDs;
the caller must supply an independently sourced option token. The produced
physical class tier is a candidate for v169, NOT a certified 13-class season
tier roster or a real Native G measurement.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

try:
    from . import v229_simc_only_source_seed as seed
    from . import v230_simc_item_metadata as itemdata
    from . import v169_source_first_representative_stage as representative
except ImportError:
    import v229_simc_only_source_seed as seed
    import v230_simc_item_metadata as itemdata
    import v169_source_first_representative_stage as representative

SCHEMA="v231_simc_source_only_class_tier_candidate_v1"
CLASS_ID={"warrior":1,"paladin":2,"hunter":3,"rogue":4,
          "priest":5,"deathknight":6,"shaman":7,"mage":8,
          "warlock":9,"monk":10,"druid":11,"demonhunter":12,"evoker":13}
INV_SLOT={1:"head",3:"shoulders",5:"chest",20:"chest",
          10:"hands",7:"legs"}
FULL=frozenset(("head","shoulders","chest","hands","legs"))
TOKEN=re.compile(r"[a-z][a-z0-9_]{2,70}\Z")


class TierCandidateBlocked(ValueError):pass


def need(ok,code):
    if not ok:raise TierCandidateBlocked(code)


def read_receipt(root):
    doc=json.loads(seed.bounded_read(Path(root)/seed.RECEIPT,2_000_000))
    need(type(doc) is dict and doc.get("schema")==seed.SCHEMA
         and doc.get("provenance_tree_blob_authenticated") is True
         and doc.get("environment_ready") is False and
         doc.get("G") is None and doc.get("J") is None,
         "V231_FIRST_PARTY_PINNED_SEED_REQUIRED")
    clean={k:v for k,v in doc.items() if k!="receipt_sha256"}
    need(doc.get("receipt_sha256")==seed.digest(
        seed.canonical(clean).encode("utf8")),
         "V231_SEED_RECEIPT_SHA_DRIFT")
    raw=seed.bounded_read(Path(root)/"item_set_bonus.inc",
                          seed.SOURCE_FILES["item_set_bonus.inc"])
    source=doc.get("source_files",{}).get("item_set_bonus.inc",{})
    need(type(source) is dict and
         source.get("sha256")==seed.digest(raw) and
         source.get("git_blob_sha1")==seed.git_blob(raw),
         "V231_SET_BYTES_NOT_MATCH_PINNED_GIT_BLOB")
    reconstructed=seed.parse_set_bonus(
        raw, doc["simc_generated_build"])
    need(reconstructed["candidate_groups"]==doc["set_bonus_candidate_groups"]
         and reconstructed["raw_rows"]==doc["set_bonus_source_rows"],
         "V231_SET_GROUPS_NOT_REPRODUCIBLE_FROM_SIMC")
    return doc,reconstructed


def select(*, seed_directory, cls, spec, set_option):
    need(type(cls) is str and cls in CLASS_ID and
         type(spec) is str and
         representative.contracts.lookup(cls,spec) is not None,
         "V231_26_DPS_SPEC_REQUIRED")
    need(type(set_option) is str and TOKEN.fullmatch(set_option),
         "V231_SEASON_SET_OPTION_REQUIRED_NOT_INFERRED")
    receipt,sets=read_receipt(seed_directory)
    groups=[g for g in sets["candidate_groups"]
            if g["set_opt"]==set_option
            and g["class_id"]==CLASS_ID[cls]]
    need(len(groups)==1,"V231_SET_OPTION_MISSING_OR_AMBIGUOUS")
    selected=groups[0]
    need(sorted(selected["observed_bonus_sizes"])==[2,4] and
         len(selected["item_ids"])==5 and
         len(set(selected["item_ids"]))==5,
         "V231_NOT_AN_EXACT_5PC_2PC_4PC_SET")
    table=itemdata.from_seed(directory=seed_directory,
                             item_ids=selected["item_ids"])
    need(table["simc_revision"]==receipt["simc_revision"] and
         table["game_build"]==receipt["simc_generated_build"] and
         table["source_receipt_sha256"]==receipt["receipt_sha256"],
         "V231_ITEM_SOURCE_BUILD_REVISION_DRIFT")
    contract=representative.contracts.lookup(cls,spec)
    armor_subclass=representative.gear.ARMOR_SUBCLASS[contract["family"]]
    mask=1<<(CLASS_ID[cls]-1)
    pieces={}
    for row in table["items"]:
        slot=INV_SLOT.get(row["inventory_type"])
        need(slot is not None and slot not in pieces and
             row["class_id"]==4 and
             row["subclass_id"]==armor_subclass and
             row["item_set_id"]==selected["set_id"] and
             row["allowed_class_mask"]==mask,
             "V231_TIER_PHYSICAL_ARMOR_CLASS_SLOT_OR_SET_INVALID")
        pieces[slot]=row["item_id"]
    need(set(pieces)==FULL,"V231_TIER_FIVE_DISTINCT_SLOTS_REQUIRED")
    result={
        "schema":SCHEMA,
        "status":"SIMC_FIRST_PARTY_CLASS_TIER_CANDIDATE_NOT_SEASON_CERTIFIED",
        "season_set_option_declared":set_option,
        "season_set_option_source_authentication":"NOT_PROVED_BY_SIMC_TABLE_ALONE",
        "game_build":receipt["simc_generated_build"],
        "simc_revision":receipt["simc_revision"],
        "seed_receipt_sha256":receipt["receipt_sha256"],
        "item_data_sha256":table["source_sha256"],
        "set_bonus_sha256":receipt["source_files"][
            "item_set_bonus.inc"]["sha256"],
        "class":cls,"spec":spec,"class_id":CLASS_ID[cls],
        "class_mask":mask,"armor_family":contract["family"],
        "set_id":selected["set_id"],"tier":selected["tier"],
        "tier_piece_ids":{k:pieces[k] for k in
                          ("head","shoulders","chest","hands","legs")},
        "four_piece_slots":["head","shoulders","hands","legs"],
        "tier_bonus_sizes":selected["observed_bonus_sizes"],
        "next_stage":"OTHER_GEAR_WEAPON_SOURCE_DISCOVERY_AND_NATIVE_G",
        "G":None,"J":None,"F":None,"O":None,"B":None,"T":None,
        "environment_ready":False,
        "native_calls":0,"historical_database_access":False,
    }
    return {**result,"receipt_sha256":seed.digest(
        seed.canonical(result).encode("utf8"))}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed-dir",type=Path,required=True)
    p.add_argument("--class",dest="cls",required=True)
    p.add_argument("--spec",required=True)
    p.add_argument("--set-option",required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args(argv)
    result=select(seed_directory=a.seed_dir,cls=a.cls,
                  spec=a.spec,set_option=a.set_option)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(
        result,indent=2,sort_keys=True,ensure_ascii=False)+"\n",
        encoding="utf8")
    print("V231_SIMC_TIER_SOURCE_CANDIDATE",result["class"],
          result["set_id"],"NOT_SEASON_APPROVED_NATIVE0")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
