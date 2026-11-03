# P3-BO — v189 pinned SimC + v190 same-build Wago consumable item stage

2026-11-03 | isolated implementation and verified CI on `probe/chat-cache-v035-20261024`

## Purpose, within existing product scope

Resume the original G/J/F/O seasonal Environment Build; retain 26 DPS, SimC DPS as objective, internal representative gear, 95% statistical interpretation and cached adaptive engine. SimC owns effects/APL/procs; our environment code owns item/quality selection, G/J/F/O, L/E/oil accounting and profile creation. No new optimizer or season-wide WSE research.

The original `v189_simc_consumable_embellishment_discovery` and `v190_consumable_item_snapshot_join` were already written and tested but not reachable from normal `v216.collect_wago_new_season_source`. This implementation reuses both instead of duplicating a collector.

## Code changes

- `v216._fresh_consumable_item_source_stage` activates only with the existing *unique* v163 WCL/DB2 same-build season scope and original v229 full-length pinned SimC revision receipt; missing scope or seed stays **PENDING** without a network request.
- Fetches a single small `engine/player/unique_gear_midnight.cpp` at the already pinned revision through **existing v189**, then uses **existing v190** to join consumable item ID/class/subclass/expansion in the **already collected** same-build `v161 Item.csv` and `ItemSparse.csv`. The stage makes zero new Wago table GETs and zero Native calls.
- v217 seals exact C++ bytes, v189 evidence and v190 candidate JSON; identities include v163 candidate bytes/receipt, v229 source receipt, game build, expansion ID, SimC revision and original Wago Item/ItemSparse SHA. Repeating the same input reuses the output with **zero incremental HTTP and zero new receipt writes**. Changed v163 input bytes fail closed without a refetch.
- Source status added to the normal collector response as `fresh_food_potion_item_sources`. A test/injected Wago transport does not trigger public SimC network without explicit SimC transport. Unsupported future parser layouts remain pending and do not turn an unverified optional item into an environment-wide blocker.
- Produced evidence covers **food and potion item candidates only**. Source handler registration, gear ID, expansion, or item class does not prove maximum quality, real SimC input applicability, effect strength or user eligibility. `ui_selectable=false`, `J/F/O` and main `G/J/F/O/B/T` remain **null**, no READY, no Policy A promotion. Existing historical static/DPS caches untouched. The optional stage may retry a small source file on a subsequent request if parsing failed.

## New and historical verification, scoped honestly

Functional and final tested code SHA: `a831bbfdea07a10f50ef85cf1f49c79aa0506b74`.

- [v212 environment contract #41564705945](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41564705945): Ubuntu and Windows **430 tests each / 0 FAIL / 4 SKIP**.
- [v113 local web #41564705863](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41564705863): Ubuntu/Windows **206 tests each PASS**.
- [v181 Windows beta #41564705853](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41564705853): both Windows Python matrices **142 tests PASS**, existing local HTTP 3-plan restore.
- [v182 UI #41564706079](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41564706079): both OS **92+82+2 focused tests PASS**.
- The initial `7797a62f...` and `e949ca7b...` commits failed v212/v113 CI because the existing collector's synthetic transport still expected exactly **7** SimC source calls, whereas the new optional stage attempts its additional small pinned source. This was corrected by supplying the pinned source fixture and testing **8 first-pass / 0 incremental repeat**; the above final SHA is green.
- These are **synthetic/offline CI and existing local loopback HTTP**, not new live Wago/Blizzard/SimC validation. Actual newly executed Native **0**, actual new external data retrieval by this coding task **0**. The engine's single extra pinned GET was validated with a mocked transport.

## Next steps (unmodified priority)

1. Authenticated same-season 13/14-slot ordinary equipment/weapon and 4pc tier, existing precise G reference or one minimum v234/v236/046 Native observation where evidence is genuinely lacking.
2. **Mandatory quantitative J/F/O**: reuse v221 gem property→physical item ID, establish highest-quality gem J, flask F and per-hand valid oil O with exact same-build SimC evidence; no invented carry-forward F=165/J=138/oil values.
3. Existing v222 B/T contract, manual final T priority, L/E/O once-only, user-verified choice registration, existing v098/adaptive SimC session, cache/cancel/resume and 95% statistical outputs. Do not turn optional food/potion IDs into a new mandatory gate.

## Authority and non-actions

Original main product development chat retains ownership. No `main` merge, immutable v003/v016 changes, actual Project Sources/Instructions/Work OS promotion, WEQUIP dependence or other Git branch modification.
