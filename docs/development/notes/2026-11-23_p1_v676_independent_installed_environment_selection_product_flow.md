# P1 v676 — 기존 설치본 상호 동등성 Gate 제거, 개별 검증 원본 선택 연결

2026-11-23 KST. 격리 브랜치: `probe/chat-cache-v035-20261024`.
제품 코드 HEAD: `3327907b4a1a446b81e6435b822b5ddeea3114c8`.

## 최신 직접 사용자 결정 및 문제

- 목적은 미래 ilvl(기본 334) 또는 사용자 지정 최종 CHMV T의 DPS 최대화에 필요한 절대 rating. 전체 장비 재분배 또는 설치 영수증 차이 판별 자체가 제품 목표가 아니다.
- 사용자 PC v675 실측: `12.1.5.70961`, ilvl334, 영약 ItemID241320·품질2 F165, 기본 보석 `240890/240898/240906/240914` J92, 무기 기름 O0. 검증 설치본 2개가 공존하며 v216 preflight/staged source 및 v113 실행 프로필의 일부 입력은 다르다. **서로 다른 두 검증 설치본의 완전한 동등성은 검증할 필요가 없고, 각각 자기 자신의 원래 영수증 검증 여부가 핵심**이라는 최신 사용자 승인을 반영한다.
- 동일시/합치기/가장 최신 파일·최소 SHA의 자동 우선 선택은 하지 않는다. 동일 숫자의 중복을 이유로 모두 비활성화하던 부정확한 부가 Gate는 제거한다.

## v676 제품 코드 변경

- `runner/v113_local_web_api.py::installed_oil_loadouts`: 후보별 `v216.find_verified_installed_season_environment`를 **정확한 installed SHA·빌드·ilvl·oil**로 검사. 보석 물리 구성·품질 조건 확인 후 원래 v212 source-stage 및 v113 profile-stage 검증(`_v672_verified_runtime_inputs_digest`를 이제 비교 없이 개별 검증만 수행) 성공 시 `individually_verified: true`와 검증된 원본 `simc_revision` 표시. 이후 SHA 간 비교·동등성 Gate·원본 field-diff 진단 수행 0회. 인증 실패는 선택지 미포함. 기존 v212/캐시/로그 파일 변경 없음.
- `runner/webui/app.js::renderInstalledFlaskChoices`: 빌드/ilvl·물리 ItemID·개별 인증 플래그로만 목록 필터링. 같은 F/J/itemID라도 독립 인증된 경우 **검증 환경 1/2** 별도 선택 가능(순위 아님). 옵션의 값은 정확한 v212 SHA; 레이블에 SHA·개인 경로 없음. 선택 시 기존 `chooseInstalledFlask` → 동일 flask ID + 선택 SHA의 유일 매칭 → `/api/v1/season-gear?installed_manifest_sha256=...` → 기존 인증 프로필/옵션 연결 경로 유지. 선택된 exact SHA는 세션/재개 시 기존 독립 검증으로 다시 검사.
- 이전 v669~v675 상호 비교 진단·복사 UI는 기본 흐름에서 숨김. 이력용 legacy helpers는 불필요한 기본 실행 호출에서 분리했으며 별도 원본 전수 감사나 추가 효과 Gate를 구현하지 않음. 음식/영약/물약/증강 룬 2열 및 장식 1·2 가로 2열 UI 유지.
- `tests/test_v669_verified_fj_physical_identity_offline.py`, `tests/test_v113_local_web_api_offline.py`, `tests/test_v667_season_failure_receipt_offline.py`: 과거 동일 F/J 무조건 선택 차단 기대를 독립 v212/v113 검증·정확 SHA 선택 가능 기대값으로 교정. 다른 빌드/ilvl·부정확한 보석·미검증 후보는 불가; 기존 v212/v113의 본래 인증은 생략되지 않음.

## 신규 검증 범위와 재사용

- [Local Web API #45125743090](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45125743090) Ubuntu3.12, Windows3.14 각 516 tests / 1 SKIP / 0 FAIL.
- [Windows Beta #45125880996](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45125880996) Win Python3.12/3.14 각 357 PASS / 0 FAIL 및 별도 패키징 5 PASS, 실제 launcher/로컬 HTTP 기존 회귀.
- GitHub Actions wrapper artifact `14795353318`; 내부 단일 제품 ZIP `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip` 1,536,048 bytes, SHA256 `2550729866fb46c4880bd48f3b1ecc38de2e276723c6cdfc65e5c8dcdbae0f43`. ZIP CRC PASS, manifest 286/286 SHA256·size PASS. 제품 ZIP에 관리형 SimC 바이너리는 포함하지 않으며 기존 계정 연결 사용.
- 새 DPS Native 0 / 새 정적 Native 0 / 외부 DB2·Wago 0 / 캐시 및 기존 설치본 삭제 0. 모든 단위·HTTP·패키지 결과는 PC 실환경 E2E 또는 전26 전문화 완성 증거가 아님.

## 사용자 PC에서 확인할 다음 한 동작

- 기존 v675 종료→v676 Windows ZIP 새 폴더 실행. 기존 관리형 SimC 저장 상태 유지. 시즌 설정은 기존 설치본 조회 전용 빌드 `12.1.5.70961`, 목표334, 기본4보석, 기름 OFF; 모든 새 시즌/Native 구축 체크 OFF. 한국 Retail 현재 70961 일치 인증은 아직 없음.
- 최적화 화면 `검증된 F/J 구성`에 `검증 환경 1`, `검증 환경 2`가 활성 표시되면 *하나*를 선택하고, 기존 `선택 환경 검증·준비` 이전에 exact SHA로 환경 후보가 정상 연결되는지 상태 문구 확인. 어느 환경이 더 효율적이라는 순위 또는 실행 동일성 주장은 없음.
- 만약 0개면 재검증 실패 상태로 보존하고 **실제로 필요한 최초 실패**만 확인. 과거 SHA 차이의 반복 감사, SimC Native 전수, 설치본 삭제 금지.
- 독립 설치본 선택은 현재 테스트 빌드의 환경 연결 시험이며 KR Live 현재 빌드와 소스 적합성은 별도로 검증. DPS E2E는 미수행.

## 변경되지 않은 범위·권한

제품 정체성 26 DPS 전문화만, G/J/F/O 공식 회계 `B=G+J+F`, `T=B+O`, O 비자유분배, L/G 내부 보호, 최고품질 등록 및 기존 Native/SEM·95% 판정·캐시/취소·재개 불변.

공식 `15/78 COMPLETE`는 제품 완성률 아님, `full_product_e2e=PENDING`, `next_review=B10` 불변.
`main`, `v003 immutable`, Project Sources/UI 실제 적용, 공식 승격·Work OS/Shared State·주 제품 개발 채팅 소유권 변경 없음.
