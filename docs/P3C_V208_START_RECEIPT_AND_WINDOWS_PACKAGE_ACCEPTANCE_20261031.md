# P3-C v208 Start Receipt + v213 Windows Package Acceptance (2026-10-31)

> **Status update:** Sections 1–5 preserve the initial receipt/package acceptance baseline. The later v215 supplier-coverage, dependency-identity, and latest-source packaging implementation in §6 supersedes the older all-26/dependency/package limitations below.

## 판정

**P3-C source-backed Environment 연결의 이번 범위는 PASS.** 실제 v213 season catalog가 Windows beta ZIP에 포함되고, package manifest와 실행 중 v113 API가 동일한 catalog identity를 사용하는 것을 Windows Server 2022에서 확인했다. 선택 특수장비의 v208 Start receipt도 v212 Environment Manifest에 결합·검증된다.

이는 Environment Builder 전체나 최종 optimizer의 26개 전문화 E2E 완료를 뜻하지 않는다. 사용자 PC에 이미 배포된 과거 ZIP을 자동 교체한 것도 아니다.

## 1. v208 Start receipt → v212 Environment Manifest

- `runner/v208_internal_exact_special_L_hydrator.py`는 선택 특수장비의 exact selected identity와 bare-L identity, 정적 L 값/digest, cache HIT·MISS 구분, Native JSON2 SHA/revision/source, SimC binary/revision, exact v213 source-catalog identity, per-start Native call count를 담은 `v208_selected_special_start_receipt_v1`을 생성한다.
- `runner/v113_local_web_api.py`는 Start 세션에 content-addressed receipt를 `start-receipts/v208-start-<receipt_sha256>.json`으로 보존하고 API 응답에 receipt reference를 포함한다.
- `runner/v212_environment_manifest.py`는 receipt digest와 선택 특수장비 identity, bare variant identity, static-cache SHA/size, v213 artifact SHA/manifest digest/build/revision, SimC revision/binary SHA, cache hit/miss 및 Native-call 집계를 교차검증한다. receipt가 없는 선택 특수장비는 `NOT_PROVIDED`로 남고 unresolved 상태를 유지한다. receipt가 없는 것을 PASS로 승격하지 않는다.
- `integration_probes/v214_p3c_v213_v098_v208_handoff.py`의 새 receipt handoff 검증은 content-valid synthetic cache fixture와 Native 금지 mock을 사용한다. 따라서 이 통합 probe는 receipt 생성·연결 plumbing 및 Native0를 증명할 뿐, 새 물리 Native L 측정 증거가 아니다. 기존 v208 Native/cache 증거는 재사용한다.
- v208 및 v212 오프라인 테스트는 fake Native fixture만 사용한다. 실제 SimC Native를 새로 호출하지 않는다.

### 검증 영수증

- v212 cross-platform workflow: [Actions #41178807936](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41178807936), Ubuntu 24.04 **26/26 PASS**, Windows 2022 **26/26 PASS**, Native0.
- v208 dedicated offline workflow: [Actions #41178704898](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41178704898) SUCCESS.
- 실제 v213 source-to-catalog workflow: [Actions #41178704794](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41178704794), artifact [#13032959504](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41178704794/artifacts/13032959504), SUCCESS.

## 2. Windows beta ZIP의 v213 catalog 결합

- `integration_probes/v181_windows_beta_packager.py`의 mandatory runtime 목록은 `runner/v208_internal_exact_special_L_hydrator.py` 및 `runner/v212_environment_manifest.py`를 필수화한다.
- `tests/test_v181_windows_beta_package_offline.py`는 두 모듈이 ZIP에 존재하고 package manifest에 기록된 SHA와 ZIP 내 실제 바이트 SHA가 일치하는지 검사한다.
- v181/v182 packaging workflows는 v208/v212 코드·테스트 변경에도 다시 실행되도록 path triggers를 보강했다. 기본 source artifact는 최신 확인본 `v213-source-to-catalog-41178704794`를 사용한다.
- ZIP manifest는 v213 catalog의 schema, game build, SimC revision, artifact file SHA, embedded manifest SHA, Native/network count, automatic UI promotion flag를 봉인한다.
- Windows live HTTP probe는 ZIP 안의 v213 file SHA와 package manifest를 확인한 뒤, 추출한 서버의 `/api/v1/season-option-catalog` 응답이 동일한 v213 schema/manifest/build/revision을 사용하는지 확인한다. 현재 승인 경계는 **7967만 선택 가능**, 8025는 developer-only, 나머지 36개는 locked로 유지한다.
- 실제 Windows Plan smoke는 Retribution Paladin 334, Fury Warrior 321, Frost Mage 344 세 프로필을 확인했다. 이는 package/API/Plan 경로 증거이며 해당 전문화의 adaptive DPS 최적화 완료 증거는 아니다.

### 최신 Windows packaging 영수증

| 항목 | 결과 |
|---|---|
| branch HEAD | `cbc2244225f6c99bb57e765ca9b03b591fbc7cce` (code baseline before this document update) |
| v181 workflow | [#41182176804](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41182176804) — Windows 2022 / Python 3.12·3.14 SUCCESS |
| v181 artifact | [#13035257931](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41182176804/artifacts/13035257931) |
| v182 workflow | [#41182176762](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41182176762) — Ubuntu 24.04 + Windows 2022 SUCCESS |
| v182 artifact | [#13034803780](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41182176762/artifacts/13034803780) |
| outer Actions artifact ZIP | 각 738,523 bytes |
| inner Windows beta ZIP | 768,322 bytes / 188 files |
| inner ZIP SHA256 | `5241d1db90f80d500a4b3408de964a82b0bcf0a3eea3e3bb7b2f999d60eb583b` |
| v213 catalog file SHA256 | `55e74d4fb3d4721a56ecbc8e76448360273ddc0181d335fa94d9d9cc4e1619ad` |
| v213 embedded manifest SHA256 | `b888123728097371705c037ae2fc0085cc6735fac870f000b7606b1428d5ced5` |
| game build / SimC revision | `12.1.5.70575` / `710c2408bfd3ae4df71b8cd55cdf01f63fd6c926` |

두 workflow artifact의 내부 ZIP SHA가 완전히 일치했다. 실제 다운로드한 두 artifact를 풀어 v213 file SHA, v213 manifest SHA, v208/v212 module bytes와 package manifest SHA를 독립 대조했다.

- v181 Python 3.12 및 3.14: 각각 102 regression tests PASS, ZIP package 2 tests PASS, extracted Windows CMD launcher check PASS, localhost HTTP security PASS, 세 Plan PASS, Native0.
- v182 Ubuntu 및 Windows: 각 70-test focused suite + 52-test compatibility suite PASS, ZIP package 2 tests PASS. Windows에서는 extracted CMD/localhost HTTP/세 Plan/restore PASS. Artifact는 Windows job에서만 업로드한다.
- v182 suite에는 `tests.test_v208_special_L_hydration_offline` 및 `tests.test_v212_environment_manifest`가 포함된다.

## 3. 보존할 범위 및 미완료 항목

**이번에 완료한 것**
1. v208 Start receipt serialization 및 v212 exact identity/provenance verification.
2. v213 source catalog를 Windows beta ZIP에 실제 포함.
3. package manifest와 runtime API가 동일한 catalog SHA/build/revision을 쓰는지 Windows에서 검증.
4. v208/v212 모듈의 package inclusion과 SHA 검사, 관련 CI path trigger 및 회귀 연결.
5. v181/v182에서 동일한 Windows ZIP 바이트 재현.

**아직 완료하지 않은 것**
- 26 DPS 전문화의 모든 current-season representative profile supplier 연결. v212 `all_specs_ready`는 아직 false다.
- dependency invalidation 및 source/cache orchestration.
- 사용자 Build API/UI, Environment readiness 표시 및 실제 사용자 입력 흐름.
- Windows one-click Build/Start, progress, cancel/resume의 제품 통합.
- 사용자 PC에 배포된 ZIP의 자동 업데이트 및 직접 GUI 클릭 검증.
- 26개 전문화 전체의 adaptive DPS E2E 및 전역 최적해 증명.

신규 SimC Native, SimC binary build, optimizer/cache mutation은 이번 P3-C package/receipt 검증에서 0회다. 기존 Native 증거와 동일한 v213 source artifact를 재사용했다.

## 4. 저장소 상태와 권한 경계

- 저장소: `degong2-code/simc-secondary-optimizer-runner` (Public; 사용자 승인 상태 유지)
- 개발 branch: `probe/chat-cache-v035-20261024`
- 최신 branch HEAD: `98104eb702b6d7712d4a27fe7b428a084f671fcf`
- `main` HEAD: `07133e0aaf738d6e4816a6486057b1cd49c018de` (변경 없음)
- 변경은 격리 branch에만 반영. main, v003 immutable, Project Sources/Instructions UI, Work OS CURRENT는 변경하지 않았다.

## 5. 다음 구현 우선순위

P3-C package/receipt handoff는 완료로 표시한다. 다음은 기존 profile suppliers와 v212/v098를 재사용해 **26 DPS specialization coverage gap을 source-backed 형태로 줄이는 작업**이다. 먼저 v212 `unresolved_dependencies`와 v169/v176 source-first evidence를 대조해 누락 supplier를 분류하고, 이미 검증된 supplier·source identity는 재실행하지 않는다. 그 다음 dependency invalidation/orchestration을 최소 구현하고, 이를 사용자 Build API/UI 및 Windows one-click Build/Start에 연결한다. 새로운 optimizer나 별도 수집기·효과 계산기는 만들지 않는다.


## 6. 2026-10-31 v215 follow-up — profile suppliers, dependency graph, latest source package

### 6.1 26-DPS plan supplier coverage

The previous “all-26 profile suppliers incomplete” wording is superseded for **plan/profile supplier availability**. v098 now computes a deterministic, cached source-supplier registry and v212 validates its contract before sealing the environment manifest.

- Existing legacy source-backed routes: 24.
- Source-independent product routes: 2.
- Union, exact and disjoint: 26/26 approved DPS contracts.
- v106 user-input routes: 26/26.
- v106 starter defaults: 26/26.
- v139 season catalog: 26/26.
- v169 current-season source-first profile suppliers: 26/26.
- gear/tier/budget raw input SHA256 values are bound to the v191 source input hashes embedded in v213.
- The current selected specialization must be a member of the exact 26-key set.
- The coverage record is v215_profile_supplier_coverage_v1. It explicitly keeps all_specs_ready=false and adaptive_native_evidence_complete=false.

**Interpretation:** the full set of current-season Plan/profile supplier routes is verified. This does not assert that every one of the 26 specializations has a current-season adaptive Native/DPS end-to-end receipt. Existing physical/native evidence remains scoped to its original profile/condition; no blanket matrix was rerun.

### 6.2 Dependency-aware identity and invalidation

- v212 seals v212_environment_dependency_graph_v1 fingerprints for v213 source catalog, v191 gear/tier/budget inputs, v196 UI projection, v098 profile/generated files, selected-special identity, static-item cache, v208 Start receipt, Windows package manifest, SimC binary and revision.
- compare_dependency_graphs() compares the current sealed environment with the previous valid manifest and reports changed inputs and affected downstream components. It is read-only; it never deletes static caches or historical sessions.
- A v208 receipt change invalidates the environment manifest only when selected-special identity and static-cache snapshot are unchanged; the exact static item cache is preserved.
- v106 session identity now binds the raw v213 artifact SHA, embedded manifest SHA, build, revision and optional package-manifest SHA. Absolute paths are excluded, so same bytes relocated to another directory retain the same session identity.
- v113 Start verifies that the current packaged source and package manifest still match the session identity. Changed source/package bytes create a new session identity instead of reusing a stale current-season session.
- The full incremental Environment Build orchestrator is not implemented yet; the current change provides deterministic dependency fingerprints, invalidation planning and source/package session isolation.

### 6.3 Latest source artifact and Windows package acceptance

The v181/v182 workflow defaults were corrected from the older v213 source run #41178704794 to the latest successful source artifact from #41194394128.

| Item | Latest evidence |
|---|---|
| Source pipeline | [#41194394128](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394128) SUCCESS |
| v213 artifact | [#13040083134](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394128/artifacts/13040083134), 117,921 bytes |
| Downloaded artifact ZIP SHA256 | aada3cf81d0528bdc45674f5979b3bb5189594b83db3d3feca6cb4ecf545423f |
| Embedded v213 manifest SHA256 | b888123728097371705c037ae2fc0085cc6735fac870f000b7606b1428d5ced5 |
| v181 Windows package | [#41194661922](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194661922), Windows Python 3.12/3.14 SUCCESS |
| v181 artifact | [#13039854689](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194661922/artifacts/13039854689), 744,988 bytes; outer artifact SHA256 2e2198d12fd611f2305a70c71ee6d1158a07654c808306531a126c5e107ea3bd |
| v182 UI/package | [#41194661890](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194661890), Ubuntu/Windows SUCCESS |
| v182 artifact | [#13040520318](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194661890/artifacts/13040520318), 744,988 bytes; outer artifact SHA256 ac6ebfc30f1dcee5d8e87e5ad9a092e16008e38b781cccc5702ed7a4c6037ab0 |

The packaged ZIP contains 188 files and includes the v213 catalog. The Windows extracted launcher and localhost API confirm that the packaged v213 identity is active; Retribution 334, Fury 321 and Frost 344 plans and restore pass with Native0. HTTP security checks pass. This is an extracted Windows runtime/HTTP test, not a claim that the user's installed PC has been updated or that every GUI action was manually clicked.

### 6.4 Cross-platform and focused regressions

- v177 [#41194394055](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394055): 12 focused tests + 84 regression tests PASS; includes v213 artifact SHA session identity and path-relocation stability. Native-one-product job SKIPPED.
- v180 [#41194394105](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394105): 26 DPS × 5 target-level plan matrix; 3 focused tests + 63 regression tests PASS. Native-six-cases job SKIPPED.
- v113 [#41194394127](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394127): Ubuntu and Windows each 145/145 PASS.
- v187 [#41194394156](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394156): 13 tests PASS.
- v191 source pipeline #41194394128 includes the actual v191→v211→v213→v196 artifact handoff and P3-C v213→v098→v212 manifest probe; integrated tests PASS, Native0.
- v181: each Windows Python version reports 117 tests PASS; actual extracted CMD/HTTP/three plans/restore PASS.
- v182: Ubuntu and Windows each report 76 focused + 67 compatibility + 2 ZIP tests PASS; Windows extracted HTTP/three plans PASS.

New SimC Native calls: **0**. New SimC binary builds: **0**. Optimizer/cache mutations: **0**. Existing v208 Native/cache receipts were reused.

**Preserved failure history:** Earlier #41194031247/#41194031277/#41194031295/#41194031263 and #41194215309/#41194215360/#41194215331/#41194215357 failed the initial supplier-set check. The defect was key normalization/partition logic: 24 legacy tuple-key source-backed suppliers and 2 source-independent suppliers must be normalized to the 26 string-key DPS contracts, then checked as a disjoint union; only user-input/starter/season-catalog registries are each compared directly to all 26. The code was corrected and final v098/v177/v180/v187/v191 runs passed. Earlier Windows package regressions #41187430260/#41187430366 also exposed pinned-revision test fixtures after the v213 artifact was injected; v177/v180 fixtures now derive the pinned revision from the source artifact, and latest v181/v182 Windows package runs pass. These failed receipts are retained, not deleted. No Native was run to resolve either test-only issue.

### 6.5 Current remaining work

1. Build the actual incremental Environment Build coordinator using existing v191/v211/v213/v196/v212 components and the dependency graph. Reuse unchanged sources; rebuild only affected dependencies; preserve historical sessions/static caches.
2. Connect Build readiness and dependency-change reporting to the user API/UI with READY / READY_WITH_LIMITATIONS / BLOCKED, missing joins, 26/26 plan-supplier coverage, cache hits and Native scope.
3. Connect the sealed v098/v208 profile to the existing v093/v094/v095 optimizer; no new optimizer.
4. Resolve only exact embellishment item/slot joins, temporary-enchant hand applicability, and gem-property→gem-item-ID joins. UNKNOWN remains UNKNOWN/PENDING.
5. Complete Windows one-click Build/Start/progress/cancel/resume integration and user-PC acceptance.
6. Full adaptive Native/DPS evidence across all 26 remains incomplete; do not repeat blanket 26×N Native matrices.

