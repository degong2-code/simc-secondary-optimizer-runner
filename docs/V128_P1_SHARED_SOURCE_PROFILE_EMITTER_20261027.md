# SIMC SECONDARY OPTIMIZER — P1/v128 shared source profile emitter

2026-10-27 | isolated development branch `probe/chat-cache-v035-20261024` only

## Purpose and user-approved architecture

Keep one common user → validated source metadata → target-level representative SimC profile → B/O/T/L-aware Native adaptive DPS optimizer → result/cache/restart path. Per-specialization talents, original SimC APL and exact class tier/ordinary/fifth/weapon records remain source-owned data; no new independent optimizer or effect model. This step is a **small source-composer consolidation** toward 27 DPS specs, not a claim that 27 have sources. Current source-backed specs remain six.

## What changed

- **`runner/v128_common_source_profile_emitter.py`** is the sole source-lines → normalized runtime/gear-line serialization implementation for the current pinned producers. It takes source text, ordered runtime `overrides`, validated physical item rows and the explicit source slot order. It preserves original source comments/APL and original `actions` lines exactly; removes only pre-existing overwritten top-level settings, physical gear and `temporary_enchant`; emits existing `v055_simc_item_selection.equipment_line` outputs. No file writes or Native subprocess.
- Routes legacy **v082 Fury**, **v083 Retribution**, **v084 Frost** through the shared emitter with their existing blank separator before override lines. Routes **v104 Rogue/Subtlety and Shaman/Elemental** through the same emitter, retaining their historical no-extra-separator layout and explicit duplicate-source-override rejection. **v086 BM Hunter** still composes through its original v082 source producer and its verified mail replacements, so it also uses the common emission path.
- All six adapter factories still validate exact source Git blobs, APL/talent identity, source weapon item IDs, selected tier and special gem options, and any per-spec source exceptions. Their existing cfg/metadata contents, typed scenario, B/O/T/F/L accounting, v122 new-session canonical output, v094 bounded Native/SEM/95%, and previous byte-sealed sessions/cache are unchanged by design.
- The distinction between **source adapter fixture emission** and **v122 canonical new-session serialization** remains important. This does not silently rewrite old `profile.simc`; v098 strict `put_once` replay and v126 old seed identity preservation are unchanged.

## Rigorous offline regressions committed

- New `tests/test_v128_common_source_profile_emitter.py`: four offline test methods. For **all six real pinned source fixtures**, compare the complete `v101.source_backed_gear` result using a separately implemented pre-v128 legacy line serializer versus new v128 emitter, **within the same output path**, requiring whole tuple equality (profile bytes, config, rows, group types, weapon form and F vector). Extra cases cover exact ordered APL/comment/gear layout with and without blank separator, duplicate setting fail-closed (v104), and malformed gear dictionary refusal. None invokes SimC Native.
- `tests/test_v098_target_user_scenario_bootstrap.py`: add a real six-spec **user scenario plan** parity test: first generate full immutable v098 plan with the independently reproduced legacy emitter, then replay the same folder with v128; require sealed `profile.simc` and `manifest.json` byte identity, identical B/O/T plan, and no simulated Native result directory. This is specifically designed to detect **v126-like multi-stage sealed manifest drift**.
- Existing focused v127, v101, v103, v106 and v114 regressions retained, including suppression of temporary-folder Explorer GUI side effects on Windows tests.

The seven-module targeted Windows command has **82** unit-test methods (prior reported 77/77 v127 + four new v128 + one new v098), and deliberately avoids all expensive real SimC runs.

## Evidence boundaries

- **Current implementation plus tests committed, but v128 Windows Python PASS/CI PASS NOT YET OBSERVED.** The last user-observed focused Windows v127 run was `Ran 77 tests in 2.998s / OK`, before v128 changes; v106 Explorer-temporary-folder test correction was likewise after that observed run.
- User's existing verified Windows Native 6/6 results for Retribution, Subtlety and Elemental and v122 common Shaman physical `240967` + four colors are **historical actual-product results**, not a fresh v128 certification.
- No new native calls, cache deletion/invalidation, per-specialization SimC mechanic gates, 27-spec support claim, main merge, immutable v003 change, Project UI source promotion or formal Work OS takeover.

## Next bounded development after focused PASS

Migrate the repeated **source gear-slot parser and typed source identity validation** into a common source adapter in another small diff, with the same exact before/after emitted-byte/source SHA comparisons. Subsequently turn verified source fixtures/tier/weapon/APL metadata into data-only entries for currently unsupported DPS specializations without guessed IDs or season-wide equipment DB. Prioritize P1 user flow over full-season Native surveys.
