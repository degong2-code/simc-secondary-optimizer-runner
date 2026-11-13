# v432 — B8 4세트 선택 교체 G/L 정적 차이 사전 계산 (미승격)

- **Capability:** `TIER.SEASON`, `GEAR.SEASON`, `CHARACTER.PROFILE`, `PRODUCT.E2E`.
- **Keywords:** B8, v432, v101, v098, v212, v222, v046 static cache, special L, crafted, 4-of-5, selected delta, 95%, SHA.
- **Prior evidence:** [v431 현 시즌 source pair 전달](2026-11-13_p1-v431-b8-sealed-season-injection-code-offline.md); [v430 B8 차단](2026-11-13_p1-v430-b8-four-of-five-new-season-source-bridge-gap.md); [v417 기본 현시즌 Native](2026-11-13_p1-v417-bounded-post-bridge-product-e2e-once.md).
- **Decision:** `CONNECT` — 오프라인·읽기 전용 **사전 계산 계층**만 구현. 기존 v101 4-of-5 및 v212 설치·v046 정적 변형·v222 예산을 재사용하며 사용자 Native/제품 실행 허가는 주지 않는다. B8 generic/current_source/product_integration=PENDING, historical=PASS 유지; 완료 7/78, next_review=B8, 전체 E2E PENDING.
- **Changes:** `runner/v432_selected_4pc_budget_bridge.py`에서 v212 검증 호출·v191 SHA 링크·v232 기준 슬롯 ID·정확 4티어를 확인하고, 교체된 슬롯의 **이전/신규 bare Native 정적 변형**만 조회. G는 공식 설치 `reference_G`에 정확 교체 delta를 적용한 **근사 참조 + 관측 차이**로 명시(전 부위 exact Native G가 아님). 특수장비 bare L을 내부 G 하한으로 1회 반영, 제작 초기 50:50 비잠금. O/J/F/E 분리·수동 최종 T 우선·불가 예산 차단; 캐시 누락은 정확 항목만 PENDING. 세션·설치 문서 원본 변경 및 SimC/Native 실행 없음. 신규 전용 테스트 8개, 기존 v187 workflow에 집중 회귀 결합.
- **Verification:** [격리 코드 커밋](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/8d2a107b682a6fc3beb894fcdc6a16eed11a8883), [v187/v432 focused #43440892382](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43440892382) **24 PASS + 36 연관 PASS / 0 FAIL**. [78 계약 #43440892251](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43440892251) SUCCESS. [범용 ledger #43440892248](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43440892248)는 이전 장부 형식 198건으로 FAILURE, 신규 코드 Native 결함 영수증 아님.
- **Remaining:** 이 사전 함수는 아직 v098의 `season_profile_inputs` 선택 장비 실 사용자 경로에 연결되지 않았다. `v098.build`의 nonempty special/embellishments **차단 유지**. v212/원본 실제 선택 부위에 대한 승인된 exact Native 스탯·동일 시즌 캐시 범위·변경 소켓/마부/무기 오일 적합성·G 기준 슬롯 출처를 실제 owner로 묶고, 이후 v096에 source/sealed budget identity를 전달해야 한다. 단순 guard 삭제/legacy 70575 재사용 금지. 오프라인 통합 성공 후 실제 70783 사용자 충돌 변형 1건 최소 Native/JSON2/DPS·SEM·95%로 B8 세 필수축 별도 판정. B1·B4·B5·B6 제품 통합 PENDING도 보존.
- **Efficiency:** 새 Native 0, 새 API·DB2 0, source rescan 0, 기존 탐색기·세션·캐시 수정 0. 변경 슬롯의 exact v046 변형만 조회, 캐시 전체 Native 재실행·78개 새로운 Gate 도입 없음.

## 사용 경계

`reconcile(...)`은 v101이 완성한 4pc 물리 장비의 **before/after**와 검증된 v212 manifest·v191 원본 링크·v232 G 슬롯 맵·시즌별 v046 캐시를 입력으로 받는 순수 단계다. 전달받은 SHA가 진짜 원본인지는 기존 v098/v212 owner가 먼저 확인해야 한다. 합성 cache·mock v212 검증으로 한 오프라인 테스트는 70783 실 source/프로필/Native 승인 증거가 아니다. 결과 `B8_SELECTED_PHYSICAL_G_L_RECONCILED_NOT_ADMITTED`도 **완료/READY가 아니며**, 현재 계절 참조 G가 10단위 근사일 수 있음을 계속 표시한다.

**다음 개발은 v098/v216 사용자 선택 변형의 설치 SHA+물리 슬롯+G/L 동시 소유권을 실제 실행 경계에서 연결**하는 것. 제품 기본 4pc v417 Native12와 26 DPS 재실행은 하지 않는다.
