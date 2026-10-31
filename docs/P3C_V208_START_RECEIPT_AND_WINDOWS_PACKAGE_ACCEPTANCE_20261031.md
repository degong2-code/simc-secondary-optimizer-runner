# P3-C v208 Start Receipt + v213 Windows Package Acceptance (2026-10-31)

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
| branch HEAD | `98104eb702b6d7712d4a27fe7b428a084f671fcf` |
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
