# 2026-11-03 · P3-BS · 대표 장비 G 총합 10 rating 표준화 → 기존 v222 예산

- **Capability:** `G.NUMERIC`, `BUDGET.GJFO`, `PRODUCT.E2E`
- **Keywords:** G, 반올림, nearest 10, 총합, 334, v234, Native JSON2, v089, v222, J, F, O, manual T
- **Prior evidence:** [P3-BL](../../P3_BL_20261103_ONE_SPEC_V233_G_PROFILE_IN_ORIGINAL_ENVIRONMENT_BUILD.md) = v233 실제 대표 원본 프로필; [P3-BM](../../P3_BM_20261103_OFFICIAL_EXPANSION_LEVEL_AND_V234_SOURCE_REPLAY.md) = v234 선택 Native 1회/원본 static v046 합계; [P3-BG](../../P3_BG_20261103_PREPROFILE_GJFO_ACCOUNTING_BRIDGE.md) = 기존 v222 단일 B/T 회계; `v089` 과거 시즌 10 rating 근사 참조는 **방법 참고만**, 새 시즌 G/J/F/O 숫자 근거 아님.
- **Decision:** `CONNECT` — 장비별/4개 스탯별 반올림 대신 **원본 관측 G 총합을 마지막에 10 rating 단위로 한 번 표준화**(5는 위로, 양수 정수). J/F는 각각 검증된 정확값으로 더하고 O는 기존 고정벡터로 T에 한 번, E/L은 원래 v222 규칙. 수동 최종 T가 우선. 같은 시즌/ilvl/무기형태/소스 정체성별 표준 참조를 구별하며 실제 원본 G와 반올림 오차를 보존한다.
- **Changes:** 기존 v222 순수 예산 계약의 G 표준화 메타데이터/정합 확인 및 focused 테스트에 국한. 새 독립 Native/아이템 스탯 계산 엔진이나 무조건 79 ilvl×26전문화 측정은 만들지 않는다.
- **Verification:** 최신 실제 GitHub 변경 후 신규 CI PASS/FAIL `NOT_VERIFIED`. 이전 동일 시즌 근사 표/기존 v234·v222 테스트는 `REUSED_HISTORY`이며 새 시즌 숫자 인증이 아니다. 이번 실 외부 HTTP/SimC Native = 0.
- **Remaining:** 실제 시즌 대표 장비에 대한 v234 G 총합 증거 또는 유효 같은 시즌 기준; 최고 품질 J/F/O·정확 적용 조건; 정상 Environment Build 소스 정규화/예산 설치 및 26 DPS DPS 최적화 E2E는 미완료. 이 helper만으로 READY 불가.
- **Efficiency:** 계산은 O(1), 원본 JSON·스탯 벡터/Native 재계산하지 않음; v222 합산 1경로 보존; 캐시 identity는 시즌/게임빌드/ilvl/무기형태/소스+반올림 정책에 의존. 성능 개선 실측은 아직 없음.
