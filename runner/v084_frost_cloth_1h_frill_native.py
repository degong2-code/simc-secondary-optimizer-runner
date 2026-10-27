#!/usr/bin/env python3
"""v084: Human Frost Mage cloth / 1H weapon + NON-WEAPON offhand.

Fixture-only source-backed profile producer. Uses common v082 static CHMV
Native runner, existing v066 static witness preflight and v015 mirror.
No per-Mage DPS solver, loot database, APL/item effect/proc reimplementation.
"""
from __future__ import annotations
import v128_common_source_profile_emitter as common_emitter
import argparse,hashlib,pathlib,re,sys

import v055_simc_item_selection as items
import v061_scenario_contract as scenario
import v082_fury_plate_dual_twohand_native as shared

SCHEMA="v084_human_frost_cloth_1h_frill_static_chmv_native_v1"
UPSTREAM_GIT_BLOB="b787824a95020a7cdd0934ed5e004695726db138"
NONTIER_GIT_BLOB="9fae08d2f1c49f3a964f9415540929723384e6fe"
FIRE_SOURCE=(pathlib.Path(__file__).resolve().parents[1]/
 "integration_probes/fixtures/v084_upstream_mid2_mage_fire_nontier_head_source.simc")
ALL_SLOTS=tuple(shared.ALL_SLOTS)
TIER_SLOTS=("shoulders","chest","hands","legs")
CRAFTED_SLOTS=("waist","off_hand")
TRINKET_SLOTS=("trinket1","trinket2")
HEAD_ID=271874
MAIN_ID=271092
OFFHAND_ID=245769
F_DECLARED={"crit_rating":165,"haste_rating":0,
            "mastery_rating":0,"versatility_rating":0}
GEMS={"head":"240983","neck":"240906/240906",
      "wrists":"240906","waist":"240906",
      "finger1":"240906","finger2":"240906"}
class Blocked(ValueError):pass
def need(x,reason):
    if not x:raise Blocked(reason)
def git_sha(raw):
    return hashlib.sha1(("blob "+str(len(raw))+"\0").encode("ascii")+raw).hexdigest()

def source_profile(original,folder):
    raw=original.encode("utf8")
    need(git_sha(raw)==UPSTREAM_GIT_BLOB,"FROST_UPSTREAM_GIT_BLOB_CHANGED")
    need('mage="MID2_Mage_Frost_Spellslinger"' in original
         and "spec=frost" in original and "race=tauren" in original
         and "role=spell" in original,"FROST_CLASS_SPECIALIZATION_SOURCE_CHANGED")
    fire=FIRE_SOURCE.read_bytes()
    need(git_sha(fire)==NONTIER_GIT_BLOB
         and "head=venomkeepers_horrific_cowl,id=271874," in fire.decode("utf8"),
         "FIRE_CLOTH_NONTIER_HEAD_SOURCE_CHANGED")
    actions=[line for line in original.splitlines() if line.startswith("actions")]
    need(len(actions)>=60 and
         sum(line.startswith("actions=") for line in actions)==1,
         "FROST_ORIGINAL_APL_MISSING")
    talents=[line.partition("=")[2] for line in original.splitlines()
             if line.startswith("talents=")]
    need(len(talents)==1,"FROST_TALENT_STRING_MISSING")
    ids={}
    for line in original.splitlines():
        if line.startswith("# Gear Summary"):break
        key,sep,v=line.partition("=")
        if sep and key in ALL_SLOTS:
            need(key not in ids,"DUPLICATE_FROST_EQUIPMENT_SLOT:"+key)
            m=re.search(r"(?:^|,)id=(\d+)(?:,|$)",v)
            need(m is not None,"FROST_SOURCE_ID_NOT_FOUND:"+key)
            ids[key]=int(m.group(1))
    need(set(ids)==set(ALL_SLOTS),"FROST_SIXTEEN_SLOTS_REQUIRED")
    need(ids["main_hand"]==MAIN_ID and ids["off_hand"]==OFFHAND_ID,
         "FROST_ORIGINAL_ONEHAND_FRILL_ID_CHANGED")
    previous_head=ids["head"]
    need(previous_head==271564,"FROST_FIFTH_TIER_HEAD_CHANGED")
    ids["head"]=HEAD_ID
    eq={}
    for slot,id_ in ids.items():
        opts={}
        if slot in GEMS:opts["gem_id"]=GEMS[slot]
        if slot in CRAFTED_SLOTS:opts["crafted_stats"]="32/49"
        eq[slot]={"slot":slot,"item_id":id_,"ilevel":334,"options":opts}
    folder=pathlib.Path(folder).resolve()
    # Preserve actual original shattered-sun flask and exact Frost APL,
    # replacing race and first-use numeric/combat settings only.
    fixed={"race":"human","fight_style":"Patchwerk",
          "desired_targets":"1","max_time":"300",
          "vary_combat_length":"0","fixed_time":"1",
          "optimal_raid":"1","threads":"1",
          "iterations":str(shared.ITERATIONS),
          "json2":str(folder/"initial_native"/"result.json")}
    fixed.update({"gear_"+k:"700" for k in scenario.STATS})
    profile=common_emitter.emit(
        original,fixed,eq,ALL_SLOTS,
        blank_before_overrides=True)
    need([line for line in profile.splitlines() if line.startswith("actions")]==actions,
         "FROST_SIMC_APL_CHANGED")
    need("off_hand=selected_245769,id=245769,ilevel=334" in profile
         and "main_hand=selected_271092,id=271092,ilevel=334" in profile,
         "FROST_1H_AND_FRILL_NOT_EXACTLY_BOUND")
    need("temporary_enchant=" not in profile,"OIL_MUST_REMAIN_OUTSIDE_TEST_T")
    cfg={
       "schema":scenario.SCHEMA,
       "character":{"class":"mage","spec":"frost","race":"human",
                    "role":"spell","talents":talents[0]},
       "source":{"kind":"user_supplied",
                 "profile_sha256":shared.sha(profile.encode("utf8"))},
       "target":{"mode":"derived_ilevel","ilevel":334,
                 "manual_total":None,"manual_total_scope":None},
       "equipment":{"tier":[eq[k] for k in TIER_SLOTS],
            "special":[],"crafted":[eq[k] for k in CRAFTED_SLOTS],
            "trinkets":[eq[k] for k in TRINKET_SLOTS]},
       "consumables":{"gem_budget_J":138,"flask_budget_F":165,
            "special_gem_id":240983,
            "flask":"flask_of_the_shattered_sun_2",
            "food":"harandar_celebration",
            "potion":"potion_of_recklessness_2",
            "weapon_temporary":None,
            "weapon_temporary_fixed_rating":{k:0 for k in scenario.STATS}},
       "combat":{"fight_style":"Patchwerk","targets":1,
            "duration_seconds":300,"vary_combat_length_pct":0.0,
            "raid_buffs":True,"bloodlust":"on_pull",
            "external_buffs":[],"events":[]},
       "constraints":{"min_fraction":{k:0 for k in scenario.STATS},
            "max_fraction":{k:1 for k in scenario.STATS},
            "minimum_rating":{k:0 for k in scenario.STATS}},
       "runtime":{"scout_iterations":35,"confirm_iterations":320,
            "max_native_calls":4,"threads":1,"resume":True,"seed":1}}
    selected=set(TIER_SLOTS)|set(CRAFTED_SLOTS)|set(TRINKET_SLOTS)
    fillers=[eq[k] for k in ALL_SLOTS if k not in selected]
    normalized=scenario.normalize(cfg)
    need(len(fillers)==8 and sum(len(cfg["equipment"][x])
              for x in ("tier","special","crafted","trinkets"))+len(fillers)==16,
         "FROST_SIXTEEN_SLOTS_OR_FOUR_TIER_CHANGED")
    need(sum(F_DECLARED.values())==normalized["budget"]["F"],
         "FROST_FLASK_F_DECLARATION_NOT_CONSISTENT")
    metadata={"armor":"cloth","race":"human",
      "weapon_form":"onehand_plus_nonweapon_offhand",
      "main_hand_source_id":MAIN_ID,"off_hand_source_id":OFFHAND_ID,
      "fifth_tier_head_replaced":previous_head,
      "non_tier_source_backed_head":HEAD_ID,
      "source_APL_lines_preserved":len(actions),
      "upstream_frost_git_blob":UPSTREAM_GIT_BLOB,
      "upstream_fire_head_git_blob":NONTIER_GIT_BLOB,
      "source_exact_item_IDs_normalized_to_ilvl334":True,
      "offhand_item_type_delegated_to_SimC":True,
      "declared_F_vector":dict(F_DECLARED),
      "F_attribution_independently_verified":False,
      "oil_included_in_T":False,
      "no_new_effect_model":True}
    return profile,cfg,fillers,metadata

def run(upstream,out,binary=None,cache_only=False):
    return shared.run(upstream,out,binary,cache_only,
        profile_factory=source_profile, expected_slots=16,
        declared_F=F_DECLARED,
        run_schema=SCHEMA, artifact_prefix="V084",
        plan_status="PASS_FROST_CLOTH_1H_FRILL_INPUT_ONLY_ZERO_NATIVE",
        success_status="PASS_REAL_FROST_CLOTH_1H_FRILL_FULL_STATIC_GENERIC_NATIVE")

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    p.add_argument("--binary",type=pathlib.Path)
    p.add_argument("--cache-only",action="store_true")
    x=p.parse_args(argv)
    return run(x.upstream,x.out,x.binary,x.cache_only)

if __name__=="__main__":sys.exit(main())
