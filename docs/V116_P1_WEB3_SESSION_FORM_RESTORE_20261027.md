# SIMC SECONDARY OPTIMIZER — P1-WEB-3 / v116 로컬 세션 입력 복원

2026-10-27 · 격리 개발 브랜치 `probe/chat-cache-v035-20261024` · **사용자 요청에 따른 구현, 승격 아님**

## 왜 필요한가

회사 PC Chrome 실제 시험에서 징벌 성기사 ilvl334 Native 6/6과 cache-only 6/6이 정상 완료됐다. 그러나 페이지를 새로고침하면 **저장된 결과는 다시 표시되더라도 사용자 입력란의 SimC 실행 경로는 빈 값(예시 placeholder `C:\SimC\simc.exe`)**이 되며, 특성/선택 장비 같은 폼 입력도 기본값으로 돌아간다. 새 시나리오 시작 시 사용자 혼동을 방지하려면 기존 세션의 정식 저장 기록을 단일 원천으로 복원해야 한다.

## 구현

- `runner/v113_local_web_api.py`: 토큰·same-origin·loopback 보호를 기존과 동일하게 적용한 `GET /api/v1/sessions/{id}/inputs` 추가. `V106_SESSION_IDENTITY.json`, `user.json`, `generated/manifest.json`을 **읽기 전용**으로 확인하여 사용자 입력/원래 실행 바이너리 경로/revision/선택 정적 캐시 경로를 반환한다. 세션 identity의 user 일치, revision·manifest 기본 형식 불일치 시 차단한다. Native 실행·세션 파일 생성·재작성·바이너리 전체 해시 재계산이 없다. 실제 Native 실행 직전의 바이너리·캐시 identity 강검증은 기존 v106 경로가 계속 담당한다.
- `runner/webui/app.js`: `restore(id)`의 status/result와 stored inputs GET 확인이 성공해야만 세션을 화면과 브라우저 `localStorage`에 확정한다. 기존 사용자가 입력한 직업/전문화, 종족, 특성, 목표 ilvl 또는 수동 T, 장신구, 기름, 전투조건, 음식/물약/증강/다이아몬드/Omnium, 특수장비 최대8·장식 최대2, binary/revision/static_cache를 폼에 복원한다. 특수장비 추가 행의 표시/숨김 및 전문화 변경 시 입력 초기화도 대응. 특성 코드/파일 경로는 **브라우저 localStorage에 쓰지 않으며, PC 로컬 세션 파일에서만 읽는다.**
- 직전 WEB-3 수정 유지: 다른 PC에서 기억된 세션은 `SESSION_NOT_FOUND`로 명확히 안내하고 무한 GET 1.4초 재요청을 중단, 일시 네트워크 장애는 30초 이내 지수 백오프 적용.
- `tests/test_v114_local_web_ui_offline.py`: 가짜 실행 바이너리 파일 및 임시 v106 세션으로 보호된 GET·입력 원형 복원·파일 불변·manifest revision drift fail-closed를 검사한다. 프런트 엔트리 포인트의 입력 복원 선행/ID 저장 순서, 8행 복원도 정적 검사. **SimC Native 사용 없음.**

## 관측 및 검증 범위

- 실제 사용자 PC 과거 영수증: Native 신규6/6 PASS, cache-only 검증6/6·추가 Native0 PASS. 본 v116 코드 실행에 따른 신규 SimC 실측이라고 주장하지 않는다.
- 신규 `runner/webui/app.js`는 V8 JavaScript **문법 파싱 PASS**. 격리된 모의 DOM/로컬 네트워크를 주입하여 저장된 징벌 입력·binary/revision·session ID 복원 PASS, 존재하지 않는 ID가 자동 확정되지 않음 PASS, 특수장비 8개+기본 2개 표시/초기화 PASS. **실제 Chrome E2E가 아닌 모의 실행**이다.
- 새 Python 테스트 및 GitHub Actions **PASS 영수증 아직 확보되지 않음**. 실제 회사 PC 새로고침·입력란 재복원과 유효 SimC 경로 재검증은 신규 빌드에서 추가 확인 필요.
- 4색 다이아몬드 `240967` Native 실제 효과, 전 전문화 27개 소스 완성, 전체 제품 완성 여부는 **이번 범위 아님**.

## Windows 최소 확인 순서

1. 격리 브랜치 최신 전체 ZIP을 **새 폴더**에 받는다. 기존 `%USERPROFILE%\SIMC_Secondary_Optimizer\runs` 폴더를 옮기거나 삭제하지 않는다.
2. 새 폴더 PowerShell에서 `py -3 -m pip install -r requirements-web-test.txt` 후 `py -3 -m unittest -q tests.test_v101_common_representative_equipment tests.test_v114_local_web_ui_offline` 실행. `OK`인지 확인한다.
3. `py -3 runner/v113_local_web_api.py --port 8765`로 로컬 서버 실행 후 `http://127.0.0.1:8765/` 접속. 완료된 징벌 세션 `abca493c00d6ee2599f1`을 GET만으로 불러온다.
4. F5 전/후 **DPS 179469.7 / SEM 259.37 / CHMV 704·804·787·887**과 원래 사용한 회사 PC `simc.exe` 전체 경로, `7bc1071`, 특성·전투조건 등이 유지되는지 확인한다. `예산/실행/재개/캐시` 버튼을 누를 필요는 없다.
5. 세션 폴더가 없는 다른 PC에서는 ID가 실제 결과로 표시되지 않고 한 번의 `SESSION_NOT_FOUND` 안내 뒤 자동 GET 반복이 멈추는지 확인한다.

## 통제

main 병합 없음. v003 immutable·Project Sources/UI·공식 Work OS/Shared State 미변경. 신규 실행 엔진·SimC 메커니즘·B/O/T·통계·캐시 identity 미변경. 다음은 CI/Windows 실기 확인 및 P1 특수장비/240967 사용자 경로 최소 검증.
