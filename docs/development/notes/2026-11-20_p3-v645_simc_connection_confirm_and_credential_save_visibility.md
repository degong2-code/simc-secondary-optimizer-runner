# P3 v645 — 사용자 SimC 경로·Git revision 명시 확인/저장 + API 키 저장 상태 가독성

**2026-11-20 KST · 격리 브랜치 · 신규 제품 기능은 명시 버튼·로컬 사용자 설정에 한정**

## 1. 사용자 보고와 버전 의미

사용자는 환경 설정에서 Blizzard/WCL Client ID·Secret 및 SimC 실행파일 경로·Git revision을 입력한 후 실제로 입력이 적용·저장됐는지 확신할 수 없다고 보고하고 **확정/저장 버튼**을 요청했다. 사용자가 SimC를 별도로 업데이트하는 현실과 게임 빌드/SimC Git revision/SimC 내장 생성 데이터 빌드의 차이를 구분할 필요도 확인했다.

- **WoW Retail 게임 빌드**는 게임 클라이언트 데이터 버전 (예: `12.1.5.70961`).
- **SimC Git revision**은 소스 변경 정체성 (예: `9933ffb`), 게임 빌드 번호와 원칙적으로 별개다.
- **SimC가 생성한 데이터의 game-build**는 `gem_data.inc`, `item_data.inc` 등 소스 헤더에서 나온 빌드이며, 현재 타깃 게임 빌드와 같은 데이터 범위인지 v216/v229가 검증한다. 최신 Git revision/가장 최근 Nightly라는 이유만으로 새 게임 빌드가 포함됐다고 추정하지 않는다.
- 이미 성공한 동일 시즌의 G/J/F/O 불변 원본은 SimC revision 변경만으로 폐기하지 않는다. 반대로 생성 데이터가 다른 빌드라면 원본 cross-build 승인 금지.
- 현재 제공된 직접 .7z `0d19401` 원본 `gem_data.inc` 헤더는 `12.1.5.70783`; `7bc1071` 원본 헤더는 `12.1.5.70448`, v639의 `9933ffb` 원본은 `12.1.5.70961`. 이는 **과거 관측 파일의 버전 비교**이지 2026-11-20 현재 업스트림 최신 Nightly 증명이나 사용자 PC의 실제 active WoW 빌드 관측이 아니다.

## 2. 구현 경로와 보안

- **기존 API 인증정보**: `runner/v348_windows_user_source_credentials.py`의 Windows Credential Manager 보관·상태·삭제 경로를 그대로 재사용. 실제 `runner/webui/index.html`에서는 이미 존재하던 `내 API 인증정보 저장` 버튼의 결과 `#source-credentials-status`를 버튼 바로 아래로 이동. `app.js::saveSourceCredentials`는 클릭 즉시 “저장 중…”, 성공 시 “저장됨 · 실제 제공자 인증/시즌 조회는 별도”, 실패 시 해당 패널에 원인 표시하고 기존 입력값을 유지해 재시도 가능. 성공 후만 비밀 입력값 지움. 비밀키를 localStorage, 설정 파일, 응답에 쓰지 않으며 실제 외부 인증을 성공이라고 표시하지 않는다.
- **새 SimC 경로·revision 확인/저장**: `#simc-connection-confirm-btn` 및 근접 `#simc-connection-status`를 기존 `#binary`/`#revision`/`#static_cache` 아래 추가. 기존 업데이트·시즌 빌드·최적화 버튼 ID/이벤트를 변경하지 않음.
- `runner/v645_simc_connection_prefs.py`: 사용자가 명시적으로 **SimC 연결 확인·저장**을 눌렀을 때 입력한 `simc.exe` 정적 경로·파일 유형/존재, revision 문법, 선택 정적 캐시 JSON 경로를 확인하고 SHA를 읽는다. **실제 사용자 로컬 `simc.exe display_build=2`를 timeout20초로 1회 호출**하여 returncode 0, 적절한 출력 및 SimulationCraft 문자열을 확인하고 빌드 문자열이 있으면 관측 game-build로 표시. DPS Native는 **0**. 실패하면 저장 파일 변경 없음. 신규 외부 API/DB2 수집 없음.
- `runner/v113_local_web_api.py`에 인증·Origin·loopback 차단을 재사용하는 GET `/api/v1/simc-connection/status`, POST `/api/v1/simc-connection/confirm` 추가. SimC 세션 작업 실행 중에는 별도 CLI 확인을 차단하고, 읽기 전용 저장 상태 조회는 허용. 잘못된 요청의 로컬 경로는 FastAPI 자동 검증 오류에서 원문을 반사하지 않도록 거부 코드만 반환.
- 저장 파일은 사용자 별도 `%USERPROFILE%\SIMC_Secondary_Optimizer\simc-user-connection.json` (일반적인 `runs` 상위, 실제 root 설정에 따름), SHA·입력 경로·user-declared revision만 들어가고 **Blizzard/WCL 비밀키는 넣지 않는다**. 임시 파일 fsync→원자적 교체, 심볼릭 링크 거부; 사용자가 ZIP을 교체해도 기존 사용자 설정 보존. 브라우저 localStorage에 SimC 경로/신규 비밀을 별도로 저장하지 않는다. 재시작 시 **이전 사용자 저장값을 불러오지만 재검증 완료라고 표시하지 않으며**, 원한다면 버튼으로 다시 기동 확인. 관리 SimC를 업데이트해서 UI에 입력값이 바뀌면 새 값 저장은 명시적 버튼 동작.
- SimC Git revision 확인의 정직성: CLI stdout에서 인쇄된 Git revision이 있을 때에만 실제 입력 prefix 일치 검사를 의미한다. 유저가 직접 내려받은 `.7z`의 파일명·SHA·관리 설치 상태는 자체 정합성이지 **공식 Git 원본의 독립적 진본 인증이 아님**. `revision_identity`에 독립적인 provenance 정도를 나눠 노출. 원본 Game-build/정확 G/J/F/O는 기존 v216/v229가 확정하며 이 설정 저장 기능이 인증 Gate를 대신하지 않는다.

## 3. 시험/비용/배포 바이트

- [v645 Windows ZIP+실 localhost CI #44659497059](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44659497059): Windows Python 3.12·3.14 **모두 SUCCESS**. 각각 **패키징 5 PASS + 웹/세션/보안/신설 SimC confirm 유닛/API 285 PASS**, 압축 해제 Windows CMD/loopback HTTP/3 plans PASS. `tests/test_v645_simc_connection_prefs_offline.py`는 **실제 SimC 프로세스가 아닌 Mock stdout과 TestClient**로 성공·원자적 저장/복원·입력 오류·SHA/managed revision mismatch·API 403/422·DPS 작업 중 409·원문 경로 미반사 검증. 이번 CI에서는 실제 SimC `display_build=2` 프로세스 실행 **0회**, DPS Native0, 시즌 API/DB2 새 수집0.
- [v388 Linux packaging #44659497030](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44659497030) PASS, [v401 completion contract #44659497246](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44659497246) PASS. 기존 v639 SimC Native64·실 시즌 70961 영수증은 계산/환경/세션 코드 변경하지 않은 범위에서 재사용하며 **새 경로 확인 기능의 진짜 Windows Nightly 실행 실측이라고 주장하지 않는다**.
- 새 [Windows ZIP artifact #14595400112](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44659497059/artifacts/14595400112) 내부 `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip`: SHA256 **`cd1e03943e5bc8df91654b94c6844063b26f021a6624a4c86a625ed8237636e6`**, 크기 1497565 bytes. 새 `v645` 사용자 설정 helper가 추가되어 제품 파일 **283개 + manifest 1**, **283/283 SHA·크기 검증 PASS**. 이전 v644 ZIP 282개 파일 수치는 역사적 배포 바이트, 새 버전 개수로 복사하지 않음. Native 바이너리, 개인 credential, 개별 사용자 환경/세션 미포함.

## 4. 실제 사용자 행동·STOP

- 먼저 Windows 사용자가 공식 최신 `simc.exe`를 확보한다(자동 Nightly HTTPS 인증서 오류 시 공식 GitHub/수동 .7z 대안). 기존 7-Zip 필요/출처 미인증 경계 유지.
- 환경 설정에서 실행파일 경로·revision 입력 후 **SimC 연결 확인·저장**을 누른다. 성공 시 CLI 기동/관측 빌드/입력 revision 신뢰 수준/로컬 저장 상태를 바로 확인한다. 저장된 경로는 ZIP 교체에도 유지. SimC 설치 성공만으로 현재 KR Retail의 생성 소스와 G/J/F/O를 허위 READY 처리하지 않는다.
- API 키는 이미 있던 버튼으로 저장하되 Windows 저장소 기록과 실제 Blizzard/WCL 네트워크 인증을 구분. 시즌 구축 후 아직 PENDING이면 첫 원본 실패/게임 빌드/revision과 `진단 영수증 복사`의 안전 필드를 대조한다.
- 정상 설치 시 실 SimC 바이너리 CLI가 예상 출력/시간 한도를 충족하는지 사용자 PC에서 최초 확인 필요; 전 26전문화 Native 반복/새 엔진/별도 시즌 데이터 DB 확대 불필요.
- 공식 `15/78 COMPLETE`/`full_product_e2e=PENDING`/`next_review=B10`, 격리 브랜치/main·v003·Project UI/Work OS·주 제품 개발 채팅 소유권 불변.
