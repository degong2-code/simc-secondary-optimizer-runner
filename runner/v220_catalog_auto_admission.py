#!/usr/bin/env python3
"""v220: approved POLICY A, reusable exact-evidence auto-admission decision.

Only a trusted internal orchestrator may supply receipts from existing source,
SimC-input, product-path and CHMV accounting validators. A caller-supplied
JSON assertion (or SimC effect handler presence) is never an admission proof.
This is a PURE decision primitive: it does not publish to UI, run Native,
calculate effect/proc/DPS, edit sessions or mutate the source catalog.
"""
from __future__ import annotations

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
    if candidate["kind"]=="consumable":
        if not slotless_consumable:
            missing.append("CONSUMABLE_NO_EQUIPMENT_SLOT_SCOPE_INVALID")
    elif candidate["slot_status"]!="SOURCE_MASK_RESOLVED" and not universal_gem:
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
            "head","shoulders","chest","legs","feet",
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
            "head":{1},"shoulders":{3},"chest":{5,20},
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


def candidate_from_source_enchant(source_catalog, row):
    """Shared v196/v216 source candidate shape; never evidence by itself."""
    if type(source_catalog) is not dict or type(row) is not dict:
        raise ValueError("AUTO_ADMISSION_SOURCE_CANDIDATE_INVALID")
    slot=row.get("source_slots")
    if (type(slot) is not list or
        not all(type(value) is str and bool(value) for value in slot)):
        raise ValueError("AUTO_ADMISSION_SLOT_SCOPE_INVALID")
    resolved=(len(slot)==1 and "/" not in slot[0] and
              not slot[0].startswith("WEAPON_SUBCLASS_"))
    return {"kind":"permanent_enchant","exact_id":row["enchant_id"],
            "simc_token":row["token"],
            "slot":slot[0] if resolved else "SOURCE_SLOT_UNRESOLVED",
            "slot_status":"SOURCE_MASK_RESOLVED" if resolved else
                          "PENDING_EXACT_SLOT_OR_HAND",
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


def preview_enchant_catalog(source_catalog, items, *,
                            trusted_internal_receipts_by_id=None):
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
        candidate=candidate_from_source_enchant(source_catalog,row)
        trusted=(None if trusted_internal_receipts_by_id is None else
                 trusted_internal_receipts_by_id.get(item_id))
        decisions.append(decide(candidate,trusted))
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
