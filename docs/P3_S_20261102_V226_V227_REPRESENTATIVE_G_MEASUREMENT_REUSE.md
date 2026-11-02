# P3-S — v226/v227 new-season representative G work planning and exact Native static cache reuse

Date: 2026-11-02 KST | Isolated branch `probe/chat-cache-v035-20261024` | No main/Project UI promotion

## 1. Purpose and ownership

Engine, not feature-specific scripts. Reuse:
- **v225** exact source bundle SHA/manifest and season-change guard, with G source gear/tier identity distinct from J/F/O budget source;
- **v169/v167/v143** existing 26-DPS representative four-tier, ordinary armor, common slots, primary-compatible weapon/form selector (no reimplementation or blanket gear recommendations);
- **v046** existing immutable same-season Native JSON2 static variant cache and `selected_gear_sum` arithmetic (no competing stat calculator);
- **v222/v216/v098/v106** downstream budgets, actual profile, sessions and adaptive SimC, unchanged in this increment.

`v226_representative_native_g_work_order.py` is **one requested spec × one target ilvl** only. It validates v225 bundle, picks representative 4-set pieces (head, shoulders, hands, legs), plain chest/wrists/waist/feet, neck/back/two rings, and correct one/two weapons. Its output contains exact per-slot item IDs, same-season gear/tier SHA256, target ilvl, weapon form, deterministic work identity, and the future **narrow static Native measurement request**. It **does not execute Native**, create a DPS user session, assume a season-level G, or copy a character's existing equipment.

The selection source is a compact representative candidate DB, not a full gear recommendation/loot DB. Weapon subclass/primary metadata is a source prefilter; actual SimC physical proficiency and resulting static rating still need Native/runtime validation. Distinct configurations are not assumed to have equal G solely because their armor/weapon type matches.

`v227_cached_native_g_observation.py` reads existing v046 static cache and matches **season + exact item ID + ilvl + normalized slot + no item modifiers** for *every* requested baseline non-trinket slot. It requires Native JSON2 source kind, consistent existing static digest and native revision/hash metadata; any missing record becomes a specific work request (**NOT zero**). On a complete exact match, it reuses `v046.selected_gear_sum` to expose `observed_G_vector_if_complete` and `observed_G_total_if_complete`. Critically, it does **not** use v046's historical J=138/F=165/T convenience fields. The output still says `G=null`, `B=null`, `T=null`, `environment_ready=false`: the historical cache does not independently identify the source game build of each native variant, and a freshly generated representative profile and E/L accounting are not yet attested for this new build. Observations are not final product-certified G.

## 2. Stage connection and update strategy

```text
Explicit new-season source artifact
    -> v225 verified bytes/origin declaration; J/F/O independently pending
    -> v226 requested spec+ilvl representative IDs / one static G work order
    -> v227 exact v046 cache lookup for those slot variants
        -> complete: observed G vector and total, still no new-build attestation
        -> partial: only missing exact IDs/ilvl/slot become next Native requests
    -> [FUTURE] attach trusted same-build Native JSON2 / representative profile
                proof and validate scaling across levels only where evidenced
    -> [FUTURE] choose same-season G reference or exact result,
                reconcile J/F/O and E/L/O, B/T via v222 -> v216/v098
    -> existing 26-DPS adaptive SimC optimizer; 95% statistics unchanged
```

Same-season v089's 79×2 rounded reference remains valid only for its historical season and conditions. Do not borrow it, J138, F165 or per-oil 16+16 when new game build/season begins. If another requested ilvl is not proved by a valid exact Native reference or validated scaling calculation, generate a targeted request instead of interpolating unsupported values.

Cache identity: `v226.work_identity_sha256` includes physical gear/tier source bytes, game build, season, target ilvl, exact per-slot IDs, class/spec and weapon form. J/F/O budget-file changes **do not** force an identical physical G measurement; their own component proof and subsequent B/T/DPS identities still change separately. SimC revision alone does not remove a same-season static cache record, while actual binary/profile/iterations/combat/O continue to define DPS cache identity.

## 3. Implemented files and CI results

- `runner/v169_source_first_representative_stage.py` accepts both package and direct-run imports without changing its gear-picking semantics. Existing independent v169 current-season offline workflow [#41385411686](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41385411686) SUCCESS, plus [v172 stage #41385411716](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41385411716) SUCCESS; no Native.
- New `runner/v226_representative_native_g_work_order.py` + `tests/test_v226_representative_native_g_work_order.py`: requested retribution 13 G slots, Fury TG 14 slots/two 2H weapons, all source IDs exact, unsupported healer/tank/augmentation blocked, target-ilvl work identity changes, J/F/O budget-file change alone does not invalidate G work, source SHA drift blocks, no full 26-spec Native sweep.
- New `runner/v227_cached_native_g_observation.py` + `tests/test_v227_cached_native_g_observation.py`: empty/partial cache, exact numeric four-stat G observations, wrong season/ilvl/metadata/static digest rejected, SimC revision changes alone don't evict same-season static entries. Numeric cache examples in tests are **synthetic fixture values**, not newly measured Native results.
- `.github/workflows/v212_environment_manifest_offline.yml`: focused Ubuntu and Windows offline CI.
- `.github/workflows/v191_unified_season_data_update.yml`: on explicitly requested `new-season-core`, additionally stage one requested class/spec G work order after v225 source validation. The workflow still does not execute Native, mutate caches or mark the environment READY.

Actual verification:
- initial [v212 #41385556594](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41385556594) FAILED in Python compile due to a v226 parenthesis typo; fixed in `2b5384629623495b0827274c7d20457a429737e8`.
- [v212 #41385607599](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41385607599) Ubuntu/Windows **164/164 PASS** each; no Native.
- [v212 #41385877222](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41385877222) Ubuntu/Windows **181/181 PASS** each, including v227; no Native.
- New-season GitHub workflow dispatch with actual newly collected source Artifact and real external Native measurement **not yet executed**. A synthetic fixture is not a proof of real-season readiness.

## 4. Next meaningful implementation

1. **Real new-season core source acquisition** into v225 artifact (current input is a supplied artifact, not an actual collection job); preserve game build + season independently, source item IDs and original response receipts.
2. **Targeted new-build Native JSON2 provenance/measurement**: bind the v226 precise source/slot/ilvl request to actual SimC binary, generated representative physical profile, static JSON2, source build and hardware/weapon layout. Reuse existing exact v046 variants and native observations; avoid a new optimizer and universal Native loop. Once independently authenticated, promote the exact G and optionally prove an ilvl scaling/ref table.
3. **J/F/O verified effects and top-quality equivalence**, then auto B/T via v222/v216 and normal profile/session/cache identity, respecting user manual final T, G-internal L/E and fixed O. Keep optional modules separate.
4. User-ready 26-DPS actual environment and adaptive DPS execution; preserve cancellation/resume and SEM/95% result semantics.

This is an isolated development report. It neither asserts original v016 integration nor Project Sources installation, main merge or Work OS promotion. Existing real Native 26-DPS historical evidence stays historical.
