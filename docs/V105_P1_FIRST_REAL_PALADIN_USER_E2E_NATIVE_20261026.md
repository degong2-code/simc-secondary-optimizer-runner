# v105 — First actual P1 user-to-SimC-to-95%-result end-to-end Native SUCCESS

**Date:** 2026-10-26 KST. **Authority:** isolated GitHub development branch only; no merge to main, no v003 / official Work OS / Project UI update.

## New top-level user scope (authoritative direct decision)

The final supported set is **the 27 DPS specializations only**. Tank and healer specialization DPS optimization support is **explicitly withdrawn** from product requirements. The previous 40-spec/all-spec goal is historical, not the current requirement. Augmentation Evoker stays as a DPS specialization. Keep target-ilvl (334 default) or inclusive manual CHMV T, SimC DPS, 95%-only statistics, no gear recommendations. Do not mistake a GitHub document for an applied Project UI change.

## Exact implementation

- `integration_probes/v105_paladin_user_e2e.py`: minimal **real-user-input** deterministic Retribution Paladin scenario. Reads pinned legacy talents and two specific trinket IDs only to produce user-equivalent controls. User does **not** provide full equipped gear, profile, filler, static cache, Native JSON2 or initial search seeds.
- Delegates to **existing** `v098.build() → v096.run_manifest() → v094 durable native → v096.user_facing_result()`, no changed optimizer, new SimC parser, proc modeling, statistics or DPS solver.
- 334 source-backed 15 physical equipment slots, Paladin class-specific tier four pieces, one main hand 2H weapon, two trinkets, no selected embellishment/special (minimal simple scenario), one main-hand Thalassian Phoenix Oil. User simple target level `334`; internal default `B=3150`, fixed `O={crit:16,haste:16,mastery:0,vers:0}` so **`T=3182`**. This is **reference rounded** B, not a new exact gear G calculation.
- Exact binary SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`, revision `7bc10711b5`. Binary restored from existing GitHub Actions artifact `v050-exact-native-binary-40153209773` (not rebuilt or downloaded from unpinned external source).
- `tests/test_v105_paladin_user_e2e_contract.py`: offline user input, 6-request plan-only, exact O vector and absent Native output, fake ELF rejection. **183 focused offline tests** all pass in [#40334571704](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40334571704); the real job reran the six immediately relevant offline test modules (**56 tests PASS**).
- `.github/workflows/v105_one_paladin_real_user_native.yml`: one-shot triggered only by `integration_probes/requests/v105_paladin_real_once.json`, requires sole changed file exactly matching request JSON, binary SHA pin and fixed six-call cap; uploads exact profile, source inputs, 6 JSON2 reports, receipts, progress, cached replay proof. Do not retrigger that request automatically on source documentation updates.

## Real Native observation and receipt

**[Actions #40335091679](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40335091679) SUCCESS** at request commit `48cbc59fe18e1ac8b5cbbe8ac9374df9983c5e17`.

- All six **new real SimC Native** calls complete successfully: two seeds, one regular scout, one material scout, two independent confirmations. Budget **6/6** exactly. No new Native requests hidden in plan-only or offline tests. The Native JSON2 files are individually SHA256 recorded in the `V105_REAL_E2E_RECEIPT.json` attached to the run.
- **Observed highest sampled mean DPS: `179171.78518578838`**, **SimC SEM: `275.802156738869`**. These are scenario-specific sampled results, NOT all-gear true best or season general DPS.
- **95%-only selected confirmation pair direction supported: `true`**. Do not equate that with global statistical dominance or proven global optimum.
- **Material near alternatives observed in this six-call search: `0`** (none *found*, not proof none exists). Different user talents / special equipment / potion / higher precision may alter the result.
- Final progress **100.0%**; v094 durable progress/ledger and final JSON present. Second `v096.run_manifest(...,cache_only=True)` replays **all 6/6** exact cached JSON2 with byte-for-byte SHA256 parity, **0 incremental Native**. All fixed B/O/T, 95% output checks pass during replay.
- Retained Actions artifact **`v105-paladin-user-native-once-40335091679`** (artifact ID `12656746917`, upload size approximately 445,240 bytes). Includes actual Native JSON2, input/identity receipts, final v094 result and v105 real receipt. No GitHub documentation can replace the native bytes/receipts when detailed forensic evidence is required.

## What this does and DOES NOT prove

**Proven now:** one concrete ordinary user scenario actually travels **user controls → internally generated full source-backed SimC 15-slot profile → Native 6-call adaptive search → observed CHMV/DPS/SEM → existing 95% user-result format → durable progress and cache-only replay**. This resolves the specific missing *first actual P1 E2E Native smoke*, without adding a new solver or recertifying the historic static gear table.

**Still open:** full Windows one-click UI, broader configurable user gems/flask/food/potion/Omnium, cancellation exercised *mid-execution* (cancel code existed earlier but v105 did not interrupt the real run), Windows environment adaptation, exact native G optional path, every supported spec's complete base-input effect correctness, all DPS 27 active. One actual real success does not prove every source special/catalyst-original proc behavior or a globally optimal CHMV.

## Next efficient P1

1. Convert current CLI arguments and existing progress/results to a **user-friendly single start entry** reusing the same v098/v096/v094 code, with output folder opening on Windows, cancel/resume and old cache identity respected; **no new Native required** for basic UI contract tests.
2. Add user-driven **gem/flask/food/potion/Omnium** selectors to exact SimC serializer, guarding budget J/F and profile SHA. Expand actual Native smoke only on a changed input behavior.
3. Use small source-mapped configs for the other 5 currently source-backed specs and gradually remaining 21 DPS specs; no all-gear catalog or repeated initial search on every spec.

**Efficiency note:** the single six-iteration set cost six actual SimC calls (two seed, one scout, one material, two confirm); immediate successful cache-only replay cost zero. Reuse same-season immutable static item cache independent of SimC revision, and exact Native DPS identity includes binary/revision/character/equipment/consumables/combat/iterations. No new expensive per-item or proc-specific gate.
