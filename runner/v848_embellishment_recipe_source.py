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
    for r in rows(paths["ItemBonus"],("ParentItemBonusListID","Type","Value_0")):
        b=number(r,"ParentItemBonusListID");kind=number(r,"Type")
        if b not in wanted_bonus_ids:continue
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
            "recipe_slot_sources":slots,
            "recipe_output_item_scope_verified":False,
            "quality_dominance_verified":False,"ui_selectable":False})
    return {"schema":SCHEMA,"status":"RECIPE_OUTPUT_SOURCE_PROJECTED",
            "game_build":game_build,"simc_revision":simc_revision,"expansion_id":expansion_id,
            "recipe_spell_count":len(wanted),"exact_recipe_spell_count":len(exact),
            "pending_recipe_spell_count":len(pending),
            "exact_output_item_count":len({x["item_id"] for x in exact.values()}),
            "matches":projected,"native_calls":0,"ui_promotion":False}


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
                atlas={number(m["quality_source_row"],"CraftingQualityAtlasSetID")
                       for m in members}
                values=[m["reagent_quality_source_rows"][0] for m in members]
                # All other source fields must agree; unknown or changed
                # conditions are not interpreted as equivalent. Do not infer
                # dominance solely from the higher QualityTier.
                ignored={"ID","ItemID","OrderIndex","ReagentEffectPct"}
                rest=[{k:v for k,v in r.items() if k not in ignored} for r in values]
                try:
                    pct=[Decimal(r["ReagentEffectPct"]) for r in values]
                    winner=max(range(len(ranks)),key=ranks.__getitem__)
                    if (len(atlas)==1 and len(set(ranks))==len(ranks)
                        and min(ranks)>0 and all(r==rest[0] for r in rest)
                        and all(v.is_finite() and v>=0 for v in pct)
                        and pct[winner]>=max(pct)):
                        preferred=members[winner]["physical"]["item_id"]
                        status="HIGHEST_SOURCE_QUALITY_CANDIDATE"
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
                "quality_dominance_verified":False,
                "exact_application_verified":False,
                "static_CHMV_owner":"EXISTING_SELECTED_PHYSICAL_VARIANT_NOT_MEASURED_HERE",
                "ui_selectable":False})
    return options

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
