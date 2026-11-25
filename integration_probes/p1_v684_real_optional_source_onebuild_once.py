#!/usr/bin/env python3
"""One genuine v216 same-build source-only food/potion observation.

Runs original zero-history v216 pipeline ONCE on the sealed 70961 SimC revision.
No character, installed budget, historical season input, SimC Native, or DPS.
Only a bounded, non-credential receipt is exported; stage bytes stay ephemeral.
"""
from __future__ import annotations

from collections import Counter
import argparse
import json
import os
import pathlib
import re
import sys
import tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]

import v216_environment_build_coordinator as original
import v212_environment_manifest as install
from p1_v524_m1_m2_source_owner_once import EphemeralActionsCredentials

BUILD="12.1.5.70961"
REV="9933ffb946fb55b1fa66657b848f519ac19006e1"
SCHEMA="p1_v684_one_build_actual_optional_consumable_source_only_v1"


def code(exc):
    value=str(exc).split(":",1)[0].split("\n",1)[0]
    return value if re.fullmatch(r"[A-Z][A-Z0-9_]{3,100}",value) else type(exc).__name__


def observe(out):
    dest=pathlib.Path(out).resolve()
    dest.mkdir(parents=True,exist_ok=True)
    path=dest/"V684_ONE_BUILD_OPTIONAL_SOURCE_ONLY.json"
    state={
        "schema":SCHEMA,
        "status":"STARTED",
        "game_build":BUILD,
        "simc_revision":REV,
        "one_original_v216_source_build":True,
        "historical_source_injected":False,
        "simc_native_calls":0,
        "dps_native_calls":0,
        "new_optimizer":False,
        "source_only_not_installed":True,
        "full_product_e2e":"PENDING",
        "actual_parser_native_accepted":False,
        "all_quality_numeric_noninferiority_proven":False,
    }
    def save():
        path.write_text(json.dumps(state,ensure_ascii=False,sort_keys=True,
                                   indent=2,allow_nan=False)+"\n",encoding="utf8")
    save()
    try:
        credentials=EphemeralActionsCredentials().load()
        if credentials is None:
            state["status"]="PENDING_EXISTING_ACTIONS_SOURCE_CREDENTIALS"
            save()
            return 2
        with tempfile.TemporaryDirectory(prefix="v684-original-stage-",dir=dest) as td:
            root=pathlib.Path(td)/"runs"
            root.mkdir()
            result=original.build_environment(
                sessions_root=root,session_folder=None,user=None,binary=None,
                revision=None,static_cache=None,source_catalog_path=None,
                bootstrap_result=None,
                fresh_collection_inputs={
                    "expected_game_build":BUILD,
                    "representative_request":{
                        "class":"paladin","spec":"retribution",
                        "target_ilevel":334},
                    "g_probe_character":{"race":"dwarf"},
                    "simc_revision_hint":REV,
                    "credentials":credentials,
                    "auto_native_G_requested":False,
                    "auto_native_F_requested":False,
                    "auto_native_O_requested":False,
                    "auto_four_stat_source_requested":False,
                })
            compilation=result.get("source_compilation") or {}
            physical=result.get("fresh_food_potion_item_sources") or {}
            wago=result.get("fresh_optional_food_potion_wago_effects") or {}
            seed=result.get("fresh_lazy_full_pinned_simc_item_source") or {}
            bridge=compilation.get("source_owned_optional_consumables")
            state["source_compilation_status"]=compilation.get("status")
            state["source_compilation_missing"]=list(
                compilation.get("missing") or [])[:20]
            state["physical_source_status"]=physical.get("status")
            state["physical_food_item_count"]=physical.get("food_item_count")
            state["physical_potion_item_count"]=physical.get("potion_item_count")
            state["wago_use_spell_status"]=wago.get("status")
            state["wago_food_item_count"]=wago.get("food_item_count")
            state["wago_potion_item_count"]=wago.get("potion_item_count")
            state["simc_full_item_seed_status"]=seed.get("status")
            state["wago_source_stage_sha256"]=(wago.get("source_stage") or {}).get(
                "receipt_sha256")
            state["simc_item_seed_receipt_sha256"]=seed.get("receipt_sha256")
            state["native_calls_reported"]=result.get("native_calls")
            if result.get("native_calls") != 0:
                raise RuntimeError("V684_SOURCE_ONLY_UNEXPECTED_NATIVE")
            if bridge is None:
                state["status"]="PENDING_ORIGINAL_V680_SOURCE_JOIN"
                state["first_blocker"]=(
                    physical.get("status") if physical.get("status") not in
                        (None,"FRESH_FOOD_POTION_FLASK_ENHANCEMENT_DB2_CANDIDATES_NOT_USER_ADMITTED")
                    else wago.get("status") if wago.get("status") not in
                        (None,"FOOD_POTION_WAGO_USE_SPELLS_SOURCE_READY")
                    else seed.get("status") if not seed.get("source_dir")
                    else "V680_SOURCE_JOIN_NOT_SEALED")
                save()
                return 2
            rows=bridge.get("rows") or []
            state["simc_wago_joined_rows"]=len(rows)
            state["joined_by_kind"]=dict(Counter(row["kind"] for row in rows))
            state["exact_source_receipt_sha256"]=bridge.get(
                "source_receipt_sha256")
            state["source_candidate_sample"]=[
                {k:row.get(k) for k in (
                    "kind","physical_item_id","simc_input_token",
                    "crafting_quality","effect_identity")}
                for row in rows[:12]]
            # This reuses the actual v212 *projection function*, but is
            # NOT an authenticated installation without original GJFO.
            projected=install.project_fresh_optional_consumables(
                game_build=BUILD,simc_revision=REV,source=bridge)
            install.verify_fresh_optional_consumables(
                projected,game_build=BUILD,simc_revision=REV)
            state["v212_source_only_projection"]={
                name:{"status":entry["status"],
                      "option_count":len(entry["options"]),
                      "sample_item_ids":[r["item_id"] for r in
                                         entry["options"][:12]]}
                for name,entry in projected["categories"].items()}
            # Preserve the complete compact join/projection, not another
            # copy of the large raw DB2/SimC files. This lets subsequent
            # reviews distinguish input, quality and parser gaps without
            # repeating an ephemeral source collection.
            state["joined_item_rows"]=[
                {k:row[k] for k in (
                    "kind","physical_item_id","simc_input_token",
                    "crafting_quality","effect_identity",
                    "use_condition_identity","name_enUS")}
                for row in rows]
            state["parser_shadowed_item_ids"]=bridge.get(
                "parser_shadowed_item_ids",[])
            state["projected_options_by_kind"]={
                kind:entry["options"]
                for kind,entry in projected["categories"].items()}
            state["quality_pending_ids_by_kind"]={
                kind:entry.get("quality_comparison_pending_item_ids",[])
                for kind,entry in projected["categories"].items()}
            reviewed=original.optional_source_join.reviewed_apl_default_groups(
                BUILD,REV)
            state["reviewed_default_token_status"]={}
            for kind,defaults in reviewed.items():
                joined={row["simc_input_token"]:row for row in rows
                        if row["kind"]==kind}
                selected={row["simc_token"]:row for row in
                          projected["categories"][kind]["options"]}
                state["reviewed_default_token_status"][kind]={
                    token:{
                        "joined_item_ids":sorted(row["physical_item_id"]
                            for row in rows if row["kind"]==kind and
                            row["simc_input_token"]==token),
                        "projected_item_id":selected.get(token,{}).get("item_id"),
                        "status":("SOURCE_PROJECTED" if token in selected else
                                  "JOINED_NOT_PROJECTED" if token in joined else
                                  "SOURCE_JOIN_MISSING")}
                    for token in defaults}
            # A source-owned row is not necessarily a user-selectable
            # choice: v212 may withhold every tie, duplicate, or shadowed
            # parser token. Do not report an empty gamer menu as PASS.
            selectable=sum(
                len(entry["options"])
                for entry in projected["categories"].values())
            state["v212_selectable_option_count"]=selectable
            state["source_only_not_installed"]=True
            if not rows:
                state["status"]="PENDING_NO_WAGO_SIMC_JOINED_ROWS"
            elif not selectable:
                state["status"]="PENDING_ALL_WAGO_SIMC_OPTIONS_WITHHELD_BY_V212"
            else:
                state["status"]="PASS_REAL_V216_SOURCE_TO_V212_OPTION_PROJECTION"
            save()
            return 0 if rows and selectable else 2
    except Exception as exc:
        state["status"]="BLOCKED_REAL_V216_OPTIONAL_SOURCE"
        state["first_blocker"]=code(exc)
        state["error_type"]=type(exc).__name__
        save()
        return 2
    finally:
        print("V684_SOURCE_ONLY_VERDICT "+json.dumps({
            k:state.get(k) for k in (
                "status","first_blocker","source_compilation_status",
                "physical_source_status","wago_use_spell_status",
                "simc_full_item_seed_status","physical_food_item_count",
                "physical_potion_item_count","simc_wago_joined_rows",
                "joined_by_kind","v212_source_only_projection",
                "v212_selectable_option_count","native_calls_reported",
                "reviewed_default_token_status","quality_pending_ids_by_kind",
                "parser_shadowed_item_ids","joined_item_rows",
                "projected_options_by_kind")
        },ensure_ascii=False,sort_keys=True),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=pathlib.Path,required=True)
    args=parser.parse_args()
    raise SystemExit(observe(args.out))
