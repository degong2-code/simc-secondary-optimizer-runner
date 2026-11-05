# SIMC SECONDARY OPTIMIZER — P3-EV 단일 엔진 인계 정본 (2026-11-05)

**분류:** GitHub 격리 개발 인계, 사용자 승인 설계/Project UI/Work OS 공식 승격 아님. **최우선:** 하나의 26 DPS 공통·시즌 교체에도 재사용 가능한 Environment Build **엔진 완성**. 특정 시즌의 정적 수치를 찾아 기록하는 프로젝트가 아니다. 이 인계 이전의 P3-ES/EN/EE 등은 역사 자료이며 필요 기능만 추적한다.

## 0. 신뢰 기준·실제 HEAD (인계 작성 직전)

- repo `degong2-code/simc-secondary-optimizer-runner`; 격리 `probe/chat-cache-v035-20261024`. **인계 작성 직전 격리 HEAD** `585d6435d28c375f25f49b967a7d982c3fc8e241` (P3-EU 검증 결과 문서), **최신 실제 제품 코드 커밋** `e92467a0be2fc0a6f343a618c1b728ef5f25bd1e`, **main HEAD** `07133e0aaf738d6e4816a6486057b1cd49c018de`. **P3-EV 문서 반영 후 격리 HEAD는 변경된다. 새 채팅은 격리·main을 각자 실제 재조회**하고 위 SHA를 최신이라고 고정하지 말 것.
- 권위 순서: **최신 사용자 직접 결정 > 승인 [v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) 및 충돌 없는 1.4 계열 > GitHub 실제 코드·봉인 원본·Actions/Native > 이 인계와 과거 작업 노트**. 26 DPS(증강 제외), 특수 보석 **정확히 1개 필수**(P3-EC; 철회된 P3-EB 0개 허용 불가), 열린 소켓에 일반/특수 장착 가능·색상/소켓 종류별 적합성 Gate 불필요(P3-EQ).
- 권장 읽는 순서: **① HEAD 2개 독립 조회 → ② 이 단일 인계 → ③ [PROTOCOL](development/PROTOCOL.md) → ④ [자산 라이브러리 INDEX](development/INDEX.md) 중 E3/E2/E1 → ⑤ [CURRENT 최상단](CURRENT_PRODUCT_DEVELOPMENT_STATE.md)와 [실행 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md) → ⑥ [P3-EU](development/notes/2026-11-05_p3-eu-fresh-environment-install-engine.md), [P3-ET](development/notes/2026-11-05_p3-et-v212-prepared-option-source-identity.md), [P3-EV](development/notes/2026-11-05_p3-ev-engine-install-continuity-handoff.md) 및 실제 관련 함수·증거/코드 SHA**. 특정 소스가 부족할 때만 B3/C4/D1/D2, A1~A3를 더 열고 과거 [INDEX 원문](development/HISTORICAL_INDEX_20261105_PRE_LIBRARY.md)·[P3-ES 인계](CHAT_CONTINUITY_HANDOFF_20261105_P3_ES_ASSET_LIBRARY.md)를 참조. **역사 P3 전체 전수 재독해 금지.**

## 1. 최종 제품 목적과 이번 완료 판정

사용자 목표 ilvl(기본 **334**) 또는 **최종 CHMV T 수동 입력**에서 미래 치명/가속/특화/유연 **최적 절대 rating**을 SimC DPS 최대화로 탐색하는 단일 웹앱. 딜러 **26개 전문화**, 직업·전문화·종족·특성·장신구2·선택 특수장비·장식 최대2·최고 품질 소모품·전투조건을 받으며 일반 장비·무기·티어4는 내부 대표 프로필. 사용자가 현재 장비 전부를 고르거나 현재 스탯을 재분배하지 않음. 최종 출력은 DPS·SEM·**95%** 판정(관측 1위와 통계적 우위 구별)·근접하면서 실제로 다른 대안·비율·캐시/취소/재개. 장비·파밍 경로 추천/전 시즌 장비 DB/탱힐·증강/자체 APL·proc·효과 엔진 제외.

**현재 개발 완료 Gate = 정상 단일 사용자 웹앱 `v216 Environment Build`의 신규 시즌 `T1`:** 시즌 원본에서 대표 일반 장비·무기·티어4 **G**, 검증된 최고품질 기본 보석 **J**, 영약 **F**, 선택 무기 기름 **O**를 자동 구축·검증 → 기존 `v222` 공식 `B=G+J+F; T=B+O; c_final=c_base+o` (수동 최종 T 우선, 특수 L·영구 E·기름 O 중복 없음, 장신구 고정치는 자유 G 밖) → 검증된 최고품질 선택지 정책 A **실제 사용자 발행** → 기존 `v212` 버전화 설치·READY/T1. **미완료.** `v098→v096/v094` 적응형 DPS는 다음 제품 단계이므로 환경 READY의 선행 Gate 아님.

**개발·시험의 차이:** 시즌별 수집/검증/예산/발행/설치 기능을 먼저 엔진으로 완성한다. **현재 시즌을 신규 시즌처럼 초기 상태에서 실행하는 통제 T1**은 이를 검증하는 시험이지, 현재 시즌 수치를 수동 확정하는 개발 목표가 아니다. 일반 개발에서는 동일 조건의 기존 영수증·캐시를 재사용하되, 최종 제로기존자료 T1 시험은 승인 v1.4.3/P3-AA 통제대로 옛 환경 자료를 답안·증거로 주입하지 않고 실제 수집 경로를 이용한다.

## 2. 코드 기준 및 P3-ET/EU 최근 변경 — Evidence와 Integration 분리

| 기능 자산 | 이미 작성·회귀 확인된 경로 (REUSE) | 아직 연결되지 않은 실제 제품 경계 |
|---|---|---|
| **A/B/C/D 신규시즌 원본** | `v161/v191/v211/v213/v217`, `v229/v230/v232/v251` 대표 장비·기본 소켓, `v221/v266/v268` 보석 ID/정적 후보·캐시, `v271` 가변 소켓 일반N+특수1, `v278/v281` 선택 F/O Native, `v285/v286` 기름 무기 관계, `v277` 선택 exact G·같은시즌 G 참조. | 원본 관측·source-only 출력을 **신규 시즌 실제 승인 G/J/F/O 및 정책 A 4-family 내부 영수증**으로 완성해 제공하는 source-owner 공급자. 구시즌 값(예: G 참조, F165/J138/O16+16) 복사 금지. |
| **E1 예산** | `runner/v222_season_budget_contract.py:preprofile_budget` 공식 수치 재계산 및 수동 T·기름 OFF. `v216` zero-history 숫자 미리보기는 미승인이라고 분리. | 기존 Source 소유자가 **정확한 시즌/효과/품질/물리 소켓·손·정적 스탯**을 검증한 자료를 `trusted_budget_evidence`로 제공해야 함. `VALID_SAME_SEASON_SOURCE` 텍스트/합성 수치가 스스로 원본 인증을 만들지 못함. |
| **E2 정책 A** | `runner/v220_catalog_auto_admission.py:decide` 4 계열 `source_relation/simc_input/product_input/chmv_budget`와 `v196.prepare_verified_fresh_choices` 준비. **P3-ET**는 `v212`에서 v213 exact ID/토큰/부위·품질/identity 재대조. | 정상 신규 시즌의 **실제 검증된 사용가능 선택지** 영수증 공급/발행은 미완료. optional만 부족하면 해당 항목만 보류, 검증된 core를 불필요하게 막지 않음. 합성 테스트의 선택지 발행 플래그 ≠ 실제 목록 발행. |
| **E3 설치 엔진 (P3-EU)** | `runner/v212_environment_manifest.py:compile_fresh_installed_environment, verify_fresh_installed_environment`가 기존 `v222+v196` 결과를 버전화하고, `runner/v216_environment_build_coordinator.py:_install_verified_fresh_environment_only`가 **`v217.execute_stage` 봉인/재개**. 원래 `v216.build_environment(fresh_collection_inputs=...)`에 내부 callable `verified_install_input_provider`를 연결; `None`이면 원래 `STAGED_NOT_INSTALLED` 유지, 확인된 자료면 설치 코드 경로 호출. provider가 수집기로 전달되지 않도록 P3-EU에서 수정. | **실제 원본 검증을 완료해 provider가 정확한 bundle을 반환하는 구현 미완료**. 현행 callable은 내부 연결 지점이며 **Python 함수 타입이 신뢰성 인증은 아님**. 실제 정상 웹앱의 신규 시즌 READY/T1 및 사용자 선택지 발행은 아직 실증 없음. |
| **F 사용자 DPS** | `v143/v139/v098` 대표 프로필, `v096/v094` 적응형 SimC DPS·캐시·95% 등 기존 기능. | 환경 T1 이후 메인 경로로 연결·실 시험. 신규 DPS 최적화 엔진 개발 불필요. |

**중요 원본 코드 Git blob SHA (인계 작성 전 HEAD에서 독립 조회):**
`v216` `aa664d80a8a3de604f89475a2bd686f210cc943c`; `v212` `987cee3bc742c9f73a2a1486853b6ff0ca9b3047`; `v222` `35a3631cba616df9518ad6cc4c73f07130e5a624`; `v196` `3550dec64a02f4bc219a096f9a0a0f6161827040`; `v220` `1d7e2cd1cf389b56067d27603080c6aef511122a`; `v217` `d8993b4f6e1af97b6a2149c3b39062660a5579b8`. 변경되면 최신 HEAD에서 재조회하고 범위 일치 여부 확인. 원본 데이터/봉인 영수증은 현재 코드가 보유한 실제 시즌·SimC revision·빌드·옵션·SHA별로 조회; 임의 이전 시즌 증거로 대체하지 않는다.

## 3. 검증 영수증의 정확한 범위

- **최종 제품 코드 P3-EU 교정** [e92467a](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/e92467a0be2fc0a6f343a618c1b728ef5f25bd1e). [focused #41994773484](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41994773484) **255 PASS/0 FAIL·DEV_LEDGER_PASS**, 해당 문서 HEAD [#41995156424](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41995156424) **255 PASS/0 FAIL·DEV_LEDGER_PASS**. [v212 #41994773720](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41994773720) Ubuntu·Windows 각 **452 tests=448 PASS/4 SKIP·Native0**. [v113 #41994773590](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41994773590), [v181 #41994773528](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41994773528), [v182 #41994773792](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41994773792) SUCCESS. 모두 코드·오프라인·합성 입력 범위, **실제 신규 시즌 환경 T1 아님**.
- **보존할 실패:** [최초 focused #41994600854](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41994600854)는 provider가 수집기 kwargs로 넘어가 1개 회귀 실패. [e92467a 교정](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/e92467a0be2fc0a6f343a618c1b728ef5f25bd1e) 뒤 PASS. 반복 재현이 필요하지 않음.
- **재사용할 과거 실 Native:** [P3-BX 소켓 #41601140696](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41601140696) 4/4는 SimC 보석 입력 수용을 증명하지 게임 내 모든 아이템의 소켓 허용성을 인증하지 않음. [F/O #41666305288](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666305288)/[#41666925906](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666925906) 등은 **해당 시즌·빌드·binary·프로필·옵션 범위에만** 적용. 신규 P3-EU 구현·검증 및 이 인계 단계에서 실 Native/게임 HTTP **0회**.
- **미관측·미실행:** 신규 시즌 G/J/F/O 실제 자동 원본 인증 완료, 검증 선택지 실 사용자 발행, 단일 웹앱 cold-start T1, `v098` DPS end-to-end는 **아직 증명하지 않음**. CI PASS를 T1 READY로 승격하지 않는다. 인계 문서 자체의 CI는 새 커밋 뒤 별도 확인.

## 4. 다음 작업·더 효율적인 경로

**즉시 P1 (가장 작은 실 개발 묶음):** 기존 `v216` 자동 수집 출력을 바탕으로 **source-owner 내부 provider**의 실제 G/J/F/O 및 정책 A 증거 생성·검증·연결을 완성한다. 단일 정상 `build_environment`에서 선택된 검증 항목만 기존 `v222/v220/v196/v212/v217`에 건네고 실제 설치/READY까지 이어지게 한다. E3→E2→E1부터 역추적하되, 값 인증이 아니라 **입력·출력 연결 기능**을 개발한다. 사용자가 명시적으로 최종 T를 지정하면 우선, 특수 gem 정확1, O 고정/명시적 미사용, L/E 중복 방지를 보존한다. **원본 증거가 이미 있으면 REUSE/CONNECT, 실 누락일 때만 EXTEND**, 독립 없음이면 NEW, 불필요하거나 범위 외면 STOP.

**즉시 P2 (완료 판정):** 내부 검증 결과·합성 fixture로 성공/보류/실패·동일조건 캐시·취소 재개·교란 차단을 최소 범위 회귀. 그다음 승인 P3-AA 통제에 따라 **현재 시즌을 신규 시즌으로 가정한 정상 웹앱 T1**(기존 환경 데이터 주입 없는 cold start, 필요한 공식 외부 원본 수집은 허용). 과거 같은 조건 Native/Actions 영수증 재사용, 실제 변경분만 최소 보완. 필요시 새 시즌의 구체적 누락값 확인은 **시험 입력 검증**이지 시즌별 하드코딩 목표가 아니다.

**후속 장기:** 환경 READY가 실증된 이후 `v098→v096/v094`의 기존 적응형 SimC를 26 DPS 단일 제품 흐름으로 완성·검증한다. 진행·취소/재개·캐시·오류 원문·SEM/95%·관측 1위·근접 대안을 유지. 신규 수렴 엔진/전문별 APL, 정밀 SEM 과투자, 비필수 전국/전수 Native, 대규모 `v216` 재작성 금지.

**매 작업 강제 자가점검:** “**이 작업이 다음 시즌에도 그대로 작동하는 하나의 엔진 완성에 기여하는가?**” → INDEX 관련 분류만 선조회 → 원본 바이트·코드/영수증 scope 확인 → Evidence/Integration 구분 → REUSE/CONNECT/EXTEND/NEW/STOP → 독립 작업 논리적 묶음 → 실제 변경 범위만 검증 → 불필요한 Native/HTTP/Actions·캐시 재생성·메모리/I/O·실행시간·구조 복잡화 점검 → 해당 라이브러리/노트 1개만 갱신.

## 5. 문서 반영·미반영·권한

**이번 P3-EV:** `docs/development/PROTOCOL.md`, `INDEX.md`, `CURRENT_PRODUCT_DEVELOPMENT_STATE.md`, `DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md`, [P3-EV 노트](development/notes/2026-11-05_p3-ev-engine-install-continuity-handoff.md) 및 이 인계 문서만 갱신. 이전 P3-ES·P3-EU 상세 기록/실패 및 역사 INDEX 스냅샷은 보존. **DOCS_ONLY / 신규 코드·원본/Native/게임 HTTP/실 T1 없음.** P3-EV 문서 커밋 HEAD·CI 검증은 아래 새 채팅에서 재조회할 것.

**미반영/미승격:** 실제 자동 source-owner와 실 READY/T1 미완료. 제품 원본 `v016_SCENARIO_CONTRACT`은 사용자 보고 기준이며 바이트 직접 통합 증거 없음. `main` 병합, `v003` immutable, 승인 v1.4.3 수정, Project Instructions/Sources **실제 UI 적용**, 공식 Work OS M0/Shared State·MAIN/WORK 주도권 변경 **하지 않음**. 기존 주 제품 개발 채팅이 일반 개발·SimC 시험을 소유. M0 미통과 자체는 일반 개발 중단 사유 아님.

## 6. 새 채팅 시작 프롬프트 — 첫 복원만, STOP

```text
SIMC SECONDARY OPTIMIZER를 GitHub에서 읽기 전용으로 독립 복원하라.

repo=degong2-code/simc-secondary-optimizer-runner
isolation=probe/chat-cache-v035-20261024
single handoff=docs/CHAT_CONTINUITY_HANDOFF_20261105_P3_EV_ENGINE_INSTALL_RESTORE.md

먼저 격리 브랜치와 main의 실제 HEAD를 각각 독립 조회하고, 최신 코드 기준 SHA·실제 Actions/Native 영수증 및 적용 범위를 검증한다.
읽기 순서: P3-EV 인계 → docs/development/PROTOCOL.md → 기능 라이브러리 docs/development/INDEX.md의 E3/E2/E1(필요 시 B3/C4/D1/D2) → CURRENT 최상단·개발자 실행 노트 → P3-EU/ET/EV 노트 → 실제 v216/v212/v222/v220/v196/v217 코드·봉인 원본·영수증. 오래된 P3 전체를 다시 읽거나 재검증하지 마라.

최종 목적은 특정 시즌 G/J/F/O 수치의 확정이 아니라 26 DPS 공통, 다음 시즌에도 재사용되는 한 개의 환경 자동 구축 및 DPS 최적화 엔진 완성이다. 현재 개발 Gate는 정상 단일 웹앱 v216의 시즌 대표 장비·티어/G/J/F/O 자동 검증 → 기존 v222 공식 B/T → v220/v196 검증 최고품질 선택지 실제 발행 → v212/v217 환경 설치 READY/T1. 현재 시즌을 신규 시즌처럼 cold-start 실행하는 시험은 엔진 완료 검증이고, 이전 시즌 값의 하드코딩이나 기존 환경 입력으로 READY를 가장하면 안 된다. 특수 보석은 정확히 1개 필수이며 모든 열린 소켓에 일반/특수 보석이 가능하다. v098→v096/v094 DPS는 환경 READY 이후다.

최근 P3-EU는 검증 입력에 대한 v212 설치·v217 봉인/재개 및 v216 내부 provider 호출 경로를 합성 회귀로 구현했다. 실제 신규 시즌 G/J/F/O·정책 A 증거를 제공하는 내부 source-owner provider와 단일 웹앱 실제 T1은 미완료다. 'verified' 문자열/임의 JSON과 합성 PASS를 실제 인증이라고 판단하지 마라. Evidence와 Integration을 분리하고 기존 구현/영수증/캐시를 반드시 선조회한 뒤 REUSE/CONNECT/EXTEND/NEW/STOP으로 다음 최소 작업을 제안하라. 독립 작업은 논리적으로 묶고 동일 기준의 기존 PASS·Native/캐시를 재사용하라. 매 작업 '이 작업이 다음 시즌에도 동일하게 작동하는 엔진 완성에 기여하는가?'를 점검하고 Native/HTTP/Actions 중복·메모리/I/O·실행시간·복잡화를 평가하라.

첫 답변은 실제 HEAD/제품 코드·최신 검증의 정확한 범위, 최종 목표와 장단기 로드맵, Evidence vs Integration별 완료/미완료, 현재 병목과 효율적 대안, 미반영·권한 제한만 간결히 보고하고 즉시 STOP하라.

사용자가 명시적으로 '진행'이라고 하기 전에는 개발·코드/문서 수정·GitHub commit/push·신규 수집·테스트/CI/Actions/Native 실행·Project UI/공식 승격을 절대 시작하지 마라.
```
