# v339 — P1 장기 재개 중 이전 관측 결과의 현재 결과 오인 방지
- **Capability:** `PRODUCT.E2E`, `DEV.CONTINUITY`.
- **Keywords:** Windows, v113, v293, v291, active, resume, saved result, display, Chrome.
- **Prior evidence:** [v334 실 N56 DPS Native12](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42983978567), [v333 Chrome 실클릭](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42983424219), [v338 CI](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43019927299).
- **Decision:** `CONNECT` — v293 `result_ready`는 구간 결과 파일 존재를 나타낼 수 있고, active 재개 중에도 true일 수 있다. 새 SimC 측정이 끝나기 전 구간 결과를 갱신된 최종 DPS처럼 보이지 않는다.
- **Changes:** `runner/webui/app.js`는 `active || !result_ready` 시 결과 영역을 숨긴다. 기존 `V291_RESULT.json`, v293 봉인, 95% 결과·캐시·정적 예산은 불변. `test_v114_local_web_ui_offline.py` 및 `p1_v333_user_browser_click_smoke.py`에 비실행/가상 active 뷰 검증 추가.
- **Verification:** 코드 및 회귀 시나리오 추가. 실제 GitHub Actions 결과 확인 전 `OFFLINE_PASS`/`USER_WEB_E2E_PASS` 주장 금지. 새 DPS/환경 Native 0회 예정.
- **Remaining:** 개인 Windows에 설치된 실제 SimC의 64상한 사용자 실행→취소·재개→결과 재열기 전체 E2E는 미실증. 브라우저 가상 상태 회귀를 실제 DPS 시험으로 간주하지 않는다.
- **Efficiency:** UI 표시 로직 1조건 변경; 추가 Native/API/캐시 write 없음. 기존 v216/v212/v290/v293 및 모든 유효 Native·CI 증거 재사용.
