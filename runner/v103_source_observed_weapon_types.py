#!/usr/bin/env python3
"""v103: source-observed weapon TYPES, not invented spec-wide skill legality.

Exact weapon subtype and hand identity from pinned original SimC fixtures +
item pages. Only the existing four v098 profiles are executable here. Rogue
and Elemental Shaman are observed source shapes for future expansion, NOT
newly enabled whole character/APL/gear profiles.

No weapon effect simulation, general equipment catalogue or Native calls.
"""
from __future__ import annotations
import functools,hashlib,pathlib,re

ROOT=pathlib.Path(__file__).resolve().parents[1]
SCHEMA="v103_source_observed_spec_weapon_types_v1"
# Exact metadata: one existing source fixture per class/spec. Specialization's
# ALLOWED other weapon forms are NOT inferred from one equipped shape.
SOURCE={
 ("warrior","fury"):("integration_probes/fixtures/v082_upstream_mid2_warrior_fury_reference.simc",
                     "3225992ed5b754ad5d61e8b785d9d859f1eed1be","dual_two_hand"),
 ("paladin","retribution"):("integration_probes/fixtures/v083_upstream_mid2_paladin_retribution_reference.simc",
                             "864e857c5d8cdbaa5b03939f077fcb657a4784aa","single_two_hand"),
 ("mage","frost"):("integration_probes/fixtures/v084_upstream_mid2_mage_frost_reference.simc",
                   "b787824a95020a7cdd0934ed5e004695726db138","one_hand_frill"),
 ("hunter","beast_mastery"):("integration_probes/fixtures/v079_upstream_mid2_hunter_beast_mastery_reference.simc",
                             "fd9399a7ee0c9c39a362ba31a0d8308e3e000490","ranged"),
 ("rogue","subtlety"):("integration_probes/fixtures/v068_upstream_mid2_rogue_subtlety_reference.simc",
                       "b704e6326959432a82d14a6b774c79183d5b2af4","dual_one_hand"),
 ("shaman","elemental"):("integration_probes/fixtures/v078_upstream_mid2_shaman_elemental_reference.simc",
                         "c92d111e37bd684647e4637dcfef3ccb92864cde","one_hand_shield")}
# Items in the exact source, (item_id, subtype, class-appropriate primary
# nature) - this is a FACTUAL WITNESS to a usable source profile, not an
# exhaustive class weapon license. Crafted random-secondary items remain
# explicitly identified; their Native stat variant must have exact options.
OBSERVED={
 ("warrior","fury"):{
     "main_hand":(268213,"axe_2h","strength_or_agility"),
     "off_hand":(237847,"polearm_2h","strength_or_agility")},
 ("paladin","retribution"):{
     "main_hand":(268213,"axe_2h","strength_or_agility")},
 ("mage","frost"):{
     "main_hand":(271092,"dagger_1h","intellect"),
     "off_hand":(245769,"held_offhand","intellect")},
 ("hunter","beast_mastery"):{
     "main_hand":(268207,"bow_ranged","agility")},
 ("rogue","subtlety"):{
     "main_hand":(271093,"dagger_1h","agility"),
     "off_hand":(237837,"dagger_1h","agility")},
 ("shaman","elemental"):{
     "main_hand":(271092,"dagger_1h","intellect"),
     "off_hand":(268262,"shield_offhand","intellect")}}
SLOTS_FOR_FORM={
    "dual_two_hand":("main_hand","off_hand"),
    "single_two_hand":("main_hand",),
    "one_hand_frill":("main_hand","off_hand"),
    "ranged":("main_hand",),
    "dual_one_hand":("main_hand","off_hand"),
    "one_hand_shield":("main_hand","off_hand")}
# Each URL is provenance for item subtype, NOT a Native effects/static witness.
TYPE_SOURCES={
 268213:"https://www.wowhead.com/item=268213",
 237847:"https://www.wowhead.com/item=237847",
 271092:"https://www.wowhead.com/item=271092",
 245769:"https://www.wowhead.com/item=245769",
 268207:"https://www.wowhead.com/item=268207",
 271093:"https://www.wowhead.com/item=271093",
 237837:"https://www.wowhead.com/item=237837",
 268262:"https://www.wowhead.com/item=268262"}
EXECUTABLE_SOURCES=frozenset((("warrior","fury"),("paladin","retribution"),
                             ("mage","frost"),("hunter","beast_mastery")))

class WeaponSourceBlocked(ValueError):pass
def need(ok,reason):
    if not ok:raise WeaponSourceBlocked(reason)
def git_blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()

@functools.lru_cache(maxsize=1)
def verify_observed():
    need(set(SOURCE)==set(OBSERVED) and set(OBSERVED)==set(EXECUTABLE_SOURCES)|{
        ("rogue","subtlety"),("shaman","elemental")},"WEAPON_SOURCE_SCOPE_DRIFT")
    ids=set()
    for key,(path,sha,form) in SOURCE.items():
        raw=(ROOT/path).read_bytes()
        need(git_blob(raw)==sha,"WEAPON_SOURCE_GIT_BLOB_DRIFT:"+"/".join(key))
        need(form in SLOTS_FOR_FORM and
             set(OBSERVED[key])==set(SLOTS_FOR_FORM[form]),
             "SOURCE_WEAPON_HAND_TOPOLOGY_DRIFT:"+"/".join(key))
        parsed={}
        for line in raw.decode("utf8").splitlines():
            if line.startswith("# Gear Summary"):break
            slot,sep,value=line.partition("=")
            if not sep or slot not in ("main_hand","off_hand"):continue
            m=re.findall(r"(?:^|,)id=([1-9][0-9]*)(?:,|$)",value)
            need(len(m)==1 and slot not in parsed,
                 "SOURCE_WEAPON_ID_AMBIGUOUS:"+"/".join(key))
            parsed[slot]=int(m[0])
        for slot,(id_,type_,primary) in OBSERVED[key].items():
            need(parsed[slot]==id_ and id_ in TYPE_SOURCES
                 and type_ in {"axe_2h","polearm_2h","dagger_1h",
                               "held_offhand","bow_ranged","shield_offhand"}
                 and primary in ("strength_or_agility","intellect","agility"),
                 "SOURCE_WEAPON_SUBTYPE_OR_ID_DRIFT:"+"/".join(key)+":"+slot)
            ids.add(id_)
    return {"schema":SCHEMA,"source_profile_shapes":len(SOURCE),
            "executable_source_shapes":len(EXECUTABLE_SOURCES),
            "unique_item_ids":len(ids),"native_calls":0,
            "not_full_spec_weapon_legality":True,
            "not_full_armory":True}

def validate_existing(key,rows,form):
    """Fail closed on original source item/hand/subtype drift only."""
    verify_observed()
    need(key in EXECUTABLE_SOURCES and
         SOURCE[key][2]==form,"EXECUTABLE_WEAPON_FORM_NOT_SOURCE_BACKED")
    for hand,(id_,subtype,primary) in OBSERVED[key].items():
        need(hand in rows and rows[hand]["item_id"]==id_,
             "EXECUTABLE_SOURCE_WEAPON_ITEM_CHANGED:"+"/".join(key)+":"+hand)
    need(set(OBSERVED[key])==set(rows)&{"main_hand","off_hand"},
         "EXECUTABLE_SOURCE_WEAPON_HANDS_CHANGED")
    return True

def source_shape(key):
    """Read-only description; a mere observation NEVER authorizes executable."""
    verify_observed()
    need(key in SOURCE,"WEAPON_SPEC_SOURCE_NOT_AVAILABLE")
    return {"spec":"/".join(key),"form":SOURCE[key][2],
            "is_currently_executable":key in EXECUTABLE_SOURCES,
            "weapons":{hand:{"item_id":id_,"subtype":kind,
                             "primary_class":primary,
                             "item_reference":TYPE_SOURCES[id_]}
                       for hand,(id_,kind,primary) in OBSERVED[key].items()},
            "all_other_weapon_forms_unassessed":True}
