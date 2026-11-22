# 2026-11-22 P3 v667 — 개인 PC 시즌 환경 실패의 안전 진단·검증 설치 F/J 선택·새 ZIP 재시작

## 실제 사용자 상황과 범위
- 사용자 PC에서 이미 자체 빌드 SimC source `6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7`, 게임 데이터 빌드 `12.1.5.70961` 및 앞서 `G=2850/J=92/F=165/O=0/T=3107` 시즌 설치 성공 기록이 있었다. 재시작/재선택 시 `V216_UNQUALIFIED_MULTIPLE_INSTALLED_FJ_VARIANTS_SELECT_EXACT_SHA`가 발생했고 뒤이은 선택 환경 요청에서 `LOCAL_SESSION_PRECHECK_BLOCKED`가 발생했으며 사용자의 화면은 유용한 실패 단계를 표시하지 못했다.
- **이 요청은 실제 PC 오류의 원인을 추측으로 수정하는 작업이 아니다.** 신뢰 가능한 최초 차단 코드·kind와 기존 v212 서명 설치본의 정확한 F/J 선택을 UI에서 확보하고, 같은 시즌 Native 반복 없이 재시도하도록 하는 최소 변경이다.

## 구현
- `runner/v113_local_web_api.py`: 기존 `blocked()`에서 미분류 예외의 내용을 유출하지 않고 code=`LOCAL_SESSION_PRECHECK_BLOCKED`, Python 예외 종류 `kind`와 고정 `stage=SEASON_ENVIRONMENT_BUILD`를 반환하도록 확장. `EnvironmentBlocked` 등 이미 정해진 원본 보호 코드 422는 기존처럼 그대로 보존. 프로필·사용자 경로·키·traceback은 반환하지 않음.
- `runner/webui/app.js`: 안전한 kind/stage/httpStatus를 HTTP 오류에 보존해 기존 시즌 실패 진단 영수증에 포함; 기존 READY 강제/캐시 삭제 없음. 실패 시 '검증 요청 중' 상태와 pending 표시를 종료하고, `진단 영수증 복사`를 활성화. F/J 중복의 경우 별도 선택 안내, 기타 오류는 근거 없는 버전 교체·Native 반복 권유 대신 첫 오류 진단을 안내.
- 기존 `verified_base_flask_installs`는 **동일 시즌/ilvl v212 receipt·v113 저장 프로필·O=0·보통 4보석 조건을 통과한 설치본**만 제공한다. `runner/webui/index.html`에 '검증된 환경 구성' 선택기를 추가하고 F/J/소켓/O=0 라벨만 표시. 정확한 설치 SHA는 선택 옵션의 내부 값으로만 보유하며 사용자에게 수동 입력·복사를 요구하지 않음. 선택한 SHA로 기존 `season-gear` read-only GET과 동일 증거를 재검증하고 예산·장비를 연결. 새 G/F Native 0; 무작위 최신/첫 설치본 선택 금지.
- 같은 영약·같은 J/F·소켓 수이지만 서로 다른 SHA인 설치본은 **같은 표시 의미로 원본 차이를 구별하지 못하므로 선택지 비활성화**, 원본 보완 대기. 다른 수치로 구분 가능한 설치본만 명시 선택 허용. 장비/기름/보석 조건이 조회 중 변경되면 이전 설치 응답 재사용 금지.
- 기존 사용자 설정/세션, Windows credential vault, 실제 SimC 바이너리, v217 봉인 단계·v216 원본 검증, CHMV 회계·O=0 보호, adaptive DPS/SEM/95%·캐시·취소·재개 코드 변경 0. 운영 main·v003 immutable·Project UI·공식 승격/주 개발 채팅 소유권 불변.

## 실제 신규 검증
- [v667 Windows 패키지 #45040741537](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45040741537): Windows2022 Python3.12,3.14 각각 **341 PASS/0 FAIL**, 패키징 각5 PASS, 기존 실제 Windows CMD 시작·로컬 HTTP·3개 세션 계획/재열람 PASS. 신규 Native DPS 0, 새로운 SimC C++ 빌드 0.
- 같은 HEAD `bbfc8ec1ebf3d79fe57dd6f1863a950a5de1db23` 기준 기존 v113 API, 공통 오프라인 focused, 78계약 일관성 등은 PASS. 테스트 시 과거 v114/v646이 오래된 UI 이벤트 표현과 DOM 컨트롤 위치만 고정해 실패하였으나, 실제 실행 보호 조건은 변경 없이 새 컨트롤을 반영해 교정하고 최종 Windows PASS 확인. 과거 실패를 제품 기능 PASS로 과장하지 않음.
- 배포: [Actions artifact #14761926246](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45040741537/artifacts/14761926246)의 wrapper에서 실제 제품 ZIP 하나만 추출. 사용자 전달 `SIMC_SECONDARY_OPTIMIZER_v667_WINDOWS_BETA.zip` **1,526,799 bytes**, SHA-256 **`67da014cdf3e50309699fe31ea483816297a6304c2ee85eb2e4ff5f3dcbde19a`**. ZIP CRC PASS, 매니페스트 286개 파일 SHA-256 PASS, 새 v667 API·UI·HTML 코드 표식 PASS. 내부 `simc.exe` 미포함·기존 managed 설치 재사용.

## 사용자의 '전부 끄고 재시작' 절차
1. 사용자의 실행 중인 로컬 배치 창은 Ctrl+C, 브라우저의 기존 127.0.0.1 탭 종료. 플랫폼이 사용자 Windows 프로세스를 대신 종료했다고 주장하지 않음.
2. 기존 v666 폴더에 덮어쓰거나 사용자별 저장 데이터 삭제하지 않고 새 v667 ZIP을 새로운 경로에 압축 1회 해제한 뒤 `START_HERE_AUTO_SETUP_AND_RUN.bat` 실행. 실행 중 단일 localhost 8765만 사용.
3. 시험 입력은 화염 마법사/목표 ilvl334, 기름 '미사용', 음식/물약/증강 룬 '미사용', 장식/선택 특수효과 장비·추가 마부 선택 없음. 공대 버프는 원한다면 OFF. **기본 검증 영약 F/J 예산과 필수 장신구 2개는 삭제할 선택 효과가 아니라 제품 실행에 필요한 증거/입력**이므로 유지.
4. 시즌 재구축 버튼을 반복하지 말고 현재 빌드의 기존 검증 설치본을 먼저 확인. 중복 F/J면 '검증된 환경 구성'에서 의미상 구분 가능한 설치본만 선택하여 재연결. 동일 숫자로 구분 불가능하면 자동 선택 금지, 진단 영수증 복사.
5. 최초 실패의 새로운 `error_code`, `error_kind`, `failure_stage`, `http_status`가 보이는 복사 영수증만 공유. 비밀키/경로/프로필 본문 수집 금지.

## 아직 확인되지 않음
- 사용자의 PC에서 시즌 오류를 일으킨 **실제 Python 예외 종류**, 동일 F/J 수치의 여러 variant 구별, 최적화 Native DPS 완주·95% 및 26 DPS E2E 검증은 여전히 미확정. 현장 실패가 곧 완치되었다는 근거 없음. 사용자가 새로운 진단을 제공하면 그 **최초 차단 하나**만 검증해 추가 작업.
- 음식·DPS 물약 기본 자동 사용, 영약별 DPS 비교, 미등록 전체 시즌 특수효과 장비 수집, B8 정적 변형 준비, 기름 환경 자동 등록은 별도 기존 P1 과제이며 이번 패키지에서 완료로 주장하지 않음.
