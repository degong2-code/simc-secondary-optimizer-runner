# P1 · 최초 시즌 Build 일반보석 4종 원본 연결 (2026-11-10)
- **Capability:** `BUDGET.GJFO`, `ENVIRONMENT.WEB`, `PRODUCT.E2E`.
- **Keywords:** cold-start, four-stat, ordinary gem source, v113, v216, zero-history, source-only, no Native, same-season.
- **Prior evidence:** 기존 `v216`의 `auto_four_stat_source_requested` 및 `collect_wago_new_season_source(auto_four_stat_gems=True)`는 이미 수집 기능을 가진다. `v113` 기본 시즌 Build는 특수보석 선택 없이 네 종류 일반보석 원본 요청을 전달하지 않았다. P3-HAV 인계·기존 UI/원본 수집 영수증을 재사용.
- **Decision:** `CONNECT` — 개발용 신규 데이터 수집기를 만들지 않고, 일반 시즌 Build에서 기존 네 종류 CHMV 일반보석 원본을 요청한다. 특수보석 ID가 명시된 `v271` 배치 경로와 보석 효과의 SimC 소유권을 유지한다.
- **Changes:** `runner/v113_local_web_api.py`의 기본 `fresh_collection_inputs`에 source-only 수집 플래그와 읽기 전용 scope를 추가; `runner/webui/app.js`에 미배치 원본 요청 상태 안내; `tests/test_v113_local_web_api_offline.py`에 기본 호출·scope 회귀 검증 추가; CURRENT/INDEX 기록 갱신.
- **Verification:** 최초 코드 커밋 `f83e71ee`의 focused #42644591883은 테스트 이전 개발 ledger NOTE_NAME/필수 필드 형식 검사에서 FAIL. 본 후속 교정 커밋의 신규 Actions 결과 확인 전 코드 PASS/Native 신규 실행을 주장하지 않는다. 과거 522 PASS+2 SKIP는 이전 HEAD의 증거.
- **Remaining:** 일반보석 4개 물리 배치·정식 J 승인, 특수보석 미선택일 때 완전한 신규 시즌 G/J/F/O READY, 기름·영약 품질 정책 A와 첫 사용자 실 DPS 단일 Build 종단은 미완료. 기본 G/F Native·영약 자동 선정은 여전히 명시 선택이다. `main`·Project UI·승인 규범은 불변.
- **Efficiency:** 기존 v217 원본 스테이지 봉인 캐시 재사용. 처음 수집 시 미확보 same-build 일반보석 원본만 증분 취득; Native/재측정/효과 판정 Gate·과거 시즌 DB 복제 없음. CPU·I/O·캐시/SHA 소유권 변경 없음.
