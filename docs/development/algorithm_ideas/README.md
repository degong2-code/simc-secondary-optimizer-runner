# CHMV 알고리즘 아이디어 정본 목록

**목적:** 대화마다 제안되는 알고리즘 아이디어를 **각각 독립된 파일**로 영속 기록하여, 한번에 동일 예산으로 비교하고 채택/기각을 근거로 결정한다. 아이디어 기록은 개발 구현이나 Native 성능 PASS가 아니다.

## 2026-11-11 최신 승인 — 품질/실행 효율 우선, 10분 초과는 폐기 사유 아님
- **최신 사용자 직접 결정:** 5~10분은 바람직한 사용자 목표지만 하드 제한이 아니다. 더 높은 정확한 SimC 확인 DPS를 합리적인 실행 비용으로 얻는 정책은 10분을 넘더라도 비교·채택 후보로 유지한다. 정확한 iterations·wall·CPU·메모리·I/O·캐시/재개 및 SEM/95 한계를 함께 기록. 연구 실행과 제품 기본 사용 시간은 별도.
- **이 채팅의 단일 아이디어 판정:** IDEA-001의 확인 예산 `quality–cost Pareto / anytime reserve`를 고도화, **새 ID 생성 없음**. 원본 [IDEA-001 상세](algorithm_ideas/IDEA-001-multifidelity-successive-halving.md)에 근거·중복·반증·단계별 최소 실증을 기록. 현재 `IDEA_ONLY`; v316 Native 실측이 먼저.

## 순서 및 상태

| 고정 ID | 알고리즘 | 문서 | 상태 | 비교에 필요한 주요 축 |
|---|---|---|---|---|
| IDEA-001 | 다중 정밀도 경쟁 탐색 (Successive Halving) | [상세](IDEA-001-multifidelity-successive-halving.md) | `IDEA_ONLY` | 측정 반복 수/승급 조건 |
| IDEA-002 | 다중 시작점 신뢰영역 (Multi-start Trust Region) | [상세](IDEA-002-multistart-trust-region.md) | `IDEA_ONLY` | 여러 지역 반경·정체·탈출 |
| IDEA-003 | 적응형 층화 탐색 (Adaptive Stratified Exploration) | [상세](IDEA-003-adaptive-stratified-exploration.md) | `IDEA_ONLY` | 전역 공간 셀별 탐사 예산 |
| IDEA-004 | 비용 인지형 지식 기울기 탐색 (Cost-aware Knowledge Gradient) | [상세](IDEA-004-cost-aware-knowledge-gradient.md) | `IDEA_ONLY` | 확인 DPS 순위 개선의 기대 정보 가치 / SimC 실행비용 |
| IDEA-005 | 조건부 짝시드 실측 분산 감소 (Paired Seed CRN) | [상세](IDEA-005-conditional-paired-rng-variance-reduction.md) | `IDEA_ONLY · HOLD_FOR_FEASIBILITY` | 재측정 후보 쌍 DPS 차이의 **실제 양의 공분산** 검증 |
| IDEA-006 | 국소 민감도 비등방성 탐색 (Active Subspace) | [상세](IDEA-006-anisotropic-active-subspace-search.md) | `OFFLINE_SCREENED · LOCAL_QUADRATIC_HOLD` (Native 0) | 기존 9,906 scout/48 precision: 국소 모델 정확도 미개선·방향 안정성 제한; 실제 방향 탐색 우위 미검증 |
| IDEA-007 | 다중 정책 온라인 포트폴리오 (Policy Bandit) | [상세](IDEA-007-online-policy-portfolio-bandit.md) | `IDEA_ONLY · INTEGRATE_LATER` | 탐색 생성기별 예산 배분과 최악 성능 완화 |
| IDEA-008 | 최종 후보 독립 홀드아웃 확인 (Post-Selection Holdout) | [상세](IDEA-008-postselection-independent-holdout-confirmation.md) | `IDEA_ONLY · INTEGRATE_FINAL_DECISION_ONLY` | 선정 표본과 검증 표본 분리, 명목95와 가족단위95 구분, 추가 비용 대비 신뢰도 |

## 중복성·통합 효율 사전 심사 (2026-11-11)

다음 판정은 **설계 검토 결과**이며 구현·실측 성능 증거가 아니다. 각 아이디어의 동기·장단점·효율 가설·증거 부족·중단 조건은 **독립 상세 문서**에 기록한다.

| ID | 기존 정책과의 중복 | 신규 엔진 필요 여부 | 통합/진행 판정 | 최소 검증 항목 |
|---|---|---|---|---|
| IDEA-001 | v290의 기존 재측정 정책과 중복 | 불필요 | **INTEGRATE_FIRST**: 35→120→320 선택 승급만 v290에 옵션으로 | 동일 iterations에서 5/10분 확인 DPS, 조기 탈락 |
| IDEA-002 | v303 지역 배분·v306 escape와 **매우 큰 중복** | 불필요 | **REUSE_AND_ABLATE**: 기존 반경 갱신 규칙만 대조 | 지역 중복/미발견 고점/CPU·Native 비용 |
| IDEA-003 | v290 전역 maximin·v312 전역 reserve와 중복 | 불필요 | **INTEGRATE_COVERAGE_OPTION**: 전역 후보만 공간 셀별 부족도 기준으로 교체 | 빈 셀 낭비 대비 신규 고점 발견 |
| IDEA-004 | v312 UCB·IDEA-001 재측정과 높은 중복 | 현 단계 불필요 | **HOLD_FOR_CALIBRATION**: 오차 확률 보정 가능 시 후보 재순위 함수만 시험 | 확률 보정, planner 비용, 같은 비용의 실제 DPS |

**통합할 때의 원칙:** IDEA-001은 *iterations/재측정 예산*, IDEA-002는 *지역 중심과 반경*, IDEA-003은 *전역 남은 공간*, IDEA-004는 *후보 기대 정보가치*를 담당한다. 서로 다른 예산 소유권은 하나의 v291 예약기에서만 최종 승인하며, v303/v312의 기존 기능을 두 번 실행하지 않는다. 단순 병합으로 인한 상승효과는 **미검증**이고, 독립 옵션의 `ablation` 이후 결합 효과를 별도로 시험한다.

## 이번 누락 제안 보완 3건의 중복·통합 사전 비교

| ID | 기존 기능/아이디어 중복 | 검증 전 결론 | 기존 엔진과 통합할 최소 단위 | 핵심 반증 |
|---|---|---|---|---|
| IDEA-005 | v290 정밀 재측정·IDEA-001 승급과 부분 중복 | **HOLD** | v291 최종 A/B 확인 방법의 실험 옵션 | 같은 seed의 실제 짝공분산이 양수인지, 실행비용 포함 CI가 더 좁아지는지 |
| IDEA-006 | v290 pairwise·v303 반경·v312 곡면과 부분 중복 | **국소 독립 fit HOLD; 기존 cubic 미분 방향만 후속 연구** | v312 기존 3차 모델의 gradient/Hessian 재활용으로 v303 지역 후보 생성방향만 변경 | 역사 48 precision RMSE 악화 및 8영역 중 4곳 방향 일치도 0.8미만; 실제 320+ 탐색 우위 미검증 |
| IDEA-007 | v303 지역 자원 배분·v312 후보 유형 배분과 구조적 중복 | **후순위 통합 연구** | v291 단일 세션 아래 *후보 생성기* 예산 선택기 | 전략 간 후보 상보성이 없거나 journal/cache 복잡성만 늘어나는지 |

- **권장 순서:** 먼저 IDEA-006 단독 옵션을 기존 v290/v303 기준으로 비교 → IDEA-005 짝공분산의 가능성만 최소 Native로 판정 → IDEA-007은 후보 생성기 순수화와 정확한 cache/journal 재개가 확보될 때 검토. 개발 순서는 v313→v314 현재 사용자가 지시한 **기존 실제 시험 순서를 바꾸지 않는다**.
- **서로 합칠 수 있는 부분:** IDEA-006이 생성한 방향 후보를 IDEA-001의 정밀도 승급 옵션으로 확인할 수 있다. IDEA-007은 위와 같은 검증된 후보 생성기에만 최종 예산을 할당한다. IDEA-005는 그 후의 소수 후보 확인 단계에서만 선택 가능하고, 동일 seed와 95% 판정을 자동으로 결합해서는 안 된다.
- **새로운 전역 최적 증명/95% 확정:** 어느 것도 제공하지 않으며 아이디어 등록을 구현·실측으로 취급하지 않는다.

## 새 아이디어 추가의 필수 심사문턱

기존의 '채팅마다 아이디어 무조건 추가'를 폐기한다. 원칙적으로 **응답마다 근거 있는 새 아이디어 최대 하나**를 검토·제안하되, 사용자가 이번 대화에서 명시적으로 요청한 **이전 누락분 보완에 한해서 IDEA-005~007 세 건**을 독립 심사 후 함께 기록했다. 이 예외를 향후 무조건 3개 제안으로 일반화하지 않는다. 다음 항목이 근거로 채워질 때만 신규 ID를 발급한다.

1. **관측된 문제/발상 이유:** 무엇이 실제 수치·원본 SimC 영수증으로 관측됐고 무엇이 추정인가.
2. **작동 메커니즘과 효율 근거:** 어떤 SimC 호출·iterations·탐색 누락·SEM 오류를 줄이는가. 이익이 발생할 수 있는 필요조건은 무엇인가.
3. **기존 아이디어 및 코드 전수 대조:** v290/v303~v306/v312 및 IDEA-001~004 등과 기능적 중복·차별성, 기존 옵션으로 해결 가능한지.
4. **장점·단점·실패 조건:** 탐색 다양성, 조기 고점 제거, 예측 모델 보정, CPU·메모리·I/O·cache/resume 복잡성.
5. **통합 우선 판단:** `REUSE` / `INTEGRATE` / `EXTEND` / `NEW` / `HOLD` 중 선택; 중복 기능이면 새로운 전체 엔진을 만들지 않는다.
6. **사전 정의한 반증/중단 기준:** 동일 신규 프로필·wall-clock·총 SimC iterations에서 최고 320+ 확인 DPS·SEM·5/10분 발견속도·실험 실패를 어떻게 측정할지.
7. **증거 상태:** `IDEA_ONLY`·오프라인 구현·실제 Native·전문화 간 검증을 분리. 앞선 대화의 아이디어를 다시 이름만 바꾸어 신규 건수로 세지 않는다.

이 기준을 통과하지 못하면 **이번 채팅에는 신규 아이디어 없음**이라고 설명하고 중복 제안의 통합/보류 사유를 제시한다. 제품 기본 v290과 보호된 main을 임의로 변경하지 않는다.

## IDEA-006 음성 오프라인 스크린 결과 (2026-11-11)

[원본 9,906 scout35/48 precision320 검증 #42856597090](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42856597090) SUCCESS, 신규 Native 0. 국소 2차 회귀의 정밀 48건 예측 RMSE는 학습 128/400/1200에서 각각 **303.929/286.451/279.108 DPS**, 같은 표본의 기존 v312 전역 3차는 **227.863/282.815/248.605**. 8개 영역의 가장 평탄한 Hessian 방향을 절반 표본으로 구했을 때 **4/8이 abs cosine 0.8 미만**. 사후 반경 선택은 독립 검증이 아니며, **국소 모델 정확도 실패를 실제 비등방성 좌표 탐색의 실패라고 과장하지 않음**. [상세 기록](../notes/2026-11-11_p2-idea006-real9906-localfit-holdout-negative.md).


## 2026-11-11 v317 개발 채팅의 단일 신규 아이디어 — IDEA-008

**근거:** [v313](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42843524976)/[v314](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42846073820) 23개 완전 Native 비교 중 명목 선택쌍 95 우위 확정 0. v291의 선정된 후보를 같은 표본으로 판정한 경우 선택편향과 다중비교가 미교정이다.

**중복 반론 검토:** IDEA-001은 재측정 예산, IDEA-005는 seed pairing 분산 감소, 기존 benchmark 홀드아웃은 새 프로필 간 일반화. 이 세 기능으로 **같은 세션에서 최종 선택한 CHMV를 미사용 Native 표본으로 검증**하는 단계가 제공되지는 않는다. 따라서 이 문제를 독립 통계적 결정 단계로 한정해 **신규 IDEA-008 한 건**에 등록한다. 새 탐색 엔진을 만들지 않는다.

**통합/반증:** v291의 단일 예약기·원본 Native 캐시/봉인을 확장할 때만 가능. 먼저 v317 단일 사용자 프로필 실제 계측 → 오프라인 독립 표본 재사용 금지 계약 → 소수 후보만 별도 seed로 최소 Native 확인 → 같은 iterations·실제 wall·장시간 품질-비용 Pareto. 추가 비용 대비 독립 승자/근접대안 신뢰성 개선이 미증명되면 HOLD. [상세](IDEA-008-postselection-independent-holdout-confirmation.md).

## 기존 실험 기준군 (새 아이디어가 아님)

| 정책/기법 | 참고 | 관측된 검증 범위 |
|---|---|---|
| 기존 기본 v290 | [실험 기록](../notes/2026-11-10_p2-v312-surrogate-5to10min-adaptive.md) | 기본 정책, 신규 v312와 같은 프로필/각 1008 Native 실제 비교 |
| v303–v306 지역 적응/escape/hybrid | [실험 기록](../notes/2026-11-10_p2-v306-offline-v305-escape-coverage.md) | 기존 지역 후보 생성/원본 증거의 범위 내 |
| v312 다중 영역 3차 대리모델 | [실험 기록](../notes/2026-11-10_p2-v312-surrogate-5to10min-adaptive.md) | `IMPLEMENTED_OPT_IN`, Warlock 1008 Native 실측; 8·16 새 프로필 비교는 별도 결과 필요 |
| GP/RBF·MADS/Sobol 가능성 | [기존 GP 비교](../notes/2026-11-10_p2-real-simc-global21-local6-gp-comparison.md) | 과거 탐구/비교의 정확한 일부 범위만. 이 목록에서 신규 Native PASS로 간주하지 않음 |

## 공통 비교 계약

1. **소스:** 사용자 요청의 *신규 생성* 프로필을 8개 DPS 전문화 × 2개 CHMV 총량·상한 분포(총 16개)로 구성. 동일 케이스에서는 클래스·특성·장신구·대표 장비·시즌/빌드·SimC SHA·기름/O·전투조건을 동일하게 고정하며 각 정책은 과거 최고점/과거 Native 캐시를 seed하지 않는다. v314는 아직 실측 결과 확인 전.
2. **예산:** Native 호출 수만 맞춘다고 동등 비교가 아니다. 총 SimC `iterations`, 확인 측정 횟수, 실제 스카우트 횟수 및 wall-clock 각 5분/10분을 모두 기록한다. 알고리즘 오버헤드도 포함하고, 5/10분 시점 최고 **정밀 재측정** DPS/SEM 비교.
3. **비교:** 전문화 간 DPS 절대값을 비교하지 않고, *동일 시나리오 안*에서 v290 대비 정밀 확인 최고 DPS 변화율을 산출한다. 결과 전체의 승/패/동률/미완료와 중앙값·분산·최악 편차, 발견 속도, 새 영역 발견 비율을 집계한다. 표본선택/다중비교 교정 없는 두 후보 간 명목95는 그 한계를 표기한다.
4. **진행:** 후보 정책을 구현한 뒤 각각 오프라인 결정론적 테스트 → 기존 사실에 맞춘 증거 분석 → 최소 원본 Native 실증 → 같은 예산의 다른 새 프로필 재현을 순서대로. 모형 예측값을 관측 SimC DPS로 대체 금지, SimC 효과·APL·proc 독립 재구현 금지.
5. **의사결정:** `IDEA_ONLY` → `IMPLEMENTED_OPT_IN` → `OFFLINE_VERIFIED` → `ACTUAL_NATIVE_OBSERVED` → `CROSS_SPEC_EVALUATED`의 **증거 범위별** 표기를 사용한다. 단계를 높일 때 Actions/원본 SHA/실제 전문화·예산과 함께 기록하고 실패·보류도 그대로 보존한다. 성능 우위 근거 없으면 v290 유지.
6. **실행 순서:** 사용자 지시대로 현재 v313 [Actions](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42843524976) 종료 뒤에 v314 [Actions](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42846073820) 시작. 아이디어 기록 작업은 실행 트리거 변경·Native 추가를 하지 않는다.

## 추가 기록 규칙

- 채팅당 **최대 1개**, 새 발상 이유·장단점·구현 중복·통합 가능성·효율 작동 조건·반증 실험을 먼저 심사한 경우에만 해당 ID를 발급해 **별도 상세 파일을 생성**한다. 설득력 없는 중복 제안은 새 ID 없이 보류한다. 이전 ID나 제안 원문을 수정할 때에는 근거를 보존하고 변경 이력을 기록한다.
- 나중에 모든 알고리즘을 한 번에 비교하도록 통합 평가표를 유지하되, 시나리오·seed·time/iteration 설정과 동일 조건 여부가 다른 실험의 성적을 섞지 않는다. 비교 문서: [벤치마크 설계](BENCHMARK_PROTOCOL.md).
