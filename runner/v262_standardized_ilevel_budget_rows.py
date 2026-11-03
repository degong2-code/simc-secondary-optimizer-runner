#!/usr/bin/env python3
"""Thin per-ilvl reference view of the EXISTING v222 G/J/F/O contract.

Only levels with an independently supplied G observation are emitted.
No item-level guessing, new Native, old-season constants or independent
stat/SimC budget math. The source verifier and product admission are external.
"""
from __future__ import annotations

import re

try:
    from . import v222_season_budget_contract as budget
except ImportError:
    import v222_season_budget_contract as budget

SCHEMA = "v262_standardized_G_ilevel_B_rows_v1"
TRACK = re.compile(r"[a-z][a-z0-9_]{0,79}\Z")


def build(*, source_catalog, source_artifact_sha256,
          evidence_by_ilevel, reference_track):
    """Calculate supplied per-ilvl standard B/T via v222, no missing rows."""
    budget.need(type(reference_track) is str
                and TRACK.fullmatch(reference_track) is not None,
                "V262_EXPLICIT_WEAPON_REFERENCE_TRACK_REQUIRED")
    budget.need(type(evidence_by_ilevel) is dict and
                1 <= len(evidence_by_ilevel) <= 200 and
                all(type(k) is int and k > 0 for k in evidence_by_ilevel),
                "V262_VERIFIED_MEASURED_LEVELS_REQUIRED")
    rows = []
    selection = None
    for ilvl in sorted(evidence_by_ilevel):
        proof = evidence_by_ilevel[ilvl]
        budget.need(type(proof) is dict and
                    type(proof.get("components")) is dict and
                    type(proof["components"].get("G")) is dict and
                    type(proof["components"]["G"].get("standardization")) is dict
                    and proof["components"]["G"].get("reference_track") ==
                        reference_track,
                    "V262_STANDARD_G_LEVEL_OR_TRACK_PROOF_REQUIRED")
        reconciled = budget.preprofile_budget(
            source_catalog=source_catalog,
            source_artifact_sha256=source_artifact_sha256,
            evidence=proof, target_ilevel=ilvl)
        components = proof["components"]
        signature = (
            reconciled["J"], reconciled["F"],
            tuple(reconciled["fixed_O"][k] for k in budget.STATS),
            tuple(reconciled["fixed_E"][k] for k in budget.STATS),
            tuple(components["O"]["applied_hands"]),
            tuple((n,components[n]["source_sha256"]) for n in ("J","F","O")),
            proof["G_reference_excludes_selected_E"],
        )
        budget.need(selection is None or signature == selection,
                    "V262_MIXED_J_F_O_E_OR_HAND_SELECTION_NOT_ONE_TABLE")
        selection = signature
        provenance = reconciled["G_standardization"]
        rows.append({
            "ilevel":ilvl,
            "G_observed":provenance["observed_G_total"],
            "G_standard":reconciled["reference_G"],
            "G_rounding_delta":provenance["rounding_delta"],
            "G_source_sha256":provenance["source_observation_sha256"],
            "J":reconciled["J"],"F":reconciled["F"],
            "B":reconciled["base_B"],"fixed_O":reconciled["fixed_O"],
            "T":reconciled["final_T"],
        })
    return {
        "schema":SCHEMA,
        "status":"REFERENCE_ROWS_ARITHMETIC_ONLY_SOURCE_ADMISSION_PENDING",
        "game_build":source_catalog["game_build"],
        "reference_track":reference_track,
        "G_rounding_policy":budget.G_ROUNDING_SCHEMA,
        "rows":rows,
        "manual_final_T_overrides_reference_on_session":True,
        "source_authentication_performed_here":False,
        "environment_ready":False,
        "network_calls":0,"native_calls":0,"cache_mutations":0,
    }
