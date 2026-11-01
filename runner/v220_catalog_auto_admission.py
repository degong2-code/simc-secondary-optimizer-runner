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
ALLOWED_KINDS=frozenset(("permanent_enchant","temporary_enchant",
                          "gem","embellishment","consumable"))
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
    if candidate["slot_status"]!="SOURCE_MASK_RESOLVED":
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


def preview_enchant_catalog(source_catalog, items):
    """Read-only preview for existing v196; no receipt means no new choices."""
    if type(source_catalog) is not dict:
        return {"schema":SCHEMA,"policy":"AUTO_AFTER_VERIFIED_EVIDENCE",
                "status":"SOURCE_CATALOG_UNAVAILABLE",
                "automatically_eligible":0,"pending":0,
                "selection_mutated":False}
    if type(items) is not list:
        raise ValueError("AUTO_ADMISSION_ITEMS_INVALID")
    decisions=[]
    seen=set()
    for row in items:
        if type(row) is not dict:
            raise ValueError("AUTO_ADMISSION_ROW_INVALID")
        item_id=row.get("enchant_id")
        if type(item_id) is not int or item_id in seen:
            raise ValueError("AUTO_ADMISSION_DUPLICATE_ID")
        seen.add(item_id)
        slot=row.get("source_slots")
        if type(slot) is not list or len(slot)!=1:
            raise ValueError("AUTO_ADMISSION_SLOT_SCOPE_UNRESOLVED")
        candidate={
            "kind":"permanent_enchant","exact_id":item_id,
            "simc_token":row["token"],"slot":slot[0],
            "slot_status":("SOURCE_MASK_RESOLVED"
                            if not slot[0].startswith("WEAPON_SUBCLASS_")
                            else "PENDING_EXACT_HAND"),
            "game_build":source_catalog["game_build"],
            "simc_revision":source_catalog["simc_revision"],
            "catalog_sha256":source_catalog["manifest_sha256"],
        }
        decisions.append(decide(candidate))
    return {"schema":SCHEMA,"policy":"AUTO_AFTER_VERIFIED_EVIDENCE",
            "status":"PREVIEW_ONLY_NO_PROOF_RECEIPTS",
            "automatically_eligible":sum(d["eligible"] for d in decisions),
            "pending":sum(not d["eligible"] for d in decisions),
            "selection_mutated":False,
            "per_item_missing_reasons":{
                str(d["identity"]["exact_id"]):d["missing"]
                for d in decisions if not d["eligible"]
            }}
