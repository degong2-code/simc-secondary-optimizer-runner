#!/usr/bin/env python3
"""Generic source relation for embellishments (no effect emulation/admission).

Source identity is supplied by the already authenticated build/SimC owner.
Never copy a previous expansion's list, guess a slot from a name, or
interpret a missing CHMV observation as zero. Recipe output relations are
physical source facts, not assertions that a final item is legally craftable.
"""
import csv
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen
import v217_stage_execution_engine as stages
import v275_pinned_simc_compiler_inputs as pinned
from collections import defaultdict
from decimal import Decimal, InvalidOperation
import v229_simc_only_source_seed as seed
import v281_consumable_simc_relation as spells

SCHEMA="v848_embellishment_recipe_output_source_v1"
RAW={
 "ModifiedCraftingReagentItem":("ID","ModifiedCraftingCategoryID","ItemBonusTreeID"),
 "ModifiedCraftingReagentSlot":("ID","Name_lang","Flags","PlayerConditionID","ReagentType"),
 "MCRSlotXMCRCategory":("ID","ModifiedCraftingCategoryID","ModifiedCraftingReagentSlotID"),
 "ModifiedCraftingSpellSlot":("ID","SpellID","ModifiedCraftingReagentSlotID","Slot","ReagentCount"),
 "CraftingQuality":("ID","QualityTier","CraftingQualityAtlasSetID"),
 "CraftingReagentQuality":("ID","ItemID","ModifiedCraftingCategoryID","OrderIndex",
                           "ReagentEffectPct","MaxDifficultyAdjustment"),
}
MAX_ROWS=400_000
MAX_RAW=8_000_000
DEFINITION="embellishment_data.inc"
DEFINITION_PATH="engine/dbc/generated/"+DEFINITION
STAGED=frozenset(("EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED"))
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
    wanted_bonus_ids={b for b,e in by_pair}
    bonus_types=defaultdict(set);effects=defaultdict(set)
    all_effect_ids=defaultdict(set)
    for r in rows(paths["ItemBonus"],("ParentItemBonusListID","Type","Value_0")):
        b=number(r,"ParentItemBonusListID");kind=number(r,"Type")
        if b not in wanted_bonus_ids:continue
        bonus_types[b].add(kind)
        if kind==23:
            effect_id=number(r,"Value_0")
            all_effect_ids[b].add(effect_id)
            if (b,effect_id) in by_pair:effects[b].add(effect_id)
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
    recipe_rows=defaultdict(list)
    for r in rows(paths["ModifiedCraftingSpellSlot"],RAW["ModifiedCraftingSpellSlot"]):
        sid=number(r,"ModifiedCraftingReagentSlotID")
        spells[sid].add(number(r,"SpellID"))
        recipe_rows[sid].append(r)
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
                    "category_id":category,"reagent_source_row":reagent,
                    "tree_id":number(reagent,"ItemBonusTreeID"),
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
            "bonus_effect_ids":sorted(all_effect_ids[pair[0]]),
            "recipe_slot_sources":[{"slot":slots[s],
                "recipe_spell_count":len(spells[s]),
                "recipe_spell_ids":sorted(spells[s]),
                "recipe_source_rows":sorted(recipe_rows[s],key=lambda r:number(r,"ID"))}
                for s in sids],
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
                          "recipe_source_rows":slot.get("recipe_source_rows",[]),
                          "slot_condition_resolved":False})
        projected.append({"simc_rows":match["simc_rows"],
            "physical_rows":match["physical_rows"],"bonus_types":match["bonus_types"],
            "bonus_effect_ids":match.get("bonus_effect_ids",[]),
            "recipe_slot_sources":slots,
            "recipe_output_item_scope_verified":False,
            "quality_dominance_verified":False,"ui_selectable":False})
    return {"schema":SCHEMA,"status":"RECIPE_OUTPUT_SOURCE_PROJECTED",
            "game_build":game_build,"simc_revision":simc_revision,"expansion_id":expansion_id,
            "recipe_spell_count":len(wanted),"exact_recipe_spell_count":len(exact),
            "pending_recipe_spell_count":len(pending),
            "exact_output_item_count":len({x["item_id"] for x in exact.values()}),
            "matches":projected,"native_calls":0,"ui_promotion":False}


def simc_token(name):
    """Mirror the ASCII portion of pinned SimC util::tokenize for inputs.
    The item serializer accepts only safe alphanumeric/underscore tokens;
    unsupported characters and ambiguous names remain unregistered.
    """
    return "".join(c.lower() if c.isascii() and c.isalpha() else
                   "_" if c==" " else c
                   for c in name.lstrip("_+")
                   if c.isascii() and (c.isalnum() or c in " _+.%"))


def material_options(result,paths):
    """Preserve physical-family and exact recipe evidence before publication.

    Never merge different modified-reagent/category/tree identities just
    because they use the same effect. Recipe applicability is item-specific,
    not a union of every slot permitted by the effect. Rank IDs are foreign
    keys, not rank numbers. Compare only source-backed quality families.
    """
    wanted={p["item_id"] for m in result["matches"] for p in m["physical_rows"]}
    quality_ids={p["crafting_quality_id"] for m in result["matches"]
                 for p in m["physical_rows"] if p.get("crafting_quality_id")}
    quality={}
    for row in rows(paths["CraftingQuality"],RAW["CraftingQuality"]):
        key=number(row,"ID")
        if key in quality_ids:
            need(key not in quality,"DUPLICATE_CRAFTING_QUALITY_ID")
            quality[key]=row
    reagent_quality=defaultdict(list)
    for row in rows(paths["CraftingReagentQuality"],RAW["CraftingReagentQuality"]):
        iid=number(row,"ItemID")
        if iid in wanted:reagent_quality[iid].append(row)
    options=[]
    for match in result["matches"]:
        family=defaultdict(list)
        slots={number(s["slot"],"ID"):s for s in match["recipe_slot_sources"]}
        for physical in match["physical_rows"]:
            key=(physical["modified_reagent_id"],physical["category_id"],
                 physical["tree_id"],physical["tree_node_id"],
                 tuple(physical["slot_ids"]))
            family[key].append(physical)
        for key,materials in sorted(family.items()):
            mid,category,tree,node,slot_ids=key
            # Same ItemID appearing twice is not a unique physical witness.
            seen=set(); members=[]
            for p in sorted(materials,key=lambda x:x["item_id"]):
                iid=p["item_id"]
                need(iid not in seen,"DUPLICATE_EMBELLISHMENT_FAMILY_ITEM")
                seen.add(iid)
                rank=quality.get(p["crafting_quality_id"])
                qr=[r for r in reagent_quality[iid]
                    if number(r,"ModifiedCraftingCategoryID")==category]
                members.append({"physical":p,"quality_source_row":rank,
                                "reagent_quality_source_rows":qr})
            links=[]
            for sid in slot_ids:
                slot=slots[sid]
                by_recipe=defaultdict(list)
                for r in slot.get("recipe_source_rows",[]):
                    by_recipe[number(r,"SpellID")].append(r)
                for output in slot["exact_recipe_outputs"]:
                    recipe=output["recipe_spell_id"]
                    # Retain original slot conditions and row, not merely
                    # the inventory type or recipe spell ID.
                    if len(by_recipe[recipe])==1:
                        links.append({"output":output,"slot_source":slot["slot"],
                                      "recipe_source_row":by_recipe[recipe][0]})
            preferred=None
            status="QUALITY_SOURCE_PENDING"
            if len(members)==1 and members[0]["physical"]["crafting_quality_id"]==0:
                status="UNRANKED_SINGLE_PHYSICAL_SOURCE"
                preferred=members[0]["physical"]["item_id"]
            elif all(m["quality_source_row"] is not None and
                     len(m["reagent_quality_source_rows"])==1 for m in members):
                ranks=[number(m["quality_source_row"],"QualityTier") for m in members]
                values=[m["reagent_quality_source_rows"][0] for m in members]
                # CraftingQualityAtlasSetID references UI textures only.
                # MaxDifficultyAdjustment affects the crafting process, not
                # an already completed item at the requested final ilvl.
                # Retain both in raw evidence but compare final-item effect
                # and application fields. Unknown fields must agree. Without
                # effect component direction proof, even a greater effect
                # percentage is not assumed to be non-inferior.
                ignored={"ID","ItemID","OrderIndex","ReagentEffectPct",
                         "MaxDifficultyAdjustment"}
                rest=[{k:v for k,v in r.items() if k not in ignored} for r in values]
                try:
                    pct=[Decimal(r["ReagentEffectPct"]) for r in values]
                    winner=max(range(len(ranks)),key=ranks.__getitem__)
                    ordered=sorted(range(len(ranks)),key=ranks.__getitem__)
                    order_indices=[number(values[i],"OrderIndex") for i in ordered]
                    if (len(set(ranks))==len(ranks) and min(ranks)>0
                        and order_indices==sorted(set(order_indices))
                        and all(r==rest[0] for r in rest)
                        and all(v.is_finite() and v>=0 for v in pct)
                        and all(v==pct[winner] for v in pct)):
                        preferred=members[winner]["physical"]["item_id"]
                        status="HIGHEST_SOURCE_QUALITY_SAME_EFFECT_SCOPE"
                    else:status="QUALITY_EFFECT_OR_CONDITION_COMPARISON_PENDING"
                except (InvalidOperation,ValueError):
                    status="QUALITY_EFFECT_OR_CONDITION_COMPARISON_PENDING"
            options.append({"simc_rows":match["simc_rows"],
                "modified_reagent_id":mid,"category_id":category,
                "tree_id":tree,"tree_node_id":node,
                "physical_family":members,"recipe_links":links,
                "recipe_output_item_ids":sorted({r["output"]["item_id"] for r in links}),
                "quality_status":status,"preferred_physical_item_id":preferred,
                "bonus_types":match["bonus_types"],
                "bonus_effect_ids":match.get("bonus_effect_ids",[]),
                "quality_dominance_verified":status=="HIGHEST_SOURCE_QUALITY_SAME_EFFECT_SCOPE",
                "exact_application_verified":False,
                "static_CHMV_owner":"EXISTING_SELECTED_PHYSICAL_VARIANT_NOT_MEASURED_HERE",
                "ui_selectable":False})
    return options


def project_installed_options(source,catalog,*,source_receipt_sha256,source_candidate_sha256):
    """Exact recipe-output intersection with the existing same-season v213.
    No recipe lists go to the UI, no static rating assumed, no effect gate.
    Conditional/unknown source shapes remain optional pending.
    """
    need(source.get("schema")==SCHEMA and
         source.get("status")=="RECIPE_OUTPUT_SOURCE_PROJECTED" and
         source.get("game_build")==catalog["game_build"] and
         source.get("simc_revision")==catalog["simc_revision"],
         "EMBELLISHMENT_INSTALL_SOURCE_IDENTITY_DRIFT")
    gear={row["item_id"]:row for group in catalog["catalog"]["gear"]["slot_groups"].values()
          for row in group if row.get("category")=="selectable_stat_craft"}
    counts=source.get("simc_token_counts",{})
    options={}; pending={}
    families=source.get("material_options",[])
    family_token_counts=defaultdict(int)
    for family in families:
        for token in {simc_token(row["name_enUS"]) for row in family.get("simc_rows",[])}:
            family_token_counts[token]+=1
    for family in families:
        preferred=family.get("preferred_physical_item_id")
        simc=family.get("simc_rows",[])
        if len(simc)!=1 or not preferred:
            continue
        effect=simc[0];token=simc_token(effect["name_enUS"])
        if not re.fullmatch(r"[a-z0-9_]{1,140}",token) or counts.get(token)!=1:
            pending[token]="SIMC_TOKEN_NOT_UNIQUE_OR_SERIALIZABLE"
            continue
        if family_token_counts[token]!=1:
            pending[token]="DISTINCT_MATERIAL_FAMILY_TOKEN_COLLISION"
            continue
        if (family.get("quality_status") not in
                ("HIGHEST_SOURCE_QUALITY_SAME_EFFECT_SCOPE","UNRANKED_SINGLE_PHYSICAL_SOURCE")
            or family.get("bonus_types")!=[23]
            or family.get("bonus_effect_ids")!=[effect["item_effect_id"]]):
            pending[token]="MATERIAL_QUALITY_OR_EFFECT_SCOPE_PENDING"
            continue
        physical=[m["physical"] for m in family["physical_family"]
                  if m["physical"]["item_id"]==preferred]
        if len(physical)!=1:continue
        material=physical[0]
        reagent=material.get("reagent_source_row",{})
        node=material.get("tree_node_context",{})
        # Only direct unconditional tree nodes; no implicit context branches.
        if (not reagent or not node or
            int(reagent.get("Flags",-1))!=0 or int(reagent.get("ItemContextOffset",-1))!=0 or
            any(int(v)!=0 for k,v in node.items()
                if k not in ("ParentItemBonusTreeID","ChildItemBonusListID")) or
            int(node.get("ChildItemBonusListID",0))!=effect["bonus_id"]):
            pending[token]="CONDITIONAL_REAGENT_OR_BONUS_TREE_PENDING"
            continue
        ids=set()
        for link in family["recipe_links"]:
            out=link["output"];slot=link["slot_source"];recipe=link["recipe_source_row"]
            row=gear.get(out["item_id"])
            if row is None:continue
            if (out.get("item_class")!=row.get("class_id") or
                out.get("item_subclass")!=row.get("subclass_id") or
                out.get("inventory_type")!=row.get("inventory_type") or
                out.get("expansion_id")!=source["expansion_id"]):
                continue
            # Use explicit Add Embellishment relation, not armor-slot guesses.
            # Retain only the observed normal optional-slot shape. Unknown
            # flags, explicit player conditions and unknown nonzero fields
            # are not silently accepted. ReagentSource is acquisition metadata.
            if (slot.get("Name_lang")!="Add Embellishment" or
                int(slot.get("PlayerConditionID",-1))!=0 or
                int(slot.get("Flags",-1)) not in (0,2) or
                int(slot.get("ReagentType",-1))!=0 or
                int(slot.get("ReagentSource",0)) not in (0,1) or
                any(int(v)!=0 for k,v in slot.items() if k.startswith("Field_")) or
                int(slot["ID"]) not in material["slot_ids"] or
                int(recipe.get("ModifiedCraftingReagentSlotID",0))!=int(slot["ID"]) or
                int(recipe.get("SpellID",0))!=out["recipe_spell_id"] or
                int(recipe.get("ReagentCount",0))!=1 or
                any(int(v)!=0 for k,v in recipe.items() if k.startswith("Field_"))):
                continue
            ids.add(out["item_id"])
        if not ids:
            pending[token]="NO_EXACT_UNCONDITIONAL_SELECTABLE_CRAFT"
            continue
        options[token]={"name":effect["name_enUS"],
            "effect":reagent.get("Description_lang",""),
            "material_item_id":preferred,"bonus_id":effect["bonus_id"],
            "item_effect_id":effect["item_effect_id"],"item_ids":sorted(ids)}
    return {"game_build":catalog["game_build"],"simc_revision":catalog["simc_revision"],
            "source_catalog_manifest_sha256":catalog["manifest_sha256"],
            "source_receipt_sha256":source_receipt_sha256,
            "source_candidate_sha256":source_candidate_sha256,
            "options":options,"pending":pending}


def verify_installed_options(registry,*,game_build,simc_revision,catalog_sha):
    need(type(registry) is dict and registry.get("game_build")==game_build and
         registry.get("simc_revision")==simc_revision and
         registry.get("source_catalog_manifest_sha256")==catalog_sha and
         all(type(registry.get(k)) is str and re.fullmatch(r"[a-f0-9]{64}",registry[k])
             for k in ("source_receipt_sha256","source_candidate_sha256")) and
         type(registry.get("options")) is dict and type(registry.get("pending")) is dict,
         "EMBELLISHMENT_INSTALLED_SCOPE_INVALID")
    for token,row in registry["options"].items():
        need(type(row) is dict and re.fullmatch(r"[a-z0-9_]{1,140}",token) and
             type(row.get("name")) is str and simc_token(row["name"])==token and
             type(row.get("effect")) is str and
             all(type(row.get(k)) is int and row[k]>0 for k in
                 ("material_item_id","bonus_id","item_effect_id")) and
             type(row.get("item_ids")) is list and bool(row["item_ids"]) and
             all(type(i) is int and i>0 for i in row["item_ids"]) and
             row["item_ids"]==sorted(set(row["item_ids"])) and token not in registry["pending"],
             "EMBELLISHMENT_INSTALLED_OPTION_INVALID:"+token)
    return True


# Same v213 source scope applies across installed targets and G/J/F/O variants.
# The optional registry is a sealed derivative, not a second v212 install.
BACKFILL_VERSION="embellishment-installed-source-attachment-v1"

def _backfill_identity(installed):
    return {k:installed[k] for k in ("game_build","simc_revision",
        "source_catalog_manifest_sha256","source_catalog_artifact_sha256")}

def _backfill_location(installed):
    identity=_backfill_identity(installed)
    sid="embellishment-install-"+stages.digest(
        stages.canonical(identity).encode("utf8"))[:24]
    return identity,sid,{"registry":"source/"+sid+".json"}

def read_installed_attachment(root,installed):
    """Read a small exact-source sealed registry; never scan raw DB2 on GET."""
    identity,sid,outputs=_backfill_location(installed)
    paths,receipt_path=stages._safe_paths(root,sid,outputs)
    path=paths["registry"][1]
    if not path.exists() and not receipt_path.exists():return None
    need(path.is_file() and 0<path.stat().st_size<=1_000_000,
         "EMBELLISHMENT_ATTACHMENT_MISSING_OR_SIZE")
    raw=path.read_bytes()
    registry=json.loads(raw)
    verify_installed_options(registry,game_build=identity["game_build"],
        simc_revision=identity["simc_revision"],
        catalog_sha=identity["source_catalog_manifest_sha256"])
    inputs={**identity,"source_receipt_sha256":registry["source_receipt_sha256"],
            "source_candidate_sha256":registry["source_candidate_sha256"]}
    receipt=stages._read_receipt(receipt_path)
    need(receipt.get("status")=="COMPLETE" and
         receipt.get("outputs",{}).get("registry")=={
             "path":outputs["registry"],"size":len(raw),"sha256":stages.digest(raw)},
         "EMBELLISHMENT_ATTACHMENT_OUTPUT_DRIFT")
    stages._check_identity(receipt,sid,BACKFILL_VERSION,
        stages._input_sha(sid,BACKFILL_VERSION,inputs),paths)
    return registry

def effective_installed_options(installed_path,installed):
    """One consumer for menu and selected-profile validation.
    None is the unchanged pre-v851 compatibility path only.
    A corrupt attachment or explicit source pending must not restore old tokens.
    """
    if "installed_embellishments" in installed:
        return installed["installed_embellishments"]["options"]
    try:
        root=Path(installed_path).parent.parent
        registry=read_installed_attachment(root,installed)
        if registry is not None:return registry["options"]
    except (OSError,ValueError,TypeError,KeyError,AttributeError,
            stages.StageExecutionBlocked):
        return {}
    return {} if installed.get("installed_embellishments_pending") is True else None

def attach_installed_options(root,installed,catalog,source,*,source_receipt_sha256,
                             source_candidate_sha256):
    identity,sid,outputs=_backfill_location(installed)
    need(catalog["manifest_sha256"]==identity["source_catalog_manifest_sha256"],
         "EMBELLISHMENT_ATTACHMENT_CATALOG_DRIFT")
    existing=read_installed_attachment(root,installed)
    if existing is not None:return existing
    registry=project_installed_options(source,catalog,
        source_receipt_sha256=source_receipt_sha256,
        source_candidate_sha256=source_candidate_sha256)
    verify_installed_options(registry,game_build=identity["game_build"],
        simc_revision=identity["simc_revision"],
        catalog_sha=identity["source_catalog_manifest_sha256"])
    inputs={**identity,"source_receipt_sha256":source_receipt_sha256,
            "source_candidate_sha256":source_candidate_sha256}
    encoded=(stages.canonical(registry)+"\n").encode("utf8")
    need(len(encoded)<=1_000_000,"EMBELLISHMENT_ATTACHMENT_SIZE")
    stages.execute_stage(root=root,stage_id=sid,stage_version=BACKFILL_VERSION,
        inputs=inputs,outputs=outputs,
        execute=lambda:stages._atomic_write(Path(root)/outputs["registry"],encoded),
        validate=lambda files:files["registry"].read_bytes()==encoded)
    return read_installed_attachment(root,installed)

def read_sealed_projection(root,catalog):
    """Reuse an actual v848/v217 source projection; not a raw source rescan.
    Different source generations may coexist only if their material/token
    relations agree. Never pick an ambiguous newest generation.
    """
    root=Path(root)
    receipts=root/".stage_receipts"
    if not receipts.is_dir() or receipts.is_symlink():return None
    candidates=sorted(receipts.glob("embellishment-source-*.json"))
    if len(candidates)>64:return None
    matched=None;signature=None
    for path in candidates:
        try:
            sid=path.stem
            if not re.fullmatch(r"embellishment-source-[a-f0-9]{24}",sid):continue
            outputs={"candidate":"source/"+sid+".json"}
            files,receipt_path=stages._safe_paths(root,sid,outputs)
            receipt=stages._read_receipt(receipt_path)
            p=files["candidate"][1]
            if not p.is_file() or not 0<p.stat().st_size<=25_000_000:continue
            raw=p.read_bytes();sha=stages.digest(raw);source=json.loads(raw)
            if (source.get("schema")!=SCHEMA or
                source.get("status")!="RECIPE_OUTPUT_SOURCE_PROJECTED" or
                source.get("game_build")!=catalog["game_build"] or
                source.get("simc_revision")!=catalog["simc_revision"] or
                source.get("expansion_id")!=catalog["expansion_id"] or
                type(source.get("simc_token_counts")) is not dict or
                source.get("native_calls")!=0 or source.get("ui_promotion") is not False):
                continue
            identity=source["source_identity"]
            if sid!="embellishment-source-"+stages.digest(
                    stages.canonical(identity).encode("utf8"))[:24]:continue
            if any(identity.get(k)!=source[k] for k in
                   ("game_build","simc_revision","expansion_id")):continue
            if (receipt.get("status")!="COMPLETE" or
                receipt.get("outputs",{}).get("candidate")!={
                    "path":outputs["candidate"],"size":len(raw),"sha256":sha}):
                continue
            stages._check_identity(receipt,sid,"embellishment-recipe-source-v1",
                stages._input_sha(sid,"embellishment-recipe-source-v1",identity),files)
            current=stages.digest(stages.canonical({
                "material_options":source["material_options"],
                "simc_token_counts":source["simc_token_counts"]}).encode("utf8"))
            if signature is not None and current!=signature:
                raise ValueError("EMBELLISHMENT_MULTIPLE_SEALED_PROJECTIONS")
            signature=current;matched=(source,receipt["receipt_sha256"],sha)
        except (OSError,TypeError,KeyError,AttributeError,stages.StageExecutionBlocked):
            continue
    return matched


def pending(reason,calls=0):
    return {"schema":SCHEMA,"status":"EMBELLISHMENT_SOURCE_PENDING",
            "reason":reason,"candidate_path":None,
            "network_calls_by_stage":calls,"native_calls":0,
            "automatic_ui_promotion":False}

def valid_raw(raw,table):
    if not isinstance(raw,bytes) or not 0<len(raw)<=MAX_RAW:return False
    try:
        line=raw.split(b"\n",1)[0].decode("utf-8-sig")
        return set(RAW[table])<=set(next(csv.reader([line])))
    except (ValueError,StopIteration,csv.Error):return False

def upstream(root,summary,keys):
    """Consume the current invocation's already verified v217 owners.

    v216 has authenticated the large raw files, so do not rehash them again.
    Require the exact COMPLETE receipt and output contract; this helper is
    not an external arbitrary-path or untrusted install admission endpoint.
    """
    need(type(summary) is dict and summary.get("status") in STAGED,
         "EMBELLISHMENT_UPSTREAM_PENDING")
    paths,receipt_path=stages._safe_paths(root,summary["stage_id"],
                                         summary["output_paths"])
    receipt=stages._read_receipt(receipt_path)
    need(receipt.get("status")=="COMPLETE" and
         receipt.get("stage_id")==summary["stage_id"] and
         receipt.get("receipt_sha256")==summary["receipt_sha256"] and
         receipt.get("output_paths")==summary["output_paths"],
         "EMBELLISHMENT_UPSTREAM_RECEIPT_DRIFT")
    out={}
    for key in keys:
        rel,p=paths[key]
        record=receipt["outputs"][key]
        need(p.is_file() and record["path"]==rel and
             record["size"]==p.stat().st_size,"EMBELLISHMENT_UPSTREAM_OUTPUT_DRIFT")
        out[key]=p
    return out,receipt["receipt_sha256"]

def pinned_definition(root,build,revision,*,transport=None,calls):
    """One optional small generated table using v275's Git-tree owner."""
    need(seed.BUILD.fullmatch(build) and seed.REV.fullmatch(revision),
         "EMBELLISHMENT_PINNED_IDENTITY")
    rel="source/embellishment_simc_"+revision
    outputs={"definition":rel+"/"+DEFINITION,"meta":rel+"/source.json"}
    inputs={"game_build":build,"simc_revision":revision,"path":DEFINITION_PATH}
    def fetch(req,timeout):
        calls[0]+=1
        return (urlopen if transport is None else transport)(req,timeout=timeout)
    def execute():
        record=pinned.pinned_git_blobs(revision=revision,
                     paths={DEFINITION:DEFINITION_PATH},transport=fetch)[DEFINITION]
        need(0<record["size"]<=200_000,"EMBELLISHMENT_DEFINITION_SIZE")
        req=Request(seed.RAW_BASE+revision+"/"+DEFINITION_PATH,
                    headers={"User-Agent":"SIMC-Secondary-Embellishment/1.0"})
        with fetch(req,90) as response:
            need(response.status==200,"EMBELLISHMENT_DEFINITION_HTTP")
            raw=response.read(record["size"]+1)
        need(len(raw)==record["size"],"EMBELLISHMENT_DEFINITION_SIZE_DRIFT")
        read_simc(raw,build,record["sha"])
        stages._atomic_write(root/outputs["definition"],raw)
        stages._atomic_write(root/outputs["meta"],(stages.canonical({
            **inputs,"git_blob_sha1":record["sha"],"sha256":seed.digest(raw),
            "size":len(raw)})+"\n").encode("utf8"))
    def validate(files):
        meta=json.loads(files["meta"].read_text("utf8"))
        raw=files["definition"].read_bytes()
        return (all(meta.get(k)==v for k,v in inputs.items()) and
                meta.get("size")==len(raw) and meta.get("sha256")==seed.digest(raw)
                and bool(read_simc(raw,build,meta["git_blob_sha1"])))
    receipt=stages.execute_stage(root=root,stage_id="embellishment-simc-"+revision,
        stage_version="pinned-embellishment-source-v1",inputs=inputs,outputs=outputs,
        execute=execute,validate=validate)
    meta=json.loads((root/outputs["meta"]).read_text("utf8"))
    raw=(root/outputs["definition"]).read_bytes()
    return read_simc(raw,build,meta["git_blob_sha1"]),receipt["receipt_sha256"]

def collect(*,stage_root,build,expansion_id,wago_stage,spell_stage,simc_stage,
            crafting_table,bonus_table,transport=None,calls=None):
    """Normal Build optional projection; no separate season DB or Native."""
    root=Path(stage_root).resolve()
    calls=[0] if calls is None else calls
    if (type(expansion_id) is not int or expansion_id<=0 or
        any(type(s) is not dict or s.get("status") not in STAGED
            for s in (wago_stage,spell_stage,simc_stage))):
        return pending("EMBELLISHMENT_EXISTING_SOURCE_OR_EXPANSION_PENDING",calls[0])
    try:
        paths,wstamp=upstream(root,wago_stage,("Item","ItemSparse","CraftingData","receipt"))
        need(json.loads(paths.pop("receipt").read_text("utf8"))["build"]==build,
             "EMBELLISHMENT_WAGO_BUILD_DRIFT")
        spell,sstamp=upstream(root,spell_stage,("spell_effect","candidate"))
        sc=json.loads(spell["candidate"].read_text("utf8"))
        need(sc.get("simc_relation_source",{}).get("game_build")==build,
             "EMBELLISHMENT_SPELL_BUILD_DRIFT")
        paths["SpellEffect"]=spell["spell_effect"]
        simc,simstamp=upstream(root,simc_stage,(seed.RECEIPT,))
        original=json.loads(simc[seed.RECEIPT].read_text("utf8"))
        revision=original["simc_revision"]
        need(original.get("schema")==seed.SCHEMA and
             original.get("simc_generated_build")==build and
             original.get("provenance_tree_blob_authenticated") is True and
             seed.REV.fullmatch(revision),"EMBELLISHMENT_SIMC_BUILD_DRIFT")
        entries,definition_stamp=pinned_definition(root,build,revision,
                                                   transport=transport,calls=calls)
        raw_stamps={}
        for name in ("ItemBonus","ItemBonusTreeNode"):
            paths[name],raw_stamps[name]=bonus_table(name)
        for name in RAW:
            paths[name],raw_stamps[name]=crafting_table(name)
        identity={"game_build":build,"expansion_id":expansion_id,
            "simc_revision":revision,"v161_stage":wstamp,"v281_stage":sstamp,
            "v229_stage":simstamp,"simc_definition_stage":definition_stamp,
            "raw_stages":raw_stamps,
            "code_sha256":stages.module_dependency_fingerprint([Path(__file__)])["sha256"]}
        generation="embellishment-source-"+stages.digest(
            stages.canonical(identity).encode("utf8"))[:24]
        relative="source/"+generation+".json"
        def execute():
            result=recipe_outputs(project(entries,paths,expansion_id),paths,
                game_build=build,simc_revision=revision,expansion_id=expansion_id)
            result["material_options"]=material_options(result,paths)
            # Match the exact full generated table, including old expansions.
            # A colliding normalized token must not select another effect.
            counts=defaultdict(int)
            for row in entries:counts[simc_token(row["name_enUS"])]+=1
            result["simc_token_counts"]=dict(counts)
            result["source_identity"]=identity
            stages._atomic_write(root/relative,
                (stages.canonical(result)+"\n").encode("utf8"))
        def validate(files):
            result=json.loads(files["candidate"].read_text("utf8"))
            return (result.get("schema")==SCHEMA and
                    result.get("source_identity")==identity and
                    result.get("native_calls")==0 and
                    result.get("ui_promotion") is False)
        stage=stages.execute_stage(root=root,stage_id=generation,
            stage_version="embellishment-recipe-source-v1",inputs=identity,
            outputs={"candidate":relative},execute=execute,validate=validate)
        result=json.loads((root/relative).read_text("utf8"))
        return {"schema":SCHEMA,"status":result["status"],
                "candidate_path":str((root/relative).resolve()),
                "source_stage":{k:v for k,v in stage.items() if k!="result"},
                "matched_effect_count":len(result["matches"]),
                "exact_recipe_spell_count":result["exact_recipe_spell_count"],
                "pending_recipe_spell_count":result["pending_recipe_spell_count"],
                "network_calls_by_stage":calls[0],"native_calls":0,
                "automatic_ui_promotion":False}
    except (OSError,ValueError,TypeError,KeyError,AttributeError,IndexError) as exc:
        reason=str(exc).split(":",1)[0]
        return pending(reason if re.fullmatch(r"[A-Z][A-Z0-9_]{1,119}",reason)
                       else "EMBELLISHMENT_OPTIONAL_SOURCE_UNAVAILABLE",calls[0])
