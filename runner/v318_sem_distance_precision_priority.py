#!/usr/bin/env python3
"""v318 IDEA-001: opt-in SEM/CHMV-diversity priority for EXISTING v290 confirmation.

Only changes which already-eligible candidate receives a 320-iteration Native
request at the EXISTING v290 precision slots. No new scout generator,
iteration level, extra Native, proc model or 95% familywise assertion.
"""
from __future__ import annotations

import math
import v290_multiscale_adaptive_policy as baseline

SCHEMA = "v318_idea001_sem_and_material_distance_confirmation_v1"
Z = baseline.Z95
MATERIAL_MOVED_FRACTION = 0.08

def next_plan(observations, *, total, lower, upper, native_calls_used,
              max_native_calls, scout_iterations=35,
              confirmation_iterations=320, max_iterations=320):
    """Retain v290's exact cadence and search; re-rank precision targets only.

    A confirmed reference is a measured candidate, never a model prediction.
    z-gap and CHMV diversity are ORDERING HEURISTICS only.
    """
    original = baseline.next_plan(
        observations, total=total, lower=lower, upper=upper,
        native_calls_used=native_calls_used,
        max_native_calls=max_native_calls,
        scout_iterations=scout_iterations,
        confirmation_iterations=confirmation_iterations,
        max_iterations=max_iterations)
    if original.get("next_request") is None or (
            original["next_request"]["phase"] != "precision"):
        return original
    by_vector, identities = baseline._best_by_vector(
        observations, total, tuple(lower), tuple(upper))
    confirmed = [(v, row) for v, row in by_vector.items()
                 if row["iterations"] >= confirmation_iterations]
    available = [(v, row) for v, row in by_vector.items()
                 if row["iterations"] < confirmation_iterations
                 and (v, confirmation_iterations) not in identities]
    if not available:
        return original
    if not confirmed:
        # First anchor is the strongest *observed* unconfirmed candidate.
        picked, _ = max(available, key=lambda x: (
            x[1]["dps_mean"], -x[1]["dps_sem"], x[0]))
        decision = "V318_FIRST_320_ANCHOR"
    else:
        anchor, reference = max(confirmed, key=lambda x: (
            x[1]["dps_mean"], x[0]))
        eligible = []
        for vec, row in available:
            delta = row["dps_mean"] - reference["dps_mean"]
            sigma = math.hypot(row["dps_sem"], reference["dps_sem"])
            z_gap = (delta / sigma if sigma > 0 else (
                math.inf if delta > 0 else -math.inf if delta < 0 else 0.0))
            # CI overlap is a *screening* threshold, never a 95% proof;
            # fallback to original v290 when none appears competitive.
            if z_gap < -Z:
                continue
            separated_region = (
                baseline._distance(vec, anchor) >=
                MATERIAL_MOVED_FRACTION * total)
            # Prefer a plausibly competitive, materially different near
            # alternative; then standardized DPS gap, not raw noisy UCB.
            eligible.append((
                (int(separated_region), z_gap, row["dps_mean"],
                 -row["dps_sem"], vec), vec))
        if not eligible:
            return original
        _, picked = max(eligible, key=lambda x:x[0])
        decision = "V318_SEM_AND_REGION_PRIORITY"
    # Preserve exact 35/320 request identities. No source profile, cache
    # or user scenario parameters are modified.
    result = dict(original)
    result["decision"] = decision
    result["next_request"] = dict(original["next_request"])
    result["next_request"]["target"] = baseline.legacy.to_target(picked)
    result["next_request"]["iterations"] = confirmation_iterations
    result["next_request"]["interpretation"] = (
        "OPT_IN_CONFIRM_PRIORITY_ONLY_NOT_GLOBAL_OR_FAMILYWISE_95")
    return result
