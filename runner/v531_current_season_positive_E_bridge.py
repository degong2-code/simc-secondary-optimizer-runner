#!/usr/bin/env python3
"""v531: exact 70783 one-user positive static E ownership for existing v212.

Reuses v528 ORIGINAL Windows Native before/after and v222 arithmetic.
Never supplies item mechanics, claims all-spec applicability, or publishes a
new season-wide catalog. The installed v212 file remains immutable.
"""
from __future__ import annotations
import hashlib,json
import v222_season_budget_contract as budget
import v529_current_season_eagle_E0_bridge as original
import v196_current_season_user_catalog as catalog

SCHEMA="v531_one_original_70783_positive_E_user_bridge_v1"
FIELD="selected_season_enchants"
ENCHANTS={
 8025:{"token":"enchant_ring__silvermoons_alacrity",
       "E":{"crit_rating":0,"haste_rating":30,"mastery_rating":0,"versatility_rating":0},
       "before":"be004cc6c4a6e1e5977d971ee868f4e6c636f0f59e708a7a43a89de94369a381",
       "after":"33cae7989e43e6ca07f45e1e9a1fbe1d9e700ab578be0aa061a0e154db418a80"},
 7965:{"token":"enchant_ring__amani_mastery",
       "E":{"crit_rating":0,"haste_rating":0,"mastery_rating":26,"versatility_rating":0},
       "before":"225625fb1a407af5ddece149cdae3f9254221a59ea35183697782109b739675d",
       "after":"a3c12722b6828260559d67f0f6e8ebb5567472ba97bbd5465b0555eaef1c77b5"}
}
CHOICES=tuple({"finger1":eid} for eid in sorted(ENCHANTS))
class PositiveEnchantBlocked(ValueError):pass
def need(ok,code):
    if not ok:raise PositiveEnchantBlocked("V531_"+code)
def check_choice(choice):
    need(type(choice) is dict and len(choice)==1 and
         set(choice)=={"finger1"} and
         type(choice["finger1"]) is int and
         choice["finger1"] in ENCHANTS,"UNVERIFIED_POSITIVE_ENCHANT_ID")
    eid=choice["finger1"]
    row=next((r for r in original.evidence()["enchant_scope"]["scoped_results"]
             if r.get("id")==eid),None)
    expect=ENCHANTS[eid]
    need(row is not None and row.get("status")=="PASS_TWO_REAL_NATIVE_STATIC_ONLY"
         and row.get("slot") in (None,"finger1")
         and row.get("source_ui_selectable") is False
         and row.get("token")==expect["token"]
         and row.get("highest_source_quality_rank")==2
         and row.get("per_profile_E")==expect["E"]
         and row.get("raw_before_SHA")==expect["before"]
         and row.get("raw_after_SHA")==expect["after"],
         "EXACT_V528_NATIVE_POSITIVE_E_SHA_OR_AMOUNT_DRIFT")
    return eid,dict(expect["E"])
def source(choice,catalog_path):
    eid,E=check_choice(choice)
    need(catalog_path is not None,"CURRENT_V213_SOURCE_REQUIRED")
    doc,rows,_=catalog.read(catalog_path)
    found=[r for r in rows if r["enchant_id"]==eid]
    need(doc.get("_v213_fresh_unapproved") is True
         and doc.get("simc_commit")==original.REVISION
         and doc.get("season_game_build")==original.BUILD
         and type(doc.get("_v213_source_catalog")) is dict
         and len(found)==1
         and found[0]["token"]==ENCHANTS[eid]["token"]
         and found[0]["source_slots"]==["finger1/finger2"]
         and found[0]["highest_source_quality_rank"]==2
         and found[0]["ui_selectable"] is False,
         "EXACT_CURRENT_SEASON_OR_QUALITY_SCOPE_MISMATCH")
    return eid,E
def project(document,choice,*,manual_final_T=None):
    """Only a user projection, not a modification of sealed installed GJFO."""
    eid,E=check_choice(choice)
    need(type(document) is dict and
         document.get("game_build")==original.BUILD and
         document.get("simc_revision")==original.REVISION and
         document.get("target_ilevel")==334 and
         document.get("official_G")==2850 and
         document.get("official_J")==92 and
         document.get("official_F")==165 and
         document.get("official_B")==3107 and
         document.get("official_T")==3107 and
         sum(document.get("official_O",{}).values())==0,
         "V212_ORIGINAL_REFERENCE_B_J_F_O_MISMATCH")
    installed=budget.retarget_verified_install(
        document=document,manual_final_T=manual_final_T)
    need(installed.get("fixed_E")==original.ZERO
         and installed.get("G_reference_excludes_selected_E") is not False
         and installed.get("effective_G")==2850
         and installed.get("reference_B")==3107,
         "ORIGINAL_G_ALREADY_HAS_SELECTED_E_OR_UNKNOWN")
    # v222's original arithmetic owns the total and fixed minima. A new
    # unenchanted-reference E is incremental ONLY for automatic ilvl mode.
    B=installed["base_B"]+(sum(E.values()) if manual_final_T is None else 0)
    T=B+sum(document["official_O"].values())
    need(B>=document["official_J"]+document["official_F"]+
         sum(installed["fixed_L"].values())+sum(E.values()) and
         (manual_final_T is None or T==manual_final_T),
         "FIXED_E_OR_MANUAL_T_FEASIBILITY_INVALID")
    return {**installed,"base_B":B,"final_T":T,
            "fixed_E":E,"effective_G":B-document["official_J"]-document["official_F"],
            "reference_B":document["official_B"]+sum(E.values()),
            "verified_user_enchant_id":eid,
            "original_v212_manifest_sha256":document["manifest_sha256"],
            "user_E_added_to_auto_B_once":sum(E.values()) if manual_final_T is None else 0,
            "user_T_manual_unchanged":manual_final_T is not None}
def user_scope(user):
    original.user_scope(user) # exact v528 item loadout, and automatic T only
def apply(rows,choice,user,*,catalog_path):
    eid,E=source(choice,catalog_path)
    user_scope(user)
    ring=rows.get("finger1")
    need(type(ring) is dict
         and ring.get("item_id")==original.ITEM_ID
         and ring.get("ilevel")==334
         and type(ring.get("options")) is dict
         and not set(ring["options"]).intersection({"enchant","enchant_id"}),
         "ORIGINAL_ONE_UNENCHANTED_RING_REQUIRED")
    ring["options"]["enchant_id"]=str(eid)
    return {"schema":SCHEMA,"status":"EXACT_V528_POSITIVE_E_SOURCE_BOUND",
            "slot":"finger1","item_id":original.ITEM_ID,
            "enchant_id":eid,"fixed_E":E,"native_calls":0}
def admit(choice,profile,normalized,binary_sha,revision):
    eid,E=check_choice(choice)
    need(binary_sha==original.BIN_SHA and
         revision==original.REVISION and
         type(profile) is str and type(normalized) is dict,
         "EXACT_V528_WINDOWS_SIMC_BINARY_REVISION_REQUIRED")
    lines=profile.splitlines(keepends=True)
    ring=[i for i,v in enumerate(lines) if v.startswith("finger1=")]
    marker=",enchant_id="+str(eid)
    need(len(ring)==1 and lines[ring[0]].count(marker)==1
         and "id="+str(original.ITEM_ID) in lines[ring[0]],
         "ONE_EXACT_POSITIVE_ENCHANT_NOT_IN_SIMC_PROFILE")
    plain=list(lines)
    plain[ring[0]]=plain[ring[0]].replace(marker,"")
    need(hashlib.sha256("".join(plain).encode("utf8")).hexdigest()==
         original.BASE_SHA,"UNENCHANTED_NATIVE_PROFILE_SHA_DRIFT")
    n=normalized.get("scenario",{})
    ch=n.get("character") or {}
    equipment=n.get("equipment") or {}
    need(ch.get("class")=="hunter" and ch.get("spec")=="survival"
         and equipment.get("special")==[] and
         equipment.get("crafted")==[],"EXACT_WITNESSED_USER_ITEM_SCOPE_DRIFT")
    return {"schema":SCHEMA,
            "status":"EXACT_CURRENT_V212_SELECTED_FIXED_E_ADMITTED_ONE_PROFILE",
            "choice":{"finger1":eid},"fixed_E":E,
            "static_CHMV_E":E,
            "original_profile_sha256":original.BASE_SHA,
            "original_before_json2_sha256":ENCHANTS[eid]["before"],
            "original_after_json2_sha256":ENCHANTS[eid]["after"],
            "gear_override_does_not_add_E_twice":True,
            "simc_effects_owner":True}
