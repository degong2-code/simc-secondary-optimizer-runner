#!/usr/bin/env python3
"""v102: minimal four-armor-family, actual-ID representative ordinary seed pool.

READINESS DATA, not a new item database or a full representative profile.
Pinned source-ID/slot, armor-material corroboration and source corrections are
separate from Native exact rating, item-proc mechanics and gear recommendations.
Never borrow crafted/random/class-restricted tier pieces as generic fillers.
No Native SimC or network calls.
"""
from __future__ import annotations
import functools,hashlib,pathlib,re

import v055_simc_item_selection as selected

ROOT=pathlib.Path(__file__).resolve().parents[1]
SCHEMA="v102_armor_family_ordinary_seed_v1"
# Pinned original Git blobs (not SimC target variant/cache identities).
SOURCE={
 "frost":("integration_probes/fixtures/v084_upstream_mid2_mage_frost_reference.simc",
          "b787824a95020a7cdd0934ed5e004695726db138"),
 "fire":("integration_probes/fixtures/v084_upstream_mid2_mage_fire_nontier_head_source.simc",
         "9fae08d2f1c49f3a964f9415540929723384e6fe"),
 "rogue":("integration_probes/fixtures/v068_upstream_mid2_rogue_subtlety_reference.simc",
          "b704e6326959432a82d14a6b774c79183d5b2af4"),
 "shaman":("integration_probes/fixtures/v078_upstream_mid2_shaman_elemental_reference.simc",
           "c92d111e37bd684647e4637dcfef3ccb92864cde"),
 "warrior":("integration_probes/fixtures/v082_upstream_mid2_warrior_fury_reference.simc",
            "3225992ed5b754ad5d61e8b785d9d859f1eed1be"),
 # Official v132 MID2 Feral gear already accepted in physical target334 Native.
 "feral_mid2":("integration_probes/fixtures/v132_MID2_Druid_Feral.simc",
               "29c4bd2329114bbdcbf36f4bc330d52e39349e72"),
 "marksman_mid2":("integration_probes/fixtures/v132_MID2_Hunter_Marksmanship.simc",
                  "87582489548939934be9bb2c5e74709ea74363b3")}
# Site corroboration confirms physical equipment ARMOR TYPE and SLOT.
# These are selected representative candidates, not a season-wide DB.
# Each tuple: (source nickname, real item_id, origin_type, user-visible name).
FAMILY_ROWS={
 "cloth":{
    "wrists":("frost",251154,"ordinary","Winter's Embrace Bracers"),
    "waist":("fire",268257,"ordinary","Caustic Chain-Wrapped Sash"),
    "feet":("frost",268255,"ordinary","Cackling Soultreads")},
 "leather":{
    "chest":("rogue",251159,"ordinary","War Trial Vestments"),
    "wrists":("web_live",268240,"ordinary","Restless Spirit Shackles"),
    "waist":("rogue",268256,"ordinary","Sash of the Forlorn Vessel"),
    "feet":("feral_mid2",268261,"ordinary","Bespittled Slitherslippers")},
 "mail":{
    "head":("marksman_mid2",271441,"ordinary","Crushing Coiler Coif"),
    "wrists":("web_live",273775,"ordinary","Hydra Scale Wristguards"),
    "waist":("shaman",268254,"ordinary","Serpentine Mixing Belt"),
    "feet":("marksman_mid2",271440,"ordinary","Greaves of the Noxious Depths")},
 "plate":{
    "wrists":("web_live",268239,"ordinary","Shellbound Bracers"),
    "waist":("warrior",268259,"ordinary","Girdle of Toxic Regret"),
    "feet":("warrior",268260,"ordinary","Scaled Fiend's Warboots")}}
FAMILY_SET=frozenset(("cloth","leather","mail","plate"))
REQUIRED_ITEM_SLOTS=frozenset(("head","shoulders","chest","wrists",
                               "hands","waist","legs","feet"))
# References are metadata only. Static rating is always from exact Native
# cache identity, not from these URLs or current equipment at another level.
ITEM_URLS={
 251154:"https://www.wowhead.com/item=251154",
 268257:"https://www.wowhead.com/item=268257",
 268255:"https://www.wowhead.com/item=268255",
 251159:"https://www.wowhead.com/item=251159",
 268240:"https://www.wowhead.com/item=268240",
 273775:"https://www.wowhead.com/item=273775",
 268239:"https://www.wowhead.com/item=268239",
 268256:"https://www.wowhead.com/item=268256",
 268261:"https://www.wowhead.com/item=268261",
 271441:"https://www.wowhead.com/item=271441",
 268254:"https://www.wowhead.com/item=268254",
 271440:"https://www.wowhead.com/item=271440",
 268259:"https://www.wowhead.com/item=268259",
 268260:"https://www.wowhead.com/item=268260"}

# Live season item pages were reviewed for material, equipment slot and
# fixed secondaries. This is item identity evidence, NOT Native JSON2 stats.
WEB_SOURCE_DETAILS={
    268240:("leather","wrists","crit/haste",
            "https://www.wowhead.com/item=268240"),
    273775:("mail","wrists","vers/mastery",
            "https://www.wowhead.com/ptr/item=273775"),
    268239:("plate","wrists","crit/mastery",
            "https://www.wowhead.com/ptr/item=268239")}
class PoolBlocked(ValueError):pass
def need(ok,reason):
    if not ok:raise PoolBlocked(reason)

def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()

def source_ids(source_key):
    """Read only the pinned data; original bonus/options are not copied."""
    rel,sha=SOURCE[source_key]
    raw=(ROOT/rel).read_bytes()
    need(git_blob(raw)==sha,"ORDINARY_SOURCE_GIT_BLOB_DRIFT:"+source_key)
    result={}
    for line in raw.decode("utf8").splitlines():
        if line.startswith("# Gear Summary"):break
        slot,sep,value=line.partition("=")
        if not sep or slot not in REQUIRED_ITEM_SLOTS:continue
        matches=re.findall(r"(?:^|,)id=([1-9][0-9]*)(?:,|$)",value)
        need(slot not in result and len(matches)==1,
             "ORDINARY_SOURCE_EQUIPMENT_ID_AMBIGUOUS:"+source_key+":"+slot)
        result[slot]=int(matches[0])
    return result

@functools.lru_cache(maxsize=1)
def verify_pool():
    """Source provenance/readiness check, not item effect/stat verification.

    Pinned immutable Git fixture bytes are checked once per process; repeated
    optimizer sessions do not reread source fixture files for every candidate.
    """
    need(set(FAMILY_ROWS)==FAMILY_SET,"ARMOR_FAMILY_POOL_MISSING")
    need(all(type(v) is dict and 1<=len(v)<=len(REQUIRED_ITEM_SLOTS)
             for v in FAMILY_ROWS.values()),"ORDINARY_POOL_SHAPE")
    used_ids=set();sources={}
    entries=0
    for family,items in FAMILY_ROWS.items():
        for slot,(source,id_,kind,name) in items.items():
            need(slot in REQUIRED_ITEM_SLOTS and
                 type(id_) is int and id_>0 and
                 name and ITEM_URLS.get(id_) and id_ not in used_ids,
                 "ORDINARY_POOL_DUPLICATE_OR_UNGROUNDED:"+family+":"+slot)
            used_ids.add(id_);entries+=1
            selected.checked_id(id_)
            if source=="web_live":
                need(kind=="ordinary" and
                     WEB_SOURCE_DETAILS.get(id_,())[:2]==(family,slot)
                     and WEB_SOURCE_DETAILS[id_][3].startswith("https://www.wowhead.com/"),
                     "PUBLIC_SEASON_ITEM_ID_MATERIAL_SLOT_DRIFT")
            else:
                need(source in SOURCE and kind in ("ordinary","legacy_reference"),
                     "ORDINARY_SOURCE_CLASSIFICATION")
                if source not in sources:sources[source]=source_ids(source)
                need(sources[source].get(slot)==id_,
                     "ORDINARY_SOURCE_ITEM_SLOT_ID_DRIFT:"+family+":"+slot)
            # No crafted/tier subclass substitutions are taken from source.
    need(entries==14,"ORDINARY_SEED_COUNT_DRIFT")
    return {"schema":SCHEMA,"status":"FOUR_FAMILY_PARTIAL_ORDINARY_POOL",
            "family_slot_counts":{x:len(FAMILY_ROWS[x])
                                  for x in sorted(FAMILY_ROWS)},
            "source_backed_item_ids":entries,"fully_equipped_profiles":0,
            "not_a_full_armor_pool":True,"native_calls":0,
            "new_variant_stats_native_verified":False}

def row(family,slot,ilevel):
    """Source-verified ID in correct family/slot, options empty by design.

    Do not claim the exact item variant is in Native static cache: changed
    target ilvl and source modifiers produce distinct digest identities.
    """
    need(type(family) is str and family in FAMILY_SET,"ARMOR_FAMILY_UNSUPPORTED")
    need(type(slot) is str and slot in FAMILY_ROWS[family],
         "ORDINARY_SLOT_NOT_SOURCE_READY:"+str(family)+":"+str(slot))
    need(type(ilevel) is int and 266<=ilevel<=344,
         "ORDINARY_ILVL_OUTSIDE_APPROVED_REFERENCE")
    source,item_id,kind,name=FAMILY_ROWS[family][slot]
    selected.checked_id(item_id)
    return {"slot":slot,"item_id":item_id,"ilevel":ilevel,"options":{}}

def provenance(family,slot):
    need(family in FAMILY_SET and slot in FAMILY_ROWS[family],
         "ORDINARY_ITEM_NOT_REGISTERED")
    source,item_id,kind,name=FAMILY_ROWS[family][slot]
    fixture=(SOURCE[source][0] if source in SOURCE else
             "LIVE_WOWHEAD_12_1_ITEM_ID_AND_MATERIAL")
    return {"armor_family":family,"slot":slot,"item_id":item_id,
            "name":name,"source_kind":kind,
            "source_file":fixture,"item_reference":ITEM_URLS[item_id],
            "not_verified_native_exact_target_variant":True,
            "not_an_item_acquisition_recommendation":True}
