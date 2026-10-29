#!/usr/bin/env python3
"""v156: ONE named Blizzard raid journal instance + encounter loot smoke.

Only a narrow verification of the v155 real-WCL discovered raid name.
No whole-season crawling, no SimC Native, no new item database or L cache.
"""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
from urllib.parse import urlencode
import v155_season_api_probe as api
import v154_blizzard_season_loot_index as existing

SCHEMA="v156_one_blizzard_journal_raid_loot_smoke_v1"
RAID_NAME="The Venomous Abyss"
ENCOUNTER_NAME="Nek'zali the Soulcoiler"
MAX_ROWS=400

def unique_named(rows, name, field):
    api.need(type(rows) is list and len(rows)<=500, "JOURNAL_"+field+"_LIST")
    matches=[]
    for row in rows:
        api.need(type(row) is dict,"JOURNAL_"+field+"_ENTRY")
        if row.get("name","").casefold()==name.casefold():
            identifier=row.get("id")
            api.need(type(identifier) is int and identifier>0,
                     "JOURNAL_"+field+"_ID_INVALID")
            matches.append(identifier)
    api.need(len(matches)==1,"JOURNAL_"+field+"_NOT_UNIQUE_OR_MISSING")
    return matches[0]

def summarize_loot(doc,encounter_id,reference):
    api.need(type(doc) is dict and doc.get("id")==encounter_id,
             "ENCOUNTER_DOCUMENT_ID_MISMATCH")
    # Reuse exactly the existing v154 parser, don't invent item IDs from
    # spell, ability or zone references.
    loot=existing.encounter_loot(doc,encounter_id)
    present=sorted(loot) if loot is not None else None
    if present is None:
        return {"status":"LOOT_FIELD_MISSING_UNKNOWN",
                "observed_item_ids":None,
                "existing_reference_matches":None}
    source=reference["known"]
    return {"status":"EXPLICIT_JOURNAL_LOOT_ITEMS",
            "observed_item_ids":present,
            "observed_unique_ids":len(present),
            "existing_reference_matches":sorted(i for i in present if i in source),
            "existing_effect_hint_matches":sorted(i for i in present
                      if i in source and source[i]["known_effect_candidate"]),
            "existing_delta_special_armor_matches":sorted(i for i in present
                      if i in source and source[i]["delta_special_armor"]),
            "no_static_L_or_simc_effect_certification":True}

def run_probe(client_id, client_secret, *, transport=api.urlopen):
    api.need(bool(client_id) and bool(client_secret),
             "BLIZZARD_CREDENTIALS_REQUIRED")
    token=api.oauth_token(api.BLIZZARD_TOKEN_URL,client_id,client_secret,
                          transport=transport)
    reqs=0
    def get(path):
        nonlocal reqs
        reqs+=1
        api.need(reqs<=3,"DATA_REQUEST_LIMIT")
        return api.request_json(api.BLIZZARD_BASE+"/data/wow/"+path+"?"+
            urlencode({"namespace":"static-kr","locale":"en_US"}),
            headers={"Authorization":"Bearer "+token},transport=transport)
    idx=get("journal-instance/index")
    raid_id=unique_named(idx.get("instances"),RAID_NAME,"INSTANCE")
    raid=get("journal-instance/"+str(raid_id))
    api.need(raid.get("id")==raid_id,"JOURNAL_INSTANCE_ID_DRIFT")
    entries=raid.get("encounters")
    api.need(type(entries) is list and len(entries)<=80,
             "JOURNAL_ENCOUNTERS_SHAPE")
    candidates=[]
    for row in entries:
        api.need(type(row) is dict and type(row.get("id")) is int
                 and type(row.get("name")) is str,
                 "JOURNAL_ENCOUNTER_METADATA_INVALID")
        candidates.append({"id":row["id"],"name":row["name"][:150]})
    exact=[row for row in candidates
           if row["name"].casefold()==ENCOUNTER_NAME.casefold()]
    if len(exact)!=1:
        return {"schema":SCHEMA,"status":"BOSS_NAME_UNMATCHED_NO_LOOT_QUERY",
            "source":"BLIZZARD_GAME_DATA_AUTHENTICATED_KR",
            "selection_basis":"WCL_V155_ACTIVE_MIDNIGHT_RAID_NAME",
            "raid":{"name":RAID_NAME,"journal_instance_id":raid_id},
            "requested_boss_name":ENCOUNTER_NAME,
            "blizzard_journal_encounter_candidates":candidates,
            "oauth_requests":1,"blizzard_game_data_requests":reqs,
            "simc_native_calls":0,"season_complete":False,
            "delve_coverage":False,"mplus_coverage":False,
            "selected_item_effects_certified":False,
            "static_L_generated":False}
    boss_id=exact[0]["id"]
    boss=get("journal-encounter/"+str(boss_id))
    ref=existing.existing_reference(existing.read_json(existing.MASTER),
                                    existing.read_json(existing.DELTA))
    loot=summarize_loot(boss,boss_id,ref)
    return {"schema":SCHEMA,"status":"BOUNDED_JOURNAL_SMOKE_COMPLETE",
            "source":"BLIZZARD_GAME_DATA_AUTHENTICATED_KR",
            "selection_basis":"WCL_V155_ACTIVE_MIDNIGHT_RAID_NAME_AND_BOSS_NAME",
            "raid":{"name":RAID_NAME,"journal_instance_id":raid_id},
            "boss":{"name":ENCOUNTER_NAME,"journal_encounter_id":boss_id},
            "loot":loot,
            "oauth_requests":1,"blizzard_game_data_requests":reqs,
            "simc_native_calls":0,"season_complete":False,
            "delve_coverage":False,
            "mplus_coverage":False,
            "selected_item_effects_certified":False,
            "static_L_generated":False}

def main(argv=None):
    parser=argparse.ArgumentParser(description="ONE actual Blizzard raid boss loot ID smoke")
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        result=run_probe(os.environ.get("BLIZZARD_CLIENT_ID",""),
                         os.environ.get("BLIZZARD_CLIENT_SECRET",""))
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,
                                      indent=2)+"\n",encoding="utf8")
        print(json.dumps({"status":result["status"],
              "loot_status":result.get("loot",{}).get("status","NOT_QUERIED"),
              "game_data_requests":result["blizzard_game_data_requests"],
              "simc_native_calls":0},sort_keys=True))
        return 0
    except (api.ProbeBlocked,existing.LootBlocked) as e:
        print(json.dumps({"status":"BLOCKED","code":str(e)}))
        return 3
    except Exception as e:
        print(json.dumps({"status":"BLOCKED","code":type(e).__name__}))
        return 3

if __name__=="__main__":
    raise SystemExit(main())
