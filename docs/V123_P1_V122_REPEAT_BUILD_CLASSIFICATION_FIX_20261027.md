# P1 / v123 — v122 common-profile repeat-build classification correction

2026-10-27 · isolated development branch `probe/chat-cache-v035-20261024` only.

## Real user Windows evidence

On the user's company Windows PC, fresh v122 ZIP in `새 폴더 (6)`, the eight-module focused offline regression returned **Ran 105 tests in 2.695s / FAILED (errors=7)**. Six subtest errors belonged to `test_all_six_new_sessions_share_canonical_profile_and_runtime_format` (Fury, Frost Mage, Retribution, Beast Mastery, Subtlety, Elemental), and one to existing `test_generated_plan_replay_without_new_native_or_replacement`. All seven had **`EXISTING_BOOTSTRAP_FILE_CHANGED:profile.simc`** at `v098.put_once` on the **second build** into the same session folder. The other 98 passed. **No actual SimC Native invoked by this unittest command**.

## Exact shared root cause

The v122 integration in `v098.build` used **`legacy=(folder/"profile.simc").is_file()`**. The first build saw no file, so it wrote the canonical new format with sorted gear lines and `json2=__SIMC_NATIVE_RESULT_PATH_REPLACED_PER_CANDIDATE__`. A second identical build saw that file and incorrectly treated it as a pre-v122 legacy profile, preserving a newly source-generated noncanonical template rather than reproducing the saved v122 result. The v098 full-byte `put_once` check correctly blocked the mismatch. This is a common serialization/version-classification bug, **not six per-specialization bugs**.

## Minimal common fix

- `runner/v122_common_profile_format.py` adds `existing_profile_uses_legacy_format(path)`: when the file is absent, the session is new. If present, only a line equal to `json2=__SIMC_NATIVE_RESULT_PATH_REPLACED_PER_CANDIDATE__` identifies a canonical v122 profile. Files without that line are old-format and use the existing backwards-compatible route. The method only **reads** the file.
- `runner/v098_target_user_scenario_bootstrap.py` calls this common version detector instead of `.is_file()`. Thus a **v122 new session remains v122 on replay**, while an old sealed session remains eligible for its historical immutable byte format.
- `tests/test_v122_common_profile_format.py` adds absent/old-without-json2/old-with-other-json2/new-with-v122-marker detection (one new test). `tests/test_v098_target_user_scenario_bootstrap.py` asserts all six newly sealed profiles remain classified as new and their second same-folder build is byte-identical. Existing source-value-drift and pre-v122 v104 cross-process tests continue to guard old-seal behavior.
- **No relaxation of the strict full-profile `put_once` byte gate**. A modified or mismatched profile still blocks; new-session files, historical results, cache files and user 0/6 Rogue `04fe21c0e61b180d305f` are not rewritten/moved/deleted.
- No new per-spec code, solver, SimC mechanism or bonus/diamond bypass. v063 candidate `json2` injection remains the common runtime.

## Proof boundaries and Windows next step

- The observed old 105-test execution **FAILS (7 ERROR)** and is not reclassified PASS.
- New source correction and regression test defined in GitHub; **new Windows Python regression not yet observed**. Expected next single focused regression count: **106 tests** (the eight v122 focused modules plus one new detector test). GitHub Actions CI and real Rogue `240967` SimC Native/socket validation still unverified.
- Only if all 106 pass, restart the local web server from the latest entire branch ZIP and open the **existing** Rogue user session `04fe21c0e61b180d305f`; same-session resume once. Keep `%USERPROFILE%\SIMC_Secondary_Optimizer\runs` intact. Inspect actual worker error/log and Native outputs when available.
- Product architectural scope: this is a first common-format migration for six source-backed archetypes. Source-backed APL/weapon/tier per-spec data is not yet migrated to one metadata registry for 27 DPS specs. Main, immutable v003, Project UI and formal Work OS/Shared State unchanged.
