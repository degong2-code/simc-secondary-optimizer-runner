# v342 — Windows Chrome 기본 64회 사용자 흐름 및 공식 SimC 소스 확인

- **Capability:** `PRODUCT.E2E`, `DEV.CONTINUITY`.
- **Keywords:** v342, P1, Windows, Chrome, 64-case, N56, cancel, resume, result, restore, official SimC, source-identity, zero Native.
- **Prior evidence:** [v341 Windows 실제 N56·12 DPS Native](2026-11-11_p1-v341-windows-n56-native-once.md), [v340 재시작 상태](2026-11-11_p1-v340-inactive-worker-windows-resume-status.md), [v333 실제 Chrome 클릭](../../../integration_probes/p1_v333_user_browser_click_smoke.py).
- **Decision:** `CONNECT` — v341의 Windows Native/worker/캐시 실증을 재사용하고, 무조건 64회 Native를 반복하기 전 실제 브라우저의 기본64 신청·취소·재개·결과·재열기 UI 계약만 적은 비용으로 검증한다. 실행 시 synthetic HTTP worker를 실제 Native처럼 표시하지 않는다. 공식 Windows SimC 배포를 2026-11-11 GitHub run 42956947906 / artifact 13827649795로 고정해 소스 SHA/버전만 점검한다.
- **Changes:** `runner/webui/app.js`에서 실제 `PAUSED_USER_CANCEL` 상태를 취소·재개 가능으로 표시하고, `BUDGET_EXHAUSTED` 후 재개 버튼이 같은 세션을 쓸데없이 재실행하지 못하도록 처리. `integration_probes/p1_v342_windows_browser64_clicks.py`는 진짜 Chrome/loopback v113이 제공한 페이지·입력·클릭 및 합성 session API만으로 64 상한/95%·SEM·근접 대안 표시 계약을 검증. `p1_v342_official_windows_source_probe.py`는 공식 바이너리 원본 SHA/배너만 수집하며 프로필/SimC DPS를 실행하지 않는다.
- **Verification:** [첫 One-shot #43045405452](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43045405452)는 검사 코드 결함으로 FAIL했다. 실제 Chrome Windows/Linux는 시작→취소→재개→모의 64회 결과까지 성공했지만, 접힌 세션 복원 영역을 열지 않고 버튼을 눌러 실패했다. Windows SimC 공식 배포 검사에서는 publisher 저장소 HEAD와 SimC 엔진의 파일명 revision을 동일시한 가정을 제거했다. 수정 재시험 영수증 전 PASS 주장 금지. 브라우저 모의 64회는 실제 Native 64회가 아니다. CLI 배너에 70783이 보여도 시즌 환경 G/J/F/O/대표 프로필 정합의 독립 증거는 필요하다.
- **Remaining:** 개인 PC에서의 실제 Windows/브라우저/SimC 64회 연속 Native, 현 70783 시즌별 정확 설치·DPS 일치 확인, 차기 시즌 최초 READY 및 26 DPS 일반화는 별도 검증 범위.
- **Efficiency:** 신규 DPS Native 0회, SimC 빌드 0회, 새 시즌 원본 수집 0회. 공식 배포 ZIP 1회 재사용하며 사용자 장비/캐시·예산·N56 정책 불변. 모든 테스트 합성/실제 증거 분리.
