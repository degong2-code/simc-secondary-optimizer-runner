# 2026-11-04 · P3-CS · 동일 빌드 SpellEquippedItems 원본의 정상 v216 Build 연결

- **Capability:** `O.OIL`, `SOURCE.SEAL`, `PRODUCT.E2E`, `BUDGET.GJFO`
- **Keywords:** P3-CS, SpellEquippedItems, Wago, weapon class, subclass, inventory mask, v281, v216, v274, v217, v285, same build
- **Prior evidence:** [PROTOCOL](../PROTOCOL.md)→[INDEX](../INDEX.md)→[P3-CR](2026-11-04_p3-cr-spell-equipped-items-original.md) 실제 동빌드 Wago HTTP200/84,334B, 3개 기름 SpellID 모두 장비 class2/masks 73572352·983039; [P3-CQ](2026-11-04_p3-cq-item-id-native-binding.md) 기존 v281 exact ItemID→Native/155 PASS, [P3-CN](2026-11-03_p3-cn-real-source-integration.md) 실제 12 SimC temp matches(숫돌 혼재), P3-CO/CP 실제 6 Native/rating 관측.
- **Decision:** `CONNECT` — 새 독립 인증기/효과 구현이 아니라 기존 Wago v217 단계와 기존 v281 물리 ItemID→주문→SimC 관계에 원래 게임 DB2 무기 클래스/인벤토리/무기 하위클래스 제한을 출처로 붙인다. 실제 대표 무기 ID와 mask가 일치하지 않으면 자격 인증하지 않는다.
- **Changes:** v285 one-table same-build SpellEquippedItems sealed stage(최대8MB, 우선 v281 유효 후보 필요, GET1/캐시 재사용0), 정확한 on-use SpellID→장비 class2/2 mask를 기존 item row에 소스 필드로 추가. 혼합 숫돌·기름 임의 등록 금지, 실제 무기/손 적용과 최고 품질 효과 동일성·F/O/READY false. 정상 v216 collector→v274 기존 v191 source compiler에 봉인 후속 v285 input을 우선 연결. 기존 v284 stage/receipt/원본 정적 캐시 불변.
- **Verification:** 신규 focused/환경/API Actions 전 NOT_RUN. P3-CR 실제 source HTTP1/155 PASS와 P3-CQ 155 PASS, 기존 Native6은 REUSED_HISTORY. 이 변경 자체 신규 Native0, 실제 Wago GET은 Actions 합성 테스트에서0, 정상 신 시즌 최초 stage에서 최대1.
- **Remaining:** 실제 장비 item class/subclass/inventory type mask·hands·ilvl120 min을 내부 대표 무기 원본과 대조하여 조건 충족한 기름만 선택 가능. 아이템 전체 효과·품질 같은 범위, +1 rounding vs 공개 tooltip 차이, F/O numeric budget ownership, G/J/v222 B/T·Policy A·26 DPS E2E 미연결.
- **Efficiency:** 실 Wago 테이블 1종만 필요, 원본 5-table과 기존 v284/SimC snapshot 재조회하지 않음. v217 receipt로 cache hit0, source 84KB, SimC Native0. main/immutable/Project UI/Work OS 불변.
