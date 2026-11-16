#!/usr/bin/env python3
"""v529: connect one ORIGINAL v528 70783 E=0 enchant to fresh v212 user route.

Exactly hunter/survival, 334, one finger1 item 268266, base profile
a84b57..., pinned de11f57 Windows binary and original v528 Native static
delta=0. This does not certify non-CHMV mechanics, arbitrary loadouts,
any other enchant or a current-season E>0 budget. SimC owns the effects.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import v196_current_season_user_catalog as catalog

SCHEMA="v529_one_verified_70783_eagle_nonchmv_v212_bridge_v1"
CHOICE={"finger1":7967}
BUILD="12.1.5.70783"
REVISION="de11f57df75dda668bae6ac7043a43b98831fa96"
BIN_SHA="1fc927d2be7f1b6064c75f004b5b22245b064a6b3e56e572af4048ba822a986d"
BASE_SHA="a84b57fe25a3b71348e5c0d92c8aa814243c316b01077aca7e1f746f0bd091a8"
ITEM_ID=268266
TRINKETS=(270175,270173)
ZERO={s:0 for s in ("crit_rating","haste_rating",
                     "mastery_rating","versatility_rating")}
NATIVE_BEFORE="db764f9bba5cd73174f1b324582185e1e9b35c76a308f35103f21af9f6bd72e6"
NATIVE_AFTER="fae7c21baa25d6f2ace6f1a747f4f22a768ff53775f23bd12c1b810eb9069621"
PROOF=Path(__file__).resolve().parents[1]/(
    "docs/development/research_receipts/"
    "p1_v528_70783_real_socket_enchant_native_compact.json")

class SourceBlocked(ValueError):
    pass

def need(ok,code):
    if not ok:
        raise SourceBlocked("V529_"+code)

def evidence():
    p=PROOF
    need(p.is_file() and not p.is_symlink() and
         0<p.stat().st_size<=100000,"ORIGINAL_EVIDENCE_FILE_MISSING")
    j=json.loads(p.read_text(encoding="utf8"))
    native=j.get("enchant_scope") or {}
    rows=native.get("scoped_results") or []
    match=[x for x in rows if x.get("id")==7967]
    need(j.get("schema")==
             "p1_v528_20261117_current_70783_socket5_6_enchant3_real_compact_v1"
         and j.get("actions_run_id")==43897717703
         and j.get("actions_conclusion")=="success"
         and j.get("game_build")==BUILD
         and j.get("target_ilevel")==334
         and j.get("simc_binary_revision")==REVISION
         and j.get("simc_binary_sha256")==BIN_SHA
         and j.get("base_profile_sha256")==BASE_SHA
         and j.get("subject")==(
              "hunter/survival, one existing 70783 representative "
              "ilvl334 source-backed profile, finger1 same physical ring")
         and native.get("physical_enchant_Native_calls")==6
         and native.get("AI_runtime_calls")==0
         and len(match)==1
         and match[0].get("status")=="PASS_TWO_REAL_NATIVE_STATIC_ONLY"
         and match[0].get("token")=="enchant_ring__eyes_of_the_eagle"
         and match[0].get("highest_source_quality_rank")==2
         and match[0].get("source_ui_selectable") is False
         and match[0].get("per_profile_E")==ZERO
         and match[0].get("raw_before_SHA")==NATIVE_BEFORE
         and match[0].get("raw_after_SHA")==NATIVE_AFTER,
         "PINNED_REAL_WINDOWS_NATIVE_STATIC_PROOF_DRIFT")
    return j

def source(choice,catalog_path):
    need(type(choice) is dict and choice==CHOICE,
         "ONLY_ONE_EXACT_FINGER1_7967")
    evidence()
    need(catalog_path is not None,
         "FRESH_V213_CATALOG_REQUIRED")
    raw,rows,_=catalog.read(catalog_path)
    original=raw.get("_v213_source_catalog") or {}
    matches=[row for row in rows if row["enchant_id"]==7967]
    need(raw.get("_v213_fresh_unapproved") is True
         and raw.get("simc_commit")==REVISION
         and raw.get("season_game_build")==BUILD
         and original.get("status") is not None
         and len(matches)==1
         and matches[0]["token"]=="enchant_ring__eyes_of_the_eagle"
         and matches[0]["source_slots"]==["finger1/finger2"]
         and matches[0]["highest_source_quality_rank"]==2
         and matches[0]["ui_selectable"] is False,
         "FRESH_CATALOG_BUILD_OR_7967_ID_QUALITY_SCOPE_DRIFT")
    return matches[0]

def user_scope(user):
    target=user.get("target") or {}
    char=user.get("character") or {}
    trinkets=user.get("trinkets") or []
    need(char.get("class")=="hunter" and char.get("spec")=="survival"
         and char.get("race")=="human"
         and target.get("ilevel")==334
         and target.get("final_T") is None
         and user.get("oil_hands")==[]
         and user.get("special_items")==[]
         and user.get("embellishments")==[]
         and [(x.get("slot"),x.get("item_id")) for x in trinkets]==[
              ("trinket1",TRINKETS[0]),("trinket2",TRINKETS[1])],
         "SINGLE_NATIVE_WITNESSED_USER_LOADOUT_ONLY")

def apply(rows,choice,user,*,catalog_path):
    row=source(choice,catalog_path)
    user_scope(user)
    ring=rows.get("finger1")
    need(type(ring) is dict and ring.get("item_id")==ITEM_ID
         and ring.get("ilevel")==334 and
         type(ring.get("options")) is dict
         and "enchant_id" not in ring["options"]
         and "enchant" not in ring["options"],
         "ONE_ORIGINAL_UNENCHANTED_RING_REQUIRED")
    ring["options"]["enchant_id"]="7967"
    return {"schema":SCHEMA,"status":"EXACT_E_ZERO_SOURCE_BOUND_PROFILE_PENDING",
            "item_id":ITEM_ID,"enchant_id":7967,
            "observed_static_CHMV_E":dict(ZERO),
            "original_native_before_sha256":NATIVE_BEFORE,
            "original_native_after_sha256":NATIVE_AFTER,
            "budget_owner":"FIXED_E_ZERO_NO_G_B_T_CHANGE",
            "same_build_v213_catalog":True,"native_calls":0}

def admit(choice,profile,normalized,binary_sha,revision):
    evidence()
    need(choice==CHOICE and type(profile) is str
         and type(normalized) is dict
         and binary_sha==BIN_SHA and revision==REVISION,
         "EXACT_WINDOWS_BINARY_OR_REVISION_REQUIRED")
    lines=profile.splitlines(keepends=True)
    ring=[i for i,v in enumerate(lines) if v.startswith("finger1=")]
    need(len(ring)==1 and
         lines[ring[0]].count("enchant_id=7967")==1 and
         "id="+str(ITEM_ID) in lines[ring[0]],
         "EXACT_ONCE_ENCHANTED_FINGER1_MISSING")
    plain=list(lines)
    plain[ring[0]]=plain[ring[0]].replace(",enchant_id=7967","")
    plain_text="".join(plain)
    need(hashlib.sha256(plain_text.encode("utf8")).hexdigest()==BASE_SHA,
         "ORIGINAL_UNENCHANTED_V528_PROFILE_SHA_MISMATCH")
    gear=normalized.get("scenario",{}).get("equipment",{})
    char=normalized.get("scenario",{}).get("character",{})
    need(type(gear) is dict and char.get("class")=="hunter"
         and char.get("spec")=="survival"
         and not gear.get("special") and not gear.get("crafted"),
         "EXACT_SEASON_NATIVE_LOADOUT_DRIFT")
    return {"schema":SCHEMA,"status":"ONE_CURRENT_SEASON_NONCHMV_E_ZERO_NATIVE_WITNESSED",
            "selected_enchant_id":7967,"slot":"finger1",
            "static_CHMV_E":dict(ZERO),
            "base_v528_source_profile_sha256":BASE_SHA,
            "original_native_before_sha256":NATIVE_BEFORE,
            "original_native_after_sha256":NATIVE_AFTER,
            "B_T_E_accounting":"E0_INSIDE_ORIGINAL_G_NO_TOTAL_CHANGE",
            "runtime_AI_calls":0,"simc_effects_owner":True}
