# v059 — Selected Equipment → CHMV Candidate → SimC DPS Bridge

**Executed 2026-10-25. Status: bounded native bridge PASS; not v015/v016 product integration.**

## Requirement and authority

Latest explicit user direction: **Trust SimC for all gear effects and DPS, and do not expand into independent proc/effect validation.** Our code owns only gear selection, CHMV rating budget/floors, constructing candidate SimC inputs, repeat-result caching, validating numeric CHMV assignment, and extracting DPS/uncertainty.

This code resides on isolated branch `probe/chat-cache-v035-20261024`. No GitHub `main`, Developer Notes v1.0, v003 immutable, Work OS, CURRENT, or Shared State modifications. Official v1.0 excludes oil from its formula; user-approved oil-inclusive pilot is **bounded**, not silently promoted as official product policy.

## Sources reused; what is newly implemented

- `runner/v055_simc_item_selection.py`: selected item id/ilevel/options pass-through, including trinkets without a reported static stat, as proved by previous v056.
- `runner/pilot.py` and byte-pinned `inputs/v031r3_reference.simc`: original full Mage representative character/gear/consumable/omnium/4pc/2-embellishment profile. No reimplementation of SimC APL or item effects.
- Prior v036 Native 334 gear report: non-trinket static `G=2849` for this old 334 profile; v042 differs by +1 due to changed head, and is not substituted.
- `runner/v059_candidate_runner_bridge.py`: exposes `project(proportions,total,floors)`, `plan(reference,selection,targets,...)`, `compose_input`, `observe_result`, and `compare` as boundaries for an existing adaptive engine to call. Native result cache keyed by selected input profile SHA, exact rating target, iterations, calibrated profile delta, and pinned binary SHA. Appends JSON2 report URL per case and reuses saved Native result only with consistent hash and final rating. No independent effect support gate.
- `tests/test_v059_candidate_runner_bridge.py`: 14 new bounded tests covering budget/floors, unreported-stat trinket, preserves original two embellishments, candidate cache identities, input override arithmetic, observed stat parity, DPS/SEM, and inconclusive comparison.

## Native acceptance: CI run #40157655114

[Actions run](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40157655114) **SUCCESS**.
- Trigger sha: `08c309ef31fb1a9119252b633d1d34cb34e36c4f`.
- Workflow: `.github/workflows/v059_candidate_two_native.yml`, bounded max 2 Native calls, 60 requested iterations per case.
- Full offline suite: **258 tests; 256 PASS, 2 SKIP**.
- Binary SHA256: `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`; one earlier SimC source commit, no new builds.
- Artifact `simc-v059-two-candidate-DPS-40157655114.zip`, SHA256 `56002f118cb85cbc7e32aa1c0fc3a0149e7bd7ca0e96b1b96b586b3ddf836288`. ZIP CRC PASS; case-by-case input, Native JSON2, stderr/stdout and exact receipt present.

**Only bounded 334 Arcane Mage proof, no globally optimized result:**

| Result | Candidate A | Candidate B |
|---|---:|---:|
| CHMV Crit | 600 | 750 |
| CHMV Haste | 1140 | 990 |
| CHMV Mastery | 1115 | 1115 |
| CHMV Versatility | 329 | 329 |
| Total T | 3184 | 3184 |
| SimC actual CHMV | exact 600/1140/1115/329 | exact 750/990/1115/329 |
| DPS mean | 192324.1023 | 191574.5434 |
| DPS SEM | 1379.5784 | 1285.6370 |
| DPS sample count | 59 | 59 |

Difference (B−A) −749.5589; approximate independent 95% difference halfwidth **3696.0940**. **Not statistically separated**, no winner declaration. This is a candidate-evaluation interface and an illustrative pair, not full automatic search convergence.

Pilot budget `T=G2849+J138+F165+O32=3184`. Nontrinket G from v036 gear, excludes external trinket secondary. Oil vector (16 crit,16 haste) fixed inside T. The v031r3 scenario's observed SimC haste-flask static addition is calibrated at +165; this benchmark's gear_haste_rating override subtracts it **once**. This specific delta is *not automatically transferable* to all specs/ilvls or other flasks. Requested-to-actual static parity is independently measured in JSON2.

## No extra SimC domain work

No APL changes, no item proc emulation, no check whether Mindpiercer proc “works,” no model of arcanoweave proc, no equipment recommendation or wide candidate scans. SimC accepts the selected IDs; SimC owns resulting mechanics and DPS.

## Next integration boundary (not claimed)

The actual v015/v016 product source is not present in the GitHub v059 isolated repo and has not been independently inspected. Connecting its existing adaptive scheduler to the exposed `plan/compose_input/observe_result/compare` functions requires obtaining its actual source lineage; v037 previously integrated with a byte-preserved *v032* runtime only. v059 does **not** rewrite or supersede either optimizer, and no formal Work OS M0 authority is required for ordinary product tests.
