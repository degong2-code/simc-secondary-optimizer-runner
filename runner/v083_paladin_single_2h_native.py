#!/usr/bin/env python3
"""v083 Retribution Paladin, Blood Elf, plate, SINGLE 2H weapon / no offhand.

A thin source-backed profile composer. All GJF, static-c, Native, cache, and
v015-derived scout execution uses the SAME bounded v082 runner—no new per-spec
optimizer, no talent/item/APL mechanics. Existing original v082 defaults stay.
"""
from __future__ import annotations
import v128_common_source_profile_emitter as common_emitter
import v129_common_source_fields as common_fields
import v130_source_identity_contract as source_identity
import argparse,hashlib,pathlib,re,sys
import v055_simc_item_selection as items
import v061_scenario_contract as scenario
import v082_fury_plate_dual_twohand_native as shared

SCHEMA="v083_retribution_plate_single_twohand_static_chmv_native_v1"
UPSTREAM_GIT_BLOB="864e857c5d8cdbaa5b03939f077fcb657a4784aa"
FURY_GIT_BLOB="3225992ed5b754ad5d61e8b785d9d859f1eed1be"
FURY_SOURCE=(pathlib.Path(__file__).resolve().parents[1]/
    "integration_probes/fixtures/v082_upstream_mid2_warrior_fury_reference.simc")
ALL_SLOTS=tuple(k for k in shared.ALL_SLOTS if k!="off_hand")
TIER_SLOTS=("head","shoulders","chest","hands")
CRAFTED_SLOTS=("wrists",)
TRINKET_SLOTS=("trinket1","trinket2")
MAIN_HAND_ID=268213
REPLACEMENT_LEGS_ID=271878
GEMS=dict(shared.GEM_ID)
DECLARED_F=dict(shared.DECLARED_F)

class Blocked(ValueError):pass
def need(ok,reason):
    if not ok:raise Blocked(reason)
def git_blob(raw):
    return hashlib.sha1(
        ("blob "+str(len(raw))+"\0").encode("ascii")+raw).hexdigest()

def source_profile(original,folder):
    initial_actions,talents=source_identity.verify(
        original,("paladin","retribution"),UPSTREAM_GIT_BLOB,
        ('paladin="MID2_Paladin_Retribution_Herald"',
         "spec=retribution","role=attack","race=dwarf"),
        min_actions=35,
        hash_error="PALADIN_UPSTREAM_SOURCE_BLOB_CHANGED",
        identity_error="PALADIN_ORIGINAL_CLASS_ROLE_IDENTITY_CHANGED",
        apl_error="ORIGINAL_PALADIN_APL_MISSING",
        talents_error="SINGLE_PALADIN_TALENT_STRING_REQUIRED",fail=need)
    fury_bytes=FURY_SOURCE.read_bytes()
    need(git_blob(fury_bytes)==FURY_GIT_BLOB and
         "legs=chausses_of_unbound_rancor,id=271878," in fury_bytes.decode("utf8"),
         "NON_TIER_PLATE_LEGS_SOURCE_PROVENANCE_CHANGED")
    ids,_=common_fields.equipment(original,ALL_SLOTS,need=need,
        duplicate_prefix="DUPLICATE_EQUIPMENT_SLOT:",
        missing_id_prefix="UPSTREAM_ITEM_ID_MISSING:")
    need(set(ids)==set(ALL_SLOTS) and "off_hand=" not in original,
         "PALADIN_MUST_HAVE_FIFTEEN_SLOTS_NO_OFFHAND")
    need(ids["main_hand"]==MAIN_HAND_ID,
         "PALADIN_TWO_HANDED_MAINHAND_CHANGED")
    original_legs=ids["legs"]
    need(original_legs==271464,"SOURCE_PALADIN_TIER_LEGS_CHANGED")
    # Four source Paladin tier items + one source-backed ordinary plate legs;
    # exact item identity validated, physical usability left to Native SimC.
    ids["legs"]=REPLACEMENT_LEGS_ID
    equipment={}
    for slot in ALL_SLOTS:
        opts={}
        if slot in GEMS:opts["gem_id"]=GEMS[slot]
        if slot in CRAFTED_SLOTS:opts["crafted_stats"]="49/36"
        equipment[slot]={"slot":slot,"item_id":ids[slot],
            "ilevel":334,"options":opts}
    folder=pathlib.Path(folder).resolve()
    overrides={
        "race":"blood_elf","fight_style":"Patchwerk",
        "desired_targets":"1","max_time":"300",
        "vary_combat_length":"0","fixed_time":"1",
        "optimal_raid":"1","threads":"1",
        "iterations":str(shared.ITERATIONS),
        "json2":str(folder/"initial_native"/"result.json"),
        "flask":"flask_of_the_blood_knights_2",
        "food":"harandar_celebration"}
    overrides.update({"gear_"+stat:"700" for stat in scenario.STATS})
    reference=common_emitter.emit(
        original,overrides,equipment,ALL_SLOTS,
        blank_before_overrides=True)
    need(initial_actions==[x for x in reference.splitlines()
                if x.startswith("actions")],
         "PALADIN_SIMC_APL_LINES_CHANGED")
    need("off_hand=" not in reference and
         "temporary_enchant=" not in reference,
         "PALADIN_SINGLE_TWOHAND_PROFILE_SLOT_OR_OIL_DRIFT")
    cfg={
      "schema":scenario.SCHEMA,
      "character":{"class":"paladin","spec":"retribution",
                   "race":"blood_elf","role":"attack",
                   "talents":talents[0]},
      "source":{"kind":"user_supplied",
                "profile_sha256":shared.sha(reference.encode("utf8"))},
      "target":{"mode":"derived_ilevel","ilevel":334,
                "manual_total":None,"manual_total_scope":None},
      "equipment":{"tier":[equipment[k] for k in TIER_SLOTS],
             "special":[],
             "crafted":[equipment[k] for k in CRAFTED_SLOTS],
             "trinkets":[equipment[k] for k in TRINKET_SLOTS]},
      "consumables":{
         "gem_budget_J":138,"flask_budget_F":165,
         "special_gem_id":240983,
         "flask":"flask_of_the_blood_knights_2",
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
    fillers=[equipment[k] for k in ALL_SLOTS if k not in selected]
    normalized=scenario.normalize(cfg)
    need(len(fillers)+4+1+2==15
         and sum(DECLARED_F.values())==normalized["budget"]["F"],
         "PALADIN_STATIC_GJF_SLOT_OR_FLASK_BUDGET_DRIFT")
    meta={
      "armor":"plate","race":"blood_elf",
      "weapon_form":"single_two_handed_no_offhand",
      "main_hand_source_id":MAIN_HAND_ID,
      "off_hand_source_id":None,
      "replaced_fifth_tier_legs_source_id":original_legs,
      "replacement_non_tier_plate_legs_id":REPLACEMENT_LEGS_ID,
      "both_source_weapons_kept":False,
      "source_paladin_APL_lines_preserved":len(initial_actions),
      "upstream_profile_git_blob":UPSTREAM_GIT_BLOB,
      "replacement_legs_upstream_fury_git_blob":FURY_GIT_BLOB,
      "declared_static_F":dict(DECLARED_F),
      "F_attribution_confirmed_independently":False,
      "representative_ilvl":334,"original_race_replaced":"dwarf",
      "four_tier_slots":list(TIER_SLOTS),
      "source_exact_item_IDs_normalized_to_ilvl334":True,
      "selected_weapon_compatibility_delegated_to_SimC":True}
    return reference,cfg,fillers,meta

def run(upstream,out,binary=None,cache_only=False):
    return shared.run(upstream,out,binary,cache_only,
          profile_factory=source_profile,expected_slots=15,
          run_schema=SCHEMA,
          plan_status="PASS_PALADIN_SINGLE_2H_EXACT_INPUT_PLAN_ZERO_NATIVE",
          success_status="PASS_REAL_RETRIBUTION_SINGLE_TWOHAND_STATIC_GENERIC_NATIVE",
          artifact_prefix="V083")

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    p.add_argument("--binary",type=pathlib.Path)
    p.add_argument("--cache-only",action="store_true")
    a=p.parse_args(argv)
    return run(a.upstream,a.out,a.binary,a.cache_only)

if __name__=="__main__":sys.exit(main())
