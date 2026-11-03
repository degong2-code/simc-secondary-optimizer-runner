# 2026-11-03 · P3-CM · 소비품 동일 빌드 실제 Wago 원본 CSV 헤더 검증

- **Capability:** `F.FLASK`, `O.OIL`, `SOURCE.SEAL`, `PRODUCT.E2E`
- **Keywords:** P3-CM, Wago, same-build, ItemEffect, SpellEffect, live CSV, v160, v280, v281
- **Prior evidence:** PROTOCOL→INDEX→P3-CK 126 PASS, P3-CL 139 PASS. v280/v281은 합성 자료로 코드 검증; v160은 원본 CSV의 제한된 헤더 조회와 현행 workflow를 이미 제공함.
- **Decision:** `REUSE` — v160의 기존 소량 실측 기능을 2개 소비품 테이블에만 확장해 실제 컬럼을 선확인. 새 시즌 전체 DB/효과 엔진/별도 인증기나 신규 Native 없음.
- **Changes:** v160에서 기본 9 테이블은 그대로 두고 선택적 --tables ItemEffect SpellEffect 두 소스 헤더만 관측. 기존 v160 Action의 opt-in live 실행과 14일 단기 artifact를 재사용. 고정 12.1.5.70575는 같은 SimC 핀 빌드이며 최신 게임/시즌 인증이 아님.
- **Verification:** [실제 Wago #41657577279](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41657577279) **ItemEffect·SpellEffect 각 HTTP200 / CSV_COLUMNS_CONFIRMED**, 신규 v160 selected offline 6 PASS. 실제 SpellEffect는 `EffectMiscValue_0`/`_1`이며 기존 v281 가정 `EffectMiscValue` 불일치 발견. v281을 `_0`, `DifficultyID`, `EffectIndex`를 사용하는 실제 열로 교정하고 같은 수집 원본 구조 회귀를 추가. 기존 P3-CL 139 PASS는 REUSED_HISTORY. 실 Wago HTTP 2회·SimC Native0. P3-CM 첫 focused #41657577306은 노트 형식으로 ledger FAIL, 노트 교정 뒤 후속 focused 증거 확인 대상.
- **Remaining:** 실제 CSV 컬럼 불일치 교정 후 같은 빌드의 **실물 item→spell→SimC 관계 전체 원본 조인**이 아직 미실행. 최고 품질·무기/손·F/O SimC rating→v222 B/T→Policy A→26 DPS E2E 미완료.
- **Efficiency:** 기존 v160 32KiB 헤더 기능/작업/증거 방식 재사용, 9종 불필요한 GET 방지, 새 대형 snapshot/Native 호출 없음. main/immutable/Project UI/Work OS 불변.
