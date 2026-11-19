#!/usr/bin/env python3
"""v220: approved POLICY A, reusable exact-evidence auto-admission decision.

Only a trusted internal orchestrator may supply receipts from existing source,
SimC-input, product-path and CHMV accounting validators. A caller-supplied
JSON assertion (or SimC effect handler presence) is never an admission proof.
This is a PURE decision primitive: it does not publish to UI, run Native,
calculate effect/proc/DPS, edit sessions or mutate the source catalog.
"""
from __future__ import annotations

import hashlib
import json
import re

SCHEMA="v220_exact_evidence_automatic_admission_policy_v1"
PROOF_STATUSES={
    "source_relation":"EXACT_SOURCE_RELATION_VERIFIED",
    "simc_input":"SIMC_INPUT_ACCEPTED",
    "product_input":"PRODUCT_INPUT_ROUTE_ACCEPTED",
    "chmv_budget":"CHMV_ACCOUNTING_VERIFIED",
}
# General-purpose temporary enchants are excluded from product choices by
# the user's 2026-11-02 policy. Weapon oil remains a separate fixed-O product
# control; its SimC serialization may still use temporary_enchant=.
ALLOWED_KINDS=frozenset(("permanent_enchant","gem",
                          "embellishment","consumable"))
HEX64=re.compile(r"[0-9a-f]{64}\Z")
HEX40=re.compile(r"[0-9a-f]{40}\Z")
# Reuse the same per-stat fixed E representation and bounds as v196/v212.
# An absent vector is UNKNOWN, never implicit E=0 on a permanent enchant.
CHMV_STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")


def _identity(candidate):
    if type(candidate) is not dict or set(candidate)!={
        "kind","exact_id","simc_token","slot","slot_status",
        "game_build","simc_revision","catalog_sha256"
    }:
        raise ValueError("AUTO_ADMISSION_CANDIDATE_FIELDS_INVALID")
    if (candidate["kind"] not in ALLOWED_KINDS or
        type(candidate["exact_id"]) is not int or candidate["exact_id"]<=0 or
        type(candidate["simc_token"]) is not str or not candidate["simc_token"] or
        type(candidate["slot"]) is not str or not candidate["slot"] or
        type(candidate["slot_status"]) is not str or
        type(candidate["game_build"]) is not str or not candidate["game_build"] or
        type(candidate["simc_revision"]) is not str or
        not HEX40.fullmatch(candidate["simc_revision"]) or
        type(candidate["catalog_sha256"]) is not str or
        not HEX64.fullmatch(candidate["catalog_sha256"])):
        raise ValueError("AUTO_ADMISSION_CANDIDATE_IDENTITY_INVALID")
    return {key:candidate[key] for key in
            ("kind","exact_id","simc_token","slot","game_build",
             "simc_revision","catalog_sha256")}


def decide(candidate, receipts=None):
    """Admissible only when all *trusted internal* proofs match one exact scope.

    Output is evidence eligibility; UI/adaptive-runtime publication is a
    separate atomic integration. A decision never itself changes approval.
    """
    identity=_identity(candidate)
    if receipts is None:
        receipts={}
    if type(receipts) is not dict:
        raise ValueError("AUTO_ADMISSION_RECEIPTS_INVALID")
    if set(receipts)-set(PROOF_STATUSES):
        raise ValueError("AUTO_ADMISSION_UNKNOWN_PROOF_FAMILY")
    missing=[]; conflicts=[]
    # Gem choices fit ANY existing socket; the product_input receipt owns
    # physical socket count and selected-item conditions.
    universal_gem=(candidate["kind"]=="gem" and
                   candidate["slot"]=="ANY_EXISTING_SOCKET" and
                   candidate["slot_status"]=="GEM_SOCKET_TYPE_NOT_APPLICABLE")
    # Food, potions and augmentation runes do NOT occupy equipment slots.
    # Reject invented equipment-slot attestations for consumables, even if
    # other receipts happen to match. Actual item/use conditions still belong
    # to the existing exact product_input proof, not a new verifier.
    slotless_consumable=(candidate["kind"]=="consumable" and
                         candidate["slot"]=="NO_EQUIPMENT_SLOT" and
                         candidate["slot_status"]==
                             "CONSUMABLE_USE_SCOPE_NOT_EQUIPMENT")
    # Source-authorized ring enchant family can apply to either ring.
    # Which real finger/item is chosen is bound later by v098/v220's
    # already-existing selected-equipment predicate, not inferred here.
    two_ring_scope=(candidate["kind"]=="permanent_enchant" and
                    candidate["slot"]=="finger1/finger2" and
                    candidate["slot_status"]==
                        "RING_HAND_SELECTED_BY_FINAL_USER_EQUIPMENT" and
                    candidate["simc_token"].startswith("enchant_ring__"))
    # A sealed v213 SimC weapon subclass mask describes a *family*, not
    # a physical hand. An eventual v098 exact equipped item must pass the
    # same original source mask before any user SimC input can be formed.
    weapon_family=(candidate["kind"]=="permanent_enchant" and
                   candidate["slot"]==
                       "WEAPON_SUBCLASS_NOT_YET_USER_SLOT_CERTIFIED" and
                   candidate["slot_status"]==
                       "WEAPON_HAND_SELECTED_BY_FINAL_USER_EQUIPMENT" and
                   candidate["simc_token"].startswith("enchant_weapon__"))
    if candidate["kind"]=="consumable":
        if not slotless_consumable:
            missing.append("CONSUMABLE_NO_EQUIPMENT_SLOT_SCOPE_INVALID")
    elif (candidate["slot_status"]!="SOURCE_MASK_RESOLVED" and
          not universal_gem and not two_ring_scope and not weapon_family):
        missing.append("EXACT_PHYSICAL_SLOT_OR_HAND_RELATION_NOT_VERIFIED")
    for family, expected_status in PROOF_STATUSES.items():
        proof=receipts.get(family)
        if proof is None:
            missing.append("EVIDENCE_MISSING:"+family)
            continue
        if type(proof) is not dict or type(proof.get("identity")) is not dict:
            conflicts.append("EVIDENCE_MALFORMED:"+family)
            continue
        if proof["identity"]!=identity:
            conflicts.append("EVIDENCE_SCOPE_MISMATCH:"+family)
            continue
        if proof.get("status")!=expected_status:
            missing.append("EVIDENCE_NOT_VERIFIED:"+family)
            continue
        if not (type(proof.get("evidence_sha256")) is str and
                HEX64.fullmatch(proof["evidence_sha256"])):
            conflicts.append("EVIDENCE_DIGEST_INVALID:"+family)
            continue
        if family=="chmv_budget":
            if proof.get("no_double_count") is not True or (
                proof.get("unknown_static_chmv") is not False):
                missing.append("CHMV_BUDGET_OWNERSHIP_NOT_SETTLED")
            # v212 can only account for a permanent enchant when its exact
            # four-stat fixed E is known. E0 is valid only when all four
            # explicit values are zero. A superficially accepted receipt
            # without this vector previously allowed v196 to publish an
            # item that v098/v096 could never execute.
            if candidate["kind"]=="permanent_enchant":
                E=proof.get("fixed_E")
                if (type(E) is not dict or set(E)!=set(CHMV_STATS)
                    or any(type(E[stat]) is not int or
                           not 0<=E[stat]<=100000
                           for stat in CHMV_STATS)):
                    missing.append("CHMV_EXACT_FIXED_E_VECTOR_REQUIRED")
        if family=="simc_input" and proof.get("effect_mechanism_reimplemented") is True:
            conflicts.append("SIMC_EFFECT_OWNERSHIP_VIOLATION")
    eligible=not missing and not conflicts
    return {
        "schema":SCHEMA,
        "policy":"AUTO_ADMIT_AFTER_ALL_EXACT_INTERNAL_VERIFIERS_PASS",
        "identity":identity,
        "status":("ELIGIBLE_FOR_ATOMIC_PUBLICATION" if eligible else
                  "BLOCKED_EVIDENCE_CONFLICT" if conflicts else
                  "PENDING_EXACT_EVIDENCE"),
        "eligible":eligible,
        "missing":missing,
        "conflicts":conflicts,
        "requires_separate_manual_approval":False,
        "ui_selection_mutated":False,
        "native_calls":0,
        "effect_proc_dps_owner":"SimC",
    }



def selected_equipment_source_mask_match(*, permanent_source, item_metadata,
                                         selected_slot):
    """Reuse SimC's permanent_enchant.cpp class/inventory/subclass predicate.

    This is a SOURCE-MASK COMPARISON, not Policy A product_input proof.
    The caller must supply SAME-BUILD, internally sealed v230 exact
    item_metadata and chosen representative equipment slot; raw user JSON
    cannot authenticate those inputs. An exact selected item is required,
    not a catalog of every weapon or current equipped items.

    SimC itself owns runeforges, effect execution and DPS. Those do not
    require this physical Wago enchant path.
    """
    if (type(permanent_source) is not dict or
        type(item_metadata) is not dict or
        type(selected_slot) is not str or
        selected_slot not in {
            "head","neck","shoulders","chest","legs","feet",
            "wrists","hands","waist","back","finger1","finger2",
            "main_hand","off_hand"}):
        raise ValueError("PERMANENT_SELECTED_ITEM_SOURCE_FIELDS_INVALID")
    keys=("item_class","inventory_type_mask","item_subclass_mask")
    if (any(type(permanent_source.get(k)) is not int or
            permanent_source[k]<0 or permanent_source[k]>=2**32
            for k in keys) or
        any(type(item_metadata.get(k)) is not int or
            item_metadata[k]<0 for k in (
                "item_id","class_id","subclass_id","inventory_type")) or
        item_metadata["item_id"]<=0 or
        item_metadata["inventory_type"]>=32 or
        item_metadata["subclass_id"]>=32):
        raise ValueError("PERMANENT_SELECTED_ITEM_EXACT_METADATA_INVALID")
    cls=permanent_source["item_class"]
    inventory_mask=permanent_source["inventory_type_mask"]
    subclass_mask=permanent_source["item_subclass_mask"]
    icls=item_metadata["class_id"]
    inv=item_metadata["inventory_type"]
    sub=item_metadata["subclass_id"]
    reasons=[]
    if cls not in (2,4):
        reasons.append("NOT_DPS_EQUIPMENT_ENCHANT_CLASS")
    if icls!=cls:
        reasons.append("ENCHANT_AND_ITEM_CLASS_MISMATCH")
    if cls==4:
        if selected_slot in ("main_hand","off_hand"):
            reasons.append("ARMOR_ENCHANT_ON_WEAPON_HAND")
        # Only the item type may establish the exact intended user slot.
        # Reuse the same retail InventoryType mapping as original v213.
        slot_types={
            "head":{1},"neck":{2},"shoulders":{3},"chest":{5,20},
            "legs":{7},"feet":{8},"wrists":{9},"hands":{10},
            "waist":{6},"back":{16},
            "finger1":{11},"finger2":{11}}
        if inv not in slot_types.get(selected_slot,set()):
            reasons.append("SELECTED_ARMOR_SLOT_ITEM_TYPE_MISMATCH")
        if not inventory_mask:
            reasons.append("ARMOR_ENCHANT_SOURCE_INVENTORY_MASK_MISSING")
    if cls==2:
        if selected_slot not in ("main_hand","off_hand"):
            reasons.append("WEAPON_ENCHANT_ON_ARMOR_SLOT")
        if not subclass_mask:
            reasons.append("WEAPON_ENCHANT_SUBCLASS_MASK_MISSING")
        # Equipment item inventory types for already-selected hand:
        # 21 means main-hand-only; 22 means off-hand-only.
        if selected_slot=="main_hand" and inv==22:
            reasons.append("OFFHAND_ONLY_ITEM_IN_MAIN_HAND")
        if selected_slot=="off_hand" and inv in (15,17,21,26):
            reasons.append("MAIN_OR_RANGED_ONLY_ITEM_IN_OFF_HAND")
    # Unlike SimC's lookup with zero inventory/subclass as a wildcard, an
    # internal exact physical ItemID proves the actual zero-coded subtype.
    # Fail closed instead of accepting a nonmatching source mask.
    if inventory_mask and not (inventory_mask & (1<<inv)):
        reasons.append("SOURCE_INVENTORY_MASK_NOT_MATCHED")
    if subclass_mask and not (subclass_mask & (1<<sub)):
        reasons.append("SOURCE_SUBCLASS_MASK_NOT_MATCHED")
    matched=not reasons
    return {
        "status":("EXACT_SELECTED_ITEM_SOURCE_MASK_MATCH_UNADMITTED"
                  if matched else "SOURCE_MASK_OR_HAND_NOT_MATCHED"),
        "matched":matched,
        "selected_slot":selected_slot,
        "selected_item_id":item_metadata["item_id"],
        "source_item_class":cls,
        "source_inventory_type_mask":inventory_mask,
        "source_item_subclass_mask":subclass_mask,
        "item_class":icls,
        "item_inventory_type":inv,
        "item_subclass_id":sub,
        "missing_or_conflicting_conditions":reasons,
        "trusted_v230_item_provenance_required":True,
        "exact_simc_input_not_attested":True,
        "same_effect_and_highest_quality_not_attested":True,
        "fixed_E_or_no_E_not_attested":True,
        "policy_A_product_input_verified":False,
        "ui_selectable":False,"native_calls":0}


def candidate_from_source_enchant(source_catalog, row, *,
                                  original_source_row=None):
    """Shared v196/v216 source candidate shape; never evidence by itself."""
    if type(source_catalog) is not dict or type(row) is not dict:
        raise ValueError("AUTO_ADMISSION_SOURCE_CANDIDATE_INVALID")
    slot=row.get("source_slots")
    if (type(slot) is not list or
        not all(type(value) is str and bool(value) for value in slot)):
        raise ValueError("AUTO_ADMISSION_SLOT_SCOPE_INVALID")
    # v196 public UI rows intentionally exclude physical class/masks.
    # The normal v212 installer may pass ONLY the original v213-sealed
    # candidate row, not metadata from a browser or an inferred ring name.
    original=original_source_row
    ring_pair=(slot==["finger1/finger2"] and
               type(row.get("token")) is str and
               row["token"].startswith("enchant_ring__") and
               type(original) is dict and
               original.get("enchant_id")==row["enchant_id"] and
               original.get("token")==row["token"] and
               original.get("quality_rank")==row.get(
                   "highest_source_quality_rank") and
               original.get("slot_group")=="finger1/finger2" and
               original.get("slot_resolution_status")==
                   "SOURCE_MASK_RESOLVED" and
               original.get("item_class")==4 and
               original.get("inventory_type_mask")==(1<<11) and
               type(original.get("item_subclass_mask")) is int and
               original["item_subclass_mask"]>=0)
    weapon_family=(
        slot==["WEAPON_SUBCLASS_NOT_YET_USER_SLOT_CERTIFIED"] and
        type(row.get("token")) is str and
        row["token"].startswith("enchant_weapon__") and
        type(original) is dict and
        original.get("enchant_id")==row["enchant_id"] and
        original.get("token")==row["token"] and
        original.get("quality_rank")==row.get(
            "highest_source_quality_rank") and
        original.get("slot_group")==
            "WEAPON_SUBCLASS_NOT_YET_USER_SLOT_CERTIFIED" and
        original.get("slot_resolution_status")==
            "WEAPON_SUBCLASS_PENDING_EXACT_HAND_APPLICABILITY" and
        original.get("item_class")==2 and
        original.get("inventory_type_mask")==0 and
        type(original.get("item_subclass_mask")) is int and
        original["item_subclass_mask"]>0)
    resolved=(len(slot)==1 and "/" not in slot[0] and
              not slot[0].startswith("WEAPON_SUBCLASS_"))
    return {"kind":"permanent_enchant","exact_id":row["enchant_id"],
            "simc_token":row["token"],
            "slot":slot[0] if (resolved or ring_pair or weapon_family)
                         else "SOURCE_SLOT_UNRESOLVED",
            "slot_status":("RING_HAND_SELECTED_BY_FINAL_USER_EQUIPMENT"
                           if ring_pair else
                           "WEAPON_HAND_SELECTED_BY_FINAL_USER_EQUIPMENT"
                           if weapon_family else
                           "SOURCE_MASK_RESOLVED" if resolved else
                           "PENDING_EXACT_SLOT_OR_HAND"),
            "game_build":source_catalog["game_build"],
            "simc_revision":source_catalog["simc_revision"],
            "catalog_sha256":source_catalog["manifest_sha256"]}


def candidate_from_source_gem(source_catalog, row):
    """Physical v221 gem ID as existing Policy A input, NOT game approval.

    SimC equipment gem_id syntax is the profile input proposal. A gem fits
    any existing socket regardless of color/type; actual socket COUNT and
    physical item/use conditions belong to product_input proof. Source facts
    alone never prove the other three evidence families or publish the gem.
    """
    if type(source_catalog) is not dict or type(row) is not dict:
        raise ValueError("AUTO_ADMISSION_GEM_SOURCE_REQUIRED")
    if (type(row.get("item_id")) is not int or row["item_id"]<=0 or
        type(row.get("gem_property_id")) is not int or
        row["gem_property_id"]<=0 or
        type(row.get("enchant_id")) is not int or
        row["enchant_id"]<0 or
        type(row.get("color_mask")) is not int or
        row["color_mask"]<0 or
        type(row.get("minimum_ilevel")) is not int or
        row["minimum_ilevel"]<0 or
        type(row.get("expansion_id")) is not int or
        row["expansion_id"]<0):
        raise ValueError("AUTO_ADMISSION_GEM_PROPERTY_FIELDS_INVALID")
    candidate={
        "kind":"gem","exact_id":row["item_id"],
        "simc_token":"gem_id="+str(row["item_id"]),
        "slot":"ANY_EXISTING_SOCKET",
        "slot_status":"GEM_SOCKET_TYPE_NOT_APPLICABLE",
        "game_build":source_catalog.get("game_build"),
        "simc_revision":source_catalog.get("simc_revision"),
        "catalog_sha256":source_catalog.get("manifest_sha256")}
    _identity(candidate)
    return candidate



def plan_optional_permanent_enchant_budget_repair(
        source_catalog, trusted_internal_receipts_by_id,
        missing_reasons_by_id, *, target_ilevel=None):
    """Diagnose *actual* missing E using the same sealed v213/v211 rows.

    The normal v216 Build calls this after the original Policy A preview.
    It does not try to prove enchant effects, run Native, change G/J/F/O,
    or promote an item. Work is bounded to missing chmv_budget receipts:
    exact unscaled raw numbers should be recovered by the v216 source path;
    scaled/ambiguous amounts need a previously verified SAME-scope SimC
    static-delta pair or the existing bounded v198/v297 measurement route.
    Source classification anomalies are kept distinct from real numeric
    gaps so a new season is not treated as a list of hard-coded item IDs.
    """
    if (type(source_catalog) is not dict or
        type(trusted_internal_receipts_by_id) is not dict or
        type(missing_reasons_by_id) is not dict or
        (target_ilevel is not None and
         (type(target_ilevel) is not int or target_ilevel<=0))):
        raise ValueError("AUTO_ADMISSION_E_RECOVERY_INPUT_INVALID")
    catalog=source_catalog.get("catalog") or {}
    classification=source_catalog.get("enchant_classification") or {}
    originals=(catalog.get("enchants") or {}).get("items")
    classified=classification.get("rows")
    if type(originals) is not list or type(classified) is not list:
        raise ValueError("AUTO_ADMISSION_E_RECOVERY_SEALED_ROWS_REQUIRED")
    by_id={}
    for row in originals:
        if (type(row) is not dict or
            type(row.get("enchant_id")) is not int or
            row["enchant_id"] in by_id):
            raise ValueError("AUTO_ADMISSION_E_RECOVERY_ORIGINAL_ID_DRIFT")
        by_id[row["enchant_id"]]=row
    types={}
    for row in classified:
        if (type(row) is not dict or
            type(row.get("enchant_id")) is not int or
            row["enchant_id"] in types):
            raise ValueError("AUTO_ADMISSION_E_RECOVERY_CLASSIFIED_ID_DRIFT")
        types[row["enchant_id"]]=row
    if set(by_id)!=set(types):
        raise ValueError("AUTO_ADMISSION_E_RECOVERY_SOURCE_COVERAGE_DRIFT")
    if set(trusted_internal_receipts_by_id)-set(by_id):
        raise ValueError("AUTO_ADMISSION_E_RECOVERY_NONCANDIDATE_RECEIPT")
    items=[]
    for key,reasons in missing_reasons_by_id.items():
        if (type(key) is not str or not key.isdecimal() or
            type(reasons) is not list or
            any(type(reason) is not str for reason in reasons)):
            raise ValueError("AUTO_ADMISSION_E_RECOVERY_PENDING_SHAPE")
        eid=int(key)
        if eid not in by_id:
            raise ValueError("AUTO_ADMISSION_E_RECOVERY_UNKNOWN_PENDING_ID")
        if "EVIDENCE_MISSING:chmv_budget" not in reasons:
            continue
        row=types[eid]
        origin=by_id[eid]
        if (row.get("token")!=origin.get("token") or
            row.get("item_class")!=origin.get("item_class") or
            row.get("inventory_type_mask")!=origin.get("inventory_type_mask") or
            row.get("item_subclass_mask")!=origin.get("item_subclass_mask")):
            raise ValueError("AUTO_ADMISSION_E_RECOVERY_SOURCE_JOIN_DRIFT")
        if (eid in trusted_internal_receipts_by_id and
            "chmv_budget" in trusted_internal_receipts_by_id[eid]):
            # The receipt exists but its identity/status/shape failed:
            # do not ask for more Native when the join is actually broken.
            raise ValueError("AUTO_ADMISSION_E_RECOVERY_RECEIPT_PREVIEW_DRIFT")
        unknown=row.get("unknown_components")
        static=row.get("static_components")
        if type(unknown) is not list or type(static) is not list:
            cause="CLASSIFICATION_INCOMPLETE"
            action="RECLASSIFY_ALREADY_PINNED_SIMC_SOURCE"
        elif unknown:
            cause="UNKNOWN_SOURCE_STAT_COMPONENT"
            action="RECLASSIFY_ALREADY_PINNED_SIMC_SOURCE"
        elif (row.get("static_chmv_rating_present_in_dbc") is True and
              row.get("budget_policy")==
                  "STATIC_E_REQUIRES_EXACT_MATCHED_NATIVE_PROFILE_AND_IS_FIXED_INSIDE_G"):
            cause="STATIC_CHMV_NUMERIC_SCOPE_NOT_YET_PROVEN"
            action="REUSE_EXACT_NATIVE_PAIR_OR_MEASURE_SELECTED_ITEM"
        elif row.get("static_chmv_rating_present_in_dbc") is False:
            cause="EXACT_SOURCE_E0_RECEIPT_WIRING_MISSING"
            action="REPAIR_SEALED_E0_SOURCE_RECEIPT_NO_NATIVE"
        else:
            cause="UNRECOGNIZED_BUDGET_COMPONENT"
            action="RECLASSIFY_ALREADY_PINNED_SIMC_SOURCE"
        relevant=[{"stat":component.get("item_mod"),
                   "scaling_id":component.get("scaling_id"),
                   "dbc_amount":component.get("dbc_amount"),
                   "coefficient":component.get("coefficient")}
                  for component in static or []
                  if type(component) is dict and
                  component.get("category")=="CHMV_SECONDARY_RATING"]
        signature=hashlib.sha256(json.dumps(
            {"game_build":source_catalog.get("game_build"),
             "simc_revision":source_catalog.get("simc_revision"),
             "catalog_sha256":source_catalog.get("manifest_sha256"),
             "enchant_id":eid,"components":relevant},
            sort_keys=True,ensure_ascii=False,
            separators=(",",":")).encode("utf8")).hexdigest()
        items.append({
            "enchant_id":eid,"token":origin["token"],
            "slot_family":origin.get("slot_group"),
            "game_build":source_catalog.get("game_build"),
            "simc_revision":source_catalog.get("simc_revision"),
            "catalog_sha256":source_catalog.get("manifest_sha256"),
            "target_ilevel":target_ilevel,
            "source_stat_signature_sha256":signature,
            "source_chmv_stat_components":relevant,
            "cause":cause,"next_action":action,
            "reuse_exact_binary_profile_item_slot_receipt_first":True,
            "new_native_calls_limit_for_single_target":(
                2 if action=="REUSE_EXACT_NATIVE_PAIR_OR_MEASURE_SELECTED_ITEM"
                else 0),
            "requires_final_representative_slot_and_mask":(
                action=="REUSE_EXACT_NATIVE_PAIR_OR_MEASURE_SELECTED_ITEM"),
            "fixed_E":None,"verified":False,"user_selectable":False})
    items.sort(key=lambda x:x["enchant_id"])
    # v631: one exact numeric-shape work order per source-equivalent
    # *single-stat* scaling family, not one Native pair per item ID.
    # Exclude stat direction from the grouping key ONLY when SimC's
    # ITEM_ENCHANTMENT_STAT source has exactly one known CHMV component,
    # no other source components/spells and identical physical masks.
    # The grouping is a collection efficiency hint, NOT a proof that a
    # measured representative's rating applies to its unmeasured siblings.
    groups={}
    for item in items:
        if item["next_action"]!=(
                "REUSE_EXACT_NATIVE_PAIR_OR_MEASURE_SELECTED_ITEM"):
            continue
        eid=item["enchant_id"]
        row=types[eid]
        comps=row.get("static_components")
        origin=by_id[eid]
        only=(comps[0] if type(comps) is list and
              len(comps)==1 and type(comps[0]) is dict else None)
        sharable=(
            only is not None
            and only.get("category")=="CHMV_SECONDARY_RATING"
            and only.get("item_mod") in CHMV_STATS
            and type(only.get("component_index")) is int
            and type(only.get("item_mod_id")) is int
            and type(only.get("scaling_id")) is int
            and only["scaling_id"] not in (0,-1)
            and type(only.get("dbc_amount")) is int
            and only["dbc_amount"]==0
            and type(only.get("coefficient")) in (int,float)
            and 0<only["coefficient"]<100000
            and row.get("unknown_components")==[]
            and row.get("spell_effects")==[])
        scope={"game_build":source_catalog.get("game_build"),
               "simc_revision":source_catalog.get("simc_revision"),
               "catalog_sha256":source_catalog.get("manifest_sha256"),
               "target_ilevel":target_ilevel,
               "slot_family":origin.get("slot_group"),
               "item_class":origin.get("item_class"),
               "inventory_type_mask":origin.get("inventory_type_mask"),
               "item_subclass_mask":origin.get("item_subclass_mask")}
        if sharable:
            scope.update({
                "source_component_index":only["component_index"],
                "scaling_id":only["scaling_id"],
                "dbc_amount":only["dbc_amount"],
                "coefficient":only["coefficient"]})
        else:
            scope.update({"unshareable_enchant_id":eid})
        group_sha=hashlib.sha256(json.dumps(
            scope,sort_keys=True,ensure_ascii=False,
            separators=(",",":")).encode("utf8")).hexdigest()
        group=groups.setdefault(group_sha,{
            "source_numeric_group_sha256":group_sha,
            "group_kind":("EXACT_SINGLE_CHMV_SOURCE_SCALING_SHAPE"
                          if sharable else "INDIVIDUAL_ENCHANT_SOURCE_SCOPE"),
            "representative_enchant_id":eid,
            "member_enchant_ids":[],
            "requires_same_representative_item_ilevel_and_slot":True,
            "numeric_transfer_approved":False,
            "new_native_calls_at_most_if_uncached":2})
        group["member_enchant_ids"].append(eid)
        item["source_numeric_group_sha256"]=group_sha
    ordered_groups=sorted(groups.values(),
                          key=lambda group:group["representative_enchant_id"])
    return {
        "schema":"v220_sealed_optional_enchant_E_repair_plan_v1",
        "source_numeric_measurement_groups_unadmitted":ordered_groups,
        "numeric_group_count":len(ordered_groups),
        "native_calls_at_most_if_each_group_uncached":2*len(ordered_groups),
        "identical_source_scale_is_not_a_native_numeric_proof":True,
        "status":("OPTIONAL_EVIDENCE_REPAIR_REQUIRED" if items else
                  "NO_MISSING_ENCHANT_EVIDENCE"),
        "pending_count":len(items),
        "items":items,
        "may_block_verified_base_GJFO":False,
        "new_native_calls_now":0,"network_calls_now":0,
        "cache_mutations":0,"options_published":False,
        "automatic_admission_granted":False}

def preview_enchant_catalog(source_catalog, items, *,
                            trusted_internal_receipts_by_id=None,
                            original_source_rows_by_id=None):
    """Reuse decide() per exact item, without publishing a user choice.

    The optional receipt map is strictly for an INTERNAL orchestrator that
    has already authenticated each source/SimC/product/budget receipt. It
    MUST NOT be populated from an HTTP request, user file, or raw DB2 row.
    Eligible here means eligible for a *later* atomic v196/v212 publication,
    not an installed or executable product choice.
    """
    if type(source_catalog) is not dict:
        return {"schema":SCHEMA,"policy":"AUTO_AFTER_VERIFIED_EVIDENCE",
                "status":"SOURCE_CATALOG_UNAVAILABLE",
                "automatically_eligible":0,"pending":0,
                "selection_mutated":False}
    if type(items) is not list:
        raise ValueError("AUTO_ADMISSION_ITEMS_INVALID")
    if (trusted_internal_receipts_by_id is not None and
        (type(trusted_internal_receipts_by_id) is not dict or
         any(type(k) is not int or k<=0 or type(v) is not dict
             for k,v in trusted_internal_receipts_by_id.items()))):
        raise ValueError("AUTO_ADMISSION_INTERNAL_RECEIPT_MAP_INVALID")
    if original_source_rows_by_id is not None and (
            type(original_source_rows_by_id) is not dict or
            any(type(k) is not int or type(v) is not dict
                for k,v in original_source_rows_by_id.items())):
        raise ValueError("AUTO_ADMISSION_ORIGINAL_SOURCE_MAP_INVALID")
    decisions=[]
    seen=set()
    for row in items:
        if type(row) is not dict:
            raise ValueError("AUTO_ADMISSION_ROW_INVALID")
        item_id=row.get("enchant_id")
        if type(item_id) is not int or item_id in seen:
            raise ValueError("AUTO_ADMISSION_DUPLICATE_ID")
        seen.add(item_id)
        # Existing per-item slot/hand PENDING still prevents publication.
        candidate=candidate_from_source_enchant(
            source_catalog,row,original_source_row=(
                None if original_source_rows_by_id is None else
                original_source_rows_by_id.get(item_id)))
        trusted=(None if trusted_internal_receipts_by_id is None else
                 trusted_internal_receipts_by_id.get(item_id))
        decisions.append(decide(candidate,trusted))
    if (original_source_rows_by_id is not None and
        set(original_source_rows_by_id)!=seen):
        raise ValueError("AUTO_ADMISSION_ORIGINAL_SOURCE_COVERAGE_DRIFT")
    if trusted_internal_receipts_by_id is not None and (
        set(trusted_internal_receipts_by_id)-seen):
        raise ValueError("AUTO_ADMISSION_RECEIPT_FOR_NONCANDIDATE")
    eligible=[d for d in decisions if d["eligible"]]
    return {"schema":SCHEMA,"policy":"AUTO_AFTER_VERIFIED_EVIDENCE",
            "status":("PREVIEW_ONLY_ELIGIBLE_NEEDS_ATOMIC_PUBLICATION"
                      if eligible else "PREVIEW_ONLY_NO_PROOF_RECEIPTS"
                      if trusted_internal_receipts_by_id is None else
                      "PREVIEW_ONLY_EXACT_PROOFS_PENDING"),
            "automatically_eligible":len(eligible),
            "pending":len(decisions)-len(eligible),
            "selection_mutated":False,
            "eligible_for_atomic_publication":[d["identity"] for d in eligible],
            "per_item_missing_reasons":{
                str(d["identity"]["exact_id"]):d["missing"]
                for d in decisions if not d["eligible"]
            },
            "per_item_conflict_reasons":{
                str(d["identity"]["exact_id"]):d["conflicts"]
                for d in decisions if d["conflicts"]
            }}
