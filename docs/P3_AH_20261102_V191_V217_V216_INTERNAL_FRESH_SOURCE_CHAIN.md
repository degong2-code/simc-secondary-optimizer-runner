# P3-AH — existing v191 compilation added to the same v216/v217 fresh-source Build stages

Date: 2026-11-02 KST. Scope: isolated development branch only. Authority: latest v1.4.3 / P3-AA single normal Environment Build and reuse existing engine. This is not a second builder, new collector, new optimizer, or final zero-history acceptance.

## Exact implemented boundary

- Extended existing runner/v241_fresh_source_stage_adapter.py with compile_fresh_v191_stage. It calls the original v191.main using explicit new-season gear, tier, v189, v190 and three SimC-generated source files with mandatory --fresh-budget-pending. It does not consult default installed budget, run HTTP, or call Native.
- The original v217.execute_stage wraps v191 output with declared input file SHA, event, target build/revision and source code dependency fingerprint; v211/v213 stage outputs remain independently sealed and reusable. A changed input fails closed rather than overwriting existing receipt. This is still a single normal Build component chain, not another product.
- The original v216.build_environment optional internal fresh_source_stage_inputs now accepts either an already compiled v191 path (P3-AG compatibility) or an exact fresh_v191_inputs mapping. In the latter case v191→v211→v213 are assembled inside the same Build call before the already-approved source preflight. As before, without verified new G/J/F/O and eligible profile, V216_FRESH_SOURCE_PROVENANCE_PASS_GJFO_NOT_READY blocks before session/cache files are created.
- Synthetic test extends tests/test_v240_v211_v213_fresh_catalog_handoff.py: source files of target build 12.2.0.99999→v191 CLI with J/F pending→same v211/v213 classifiers→three receipt-backed stages reused without writes on identical second call. No user options were automatically admitted; source retrieval is explicitly unauthenticated by this adapter.

## Actual CI results

- Initial code commit 6a87385f118a65136423634a8ecf01d17ea4caa7: Actions #41414283084 had a test-only ERROR from checking absent top-level J/F fields, not a compiler or Native failure. Corrected the test to assert the real v191 consumables reference fields.
- Corrected code HEAD 4fd987a9ff841bf754423c2f05a1d1597cabcdcb: Actions #41414370975 Ubuntu and Windows each Ran 322 tests, OK (skipped=2), all jobs SUCCESS. Explicit no-out Native-zero stage PASS. No fresh real external HTTP, no new Native.
- Existing P3-AG Actions #41413612926 321 tests each (2 SKIP) PASS and its v113/v181/v182 legacy regression SUCCESS are preserved historical narrower evidence, not re-run on every minor doc revision.

## Still missing / highest-priority next patch

The end-user POST /api/v1/environment/build is still the old installed-season jobs.plan() path. Real fresh Wago DB2/Blizzard/WCL/public GitHub/SimC collection, target-season detection, dynamically discovered tier anchors, normal source joins v161/163/162/171/165→v167/v168/v189/v190 into the v191 input files are not yet initiated inside the same Build call. The current adapter accepts explicit source files, so it cannot establish upstream fetch authenticity. It must never promote its local SHA check to upstream HTTP provenance. J/F/O and representative G proof, policy A, fresh v222/v212/profile installation, and complete Build→Start→adaptive E2E remain unfinished.

Next work should attach existing collectors and trusted fetch receipts to the same normal Build request, with source build/season identity, explicit missing-credential behavior and v217 stage idempotence. Make the fresh v191 inputs from newly fetched sources (not data/current_season_*). Use source-derived tier anchors and preserve M+ inclusion. After new G/J/F/O inputs are proven, existing v222 calculates B/T and existing v212 can be generalized to install; only then release PENDING. One minimal actual external fetch verification when supported, not 26-spec/native full sweep. Final zero-prior-data controlled experiment stays deferred until same engine is complete.

Efficiency: no Native calls, no duplicate v191/v211/v213 execution on unchanged stage inputs; input/output checks require bounded SHA I/O only. Real Wago-scale memory, I/O and execution-time measurements have not been observed in this change. main/v003/original v016/Project Sources UI/Work OS/visibility unchanged.
