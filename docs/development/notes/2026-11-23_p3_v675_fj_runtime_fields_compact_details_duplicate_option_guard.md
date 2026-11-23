# P3 v675 — 검증 F/J 설치본의 v113 실행 필드별 차이 진단 및 소모품 중복값 방어

2026-11-23 KST · 격리 브랜치 `probe/chat-cache-v035-20261024`

## 실 PC 문제와 범위

- 사용자 v674 화면에서 음식 검색창의 **선택된 값** `미사용 (이번 시즌 기본)`과 **열린 검색 결과 1개**가 같은 문자열로 표시됨. 이는 단일 원본 옵션이 화면에서 두 번 보이는 상호작용이지, 원본 선택지에 같은 토큰이 2개 있다는 실측 증거는 아님.
- 드롭다운/레이아웃은 v674에서 한 줄 표시·2열·F/J 전체 폭이 화면상 정상 확인. v675는 기존 외형을 보존.
- 70961/ilvl334/F165/J92·기름 OFF의 정확한 v212 설치본 2개는 사용자 PC에서 계속 선택 보류. 최신 안내 이유는 `DIFFERENT_RUNTIME_SNAPSHOT` (**v113 실행 프로필 입력 차이**). 기존 v670~v671은 `SOURCE_STAGES` 중 v216 SHA의 차이를 확인했으며 동일 실행 입력까지 인증하지 않았음.
- 두 설치본의 실제 개인 v113 파일을 본 개발 환경에서는 열람하지 못하므로 어떤 필드가 다른지 **여기서 추정하거나 READY/동등성을 승인하지 않음**.

## 최소 변경

1. `runner/webui/app.js::populateSelect`에서 DOM select 값 `String(value)`가 완전히 같은 선택지만 첫 항목으로 정규화해 중복 생성 방지. **서로 다른 SimC 토큰·옵션 ID는 그대로 유지**. 검색창과 그 안의 단일 결과가 함께 보이는 것은 기존 정상 동작.
2. F/J 기존 상태 영역은 `동일 F/J 설치본 2건 · 원본 차이로 선택 보류`처럼 짧게 표기. 긴 봉인 원본 이유·v212/v113 차이는 접을 수 있는 `원본 차이 자세히`에만 설명. HTML 구조/기존 SELECT ID/선택 로직 변경 없음.
3. `runner/v113_local_web_api.py::_v675_runtime_input_field_digests`를 추가. 이미 각 v212 단계와 v113 원본 snapshot을 **정확한 SHA·원래 v217 단계 영수증으로 재검증한 경우에만** 기존 정규화된 runtime snapshot의 필드별 해시를 추가 계산. 스냅샷 형식/카탈로그, 실행·READY, 대표 SimC/일반 장비·티어·원본, 게임 빌드·마부·O/ilvl, SimC 소스 프로필·보석배치/예산/ItemID, source path·revision 등 **24개 고정 범주**에 존재 여부와 값 함께 비교. 미지의 추가 필드는 `OTHER_*`에 포함해 **fail-closed**.
4. `DIFFERENT_RUNTIME_SNAPSHOT`가 실재할 때만 `verified_runtime_input_difference_codes`를 각 정확 v212 후보에 응답. 해시·값·SHA·경로는 네트워크/브라우저로 전달하지 않음. 기존 진단 복사에 고정 범주 `runtime_difference_codes` 추가, schema `v675_local_verified_fj_collision_diagnostic_v1`로 구분.
5. 설치본 대표 선정의 `_v672_verified_runtime_inputs_digest`와 `verified_runtime_equivalent_representative` 정확 SHA 승인 **동일**, G/J/F/O 원본·수치·프로필 차이의 선택 차단 **동일**, Native/캐시/세션/READY/95% 통계 **불변**.

## 증거 및 회귀

- 합성 v113 프로필의 `simc_input_token` 변화는 `COMPILATION_V098_PROFILE` 차이 **하나만** 감지. 미지의 필드 추가도 `OTHER_COMPILATION_FIELDS`로 차단, missing과 present null 구분.
- synthetic JS: 같은 `source_default` 등 DOM value 1개만, 다른 효과 값 유지. 기존 v669~v674 exact F/J 판단 재사용, 동일 SHA 임의 선택 금지, 화면 접힘/세부 라벨 및 복사 JSON scope/민감정보 비노출 검증.
- [Windows Actions #45121662682](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45121662682): Windows Python 3.12/3.14 각 **357 PASS/0 FAIL** + 각 Windows 추출 CMD/localhost/3 plan **5 PASS**, 제품 ZIP Action artifact #14794191248.
- [API Actions #45121662611](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45121662611): Ubuntu Python3.12, Windows Python3.14 각 **516 tests, 1 SKIP/0 FAIL**.
- 별도 추출한 단일 제품 `SIMC_SECONDARY_OPTIMIZER_v675_WINDOWS_BETA.zip`: **1,538,559 bytes**, SHA256 `6a81508879cb2c929f8d1d11d5bc84ddd9192b450d5f44b366f59314acd742f0`; CRC 및 V181 manifest **286/286 SHA·size PASS**, 번들 `simc.exe` 없음.
- 신규 DPS Native 0회, 컴파일 0회, 외부 API 수집/캐시 폐기 0회. 로컬 조회 시 기존 동일 물리 2개 후보의 이미 인증된 v113 스냅샷 내부 필드 해시 24개 계산만 추가. 개인 경로·비밀키는 응답하지 않음.

## 현장 다음 단계와 한계

v675 ZIP을 새 폴더로 실행, 기존 관리형 70961 SimC 및 캐시를 유지. 로컬 저장 설치본 조회용 `12.1.5.70961`/ilvl334/4 소켓/기름 OFF. **시즌 환경 설치·Native/최적화 금지**. F/J 전체 폭 아래 `원본 차이 자세히`에서 정확한 v113 필드 범주를 확인하거나 `중복 원본 진단 복사` JSON만 전달받아 실제 근거와 대조. 실행에 유의미한 차이가 있으면 대표 설치본 자동 선택 차단을 유지; 역사 v216 원본이 없다는 사실을 덮지 않음. 현재 KR Live build 일치/실 PC v675 표시/실제 DPS 최적화 E2E **미검증**.

공식 `15/78 COMPLETE`는 제품 구현률이 아니며 `full_product_e2e=PENDING`, `next_review=B10` 불변. `main` 병합·immutable·Project UI·Work OS 승격·주 제품 개발 채팅 권한 변경 없음.
