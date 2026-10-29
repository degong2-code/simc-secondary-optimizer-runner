#!/usr/bin/env python3
"""v169: NEW season physical representative plan from v167 IDs + v168 tier.

Does NOT promote the old v098 defaults, old v144/WEQUIP item seeds, or run
Native. Fixed 4pc use four authentic ItemSet IDs (head/shoulders/hands/legs);
a plain chest replaces the fifth. Weapon subclass proficiency, sockets,
effects and 334/266-344 scaling require existing SimC Native acceptance.
Only non-equipment gem/consumable settings may be reused from the approved
same-season v139 runtime configuration, with J/F cross-checked to v165.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

import v143_specialization_contracts as contracts
import v167_product_season_gear_adapter as gear

ROOT=Path(__file__).resolve().parents[1]
TIER_PATH=ROOT/"data/current_season_tier_itemsets.json"
BUDGET_PATH=ROOT/"data/current_season_chmv_consumables.json"
SCHEMA="v169_source_first_physical_representative_preview_v1"
SLOT_TO_INV={"chest":{5,20},"wrists":{9},"waist":{6},"feet":{8},
             "neck":{2},"back":{16},"finger1":{11},"finger2":{11}}
FOUR=("head","shoulders","hands","legs")
ORDINARY=("chest","wrists","waist","feet")
COMMON=("neck","back","finger1","finger2")

# Conservative stable weapon-type preferences, NOT a certification of SimC
# proficiency, skill usage, weapon main-stat compatibility or exact option.
# Subclass values are retail Item.ClassID=2 weapon subclasses. Prefer
# sensible archetype shapes instead of blindly picking the lowest item ID
# (which could otherwise choose a dagger for Frost DK).
FORM_SUBCLASS_PREFS={
    "one_hand_frill":(15,7,4),
    "one_hand_shield":(4,15,0),
    "dual_one_hand":(7,0,4,13),
    "single_one_hand":(7,0,4),
    "dual_two_hand":(8,1,5),
    "single_two_hand":(8,1,5,6,10),
    "ranged":(2,3,18)
}
SPEC_SUBCLASS_PREFS={
    "deathknight/frost":(7,0,4),
    "demonhunter/havoc":(9,7,0,13),
    "demonhunter/devourer":(9,7,0,13),
    "druid/feral":(10,6,5),
    "hunter/survival":(6,10),
    "monk/windwalker":(10,6),
    "rogue/assassination":(15,13),
    "rogue/subtlety":(15,13),
    "rogue/outlaw":(7,13,0,4),
    "shaman/enhancement":(4,0,13),
}

class RepresentativeBlocked(ValueError):pass
def need(v,code):
    if not v:raise RepresentativeBlocked(code)

def load_tier(path=TIER_PATH):
    p=Path(path)
    need(p.is_file() and 0<p.stat().st_size<40000,"TIER_SOURCE_MISSING")
    result=json.loads(p.read_text(encoding="utf8"))
    need(result.get("schema")=="v168_source_first_class_tier_5pc_v1"
         and result.get("status")=="SOURCE_VERIFIED_13_CLASS_FIVE_PIECE_IDS"
         and result.get("class_count")==13 and result.get("item_count")==65
         and result.get("native_calls")==0
         and result.get("production_profile_promoted") is False,
         "TIER_SOURCE_NOT_VERIFIED")
    return result

def available_plain(db,*,slot,family=None,class_mask=None,used=()):
    wanted=SLOT_TO_INV[slot]
    family_sub=gear.ARMOR_SUBCLASS.get(family)
    candidates=[]
    for item in db["items"]:
        if item["category"]!="plain_representative_candidate" or (
            item["inventory_type"] not in wanted or item["item_id"] in used):
            continue
        if family is not None and (item["class_id"]!=4 or
                                   item["subclass_id"]!=family_sub):
            continue
        mask=item["allowed_class_mask"]
        if class_mask is not None and type(mask) is int and (
            mask&class_mask)!=class_mask:
            continue
        candidates.append(item["item_id"])
    return sorted(candidates)

def shape_weapons(db,weapon_form,class_mask,*,spec_key):
    """Inventory form, not class weapon-subclass proficiency certification."""
    need(weapon_form in contracts.WEAPON_FORMS,"WEAPON_FORM_UNKNOWN")
    main_one=[x for x in db["items"]
        if x["category"]=="plain_representative_candidate"
        and x["class_id"]==2 and x["inventory_type"]==13]
    two_hand=[x for x in db["items"]
        if x["category"]=="plain_representative_candidate"
        and x["class_id"]==2 and x["inventory_type"]==17]
    ranged=[x for x in db["items"]
        if x["category"]=="plain_representative_candidate" and
        x["class_id"]==2 and x["inventory_type"] in (15,26)
        and x["subclass_id"] in (2,3,18)]
    shield=[x for x in db["items"]
        if x["category"]=="plain_representative_candidate"
        and x["class_id"]==4 and x["inventory_type"]==14
        and x["subclass_id"]==6]
    frill=[x for x in db["items"]
        if x["category"]=="plain_representative_candidate"
        and x["class_id"]==4 and x["inventory_type"]==23
        and x["subclass_id"]==0]
    prefs=SPEC_SUBCLASS_PREFS.get(
        spec_key,FORM_SUBCLASS_PREFS[weapon_form])
    def candidates(rows):
        valid=[x for x in rows if x["subclass_id"] in prefs and (
            x.get("allowed_class_mask") is None or
            type(x["allowed_class_mask"]) is int and
            (x["allowed_class_mask"]&class_mask)==class_mask)]
        return [x["item_id"] for x in sorted(valid,key=lambda x:(
            prefs.index(x["subclass_id"]),x["item_id"]))]
    def support(rows):
        # A shield/frill is armor, NOT one of the weapon subclasses above.
        return sorted(x["item_id"] for x in rows if (
            x.get("allowed_class_mask") is None or
            type(x["allowed_class_mask"]) is int and
            (x["allowed_class_mask"]&class_mask)==class_mask))
    if weapon_form=="ranged":pool=candidates(ranged); need(pool,"NO_RANGED_BASE_WEAPON");return {"main_hand":pool[0]}
    if weapon_form in ("dual_two_hand","single_two_hand"):
        pool=candidates(two_hand)
        count=2 if weapon_form=="dual_two_hand" else 1
        need(len(pool)>=count,"NO_TWO_HAND_BASE_WEAPON_PAIR")
        return dict(zip(contracts.WEAPON_FORMS[weapon_form],pool[:count]))
    pool=candidates(main_one)
    count=2 if weapon_form=="dual_one_hand" else 1
    need(len(pool)>=count,"NO_ONE_HAND_BASE_WEAPON")
    weapon={"main_hand":pool[0]}
    if weapon_form=="dual_one_hand":weapon["off_hand"]=pool[1]
    if weapon_form=="one_hand_frill":
        values=support(frill); need(values,"NO_NON_WEAPON_OFFHAND_BASE")
        weapon["off_hand"]=values[0]
    if weapon_form=="one_hand_shield":
        values=support(shield); need(values,"NO_SHIELD_BASE")
        weapon["off_hand"]=values[0]
    return weapon

def select_class_spec(db,tier,cls,spec):
    db=gear.validate(db)
    need(tier.get("retail_build")==db["season_build"],
         "GEAR_AND_TIER_BUILD_MISMATCH")
    contract=contracts.lookup(cls,spec)
    need(contract is not None,"26_DPS_SPEC_CONTRACT_REQUIRED")
    info=tier["classes"].get(cls)
    need(type(info) is dict,"TIER_CLASS_MISSING")
    class_mask=info.get("allowed_class_mask")
    need(type(class_mask) is int and class_mask>0 and
         class_mask&(class_mask-1)==0,"TIER_CLASS_MASK_INVALID")
    family=contract["family"]
    tier5=info["pieces"]
    need(set(tier5)==set(contracts.TIER_SLOTS),"TIER_FIVE_SLOTS_MISSING")
    used=set(tier5.values())
    result={"tier_ids":dict(tier5),"four_tier_slots":list(FOUR),
            "ordinary":{},"weapons":{}}
    for slot in ORDINARY:
        matches=available_plain(db,slot=slot,family=family,
                                class_mask=class_mask,used=used)
        need(matches,"PLAIN_BASE_NOT_AVAILABLE_"+family+"_"+slot)
        result["ordinary"][slot]=matches[0]
        used.add(matches[0])
    for slot in COMMON:
        matches=available_plain(db,slot=slot,class_mask=class_mask,used=used)
        need(matches,"PLAIN_COMMON_NOT_AVAILABLE_"+slot)
        result.setdefault("common_gear",{})[slot]=matches[0]
        used.add(matches[0])
    result["weapons"]=shape_weapons(db,contract["weapon_form"],class_mask,\
                                     spec_key=cls+"/"+spec)
    need(len(set(result["weapons"].values()))==len(result["weapons"]),
         "DUPLICATE_WEAPON_IDS")
    return {"class":cls,"spec":spec,"armor_family":family,
            "weapon_form":contract["weapon_form"], **result,
            "weapon_subclass_proficiency_native_unverified":True,
            "tier_id_source":"ACTUAL_CURRENT_DB2_ITEMSET_NOT_PROFILE_COPY",
            "native_calls":0}

def build_all(db,tier):
    need(gear.validate(db)["season_build"]==tier["retail_build"],
         "GEAR_TIER_BUILD_MISMATCH")
    specs={}
    common=None
    for key in sorted(contracts.CONTRACTS):
        cls,spec=key.split("/")
        item=select_class_spec(db,tier,cls,spec)
        selected=item.pop("common_gear")
        if common is None:common=selected
        need(common==selected,"COMMON_GEAR_DRIFT")
        specs[key]=item
    need(len(specs)==26,"EXPECTED_26_DPS")
    return {"schema":SCHEMA,"status":"SOURCE_FIRST_COMPLETE_PHYSICAL_CANDIDATE_PREVIEW_ONLY",
       "season_build":db["season_build"],"target_ilevel_preview":334,
       "common_gear":common,"specializations":specs,
       "tier_classes":len(tier["classes"]),"dps_specs":len(specs),
       "four_piece_each":True,"old_profile_item_ids_copied":False,
       "weapon_class_proficiency_simc_verified":False,
       "all_items_physical_simc_accepted":False,
       "profile_activated_in_v098":False,"simc_native_calls":0}

def season_scope(*,db=None,tier=None,settings=None):
    """One opt-in, same-season equipment catalog for internal v098 stage only.

    The stable v139 serializer, gem/consumable declarations, and 26 contracts
    remain unchanged. No v144 equipment ID is copied; v171 + v168 supply
    every ordinary/weapon/tier item ID. Never alter pure.catalog() on disk.
    """
    import v139_pure_target_profile_composer as pure
    db=gear.read() if db is None else gear.validate(db)
    tier=load_tier() if tier is None else tier
    candidate=build_all(db,tier)
    config=pure.catalog() if settings is None else pure.validate_season(settings)
    budget=json.loads(BUDGET_PATH.read_text(encoding="utf8"))
    need(budget.get("retail_build")==candidate["season_build"] and
         config["default_consumables"]["gem_budget_J"]==
            budget["ordinary_gem"]["total_J"] and
         config["default_consumables"]["flask_budget_F"]==
            budget["flasks"]["total_F"],
         "P1_J_F_BUDGET_NOT_ALIGNED")
    scope={k:config[k] for k in ("schema","season","target_ilevel",
                                "character_level","gems","default_consumables")}
    if config.get("simc_item_db_source") is not None:
        scope["simc_item_db_source"]=config["simc_item_db_source"]
    scope.update({"common_gear":candidate["common_gear"],
          "specializations":{k:{
             "tier_ids":v["tier_ids"],
             "four_tier_slots":v["four_tier_slots"],
             "ordinary":v["ordinary"],
             "weapons":v["weapons"]}
             for k,v in candidate["specializations"].items()}})
    return pure.validate_season(scope)


def compose_stage(character,trinkets,*,db=None,tier=None,settings=None):
    """Build a NEW-SOURCE preview via existing v139 pure formatter ONLY.

    V139 standalone profile text has staging gear_* placeholders; do not feed
    it to DPS or count its physical compatibility as Native PASS.
    """
    import v139_pure_target_profile_composer as pure
    scope=season_scope(db=db,tier=tier,settings=settings)
    # If no more than four unchanged tier pieces, pure v139 retains default
    # SimC APL and no source character profile read.
    profile,proof,rows,tier_slots=pure.compose(
        character,trinkets,season=scope,target_ilevel=scope["target_ilevel"])
    need(proof["status"]=="STAGED_NOT_USER_READY"
         and proof["native_calls"]==0,"PROFILE_STAGE_WAS_PROMOTED")
    return {"schema":SCHEMA,"status":"PROFILE_TEXT_PREVIEW_ONLY_NOT_NATIVE_ACCEPTED",
       "profile_text":profile,"profile_receipt":proof,
       "spec":character["class"]+"/"+character["spec"],
       "new_current_season_equipment_only":True,
       "source_profile_item_ids_copied":False,
       "full_profile_native_accepted":False,
       "native_calls":0}
def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args(argv)
    try:
        result=build_all(gear.read(),load_tier())
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2,sort_keys=True,
                            ensure_ascii=False)+"\n",encoding="utf8")
        print(json.dumps({"status":result["status"],"specs":result["dps_specs"],
            "class_sets":result["tier_classes"],"native":0},sort_keys=True))
        return 0
    except (RepresentativeBlocked,gear.GearBlocked,ValueError,
            KeyError,OSError,TypeError) as exc:
        code=str(exc) if isinstance(exc,(RepresentativeBlocked,gear.GearBlocked)) else type(exc).__name__
        print(json.dumps({"status":"BLOCKED","code":code}))
        return 3
if __name__=="__main__":
    raise SystemExit(main())
