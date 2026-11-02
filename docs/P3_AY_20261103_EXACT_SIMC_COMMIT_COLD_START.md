# P3-AY — Exact first-party SimC source revision and no-history cold start (2026-11-03 KST)

## Scope and authority

Implements an **internal source acquisition dependency** of the already established `v113 → v216 → v229 → v251/v232` Build. Reuses the existing user-provided `revision` (7–12 hex short or exact 40 hex). Does not create a parallel optimizer, add any new user input fields, claim current-season proof, install an environment or touch current gear. Approved 26 DPS only; main/v003/v016/Project UI/official Work OS unchanged.

## Implementation

- `v229.resolve_exact_commit()`: a short revision is resolved at GitHub REST `api.github.com/repos/simulationcraft/simc/commits/{prefix}`; only a 40-character lowercase hex `sha` beginning with that exact prefix is accepted. An already exact 40-hex revision needs zero lookup. Response is size bounded and mismatching/invalid results fail closed. **The source commit is NOT an independent attestation that the user's SimC executable was compiled from those bytes.**
- `v216._resolve_one_spec_simc_commit_stage()`: resolves only after the same-build authenticated gear candidate and physical raid/tier bridge paths exist. Existing v217 source-stage receipts are keyed by revision hint to preserve historical pins across revision changes; second identical execution is 0 HTTP. This stage records `binary_attested:false`, `season_verified:false`, `environment_ready:false`.
- The normal `v113` Build API passes its existing `UserRequest.revision` into `v216` without asking for SHA, item IDs or installed-gear totals. Only fully pinned source revision proceeds to `v229` collection.
- New `cold_start` event in `v229.inventory/collect` handles a truly absent previous game build. It expressly requires `previous_game_build=None` and remains source-only (`active_season_not_automatically_inferred=true`, `G/J/F/O/B/T=null`, no Native). Existing `season_change` and `expansion_change` still reject a missing or same previous build; no bypass by silently inventing the old build.
- The normal v216 Build maps default season-change **source collection only** to `cold_start` if no previous build is available. Its evidence result records `simc_source_event`. Downstream season approval and v212/SimC start remain blocked until independent evidence exists.

## Verification

- `tests/test_v257_exact_simc_commit_in_build.py`: exact short resolution and stage reuse, exact 40-hex zero lookup, source path incompleteness zero HTTP, mismatched SHA rejection, invalid source hint, old pin preserved after revision change, and v216 original v229 cold-start seven mocked source HTTP calls followed by zero repeat.
- `tests/test_v229_simc_only_source_seed.py`: no-history cold-start has no inherited build or G approval; season-change without prior build still fails; cold-start with a prior build is invalid.
- `tests/test_v113_local_web_api_offline.py`: existing Build API forwards existing revision and class/spec/ilevel, with no extra UI fields.
- **Verified final code [Actions #41477748894](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41477748894): Ubuntu and Windows each 385 tests, 0 FAIL, 4 SKIP, SUCCESS; `V212_ENVIRONMENT_MANIFEST_NATIVE0_PASS` in both job logs.**
- API [Actions #41477116168](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41477116168) on the API-test stage: Ubuntu/Windows SUCCESS. This precedes later cold-start additions; the final v212 suite includes previous API-related module smoke through its own coverage, but a fresh v113 run on the final HEAD was not requested.
- All HTTP counts in these tests are **synthetic transport observations**. New actual Wago, GitHub SimC source HTTP and Native calls initiated by this task: **zero**.

## Remaining prioritized path

1. Run ONE bounded real same-build source acquisition, reusing previously proven P3-AT GitHub/Wago references where valid, and verify the exact selected full revision and `item_data.inc`. Binary-to-source provenance still requires an explicit independent check if used as a product assurance; a Git source SHA alone is not that proof.
2. Measure one existing `v167×v251×v232` representative candidate's actual available ordinary slots and weapon form, without substituting old PvP IDs. If insufficient, report missing slots and preserve source cache.
3. Only after representative identity/season proof: reuse existing optional Native G or valid same-season G reference, establish top-quality J/F/O and permanent E ownership; integrate with v222 B/T and the original v098/v212/adaptive SimC path. Do not run blanket multi-spec Native or create a new effect evaluator.
4. The final no-prior-data end-to-end acceptance is still pending. This feature enables source discovery in that path; it does not fulfill the end-to-end condition.

**Status:** code implemented and offline verified; production automatic seasonal G/J/F/O and actual user DPS run still not complete.
