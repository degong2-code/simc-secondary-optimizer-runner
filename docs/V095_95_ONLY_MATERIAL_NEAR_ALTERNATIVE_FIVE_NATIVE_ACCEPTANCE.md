# v095 — 95% 단일 판정·실제 큰 폭 분배 대안·SimC 검증

**2026-10-26 / 격리 제품 개발 / user-requested 95% ONLY.**

## 사용자 의사결정·공식 CHMV 계약
사용자는 **기존 95%를 유지**하며 **97% 비교표시를 완전히 제거**하라고 명시했다. 97%는 이전 고려안이었으며 이번 정책에는 사용하지 않는다. **95%로 판단해도 SEM 자체가 줄어드는 것이 아니며**, 관측 평균 DPS 순위와 통계적으로 입증된 우열은 구분한다. 공식 공식식 `T=G+J+F+O`; 기본 자유 분배 `B=G+J+F`, 기름 고정 O; Native SimC 실측 rating/dps/SEM은 SimC 계산 결과.

## v095 최소 변경·재사용
- 신규 `runner/v095_material_precision_policy.py`: **기존 v065.neighbors / score_direction**에 더 큰 `ceil(B*0.10)` 이동폭을 명시해 평가할 분배 후보를 제안하는 얇은 모듈. 유효 하한·상한·B 합계는 동일 v065 검증 사용, 새로운 최적화 알고리즘은 제작하지 않는다. 아직 측정하지 않은 후보를 '근접 성능'으로 표현하지 않는다.
- 이미 소스·캐시를 검증한 `runner/v094_durable_inclusive_adaptive_runner.py`에 opt-in `material_scouts=0..2`와 CLI `--material-scouts`를 연결했다. `2 초기 후보 + 일반 scout + material scout + 2 fresh confirmation` 호출 한도와 세션 봉인을 함께 검증한다. `material_scouts=1, scouts=0` 시 최소 **5회**를 시나리오의 `max_native_calls`가 명시 허용해야 한다. 기존 기본 4회 호출 제한을 몰래 넘지 않는다.
- 선택은 B 좌표, Native 입력/캐시는 **고정 O 포함 T 좌표**. 장비16슬롯·APL·티어·장신구·프로필·원본 바이너리·기름 identity를 보존. 기존 v065 실행/JSON2·SHA 캐시·재개를 호출.
- 기존 `v094._candidate_summary`가 **실측 대상에 대해서만** 소재 거리 10%+관측 손실1% 이내 대안으로 표시, 그 후보가 95% 기준 **열세**면 `OBSERVED_NEAR_BUT_LOWER_AT_95`, 아직 구분되지 않으면 `OBSERVED_NEAR_UNRESOLVED_AT_95`로 분리한다.
- `precision_plan`은 95%에서 평균 DPS 차이를 구분하지 못할 때 **현재 SEM에 근거한 확인 iterations 추정 제안**만 한다. 실제 추가 Native 실행은 시나리오에 허용된 confirm_iterations와 호출 상한을 넘을 수 없으며, 이번 실제 시험에서는 95% 구분이 되었기에 **추가 반복은 수행하지 않았다**. 범용 자동 precision-escalation 전체 라이프사이클 완성으로 주장하지 않는다.
- 97% 신뢰구간 계산·필드·표시 **신규 결과에서 전부 제거**. GitHub 과거 v094 히스토리 문서의 당시 97% 실험 기록은 이력으로 남을 수 있으나 현재 런타임 UI는 오직 95% 사용.
- 효율: 별도 탐색 엔진·정적 G 재측정·아이템 효과 연구 Gate 없음. Native 호출 5회/5회 SHA 재개, 입력 원본 보존. JSON2 검사·캐시는 기존 경로 재사용.

## 정확한 GitHub CI
최종 [Actions #40268656884](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40268656884) **SUCCESS: 총540 테스트 중 538 PASS/2 역사 SKIP/0 FAIL**; 파일·계약 Git blob SHA 핀, 전체 pilot PASS, CI Native **0회**. 초기 Actions #40268201579 역시 SUCCESS (537PASS/2SKIP). 최종 GH source artifact **ID 12627632078**, ZIP SHA256 **`543aa5d35302933f5b654cac87e6082a536c520552fab17b627d9876e434bbae`**. 이를 로컬로 내려받아 Git blob SHA가 최신 v094 `687e2509cb8780972c4c931bfdb4b1f902435dcc`, v095 `5c3d5d2f180025e7aa9f3782b8d87ff4c0ce1ea8`와 일치함을 재검증.

## 실제 Native 신규 5건 (CI 실행과 분리)

분노 전사 Fury, 334레벨, 양손 2H 무기쌍수, 최고 품질 기름 양쪽 적용, **B=3350**, 고정 `o=(치명32,가속32,0,0)`, **최종 T=3414**, 동일 정확 장비 16개. 기존 고정 SimC binary SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`, revision `7bc10711b5`. 호출 한도는 이 시험의 typed scenario에 사용자 허가 범위에서 **5**로 명시 설정했다(기존 4회 묵시 변경 아님).

| 실제 Native 단계 | 최종 T: 치명/가속/특화/유연 | DPS | SEM | Iterations |
|---|---|---:|---:|---:|
| 초기 A | 870/870/837/837 | 203297.24 | 786.76 | 35 |
| 초기 B | 970/770/837/837 | 201328.48 | 870.97 | 35 |
| 기존 v065 기반 **큰 폭 대안 Scout** | 535/870/837/1172 | 202391.95 | 975.39 | 35 |
| **초기 A 신규 정밀 확인** | 870/870/837/837 | **203286.64** | **534.90** | 80 |
| **대안 신규 정밀 확인** | 535/870/837/1172 | **201534.15** | **530.09** | 80 |

최고 A와 대안의 B 좌표 간 이동량은 **335 rating = B의 정확히 10%**. 정밀 확인 DPS 차이 **1752.48**, A 대비 상대 DPS 감소 **0.8621%**, 95% 차이의 정규근사 반폭 **1475.98**. **1% 이내의 성능을 관측한 '실질적으로 다른 대안'은 이번에 확보했지만, 95% 근사 기준에서는 열세로 관측**됐다. 동급 성능이나 절대 글로벌 최적을 입증하지 않는다. 두 정밀 확인은 각각 80 iterations/79 samples, 서로 다른 SimC seed 확인. 95%에서 비교가 구분되어 추가 반복 추천/호출 없음.

5건 실행 후 **최종 GitHub 소스 바이트(기존 SimC 입력과 동일, 결과 라벨·단계 메타데이터 교정만)를 적용한 캐시-only 재실행에서 5/5 CACHED_VERIFIED_NATIVE, 추가 Native0회**. 보고서의 phase, 현 실행 cache HIT, 95% 우열 라벨 정합도 확인.

원본 Native JSON2/입력·원문 stderr/stdout·resume 진행/세션·실제 실행/재생 스크립트·최종 GitHub CI 소스 ZIP·SHA256 전수 manifest는 사용자 인계 ZIP **`SIMC_SECONDARY_OPTIMIZER_V095_MATERIAL_95_NATIVE_PROOF.zip`**, SHA256 **`6c3d213eab5b4b98ea0be11971c2231f41e59df788acb4740f99d6a7749d21da`**, **38 엔트리**로 보존. GitHub compact [실제 Native 영수증](../integration_probes/data/v095_material_95_five_real_native_receipt.json)도 기록.

## 남아 있는 제품 경계
실질적 대안 1개를 찾았다는 것이 전 전문화/다른 시나리오/전역 최적성을 입증한 것은 아니다. **SEM에 따른 추가 iterations 계산은 제안 단계**이고, 새 실행 한도를 확보한 조건에서 실제 반복 실행·추가 Native 독립 확인까지 자동 연결하는 기능은 후속 과제다. 임의 선택 특수장비 L, 모든 전문화, 원본 v015/v016 코드 완전 합치기, 완성 Windows UI는 미완료. 사용자가 공식 승인한 v1.3 Source의 Project UI 실제 적용과 독립 Work OS 원본 상태 변경도 여전히 영수증 미확인. GitHub main/v003 보호, 공식 M0 상태 임의 승격 없음.
