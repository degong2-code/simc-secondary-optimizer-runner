"""One source-only observation of explicit trinket specialization metadata.

Not a product filter, loot rule engine, effect certificate or Native test.
The existing authenticated rotation cohort supplies IDs; build is derived
from its receipt. Missing override rows are UNKNOWN, not exclusion evidence.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from v737_trinket_loot_spec_source import TABLES,need,sha,classify


def fetch(table,build,root):
    bound,_=TABLES[table]
    url="https://wago.tools/db2/"+table+"/csv?"+urlencode({"build":build,"locale":"enUS"})
    req=Request(url,headers={"User-Agent":"SIMC-Secondary-DB2-Role/1.0","Accept":"text/csv"})
    with urlopen(req,timeout=60) as response:
        need(response.status==200,"ROLE_SOURCE_HTTP:"+table)
        raw=response.read(bound+1)
    need(0<len(raw)<=bound,"ROLE_SOURCE_SIZE:"+table)
    (root/(table+".csv")).write_bytes(raw)
    print("V735_RAW",table,len(raw),sha(raw),flush=True)
    return raw,{"url":url,"bytes":len(raw),"sha256":sha(raw)}

def observe(prior,out):
    out.mkdir(parents=True,exist_ok=True)
    raw_dir=out/"raw";raw_dir.mkdir(exist_ok=True)
    result_path=out/"V735_TRINKET_ROLE_SOURCE.json"
    result={"schema":"p1_v735_trinket_explicit_spec_source_observation_v1",
            "status":"STARTED","native_calls":0,"new_network_attempts":0,
            "product_selection_mutated":False,"full_season_coverage":False,
            "equipment_eligibility_proven":False,"dps_effect_usefulness_proven":False,
            "sources":{}}
    def save():
        result_path.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n","utf8")
    try:
        raw=prior.read_bytes()
        need(0<len(raw)<2_000_000,"ROLE_PRIOR_SIZE")
        doc=json.loads(raw)
        build=doc["game_build"]
        need(doc.get("schema")=="p1_v708_real_mplus_trinket_source_only_v1"
             and type(build) is str and re.fullmatch(r"\d+(?:\.\d+){3}",build)
             and doc.get("native_calls")==0,"ROLE_PRIOR_SCHEMA_BUILD_NATIVE_INVALID")
        need(doc.get("authenticated_rotation_trinket_coverage_verified") is True
             and doc.get("status")=="PASS_REAL_AUTHENTICATED_ROTATION_TRINKET_COVERAGE",
             "ROLE_PRIOR_NOT_AUTHENTICATED_ROTATION_COVERAGE")
        dungeons=doc.get("dungeons")
        need(type(dungeons) is list and len(dungeons)>0
             and len(dungeons)==doc.get("reviewed_dungeons")==doc.get("expected_wcl_dungeons")
             and doc.get("missing_rotation_trinket_ids")==[]
             and doc.get("unmapped_challenge_mode_ids")==[],
             "ROLE_PRIOR_ROTATION_INCOMPLETE")
        cohort={}
        seen_dungeons=set()
        for dungeon in dungeons:
            did=dungeon.get("challenge_mode_id")
            need(type(did) is int and did>0 and did not in seen_dungeons
                 and dungeon.get("status")=="DUNGEON_JOURNAL_OBSERVED"
                 and dungeon.get("registered_rotation_trinket_ids")==dungeon.get("rotation_eligible_trinket_ids")
                 and dungeon.get("missing_rotation_trinket_ids")==[],
                 "ROLE_PRIOR_DUNGEON_INCOMPLETE")
            seen_dungeons.add(did)
            registered=dungeon["registered_rotation_trinkets"]
            need(type(registered) is list and len(registered)>0
                 and sorted(x["item_id"] for x in registered)==dungeon["registered_rotation_trinket_ids"],
                 "ROLE_PRIOR_DUNGEON_ID_DRIFT")
            for item in registered:
                iid=item["item_id"];name=item["name"]
                need(type(iid) is int and iid>0 and isinstance(name,str) and bool(name)
                     and (iid not in cohort or cohort[iid]==name),"ROLE_COHORT_ITEM_INVALID")
                cohort[iid]=name
        need(0<len(cohort)<=2000 and len(cohort)==doc["registered_rotation_trinket_count"],
             "ROLE_COHORT_COUNT_DRIFT")
        result.update(game_build=build,prior_sha256=sha(raw),scope="VERIFIED_MPLUS_ROTATION_ONLY",
                      item_count=len(cohort),dungeon_count=len(seen_dungeons))
        print("V735_PRIOR_SCOPE",build,len(seen_dungeons),len(cohort),sha(raw),flush=True)
        save()
        sources={}
        for table in TABLES:
            result["new_network_attempts"]+=1
            save()
            sources[table],result["sources"][table]=fetch(table,build,raw_dir)
        rows=classify(cohort,sources)
        result.update(status="OBSERVED_EXPLICIT_LOOT_SPEC_METADATA",
                      rows=rows,counts=dict(sorted(Counter(r["status"] for r in rows).items())))
        save()
        print("V735_ROLE_COUNTS",json.dumps(result["counts"],sort_keys=True),flush=True)
        for row in rows:
            print("V735_ROLE",row["item_id"],row["name"],row["status"],
                  ",".join(row["observed_roles"]),flush=True)
        return 0
    except Exception as exc:
        result.update(status="ROLE_SOURCE_PENDING",error=type(exc).__name__+":"+str(exc)[:240])
        save()
        print("V735_PENDING",result["error"],flush=True)
        return 3

def replay(folder):
    """Use exact v736 raw evidence without additional network acquisition."""
    receipt=json.loads((folder/"V735_TRINKET_ROLE_SOURCE.json").read_text("utf8"))
    need(receipt.get("status")=="OBSERVED_EXPLICIT_LOOT_SPEC_METADATA"
         and receipt.get("native_calls")==0,"ROLE_REPLAY_RECEIPT_INVALID")
    build=receipt["game_build"]
    sources={}
    for table in TABLES:
        raw=(folder/"raw"/(table+".csv")).read_bytes()
        evidence=receipt["sources"][table]
        expected="https://wago.tools/db2/"+table+"/csv?"+urlencode({"build":build,"locale":"enUS"})
        need(evidence=={"url":expected,"bytes":len(raw),"sha256":sha(raw)},
             "ROLE_REPLAY_RAW_DRIFT:"+table)
        sources[table]=raw
    cohort={x["item_id"]:x["name"] for x in receipt["rows"]}
    need(len(cohort)==len(receipt["rows"])==receipt["item_count"],"ROLE_REPLAY_COHORT_DRIFT")
    rows=classify(cohort,sources)
    need(rows==receipt["rows"],"ROLE_REPLAY_CLASSIFICATION_DRIFT")
    counts=dict(sorted(Counter(r["status"] for r in rows).items()))
    need(counts==receipt["counts"],"ROLE_REPLAY_COUNTS_DRIFT")
    print("V737_ROLE_REPLAY",json.dumps({"game_build":build,"item_count":len(rows),
          "counts":counts,"new_network_calls":0,"native_calls":0},sort_keys=True))
    return 0


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--prior",type=Path)
    parser.add_argument("--out",type=Path)
    parser.add_argument("--replay",type=Path)
    args=parser.parse_args()
    if args.replay is not None:
        need(args.prior is None and args.out is None,"ROLE_REPLAY_EXCLUSIVE")
        raise SystemExit(replay(args.replay))
    need(args.prior is not None and args.out is not None,"ROLE_OBSERVATION_INPUT_REQUIRED")
    raise SystemExit(observe(args.prior,args.out))
