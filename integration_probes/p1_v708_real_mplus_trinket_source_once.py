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
    return {"expected_wcl_dungeons":expected,"reviewed_dungeons":len(rows),
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
