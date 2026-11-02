# P3-BH — Same-build Wago item ↔ SimC gem property source join inside existing Environment Build
2026-11-03

## Authority / focus
Approved v1.4.3 + DPS26 + P3-AA single-engine policy; implementation on the isolated `probe/chat-cache-v035-20261024` branch only. This work is a **real implementation of the existing gem-source join into the original Build**, not creation of a second source engine or an assertion that new-season J is measured.

## Previously present, unused functionality
- `v161` already obtains a pinned same-build Wago `Item.csv` / `ItemSparse.csv` snapshot with original SHA, size, locale and build receipts.
- `v213` preserves pinned SimC gem_property records and source provenance.
- `v221_gem_item_db2_relation.join` already validates ItemSparse foreign key `Gem_properties` → actual gem item ID and joins only same-build, current-expansion candidates. Its result is **identity only, not highest-quality J, effect rating, socket applicability or User UI admission**.
- Before this change the normal `v216.build_environment` fresh-source branch did not call `v221`; users would have had to invoke the separate source join outside Build.

## Implementation
- `runner/v216_environment_build_coordinator.py` now contains `_fresh_gem_item_source_stage`, reusing **the original v221**, v217 receipts, the supplied existing `v161` snapshot and the fresh pinned v213 catalog. The stage seals `fresh_source/v221_new_season_gem_item_candidates.json` without HTTP, Native or optimizer cache mutation.
- It checks catalog game build against requested build and rehashes the two original DB2 tables against the v161 receipt **even on a cache hit**, then lets v217 verify the compact output SHA and reuse it without reparsing both big CSVs. This is deliberate data-integrity vs I/O balance: no Wago redownload or giant in-memory duplication; two bounded streaming hashes on replay.
- `preflight_new_season_source` can accept an internal snapshot folder and stage root, records exact-link count and stage receipt, but always leaves `J=null`, `environment_ready=false` and appends `GEM_J_HIGHEST_QUALITY_EFFECT_AND_SOCKET_BUDGET_PROOF`. It **cannot** promote physical ID join to proven numeric J.
- `build_environment(fresh_source_stage_inputs={...,"wago_snapshot_folder": existing_folder})` passes the optional snapshot to the same preflight **before any user session is created**. The four original fresh-source fields still work unchanged, and the option is **internal-only**. Current `v113.collect_fresh_source` separately collects sources but does not yet automatically compose all v191/v213 and numeric G/J/F/O into this Build path. Do not report finished normal user E2E.
- No new source collection loop, quality equivalence guess, lower-grade display, G/J/F/O numeric fallback, standalone second engine, historical static/DPS cache invalidation or automatic READY.

## Code and CI receipts
- Feature code: [`783b9da39bc071082966d27d15f2a5ef25fc4610`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/783b9da39bc071082966d27d15f2a5ef25fc4610).
- First feature CI [#41548052228](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41548052228) **FAIL 1** in a new test expecting a DB2 error for an already mismatched v213 game build. Correct code blocked earlier as `V216_FRESH_GEM_V213_GAME_BUILD_MISMATCH`; this historical failed CI is **preserved**.
- Test-only correction [`e28aade55edbeb66138ddd25310e188a1360c7a0`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/e28aade55edbeb66138ddd25310e188a1360c7a0) distinguished genuine v213 build drift from corrupted Wago snapshot build; its four Actions checks all **SUCCESS**.
- Added same normal Build pre-session route test, correcting its Python context-manager syntax before final acceptance. Latest functional/test SHA: `ab0eb108f9cc4f03481ea9dfa868dbb47ea67033`.
- [v212 contract #41548414140](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41548414140): Ubuntu/Windows each **417 tests, 0 FAIL, 4 SKIP**, including direct original v221 joins, exact cached receipt reuse, changed DB2 hash rejection, cross-build rejection and normal Build preflight wiring.
- [v113 offline API #41548414308](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41548414308): Ubuntu/Windows success.
- [v182 UI #41548414262](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41548414262): Ubuntu/Windows success.
- [v181 Windows beta #41548414349](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41548414349): check actual job completion/conclusion before claiming success.
- These tests are **deterministic offline fixtures** using re-used test snapshots. In this task actual external Wago/SimC HTTP calls=0, actual SimC Native=0; no actual live season numeric J/F/O/G measurement, no adaptive DPS E2E.

## Next concrete development (engine-first)
1. Reuse the same `v216` already-collected current-season `v163/v165/v167` and one-spec `v232` source receipts to resolve selected ordinary gear/weapons' **individual season provenance** before any G promotion. Prefer source-backed current-season candidates; old Localbots-only or M+ unknown world-state must not be promoted as genuine active-season G. Reuse `v226/v227/v228` and minimal exact Native if necessary; do not rerun all 26.
2. Extend exact J source physical item-to-property relation to independently verified highest-quality item's static rating, gem/socket eligibility and number of slots (never assume old J=138). Similarly independently verify F, oil O and permanent E/weapon applicability from same season and pinned SimC; no generic temporary-enchant expansion.
3. Feed only authenticated complete G/J/F/O evidence to the existing P3-BG `v222.preprofile_budget`, then v098 profile + `v222.reconcile`, v220/v196 Policy A and v212 install through **same** normal Build. No numerical budget from source-identity alone.
4. Finally run P3-AA clean-history same-engine control after normal Build actually creates a runnable environment.

**Scope/status:** P3-BH source relationship wiring implemented; **not** J budget solved or full seasonal Environment Build ready. User primary product chat remains owner; main, v003 immutable, original v016, Project UI, Work OS, shared state and WEQUIP authority unaffected.
