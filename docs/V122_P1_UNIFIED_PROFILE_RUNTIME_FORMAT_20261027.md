# P1 v122 — common target-level SimC session profile format (2026-10-27)

**User's direct decision:** avoid accumulating independent per-spec SimC execution conventions. Build the product around one user schema → one representative-equipment and profile-output contract → one candidate/Native engine. Per-spec differences are verified **data** (class/spec/race/talents, tier IDs, representative weapon topology and items, exact APL source), not new optimizers or new file shapes. Target: **27 DPS specializations**, currently **six source-backed**; do not claim all 27 implemented.

## This commit — FIRST migration slice, not 27-spec completion

- New **`runner/v122_common_profile_format.py`** provides canonical profile gear-slot order (stable sorted official slot keys) and a single runtime input formatter for **all current six** archetypes, regardless of which source-backed factory supplies class/APL/item rows.
- `runner/v098_target_user_scenario_bootstrap.py` routes **every current archetype** through common `order_rows` and `finalize`. For **new sessions**, full equipment lines get a deterministic slot order, and profile has exactly one `iterations=`, one `json2=__SIMC_NATIVE_RESULT_PATH_REPLACED_PER_CANDIDATE__`, and four controlled `gear_*` fields. The existing v063 Native candidate compiler replaces this placeholder with the exact per-candidate absolute output path and strictly checks one `json2=`; no new SimC handler, DPS optimizer or statistic implementation.
- **Historical same-ID sessions** detected by an existing sealed `profile.simc` preserve their existing slot order and runtime profile *bytes*. In particular, formerly json2-less v104 Rogue/Subtlety/Shaman/Elemental profiles are read-only legacy input and get `json2` only on per-candidate Native render (v121). Previous successful Paladin receipts or paused Rogue `04fe21c0e61b180d305f` should not be rewritten, moved, or treated as invalid solely because new sessions now have a more uniform format. Existing `put_once` full byte parity remains.
- Existing v101 shared representative gear/selected-effect/4-tier logic, v096/v094 Native search, v062 L, B/O/T, 95% decisions and cache identities are unchanged. `v101.ARCHETYPES` still maps six pinned source providers. **Those producers have NOT YET been replaced with a unified metadata-only source registry**. Their exact sources/APL can remain pinned for correct SimC behavior while migration proceeds. Do not remove old fixtures or forcibly migrate existing saves.
- Existing v121 dedicated `input_parts(...allow_missing_json2_template=True)` compatibility stays for older saves only; new sessions require strict complete runtime input.

## New offline regression evidence to obtain

- `tests/test_v098_target_user_scenario_bootstrap.py` has an additional six-spec test: **each new profile** has alphabetical gear order, 1 iterations, 1 placeholder json2, valid 4 gear overrides, no Native, same byte identity on repeated build. Existing v104 cross-process historical regression deliberately simulates **old producer** by bypassing v122 formatting in child process, then verifies replay of unchanged old profile under new code.
- `tests/test_v122_common_profile_format.py`: three tests (new and legacy runtimes, stable order, missing/duplicate protections).
- Corrected **two newline-escape test bugs** in v121 `tests/test_v063_numeric_injection.py` and new v122 tests, discovered by reviewing GitHub source, **before** requesting a new Windows run.
- Focused command covering v098, v101, v114, v062, v063, v093, v064, v122: expected **105 tests** (30+11+11+19+15+5+11+3). **This version's Windows/CI tests and Native execution have NOT been performed yet.** Previous 69/69 PASS and user Rogue `InjectionError:MISSING_OR_DUPLICATE_INPUT:json2=` (Native0) are historical evidence, not proof of v122. Only one **new combined** focused Windows run should be needed to check the v121 and v122 changes together.

## Next bounded phases

1. Validate v122 six-spec runtime invariants, legacy replay, no-SimC preflight; fix actual failures without blanket native reruns or repeatedly asking for full ZIP until code is ready.
2. Resume **existing** company Rogue `04fe21c0e61b180d305f` once after offline PASS; inspect native JSON2, 6 physically equipped ordinary gems/four colors and SimC acceptance, not a separate proc fidelity certification.
3. Move remaining per-spec producer-specific **profile construction** differences into one typed `DpsArchetypeData`/verified source registry: class/spec/race/role, APL/talents, weapon form, tier4+ordinary fifth, selected source item IDs, primary stat/weapon parameters, source provenance and Native-bound options. Require exact source-backed inputs for each additional DPS spec; no invented IDs or APL; do not build a season-wide item DB.
4. Extend source-backed data one specialization at a time from the current six toward 27 DPS specs. Reuse the same v122 serializer, v101 gear assembler, v096+v094 adaptive Native core, browser UI and cache. **No per-spec optimizer forks**.

## Safety/authorization

Only isolated development branch changed. **No main merge, v003 modification, Work OS/Shared State/Product Project UI promotion.** Existing completed sessions and historical Native bytes untouched. No Native SimC executed while authoring v122 and its offline tests.
