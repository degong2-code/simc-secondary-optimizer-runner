#!/usr/bin/env python3
"""v196: small, versioned season option manifest for the local UI.

This is a UI/data bridge, NOT another collection engine. It reads an exact
v191 derived snapshot with SimC highest-source-rank enchant IDs. A collection
candidate MUST NOT become a selectable SimC/user option without budget and
per-item evidence. Already authorized v108/v188 choices remain unchanged.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path

import v108_native_consumable_inputs as v108
import v188_user_choice_metadata as v188
import v197_enchant_effect_families as effect_groups
import v197_verified_effect_budget as fixed_budget
import v202_one_enchant_admission as observed_enchant
import v213_source_to_catalog as source_bridge
import v220_catalog_auto_admission as auto_admission

SCHEMA="v196_current_season_ui_catalog_v1"
SOURCE_SCHEMA="v196_source_first_enchant_candidates_v1"
DEFAULT=Path(__file__).resolve().parents[1]/"data/current_season_simc_enchant_candidates.json"
SLOTS={1:"head",3:"shoulders",5:"chest",20:"chest",8:"feet",11:"finger1/finger2"}

class CatalogBlocked(ValueError):
    pass
def need(condition,code):
    if not condition:
        raise CatalogBlocked(code)

def read(path=DEFAULT):
    path=Path(path)
    need(path.is_file() and 0<path.stat().st_size<=25_000_000,
         "SEASON_ENCHANT_CANDIDATES_ABSENT")
    document=json.loads(path.read_text("utf8"))
    source_classification_rows=None
    source_catalog=None
    if type(document) is dict and document.get("schema")==source_bridge.SCHEMA:
        source_bridge.verify_catalog(document)
        source_classification_rows=document["enchant_classification"]["rows"]
        fresh_catalog=(document["enchant_classification"].get(
            "source_manifest_sha256") is not None)
        source_catalog={
          "schema":document["schema"],
          "status":document["status"],
          "manifest_sha256":document["manifest_sha256"],
          "summary":document["catalog_summary"],
          "related_source_counts":document["related_source_counts"],
          "source_provenance":document["source_provenance"]
        }
        document=dict(document["v196_enchant_source"])
        document["_v211_classification_rows"]=source_classification_rows
        document["_v213_source_catalog"]=source_catalog
        document["_v213_fresh_unapproved"]=fresh_catalog
    from_v213="_v213_source_catalog" in document
    fresh=from_v213 and document.get("_v213_fresh_unapproved") is True
    expected_artifact_id=(None if from_v213 else 12961140046)
    need(type(document) is dict and
         document.get("schema")==SOURCE_SCHEMA and
         document.get("status")=="SOURCE_OBSERVED_NOT_NATIVE_BUDGET_VERIFIED" and
         (fresh or document.get("season_game_build")=="12.1.5.70575") and
         (fresh or document.get("simc_commit")==
             "710c2408bfd3ae4df71b8cd55cdf01f63fd6c926") and
         document.get("user_selectable") is False and
         document.get("source_artifact_id")==expected_artifact_id,
         "SOURCE_FIRST_ENCHANT_PROVENANCE_INVALID")
    related=document.get("related_source_counts")
    if from_v213:
        expected_related=source_catalog["related_source_counts"]
        need(type(related) is dict and related==expected_related and
             document.get("related_source_status")==
             "EVIDENCE_ONLY_NO_NEW_USER_OPTIONS",
             "V213_RELATED_SOURCE_COUNTS_MISMATCH")
    else:
        need(type(related) is dict and
             related=={
               "gear_item_candidates":511,"tier_piece_ids":65,
               "food_raw_item_candidates":192,"potion_raw_item_candidates":61,
               "food_handler_registrations":37,"potion_handler_registrations":5,
               "embellishment_darkmoon_registrations":20,
               "temporary_enchant_entries":117,"gem_property_records":2409}
             and document.get("related_source_status")==
             "EVIDENCE_ONLY_NO_NEW_USER_OPTIONS",
             "PINNED_SEASON_SOURCE_COUNTS_MISMATCH")
    rows=document.get("rows")
    need(type(rows) is list and
         (1<=len(rows)<=1000 if fresh else len(rows)==38),
         "CURRENT_SEASON_ENCHANT_COUNT_INVALID")
    names=set();ids=set();group_counts=Counter();clean=[]
    for r in rows:
        need(type(r) is dict and
             set(r)=={"token","enchant_id","quality_rank","item_class",
                      "inventory_type_mask","item_subclass_mask","approved"},
             "SOURCE_FIRST_ENCHANT_ROW_FIELDS")
        name=r["token"];item_id=r["enchant_id"]
        need(type(name) is str and name.startswith("enchant_")
             and name not in names and
             type(item_id) is int and item_id>0 and item_id not in ids and
             r["approved"] is False and
             (type(r["quality_rank"]) is int and r["quality_rank"]>=0
              if fresh else r["quality_rank"]==2),
             "SOURCE_FIRST_ENCHANT_ROW_INVALID")
        names.add(name);ids.add(item_id)
        mask=r["inventory_type_mask"]
        need(type(mask) is int and mask>=0 and
             type(r["item_subclass_mask"]) is int and
             r["item_subclass_mask"]>=0,"SOURCE_ENCHANT_MASK_INVALID")
        category=name.split("__")[0].replace("enchant_","")
        allowed={"boots","chest","helm","ring","shoulders","weapon"}
        need(category in allowed,"UNKNOWN_ENCHANT_CATEGORY")
        if category=="weapon":
            need(r["item_class"]==2 and mask==0,
                 "WEAPON_ENCHANT_SUBCLASS_REQUIRES_SEPARATE_CHECK")
            slots=["WEAPON_SUBCLASS_NOT_YET_USER_SLOT_CERTIFIED"]
        else:
            need(r["item_class"]==4 and mask>0,
                 "ARMOR_ENCHANT_INVENTORY_MASK_INVALID")
            types=[n for n in range(1,31) if mask&(1<<n)]
            need(types and all(t in SLOTS for t in types),
                 "UNRECOGNIZED_ARMOR_ENCHANT_INVENTORY_TYPE")
            slots=sorted(set(SLOTS[t] for t in types))
        group_counts[category]+=1
        clean.append({"token":name,"enchant_id":item_id,
                      "highest_source_quality_rank":r["quality_rank"],
                      "source_slots":slots,"kind":category,
                      "ui_selectable":False,
                      "blocked_reason":"EFFECT_STATIC_RATING_AND_NATIVE_INPUT_UNVERIFIED"})
    need(fresh or dict(group_counts)=={"boots":3,"chest":4,"helm":6,"ring":9,
                              "shoulders":6,"weapon":10},
         "CURRENT_SEASON_ENCHANT_CATEGORY_COUNTS_INVALID")
    return document,clean,dict(sorted(group_counts.items()))


def prepare_verified_fresh_choices(source_catalog, source_ui,
                                  trusted_internal_receipts_by_id, *,
                                  return_policy_A_preview=False):
    """Normal Build's existing Policy A -> versioned candidate install input.

    Must only be invoked with the original v217/v216 internally authenticated
    receipts; never from HTTP, a browser upload, or a user-supplied JSON proof.
    This is preparation, NOT publication. v212 owns the eventual install.
    """
    source_bridge.verify_catalog(source_catalog)
    need(type(source_ui) is dict and source_ui.get("schema")==SCHEMA
         and source_ui.get("status")==
             "FRESH_SEASON_CANDIDATES_UNAPPROVED_NOT_ENVIRONMENT_READY"
         and source_ui.get("environment_ready") is False
         and source_ui.get("season_build")==source_catalog["game_build"]
         and source_ui.get("simc_revision")==source_catalog["simc_revision"]
         and type(source_ui.get("source_catalog")) is dict
         and source_ui["source_catalog"].get("manifest_sha256")==
             source_catalog["manifest_sha256"]
         and source_ui.get("enchant_candidates",{}).get("selectable_count")==0,
         "FRESH_POLICY_A_SOURCE_UI_IDENTITY_REQUIRED")
    items=source_ui["enchant_candidates"].get("items")
    source_items=source_catalog["v196_enchant_source"]["rows"]
    need(type(items) is list and len(items)==len(source_items)
         and sorted((x["enchant_id"],x["token"],
                     x["highest_source_quality_rank"])
                    for x in items)==sorted((
                     x["enchant_id"],x["token"],x["quality_rank"])
                     for x in source_items)
         and all(x.get("ui_selectable") is False for x in items),
         "FRESH_POLICY_A_ITEM_SOURCE_ROW_DRIFT")
    # An internal caller may not replace an unresolved ring/weapon source
    # mask with a convenient single slot to bypass v220's applicability.
    original_by_id={r["enchant_id"]:r for r in source_items}
    for row in items:
        original=original_by_id[row["enchant_id"]]
        if row["token"].startswith("enchant_weapon__"):
            original_slots=["WEAPON_SUBCLASS_NOT_YET_USER_SLOT_CERTIFIED"]
        else:
            mask=original["inventory_type_mask"]
            need(type(mask) is int and mask>0,
                 "FRESH_POLICY_A_ITEM_MASK_INVALID")
            covered=[n for n in range(1,31) if mask & (1<<n)]
            need(covered and all(n in SLOTS for n in covered),
                 "FRESH_POLICY_A_ITEM_MASK_INVALID")
            original_slots=sorted(set(SLOTS[n] for n in covered))
        need(row.get("source_slots")==original_slots,
             "FRESH_POLICY_A_ITEM_SOURCE_SLOT_DRIFT")
    need(type(trusted_internal_receipts_by_id) is dict,
         "FRESH_POLICY_A_INTERNAL_PROOFS_REQUIRED")
    context={"game_build":source_catalog["game_build"],
             "simc_revision":source_catalog["simc_revision"],
             "manifest_sha256":source_catalog["manifest_sha256"]}
    decision=auto_admission.preview_enchant_catalog(
        context,items,
        trusted_internal_receipts_by_id=trusted_internal_receipts_by_id)
    admissible={x["exact_id"]:x
                for x in decision["eligible_for_atomic_publication"]}
    ready=[]
    quality_pending=[]
    for row in items:
        item_id=row["enchant_id"]
        if item_id not in admissible:
            continue
        candidate=auto_admission.candidate_from_source_enchant(context,row)
        # The existing product_input proof family owns quality and use
        # conditions. A bare highest_source_quality_rank cannot prove either.
        product=trusted_internal_receipts_by_id[item_id]["product_input"]
        required=("highest_available_quality_verified",
                  "same_effect_and_use_conditions_verified",
                  "exact_application_scope_verified")
        if (not all(product.get(x) is True for x in required)
            or not (type(product.get("quality_source_sha256")) is str
                    and auto_admission.HEX64.fullmatch(
                        product["quality_source_sha256"]))
            or product.get("verified_quality_rank")!=
                    row["highest_source_quality_rank"]):
            quality_pending.append(item_id)
            continue
        ready.append({
            "enchant_id":item_id,
            "simc_token":candidate["simc_token"],
            "slot":candidate["slot"],
            "highest_verified_quality_rank":
                row["highest_source_quality_rank"],
            "policy_A_source_relation_sha256":
                trusted_internal_receipts_by_id[item_id][
                    "source_relation"]["evidence_sha256"],
            "quality_source_sha256":product["quality_source_sha256"],
            "exact_v220_identity":admissible[item_id],
        })
    ready.sort(key=lambda x:x["enchant_id"])
    payload={
        "schema":"v196_fresh_verified_option_install_inputs_v1",
        "status":("EXACT_OPTIONS_PREPARED_FOR_VERSIONED_INSTALL"
                  if ready else "EXACT_OPTIONS_NOT_YET_PREPARED"),
        "game_build":context["game_build"],
        "simc_revision":context["simc_revision"],
        "source_catalog_manifest_sha256":context["manifest_sha256"],
        "verified_option_inputs_unpublished":ready,
        "v220_exact_proof_eligible_count":len(admissible),
        "quality_use_scope_pending_item_ids":sorted(quality_pending),
        "other_proofs_pending_by_item_id":
            dict(decision["per_item_missing_reasons"]),
        "selection_mutated":False,
        "ui_selectable":False,"environment_ready":False,
        "environment_installed":False,"options_published":False,
        "native_calls":0,"network_calls":0,
    }
    encoded=json.dumps(payload,sort_keys=True,
        ensure_ascii=False,separators=(",",":"),allow_nan=False).encode("utf8")
    prepared={**payload,"prepared_options_sha256":
        hashlib.sha256(encoded).hexdigest()}
    # The normal Build needs the same v220 diagnostics. Return the already
    # computed single-pass decision instead of walking the candidates twice.
    return (prepared,decision) if return_policy_A_preview else prepared

def public_options(path=DEFAULT, *, trusted_internal_receipts_by_id=None):
    """Project source candidates and existing v220 decisions, not an approval.

    Only the normal *internal* Build may supply previously authenticated
    exact item receipts. The local HTTP catalog route never accepts such
    evidence from a request. Even eligible results remain UNPUBLISHED until
    the correct versioned v212 product-input path admits them.
    """
    source,enchants,counts=read(path)
    source_classification_rows=source.pop("_v211_classification_rows",None)
    source_catalog=source.pop("_v213_source_catalog",None)
    # The unchanged product UI bridge can inspect new-build source data,
    # but no legacy v108/v188/7967/8025/E/J/F approvals are transferable.
    if source.pop("_v213_fresh_unapproved",False):
        classification=source_classification_rows
        need(type(classification) is list and len(classification)==len(enchants),
             "FRESH_SEASON_CLASSIFICATION_COVERAGE_MISMATCH")
        by_id={r["enchant_id"]:r for r in classification}
        need(len(by_id)==len(enchants),
             "FRESH_SEASON_DUPLICATE_CLASSIFICATION_ID")
        for item in enchants:
            classified=by_id.get(item["enchant_id"])
            need(classified is not None and
                 classified["token"]==item["token"] and
                 classified["selection_status"]==
                     "LOCKED_PENDING_CURRENT_SEASON_ITEM_EFFECT_PROOF" and
                 classified["native_E_evidence"]["static_E"] is None,
                 "FRESH_SEASON_UNAUTHORIZED_ENCHANT_APPROVAL_OR_NATIVE_E")
            item["blocked_reason"]="NEW_SEASON_ITEM_EFFECT_QUALITY_AND_CHMV_PROOF_PENDING"
        # Reuse the SAME v220 policy decision that will be used for
        # future exact evidence.  The normal new-season source contains
        # candidates only, so each remains unapproved until trusted
        # source/SimC/product/CHMV receipts actually exist. This is a
        # read-only projection, not an additional approval gate.
        admission_preview=auto_admission.preview_enchant_catalog(
            {"game_build":source["season_game_build"],
             "simc_revision":source["simc_commit"],
             "manifest_sha256":source_catalog["manifest_sha256"]},
            enchants,
            trusted_internal_receipts_by_id=trusted_internal_receipts_by_id)
        need((trusted_internal_receipts_by_id is not None or
              admission_preview["automatically_eligible"]==0) and
             admission_preview["selection_mutated"] is False,
             "FRESH_SEASON_POLICY_A_SOURCE_ONLY_MUST_REMAIN_PENDING")
        return {
            "schema":SCHEMA,
            "status":"FRESH_SEASON_CANDIDATES_UNAPPROVED_NOT_ENVIRONMENT_READY",
            "season_build":source["season_game_build"],
            "simc_revision":source["simc_commit"],
            "source_artifact_id":source["source_artifact_id"],
            "related_source_counts":dict(source["related_source_counts"]),
            "related_source_status":source["related_source_status"],
            "source_catalog":source_catalog,
            "automatic_admission":{
                **admission_preview,
                "status":("ELIGIBLE_NOT_PUBLISHED_TO_PRODUCT"
                          if admission_preview["automatically_eligible"] else
                          "PENDING_EXACT_ITEM_AND_BUDGET_PROOFS"),
                "approved_count":0,
                "eligible_count_unpublished":
                    admission_preview["automatically_eligible"],
                "v212_install_or_user_selection_authorized":False},
            "existing_allowed_input_choices":{},
            "proven_armor_embellishments":{},
            "enchant_candidates":{"total":len(enchants),"groups":counts,
                                  "items":enchants,"selectable_count":0,
                                  "source_classified_count":len(classification),
                                  "effect_classification_status":
                                      "NEW_BUILD_SOURCE_ONLY_NOT_NATIVE_E_OR_USER_ADMITTED"},
            "budget_effect_contract":{
                "fixed_enchant_E_part_of":"GEAR_G_ALREADY_INSIDE_FINAL_T",
                "no_extra_T_or_O_increment":True,
                "status":"NEW_SEASON_E_NOT_VERIFIED"},
            "future_categories":{
                "flask":"NEW_SEASON_F_SOURCE_EVIDENCE_PENDING",
                "ordinary_gems":"NEW_SEASON_J_SOURCE_EVIDENCE_PENDING",
                "weapon_oil":"NEW_SEASON_O_SOURCE_EVIDENCE_PENDING"},
            "environment_ready":False,"G":None,"J":None,"F":None,
            "O":None,"B":None,"T":None,
            "native_calls_now":0,"game_db_recollection_now":0,
            "new_approval_granted":False,
            "optimizer_or_cache_mutated":False}
    need(trusted_internal_receipts_by_id is None,
         "LEGACY_SEASON_POLICY_A_INTERNAL_PROOFS_WRONG_PATH")
    enchants=effect_groups.decorate(
        enchants,source_classification_rows=source_classification_rows)
    # A single source-classified nonCHMV choice has a separate two-Native
    # Windows E=0 witness. Do not generalize its rating classification to
    # unknown enchants, nor unlock the numeric rating-family choices.
    eagle_selectable=False
    try:
        import v206_nonchmv_eagle_selection as eagle
        eagle.evidence()
        eagle.source(path)
        matching=[r for r in enchants
                  if r["token"]=="enchant_ring__eyes_of_the_eagle"
                  and r["enchant_id"]==7967
                  and r["effect_family"]=="crit_effectiveness"]
        need(len(matching)==1,"EAGLE_SOURCE_EFFECT_CATALOG_DRIFT")
        matching[0]["ui_selectable"]=True
        matching[0]["blocked_reason"]=None
        matching[0]["static_CHMV_budget_impact"]="NO_INCREMENT_FROM_NONCHMV_EFFECT"
        matching[0]["native_E_zero_scope"]="WINDOWS_PALADIN_334_2_NATIVE_ONLY"
        eagle_selectable=True
    except (OSError,ValueError,KeyError):
        # Degraded catalog still lists the same 38 items without claiming
        # independent acceptance, budget numbers or broader Native proof.
        eagle_selectable=False
    # Optional v202 observation must never make the *existing* 38-entry
    # read-only catalog disappear if its separate evidence file is absent
    # or mismatched. Missing proof never unlocks any enchant.
    try:
        data,proof_sha=observed_enchant.read()
    except (observed_enchant.EnchantAdmissionBlocked,OSError,
            ValueError,KeyError):
        data=None
        proof_sha=None
    if data is not None:
        matching=[r for r in enchants if r["enchant_id"]==data["enchant_id"]]
        need(len(matching)==1 and matching[0]["ui_selectable"] is False,
             "NATIVE_EVIDENCE_ENCHANT_CATALOG_MISMATCH")
        matching[0]["measured_E_in_one_simc_native_scope"]=dict(data["static_enchant_E"])
        matching[0]["native_scope"]="mage/frost ilvl334 Linux 710c240 finger1"
        matching[0]["same_gear_override_delta_zero"]=True
        matching[0]["evidence_sha256"]=proof_sha
    labels=v188.labels()
    # The only actual user choices in this first stage are exactly the
    # legacy Native/source-verified tokens. Do not enable 192/61 raw DB2
    # food/potion candidates or new 38 enchant IDs.
    approved={
        k:[{"value":token,"label":label,"ui_selectable":True}
           for token,label in sorted(labels[k].items())]
        for k in ("food","potion","augmentation","diamond_id")}
    need(set(labels["food"])==set(v108.SUPPORTED["food"])|{"source_default"}
         and set(labels["potion"])==set(v108.SUPPORTED["potion"])|{"source_default"}
         and set(labels["augmentation"])==
             set(v108.SUPPORTED["augmentation"])|{"source_default"}
         and set(labels["diamond_id"])==
             {"0",*(str(x) for x in v108.DIAMONDS)},
         "V108_USER_APPROVED_CHOICES_DRIFT")
    source_classified=sum("source_effect_classification" in x for x in enchants)
    source_classification_counts={
        "static_chmv_rating":sum(bool(x.get("source_static_chmv_rating_present"))
                                  for x in enchants),
        "static_nonchmv_only_or_mixed":sum(
            bool(x.get("source_effect_classification",{}).get("static_components"))
            and not x.get("source_static_chmv_rating_present",False)
            for x in enchants),
        "spell_effects":sum(bool(x.get("source_effect_classification",{}).get("driver_spell_ids"))
                            for x in enchants),
        "native_E_measured":sum(x.get("source_native_E_status") not in
                                (None,"NOT_MEASURED") for x in enchants)
    }
    return {
        "schema":SCHEMA,"status":"SOURCE_COMBINED_WITH_CLEAR_APPROVAL_BOUNDARY",
        "season_build":source["season_game_build"],
        "one_enchant_native_evidence_status":(
            "EXACT_SCOPE_OBSERVED_READ_ONLY" if data is not None
            else ("OPTIONAL_RATING_EVIDENCE_UNAVAILABLE_EAGLE_SEPARATE"
                  if eagle_selectable else
                  "OPTIONAL_EVIDENCE_UNAVAILABLE_ALL_ENCHANT_CHOICES_LOCKED")),
        "simc_revision":source["simc_commit"],
        "source_artifact_id":source["source_artifact_id"],
        "related_source_counts":dict(source["related_source_counts"]),
        "related_source_status":source["related_source_status"],
        "source_catalog":source_catalog,
        "automatic_admission":auto_admission.preview_enchant_catalog(
            {"game_build":source["season_game_build"],
             "simc_revision":source["simc_commit"],
             "manifest_sha256":source_catalog["manifest_sha256"]}
            if source_catalog else None,enchants),
        "existing_allowed_input_choices":approved,
        "proven_armor_embellishments":v188.public_embellishments(),
        "enchant_candidates":{"total":len(enchants),"groups":counts,
                              "items":enchants,"selectable_count":int(eagle_selectable),
                              "same_effect_stronger_ring_enchants":sum(
                               x["preferred_if_same_effect_source"]==
                                  "STRONGER_VARIANT_REPORTED" for x in enchants),
                              "effect_family_sources":list(
                                  effect_groups.SOURCE_REFERENCES),
                              "source_classified_count":source_classified,
                              "source_classification_counts":source_classification_counts,
                              "effect_classification_status":(
                                  "PINNED_SIMC_DBC_SPELLTEXT_AND_HANDLER_CLASSIFIED_NOT_NATIVE_GENERALIZED"
                                  if source_classified==38 else
                                  "SOURCE_CLASSIFICATION_INCOMPLETE")},
        "budget_effect_contract":{"schema":fixed_budget.SCHEMA,
              "fixed_enchant_E_part_of":"GEAR_G_ALREADY_INSIDE_FINAL_T",
              "requires_exact_companion_native_receipt":True,
              "no_extra_T_or_O_increment":True,
              "status":"NO_VERIFIED_ENCHANT_E_VECTOR_PROVIDED"},
        "future_categories":{
            "flask":"CURRENT_F_165_FIXED_NOT_ALTERNATIVE_VALIDATED",
            "ordinary_gems":"CURRENT_J_138_FIXED_NOT_ALTERNATIVE_VALIDATED",
            "special_diamonds":"TWO_PRIMARY_ONLY_ITEMS_ALREADY_ALLOWED",
            "temporary_enchants":"SOURCE_CANDIDATES_NOT_SLOT_BUDGET_CONNECTED",
            "additional_embellishments":"SIMC_EFFECTS_SOURCE_DISCOVERED_ITEM_SLOT_JOIN_PENDING",
            "food_potions_expanded":"DB2_RAW_192_FOOD_61_POTION_NOT_NATIVE_MATCHED",
        },
        "native_calls_now":0,"game_db_recollection_now":0,
        "new_approval_granted":eagle_selectable,
        "optimizer_or_cache_mutated":False
    }
