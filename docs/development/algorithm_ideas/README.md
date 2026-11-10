# CHMV 알고리즘 아이디어 정본 목록

**목적:** 대화마다 제안되는 알고리즘 아이디어를 **각각 독립된 파일**로 영속 기록하여, 한번에 동일 예산으로 비교하고 채택/기각을 근거로 결정한다. 아이디어 기록은 개발 구현이나 Native 성능 PASS가 아니다.

## 순서 및 상태

| 고정 ID | 알고리즘 | 문서 | 상태 | 비교에 필요한 주요 축 |
|---|---|---|---|---|
| IDEA-001 | 다중 정밀도 경쟁 탐색 (Successive Halving) | [상세](IDEA-001-multifidelity-successive-halving.md) | `IDEA_ONLY` | 측정 반복 수/승급 조건 |
| IDEA-002 | 다중 시작점 신뢰영역 (Multi-start Trust Region) | [상세](IDEA-002-multistart-trust-region.md) | `IDEA_ONLY` | 여러 지역 반경·정체·탈출 |
| IDEA-003 | 적응형 층화 탐색 (Adaptive Stratified Exploration) | [상세](IDEA-003-adaptive-stratified-exploration.md) | `IDEA_ONLY` | 전역 공간 셀별 탐사 예산 |
| IDEA-004 | 비용 인지형 지식 기울기 탐색 (Cost-aware Knowledge Gradient) | [상세](IDEA-004-cost-aware-knowledge-gradient.md) | `IDEA_ONLY` | 확인 DPS 순위 개선의 기대 정보 가치 / SimC 실행비용 |

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

- 채팅당 **새 아이디어 1개**를 제안할 경우 해당 ID를 발급해 **별도 상세 파일을 먼저 생성**하고 이 표에 추가한다. 이전 ID나 제안 원문을 수정할 때에는 근거를 보존하고 변경 이력을 기록한다.
- 나중에 모든 알고리즘을 한 번에 비교하도록 통합 평가표를 유지하되, 시나리오·seed·time/iteration 설정과 동일 조건 여부가 다른 실험의 성적을 섞지 않는다. 비교 문서: [벤치마크 설계](BENCHMARK_PROTOCOL.md).
