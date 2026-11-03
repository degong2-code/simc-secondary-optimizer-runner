# 2026-11-03 · P3-BT · ilvl별 표준 G/B를 기존 정상 Environment Build에 연결

- **Capability:** `G.NUMERIC`, `BUDGET.GJFO`, `PRODUCT.E2E`
- **Keywords:** G, 표준, 반올림, nearest10, ilvl, Environment Build, v216, v222, v262, G/J/F/O, source reuse
- **Prior evidence:** [P3-BS](2026-11-03_p3-bs-standardized-g-budget.md) 기존 v046→v234 관측 G/표준 G 및 v222 산술, v262 ilvl별 표; [P3-BG](../../P3_BG_20261103_PREPROFILE_GJFO_ACCOUNTING_BRIDGE.md) 정상 v216 `preflight_new_season_source` 이미 `v222.preprofile_budget` 연동; [P3-BQ](2026-11-03_p3-bq-continuity-correction.md) 중복 구현·검증 방지.
- **Decision:** `CONNECT` — 별도 예산 엔진을 만들지 않고 이미 존재하는 `v262`의 **실측 ilvl별 표준 산술**을 `v216` 정상 신규 시즌 preflight에 연결, 목표 ilvl·수동 T도 기존 `v222`에 한 번만 보낸다. 소스 수집과 수치 인증을 혼동하지 않고 실제 부족한 G/J/F/O만 추적한다.
- **Changes:** `v216.preflight_new_season_source`에서 기존 `v262.build`의 실측 ilvl별 B/T 행을 조건부 소비하고 원래 제안 예산과 목표 ilvl 행 일치 확인; 기존 `build_environment`의 신규 시즌 경로에도 선택 인자를 전달. Focused synthetic 회귀 및 INDEX/CURRENT 갱신.
- **Verification:** 새 코드/회귀를 작성하되 **신규 실제 CI 결과는 별도 확인**; 기존 v222·v234 회귀·SimC/G 소스 영수증은 적용 범위 내 역사 증거만 재사용. 이번 신규 Native/게임 HTTP 0회.
- **Remaining:** ilvl별 실제 G 측정/유효 동시즌 기준의 정규 공급, 최고 품질 J/F/O 수치·무기 손 조건 수집, 정책 A 등록/제품 프로필·최적화 E2E. 표준 B 표가 산술상 유효하다는 것과 모든 시즌 소스가 확정된 것은 다름.
- **Efficiency:** 새 DB/Native 실행·중복 G 계산 없음. 추가 구조는 v262 한 번 호출해 기존 v222 산술을 재사용, 유효 레벨만 검사. 시즌/무기 트랙·측정 원본 SHA 구분, 기존 캐시 보존; 추가 시간·I/O는 미측정.
