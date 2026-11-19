# P3 v641 — 최초 사용자 최적화 클릭 시 SimC 설정 사전검사·불필요 시즌 API 차단

**2026-11-20 KST · 격리 브랜치 · 소규모 사용자 첫 실행 흐름 수선 · 신규 Native 0**

## 1. 실제 발견한 사용자 경계와 원인

- 이전 Windows beta의 `runner/webui/app.js`에서 `start-btn` 클릭은 `manualFinalTOrNull()` 후 즉시 `prepareSeasonBeforeOptimizerStart()`를 호출했다. **그 뒤에야** `binary`/`revision` 미입력을 검사했다.
- 환경 미설치 첫 사용자에게 `prepareSeasonBeforeOptimizerStart()`는 `buildSeasonEnvironment(false)`를 호출해 `environment/myth-target` 및 시즌 원본 `environment/season-build` API·필요 시 Native 준비까지 요청할 수 있다. 따라서 실제 SimC 경로 또는 revision 입력이 누락된 사용자도 **불필요한 원본 수집·대기 이후에야 SimC 설정 미완료**를 알 수 있었다.
- 이는 독자 효과 Gate나 SimC 지원 인증 문제가 아닌 **클릭 단계의 검사 순서** 문제이며, 이미 v639에서 PASS한 SimC 스탯/탐색/통계 엔진을 바꿀 이유가 아니다.

## 2. 최소 수정

- 기존 `start-btn` 이벤트 안에서 `manualFinalTOrNull()` 다음에 `binary.checkValidity()`·`revision.checkValidity()` 검사를 배치하고, 미입력/잘못된 형식이면 기존 `settings` 뷰와 `simc-technical-panel`을 열고 해당 입력에 포커스·유효성 메시지를 표시한 후 **시즌/API 전에 종료**하도록 변경. 이후 기존 `prepareSeasonBeforeOptimizerStart()`→명시적 DPS 실행 로직 유지.
- **별도의** `시즌 환경 확인·설치`(`season-build-btn`) 및 환경 원본 수집 기능 자체는 변경하지 않았다. 기존 수동 최종 T의 사전 검증과 user-managed 설치 경로도 그대로.
- 신규 엔드포인트/DB/캐시/SimC 엔진/사용자 데이터 포맷/배포 파일 선정 로직 없음.

## 3. 검증과 증거 경계

- 실제 제품 `start-btn` 핸들러 코드를 Node에서 실행하는 `tests/test_p1_v568_first_user_environment_bridge_offline.py` 회귀를 추가:
  1. SimC `binary` 미입력 → 설정 화면·경로 포커스, 시즌/API 요청 **0**.
  2. revision HTML 검증 실패 → 설정 화면·revision 포커스, 시즌/API **0**.
  3. 유효한 SimC 설정 + 환경 미설치 → 시즌 준비 **1**, DPS 요청 **0**.
  4. 유효한 SimC 설정 + 준비된 시즌 → 기존 세션 시작 API **1**.
- 원래 Windows ZIP 워크플로 `v181_windows_beta_packaging.yml`의 기존 테스트 목록에 위 regression 추가하고 해당 시험 파일을 change trigger에 포함. 원래 패키저 `v181.select()` 한 경로 재사용.
- 최초 [Windows #44637608135](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44637608135) **FAIL · Native 0**: 새 QA 테스트에만 `return {session_id:"mock-only";}` 오타가 있었음. **런타임 원본 JS 오류 아님**. 한 글자 수정해 본래 제품·기존 tests 재실행.
- 최종 [**Windows #44637919613**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44637919613) **Python 3.12/3.14 양쪽 SUCCESS**: 각 **패키지 5 PASS/0 FAIL + 웹/세션/보안/UI 273 PASS/0 FAIL**. 추출 CMD, 127.0.0.1 HTTP, 3개 실제 localhost 사용자 계획 및 보안 상태 PASS, SimC **Native 0**. 위 4가지 실제 JS 클릭 분기를 테스트 안에서 실행.
- 새 실물 Windows beta ZIP [artifact #14583844957](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44637919613/artifacts/14583844957): 내부 `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip` **SHA256 `b31c88bc3c30d80e695c871b61f82185816f28d25c280f246012275831501f8a`**, **282파일·283엔트리·282/282 본문 SHA 검증**. 이전 베타의 사용자 최소 FastAPI/Uvicorn 의존성·SimC별도 설치/키·시즌 검증 안내는 보존.
- 앞선 **v639 원본 이전 ZIP에서 현 시즌 SimC Native64·DPS/SEM/95%/5 근접 대안·저장/재열람 PASS**는 *계산 엔진·세션/캐시·동일 입력 계약이 이번에 변경되지 않았으므로* 재사용한다. 단, **새 ZIP 자체에서 70961 Native64 재실행했다는 뜻 아님**.

## 4. STOP·남은 일반 사용자 조건

- **본 첫-click 사전검사 결함 해결**. API/DB/Native/추가 설치 시험·전 전문화 전수 반복 불필요하므로 같은 범위는 STOP.
- 사용자 PC에 Python3.12+, Windows SimC CLI 또는 공식 관리 설치(7-Zip 필요 가능), 신규 시즌 인증 원본을 위한 Blizzard/WCL 키가 필요할 수 있으며, 외부 인증/유효한 동빌드 source가 없을 때 READY를 거짓 표시하면 안 된다.
- 실제 개인 PC의 winget 첫 설치·기관 PC 제한·26개 전문화 전체·모든 선택 조합·후속 신규 시즌 등은 여전히 미입증. 현재 제품은 **Python 소스 Windows 베타 ZIP**, 독립 EXE가 아님.
- **공식 상태 변경 없음:** `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10`; main, v003 immutable, Project Sources UI, Work OS/Shared State 승격, 주 제품 개발 채팅 소유권 불변.
