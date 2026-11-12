# v349 — 실사용 시즌 환경 UX 피드백: 진행 중 상태·소켓 총량·ID 입력 분리

- **Capability:** `ENVIRONMENT.WEB`, `PRODUCT.E2E`, `DEV.CONTINUITY`.
- **Keywords:** v349, real-user screenshot, progress, pending diagnosis, full socket count, special gem, advanced ItemID, Wago DB2, user feedback.
- **Prior evidence:** 사용자의 2026-11-12 Windows 실제 베타 스크린샷에서 `12.1.5.70783` Wago `EXECUTED_AND_SEALED`, 원본 컴파일 PENDING, 미해결 27건 확인. v348 Windows API 저장·실 HTTP 시험 완료, 유효 사용자키 70783 READY 실증 없음. 기존 `v216` 보석 기본 4종+특수 1개의 소켓 총량 제한과 `v113` 사용자 UI 확인.
- **Decision:** `CONNECT` — 원본 환경 자동 검증과 캐릭터별 품목 선택을 명확히 분리한다. 일반 사용자에게 특수보석·영약·기름 ItemID 조사를 요구하지 않고, 정확한 수동 ItemID를 기존 내부 재현용 고급 경로로만 보존한다. 소켓 입력은 특별 보석을 **포함한 전체 소켓 수**, 바꾸면 해당 J와 SimC 프로필에 대해 재검증 필요. 현재 `4` 일반보석 기본과 고급의 특수보석 지정·총 5 이상 기존 원칙은 변경하지 않는다.
- **Changes:** 브라우저에 정직한 indeterminate 진행 표시·경과 초·최종 요약 추가. HTTP 요청 완료 전 가짜 퍼센트나 원본 단계 완료를 주장하지 않는다. `season_join`과 Blizzard/WCL 인증 상태 및 Wago 수집 결과를 구분하여 첫 미완료의 후속 파급을 설명한다. 소켓 계산 breakdown을 즉시 갱신한다. 수동 품목 ItemID 부분을 접힌 개발/문제해결용 고급 화면에 배치. 기존 v216 원본 파이프라인·인증·기존 서버 입력·Native/캐시·J/F/O 정책 변경 없음.
- **Verification:** Windows/Ubuntu 프런트와 HTML/JS 오프라인 단위검사 실행 전 PENDING. 실사용 사용자 키로 READY 실증과 브라우저 장시간 진행 표시 실사용 시험은 별개.
- **Remaining:** 활성 원본 수집 내부 단계의 실시간 세부 퍼센트/중단·재개는 이번 수정 범위에 없음. `미해결 27건`은 최종 컴파일 의존성 수이며 27개 독립 오류나 진행 상태가 아님. 시즌 소스 자동 등록이 미완료인 범위는 별도 P1 통합이 필요하며, 고급 ID 입력이 그 대신이 되어서는 안 된다.
- **Efficiency:** 신규 Native0/네트워크0; 단순 브라우저 타이머는 현재 실행 동안만, 응답·오류 시 해제. 환경 요청 중에는 추가 백엔드 폴링·중복 수집을 만들지 않으며 기존 Wago/SimC 원본·DPS 캐시를 변경하지 않는다.
