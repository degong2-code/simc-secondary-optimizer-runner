# P3 v643 — SimC '공식 업데이트 확인' 무반응처럼 보이는 UI 개선

**2026-11-20 KST · 실제 사용자 피드백 · 격리 브랜치만 변경 · 신규 SimC/시즌/Native/DB2 호출 0**

## 실제 첫 사용자 문제

- 설정 → SimulationCraft 연결 및 업데이트 → 설정 · SimulationCraft 관리 → `공식 업데이트 확인` 버튼을 눌러도 사용자 화면에 변화가 없는 것처럼 보인다고 신고.
- `runner/webui/app.js::checkSimcUpdater()`는 버튼 클릭 직후 `POST /api/v1/simc-updates/check`의 완료를 먼저 기다린 후, 그제야 후보나 오류를 패널에 렌더링했다. 공식 HTTPS 인덱스 후 필요하면 GitHub nightly 메타데이터 대체 조회를 수행하기 때문에 네트워크·TLS 상태에 따라 기다림이 발생할 수 있다.
- 요청 자체의 실패는 `withBusy()`가 페이지 최상단 공통 `#notice`에만 기록하여 아래 접힌 SimC 관리자 안에서는 사용자가 놓치기 쉽다. 또한 `withBusy`의 글로벌 busy 상태에서는 업데이트 확인 클릭을 조용히 무시했다.
- **이번 조사로 사용자 PC의 실제 HTTP/서버 오류 원인이 특정된 것은 아니다.** 바로 표시되지 않는 사용자 피드백과 조용한 클릭 무시는 코드로 확인된 UX 결함.

## 최소 수정

- 제품 `runner/webui/app.js`의 기존 클릭 경로만 수정. 클릭 즉시 `simc-check-btn`을 비활성화하고 텍스트를 `공식 업데이트 조회 중…`으로 전환. **같은 SimC 관리 패널 안** `simc-update-candidate`에도 `SimC 공식 배포 목록 확인 중입니다…`을 먼저 표시.
- 조회가 성공하면 기존 공식 Windows x64 후보/리비전·7-Zip 가용성·대체 다운로드 안내를 그대로 표시. 실패 시 같은 위치에 오류 코드와 연결/수동 .7z 설치 안내 표시(기존 전역 `#notice` 오류 병행). 성공·실패 모두 버튼 상태를 복구하고 후보 설치 활성 조건은 보존.
- 다른 글로벌 작업 중 버튼을 누르면 `다른 요청을 처리 중입니다…`을 즉시 표시하되 다른 작업이나 SimC를 취소하지 않음.
- 서버 `v113/v193`의 공식 네트워크 조회·TLS 검증·실제 실행파일/업데이트 권한·시즌 빌드·DPS/SEM/95% 계산·캐시·사용자 세션 변경 없음. 요청 반복/재시도·외부 타이머/백그라운드 네트워크 요청 추가 없음.

## 검증

- 기존 Windows beta workflow에 `tests/test_p3_v643_simc_update_feedback_offline.py`를 포함. **실제 배포 원본 `checkSimcUpdater()` 함수 코드를 Node에서 실행**해 미해결 Promise 동안 버튼/같은 패널의 즉시 진행 표시, 정상 후보 설치 활성, HTTP 오류 후 인라인 실패 안내·버튼 원복, 글로벌 busy에서 클릭 방치 금지 등을 확인.
- [Windows v181 Actions #44653014068](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44653014068): **Windows Python3.12 및 3.14 모두 SUCCESS**, 각각 패키징 **5 PASS** + 기존 웹/세션/보안/업데이트·신규 UI **278 PASS**, 추출 실제 CMD·로컬 HTTP·3 user plans PASS, Native0.
- 현재 [ZIP artifact #14592325421](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44653014068/artifacts/14592325421) 내부 `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip`: **SHA256 `540f88f5a5e56a57babdcd4fbda4d9ed13f8303c6151fc724d97c52c5385822e`**, ZIP **282 소스 파일 + manifest 1**, 각 소스 **282/282 SHA·bytes PASS**, 해당 UI JS 표시 확인. SimC 바이너리·사용자 세션/키 포함 없음.
- 검증은 사용자 가시성·오류 경계·기존 로컬 웹 회귀이며 **사용자 PC의 실제 공식 업데이트 서버 HTTPS 조회 성공, Windows .7z 다운로드·7-Zip·실 SimC CLI 실행을 재현한 것이 아니다.** 서버 오류/TLS/기업망/방화벽 문제가 있으면 패널에 원인·수동 경로를 표시하며 TLS 우회 금지.

## 결론 및 범위

- 사용자 신고와 관련된 **코드로 재현되는 '무반응처럼 보이는 피드백 결함'은 FIX, 실제 원격 조회 성공은 사용자 기기 재확인 PENDING**.
- 이미 받은 옛 ZIP은 자동 업데이트되지 않으므로 새 v643 ZIP을 **새 폴더에 전체 압축 해제**해 BAT로 실행, `Ctrl+F5` 새로고침 후 같은 버튼을 눌러 인라인 상태·오류 텍스트 확인. 기존 `runs`·`web-python` 삭제하지 않음.
- `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10` 유지. main·v003 불변·Project Sources/Work OS 승격 없음. 주 개발 채팅 소유권 유지.
