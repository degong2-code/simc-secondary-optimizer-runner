# 2026-11-03 · P3-BQ · 중복 티어 시즌 조사 방지·개발 기록 규약

- **Capability:** `TIER.SEASON`, `GEAR.SEASON`, `G.NUMERIC`, `J.GEM`, `F.FLASK`, `O.OIL`, `BUDGET.GJFO`, `SOURCE.SEAL`, `PRODUCT.E2E`, `DEV.CONTINUITY`
- **Keywords:** tier, 티어, season, 시즌 구분, ItemLevel, 197, 219, 101/118, 13x5, 재검증, 인계, 중복 개발, GJFO
- **Prior evidence:** [P3-AQ](../../P3_AQ_20261102_TIER_TOKEN_BASE_ILVL_SOURCE_PROOF.md) = S1 197×65 / S2 219×65; [P3-AR](../../P3_AR_20261102_RAID_BONUS_TREE_TIER_SEASON_CORROBORATION.md) = 현재 레이드 101/118 시즌2 보너스 그룹 대응; [P3-AT](../../P3_AT_20261102_NORMAL_SIMC_SOURCE_INTEGRATION.md) = 같은 빌드 13직업×5 부위 SimC 정확 일치. [P3-BP](../../P3_BP_20261103_ONCE_ONLY_SOURCE_SEAL_REUSE.md) = v217 원본 SHA 재사용 코드 커밋, CI 미확인.
- **Decision:** `REUSE` — 티어 시즌 구분의 **기존 결합 근거를 우선 재사용**. 기초 ilvl만으로 활성 시즌을 단정하지 않되 이미 확보된 활성 레이드·보너스 그룹·SimC 정확 ID를 무시한 새로운 인증기/원본 조사 재개 금지. 기존 `false/PENDING`은 추가 증거 부재와 제품 미승격을 구별할 것. 실제 없는 조건만 `CONNECT/EXTEND`.
- **Changes:** [PROTOCOL](../PROTOCOL.md), [INDEX](../INDEX.md), [TEMPLATE](../TEMPLATE.md), 개발자 실행 노트/CURRENT/인계 포인터, 경량 구조 검사기와 focused 테스트. 제품의 티어 판정·G·DPS 코드 자체는 이번 작업에서 변경하지 않음.
- **Verification:** 과거 실제 Wago/SimC 영수증과 기존 CI는 위 링크에 한정해 **REUSED_HISTORY**. 이번 작업의 GitHub 문서/검사기 작성은 새 원본 수집·실제 Native/제품 READY가 아님. 신규 검사기 CI PASS는 현재 **NOT_VERIFIED**.
- **Remaining:** 기존 v245/v250/v251 판정과 대표 티어 선택 연결; 일부 선택 장비의 시즌 출처 조건; 실제 G/J/F/O 정적 수치·최고 품질/유효 적용→기존 v222 B/T→Policy A/READY→적응형 DPS E2E. 프로젝트 UI 지침/Sources 실제 적용 미확인.
- **Efficiency:** 기존 문서·동일 빌드 원본·기능·영수증을 **인덱스 경유로 재사용**, 작업당 1개 짧은 노트; 새 원본 HTTP 0회/SimC Native 0회. 기록 검사는 stdlib 파일 검사만, 영구적인 제품 인증 Gate/전수 Native 없음. CI/실행 시간 절감 효과 미측정.
