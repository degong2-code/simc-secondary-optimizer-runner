# v340 — P1 Windows 서버 재시작 뒤 중단된 장기 세션 표시·안전 재개
- **Capability:** `PRODUCT.E2E`, `DEV.CONTINUITY`.
- **Keywords:** v293, v113, Windows, restart, stale worker, RUNNING, QUEUED, resume, 95%.
- **Prior evidence:** [v339 UI PASS](2026-11-11_p1-v339-resume-active-result-display-guard.md), [v205 Windows 6 Native](../../../integration_probes/v205_one_windows_user_native_http.py), [v334 N56 12 Native](2026-11-11_p1-v334-primary-n56-native-once.md).
- **Decision:** `CONNECT` — 장기 세션 봉인 상태 `RUNNING/QUEUED`만으로 작업자가 현재 살아있다고 판단하지 않는다. v113 OS activity가 false인데 v293 저장 상태가 이전 RUNNING인 경우 일반 ‘대기’ 대신 재개 가능한 실행 중단을 표시한다.
- **Changes:** v113/v293/v291·Native/캐시 동작은 불변. v113 API 기존 세션 재열기/상태·95% 합성 결과 읽기/재개 회귀를 Windows 포함 테스트에 추가. Chrome에서 orphan state UI를 실제 렌더링 검사. UI 표시 2개 분기만 추가.
- **Verification:** 새 실증은 Actions 영수증 확인 후 별도 기록. Windows·Linux 오프라인 및 Chrome 검사 목표; 새 SimC Native 호출 없음. 기존 v205/v334 증거를 신규 현재 Windows Native로 재해석하지 않는다.
- **Remaining:** 개인 Windows 실제 설치 SimC를 이용한 N56/64회 시작→취소→재개→95% 결과 재열기 통합 Native는 미실증. 미래 시즌 READY도 별개.
- **Efficiency:** 정확 재사용 세션의 네트워크·Native·프로필 생성0, GET 상태·결과 읽기 only. 새 알고리즘·원본·GJFO 변경 없음.
