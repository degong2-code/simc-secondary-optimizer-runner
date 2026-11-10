"""Pure adaptive regional radius/resource planner; no SimC execution."""
from __future__ import annotations
import math
import statistics
import v290_multiscale_adaptive_policy as base
import v302_weak_multiregion_zoom as geometry

SCHEMA = "v303_adaptive_region_resource_policy_v1"
MIN_RADIUS, MAX_RADIUS, EDGE = 0.005, 0.25, 0.80

class PolicyBlocked(ValueError):
    pass

def need(ok, reason):
    if not ok:
        raise PolicyBlocked(reason)

def vector(row):
    return tuple(row["vector"] if "vector" in row else base.legacy.key(row["target"]))

def score(row):
    mean, sem = row["dps_mean"], row["dps_sem"]
    return mean - 0.5 * min(sem, mean * 0.02)

def initialize_regions(global_observations, *, total, max_regions=8, radius_fraction=0.065):
    need(type(total) is int and total > 0 and type(max_regions) is int
         and 1 <= max_regions <= 8 and MIN_RADIUS <= radius_fraction <= MAX_RADIUS,
         "INITIAL_REGION_PARAMETERS")
    selected = geometry.loose_regions(global_observations, total=total,
        max_regions=max_regions, relative_loss=0.03, minimum_distance_fraction=0.08)
    regions = []
    for i, center in enumerate(selected["centers"]):
        center = tuple(center)
        need(len(center) == 4 and sum(center) == total, "GLOBAL_SHORTLIST_CENTER_INFEASIBLE")
        regions.append({"region_id": f"r{i}", "center": center,
                        "radius_fraction": radius_fraction})
    return {"schema": SCHEMA, "regions": regions,
            "global_seed_count": len(global_observations),
            "eligible_count": selected["eligible_count"],
            "global_optimum_proven": False}

def _metrics(region, rows, total, median_sem):
    center = tuple(region["center"])
    radius_fraction = region.get("radius_fraction", 0.065)
    ordered = sorted(rows, key=lambda r: r["sequence"])
    if not ordered:
        return {"center": center, "radius_fraction": radius_fraction,
                "weight": 1.0, "scout_used": 0, "exhausted": False}
    prior = recent = max(ordered, key=score)
    improvement_z, stable = 0.0, False
    if len(ordered) >= 4:
        half = len(ordered) // 2
        prior, recent = max(ordered[:half], key=score), max(ordered[half:], key=score)
        delta = score(recent) - score(prior)
        improvement_z = delta / max(math.hypot(prior["dps_sem"], recent["dps_sem"]), 1e-9)
        stable = vector(prior) == vector(recent)
    best = vector(max(ordered, key=score))
    radius = max(1, round(total * radius_fraction))
    edge_ratio = max(abs(best[i] - center[i]) / radius for i in range(4))
    sem_ratio = recent["dps_sem"] / median_sem if median_sem else 0.0
    record, last = -math.inf, -1
    for i, row in enumerate(ordered):
        if score(row) > record:
            record, last = score(row), i
    stagnant = len(ordered) - 1 - last
    factor = 1.0
    if len(ordered) >= 4:
        if edge_ratio >= EDGE:
            factor = 1.50 if improvement_z > 0 else 1.25
        elif stable and improvement_z > 0.5:
            factor = 0.75
        elif stagnant >= 3 and sem_ratio <= 1.0:
            factor = 0.70
    next_radius = min(MAX_RADIUS, max(MIN_RADIUS, radius_fraction * factor))
    progress = min(1.0, max(0.0, improvement_z) / 2.0)
    uncertainty = min(1.0, max(0.0, sem_ratio) / 2.0)
    weight = (0.50 + 0.40 * progress + 0.25 * uncertainty
              + 0.15 * float(stable) + 0.20 * float(edge_ratio >= EDGE))
    weight = max(0.05, weight / (1.0 + 0.20 * stagnant))
    return {"center": best, "radius_fraction": next_radius, "weight": weight,
            "improvement_z": improvement_z, "uncertainty_ratio": sem_ratio,
            "rank_stable": stable, "edge_ratio": edge_ratio, "stagnation": stagnant,
            "scout_used": sum(r["phase"] == "scout" for r in ordered)}

def _allocate(regions, weights, budget, max_share, already=None):
    """Rebalance only UNCOMMITTED calls: never erase spent regional Native."""
    ids = [r["region_id"] for r in regions]
    already = {} if already is None else already
    result = {rid: already.get(rid, 0) for rid in ids}
    need(all(type(v) is int and v >= 0 for v in result.values())
         and sum(result.values()) <= budget, "REGIONAL_SPENT_BUDGET")
    if not ids:
        return {}
    if len(ids) == 1:
        return {ids[0]: budget}
    left = budget - sum(result.values())
    cap = max(max(result.values()), math.ceil(
        budget * max(float(max_share), 1 / len(ids))))
    while left:
        active = [rid for rid in ids if result[rid] < cap]
        if not active:
            # Relax only when surviving regions cannot absorb remaining
            # allocation, e.g. other regions became exhausted.
            cap += max(1, math.ceil(left / len(ids)))
            continue
        total_weight = sum(weights[rid] for rid in active)
        shares = {rid: left * weights[rid] / total_weight for rid in active}
        saturated = [rid for rid in active if shares[rid] >= cap - result[rid]]
        if saturated:
            for rid in saturated:
                amount = cap - result[rid]
                result[rid] += amount
                left -= amount
            continue
        floors = {rid: math.floor(shares[rid]) for rid in active}
        for rid, amount in floors.items():
            result[rid] += amount
            left -= amount
        order = sorted(active, key=lambda rid: (
            -(shares[rid] - floors[rid]), -weights[rid], rid))
        for rid in order:
            if left and result[rid] < cap:
                result[rid] += 1
                left -= 1
        need(left == 0, "REGIONAL_REMAINDER_NOT_ALLOCATED")
    need(sum(result.values()) == budget, "REGIONAL_BUDGET_APPORTIONMENT_DRIFT")
    return result


def _candidate(total, lower, upper, center, radius_fraction, observed):
    radius, maximum = max(1, round(total * radius_fraction)), round(total * MAX_RADIUS)
    while radius <= maximum:
        pool = geometry.residual_lattice(total, lower, upper, 6, center=center, radius=radius)
        picks = geometry.bounded_farthest(pool, 1, seed=center, exclude=observed)
        if picks:
            return picks[0], radius
        radius = max(radius + 1, math.ceil(radius * 1.5))
    return None, radius

def next_plan(observations, *, total, lower, upper, regions, total_scout_calls,
              scout_iterations, confirmation_iterations, global_scout_calls_used=0,
              reserve_fraction=0.15, min_global_reserve=8, max_region_share=0.40):
    """Propose one local scout; global reserve remains available to v290.

    Budget counts scout requests. Existing exact scout/confirmation iterations
    remain unchanged. Caller persists region_id and sequence in its journal.
    """
    need(type(total) is int and type(lower) in (tuple, list) and type(upper) in (tuple, list)
         and len(lower) == len(upper) == 4
         and all(type(x) is int for x in (*lower, *upper))
         and all(0 <= lo <= hi <= total for lo, hi in zip(lower, upper))
         and sum(lower) <= total <= sum(upper), "STAT_BOUNDS")
    need(type(scout_iterations) is int and scout_iterations > 0
         and type(confirmation_iterations) is int and confirmation_iterations > scout_iterations,
         "ITERATION_IDENTITIES")
    need(type(total_scout_calls) is int and total_scout_calls >= 1
         and type(global_scout_calls_used) is int
         and 0 <= global_scout_calls_used <= total_scout_calls
         and type(reserve_fraction) in (int, float)
         and 0 <= reserve_fraction < 0.50
         and type(min_global_reserve) is int and min_global_reserve >= 0
         and type(max_region_share) in (int, float)
         and 0 < max_region_share <= 1, "SCOUT_CALL_BUDGET")
    need(type(regions) is list and 1 <= len(regions) <= 8
         and type(observations) is list, "REGIONS_REQUIRED")
    reserve = min(total_scout_calls - 1, max(min_global_reserve,
                  math.ceil(total_scout_calls * reserve_fraction)))
    need(global_scout_calls_used <= reserve, "GLOBAL_RESERVE_OVERSPENT")
    regional_budget = total_scout_calls - reserve
    region_map = {}
    for region in regions:
        rid, center = region["region_id"], tuple(region["center"])
        need(rid not in region_map and len(center) == 4
             and base.legacy.eligible(center, total, lower, upper), "REGION_ID_OR_CENTER")
        radius = region.get("radius_fraction", 0.065)
        need(MIN_RADIUS <= radius <= MAX_RADIUS, "REGION_RADIUS")
        region_map[rid] = dict(region, center=center)

    seen_seq, seen_identity, observed = set(), set(), set()
    by_region = {rid: [] for rid in region_map}
    sems = []
    for row in observations:
        rid, seq, iters = row.get("region_id"), row["sequence"], row["iterations"]
        need(rid is None or rid in region_map, "OBSERVATION_UNKNOWN_REGION")
        need(type(seq) is int and seq not in seen_seq, "DUPLICATE_SEQUENCE")
        seen_seq.add(seq)
        need(iters in (scout_iterations, confirmation_iterations), "ITERATION_IDENTITY")
        mean, sem = row["dps_mean"], row["dps_sem"]
        need(type(mean) in (int, float) and math.isfinite(mean) and mean > 0
             and type(sem) in (int, float) and math.isfinite(sem) and sem >= 0,
             "OBSERVATION_DPS_SEM")
        vec = vector(row)
        need(base.legacy.eligible(vec, total, lower, upper), "OBSERVATION_INFEASIBLE")
        identity = (vec, iters)
        need(identity not in seen_identity, "DUPLICATE_NATIVE_VECTOR_ITERATION_IDENTITY")
        seen_identity.add(identity)
        phase = row.get("phase", "scout" if iters == scout_iterations else "precision")
        need(phase == ("scout" if iters == scout_iterations else "precision"),
             "PHASE_ITERATION_DRIFT")
        clean = dict(row, vector=vec, phase=phase)
        observed.add(vec)
        sems.append(float(row["dps_sem"]))
        if rid is not None:
            by_region[rid].append(clean)

    median_sem = statistics.median(sems) if sems else 0.0
    metrics, candidates = {}, {}
    for rid, region in region_map.items():
        m = _metrics(region, by_region[rid], total, median_sem)
        if region.get("remaining_candidates") == 0:
            pick, actual_radius = None, round(total * m["radius_fraction"])
        else:
            pick, actual_radius = _candidate(total, lower, upper, m["center"],
                                             m["radius_fraction"], observed)
        m["exhausted"] = pick is None
        if pick is not None:
            m["radius_fraction"] = min(MAX_RADIUS, actual_radius / total)
            candidates[rid] = pick
        metrics[rid] = m

    regional_used = sum(m["scout_used"] for m in metrics.values())
    need(regional_used <= regional_budget, "REGIONAL_BUDGET_OVERSPENT")
    active = [r for r in region_map.values() if not metrics[r["region_id"]]["exhausted"]]
    reserve_left = reserve - global_scout_calls_used
    if not active:
        return {"schema": SCHEMA,
                "status": "GLOBAL_RESERVE_ONLY" if reserve_left else "BUDGET_EXHAUSTED",
                "post_global_scout_calls": total_scout_calls,
                "global_reserve_calls": reserve, "global_reserve_remaining": reserve_left,
                "regional_budget_calls": regional_budget, "regional_calls_used": regional_used,
                "allocations": [], "next_request": None,
                "global_fallback_policy": base.SCHEMA, "global_optimum_proven": False}

    weights = {r["region_id"]: metrics[r["region_id"]]["weight"] for r in active}
    used = {r["region_id"]: metrics[r["region_id"]]["scout_used"] for r in active}
    inactive_spent = regional_used - sum(used.values())
    allocations = _allocate(active, weights, regional_budget - inactive_spent,
                            max_region_share, already=used)
    left = regional_budget - regional_used
    eligible = [rid for rid in allocations if allocations[rid] > used[rid]]
    selected = (sorted(eligible, key=lambda rid: (-(allocations[rid] - used[rid]),
                -weights[rid], rid))[0] if left > 0 and eligible else None)
    status = ("NEXT_LOCAL_NATIVE_PROPOSED" if selected else
              "GLOBAL_RESERVE_ONLY" if reserve_left else "BUDGET_EXHAUSTED")
    request = None
    if selected:
        m = metrics[selected]
        request = {"region_id": selected, "phase": "scout",
                   "target": base.legacy.to_target(candidates[selected]),
                   "iterations": scout_iterations, "center": list(m["center"]),
                   "radius_fraction": m["radius_fraction"],
                   "interpretation": "UNMEASURED_NATIVE_CANDIDATE"}
    rows = []
    for rid in sorted(region_map):
        m = metrics[rid]
        rows.append({"region_id": rid, "target_scout_calls": allocations.get(rid, m["scout_used"]),
            "used_scout_calls": m["scout_used"], "weight": round(m["weight"], 8),
            "center": list(m["center"]), "radius_fraction": round(m["radius_fraction"], 8),
            "improvement_z_heuristic": round(m.get("improvement_z", 0), 8),
            "uncertainty_ratio": round(m.get("uncertainty_ratio", 1), 8),
            "rank_stable_heuristic": m.get("rank_stable", False),
            "edge_ratio": round(m.get("edge_ratio", 0), 8),
            "stagnation": m.get("stagnation", 0), "exhausted": m["exhausted"]})
    return {"schema": SCHEMA, "status": status,
            "post_global_scout_calls": total_scout_calls,
            "global_reserve_calls": reserve, "global_reserve_remaining": reserve_left,
            "regional_budget_calls": regional_budget, "regional_calls_used": regional_used,
            "regional_calls_remaining": left, "selected_region": selected,
            "allocations": rows, "next_request": request,
            "global_fallback_policy": base.SCHEMA, "global_optimum_proven": False,
            "statistical_claim": "ALLOCATION_HEURISTICS_ONLY_NOT_95_PERCENT"}

def comparison_budget_contract(*, initial_global_calls, scout_iterations,
        post_global_scout_calls, confirmation_iterations, confirmation_calls,
        wall_clock_budget_seconds):
    """Five-method equal-iterations cohort with one common wall-clock cap."""
    methods = ("fixed_local6", "adaptive_region", "gp_ucb", "mads_like", "sobol")
    need(initial_global_calls >= 1 and scout_iterations > 0 and post_global_scout_calls >= 1
         and confirmation_iterations > scout_iterations and confirmation_calls >= 1
         and wall_clock_budget_seconds > 0, "COMPARISON_BUDGET")
    reserve = min(post_global_scout_calls - 1,
                  max(8, math.ceil(post_global_scout_calls * 0.15)))
    return {"schema": "p2_equal_iterations_wall_clock_cap_contract_v1",
        "methods": methods, "initial_global_calls": initial_global_calls,
        "post_global_scout_calls": post_global_scout_calls,
        "adaptive_regional_scout_calls": post_global_scout_calls - reserve,
        "adaptive_global_reserve_calls": reserve, "confirmation_calls": confirmation_calls,
        "scout_iterations": scout_iterations, "confirmation_iterations": confirmation_iterations,
        "requested_iterations_per_method":
            (initial_global_calls + post_global_scout_calls) * scout_iterations
            + confirmation_calls * confirmation_iterations,
        "native_requests_per_method": initial_global_calls + post_global_scout_calls + confirmation_calls,
        "wall_clock_budget_seconds_per_method": float(wall_clock_budget_seconds),
        "same_initial_global_sample_required": True,
        "same_binary_profile_combat_and_bounds_required": True,
        "native_cache_identity": "(vector,iterations,binary,profile,combat)",
        "separate_equal_wall_clock_cohort_required_for_throughput_claim": True,
        "methods_promoted_by_contract": False}

def validate_comparison_receipts(contract, receipts):
    need(set(receipts) == set(contract["methods"]), "COMPARISON_METHOD_SET")
    fields = ("binary_sha256", "profile_sha256", "combat_sha256",
              "initial_global_sample_sha256", "bounds_sha256")
    common = None
    for method in contract["methods"]:
        row = receipts[method]
        identity = tuple(row.get(k) for k in fields)
        need(all(type(v) is str and len(v) == 64 for v in identity),
             "COMPARISON_IDENTITY_MISSING")
        if common is None:
            common = identity
        need(identity == common, "COMPARISON_SHARED_IDENTITY_DRIFT")
        need(row.get("requested_iterations") == contract["requested_iterations_per_method"],
             "COMPARISON_ITERATIONS_NOT_EQUAL")
        elapsed = row.get("wall_clock_seconds")
        need(type(elapsed) in (int, float) and 0 < elapsed <=
             contract["wall_clock_budget_seconds_per_method"], "COMPARISON_WALL_CLOCK_CAP")
        need(row.get("native_requests") == contract["native_requests_per_method"],
             "COMPARISON_NATIVE_REQUESTS_NOT_EQUAL")
        new, cached = row.get("new_native_calls"), row.get("cache_reuses")
        need(type(new) is int and type(cached) is int and new >= 0 and cached >= 0
             and new + cached == row["native_requests"], "COMPARISON_CACHE_ACCOUNTING")
        need(row.get("global_optimum_proven") is False, "COMPARISON_GLOBAL_OPTIMUM_CLAIM")
    return {"status": "COMPARISON_RESOURCE_RECEIPTS_VALID",
            "requested_iterations_per_method": contract["requested_iterations_per_method"],
            "native_requests_per_method": contract["native_requests_per_method"],
            "actual_wall_clock_seconds": {
                m: receipts[m]["wall_clock_seconds"] for m in contract["methods"]},
            "dps_quality_assessed": False, "statistical_superiority_claimed": False}
