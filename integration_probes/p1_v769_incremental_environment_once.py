#!/usr/bin/env python3
"""One actual v113 same-season target-level increment, no DPS or SimC rebuild.

Use the existing source-bound CLI cache, one contiguous session root and
ordinary automatic Build. Earlier real Windows receipt is not a raw workspace.
Only bounded non-secret receipts leave the runner.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from p1_v524_m1_m2_source_owner_once import (
    EphemeralActionsCredentials, bounded_code, digest)
import v113_local_web_api as web
import v216_environment_build_coordinator as engine
import v289_retail_live_build_source as retail

BUILD="12.1.5.70961"
REV="9933ffb946fb55b1fa66657b848f519ac19006e1"

def need(ok,code):
    if not ok:
        raise RuntimeError(code)

# v772: retain the existing J/F producer's decision evidence on failure.
# No new source lookup, Native invocation, admission check or raw profile dump.
def _diagnostic_fields(row):
    if not isinstance(row,dict):
        return None
    keys=("status","reason","tier_source_status","requires","missing",
          "new_native_calls","candidate_count","sample_count",
          "selected_tier_candidate_count","selected_exact_item_id",
          "selected_source_token","selected_source_quality",
          "selected_physical_items_unadmitted","attempted","remaining",
          "all_source_candidate_count","physical_item_id",
          "ordinary_gem_id","failed_variant","native_status","native_returncode",
          "F_candidate_unadmitted","J_candidate_unadmitted",
          "simc_effective_two_stat_vector_unadmitted",
          "simc_unbuffed_gear_two_stat_vector_unadmitted",
          "simc_unbuffed_gear_rating_source","static_CHMV_candidate")
    out={key:row[key] for key in keys if key in row}
    if row.get("native_error"):
        out["native_error_code"]=bounded_code(row["native_error"])
    return out

def _jf_failure_details(progress,compiler):
    keys=("ordinary_gem_v221_v230_source_candidates_unadmitted",
          "four_stat_pinned_dbc_j_source_unadmitted",
          "four_stat_simc_native_j_source_unadmitted",
          "automatic_default_F_source_selection_unadmitted",
          "automatic_F_native_measurements_unadmitted",
          "selected_J_F_source_owner_numeric_unadmitted",
          "selected_J_F_source_owner_quality_unadmitted",
          "selected_auto_v222_numeric_preview_unadmitted",
          "selected_physical_F_O_budget_link_unadmitted")
    out={}
    for key in keys:
        row=compiler.get(key)
        if not isinstance(row,dict):
            row=progress.get(key)
        if not isinstance(row,dict):
            continue
        detail=_diagnostic_fields(row)
        for field in ("per_item","native_observations_unadmitted"):
            entries=row.get(field)
            if isinstance(entries,list):
                detail[field]=[_diagnostic_fields(entry)
                               for entry in entries[:24]]
        if key.startswith("selected_J_F_source_owner_"):
            for component in ("J","F"):
                item=row.get(component)
                detail[component]=(None if not isinstance(item,dict) else
                    {k:item[k] for k in ("rating","physical_item_id",
                       "ordinary_gem_item_ids","crafting_quality",
                       "simc_input_token","static_CHMV_vector",
                       "numeric_source_owner","status","reason")
                     if k in item})
        out[key]=detail
    out["original_J_F_verified_component_names"]=progress.get(
        "original_J_F_verified_component_names")
    return out

def summary(r):
    progress=r.get("zero_history_build") or {}
    compiler=r.get("source_compilation") or {}
    raw=r.get("source_stage") or {}
    full=r.get("fresh_lazy_full_pinned_simc_item_source") or {}
    return {
        "environment_ready":r.get("environment_ready"),
        "environment_installed":r.get("environment_installed"),
        "native_calls":r.get("native_calls"),
        "budget":{k:r.get(k) for k in ("G","J","F","O","B","T")},
        "source_stage_status":raw.get("status"),
        "source_stage_receipt_sha256":raw.get("receipt_sha256"),
        "same_build_cache_reuse":progress.get("same_build_cache_reuse"),
        "full_item_source_receipt_sha256":full.get("receipt_sha256"),
        "full_item_source_network_calls":full.get("network_calls_by_stage"),
        "compiler_status":compiler.get("status"),
        "catalog_receipt_sha256":(compiler.get("v213_stage") or {}).get("receipt_sha256"),
        "installed_manifest_sha256":(compiler.get("verified_environment_install") or {}).get("manifest_sha256",r.get("installed_manifest_sha256")),
        "requires":list(progress.get("requires") or [])[:40],
        **({"jf_failure_details":_jf_failure_details(progress,compiler)}
           if r.get("environment_ready") is not True else {}),
        "dps_optimization_started":(r.get("web_environment_scope") or {}).get("dps_optimization_started"),
    }

def verify_ready(r):
    need(r.get("environment_ready") is True and
         r.get("environment_installed") is True,"V769_ENVIRONMENT_NOT_READY")
    need(r["B"]==r["G"]+r["J"]+r["F"] and
         r["T"]==r["B"]+sum(r["O"].values()) and
         not any(r["O"].values()),"V769_GJFO_ACCOUNTING_DRIFT")
    need(type(r.get("native_calls")) is int and r["native_calls"]>=0,
         "V769_NATIVE_COUNT_MISSING")
    need((r.get("web_environment_scope") or {}).get(
        "dps_optimization_started") is False,"V769_UNEXPECTED_DPS")

def run(args):
    out=Path(args.out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    dest=out/"V769_INCREMENTAL_ENVIRONMENT.json"
    doc={"schema":"p1_v769_real_same_season_incremental_environment_v1",
         "status":"STARTED","game_build":BUILD,"revision":REV,
         "baseline_target":334,"increment_target":330,
         "new_user_dps_native_calls":0,"prior_package_upgrade_tested":False,
         "full_product_e2e":"PENDING"}
    def save():
        dest.write_text(json.dumps(doc,sort_keys=True,indent=2,
                                   ensure_ascii=False)+"\n",encoding="utf8")
        print("V769_RECEIPT "+json.dumps(doc,sort_keys=True),flush=True)
    try:
        binary=Path(args.simc).resolve()
        meta=Path(args.identity).resolve()
        if not binary.is_file() or not meta.is_file():
            doc["status"]="PENDING_EXISTING_SOURCE_BOUND_BINARY_CACHE_MISSING"
            return 2
        identity=json.loads(meta.read_text(encoding="utf-8-sig"))
        need(identity["game_build"]==BUILD and identity["source_commit"]==REV
             and identity["binary_sha256"]==digest(binary),
             "V769_EXISTING_BINARY_IDENTITY_DRIFT")
        doc["binary_sha256"]=identity["binary_sha256"]
        live=retail.discover(region="KR")
        doc["observed_live_build"]=live["game_build"]
        if live["game_build"]!=BUILD:
            doc["status"]="PENDING_LIVE_BUILD_CHANGED"
            return 2
        need(EphemeralActionsCredentials().load() is not None,
             "V769_SOURCE_CREDENTIALS_MISSING")
        banner=subprocess.run([str(binary)],input="",capture_output=True,
                    text=True,errors="replace",cwd=binary.parent,timeout=25)
        need(banner.returncode==0 and BUILD in (banner.stdout+banner.stderr),
             "V769_SIMC_BANNER_BUILD_DRIFT")
        with tempfile.TemporaryDirectory(prefix="v769-") as temp:
            root=Path(temp)/"runs"
            root.mkdir()
            credentials=EphemeralActionsCredentials()
            jobs=web.LocalJobs(root,source_credential_store=credentials)
            base=dict(game_build=BUILD,auto_initial_core_build=True,
                      auto_initial_core_simc_binary=str(binary),
                      simc_revision_hint=REV,existing_special_gem_id=None,
                      source_target_socket_count=4)
            doc["stage"]="BASELINE"
            save()
            first=jobs.build_season_environment(target_ilevel=334,**base)
            doc["baseline"]=summary(first)
            save()
            verify_ready(first)
            first_sha=doc["baseline"]["installed_manifest_sha256"]
            need(isinstance(first_sha,str) and len(first_sha)==64,
                 "V769_BASELINE_INSTALL_SHA_MISSING")
            docs=root/"_fresh_season_sources"/("wago_"+BUILD)/"fresh_source"
            original=docs/("v212_installed_"+first_sha[:20]+".json")
            original_sha=digest(original)
            # A new LocalJobs instance tests on-disk reuse after server restart;
            # no synthetic source injection or reuse of first in-memory result.
            jobs=web.LocalJobs(root,source_credential_store=credentials)
            doc["stage"]="INCREMENT"
            save()
            second=jobs.build_season_environment(target_ilevel=330,**base)
            doc["increment"]=summary(second)
            save()
            verify_ready(second)
            need(doc["increment"]["same_build_cache_reuse"] is True and
                 doc["increment"]["source_stage_receipt_sha256"]==
                 doc["baseline"]["source_stage_receipt_sha256"],
                 "V769_ORIGINAL_WAGO_STAGE_NOT_REUSED")
            need(doc["increment"]["full_item_source_network_calls"]==0 and
                 doc["increment"]["full_item_source_receipt_sha256"]==
                 doc["baseline"]["full_item_source_receipt_sha256"],
                 "V769_ORIGINAL_SIMC_ITEM_SOURCE_NOT_REUSED")
            need(doc["increment"]["catalog_receipt_sha256"]==
                 doc["baseline"]["catalog_receipt_sha256"],
                 "V769_FIXED_CATALOG_NOT_REUSED")
            need(digest(original)==original_sha,
                 "V769_ORIGINAL_INSTALL_MODIFIED")
            for level,sha in ((334,first_sha),(330,doc["increment"]["installed_manifest_sha256"])):
                need(isinstance(sha,str) and len(sha)==64,
                     "V769_INSTALL_SHA_MISSING")
                need(engine.find_verified_installed_season_environment(
                         root,level,expected_game_build=BUILD,
                         expected_installed_manifest_sha256=sha) is not None,
                     "V769_EXACT_INSTALL_NOT_RESTORABLE")
                need(jobs.restore_verified_fresh_profile(
                         target_ilevel=level,game_build=BUILD,
                         expected_installed_manifest_sha256=sha) is not None,
                     "V769_EXACT_PROFILE_NOT_RESTORABLE")
            doc["stage"]="REOPEN"
            repeat=jobs.build_season_environment(target_ilevel=330,**base)
            doc["reopen"]=summary(repeat)
            need(repeat.get("native_calls")==0 and
                 repeat["web_environment_scope"].get(
                     "reused_verified_installed_season") is True and
                 repeat["T"]==second["T"],
                 "V769_INCREMENT_REOPEN_NOT_ZERO_NATIVE")
            doc["status"]="PASS_REAL_SAME_SEASON_TARGET_INCREMENT_AND_REOPEN"
            return 0
    except Exception as exc:
        doc["status"]="BLOCKED_ORIGINAL_PRODUCT_PATH"
        doc["first_blocker"]=bounded_code(exc)
        return 2
    finally:
        save()

def observe_simc_defaults(args):
    """One profile-generation process; never enter the optimizer or Build.

    Read only the exact default food/potion emitted by SimC. Generated
    character profiles are ephemeral, not representative equipment inputs.
    """
    import re
    import v106_user_session_controller as sessions
    out=Path(args.out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    dest=out/"V784_SIMC_DEFAULTS.json"
    doc={"schema":"p1_v784_simc_native_profile_defaults_v1",
         "game_build":BUILD,"simc_revision":REV,"character_level":90,
         "status":"STARTED","profile_generation_processes":0,
         "environment_builds":0,"dps_simulations":0,
         "actual_installed_environment_verified":False}
    try:
        binary=Path(args.simc).resolve()
        identity_path=Path(args.identity).resolve()
        if not binary.is_file() or not identity_path.is_file():
            doc["status"]="PENDING_EXISTING_SOURCE_BOUND_BINARY_CACHE_MISSING"
            return 2
        identity=json.loads(identity_path.read_text(encoding="utf-8-sig"))
        need(identity["game_build"]==BUILD and identity["source_commit"]==REV
             and identity["binary_sha256"]==digest(binary),
             "V784_EXISTING_BINARY_IDENTITY_DRIFT")
        doc["binary_sha256"]=identity["binary_sha256"]
        roster=sorted(sessions.SUPPORTED)
        need(len(roster)==26,"V784_DPS_ROSTER_DRIFT")
        with tempfile.TemporaryDirectory(prefix="v784-") as td:
            root=Path(td)
            lines=["save_profiles=1","save_profile_with_actions=0",
                   "offline=1","threads=1"]
            files={}
            for n,(cls,spec) in enumerate(roster):
                controls=sessions.standard_controls((cls,spec))
                actor="defaults_"+str(n)
                file=actor+".simc"
                files[cls+"/"+spec]=(file,spec)
                lines.extend([cls+"="+actor,"spec="+spec,"level=90",
                              "race="+controls["race"],"load_default_talents=1",
                              "flask=disabled","augmentation=disabled",
                              "temporary_enchant=disabled","save="+file])
            input_path=root/"defaults_input.simc"
            input_path.write_text("\n".join(lines)+"\n",encoding="utf8")
            doc["profile_generation_processes"]=1
            process=subprocess.run([str(binary),input_path.name],cwd=root,
                capture_output=True,text=True,errors="replace",timeout=120)
            output=process.stdout+"\n"+process.stderr
            doc["returncode"]=process.returncode
            doc["generation_branch_observed"]="Generating profiles" in output
            doc["simulation_branch_observed"]="Simulating..." in output
            if doc["simulation_branch_observed"]:
                doc["dps_simulations"]=None
                raise RuntimeError("V784_UNEXPECTED_SIMULATION_BRANCH")
            doc["generated_profile_count"]=sum((root/f).is_file()
                                                for f,_ in files.values())
            doc["diagnostic_tail"]=output[-1800:]
            observed={}
            missing=[]
            for key,(file,spec) in files.items():
                path=root/file
                if not path.is_file() or path.stat().st_size>500_000:
                    missing.append(key)
                    continue
                values={}
                for line in path.read_text(encoding="utf8").splitlines():
                    if "=" not in line or line.startswith("#"):
                        continue
                    name,value=line.split("=",1)
                    if name in ("spec","level","food","potion"):
                        if name in values:
                            raise RuntimeError("V784_DUPLICATE_PROFILE_FIELD")
                        values[name]=value.strip()
                if (values.get("spec")!=spec or values.get("level")!="90" or
                        not all(re.fullmatch(r"[a-z0-9_]{1,100}",values.get(k,""))
                                for k in ("food","potion"))):
                    missing.append(key)
                    continue
                observed[key]={k:values[k] for k in ("food","potion")}
            doc["observed_defaults"]=observed
            doc["missing_specs"]=missing
            expected={}
            for kind,tokens in engine.optional_source_join.reviewed_apl_default_groups(BUILD,REV).items():
                for token,specs in tokens.items():
                    for spec in specs.split():
                        expected.setdefault(spec,{})[kind]=token
            doc["mismatches_against_reviewed_snapshot"]={
                key:{"observed":observed.get(key),"reviewed":expected.get(key)}
                for key in sorted(set(observed)|set(expected))
                if observed.get(key)!=expected.get(key)}
            need(process.returncode==0 and doc["generation_branch_observed"]
                 and not missing and len(observed)==26,
                 "V784_PROFILE_GENERATION_INCOMPLETE")
            doc["status"]="PASS_REAL_SIMC_PROFILE_DEFAULT_EXTRACTION"
            return 0
    except Exception as exc:
        doc["status"]="BLOCKED_PROFILE_DEFAULT_EXTRACTION"
        doc["first_blocker"]=bounded_code(exc)
        return 2
    finally:
        dest.write_text(json.dumps(doc,ensure_ascii=False,sort_keys=True,
                                   indent=2)+"\n",encoding="utf8")
        print("V784_DEFAULTS "+json.dumps(doc,sort_keys=True),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--simc",required=True)
    p.add_argument("--identity",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--defaults-only",action="store_true")
    args=p.parse_args()
    sys.exit(observe_simc_defaults(args) if args.defaults_only else run(args))
