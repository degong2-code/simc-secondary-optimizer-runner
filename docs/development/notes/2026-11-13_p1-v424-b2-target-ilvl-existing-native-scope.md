# v424 — B2 목표 ilvl: 기존 비334 실 Native + 현재 334 제품 증거 재사용

- **Capability:** `CHARACTER.PROFILE`, `ENVIRONMENT.WEB`.
- **Keywords:** B2, target ilevel, ilvl334, v098, v106, v113, v169, v180, v216, v212, B/T, six non334 native, source SHA, cache identity.
- **Prior evidence:** [v423 B1 전문화 경계](2026-11-13_p1-v423-b1-26dps-contract-scoped-evidence.md), [v417 현재 Windows 제품](2026-11-13_p1-v417-bounded-post-bridge-product-e2e-once.md), [v422 소스 봉인](2026-11-13_p1-v422-a11-source-stage-receipt-reuse-three-axis.md); [v180 과거 실행 #40980268952](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40980268952).
- **Decision:** `REUSE` — **B2 generic/current_source/product_integration PASS, historical PASS; 요소 COMPLETE (ilvl 전달 범위)**. 과거 여섯 비334 실 Native의 성취와 최신 70783 기본334 실 제품을 결합한다. 최신 70783 비334 전체 ZERO-SOURCE 통합, 26×전 레벨 Native, 정밀 G는 완료로 주장하지 않는다.
- **Changes:** B2 완료 계약 JSON·자동 생성 상태표/추적표·v401 회귀 단언·현재 개발상태/인덱스 갱신. 프로그램 원본·SimC 코드·최적화 알고리즘 수정 없음.
- **Verification:** 현재 실제 Windows [v417 #43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756), tested SHA `89d4810baf5e05f1c5c6f355f39a5f35ca9ec4e7`; 이전 대상 레벨 변형/실 Linux Native [v180 #40980268952](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40980268952), tested SHA `4eaa5e2554e695527d96234e6f5236e644134696`; 현재 로컬 웹 오프라인 [v113 #43391249405](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43391249405), tested SHA `5732defbeba44db51427e7c1172724365ccca298`.
- **Remaining:** 다음 B3 일반 방어구 ID·부위·타입·ilvl 검토. B1 26전문화 전체 제품 통합, 새 빌드 비334 자동 환경 G/J/F/O 실 설치·Native, B11/B12 정확 G·근사 회계는 별도. 최종 USER-E2E PENDING.
- **Efficiency:** 추가 외부 소스 수집0, 새 Native0, 실제 프로필 생성/캐시 재작성0. 동일 시즌 영수증/기존 v094/v098/v106/v216/v212 재사용. 개발 노트 장부의 과거 198개 CI 오류는 별도.

## 1. 독립된 B2 증거

**GENERALIZATION_REGRESSION:** [v180 #40980268952](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40980268952)의 offline job에서 `tests.test_v180_multilevel_current_season_product_offline` **3 PASS**: 26 DPS × 목표 **266, 300, 321, 340, 344 = 130** 프로필/계획, 모두 장비 각 행 `ilevel` 동일, 4티어, 전문화/Fury 차등 동일시즌 참조 B 및 T=B+O, 130개 분리 세션 identity, 기존 334/비334 세션 보존, 범위 밖 265/345 거부, 웹 321/344 plan·재열기 두 단계 모두 Native0. 초기 `v089` B 참조는 해당 당시 승인 조건에서 10 rating 단위 근사이며 exact Native G로 과장하지 않는다.

**CURRENT_SOURCE_REAL:** [v417 실제 Windows #43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756), KR Retail `12.1.5.70783`, 기본 목표 **334**, v191 원본 기어209/티어65 → v216/v212 설치 G2850/J92/F165/O0/B=T3107 → 실제 Survival Hunter 대표 프로필 및 SimC DPS Native12, SEM/95% 스냅샷. v098의 현재 `SEASON_V216_GEAR_TIER_BUILD_OR_USER_TARGET_DRIFT` 및 `FRESH_SEASON_V191_GEAR_TIER_AND_INSTALLED_CATALOG_DRIFT` 검사, v113 설치본 조회 시 `verified_target_ilevel` 검사로 빌드와 목표 값의 혼용을 차단한다. 이 실 현재 원본은 **334 조건**이고 70783의 다른 ilvl 실 설치는 이번 증거가 아니다.

**PRODUCT_INTEGRATION_REAL / HISTORICAL_SCOPED:** 과거 [v180 실제 #40980268952](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40980268952)는 지정한 `current_season_product=True` user controls → 기존 v106/v098 대표 장비·레벨·예산→v096/v094 Native→DPS·SEM·95% 출력·저장·SHA cache-only까지 수행. 분노266, 야수300, 징벌321(수동 최종 T3500), 무법330(2대상·180초), 황폐340, 냉법344: **각 6 real Native /6 cache-only SHA, 총 신규36/캐시36, FAIL0**. 당시 SimC revision `7bc10711b5`·바이너리 SHA `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`. 이는 과거 소스 기반 제품 경로/선택 조건의 실제 증거이며 새로운 시즌 70783 v216 신규 수집/설치가 여섯 레벨 모두 성공했다는 증거가 아니다.

## 2. 판정 한계

B2에서 확인한 것은 **기본334, 지정 목표 레벨, ilvl별 장비 프로필/예산·세션 분리와 실제 SimC 결과의 일관된 전달**이다. 타 전문화 무기 적법성·각 레벨의 새 시즌 exact G·전체 일반장비/품질 자동등록은 B1/B3/B4/B5/B11/B12에서 독립 판단한다. v180 옛 시즌 근사 참조를 v417 새 70783 원본의 숫자 증명으로 복사하지 않는다. 최종 제품 E2E는 PENDING.
