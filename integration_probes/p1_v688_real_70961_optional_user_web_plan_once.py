#!/usr/bin/env python3
"""One original 70961 build -> v212 option -> actual v113 HTTP -> SimC profile.

No old installed file injected. Reuses v610 original source-owned GJFO/Policy A
Build and cached same-source Windows SimC binary. No user Native / DPS.
The Build's original, bounded G/J/F/E Native probes remain independently owned.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
import p1_v610_real_installed_enchant_one_build as original
import v113_local_web_api as web
import v106_user_session_controller as sessions
import v212_environment_manifest as installed
from fastapi.testclient import TestClient

BUILD="12.1.5.70961"
REV="9933ffb946fb55b1fa66657b848f519ac19006e1"
SCHEMA="p1_v688_real_same_build_optional_install_web_plan_profile_v1"


def digest(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()


def followup(*,jobs,environment_result,document,installed_path,binary,
             revision,output_folder):
    out=pathlib.Path(output_folder)/"V688_REAL_OPTIONAL_USER_STAGE.json"
    result={"schema":SCHEMA,"status":"STARTED","game_build":BUILD,
            "simc_revision":revision,"real_original_v216_v212_build":True,
            "historical_installed_document_injected":False,
            "new_dps_native_calls":0,"user_optimizer_executed":False,
            "native_simc_consumable_parser_accepted":False,
            "all_quality_numeric_noninferiority_proven":False,
            "full_product_e2e":"PENDING"}
    def save():
        out.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,
                                  indent=2,allow_nan=False)+"\n","utf8")
    save()
    try:
        installed.verify_fresh_installed_environment(document)
        original_install=environment_result["source_compilation"][
            "verified_environment_install"]
        if (document["game_build"]!=BUILD or
            document["simc_revision"]!=revision or
            document["manifest_sha256"]!=original_install["manifest_sha256"] or
            pathlib.Path(installed_path).resolve()!=pathlib.Path(
                original_install["stage_output_path"]).resolve()):
            raise RuntimeError("V688_EXACT_ORIGINAL_V212_INSTALL_IDENTITY_DRIFT")
        optional=document.get("installed_optional_consumables")
        if not isinstance(optional,dict):
            result["status"]="PENDING_REAL_OPTIONAL_NOT_IN_V212_INSTALL"
            save()
            return result
        foods=optional["categories"]["food"]["options"]
        potions=optional["categories"]["potion"]["options"]
        result["source_owned_installed_food_count"]=len(foods)
        result["source_owned_installed_potion_count"]=len(potions)
        result["installed_manifest_sha256"]=document["manifest_sha256"]
        result["installed_B"]=document["official_B"]
        result["installed_T"]=document["official_T"]
        if not foods:
            result["status"]="PENDING_INSTALLED_FOOD_OPTIONS_EMPTY"
            save()
            return result
        # Prefer the actual v684 same-revision physical source sample if
        # that candidate is installed; never invent or add a missing row.
        food=next((row for row in foods if row["item_id"]==242273),foods[0])
        token=food["simc_token"]
        result["selected_food_item_id"]=food["item_id"]
        result["selected_food_simc_token"]=token
        result["selected_food_source_quality_rank"]=food["quality"]
        app=web.create_app(root=jobs.root,token="v688-actual-local-once")
        headers={"x-simc-local-token":"v688-actual-local-once",
                 "origin":"http://127.0.0.1:8765"}
        with TestClient(app,base_url="http://127.0.0.1:8765") as client:
            query={"game_build":BUILD,"target_ilevel":334,
                   "installed_manifest_sha256":document["manifest_sha256"]}
            res=client.get("/api/v1/season-option-catalog",
                           params=query,headers=headers)
            result["real_v113_exact_catalog_http"]=res.status_code
            if res.status_code!=200:
                result["status"]="PENDING_REAL_V113_EXACT_CATALOG_HTTP"
                result["first_blocker"]="CATALOG_HTTP_"+str(res.status_code)
                save()
                return result
            published=res.json()
            choices=published.get("installed_optional_consumable_choices",{})
            matched=[row for row in choices.get("items",[])
                     if row.get("kind")=="food" and
                        row.get("item_id")==food["item_id"] and
                        row.get("simc_token")==token]
            if (published.get("source_scope")!=
                    "VERIFIED_INSTALLED_V212_OPTION_CATALOG" or
                choices.get("installed_manifest_sha256")!=
                    document["manifest_sha256"] or
                token not in choices.get("food",[]) or len(matched)!=1):
                raise RuntimeError("V688_INSTALLED_OPTION_NOT_IN_EXACT_V113_MENU")
            result["same_v212_sha_used_by_ui"]=True
            controls=sessions.standard_controls(("paladin","retribution"))
            controls["oil_hands"]=[]
            controls["consumable_choices"]={
                **controls["consumable_choices"],"food":token}
            request={"controls":controls,"binary":str(binary),
                     "revision":revision,"current_season_product":True,
                     "installed_season_game_build":BUILD,
                     "installed_manifest_sha256":document["manifest_sha256"]}
            planned=client.post("/api/v1/sessions/plan",json=request,
                                headers={**headers,
                                         "content-type":"application/json"})
            result["real_v113_user_plan_http"]=planned.status_code
            if planned.status_code!=200:
                detail=planned.json().get("detail")
                result["status"]="PENDING_REAL_V113_OPTIONAL_USER_PLAN"
                result["first_blocker"]=(detail.get("code") if
                    isinstance(detail,dict) else
                    "USER_PLAN_HTTP_"+str(planned.status_code))
                save()
                return result
            plan=planned.json()
            folder=app.state.jobs.folder(plan["session_id"])
            profile_path=folder/"generated"/"profile.simc"
            if not profile_path.is_file() or profile_path.is_symlink():
                raise RuntimeError("V688_FINAL_USER_SIMC_PROFILE_MISSING")
            profile=profile_path.read_text(encoding="utf8")
            lines=profile.splitlines()
            if (lines.count("food="+token)!=1 or
                lines.count("potion=disabled")!=1 or
                lines.count("augmentation=disabled")!=1 or
                sum(line.startswith("food=") for line in lines)!=1):
                raise RuntimeError("V688_FINAL_SIMC_CONSUMABLE_INPUT_MISMATCH")
            sealed=plan["environment_manifest"]
            if (sealed["fresh_v212_installed_manifest_sha256"]!=
                    document["manifest_sha256"] or
                plan["plan"]["base_B"]!=document["official_B"] or
                plan["plan"]["final_T"]!=document["official_T"] or
                plan["native_calls"]!=0):
                raise RuntimeError("V688_REAL_USER_INSTALL_B_T_OR_NATIVE_DRIFT")
            result["real_user_profile_sha256"]=hashlib.sha256(
                profile.encode("utf8")).hexdigest()
            result["real_user_B"]=plan["plan"]["base_B"]
            result["real_user_T"]=plan["plan"]["final_T"]
            result["same_v212_sha_used_by_profile"]=True
            result["simc_food_assignment_once"]=True
            result["real_v113_plan_status"]=plan["status"]
            result["status"]="PASS_ORIGINAL_V113_OPTIONAL_PROFILE_ZERO_NATIVE"
            save()
            return result
    except Exception as exc:
        result["status"]="BLOCKED_REAL_OPTIONAL_USER_PROFILE"
        result["first_blocker"]=original.bounded_code(exc)
        result["exception_type"]=type(exc).__name__
        save()
        return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--simc",required=True)
    parser.add_argument("--source-commit-file",required=True)
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    source_commit=pathlib.Path(args.source_commit_file).read_text(
        encoding="utf8").strip()
    if source_commit!=REV:
        raise SystemExit("V688_SOURCE_REVISION_NOT_PINNED")
    binary=pathlib.Path(args.simc).resolve(strict=True)
    if binary.name.lower()!="simc.exe":
        raise SystemExit("V688_SOURCE_BUILT_WINDOWS_SIMC_REQUIRED")
    original.BUILD=BUILD
    original.REV=REV
    original.EXE_SHA=digest(binary)
    original.SCHEMA=SCHEMA
    out=pathlib.Path(args.out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    code=original.run(binary,out,postinstall=followup)
    path=out/"V610_REAL_ENCHANT_ADMISSION_ONE_BUILD.json"
    if path.is_file():
        source=json.loads(path.read_text("utf8"))
        source["schema"]=SCHEMA
        source["actual_simc_source_commit"]=source_commit
        source["source_compiled_simc_sha256"]=original.EXE_SHA
        (out/"V688_REAL_70961_OPTIONAL_USER_PROFILE_ONCE.json").write_text(
            json.dumps(source,ensure_ascii=False,sort_keys=True,
                       indent=2,allow_nan=False)+"\n",encoding="utf8")
        path.unlink()
    return code


if __name__=="__main__":
    sys.exit(main())
