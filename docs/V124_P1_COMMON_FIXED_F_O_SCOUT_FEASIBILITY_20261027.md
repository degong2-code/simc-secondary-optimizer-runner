# SIMC SECONDARY OPTIMIZER — P1/v124 universal fixed-component candidate feasibility

2026-10-27 · isolated `probe/chat-cache-v035-20261024` only · **new Python/Windows/CI PASS not yet observed**.

## New actual company Windows run — 3 Native, then BLOCKED

User resumed existing Rogue/Subtlety 334 / diamond 240967 / double oil session `04fe21c0e61b180d305f` after v123 Windows focused 106/106 PASS. User screenshot and supplied `V094_PROGRESS(5).json` show **completed_jobs=3 / planned_jobs=6, progress_percent=50.0, new_native_attempts=3, cache_verified_hits=0, PARTIAL_OR_BLOCKED, InjectionError:STATIC_TARGET_BELOW_DECLARED_FLASK_VECTOR**. Supplied `V094_SESSION_IDENTITY(3).json` shows **Fcrit165**, **Ocrit32/Ohaste32**, B3150/O64/T3214, SHA binary `b0ea12ee3ac233a4a590609e2a5bd4c4db45c5f8ae6f8994b1b8d0de4d5acff4`, revision `7bc1071`, 95% judgement only. Sealed identity/other user Native receipts are immutable. 3 completed jobs do NOT by themselves independently prove `240967` effect or raw JSON2 byte parity; no such acceptance claim is made without user-provided native files.

## Root cause and math

Existing v065 policy bounds rely on v062 `effective_floor_if_possible`, which protects user minima and Native-observed selected special-item fixed L. A separate v063 strict renderer requires each `gear_* = c_final - F` to be nonnegative. With oil fixed in gear override once, `c_final=B_candidate+O`, hence **for every stat k**:

```
B_candidate[k] + O[k] >= F[k]
B_candidate[k] >= max(0, F[k] - O[k], locked_L[k], user_min[k])
```

In the observed Rogue profile, **B_crit >= 165-32 = 133**. The first two seed jobs and one scout completed, then the *material scout* (10% B transfer, chosen by old L-only bounds) proposed a vector that could satisfy v065 search bounds but was refused by v063 as an impossible negative gear override **before a fourth Native run**. Do not loosen v063's negative-gear refusal or attribute F to arbitrary proc/talent mechanics.

## Common implementation (no per-spec optimizer)

1. `runner/v065_v015_scheduler_adapter.py`: `budget_with_fixed_components(normalized,static_budget,F,O)` returns a **deep copied bounds-only** budget with per-stat minima `max(exact_L/user_min, F-O, 0)`, validating F sum and exact O against the scenario. `policy.bounds` enforces feasibility. Original v062 budgets, source profiles, caches, session JSON and identity untouched.
2. `runner/v098_target_user_scenario_bootstrap.py`: *all six currently source-backed* newly planned seed pairs use the same augmented bounds. No altered B/O/T formulas or Native calls.
3. `runner/v096_unified_product_entry.py`: manifests validate all seed vectors against the same feasibility bounds at source-preflight time.
4. `runner/v093_inclusive_adaptive_scheduler_bridge.py`: `feasible_budget(context,F)` used in candidate request preflight (any phase), scout selection/observation checks and confirmation selection. The optional `start_scout(flask_vector=...)` is explicitly supplied by actual v094 runtime; older direct unit-test calls remain backward compatible. Only the native request builder validates/constructs gear/case keys and oil identity as before.
5. `runner/v094_durable_inclusive_adaptive_runner.py`: the **material** candidate choice and initial scout setup use augmented bounds. Thus seeds, ordinary scouts, material scouts and confirmation candidates use the same feasibility rule during product execution.
6. `tests/test_v124_fixed_component_candidate_bounds.py`: four new offline unit tests covering actual Rogue 240967 user manifest (crit F165/O32), 2h Warrior haste F165/O32, L dominance over fixed floor, impossible candidate refusal before native, candidate on exactly feasible zero gear override boundary, material-neighbor previously selecting illegal B and adjusted policy selecting feasible B, data drift refusal. All Native-shaped measurements are explicitly synthetic offline fixtures. `tests/test_v098_target_user_scenario_bootstrap.py` existing six-spec canonical profile test now checks generated seeds satisfy B+O>=F.

## Validation/continuation

- Prior v123 **Windows focused 106/106 PASS** precedes the v124 code. Never relabel as v124 PASS.
- **New v124 Windows/CI focused test PASS pending; code and tests are committed but not executed on user's Windows.** Expected relevant regression **110 tests** (prior 106 + new 4).
- Existing Rogue 3/6 session can be resumed *without clearing caches or changing session identity* after focused offline tests pass. The runner revisits the two seeds and scout through verified Native cache, and then chooses a newly feasible material target; if no other blocker, at most 3 new Native candidates complete the 6-call bounded session. Do not claim success before actual receipt.
- Final verify physical six ordinary gems/four colors and SimC Native socket/input/JSON2 acceptance separately; avoid independent proc-activation gate.
- Main, v003 immutable, formal Work OS/Shared State, Project UI, existing three Native result bytes, cache policy and 95% statistical policy remain unchanged.
