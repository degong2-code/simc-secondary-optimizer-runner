#!/usr/bin/env python3
"""v159: narrowly test Blizzard REST Delve discovery, independently of all item DBs.

Opt-in metadata probe only. No guessed Delve gear pool, previous-season
catalogue, Wowhead, SimC Native or user runtime dependency.
A 404 for candidate paths proves *only* those paths fail, not all possible APIs.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import os
from pathlib import Path
from urllib.parse import urlencode
import v155_season_api_probe as api

SCHEMA="v159_blizzard_rest_delve_discovery_probe_v1"
PATHS=(
    ("journal_instance_index","journal-instance/index"),
    ("candidate_delve_index","delve/index"),
    ("candidate_delve_season_index","delve/season/index"),
)
MAX_DETAIL=1

def summarize_index(payload):
    rows=payload.get("instances")
    api.need(type(rows) is list and len(rows)<=1000,
             "JOURNAL_INSTANCE_INDEX_INVALID")
    fields=Counter()
    classifications=Counter()
    labeled=[]
    all_valid=[]
    for row in rows:
        api.need(type(row) is dict,"JOURNAL_INSTANCE_ROW_INVALID")
        item_id=row.get("id")
        name=row.get("name")
        api.need(type(item_id) is int and item_id>0 and
                 type(name) is str,"JOURNAL_INSTANCE_ID_NAME_INVALID")
        fields.update(row.keys())
        all_valid.append({"id":item_id,"name":name})
        for k in ("type","instance_type","category","instance_category"):
            if k in row:
                val=row[k]
                if isinstance(val,dict):
                    val=val.get("name",val.get("type"))
                if isinstance(val,(str,int)):
                    classifications[str(k)+":"+str(val)]+=1
        if any("delve" in str(row.get(k,"")).casefold()
               for k in ("name","type","instance_type","category","instance_category")):
            labeled.append({"id":item_id,"name":name})
    return {"total_journal_instances":len(rows),
            "row_field_frequency":dict(sorted(fields.items())),
            "explicit_type_frequencies":dict(sorted(classifications.items())),
            "delve_explicitly_labeled_rows":labeled,
            "delve_explicitly_labeled_count":len(labeled),
            "all_instances_searched":True,
            "unlabeled_delves_excluded_from_diagnosis":True},all_valid

def run_probe(client_id,client_secret,*,transport=api.urlopen):
    api.need(bool(client_id) and bool(client_secret),
             "BLIZZARD_CREDENTIALS_REQUIRED")
    token=api.oauth_token(api.BLIZZARD_TOKEN_URL,
                          client_id,client_secret,transport=transport)
    get_count=0
    def get(path):
        nonlocal get_count
        get_count+=1
        api.need(get_count<=4,"MAX_GAME_DATA_CALLS")
        return api.request_json(api.BLIZZARD_BASE+"/data/wow/"+path+"?"+
            urlencode({"namespace":"static-kr","locale":"en_US"}),
            headers={"Authorization":"Bearer "+token},
            transport=transport)
    result={
        "schema":SCHEMA,"status":"REST_DELVE_ROUTE_DIAGNOSTIC_COMPLETE",
        "source_authority":"BLIZZARD_REST_GAME_DATA_AUTHENTICATED_KR",
        "api_route_results":{},"journal_index":None,
        "one_journal_detail":None,
        "oauth_calls":1,"blizzard_game_data_requests":0,
        "item_ids_discovered":[],"delve_loot_pool_identified":False,
        "delve_season_membership_verified":False,
        "no_previous_item_db_used":True,"simc_native_calls":0,
        "limitations":["Undocumented candidate route 404 is not proof of all API absence",
                       "Journal index contains instances, not necessarily Delves",
                       "No claimed Delve loot pool or current season completeness"]}
    for name,path in PATHS:
        try:
            data=get(path)
        except api.ProbeBlocked as exc:
            result["api_route_results"][name]={
                "status":"NOT_HTTP_200","error_code":str(exc)}
            continue
        result["api_route_results"][name]={
            "status":"HTTP_200","top_level_keys":sorted(data)}
        if name=="journal_instance_index":
            summary,_=summarize_index(data)
            result["journal_index"]=summary
            labeled=summary["delve_explicitly_labeled_rows"]
            if labeled:
                # Only an explicitly tagged Delve is eligible for the one
                # bounded detail read; no preloaded season name or item ID.
                first=labeled[0]
                result["one_journal_detail"]={
                    "requested_id":first["id"],"requested_name":first["name"],
                    "status":"NOT_QUERIED_YET"}
    detail=result["one_journal_detail"]
    if detail and detail["status"]=="NOT_QUERIED_YET":
        try:
            payload=get("journal-instance/"+str(detail["requested_id"]))
            detail["status"]="HTTP_200"
            detail["keys"]=sorted(payload)
            detail["encounter_count"]=(
                len(payload["encounters"]) if
                type(payload.get("encounters")) is list else None)
            detail["loot_item_ids_present"]=bool(
                type(payload.get("items")) is list or
                type(payload.get("loot")) is list)
        except api.ProbeBlocked as exc:
            detail["status"]="NOT_HTTP_200"
            detail["error_code"]=str(exc)
    result["blizzard_game_data_requests"]=get_count
    return result

def main(argv=None):
    parser=argparse.ArgumentParser(description="Bounded Blizzard REST Delve route audit")
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        output=run_probe(os.environ.get("BLIZZARD_CLIENT_ID",""),
                         os.environ.get("BLIZZARD_CLIENT_SECRET",""))
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(output,ensure_ascii=False,indent=2,
                                       sort_keys=True)+"\n",encoding="utf8")
        print(json.dumps({"status":output["status"],
             "route_results":{k:v["status"] for k,v in
                              output["api_route_results"].items()},
             "game_data_requests":output["blizzard_game_data_requests"],
             "simc_native_calls":0},sort_keys=True))
        return 0
    except api.ProbeBlocked as exc:
        print(json.dumps({"status":"BLOCKED","code":str(exc)}))
        return 3
    except Exception as exc:
        print(json.dumps({"status":"BLOCKED","code":type(exc).__name__}))
        return 3

if __name__=="__main__":
    raise SystemExit(main())
