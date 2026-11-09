# P1 · 일반 사용자 최초 시즌 Build의 일반보석 4종 소스 연결 (2026-11-10)

- **Capability:** `BUDGET.GJFO`, `ENVIRONMENT.WEB`, `PRODUCT.E2E`.
- **Prior:** 기존 v216의 `auto_four_stat_source_requested` → `collect_wago_new_season_source(auto_four_stat_gems=True)` → 기존 v221/v266/v230 원본 단계가 이미 구현되어 있음. v113 기본 웹 Build는 특수보석 ItemID가 없는 한 이 소스 플래그를 전달하지 않아 소스가 수집되지 않았음.
- **Decision:** `CONNECT`. v113 일반 시즌 Build가 기존 네 종류 CHMV 일반보석 원본 수집을 항상 요청. 특수보석 ID가 있는 기존 v271 기본 배치 요청은 그대로 유지. 특수보석 자체를 탐색하거나 효과를 해석하지 않음.
- **Safety:** 원본 수집 요청은 J 수치·품질 인증·소켓·물리 배치·사용자 등록을 의미하지 않음. 정확히 같은 시즌 v217 단계 캐시를 재사용. 시즌별 새로운 원본에 오래된 70783 G/J/F/O 값을 복사하지 않음. 신규 Native 0회이며 효과는 SimC가 담당.
- **Code:** `runner/v113_local_web_api.py`, `runner/webui/app.js`; 기존 `tests/test_v113_local_web_api_offline.py`의 기본 Build 계약 검증 추가.
- **Remaining:** 특수보석 ID가 없는 기본 사용자 Build에서 **일반보석 4개 자동 배치와 공식 J 승인**은 아직 미연결. 기본 G/F Native·영약 선정은 사용자 명시 선택 상태로 유지되며 새 시즌 최초 READY 전주기는 **미실증**. 검증 설치 영약/기름 UI·기존 양의 O 실 DPS 영수증은 재사용하고 반복하지 않음.
- **Verification:** 커밋은 GitHub 격리 브랜치에 한정. 실제 CI 결과는 해당 새 HEAD Actions에서 별도 확인하기 전까지 `NOT_RUN`. 기존 522 PASS/2 SKIP는 이전 HEAD의 증거.
- **Performance:** 기존 v217 동일 시즌 소스 영수증을 재사용; 새 Native/효과 Gate/DB 전수 수집 없음. 추가될 수 있는 것은 아직 수집되지 않은 이번 시즌 네 종류의 raw source 한 번이며, 같은 빌드 반복은 seal-cache를 사용.
- **Authority:** main, v003 immutable, 승인 v1.4.3, Project UI, Work OS, 주 제품 개발 채팅 소유권 불변.
