# 2026-11-04 · P3-CR · 실제 같은 빌드 기름 적용 무기 원본 최소 확인

- **Capability:** `O.OIL`, `F.FLASK`, `SOURCE.SEAL`, `BUDGET.GJFO`, `PRODUCT.E2E`
- **Keywords:** P3-CR, oil, SpellEquippedItems, game weapon class, inventory mask, item quality, native contrast, P3-CQ
- **Prior evidence:** [PROTOCOL](../PROTOCOL.md)→[INDEX](../INDEX.md), [P3-CQ](2026-11-04_p3-cq-item-id-native-binding.md) 정상 v216의 v281 ItemID→Native 연결 155 PASS, 실제 P3-CO/CP Native6회, 실 Wago 원본 P3-CN. 외부 WoW 주문 설명은 1237006/1237008의 Main/Off Hand·무기 및 최소 아이템레벨120을 보고하나 같은 source 빌드 DB2 수치 마스크 직접 검증 전 미승격.
- **Decision:** `EXTEND` — 실제 제품 입력의 물리 무기 적합성을 결정할 수 있는 원본 부족만 좁혀 SpellEquippedItems 한 테이블을 동일 12.1.5.70575 빌드에서 1회 확인. 별도 효과 엔진·인증 Gate/전수 Native·아이템 전체 DB 수집 금지.
- **Changes:** 기존 Wago CSV/샘플 조회 경로를 이용하여 대상 Phoenix Oil 사용 주문 1237006/1237008과 Dawn Oil 1237001의 SpellEquippedItems 컬럼·정확한 행만 관측하는 one-shot Action, 결과는 소형 SHA receipt. 기존 품질/rating/최적화 동작 미변경.
- **Verification:** [실제 Wago #41732744145](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41732744145) SUCCESS, 동일 Retail build 12.1.5.70575 SpellEquippedItems CSV 84,334B, SHA256=79a27158f88ca0f8ace9d1924bec2fd8af1eb6c2e121cc30a7e2f1213eb37fbc, 실제 HTTP1·Native0. SpellID=1237001(Dawn), 1237006(Phoenix rank2), 1237008(Phoenix rank1) 모두 EquippedItemClass=2, EquippedItemInvTypes=73572352, EquippedItemSubclass=983039; DB2 RowID=254975/254979/254980. [focused #41732744058](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41732744058) 155 PASS/0 FAIL, DEV_LEDGER_PASS. P3-CQ 155 PASS·실 Native6회는 REUSED_HISTORY. 실제 대표 무기 mask까지 대조하지 않았고 F/O는 미승격.
- **Remaining:** 결과에 따라 같은 기존 v281의 소비품 관계로 class/mask를 연결하고 무기/손·최저 ilvl이 실제 대표 프로필과 일치할 때만 영구예산 소유권에 사용. F/O 숫자와 v222 B/T·품질 A·26 DPS E2E 미완료.
- **Efficiency:** Wago 테이블 1종/행 3개만 필터, 8MB upper bound, 대형 원본 저장0, 기존 핀 SimC/source/Native 캐시 재사용. main·immutable·Project UI/Work OS 변경 없음.
