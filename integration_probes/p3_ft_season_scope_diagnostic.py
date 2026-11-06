"""One bounded source-only diagnostic of ambiguous WCL/DB2 raid scope.

Uses the EXISTING v155 and v163 logic, not a new season classifier.
Collects only five small same-build DB2 tables in a temporary directory.
No Native, policy admission, secrets, account data, or full Wago download.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import urlencode
from urllib.request import Request,urlopen

from runner import v155_season_api_probe as api
from runner import v163_zero_seed_db2_join as join
from runner import v242_authenticated_season_source_stage as auth
from runner import v289_retail_live_build_source as retail

TABLES=("MythicPlusSeasonTrackedMap","MapChallengeMode",
        "JournalEncounter","JournalTierXInstance","JournalTier")
MAX_CSV=5_000_000
OUT=Path("p3_ft_season_scope_diagnostic.json")


def raid_candidates(report,encounters,tier_links,mplus_zone_id=None):
    """Diagnostic projection of the original v163 journal-tier criteria."""
    by_tier={}
    for row in tier_links:
        tid=join.number(row["JournalTierID"])
        iid=join.number(row["JournalInstanceID"])
        by_tier.setdefault(tid,set()).add(iid)
    zones=(report.get("wcl") or {}).get("midnight_zones") or []
    projected=[]
    for z in zones:
        if z.get("wcl_frozen") is not False or not z.get("encounters"):
            continue
        found=[join.uniquely_match(e["name"],encounters,"Name_lang")
               for e in z["encounters"]]
        instances={join.number(e["JournalInstanceID"])
                   for e in found if e is not None}
        tiers=sorted(t for t,ids in by_tier.items()
                     if t>0 and instances and instances<=ids)
        # Use the SAME resolver as the production v163 join, not the
        # historical "exactly one matching tier" diagnostic shortcut.
        scoped_tier=(join.resolve_raid_journal_tier(tier_links,instances)
                     if found and all(x is not None for x in found)
                     else None)
        projected.append({
            "zone_id":z["zone_id"],
            "zone_name":z["zone_name"],
            "encounters":len(z["encounters"]),
            "matched_encounters":len([e for e in found if e is not None]),
            "journal_instance_ids":sorted(instances),
            "matching_raid_tier_ids":(
                tiers if all(e is not None for e in found) else []),
            "fully_matched_to_journal":all(e is not None for e in found),
            "selected_journal_tier_id_source_only":scoped_tier,
            "qualified_by_original_raid_rule":(
                z["zone_id"]!=mplus_zone_id and scoped_tier is not None
                and all(e is not None for e in found)),
        })
    return projected


def related_journal_tier_sources(raids,mplus_zone_id,tier_rows,links):
    """Pure projection of same-build metadata, NEVER picks a raid tier."""
    active=[x for x in raids if x["zone_id"]!=mplus_zone_id
            and x["fully_matched_to_journal"]]
    tids={t for raid in active for t in raid["matching_raid_tier_ids"]}
    iids={iid for raid in active for iid in raid["journal_instance_ids"]}
    return {
        "journal_tier_headers":sorted(tier_rows[0]) if tier_rows else [],
        "journal_tier_candidate_rows":[
            {k:v for k,v in row.items()
             if k in ("ID","Name_lang","Flags","Type","ExpansionID",
                      "AvailabilityCondition","Name")}
            for row in tier_rows if join.number(row.get("ID")) in tids],
        "tier_link_headers":sorted(links[0]) if links else [],
        "matching_raid_tier_link_rows":[
            {k:v for k,v in row.items()
             if k in ("ID","JournalTierID","JournalInstanceID",
                      "AvailabilityCondition","Flags","ExpansionID")}
            for row in links
            if join.number(row.get("JournalTierID")) in tids
            and join.number(row.get("JournalInstanceID")) in iids]
    }


def main():
    receipt={
        "schema":"p3_ft_raid_scope_source_only_diagnostic_v1",
        "status":"NOT_RUN",
        "environment_ready":False,"native_calls":0,
        "credentials_logged":False,"all_10_wago_tables_collected":False,
    }
    try:
        missing=[k for k in auth.FIELDS if not os.environ.get(k)]
        receipt["missing_secret_names"]=missing
        if missing:
            receipt["status"]="AUTH_INPUTS_MISSING"
            return 2
        live=retail.discover(region="KR")
        build=live["game_build"]
        receipt["game_build"]=build
        receipt["build_source_sha256"]=live["source_sha256"]
        report=api.run_probe(*(os.environ[k] for k in auth.FIELDS))
        receipt["provider_status"]={
            "blizzard":{k:v.get("status") for k,v in
                        report["blizzard"]["endpoints"].items()},
            "wcl":report["wcl"].get("status"),
        }
        with tempfile.TemporaryDirectory(prefix="p3-ft-source-") as tmp:
            folder=Path(tmp)
            receipt["db2_table_provenance"]={}
            for name in TABLES:
                url="https://wago.tools/db2/"+name+"/csv?"+urlencode({
                    "build":build,"locale":"enUS"})
                req=Request(url,headers={"User-Agent":"simc-secondary-p3-ft/1"})
                with urlopen(req,timeout=45) as reply:
                    if reply.status!=200:
                        raise RuntimeError("DB2_SOURCE_HTTP_INVALID:"+name)
                    raw=reply.read(MAX_CSV+1)
                if not 0<len(raw)<=MAX_CSV:
                    raise RuntimeError("DB2_SOURCE_SIZE_UNSAFE:"+name)
                (folder/(name+".csv")).write_bytes(raw)
                receipt["db2_table_provenance"][name]={
                    "bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
            try:
                scope=join.discover_unique_live_scope(folder,report)
                receipt["original_scope_status"]="UNIQUE_LIVE_SCOPE_RETURNED"
                receipt["original_scope"]=scope
            except join.JoinBlocked as exc:
                receipt["original_scope_status"]="ORIGINAL_V163_PENDING"
                receipt["original_scope_reason"]=str(exc).split(":",1)[0]
            # Reuse v163's EXACT M+ name/set match so the already
            # identified active dungeon zone is not counted as a raid.
            challenge={join.number(x["ID"]):x for x in
                       join.read_rows(folder,"MapChallengeMode")}
            groups={}
            for row in join.read_rows(folder,"MythicPlusSeasonTrackedMap"):
                sid=join.number(row["DisplaySeasonID"])
                mode=challenge.get(join.number(row["MapChallengeModeID"]))
                if sid>0 and mode and mode.get("Name_lang"):
                    groups.setdefault(sid,set()).add(
                        join.norm(mode["Name_lang"]))
            active=(report.get("wcl") or {}).get("midnight_zones") or []
            mplus_matches=[(z["zone_id"],sid) for z in active
                 if z.get("wcl_frozen") is False and z.get("encounters")
                 for sid,names in groups.items()
                 if names and {join.norm(e["name"])
                               for e in z["encounters"]}==names]
            receipt["mplus_zone_id_candidates"]=mplus_matches
            mplus_id=(mplus_matches[0][0]
                      if len(mplus_matches)==1 else None)
            encounters=list(join.read_rows(folder,"JournalEncounter"))
            links=list(join.read_rows(folder,"JournalTierXInstance"))
            receipt["raid_zone_diagnostics"]=raid_candidates(
                report,encounters,links,mplus_zone_id=mplus_id)
            receipt["qualified_raid_zone_count"]=sum(
                x["qualified_by_original_raid_rule"]
                for x in receipt["raid_zone_diagnostics"])
            # Exercise the REAL v163 source-condition resolver on the same
            # current-build original rows; does not install the environment.
            receipt["v163_source_condition_tier_resolution_unadmitted"]={
                str(x["zone_id"]):join.resolve_raid_journal_tier(
                    links,x["journal_instance_ids"])
                for x in receipt["raid_zone_diagnostics"]
                if x["zone_id"]!=mplus_id and
                   x["fully_matched_to_journal"]
            }
            receipt.update(related_journal_tier_sources(
                receipt["raid_zone_diagnostics"],mplus_id,
                list(join.read_rows(folder,"JournalTier")),links))
            receipt["status"]="SOURCE_ONLY_DIAGNOSTIC_COMPLETE"
    except Exception as e:
        receipt["status"]="DIAGNOSTIC_BLOCKED"
        receipt["reason_code"]=(
            str(e).split(":",1)[0]
            if isinstance(e,(api.ProbeBlocked,join.JoinBlocked,RuntimeError))
            else type(e).__name__)
    finally:
        OUT.write_text(json.dumps(receipt,ensure_ascii=False,
                      sort_keys=True,indent=2)+"\n",encoding="utf8")
        print("P3_FT_SCOPE",json.dumps({
            k:receipt.get(k) for k in (
                "status","game_build","provider_status",
                "original_scope_reason","qualified_raid_zone_count",
                "reason_code")},ensure_ascii=False))
    return 0 if receipt["status"]=="SOURCE_ONLY_DIAGNOSTIC_COMPLETE" else 2


if __name__=="__main__":
    raise SystemExit(main())
