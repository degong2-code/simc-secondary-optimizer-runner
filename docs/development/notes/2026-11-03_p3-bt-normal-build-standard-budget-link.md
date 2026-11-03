# 2026-11-03 · P3-BT · ilvl별 표준 G/B를 기존 정상 Environment Build에 연결

- **Capability:** `G.NUMERIC`, `BUDGET.GJFO`, `PRODUCT.E2E`
- **Keywords:** G, 표준, 반올림, nearest10, ilvl, Environment Build, v216, v222, v262, G/J/F/O, source reuse
- **Prior evidence:** [P3-BS](2026-11-03_p3-bs-standardized-g-budget.md) 기존 v046→v234 관측 G/표준 G 및 v222 산술, v262 ilvl별 표; [P3-BG](../../P3_BG_20261103_PREPROFILE_GJFO_ACCOUNTING_BRIDGE.md) 정상 v216 `preflight_new_season_source` 이미 `v222.preprofile_budget` 연동; [P3-BQ](2026-11-03_p3-bq-continuity-correction.md) 중복 구현·검증 방지.
- **Decision:** `CONNECT` — 별도 예산 엔진을 만들지 않고 이미 존재하는 `v262`의 **실측 ilvl별 표준 산술**을 `v216` 정상 신규 시즌 preflight에 연결, 목표 ilvl·수동 T도 기존 `v222`에 한 번만 보낸다. 소스 수집과 수치 인증을 혼동하지 않고 실제 부족한 G/J/F/O만 추적한다.
- **Changes:** 정상 `v216.preflight_new_season_source`가 기존 `v262.build→v222.preprofile_budget`의 실제 제공 ilvl별 G/B/T 행을 소비하고 목표 ilvl·수동 T 일치 확인. 더 나아가 기존 `v234.execute`에서 이미 생성한 **한 번 실행된 Native G receipt**(outer PASS/inner source identity·SHA·원 G·표준 G)를 **재실행 없이 선택 입력 경로로 재사용**, 누락 J/F/O 시 G 값만 미승인 표시; 공급된 GJFO 행의 G 원본 SHA·반올림 수치가 Native receipt와 달라지면 거부. `build_environment`의 원래 신규 시즌 preflight에 선택 인자 전달. `test_v264` synthetic 회귀, INDEX/CURRENT 갱신. 신규 수집기·예산 엔진·독립 시즌 인증기 없음.
- **Verification:** v216 정상 preflight 멀티 ilvl/수동 T, 구형 경로 보존, v234 Native receipt 1회 재사용과 잘못된 SHA·source G 충돌·미확정 JFO 시 G-only pending을 다루는 synthetic 테스트 코드 작성. 변경 후 **새 CI PASS/FAIL 미확인**(`NOT_VERIFIED`), 실행 Native/외부 HTTP 0회. 역사 v222/v234 계약과 이미 확보한 소스 영수증은 해당 범위만 `REUSED_HISTORY`.
- **Remaining:** 실제 새 시즌의 ilvl별 G Native 영수증 또는 유효 동시즌 참조는 아직 확보하지 않음. 기존 v232에서 **선정된 일반 장비 중 어떤 부위가 출처 보류인지**는 해당 source receipt의 `pending_non_tier_season_source_slots`를 활용하며 다시 전체 장비/티어 인증 조사를 시작하지 않는다. 최고 품질 J/F/O 실제 금액·적용 조건의 원본 공급, 제품 정책 A 등록·v098/최적화 E2E 및 CI 실행 증거는 미완료. `v216` 표준 예산 행은 계산 미리보기이지 시즌 환경 설치/READY가 아니다.
- **Efficiency:** 새 DB/Native 실행·중복 G 계산 없음. 추가 구조는 v262 한 번 호출해 기존 v222 산술을 재사용, 유효 레벨만 검사. 시즌/무기 트랙·측정 원본 SHA 구분, 기존 캐시 보존; 추가 시간·I/O는 미측정.
