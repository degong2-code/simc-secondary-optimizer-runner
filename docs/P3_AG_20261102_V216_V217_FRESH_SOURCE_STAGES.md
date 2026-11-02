# P3-AG — v216 existing Build stage adapter for fresh v191→v211→v213 (2026-11-02)

**Scope:** isolated branch only; this is one incremental step in the original Environment Build, **not** a second optimizer, collector, profile generator or environment builder. Product goal remains the repeatable per-season Environment DB Build engine, not isolated feature accumulation.

## Implemented

- Added only \`runner/v241_fresh_source_stage_adapter.py\`: takes an already newly generated v191 season candidate and the exact pinned SimC source manifest/bytes, verifies explicit independently supplied target build + exact SimC revision, null historic J/F/budget SHA and six source-file SHA/size identities.
- Uses the original \`v211.compile_fresh_season\` and \`v213.compile_catalog/verify_catalog\` via existing \`v217.execute_stage\` (two sequential sealed stages). v217 verifies hashed outputs and immutable input identity before reuse; changed evidence fails closed instead of overwriting the old stage/season. No native or network calls by adapter. A dedicated source-stage root is required, not a product cache.
- The existing \`v216.build_environment\` accepts an **internal optional** \`fresh_source_stage_inputs\` that assembles the candidate before its unchanged \`preflight_new_season_source\`. Missing G/J/F/O, item admission and profile still raise \`V216_FRESH_SOURCE_PROVENANCE_PASS_GJFO_NOT_READY\` **before writing session/bootstrap/cache files**. No old installed 7967/E/J/F approval is carried forward.
- Added a synthetic same-build stage/reuse/blocked-install regression to \`tests/test_v240_v211_v213_fresh_catalog_handoff.py\`, and added adapter path/compile to existing v212 Ubuntu/Windows workflow. Existing pinned-season Build path remains unchanged.

## Newly observed validation

- Initial commit \`18c6c552bc052083d6b6a5a869aff01927c601ff\`: Ubuntu 320 existing + 1 new test; first run [#41413465497](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41413465497) **FAILED** (1 test exception import namespace mismatch); source stage functionality wasn't the failing predicate, no Native.
- Focused correction \`c05081d8b15f1ee73ae11e93e814d29ea2347d95\`: [Actions #41413612926](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41413612926) Ubuntu **321 tests / OK (skipped=2)** and Windows **321 tests / OK (skipped=2)**, both SUCCESS; zero new Native, zero actual new external HTTP, no \`out\` generated. The same previous commit's v113, v181, v182 workflows succeeded. No actual new season provenance, G/J/F/O or complete Build established.

## Unfinished and next small vertical slice

**This is an internally callable Build bridge, not yet the normal user API's fresh-source acquisition path.** v113 POST Build still invokes installed-season \`jobs.plan()\`; this adapter starts from v191 input files already produced outside the request. There is still no same-request new Wago/Blizzard/WCL/SimC live collection, season/tier-anchor discovery, or v165/v167→v191 fresh-source generation. Upstream provenance is deliberately labelled \`upstream_fetch_authenticated_by_adapter=false\`; hashing local bytes is not proof of their remote origin.

Next: link existing normal network collectors and source receipts to the original Build request, with v217 stage idempotency; generate v191 from fresh collected season/gear/tier/SimC inputs *within the same request*, then pass it through this bridge. Verify that no \`data/current_season_*\` or old J/F/E/7967 is read; preserve M+ and tier eligibility, cache identity and zero premature install. Only after mandatory new same-season G/J/F/O proofs flow into v222 and fresh v212/profile can v216 release READY. The final zero-prior-data control experiment is **not yet conducted** and must retain normal new external collection.

## Efficiency / ownership

Reuses existing classifiers, stage engine and manifest. The same input rerun emits **0 new stage receipt writes** and avoids reclassifying v211/rejoining v213; change detection uses SHA of source files and exact code dependency closure. Bounded input byte limits, no duplicate Native, no old cache mutation; source compilation and v217 output SHA I/O are bounded but no real Wago-scale throughput metric has been measured. All changes isolated; no main/v003/v016/Project UI/Work OS changes.
