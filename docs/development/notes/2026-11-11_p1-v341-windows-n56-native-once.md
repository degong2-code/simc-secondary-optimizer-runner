# v341 — Windows 실 Native N56 단일 사용자 중단·재개 시험

- **Capability:** `PRODUCT.E2E`, `DEV.CONTINUITY`.
- **Keywords:** P1, v341, Windows, N56, Native, one-spec, cancel, restart, continuous, SHA cache, v293.
- **Prior evidence:** [v205 이전 Windows 6 Native](../../../integration_probes/v205_one_windows_user_native_http.py), [v334 실제 Linux N56 12 Native](2026-11-11_p1-v334-primary-n56-native-once.md), [v340 Windows 재시작 UI](2026-11-11_p1-v340-inactive-worker-windows-resume-status.md).
- **Decision:** `CONNECT` — 서로 다른 기존 실증 사이 Windows N56 전주기 확인만 한 전문화·12회로 제한한다. 시즌 환경·탐색 엔진·Native 캐시는 재개발하지 않는다.
- **Changes:** `integration_probes/p1_v341_windows_n56_resume_once.py`와 one-shot workflow. Windows-2022, 고정 SHA 과거 공식 `710c2408bf` SimC, 징벌 성기사 ilvl334 기본 프로필. v113 `/longrun/start` → v293 N56 두 케이스 → 새 HTTP 앱 객체로 입력/진행 읽기 → 실제 취소 → bounded 중단 → continuous 재개 → 최대 12회 DPS·SEM·95% → cache-only SHA 재사용 → 세션 다시 열기. 이는 현 `12.1.5.70783`의 검증으로 승격하지 않는다.
- **Verification:** [1회 Windows Native Actions #43040430950](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43040430950) 최초 확인 당시 진행 중이며, 실제 영수증이 생성되기 전 PASS를 주장하지 않는다. 기존 [공통 offline #43040430827](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43040430827)은 이 노트의 개발 ledger 필수 필드 누락으로 FAIL; 본 문서 교정 뒤 해당 실패와 최종 CI 상태를 구분해 기록한다.
- **Remaining:** 개인 Windows 실제 브라우저의 64회 전체 기본 실행, 현재 `70783` Windows 실 Native, 미래 시즌 최초 READY, 26개 전문화 일반화는 아직 미실증.
- **Efficiency:** 신규 DPS Native 상한 12회, 기존 공식 바이너리와 원본 회계 재사용. 선택 특수장비·G/J/F/O 추가 정적 Native 없음. Native JSON2·SHA 영수증은 기간 제한 artifact 보존. 전 전문화 반복·새 엔진·추가 데이터 수집 금지.
