#!/usr/bin/env python3
"""Discover profession recipes from a clean state using Blizzard Game Data.

No previous item IDs, WEQUIP source, crafted list, or seeded samples are read.
The API does not always publish recipe output IDs: UNKNOWN remains UNKNOWN.
This bounded collector is independent of SimC and the user optimizer.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlencode
import v155_season_api_probe as auth

SCHEMA="v157_source_first_blizzard_profession_recipes_v2"
MAX_RECIPE_DETAILS=3


def need(ok,code):
    if not ok:
        raise auth.ProbeBlocked(code)


def named(rows,term):
    need(type(rows) is list and len(rows)<=500,"LIST_SHAPE")
    return [r for r in rows if type(r) is dict and
            type(r.get("name")) is str and
            term.casefold() in r["name"].casefold() and
            type(r.get("id")) is int and r["id"]>0]


def categories_with_recipes(tier):
    categories=tier.get("categories")
    if type(categories) is not list:
        return {"status":"RECIPE_CATEGORIES_NOT_EXPOSED","recipes":[]}
    need(len(categories)<=400,"CATEGORY_COUNT_LIMIT")
    found={}
    def walk(rows,depth):
        need(depth<4,"CATEGORY_NESTING_LIMIT")
        for row in rows:
            need(type(row) is dict,"CATEGORY_ROW_INVALID")
            recipes=row.get("recipes",[])
            need(type(recipes) is list and len(recipes)<=1000,
                 "RECIPE_LIST_LIMIT")
            for recipe in recipes:
                if (type(recipe) is dict and type(recipe.get("id")) is int
                        and type(recipe.get("name")) is str):
                    rid=recipe["id"]
                    need(rid>0,"RECIPE_ID_INVALID")
                    if rid in found:
                        need(found[rid]==recipe["name"],
                             "DUPLICATE_RECIPE_ID_CONFLICT")
                    found[rid]=recipe["name"]
            sub=row.get("sub_categories",row.get("subcategories",[]))
            need(type(sub) is list,"SUBCATEGORY_SHAPE")
            if sub:
                walk(sub,depth+1)
    walk(categories,0)
    need(len(found)<=4000,"TOTAL_RECIPE_LIMIT")
    return {"status":"EXPLICIT_RECIPE_REFS",
            "recipes":[{"id":i,"name":found[i]} for i in sorted(found)]}


def output_item_ids(recipe):
    """Only explicit output IDs qualify. Missing fields remain unknown."""
    fields=[]
    for key in ("crafted_item","crafted_items"):
        if key not in recipe:
            continue
        values=recipe[key] if type(recipe[key]) is list else [recipe[key]]
        need(len(values)<=30,"OUTPUT_ITEM_LIST_LIMIT")
        for value in values:
            if type(value) is dict and type(value.get("id")) is int:
                need(value["id"]>0,"OUTPUT_ITEM_ID_INVALID")
                fields.append(value["id"])
    return sorted(set(fields)) if fields else None


def gather(client_id,client_secret,*,profession="Tailoring",
           expansion="Midnight",transport=auth.urlopen):
    need(bool(client_id) and bool(client_secret),
         "BLIZZARD_CREDENTIALS_REQUIRED")
    need(type(profession) is str and 1<=len(profession)<=80 and
         type(expansion) is str and 1<=len(expansion)<=80,
         "PROFESSION_OR_EXPANSION_INVALID")
    token=auth.oauth_token(auth.BLIZZARD_TOKEN_URL,
                           client_id,client_secret,transport=transport)
    count=0
    def get(path):
        nonlocal count
        count+=1
        need(count<=6,"BLIZZARD_CRAFT_REQUEST_CEILING")
        return auth.request_json(auth.BLIZZARD_BASE+"/data/wow/"+path+"?"+
                  urlencode({"namespace":"static-kr","locale":"en_US"}),
                  headers={"Authorization":"Bearer "+token},transport=transport)
    index=get("profession/index")
    rows=index.get("professions")
    matches=named(rows,profession) if type(rows) is list else []
    result={"schema":SCHEMA,"status":"PROFESSION_DISCOVERY_PARTIAL",
            "source_authority":"BLIZZARD_API_RESPONSE",
            "selected_profession_query":profession,
            "selected_expansion_query":expansion,
            "profession_id":None,"skill_tier_id":None,
            "profession_matches":matches,
            "available_skill_tiers":[],
            "recipe_index_status":"NOT_QUERIED",
            "discovered_recipe_references":[],
            "sampled_recipe_details":[],
            "blizzard_game_data_requests":count,
            "oauth_requests":1,
            "prior_item_data_used":False,
            "craftable_item_catalog_complete":False,
            "simc_native_calls":0,"static_L_generated":False}
    if len(matches)!=1:
        result["status"]="PROFESSION_NOT_UNIQUELY_IDENTIFIED"
        return result
    pid=matches[0]["id"]
    result["profession_id"]=pid
    detail=get("profession/"+str(pid))
    tiers=detail.get("skill_tiers")
    tierrows=tiers if type(tiers) is list else []
    matching=named(tierrows,expansion)
    result["available_skill_tiers"]=[
        {"id":t["id"],"name":t["name"]} for t in tierrows if
        type(t) is dict and type(t.get("id")) is int and
        type(t.get("name")) is str]
    if len(matching)!=1:
        result["status"]="EXPANSION_TIER_NOT_UNIQUELY_IDENTIFIED"
        result["blizzard_game_data_requests"]=count
        return result
    tierid=matching[0]["id"]
    result["skill_tier_id"]=tierid
    catalog=categories_with_recipes(
        get("profession/"+str(pid)+"/skill-tier/"+str(tierid)))
    result["recipe_index_status"]=catalog["status"]
    result["discovered_recipe_references"]=catalog["recipes"]
    # Deterministic API-only sample. Never rank recipes using historical
    # crafting names, item IDs, WEQUIP or a previous season's database.
    for row in catalog["recipes"][:MAX_RECIPE_DETAILS]:
        doc=get("recipe/"+str(row["id"]))
        need(doc.get("id")==row["id"],"RECIPE_DETAIL_ID_CONFLICT")
        ids=output_item_ids(doc)
        result["sampled_recipe_details"].append({
            "recipe_id":row["id"],"recipe_name":row["name"],
            "crafted_output_item_ids":ids,
            "status":"EXPLICIT_ITEM_IDS" if ids is not None
                     else "OUTPUT_IDS_NOT_EXPOSED_UNKNOWN"})
    result["status"]="BOUNDED_API_FIRST_RECIPE_DISCOVERY"
    result["blizzard_game_data_requests"]=count
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description="Blizzard recipes only, no historic item lists")
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--profession",default="Tailoring")
    p.add_argument("--expansion",default="Midnight")
    args=p.parse_args(argv)
    try:
        data=gather(os.environ.get("BLIZZARD_CLIENT_ID",""),
                    os.environ.get("BLIZZARD_CLIENT_SECRET",""),
                    profession=args.profession,expansion=args.expansion)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(data,sort_keys=True,ensure_ascii=False,
                            indent=2)+"\n",encoding="utf8")
        print(json.dumps({
            "status":data["status"],
            "discovered_recipes":len(data["discovered_recipe_references"]),
            "sampled":len(data["sampled_recipe_details"]),
            "api_requests":data["blizzard_game_data_requests"],
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
