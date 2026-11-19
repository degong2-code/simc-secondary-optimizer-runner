#!/usr/bin/env python3
"""v619 real single user-selected v212 E0 enchant → original adaptive SimC.

All execution paths are existing v113→v216/v217/v212→v106→v098→v096→v094.
One real 70961 source workspace, same source-bound Windows CLI cache,
exactly one actual source-verified physical enchant selected, and one
existing bounded adaptive solver. No effect/proc/grade performance Gate.
This is an internal user scenario, not proof that web UI has a picker yet.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
import p1_v610_real_installed_enchant_one_build as actual
import v098_target_user_scenario_bootstrap as user_profile
import v106_user_session_controller as sessions
import v096_unified_product_entry as runtime
import v212_environment_manifest as installed

BUILD="12.1.5.70961"
REV="9933ffb946fb55b1fa66657b848f519ac19006e1"
SCHEMA="p1_v619_real_70961_exact_user_installed_E0_native_once_v1"
ENCHANT_ID=7957
SLOT="chest"
TOKEN="enchant_chest__mark_of_nalorakk"


def digest(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()


def followup(*,jobs,environment_result,document,installed_path,binary,
             revision,output_folder):
    destination=pathlib.Path(output_folder)/"V619_REAL_USER_ENCHANT_DPS.json"
    report={"schema":SCHEMA,"status":"STARTED",
            "game_build":BUILD,"simc_revision":revision,
            "simc_binary_sha256":digest(binary),
            "actual_source_catalog_verification_reused":True,
            "user_supplied_full_gear":False,
            "chosen_user_character":{"class":"paladin","spec":"retribution"},
            "target_ilevel":334,"chosen_enchant_id":ENCHANT_ID,
            "chosen_slot":SLOT,"effect_proc_dps_owner":"SimC",
            "internal_user_scenario_not_web_picker":True,
            "new_native_optimizer":False,"global_optimum_proven":False}
    def save():
        destination.write_text(json.dumps(report,ensure_ascii=False,
            sort_keys=True,indent=2,default=str,allow_nan=False)+"\n",
            encoding="utf8")
    save()
    try:
        installed.verify_fresh_installed_environment(document)
        chosen=[row for row in document["published_verified_options"]
                if row.get("enchant_id")==ENCHANT_ID
                and row.get("slot")==SLOT
                and row.get("simc_token")==TOKEN]
        if len(chosen)!=1 or chosen[0].get("verified_fixed_E")!={
                stat:0 for stat in ("crit_rating","haste_rating",
                                    "mastery_rating","versatility_rating")}:
            report["status"]="PENDING_ORIGINAL_USER_ENCHANT_CHOICE_NOT_PUBLISHED"
            save()
            return report
        report["installed_v212_sha256"]=document["manifest_sha256"]
        report["original_v212_published_count"]=len(
            document["published_verified_options"])
        report["official_budget"]={k:document["official_"+k]
            for k in ("G","J","F","B","T")}
        report["original_gear_enchant_source"]=chosen[0]["exact_v220_identity"]
        controls=sessions.standard_controls(("paladin","retribution"))
        controls["oil_hands"]=[]
        controls["enchant_choices"]={SLOT:ENCHANT_ID}
        user=sessions.user_scenario(controls)
        folder=pathlib.Path(output_folder)/"v619-user-session"
        folder.mkdir(parents=True,exist_ok=True)
        report["status"]="ORIGINAL_USER_INPUT_ACCEPTED"
        save()
        result=user_profile.preview_from_environment_build(
            user,folder,binary,revision,
            environment_result=environment_result)
        report["v098_status"]=result.get("status")
        report["v098_first_missing"]=list(result.get("missing") or [])[:10]
        report["v098_fresh_installed_v212_source_reused"]=result.get(
            "fresh_installed_v212_source_reused")
        if result.get("status")!=(
                "READY_SOURCE_BOUND_SEASON_MANIFEST_ZERO_NATIVE"):
            report["status"]="PENDING_ORIGINAL_USER_PROFILE_SCOPE"
            report["first_blocker"]=result.get("status")
            save()
            return report
        manifest=pathlib.Path(result["generated_manifest"]).resolve()
        if manifest!=folder.resolve()/"manifest.json":
            raise RuntimeError("V619_ORIGINAL_USER_MANIFEST_PATH_DRIFT")
        profile=(folder/"profile.simc").read_text(encoding="utf8")
        eid="enchant_id="+str(ENCHANT_ID)
        matched=[l for l in profile.splitlines() if l.startswith(SLOT+"=")]
        if len(matched)!=1 or matched[0].count(eid)!=1 or sum(
                line.split(",").count(eid) for line in profile.splitlines())!=1:
            raise RuntimeError("V619_EXACT_USER_ENCHANT_PROFILE_NOT_ONCE")
        report["original_profile_sha256"]=hashlib.sha256(
            profile.encode("utf8")).hexdigest()
        report["selected_user_item_line_sha256"]=hashlib.sha256(
            matched[0].encode("utf8")).hexdigest()
        report["real_item_id"]=next(
            int(value.split("=",1)[1]) for value in
            matched[0].split("=",1)[1].split(",")
            if value.startswith("id="))
        report["v096_budget_source"]=result["plan"].get("budget_source")
        report["v096_plan_base_B"]=result["plan"].get("base_B")
        report["v096_plan_final_T"]=result["plan"].get("final_T")
        report["v096_selected_E0_identity_present"]=(
            bool(result["plan"].get("selected_user_installed_E0"))
            or bool(result["plan"].get("season_source_identity")))
        if (report["v096_plan_base_B"]!=document["official_B"] or
                report["v096_plan_final_T"]!=document["official_T"]):
            raise RuntimeError("V619_USER_TARGET_B_T_INSTALLED_DRIFT")
        report["status"]="PASS_ORIGINAL_USER_PROFILE_NATIVE_NOT_YET"
        save()
        native=runtime.run_manifest(manifest,open_folder=False)
        report["original_v096_run_status"]=native.get("status")
        report["new_dps_native_calls"]=native.get("native_calls_cumulative")
        report["verified_dps_cache_hits"]=native.get("cache_hits_this_run")
        report["result_path_recorded"]=pathlib.Path(
            native.get("result_path","")).name
        observed=native.get("user_result") or {}
        report["actual_user_result"]=observed
        report["native_result_recorded"]=bool(observed)
        report["global_optimum_proven"]=False
        if (native.get("base_B")==document["official_B"]
            and native.get("final_T")==document["official_T"]
            and native.get("budget_source")==(
                "ADMITTED_FRESH_SEASON_GJFO_V212_V217")
            and type(native.get("native_calls_cumulative")) is int
            and native["native_calls_cumulative"]>=1
            and bool(observed)):
            report["status"]="PASS_ORIGINAL_V098_V096_ENCHANT_NATIVE_DPS"
        else:
            report["status"]="PENDING_ORIGINAL_USER_NATIVE_RESULTS"
            report["first_blocker"]=native.get("status")
        save()
        return report
    except Exception as exc:
        report["status"]="BLOCKED_"+type(exc).__name__
        # Safely classify; raw SimC failure text stays within logs, not in a
        # public artifact containing local paths/credentials.
        report["first_blocker"]=actual.bounded_code(exc)
        save()
        return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--simc",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--source-commit-file",required=True)
    args=p.parse_args()
    rev=pathlib.Path(args.source_commit_file).read_text("utf8").strip()
    if rev!=REV:
        raise SystemExit("V619_ORIGINAL_GIT_COMMIT_MISMATCH")
    binary=pathlib.Path(args.simc).resolve(strict=True)
    if binary.name.lower()!="simc.exe":
        raise SystemExit("V619_SOURCE_BOUND_CLI_REQUIRED")
    actual.BUILD=BUILD
    actual.REV=REV
    actual.EXE_SHA=digest(binary)
    actual.SCHEMA=SCHEMA
    return actual.run(binary,args.out,postinstall=followup)


if __name__=="__main__":
    sys.exit(main())
