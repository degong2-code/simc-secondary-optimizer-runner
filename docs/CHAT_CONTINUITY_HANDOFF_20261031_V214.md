# SIMC SECONDARY OPTIMIZER — 2026-10-31 v214 P3-C 정본 인계

**목적:** P3-B v213 source-to-catalog PASS에 이어 P3-C의 첫 실제 v213→v196→v098→v212 Environment Manifest 연결, v208 selected-special 경로 전달, CI/Artifact 증거를 정확히 복원하고 다음 P3-C/P3-D 작업으로 이어간다.

**상태:** P3-C 첫 source-backed integration slice는 실제 Actions에서 PASS했다. 그러나 이는 원클릭 Environment Builder 완성이 아니다. 현재 실제 v098 profile witness는 Retribution 334 한 전문화이며 all_specs_ready=false; Windows beta package에는 v213 artifact가 아직 포함되지 않는다. v208 probe는 mocked cache-hit plumbing only이고 새 L Native 증거가 아니다. main/v003/original v016/Project Sources/Instructions UI/visibility/official Work OS authority는 변경하지 않았다.

## 0. 저장소·기준·HEAD

- Repository: degong2-code/simc-secondary-optimizer-runner
- Branch: probe/chat-cache-v035-20261024
- P3-C implementation source run: [#41172423986](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41172423986), commit 1ef1f3f73e619f6b42a95e71cfca0f6d2f864fc7, SUCCESS.
- P3-C code + tests commits: 2c6e5a15df7038d812ee3176eba311c7959ebac4, c8dbf30c6b2cffe881b4501f62fa29bdb2bf3f42, b6b764d6d1b1c534a29fb5b00c69f25441ddbd92, 1ef1f3f73e619f6b42a95e71cfca0f6d2f864fc7.
- This handoff commit moves the branch HEAD. Always fetch actual HEAD before continuing.
- Repository visibility was Public; no visibility change. Main HEAD at last check: 07133e0aaf738d6e4816a6486057b1cd49c018de; no main write/merge.
- Product scope is exactly **26 DPS specializations**, excluding Augmentation Evoker, tanks and healers. The user-uploaded v1.4.1 2026-10-29 file contains an older 27/Augmentation statement; do not follow that stale wording. CURRENT top and the 2026-10-31 user correction define 26. The repository’s runner/v143_specialization_contracts.py has 26 contracts and excludes evoker/augmentation.
- Core product remains target-level CHMV optimization using SimC DPS, not current worn gear redistribution or gear-set recommendation.

## 1. P3-C implementation

### 1.1 v212 Environment Manifest v2 directly consumes v213

runner/v212_environment_manifest.py is now schema v212_simc_environment_manifest_v2. Its CLI accepts:
- --source-to-catalog: exact v213 artifact;
- --bootstrap-result: v098 result JSON;
- --target-root: generated target profile folder;
- --out: sealed Environment Manifest.

It verifies the v213 embedded manifest digest and raw artifact file SHA, v191/v211 source identities and SHA256, exact game build/40-character SimC revision, and derives the v196 approved UI projection from the same exact v213 path. It no longer treats separately supplied v191/v211/v196 JSON documents as independent source authorities.

Approval boundary:
- 7967 is the only existing user-selectable enchant;
- 8025 remains developer-only;
- the other 36 remain locked;
- the v098 selected enchant must be the exact existing 7967 choice and appear once on the profile ring line;
- its static E remains zero within the existing evidence scope and it adds no CHMV budget.

The manifest binds v213 raw artifact SHA + embedded digest, v191/v211 component/source SHA, normalized v196 UI projection identity, v098 normalized semantic result identity, target manifest/profile/scenario/fillers file SHA, SimC binary SHA, and optional static-cache SHA. It does not copy the full user profile or local absolute paths.

Raw bootstrap JSON SHA is deliberately not part of the environment digest because that JSON includes relocation-sensitive absolute paths. Instead, a normalized semantic projection and every generated target file SHA are hashed; relocating the same target directory preserves the digest.

Selected special rows are represented by exact slot/item/ilevel/options identity SHA and require a bound static-cache snapshot. A separate v208 Start receipt is not yet serialized.

### 1.2 Existing v206/v098/v208/v113 path propagation

- runner/v206_nonchmv_eagle_selection.py: source, check_choice, apply, admit accept an optional exact catalog path. The legacy default remains unchanged when omitted.
- runner/v098_target_user_scenario_bootstrap.py: build and run accept optional source_catalog_path, so selected 7967 can be validated against the supplied v213 artifact.
- runner/v208_internal_exact_special_L_hydrator.py: hydrate forwards the same optional v213 path into the existing v098 static-special pre-budget stage.
- runner/v196_current_season_user_catalog.py: the eagle source lookup uses the exact supplied path.
- runner/v113_local_web_api.py: detects data/current_season_source_to_catalog.json inside a package and uses it for catalog options, Plan and Start/v208 when present. If absent, it deliberately falls back to the current legacy catalog.
- The current Windows beta ZIP does not include the v213 artifact yet, so the tested package runtime still uses legacy fallback. Do not claim the package has switched to v213.

### 1.3 Actual source-backed P3-C receipt

[Actions #41172423986](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41172423986): SUCCESS.

Artifact [#13031735907](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41172423986/artifacts/13031735907), 103,321 bytes compressed, 7-day retention. It contains v191/v211/v213 components, v098 bootstrap/profile, v212 Environment Manifest, and the v208 path-plumbing receipt.

Exact identities:
- v213 raw artifact SHA256: 55e74d4fb3d4721a56ecbc8e76448360273ddc0181d335fa94d9d9cc4e1619ad
- embedded v213 manifest SHA256: b888123728097371705c037ae2fc0085cc6735fac870f000b7606b1428d5ced5
- v212 Environment Manifest SHA256: 988a0b40f1123ee1271c6f761896bdb21f798ec4c734266a1d8feb7e311ce275

Actual v098 current-season Retribution 334 profile:
- existing approved ring enchant 7967 injected exactly once;
- existing E=0 proof scope retained;
- no CHMV budget increment and no B/T change;
- v098 plan Native0.

P3-C integrated test output:
- P3C_V213_TO_V196_EXACT_7967_APPROVAL_PASS
- P3C_V098_CURRENT_SEASON_RETRIBUTION_PROFILE_PASS_NATIVE0
- P3C_V212_SOURCE_CATALOG_ENVIRONMENT_MANIFEST_PASS_NATIVE0
- P3C_V208_SELECTED_SPECIAL_CACHE_HIT_PATH_PASS_NATIVE0

**v208 caveat:** the probe mocks the cache load and missing-variant lookup to force a cache-hit plumbing path and prove that the exact v213 path is forwarded to v208→v098. It does not verify actual cache bytes or make a new L observation. Existing v208 Native/cache receipts are reused; no Native was run here.

### 1.4 Cross-platform and adjacent regression evidence

- [v212 offline contract #41172225040](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41172225040): Ubuntu 23/23 PASS, Windows 23/23 PASS, Native0.
- [v098 offline #41172082190](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41172082190): SUCCESS.
- [v113 Local Web API #41172082178](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41172082178): Windows 2022 and Ubuntu 24.04 SUCCESS.
- [Windows beta #41172082207](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41172082207): Python 3.12 and 3.14 each 101 tests PASS, ZIP tests 2/2, extracted launcher/localhost HTTP security and three plans PASS. Artifact [#13031975054](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41172082207/artifacts/13031975054), ZIP SHA256 fda587b6a96b7e67a521d4564c85c330af56e9ae4a726ad5e3115b4c2434a1d0. This ZIP has 187 files/691,549 bytes and does not contain the v213 artifact.
- The P3-C pipeline #41172423986 ran v191 focused 6 tests PASS and the integrated source/classifier/catalog/v208 suite 29 tests PASS.
- Existing opt-in Native jobs in v177/v180 were skipped. New SimC Native calls: **0**; new SimC binary builds: **0**; optimizer/cache mutation: **0**.

## 2. Current P3 status

| Workstream | State |
|---|---|
| P3-A v212 Environment Manifest v2 direct v213 input | Implemented; 23/23 Ubuntu + Windows |
| P3-B v191→v211→v213→v196 actual source/catalog | Implemented; actual artifact + cross-platform regressions |
| P3-C actual v213→v196→v098→v212 profile/manifest slice | First source-backed slice PASS |
| P3-C v208 real selected-L Start receipt serialization | Not implemented; current test is mocked cache-hit plumbing only |
| P3-C all-26 profile-supplier readiness | Not complete; current v098 result all_specs_ready=false, witness is one Retribution 334 profile |
| Windows beta includes v213 artifact/default UI path | Not complete; current package uses legacy fallback |
| Dependency invalidation/orchestration | Not implemented |
| User-facing Build API/UI and optimizer handoff | Not complete |
| P3-D Windows one-click Build/Start/progress/cancel/resume | Not implemented |

### Next P3-C work

1. Package the actual generated v213 artifact into the Windows beta and bind its version/SHA to the app build. Switch the default UI/Plan/Start source only after that artifact is included and validated; do not leave a missing-file fallback masquerading as v213.
2. Define a versioned v208 Start receipt containing exact selected-special identity, cache hit/miss, Native JSON2 source/hash, measured L, and Native calls. Connect it to v212 without changing existing v208 L/E responsibility.
3. Complete readiness/coverage for all 26 DPS profile suppliers using existing v143/v169/v098 paths and reuse physical/native evidence; do not rerun a blanket Native matrix.
4. Add dependency-aware invalidation only for the components actually changed.
5. Then connect the sealed environment to the existing v093/v094/v095 optimizer and the production user Build/Start path.

No new optimizer, profile generator, effect engine, or gear-set recommender.

## 3. Required reading order

1. Read-only verify actual branch HEAD, main HEAD, repository visibility, latest Actions and artifact expiry.
2. This handoff in full.
3. docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md top.
4. docs/DEVELOPER_NOTES_v1.4.2_LATEST_USER_POLICY_ADDENDUM_20261030.md and the latest 26-DPS scope correction. The attached 2026-10-29 v1.4.1 copy contains an old 27/Augmentation statement; the latest user-approved scope is exactly 26 DPS excluding Augmentation.
5. docs/P3_ENVIRONMENT_BUILDER_TARGET_ARCHITECTURE_20261031.md §7–10.
6. Inspect only P3-C interfaces needed: v212/v213/v196/v206/v098/v208/v113; integration_probes/v214_p3c_v213_v098_v208_handoff.py; focused tests and workflow.
7. Reuse P3-B/P3-C Actions receipts above. Do not repeat unrelated Native, cache or all-26 physical evidence.

## 4. New-chat start prompt

You are continuing SIMC SECONDARY OPTIMIZER on the isolated branch probe/chat-cache-v035-20261024.

First response must be read-only: fetch actual branch HEAD, main HEAD, visibility, latest Actions and artifact status; read this handoff, CURRENT top, v1.4.2 policy and P3 architecture §7–10. Report P3-A/P3-B/P3-C implemented status, exact Actions/Artifact/SHA evidence, limitations and next P3-C work. **Do not edit code/docs, commit, run Actions, run Native, package/deploy, merge main, change visibility or alter Project Sources/Instructions until I say “진행”.**

Keep product scope exactly 26 DPS specializations excluding Augmentation Evoker, tanks and healers. Preserve T=G+J+F+O, B=G+J+F, oil O once, special bare-L/J/E separation, SimC ownership of items/procs/APL/DPS, 95% statistical display, exact 7967-only existing user approval, and reuse of valid Native/cache receipts. Unknown joins remain UNKNOWN/PENDING, never zero.

Continue P3-C by packaging the v213 artifact, serializing exact v208 Start receipts, completing the 26-DPS profile supplier readiness and dynamic dependency invalidation, then connect the sealed environment to the existing optimizer. Do not build another optimizer/profile generator/effect engine or repeat blanket Native matrices.

No main/v003/original v016/Project UI/official Work OS authority or repository visibility change without separate explicit authorization.

---

**END — V214 continuity handoff. Re-read actual HEAD before continuing.**
