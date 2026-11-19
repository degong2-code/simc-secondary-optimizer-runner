# P1 v622 — 웹 저장 세션 목록의 v293 장기 결과 누락 교정 (ZERO Native)

2026-11-19 KST · 격리 브랜치 `probe/chat-cache-v035-20261024` · 기존 v621의 실제 70961 Chrome 취소/재개 직후 사용자 결과·재열람 경계에서 첫 소비 결손만 수정.

## 정확한 사용자 장애와 기존 자산

- 일반 웹 `최적 스탯 찾기`는 기존 `v113 → v293/v291` 장기 적응형 세션이다. 최종 보고서는 `generated/v291_longrun_<budget>/simc_results/V291_RESULT.json`, 진행·워커 상태는 v293 파일로 저장된다.
- 그런데 `v113.LocalJobs.recent_sessions`의 저장 목록은 **구형 `V106_USER_RESULT.json` 존재와 `V106_WORKER_STATE.json` 상태만** 읽었다. v570의 실제 64 Native 완료·결과 DOM 성공과 v621의 취소/재개 성공이 있더라도, **최근 세션 목록에 장기 완료를 '결과 저장'으로 표시하지 못하고 시작 전/옛 갱신 시각으로 보일 수 있는 실제 소비 연결 결함**이다.
- 기존 `v293.read_status`는 저장된 v293 설정·원래 manifest SHA, 진척·worker·`result_ready`를 **Native 없이** 읽을 수 있다. 신규 결과 파서/SimC 실행기/캐시/세션 스키마가 필요하지 않다.

## 최소 FIX

1. `runner/v113_local_web_api.py`의 읽기 전용 `recent_sessions`에서 v293 설정이 존재하면 기존 `v293.read_status`로 상태를 구한다. **`BUDGET_EXHAUSTED` + 실제 V291_RESULT 파일 + 완료 후보 수=상한**인 경우에만 목록의 `result_saved=true`. `PAUSED_USER_CANCEL` 및 `BLOCKED_OR_PARTIAL`은 부분 관측 파일이 남아도 완료로 표시하지 않는다. v293 worker 파일 mtime으로 최신 순서도 반영한다. 기존 v106 경로는 그대로 둔다.
2. `runner/webui/app.js` 최근 세션 목록에서 결과 저장/취소/시간 제한/회차 중단/실행 차단을 한국어로 구별한다. 결과 렌더러, 서버 `/longrun/result`, `Start/Cancel/Resume`, 시즌 원본·영구 마부·L/E/O·95%·SimC 통계는 변경하지 않는다.
3. `tests/test_v113_local_web_api_offline.py`의 v622 focused 테스트는 봉인된 합성 v293 세션에 대해 완료64, 취소4, 차단4와 **잔존 V291_RESULT**를 구별하고 API read-only·Native0·수정된 worker 시각을 확인한다. `tests/test_v114_local_web_ui_offline.py`는 저장 목록의 한국어 상태 표기를 점검한다.

## GitHub 코드·실검증·재사용 경계

- 코드: `9d16750435ba41d994583528d075a6c8400541cd`, `38227245f6fd26e6bed371dc25a9e13334bb5688`.
- 회귀: `66832f405676a11fc52e70f6fa808e1f59c2d8dc` 및 `25c353153328792064bef7c77847539d277e27fa`.
- [P1 v388 offline #44451566072](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44451566072) **SUCCESS**, `test_v113_local_web_api_offline` **89/89 PASS**, 신규 v622 상태 판정 테스트 포함. [78 계약 #44451566217](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44451566217) **SUCCESS**; 후속 커밋의 78 계약 [#44451836253](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44451836253) **SUCCESS**.
- 새로운 `test_v114` 표기 테스트는 코드를 추가했지만 같은 최신 HEAD에 대한 별도의 v114 Actions 실행 완료는 **미확인**. 이는 신규 Chrome 검증 PASS가 아님.
- 기존 제품 증거만 재사용: v570 **70961 이전 빌드 70783** 일반 Chrome 완결 DPS64·결과 표시, v619 **70961** 실제 E0 `7957` 선택→대표 ItemID `268222`→DPS Native6·SEM·95%, v621 **70961** Chrome E0 선택→Start/Cancel/HTTP 재시작/Resume·Native 누적4(부분).
- **이번 신규 Native 0, SimC 재컴파일 0, 게임 HTTP/DB2 수집 0, 캐시 무효화 0**. 진행 중인 사용자 세션·결과 파일 변경/이동 없음.

## 여전히 PENDING · STOP

- 이번 v622는 **기존 완료 결과를 최근 세션 목록에서 올바르게 발견·분류하는 결함 수정**이다. v621의 부분 4후보가 64후보 최종 95% 완료 결과가 되었다는 뜻이 아니다.
- **현재 최초 남은 P1 확인**: 동일 **실 70961 가슴 E0 웹 사용자 세션**의 자연스러운 `BUDGET_EXHAUSTED` → 최종 rating/비율/DPS/SEM/95%·대안 DOM → HTTP 재시작 후 저장·재열람의 **단일 실환경 연결 검증**. v570/619/621 및 기존 브라우저/결과 UI 테스트를 더 재사용하고, 끝까지 필요할 때만 bounded 단일 시나리오 최소 Native를 추가한다. 기본 64회를 무조건 재실행하지 않는다.
- E>0 다부위 E와 마부 미승인 19개, DK 룬벼리기·옴니움 장서 등 선택 기능은 별도 우선순위. 효과 엔진·새 solver·시즌 전수수집 금지.
- 공식 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10` 그대로. main·v003 immutable·원본 v016 직접 통합·Project Sources UI·Work OS M0/Shared State·기존 주 제품 개발 채팅 소유권 변경 없음.
