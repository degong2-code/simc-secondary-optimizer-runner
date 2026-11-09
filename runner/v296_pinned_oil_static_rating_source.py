#!/usr/bin/env python3
"""Unbuffed temporary weapon-oil CHMV directly from the season-pinned SimC DBC.

v269/v278 JSON2 buffed_stats include talent/rounding; they are observations,
NOT O component ownership. Reuse v275's already sealed/generated same-build
spell_item_enchantment.inc and v211 source parser, not a new collector or
a spell/proc effect interpreter. Unrecognized/scaled effects remain pending.
"""
from __future__ import annotations
import hashlib,json,pathlib,re
import v211_enchant_source_effect_classification as enchant
import v266_gem_enchant_raw_stat_source as rawstat

SCHEMA="v296_pinned_simc_raw_oil_static_rating_v1"
STATUS="SAME_BUILD_SIMC_RAW_OIL_STATIC_SOURCE_ONLY"
PENDING="SIMC_RAW_OIL_NONSTATIC_OR_UNAVAILABLE"
STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")
REV=re.compile(r"[a-f0-9]{40}\Z")
SHA=re.compile(r"[a-f0-9]{64}\Z")
MAPPING=rawstat.CHMV
KIND=rawstat.STAT_ENCHANT_EFFECT

class OilSourceBlocked(ValueError):pass
def need(ok,code):
    if not ok:raise OilSourceBlocked(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(row):
    return json.dumps(row,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False)

def extract(*,generated_text,game_build,simc_revision,enchant_ids,
            original_git_blob_sha1=None):
    """One pass of v211's exact generated DBC for selected original v281 IDs.

    Return only integer, unscaled ITEM_ENCHANTMENT_STAT points. Any mixed,
    scaled, unknown, absent or zero-only record stays explicitly unadmitted.
    """
    need(type(generated_text) is str and bool(generated_text) and
         len(generated_text.encode("utf8"))<=enchant.MAX_SOURCE
         and type(game_build) is str and bool(game_build)
         and type(simc_revision) is str and REV.fullmatch(simc_revision)
         and type(enchant_ids) in (set,list,tuple) and
         0<len(enchant_ids)<=128 and
         all(type(x) is int and 0<x<10_000_000 for x in enchant_ids),
         "O_RAW_SOURCE_INPUT_INVALID")
    need(enchant.build_from_header(generated_text,
         "spell_item_enchantment.inc")==game_build,
         "O_RAW_SOURCE_GENERATED_GAME_BUILD_DRIFT")
    wanted=set(enchant_ids)
    # Existing parser authenticates the *complete exact selected ID subset*
    # and the array representation; a partial/duplicate source is rejected.
    try: rows=enchant.parse_dbc_rows(generated_text,wanted)
    except enchant.SourceBlocked as exc:
        raise OilSourceBlocked("O_RAW_SOURCE_PARSER:"+str(exc)) from exc
    raw=generated_text.encode("utf8")
    if original_git_blob_sha1 is not None:
        need(type(original_git_blob_sha1) is str and
             re.fullmatch("[a-f0-9]{40}",original_git_blob_sha1) and
             enchant.git_blob_sha(raw)==original_git_blob_sha1,
             "O_RAW_SOURCE_GIT_BLOB_DRIFT")
    options=[]
    for ident in sorted(wanted):
        row=rows[ident]
        vector={stat:0 for stat in STATS}
        exact=(row["id_scaling"]==0 and
               row["req_skill"]==0 and row["req_skill_value"]==0)
        reasons=[]
        if not exact:reasons.append("SCALING_OR_SKILL_CONDITION")
        for typ,amount,property_id,coeff in zip(
                row["ench_type"],row["ench_amount"],
                row["ench_prop"],row["ench_coeff"]):
            if typ==0:continue
            if typ!=KIND or property_id not in MAPPING or amount<=0 or coeff!=0:
                exact=False
                reasons.append("NOT_A_PURE_STATIC_CHMV_COMPONENT")
            else:
                vector[MAPPING[property_id]]+=amount
        if not any(vector.values()):
            exact=False;reasons.append("NO_STATIC_CHMV_COMPONENT")
        # This rejects a generated row with a minimum/maximum item level
        # outside its actual game's usable range only at application time.
        # Do not infer player weapon eligibility from the numerical record.
        options.append({
          "enchant_id":ident,
          "status":STATUS if exact else PENDING,
          "static_CHMV_vector":dict(vector) if exact else None,
          "source_min_ilevel":row["min_ilevel"],
          "source_max_ilevel":row["max_ilevel"],
          "source_reason_codes":sorted(set(reasons)),
          "source_unbuffed":True,
          "native_buffed_stats_not_used_for_O":True,
          "weapon_hand_verified":False,
          "physical_item_verified":False,
          "user_selectable":False,
        })
    doc={"schema":SCHEMA,"game_build":game_build,
         "simc_revision":simc_revision,
         "source_path":enchant.FRESH_FIXED_PATHS[
             "spell_item_enchantment.inc"],
         "source_sha256":sha(raw),
         "source_git_blob_sha1":enchant.git_blob_sha(raw),
         "selected_enchant_ids":sorted(wanted),
         "items":options,
         "native_calls":0,"network_calls":0,
         "source_unbuffed":True,
         "no_effect_mechanism_reimplementation":True,
         "user_selectable":False,"O":None,"environment_ready":False}
    return {**doc,"manifest_sha256":sha(canonical(doc).encode("utf8"))}

def from_v275(*,pinned_source,stage_root,game_build,
              simc_revision,enchant_ids):
    """Consume the original v275 compiled source from its v217 workspace.

    Fail-closed on source drift. No network, Native, new DB, or extra Gate.
    """
    need(type(pinned_source) is dict and
         pinned_source.get("status")=="PINNED_V211_AND_GENERATED_SOURCES_SEALED"
         and pinned_source.get("simc_revision")==simc_revision
         and type(pinned_source.get("source_stage")) is dict
         and pinned_source["source_stage"].get("status") in
             ("EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED"),
         "O_RAW_PINNED_V275_SOURCE_REQUIRED")
    root=pathlib.Path(stage_root).resolve()
    folder=pathlib.Path(pinned_source["source_dir"]).resolve()
    path=pathlib.Path(pinned_source["manifest_path"]).resolve()
    need(folder.is_dir() and not folder.is_symlink() and
         path.is_file() and not path.is_symlink() and
         path.parent==folder and folder.is_relative_to(root),
         "O_RAW_SOURCE_FILES_OUTSIDE_STAGE")
    manifest=json.loads(path.read_text(encoding="utf8"))
    # Reuse v211's original full v275 source SHA/build authentication.
    sources,receipts=enchant.load_fresh_sources(
        folder,manifest,game_build=game_build,
        simc_revision=simc_revision)
    original=receipts["spell_item_enchantment.inc"]
    answer=extract(
        generated_text=sources["spell_item_enchantment.inc"],
        game_build=game_build,simc_revision=simc_revision,
        enchant_ids=enchant_ids,
        original_git_blob_sha1=original["git_blob_sha1"])
    need(answer["source_sha256"]==original["sha256"],
         "O_RAW_V275_SOURCE_SHA_DRIFT")
    return answer

def project_source_oils(*,source,worklist,native_numeric):
    """Replace buffed-JSON2 oil candidates with original unbuffed DBC points.

    Reuses exact v281 physical-item work orders. Other v278 numeric families
    (including F) remain on their unchanged native path. No product admission.
    """
    need(type(source) is dict and source.get("schema")==SCHEMA and
         source.get("source_unbuffed") is True and
         type(source.get("items")) is list and
         type(worklist) is dict and type(worklist.get("oil")) is list and
         type(native_numeric) is dict and
         native_numeric.get("status")==
             "PHYSICAL_ITEM_SIMC_F_O_CANDIDATES_UNADMITTED",
         "O_RAW_PROJECT_SOURCE_AND_NATIVE_REQUIRED")
    by_id={r["enchant_id"]:r for r in source["items"]}
    need(len(by_id)==len(source["items"]) and
         set(by_id)==set(source["selected_enchant_ids"]),
         "O_RAW_PROJECT_SOURCE_ID_DRIFT")
    old={ (r["physical_item_id"],r["selected_hand"]):r
          for r in native_numeric.get("oil",[]) }
    need(len(old)==len(native_numeric.get("oil",[])),
         "O_RAW_PROJECT_DUPLICATE_OLD_NATIVE")
    result=[];seen=set()
    for selected in worklist["oil"]:
        need(type(selected) is dict and
             selected.get("kind")=="temporary_enchant" and
             selected.get("selected_hand") in ("main_hand","off_hand") and
             type(selected.get("physical_item_id")) is int and
             selected["physical_item_id"]>0 and
             type(selected.get("simc_enchant_id")) is int and
             selected["simc_enchant_id"]>0 and
             type(selected.get("source_candidate_sha256")) is str and
             SHA.fullmatch(selected["source_candidate_sha256"]) and
             type(selected.get("source_stage_receipt_sha256")) is str and
             SHA.fullmatch(selected["source_stage_receipt_sha256"]) and
             type(selected.get("simc_input_token")) is str and
             type(selected.get("crafting_quality")) is int,
             "O_RAW_PROJECT_V281_PHYSICAL_IDENTITY_REQUIRED")
        key=(selected["physical_item_id"],selected["selected_hand"])
        need(key not in seen,"O_RAW_PROJECT_DUPLICATE_PHYSICAL_HAND")
        seen.add(key)
        origin=by_id.get(selected["simc_enchant_id"])
        need(origin is not None,
             "O_RAW_PROJECT_ENCHANT_ID_NOT_IN_SEALED_SOURCE")
        prev=old.get(key)
        if prev is not None:
            need(all(prev.get(k)==v for k,v in (
                ("simc_enchant_id",selected["simc_enchant_id"]),
                ("simc_input_token",selected["simc_input_token"]),
                ("crafting_quality",selected["crafting_quality"]),
                ("physical_item_source_candidate_sha256",
                 selected["source_candidate_sha256"]),
                ("physical_item_source_stage_sha256",
                 selected["source_stage_receipt_sha256"]))),
                 "O_RAW_PROJECT_ORIGINAL_V281_V278_IDENTITY_DRIFT")
        vector=origin["static_CHMV_vector"]
        # Preserve the discrepancy for diagnosis; NEVER use the 16/17-like
        # buffed delta as the selected static O rating or force equality.
        observed=prev.get("buffed_CHMV_observation_unadmitted") if prev else None
        result.append({
          "kind":"temporary_enchant",
          "physical_item_id":selected["physical_item_id"],
          "crafting_quality":selected["crafting_quality"],
          "simc_input_token":selected["simc_input_token"],
          "simc_enchant_id":selected["simc_enchant_id"],
          "selected_hand":selected["selected_hand"],
          "game_build":source["game_build"],
          "simc_revision":source["simc_revision"],
          "physical_item_source_stage_sha256":
              selected["source_stage_receipt_sha256"],
          "physical_item_source_candidate_sha256":
              selected["source_candidate_sha256"],
          "status":("SIMC_RAW_STATIC_NUMBER_SOURCE_ONLY"
                    if vector is not None else
                    "SIMC_RAW_NONSTATIC_OIL_SOURCE_PENDING"),
          "rating_candidate_unadmitted":dict(vector) if vector else None,
          "static_CHMV_vector_unadmitted":dict(vector) if vector else None,
          "static_O_unbuffed_source_sha256":source["source_sha256"],
          "source_min_ilevel":origin["source_min_ilevel"],
          "source_max_ilevel":origin["source_max_ilevel"],
          "buffed_CHMV_observation_unadmitted":observed,
          "buffed_snapshot_disagrees_with_raw_source":
              (observed != vector if observed is not None
               and vector is not None else None),
          "simc_native_receipt_sha256":(
              list(prev["simc_native_receipt_sha256"]) if prev else []),
          "same_effect_quality_group_verified":False,
          "weapon_and_hand_applicability_verified":False,
          "budget_ownership_verified":False,
          "source_admitted":False,
          "environment_ready":False,
        })
    return {**native_numeric,"oil":result,
            "oil_O_source":"PINNED_SIMC_RAW_ITEM_ENCHANTMENT_NOT_BUFFED_JSON2",
            "oil_raw_source_sha256":source["source_sha256"],
            "O":None,"environment_ready":False}
