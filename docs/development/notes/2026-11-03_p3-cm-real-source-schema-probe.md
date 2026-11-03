# 2026-11-03 · P3-CM · 소비품 동일 빌드 실제 Wago 원본 CSV 헤더 검증

- **Capability:** F.FLASK, O.OIL, SOURCE.SEAL, PRODUCT.E2E
- **Keywords:** P3-CM, Wago, same-build, ItemEffect, SpellEffect, live CSV, v160, v280, v281
- **Prior evidence:** PROTOCOL→INDEX→P3-CK 126 PASS, P3-CL 139 PASS. v280/v281은 합성 자료로 코드 검증; v160은 원본 CSV의 제한된 헤더 조회와 현행 workflow를 이미 제공함.
- **Decision:** REUSE — v160의 기존 소량 실측 기능을 2개 소비품 테이블에만 확장해 실제 컬럼을 선확인. 새 시즌 전체 DB/효과 엔진/별도 인증기나 신규 Native 없음.
- **Changes:** v160에서 기본 9 테이블은 그대로 두고 선택적 --tables ItemEffect SpellEffect 두 소스 헤더만 관측. 기존 v160 Action의 opt-in live 실행과 14일 단기 artifact를 재사용. 고정 12.1.5.70575는 같은 SimC 핀 빌드이며 최신 게임/시즌 인증이 아님.
- **Verification:** 실측 액션 결과 대기 (NOT_VERIFIED). 기존 focused 139 PASS는 REUSED_HISTORY. 이 probe 최대 실제 Wago HTTP2, Native0.
- **Remaining:** 실제 CSV 컬럼 확인 후 v280/v281 파서 정정, 실제 item→spell→SimC 조인, 최고품질·손/무기 조건 및 F/O SimC rating→v222 B/T→Policy A→제품 E2E.
- **Efficiency:** 기존 v160 32KiB 헤더 기능/작업/증거 방식 재사용, 9종 불필요한 GET 방지, 새 대형 snapshot/Native 호출 없음. main/immutable/Project UI/Work OS 불변.
