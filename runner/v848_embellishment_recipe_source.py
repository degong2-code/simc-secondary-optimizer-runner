#!/usr/bin/env python3
"""Generic source relation for embellishments (no effect emulation/admission).

Source identity is supplied by the already authenticated build/SimC owner.
Never copy a previous expansion's list, guess a slot from a name, or
interpret a missing CHMV observation as zero. Recipe output relations are
physical source facts, not assertions that a final item is legally craftable.
"""
import csv
import re
from collections import defaultdict
import v229_simc_only_source_seed as seed
import v281_consumable_simc_relation as spells

SCHEMA="v848_embellishment_recipe_output_source_v1"
RAW={
 "ModifiedCraftingReagentItem":("ID","ModifiedCraftingCategoryID","ItemBonusTreeID"),
 "ModifiedCraftingReagentSlot":("ID","Name_lang","Flags","PlayerConditionID","ReagentType"),
 "MCRSlotXMCRCategory":("ID","ModifiedCraftingCategoryID","ModifiedCraftingReagentSlotID"),
 "ModifiedCraftingSpellSlot":("ID","SpellID","ModifiedCraftingReagentSlotID","Slot","ReagentCount"),
}
MAX_ROWS=400_000
# Actual equipment craft relation: Effect=288, misc[0] -> CraftingData.ID.
# Effect=301 is the distinct enchant recipe path used by v583. Unknown
# effect kinds are pending, not inferred from coincident numeric IDs.
CRAFT_EFFECT=288
EQUIPMENT_CRAFT_TYPE=0
def need(ok,code):
    if not ok:raise ValueError(code)
def rows(path,columns):
    with path.open(encoding="utf-8-sig",newline="") as stream:
        r=csv.DictReader(stream)
        need(set(columns)<=set(r.fieldnames or []),"COLUMN_MISSING:"+path.name)
        for n,row in enumerate(r):
            need(n<MAX_ROWS,"ROW_LIMIT:"+path.name)
            yield row
def number(row,k):
    return int(row[k])

def read_simc(raw,build,expected_blob):
    need(type(expected_blob) is str and re.fullmatch(r"[a-f0-9]{40}",expected_blob) and
         seed.git_blob(raw)==expected_blob,"SIMC_ORIGINAL_GIT_BLOB_DRIFT")
    need(type(raw) is bytes and 0<len(raw)<=200_000,"SIMC_SOURCE_SIZE")
    s=raw.decode("utf8")
    need(s.splitlines()[0]=="// Embellishment data, wow build "+build,"SIMC_BUILD_DRIFT")
    header=re.search(r"std::array<embellishment_data_t,\s*(\d+)>",s)
    need(header is not None,"SIMC_COUNT_MISSING")
    match=re.compile(r'^\s*\{\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\},?\s*$')
    entries=[]
    for line in s.splitlines()[2:]:
        if not line.strip() or line.strip()=="} };":continue
        m=match.fullmatch(line)
        need(m is not None,"SIMC_ROW_UNPARSED")
        entries.append({"name_enUS":m[1],"bonus_id":int(m[2]),
            "item_effect_id":int(m[3]),"spell_id":int(m[4])})
    need(0<len(entries)<=1000 and len(entries)==int(header[1]) and
         len({(r["bonus_id"],r["item_effect_id"],r["spell_id"],r["name_enUS"]) for r in entries})==len(entries),
         "SIMC_COUNT_OR_DUPLICATE_DRIFT")
    return entries
def project(entries,paths,expansion):
    need(type(expansion) is int and expansion>0,"EXPANSION_REQUIRED")
    # Exact physical reagent -> tree -> type23 bonus/effect -> SimC row.
    by_pair=defaultdict(list)
    for e in entries:by_pair[(e["bonus_id"],e["item_effect_id"])].append(e)
    bonus_types=defaultdict(set);effects=defaultdict(set)
    for r in rows(paths["ItemBonus"],("ParentItemBonusListID","Type","Value_0")):
        b=number(r,"ParentItemBonusListID");kind=number(r,"Type")
        bonus_types[b].add(kind)
        if kind==23 and (b,number(r,"Value_0")) in by_pair:
            effects[b].add(number(r,"Value_0"))
    trees=defaultdict(list)
    for r in rows(paths["ItemBonusTreeNode"],("ID","ParentItemBonusTreeID",
                    "ChildItemBonusListID","ChildItemBonusTreeID","ChildItemBonusListGroupID")):
        b=number(r,"ChildItemBonusListID")
        if b in effects:
            for e in sorted(effects[b]):
                trees[number(r,"ParentItemBonusTreeID")].append((b,e,r))
    mcri={number(r,"ID"):r for r in rows(paths["ModifiedCraftingReagentItem"],
                                        RAW["ModifiedCraftingReagentItem"])}
    slots={number(r,"ID"):r for r in rows(paths["ModifiedCraftingReagentSlot"],
                                        RAW["ModifiedCraftingReagentSlot"])}
    categories=defaultdict(set)
    for r in rows(paths["MCRSlotXMCRCategory"],RAW["MCRSlotXMCRCategory"]):
        sid=number(r,"ModifiedCraftingReagentSlotID")
        if slots.get(sid,{}).get("Name_lang")=="Add Embellishment":
            categories[number(r,"ModifiedCraftingCategoryID")].add(sid)
    spells=defaultdict(set)
    for r in rows(paths["ModifiedCraftingSpellSlot"],RAW["ModifiedCraftingSpellSlot"]):
        spells[number(r,"ModifiedCraftingReagentSlotID")].add(number(r,"SpellID"))
    found=defaultdict(list)
    for r in rows(paths["ItemSparse"],("ID","Display_lang","ExpansionID","ModifiedCraftingReagentItemID")):
        if number(r,"ExpansionID")!=expansion:continue
        mid=number(r,"ModifiedCraftingReagentItemID")
        reagent=mcri.get(mid)
        if reagent is None:continue
        category=number(reagent,"ModifiedCraftingCategoryID")
        if not categories[category]:continue
        for b,e,node in trees.get(number(reagent,"ItemBonusTreeID"),()):
            for source in by_pair[(b,e)]:
                if source["name_enUS"]!=r["Display_lang"]:continue
                found[(b,e)].append({
                    "item_id":number(r,"ID"),"modified_reagent_id":mid,
                    "category_id":category,"tree_id":number(reagent,"ItemBonusTreeID"),
                    "tree_node_id":number(node,"ID"),
                    "tree_node_context":{k:v for k,v in node.items() if k!="ID"},
                    "slot_ids":sorted(categories[category])})
    ids={r["item_id"] for group in found.values() for r in group}
    quality={number(r,"ID"):number(r,"CraftingQualityID") for r in rows(
        paths["Item"],("ID","CraftingQualityID")) if number(r,"ID") in ids}
    result=[]
    for pair,physical in sorted(found.items()):
        for r in physical:r["crafting_quality_id"]=quality.get(r["item_id"])
        sids=sorted({s for r in physical for s in r["slot_ids"]})
        result.append({"simc_rows":by_pair[pair],"physical_rows":physical,
            "bonus_types":sorted(bonus_types[pair[0]]),
            "recipe_slot_sources":[{"slot":slots[s],
                "recipe_spell_count":len(spells[s]),
                "recipe_spell_ids":sorted(spells[s])} for s in sids],
            "recipe_output_item_scope_verified":False,
            "quality_dominance_verified":False,"ui_selectable":False})
    return result

def recipe_outputs(matches,paths,*,game_build,simc_revision,expansion_id):
    """One shared SpellEffect scan for all referenced recipes.

    Input paths belong to the original same-build source stages, validated
    by the caller. Multiple CraftingData outputs, nonzero difficulty,
    missing item/sparse rows and unknown types remain explicit. Only
    weapon/armor outputs in the supplied expansion are projected.
    """
    need(type(game_build) is str and seed.BUILD.fullmatch(game_build) and
         type(simc_revision) is str and seed.REV.fullmatch(simc_revision) and
         type(expansion_id) is int and expansion_id>0,"SOURCE_IDENTITY_REQUIRED")
    wanted={sid for m in matches for slot in m["recipe_slot_sources"]
            for sid in slot["recipe_spell_ids"]}
    need(len(wanted)<=20000 and all(type(i) is int and i>0 for i in wanted),
         "RECIPE_SPELL_SCOPE_INVALID")
    effects=spells.scan_spell_effects(paths["SpellEffect"],wanted) if wanted else []
    links=defaultdict(list)
    observed=defaultdict(set)
    nondefault_craft=set()
    for row in effects:
        sid=row["spell_id"]
        observed[sid].add(row["effect"])
        if row["effect"]==CRAFT_EFFECT:
            if row["difficulty_id"]==0:links[sid].append(row)
            else:nondefault_craft.add(sid)
    craft_ids={r["enchant_id"] for group in links.values() for r in group
               if r["enchant_id"]>0}
    craft={}
    for r in rows(paths["CraftingData"],("ID","Type","CraftedItemID")):
        cid=number(r,"ID")
        if cid in craft_ids:
            need(cid not in craft,"DUPLICATE_CRAFTING_DATA_ID")
            craft[cid]={"crafting_data_id":cid,"crafting_type":number(r,"Type"),
                        "item_id":number(r,"CraftedItemID")}
    item_ids={r["item_id"] for r in craft.values() if r["item_id"]>0}
    item={}
    for r in rows(paths["Item"],("ID","ClassID","SubclassID","InventoryType")):
        iid=number(r,"ID")
        if iid in item_ids:
            need(iid not in item,"DUPLICATE_ITEM_ID")
            item[iid]={"item_class":number(r,"ClassID"),"item_subclass":number(r,"SubclassID"),
                       "inventory_type":number(r,"InventoryType")}
    sparse={}
    for r in rows(paths["ItemSparse"],("ID","ExpansionID","InventoryType","Display_lang")):
        iid=number(r,"ID")
        if iid in item_ids:
            need(iid not in sparse,"DUPLICATE_SPARSE_ITEM_ID")
            sparse[iid]={"expansion_id":number(r,"ExpansionID"),
                         "inventory_type":number(r,"InventoryType"),
                         "name_enUS":r["Display_lang"]}
    exact={};pending={}
    for sid in sorted(wanted):
        raw=links.get(sid,[])
        if len(raw)!=1 or sid in nondefault_craft:
            pending[sid]="CRAFT_EFFECT_MISSING_OR_AMBIGUOUS"
            continue
        row=raw[0]; cr=craft.get(row["enchant_id"])
        if cr is None or cr["item_id"]<=0:
            pending[sid]="CRAFTING_DATA_OUTPUT_MISSING"
            continue
        if cr["crafting_type"]!=EQUIPMENT_CRAFT_TYPE:
            pending[sid]="CRAFTING_DATA_TYPE_NOT_EQUIPMENT_OUTPUT"
            continue
        iid=cr["item_id"]; meta=item.get(iid); sp=sparse.get(iid)
        if not meta or not sp:
            pending[sid]="OUTPUT_ITEM_METADATA_MISSING"
            continue
        if (sp["expansion_id"]!=expansion_id or
            meta["item_class"] not in (2,4) or meta["inventory_type"]<=0 or
            meta["inventory_type"]!=sp["inventory_type"]):
            pending[sid]="OUTPUT_ITEM_NOT_MATCHED_EXPANSION_EQUIPMENT"
            continue
        exact[sid]={**cr,**meta,"recipe_spell_id":sid,
                    "effect_code":row["effect"],"effect_index":row["effect_index"],"expansion_id":sp["expansion_id"],
                    "name_enUS":sp["name_enUS"]}
    projected=[]
    for match in matches:
        slots=[]
        for slot in match["recipe_slot_sources"]:
            sids=slot["recipe_spell_ids"]
            outputs=[exact[s] for s in sids if s in exact]
            slots.append({"slot":slot["slot"],"recipe_spell_count":len(sids),
                          "exact_recipe_outputs":outputs,
                          "pending_recipe_spells":[{"spell_id":s,"reason":pending[s],
                              "observed_effect_codes":sorted(observed.get(s,()))}
                              for s in sids if s in pending],
                          "slot_condition_resolved":False})
        projected.append({"simc_rows":match["simc_rows"],
            "physical_rows":match["physical_rows"],"bonus_types":match["bonus_types"],
            "recipe_slot_sources":slots,
            "recipe_output_item_scope_verified":False,
            "quality_dominance_verified":False,"ui_selectable":False})
    return {"schema":SCHEMA,"status":"RECIPE_OUTPUT_SOURCE_PROJECTED",
            "game_build":game_build,"simc_revision":simc_revision,"expansion_id":expansion_id,
            "recipe_spell_count":len(wanted),"exact_recipe_spell_count":len(exact),
            "pending_recipe_spell_count":len(pending),
            "exact_output_item_count":len({x["item_id"] for x in exact.values()}),
            "matches":projected,"native_calls":0,"ui_promotion":False}
