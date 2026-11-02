# P3-AV — Normal Environment Build to one-spec SimC representative source bridge (2026-11-03 KST)

## Purpose
Continue P3-AU, P3-AT and approved v1.4.3 inside the **same** normal Environment Build pipeline, without adding another optimizer, another season database or a new SimC source parser. Only one requested DPS specialization is eligible; no 26-spec Native sweep.

## Implemented on isolated branch
- `runner/v216_environment_build_coordinator.py`: `collect_wago_new_season_source(representative_request=...)` passes the already discovered v167 gear candidates + v251 physical DB2/raid tier cohort into `_one_spec_ordinary_simc_stage`.
- When a **complete, already pinned v229 SimC seed containing item_data.inc** is present, `v251.select_for_simc` derives one exact `v231` class tier candidate; `v232.find_candidate` intersects SimC physical item metadata and the new-build Wago plain-gear candidate IDs, and runs existing `v169` selection. It saves a per-spec source-only candidate under `v217` with the explicit build, spec, target ilvl, byte hashes and transitive code fingerprint. Reused stage skips the parser and Native/network entirely.
- If request is missing, authenticated DB2 gear/tier is incomplete, or pinned full item data is unavailable: distinct PENDING statuses; **no implicit item_data download, no previous season fallback and no environment install**. Unsupported DPS, wrong build and unsafe source paths fail closed.
- G/J/F/O/B/T remain null. None of this certifies actual season membership, SimC static gear effects, weapon proficiency, Native G, Policy-A admissions or a complete user profile.
- The normal user's `POST /api/v1/environment/build` currently supplies `fresh_season_build` only; it **does not yet supply `representative_request` or provision the full pinned item_data**. Thus this addition is a verified internal optional path, not a claimed live user-facing E2E. This is the next integration gap.

## Evidence
- `tests/test_v255_one_spec_simc_representative_in_build.py`: 4 new synthetic tests covering a one-spec `v232` physical candidate with mocked `v251.select_for_simc` wrapper, second-run receipt reuse, absent full item_data, bad build / unsupported Augmentation, and missing required ordinary slot. The real `v251` exact-13x5 source-join tests remain in their original suite.
- [Actions #41474110912](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41474110912), code commit `1f5a3ac406d37b7ad34434c09a5fa39eecc72ab2`: **Ubuntu 368 tests, 0 FAIL, 4 SKIP; Windows 368 tests, 0 FAIL, 4 SKIP**. First integration PASS.
- Final code adds `v216/v251/v231/v229/v232/v230/v169/v167/v217` transitive dependency hashes to the stage so changes do not reuse stale results. Its last code commit is `803d7cd59d25baf6b6d30cc6744e5e2fddcb4b81`. This code change requires its own CI receipt; do not copy the previous PASS to this SHA.
- New real Wago HTTP **0**, new SimC Native **0**, new physical or DPS samples **0**. Historical P3-AT receipts reused as background only, no user sessions/caches modified, `main` untouched.

## Efficiency, risk and next steps
- No new item parsing and no regular Native calls. One-spec source receipt/checkpoint reuses v217; only one full pinned item_data SHA is streamed in 1MiB chunks for stage identity when available. The existing v232 parser then reads exact content for selected slots.
- Avoid granting season membership from Wago build identity, a tier ID, or `source_kinds` labels alone. The S1 and S2 physical roster coexist; old PvP/Sinful Gladiator must never be used for a new season representative G.
- Next: verify final dependency-fingerprint change in GitHub logs, then connect selected spec/target ilvl from the **existing** user controls and add controlled, lazy **same-revision full item_data** provisioning only when valid gear/tier evidence exists; inspect actual one-spec Wago×SimC coverage before any Native, verify G source/physical loadout and only then use v222 for B/T with separately authenticated J/F/O.
- Final zero-prior-data test remains a single normal Build, not a second reference-validation engine.
