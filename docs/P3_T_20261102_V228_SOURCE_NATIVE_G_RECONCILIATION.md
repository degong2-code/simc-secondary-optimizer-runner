# P3-T — v228 raw Native JSON2 ↔ representative G source/profile reconciliation

Date: 2026-11-02 (KST). Isolated development only; no main merge, Project UI update, v003/v016 promotion or Work OS promotion.

## Goal

Carry forward P3-S without inventing an independent stat simulator, season reference table, or full 26-spec Native sweep. A new season's representative equipment source must be checked against the actual static item observations from a pinned SimC JSON2 file **before** any G is accepted. The existing v046 Native JSON2 parser and v227 static G observation adapter remain the owners of item stats and arithmetic.

## Exact data path

```text
v225 fixed manifest + gear/tier/budget source files (read-only)
    -> v226 one-class/spec/itemlevel representative G work order
    -> v228 receives source bundle + exact work-order receipt
                   + profile.simc bytes + Native JSON2 bytes
    -> independently regenerate v226 from same v225 source/season
    -> reconcile all 13/14 physical slot IDs/ilvl between source work order,
       profile equipment declarations and Native JSON2 gear array
    -> require bare equipment (no gem, flask, oil, enchant, gear_rating override)
    -> compare JSON2 git_revision prefix with pinned SimC source revision
    -> existing v046.native_records (unknown nontrinket static fields blocked)
    -> temporary in-memory v046 cache + existing v227.observe
    -> observed G vector/total, Native file hash and profile file hash
       (NO final G/B/T promotion; no Native launches by this verifier)
```

The temporary v046 cache is never written to disk. Missing slots and variants block the actual JSON2 reconciliation; the earlier v227 standalone cache path still reports only the exact missing Native variants for targeted follow-up. Slot normalization follows v046: shoulder→shoulders, wrist→wrists, hand→hands, ring1→finger1, ring2→finger2. A pooled ambiguous `finger` entry is not sufficient to distinguish the two representative ring items. Trinkets are excluded from G and are not silently made zero; this particular **bare representative measurement** requires the 13/14 G-only pieces to match exactly and rejects extra trinket lines in its evidence.

## New v228 and validation boundary

`runner/v228_source_native_g_reconciliation.py` is an artifact-intake **reconciler**, not a Native launcher. It validates:
- exact work-order receipt sha and regenerated v226 work-order identity (prevent mixing different gear/tier/season);
- profile `class=character`, `spec=...` and exactly one bare `slot=...id=...ilevel=...source=local` record per G slot;
- no unrequested second class, oils/flasks/gems/enchant values or stat overrides;
- Native JSON2 exact observed gear IDs/levels/slots/options and `unknown` stat handling through existing v046;
- pinned SimC commit revision prefix; read-only source and Native/profile SHA256 identity;
- v227 G vector arithmetic with **no** historical J=138/F=165/T or oil O value adopted.

**Known remaining authentication gaps:** the JSON2 gear match is strong physical observation, but does **not** independently prove that the precise `profile.simc` bytes were the executed input; JSON2 `git_revision` does not independently authenticate the compiled game DB build of the actual binary, and v225 recorded source URLs/manifest hashes remain unverified upstream origin declarations. The source-bound observation is therefore `observed_G_total` / `observed_G_vector`, not an approved `G`. `G/J/F/O/B/T` remain null, `authenticated_new_season_G=false`, `environment_ready=false`.

Consequently a fabricated JSON2 fixture passing these structural tests is **never** reported as a new-season Native experiment. Real same-build origin, executable SHA, source collection proof, execution provenance and static L/E/gear accounting must be linked before promotion. Full user-created profiles, trinkets and selected special gear are handled downstream by existing product paths, not automatically approved from this bare-G source check.

## Verification and efficiency

- Added `tests/test_v228_source_native_g_reconciliation.py` for synthetic exact gear, incomplete item or wrong ilvl, extra/offhand/trinket and aliased slots, ambiguous ring mapping, character contamination, gem/oil/flask/enchant overrides, tampered work receipts, bad SimC revision, Native unknown fields, Fury dual 2H and deterministic CLI receipt. These tests intentionally **do not claim real SimC Native results**.
- Integrated into existing Ubuntu/Windows `v212_environment_manifest_offline.yml` focused contract workflow; no new CI workflow or expensive source-fetch stage. No Native calls or persistent cache writes in this phase.
- [Actions initial 198/198 PASS both platforms](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41387404446), Native0. Subsequent strict input and slot-alias tests run through the same matrix; see latest run receipt, not this document, for final expanded count.
- Previous v046 historical static data and the v089 79x2 reference are reused only under their actual same-season conditions; unrelated SimC revision changes alone do not invalidate the per-season static variant cache.

## Next real-product tasks

1. **Actual new-season source acquisition** (Blizzard Game Data/build-specific DB2, pinned SimC source) that produces v225 source manifest and its original retrieval receipts. v225 itself does not download them.
2. **Targeted actual native measurement**, using only missing v227 requested item variants. Ensure the executed input profile hash and actual Native binary hash/build are independently linked (CI execution receipt, trusted artifact) before a numeric G is accepted. Do not launch 26xall-ilvl Native measurements automatically.
3. Validate a new-season G reference/scaling rule at the needed representative archetype/itemlevel points, and reuse it only where the observed evidence covers. No speculative level interpolation.
4. Independently validate quality/effect/weapon-condition J/F/O and optional fixed L/E, then v222/v216 B/T and real v098 user profile. Preserve manual T priority, prior DPS/cache identities, cancel/resume and 95% statistics.

Status: **implemented source/profile/Native JSON2 consistency adapter; real-source/native execution authentication and final G budget promotion still unimplemented**.
