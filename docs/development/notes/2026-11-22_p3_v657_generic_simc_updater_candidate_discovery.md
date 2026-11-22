# 2026-11-22 P3 v657 — 범용 SimC 업데이트 관리자 P1

범위: `probe/chat-cache-v035-20261024` 격리 브랜치만. 기존 UI v653 디자인, 제품 최적화/시즌 G/J/F/O/Native/캐시/세션/워크플로 권한 불변.

## 문제와 해결
기존 v655는 공식 Nightly 인덱스에서 첫 번째 1개 패키지만 검사했으며, Git short SHA의 문자열 순서는 커밋 날짜 순서가 아니었다. 70961에 일치하는 패키지가 존재해도 이전 버전 한 개가 먼저 나열되면 놓치는 구조였다.

v657은 **범용**으로 공식 Windows x64 .7z 후보를 최대 12개까지 순차 검사한다. 공식 Git short revision에서 먼저 `client_data_version.inc`의 Live 빌드를 빠르게 읽어 불일치 후보의 3개 대형 헤더 조회를 줄이고, 일치 후보에 한해서 기존 3개 생성 헤더를 모두 검증한다. 프로세스 로컬 커밋별 캐시(최대 32개), 동시 호환성 확인 간 구세대 offer 무효화, 공식 파일 목록의 버전 계열 및 인덱스 순서 보존을 적용한다. **Git SHA 문자열을 최신순으로 취급하지 않으며 엄밀한 최신 빌드 판정도 주장하지 않는다**.

공식 배포에 호환 후보가 없으면 공식 `simc/midnight` HEAD를 **40자리 SHA**로 고정하여 원본 3개 헤더 일치 여부를 검사할 수 있다. 이는 `source_only_candidate`이며 **다운로드 가능한 패키지·실행파일·활성화 offer가 아니다**. 향후 별도 빌드 경로가 필요하며 v657에서 자체 컴파일 또는 자동 배포를 구현/실행하지 않는다.

기존 `check` API/설치/롤백 유지; `check-compatible` 사용자 버튼 및 v653 CSS 불변, HTML/JS 출력에 source-only와 후보 검사 수를 명확히 구분. 한 번의 호환성 검사에서 Native DPS 0, 전체 시즌 환경 재구축 없음.

## 검증 경계
신규 테스트 `tests/test_p3_v657_generic_simc_discovery_offline.py`는 동일 버전 계열의 SHA 순서 오판, 첫 후보 불일치 뒤 성공, 일부 후보 오류, 전부 불일치 시 차단, 원본만 있을 때 설치 금지, 최소 원본 조회, HTTPS 리디렉션 차단, 동시 검사 경합을 다룸. 실제 Windows SimC 70961 실행파일 및 실제 official HTTPS 다운로드/Native 시험은 **미검증**, CI 결과는 별도 기록해야 한다.

다음은 공식 CI 완료 후 변경 파일과 영수증을 확인하고, P2 별도 공식 CMake/CPack Windows Release CLI 빌드 경로(사용자 명시 실행·결과 검증·캐시된 패키지 재사용) 연결 여부를 결정한다. v656의 299 PASS는 역사 증거로만 재사용한다.

## 구현 후 실제 Actions 검증

- `bd4a1af1feda95d5c2ec4bb3a5fcf86575c7e081` 기준 Windows [v181 run #45006558649](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45006558649): Python 3.12와 3.14 양쪽 SUCCESS, 각각 기존 회귀 **299/299 PASS**, Windows CMD/localhost HTTP/3 계획 및 패키징 5건 PASS. 신규 v657 전용 테스트는 기존 299건 목록에 포함되지 않음.
- `af2ce5ce3a4a29d9d9e711c97c71e488e71ed6da` 기준 [v657 전용 run #45006800115](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45006800115): Python 3.12·3.14 양쪽 SUCCESS, **각 35/35 오프라인 단위 테스트 PASS**(신규 9건 + 기존 updater 회귀); Native0.
- 병행 v182 UI run #45006800048은 과거 테스트가 v652 이후 변경된 `diagnoseSeasonBuildEvidence().firstMissing` 표시와 별도로 추출한 `seasonBuildRecoveryPlan`을 오래된 방식으로 고정하여 실패. **제품 JS·CSS 수정 없이 테스트에만 navigation stub·현재 확정 문구 기준을 반영**, 새 확인 CI는 후속 커밋 기준 별도 판정.
- 실제 70961 Windows Native 실행/공식 서버 실 다운로드/원본 시즌 구축은 이 변경으로 검증되지 않음. 외부 원본 검사도 unit fixture이며 Live 시험으로 표시하지 않음.
