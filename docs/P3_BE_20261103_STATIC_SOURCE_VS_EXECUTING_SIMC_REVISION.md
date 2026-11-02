# P3-BE — Preserve same-season source on a new SimC runtime (2026-11-03 KST)

## Scope and approved rule

A same-season balance/APL SimC update **must not** invalidate static representative gear, G/J/F/O, approved item identities or pinned static source merely because the executable's revision differs. The *actual executable binary/revision*, actual candidate/profile, fight/iterations and cache identity **must** change for new DPS results. New selected static measurements must be revision-bound; a verified exact variant static-cache HIT may retain its original Native measurement provenance. No reimplementation of SimC item effects.

Prior P3-BD already added `v258` metadata-only SimC pinned generated-file delta advisory, requiring four Git-tree metadata calls (five with short-SHA resolution), not downloading the entire Wago DB or re-running Native. Do not duplicate this work or treat the four file hashes as total APL/SimC semantic equivalence.

## Implementation — existing v212, no second engine

In `runner/v212_environment_manifest.py`, the immutable `v213`/v196 *source catalog* continues to require its own original `simc_revision` and exact packaged source/build SHA. It is **not** rewritten when a user updates SimC.

The existing `v098` target's `native_revision` is now independently validated as an actual 7–40-character lowercase hexadecimal revision, instead of forced equal to `v213.simc_revision`. The v212 dependency graph now keys its `simc_revision` to the **actual executing v098 revision**, and `simc_binary` to the actual file SHA. Historical receipts at matching source/runtime revisions retain their previous semantics; new-version runs have distinct environment/DPS identities, while static source and selected cache source hashes remain unchanged.

For a selected special item `v208` receipt, verify its `simc.revision` and `simc.binary_sha256` against the **new running** executable. Separately verify `source_catalog.simc_revision` against the **old pinned** catalog. Historical `NATIVE_JSON2_RESOLVED_VARIANT` HITs may carry an older valid hex `native_json2.revision` because the exact static variant and cache SHA are already sealed and rechecked; `MISS_NEW_NATIVE_JSON2` and `MISS_REUSED_NATIVE_JSON2` must match the **executing** revision. All existing exact selected identity, L, digest and cache ownership checks remain.

No automatic season promotion, Native invocation, new data download, source rewrite, static-cache purge, or existing historical session mutation. `v193` continues to own actual local SimC installation/update/rollback, and `v151/v212/v258` own change analysis.

## Regression evidence

- `tests/test_v212_environment_manifest.py` now covers: unchanged source catalog/UI/budget at a different installed SimC revision and binary SHA; separate `simc_binary`/`simc_revision` dependency invalidation and adaptive DPS cache; old exact variant Native static HIT with the new runtime receipt; a new Native miss requiring the new runtime revision; malformed runtime identity blocked.
- An initial code+test run [#41486005364](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41486005364) found **one synthetic test receipt error**: its `simc.binary_sha256` still referenced the old binary, correctly rejected by v212. Corrected test receipt; preserved initial failure.
- Final functional commit: `8da68a536af493368cdfd48cb44cf87e1e67d10a`. **[Actions #41486152811](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41486152811): Ubuntu/Windows each 408 tests / 0 FAIL / 4 SKIP, SUCCESS, Native0.**
- Final supporting workflows: [v113 #41486152823](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41486152823) PASS on Ubuntu/Windows; [v181 #41486152797](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41486152797) PASS on Windows Python 3.12/3.14; [v182 #41486152836](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41486152836) PASS on Windows/Ubuntu. **New real SimC Native executions: 0; actual new-version Windows user E2E not yet run.**

## Remaining next

1. Verify user current updater-selected SimC binary SHA/revision and a verified **same-season static source** through the existing local web API, with a new session and no gear/source re-collection.
2. Run ONE actual updated-SimC physical profile and a bounded adaptive DPS pilot, observing that the previous source and static cache retain their bytes while the new DPS cache is separated. Record SEM and 95% observational top as existing product already does.
3. G/J/F/O exact same-season source approval/automatic installation and full 26 DPS product coverage remain separate, unfinished work. Do not count this source/runtime decoupling as full season G/J/F/O completion.

**Authority:** latest user's same-season SimC update policy; isolated branch only. Do not update main, v003, original v016, Project UI or official Work OS promotion.
