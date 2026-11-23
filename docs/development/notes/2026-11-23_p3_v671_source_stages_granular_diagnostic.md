# P3 v671 — 개인 PC F/J 중복 설치본 SOURCE_STAGES 유일 차이의 단계별 분해

2026-11-23 KST · 격리 브랜치 `probe/chat-cache-v035-20261024`

## 직접 사용자 PC 실측(v670 진단 영수증)

- 사용자가 전달한 `v670_local_verified_fj_collision_diagnostic_v1`: game_build `12.1.5.70961`, ilvl334, 동일 물리 구성인 검증 설치본 **2개**. 영약 ItemID `241320` 품질2, F165; 보석 4개 ItemID `240890/240898/240906/240914`, J92.
- 검출된 원본 차이 코드는 `SOURCE_STAGES` **한 개**. 이는 v670가 검사한 다른 소스·예산 그룹에 차이를 발견하지 못했다는 뜻일 뿐, 완전한 실행 동등성이나 현재 Retail build 일치 인증이 아니다.
- `SOURCE_STAGES` 묶음은 `staged_source_environment_sha256`, `original_v216_preflight_sha256`, `original_v217_stage_receipts`의 조합. v212의 stage manifest는 v216 사전 검증 SHA와 v217 단계 영수증을 포함하므로 단순 실행시각 차이로 해석하거나 임의 설치 SHA를 선택하는 것은 금지.
- 사용자 PC 저장된 원본 `v212`/`v113` 파일 자체는 GitHub에 없으며 여기서는 열람하지 않음.

## 최소 구현

- `runner/v113_local_web_api.py::_v670_sealed_fj_difference_proofs`의 **기존 안전 진단만** 증분 확대. `SOURCE_STAGES` 통합 범주를 보존하며 같은 봉인된 `v212` 필드에서 `STAGED_SOURCE_MANIFEST`, `V216_PREFLIGHT_SEAL`, `V217_V191_RECEIPT`, `V217_V211_RECEIPT`, `V217_V213_RECEIPT`, `V217_OTHER_RECEIPTS` 차이를 구분. SHA 원문·사용자 경로·프로필·비밀키는 응답에 포함하지 않음.
- `runner/webui/app.js`에서 위 범주를 한국어 단계 설명으로 표시. 기존 `중복 원본 진단 복사` 버튼 및 exact build/ilvl scope 검증을 재사용. 원본 동일성이 확정되지 않은 복수 설치본의 선택 차단은 그대로 유지.
- 기존 v212/v216/v217 stage fingerprint·READY 판정·G/J/F/O 회계·SimC Native/DPS·캐시·저장·취소·재개·공식 95% 통계 로직 변경 없음. G/F·DB2·HTTP 새 수집이나 C++ 컴파일, DPS Native 실행 0회. 신규 외부 의존성 없음.
- 테스트 `tests/test_v669_verified_fj_physical_identity_offline.py`에 동일 예산·물리 ItemID지만 v216 preflight 및 v217 v211 receipt가 다른 합성 예제 추가. 차이 코드를 분리하고 raw SHA 비노출/차단 유지 검증. 기존 v670 UI·API 회귀도 재사용.

## 새 검증

- 제품 코드 HEAD: `171535f6300d399f7f796d427d08a9456f2a53ed`.
- [Windows Beta/실 local HTTP Actions #45104708877](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45104708877): Windows Python 3.12·3.14 **각 350 PASS/0 FAIL**, 기존 패키지 관련 5 PASS, 로컬 CMD/HTTP/기존 계획 회귀 성공. 실제 6-case DPS Native는 SKIP, 신규 DPS Native 0.
- [v113 API #45104708896](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45104708896): Ubuntu Python 3.12·Windows Python 3.14 각 **509 tests OK(skip1)/0 FAIL**.
- GitHub Actions wrapper [artifact #14786414927](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45104708877/artifacts/14786414927)은 단일 제품 ZIP과 다른 파일. 내부 `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip`: **1,532,968 bytes**, SHA-256 `1652f5650d09c7c098acf5e7ba055a8a74b2580514406858dd8bb8268754d0a3`, manifest **286/286 SHA·size PASS**, CRC PASS, 포함된 `simc.exe` 없음.

## 다음 현장 조작 및 STOP 조건

- v671 ZIP 새 폴더, 이전 CMD 종료/탭 정리. 기존 관리형 SimC 70961 유지. 기존 70961 설치본 조회 용도로만 `12.1.5.70961`/ilvl334, 기본 4보석, 기름 OFF, 비필수 특수장비·장식 OFF. 시즌 G/F 자동 산출 및 모든 Native 옵션 OFF.
- `시즌 환경 확인·설치`나 DPS 시작은 누르지 말고, 최적화 화면의 영약→검증된 환경 구성 아래 `중복 원본 진단 복사`를 1회 눌러 코드만 전달. 현재 KR Live 일치 및 새로운 READY/DPS E2E를 주장하지 않음.
- `V216_PREFLIGHT_SEAL`, v217 세 단계, `STAGED_SOURCE_MANIFEST` 중 정확히 무엇이 달랐는지 확인 후, 이미 검증된 결과/대표 프로필에 유의미한 차이인지 최소 검토. 추가 원본을 검증할 수 없으면 fail-closed 유지. 무조건 SHA 병합·랜덤/latest 선택·새 Native 전수 금지.

공식 `15/78 COMPLETE`(제품 구현률 아님), `full_product_e2e=PENDING`, `next_review=B10` 불변. main·v003 immutable·Project Sources/Instructions 실제 적용·Work OS·Shared State·원본 v016 직접 통합·기존 주 개발 채팅 소유권 변경 없음.
