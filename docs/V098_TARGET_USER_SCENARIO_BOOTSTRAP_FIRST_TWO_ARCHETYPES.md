# v098 — TARGET-LEVEL USER SCENARIO → INTERNAL REPRESENTATIVE SIMC INPUT

Date: 2026-10-26 KST. **Implemented P1 bounded integration (two already source-backed archetypes), not complete UI/all specs.** This is a GitHub isolated development record, not Project Source/Work OS promotion.

## User goal and newly implemented route

`runner/v098_target_user_scenario_bootstrap.py` accepts a compact user-facing JSON containing only:
- `character`: class, spec, race and talent string.
- `target`: desired ilvl (v087 validated range 266–344) and **optional** user final-inclusive `final_T`; when absent, selects verified rounded Native-derived baseline B.
- **Exactly two** user-selected trinket IDs, plus optional selected special items and **0–2** crafted embellishment gear rows; their item IDs/options are exact and SimC-owned, never invented by the tool.
- Optional oil hand(s); basic combat target count, seconds and raid buffs.

Full currently-equipped user gear, current CHMV, full SimC source profile, filler gear, initial B seeds and SHA fields are **not** supplied by the user. The program obtains its target-level representative SimC profile from a source-verified internal fixture, scales all 16 slot item-level declarations to the chosen goal, preserves 4 actual tier piece slots, representative primaries and weapon performance, rewrites selected items, and preserves the source APL intact. Character race/talents and a bounded combat selection override that internal source, never the current equipped gear. `v091`/ `v090` require exact selected nontrinket special L and existing unchanged statutory budget handling; no cache miss is invented as zero. Missing static trinket data never blocks.

The bridge creates `profile.simc`, `scenario.json`, `fillers.json`, `manifest.json` privately and passes them unchanged to existing `v096_unified_product_entry.source`. It generates two legal, *meaningfully separated where permitted* initial B rating vectors (up to 10% B transfer under floors/caps). It does NOT add a new scheduler. Existing v093/v094/v095 stay responsible for actual Native simulation, DPS/SEM, 95% decision, near alternatives, SHA cache, progress/cancel and resume.

`--execute` is deliberately explicit. Without it, only the validated plan is made (no Native). `--cache-only` delegates to existing source-locked replay. Native binary path and revision are runtime/deployment inputs, **not yet a polished end-user app**.

## Current verified archetypes and limitations

- `warrior/fury`: v082 pinned source, plate, dual twohand Titan's Grip reference B; at ilvl334 B3350 and both oils T3414.
- `mage/frost`: v084 pinned source, cloth, onehand+nonweapon offhand reference B; at ilvl334 B3150 and one oil T3182.
- Any other class/spec currently **fails closed** with `REPRESENTATIVE_ARCHETYPE_NOT_READY`. v098 does **not** mean other specs are unsupported by SimC; only their user-input internal profile supplier is not yet connected to v098. Native evidence for other specs remains reusable.
- Exact nontrinket selected special L still requires existing static cache for that exact variant or later targeted Native lookup (not implemented as automatic in v098). No invented zero, no user-equipment scanning.
- The internal factory templates have source-bound consumables and are **not yet arbitrary user chosen** flasks/food/potions/talents-import/Omnium selector. Planned user UX/generalized representative-profile layer needed for all specs, constraints, defaults, runtime install/Windows one-click. A selected optional SimC imported profile has not yet been built for v098.
- Representative ilvl registry rounds to 10 and differs at most ±5 from **measured reference model**; it is not measured exact G for every gear variant.

## Verification evidence

New `tests/test_v098_target_user_scenario_bootstrap.py`: eight offline cases for Fury/Frost, full 16-slot auto assembly and selected trinket options, cross-level/race, manual final-inclusive T, no current-gear/full-profile user input, source-locked manifest replay, oil eligibility, special L unavailable fail-closed, tier collision, explicitly unavailable class/spec, and seed diversity. The workflow re-runs adjacent v089–v097 source/Native-input regression tests and pilot, **NO SimC Native**.

- [Initial workflow #40295140480](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40295140480): SUCCESS; source compile + tests + pilot.
- [After seed diversity #40295273136](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40295273136): SUCCESS.
- **[Final focused #40295306726](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40295306726): SUCCESS**, includes explicit 10%-B transfer regression. Zero new Native. This is offline/CI evidence only: no new real Fury/Frost DPS measurement and no full all-spec product release.
- Code commit at final focused CI `c2a84855b07d9ca5a3e2891c4f7647abccfc5737`.

## Next development P1 (preserve user goal)

Extend the **existing** source-backed representative-profile supplier to user-selected class/specs and the specified selected gear/consumables/Omnium/talents with minimal additional abstractions, using previous v071/v078/v079–v086, v082–v084 Native evidence and reusable cache. Add optional user profile character/talent import without copying current gear. Make normal user entry and execution/95%-result/cache/cancel/restart a usable one-click Windows route, then run minimal new Native only for actually changed input structures. Exact Native G remains optional; new optimizer/effect-support Gate not needed.

No changes to GitHub main, immutable v003, official Work OS/Shared State, ChatGPT Project Source or Instructions by this action.


## 2026-10-26 P1 continuation — 4 archetypes and optional character-only SimC import

This section updates the bounded v098 status above **without rewriting its historical two-archetype acceptance**. Reused existing verified source-backed builders:

- `paladin/retribution`: v083 original source, source-backed non-tier plate legs, exact 4 tier pieces; **15 slots, single 2H, no offhand**. Standard 334 reference B3150; mainhand oil adds 32 to final T.
- `hunter/beast_mastery`: v086 corrected v079 Hunter source, replaces the old `unknown` head/feet with previously proven **249317 and 249320**, retains pet/APL and 4 tiers; **15 slots, ranged no offhand**. Standard 334 reference B3150; mainhand oil adds 32 to final T. Do not treat historical uncorrected Hunter T2797 as standard 334.
- Existing `warrior/fury` (16 slots) and `mage/frost` (16 slots) paths remain unchanged in structure. All four now accept representative ilvl 266–344 via existing rounded ilvl lookup and can use the manual final-inclusive T override.

**Optional user SimC source import**: `import_simc_profile` may be provided as a file path in the user scenario JSON (resolved relative to that JSON); in that case `character` is `null`. The importer extracts ONLY the single unambiguous `class/spec/race/talents` assignment from the uploaded text and discards every source gear row. Generated SimC profile, equipment and CHMV budget still come exclusively from our internally selected target-ilvl representative archetype and the user-selected special/trinket/embellishment fields. If both manual character and import are specified, or character assignment is missing/duplicated, **fail closed**. This narrow import does not claim support for every possible SimC textual/profile export syntax or a complete external profile parser.

**Current verification:** [focused GitHub Actions #40297311700](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40297311700) **SUCCESS**: code compile, adjacent v089–v097 plus v098 tests and baseline pilot; **14 v098 test methods** including 4 archetype representation, target-level 321 rerender, fixed-corrected Hunter, optional SimC character import with intentionally fake current gear, duplicate/missing character data refusals and no Native output in plan mode. Final code/test commit `d2538fd089c283aceff231710315c6bd021761ff`; **zero new SimC Native**. Previous four-archetype-focused [#40297046227](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40297046227) also SUCCESS.

**Next missing product work**: generic verified representative source supply for additional specs; proper user-choice controls and correctly mapped user-flask/gem/food/potion/Omnium inputs; exact-special-L on-demand cache lookup (currently fail-closed); optional import broader shape only if needed; easy Windows launch/progress/result. Existing v096 source-locked runner still requires a SimC binary and revision runtime configuration, internally generated by this user bootstrap, which is not yet a distribution-ready Windows UI. Prior-spec Native proves original bounded scenarios only; arbitrary imported talents or races under this P1 extension have NOT been newly Native verified. No main/Work OS/source changes.
