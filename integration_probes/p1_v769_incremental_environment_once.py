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
        "requires":list(progress.get("requires") or [])[:12],
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

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--simc",required=True)
    p.add_argument("--identity",required=True)
    p.add_argument("--out",required=True)
    sys.exit(run(p.parse_args()))
