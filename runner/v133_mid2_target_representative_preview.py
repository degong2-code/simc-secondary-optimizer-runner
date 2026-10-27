#!/usr/bin/env python3
"""v133 common, non-executable TARGET-334 profile previews for 17 MID2 DPS.

One data-driven compiler (NOT 17 source factories and NOT new DPS engine).
Preserves original source APL and weapon identities, normalizes four tier
pieces, and reports incomplete product requirements honestly. It never
claims v098 manifest readiness, applies a CHMV rating, or calls Native SimC.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import pathlib
import sys
import v055_simc_item_selection as item
import v135_source_gem_colors as common
import v127_dps_source_metadata as registry
import v128_common_source_profile_emitter as emitter
import v129_common_source_fields as fields
import v132_dps_source_batch_smoke as sources

SCHEMA="v133_shared_mid2_target_representative_preview_v1"
LEVEL=334
FIVE=("head","shoulders","chest","hands","legs")
ARMOR={"deathknight":"plate","demonhunter":"leather","druid":"leather",
       "hunter":"mail","mage":"cloth","monk":"leather","priest":"cloth",
       "rogue":"leather","shaman":"mail","warlock":"cloth","warrior":"plate"}
# All positive tier IDs have direct provenance in the 24 frozen MID2
# source set or in the seven existing source-pinned v127 rows. No arithmetic
# reconstruction of season-item IDs is allowed. None marks source effects.
FIVE_TIER={
 "deathknight":(271474,271472,271477,271475,271473),
 "demonhunter":(271537,271535,271540,271538,271536),
 "druid":(271528,271526,271531,271529,271527),
 # Three previously missing tier IDs independently grounded against
 # MID2 tier-set item identity: 271520 Monk gloves (WoWTopGear),
 # 271553 Priest shoulders (WoWDB/Wowhead), 271546 Warlock head
 # (TransmogDB source set). They remain *item-ID* evidence, not a new
 # Native exact-rating/proc receipt.
 "monk":(271519,271517,271522,271520,271518),
 "priest":(271555,271553,271558,271556,271554),
 "warlock":(271546,271544,271549,271547,271545)}
for _e in registry.SOURCE_BACKED:
    FIVE_TIER.setdefault(_e.character_class,
                          tuple(_e.tier_ids()[slot] for slot in FIVE))
# A single standard non-tier/off-slot policy PER ARMOR FAMILY, not per spec.
# Plate legs: the user's earlier source-backed v127 Warrior Fury 271878.
# Leather chest 251159 and cloth head 271874 likewise already pinned;
# mail head 249317 comes from the existing corrected v086 source.
ORDINARY_OFF={"plate":("legs",271878),"leather":("chest",251159),
              "mail":("head",249317),"cloth":("head",271874)}
# The complete 5-tier IDs are now item-identity sourced; leave the
# fallback mechanism in place for any future source with genuinely unknown
# fifth-tier evidence, rather than guessing a contiguous numeric ID.
UNRESOLVED_FIFTH={}
class PreviewBlocked(ValueError):pass

def need(ok,code):
    if not ok:raise PreviewBlocked(code)

# Feral's pinned MID2 source has a head without an equipped diamond and
# only three ordinary gems (the special 240983 is placed in the neck).
# Same-ID MID2 Rogue/Monk source witnesses establish these neck/wrist/waist
# physical positions. Head 271528 is the actual Druid tier item; its head
# socket is additionally witnessed in a public live-character gear record,
# but the exact 334 variant STILL requires real SimC acceptance.
# Candidate preview ONLY: do not register Feral as user-ready before Native.
FERAL_SOCKET_ROWS={
    "head":(271528,"240983"),
    "neck":(268265,"240914/240890"),
    "wrists":(244576,"240890"),
    "waist":(268256,"240908")}
FERAL_RING_ROWS={"finger1":(268249,"240898"),
                 "finger2":(268252,"240900")}

def feral_candidate_sockets(key,ids,mods):
    if key!="druid/feral":return False
    need(all(ids.get(slot)==item_id for slot,(item_id,_) in
             {**FERAL_SOCKET_ROWS,**FERAL_RING_ROWS}.items()),
         "V133_FERAL_SOCKET_REFERENCE_ITEM_DRIFT")
    need(mods["neck"].get("gem_id")=="240983" and
         "gem_id" not in mods["head"] and
         all("gem_id" not in mods[slot] for slot in ("wrists","waist")) and
         all(mods[slot].get("gem_id")==gem for slot,(_,gem)
             in FERAL_RING_ROWS.items()),
         "V133_FERAL_ORIGINAL_SOCKET_LAYOUT_DRIFT")
    for slot,(_,gems) in FERAL_SOCKET_ROWS.items():
        mods[slot]["gem_id"]=gems
    return True

def draft(key,ilevel=LEVEL):
    need(key in sources.NEW,"V133_SOURCE_KEY_NOT_PINNED")
    need(isinstance(ilevel,int) and 266<=ilevel<=344,"V133_LEVEL_INVALID")
    original=sources.validate_source(key)
    source=original["source"]
    cls,spec=key.split("/")
    ids,mods=fields.equipment(source,item.SLOTS,need=need,
         duplicate_prefix="V133_SOURCE_DUPLICATE_SLOT:",
         missing_id_prefix="V133_SOURCE_ITEM_ID_MISSING:",
         include_gem_enchant=True)
    need(len(ids) in (15,16),"V133_PHYSICAL_GEAR_COUNT")
    tier=dict(zip(FIVE,FIVE_TIER[cls]))
    family=ARMOR[cls]
    offslot,ordinary=ORDINARY_OFF[family]
    missing=[slot for slot,id_ in tier.items() if id_ is None]
    if missing:
        offslot=UNRESOLVED_FIFTH[cls]
        ordinary=ids[offslot]
        need(missing==[offslot],"V133_UNPROVEN_TIER_LAYOUT")
    else:
        # Expected original source may equip a special/crafted fifth or even
        # all five tier items. Only the existing family off-slot is changed.
        need(tier[offslot] is not None,"V133_OFFSLOT_MISSING_TIER")
    source_four={slot for slot in FIVE if tier[slot] is not None and
                 ids[slot]==tier[slot]}
    need(len(source_four)>=3,"V133_SOURCE_CLASS_TIER_NOT_RECOGNIZED")
    for slot in FIVE:
        if slot==offslot:
            ids[slot]=ordinary
            # A replaced physical item does not retain crafted/random
            # source modifiers; gems are dealt with separately at product
            # completion, not silently transferred to another item.
            if slot!=UNRESOLVED_FIFTH.get(cls):
                # Two exact replacement head item IDs have prior
                # source-backed socket witnesses in the existing v127
                # representative pipeline. Preserve ONLY a source-observed
                # diamond there, never an unproven socket on new armor.
                diamond=mods[slot].get("gem_id")
                if (slot=="head" and diamond in ("240983","240967")
                    and (family,ordinary) in
                       {("cloth",271874),("mail",249317)}):
                    mods[slot]={"gem_id":diamond}
                else:
                    mods[slot]={}
        else:
            need(tier[slot] is not None,"V133_FOUR_TIER_ID_UNAVAILABLE")
            ids[slot]=tier[slot]
            mods[slot]={k:v for k,v in mods[slot].items()
                        if k in ("gem_id","enchant","enchant_id")}
    # Reposition only ID-/source-witnessed physical gems on the staged
    # Feral representative. The original official source bytes stay pinned.
    feral_candidate_sockets(key,ids,mods)
    rows={slot:{"slot":slot,"item_id":id_,"ilevel":ilevel,
               "options":item.checked_options(mods.get(slot,{}))}
          for slot,id_ in ids.items()}
    selected=[slot for slot in FIVE if slot!=offslot]
    need(all(rows[s]["item_id"]==tier[s] for s in selected),
         "V133_FOUR_TIER_ASSEMBLY_DRIFT")
    # This is a preview only, no free-CHMV search budget and no execution.
    # Original APL and source's race/talents/flask/folio remain unaltered.
    overlays={"fight_style":"Patchwerk","desired_targets":"1",
              "max_time":"300","optimal_raid":"1",
              "iterations":"35","threads":"1","vary_combat_length":"0",
              "fixed_time":"1"}
    order=tuple(slot for slot in (
          "head","neck","shoulders","back","chest","wrists","hands","waist",
          "legs","feet","finger1","finger2","trinket1","trinket2",
          "main_hand","off_hand") if slot in rows)
    output=emitter.emit(source,overlays,rows,order,
                        blank_before_overrides=False,need=need,
                        check_duplicate_overrides=True)
    old_apl=fields.matching_lines(source,"actions")
    need(fields.matching_lines(output,"actions")==old_apl,
         "V133_APL_BYTES_DRIFT")
    diamond=rows["head"]["options"].get("gem_id")
    ordinary_gems=[v for slot,row in rows.items() if slot!="head"
                   for v in row["options"].get("gem_id","").split("/") if v]
    reserved_flags=[]
    if len(missing):
        reserved_flags.append("FIFTH_TIER_ID_NOT_SOURCE_OBSERVED")
    if diamond not in ("240967","240983"):
        reserved_flags.append("REPRESENTATIVE_HEAD_DIAMOND_NOT_READY")
    if len(ordinary_gems)!=6:
        reserved_flags.append("SIX_PHYSICAL_ORDINARY_GEMS_NOT_READY")
    if diamond=="240967":
        colors={common.SOURCE_GEM_COLOR.get(int(x)) for x in ordinary_gems
                if x.isdigit()}
        if None in colors or colors!=set(common.FOUR_COLOR_GEMS):
            reserved_flags.append("FOUR_GEM_COLORS_NOT_READY")
    if len({row["item_id"] for row in rows.values()})!=len(rows):
        reserved_flags.append("REPEATED_REPRESENTATIVE_ITEM_IDS_REVIEW")
    # A cross-source socket witness does not prove this exact Feral
    # target-334 variant's Native acceptance. Keep product/UI disabled.
    if key=="druid/feral":
        reserved_flags.append("FERAL_REPRESENTATIVE_SOCKET_NATIVE_NOT_YET_VERIFIED")
    # The season source is not a guaranteed plain-ordinary armor set:
    # source leftovers still require the common P1 source/ordinary policy.
    reserved_flags.append("NON_TIER_SOURCE_GEAR_NOT_ALL_STANDARDIZED")
    reserved_flags.append("SOURCE_FLASK_F_OMNIUM_MAPPING_NOT_YET_VALIDATED")
    result={"schema":SCHEMA,"key":key,"source_git_blob":original["git_blob"],
            "source_sha256":original["sha256"],"level":ilevel,
            "material":family,"original_tier_count":len(source_four),
            "four_tier_slots":selected,"offslot":offslot,
            "original_offslot_item":None, "offslot_item":ordinary,
            "missing_fifth_tier_id":missing,
            "weapon_ids":{hand:ids[hand] for hand in
                          ("main_hand","off_hand") if hand in ids},
            "physical_items":len(rows),
            "ordinary_gem_count":len(ordinary_gems),
            "diamond_id":diamond,
            "apl_lines":len(old_apl),
            "open_product_conditions":reserved_flags,
            "ready_for_user_optimizer":False,"native_calls":0,
            "profile_sha256":hashlib.sha256(output.encode("utf8")).hexdigest()}
    return result,output

def preview_all(ilevel=LEVEL,write_profiles=None):
    results=[]
    if write_profiles is not None:
        pathlib.Path(write_profiles).mkdir(parents=True,exist_ok=True)
    for key in sources.NEW:
        data,profile=draft(key,ilevel)
        results.append(data)
        if write_profiles is not None:
            dest=pathlib.Path(write_profiles)/(key.replace("/","__")+".simc")
            dest.write_text(profile,encoding="utf8",newline="\n")
    return {"schema":SCHEMA,"status":"PASS_17_PROFILES_STAGED_NOT_EXECUTABLE",
            "source_count":len(results),"native_calls":0,
            "ready_for_user_optimizer":0,
            "missing_exact_fifth_tier":sum(
                bool(x["missing_fifth_tier_id"]) for x in results),
            "specs":results}
def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--ilevel",type=int,default=LEVEL)
    parser.add_argument("--out",type=pathlib.Path,
      default=pathlib.Path.home()/"SIMC_Secondary_Optimizer"/"target_preview_v133")
    a=parser.parse_args(argv)
    try:
        report=preview_all(a.ilevel,a.out/"profiles")
        a.out.mkdir(parents=True,exist_ok=True)
        (a.out/"V133_TARGET_PREVIEW.json").write_text(
          json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
        print(report["status"],"count",report["source_count"],
              "fifth_unknown",report["missing_exact_fifth_tier"],
              "Native",report["native_calls"])
        status=0
    except (ValueError,KeyError,OSError) as e:
        print("V133_BLOCKED",type(e).__name__,str(e),file=sys.stderr)
        status=3
    print("RESULT_DIR:",a.out.resolve())
    if os.name=="nt" and a.out.exists():
        try:os.startfile(str(a.out.resolve()))
        except OSError:pass
    return status
if __name__=="__main__":
    raise SystemExit(main())
