"""P3-GA exact 70783 raid-loot expansion distribution diagnostic.

Reuses prior P3-FV 70783 verified raid instance scope as *diagnostic input*.
Never admits a current expansion, publishes an item or runs Native/DPS.
Only four necessary DB2 tables are fetched; no extra WCL/Blizzard secrets.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import tempfile
from urllib.parse import urlencode
from urllib.request import Request,urlopen

from runner import v163_zero_seed_db2_join as join
from runner import v289_retail_live_build_source as retail

SOURCE_BUILD="12.1.5.70783"  # One-off evidence-scoped diagnostic, not product logic.
RAID_INSTANCES=(1317,1320,1324)  # Previously proven exact P3-FV instance IDs.
TABLES=("JournalEncounter","JournalEncounterItem","Item","ItemSparse")
MAX_FILE=210_000_000
MAX_TOTAL=260_000_000
OUT=Path("p3_ga_raid_loot_expansion_diagnostic.json")


def summarize_raid_loot(encounters,loots,items,sparse):
    """Return class/expansion distribution; do not select an expansion ID."""
    eids={join.number(x.get("ID")) for x in encounters
          if join.number(x.get("JournalInstanceID")) in RAID_INSTANCES}
    selected={join.number(x.get("ItemID")) for x in loots
              if join.number(x.get("JournalEncounterID")) in eids
              and join.number(x.get("ItemID"))>0}
    by_item={join.number(x.get("ID")):join.number(x.get("ClassID"))
             for x in items if join.number(x.get("ID")) in selected}
    by_sparse={join.number(x.get("ID")):join.number(x.get("ExpansionID"))
               for x in sparse if join.number(x.get("ID")) in selected}
    groups={"equipment":{},"non_equipment":{}}
    samples={"equipment":{},"non_equipment":{}}
    missing={"Item":sorted(selected-set(by_item)),
             "ItemSparse":sorted(selected-set(by_sparse))}
    for iid in sorted(selected):
        if iid not in by_item or iid not in by_sparse:
            continue
        kind="equipment" if by_item[iid] in (2,4) else "non_equipment"
        eid=str(by_sparse[iid])
        groups[kind][eid]=groups[kind].get(eid,0)+1
        samples[kind].setdefault(eid,[])
        if len(samples[kind][eid])<5:
            samples[kind][eid].append(iid)
    equip_exp={eid for eid,count in groups["equipment"].items()
               if int(eid)>0 and count>0}
    return {
        "matched_raid_encounter_ids":len(eids),
        "raid_loot_item_count":len(selected),
        "complete_item_class_and_expansion_rows":
            len(selected-set(missing["Item"])-set(missing["ItemSparse"])),
        "missing_count":{k:len(v) for k,v in missing.items()},
        "missing_examples":{k:v[:8] for k,v in missing.items()},
        "expansion_by_item_class_counts":groups,
        "examples_by_expansion_item_class":samples,
        "equipment_expansion_candidate_count":len(equip_exp),
        "candidate_equipment_expansion_ids_source_only":
            sorted(map(int,equip_exp)),
        "unique_equipment_expansion_observed_source_only":
            len(equip_exp)==1 and bool(groups["equipment"])
            and not missing["Item"] and not missing["ItemSparse"],
        "environment_ready":False,
        "native_calls":0,
    }


def main():
    receipt={"schema":"p3_ga_exact_build_raid_loot_expansion_observation_v1",
             "status":"NOT_RUN","requested_build":SOURCE_BUILD,
             "raid_instances_source":"P3_FV_VERIFIED_70783_ZONE_53_TIER_505",
             "environment_ready":False,"new_native_calls":0,
             "old_season_item_ids_imported":False,
             "source_file_identities":{}}
    try:
        live=retail.discover(region="KR")
        receipt["actual_retail_build"]=live["game_build"]
        if live["game_build"]!=SOURCE_BUILD:
            receipt["status"]="LIVE_BUILD_CHANGED_DIAGNOSTIC_NOT_APPLICABLE"
            return 2
        with tempfile.TemporaryDirectory(prefix="p3-ga-loot-only-") as td:
            root=Path(td)
            total=0
            for table in TABLES:
                url="https://wago.tools/db2/"+table+"/csv?"+urlencode({
                    "build":SOURCE_BUILD,"locale":"enUS"})
                req=Request(url,headers={"User-Agent":"simc-secondary-p3-ga/1",
                                         "Accept":"text/csv"})
                target=root/(table+".csv")
                sha=hashlib.sha256()
                count=0
                with urlopen(req,timeout=90) as resp:
                    if resp.status!=200:
                        raise RuntimeError("P3_GA_DB2_HTTP_INVALID_"+table)
                    with target.open("wb") as out:
                        while True:
                            part=resp.read(262144)
                            if not part:break
                            count+=len(part)
                            if count>MAX_FILE or total+count>MAX_TOTAL:
                                raise RuntimeError("P3_GA_SOURCE_LIMIT_EXCEEDED")
                            out.write(part)
                            sha.update(part)
                if count==0:
                    raise RuntimeError("P3_GA_DB2_EMPTY_"+table)
                total+=count
                receipt["source_file_identities"][table]={
                    "bytes":count,"sha256":sha.hexdigest()}
            receipts={name:join.read_rows(root,name) for name in TABLES}
            result=summarize_raid_loot(
                receipts["JournalEncounter"],
                receipts["JournalEncounterItem"],
                receipts["Item"],receipts["ItemSparse"])
            receipt["loot_distribution"]=result
            receipt["status"]=(
                "SOURCE_ONLY_RAID_LOOT_EXPANSION_OBSERVED"
                if result["raid_loot_item_count"] and
                   result["matched_raid_encounter_ids"]
                else "RAID_LOOT_IDENTITIES_PENDING")
    except Exception as e:
        receipt["status"]="SOURCE_ONLY_DIAGNOSTIC_BLOCKED"
        receipt["reason"]=str(e).split(":",1)[0][:125]
        receipt["error_type"]=type(e).__name__
    finally:
        receipt["observed_at_utc"]=datetime.now(timezone.utc).isoformat()
        OUT.write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,
                                   indent=2)+"\n",encoding="utf8")
        print("P3_GA_RAID_LOOT_EXPANSIONS",json.dumps({
            "status":receipt["status"],
            "actual_build":receipt.get("actual_retail_build"),
            "distribution":receipt.get("loot_distribution",{}).get(
                "expansion_by_item_class_counts"),
            "missing":receipt.get("loot_distribution",{}).get("missing_count"),
            "reason":receipt.get("reason"),
        },ensure_ascii=False),flush=True)
    return 0 if receipt["status"]=="SOURCE_ONLY_RAID_LOOT_EXPANSION_OBSERVED" else 2

if __name__=="__main__":
    raise SystemExit(main())
