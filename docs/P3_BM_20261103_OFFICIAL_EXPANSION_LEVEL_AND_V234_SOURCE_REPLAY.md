# P3-BM — Same-source Midnight character level and existing v234 Native-G replay
2026-11-03 · implementation on isolated `probe/chat-cache-v035-20261024`

## Scope / approved priority

This change continues the **same** v216 Environment Build chain for the 26 DPS specialties. The user's prior WorldStateExpressionID investigation is **closed** because it did not prove a useful canonical, season-wide loot discriminator. No new WSE parser, universal item DB, separate gate or optimization engine is being developed.

The desired sequence remains source-backed representative ordinary gear/weapons/4pc tier → authenticated/observed G where necessary → same-season highest-quality gem J, flask F, oil O (and E/L accounting) → v222 B/T → v098 target absolute CHMV and existing adaptive SimC, 95% classification, cache/cancel/resume. Exact Native G is optional where a valid season reference exists; it is **not** a mandatory all-26-spec gate.

## Implemented code (test code SHA `5bf0f7fca5daa8c63d3869da07df3aa414e3d802`)

1. `runner/v216_environment_build_coordinator.py`: a **source-scoped maximum-level resolver** `_source_expansion_level` returns level 90 only when `v163` uniquely joined same-build WCL-active zones and DB2 with `source_scope.source_basis=LIVE_WCL_ACTIVE_ZONES_AND_SAME_BUILD_DB2`, `expansion_id=11`, and game-major `12`. Explicit source is Blizzard's *Midnight Content Update Notes* published 2026-03-03: https://worldofwarcraft.blizzard.com/en-us/news/24244646. Versioned reference does **not** infer level from the item-level target, WorldStateExpressionID, user's current gear or last season's G; missing/unknown expansion/mismatched game major returns `SEASON_CHARACTER_LEVEL_SOURCE_PENDING` and `level=None`. This is an expansion level cap, reused across matching seasons, not a J/F/O budget.
2. Normal `v113.LocalJobs.collect_fresh_source` now passes already validated `user_scenario.character.race` and `.talents` to existing `v216.collect_wago_new_season_source` as `g_probe_character` **without asking the user for level or internal files**. `v216` retains compatibility with explicit level for internal callers; when omitted it only fills the proven source-scoped level. If source missing or explicit level conflicts with the authenticated cap, it reports `FRESH_G_PROBE_LEVEL_SOURCE_PENDING`; no unproven default.
3. Original v216→v232→v233 one-spec physical G profile is prepared/reused by v217, and a small per-request `fresh_one_spec_character_level_source` receipt is shown in the source response. The existing `v233` stage output remains `G=None, environment_ready=False`; no automatic SimC subprocess/extra Native occurs.
4. Original `runner/v234_source_only_one_native_G.py` now accepts optional `season_gear_db` (CLI `--season-gear-db`) and forwards it to `v233.build` so v232's selected actual v167 same-build IDs can be **replayed without drift**. The original `max_new=0` produces an exact Native plan with zero subprocess; `max_new=1` still requires explicit pinned binary SHA and one invocation at most, then existing v046 static JSON2 parser. No independent stat calculator, no new Native job, no relaxed numerical G promotion.
5. Changes are additive to the original public user controls and source API. No added general user level/seed/SHA/gear form, no old-session mutation, no full season DB, no special-effect simulation. Previously verified same-season static item cache and DPS cache identity policy are unchanged.

## Validation evidence

- [v212 offline contract run #41558072540](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41558072540): Ubuntu 24.04 and Windows 2022 each **428 tests, 0 FAIL, 4 SKIP**, SUCCESS.
- [v113 local web/API #41558072525](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41558072525): Ubuntu Py3.12 and Windows Py3.14 each **202 tests, PASS**, SUCCESS.
- [v181 Windows beta #41558072648](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41558072648): both Windows Python matrices **139 tests PASS**, existing live **local loopback HTTP** three-plan restore `V181_WINDOWS_BETA_LIVE_3_PLANS_RESTORE_ZERO_NATIVE_PASS`. This does NOT mean a new external Blizzard/Wago call was performed.
- [v182 UI #41558072611](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41558072611): Ubuntu and Windows each 92+81+focused2 offline tests PASS.
- New tests: official 12.x/expansion11 level90 with wrong game-major/expansion/unverified source pending; validates user race/talents before any source HTTP; v113 forwards user context to v216; v234 `max_new=0` with exact v167 selected source replays v233, produces JSON2 command without Native; missing v167 detects REPLAY_DRIFT. Final code/CI SHA above. Initial `de8c488...` feature commit and `5bf0f7fc...` test commit; final focused code SHA `5bf0f7fc...`.
- Newly executed real SimC Native subprocesses in this task: **0**. Newly collected external Wago/Blizzard/WCL/SimC HTTP: **0**. Reused existing source proofs/fixtures and GitHub CI; no numeric G/J/F/O or actual current-season tier/gear acceptance claimed.

## Technical boundaries and next slice

- Source-backed game-level contract now exists, but one-spec profile still requires the original v163 + v245/v250/v251 + v229/v232 source links. New fresh season without verified active scope or exact tier/ordinary gear remains PENDING, not a product READY.
- G observed via v234 is optional; real profile/source and compiled binary require exact same-build evidence and current-season slot membership. This change only prepares/replays the Native plan.
- Stage identity is already based on v217 source/output SHA. Review possible broad transitive `v216` module fingerprints and versioned stage outputs on a *necessary* future source-stage code modification to avoid wasting same-season HTTP/cache on implementation-only changes. Do not proactively replay native/all specs or clear existing static cache.
- Next highest-value task: use retained actual season source evidence to finish the selected 13/14 representative and tier membership or a valid same-season G reference, then one minimal v234 Native only where needed; in parallel authenticate highest-quality J/F/O with existing v221/v191 source stages and plug into v222. Restore the normal UI user → representative Build → optimization session; retain 95% statistical outputs and observed first/near alternatives.

## Authority

Only the authorized isolated branch changed. Main product development chat retains implementation/product Native ownership. `main`, immutable `v003`, original `v016`, Project UI/Sources, official Work OS/Shared State and WEQUIP remain untouched. This is a code+offline-acceptance result, **not** full Environment Build completion.
