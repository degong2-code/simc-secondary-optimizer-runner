# P3-AE — v216 single Build coordinator fresh-season source preflight, no premature installation

**2026-11-02 KST.** Policy [P3-AA](P3_AA_20261102_SINGLE_ENGINE_FRESH_SEASON_CONTROL_ACCEPTANCE.md): one real Environment Build engine; when it is complete, zero previously stored sources/season references/caches/receipts, **normal fresh Wago DB2/Blizzard/WCL/public GitHub/SimC collection allowed**. This is incremental ordinary-product development, not the final zero-history acceptance.

## What changed and why

Existing `v216.build_environment` accepted an installed v213 source artifact, the old v098 bootstrap, and `v212.compile_from_paths` assumed prior-season exact 38 enchant approvals (7967) and an already materialized B/T plan. P3-AB/P3-AC/P3-AD made the **same existing v165→v167 and v191→v211→v213→v196 source functions** able to produce a new season candidate catalog with J/F pending and no old E/7967 approvals, but passing that candidate directly to legacy v212 would be unsafe.

**Added a source-validation step inside the original v216 Build owner, NOT a separate Environment Builder:**

- `runner/v216_environment_build_coordinator.py::preflight_new_season_source` consumes the exact new v213 source artifact **read-only**, checks self-digest/structure with `v213.verify_catalog`, projects it via existing `v196.public_options`, requires externally supplied **expected target game build** and exact 40-hex SimC revision to match the source and UI. An artifact cannot self-confirm its own game build.
- Verifies fresh v211 SimC source manifest identity, `v191.sha256_by_input.budget=null` and **flask F and gem J reference=null**, no preinstalled budget hash, no preauthorized E/7967, zero selectable candidates, no G/J/F/O/B/T values, `environment_ready=false`.
- Returns a deterministic hash-sealed, read-only **candidate preflight** `v216_new_season_source_preflight_v1`: counts of ordinary gear candidates, tier pieces, enchant candidates, exact source manifest/hash, explicit missing G/J/F/O and profile/install dependencies. **Does not prove upstream HTTP retrieval, new-season eligibility, true numerical budget or users' options**.
- `v216.build_environment` detects a fresh source manifest and invokes this shared preflight **BEFORE writing bootstrap/session manifest or reading previous sessions**. It requires a separately supplied `expected_new_season_build`; if absent/mismatched, blocks. When valid source but G/J/F/O/eligible profile/approval remain pending, it raises `V216_FRESH_SOURCE_PROVENANCE_PASS_GJFO_NOT_READY:<preflight-sha256>`, rather than forcing fresh source into legacy `v212` pinned 7967 path. Original same-season packaged Build logic and historical receipts remain unchanged.
- Strict source SHA/manifest/gear tampering fails closed. Prior-season J/F reference in a would-be "fresh" catalog is rejected. Tests prove **zero writes to session** on every blocked fresh attempt, no historical cache changes.

This is a **safe new-season candidate-stage transition**, not a completed new-season installation. The application API still calls existing `v113.plan` for the installed current season; the full new-season Build button, live fetch, completed J/F/O/G, policy A admission, new season profile and `v212` generalization are still missing. Do not advertise this read-only preflight as a user-facing completed feature or final controlled acceptance.

## Evidence

- Extended `tests/test_v240_v211_v213_fresh_catalog_handoff.py`: synthetic *new-build* v213 source and v211 exact hash fixture. Explicitly tests **first** stale J/F source acceptance is blocked, **then** no prior budget SHA/references gives verified read-only source preflight, requires independently supplied build, rejects incorrect build/SimC revision and altered gear count, and proves `v216.build_environment` leaves session unchanged before blocking due to missing G/J/F/O.
- Final GitHub Actions [#41408530210](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41408530210): **Ubuntu 320 tests, 0 FAIL, 2 SKIP; Windows 320 tests, 0 FAIL, 2 SKIP**. This is offline synthetic and existing-product regression only. Actual new-season HTTP **0**, actual new Native **0**; old sources/caches not mutated. Earlier intermediate offline failures after an accidental test fixture old budget and a game-build regex escaping typo remain historical failures, not product Native failures; they were corrected before final PASS.
- No main merge, no v003 immutable mutation, no existing owner transfer, no Work OS promotion, no Project Sources/Instructions UI change or original v016 integration claim.

## Next shortest path toward complete product Build

1. Wire normal **new season source discovery + fresh Wago/Blizzard/WCL/public GitHub/SimC fetch** into the **same v216 Build request** (reuse v160/161/163/162/171/168/v189-v191 source collectors, existing `v217` receipt-backed stage engine and incremental cache policies). Derive new tier anchors from new source, never from installed 511-gear/reference values in a cold-start.
2. Reuse `v226-v228` same-build representative gear G work orders/verified numeric evidence only as needed; source-verify J/F highest-quality and weapon oil O and E/L fixed budget scope. Feed signed new-source proofs into **existing v222**, preserving B=G+J+F/T=B+O/manual T authority without copying old F165/J138/G≈2850.
3. Generalize **existing v212** manifest and profile route to actual newly proven G/J/F/O and policy-A automatic choice admission; only then replace the intentional pending GJFO block in v216 and install a new environment. Keep old exact 7967 installed path backward compatible.
4. After real Build/consumer optimization works, perform the user's **same-engine zero-old-data acceptance**, with normal external fresh collection permitted. Seal new output before independent comparison. No parallel SimC-only product/engine.
