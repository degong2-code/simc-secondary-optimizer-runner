# P3-HV · 기존 v065/v095 후보 선택 Native 호출당 CHMV 방향 커버리지 개선

- **Capability:** `PRODUCT.E2E`, `SOURCE.SEAL`
- **Keywords:** axis coverage, adaptive SimC, candidate selection, v065, v095, Native efficiency
- **Prior evidence:** [P3-HT 실 v094 6회](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42470887863), [P3-HU 실 v094 6회](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42472633337)에서 seed2+scout1+material1+confirm2, unique CHMV 최대4. 실제 관측 모든 후보에서 **mastery rating 735 고정**. 초기 두 씨앗은 치명↔가속만 이동하고 기존 score_direction=0 tie가 사전순 candidate를 선택해 최소 6회 Native로 전문화 차이를 포착하기 어려움. 신뢰도 낮은 저반복 scout 34회 / SEM 700~1,000, confirm 약319회 / SEM 280.
- **Decision:** `CONNECT` — **새 엔진/효과 계산이 아닌**, 원래 v065의 feasible neighbor 중 관측하지 않은 CHMV 축을 우선 탐색하도록 별도 OPT-IN ordering helper 추가. v095 원거리 후보도 같은 policy를 사용하도록 선택형 준비. 기존 `choose_next`·default `material_neighbor`·원본 v015/v016은 바이트/동작 불변. 새 통계 수준은 여전히 95%, 최적해 입증 불가.
- **Changes:** `v065.axis_coverage_choice`는 관측 후보별 rating min/max span, 새로 탐색할 축 수, normalized span 증가를 계산한 뒤 실제 SimC를 호출하지 않고 후보 1개만 선택. 기존 stat별 L/O 하한·B 제약을 v065.neighbors로 보존. `v095.material_neighbor(selection_policy='axis_coverage_v1')`은 opt-in에서만 새 ordering 사용, 기존 경로는 byte-identical.
- **Verification:** 코드 초안; 오프라인 focused/legacy+new 테스트 PENDING, 실제 Native 0회. 이전 실제 DPS 값은 **재사용 증거**이며 새 알고리즘 개선 DPS 입증이 아님.
- **Remaining:** v094/v096에 명시적 search identity OPT-IN 연결, 기존 sealed session 재개/캐시 drift 방지, 오프라인 PASS 후 최소 one-shot 실제 Native에서 4축 탐색과 DPS/SEM 관측. 전체 26전문화 native 및 새 전역 탐색 엔진 금지.
- **Efficiency:** 고정 6회 Native 기준 후보 다양성 개선, 추가 Native0; 후보 생성 시간 O(12×4×관측 수)로 SimC 대비 미미. 적응형 실행시간과 캐시/메모리/I/O 비용 증가 없음.
