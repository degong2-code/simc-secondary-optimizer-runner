# P3-AW — Existing Build API reuses validated user spec and target level (2026-11-03 KST)

## Implemented on the original normal product entrypoint
- `runner/v113_local_web_api.py` now calls the **already existing** `sessions.user_scenario(controls)` before the fresh-season network acquisition. It passes only its verified `character.class`, `character.spec` and `target.ilevel` as `representative_request` to `v216.collect_wago_new_season_source`. No user-facing source/SHA/gear seed fields and no second parser/optimizer.
- `tests/test_v113_local_web_api_offline.py` verifies the exact propagated request on the existing `POST /api/v1/environment/build`, and ensures the normal prior-season plan is not invoked.
- Invalid/unsupported specialization is rejected by the original 26-DPS scenario validator; the v216 early input guard occurs before large Wago HTTP. This path does not silently use current equipped gear as G.
- The Build still does **not** automatically acquire a fully pinned `item_data.inc` file, nor attest the active season's gear/tier; `v255` one-spec source stage returns PENDING when this prerequisite is missing. No G/J/F/O, no B/T, no environment installation, no adaptive Native E2E. This is the original Build's control-plane bridge, not the final execution engine.

## Actual evidence versus missing verification
- First P3-AV source-stage functional code `803d7cd59d25baf6b6d30cc6744e5e2fddcb4b81`, [v212 Actions #41474328927](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41474328927) Ubuntu and Windows **368 tests each / 0 FAIL / 4 SKIP**, source/Native0.
- P3-AW API control forwarding code `7b5b6259ccf27ae1b8089cfab1aa7b30c082233b` and updated API assertion `363ab5477e7df39a4ea12d3274f57810b426e073`. [v113 Actions #41474745563](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41474745563): actual Ubuntu 24.04 Python 3.12 and Windows 2022 Python 3.14 job logs, **189 tests each, both SUCCESS, 0 FAIL**; no Native asserted by offline nature.
- Ancillary `v177/v180` workflow jobs are triggered by `v113` edits but their Native jobs are **opt-in commit-message gated**, and this commit does not use the Native trigger labels. Do not count either as a newly-run Native test.
- No new real Wago HTTP, no new Native SimC, no product season installation, no changes to `main`/v003/v016/Project UI/Work OS.

## Next
The immediate useful work is a tightly bounded **lazy existing-v229 pinned full item_data** provisioner in the original v216 Build, only after the requested source/season/raid/SimC input consistency is established; then test one target spec against real same-build Wago plain gear and report missing slots without old PvP fallback. Use existing v251/v232/v233/v234/v236/Native data paths, source/CI cache reuse, and no unconditional matrix of all specs or target levels.
