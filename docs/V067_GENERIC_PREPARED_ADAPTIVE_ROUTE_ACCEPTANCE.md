# v066–v067 — Profile-neutral Scenario Preflight and Reused v065 Adaptive Runner

**Date:** 2026-10-25 (Asia/Seoul). **Status:** isolated branch development PASS, not official product MAIN integration. **Authority:** user-applied Project Source `SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.2_PROJECT_SOURCE_REPLACEMENT.md`.

## Purpose / scope

Previous v065 showed 334 Arcane Mage native adaptive scouting, then two fresh 320-iteration confirmations. That driver still created its setup from a **Mage-only 334 Native reference**, `G=2849`, `T=3152`, and binary SHA `64089f2f...`.

**v066** moves setup to external inputs: exact v061 scenario, 13-slot representative *filler* items, Native static item-variant cache, full SimC profile text, two numeric Native JSON2 witness cases, requested SimC binary SHA. It recomputes official v1.2 `T=G+J+F` from actual selected static nontrinket records, locks only selected special L, and derives the **numeric input→final JSON2 offset for this exact profile alone**. It rejects absent nontrinket variants, profile drift, missing numeric witnesses and mismatched user-supplied SHA; unknown static trinket never blocks selection. It never changes the user-selected profile equipment, APL, item options or effect mechanics.

**v067** exposes this v066 preparation as a thin CLI route to the **existing v065 scheduler and Native runner**, rather than copying the adaptive candidate algorithm. v065's existing entrypoint now permits an externally prepared context and a scenario-scoped binary SHA. A new `--cache-only` mode forbids launching Native when the corresponding exact cached result is absent; it does not automatically rerun failed/missing executions. The full v065 candidate selection and confirmation implementation is reused unchanged.

The previous v065 receipt did not contain the newer `scoped_simc_binary_sha256` field. A narrow backward-compatible resume permits that missing field **only in cache-only mode with all four prior attempts already spent and identical scenario/budget/calibration/source identities**. Each of four exact Native case files/receipts must then independently pass v064 key+JSON2 SHA256+numeric rating and source input verification. Non-cache-only legacy migration is refused. No old execution artifact was rewritten as the source of truth.

## Actual CI and controls

- [v066 initial FAIL #40174795749](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40174795749) — seven new synthetic tests used a 320-iteration legacy baseline while the generated scenario had confirm cap 60. No Native calls.
- [v066 second FAIL #40174887668](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40174887668) — a new test expected an InjectionError, correctly got PreflightBlocked for cross-profile calibration rejection. No Native calls.
- [v066 PASS #40174975829](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40174975829) — **357 tests: 355 PASS / 2 SKIP**. Two previous **real** v063 Arcane Native JSON2 numerical witnesses replayed; exact static `G2849+J138+F165=T3152`, profile-specific observed haste +165 numeric offset and next v015-derived CHMV proposal. **0 new Native calls**.
- [v067 first FAIL #40175453559](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40175453559) — true archived v065 `V065_PROGRESS.json` lacked the newly introduced scoped-binary-hash field; **strict block** before any Native call. Logs and failed receipt retained.
- [v067 corrected PASS #40175621237](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40175621237) — **364 tests: 362 PASS / 2 SKIP**. Reused v063's two real Native calibration outputs and **v065's four actual adaptive Native case outputs**. With `--cache-only` and verified pinned binary, all four v065 cases returned verified cache hits, cumulative Native-attempt count stayed **4**, every archived result JSON2 SHA256 stayed byte-identical, and **0 additional Native calls**. Original [v065 Native receipt #40171473855](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40171473855) remains unchanged.
- v067 PASS artifact `simc-v067-generic-route-zero-native-40175621237`, GitHub-reported ZIP digest SHA256 `88382e8ff1c6968b487b788dfe4bc27c7974201f68288f18d8cc8a45c850f00a`.
- Neither legacy v015 71/71 nor v016 104/104 was rerun; those remain historical receipts. Original v015/v016 ZIP bytes remain intact.

## Precise acceptance boundary

**PASS:** generic data-flow and exact input/runtime identity without Mage constants in new v066/v067 entrypoint, reuse of one v015-derived scheduler, exact G/J/F budget, per-profile numeric offset, independent prior Native witness selection, strict result cache, fail-closed cancel/cache-only behaviour, existing Arcane real Native case replay.

**NOT YET PROVEN:** non-Mage actual SimC profile item compatibility, 27+/tank/healer specialization Native success, automatic representative equipment assembly for arbitrary spec/ilvl, automatic collection of the two necessary *new* numeric calibration witnesses, independent numeric attribution of gem/enchant-laden Native static rows, flexible iteration policy in the underlying v065 bounded 2-scout/2-confirm pilot, full production explorer UI/convergence. Synthetic warrior unit fixtures are *input-structure checks only*, not a Warrior Native PASS. The user still must provide exact selected item IDs/options and a fully valid class profile until the profile assembler/Native bootstrap is implemented.

No SimC item effect/proc/trigger certification gate, no full item gear database and no WEQUIP runtime dependency.

## Exact next implementation

1. Profile-neutral **two controlled numeric Native witness bootstrap** for any SimC-valid specialization profile; obtain the two profile-scoped offset observations by varying only gear rating overrides. Strict ≤2 Native calls, no independent proc verification.
2. Native static cache augmentation only for missing exact chosen nontrinket gear variants, without season-wide refresh or automatically discarding static cache across SimC revisions.
3. Enable spec/scenario-configurable scout/confirm iterations within bounded budget, then run at least one true non-Mage class profile with exact item selection, rate parity and DPS/SEM, without interpreting proc details.
4. Existing scenario/runner can evolve into progress/cancel/resume UI with near-best statistically meaningful alternatives.

**Product status:** active development in the original user product chat. GitHub `main`, Work OS `CURRENT`, Project Instructions, Project Sources and original v003 immutable files are unchanged.
