# SIMC SECONDARY OPTIMIZER — P1/v130 common SHA, identity, APL and talent contract

2026-10-27 · isolated `probe/chat-cache-v035-20261024` only

## Grounded evidence

User company Windows PowerShell in `새 폴더 (13)` ran the previous eight focused modules: **`Ran 87 tests in 3.284s / OK`**, PASS87/FAIL0/ERROR0. The `V106_BLOCKED` and temp RESULT_DIR outputs are synthetic offline negative-path tests, not failed native jobs. **No real SimC Native called** in this run. This is scoped **v129 PASS**, not v130 proof. Existing Retri, Subtlety, Elemental Native6/6 and Subtlety caches remain historical prior evidence, and have not been repeated.

## Implementation: common validation, fixed source-specific semantics

New `runner/v130_source_identity_contract.py` has a pure read-only `verify` helper: exact Git blob SHA computed on source bytes; the SHA must agree with the independent v127 immutable source registry and the caller's original pinned fixture hash. It then verifies original class/spec/race/role identifying text markers, required count of original SimC `actions*` lines including exactly one primary `actions=`, and exactly one `talents=` where the existing source producer required it. Returns original, unchanged action lines and talent values. The **exact historical source-specific diagnostics** are passed through by each legacy factory.

`runner/v082_fury_plate_dual_twohand_native.py`, `v083_paladin_single_2h_native.py`, and `v084_frost_cloth_1h_frill_native.py` now use this helper in place of their duplicate primary SHA/class/APL/talents loops. Preserve their respective APL thresholds: Fury **more than 35**, Retribution **at least 35**, Frost **at least 60**, each with one base action and one talents field. `runner/v104_shared_pinned_rogue_shaman_composer.py` for Rogue Subtlety/Shaman Elemental uses the same helper for exact source SHA/class/spec/role and at least 15 action lines with one base, while retaining v104's own independently guarded settings parser and mandatory fields; v104 does not previously insist on exactly one talent in this *particular* helper (its settings reader already checks duplicates). Hunter BM remains backed by the source-pinned Fury producer adapter, reusing the same validator.

**Source-specific ID/weapon/tier/fifth ordinary checks stay in existing factories** and in independent v103/v127. v129 source gear/settings parser, v128 emitter, v122 canonical session, v094 adaptive Native/95%, user input, B/O/T/F/L budgets and durable cached receipts are untouched. The helper is one SHA per pre-existing source-producer execution, no new network, source DB or Native validation gate. No in-place stored source/profile/manifest mutation.

## Proportionate tests

New `tests/test_v130_source_identity_contract.py` has **5 offline test methods**. One independently implements the pre-v130 identity/APL/talent loop as a shadow helper and compares the **entire producer tuple for all six pinned source fixtures** before/after. The other four cover six exact Git source blobs and tampering refusal, independent v127 SHA drift refusal, original identity/APL line count/duplicate primary-action rejection, and optional talent count semantics retained for v104. The previously Windows-confirmed 87 tests remain. The one required focused Windows command is the previous eight modules plus new v130 module — **92 test methods expected**.

**No Windows Python or GitHub Actions PASS has been observed after v130 code edits**; do not describe 92/92 as PASS before actual user output. No need for another real Native run when the full source-produced profile byte-parity regression passes.

## Next substantive product step

P1 architecture is now common v127 metadata → v129 source fields → v130 source identity/APL validation → v128 byte-preserving emitter → v101 representative equipment → v122 runtime → v094 Native. The five existing fixture adapters still have justified source-validated, class-specific weapon/gear/fifth-ordinary construction. Expansion toward 27 DPS remains at **6 source-backed**, and requires source-pinned SimC input and exact relevant metadata for each new specialization, not inventing IDs or extending WEQUIP/database scope. Prefer new verified source coverage and user flow over repeating historical native/regression tests.

Scope remains isolated branch only; no main merge, immutable v003 changes, Project UI source promotion, Shared State or formal Work OS authority changes.
