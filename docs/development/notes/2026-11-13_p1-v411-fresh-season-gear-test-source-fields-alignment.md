# v411 — P1 새 시즌 장비 소스 회귀의 정확한 출처 필드 복구

- **Capability:** `GEAR.SEASON`
- **Keywords:** P1, G, fresh season, v165, v166, v167, v216, journal, DisplaySeasonID, synthetic source
- **Prior evidence:** [v410 새 시즌 분류기 수정](2026-11-13_p1-v410-fresh-season-v211-optional-quality-classifier-unbound.md), [v212 오프라인 CI #43387395307](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43387395307)
- **Decision:** `REUSE` 원래 v165 현재 시즌 출처 검증. 합성 원본 fixture가 필수 DisplaySeasonID/저널 관계를 누락한 것을 복원, 실제 제품 검증 기준 완화 없음
- **Changes:** v254/v238 양성 fixture에 실제 필드 `display_season_id`, 양수 `journal_instance_id`/`journal_encounter_id` 및 기존 `season_evidence`를 일치시킴. v216 불충분한 provider synthetic 상태 기대 및 v114 현재 UI 문구 테스트를 갱신
- **Verification:** 새 CI v411 집중 회귀 및 기존 v212/v113 오프라인의 PASS/FAIL을 별도 기록; 신규 Native 0
- **Remaining:** 이 합성 소스 테스트 통과는 전체 시즌 G/J/F/O 실제 구축·사용자 제품 E2E 완료가 아님; 해당 구현을 이어갈 것
- **Efficiency:** 신규 Native 0, DB2/HTTP 0, 실행 제품 코드 0 변경. 캐시·프로필/결과 스냅샷 그대로

기존 테스트에 이름·출처 키만 있어도 현재 시즌 후보가 된다는 과거 가정을 제거하고, 원본 ID 관계가 실제로 존재할 때만 양성 후보로 검증한다.
