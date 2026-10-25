#!/usr/bin/env python3
"""v086: fixed-secondary mail representative Hunter head and feet.

This ONLY corrects first-use source input IDs/options for two gear fillers.
Old v079-v081 profiles, SHA receipts and Native caches remain immutable.
No loot optimizer, per-item effect checker, random-roll guessing, or new APL.
Exact ilvl334 alternative items 249317/249320 were measured in ONE real
SHA-pinned SimC Native from v079 source with 13 other gear slots unchanged.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys
import v061_scenario_contract as scenario
import v079_hunter_ranged_generic_native as base

SCHEMA="v086_hunter_fixed_mail_head_feet_profile_v1"
REPLACEMENTS={"head":(271441,249317),"feet":(271440,249320)}
NATIVE_EVIDENCE_JSON_SHA256="e55bfa2fa9b255bf2f3b74bb85b255eebf774ba939b43348ab314c7b782f27c2"
KNOWN_NATIVE_HEAD_SECONDARY={"crit_rating":139,"haste_rating":62,
                              "mastery_rating":0,"versatility_rating":0}
KNOWN_NATIVE_FEET_SECONDARY={"crit_rating":48,"haste_rating":0,
                              "mastery_rating":0,"versatility_rating":102}
MEASURED_NONTRINKET_G=2845
MEASURED_OFFICIAL_T=3148

class Blocked(ValueError):pass
def need(ok,why):
    if not ok:raise Blocked(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()

def source_profile(original,root):
    reference,config,fillers,prior=base.source_profile(original,root)
    lines=reference.splitlines()
    for slot,(old_id,new_id) in REPLACEMENTS.items():
        expected_prefix=slot+"=selected_"+str(old_id)+",id="+str(old_id)+","
        matching=[i for i,line in enumerate(lines) if line.startswith(expected_prefix)]
        need(len(matching)==1,"EXPECTED_OLD_RANDOM_SECONDARY_SLOT_ABSENT:"+slot)
        old_line=lines[matching[0]]
        need("ilevel=334" in old_line
             and "crafted_stats=" not in old_line,
             "EXPECTED_SOURCE_VARIANT_NOT_IDENTICAL:"+slot)
        # Original Hunter head socket marker preserved; no random stat guess.
        options=",gem_id=240983" if slot=="head" else ""
        lines[matching[0]]=slot+"=selected_"+str(new_id)+",id="+str(new_id)+\
                           ",ilevel=334,source=local"+options
        matches=[f for f in fillers if f["slot"]==slot]
        need(len(matches)==1 and matches[0]["item_id"]==old_id,
             "FIXED_MAIL_MUST_REPLACE_FILLER_NOT_TIER_SPECIAL_OR_TRINKET:"+slot)
        matches[0]["item_id"]=new_id
        matches[0]["options"]=({"gem_id":"240983"} if slot=="head" else {})
    result="\n".join(lines)+"\n"
    source_actions=[line for line in reference.splitlines() if line.startswith("actions")]
    final_actions=[line for line in result.splitlines() if line.startswith("actions")]
    need(source_actions==final_actions,"FROZEN_HUNTER_APL_CHANGED")
    need([line for line in reference.splitlines() if line.startswith("talents=")]==
         [line for line in result.splitlines() if line.startswith("talents=")],
         "FROZEN_HUNTER_TALENTS_CHANGED")
    need(len(fillers)==7
         and {z["item_id"] for z in fillers}.issuperset({249317,249320}),
         "FILLER_SLOTS_OR_SOURCE_IDS_CHANGED")
    config["source"]["profile_sha256"]=sha(result.encode("utf8"))
    n=scenario.normalize(config)
    need(len(config["equipment"]["tier"])==4
         and len(config["equipment"]["trinkets"])==2
         and n["scenario"]["target"]["ilevel"]==334,
         "HUNTER_STATIC_SOURCE_SCENARIO_DRIFT")
    meta=dict(prior)
    meta.update({"replaced_random_stat_filler_items":REPLACEMENTS,
                 "exact_native_evidence_json_sha256":NATIVE_EVIDENCE_JSON_SHA256,
                 "verified_nontrinket_G_for_these_exact_native_options":MEASURED_NONTRINKET_G,
                 "verified_T_with_declared_J138_F165":MEASURED_OFFICIAL_T,
                 "nontrinket_unclassified_unknown_items":0,
                 "item_effects_owned_by":"SimC",
                 "not_an_equipment_recommender":True})
    return result,config,fillers,meta

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args(argv)
    source,cfg,filler,meta=source_profile(a.upstream.read_text("utf8"),a.out)
    out=a.out.resolve()
    out.mkdir(parents=True,exist_ok=True)
    (out/"V086_REFERENCE.simc").write_text(source,encoding="utf8")
    (out/"V086_SCENARIO.json").write_text(json.dumps(cfg,indent=2)+"\n")
    (out/"V086_FILLERS.json").write_text(json.dumps(filler,indent=2)+"\n")
    (out/"V086_PROFILE_META.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(json.dumps({"status":"PASS_FIXED_MAIL_EXACT_PROFILE_INPUT_ONLY",
       "new_native_calls":0,
       "previous_real_native_json_sha256":NATIVE_EVIDENCE_JSON_SHA256,
       "corrected_G_observed_prior":MEASURED_NONTRINKET_G,
       "corrected_T_observed_prior":MEASURED_OFFICIAL_T}))
    return 0

if __name__=="__main__":sys.exit(main())
