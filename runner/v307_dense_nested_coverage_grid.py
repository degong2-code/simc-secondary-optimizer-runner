#!/usr/bin/env python3
"""v307 opt-in coverage-first, nested exact-CHMV grid with bounded local zoom.

"Complete" means *every* feasible target in a specified finite lattice was
measured, NEVER every integer rating combination or global DPS optimality.
All DPS/SEM come from accepted SimC observations; this policy only proposes
integer targets. Layers 6/11/21/41/81 are nested at their final integer B
vectors, including clipped stat floors/caps and rotated residual axes.
"""
from __future__ import annotations

import itertools
import math
from collections import Counter, defaultdict
from functools import lru_cache

import v290_multiscale_adaptive_policy as base
import v298_adaptive_percent_grid as bounds
import v302_weak_multiregion_zoom as geometry

SCHEMA = "v307_dense_nested_coverage_first_experimental_v1"
LEVELS = (6, 11, 21, 41, 81)
DEFAULT_MAX_LEVEL = 21
SURVEY = "global_grid"
LOCAL = "regional_dense"
CONFIRM = "measured_confirm"
METADATA = ("grid_stage", "grid_level", "grid_cursor", "grid_origin")
MASK64 = (1 << 64) - 1


class GridBlocked(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise GridBlocked(reason)


def _params(total, lower, upper, max_level):
    lower, upper = bounds._bounds(total, lower, upper)
    need(type(max_level) is int and max_level in LEVELS,
         "V307_GRID_LEVEL_6_11_21_41_81")
    return tuple(lower), tuple(upper)


def _hash(v):
    # Explicit stable integer mixing, no random salted Python hash().
    h = 0xcbf29ce484222325
    for i, x in enumerate(v):
        h ^= ((x + 1) * (i + 11) * 0x9e3779b1) & MASK64
        h = (h * 0x100000001b3) & MASK64
    return h


@lru_cache(maxsize=5)
def lattice(total, lower, upper, level):
    """Exact rotated residual lattice; bound future 81-point memory to opt-in.

    The source v302 handles 11/21/41. Our 6/81 global extensions repeat its
    exact integer _level and fourth-residual construction without changing its
    immutable source/SHA. All 81-point construction is LAZY: never necessary
    for default max_level=21 or for a low-call budget.
    """
    lower, upper = _params(total, lower, upper, level)
    if level in geometry.GLOBAL_LEVELS:
        return geometry.residual_lattice(total, lower, upper, level)
    axes = [tuple(sorted(set(geometry._level(
        lower[i], upper[i], k, level) for k in range(level))))
        for i in range(4)]
    values = set()
    for dependent in range(4):
        free = tuple(i for i in range(4) if i != dependent)
        for triple in itertools.product(*(axes[i] for i in free)):
            remaining = total - sum(triple)
            if not lower[dependent] <= remaining <= upper[dependent]:
                continue
            vec = [0, 0, 0, 0]
            for i, item in zip(free, triple):
                vec[i] = item
            vec[dependent] = remaining
            values.add(tuple(vec))
    need(all(base.legacy.eligible(v, total, lower, upper) for v in values),
         "V307_GLOBAL_GRID_FEASIBILITY")
    return tuple(sorted(values))


def _cell(vector, lower, upper):
    # Stable 4x4x4x4 stratification. This is scheduling, NOT extra
    # resolution or proof that any unsampled subcell has no DPS peak.
    return tuple(min(3, 4 * (v - lo) // (hi - lo + 1))
                 for v, lo, hi in zip(vector, lower, upper))


@lru_cache(maxsize=5)
def ordered_new_level(total, lower, upper, level):
    lower, upper = _params(total, lower, upper, level)
    earlier = LEVELS[LEVELS.index(level) - 1] if level != LEVELS[0] else None
    covered = set(lattice(total, lower, upper, earlier)) if earlier else set()
    fresh = [v for v in lattice(total, lower, upper, level)
             if v not in covered]
    groups = defaultdict(list)
    for v in fresh:
        groups[_cell(v, lower, upper)].append(v)
    # Alternate across occupied coarse cells, rather than exhaust one
    # lexicographic strip and silently miss an unrelated high-DPS region.
    for group in groups.values():
        group.sort(key=lambda v: (_hash(v), v))
    buckets = [groups[k] for k in sorted(groups)]
    result = []
    for round_ in itertools.zip_longest(*buckets):
        result.extend(v for v in round_ if v is not None)
    need(len(result) == len(fresh) and len(set(result)) == len(fresh),
         "V307_GLOBAL_LEVEL_SCHEDULING_NOT_BIJECTIVE")
    return tuple(result)


def budget(max_native_calls):
    need(type(max_native_calls) is int and 24 <= max_native_calls <= 100000,
         "V307_NATIVE_BUDGET_24_TO_100000")
    confirms = min(16, max(2, math.ceil(max_native_calls * .03)))
    scout = max_native_calls - confirms
    survey = math.ceil(scout * .84)
    return {
        "total": max_native_calls,
        "scout": scout,
        "survey_target": survey,
        "local_target": scout - survey,
        "confirmation_calls": confirms,
        "survey_preference": .84,
        "global_optimum_proven": False,
    }


def _vector(row):
    return tuple(base.legacy.key(row["target"]))


def _scout_rows(rows, total, lower, upper):
    measured = {}
    for row in rows:
        v = base._row(row, total, lower, upper)
        if row["phase"] == "scout":
            need(v not in measured, "V307_DUPLICATE_SCOUT_VECTOR")
            measured[v] = row
    return measured


def _global_next(rows, observed, *, total, lower, upper, max_level):
    for level in LEVELS:
        if level > max_level:
            break
        old = [r["grid_cursor"] for r in rows
               if r["grid_stage"] == SURVEY and
                  r["grid_level"] == level]
        cursor = max(old) + 1 if old else 0
        order = ordered_new_level(total, lower, upper, level)
        while cursor < len(order) and order[cursor] in observed:
            cursor += 1
        if cursor < len(order):
            return (order[cursor], level, cursor)
    return None


def _centers(measured, total, count=8):
    # Do not drop distinct peaks merely because their initial 35-iteration
    # measurement was noisy; loose ranking and a diversity floor remain.
    ranked = sorted(measured, key=lambda v: (
        -(measured[v]["dps_mean"] - .5 * measured[v]["dps_sem"]), v))
    chosen = []
    for v in ranked:
        if all(base._distance(v, x) >= total * .08 for x in chosen):
            chosen.append(v)
            if len(chosen) >= count:
                break
    return chosen


def _local_next(rows, measured, *, total, lower, upper):
    centers = _centers(measured, total)
    if not centers:
        return None
    visits = Counter(tuple(r["grid_origin"]) for r in rows
                     if r["grid_stage"] == LOCAL)
    best = max(measured[v]["dps_mean"] - .5 * measured[v]["dps_sem"]
               for v in centers)
    choices = []
    seen = set(measured)
    for center in centers:
        r = measured[center]
        score = r["dps_mean"] - .5 * r["dps_sem"]
        uncertainty = max(1., math.hypot(r["dps_sem"], r["dps_sem"]))
        gap = max(0., (best - score) / uncertainty)
        # A weak region retains >=1/3 of the relative sampling weight
        # of a leading center; never hard-discard from the coverage audit.
        weight = 1. + 2. * math.exp(-min(10., gap) / 2.)
        potential = (visits[center] + 1) / weight
        radius = max(1, round(total * .05))
        # Reuse v302's tested six-level bounded, multi-axis local grid.
        pool = geometry.residual_lattice(
            total, lower, upper, 6, center=center, radius=radius)
        fresh = [v for v in pool if v not in seen]
        if not fresh:
            continue
        # Small moves early, broader locally later; different region modes
        # are still visited and exact existing Native candidates are excluded.
        fresh.sort(key=lambda v: (
            base._distance(v, center), _hash(v), v))
        pos = min(visits[center], len(fresh)-1)
        candidate = fresh[pos]
        choices.append((potential, -score, center, candidate, pos))
    if not choices:
        return None
    _, _, center, candidate, _ = min(choices)
    return candidate, center


def next_plan(observations, *, total, lower, upper, max_native_calls,
              scout_iterations, confirmation_iterations, max_level=DEFAULT_MAX_LEVEL,
              complete_grid_first=False):
    lower, upper = _params(total, lower, upper, max_level)
    opts = budget(max_native_calls)
    need(type(complete_grid_first) is bool,
         "V307_COMPLETE_GRID_FIRST_BOOL_REQUIRED")
    need(type(observations) is list and
         type(scout_iterations) is int and
         type(confirmation_iterations) is int and
         1 <= scout_iterations < confirmation_iterations,
         "V307_HISTORY_AND_ITERATIONS_REQUIRED")
    for r in observations:
        need(all(k in r for k in METADATA) and
             r["grid_stage"] in (SURVEY, LOCAL, CONFIRM) and
             (r["phase"], r["iterations"]) ==
             (("scout", scout_iterations) if r["grid_stage"] != CONFIRM
              else ("precision", confirmation_iterations)),
             "V307_HISTORY_GRID_METADATA_OR_PHASE_DRIFT")
        if r["grid_stage"] == SURVEY:
            need(r["grid_level"] in LEVELS and
                 r["grid_level"] <= max_level and
                 type(r["grid_cursor"]) is int and
                 r["grid_cursor"] >= 0 and r["grid_origin"] is None,
                 "V307_SURVEY_METADATA_DRIFT")
        elif r["grid_stage"] == LOCAL:
            need(r["grid_level"] == 6 and
                 r["grid_cursor"] is None and
                 type(r["grid_origin"]) in (list, tuple) and
                 len(r["grid_origin"]) == 4,
                 "V307_LOCAL_METADATA_DRIFT")
        else:
            need(r["grid_level"] is None and
                 r["grid_cursor"] is None and r["grid_origin"] is None,
                 "V307_CONFIRM_METADATA_DRIFT")
    if len(observations) >= max_native_calls:
        return {"schema": SCHEMA, "status": "BUDGET_EXHAUSTED",
                "next_request": None, "global_optimum_proven": False}
    measured = _scout_rows(observations, total, lower, upper)
    completed_scouts = sum(r["phase"] == "scout" for r in observations)
    completed_surveys = sum(r["grid_stage"] == SURVEY for r in observations)
    completed_local = sum(r["grid_stage"] == LOCAL for r in observations)
    completed_confirmation = sum(r["grid_stage"] == CONFIRM for r in observations)
    if completed_scouts >= opts["scout"]:
        ranked = sorted(measured, key=lambda v: (
            -(measured[v]["dps_mean"] - .5 * measured[v]["dps_sem"]), v))
        confirmed = {_vector(r) for r in observations if r["phase"] == "precision"}
        candidate = next((v for v in ranked if v not in confirmed), None)
        if candidate is None:
            return {"schema":SCHEMA,"status":"NO_DISTINCT_CONFIRM_TARGET",
                    "next_request":None,"global_optimum_proven":False}
        return {
            "schema":SCHEMA,"status":"NEXT_NATIVE_PROPOSED",
            "decision":"V307_TOP_OBSERVED_CONFIRM_ONLY",
            "next_request":{"phase":"precision",
                "target":base.legacy.to_target(candidate),
                "iterations":confirmation_iterations,
                "grid_stage":CONFIRM,"grid_level":None,
                "grid_cursor":None,"grid_origin":None},
            "global_optimum_proven":False}
    fresh = _global_next(observations, measured,
                         total=total, lower=lower, upper=upper,
                         max_level=max_level)
    coarse_total = len(ordered_new_level(
        total, lower, upper, LEVELS[0]))
    coarse_completed = completed_surveys >= coarse_total
    # If a small session barely finishes the coarse layer, guarantee a
    # meaningful slice of the next nested level rather than spending every
    # remaining scout on local zoom just because the 84% quota was reached.
    survey_target = max(opts["survey_target"], min(opts["scout"],
        coarse_total + max(1, round(max(0, opts["scout"]-coarse_total)*.60))))
    # Full-survey opt-in visits all available nested global targets before
    # optional local work. A typed budget of len(level11)+confirmations is
    # then sufficient for *complete* level11; the legacy 84% scheduling is
    # retained unchanged without this explicit option.
    # Coverage-first: complete the lowest feasible lattice before zoom.
    # Thereafter spend ~1 in 7 post-coarse scouts on local zoom, unless
    # global quota exhausted. Never discard unscanned regions by DPS score.
    should_local = (not complete_grid_first and coarse_completed and
                    completed_local < opts["local_target"] and
                    (completed_surveys >= survey_target or
                     (len(observations) - coarse_total) % 7 == 6 or
                     fresh is None))
    chosen = _local_next(observations, measured, total=total,
                         lower=lower, upper=upper) if should_local else None
    if chosen is not None:
        candidate, anchor = chosen
        stage, level, cursor, origin = LOCAL, 6, None, list(anchor)
    elif fresh is not None:
        candidate, level, cursor = fresh
        stage, origin = SURVEY, None
    else:
        chosen = _local_next(observations, measured, total=total,
                             lower=lower, upper=upper)
        if chosen is None:
            return {"schema":SCHEMA,"status":"V307_NO_UNSEEN_GRID_TARGET",
                    "next_request":None,"global_optimum_proven":False}
        candidate, anchor = chosen
        stage, level, cursor, origin = LOCAL, 6, None, list(anchor)
    need(base.legacy.eligible(candidate,total,lower,upper)
         and candidate not in measured,
         "V307_NEW_CANDIDATE_BOUNDS_OR_IDENTITY")
    return {
        "schema": SCHEMA,"status":"NEXT_NATIVE_PROPOSED",
        "decision":"V307_"+stage.upper(),
        "next_request":{"phase":"scout",
            "target":base.legacy.to_target(candidate),
            "iterations":scout_iterations,
            "grid_stage":stage,"grid_level":level,
            "grid_cursor":cursor,"grid_origin":origin},
        "global_optimum_proven":False}



def audit_recorded_history(observations, *, total, lower, upper,
                           max_level=DEFAULT_MAX_LEVEL):
    """Audit committed *metadata* independently of original Native bytes.

    v291 authenticates the original SimC input/JSON2/receipt for each case.
    This pass additionally rejects missing/skipped global lattice cells,
    fabricated survey cursors, local anchors not previously measured and
    repeated confirmation vectors. One linear pass over sealed journal and
    cached finite level-order tuples; no SimC and no per-row full policy replay.
    """
    lower, upper = _params(total, lower, upper, max_level)
    need(type(observations) is list, "V307_HISTORY_AUDIT_LIST_REQUIRED")
    seen, confirmed = set(), set()
    last_cursor = {}
    precisions_started = False
    scans, locals_ = 0, 0
    for r in observations:
        v = _vector(r)
        need(base.legacy.eligible(v,total,lower,upper),
             "V307_RECORDED_RATING_OUTSIDE_BOUNDS")
        stage = r.get("grid_stage")
        need(stage in (SURVEY,LOCAL,CONFIRM) and
             all(k in r for k in METADATA),
             "V307_RECORDED_STAGE_FIELDS_REQUIRED")
        if stage == CONFIRM:
            precisions_started = True
            need(r.get("phase") == "precision" and
                 v in seen and v not in confirmed and
                 all(r[k] is None for k in
                     ("grid_level","grid_cursor","grid_origin")),
                 "V307_RECORDED_CONFIRM_TARGET_DRIFT")
            confirmed.add(v)
            continue
        need(not precisions_started and r.get("phase") == "scout" and
             v not in seen, "V307_RECORDED_SCOUT_SEQUENCE_DRIFT")
        if stage == SURVEY:
            expected = None
            for level in LEVELS:
                if level > max_level:
                    break
                order=ordered_new_level(total,lower,upper,level)
                cursor=last_cursor.get(level,-1)+1
                while cursor < len(order) and order[cursor] in seen:
                    cursor+=1
                if cursor < len(order):
                    expected=(order[cursor],level,cursor)
                    break
            need(expected is not None and
                 (v,r["grid_level"],r["grid_cursor"])==expected and
                 r["grid_origin"] is None,
                 "V307_RECORDED_SURVEY_SEQUENCE_DRIFT")
            last_cursor[r["grid_level"]]=r["grid_cursor"]
            scans+=1
        else:
            anchor=r["grid_origin"]
            need(type(anchor) in (list,tuple) and len(anchor)==4 and
                 all(type(x) is int for x in anchor),
                 "V307_RECORDED_LOCAL_ANCHOR_TYPE")
            center=tuple(anchor)
            need(center in seen and r["grid_level"]==6 and
                 r["grid_cursor"] is None and
                 v in geometry.residual_lattice(
                     total,lower,upper,6,center=center,
                     radius=max(1,round(total*.05))),
                 "V307_RECORDED_LOCAL_GEOMETRY_OR_PROOF_DRIFT")
            locals_+=1
        seen.add(v)
    return {"verified_metadata_rows":len(observations),
            "surveys":scans,"locals":locals_,
            "confirmations":len(confirmed),
            "unique_scouts":len(seen),
            "source_native_bytes_reauthenticated_here":False}

def coverage(observations, *, total, lower, upper, max_level=DEFAULT_MAX_LEVEL):
    """Truthful geometric coverage. Only observed, unique scout vectors count."""
    lower, upper = _params(total,lower,upper,max_level)
    observed={_vector(r) for r in observations if r["phase"] == "scout"}
    result={}
    for level in LEVELS:
        if level>max_level:
            break
        layer=set(lattice(total,lower,upper,level))
        n=len(layer & observed)
        result[str(level)] = {
            "feasible_targets": len(layer),
            "observed_targets": n,
            "unobserved_targets": len(layer)-n,
            "complete_at_this_resolution":n==len(layer)}
    done=[int(k) for k,v in result.items() if v["complete_at_this_resolution"]]
    return {"schema": SCHEMA,"levels":result,
            "highest_complete_level":max(done) if done else None,
            "total_unique_scout_vectors":len(observed),
            "user_grid_not_continuous_global_optimum_proof":True,
            "familywise_95_proven":False}
