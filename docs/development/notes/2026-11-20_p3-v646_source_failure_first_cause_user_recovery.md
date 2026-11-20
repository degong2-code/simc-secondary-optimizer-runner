# P3 v646 — 환경 구축 PENDING 연쇄 목록을 실제 최초 실패 원인·복구 동작으로 안내

**2026-11-20 KST · isolation branch `probe/chat-cache-v035-20261024` · P3 사용자 문제 개선 · 기존 v216/v229/Native/예산 엔진 변경 0**

## 사용자 문제 및 원인

사용자가 `0d19401` 공식 SimC GitHub Nightly를 설치한 상태에서 최신 KR Retail `12.1.5.70961` 환경 구축을 시도하면, 같은 빌드가 아닌 원본은 검증 대상에 쓸 수 없다. 기존 `v229`는 원본 `item_set_bonus.inc`, `gem_data.inc`, `temporary_enchant.inc`의 실측 생성 빌드를 대조하고 `V229_GENERATED_SIMC_COMPILED_BUILD_MISMATCH` 등으로 보류할 수 있다. 당시 `0d19401` 원본 헤더는 `12.1.5.70783`이며 `9933ffb`와 `6924096` 소스 헤더는 `12.1.5.70961`이었다. **이것은 실제 PC 설치 바이트·현재 인게임 빌드의 직접 측정/최신 Windows 실행파일 가용성 증명이 아님.**

`v216.collect_wago_new_season_source`는 이미 `fresh_pinned_first_party_simc_source.status/reason`, `fresh_pinned_simc_commit_resolution.status/reason`, `fresh_pinned_v211_source.status/reason`, 인증 시즌 원본 상태를 포함하여 리턴한다. 그러나 `v274`의 컴파일 입력 누락 목록과 `zero_history_build.requires`가 UI의 1차 메시지를 차지해 사용자에게 `REPRESENTATIVE_TIER_SOURCE_PENDING`, `FRESH_COMPILER_INPUT_*`가 다수 독립 오류처럼 보였고, 올바른 후속 행동을 유도하지 못했다. **문제는 기존 PENDING 무결성 자체가 아니라 원인 해석과 UX 연결.** 일반 제품의 환경 구축 성공을 가정하거나 과거 소스/캐시로 READY를 강제할 수 없다.

## v646 구현

1. `runner/webui/app.js::seasonBuildRecoveryPlan`에서 **이미 응답에 존재하는 상위 status/reason만** 읽어 우선 해결할 이유를 분류. SimC 데이터 빌드가 실제로 다르다는 코드(`V229_GENERATED_SIMC_COMPILED_BUILD_MISMATCH`, `V229_ITEM_DATA_BUILT_FOR_DIFFERENT_GAME_BUILD`)에만 `SimC 원본 데이터와 요청 게임 빌드 불일치`를 표시한다. `V229_SET_BONUS_BUILD_OR_HEADER_MISMATCH`는 빌드가 아니라 헤더 파싱 오류 가능성도 있어 **무조건 불일치로 단정하지 않는다**.
2. 확인 가능한 다른 경우도 구분: Git revision 미입력/공식 원본 조회 불가, Blizzard 공개 KR Retail 버전 조회 실패, Blizzard/WCL 인증정보 미확정, Wago DB2 원본 조회 실패, 검증 설치된 F/J 후보 복수 선택 필요. 상위 실패 증거가 없으면 연쇄 PENDING `8종` 등만 표시되는 상태를 **'최초 원인 미확정/진단 영수증 복사'**로 정직하게 안내한다. 어느 항목도 사용자에게 필수 원본 파일 8개를 각각 입력하라고 요구하지 않는다.
3. `runner/webui/index.html`의 기존 시즌 결과 요약 바로 아래 `#season-build-remedy`와 `#season-build-remedy-action` 추가. 다크/골드 테마의 가벼운 여백·타이포(`styles.css`), 전체폭 추가 장식선 없음. 기능이 바뀌는 실제 동작: SimC 문제 → SimC 연결·업데이트 접기를 열고 `#revision` 포커스, API 인증 문제 → 기존 안전한 credential 입력란, 복수 F/J → 선택 화면, 공식 서버 문제 → 기존 요청 버튼으로 포커스 이동(새 원격 호출 자동 시작 금지), 최초 원인 미확정 → 허용 목록만 복사하는 기존 진단 기능. **원인/대응이 같은 위치**, 클릭 후 기능 연결 보존.
4. `compactSeasonBuildReceipt`에 상위 소스·Git revision resolution·분류 status/reason과 `recovery_kind`를 허용 목록 코드로만 추가. 원본 경로·API 키·임의 예외 문자열 미반출. 기존 source collector/빌드 조회/Native/보안/캐시/실행 계약 변경 0.
5. GitHub 대체 Nightly 링크는 `GitHub Windows nightly 기록(최신/빌드 일치 미검증)`으로 변경하고 배포 날짜를 노출. `0d19401`처럼 최근 배포물이라도 **현재 Retail과 호환된다고 인정하지 않는다**. 공식 HTTPS 직접 후보도 설치 전에 게임 빌드 검증이 필요하다고 명시. TLS 검증 우회·자동 대체·GitHub API 조회 증설 없음.

## 회귀와 영수증

- [Windows v181 beta ZIP+실 localhost #44670032176](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44670032176): Windows 3.12/3.14 모두 **패키징 5 PASS + 웹/세션/보안/기능 287 PASS**, 실제 Windows CMD / loopback HTTP / 3 plans PASS, 신규 SimC Native0, 원격 시즌 원본 수집0.
- 새 `tests/test_p3_v646_season_recovery_navigation_offline.py`은 **제품의 실제 JavaScript 함수**를 Node에서 평가하여 명시적 SimC 생성 빌드 불일치와 단순 GitHub 소스 조회 실패를 다르게 분류하고, 인증/공식 빌드/원본 부족/복수 F/J/복구 버튼/READY 숨김을 시험. 기존 `v114`의 일부 분리 실행 단위테스트는 새 dependency를 fixture로 명시해 유지, 제품에 조용한 런타임 함수 검사를 삽입하지 않음.
- [ZIP 아티팩트 #14599159203](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44670032176/artifacts/14599159203)의 내부 `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip`: 1,500,038 bytes, SHA256 `28ca329a752c200b73ede18dacbcd1e12e1c3d97c4daa08a2037ae2aa9d97a00`. **283 source entries + manifest1**, 283/283 바이트·SHA 매칭 확인, SimC 바이너리·개인 캐시·비밀키 없음.
- 개발 중 실패한 첫 CI #44669394808와 둘째 #44669853071은 **기존 test harness의 새 helper 의존성/Windows stderr 인코딩 및 새 한국어 제목 assertion**으로 실패한 시행착오이며, 최종 #44670032176 PASS로 교정. 기존 회귀를 빼거나 검사 기대치를 완화하여 통과시킨 것이 아니라, 실제 isolated JS harness의 모의 의존성을 추가하고 한국어 제목을 명확화.

## 남은 범위와 STOP

- 아직 사용자 PC의 최신 Nightly 실제 다운로드 또는 SimC 바이너리 내장 빌드 확인 결과는 받지 못했다. v646 분류기는 사용자 PC의 `fresh_pinned_first_party_simc_source.reason`이 실제 해당 코드를 보고할 때만 버전 불일치를 확정한다. 정확한 오류가 없거나 출처가 부족하면 진단을 요구하며 전체 지원 환경을 READY 처리하지 않는다.
- 실제 70961 호환 **Windows 컴파일 바이너리 배포가 공식 경로에 없을 수도 있음**. GitHub에서 최근 아티팩트를 자동 제공한다고 해결된다는 보장은 없으며, 유효한 공식 배포 확인·로컬 경로 확인·실제 빌드 검증 후 기존 환경 구축을 다시 실행한다. 새 Python 효과 엔진/세컨드 원본 콜렉터/전 전문화 Native 재실행 금지.
- 다음 사용자 PC 시험: v646 ZIP 사용 → 해당 SimC 연결 확인·저장 → 시즌 환경 확인·설치 → 첫 원인/대응 메시지와 진단 영수증을 대조. 이후 다른 미확정 원인이 발견되면 **실제 원인에 한정**해 회복 지침 보강.
- 공식 `15/78 COMPLETE`/`full_product_e2e=PENDING`/`next_review=B10` 유지. 격리 브랜치만 변경, main/v003/Project UI/Work OS/M0/주 개발 채팅 권한 불변.
