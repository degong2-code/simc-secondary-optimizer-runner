#!/usr/bin/env python3
"""One pinned 70961 crafting-relation source observation, NOT UI admission.

Reuse original public v708/v716 raw bytes, original v217 seal and v216
raw acquisition. No fresh environment Build, Blizzard secrets, Native,
or claim that a source recipe spell is a legal final equipment item.
"""
import argparse
import csv
import io
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
import v216_environment_build_coordinator as env
import v217_stage_execution_engine as stages
import v229_simc_only_source_seed as seed

BUILD="12.1.5.70961"
REV="6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7"
EXPANSION=11
SIMC_PATH="engine/dbc/generated/embellishment_data.inc"
SIMC_BLOB="fc42a61cfc69481455539d074310310668f26a3f"
RAW={
 "ModifiedCraftingReagentItem":("ID","ModifiedCraftingCategoryID","ItemBonusTreeID"),
 "ModifiedCraftingReagentSlot":("ID","Name_lang","Flags","PlayerConditionID","ReagentType"),
 "MCRSlotXMCRCategory":("ID","ModifiedCraftingCategoryID","ModifiedCraftingReagentSlotID"),
 "ModifiedCraftingSpellSlot":("ID","SpellID","ModifiedCraftingReagentSlotID","Slot","ReagentCount"),
}
MAX_BYTES=8_000_000
MAX_ROWS=400_000
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
def reuse(root,stage,keys,expected=None):
    receipt=stages._read_receipt(root/".stage_receipts"/(stage+".json"))
    need(receipt["status"]=="COMPLETE" and receipt["stage_id"]==stage and
         (expected is None or expected==receipt["receipt_sha256"]),"OLD_STAGE_SCOPE")
    paths={k:(receipt["output_paths"][k],root/receipt["output_paths"][k]) for k in keys}
    for rel,p in paths.values():
        need(p.resolve().is_relative_to(root.resolve()) and not p.is_symlink(),"OLD_PATH")
    actual,_=stages._snapshot(paths)
    need(all(receipt["outputs"].get(k)==v for k,v in actual.items()),"OLD_STAGE_BYTES")
    return {k:p for k,(_,p) in paths.items()},receipt["receipt_sha256"]
def obtain(url,cap,counter):
    counter[0]+=1
    req=Request(url,headers={"User-Agent":"SIMC-Secondary-CraftingSource/1.0"})
    with urlopen(req,timeout=75) as r:
        need(r.status==200,"SOURCE_HTTP_NON200")
        data=r.read(cap+1)
    need(0<len(data)<=cap,"SOURCE_SIZE")
    return data
def valid_csv(raw,cols):
    if not 0<len(raw)<=MAX_BYTES:return False
    try:return set(cols)<=set(next(csv.reader(io.StringIO(
        raw[:min(len(raw),65536)].decode("utf-8-sig")))))
    except (ValueError,StopIteration,csv.Error):return False
def read_simc(raw,build):
    need(seed.git_blob(raw)==SIMC_BLOB,"SIMC_ORIGINAL_GIT_BLOB_DRIFT")
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
    need(len(entries)==int(header[1]),"SIMC_COUNT_DRIFT")
    return entries
def project(entries,paths,expansion):
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
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();root=a.root.resolve();a.out.mkdir(parents=True,exist_ok=True)
    doc={"game_build":BUILD,"simc_revision":REV,"expansion_id":EXPANSION,
         "status":"SOURCE_PENDING","native_calls":0,"new_approval_granted":False}
    count=[0]
    try:
        paths,stage=reuse(root,"fresh-wago-db2",("ItemSparse","Item","CraftingData","receipt"),
                           "8983e9a8c621d36e0af44e78f88e31469417be4685ce077f6cf3ceccf21f610d")
        need(json.loads(paths["receipt"].read_text("utf8"))["build"]==BUILD,"OLD_BUILD")
        doc["reused_receipts"]={"wago":stage}
        for table in ("ItemBonusTreeNode","ItemBonus"):
            old,stamp=reuse(root,"season-bonus-raw-"+table,("raw",))
            paths[table]=old["raw"];doc["reused_receipts"][table]=stamp
        raw=obtain("https://raw.githubusercontent.com/simulationcraft/simc/"+REV+"/"+SIMC_PATH,
                   200_000,count)
        entries=read_simc(raw,BUILD)
        doc["simc_source"]={"path":SIMC_PATH,"git_blob_sha1":SIMC_BLOB,
                           "sha256":stages.digest(raw),"row_count":len(entries)}
        doc["new_receipts"]={}
        for table,cols in RAW.items():
            url="https://wago.tools/db2/"+table+"/csv?"+urlencode({"build":BUILD,"locale":"enUS"})
            path,_,stamp=env._sealed_season_raw_source(
                root=root,source_id="season-crafting-raw-"+table,build=BUILD,url=url,
                relative="source/raw_"+table+".csv",
                obtain=lambda:obtain(url,MAX_BYTES,count),
                validate_bytes=lambda raw:valid_csv(raw,cols))
            paths[table]=path;doc["new_receipts"][table]=stamp
        matches=project(entries,paths,EXPANSION)
        doc.update(status="EXACT_CRAFTING_REAGENT_EFFECT_RELATIONS_OBSERVED" if matches
                   else "NO_EXACT_CRAFTING_RELATIONS_OBSERVED",
                   matches=matches,matched_effect_rows=len(matches),
                   physical_item_count=len({p["item_id"] for m in matches for p in m["physical_rows"]}))
    except Exception as e:
        doc["first_blocker"]={"type":type(e).__name__,"code":str(e)[:240]}
    finally:
        doc["new_source_requests"]=count[0]
        (a.out/"V847_EMBELLISHMENT_SOURCE.json").write_text(
            json.dumps(doc,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")
        print("V847",doc["status"],"native0","requests",count[0],
              "matches",doc.get("matched_effect_rows"),"blocker",doc.get("first_blocker"))
    return 0 if doc["status"]=="EXACT_CRAFTING_REAGENT_EFFECT_RELATIONS_OBSERVED" else 2
if __name__=="__main__":raise SystemExit(main())
