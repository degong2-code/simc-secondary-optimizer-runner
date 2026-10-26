#!/usr/bin/env python3
"""v101 shared representative-equipment assembly for existing source-backed profiles.

Four armor-family mapping + weapon-slot forms + CLASS-tier item IDs are
separate from per-spec SimC APL/profile producers. The four existing producers
remain the only executable source-backed cases. No new gear catalog, effect
model, rebalancing engine, source-profile rewrite, or Native SimC calls.
"""
from __future__ import annotations
import copy,pathlib

import v055_simc_item_selection as items
import v102_ordinary_armor_seed_pool as ordinary_pool
import v103_source_observed_weapon_types as weapon_types
import v082_fury_plate_dual_twohand_native as fury
import v083_paladin_single_2h_native as paladin
import v084_frost_cloth_1h_frill_native as frost
import v086_hunter_fixed_mail_representative as hunter
import v104_shared_pinned_rogue_shaman_composer as first_use

ARMOR_CLASSES={
    "cloth":frozenset(("mage","priest","warlock")),
    "leather":frozenset(("demonhunter","druid","monk","rogue")),
    "mail":frozenset(("evoker","hunter","shaman")),
    "plate":frozenset(("deathknight","paladin","warrior"))}
CLASS_ARMOR={cl:armor for armor,classes in ARMOR_CLASSES.items() for cl in classes}
TIER_FIVE=("head","shoulders","chest","hands","legs")
# Exact identity for the four source-backed class sets ONLY.
# No unverified item identities for the other nine classes.
CLASS_TIER_ITEMS={
    "warrior":{"head":271456,"shoulders":271454,"chest":271459,
               "hands":271457,"legs":271455},
    "paladin":{"head":271465,"shoulders":271463,"chest":271468,
               "hands":271466,"legs":271464},
    "mage":{"head":271564,"shoulders":271562,"chest":271567,
            "hands":271565,"legs":271563},
    "hunter":{"head":271492,"shoulders":271490,"chest":271495,
              "hands":271493,"legs":271491},
    "rogue":dict(first_use.TIERS["rogue"]),
    "shaman":dict(first_use.TIERS["shaman"])}
# Slot topology, not a promise that any given class can wield every subtype.
WEAPON_FORMS={
    "dual_two_hand":("main_hand","off_hand"),
    "dual_one_hand":("main_hand","off_hand"),
    "one_hand_shield":("main_hand","off_hand"),
    "one_hand_frill":("main_hand","off_hand"),
    "single_one_hand":("main_hand",),
    "single_two_hand":("main_hand",),
    "ranged":("main_hand",)}
ARCHETYPES={
    ("warrior","fury"):("v082_upstream_mid2_warrior_fury_reference.simc",
                        fury.source_profile,"dual_two_hand",fury.DECLARED_F),
    ("mage","frost"):("v084_upstream_mid2_mage_frost_reference.simc",
                      frost.source_profile,"one_hand_frill",frost.F_DECLARED),
    ("paladin","retribution"):("v083_upstream_mid2_paladin_retribution_reference.simc",
                               paladin.source_profile,"single_two_hand",
                               paladin.DECLARED_F),
    ("hunter","beast_mastery"):(
        "v079_upstream_mid2_hunter_beast_mastery_reference.simc",
        hunter.source_profile,"ranged",
        {"crit_rating":0,"haste_rating":165,"mastery_rating":0,
         "versatility_rating":0}),
    ("rogue","subtlety"):(
        first_use.PROFILES[("rogue","subtlety")]["filename"],
        first_use.producer(("rogue","subtlety")),"dual_one_hand",
        first_use.F_DECLARED),
    ("shaman","elemental"):(
        first_use.PROFILES[("shaman","elemental")]["filename"],
        first_use.producer(("shaman","elemental")),"one_hand_shield",
        first_use.F_DECLARED)}
FIXTURES=pathlib.Path(__file__).resolve().parents[1]/"integration_probes/fixtures"
# Fifth item is class-specific; previous representative ordinary item is
# source-specific (the v086 Hunter head differs from v079).
FIFTH_TIER={
    ("warrior","fury"):("legs",271455,271878),
    ("paladin","retribution"):("legs",271464,271878),
    ("mage","frost"):("head",271564,271874),
    ("hunter","beast_mastery"):("head",271492,249317),
    ("rogue","subtlety"):("chest",271513,251159),
    ("shaman","elemental"):("head",271483,249317)}

def ordinary_armor_seed(family,slot,ilevel):
    """Explicitly source-backed ordinary candidate for a future class build.

    The returned row is NOT automatically injected into current four already
    source-validated archetypes; missing ordinary family slots fail closed.
    """
    ordinary_pool.verify_pool()
    return ordinary_pool.row(family,slot,ilevel)

def available_ordinary_seed_slots(family):
    """Coverage is partial; no promise of an entire season armor set."""
    if family not in ordinary_pool.FAMILY_ROWS:return ()
    return tuple(sorted(ordinary_pool.FAMILY_ROWS[family]))

def source_backed_gear(key,folder,ilevel,need):
    """Factory APL is source-owned; ALL subsequent gear assembly is shared."""
    need(key in ARCHETYPES,"REPRESENTATIVE_ARCHETYPE_NOT_READY")
    filename,producer,form,F=ARCHETYPES[key]
    need(form in WEAPON_FORMS,"WEAPON_FORM_NOT_MAPPED")
    template=(FIXTURES/filename).read_text(encoding="utf8")
    base,cfg,fillers,_=producer(template,folder)
    need((cfg["character"]["class"],cfg["character"]["spec"])==key,
         "SOURCE_CHARACTER_DRIFT")
    need(key[0] in CLASS_ARMOR and key[0] in CLASS_TIER_ITEMS,
         "CLASS_ARMOR_OR_TIER_SOURCE_NOT_READY")
    # The minimum four-armor-family seed catalog has independent, pinned
    # source ID/slot provenance. It does not replace this builder's already
    # checked equipment or claim complete target-ilvl Native stat records.
    ordinary_pool.verify_pool()
    rows={r["slot"]:copy.deepcopy(r) for group in
          (cfg["equipment"]["tier"],cfg["equipment"]["crafted"],
           cfg["equipment"]["trinkets"],fillers) for r in group}
    groups={r["slot"]:group for group in ("tier","crafted","trinkets")
            for r in cfg["equipment"][group]}
    need(len(rows) in (15,16),"TEMPLATE_EXPECTED_FIFTEEN_OR_SIXTEEN_SLOTS")
    need(set(rows)&{"main_hand","off_hand"}==set(WEAPON_FORMS[form]),
         "SOURCE_WEAPON_TOPOLOGY_DRIFT")
    # Source-observed EXACT weapon subtypes and IDs, no imagined
    # alternate class/spec skill permissions or changed weapon DPS.
    weapon_types.validate_existing(key,rows,form)
    expected_tier=CLASS_TIER_ITEMS[key[0]]
    need(len(cfg["equipment"]["tier"])==4
         and all(slot in TIER_FIVE and row["item_id"]==expected_tier[slot]
                 for slot,row in
                 ((r["slot"],r) for r in cfg["equipment"]["tier"])),
         "SOURCE_CLASS_TIER_ID_DRIFT")
    fifth,known_tier,ordinary=FIFTH_TIER[key]
    need(known_tier==expected_tier[fifth] and groups.get(fifth) is None
         and rows[fifth]["item_id"]==ordinary,
         "SOURCE_FIFTH_CLASS_TIER_OR_ORDINARY_ID_DRIFT")
    for row in rows.values():
        row["ilevel"]=ilevel
    return base,cfg,rows,groups,form,F

def reconcile_four_tier(key,rows,groups,taken,ilevel,need):
    """Restore an exact source-backed fifth tier when one of four is displaced."""
    need(key in FIFTH_TIER,"FIFTH_CLASS_TIER_ID_UNAVAILABLE")
    count=sum(groups.get(k)=="tier" for k in TIER_FIVE)
    need(count<=4,"FIVE_TIER_LAYOUT_OUTSIDE_FOUR_ROW_CONTRACT")
    added=[]
    if count<4:
        slot,tier_id,ordinary_id=FIFTH_TIER[key]
        need(slot not in taken and groups.get(slot) is None
             and rows[slot]["item_id"]==ordinary_id,
             "FOUR_TIER_UNAVAILABLE_SELECTED_FIFTH_OR_UNKNOWN_SOURCE")
        options={k:v for k,v in rows[slot]["options"].items()
                 if k in ("gem_id","enchant","enchant_id")}
        rows[slot]={"slot":slot,"item_id":tier_id,"ilevel":ilevel,
                    "options":options}
        groups[slot]="tier"
        added.append(slot)
    need(sum(groups.get(k)=="tier" for k in TIER_FIVE)==4,
         "FOUR_TIER_NOT_SATISFIED")
    return added

def apply_user_equipment(key,rows,groups,user,ilevel,need):
    """Overlay selected items and reassign tier 4pc without item-combo search.

    Mutates only its private rows/groups objects. Selected catalyst specials
    are represented as ONE tier row plus optional typed fixed-L metadata.
    """
    taken=set()
    for group,selection in (("trinkets",user["trinkets"]),
                            ("special",user["special_items"]),
                            ("crafted",user["embellishments"])):
        for raw in selection:
            need(type(raw) is dict and set(raw)=={"slot","item_id","options"},
                 "SELECTED_ITEM_FIELDS")
            slot=raw["slot"]
            need(slot in rows and slot not in taken,
                 "SELECTED_SLOT_INVALID_OR_DUPLICATE")
            taken.add(slot)
            opts=items.checked_options(raw["options"])
            items.checked_id(raw["item_id"])
            slot_group=group
            if group=="trinkets":
                need(slot in ("trinket1","trinket2") and not
                     (set(opts)&{"crafted_stats","embellishment",
                                  "redirected_base_stats"}),
                     "INVALID_TRINKET_SELECTION")
            elif group=="special":
                need(not slot.startswith("trinket") and
                     not (set(opts)&{"crafted_stats","embellishment"}),
                     "SPECIAL_NOT_VALID_NONCRAFTED_SLOT")
                if groups.get(slot)=="tier":
                    need(raw["item_id"]==CLASS_TIER_ITEMS[key[0]][slot]
                         and "redirected_base_stats" in opts
                         and int(opts["redirected_base_stats"])!=raw["item_id"],
                         "CATALYST_CLASS_TIER_ID_AND_ORIGIN_REQUIRED")
                    slot_group="tier"
                elif (slot==FIFTH_TIER[key][0] and
                      "redirected_base_stats" in opts):
                    need(raw["item_id"]==CLASS_TIER_ITEMS[key[0]][slot] and
                         int(opts["redirected_base_stats"])!=raw["item_id"],
                         "CATALYST_FIFTH_CLASS_TIER_ID_OR_ORIGIN")
                    slot_group="tier"
                else:
                    need("redirected_base_stats" not in opts,
                         "CATALYST_REQUIRES_CLASS_TIER_SLOT")
            else:
                need(not slot.startswith("trinket") and
                     "embellishment" in opts and
                     "redirected_base_stats" not in opts,
                     "EMBELLISHMENT_NOT_ON_CRAFTED_EQUIPMENT")
            rows[slot]={"slot":slot,"item_id":raw["item_id"],
                        "ilevel":ilevel,"options":opts}
            groups[slot]=slot_group
    need({r["slot"] for r in user["trinkets"]}=={"trinket1","trinket2"},
         "USER_TRINKET_SLOTS_NOT_EXACT")
    restored=reconcile_four_tier(key,rows,groups,taken,ilevel,need)
    catalyst=[{"slot":slot,"tier_item_id":row["item_id"],
               "source_item_id":int(row["options"]["redirected_base_stats"])}
              for slot,row in rows.items()
              if groups.get(slot)=="tier"
              and "redirected_base_stats" in row["options"]]
    return restored,catalyst

def physical_gear_groups(rows,groups,catalyst):
    """Build current v061 contract with no duplicate slots or special L."""
    equip={g:[copy.deepcopy(row) for slot,row in rows.items()
              if groups.get(slot)==g]
           for g in ("tier","special","crafted","trinkets")}
    if catalyst:
        equip["catalyst_special_tier_slots"]=sorted(x["slot"] for x in catalyst)
    fillers=[copy.deepcopy(row) for slot,row in rows.items()
             if slot not in groups]
    return equip,fillers
