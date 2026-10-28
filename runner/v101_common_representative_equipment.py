#!/usr/bin/env python3
"""Shared source-backed representative-equipment assembly.

v127 owns declarative specialization source, tier, weapon, F and fifth-item
metadata. The v082/v083/v084/v086/v104 producers remain immutable source/APL
adapters while all downstream gear, CHMV and Native execution logic is shared.
No seasonal equipment DB, proc engine, or general 27-spec readiness claim.
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
import v127_dps_source_metadata as metadata
import v134_shared_mid2_profile_adapter as generic
import v133_mid2_target_representative_preview as target_preview
import v132_dps_source_batch_smoke as mid2_pins

ARMOR_CLASSES={
    "cloth":frozenset(("mage","priest","warlock")),
    "leather":frozenset(("demonhunter","druid","monk","rogue")),
    "mail":frozenset(("evoker","hunter","shaman")),
    "plate":frozenset(("deathknight","paladin","warrior"))}
CLASS_ARMOR={cl:armor for armor,classes in ARMOR_CLASSES.items() for cl in classes}
TIER_FIVE=("head","shoulders","chest","hands","legs")
# v127 source-backed metadata supplies per-spec tier, F, fixture, weapon and
# fifth ordinary selection. Legacy producers remain exact APL adapters.
CLASS_TIER_ITEMS={entry.character_class:entry.tier_ids()
                  for entry in metadata.SOURCE_BACKED}
# The 17 MID2 pinned sources reuse the same v134 adapter. Feral entered
# beta after v133 physical Native acceptance and subsequently completed
# its own target334 adaptive 6/6 Native/selected-pair 95% user receipt.
# Keep v136's separate historical accepted sixteen source receipts frozen.
GENERIC_PENDING=frozenset(
    tuple(k.split("/")) for k in mid2_pins.NEW)
for _key in GENERIC_PENDING:
    _cls=_key[0]
    _tier=dict(zip(TIER_FIVE,target_preview.FIVE_TIER[_cls]))
    if _cls not in CLASS_TIER_ITEMS:
        CLASS_TIER_ITEMS[_cls]=_tier
    else:
        assert CLASS_TIER_ITEMS[_cls]==_tier, "MID2_CLASS_TIER_DATA_DRIFT"
WEAPON_FORMS={
    "dual_two_hand":("main_hand","off_hand"),
    "dual_one_hand":("main_hand","off_hand"),
    "one_hand_shield":("main_hand","off_hand"),
    "one_hand_frill":("main_hand","off_hand"),
    "single_one_hand":("main_hand",),
    "single_two_hand":("main_hand",),
    "ranged":("main_hand",)}

PRODUCERS={
    "v082_fury":fury.source_profile,
    "v083_retribution":paladin.source_profile,
    "v084_frost":frost.source_profile,
    "v086_fixed_mail":hunter.source_profile}

def resolved_producer(entry):
    if entry.producer_id=="v104_shared":
        return first_use.producer(entry.key)
    if entry.producer_id not in PRODUCERS:
        raise metadata.SourceMetadataBlocked(
            "UNRESOLVED_SOURCE_PRODUCER:"+entry.producer_id)
    return PRODUCERS[entry.producer_id]

ARCHETYPES={
    entry.key:(entry.source_fixture,resolved_producer(entry),
               entry.weapon_form,entry.flask_vector())
    for entry in metadata.SOURCE_BACKED}
FIXTURES=pathlib.Path(__file__).resolve().parents[1]/"integration_probes/fixtures"
FIFTH_TIER={entry.key:entry.fifth_replacement()
            for entry in metadata.SOURCE_BACKED}

def validate_source_registry():
    """Fail closed on changes to six prior source-pinned contracts."""
    metadata.validate()
    for entry in metadata.SOURCE_BACKED:
        key=entry.key
        if CLASS_ARMOR.get(key[0])!=entry.armor_family:
            raise metadata.SourceMetadataBlocked(
                "REGISTERED_ARMOR_FAMILY_DRIFT:"+"/".join(key))
        if entry.producer_id=="v104_shared":
            source=first_use.PROFILES[key]
            if not (entry.source_fixture==source["filename"] and
                    entry.source_git_blob==source["source_sha"] and
                    entry.tier_ids()==first_use.TIERS[key[0]] and
                    entry.fifth_ordinary==source["fifth"] and
                    entry.flask_vector()==first_use.F_DECLARED):
                raise metadata.SourceMetadataBlocked(
                    "V104_LEGACY_PRODUCER_METADATA_DRIFT:"+"/".join(key))
        else:
            old_F={
                "v082_fury":fury.DECLARED_F,
                "v083_retribution":paladin.DECLARED_F,
                "v084_frost":frost.F_DECLARED,
                "v086_fixed_mail":{"crit_rating":0,"haste_rating":165,
                                  "mastery_rating":0,"versatility_rating":0}
            }[entry.producer_id]
            if entry.flask_vector()!=old_F:
                raise metadata.SourceMetadataBlocked(
                    "REGISTERED_SOURCE_FLASK_F_DRIFT:"+"/".join(key))
    return True

def ordinary_armor_seed(family,slot,ilevel):
    """Explicitly source-backed ordinary candidate for a future class build.

    The returned row is NOT automatically injected into the six already
    source-validated archetypes; missing ordinary family slots fail closed.
    """
    ordinary_pool.verify_pool()
    return ordinary_pool.row(family,slot,ilevel)

def available_ordinary_seed_slots(family):
    """Coverage is partial; no promise of an entire season armor set."""
    if family not in ordinary_pool.FAMILY_ROWS:return ()
    return tuple(sorted(ordinary_pool.FAMILY_ROWS[family]))

# P1-WEB-3: representative 23-rating gem examples, with source-observed
# colors. This is NOT a second gem/stat effect engine; SimC owns color effects.
from v135_source_gem_colors import SOURCE_GEM_COLOR, FOUR_COLOR_GEMS
# Source drafts inspect the common gem-color data. Register 16 new source
# adapters only after the shared constants are initialized, avoiding an
# import-time v101 -> v134 -> v133 -> v101 initialization cycle.
# A single pinned-source metadata read builds both registries. Previously
# the 17 source previews/fixture hashes were redundantly reread in two loops
# during each fresh server process startup, without adding integrity evidence.
for _key in sorted(GENERIC_PENDING):
    _info=generic.source_metadata("/".join(_key))
    ARCHETYPES[_key]=(_info["fixture"],generic.producer(_key),
                      _info["form"],_info["F"])
    _slot,_ordinary=_info["fifth"]
    FIFTH_TIER[_key]=(_slot,_info["tier"][_slot],_ordinary)
# v104 pins these two original source wrist slots as socketed, but its
# ordinary wrist replacements discard the source options. For 240967 ONLY,
# recover that one source-observed gem position before four-color adjustment.
# This is not proof the replacement item accepts a socket in Native SimC.
SOURCE_SOCKETED_WRIST_REPLACEMENTS={
    268240:240900,   # Subtlety: original wrist 271506 carried 240900
    273775:240906}  # Elemental: original wrist 244584 carried 240906

def ensure_representative_gem_colors(rows,diamond_id,need):
    """Keep six real ordinary gems; for 240967 cover all four colors.

    Fixes only missing colors, leaving a source profile unchanged if its
    socketed gems already cover all colors. Existing 240983 source scenarios
    are byte-preserved. The optimizer may overwrite secondary rating via
    gear_*; actual gem IDs remain on the physical items for SimC effects.
    """
    if diamond_id!=240967:
        return False
    slots=[]
    for slot in sorted(rows):
        if slot=="head" or slot.startswith("trinket"):
            continue
        gem_ids=rows[slot]["options"].get("gem_id")
        if gem_ids is None:
            continue
        tokens=gem_ids.split("/")
        need(all(t.isdigit() and int(t) not in (240967,240983) for t in tokens),
             "REPRESENTATIVE_ORDINARY_GEM_INVALID")
        for idx,token in enumerate(tokens):
            slots.append((slot,idx,int(token)))
    if len(slots)==5:
        wrist=rows.get("wrists")
        prior=(SOURCE_SOCKETED_WRIST_REPLACEMENTS.get(wrist["item_id"])
               if wrist else None)
        # Fail closed on arbitrary five-gem layouts; only the two source-
        # pinned v104 substitutions are allowed to regain the one wrist gem.
        if (prior is not None and
            "gem_id" not in wrist["options"] and
            all(gem_id==prior for _,_,gem_id in slots)):
            wrist["options"]["gem_id"]=str(prior)
            slots.append(("wrists",0,prior))
    need(len(slots)==6,"REPRESENTATIVE_SIX_ORDINARY_GEMS_REQUIRED")
    present=set()
    replaceable=[]
    for slot,idx,gem_id in slots:
        color=SOURCE_GEM_COLOR.get(gem_id)
        if color is None or color in present:
            replaceable.append((slot,idx))
        else:
            present.add(color)
    missing=[color for color in FOUR_COLOR_GEMS if color not in present]
    need(len(replaceable)>=len(missing),"REPRESENTATIVE_GEM_COLORS_NOT_FEASIBLE")
    # For the 240967 physical color-set contract, source gems with no
    # validated color mapping cannot be counted as one of the four colors.
    # Replace only those unknown-color IDs with previously source-seen gems;
    # keep original IDs otherwise. The existing seven 240967 plans contain
    # no such unknown IDs, so their sealed bytes remain unchanged.
    unknown={(slot,idx) for slot,idx,gem_id in slots
             if SOURCE_GEM_COLOR.get(gem_id) is None}
    replacement={(slot,idx):FOUR_COLOR_GEMS[color]
                 for (slot,idx),color in zip(replaceable,missing)}
    for slot,idx in unknown:
        replacement.setdefault((slot,idx),FOUR_COLOR_GEMS["garnet"])
    if not replacement:
        return False
    slot_tokens={slot:rows[slot]["options"]["gem_id"].split("/")
                 for slot,_,_ in slots}
    for (slot,idx),gem_id in replacement.items():
        slot_tokens[slot][idx]=str(gem_id)
    for slot,tokens in slot_tokens.items():
        rows[slot]["options"]["gem_id"]="/".join(tokens)
    return True

# Opt-in only. A 35-iteration physical Native smoke accepted this precise
# season-2 Havoc feet replacement; target CHMV/native gear_* is NOT certified.
# Never rewrite the 24 existing default profiles or historical DPS identities.
ORDINARY_VARIANTS={
    "mid2_havoc_leather_feet_v1":{
        "key":("demonhunter","havoc"),"family":"leather","slot":"feet",
        "source_item_id":159327,"item_id":268261,
        "options":{"enchant_id":"7963"}}
}

def source_backed_gear(key,folder,ilevel,need,*,ordinary_variant=None):
    """Factory APL is source-owned; gear assembly is shared; variant opt-in."""
    need(key in ARCHETYPES,"REPRESENTATIVE_ARCHETYPE_NOT_READY")
    if ordinary_variant is not None:
        need(type(ordinary_variant) is str
             and ordinary_variant in ORDINARY_VARIANTS,
             "ORDINARY_VARIANT_NOT_PINNED")
        spec=ORDINARY_VARIANTS[ordinary_variant]
        need(key==spec["key"] and ilevel==334,
             "ORDINARY_VARIANT_SPEC_OR_TARGET_LEVEL_NOT_VERIFIED")
    validate_source_registry()
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
    if key in GENERIC_PENDING:
        # All new weapon item IDs were accepted by original-source SimC
        # smoke; preserve exactly those hand IDs on representative profiles.
        _source=mid2_pins.validate_source("/".join(key))["source"]
        _ids,_=generic.draft.fields.equipment(_source,items.SLOTS,need=need,
            duplicate_prefix="MID2_SOURCE_DUPLICATE_WEAPON_OR_GEAR:",
            missing_id_prefix="MID2_SOURCE_MISSING_ID:")
        need(all(rows[hand]["item_id"]==_ids[hand]
                 for hand in WEAPON_FORMS[form]),
             "MID2_SOURCE_WEAPON_ITEM_DRIFT")
    else:
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
    if ordinary_variant is not None:
        spec=ORDINARY_VARIANTS[ordinary_variant]
        slot=spec["slot"]
        need(groups.get(slot) is None
             and rows[slot]["item_id"]==spec["source_item_id"]
             and rows[slot]["options"]==spec["options"],
             "ORDINARY_VARIANT_SOURCE_SLOT_OR_OPTIONS_CHANGED")
        candidate=ordinary_pool.row(spec["family"],slot,ilevel)
        need(candidate["item_id"]==spec["item_id"]
             and candidate["options"]=={}
             and ordinary_pool.provenance(spec["family"],slot)["source_kind"]=="ordinary",
             "ORDINARY_VARIANT_PROVENANCE_CHANGED")
        # Keep exactly the separately source-observed original enchant.
        # No sockets, proc reimplementation, primary/rating guess or gear_DB.
        rows[slot]={**candidate,"options":dict(spec["options"])}
    return base,cfg,rows,groups,form,F

def reconcile_four_tier(key,rows,groups,taken,ilevel,need,*,fifth_override=None):
    """Restore an exact source-backed fifth tier when one of four is displaced."""
    fifth_data=FIFTH_TIER.get(key) if fifth_override is None else fifth_override
    need(fifth_data is not None,"FIFTH_CLASS_TIER_ID_UNAVAILABLE")
    count=sum(groups.get(k)=="tier" for k in TIER_FIVE)
    need(count<=4,"FIVE_TIER_LAYOUT_OUTSIDE_FOUR_ROW_CONTRACT")
    added=[]
    if count<4:
        slot,tier_id,ordinary_id=fifth_data
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

def apply_user_equipment(key,rows,groups,user,ilevel,need,*,
                         tier_override=None,fifth_override=None):
    """Overlay selected items and reassign tier 4pc without item-combo search.

    Mutates only its private rows/groups objects. Selected catalyst specials
    are represented as ONE tier row plus optional typed fixed-L metadata.
    """
    tier_map=(CLASS_TIER_ITEMS[key[0]] if tier_override is None
              else tier_override)
    fifth_data=(FIFTH_TIER[key] if fifth_override is None
                else fifth_override)
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
            # Retain the existing representative socket layout when a user
            # swaps special/crafted gear. SimC must still accept the exact item.
            if group in ("special","crafted") and "gem_id" not in opts:
                source_gems=rows[slot]["options"].get("gem_id")
                if source_gems:
                    opts["gem_id"]=source_gems
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
                    need(raw["item_id"]==tier_map[slot]
                         and "redirected_base_stats" in opts
                         and int(opts["redirected_base_stats"])!=raw["item_id"],
                         "CATALYST_CLASS_TIER_ID_AND_ORIGIN_REQUIRED")
                    slot_group="tier"
                elif (slot==fifth_data[0] and
                      "redirected_base_stats" in opts):
                    need(raw["item_id"]==tier_map[slot] and
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
    restored=reconcile_four_tier(key,rows,groups,taken,ilevel,need,
                                  fifth_override=fifth_data)
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
