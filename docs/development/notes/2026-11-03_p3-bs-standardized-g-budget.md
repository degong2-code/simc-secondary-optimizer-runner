# 2026-11-03 · P3-BS · 대표 장비 G 총합 10 rating 표준화 → 기존 v222 예산

- **Capability:** `G.NUMERIC`, `BUDGET.GJFO`, `PRODUCT.E2E`
- **Keywords:** G, 반올림, nearest 10, 총합, 334, v234, Native JSON2, v089, v222, J, F, O, manual T
- **Prior evidence:** [P3-BL](../../P3_BL_20261103_ONE_SPEC_V233_G_PROFILE_IN_ORIGINAL_ENVIRONMENT_BUILD.md) = v233 실제 대표 원본 프로필; [P3-BM](../../P3_BM_20261103_OFFICIAL_EXPANSION_LEVEL_AND_V234_SOURCE_REPLAY.md) = v234 선택 Native 1회/원본 static v046 합계; [P3-BG](../../P3_BG_20261103_PREPROFILE_GJFO_ACCOUNTING_BRIDGE.md) = 기존 v222 단일 B/T 회계; `v089` 과거 시즌 10 rating 근사 참조는 **방법 참고만**, 새 시즌 G/J/F/O 숫자 근거 아님.
- **Decision:** `CONNECT` — 장비별/4개 스탯별 반올림 대신 **원본 관측 G 총합을 마지막에 10 rating 단위로 한 번 표준화**(5는 위로, 양수 정수). J/F는 각각 검증된 정확값으로 더하고 O는 기존 고정벡터로 T에 한 번, E/L은 원래 v222 규칙. 수동 최종 T가 우선. 같은 시즌/ilvl/무기형태/소스 정체성별 표준 참조를 구별하며 실제 원본 G와 반올림 오차를 보존한다.
- **Changes:** `v222.standardize_representative_G`가 **총 G 단 1회** nearest-10 half-up을 계산하고 raw/standard/delta/source SHA·ilvl을 기록, 기존 `preprofile_budget`는 검증된 G meta가 있을 때만 정합성 검사(구형 출력 형식 유지). 기존 `v234.observe`는 재사용한 v046 Native G 합계에 미승인 rounded-G preview 추가(JSON2 SHA 중복 계산 제거). 얇은 `v262`는 **관측 자료를 입력받은 ilvl만** 기존 v222로 B/T 행 생성. `tests/test_v222...`, `test_v262...`, `test_v263...` 회귀 신규 작성. 새 독립 스탯·Native 엔진 없음.
- **Verification:** 기존 v089 10 rating 참조와 v234/v222 역사 계약만 `REUSED_HISTORY`. 10단위 경계·총합만 반올림·수동 T/E/L/O·원본 SHA/ilvl drift·Native 관측 preview·ilvl별 출처/선택 동등성에 대한 **합성 테스트 코드 작성**, 신규 CI 실행 PASS/FAIL `NOT_VERIFIED`; 실제 외부 게임 HTTP0/SimC Native0. 변경 후 실 Source/Native 미실행, READY 미주장.
- **Remaining:** 실제 해당 시즌/ilvl/무기 트랙의 Native G 원본 실측 또는 유효 같은 시즌 G 참조는 아직 없음. 인증된 최고 품질 J/F/O/장비 선택 적용과 v216→v222 정상 설치·정책 A·26 DPS DPS E2E 미완료. v262는 **측정된 레벨만 출력**하고 누락 ilvl/새 시즌 J/F/O를 보간·추정하지 않음.
- **Efficiency:** G 표준화 O(1), 기존 v046 합계·v222 B/T 재사용; v234 Native JSON2 SHA는 한 번만 계산. 표준 ilvl 행은 입력된 측정 레벨당 O(1) 추가·Native/HTTP0, 임의 79×26 전수 반복 없음. G 원본/정책/track·소모품 소스별 캐시 키 구분은 최종 환경 설치 때 반영해야 하며 실측 실행시간·메모리/I/O 개선은 미측정.
