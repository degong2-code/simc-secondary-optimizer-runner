#!/usr/bin/env python3
"""v108: bounded SimC-native consumable and primary-only diamond overrides.

Not a consumable optimizer or stat-effect simulator. Supported flask stays
source-pinned because declared F=165 has not been Native remeasured for an
alternative flask. Omnium Folio is NOT augmentation (augment rune): do not
invent a SimC option for its five chosen runes.
"""
from __future__ import annotations
import copy, hashlib, re
import v061_scenario_contract as scenario

SCHEMA="v108_source_native_consumable_overrides_v1"
ASSIGNMENTS=("flask","food","potion","augmentation")
# Exact spellings witnessed in pinned six MID2 SimC source fixtures.
SUPPORTED={
 "food":frozenset(("harandar_celebration","silvermoon_parade","royal_roast","disabled")),
 "potion":frozenset(("potion_of_recklessness_2","lights_potential_2","disabled")),
 "augmentation":frozenset(("void_touched","void_touched_augment_rune","disabled"))}
# Both are PRIMARY or effect-only Midnight diamonds; they contribute
# zero secondary rating, so they do not alter legacy fixed J=138.
DIAMONDS=frozenset((240983,240967))
# Whole loadouts from six pinned MID2 fixtures. Mixing rune choices between
# independently sourced rows is NOT enabled until checked on real SimC.
OMNIUM_PRESETS=frozenset((
 "136822:1/136816:1/136817:1/136818:1/136814:1",
 "136822:1/136819:1/136817:1/136815:1/136814:1",
 "136822:1/136819:1/136817:1/136821:1/136814:1",
 "136822:1/136823:1/136817:1/136818:1/136814:1",
 "136822:1/136816:1/136817:1/136821:1/136814:1",
 "136822:1/136816:1/136817:1/136815:1/136814:1"))
CHOICE_FIELDS=frozenset(("flask","food","potion","augmentation",
                         "diamond_id","omnium_talents"))

class ConsumableBlocked(ValueError):pass
def need(ok,why):
    if not ok:raise ConsumableBlocked("V108_"+why)

def source_tokens(profile):
    out={}
    for line in profile.splitlines():
        key,sep,value=line.partition("=")
        if sep and key in ASSIGNMENTS+("omnium_talents",):
            need(key not in out,"DUPLICATE_CONSUMABLE_SOURCE:"+key)
            need(bool(re.fullmatch(r"[a-z0-9_]{1,90}",value)),
                 "SOURCE_CONSUMABLE_TOKEN_INVALID:"+key)
            out[key]=value
    need(set(out)==set(ASSIGNMENTS),"SOURCE_FOUR_CONSUMABLES_REQUIRED")
    return out

def default_choice(profile,head):
    tokens=source_tokens(profile)
    gem=head.get("options",{}).get("gem_id")
    need(gem is None or gem.isdigit() and int(gem) in DIAMONDS,
         "SOURCE_PRIMARY_ONLY_DIAMOND_NOT_READY")
    folio=[line.partition("=")[2] for line in profile.splitlines()
           if line.startswith("omnium_talents=")]
    need(len(folio)==1 and folio[0] in OMNIUM_PRESETS,
         "SOURCE_OMNIUM_LOADOUT_NOT_PINNED")
    return {**tokens,"diamond_id":int(gem) if gem else 0,
            "omnium_talents":folio[0]}

def validate_choice(raw,base):
    need(type(raw) is dict and set(raw)==CHOICE_FIELDS,"CHOICE_FIELDS")
    need(type(base) is dict and set(base)==CHOICE_FIELDS,"DEFAULT_CHOICES_FIELDS")
    result={}
    need(raw["flask"] in ("source_default",base["flask"]),
         "ALTERNATE_FLASK_F_VECTOR_NOT_NATIVE_VERIFIED")
    result["flask"]=base["flask"]
    for key in ("food","potion","augmentation"):
        v=raw[key]
        if v=="source_default":v=base[key]
        need(type(v) is str and v in SUPPORTED[key],
             "UNVERIFIED_SIMC_TOKEN:"+key)
        result[key]=v
    diamond=base["diamond_id"] if raw["diamond_id"]==0 else raw["diamond_id"]
    need(type(diamond) is int and diamond in (DIAMONDS|{0}),
         "DIAMOND_SECONDARY_BUDGET_NOT_VERIFIED")
    result["diamond_id"]=diamond
    folio=raw["omnium_talents"]
    if folio=="source_default":folio=base["omnium_talents"]
    need(type(folio) is str and folio in OMNIUM_PRESETS,
         "OMNIUM_LOADOUT_NOT_SOURCE_OBSERVED")
    result["omnium_talents"]=folio
    return result

def apply(profile,cfg,rows,chosen=None):
    """Profile/cfg are already assembled from exact user gear rows.

    Receives user selections BEFORE oil.configure() rehashes the final SimC
    profile. Existing v098/v061 remain owners of budget B,J,F/O/L, Native.
    """
    initial=default_choice(profile,rows["head"])
    raw=initial if chosen is None else validate_choice(chosen,initial)
    need(cfg["consumables"]["gem_budget_J"]==138 and
         cfg["consumables"]["flask_budget_F"]==165,
         "SOURCE_J_F_UNEXPECTED")
    need(cfg["consumables"]["flask"]==initial["flask"],
         "SOURCE_FLASK_SCENARIO_MISMATCH")
    seen=set();out=[]
    for line in profile.splitlines():
        key,sep,_=line.partition("=")
        if sep and key in ASSIGNMENTS:
            need(key not in seen,"DUPLICATE_PROFILE_CONSUMABLE:"+key)
            seen.add(key)
            out.append(key+"="+raw[key])
        else:
            out.append(line)
    need(seen==set(ASSIGNMENTS)|{"omnium_talents"},
         "INCOMPLETE_CONSUMABLE_OR_OMNIUM_ASSIGNMENTS")
    updated=copy.deepcopy(cfg)
    for key in ("flask","food","potion"):
        updated["consumables"][key]=raw[key]
    # v061 consumable schema has no separate augmentation: the SimC line
    # and final profile_sha256 are the exact Native ownership boundary.
    head=rows["head"]
    need((str(head["options"].get("gem_id","0"))==
          str(initial["diamond_id"])),"DIAMOND_SOURCE_ROW_CHANGED")
    if raw["diamond_id"]:
        head["options"]["gem_id"]=str(raw["diamond_id"])
    else:
        head["options"].pop("gem_id",None)
    updated["consumables"]["special_gem_id"]=raw["diamond_id"] or None
    new_profile="\n".join(out).rstrip()+"\n"
    updated["source"]["profile_sha256"]=hashlib.sha256(
        new_profile.encode("utf8")).hexdigest()
    # The equipment override happens after profile's original gear rows
    # were generated: caller must recompose equipment lines using head.
    scenario.normalize(updated)
    return {"profile":new_profile,"scenario":updated,
            "selected":raw,"changed":raw!=initial,
            "gem_secondary_J_unchanged":True,
            "flask_F_unchanged":True,
            "omnium_folio_not_augmentation":True,
            "omnium_whole_source_preset_only":True}

def set_head_gem(profile,head):
    """Replace ONLY existing head equipment line, preserving other options."""
    import v055_simc_item_selection as items
    slots=[line for line in profile.splitlines() if line.startswith("head=")]
    need(len(slots)==1,"SINGLE_HEAD_REQUIRED")
    new_line=items.equipment_line(
        "head",head["item_id"],head["ilevel"],head["options"])
    out=[new_line if line.startswith("head=") else line
         for line in profile.splitlines()]
    return "\n".join(out).rstrip()+"\n"
