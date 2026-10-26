#!/usr/bin/env python3
"""v089: opt-in S2 ilvl CHMV reference -> existing v061 manual-T contract.

No general gear database, no full product v015/v016 integration, no SimC calls,
no oil in T, no fixed special L invented.  Preserve exact-native-G mode and
explicit user manual totals.  The per-ilvl table is user-authorized rounded
reference data, not a change to approved T=G+J+F derivation policy.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,pathlib,sys
import v061_scenario_contract as scenario

SCHEMA="v089_opt_in_ilevel_static_budget_selector_v1"
REF_SCHEMA="midnight_s2_native_ilvl_chmv_reference_v1"
REF_PATH=pathlib.Path(__file__).resolve().parents[1]/"integration_probes"/"data"/"midnight_s2_ilvl_chmv_reference_v1.json"
REFERENCE_MODE="reference_rounded_opt_in"
NATIVE_MODE="exact_native_G"
LAYOUTS=frozenset(("single_one_hand","single_two_hand","one_hand_shield",
                  "one_hand_frill","dual_one_hand","dual_two_hand",
                  "ranged","other"))
TRACK_COMMON="general"
TRACK_FURY="fury_dual_2h"
class BudgetSelectionBlocked(ValueError):pass
def need(ok,msg):
    if not ok:raise BudgetSelectionBlocked(msg)
def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,
                      allow_nan=False)
def sha(data):
    return hashlib.sha256(data).hexdigest()
def load_registry(path=REF_PATH):
    p=pathlib.Path(path)
    raw=p.read_bytes()
    reg=json.loads(raw)
    need(type(reg) is dict and reg.get("schema")==REF_SCHEMA
         and reg.get("status")=="REFERENCE_ONLY_NOT_APPROVED_AS_AUTOMATIC_PRODUCT_DEFAULT"
         and reg.get("season")=="midnight_s2"
         and reg.get("formula")=="T=G+J+F"
         and reg.get("J")==138 and reg.get("F")==165
         and reg.get("O")=="external excluded"
         and reg.get("rating_semantics")=="STATIC_CHMV_C_V1",
         "REFERENCE_PROVENANCE_CONTRACT_MISMATCH")
    need(type(reg.get("values")) is list and len(reg["values"])==79,
         "REFERENCE_79_ILVL_ROWS_REQUIRED")
    seen=set()
    for i,row in enumerate(reg["values"]):
        need(type(row) is dict and set(row)==
             {"ilvl","general","fury_dual_2h","is_season_track"}
             and type(row["ilvl"]) is int and row["ilvl"]==266+i
             and type(row["is_season_track"]) is bool
             and type(row["general"]) is int and row["general"]>0
             and type(row["fury_dual_2h"]) is int and row["fury_dual_2h"]>0
             and row["general"]%10==0 and row["fury_dual_2h"]%10==0,
             "REFERENCE_ROW_INVALID_OR_FABRICATED:"+str(i))
        need(row["ilvl"] not in seen,"REFERENCE_ILVL_DUPLICATE")
        seen.add(row["ilvl"])
        if i:
            previous=reg["values"][i-1]
            need(row["general"]>=previous["general"]
                 and row["fury_dual_2h"]>=previous["fury_dual_2h"],
                 "REFERENCE_STATS_NOT_MONOTONIC")
    need(reg["values"][334-266]["general"]==3150
         and reg["values"][334-266]["fury_dual_2h"]==3350,
         "REFERENCE_334_ANCHOR_CHANGED")
    return reg,sha(raw)

def pick_track(char,weapon_layout):
    need(type(weapon_layout) is str and weapon_layout in LAYOUTS,
         "WEAPON_LAYOUT_MUST_BE_EXPLICIT")
    is_fury=(char["class"]=="warrior" and char["spec"]=="fury")
    if is_fury:
        need(weapon_layout=="dual_two_hand","FURY_REQUIRES_DUAL_2H_FOR_THIS_TRACK")
        return TRACK_FURY
    need(weapon_layout!="dual_two_hand",
         "ONLY_VALIDATED_FURY_HAS_DUAL_2H_REFERENCE")
    return TRACK_COMMON

def resolve(doc, *, mode=NATIVE_MODE, weapon_layout,
            reference_path=REF_PATH):
    """Select T once, then delegate typed input to current v061/v062.

    This adapter is deliberately OPT IN.  Source mode='derived_ilevel' remains
    exact native G if selected; reference opt-in uses EXISTING 'manual_total'
    machinery without modifying the approved v061 schema or its official
    T=G+J+F formula.  The source distinction is preserved in this receipt.
    """
    need(mode in (NATIVE_MODE,REFERENCE_MODE),"TARGET_BUDGET_MODE")
    plan=scenario.normalize(doc)
    original=plan["scenario"]
    target=original["target"]
    selected_manual=target["mode"]=="manual_total"
    if selected_manual:
        # User's actual manual total always wins; never fetch/replace with table.
        need(target["manual_total_scope"]==scenario.MANUAL_TOTAL_SCOPE,
             "MANUAL_TOTAL_SCOPE_DRIFT")
        return {"schema":SCHEMA,"status":"READY_USER_MANUAL_TOTAL",
           "source_mode":"user_manual_total","requested_mode":mode,
           "native_G_required_for_T":False,
           "native_special_L_still_required":True,
           "resolved_T":target["manual_total"],
           "selected_track":None,"weapon_layout":weapon_layout,
           "reference_sha256":None,"reference_row":None,
           "scenario_plan":plan,"scenario":copy.deepcopy(original),
           "official_formula_unchanged":"T=G+J+F",
           "external_O":plan["budget"]["external_temporary_rating"],
           "original_product_integrated":False,
           "native_calls":0}
    if mode==NATIVE_MODE:
        return {"schema":SCHEMA,"status":"WAIT_EXACT_NATIVE_G",
           "source_mode":NATIVE_MODE,"requested_mode":mode,
           "native_G_required_for_T":True,
           "native_special_L_still_required":True,
           "resolved_T":None,"selected_track":None,
           "weapon_layout":weapon_layout,"reference_sha256":None,
           "reference_row":None,"scenario_plan":plan,
           "scenario":copy.deepcopy(original),
           "official_formula_unchanged":"T=G+J+F",
           "external_O":plan["budget"]["external_temporary_rating"],
           "original_product_integrated":False,"native_calls":0}
    track=pick_track(original["character"],weapon_layout)
    reg,ref_sha=load_registry(reference_path)
    i=target["ilevel"]-266
    need(0<=i<79,"ITEMLEVEL_OUTSIDE_VERIFIED_REFERENCE")
    row=reg["values"][i]
    need(row["ilvl"]==target["ilevel"],"REFERENCE_ILVL_INDEX_DRIFT")
    # The 79×2 table is bound to exactly the v087 declared J/F convention.
    need(plan["budget"]["J"]==reg["J"] and plan["budget"]["F"]==reg["F"],
         "REFERENCE_GEM_FLASK_BUDGET_MISMATCH")
    effective=copy.deepcopy(original)
    effective["target"]={"mode":"manual_total",
       "ilevel":target["ilevel"],"manual_total":row[track],
       "manual_total_scope":scenario.MANUAL_TOTAL_SCOPE}
    resolved=scenario.normalize(effective)
    need(resolved["budget"]["T"]==row[track]
         and resolved["budget"]["external_temporary_rating"]==
             plan["budget"]["external_temporary_rating"]
         and resolved["scenario"]["equipment"]==plan["scenario"]["equipment"]
         and resolved["scenario"]["character"]==plan["scenario"]["character"]
         and resolved["scenario"]["combat"]==plan["scenario"]["combat"],
         "REFERENCE_RESOLUTION_ALTERED_PROFILE_OR_O")
    return {"schema":SCHEMA,"status":"READY_OPT_IN_REFERENCE_TOTAL_NOT_FULL_P3",
       "source_mode":REFERENCE_MODE,"requested_mode":mode,
       "native_G_required_for_T":False,
       "native_special_L_still_required":True,
       "resolved_T":row[track],"selected_track":track,
       "weapon_layout":weapon_layout,
       "weapon_layout_source":"CALLER_DECLARED_REQUIRES_PROFILE_VERIFICATION",
       "reference_sha256":ref_sha,"reference_row":dict(row),
       "reference_rounding":"nearest 10, original representative Native delta <=5",
       "scenario_plan":resolved,"scenario":effective,
       "official_formula_unchanged":"T=G+J+F",
       "external_O":resolved["budget"]["external_temporary_rating"],
       "T_includes_oil":False,"native_calls":0,
       "original_product_integrated":False,
       "warning":"REFERENCE_OPT_IN_NEEDS_EXACT_SPECIAL_L_AND_P3_NATIVE_RECONCILIATION"}

def main(argv=None):
    p=argparse.ArgumentParser(description="v089 opt-in reference budget adapter")
    p.add_argument("--scenario",required=True,type=pathlib.Path)
    p.add_argument("--mode",choices=(NATIVE_MODE,REFERENCE_MODE),
                   default=NATIVE_MODE)
    p.add_argument("--weapon-layout",required=True,choices=sorted(LAYOUTS))
    p.add_argument("--reference",type=pathlib.Path,default=REF_PATH)
    p.add_argument("--out",required=True,type=pathlib.Path)
    args=p.parse_args(argv)
    data=json.loads(args.scenario.read_text("utf8"))
    result=resolve(data,mode=args.mode,weapon_layout=args.weapon_layout,
                   reference_path=args.reference)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,
                    indent=2)+"\n",encoding="utf8")
    print(SCHEMA,result["status"],"T",result["resolved_T"],
          "track",result["selected_track"],"Native",result["native_calls"])
    return 0
if __name__=="__main__":
    sys.exit(main())
