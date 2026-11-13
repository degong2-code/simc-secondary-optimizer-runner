# v421 — A10 원본 통합 컴파일: 기존 3축 증거 재사용

- **Capability:** `SOURCE.SEAL` / `ENVIRONMENT.WEB` / `PRODUCT.E2E`, 요소 **A10**.
- **Keywords:** A10, v274, v275, v241, v191, v211, v213, v216, v212, source compiler, SHA, ZERO-SOURCE, catalog, product integration.
- **Prior evidence:** [v383 역사](2026-11-13_p1-v383-a10-a11-g2-archived-native-receipt-reuse.md), [v409](2026-11-13_p1-v409-a8-simc-metadata-and-result-snapshot-policy.md), [v410](2026-11-13_p1-v410-fresh-season-v211-optional-quality-classifier-unbound.md), [v417](2026-11-13_p1-v417-bounded-post-bridge-product-e2e-once.md), [v420](2026-11-13_p1-v420-a9-simc-source-bytes-scope.md).
- **Decision:** `REUSE` — COMPLETE (요소 범위). 새 컴파일러·Native·원본 수집 없이 기존 v274→v241→v191/v211/v213→v216/v212의 필요 입력·검증·카탈로그 결과를 확인했다.
- **Changes:** 78 JSON/자동 생성표·추적표, v401 상태 고정 단언 조정, CURRENT/START_HERE/INDEX 기록. 제품 컴파일·SimC 코드 변경 없음.
- **Verification:** 현재 v417 실제 Windows #43394408756, v410 가변원본 80 PASS #43387395448, v409 원본 60 PASS #43386905854, v344 역사 #43114134208; 새 계약 CI #43405396556 SUCCESS.
- **Remaining:** A11 source/build/SHA/봉인·재개 독립 검토, 나머지 요소·전체 USER-E2E PENDING.
- **Efficiency:** 신규 Native0, 외부 원본 수집0, 컴파일 재실행0; 기존 캐시·영수증 재사용. 개발 장부의 198개 역사 오류는 별도이며 A10 판정과 구분.
- **수락 범위:** A10의 원본 통합 컴파일이며 각 G/J/F/O 숫자, 선택 품질 승인, 26 DPS 전체 Native, 미래 미출시 시즌 실측, 최종 ZERO-SOURCE→USER-E2E는 아니다.

## 1. 현재 원본 및 실 소비

`v274.NEEDED`는 정확히 **9개**: `GEAR_V167`, `TIER_V168`, `V189`, `V190`, `GENERATED_PERMANENT`, `GENERATED_TEMPORARY`, `GENERATED_GEM`, `SIMC_V211_SIX_SOURCE_FILES_AND_MANIFEST`, `PINNED_SIMC_REVISION`. `COMPILER_INPUT_OWNER`는 각 공급자를 기존 v216/v167, v216/v251/v276, v216/v189, v216/v190/v281/v285, v275, v229/v275, v229/v275, v275, v229로 분류한다. 이는 **카탈로그 컴파일에 필요한 파일**이지 각 예산의 독립 수치 인증 요건이 아니다.

기존 `v275`는 v229/v189 pinned Git tree/blob+generated 소스를 봉인·재사용한다. `v274.discover/compile_collected`는 공급자 누락을 보고하고 충족 시 기존 `v241`를 호출한다. `v241.source_inputs`는 동일 게임 빌드/SimC revision, 6개 소스 manifest/bytes SHA/크기, 구 시즌 J/F 참조 혼입을 검사한다. `v191` 소스 후보, `v211` source-only 메타데이터 분류, `v213.compile_catalog/verify_catalog` 결과를 `v216.preflight_new_season_source` 및 `v212` 설치가 사용한다.

**CURRENT_SOURCE_REAL:** [v417 실제 Windows #43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756), tested SHA `89d4810baf5e05f1c5c6f355f39a5f35ca9ec4e7`, Retail KR 12.1.5.70783 / pinned source revision `de11f57df75dda668bae6ac7043a43b98831fa96`. 실제 Job 로그의 `V191_UNIFIED SOURCE_COMBINED_NOT_YET_USER_SELECTABLE gear 209 tier 65 enchant_candidates 772 NATIVE_0 NO_UI_PROMOTION` 이후 정상 환경 설치와 실제 사용자 SimC 실행 성공. 실제 원본 [artifact #14021859656](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756/artifacts/14021859656). 209/65/772는 카탈로그 **후보 수**이지 전 품목 승인 수가 아니다. [v344 역사 #43114134208](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43114134208)도 `FRESH_V191_V211_V213_COMPILED_UNADMITTED` 및 v212 설치 성공을 기록한다.

## 2. 범용 회귀

**GENERALIZATION_REGRESSION:** [v410 focused #43387395448](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43387395448), tested SHA `411d98508e978a915a3a5204d1f67080a920a9f9`, **80 PASS/0 FAIL**. 실제 로그에 `test_v239_v211_fresh_season_dynamic_classifier`의 다른 빌드/원본 파일 SHA/manifest 및 가변 후보, `test_v240_v211_v213_fresh_catalog_handoff`의 새 입력 v191→v211→v213 연속 컴파일·v216 preflight·구 시즌 승인 비상속, `test_v213_source_to_catalog`의 빌드/revision 불일치·manifest digest·잘못된 분류 차단 회귀가 포함된다. [v409 focused #43386905854](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43386905854), tested `94150580bbc4745c25c559db2f185d20de009e6d`, **60 PASS**, v275 pinned bytes/blob·동일 출처 재사용·변조 차단 근거도 재사용. `test_v274_zero_history_source_compiler_wiring.py`는 9입력 공급자·누락/잘못된 타입·기존 컴파일러 전달 검사를 보유하며 이번 작업에서 재실행하지 않았다. 범용 회귀는 변경된 시즌/소스의 **합성 변형**이지 미래 시즌 원본 실측이 아니다.

## 3. 제품 통합

**PRODUCT_INTEGRATION_REAL:** 같은 [v417 성공 #43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756)에서 단일 Survival Hunter/ilvl334/일반 보석4/O0의 원본 컴파일→v216/v212 설치 G2850/J92/F165/O0/B=T3107(환경 Native3)→사용자 v113/v098/v096/v293 실제 DPS Native12→기존 결과 저장/조회 성공을 확인했다. DPS178334.8563, SEM298.6111, 관측 CHMV373/1078/1491/165. 선택쌍의 명목 95% 방향 지지이며 전역 최적·26 DPS 전체 증명이 아니다.

## 4. 판정과 후속

- **A10 generic/current_source/product_integration PASS**, 기존 **historical PASS** 유지. 요소별 COMPLETE, 전체 제품 E2E PENDING.
- 코드 구현·기존 소스·캐시·기존 영수증 재사용. **제품 코드 수정0, 신규 외부 원본 수집0, 신규 Native0, 신규 컴파일 실행0**. 완료 계약 JSON·자동 생성표·상세 78표·v401 상태 고정 테스트 및 진입 문서만 변경한다.
- 실 사용자 새 요청의 `source_compilation.missing`은 확보하지 않았으므로 고장이 있다고 추측하지 않는다. 컴파일 카탈로그 결손과 실제 G/J/F/O 필수 원본 결손은 계속 분리한다.
- **다음 A11 원본 영수증:** 기존 v217/v212 원본 stage의 source/build/SHA/봉인/재개/검증된 선택 요청 소비를 개별 증거로 확인한다. v344/v417 성공은 자동 전체 READY가 아니다.
