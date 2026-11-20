# P3 v644 — Windows 환경 설정 UI 정리 + 7-Zip 미검출 안내 + 시즌 원본 연쇄 진단

**2026-11-20 KST · 격리 브랜치 · P3 디자인 Phase B · 제품 계산 엔진/원본 수집/캐시 미변경**

## 1. 실제 사용자 보고

1. 로컬 SimC `.7z` 파일이 존재하는데 `내 PC의 .7z 파일 설치` 요청이 `SEVEN_ZIP_REQUIRED`로 종료됨. 원본 `v193_simc_local_updater.py::find_sevenzip`는 운영체제에서 `7z.exe`를 PATH나 `%ProgramFiles%\7-Zip` 등의 표준 위치에서 탐색한다. **아카이브 존재는 해제 도구 존재를 의미하지 않는다.** 사용자 PC의 실제 7-Zip 설치 여부·경로는 별도 확인 전 미확정. 확인된 문제는 메시지 위치/뜻이 불명확한 UI 경험이며, 보안 무력화나 새로운 압축 엔진 도입 이유가 아니다.
2. 환경 구축 후 `REPRESENTATIVE_TIER_SOURCE_PENDING`, `G_NATIVE_RATING_OBSERVATION_PENDING`, `HIGHEST_QUALITY_GEM_J_SOURCE_PENDING`, `HIGHEST_QUALITY_FLASK_F_SOURCE_PENDING`, `WEAPON_OIL_O_EXACT_APPLICATION_AND_RATING_PENDING`, `FRESH_COMPILER_INPUT_*`와 `SOURCE_COMPILER:*`, `J/F 원본·품질`이 동시에 보고됨. 실제 `v216::_zero_history_source_progress` 및 `v274::discover`에서 **시즌 컴파일 원본 입력의 누락 → G Native/소모품 원본/설치 보류라는 연쇄적 PENDING**을 반환하는 경로를 확인. 사용자 보고에 `GEAR_V167` 누락은 없지만 TIER_V168/V189/V190/GENERATED_PERMANENT/GENERATED_TEMPORARY/GENERATED_GEM/SIMC_V211_SIX_SOURCE_FILES_AND_MANIFEST/PINNED_SIMC_REVISION의 **8개 컴파일러 입력은 누락**. `v229`는 7~12자리 revision 힌트를 40자리 Git commit으로 확인할 수 있으나, 사용자 PC의 소스 수집·GitHub API·버전 정확성·인증 키·빌드 일치가 **어느 단계에서** 실패했는지는 현재 게시된 코드 목록만으로 단정할 수 없다. `full_product_e2e=PENDING`이며 G/J/F/O 예산·환경 설치를 임의로 READY 선언하면 안 됨.

## 2. 구현

- **설정 페이지 편집 규칙** [확정 디자인 계약](../2026-11-20_p3_settings_results_ui_design_contract.md) Phase B만 실제 적용. `runner/webui/styles.css`에서 기존 v363 설정/결과 결합 selector를 분리해 **설정 전용** 패널·section-head·fold/summary·필드·버튼의 연속 full-width `border-bottom`을 제거/완화. 데스크톱 최대 ~1140px·충분한 그룹 간 여백·12px 내외 라벨·흐리지 않은 필드 배경/포커스·길게 늘어나지 않는 액션 버튼·모바일 단일 열 및 버튼 줄바꿈 적용. 기존 다크/금색 대비, section text, help hover/focus는 보존. **결과 확인 화면 스타일과 최적화 화면 CSS는 현 단계 미변경.** 무의미한 CSS 파일 끝의 새 !important 누적 대신 기존 규칙 분리·수정으로 적용.
- `runner/webui/index.html`의 SimC 후보 조회 상태 `#simc-update-candidate`를 **업데이트 버튼 바로 아래**로 이동; ID/역할·기존 바인딩 유지. 새로운 `#simc-local-install-status`(role=status/aria-live=polite)를 수동 설치 버튼 바로 아래 추가. 검증된 공식 [7-Zip 다운로드](https://www.7-zip.org/download.html) 링크 추가. `#season-build-pending`의 설명을 내부 연쇄 진단임을 분명히 하는 텍스트로 변경.
- `runner/webui/app.js`에서 현지 `displaySimcUpdater` 결과의 extractor 가용성을 같은 관리 패널에 명시. `installLocalSimcUpdater()`는 클릭 즉시 진행 상태, 성공 후 버전 반영, `SEVEN_ZIP_REQUIRED`일 때 **.7z 경로와 별개로 설치 가능한 `7z.exe`를 찾아야 한다**는 안내와 공식 링크를 같은 위치에 표시. 기존 서버 422/보안 차단/설치 기능 및 7-Zip 요구사항 불변.
- `diagnoseSeasonBuildEvidence`는 SOURCE_COMPILER 첫 원인을 한국어(티어·소모품·효과·마부·보석·정확한 SimC revision)로 설명하고 입력 누락 **8종**처럼 의존성을 집약해 노출. 기존 상세 내부 코드 목록은 접기 고급 진단에 보존; `showSeasonEnvironmentBuild`는 '연쇄 미완료이며 사용자 개별 항목 입력이 아님'을 밝혀 무의미한 우회/재실행을 막음. **원본 수집·기능/소스 변경, 숫자 기본값 도입, 허위 G/J/F/O 인증 없음.**

## 3. 실제 검사

- [Windows beta ZIP+real localhost HTTP CI #44655842591](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44655842591): Windows Python **3.12/3.14 각각 PASS**, 패키징 **5**/UI·기능·보안·세션 **281** test, 실제 압축 해제+CMD+loopback HTTP+3 plans PASS. 신규 Native0.
- `tests/test_p3_v644_settings_ui_and_sevenzip_feedback_offline.py`: 기존 DOM ID 무중복·핵심 바인딩 보존, 기존 CSS/반응형 규칙, 라이브 제품 JS `installLocalSimcUpdater` Promise 모의 실행 중 `SEVEN_ZIP_REQUIRED`→same-panel 오류, 정상 설치 메시지, 잘못된 경로 차단, UI 진단 raw 코드 접기 여부 검증. 실제 .7z/공식 Nightly 서버·개인 7-Zip 기동 시험은 미수행.
- [CI artifact #14593097643](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44655842591/artifacts/14593097643) 안의 `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip` SHA256 **`b2d3bb0c274316c70fdaac00db5d9af2dad6331ae2ea4157081c0c1b7a00d50d`**; 282 source files + manifest, **282/282 SHA·size 확인**, SimC 실행파일/사용자 credential/session 미포함.
- 별도 headless 브라우저 시각 캡처는 이 실행 환경에서 브라우저 페이지 접근 `ERR_BLOCKED_BY_ADMINISTRATOR`로 수행하지 못했음. **실제 화면의 미적 가독성은 사용자 PC에서 검토가 필요**. CI는 DOM/JS 연결·CSS/반응형 선언·HTTP를 검증한 것이지 사람 눈의 최종 디자인 인수는 아님.

## 4. 후속과 권한

- 사용자 PC: 실제 7-Zip x64 설치 여부와 표준 경로 `C:\Program Files\7-Zip\7z.exe`를 확인, 이미 설치했다면 탐색 경로/커스텀 경로만 추가 진단. ZIP 교체 후 이전 BAT 창 종료, 새 폴더에 풀어 실행; 개인 기존 `runs`·`web-python` 삭제 금지.
- 환경 PENDING: 사용자가 안전하게 복사한 `진단 영수증 복사`에서 `game_build`, `source_stage_status`, `compiler_status`, `compiler_missing`, `source_mode`, `G/J/F/O 원본 소유자`의 실제 값을 확인해야 원본 수집/버전/빌드/인증의 첫 결손을 특정 가능. 비밀키나 개인 경로는 요구하지 않음. 무조건적인 Native 26 spec/전수 수집 불가.
- 다음 디자인 Phase C는 **결과 확인 화면**이다. Phase D는 재현된 기능 피드백 누락만 최소 수정. v639 기존 Native64/통계/캐시 증거는 변경되지 않은 영역만 재사용.
- 공식 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10`, 주 개발 채팅·격리 브랜치/main/v003/Project Sources UI/Work OS 권한 유지.
