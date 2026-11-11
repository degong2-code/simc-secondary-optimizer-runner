"""One actually NEW user product profile: four ordinary gems, no old profile.

Source-first: normal v113 LocalJobs zero-history Build -> v216/v212 verified
G/J/F/O -> user v106/v098 -> actual FastAPI v293/v291 -> native SimC JSON2.
Never copy any HAE historic input.simc or preexisting carried DPS results.

Rotating scenario IDs are deliberately user-like and supported. Each new P2
quality campaign selects ONE new profile ID, shared by all policy arms within
that campaign; different campaigns should rotate IDs to prevent overfitting.
"""
from __future__ import annotations
import hashlib
import json
import os
import pathlib
import re
import tempfile
import zipfile

from runner import v106_user_session_controller as users
from runner import v289_retail_live_build_source as retail
from runner import v063_numeric_injection as numeric

SCHEMA="p2_fresh_user_profile_e2e_once_v1"
BINARY_SHA="6b83e4d5d2216faf91511fb00ae712cdf4cc0224b0c83107e8c9c7358c24bfc6"
REVISION="c20e2ad52e4c33711f74272309a5748125175fe8"
BUILD="12.1.5.70783"
CASES={
    "frost_mage_4ordinary_T3300":
        dict(character_class="mage",character_spec="frost",character_race="human",
             target_ilevel=334,final_T=3300,sockets=4,special_gem=None),
    "arms_warrior_4ordinary_T3250":
        dict(character_class="warrior",character_spec="arms",character_race="human",
             target_ilevel=334,final_T=3250,sockets=4,special_gem=None),
    # v319: brand-new user-produced spec, not among v313/v314 10 distinct DPS.
    "windwalker_monk_4ordinary_auto_T":
        dict(character_class="monk",character_spec="windwalker",
             character_race="human",target_ilevel=334,final_T=None,
             sockets=4,special_gem=None),
    # v320: new 26-DPS specialization (not v313/v314/v319).
    "shadow_priest_4ordinary_auto_T":
        dict(character_class="priest",character_spec="shadow",
             character_race="human",target_ilevel=334,final_T=None,
             sockets=4,special_gem=None),
    # v324: independent fresh DPS specialization, not v313/v314/v319/v321.
    "balance_druid_4ordinary_auto_T":
        dict(character_class="druid",character_spec="balance",
             character_race="night_elf",target_ilevel=334,final_T=None,
             sockets=4,special_gem=None),
    # v325: distinct 26-DPS specialization, never before benchmarked here.
    "devastation_evoker_4ordinary_auto_T":
        dict(character_class="evoker",character_spec="devastation",
             character_race="dracthyr",target_ilevel=334,final_T=None,
             sockets=4,special_gem=None),
    # v327 independent new 26-DPS specialist, not historical benchmark.
    "havoc_demonhunter_4ordinary_auto_T":
        dict(character_class="demonhunter",character_spec="havoc",
             character_race="night_elf",target_ilevel=334,final_T=None,
             sockets=4,special_gem=None),
    # v329 genuinely new DPS spec, same P1 season auto G/J/F/O
    "affliction_warlock_4ordinary_auto_T":
        dict(character_class="warlock",character_spec="affliction",
             character_race="human",target_ilevel=334,final_T=None,
             sockets=4,special_gem=None),
    # v330 IDEA-003 independent new Feral DPS specialist
    "feral_druid_4ordinary_auto_T":
        dict(character_class="druid",character_spec="feral",
             character_race="night_elf",target_ilevel=334,final_T=None,
             sockets=4,special_gem=None),
    "destruction_warlock_4ordinary_T3400":
        dict(character_class="warlock",character_spec="destruction",
             character_race="human",target_ilevel=334,final_T=3400,
             sockets=4,special_gem=None),
}
PREVIOUS_PROFILES={("shaman","enhancement",3107,True),
                   ("paladin","retribution",3500,True)}
RECEIPT=pathlib.Path("p2_fresh_user_profile_e2e_receipt.json")


class ProductCaseBlocked(RuntimeError):
    pass


def need(condition,reason):
    if not condition:
        raise ProductCaseBlocked(reason)


def selected_case(case_id):
    need(type(case_id) is str and case_id in CASES,
         "EXPLICIT_DIFFERENT_PROFILE_CASE_REQUIRED")
    item=dict(CASES[case_id])
    need((item["character_class"],item["character_spec"],
          item["final_T"],item["special_gem"] is not None)
         not in PREVIOUS_PROFILES,
         "PAST_PROFILE_CASE_REUSE_PROHIBITED")
    need((item["character_class"],item["character_spec"])
         in users.SUPPORTED,"FRESH_CASE_UNSUPPORTED_DPS_SPEC")
    choice=users.standard_controls(
        (item["character_class"],item["character_spec"]))
    choice["race"]=item["character_race"]
    choice["final_T"]=item["final_T"]
    need(choice["consumable_choices"]["diamond_id"]==0,
         "FRESH_CASE_SPECIAL_GEM_DISABLED")
    return item,choice


def run():
    need(os.getenv("P2_NEW_PRODUCT_PROFILE_ONCE")=="1",
         "EXPLICIT_FRESH_PRODUCT_NATIVE_OPT_IN_REQUIRED")
    case_id=os.getenv("P2_FRESH_PROFILE_CASE","")
    case,controls=selected_case(case_id)
    binary=pathlib.Path("out/binary/simc").resolve(strict=True)
    need(hashlib.sha256(binary.read_bytes()).hexdigest()==BINARY_SHA,
         "FRESH_PRODUCT_SIMC_BINARY_SHA_MISMATCH")
    report=dict(schema=SCHEMA,status="NOT_STARTED",case_id=case_id,
                selected=case,manual_final_T=case["final_T"],
                old_hae_profile_reused=False,
                previous_profile_data_imported=False,
                previous_dps_cache_reused=False,
                source_build_expected=BUILD,
                new_environment_native_calls=0,
                new_product_dps_native_calls=0,
                real_user_windows_click_tested=False,
                global_optimum_proven=False)
    def save():
        RECEIPT.write_text(json.dumps(
            report,sort_keys=True,indent=2,ensure_ascii=False,
            allow_nan=False)+"\n",encoding="utf8")
    save()
    try:
        live=retail.discover(region="KR")
        report["live_game_build"]=live["game_build"]
        need(live["game_build"]==BUILD,
             "CURRENT_RETAIL_BUILD_DIFFERS_FROM_PINNED_SIMC_SOURCE")
        need(all(os.environ.get(x) for x in
                 ("BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
                  "WCL_CLIENT_ID","WCL_CLIENT_SECRET")),
             "LIVE_SEASON_SOURCE_CREDENTIALS_MISSING")
        with tempfile.TemporaryDirectory(prefix="p2-fresh-product-") as temporary:
            root=pathlib.Path(temporary)
            need(not list(root.iterdir()),"FRESH_PRODUCT_WORKSPACE_NOT_EMPTY")
            from runner import v113_local_web_api as web
            jobs=web.LocalJobs(root)
            environment=jobs.build_season_environment(
                game_build=BUILD,
                target_ilevel=case["target_ilevel"],
                auto_initial_core_build=True,
                auto_initial_core_simc_binary=str(binary),
                simc_revision_hint=REVISION,
                existing_special_gem_id=None,
                source_target_socket_count=case["sockets"])
            compiled=environment.get("source_compilation") or {}
            layout=compiled.get("physical_gem_layout_unadmitted") or {}
            report["environment_ready"]=environment.get("environment_ready")
            report["environment_installed"]=environment.get("environment_installed")
            report["environment_budget"]={k:environment.get(k) for k in
                ("G","J","F","O","B","T")}
            report["new_environment_native_calls"]=environment.get("native_calls",0)
            report["physical_layout"]={
                "special_gem_id":layout.get("special_gem_id"),
                "ordinary_gems":layout.get("ordinary_gem_ids"),
                "socket_total":layout.get("socket_total")}
            need(environment.get("environment_ready") is True and
                 environment.get("environment_installed") is True and
                 isinstance(report["new_environment_native_calls"],int)
                 and 0<=report["new_environment_native_calls"]<=3,
                 "FRESH_PRODUCT_ENVIRONMENT_NOT_READY_OR_NATIVE_OVERSPENT")
            need(layout.get("special_gem_id") is None and
                 layout.get("socket_total")==case["sockets"] and
                 len(layout.get("ordinary_gem_ids") or [])==case["sockets"] and
                 len(set(layout["ordinary_gem_ids"]))==case["sockets"],
                 "FRESH_PRODUCT_4_ORDINARY_NO_SPECIAL_LAYOUT_DRIFT")
            need(environment["B"]==environment["G"]+environment["J"]+
                 environment["F"] and environment["T"]==environment["B"] and
                 sum(environment["O"].values())==0,
                 "FRESH_PRODUCT_ORIGINAL_GJFO_ACCOUNTING_DRIFT")
            installed=compiled.get("verified_environment_install") or {}
            need(installed.get("status")==
                 "FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY",
                 "FRESH_PRODUCT_V212_INSTALL_NOT_SEALED")
            report["installed_manifest_sha256"]=installed.get("manifest_sha256")
            save()
            # Product Web API only: v098 builds new class/spec/talents/trinkets,
            # not an altered or copied historical Enhancement .simc file.
            from integration_probes import p3_haj_real_local_web_native_e2e as real_web
            result=real_web.execute(
                root,binary,REVISION,BUILD,environment,
                receipt_file=pathlib.Path(
                    "p2_new_frost_web_receipt.json"),
                manual_final_T=case["final_T"],
                selected_oil_item_ids_by_hand={},
                character_class=case["character_class"],
                character_spec=case["character_spec"],
                character_race=case["character_race"],
                expected_socket_count=case["sockets"])
            report["web_execution_status"]=result["status"]
            report["new_product_dps_native_calls"]=result[
                "new_native_dps_calls"]
            report["product_result"]=result.get("reported")
            report["generated_input_sha256"]=result.get(
                "new_profile_input_sha256")
            report["native_evidence"]=result.get("native_evidence")
            need(result["status"]==
                 "PASS_REAL_FASTAPI_LONGRUN_PREPARE_RUN_RESUME_CACHE" and
                 2<=report["new_product_dps_native_calls"]<=4 and
                 report["product_result"]["final_T"]==case["final_T"],
                 "FRESH_PRODUCT_WEB_NATIVE_RESULT_INVALID")
            with zipfile.ZipFile(
                    "p3_haj_web_native_evidence.zip") as archive:
                names=[x for x in archive.namelist()
                       if x.endswith("/input.simc")]
                need(names,"FRESH_PRODUCT_NATIVE_INPUT_NOT_RETAINED")
                source=archive.read(names[0]).decode("utf8")
                segments=numeric.input_parts(source)
                need(("spec="+case["character_spec"]) in source and
                     re.search(r"(?m)^"+case["character_class"]+
                               r"=",source) is not None,
                     "FRESH_PRODUCT_CHARACTER_NOT_IN_NATIVE_SOURCE")
                # Only a compact source checksum; original exact Native
                # evidence is already in a bounded archive for diagnostics.
                report["new_profile_stable_sha256"]=segments["stable_sha256"]
                report["source_from_product_v098"]=True
            report["status"]="PASS_NEW_SPEC_FOUR_ORDINARY_REAL_PRODUCT_NATIVE"
            save()
            print("P2_FRESH_PRODUCT_REAL_NATIVE_PASS",
                  json.dumps({k:report[k] for k in (
                      "status","case_id","new_environment_native_calls",
                      "new_product_dps_native_calls","environment_budget",
                      "new_profile_stable_sha256","product_result")},
                             sort_keys=True),flush=True)
    except BaseException as error:
        report["status"]="BLOCKED_OR_PARTIAL_"+type(error).__name__
        value=str(error)
        report["first_stable_error_code"]=(
            value if re.fullmatch(r"[A-Z][A-Z0-9_]{3,100}",value)
            else type(error).__name__)
        save()
        raise
    return report


if __name__=="__main__":
    run()
