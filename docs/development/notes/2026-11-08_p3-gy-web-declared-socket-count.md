# 2026-11-08 · P3-GY · 선언 소켓 사용자 웹/API → 원래 v216 연결

- **Capability:** `SOCKET.LAYOUT`, `ENVIRONMENT.WEB`
- **Keywords:** P3-GY, web season-build, source_target_socket_count, N sockets, v113, v216, v271
- **Prior evidence:** P3-GW `e368944b`와 [focused #42386036556](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42386036556) 391 PASS/2 SKIP/Native0; v216에 선언 N(기본5)·v271 고정 N 보석 배치 구현됨. v113 웹에는 N 입력·전달이 없어 5개 기본만 사용. 기존 F #42196731158 및 G/F #42332836316은 해당 원래 프로필 한정.
- **Decision:** `CONNECT` — 현재 v113 season-build API/UI만 확장해 사용자 N을 원래 `v216.source_target_socket_count`로 전송. N은 프로필 의도이지 소켓 아이템/게임 장착 허가 증거가 아님. 별도 소켓 획득 원본·효과 Gate·보석 조합 DPS 탐색은 `STOP`.
- **Changes:** API Pydantic N=5~64 선택 및 특수 ID 필수 사전 검사; 기존 지정 ID가 있으면 기본 N=5도 명시 전달, 사용자가 정한 N은 그대로 전달. HTML 소켓 수 입력·JS 정수 검사/요청·결과에 미검증 선언 수 표시. 기존 설치 재사용 정책·G/J/F/O·gear_*·v222/v212 코드 불변.
- **Verification:** 신규 오프라인 v113 HTTP 테스트(5/7/8/64, 기본5, 범위/특수 ID 차단, Native0) + v114 HTML/JS 정적 계약 추가. **이번 기록 시점 새 CI 영수증 미확인, Native/시즌 HTTP 실행하지 않음.** 이전 P3-GW PASS는 코드/합성 범위로만 재사용.
- **Remaining:** 실 SimC의 선언 `gem_id` 전체 수용/JSON2 확인, 동일 시즌 이중스탯 최고품질 J 원본 수치·현재 item identity G 대응, 실제 v222 G/J/F/O/B/T 및 v212/v217 installed/READY; 26 DPS E2E 별도. P3-GW의 64 최대값은 원래 v271 슬롯당 최대 3의 실제 선택 장비 슬롯 용량에도 종속됨.
- **Efficiency:** v113 thin adapter + 기존 v216/v271 입력 전달만; 신규 수집기/예산기/Native/게임 HTTP/캐시 변경 없음. 논리 작업 하나의 커밋·검증 묶음으로 처리. 격리 외 `main`, immutable v003, Project UI, Work OS, 기존 주 개발 소유권 불변.
