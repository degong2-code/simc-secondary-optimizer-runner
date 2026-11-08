"""P3-HT one-time read-only audit of ALREADY EXECUTED v094 native cases.

No fresh SimC, profile modification, effect emulation or independent tier
gate. The existing v065/v094 native SHA receipts remain authoritative.
Store the exact chosen case bytes so reviewers can inspect tier, primary stats,
raid buffs and consumables without an additional expensive native run.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import zipfile

SCHEMA="p3_ht_existing_v094_one_native_case_audit_v1"
PHASE_FOLDERS={
    "SEED_00":"search/seed_00",
    "SEED_01":"search/seed_01",
    "SCOUT_00":"search/scout_00",
    "MATERIAL_00":"search/material_00",
    "CONFIRM_00":"confirmations/confirm_00",
    "CONFIRM_01":"confirmations/confirm_01",
}
ARCHIVE_NAME="p3_ht_dps_native_audit.zip"

class AuditBlocked(ValueError):
    pass

def need(ok,code):
    if not ok:
        raise AuditBlocked(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def read_bounded(path,limit):
    need(path.is_file() and not path.is_symlink()
         and 0<path.stat().st_size<=limit,"P3_HT_NATIVE_SOURCE_FILE_MISSING_OR_TOO_LARGE")
    return path.read_bytes()

def _interesting_action_rows(player):
    items={}
    for field in ("stats","buffs","procs"):
        source=player.get(field,[])
        if type(source) is not list:
            source=[]
        entries=[]
        for row in source:
            if type(row) is not dict:
                continue
            name=row.get("name")
            if type(name) is str and any(token in name.lower() for token in
                ("nova","blaze","burning_core","short_circuit",
                 "crash_lightning","set_bonus","tier","doom_winds")):
                entries.append({key:row.get(key) for key in
                    ("name","spell_name","num_executes","start_count",
                     "trigger_count","uptime","compound_amount") if key in row})
        items[field]=entries
    return items

def _one_case(folder,row):
    input_bytes=read_bounded(folder/"input.simc",200_000)
    native_bytes=read_bounded(folder/"result.json",15_000_000)
    need(sha(input_bytes)==row.get("input_sha256") and
         sha(native_bytes)==row.get("native_sha256"),
         "P3_HT_ORIGINAL_NATIVE_RESULT_OR_INPUT_SHA_MISMATCH")
    doc=json.loads(native_bytes)
    sim=doc.get("sim")
    need(type(sim) is dict and
         type(sim.get("players")) is list and
         len(sim["players"])==1,"P3_HT_NATIVE_ONE_PLAYER_REQUIRED")
    actor=sim["players"][0]
    collected=actor.get("collected_data") or {}
    attributes=(collected.get("buffed_stats") or {}).get("attribute") or {}
    need(type(attributes) is dict,"P3_HT_NATIVE_PRIMARY_ATTRIBUTE_MISSING")
    equipment=actor.get("gear") or {}
    need(type(equipment) is dict,"P3_HT_NATIVE_GEAR_MISSING")
    summary={
        "phase":row["phase"],"dps_mean":row["dps_mean"],
        "dps_sem":row["dps_sem"],"samples":row["samples"],
        "native_sha256":row["native_sha256"],
        "input_sha256":row["input_sha256"],
        "player":{"name":actor.get("name"),
                  "race":actor.get("race"),
                  "specialization":actor.get("specialization"),
                  "level":actor.get("level"),
                  "talents":actor.get("talents")},
        "primary_attributes":attributes,
        "gear_primary_rating_sum":sum(
            sum(v.get(k,0) for k in ("agiint","stragiint","agility",
                                     "strength","intelligence","intellect"))
            for v in equipment.values() if type(v) is dict),
        "gear":{"slots":list(equipment),"pieces":[{
            "slot":slot,"name":item.get("name"),
            "ilevel":item.get("ilevel"),"encoded_item":item.get("encoded_item")}
            for slot,item in equipment.items() if type(item) is dict]},
        "raid_overrides":sim.get("overrides"),
        "raid_optimal_setting":(sim.get("options") or {}).get("optimal_raid"),
        "simc_iterations":(sim.get("options") or {}).get("iterations"),
        "precombat_consumables":{k:actor.get(k) for k in
                ("flask","food","potion","augmentation","temporary_enchant")},
        "constant_buffs":[{
            "name":b.get("name"),"uptime":b.get("uptime")}
            for b in actor.get("buffs_constant",[])
            if type(b) is dict],
        "tier_relevant_actual_actions":_interesting_action_rows(actor),
    }
    return summary,input_bytes,native_bytes

def record(applied,native,root,*,output_path):
    root=pathlib.Path(root).resolve(strict=True)
    manifest=pathlib.Path(applied["generated_manifest"]).resolve(strict=True)
    need(manifest.is_relative_to(root) and
         manifest.name=="manifest.json","P3_HT_INSTALLED_USER_MANIFEST_PATH_DRIFT")
    profile=read_bounded(manifest.parent/"profile.simc",250_000)
    output=pathlib.Path(applied["output_dir"]).resolve(strict=True)
    need(output.is_relative_to(root) and output.name=="simc_results" and
         output.parent==manifest.parent,
         "P3_HT_V094_OUTPUT_PATH_DRIFT")
    report_bytes=read_bounded(output/"V094_RESULT.json",3_000_000)
    report=json.loads(report_bytes)
    rows=report.get("observations")
    need(type(rows) is list and len(rows)==6 and
         set(row.get("phase") for row in rows)==set(PHASE_FOLDERS),
         "P3_HT_EXACT_SIX_NATIVE_PHASES_REQUIRED")
    summaries={}
    selected=None
    best=max(rows,key=lambda row:row["dps_mean"])
    requested=(native.get("user_result") or {}).get(
        "observed_first_choice",{}).get("observed_dps_mean")
    need(type(requested) in (float,int) and
         abs(best["dps_mean"]-requested)<0.000001,
         "P3_HT_OBSERVED_FIRST_CHOICE_RESULT_DRIFT")
    for row in rows:
        folder=(output/PHASE_FOLDERS[row["phase"]]).resolve(strict=True)
        need(folder.is_relative_to(output) and folder.is_dir(),
             "P3_HT_V094_NATIVE_PHASE_PATH_DRIFT")
        brief,source_raw,native_raw=_one_case(folder,row)
        summaries[row["phase"]]=brief
        if row is best:
            selected=(source_raw,native_raw,brief)
    need(selected is not None,"P3_HT_BEST_NATIVE_CASE_MISSING")
    compact={"schema":SCHEMA,"status":"EXISTING_SIMC_NATIVE_JSON2_OBSERVED_NO_EXTRA_CALL",
             "chosen_phase":best["phase"],"observations":summaries,
             "native_calls_added_by_audit":0,"reuses_original_v094":True,
             "tier_effect_interpretation_or_gate":False}
    raw=json.dumps(compact,sort_keys=True,ensure_ascii=False,indent=2).encode("utf8")
    output_path=pathlib.Path(output_path)
    need(not output_path.exists(),"P3_HT_AUDIT_OUTPUT_ALREADY_EXISTS")
    with zipfile.ZipFile(output_path,"w",compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6) as z:
        z.writestr("audit_summary.json",raw)
        z.writestr("exact_user_profile.simc",profile)
        z.writestr("v094_native_observations.json",report_bytes)
        z.writestr("selected_case_input.simc",selected[0])
        z.writestr("selected_case_native.json",selected[1])
    return {"status":compact["status"],"chosen_phase":best["phase"],
            "case_count":len(rows),"audit_archive":output_path.name,
            "audit_zip_sha256":sha(output_path.read_bytes()),
            "selected_case_input_sha256":best["input_sha256"],
            "selected_case_native_sha256":best["native_sha256"],
            "native_calls_added":0,
            "native_summary":selected[2]}
