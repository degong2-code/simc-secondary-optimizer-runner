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
# Current-season code-only tier placement changes must rekey new v106 sessions.
CURRENT_SEASON_TIER_LAYOUT_POLICY="v187_selected_4_of_5_and_catalyst_overflow_v1"
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

class _LazySourceRegistry(dict):
    """Keep all 24 legacy keys visible without reading 17 source fixtures.

    A legacy value is resolved and source-validated only on first access.
    The existing source producer performs its original checks on execution.
    This registry is NOT part of the source-independent season compiler.
    """
    def __getitem__(self,key):
        value=dict.__getitem__(self,key)
        if value is None:
            _resolve_generic_source(key)
            value=dict.__getitem__(self,key)
        return value

    def get(self,key,default=None):
        return self[key] if key in self else default

    def _resolve_all(self):
        for key in self:
            self[key]

    def items(self):
        self._resolve_all()
        return dict.items(self)

    def values(self):
        self._resolve_all()
        return dict.values(self)

    def copy(self):
        self._resolve_all()
        return dict.copy(self)


ARCHETYPES=_LazySourceRegistry({
    entry.key:(entry.source_fixture,resolved_producer(entry),
               entry.weapon_form,entry.flask_vector())
    for entry in metadata.SOURCE_BACKED})
FIXTURES=pathlib.Path(__file__).resolve().parents[1]/"integration_probes/fixtures"
FIFTH_TIER=_LazySourceRegistry({
    entry.key:entry.fifth_replacement()
    for entry in metadata.SOURCE_BACKED})

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
# Publish all 24 supported legacy keys without opening complete official
# SimC fixture files at import.  For old 17-source execution (or legacy
# defaults), resolve the same v134 metadata and validate the same source
# bytes only when that particular spec is accessed.  New v139/v144 pure
# profile construction can therefore start independently of those fixtures.
for _key in GENERIC_PENDING:
    dict.__setitem__(ARCHETYPES,_key,None)
    dict.__setitem__(FIFTH_TIER,_key,None)

def _resolve_generic_source(key):
    if key not in GENERIC_PENDING:
        raise KeyError(key)
    info=generic.source_metadata("/".join(key))
    slot,ordinary=info["fifth"]
    need_tier=CLASS_TIER_ITEMS[key[0]]
    assert info["tier"]==need_tier and info["tier"][slot]>0, (
        "MID2_CLASS_TIER_DATA_DRIFT")
    dict.__setitem__(ARCHETYPES,key,
                     (info["fixture"],generic.producer(key),
                      info["form"],info["F"]))
    dict.__setitem__(FIFTH_TIER,key,
                     (slot,info["tier"][slot],ordinary))
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

def reconcile_current_season_five_tier(key,rows,groups,taken,ilevel,
                                       need,*,tier_map):
    """Deterministic 4-of-5 layout after user items, not gear-combo search.

    User-selected occupied slots are immutable. Native/catalyzed tier rows
    count once, crafted and ordinary specials do not. Only unoccupied tier
    slots can be internally promoted/demoted. Never invent an item ID.
    """
    import v143_specialization_contracts as contracts
    import v167_product_season_gear_adapter as product_gear
    import v169_source_first_representative_stage as source_stage
    need(set(tier_map)==set(TIER_FIVE),
         "CURRENT_SEASON_FIVE_CLASS_TIER_IDS_REQUIRED")
    need(all(slot in rows for slot in TIER_FIVE),
         "CURRENT_SEASON_FIVE_PHYSICAL_TIER_SLOTS_REQUIRED")
    restored=[]
    tier_count=sum(groups.get(slot)=="tier" for slot in TIER_FIVE)
    # The user may freely place ONE crafted/non-catalyst special on a tier
    # position; a second one inside these five makes four tiers impossible.
    if tier_count<4:
        for slot in TIER_FIVE:
            if groups.get(slot) is None and slot not in taken:
                options={k:v for k,v in rows[slot]["options"].items()
                         if k in ("gem_id","enchant","enchant_id")}
                rows[slot]={"slot":slot,"item_id":tier_map[slot],
                            "ilevel":ilevel,"options":options}
                groups[slot]="tier"
                restored.append(slot)
                tier_count+=1
                if tier_count==4:break
        need(tier_count==4,"FOUR_TIER_IMPOSSIBLE_USER_OCCUPIES_TOO_MANY_SLOTS")
    # An eligible catalyst special in the original fifth (chest) is a tier
    # contributor, so exactly ONE other unselected native tier must become
    # an ordinary *same-season, same-armor, correct-primary* representative.
    if tier_count>4:
        spec=contracts.lookup(*key)
        need(spec is not None,"CURRENT_SEASON_SPEC_UNKNOWN")
        product=product_gear.read()
        family=product_gear.ARMOR_SUBCLASS[spec["family"]]
        codes=source_stage.PRIMARY_STAT_CODES[spec["primary"]]
        tier=source_stage.load_tier()
        mask=tier["classes"][key[0]]["allowed_class_mask"]
        inventory={"head":(1,),"shoulders":(3,),"chest":(5,20),
                   "hands":(10,),"legs":(7,)}
        used={r["item_id"] for r in rows.values()}
        for slot in ("legs","hands","shoulders","head","chest"):
            if slot in taken or groups.get(slot)!="tier":continue
            candidates=sorted(x["item_id"] for x in product["items"]
                if x["category"]=="plain_representative_candidate"
                and x["class_id"]==4 and x["subclass_id"]==family
                and x["inventory_type"] in inventory[slot]
                and x["item_id"] not in used
                and type(x.get("stat_modifier_codes")) is list
                and any(code in codes for code in x["stat_modifier_codes"])
                and (x["allowed_class_mask"] is None or
                     (type(x["allowed_class_mask"]) is int and
                      (x["allowed_class_mask"]&mask)==mask)))
            if not candidates:continue
            options={k:v for k,v in rows[slot]["options"].items()
                     if k in ("gem_id","enchant","enchant_id")}
            rows[slot]={"slot":slot,"item_id":candidates[0],
                        "ilevel":ilevel,"options":options}
            del groups[slot]
            tier_count-=1
            if tier_count==4:break
        need(tier_count==4,
             "FOUR_TIER_UNAVAILABLE_ORDINARY_REPLACEMENT_FOR_FIFTH_CATALYST")
    need(sum(groups.get(slot)=="tier" for slot in TIER_FIVE)==4,
         "FOUR_TIER_CURRENT_SEASON_NOT_SATISFIED")
    need(all(rows[slot]["item_id"]==tier_map[slot]
             for slot in TIER_FIVE if groups.get(slot)=="tier"),
         "FOUR_TIER_CLASS_ITEM_ID_MISMATCH")
    return restored


def apply_user_equipment(key,rows,groups,user,ilevel,need,*,
                         tier_override=None,fifth_override=None,
                         flexible_current_tier=False):
    """Overlay selected items and reassign tier 4pc without item-combo search.

    Mutates only its private rows/groups objects. Selected catalyst specials
    are represented as ONE tier row plus optional typed fixed-L metadata.
    """
    need(type(flexible_current_tier) is bool,"FLEXIBLE_TIER_FLAG_BOOL")
    need(not flexible_current_tier or tier_override is not None,
         "CURRENT_SEASON_TIER_SOURCE_REQUIRED")
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
                    if ("redirected_base_stats" in opts or
                        not flexible_current_tier):
                        need(raw["item_id"]==tier_map[slot]
                             and "redirected_base_stats" in opts
                             and int(opts["redirected_base_stats"])!=raw["item_id"],
                             "CATALYST_CLASS_TIER_ID_AND_ORIGIN_REQUIRED")
                        slot_group="tier"
                    else:
                        need(raw["item_id"]!=tier_map[slot],
                             "NONCATALYST_SPECIAL_CANNOT_IMPERSONATE_TIER")
                        slot_group="special"
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
    if flexible_current_tier:
        restored=reconcile_current_season_five_tier(
            key,rows,groups,taken,ilevel,need,tier_map=tier_map)
    else:
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
