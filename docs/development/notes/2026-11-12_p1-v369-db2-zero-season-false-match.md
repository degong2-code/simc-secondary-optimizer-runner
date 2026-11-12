# v369 — DB2 시즌 ID 0의 가짜 시즌 일치 차단

- **Capability:** `ENVIRONMENT.SEASON`, `DEV.CONTINUITY`, `PRODUCT.E2E`.
- **Keywords:** v369, source approval, `DisplaySeasonID=0`, v163, Blizzard WCL DB2, fail-closed, exact numeric, Policy A.
- **Prior evidence:** 사용자 2026-11-12 환경 구축 **전역** 원본 출처 원칙(v368). 사용자 업로드 `v163_unapproved_candidates_token_provenance.json` 빌드 12.1.5.70783, DB2 선택 시즌37, WSE 52104/52105 보류; 이 사용자 파일의 시즌0 *선택* 오류 발생 증거는 없음. GitHub v368 HEAD `59ffb5f361812a84ca1a6b935042e8e497296feb`의 v163 실코드 감사.
- **Decision:** 실제 안전성 결함만 CONNECT/FIX. `discover_unique_live_scope`는 `sid>0`을 조건으로 하지만 `build_index`는 WCL 던전명이 일치하는 `MythicPlusSeasonTrackedMap.DisplaySeasonID=0`을 유일한 시즌으로 선택할 수 있었고, `classify_era(0,0,0)`가 `DB2_DISPLAY_SEASON_MATCH`를 반환했다. 이 상태에서는 DB2의 미범위(0) 획득 기록이 잘못 시즌 일치로 분류될 위험.
- **Changes:** `runner/v163_zero_seed_db2_join.py`에서 관련 DB2 시즌 필드를 정확한 0 이상 정수 문자열로 판독하고 유효하지 않으면 차단. 시즌 **선택 후보**는 양수만 허용; 유효한 획득 기록의 명시적 0은 보류 `UNKNOWN_UNSCOPED_JOURNAL`. `classify_era`는 선택 시즌 0/음수 차단. WSE 양수는 그대로 보류. `tests/test_v163_db2_zero_seed.py`에 0/비정상 시즌ID 및 실제 CSV receipt SHA 재생성 음성 사례 추가. 기존 API·SimC·UI·v212·캐시 변경 없음.
- **Verification:** 커밋 직후 기존 `.github/workflows/v163_zero_seed_db2_join.yml`의 offline CI 영수증 확인 필요(작성 시 미실행). 사용자 제공 JSON은 원본 바이트 변경하지 않음. 신규 Native/시즌 API/DB2 수집 **0**. 이 변경은 **가짜 승인 방지**이며 실제 70783 시즌 JOIN 완료·G/J/F/O READY 근거 아님.
- **Remaining:** 시즌 범위 독립 인증과 개별 아이템별 조건 결합은 여전히 PENDING. 다른 A~G `approved/READY` 소비 지점에서 동일한 0/결측→승인 변환이 있는지 국소 추적. 동일 시즌 v217 봉인 및 static cache 재사용, 과거 전체 재검증 금지.
- **Efficiency:** 기존 v163 단일 파서/기존 전용 unittest 보강, 수집·Native0. 불필요한 새 승인 Gate/AI 조회/전문 26개 Native 반복 없음.
