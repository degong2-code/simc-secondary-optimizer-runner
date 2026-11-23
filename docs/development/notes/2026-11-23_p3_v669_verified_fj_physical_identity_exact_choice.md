# P3 v669 — 같은 F/J 수치의 검증 설치본: 실제 영약·보석 물리 ID 구별과 정확 SHA 재연결

2026-11-23 KST · 격리 브랜치 `probe/chat-cache-v035-20261024`
제품 코드/테스트 HEAD: `9ee7404baaf65b778851f62237b53e21b6ea1688`

## 첫 사용자 PC 장애와 미확정 원인

- 사용자 PC의 관리형 SimC 실 CLI 빌드 `12.1.5.70961` 연결 성공. 앞선 `12.1.5.70575` 수동 파일과 별개이며, **현재 KR Live BuildId 일치가 이 사실만으로 확인되는 것은 아님**.
- 시즌 환경 기본 ilvl334 기름 미사용에서 `V216_UNQUALIFIED_MULTIPLE_INSTALLED_FJ_VARIANTS_SELECT_EXACT_SHA` HTTP422. 기존 인증된 F/J 설치본이 여러 개라 임의의 SHA를 재사용하지 않는 안전 차단; Native DPS·새 시즌 READY 아님.
- 사용자 입력 화면에서 `flask of thalassian resistance 2 · 품질2 · F165`로 하나의 영약이 보이지만, 검증된 설치본이 여러 개이며 F/J·소켓 숫자만으로 구별되지 않는다는 안내. 이는 실제 영약/보석 물리 ID의 차이가 있는지 확정한 것이 아님.
- v667 화면은 `flask_item_id/F/J/socket_total` 동률이면 설치 SHA가 다르다는 이유만으로 모든 선택을 disabled 처리. 저장된 v113 프로필의 `source_compilation.physical_gem_layout_unadmitted.ordinary_gem_ids`와 v212의 `official_F_physical_source.crafting_quality`를 활용하면 실제 원본 조건의 차이 여부를 한 번 더 비교할 수 있음.

## 최소 구현 — 기존 소스·캐시/보호 유지

- `runner/v113_local_web_api.py::LocalJobs.installed_oil_loadouts`: 기존 v212 manifest hash/빌드/ilvl, exact installed SHA, 로컬 v113 snapshot/4보석 호환성 검사를 통과한 O=0 영약 설치본에만 `flask_quality`와 저장된 `ordinary_gem_item_ids` 4개를 **표시 목적**으로 포함. 값이 비정상·미관측이면 사용자 후보에 등록하지 않음. 별도 G/J/F/O 승인이나 새 Native 실행은 없음.
- `runner/webui/app.js::renderInstalledFlaskChoices`: 같은 numeric F/J/socket 후보를 받은 경우에만 검증 프로필의 **영약 물리 ItemID/품질과 4개 보석 ItemID(정렬된 집합)**를 사용자 텍스트에 표시. 물리 입력 키가 서로 다른 설치본만 기존 정확 `installed_manifest_sha256` 내부 값으로 개별 선택 가능. 같은 물리 키가 복수면 **여전히 둘 다 disabled**; raw SHA 순서·최신 수정시각·수치 동률을 사용자 선택 근거로 사용하지 않음.
- 기존 `chooseInstalledFlask`는 여전히 일치하는 installed SHA로 `/api/v1/season-gear` read-only GET을 수행하고, 최종 세션 계획은 기존 v113/v217/v212 봉인 검증을 다시 사용. 조합 변경/기름 ON/소켓·빌드 불일치 등은 기존 fail-closed.
- v653 기본 UI 디자인·O=0/양수 O·고정 L/E 회계·95% adaptive/native·DPS 캐시/세션/취소·재개, SimC 업데이트 관리자는 수정하지 않음. 신규 원본/DB2/HTTP 실수집/SimC C++ 컴파일·DPS Native0, 기존 캐시 삭제0.

## 새로운 검증 및 이전 실패의 분리

- 신규 `tests/test_v669_verified_fj_physical_identity_offline.py`: 기존 로컬 v212/v113 파일 형태의 합성 fixture로 같은 F/J이지만 다른 4보석 ItemID의 백엔드 반환 확인, 실제 JS 함수에서 다른 물리 구성을 별도 선택 가능/같은 구성은 차단/누락·빌드 불일치 차단/원문 SHA 비노출 확인. 외부 HTTP·Native·DB2 없음.
- v490의 기존 API fixture는 추가된 물리 source 필드 2개 때문에 초기 #45100214854/#45100214733/#45100214856에서 **각각 1개 정확 응답 필드 테스트 실패**. `tests/test_v113_local_web_api_offline.py` 기존 fixture 기대값을 실제 새 응답으로 정정. 제품 예산·보호 경로는 그대로이며 과거 FAIL을 숨기지 않음.
- 변경 HEAD `9ee7404baaf65b778851f62237b53e21b6ea1688`에 v669 신규 테스트를 기존 v113 API와 v181 Windows packaging 회귀 목록에 등록.
- [v113 API #45100485610](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45100485610) Ubuntu/Windows SUCCESS, Ubuntu 505 tests OK(skip1); [Windows ZIP #45100485693](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45100485693) Python3.12·3.14 각각 **346 tests PASS/0 FAIL**, package 5 PASS, Windows CMD/localhost/3 기존 plans PASS. [v182 UI #45100485591](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45100485591), [v177 #45100485614](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45100485614), [v180 offline #45100485586](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45100485586), [focused #45100485568](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45100485568), [78 정합 #45100485575](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45100485575): SUCCESS. 실제 six-case Native는 SKIPPED, 새 DPS Native0.
- 새 패키지 [Actions artifact #14784882547](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45100485693/artifacts/14784882547)는 wrapper이며, 내부 단일 제품 ZIP `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip` **1,530,189 bytes**, SHA256 `096847115af9e4afe4633f47a46c513272bd14359e65896951565a5dc46c7fda`, 286개 source SHA/size 매니페스트 일치·ZIP CRC PASS, 포함 simc.exe/개인 세션 0. 단일 제품 ZIP을 사용자 전달 시 별도 이름 `SIMC_SECONDARY_OPTIMIZER_v669_WINDOWS_BETA.zip`으로 저장해도 바이트 SHA는 동일함.

## 검증 경계/다음 최소 행동

- **사용자 개인 PC의 실제 v669 F/J 변형 목록/실제 구별 가능 여부, 현재 KR Live 일치, 시즌 READY→장신구2→SimC DPS/SEM/95% 전 과정은 아직 미검증**. 동일 숫자 F/J라도 실제 4보석 ItemID까지 같다면 이 수정은 안전 차단을 해제하지 않음. 실제 로컬 설치 SHA나 원본 효과를 추측해 선택하지 말고 첫 증거를 다시 확보.
- 사용자 다음 1회 시험: 기존 v668 CMD 종료/localhost 탭 정리 → v669 ZIP 새 폴더에 1회 압축 해제→ 기존 검증 관리형 70961 SimC 재사용 → 70961을 현재 KR Live로 자동 인정하지 않음 → 기름 OFF/4보석/ilvl334/특수장비·장식 없음 → 검증된 환경 구성 선택지에 보석 ItemID가 달라 보이는지 확인. 같아서 disabled면 여기서 STOP/원본 차이 추가 분석. 다를 때만 해당 정확 SHA 로컬 read-only 재연결; 서버가 READY 및 현재 시즌 일치를 재인증하지 않은 상태에서 DPS 실행 금지.
- NEXT: 동일 물리 ID 중복이면 기존 설치 receipts의 원본 근거를 최소 범위에서 비교해 다른 의미 있는 차이만 표시; 절대 무작위 SHA 선택·새 Native 전수·기존 캐시 삭제하지 않음. 공식 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10` 유지; main·v003 immutable·원본 v016·Project UI·Work OS·Shared State·주 제품 채팅 소유권 변경 없음.
