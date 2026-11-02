# P3-P — Installed-season G/J/F/O verification wired to real Environment Build

2026-11-02 | isolated branch `probe/chat-cache-v035-20261024`

## Implemented (not new-season auto refresh)

- `v216_environment_build_coordinator.py` automatically selects the fixed app-local v223 G/J/F/O source verifier when an installed, exact `data/current_season_source_to_catalog.json` exists and no selected special L, embellishment or unverified fixed E is present. No new UI input, generic collector or competing profile generator. Options requiring exact L/E continue through the existing path and retain the explicit `INSTALLED_REFERENCE_ONLY_GJFO_REFRESH_NOT_VERIFIED` limitation; they are not marked proven by this verifier.
- Source-bound G/J/F/O uses the existing v213+v191 SHA-proven current-season gear, tier and CHMV source files, the historical v089 79×2 rounded **same-season** Native-derived reference, v091 oil handling, and v222 B/T contract. **This is a consistency/reference proof, not exact new Native G measurement, new quality equivalence validation, or permission to register new user options.**
- Important corrected discovery: v098 persists **pre-oil** `generated/profile.simc` and `generated/scenario.json`. The real SimC candidate oil token is assembled by the **existing v091.configure**, not stored in the original profile. The new v223 audit now replays that exact serializer from sealed source profile/scenario and verifies hands, original profile SHA, token and O vector without altering files or reimplementing oil effects.
- `v216` receipt includes source input SHA, rounded-reference flag, existing plan B/T/O and profile-oil serializer status. A previously sealed budget's source SHA cannot change in the same session, even if B/T arithmetic happens to remain equal. The check occurs **before writing** the environment manifest or receipt. The existing v106 session identity already binds v213 source, gear/tier/budget bytes, user, binary, revision, selections and static cache; no gratuitous new session-key version was added. No cached DPS/static item bytes were touched.
- Existing status remains `SEASON_GJFO_AUTO_REFRESH_NOT_VERIFIED`, because **new-season G/J/F/O sourcing, higher-quality effect equivalence, universal L/E and exact option/slot verification, user catalog atomic auto-admission, and product-level automatic B/T regeneration are incomplete**. This is a **current-season installed-data audit**, not finished new-season DB engine.

## Actual tests and failure history

- Pre-correction [#41377954832](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41377954832) focused **FAIL**, because a v223 fixture stored the profile in the old directory. [#41377954892](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41377954892) Windows **FAIL** because the new verifier incorrectly expected an oil token already present in the v098 pre-oil profile. Both are retained as failed evidence; no Native was run.
- The actual v098 pre-oil profile and v091 serializer were inspected/tested; oil verification now replays the existing adapter.
- [#41378433042](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41378433042): Windows Python 3.12/3.14 both **SUCCESS**, exact v213 source linked; actual generated v098 Paladin source profile G/J/F/O verification PASS; extracted Windows launcher, loopback HTTP 3 product plans/restore PASS, existing 138 offline regressions PASS per matrix. Native0.
- [#41378567804](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41378567804): Ubuntu **108/108 PASS**, Windows **108/108 PASS**, including newly added immutable proof-source drift test. Native0.
- [#41378662841](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41378662841): Windows 3.12/3.14 both **SUCCESS**; real local HTTP Build returned v223 source-proven, v091-replayed budget receipts for:
  - Paladin Retribution, ilvl 334: B=3150, T=3182
  - Warrior Fury, ilvl 321: B=3170, T=3234 (two-weapon O=64)
  - Mage Frost, ilvl 344: B=3290, T=3322
  Existing 138 offline tests PASS per matrix, no Native.
- [#41378662943](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41378662943) existing UI/Omnium offline workflow **SUCCESS**. This does not mean optional Omnium module conversion is complete.

## Runtime cost and boundaries

Default app-local source verifier performs read-only SHA+JSON checks on three already installed small source files and one historical reference table; a short pre-oil profile/scenario is verified via existing v091. Repeated plan execution stays within existing v216 receipt/idempotence and v217/v218 profile stage reuse rules. No additional source network calls, Native SimC runs, redundant collectors, cache mutation or new full 26-spec sweep. Historical v176 physical baseline and other Native receipts are reused within their original scope; **no global adaptive optimization acceptance is claimed**.

## Next priority

Within the **same** v191→v211→v213 source and v216 Build pipeline, implement request-driven season change acquisition/verification for **G, J, F and O together**, with a versioned source-to-budget evidence producer and fail-closed Build if any mandatory component is unknown. Confirm top-quality exact effect/conditions and SimC input ownership before auto-registering through existing v220→v196, then feed a new B/T and profile into existing v098/v094 with cache versioning. Preserve manual T, fixed L/E/O accounting, 26 DPS, SimC effects owner, 95% statistics, optional Omnium separation and user ownership/branch restrictions. Avoid rebuilding full season equipment DB or universal Native loops.

This document is a repo handoff addendum; it does not assert Project UI installation, CURRENT replacement, main merge, original v016 byte acceptance, or official Work OS promotion.
