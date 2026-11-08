# P3-HAB · 최종 CHMV T 기준 각 스탯 50% 이상 배분 금지 (2026-11-08)

- **Capability:** `OPTIMIZER.POLICY`, `BUDGET.GJFO`
- **Keywords:** strict half cap, CHMV, final T, B+O, integer rounding, locked L/E, hard upper, v061/v065/v063, Native
- **Prior evidence:** 승인 설계 §8.1: 초기 각 스탯 범위 0~50%, 사용자 min/max 조정; 코드 `v061`과 `v065.bounds`에서 `floor(B * max_fraction)`를 포함하여 정수상 정확히 50%를 허용했음. `v098.initial_seeds`는 기존 bounds를 사용하며 `v290/v291` 역시 `v065.bounds`를 통과. 2026-11-08 사용자 직접 결정은 위 경계보다 엄격함.
- **Decision:** `EXTEND` — 모든 2차스탯에서 **최종** `c_final[s]=c_base[s]+O[s] < T/2` 필수. 정수 최종 cap `(T-1)//2`; 자유분배 기본 cap `(T-1)//2-O[s]`, `T=B+sum(O)`. 기존 사용자 `max_fraction`는 추가로 더 엄격한 cap을 줄 수 있으나 이 규칙을 완화하지 못함. L/E/F 고정치 위반·분배 공간 없음은 Native 전 명시 차단.
- **Changes:** `v061.strict_final_half_base_caps` 단일 계산 함수를 `v061.normalize` 수동 총량 사전 검증, `v065.bounds` 전체 scout/seed/confirm/v290·v291 범위, `v063.check_target` SimC numeric 직접 후보 주입 마지막 검증에 재사용. 기름 O는 한 번만 포함, 이전 원본/바이너리/SimC effect 미변경. 별도 탐색 알고리즘 생성 안 함. 기존 v094/v291 실행 세션에서 새 규칙에 위배되는 과거 후보는 재사용 금지·검증 실패로 차단(실행 성공을 가장하지 않음).
- **Verification:** 최초 strict-cap 코드 `a108fa3b`의 [focused #42485784565](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42485784565): **460 PASS/2 SKIP/0 FAIL**, `DEV_LEDGER_PASS`, 신규 strict cap 4 PASS. 별도의 기존 [v202 #42485784560](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42485784560), v182 #42485784499, v181 #42485784598은 **각 FAIL**: 기존 v202 테스트가 3000 B 중 versatility 1881(62.7%) 집중 배분을 적합 후보로 기대한 동일 원인. 수정본은 E floor 218(불합격) / 219(합격)을 보존하면서 vers 1281로 대체하고 이전1881은 명시적 부적합으로 시험. 수정 뒤 전체 CI 결과는 별도로 확인. Native 신규0; 기존 실 Native3/6 중 과도한 집중 사례는 역사 증거로만 보존.
- **Remaining:** UI의 기존 50% 상한 문구는 사용자에게 '50% **미만**'으로 안내하고, 기존 sealed 결과 불일치 시 새 세션을 생성하도록 제품 경로를 확정. 새 실제 7회 이상 SimC 측정은 별도 성능 시험.
- **Efficiency:** 4개의 정수 상한 연산만 추가; 새로운 Native, 원본/API 재수집, 추가 최적화 엔진, 효과 인증 Gate 0. 모든 후속 탐색은 후보 생성 전에 제약 적용하여 불필요한 SimC 실행 방지.
