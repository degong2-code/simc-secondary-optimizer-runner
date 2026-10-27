# SIMC SECONDARY OPTIMIZER — P1/v127 source-backed per-spec data registry

2026-10-27 | isolated development branch `probe/chat-cache-v035-20261024` only

## User's approved direction

One unified user-input schema → representative gear and profile serializer → CHMV accounting → existing adaptive SimC Native DPS engine → 95% results, cache, cancel/resume. Per-spec differences must be **source-validated data**, rather than new optimizer or Native execution forks. Final intended support is 27 DPS specializations; the currently **source-backed/executable set remains six** (Fury Warrior, Retribution Paladin, Frost Mage, Beast Mastery Hunter, Subtlety Rogue, Elemental Shaman). Existing completed Windows Native 6/6 results for Retribution, Subtlety and Elemental and current cache bytes are historical evidence, not to be changed or repeated without a concrete invalidation.

## Implementation — first data-layer consolidation

- New `runner/v127_dps_source_metadata.py` contains immutable, typed (`@dataclass(frozen=True)`) `Archetype` records for precisely six supported archetypes. Each has class/spec, armor family, pinned exact source fixture filename and Git blob SHA, legacy provider token, source-observed weapon form, all five exact class tier IDs, separately verified ordinary fifth-item slot/ID, and exact static flask F vector. **No SimC APL/proc effect is reimplemented**; actual APL/gear-source fixtures remain pinned and remain with SimC.
- `runner/v101_common_representative_equipment.py` now derives `CLASS_TIER_ITEMS`, `FIFTH_TIER`, and its existing backward-compatible `ARCHETYPES` tuple API **from the registry**; there is no second six-spec hardcoded tier/weapon/F list in v101. The provider resolver is a *small legacy source-adapter map*: v082 Fury, v083 Retribution, v084 Frost, v086 corrected Hunter, and one shared v104 producer for Rogue/Shaman. This is an intentional intermediate step: no new gear builder or SimC optimizer, and source factories still include four historical Python producer implementations plus v104's shared source composer.
- Each source-backed gear build verifies registry provenance/weapon shape/armor/F/tier against the independent existing `v103` weapon-source metadata and the existing v104 pins, and continues using the unchanged source-producer verification, shared equipment composition, v122 canonical serializer and v094 bounded engine. Source file hashes are verified during the source-backed producer and by the new unit test. Unsupported specs remain fail-closed, with **no guessed item IDs, tier IDs, APLs, or player input requirements**.
- Existing `v098.ARCHETYPES=common.ARCHETYPES` and `v106.SUPPORTED/source_defaults` are preserved in public shape: previously saved user/session files and the six browser choices retain their existing identity. No modifications to v003/main, Work OS, Project Sources/UI, WEQUIP, season item DB or static/DPS cache.
- Input metadata is frozen but its exposed budget F dictionary is materialized independently for every consumer, avoiding accidental shared state mutation.

## Verification status and minimal relevant next step

- `tests/test_v127_dps_source_metadata.py`: 6 focused new offline tests. Verify all six source Git blob SHAs against real bundled original fixture bytes, tier/weapon/F/fifth equivalence, all six generated representative source profiles, unsupported spec refusal, immutable records, and targeted metadata/source-provider drift fail-closed.
- Existing `tests.test_v101_common_representative_equipment`, `tests.test_v098_target_user_scenario_bootstrap`, `tests.test_v106_user_session_controller`, `tests.test_v114_local_web_ui_offline` and previously run v125/v126 tests remain required regression. New source code **has been committed but no Windows or GitHub Actions Python tests or Native run has yet been observed for v127**. Do not relabel earlier Windows 143/143 PASS or subsequent genuine Rogue/Shaman Native6/6 as v127 test results.
- No need to run any new Native simulation for this source-metadata-only change if the offline same-source/source-profile identity regressions pass. Reuse existing user evidence. A small directed Windows offline command in the chat validates v127 (no SimC invocation).
- Efficiency: this is bounded to six typed source rows, no season DB, Native repeat, new effect gate, network access, cache invalidation, new optimizer, or permanent WEQUIP dependency. Strict registry checks are deterministic in-memory and small; source fixture hash verification stays with existing producers.

## Not completed — explicit boundary

1. The six source-backed producers have NOT all been replaced with a **single universal source-to-representative profile parser**. v127 centralizes their declarative input metadata while preserving producer adapters to protect real SimC source behavior and existing byte identities. Migrating the remaining factory-specific assembly to one generic source composer is the next P1 slice, after a focused parity test.
2. Expansion from six to 27 DPS specializations requires exact verified source fixture, tier IDs, ordinary representative gear coverage, correct weapon form, source APL and flask bindings **for each new specialization**; neither generic class permissions nor unsupported numeric IDs may be inferred from current six examples.
3. Existing 95% bounded observed best is not proof of global optimum. Current 6-candidate search and user's formula `T=B+O` unchanged.
