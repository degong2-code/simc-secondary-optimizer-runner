# SIMC SECONDARY OPTIMIZER — P1/v129 source field parsing consolidation

2026-10-27 · isolated development branch `probe/chat-cache-v035-20261024`

## Latest directly observed Windows regression

User tested v128 on Windows from `새 폴더 (12)`:

```
py -3 -m unittest -q tests.test_v127_dps_source_metadata tests.test_v128_common_source_profile_emitter tests.test_v101_common_representative_equipment tests.test_v103_source_observed_weapon_types tests.test_v098_target_user_scenario_bootstrap tests.test_v106_user_session_controller tests.test_v114_local_web_ui_offline
Ran 82 tests in 3.551s
OK
```

**82/82 PASS, FAIL0/ERROR0, actual Native0.** Output includes `V106_BLOCKED` for deliberately rejected synthetic cache-only scenarios, not test failures. Prior Explorer popup suppression (v106 test mock) was included, with no popup reported in pasted log. This is **v128 Windows proof**, not v129 PASS.

## v129 implementation (pending fresh focused regression)

- New `runner/v129_common_source_fields.py` centralizes **read-only** source SimC gear-slot ID extraction (both exact legacy regex variant and v104 item comma-fields variant), original gem/enchant/enchant_id modifiers, source top-level character/consumable names, and ordered `actions`/`talents` line selection.
- The actual source adapters `v082` Fury, `v083` Retribution, `v084` Frost call common `equipment(...include_gem_enchant=False)`, `matching_lines(...,"actions")` and `matching_lines(...,"talents=")`, preserving their **exact original error code prefixes and caller's pinned source SHA, class/spec/role/weapon/APL checks**.
- `v104` shared Rogue/Subtlety + Shaman/Elemental adapter delegates old `extract_gear` to common `equipment(...include_gem_enchant=True)` (preserve exact gem and enchant modifiers), original names to `settings(...duplicate_prefix="SOURCE_DUPLICATE_SETTING:")`, and actions lines to `matching_lines`. Every previously checked physical weapon/Tier/fifth/ordinary source input remains gated. BM Hunter v086 already composes from v082, so is covered by that source parsing path.
- `v128` shared source profile emitter still owns serialized runtime/gear text, v127 registry owns verified metadata, v101 shared assembly owns representative gear, v122 canonical session runtime and v094 bounded adaptive Native/95%-statistics/cache/worker unchanged. No source fixture, external proc mechanism, missing 21-spec APL/tier/weapon metadata, Native witness or session byte modified.

## Tests and evidence boundaries

- New `tests/test_v129_common_source_fields.py` has **5** offline tests. For all 6 pinned real fixtures, monkeypatch the new parser with an independently copied pre-v129 parser, compare entire original producer result (profile bytes, cfg, fillers, 4-tier, F/weapon): exact equality required in same output directory. Further test original duplicate and missing item ID error codes, gem/enchant modifiers and `# Gear Summary` stop, repeated source character setting rejection, exact APL order, and missing/bad slot fail-closed.
- Retained previously verified 7-module 82-test suite. Combined proposed Windows focused command is **8 modules / 87 tests expected**, **new v129 Windows / CI PASS not yet observed**.
- No actual SimC Native run added. Historical Windows full UI Native6/6 evidence remains Retribution, Subtlety and Elemental; not evidence of v129 modified parser's Native execution, but byte-equivalence test is the proportionate check required for read-only refactoring.

## Explicit remaining scope

- Source-specific **identity and provenance verification** remains pinned in legacy v082/v083/v084/v104 adapters, by design. v129 centralizes parsing, **not yet the full universal source/profile producer or source metadata for all 27 DPS**.
- Next P1 slice can remove duplicated source identity guard scaffolding and normalize already-known metadata checks by strict source registry descriptors while retaining source-specific producer validations where necessary. Expansion beyond 6 requires verified per-spec source and cannot infer IDs or APL from these six.
- main, immutable v003, Project UI/Sources, official Work OS M0/Shared State untouched. No WEQUIP runtime dependency, new effect gate, full-season DB or additional Native calls.
