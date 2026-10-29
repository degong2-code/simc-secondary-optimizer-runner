#!/usr/bin/env python3
"""v155: bounded, opt-in Blizzard + WCL season discovery probe.

Never invoked from product runtime. No Native SimC, DPS engine, loot DB,
client secret logging, broad crawling, or scheduled background activity.
Only fixed first-party API hosts, fixed paths, strict request ceilings.
"""
from __future__ import annotations
import argparse
import base64
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

SCHEMA="v155_season_discovery_provider_probe_v1"
USER_AGENT="SIMCSecondaryOptimizer-P1-DataProbe/1.0"
BLIZZARD_BASE="https://kr.api.blizzard.com"
WCL_BASE="https://www.warcraftlogs.com"
BLIZZARD_TOKEN_URL="https://oauth.battle.net/token"
MAX_RESPONSE_BYTES=1_500_000
TIMEOUT_SECONDS=12

class ProbeBlocked(ValueError):pass

def need(value,code):
    if not value:raise ProbeBlocked(code)

def basic_auth(user,secret):
    need(bool(user) and bool(secret),"CREDENTIAL_PAIR_REQUIRED")
    return "Basic "+base64.b64encode((user+":"+secret).encode("utf8")).decode("ascii")

def request_json(url, *, method="GET", headers=None, data=None, transport=urlopen):
    need(url.startswith((BLIZZARD_BASE+"/data/wow/",
                         WCL_BASE+"/api/v2/client",
                         WCL_BASE+"/oauth/token",
                         BLIZZARD_TOKEN_URL)), "UNAPPROVED_URL")
    req=Request(url,data=data,headers={"User-Agent":USER_AGENT,
                "Accept":"application/json",**(headers or {})},method=method)
    try:
        with transport(req,timeout=TIMEOUT_SECONDS) as response:
            raw=response.read(MAX_RESPONSE_BYTES+1)
            status=response.status
    except HTTPError as e:
        # Never echo remote error bodies (may contain request metadata).
        raise ProbeBlocked("HTTP_"+str(e.code)) from None
    except (URLError,TimeoutError):
        raise ProbeBlocked("NETWORK_UNAVAILABLE") from None
    need(status==200,"HTTP_UNEXPECTED_STATUS")
    need(len(raw)<=MAX_RESPONSE_BYTES,"RESPONSE_TOO_LARGE")
    result=json.loads(raw)
    need(type(result) is dict,"RESPONSE_NOT_JSON_OBJECT")
    return result

def oauth_token(url,client_id,client_secret,*,transport=urlopen):
    body=urlencode({"grant_type":"client_credentials"}).encode("ascii")
    doc=request_json(url,method="POST",data=body,headers={
        "Authorization":basic_auth(client_id,client_secret),
        "Content-Type":"application/x-www-form-urlencoded"},transport=transport)
    token=doc.get("access_token")
    need(type(token) is str and bool(token),"OAUTH_TOKEN_NOT_RETURNED")
    return token

def summarize_blizzard(raw):
    """Preserve schema clues; never mistake dungeon index for season rotation."""
    current=raw.get("current_season")
    if isinstance(current,dict):
        current_id=current.get("id")
    else:
        current_id=None
    need(current_id is None or type(current_id) is int,
         "CURRENT_SEASON_ID_INVALID")
    keys=sorted(raw)
    list_sizes={k:len(v) for k,v in raw.items() if type(v) is list}
    return {"keys":keys,"list_sizes":list_sizes,
            "current_season_id":current_id,
            "current_season_discovery":("DIRECT" if current_id else
                                        "NOT_PRESENT"),
            "season_rotation_dungeon_ids_verified":False,
            "journal_loot_fields_checked":False}

def parse_wcl_expansions(doc):
    need(not doc.get("errors"),"WCL_GRAPHQL_ERRORS")
    data=doc.get("data")
    need(type(data) is dict and type(data.get("worldData")) is dict,
         "WCL_WORLD_DATA_INVALID")
    exps=data["worldData"].get("expansions")
    need(type(exps) is list and len(exps)<=100,
         "WCL_EXPANSIONS_INVALID")
    valid=[]
    for row in exps:
        need(type(row) is dict and type(row.get("id")) is int
             and type(row.get("name")) is str,
             "WCL_EXPANSION_ROW_INVALID")
        valid.append({"id":row["id"],"name":row["name"]})
    return valid

def select_midnight_expansion(exps):
    matches=[x for x in exps if "midnight" in x["name"].casefold()]
    return matches[0]["id"] if len(matches)==1 else None

def parse_wcl_zones(doc):
    need(not doc.get("errors"),"WCL_GRAPHQL_ERRORS")
    data=doc.get("data")
    need(type(data) is dict and type(data.get("worldData")) is dict,
         "WCL_WORLD_DATA_INVALID")
    zones=data["worldData"].get("zones")
    need(type(zones) is list and len(zones)<=200,"WCL_ZONE_LIST_INVALID")
    out=[]
    for zone in zones:
        need(type(zone) is dict and type(zone.get("id")) is int and
             type(zone.get("name")) is str, "WCL_ZONE_ROW_INVALID")
        encounters=zone.get("encounters") or []
        need(type(encounters) is list and len(encounters)<=80,
             "WCL_ENCOUNTERS_INVALID")
        entries=[]
        for encounter in encounters:
            need(type(encounter) is dict and
                 type(encounter.get("id")) is int and
                 type(encounter.get("journalID")) is int and
                 type(encounter.get("name")) is str,
                 "WCL_JOURNAL_ID_NOT_AVAILABLE")
            entries.append({"wcl_encounter_id":encounter["id"],
                "blizzard_journal_encounter_id":encounter["journalID"],
                "name":encounter["name"]})
        out.append({"zone_id":zone["id"],"zone_name":zone["name"],
                    "wcl_frozen":zone.get("frozen"),
                    "encounters":entries})
    return out

def run_probe(blizzard_id,blizzard_secret,wcl_id=None,wcl_secret=None,
              *,transport=urlopen):
    need(bool(blizzard_id)==bool(blizzard_secret),
         "BLIZZARD_PAIR_INCOMPLETE")
    need(bool(wcl_id)==bool(wcl_secret),"WCL_PAIR_INCOMPLETE")
    need(bool(blizzard_id),"BLIZZARD_SECRETS_NOT_CONFIGURED")
    report={"schema":SCHEMA,"mode":"LIVE_AUTHENTICATED_BOUNDED",
        "native_simc_calls":0,"static_L_generated":False,
        "season_loot_complete":False,
        "item_catalog_generated":False,
        "blizzard":{"requests":0,"endpoints":{}},
        "wcl":{"requests":0,"status":"NOT_CONFIGURED"}}
    token=oauth_token(BLIZZARD_TOKEN_URL,blizzard_id,blizzard_secret,
                      transport=transport)
    # One season index + one optional-dungeon index + one period index +
    # one journal index: never enumerate all instances or items.
    endpoints=(
        ("keystone_season_index",
         "/data/wow/mythic-keystone/season/index","dynamic-kr"),
        ("keystone_dungeon_index",
         "/data/wow/mythic-keystone/dungeon/index","dynamic-kr"),
        ("keystone_period_index",
         "/data/wow/mythic-keystone/period/index","dynamic-kr"),
        ("journal_instance_index",
         "/data/wow/journal-instance/index","static-kr"))
    for name,path,namespace in endpoints:
        url=BLIZZARD_BASE+path+"?"+urlencode({
            "namespace":namespace,"locale":"en_US"})
        report["blizzard"]["requests"]+=1
        try:
            result=request_json(url,headers={
                "Authorization":"Bearer "+token},transport=transport)
            report["blizzard"]["endpoints"][name]={
                "status":"HTTP_200",
                "data":summarize_blizzard(result)}
        except ProbeBlocked as e:
            report["blizzard"]["endpoints"][name]={
                "status":"NOT_VERIFIED","error_code":str(e)}
    if wcl_id:
        wcltoken=oauth_token(WCL_BASE+"/oauth/token",wcl_id,wcl_secret,
                            transport=transport)
        def graphql(query,variables=None):
            payload=json.dumps({"query":query,"variables":variables or {}},
                    separators=(",",":")).encode("utf8")
            report["wcl"]["requests"]+=1
            return request_json(WCL_BASE+"/api/v2/client",
                     method="POST",data=payload,headers={
                         "Authorization":"Bearer "+wcltoken,
                         "Content-Type":"application/json"},
                     transport=transport)
        try:
            exps=parse_wcl_expansions(graphql(
                "{ worldData { expansions { id name } } }"))
            report["wcl"]["expansions"]=exps
            midnight_id=select_midnight_expansion(exps)
            report["wcl"]["midnight_expansion_id"]=midnight_id
            if midnight_id is not None:
                zone_query="""query($expansion: Int) {
                  worldData { zones(expansion_id: $expansion) {
                    id name frozen encounters { id name journalID }
                  } } }"""
                report["wcl"]["midnight_zones"]=parse_wcl_zones(
                    graphql(zone_query,{"expansion":midnight_id}))
                report["wcl"]["status"]="ZONES_WITH_JOURNAL_IDS_RETURNED"
            else:
                report["wcl"]["status"]="MIDNIGHT_EXPANSION_NOT_UNIQUELY_FOUND"
        except ProbeBlocked as e:
            report["wcl"]["status"]="NOT_VERIFIED"
            report["wcl"]["error_code"]=str(e)
    report["interpretation"]={
        "keystone_index_is_not_proof_of_rotation":True,
        "wcl_zone_frozen_is_not_raid_season_membership":True,
        "blizzard_journal_raid_and_delve_loot_unverified":True,
        "no_prior_wequip_data_auto_promoted":True}
    return report

def main(argv=None):
    parser=argparse.ArgumentParser(description="Fixed small live API probe; NO Native")
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args(argv)
    try:
        report=run_probe(os.environ.get("BLIZZARD_CLIENT_ID",""),
                          os.environ.get("BLIZZARD_CLIENT_SECRET",""),
                          os.environ.get("WCL_CLIENT_ID",""),
                          os.environ.get("WCL_CLIENT_SECRET",""))
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,sort_keys=True,ensure_ascii=False,
                            indent=2)+"\n",encoding="utf8")
        print(json.dumps({"status":"PROBE_COMPLETE",
               "blizzard_requests":report["blizzard"]["requests"],
               "wcl_requests":report["wcl"]["requests"],
               "output":args.out.name,
               "native_simc_calls":0},sort_keys=True))
        return 0
    except ProbeBlocked as e:
        print(json.dumps({"status":"BLOCKED","code":str(e)}),file=sys.stderr)
        return 3
    except Exception as e:
        # Do not reveal exception messages or URLs that could contain credentials.
        print(json.dumps({"status":"BLOCKED",
                          "code":type(e).__name__}),file=sys.stderr)
        return 3

if __name__=="__main__":
    raise SystemExit(main())
