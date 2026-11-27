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


def observe_special_gem_source(result,state,save):
    """One original same-build source scope; never publish a raw candidate."""
    compilation=result.get("source_compilation") or {}
    state["source_compilation_status"]=compilation.get("status")
    state["native_calls_reported"]=result.get("native_calls")
    state["environment_installed"]=result.get("environment_installed") is True
    if state["native_calls_reported"]!=0 or state["environment_installed"]:
        raise RuntimeError("V820_SOURCE_ONLY_SCOPE_DRIFT")
    if compilation.get("status")!="FRESH_V191_V211_V213_COMPILED_UNADMITTED":
        raise RuntimeError("V820_ORIGINAL_COMPILATION_PENDING")
    src=original._fresh_gem_item_source_stage(
        stage_root=compilation["stage_root"],
        wago_folder=pathlib.Path(result["snapshot_receipt_path"]).parent,
        source_catalog_path=compilation["source_catalog_path"],
        expected_game_build=BUILD)
    state["v221"]={k:src.get(k) for k in ("status","physical_gem_item_links","simc_dbc_build_matched")}
    state["v221"]["receipt_sha256"]=src["source_stage"]["receipt_sha256"]
    save()
    args=dict(stage_root=compilation["stage_root"],build=BUILD,
              v221_candidate_path=src["candidate_path"])
    view=original.gem_enchant_stage.view(**args)
    ids=view.get("primary_attribute_special_gem_ids_source_only")
    state["v268_status"]=view.get("status")
    state["gem_enchant_source_sha256"]=view.get("enchant_source_sha256")
    state["primary_candidate_ids"]=ids
    state["intrinsic_socket_source"]={k:(result.get("fresh_one_spec_simc_representative") or {}).get(k)
        for k in ("status","intrinsic_socket_total_source_only",
                  "intrinsic_socket_counts_by_selected_slot_source_only")}
    save()
    if not isinstance(ids,list) or not 0<len(ids)<=16 or len(set(ids))!=len(ids):
        raise RuntimeError("V820_PRIMARY_GEM_SOURCE_EMPTY_OR_SCOPE_TOO_LARGE")
    seed=result["fresh_lazy_full_pinned_simc_item_source"]["source_dir"]
    quality=original._fresh_selected_gem_simc_quality_stage(
        stage_root=compilation["stage_root"],seed_directory=seed,
        game_build=BUILD,simc_revision=REV,selected_item_ids=ids)
    state["quality_source_status"]=quality.get("status")
    state["quality_source_receipt_sha256"]=quality.get("v230_stage_receipt_sha256")
    if quality.get("quality_source_authenticated") is not True:
        raise RuntimeError("V820_ORIGINAL_SELECTED_ITEM_METADATA_PENDING")
    metadata={row["item_id"]:row for row in quality["selected_item_quality_unadmitted"]}
    rows=[]
    state["candidate_rows"]=rows
    for item in ids:
        # Only the bounded primary cohort is projected; the original v266
        # join is cached. No additional collection, Native, or item DB.
        selected=original.gem_enchant_stage.view(**args,
            selected_source_gem_item_ids=[item],selected_special_gem_item_id=item)
        if (selected.get("selected_gem_v221_source_properties_complete") is not True
                or selected.get("selected_special_gem_primary_role_observed_source_only") is not True
                or selected.get("enchant_source_sha256")!=state["gem_enchant_source_sha256"]
                or selected.get("native_calls")!=0 or selected.get("network_calls")!=0):
            raise RuntimeError("V820_EXACT_PRIMARY_ITEM_SOURCE_DRIFT")
        rows.append({"item_id":item,"metadata":metadata[item],
            "physical_property":selected["selected_gem_v221_source_properties_unadmitted"][0],
            "source_effect":selected["selected_special_gem_raw_effect_unadmitted"],
            "positive_CHMV_accounting_pending":selected[
                "selected_special_gem_positive_CHMV_accounting_pending_source_only"],
            "user_selectable":False})
        save()
    state["status"]="PASS_REAL_PRIMARY_GEM_SOURCE_OBSERVED_NOT_ADMITTED"
    state["actual_special_gem_profile_verified"]=False
    save()
    return 0


def observe_socket_bonus_source(result,state,save):
    """Actual selected source rows, no new collection or admission."""
    comp=result["source_compilation"]
    rep=result["fresh_one_spec_simc_representative"]
    review=result["fresh_selectable_bonus_effect_review"]
    state.update(source_compilation_status=comp.get("status"),
        native_calls_reported=result.get("native_calls"),
        environment_installed=result.get("environment_installed") is True,
        bonus_review_status=review.get("status"),
        bonus_review_item_count=review.get("socket_bonus_source_item_count"),
        representative_status=rep.get("status"))
    save()
    if (state["native_calls_reported"]!=0 or state["environment_installed"]
            or comp.get("status")!="FRESH_V191_V211_V213_COMPILED_UNADMITTED"
            or rep.get("status")!="FRESH_ONE_SPEC_SIMC_G_SOURCE_CANDIDATE_PENDING_NATIVE"
            or review.get("status")!="POTENTIAL_BONUS_EFFECT_LINKS_OBSERVED"):
        raise RuntimeError("V825_ORIGINAL_SOURCE_SCOPE_PENDING")
    root=pathlib.Path(comp["stage_root"]).resolve()
    review_path=pathlib.Path(review["candidate_path"]).resolve()
    stage=review["source_stage"]
    sid=stage["stage_id"]
    rel="source/"+sid+".json"
    if review_path!=root/rel or not review_path.is_file() or review_path.stat().st_size>12_000_000:
        raise RuntimeError("V825_BONUS_REVIEW_PATH_OR_SIZE_DRIFT")
    doc=json.loads(review_path.read_text("utf8"))
    inputs=doc["source_identity"]
    if (doc["schema"]!=original.bonus_effect_review.SCHEMA or doc["game_build"]!=BUILD
            or inputs["game_build"]!=BUILD or
            sid!=original._derived_source_generation("season-bonus-effect-review",inputs)):
        raise RuntimeError("V825_BONUS_REVIEW_IDENTITY_DRIFT")
    proof=original.stage_engine.verify_stage(root=root,stage_id=sid,
        stage_version="bonus-effect-source-only-v1",inputs=inputs,outputs={"review":rel})
    if proof["receipt_sha256"]!=stage["receipt_sha256"]:
        raise RuntimeError("V825_BONUS_REVIEW_RECEIPT_DRIFT")
    source_path=pathlib.Path(rep["candidate_path"])
    source=json.loads(source_path.read_text("utf8"))
    if (source["schema"]!=original.simc_representative.SCHEMA
            or source["game_build"]!=BUILD or source["simc_revision"]!=REV
            or source["target_ilevel"]!=334
            or source["receipt_sha256"]!=original.simc_source.digest(
                original.simc_source.canonical({k:v for k,v in source.items()
                    if k!="receipt_sha256"}).encode("utf8"))
            or source["selected_intrinsic_socket_count_by_slot_source_only"]!=rep[
                "intrinsic_socket_counts_by_selected_slot_source_only"]):
        raise RuntimeError("V825_ORIGINAL_V232_SOURCE_DRIFT")
    projection=doc["socket_bonus_source_only"]
    by_id={r["item_id"]:r for r in projection["items"]}
    by_bonus={r["bonus_id"]:r for r in projection["bonus_lists"]}
    selected=source["selected_G_slot_ids"]
    slots=("head","neck","finger1","finger2","wrists","waist")
    state.update(v232_receipt_sha256=source["receipt_sha256"],
        v232_stage_receipt_sha256=rep["source_stage"]["receipt_sha256"],
        bonus_review_receipt_sha256=proof["receipt_sha256"],
        bonus_source_identity=inputs,
        selected_rows=[{"slot":slot,"item_id":selected[slot],
            "intrinsic_socket_count":source["selected_intrinsic_socket_count_by_slot_source_only"][slot],
            "candidate_bonus_lists":[by_bonus[b] for b in
                by_id.get(selected[slot],{}).get("candidate_bonus_list_ids",[])]}
            for slot in slots],
        original_selected_gear_season_provenance=source.get("selected_ordinary_source_provenance"),
        game_socket_legal_verified=False,automatic_bonus_attachment=False)
    state["selected_slots_with_reachable_bonus"]=sum(
        bool(row["candidate_bonus_lists"]) for row in state["selected_rows"])
    state["status"]="PASS_REAL_SELECTED_SOCKET_BONUS_SOURCE_OBSERVED_NOT_ADMITTED"
    save()
    return 0


def observe(out, *, special_gems=False,socket_bonuses=False):
    dest=pathlib.Path(out).resolve()
    dest.mkdir(parents=True,exist_ok=True)
    path=dest/("V825_SELECTED_SOCKET_BONUS_SOURCE.json" if socket_bonuses else
               "V820_SPECIAL_GEM_SOURCE_ONLY.json" if special_gems else
               "V684_ONE_BUILD_OPTIONAL_SOURCE_ONLY.json")
    state={
        "schema":("p1_v825_real_selected_socket_bonus_source_only_v1" if socket_bonuses else
                  "p1_v820_real_primary_gem_source_only_v1" if special_gems else SCHEMA),
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
                    "auto_four_stat_source_requested":special_gems,
                })
            if socket_bonuses:
                return observe_socket_bonus_source(result,state,save)
            if special_gems:
                return observe_special_gem_source(result,state,save)
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
        state["status"]=("BLOCKED_REAL_V216_SOCKET_BONUS_SOURCE" if socket_bonuses else
                         "BLOCKED_REAL_V216_SPECIAL_GEM_SOURCE" if special_gems else "BLOCKED_REAL_V216_OPTIONAL_SOURCE")
        state["first_blocker"]=code(exc)
        state["error_type"]=type(exc).__name__
        save()
        return 2
    finally:
        if socket_bonuses:
            print("V825_SELECTED_SOCKET_BONUS_SOURCE "+json.dumps(state,ensure_ascii=True,sort_keys=True),flush=True)
        if special_gems:
            print("V820_SPECIAL_GEM_SOURCE "+json.dumps(state,ensure_ascii=True,sort_keys=True),flush=True)
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


def replay_ordered_lookup(previous, out, *, quality_replay=False):
    """Reuse real v778 joined rows; fetch only exact item_data.inc.

    No original v216 Build, Wago, Blizzard, WCL, binary or Native.
    The old Actions artifact is evidence for the prior source join, not
    a replacement for an installed season or a fresh physical-source check.
    """
    import hashlib
    import v229_simc_only_source_seed as seed
    import v230_simc_item_metadata as metadata
    previous=pathlib.Path(previous)
    raw_receipt=previous.read_bytes()
    old=json.loads(raw_receipt)
    if (old.get("schema")!=SCHEMA or old.get("game_build")!=BUILD or
        old.get("simc_revision")!=REV or
        old.get("status")!="PASS_REAL_V216_SOURCE_TO_V212_OPTION_PROJECTION" or
        old.get("native_calls_reported")!=0 or
        old.get("source_only_not_installed") is not True or
        old.get("simc_wago_joined_rows")!=60 or
        not re.fullmatch(r"[a-f0-9]{64}",old.get("exact_source_receipt_sha256",""))):
        raise ValueError("V780_ORIGINAL_V778_RECEIPT_SCOPE_MISMATCH")
    rows=old["joined_item_rows"]
    ids=[r["physical_item_id"] for r in rows]
    if len(rows)!=60 or len(set(ids))!=60:
        raise ValueError("V780_ORIGINAL_JOIN_COVERAGE_MISMATCH")
    # The Git tree is immutable. Authenticate only the needed generated
    # blob, not every other season input that v229 can collect.
    tree=seed.discover_generated_tree(REV,quality_files=quality_replay)
    meta=tree["item_data.inc"]
    raw=seed.fetch_generated_blob(revision=REV,name="item_data.inc",
        expected_sha=meta["sha"],expected_size=meta["size"])
    if len(raw)!=meta["size"] or seed.git_blob(raw)!=meta["sha"]:
        raise ValueError("V780_PINNED_ITEM_BLOB_MISMATCH")
    parsed=metadata.parse_exact(raw,build=BUILD,item_ids=ids,
        include_consumable_parser_names=True)
    del raw
    by_id={row["item_id"]:row for row in parsed["items"]}
    owner=original.optional_source_join
    index=owner.ordered_consumable_parser_index(
        parsed["consumable_parser_name_rows"])
    first={}
    for row in rows:
        item_id=row["physical_item_id"]
        item=by_id[item_id]
        kind=row["kind"]
        rank=item["crafting_quality"]
        if (item["class_id"]!=0 or item["inventory_type"]!=0 or
            item["subclass_id"]!=owner.SUBCLASS[kind] or
            rank!=row["crafting_quality"] or item["name"]!=row["name_enUS"] or
            owner.candidate_token(item["name"],rank)!=row["simc_input_token"]):
            raise ValueError("V780_ORIGINAL_JOIN_ITEM_DRIFT")
        first[str(item_id)]=owner.first_consumable_match(
            index,kind,owner.parser_name_stem(item["name"]),rank)
    shadowed=sorted(int(i) for i,match in first.items() if match!=int(i))
    bridge={"game_build":BUILD,"simc_revision":REV,
            "source_receipt_sha256":old["exact_source_receipt_sha256"],
            "rows":rows,"parser_first_match_item_ids":first,
            "parser_shadowed_item_ids":shadowed}
    if quality_replay:
        # Diagnostic only: deliberately do NOT reuse reviewed magnitudes
        # when testing the new extraction. The retained Wago join is not a
        # new install and the resulting numeric data cannot publish options.
        parsed["source_receipt_sha256"]=old["exact_source_receipt_sha256"]
        return replay_direct_quality(out,rows,parsed,tree,owner,seed)
    quality=owner.reviewed_quality_item_evidence(BUILD,REV,rows,parsed)
    if quality is None:
        raise ValueError("V783_REVIEWED_QUALITY_SOURCE_MISMATCH")
    bridge["reviewed_quality_item_evidence"]=quality
    projected=install.project_fresh_optional_consumables(
        game_build=BUILD,simc_revision=REV,source=bridge)
    install.verify_fresh_optional_consumables(
        projected,game_build=BUILD,simc_revision=REV)
    options={kind:entry["options"]
             for kind,entry in projected["categories"].items()}
    defaults={}
    for kind,tokens in owner.reviewed_apl_default_groups(BUILD,REV).items():
        defaults[kind]={token:next((r["item_id"] for r in options[kind]
                                    if r["simc_token"]==token),None)
                        for token in tokens}
    # Exercise the existing API default preference with the actual projected
    # tokens; this is not an authenticated installed manifest or UI run.
    import v113_local_web_api as api
    approved={kind:[r["simc_token"] for r in entries]
              for kind,entries in options.items()}
    preferences=api._v775_source_optional_defaults(
        {"game_build":BUILD,"simc_revision":REV},approved)
    expected={}
    for kind,tokens in owner.reviewed_apl_default_groups(BUILD,REV).items():
        for token,specs in tokens.items():
            for spec in specs.split():
                expected.setdefault(spec,{})[kind]=token
    expected_potions={241288,241289,241308,271887}
    rejected_lower={241309,271886}
    actual_potions={r["item_id"] for r in options["potion"]}
    joined_ids=set(ids)
    quality_ids={241288,241289,241308,241309,271886,271887}
    checks={
        "all_26_spec_default_preferences":len(expected)==26 and
            all(set(v)=={"food","potion"} for v in expected.values()) and
            preferences==expected,
        "all_seven_default_tokens_projected":
            sum(len(v) for v in defaults.values())==7 and
            all(i is not None for v in defaults.values() for i in v.values()),
        "expected_potion_choices_present":expected_potions<=actual_potions,
        "lower_dominated_potions_not_projected":not rejected_lower&actual_potions,
        "no_parser_shadow":not shadowed,
    }
    success=all(checks.values())
    state={"schema":"p1_v780_ordered_optional_lookup_replay_v1",
           "status":("PASS_V783_RETAINED_SOURCE_DEFAULT_PREFERENCES" if success
                     else "PENDING_V783_RETAINED_SOURCE_DEFAULT_PREFERENCES"),
           "checks":checks,"recommended_tokens_by_spec":preferences,
           "reviewed_quality_item_evidence":quality,
           "quality_joined_item_ids":sorted(quality_ids&joined_ids),
           "quality_missing_join_item_ids":sorted(quality_ids-joined_ids),
           "actual_installed_environment_verified":False,
           "actual_native_verified":False,
           "game_build":BUILD,"simc_revision":REV,
           "prior_run_id":45566131185,"prior_artifact_id":14999673517,
           "prior_receipt_sha256":hashlib.sha256(raw_receipt).hexdigest(),
           "item_data_git_blob":meta["sha"],"item_data_sha256":parsed["source_sha256"],
           "item_data_bytes":meta["size"],"reused_joined_rows":len(rows),
           "full_environment_builds":0,"wago_network_calls":0,
           "simc_native_calls":0,"dps_native_calls":0,
           "source_only_not_installed":True,
           "all_quality_numeric_noninferiority_proven":False,
           "parser_first_match_item_ids":first,
           "parser_shadowed_item_ids":shadowed,
           "quality_pending_ids_by_kind":{
               kind:entry.get("quality_comparison_pending_item_ids",[])
               for kind,entry in projected["categories"].items()},
           "option_counts":{kind:len(items) for kind,items in options.items()},
           "projected_options_by_kind":options,
           "reviewed_default_projected_item_ids":defaults}
    out=pathlib.Path(out)
    out.mkdir(parents=True,exist_ok=True)
    (out/"V780_ORDERED_LOOKUP_REPLAY.json").write_text(
        json.dumps(state,sort_keys=True,indent=2,ensure_ascii=False)+"\n",
        encoding="utf8")
    print("V780_REPLAY "+json.dumps(state,sort_keys=True,ensure_ascii=False),flush=True)
    return 0 if success else 2



def replay_direct_quality(out,rows,metadata,tree,owner,seed):
    """Actual exact generated files, no Build, Native or source-join repeat."""
    out=pathlib.Path(out)
    out.mkdir(parents=True,exist_ok=True)
    state={"schema":"p1_v795_direct_quality_actual_source_replay_v1",
           "game_build":BUILD,"simc_revision":REV,
           "prior_run_id":45566131185,"prior_artifact_id":14999673517,
           "source_only_not_installed":True,"full_environment_builds":0,
           "wago_network_calls":0,"simc_native_calls":0,"dps_native_calls":0,
           "status":"STARTED","source_files":{},
           "retained_join_rows":len(rows)}
    def save():
        (out/"V795_DIRECT_QUALITY_REPLAY.json").write_text(
            json.dumps(state,sort_keys=True,indent=2,ensure_ascii=False)+"\n",
            encoding="utf8")
        print("V795_QUALITY_REPLAY "+json.dumps(state,sort_keys=True,
              ensure_ascii=False),flush=True)
    groups=owner.pending_direct_quality_families(rows,metadata,None)
    state["eligible_groups"]=[[r["physical_item_id"] for r in g] for g in groups]
    # Even if no current family qualifies, validate the real table format
    # and exact Light's Potential spell/effect rows independently. Do not
    # force a missing physical rank into an admitted family.
    sid=1236616
    raw={}
    try:
        for name,limit in seed.OPTIONAL_QUALITY_FILES.items():
            meta=tree[name]
            if not 0<meta["size"]<=limit:
                raise ValueError("V795_SOURCE_SIZE_DRIFT:"+name)
            data=seed.fetch_generated_blob(revision=REV,name=name,
                expected_sha=meta["sha"],expected_size=meta["size"])
            if len(data)!=meta["size"] or seed.git_blob(data)!=meta["sha"]:
                raise ValueError("V795_SOURCE_BLOB_DRIFT:"+name)
            raw[name]=data
            state["source_files"][name]={"size":len(data),
                 "git_blob_sha1":meta["sha"],"sha256":seed.digest(data)}
        save()
        spells,effects=owner._quality_spell_fields(raw["sc_spell_data.inc"],BUILD,{sid})
        state["observed_direct_spell"]={"spell_id":sid,
            "spell_rows":spells.get(sid,[]),"effect_rows":effects.get(sid,[])}
        if len(spells.get(sid,[]))!=1 or not effects.get(sid):
            raise ValueError("V795_REAL_SPELL_ROWS_MISSING")
        # Only complete eligible groups enter the producer. If there are
        # none, the producer returns before physical/scale table parsing.
        # The successful no-family receipt proves spell layout only.
        found=owner.direct_quality_source_families(game_build=BUILD,
            simc_revision=REV,rows=rows,metadata=metadata,
            families=groups,source_bytes=raw)
        state["observed_families"]=found
        state["actual_complete_family_count"]=len(found)
        state["status"]=("PASS_ACTUAL_DIRECT_SOURCE_FAMILIES_OBSERVED" if found
                         else "PASS_REAL_SPELL_LAYOUT_NO_COMPLETE_DIRECT_FAMILY")
        save()
        return 0
    except (ValueError,TypeError,KeyError,OSError,IndexError,OverflowError) as exc:
        state["status"]="BLOCKED_ACTUAL_DIRECT_SOURCE"
        state["first_blocker"]=str(exc)[:300]
        save()
        return 2

def replay_special_gem_enchants(prior,out):
    """Reuse actual v820 item rows and the original v275 pinned source reader.
    No full Build, Wago, item database, binary, Native, or option promotion.
    """
    import v275_pinned_simc_compiler_inputs as compiler
    import v229_simc_only_source_seed as seed
    import v211_enchant_source_effect_classification as classifier
    out=pathlib.Path(out)
    out.mkdir(parents=True,exist_ok=True)
    state={"schema":"p1_v821_exact_primary_gem_enchant_source_replay_v1",
           "game_build":BUILD,"simc_revision":REV,"status":"STARTED",
           "prior_run_id":46020391704,"prior_job_id":140578213118,
           "full_environment_builds":0,"wago_network_calls":0,
           "new_github_request_attempts":0,"simc_native_calls":0,
           "dps_native_calls":0,"source_only_not_installed":True,
           "quality_noninferiority_verified":False,
           "actual_socket_applicability_verified":False,
           "source_files":{}}
    def save():
        (out/"V821_SPECIAL_GEM_ENCHANT_REPLAY.json").write_text(
            json.dumps(state,ensure_ascii=True,sort_keys=True,indent=2,
                       allow_nan=False)+"\n",encoding="utf8")
    def fetch(req,timeout):
        state["new_github_request_attempts"]+=1
        return seed.urlopen(req,timeout=timeout)
    try:
        raw=pathlib.Path(prior).read_bytes()
        old=json.loads(raw)
        rows=old["candidate_rows"]
        if (old.get("schema")!="p1_v820_real_primary_gem_source_only_v1"
                or old.get("status")!="PASS_REAL_PRIMARY_GEM_SOURCE_OBSERVED_NOT_ADMITTED"
                or old.get("game_build")!=BUILD or old.get("simc_revision")!=REV
                or old.get("native_calls_reported")!=0
                or old.get("environment_installed") is not False
                or old.get("v221",{}).get("physical_gem_item_links")!=75
                or len(rows)!=11 or [r["item_id"] for r in rows]!=old["primary_candidate_ids"]
                or len({r["item_id"] for r in rows})!=len(rows)
                or any(r["physical_property"]["item_id"]!=r["item_id"]
                       or r["metadata"]["item_id"]!=r["item_id"]
                       or r["source_effect"]["primary_special_role_observed_source_only"] is not True
                       or r["user_selectable"] is not False for r in rows)):
            raise ValueError("V821_RETAINED_V820_SCOPE_MISMATCH")
        state["prior_compact_sha256"]=seed.digest(raw)
        state["prior_v221_receipt_sha256"]=old["v221"]["receipt_sha256"]
        ids={r["physical_property"]["enchant_id"] for r in rows}
        if len(ids)!=len(rows):
            raise ValueError("V821_RETAINED_ENCHANT_ID_DRIFT")
        paths={name:compiler.COMPILER_INPUTS[name] for name in
               ("spell_item_enchantment.inc","spelltext_data.inc")}
        meta=compiler.pinned_git_blobs(revision=REV,paths=paths,transport=fetch)
        content={}
        for name,path in paths.items():
            req=seed.Request(seed.RAW_BASE+REV+"/"+path,headers={
                "User-Agent":"SIMC-Secondary-v275-source-collector/1.0",
                "Accept":"text/plain"})
            with fetch(req,timeout=90) as response:
                if response.status!=200:
                    raise ValueError("V821_PINNED_HTTP_NON200:"+name)
                data=response.read(classifier.MAX_SOURCE+1)
            row=meta[name]
            if len(data)!=row["size"] or seed.git_blob(data)!=row["sha"]:
                raise ValueError("V821_PINNED_SOURCE_BLOB_SHA_DRIFT:"+name)
            source=data.decode("utf8")
            if classifier.build_from_header(source,name)!=BUILD:
                raise ValueError("V821_PINNED_BUILD_DRIFT:"+name)
            content[name]=source
            state["source_files"][name]={"size":len(data),
                "git_blob_sha1":row["sha"],"sha256":seed.digest(data)}
            save()
        enchants=classifier.parse_dbc_rows(content["spell_item_enchantment.inc"],ids)
        texts=classifier.parse_spelltexts(content["spelltext_data.inc"])
        cohort=[]
        for row in rows:
            item=row["item_id"]
            enc=enchants[row["physical_property"]["enchant_id"]]
            # Preserve raw source fields and linked spell descriptions;
            # do not evaluate scaling or invent an effect/quality decision.
            spell_ids=sorted({sid for sid in [enc["id_spell"],
                *(prop for typ,prop in zip(enc["ench_type"],enc["ench_prop"])
                  if typ==3)] if sid>0})
            cohort.append({"item_id":item,"metadata":row["metadata"],
                "physical_property":row["physical_property"],
                "enchant_source_row":enc,"linked_spell_source_text":{
                    str(i):classifier.resolve_spelltext(i,texts) for i in spell_ids},
                "user_selectable":False})
        state.update(status="PASS_EXACT_PINNED_SPECIAL_GEM_ENCHANT_ROWS_NOT_ADMITTED",
                     candidate_rows=cohort)
        save()
        return 0
    except Exception as exc:
        state.update(status="BLOCKED_EXACT_SPECIAL_GEM_SOURCE_REPLAY",
                     first_blocker=code(exc),error_type=type(exc).__name__)
        save()
        return 2
    finally:
        print("V821_SPECIAL_GEM_ENCHANT_REPLAY "+json.dumps(
            state,ensure_ascii=True,sort_keys=True,allow_nan=False),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=pathlib.Path,required=True)
    parser.add_argument("--replay-v778",type=pathlib.Path)
    parser.add_argument("--quality-replay",action="store_true")
    parser.add_argument("--special-gems",action="store_true")
    parser.add_argument("--socket-bonuses",action="store_true")
    parser.add_argument("--replay-special-enchants",type=pathlib.Path)
    args=parser.parse_args()
    if args.socket_bonuses and (args.special_gems or args.replay_v778 or args.replay_special_enchants or args.quality_replay):
        parser.error("socket bonus source is exclusive")
    if args.replay_special_enchants is not None:
        if args.special_gems or args.replay_v778 or args.quality_replay:
            parser.error("special enchant replay is exclusive")
        raise SystemExit(replay_special_gem_enchants(args.replay_special_enchants,args.out))
    raise SystemExit(replay_ordered_lookup(args.replay_v778,args.out,
                         quality_replay=args.quality_replay)
                     if args.replay_v778 else observe(args.out,special_gems=args.special_gems,
                                                     socket_bonuses=args.socket_bonuses))
