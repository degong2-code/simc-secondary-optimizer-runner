# 2026-11-03 · P3-BU · 일반 대표 G는 현재 시즌 소속이 아니라 물리·스탯 조건으로 판단

- **Capability:** `GEAR.SEASON`, `G.NUMERIC`, `BUDGET.GJFO`, `PRODUCT.E2E`
- **Keywords:** G, generic budget, 대표일반장비, 시즌 비필수, armor, primary, plain, ItemXItemEffect, v232, v233, v234, v216
- **Prior evidence:** [P3-BI](../../P3_BI_20261103_SELECTED_GEAR_SEASON_PROVENANCE_AND_G_PENDING.md) 기존 v165/166/167 plain 분류·WSE 출처 및 v232 선택; [P3-BL](../../P3_BL_20261103_ONE_SPEC_V233_G_PROFILE_IN_ORIGINAL_ENVIRONMENT_BUILD.md) v233 exact profile; [P3-BT](2026-11-03_p3-bt-normal-build-standard-budget-link.md) v234 G 원본→v216 재사용. 기존 v169의 전문화 주스탯/무기 형태 선정을 그대로 재사용.
- **Decision:** `CONNECT` — **사용자 2026-11-03 직접 정정 우선**: 같은 목표 ilvl/같은 슬롯 예산을 가진 일반 장비의 G 계산에서 *현재 시즌 획득 가능성*은 필수 조건이 아니다. 물리 슬롯/착용 재질·전문화 허용/사용 주능력치·무기 형태/일반 ItemSet=0·특수효과 없는 plain 분류 및 실제 Native static 수치가 핵심이다. 기존 시즌 출처 정보는 프로필 품질/획득 진단으로 유지하되 G 표준 참조를 막는 전용 Gate를 신설하지 않는다.
- **Changes:** v232의 기존 소스·물리 후보 선별에 primary-stat 적합 판별(부위별 적용), 기존 v165→v167 plain 효과 분류·기존 v169 weapon shape 재사용; 선택 소스에 G 물리 적합성/시즌 별개 구분 출력. v233/v234의 원본 정체성·Native G 결과에 해당 적합성 계승, v216 원래 Native 영수증 재사용 경로가 시즌 여부와 독립하여 G 산술 가능성을 표기. 관련 focused 회귀, INDEX/CURRENT 갱신. 별도 아이템 DB/시즌 인증 엔진 없음.
- **Verification:** 이전 SimC/DB2/Native 문서·테스트는 해당 범위만 `REUSED_HISTORY`. 신규 focused 실제 실행 PASS/FAIL은 확인 전 `NOT_VERIFIED`, 신규 Native/외부 데이터 HTTP 0회, 과거 artifact/캐시는 보존.
- **Remaining:** 실제 측정된 ilvl별 G·확정 J/F/O 값/선택 장비 L/E, 정책 A 등록·제품 프로필/SimC DPS E2E 미완료. 일반 장비 예산 적합성을 모든 장비/모든 슬롯의 예산이 같다는 주장으로 확대하지 않으며, 티어 실전 효과·특수장비/장신구 선택은 별도로 관리한다.
- **Efficiency:** 기존 v232 메타데이터 1회 파싱·v169 무기 적합성·v165 ItemXItemEffect 분류·v046 Native 합계 재사용. 시즌 미확정 아이템에 대한 WSE 별도 조사/새 Gate/무조건 26×79 Native 반복 없음. 코드 지문 변경 시 해당 source stage만 변화, 기존 시즌 정적 캐시 일괄 삭제 금지.
