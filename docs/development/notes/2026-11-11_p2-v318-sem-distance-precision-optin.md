# 2026-11-11 P2 v318 — IDEA-001 SEM·CHMV 거리 기반 정밀확인 우선순위 (선택형)

- **재사용 정책:** 기존 v290 고유 탐색 / 글로벌 reserve / 35·320 iterations / 기존 정밀 확인 주기 그대로. 별도 v318 pure policy는 **기존 v290에서 precision 액션을 만든 시점에만** 확정 320 후보 중 무엇을 먼저 재측정할지 정한다. 같은 Native 호출 횟수, 다른 정밀 후보의 실제 DPS 개선 가능성이 가설이다.
- **근거:** v315 기존 실 Native 23조건에서 v290/v312 iteration 예산 불일치; 최근 기존 v314 2전문화 n35·n120·n320 ×3 실제 비용에서 320은 35 대비 wall 약5.5~6배. 추가 중간 120은 ~45% 추가 호출 시간. 작은 noise 관측 고점을 과도하게 신뢰하지 않으면서 먼 대안을 보호한다.
- **새 코드:** `runner/v318_sem_distance_precision_priority.py` → `runner/v291_durable_multiscale_native_runner.py::run(...,sem_precision_priority_optin=True)` 단일 통합. 기본 false·원형 v290 코드/sha 미변경. 별도 session seal에 v318 정확 소스 SHA 포함. 변경된 pending 복구는 동일 planner 재계산 후 비교, 과거 v290 세션과 섞지 않음.
- **후보 선택:** precision 슬롯에서 아직 320을 실행하지 않은 후보 중 첫 320은 관측 최고를 우선. 이후 이미 320이 확인된 최고와의 `z_gap=(DPS_i - DPS_confirmed)/hypot(SEM_i, SEM_confirmed)`가 -1.96 이상인 후보만 경쟁 후보로 선별하고, 이동한 rating이 전체 T의 8% 이상인 먼 대안을 우선한다. 성능 판정용 95%가 아니라 **우선순위 휴리스틱**이다. 해당 경쟁 후보가 없으면 원형 v290 결정을 유지. 후보 기존 Native JSON2만 사용; DPS 예측/효과 재구현0.
- **장점:** 후보 좌표 생성/검증/Native 캐시·중단·재개 중복 구현 없이, 통계 오차와 멀리 떨어진 근접 대안에 확인 예산을 집중. 장점은 **가설**, 반드시 원본 v290과 똑같은 total iterations/wall에서 SimC 품질 평가 필요.
- **위험:** 큰 SEM 후보의 우연한 UCB로 확인 slot 낭비, 멀리 떨어진 경합 후보 편향, early high scout mean 민감성. threshold 8%/z=-1.96은 조정 가능한 검증 전 정책값으로 제품 95% 통계적 보증 아님. 이 실험은 정밀 확인 *횟수나 주기*를 바꾸지 않아 계산비 감소가 자동 실현되는 것도 아니다.
- **시험:** 새 `tests/test_p2_v318_sem_precision_optin_offline.py`로 pure ordering/입력 검증 및 synthetic v291 Native0 replay·다른 알고리즘/기존 seal 분리를 검증하도록 코드를 추가. Workflow [v318 opt-in focused](../../.github/workflows/p2_v318_sem_precision_offline_once.yml)는 push sentinel 시 GitHub CI 실행, 결과 PASS는 실행 영수증 확인 뒤 기록. 새 Native0, 실제 DPS 향상 증거0.
- **다음 순서:** v317 실 Native 타이밍 확인 → 이 v318 focused/offline CI PASS → 실제 새 사용자 프로필에서 원본 v290 vs opt-in v318의 동일 iterations, 동일 wall 별도 최소 A/B. 품질 개선 확인 전 default 바꾸지 않음.
