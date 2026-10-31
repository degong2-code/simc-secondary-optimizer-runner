# DPS specialization scope correction — 2026-10-31

## Current approved scope

**Exactly 26 DPS specializations are in scope. Augmentation Evoker, all tank specializations, and all healer specializations are excluded.**

This is the user's latest direct decision. The earlier uploaded copy of the v1.4.1 DPS-only source incorrectly stated 27 DPS specializations including Augmentation Evoker. That was a documentation/continuity error, not an approved expansion of product scope.

## Corrected source replacement

- Replacement file: `SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.1_DPS_ONLY_SCOPE_CORRECTION_20261031.md`
- SHA256: `d85ada7d20cb91730cad532d8d31908e2452e8700205ee46af136f2e5712a6d7`
- The corrected file preserves the v1.4.1 CHMV, SimC responsibility, statistics, budget, and product-flow policies while correcting all active scope/roadmap statements to 26 DPS and excluding Augmentation Evoker.
- The file is prepared for manual Project Sources replacement. This GitHub update does not itself change Project Sources/Instructions UI.

## Code and test scope audit

- `runner/v143_specialization_contracts.py`: current specialization contract set has 26 entries; no `evoker/augmentation`.
- `integration_probes/v176_all_26_source_first_physical_native.py`: fail-closed check requires `len(ALL) == 26` and exact equality with `sessions.SUPPORTED`.
- `tests/test_v176_all_26_source_first_physical_native.py`: checks 26 profiles and explicitly asserts that `evoker/augmentation` is absent.
- Existing [Actions #40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357) is SUCCESS. Its actual job log records `FINISHED_ALL_26_PHYSICAL_PASS` and `26 PASS_PHYSICAL_NATIVE`; 25 Native calls were new and the exact previous Paladin physical receipt was reused once.
- This is an ilvl334, 35-iteration **physical SimC profile smoke**. It does not prove that all 26 specializations have completed adaptive CHMV optimization E2E.

## Change and verification boundary

- Documentation/policy correction only. No product code or test code changed.
- No new SimC Native calls and no new Actions run were started. Existing code assertions, offline tests, and physical Native receipt were reused.
- P3 architecture already states 26 DPS and excludes Augmentation Evoker; it required no edit.
- `main`, immutable `v003`, original `v016`, repository visibility, Project Sources/Instructions UI, and official Work OS authority were not changed.
