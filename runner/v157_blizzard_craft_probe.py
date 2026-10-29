#!/usr/bin/env python3
"""v157: limited official Blizzard profession → skill-tier → recipe output probe.

One source-data diagnostic, NOT an item DB or runtime gear dependency.
No World of Warcraft character authorization, no SimC DPS/Native calls.
Output is a report of explicit JSON fields only, with unknown retained.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlencode
import v155_season_api_probe as auth

SCHEMA="v157_blizzard_crafted_output_discovery_v1"
REPO=Path(__file__).resolve().parents[1]
EXISTING=REPO/"integration_probes/catalog/v057_crafted_gear_51_recipe_ids.json"
MAX_RECIPES=3

def need(ok,code):
    if not ok:
        raise auth.ProbeBlocked(code)

def named(rows,term):
    need(type(rows) is list and len(rows)<=500,"LIST_SHAPE")
    return [r for r in rows if type(r) is dict and
            type(r.get("name")) is str and term.casefold() in
            r["name"].casefold() and
            type(r.get("id")) is int and r["id"]>0]

def categories_with_recipes(tier):
    cats=tier.get("categories")
    if type(cats) is not list:
        return {"status":"RECIPE_CATEGORIES_NOT_EXPOSED","recipes":[]}
    need(len(cats)<=400,"CATEGORY_COUNT_LIMIT")
    out=[]
    def walk(rows,depth):
        need(depth<4,"CATEGORY_NESTING_LIMIT")
        for row in rows:
            need(type(row) is dict,"CATEGORY_ROW_INVALID")
            recipes=row.get("recipes",[])
            need(type(recipes) is list and len(recipes)<=1000,
                 "RECIPE_LIST_LIMIT")
            for rr in recipes:
                if (type(rr) is dict and type(rr.get("id")) is int
                        and type(rr.get("name")) is str):
                    out.append({"id":rr["id"],"name":rr["name"]})
            sub=row.get("sub_categories",row.get("subcategories",[]))
            need(type(sub) is list,"SUBCATEGORY_SHAPE")
            if sub:walk(sub,depth+1)
    walk(cats,0)
    seen={r["id"]:r for r in out}
    need(len(seen)<=4000,"TOTAL_RECIPES_LIMIT")
    return {"status":"EXPLICIT_RECIPE_REFS","recipes":list(seen.values())}

def output_item_ids(recipe):
    """Missing crafted output is unknown rather than a guaranteed non-gear."""
    fields=[]
    for field in ("crafted_item","crafted_items"):
        if field not in recipe:continue
        values=recipe[field] if type(recipe[field]) is list else [recipe[field]]
        need(len(values)<=30,"OUTPUT_ITEM_LIST_LIMIT")
        for v in values:
            if type(v) is dict and type(v.get("id")) is int:
                fields.append(v["id"])
    return sorted(set(fields)) if fields else None

def source_reference():
    j=json.loads(EXISTING.read_text(encoding="utf8"))
    need(j.get("schema")=="v057_midnight_s2_crafted_equipment_ids_v1",
         "EXISTING_CRAFT_REFERENCE_SCHEMA")
    items=j["items"]
    need(type(items) is list and len(items)==51,"EXISTING_CRAFT_REFERENCE_COUNT")
    ids={r["item_id"] for r in items}
    need(len(ids)==51,"EXISTING_CRAFT_ID_DUPLICATE")
    return ids,[r["name_en"] for r in items]

def recipe_score(recipe, names):
    n=recipe["name"].casefold().replace("'","")
    tokens=set()
    for name in names:
        for word in name.casefold().replace("'","").split():
            if len(word)>=5 and word not in ("woven","gear"):
                tokens.add(word)
    return sum(1 for word in tokens if word in n)

def gather(client_id,client_secret,*,transport=auth.urlopen):
    token=auth.oauth_token(auth.BLIZZARD_TOKEN_URL,client_id,client_secret,
                          transport=transport)
    ids,names=source_reference()
    count=0
    def get(path):
        nonlocal count
        count+=1
        need(count<=6,"BLIZZARD_CRAFT_REQUEST_CEILING")
        return auth.request_json(auth.BLIZZARD_BASE+"/data/wow/"+path+"?"+
                  urlencode({"namespace":"static-kr","locale":"en_US"}),
                  headers={"Authorization":"Bearer "+token},transport=transport)
    index=get("profession/index")
    professions=index.get("professions")
    tailoring=named(professions,"Tailoring") if type(professions) is list else []
    result={"schema":SCHEMA,"status":"PROFESSION_DISCOVERY_PARTIAL",
            "blizzard_game_data_requests":0,"oauth_requests":1,
            "season":"midnight_s2","existing_reference_ids":len(ids),
            "profession_index_count":len(professions) if type(professions) is list else None,
            "profession_match_names":[r["name"] for r in tailoring],
            "profession_id":None,"skill_tier_id":None,
            "skill_tier_names":[],"recipe_references":None,
            "sampled_recipe_results":[],"static_L_generated":False,
            "crafted_item_catalog_complete":False,"delve_item_catalog_queried":False,
            "simc_native_calls":0}
    if len(tailoring)!=1:
        result["status"]="TAILORING_NOT_UNIQUELY_IDENTIFIED"
        result["blizzard_game_data_requests"]=count
        return result
    pid=tailoring[0]["id"]
    result["profession_id"]=pid
    detail=get("profession/"+str(pid))
    tiers=detail.get("skill_tiers")
    matches=named(tiers,"Midnight") if type(tiers) is list else []
    result["skill_tier_names"]=[r["name"] for r in tiers if
       type(r) is dict and type(r.get("name")) is str] if type(tiers) is list else []
    if len(matches)!=1:
        result["status"]="MIDNIGHT_TIER_NOT_UNIQUELY_IDENTIFIED"
        result["blizzard_game_data_requests"]=count
        return result
    tierid=matches[0]["id"]
    result["skill_tier_id"]=tierid
    tier=get("profession/"+str(pid)+"/skill-tier/"+str(tierid))
    refs=categories_with_recipes(tier)
    result["recipe_list_status"]=refs["status"]
    result["recipe_references"]=len(refs["recipes"])
    selected=sorted(refs["recipes"],key=lambda r:(-recipe_score(r,names),r["id"]))[:MAX_RECIPES]
    for r in selected:
        doc=get("recipe/"+str(r["id"]))
        item_ids=output_item_ids(doc)
        result["sampled_recipe_results"].append({
            "recipe_id":r["id"],"recipe_name":r["name"],
            "crafted_output_item_ids":item_ids,
            "overlap_existing_51":sorted(ids.intersection(item_ids or [])),
            "status":"OUTPUT_ID_EXPLICIT" if item_ids is not None else
                     "OUTPUT_ID_UNEXPOSED_UNKNOWN"})
    result["blizzard_game_data_requests"]=count
    result["status"]="BOUNDED_CRAFT_RECIPE_SAMPLE_COMPLETE"
    return result

def verify_reference_item_ids(client_id,client_secret,*,transport=auth.urlopen):
    """Revalidate three old ID/name pairs with official Item API only.

    Item detail name identity is not proof of a recipe producing that item.
    It is intentionally a separate evidence tier from explicit crafted_item.
    """
    ref=json.loads(EXISTING.read_text(encoding="utf8"))
    need(ref.get("schema")=="v057_midnight_s2_crafted_equipment_ids_v1",
         "REFERENCE_SCHEMA")
    targets=("Adherent's Silken Shroud","Martyr's Crown","Martyr's Gloves")
    index={row["name_en"]:row["item_id"] for row in ref["items"]}
    need(all(k in index for k in targets),"REFERENCE_CRAFT_TARGET_MISSING")
    token=auth.oauth_token(auth.BLIZZARD_TOKEN_URL,client_id,client_secret,
                          transport=transport)
    out=[]
    for name in targets:
        item_id=index[name]
        data=auth.request_json(auth.BLIZZARD_BASE+"/data/wow/item/"+str(item_id)+
             "?"+urlencode({"namespace":"static-kr","locale":"en_US"}),
             headers={"Authorization":"Bearer "+token},transport=transport)
        need(data.get("id")==item_id,"OFFICIAL_ITEM_ID_MISMATCH")
        official=data.get("name")
        need(type(official) is str,"OFFICIAL_ITEM_NAME_MISSING")
        out.append({"item_id":item_id,"existing_reference_name":name,
                    "blizzard_item_name":official,
                    "names_equal_casefold":name.casefold()==official.casefold(),
                    "item_class":data.get("item_class",{}).get("name")
                        if type(data.get("item_class")) is dict else None,
                    "inventory_type":data.get("inventory_type",{}).get("name")
                        if type(data.get("inventory_type")) is dict else None,
                    "official_recipe_output_link_verified":False})
    return {"schema":"v157_blizzard_item_reference_crosscheck_v1",
            "status":"THREE_OFFICIAL_ITEM_IDS_QUERIED",
            "oauth_requests":1,"blizzard_game_data_requests":len(out),
            "reference_is_prior_guide_not_api_truth":True,
            "crafting_recipe_output_link_verified":False,
            "simc_native_calls":0,"items":out}

def main(argv=None):
    p=argparse.ArgumentParser(description="Up to 6 Blizzard Game Data queries, no SimC")
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--verify-existing-item-ids",action="store_true")
    args=p.parse_args(argv)
    try:
        r=(verify_reference_item_ids if args.verify_existing_item_ids else gather)(
                 os.environ.get("BLIZZARD_CLIENT_ID",""),
                 os.environ.get("BLIZZARD_CLIENT_SECRET",""))
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(r,sort_keys=True,ensure_ascii=False,indent=2)+"\n",
                            encoding="utf8")
        print(json.dumps({"status":r["status"],
                          "api_requests":r["blizzard_game_data_requests"],
                          "sample_count":len(r.get("sampled_recipe_results",
                                                r.get("items",[]))),
                          "native":0}))
        return 0
    except auth.ProbeBlocked as e:
        print(json.dumps({"status":"BLOCKED","code":str(e)}))
        return 3
    except Exception as e:
        print(json.dumps({"status":"BLOCKED","code":type(e).__name__}))
        return 3

if __name__=="__main__":
    raise SystemExit(main())
