#!/usr/bin/env python3
"""One exact-build source-only observation; reuse v216/v161/v163/v165-167.

No installed environment, G/J/F/O, SimC binary, DPS, or separate collector.
Keep the public DB2 snapshot reusable; never export credentials/provider bodies.
"""
import argparse
import json
import os
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner")]
import v216_environment_build_coordinator as original

BUILD="12.1.5.70961"
SCHEMA="p1_v708_real_mplus_trinket_source_only_v1"

def safe_code(value):
    text=str(value).split(":",1)[0]
    return text if re.fullmatch(r"[A-Z][A-Z0-9_]{2,119}",text) else type(value).__name__

def project(source, gear, candidate):
    """Compare original v163 membership and v707 reconciled catalog."""
    season=source["db2_display_season_id"]
    baseline={}
    for row in source["items"]:
        if row["slot"]!=12:continue
        for origin in row["acquisition_sources"]:
            if original.source_gear_pool._journal_origin_current(origin,season,raid=False):
                baseline.setdefault(origin.get("challenge_mode_id"),set()).add(row["item_id"])
    visible={x["item_id"]:x["name"] for x in candidate["items"] if x["category"]=="trinket"}
    rows=[]
    for entry in gear.get("mplus_trinket_coverage") or []:
        current=set(entry["current_trinket_ids"])
        eligible=set(entry.get("rotation_eligible_trinket_ids",current))
        prev=baseline.get(entry["challenge_mode_id"],set())
        registered=eligible&set(visible)
        rows.append({**entry,"original_v163_current_trinket_ids":sorted(prev),
                     "newly_recovered_current_ids":sorted(registered-prev),
                     "registered_current_trinkets":[{"item_id":i,"name":visible[i]}
                                                     for i in sorted(current&registered)],
                     "registered_rotation_trinkets":[{"item_id":i,"name":visible[i]}
                                                     for i in sorted(registered)],
                     "missing_current_trinket_ids":sorted(current-registered),
                     "rotation_eligible_trinket_ids":sorted(eligible),
                     "registered_rotation_trinket_ids":sorted(registered),
                     "missing_rotation_trinket_ids":sorted(eligible-registered)})
    all_current={i for row in rows for i in row["current_trinket_ids"]}
    all_registered={i for row in rows for i in row["registered_current_trinket_ids"]}
    all_eligible={i for row in rows for i in row["rotation_eligible_trinket_ids"]}
    all_rotation_registered={i for row in rows for i in row["registered_rotation_trinket_ids"]}
    all_baseline={i for row in rows for i in row["original_v163_current_trinket_ids"]}
    missing=all_current-all_registered
    unmapped=[x["challenge_mode_id"] for x in rows if x["status"]!="DUNGEON_JOURNAL_OBSERVED"]
    pending=sorted({i for row in rows for key in ("unscoped_unresolved_trinket_ids",
                                                 "unresolved_loot_ids")
                    for i in row.get(key,[])})
    expected=source.get("wcl_mplus_dungeons")
    # Even zero set difference is not proof if the rotation or any dungeon's
    # loot was not observed. Unknown season rows stay pending.
    explicit_ok=(type(expected) is int and expected>0 and len(rows)==expected
                 and not unmapped and all(r["current_trinket_ids"] for r in rows)
                 and not missing and all(not r["missing_current_trinket_ids"] for r in rows))
    rotation_ok=(type(expected) is int and expected>0 and len(rows)==expected
                 and not unmapped and all(r["rotation_eligible_trinket_ids"] for r in rows)
                 and all(not r["missing_rotation_trinket_ids"] for r in rows)
                 and not pending)
    # v715: use the SAME authenticated derived gear source and A7 proof.
    # The two independent sets are source membership and final product rows.
    direct_rows=(gear.get("selectable_source_extension") or {}).get(
        "mplus_dungeon_review",[])
    eligible_special={i for row in direct_rows for i in
                      row.get("rotation_unscoped_admitted_special_ids",[])}
    observed_special={i for row in direct_rows for i in
                      row.get("unscoped_direct_special_ids",[])}
    special={x["item_id"]:x for x in candidate["items"]
             if x["category"]=="special_effect_gear_candidate" and
             any(original.source_gear_pool._rotation_special_origin_current(
                 origin,season) for origin in x["source_evidence"])}
    registered_special=eligible_special&set(special)
    return {"expected_wcl_dungeons":expected,"reviewed_dungeons":len(rows),
            "rotation_unscoped_direct_special_observed_ids":sorted(observed_special),
            "rotation_direct_special_eligible_ids":sorted(eligible_special),
            "rotation_direct_special_registered_ids":sorted(registered_special),
            "rotation_direct_special_missing_ids":sorted(eligible_special-registered_special),
            "rotation_direct_special_conflict_or_pending_ids":sorted(observed_special-eligible_special),
            "rotation_direct_special_registered_items":[
                {"item_id":i,"name":special[i]["name"],
                 "inventory_type":special[i]["inventory_type"]} for i in sorted(registered_special)],
            "unmapped_challenge_mode_ids":unmapped,
            "original_mapped_dungeons":source.get("mapped_mplus_dungeons"),
            "current_trinket_count":len(all_current),
            "registered_current_trinket_count":len(all_registered),
            "original_v163_current_trinket_count":len(all_baseline),
            "newly_recovered_current_ids":sorted(all_rotation_registered-all_baseline),
            "rotation_eligible_trinket_count":len(all_eligible),
            "registered_rotation_trinket_count":len(all_rotation_registered),
            "missing_rotation_trinket_ids":sorted(all_eligible-all_rotation_registered),
            "authenticated_rotation_trinket_coverage_verified":bool(rotation_ok),
            "missing_current_trinket_ids":sorted(missing),
            "unscoped_or_unresolved_loot_ids":pending,
            "explicit_current_rotation_coverage_verified":bool(explicit_ok),
            "full_season_completeness_confirmed":False,
            "dungeons":rows,
            "total_catalog_trinkets":len(visible),
            "total_catalog_special_effect_candidates":sum(x["category"]=="special_effect_gear_candidate"
                                                          for x in candidate["items"])}


def observe_registered_boss_bonus_sources(folder, source):
    """One bounded diagnostic, not a new admission path or effect engine.

    Use the same authenticated WCL scope, exact pinned DB2 snapshot, original
    v706 bonus discovery and v217 raw owner. Preserve all newly needed public
    tables so a subsequent investigation need not fetch them again.
    """
    import csv
    from collections import defaultdict
    from urllib.parse import urlencode
    from urllib.request import Request
    pool=original.source_gear_pool
    join=original.season_join
    review=original.bonus_effect_review
    stages=original.stage_engine
    # The public raw artifact is reused; v155 is a fresh authenticated
    # provider receipt in this job. Do not export provider bodies or keys.
    files,receipt_path=stages._safe_paths(folder,"fresh-v155",
        {"report":"source/season_api_report.json"})
    receipt=stages._read_receipt(receipt_path)
    assert receipt["status"]=="COMPLETE" and receipt["stage_id"]=="fresh-v155"
    stages._verify_outputs(receipt,files)
    report=json.loads(files["report"][1].read_text("utf8"))
    assert report["mode"]=="LIVE_AUTHENTICATED_BOUNDED"
    scope=source["auto_source_scope"]
    season=source["db2_display_season_id"]
    for kind in ("raid","mplus"):
        zone=join.named_zone(report,scope[kind+"_zone"],
                            wcl_expansion_id=scope["wcl_expansion_id"])
        assert zone["zone_id"]==source["wcl_zone_ids"][kind]
    journal=list(pool.read_csv(folder/"wago/JournalEncounter.csv",
                               ("ID","JournalInstanceID","Name_lang")))
    # Focus targets are diagnostics ONLY. Discovery is across all registered
    # same-expansion active WCL encounters, not hardcoded production IDs.
    targets={271874,271875,271876,271878,281235,281236,281238,281239}
    matched=defaultdict(list)
    for zone in join.wcl_zone_sources(report):
        if zone.get("wcl_frozen") is not False or zone.get("expansion_id")!=scope["wcl_expansion_id"]:
            continue
        for boss in zone.get("encounters",[]):
            row=join.uniquely_match(boss["name"],journal,"Name_lang")
            if row is not None:
                matched[int(row["ID"])].append({"wcl_zone_id":zone["zone_id"],
                    "wcl_boss_name":boss["name"],"journal_encounter_id":int(row["ID"]),
                    "journal_instance_id":int(row["JournalInstanceID"]),
                    "journal_name":row["Name_lang"]})
    journal_by_id={int(row["ID"]):row for row in journal}
    loot=defaultdict(list)
    target_journal=defaultdict(list)
    for row in pool.read_csv(folder/"wago/JournalEncounterItem.csv",
                ("ID","JournalEncounterID","ItemID","DisplaySeasonID")):
        iid=int(row["ItemID"]); eid=int(row["JournalEncounterID"])
        if iid<=0 or (eid not in matched and iid not in targets):continue
        raw_season=join.exact_display_season_id(row["DisplaySeasonID"])
        if iid in targets:
            target_journal[iid].append({"journal_encounter_id":eid,
                "journal_name":journal_by_id.get(eid,{}).get("Name_lang"),
                "raw_display_season_id":raw_season,
                "authenticated_wcl_matches":matched.get(eid,[])})
        if eid in matched and raw_season in (0,season):
            loot[iid].extend({**origin,"raw_display_season_id":raw_season}
                             for origin in matched[eid])
    wanted=set(loot)|targets
    sparse={int(row["ID"]):row for row in pool.read_csv(
        folder/"wago/ItemSparse.csv",("ID","InventoryType","Display_lang","ItemSet","ExpansionID"))
        if int(row["ID"]) in wanted}
    wanted={iid for iid in wanted if iid in sparse and
            int(sparse[iid]["InventoryType"]) in pool.SPECIAL_INVENTORY_TYPES
            and int(sparse[iid]["ExpansionID"])==source["db2_expansion_id"]}
    direct,_=pool.effects(folder/"source/raw_gear_effect.csv",wanted)
    attempted=[0]
    table_paths={}; identities={}
    for table in review.COLUMNS:
        # Existing v250 sealed files, when available, take precedence.
        existing=folder/("source/v250_bonus_"+table+".csv")
        if table in original.raid_bonus.TABLES and existing.is_file():
            raise RuntimeError("V716_EXISTING_V250_SOURCE_REQUIRES_RECEIPT_REUSE")
        url="https://wago.tools/db2/"+table+"/csv?"+urlencode({"build":BUILD,"locale":"enUS"})
        def obtain():
            attempted[0]+=1
            req=Request(url,headers={"User-Agent":"SIMC-Secondary-Bonus/1.0","Accept":"text/csv"})
            with original.urlopen(req,timeout=75) as response:
                assert response.status==200
                data=bytearray()
                while True:
                    chunk=response.read(262144)
                    if not chunk:break
                    data.extend(chunk)
                    assert len(data)<=review.MAX_BYTES[table]
            return bytes(data)
        def valid(raw):
            return review.valid_raw_table(raw,table)
        path,raw,seal=original._sealed_season_raw_source(root=folder,
            source_id="season-bonus-raw-"+table,build=BUILD,url=url,
            relative="source/raw_"+table+".csv",obtain=obtain,validate_bytes=valid)
        table_paths[table]=path
        identities[table]={"sha256":original.digest(raw),"receipt_sha256":seal}
        del raw
    # Exercise the real source expansion used in both Environment Build
    # and existing-season refresh. Focus IDs are never fed into its scope.
    expanded=pool.expand_selectable_source(source,folder/"wago",
        folder/"source/raw_gear_effect.csv",wcl_report=report)
    extension=expanded["selectable_source_extension"]
    product_review_ids=set(extension.get("indirect_review_item_ids",[]))
    product_review_ids.update(row["item_id"] for row in expanded["items"])
    product_review_ids &= wanted
    result=review.discover(wanted,table_paths)
    by_id={row["item_id"]:row for row in result["items"]}
    # Retain source links, not an invented obtainable variant. No automatic
    # attachment, source-season promotion, G update, or independent proc test.
    def item_row(iid):
        row=sparse.get(iid,{})
        return {"item_id":iid,"name":row.get("Display_lang"),
            "inventory_type":int(row["InventoryType"]) if row else None,
            "direct_item_effect_record":iid in direct,
            "registered_current_wcl_origins":loot.get(iid,[]),
            "journal_occurrences":target_journal.get(iid,[]),
            "bonus_effects":by_id.get(iid,{}).get("bonus_effects",[]),
            "applicable_variant_verified":False}
    focus=[item_row(iid) for iid in sorted(targets)]
    all_indirect=[item_row(iid) for iid in sorted(set(by_id)-direct)]
    return {"status":"OBSERVED_REGISTERED_BOSS_BONUS_SOURCE_ONLY",
        "game_build":BUILD,"authenticated_wcl_expansion_id":scope["wcl_expansion_id"],
        "active_display_season_id":season,"registered_journal_encounter_count":len(matched),
        "reviewed_equipment_count":len(wanted),"raw_bonus_network_calls":attempted[0],
        "raw_bonus_sources":identities,"focus_items":focus,
        "registered_boss_indirect_candidates":all_indirect,
        "focus_registered_count":sum(bool(x["registered_current_wcl_origins"]) for x in focus),
        "focus_bonus_link_count":sum(bool(x["bonus_effects"]) for x in focus),
        "focus_product_review_scope_ids":sorted(targets&product_review_ids),
        "focus_product_review_missing_ids":sorted(
            {x["item_id"] for x in focus if x["registered_current_wcl_origins"]}-product_review_ids),
        "native_calls":0,"budget_rebuilt":False,"automatic_registration":False,
        "full_season_completeness_confirmed":False}

def observe(out):
    dest=Path(out).resolve()
    dest.mkdir(parents=True,exist_ok=True)
    path=dest/"V708_REAL_MPLUS_TRINKET_COVERAGE.json"
    state={"schema":SCHEMA,"game_build":BUILD,"status":"STARTED",
           "native_calls":0,"budget_rebuilt":False,"environment_installed":False,
           "full_season_completeness_confirmed":False,
           "unregistered_field_boss_search":False}
    def save():
        path.write_text(json.dumps(state,ensure_ascii=False,indent=2,sort_keys=True,
                                   allow_nan=False)+"\n","utf8")
    save()
    try:
        credentials={key:os.environ.get(key,"") for key in original.discovery_stage.FIELDS}
        if not all(credentials.values()):
            state["status"]="PENDING_EXISTING_ACTIONS_CREDENTIALS"
            return 2
        root=dest/"runs"
        root.mkdir(exist_ok=True)
        reuse=os.environ.get("V709_REUSE_REQUIRED")=="1"
        folder=root/"_fresh_season_sources"/("wago_"+BUILD)
        def forbid_db2(*args,**kwargs):
            raise RuntimeError("V709_UNEXPECTED_DB2_REDOWNLOAD")
        if reuse and not (folder/"wago/receipt.json").is_file():
            raise RuntimeError("V709_REUSE_ARTIFACT_MISSING")
        collected=original.collect_wago_new_season_source(
            sessions_root=root,expected_game_build=BUILD,credentials=credentials,
            myth_target_source_only=True,fetch=forbid_db2 if reuse else None)
        state["wago_snapshot_executed"]=collected["source_stage"].get("executed")
        state["raw_db2_reuse_required"]=reuse
        if reuse and state["wago_snapshot_executed"] is not False:
            raise RuntimeError("V709_RAW_SOURCE_REUSE_NOT_CONFIRMED")
        state["source_network_calls"]=collected["network_calls_by_stage"]
        state["wago_source_stage_sha256"]=collected["source_stage"]["receipt_sha256"]
        linked=collected["season_join"]
        state["season_join_status"]=linked.get("status")
        if not linked.get("candidate_path"):
            state.update(status="PENDING_AUTHENTICATED_SEASON_JOIN",
                         first_blocker=linked.get("reason"))
            return 2
        folder=root/"_fresh_season_sources"/("wago_"+BUILD)
        source=json.loads(Path(linked["candidate_path"]).read_text("utf8"))
        state["original_v163_sha256"]=original.digest(Path(linked["candidate_path"]).read_bytes())
        if os.environ.get("V716_BONUS_REVIEW")=="1":
            state.update(observe_registered_boss_bonus_sources(folder,source))
            print("V716_FOCUS "+json.dumps(state["focus_items"],ensure_ascii=False,sort_keys=True),flush=True)
            print("V716_SUMMARY "+json.dumps({k:state[k] for k in ("focus_registered_count","focus_bonus_link_count","raw_bonus_network_calls","reviewed_equipment_count","focus_product_review_scope_ids","focus_product_review_missing_ids")},sort_keys=True),flush=True)
            return 0
        # The same stage used by existing-season refresh, without the
        # unrelated optional bonus/tier/SimC investigation.
        def reuse_transport(req,timeout):
            if "/ItemXItemEffect/" in req.full_url:
                raise RuntimeError("V709_UNEXPECTED_EFFECT_REDOWNLOAD")
            return original.urlopen(req,timeout=timeout)
        gear=original._fresh_ordinary_gear_source_stage(
            stage_root=folder,wago_folder=folder/"wago",build=BUILD,
            linked=linked,include_delve=True,transport=reuse_transport if reuse else None)
        state["gear_network_calls"]=gear["network_calls_by_stage"]
        state["gear_status"]=gear["status"]
        a7=gear.get("a7_auto_source_choice_provenance") or {}
        state["source_provenance_verified"]=a7.get("candidate_provenance_verified",False)
        state["delve_status"]=gear.get("supplementary_delve_status")
        state["delve_unresolved_count"]=gear.get("supplementary_delve_unresolved_count")
        if not gear.get("candidate_path"):
            state.update(status="PENDING_GEAR_SOURCE",first_blocker=gear.get("reason"))
            return 2
        candidate_path=Path(gear["candidate_path"])
        candidate=json.loads(candidate_path.read_text("utf8"))
        state["candidate_sha256"]=original.digest(candidate_path.read_bytes())
        state["gear_source_stage_sha256"]=gear["source_stage"]["receipt_sha256"]
        state.update(project(source,gear,candidate))
        print("V715_DIRECT_SPECIAL_SOURCE "+json.dumps({k:v for k,v in state.items()
            if k.startswith("rotation_direct_special_") or
               k=="rotation_unscoped_direct_special_observed_ids"},
            sort_keys=True,ensure_ascii=False))
        if state["rotation_direct_special_missing_ids"]:
            state.update(status="PENDING_DIRECT_SPECIAL_SOURCE_JOIN",
                         first_blocker="V715_DIRECT_SPECIAL_ELIGIBLE_ID_MISSING")
            return 2
        state["registered_boss_review"]=(gear.get("selectable_source_extension") or {}).get(
            "supplementary_wcl_boss_review")
        if not state["source_provenance_verified"]:
            state.update(status="PENDING_SOURCE_PROVENANCE",first_blocker=a7.get("reason"))
        elif state["authenticated_rotation_trinket_coverage_verified"]:
            state["status"]="PASS_REAL_AUTHENTICATED_ROTATION_TRINKET_COVERAGE"
        elif not state["explicit_current_rotation_coverage_verified"]:
            state["status"]="OBSERVED_REAL_MPLUS_COVERAGE_GAPS"
        elif state["unscoped_or_unresolved_loot_ids"]:
            state["status"]="OBSERVED_REAL_EXPLICIT_CURRENT_MATCH_UNRESOLVED_LOOT_PENDING"
        else:
            state["status"]="PASS_REAL_EXPLICIT_CURRENT_ROTATION_COVERAGE"
        # One completed observation is useful even when it documents gaps.
        # Only the explicit PASS status is a verified positive result.
        return 0 if state["source_provenance_verified"] else 2
    except Exception as exc:
        import traceback
        state["failure_frames"]=[{"file":Path(frame.filename).name,"line":frame.lineno,"function":frame.name}
            for frame in traceback.extract_tb(exc.__traceback__)[-5:]]
        print("SOURCE_FAILURE_FRAMES "+json.dumps(state["failure_frames"],sort_keys=True),flush=True)
        state.update(status="BLOCKED_REAL_SOURCE_OBSERVATION",
                     first_blocker=safe_code(exc),error_type=type(exc).__name__)
        return 2
    finally:
        save()
        print("V708_SOURCE_VERDICT "+json.dumps({k:state.get(k) for k in (
            "status","first_blocker","expected_wcl_dungeons","reviewed_dungeons",
            "current_trinket_count","registered_current_trinket_count",
            "original_v163_current_trinket_count","newly_recovered_current_ids",
            "missing_current_trinket_ids","unmapped_challenge_mode_ids",
            "rotation_eligible_trinket_count","registered_rotation_trinket_count",
            "missing_rotation_trinket_ids","authenticated_rotation_trinket_coverage_verified",
            "wago_snapshot_executed","source_network_calls","gear_network_calls",
            "explicit_current_rotation_coverage_verified","native_calls")},
            ensure_ascii=True,sort_keys=True),flush=True)
        # Small per-dungeon evidence in actual Actions logs, not raw sources.
        for row in state.get("dungeons",[]):
            print("V708_DUNGEON "+json.dumps(row,ensure_ascii=True,sort_keys=True),flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True)
    raise SystemExit(observe(parser.parse_args().out))
