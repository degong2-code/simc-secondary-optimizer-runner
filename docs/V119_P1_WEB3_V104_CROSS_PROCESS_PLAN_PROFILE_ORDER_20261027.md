# P1-WEB-3 / v119 — v104 cross-process immutable plan/profile replay correction

2026-10-27 · isolated development branch only · Python focused Windows PASS **pending**.

## User-observed blocker

Company-PC Chrome test planned Rogue/Subtlety ilvl334 with `240967` special diamond and two weapon oils. `/plan` succeeded with `B3150 + O64 = T3214`, user session `04fe21c0e61b180d305f`, no Native execution. Clicking `SimC 최적화 실행` and then `같은 세션 재개` yielded `UserScenarioBlocked:EXISTING_BOOTSTRAP_FILE_CHANGED:profile.simc`, worker inactive, progress 0/6, Native cumulative 0. Previous Paladin completed session and cache are unaffected.

## Source-level root cause

`runner/v104_shared_pinned_rogue_shaman_composer.py` used `ALL_SLOTS=tuple(item_mod.SLOTS)`, where `item_mod.SLOTS` is a Python set. The loop `for slot in ALL_SLOTS` constructs the v104 full source profile/filler output in a process-specific order. `v113` web planning occurs in the long-lived Python webserver process while `v106` execution occurs in a newly spawned Python worker with a different randomized hash seed. The same slot names, IDs and options can be serialized in a different order, causing strict `v098.put_once(profile.simc)` byte equality to fail. This is consistent with the observed error and supported by code inspection; the new cross-process test must confirm it independently.

## Minimal implementation

1. `runner/v104_shared_pinned_rogue_shaman_composer.py`: canonical sorted slot tuple, preventing process-specific ordering in newly planned Rogue/Subtlety and Shaman/Elemental cases.
2. `runner/v098_target_user_scenario_bootstrap.py`: for only these two v104 archetypes, when a prior `profile.simc` is present, recover its equipment **slot order only** and use that ordering when serializing newly constructed rows. All item IDs, gem IDs, enchants, user options, source fixture bytes, profile hash, scenario/B/O/T and SimC mechanics are computed through the existing code. All `put_once` complete-byte checks remain mandatory. A malicious or semantically changed existing profile is **never** silently accepted or overwritten; if full rebuilt output differs, the existing `EXISTING_BOOTSTRAP_FILE_CHANGED` block remains.
3. `runner/webui/app.js`: a worker with `BLOCKED_OR_PARTIAL` now displays `실행 차단`, not generic `대기`.
4. `tests/test_v098_target_user_scenario_bootstrap.py`: create a `240967` plan in a separate Python process emulating the old reversed set slot order and `PYTHONHASHSEED=23`; replay the same immutable profile on a fresh Python process with `PYTHONHASHSEED=137` using the corrected canonical composer; require plan PASS, same profile bytes and **Native0**, both Rogue/Subtlety and Shaman/Elemental. Another regression confirms a truly modified profile fails closed and is never rewritten.
5. `tests/test_v114_local_web_ui_offline.py`: assert blocked worker state has an actionable label.

No main merge, change to v003, changes to formal Work OS / Project UI, new optimizer, cache invalidation or rewriting prior completed SimC results. User's prior 6/6 successful Paladin run remains separate historical evidence.

## Next Windows verification

From a fresh full ZIP of the latest isolated branch, in a new folder:

```powershell
py -3 -m unittest -q tests.test_v098_target_user_scenario_bootstrap tests.test_v101_common_representative_equipment tests.test_v114_local_web_ui_offline
```

Do not start Native if any test fails. If tests pass, close old Uvicorn, start `py -3 runner/v113_local_web_api.py --port 8765` from the NEW folder, open the existing local Rogue session `04fe21c0e61b180d305f` (read-only) and click `같은 세션 재개` ONCE; this can execute up to six Native candidates if preflight succeeds. Preserve the existing default `%USERPROFILE%\SIMC_Secondary_Optimizer\runs` directory and unfinished draft; no manual deletion/rename/repair. Observe worker log and progress. Once running, separately check physical six ordinary gem IDs/four colors in generated profile and SimC's actual socket acceptance. This is not an independent activation certification for proc semantics.

**Status:** source-level fix + regression definitions committed; actual user Windows Python and Native regression pending.
