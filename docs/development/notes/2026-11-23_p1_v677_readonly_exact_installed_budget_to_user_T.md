# P1 v677 — 검증된 기존 설치본을 G/J/F/O·B/T 및 사용자 프로필 준비로 연결 (Native0)

2026-11-23 KST · `probe/chat-cache-v035-20261024` 격리 개발 · 신규 제품 코드 HEAD `5ae25da68260174a09b84b0466e5d76b03e57bc3`, 신규 API 회귀 테스트 HEAD `9fae15d6a4d4049a6db07f59f874a6f5df8d1147`.

## 승인된 제품 목적과 최신 개인 PC 실측

- 사용자 목표는 기본 목표 ilvl 334(또는 수동 최종 T)에 대해 26개 DPS 전문화의 치명·가속·특화·유연 **최적 절대 rating**을 SimC DPS로 찾는 제품. 현재 장비 총계 재분배·전체 시즌 DB·장비 추천·과도한 동등성 비교 Gate는 범위 밖.
- 이전 v676 개인 PC 캡처에서 `12.1.5.70961`(기존 설치본 조회용, **현재 KR Live 검증 아님**), 화염 마법사/드워프, ilvl334, 소켓4, 기름 미사용, 영약 F165, 보석 J92, `검증 환경 1`의 정확한 설치 SHA 선택 확인. 다만 UI의 T는 여전히 `시즌 구성 검증 후 표시`.
- v676 버튼 `선택 환경 검증·준비`가 `buildSeasonEnvironment(true)`를 호출하면 선택된 기존 설치본이 있음에도 G/F Native를 다시 요청할 수 있는 문제를 발견. v677은 **그 경우 기존 원본만 읽는 경로**를 구현. UI에서 Native·시즌 재구축을 자동 시작하지 않는다.

## 구현

1. `runner/v113_local_web_api.py`: GET `/api/v1/environment/installed-budget`, 내부 `_v677_verified_existing_budget`. 사용자가 선택한 정확한 `installed_manifest_sha256`/빌드/ilvl/영약 ItemID/대표 G track를 검증. 기존 v216 exact-SHA v212 설치·카탈로그·단계 영수증, v113 저장 프로필 단계, 일반 보석 4개, 기름 미사용/고정 O=0, 기존 예산 원본 검증을 재사용.
2. G/J/F/O/B/T는 **원래 v212 설치 문서와 별도 확인한 v216 재사용 영수증에 일치**하는 경우에만 반환한다. `B=G+J+F`, `T=B+sum(O)` 회계 확인. 수치 누락을 0으로 추정하지 않는다. 소켓·flask·G track·manifest SHA 중 하나라도 다르면 HTTP 409/422 차단한다. 신규 Native/DB2/Wago/외부 네트워크·캐시 쓰기 0. 복수 설치본의 상호 동등성 요구 0.
3. `runner/webui/app.js`: `선택 환경 검증·준비`에서 명시적으로 선택한 기존 F/J 설치 SHA가 있으면 **오직 위 read-only GET**을 호출. 필요 시 동일 SHA의 기존 `/api/v1/season-gear` GET으로 장비 후보를 연결한다. 요청 도중 선택 변경은 거절. 결과에 70961 같은 조회용 설치 빌드의 `current_retail_build_verified:false`가 명시되며 **현재 Retail READY로 과장하지 않는다**.
4. 자동 예산 모드에는 설치본과 시즌·ilvl·F/보석/O·G track·정확한 후보 SHA가 모두 일치할 때만 공식 기존 T를 표시한다. 수동 최종 T는 사용자 입력이 우선. 입력 조건이나 설치본을 바꾸거나 장비 후보를 재연결하면 숫자 근거를 무효화한다.
5. 새 최적화 진입에서 시즌 장비 후보가 빠졌어도 **정확한 설치 SHA가 선택되어 있으면** 동일 read-only prepare로 복구하며, G/F Build로 fallthrough하지 않는다. 기존 설치본이 있으나 선택 안 한 일반4보석 O0 구성은 먼저 정확한 선택을 요구한다. 선택적 다른 기름·소켓·특수보석 등 고급 구성의 이전 명시적 동의 기반 Build 경로는 보존한다.
6. 보존: 기존 적응형 SimC·DPS Native/SEM/95% 통계·후보 생성·캐시·취소·재개·저장 세션/원본 영수증/Native 캐시를 변경하지 않는다. 새 보조 효과 엔진·별도 proc 인증·시즌 전체 아이템 DB도 만들지 않았다.

## 신규 시험과 한계

- 새 `tests/test_v677_existing_budget_readonly_p1.py`: FastAPI GET exact budget, wrong build/ilvl/SHA/flask/G track·예산 오차·보석 증거 누락 차단, 파일 바이트 보존, Subprocess/네트워크 차단, 실제 JS 버튼은 GET만 호출하고 Native Build를 호출하지 않음. 기존 `tests/test_v113_local_web_api_offline.py`의 정규 CI에 포함.
- 종전 v568 독립 JS harness에서 임의 문자열 `334`를 `season-verified-budget`으로 반환하여 `oilUseIntent` 참조 오류 발생한 회귀를 정확한 64자리 SHA 형태 선검증으로 수정. 원래 첫 클릭 복구·무선택 빌드 계약 유지.
- [v113 API #45128081605](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45128081605): Ubuntu 3.12/Windows 3.14 각각 **521 tests OK (skipped=1), 0 FAIL**.
- [Windows ZIP #45128051271](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45128051271): Windows Python 3.12/3.14 각각 **357 PASS/0 FAIL**, 별도 패키지 5 PASS, 기존 실제 loopback HTTP 및 세션·캐시 오프라인 회귀.
- GitHub Actions wrapper artifact #14796064684의 내부 Windows ZIP을 실제로 분리·확인: `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip`, **1,538,784 bytes**, SHA-256 **`18a9119e486a3a5a9b469c8c848504a752dc3331a69deea915193bb5b42c3eeb`**. ZIP CRC·V181 manifest **286/286 파일 SHA·size PASS**. 관리형 `simc.exe` 포함하지 않음.
- Native 신규 호출 **0회**. 정적 기존 시즌 증거는 valid same-build 조건에서만 재사용한다. **사용자 PC v677 read-only 준비/자동 T 실제 검증은 아직 미실행**, 현재 KR Live 빌드 일치 미확정, 실제 DPS 최적화·전26 전문화 end-to-end 완료 주장 금지.

## 다음 사용자 PC 동작

- 기존 v676 CMD/탭 종료, v677 Windows ZIP 새 폴더 설치. 기존 `simc-managed`와 시즌 설치 영수증·캐시·run 폴더를 삭제하지 않는다.
- 기존 검증 설치본 조회 조건 `12.1.5.70961`, 목표 334, 일반 보석4, 기름 OFF, 화염 마법사/드워프, 기존 특성, F165(설치 영약), 신규 G/F Native/시즌 자동 구축 고급 체크 모두 OFF.
- `검증 환경 1`을 선택하고 **`선택 환경 검증·준비`를 단 한 번 누름**. 기존 exact GET이 성공하면 최종 T 숫자와 원래 G/J/F/O 회계 및 `Native 0회` 상태가 표시돼야 한다. 실패하면 안전한 오류 코드/상태 문구를 보고 source 문제부터 확인한다. **이번 시험은 DPS 최적화 시작 전까지**.
- 이후 현재 KR Retail 빌드 재확인 및 실제 장신구 2개·목표 조건 연결로 사용자 실제 SimC 제품 E2E 진입.

공식 상태 `15/78 COMPLETE`는 완성률 아님, `full_product_e2e=PENDING`, `next_review=B10`. `main`/v003 immutable/Project UI/공식 Work OS·Shared State/원본 v016 통합/기존 주 제품 개발 채팅 소유권 변경 없음.
