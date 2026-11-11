#!/usr/bin/env python3
"""v337: REAL installed-state cold-start and official ko localization once.

Immutable, vetted same-build source/77 item labels/64 playable terms remain
available. NO preinstalled season G/J/F/O, receipts, sessions, or local name
caches. Different future-season readiness is not claimed.
"""
import json
import os
import pathlib
import sys
import tempfile
from runner import v113_local_web_api as web
from runner import v216_environment_build_coordinator as core
from runner import v289_retail_live_build_source as retail
from runner import v335_environment_official_ko_localization as names
from runner import v336_environment_ko_playable_terms as terms

BUILD="12.1.5.70783"
REV="c20e2ad52e4c33711f74272309a5748125175fe8"
DEST=pathlib.Path("p1_v337_zero_history_environment_locale_receipt.json")
def must(ok,msg):
    if not ok: raise RuntimeError("V337_"+msg)

def summary(r):
    ko=r.get("official_ko_localization") or {}
    terms_ko=r.get("official_ko_terms") or {}
    scope=r.get("web_environment_scope") or {}
    return dict(
        environment_ready=r.get("environment_ready"),
        environment_installed=r.get("environment_installed"),
        native_calls=r.get("native_calls"),
        source_reused=scope.get("reused_verified_installed_season"),
        budget={k:r.get(k) for k in ("G","J","F","O","B","T")},
        ko_items={k:ko.get(k) for k in ("status","selected_item_count",
              "verified_names","pending_names","network_calls_now",
              "new_official_name_records","existing_same_build_name_records_reused")},
        ko_terms={k:terms_ko.get(k) for k in ("status","verified_count",
              "missing_count","network_calls_now","reused_same_build_cache")})

def run():
    result={"schema":"v337_real_empty_installed_environment_with_official_ko_v1",
            "status":"NOT_RUN","future_season_proven":False,
            "historical_packaged_same_build_locale_seed_allowed":True,
            "new_user_dps_native_calls":0,"max_new_environment_native_calls":3}
    live=retail.discover(region="KR")
    build=live["game_build"]
    result["observed_retail_KR_build"]=build
    if build!=BUILD:
        result["status"]="BLOCKED_LIVE_BUILD_DIFFERENT_FROM_PINNED_BINARY"
        return result
    if any(not os.getenv(k) for k in
           ("BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
            "WCL_CLIENT_ID","WCL_CLIENT_SECRET")):
        result["status"]="BLOCKED_MISSING_SOURCE_CREDENTIALS"
        return result
    binary=pathlib.Path("out/binary/simc").resolve()
    must(binary.is_file() and not binary.is_symlink(),"BINARY_NOT_EXACT_FILE")
    with tempfile.TemporaryDirectory(prefix="v337-original-empty-") as dir:
        root=pathlib.Path(dir)
        must(not list(root.iterdir()),"ROOT_NOT_EMPTY")
        must(core.find_verified_installed_season_environment(
            root,334,expected_game_build=build) is None,
            "PREINSTALLED_NUMERIC_RECEIPT")
        must(not names._path(root,build).exists() and
             not terms.path_for(root,build).exists(),
             "PREINSTALLED_LOCAL_KOREAN_NAMES")
        result["fresh_root_confirmed"]=True
        job=web.LocalJobs(root)
        args=dict(game_build=build,target_ilevel=334,
              auto_initial_core_build=True,
              auto_initial_core_simc_binary=str(binary),
              simc_revision_hint=REV,existing_special_gem_id=None,
              source_target_socket_count=4)
        one=job.build_season_environment(**args)
        result["first"]=summary(one)
        must(one.get("environment_ready") is True and
             one.get("environment_installed") is True,
             "NUMERIC_INSTALL_NOT_READY")
        must(type(one.get("native_calls")) is int and
             0<=one["native_calls"]<=3,
             "FIRST_ENVIRONMENT_NATIVE_OVER_3")
        must(one["B"]==one["G"]+one["J"]+one["F"] and
             one["T"]==one["B"]+sum(one["O"].values()),
             "GJFO_BUDGET_INCONSISTENT")
        layout=(one.get("source_compilation") or {}).get(
            "physical_gem_layout_unadmitted") or {}
        must(layout.get("socket_total")==4 and
             layout.get("special_gem_id") is None and
             len(layout.get("ordinary_gem_ids") or [])==4,
             "FOUR_ORDINARY_GEM_LAYOUT_DRIFT")
        must(job.load_fresh_profile_for_user(
             334,explicit_build=build) is not None,
             "VERIFIED_SOURCE_USER_PROFILE_MISSING")
        result["first_user_profile_ready"]=True
        ko=one.get("official_ko_localization") or {}
        term=one.get("official_ko_terms") or {}
        must(ko.get("status") in (names.STATUS_READY,names.STATUS_PARTIAL),
             "V335_FIRST_ENVIRONMENT_LOCALIZATION_NOT_CONNECTED")
        must(type(ko.get("selected_item_count")) is int and
             ko["selected_item_count"]>0 and ko.get("verified_names",0)>0,
             "V335_NO_VERIFIED_SOURCE_BOUND_ITEM_LABEL")
        must(term.get("status")=="COMPLETE" and
             term.get("verified_count")==64 and
             term.get("network_calls_now")==0,
             "V336_PACKAGED_SIGNED_SAME_BUILD_TERMS_NOT_REUSED")
        must(names.cache_status(root,build)["status"]==
             "READ_ONLY_VERIFIED_OFFICIAL_NAMES",
             "V335_FIRST_CACHE_NOT_PERSISTED")
        result["first_environment_with_localization_ready"]=True
        two=job.build_season_environment(**args)
        result["second"]=summary(two)
        must(two.get("environment_ready") is True and
             two.get("environment_installed") is True and
             two.get("native_calls")==0,
             "SECOND_BUILD_NOT_ZERO_NATIVE_REUSE")
        must(two.get("web_environment_scope",{}).get(
              "reused_verified_installed_season") is True,
             "SECOND_BUILD_RECOLLECTED_VERIFIED_SOURCE")
        must(all(two.get(k)==one.get(k) for k in
                 ("G","J","F","O","B","T")),
             "SECOND_BUILD_BUDGET_CHANGED")
        second_names=two.get("official_ko_localization") or {}
        second_terms=two.get("official_ko_terms") or {}
        must(second_names.get("network_calls_now")==0 and
             second_names.get("new_official_name_records")==0 and
             second_terms.get("network_calls_now")==0,
             "SECOND_BUILD_DUPLICATE_OFFICIAL_API")
        must(second_names.get("selected_item_count")==
             ko.get("selected_item_count") and
             second_names.get("verified_names")==ko.get("verified_names") and
             second_names.get("pending_names")==ko.get("pending_names"),
             "SECOND_BUILD_LOCALE_WORKLIST_SHRANK")
        result["second_zero_native_and_zero_locale_network"]=True
        result["second_worklist_exactly_retained"]=True

        # Different future-season build ID cannot inherit the known 70783
        # localization. Never construct a fake READY season to pass this.
        unknown="12.1.5.99999"
        must(names.read_names(root,unknown,{158367})=={} and
             terms.public(root,unknown)["status"]==
             "NO_VERIFIED_OFFICIAL_TERMS",
             "UNKNOWN_BUILD_FALSLY_INHERITED_KOREAN_LABELS")
        result["foreign_build_does_not_reuse_old_names"]=True

        cache=names._path(root,build)
        saved=cache.read_bytes()
        try:
            cache.write_bytes(saved+b"tamper")
            must(names.read_names(root,build,{158367})=={},
                 "TAMPERED_LABEL_CACHE_ACCEPTED")
        finally:
            cache.write_bytes(saved)
        must(core.find_verified_installed_season_environment(
             root,334,expected_game_build=build) is not None,
             "OPTIONAL_LABEL_TAMPER_REVOKED_NUMERIC_ENVIRONMENT")
        result["tampered_label_fails_closed_without_numeric_damage"]=True
        result["status"]="PASS_REAL_INSTALLED_STATE_COLD_START_AND_REUSE"
    return result

def main():
    receipt={"schema":"v337_real_empty_installed_environment_with_official_ko_v1",
             "status":"NOT_RUN"}
    try:
        receipt=run()
    except Exception as exc:
        receipt.update(status="BLOCKED_REAL_EXPERIMENT",
                       error_type=type(exc).__name__,
                       error_code=str(exc).split(":",1)[0][:180])
    DEST.write_text(json.dumps(receipt,indent=2,ensure_ascii=False,
                  sort_keys=True)+"\n",encoding="utf8")
    print("V337_REAL_COLD_START_RECEIPT "+
          json.dumps(receipt,ensure_ascii=False,sort_keys=True),flush=True)
    return 0 if receipt["status"]=="PASS_REAL_INSTALLED_STATE_COLD_START_AND_REUSE" else 1

if __name__=="__main__":
    sys.exit(main())
