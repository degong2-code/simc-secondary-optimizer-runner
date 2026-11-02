# SIMC SECONDARY OPTIMIZER — P3-BF → 시즌 G/J/F/O 엔진 연속 개발 인계 정본

**기준일:** 2026-11-03 KST. **역할:** 새 채팅 단일 최신 복원 문서. 프로젝트를 새로 시작하거나 이전 원본·Native·CI를 전수 재감사하지 않는다.

**저장소/격리 브랜치:** `degong2-code/simc-secondary-optimizer-runner` / `probe/chat-cache-v035-20261024`.
**인계 작성 직전 실제 HEAD:** `66139475dced763b08252ba68730d7ec0d3d58b5`, **main:** `07133e0aaf738d6e4816a6486057b1cd49c018de`.
**마지막 P3-BF 기능·시험 코드 기준:** `7f007b4c62e664aefd3c2070de7dd09809774bca`, 핵심 v106 수정 `422783d3df0ec402ee2aaca3c8500c66d3cf9fe3`. 문서 커밋 후 HEAD는 변경되므로 새 채팅에서 반드시 실제 브랜치 HEAD를 재조회한다. 기능 SHA와 문서 HEAD를 혼동하지 않는다.

> **첫 응답 규칙:** 읽기/복원/검증 보고만 수행하고 즉시 중단. 사용자 **“진행”** 전 코드 수정·커밋·Actions 실행·Native·신규 외부 원본 수집 금지.

## 1. 최신 사용자 승인 계약과 제품 목표

장기 목표는 **새 시즌마다 필요한 기능·원본·선택지를 자동 발견·구축·갱신하는 하나의 범용 Environment DB Build 엔진**이다. 한 시즌의 아이템을 수동 등록하거나 티어 이름 웹검색, 별도 SimC-only 엔진, 새 최적화 알고리즘을 만드는 일이 아니다. 모든 변경에서 **“다음 시즌에도 같은 계약·수집기·검증기가 재사용되는가?”**를 자가점검한다.

지원: **26 DPS 전문화만**; 증강 기원사·탱커·힐러 제외. 목표 ilvl 기본 **334** 또는 사용자의 직접 입력 최종 CHMV **T**에서 SimC DPS 최대의 치명·가속·특화·유연 **절대 rating**을 찾는다. 관측 1순위, DPS·SEM·**95% 판정만**, 실질적으로 다른 근접 대안·비율, 캐시·취소·재개를 제공하며 전역 최적이 입증되지 않았으면 명시한다. 현재 착용 장비 재분배·장비 조합/획득 경로·전체 시즌 장비 DB는 제외. 일반 사용자는 클래스/전문화/종족/특성, 목표 ilvl/T, 장신구2, 선택 특수장비, 장식 최대2, 소모품·기름·전투조건을 입력; 일반장비·무기·티어4pc·SimC 프로필은 내부 생성. 업로드한 현재 SimC 장비를 목표 예산으로 복사 금지.

**회계:** `G` 대표 비장신구·무기 예산, `J` 보석, `F` 최고 품질 영약, `O` 실제 적용 가능한 무기 기름의 고정 비자유분배 rating. **`B=G+J+F; T=B+O; c_final=c_base+o`**. 수동 T가 최우선이며 `B=T-O`로 환산. `L`(선택 특수장비)은 G에 이미 포함된 스탯별 하한으로 재가산 금지, `E`(영구 정적 마부)는 승인된 예산 내에서만 한 번 반영, 기름 O도 gear_*에 한 번만 반영. 장신구 고정 스탯은 자유 G 밖이고 미관측≠0; 제작 초기 50:50은 L이 아니다. 과거 v089 79×2 B, J=138, F=165, 무기당 치명16/가속16은 **새 시즌의 증명값이 아니다**. exact Native G는 선택적 정밀 경로로, 전 전문화·전 ilvl Native 전수 실행 금지.

정책 A: 정확한 ID·출처·시즌·입력·CHMV 귀속·적용 조건 검증 후 자동 사용자 등록. 품질 단계는 동일 효과/사용조건/범위가 입증되고 높은 품질이 모든 수치에서 열등하지 않을 때만 최고 품질로 병합. 영구 마부 수집 대상, 일반 임시 마부 제외, 무기 기름 별도 지원. Omnium 등 시즌별 특수 시스템은 ON/OFF 선택 모듈이고 GPT 영구 런타임 의존성 금지. SimC가 효과/proc/APL/DPS를 계산하며 **독립 효과 인증 Gate/효과 재구현 금지**.

**최신 2026-11-03 사용자 직접 결정:** 같은 시즌의 잦은 SimC balance/APL 업데이트는 원칙적으로 정적 환경 변경이 아니다. 기존 장비·티어·G/J/F/O·동일 시즌 정적 아이템 캐시 유지, 실제 바이너리 SHA·revision·프로필/APL·전투조건·iterations에 따른 **DPS 캐시만 분리**. 기존 `v151/v258` 메타데이터 기반 짧은 변경 확인을 활용하고 전수 Wago/SimC item_data 재수집·26 DPS Native 반복 금지. 빌드가 달라졌다는 이유만으로 동일 시즌 DB 폐기 금지. `cold_start`는 과거 게임 빌드가 없다는 뜻이 아니라 **프로그램에 이전 빌드 기록이 없는 수집 상태**다. 시즌 판단은 클라이언트/Blizzard API의 구조화 시즌 정보와 기존 v155/v242, WCL 보조 교차검증을 사용하고 자유 웹검색을 제품 판정 로직으로 쓰지 않는다.

**완료 Gate:** 필수 G/J/F/O의 동일 시즌 정합성·B/T·L/E/O·대표 프로필/실제 SimC 입력 증거가 없으면 ready/설치/최적화 시작 승인 금지. 선택 옵션 미검증 시 해당 옵션만 보류. 최종 제로기존자료 시험은 **일반 사용자의 단일 Build 엔진 그대로** 사용하되 과거 수집 자료·영수증·ID seed·캐시·정답은 차단하고 Wago/Blizzard/WCL/SimC 등의 **정상 신규 외부 다운로드는 허용**; 출력 봉인 뒤 독립 비교한다.

## 2. 필독 순서와 파일 경로

1. **이 문서 전체** → `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 최상단 P3-BF/P3-BE/P3-BC/P3-BA/P3-AZ 항목과 원격 HEAD. CURRENT의 구형 상단 포인터는 역사 스냅샷일 수 있다.
2. 승인 기준: `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md` → `docs/DPS26_SCOPE_CORRECTION_20261031.md` → `docs/P3_AA_20261102_SINGLE_ENGINE_FRESH_SEASON_CONTROL_ACCEPTANCE.md` → `docs/DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md` → `docs/P3_ENVIRONMENT_BUILDER_TARGET_ARCHITECTURE_20261031.md`. 오래된 20261029 v1.4.1은 27 DPS/증강 포함을 적어 현재 범위에서 **폐기**되었다.
3. 실제 최근 개발: `docs/P3_BF_20261103_ENV_BUILD_SESSION_SIMC_REVISION_BRIDGE.md` → `docs/P3_BE_20261103_STATIC_SOURCE_VS_EXECUTING_SIMC_REVISION.md` → `docs/P3_BC_20261103_SAME_SEASON_SIMC_REFRESH_STATIC_ENV_REUSE.md` → `docs/P3_BB_20261103_ACTIVE_SEASON_SOURCE_AND_NO_PRIOR_BUILD_GATE.md` → `docs/P3_BA_20261103_REAL_WAGO_SIMC_ONE_SPEC_SOURCE_COVERAGE.md` → `docs/P3_AZ_20261103_PREVIOUS_BUILD_HISTORY_AND_REAL_SIMC_SOURCE.md`. 이전 단계 원본/교차검증의 상세 근거는 `docs/CHAT_CONTINUITY_HANDOFF_20261102_P3_AT_SIMC_TO_GJFO_ENGINE_NEXT.md`.
4. 현재 코드: `runner/v113_local_web_api.py` → `runner/v106_user_session_controller.py` → `runner/v216_environment_build_coordinator.py` → `runner/v217_stage_execution_engine.py` → `runner/v212_environment_manifest.py`. 필요한 연결부만 추가로 `v155/v242` 시즌, `v161/v163/v165/v166/v167/v169/v245/v250/v251/v229/v231/v232` 원본/대표 장비, `v151/v258` 경량 변경검사, `v221/v222/v223/v224/v225/v226/v227/v228` 예산, `v190/v191/v211/v213/v196` 카탈로그, `v098/v093/v094/v095` 기존 적응형 SimC 읽기.
5. GitHub Actions는 **run → jobs → job log**로 확인. 성공·실패·역사 Native·실원본·합성 CI 각각의 적용 범위를 `4대로 구별한다.

**규범 우선권:** 최신 사용자 직접 결정 > 최신 승인 설계 정책 > GitHub 실제 코드/CURRENT/Actions·Native 영수증 > 과거 인계/역사 문서.

## 3. 실제 구현 완료 vs 미완료

**P3-AT~P3-BA:** 하나의 정상 `v113→v216` Build에서 Wago·Blizzard/WCL·정확한 DB2 티어 13직업×5부위 원본→SimC 소스/선택적 전체 item_data→징벌 성기사 13부위 후보 등 물리 교차검증과 v217 SHA receipt 재사용 구현·증명. **티어 이름 선검색은 정상 경로가 아니다.** Wago 전체 빌드 DB에는 구시즌 아이템도 함께 있으므로 시즌 소속은 별도 증명; 옛 PvP 장비를 새 대표 후보로 끌어오지 않는다.

**P3-AZ/BB:** 실제 시즌 이벤트와 프로그램이 보유한 과거 빌드 기록을 분리. 이전 기록이 없거나 시즌 변경 시 클라이언트 빌드가 같더라도 소스 단계 진입 가능; 실제 원본 내부 build/blob 정합성 유지.

**P3-BC/BD/BE:** 같은 시즌 정적 환경·G/J/F/O는 SimC balance-only nightly마다 자동 무효화하지 않는다. `v258`은 소수 Git metadata로 변경 영향 advisory(전체 SimC/게임 효과 의미 동등성 입증 아님). v212는 정적 v213 소스 revision과 실제 v098 실행 revision/binary SHA를 구분. Native 정확 변형 캐시의 기존 HIT 영수증은 역사 source revision 허용, 신규 Native MISS는 실제 실행 revision 필요.

**최신 P3-BF:** v212 교정만으로는 사용자 정상 진입점 `v106.source_catalog_identity`가 `source_revision==runtime_revision`을 강제해 실제 계획 실패. v106을 교정하여 v213 원본 schema/SHA/기록을 보존하며 runtime revision·binary SHA는 세션/DPS 캐시 정체성으로 분리. 실제 v216 이전/새 세션의 동일 source/gear/tier/budget/static-cache 바이트 보존과 다른 DPS identity, v113 loopback API 계획 회귀 PASS. **실제 새 SimC Native 실행한 것은 아니다.**

**핵심 미구현/미승격:** 새 시즌 **G/J/F/O 전체 자동 소스/수치·품질 검증** → v222 **B/T·L/E/O 정합** → **정책 A** 최고품질 자동 사용자 옵션 발행 → v212 설치 및 대표 SimC 프로필 → 진짜 새 SimC 바이너리 기반 adaptive DPS/SEM/95%·캐시/취소·재개 E2E → 같은 엔진의 제로기존자료 수용 시험. 신규 시즌 G 미확정 시 G를 오래된 수치로 채워 READY 표기 금지.

## 4. 실제 영수증 (2026-11-03 GitHub API로 재확인)

| 실행 | 결과 및 입증 경계 |
|---|---|
| [v212 #41538567324](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41538567324) | Ubuntu/Windows **각 409 tests / 0 FAIL / 4 SKIP**, SUCCESS, Native0. 합성 v106→v216→v212 source/runtime 세션 분리, 신규 SimC 물리/DPS Native 아님 |
| [v113 #41538766459](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41538766459) | Ubuntu/Windows **각 194 tests**, SUCCESS. loopback ASGI 실제 HTTP 계획이지만 SimC Native 아님 |
| [v181 #41538766461](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41538766461) | Windows Python3.12/3.14 **각 139 tests**, SUCCESS. 패키징/로컬 계획 |
| [v182 #41538766716](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41538766716) | Ubuntu/Windows focused **각 2 tests**, SUCCESS. 사용자 UI 일부 |
| [초기 실패 #41538243862](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41538243862) | Ubuntu/Windows FAIL: `V106_V213_SOURCE_CATALOG_SESSION_IDENTITY_MISMATCH`; P3-BF로 수정, 실패 이력 보존 |
| [P3-BE #41486152811](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41486152811) | 이전 v212 단계 각 408 tests/4 SKIP, SUCCESS. v106 해결 전 범위 |
| [P3-BA Wago×SimC #41479710886](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41479710886) | **실원본** Wago Item 9,103,685B, ItemSparse 51,691,672B, ItemXItemEffect 1,175,163B; 328/328 원본 일반 아이템 물리 대조, 징벌 13부위 source 후보. 활성 시즌·정확 G 승인 아님 |
| [P3-AZ 전체 SimC #41478919832](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41478919832) | **실원본** 정확한 SimC revision `710c2408bfd3ae4df71b8cd55cdf01f63fd6c926`의 item_data.inc 26,439,588B Git blob; 티어5/SimC-only 13부위. 신규 Native0 |
| [티어 ID #41455991413](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41455991413) | **실원본** Wago×SimC 13직업×5 실제 티어 ID. 전체 환경 시즌 승인 아님 |
| [26 DPS Native #40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357) | **역사 실제 Native** 26개 physical profile smoke, 26개 adaptive 최적화 E2E 아님 |
| [G=2847 Native #41396545012](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41396545012) | **역사 실제 측정** 값이지만 구 PvP 대표장비 혼합: `FAIL_ACTIVE_SEASON_REPRESENTATIVE_AUTHENTICATION`, 새 시즌 유효 G 사용 금지 |

**Run별 코드 신분:** v212 #41538567324의 테스트 대상 HEAD는 `743f3d3d4fce4d2146a962ce204ae891d4494415`, 이후 v113/v181/v182 #41538766459/#41538766461/#41538766716은 `7f007b4c62e664aefd3c2070de7dd09809774bca`를 대상으로 했다. 모든 PASS를 최종 문서 HEAD에 대한 독립 재실행으로 오해하지 않는다. 본 인계 작성 중 **새 Native 0, 신규 원본 HTTP 0, Actions 신규 실행 0**. P3-BF 기능·테스트 결과는 각 당시 source/runtime SHA에 한정. 새 버전 실제 Windows SimC 물리·적응형 DPS 시험 미완료.

## 5. 우선 로드맵과 효율적인 실제 다음 작업

**단기 1 — 핵심 G/J/F/O 수직 통합:** 현 정상 `v216`의 입력과 `v221/v222/v223/v224/v225/v226/v227/v228` 계약을 비교하여 어떤 원본/고정치가 아직 수동·구시즌 참조로 남아 있는지 먼저 특정. 재수집보다는 **같은 시즌 이미 검증된 대표 일반장비/무기·티어**를 한 전문화/ilvl334의 실제 G/정확한 유효 시즌 참조에 연결하고, 독립된 최고품질 보석 J·영약 F·기름 O·영구마부 E의 정확한 ID·품질·효과/고정 스탯을 병행해 조사. 새 시즌에서는 G까지 모두 새로 증명. **기존 v222 재사용**; 사용자 수동 최종 T 우선. Native는 새로 필요해진 정확 변형만 최소 호출. 출처 미확정은 항목별 PENDING.

**단기 2 — 제품 연결:** 검증된 기본 예산·선택지에 대해서만 v191/v213/v196의 정책 A 발행·v212 환경 설치·내부 대표 SimC 프로필 통합. 95% 통계와 적응형 후보 생성기는 그대로 재사용.

**중기:** 실제 새 SimC 바이너리 1개·전문화 1개로 Windows Native와 adaptive DPS의 재사용/캐시 분리·SEM/95%·취소·재개 E2E 검증, 그 뒤 26 DPS 지원 확대. 최종 P3-AA 빈 기존자료 통제실험은 **하나의 정상 Build** 완성 후 실시; 신규 외부 수집 허용, 이전 캐시/정답 차단.

**장기:** 신규 시즌마다 사용자가 버튼 하나로 환경 DB를 발견/갱신/검증하고 기존 최적화에 연결하는 **범용 엔진의 반복적 재현성**.

**매 변경 평가:** 독립 작업은 묶어 호출 수를 줄이되 **원본 출처→G/J/F/O 검증→B/T→옵션 발행→설치/SimC 실행** 완료/실패 경계를 따로 증빙. 같은 검증 기준·기존 receipt/Native·CI 재사용, 중복 HTTP/Native·캐시·메모리·I/O·총 실행시간·구조 단순화 확인. 너무 작은 SEM 보정/새 효과 인증 Gate/전수 Native보다 누락된 핵심 연결 우선.

## 6. 권한과 적용되지 않은 사항

- **허용:** 기존 주 제품 개발 채팅이 소유한 격리 브랜치에서의 후속 구현/시험(사용자의 “진행” 후).
- **별도 사용자 지시:** GitHub main 병합, immutable v003, 원본 v016 공식 통합/변경, ChatGPT Project UI Sources/Instructions의 실제 변경, 공식 Work OS M0/Shared State/MAIN·WORK 주도권 이전. WEQUIP runtime authority 도입 금지.
- 승인 v1.4.3 정책 본문은 이번 인계로 변경하지 않음. GitHub 문서 변경은 Project UI 등록 증거가 아님. 옛 v1.4.1 20261029의 27 DPS/증강 포함 폐기.
- **미승격:** 새 시즌 G/J/F/O 및 B/T 자동 승인, 정책 A 전체 옵션/설치, 실제 updated-SimC Native/DPS E2E, 26 DPS adaptive 전체, 제로기존자료 최종 Acceptance. 과거 원본 v016 최신 사용자 보고 상태와 공식 통합 상태는 구분.

## 7. 새 채팅 시작 프롬프트 (전문 복사)

~~~text
기존 SIMC SECONDARY OPTIMIZER 개발을 이어받아라. 새 프로젝트를 시작하거나 이미 검증된 코드·원본·캐시·Native·Actions를 전수 반복하지 마라.

GitHub degong2-code/simc-secondary-optimizer-runner 의 격리 브랜치 probe/chat-cache-v035-20261024 에서 다음 단일 최신 인계 정본 전체를 먼저 읽어라:
docs/CHAT_CONTINUITY_HANDOFF_20261103_P3_BF_ENGINE_GJFO_NEXT.md

인계에 정해진 순서로 CURRENT 최상단, 승인 v1.4.3, DPS26 교정, P3-AA 단일 Build 통제실험, 개발자 실행 노트, P3-BF/BE/BC/BA 실제 코드/영수증을 대조해라. GitHub 최신 HEAD·main·실제 Actions jobs/logs를 확인하고 기능 코드와 문서 HEAD, 합성 CI·실제 원본·실제 Native·역사 증거·미구현/미승격을 엄격히 분리해라.

이 프로젝트의 최종 목표는 기능 하나씩 만드는 것이 아니라 다음 시즌에도 필요한 기능과 환경 원본·아이템 선택지를 자동 발견·구축·갱신하는 하나의 범용 Environment DB 구축 엔진이다. 이 목표를 매 작업 자가점검해라. 정상 제품 한 개의 v113→v216 Build가 시즌·대표 일반장비/무기/티어→G/J/F/O→B/T→최고 품질 정책 A→v212 설치·프로필→기존 적응형 SimC DPS/SEM/95%·근접 대안·캐시/취소/재개에 연결되도록 개발한다.

26개 DPS(증강/탱커/힐러 제외), 목표 ilvl 기본334 또는 수동 최종 T 우선, B=G+J+F 및 T=B+O, SimC 자체 효과/proc/APL/DPS 책임, 장비 추천/현재 장비 재분배 금지. 이미 P3-BF에서 같은 시즌 기존 정적 원본과 자주 바뀌는 실행 SimC revision/바이너리 SHA·DPS 세션을 분리했으므로 그 작업을 반복하지 마라. SimC 업데이트만으로 과거 동일 시즌 정적 DB를 폐기하거나 Wago 전체/26전문화 Native를 재수집하지 마라. 기존 v151/v258의 경량 변경 영향 검사 및 영수증을 재사용하라. 과거 티어 이름 선검색/PvP 대표장비/새 시즌에 옛 J/F/O/G 수치를 복사하는 방식으로 회귀하지 마라.

독립 작업은 효율적으로 묶되 검증 경계를 분리하고, 동일 기준의 완료 검증·기존 CI/Native/cache 영수증을 재사용해라. 코드 변경마다 Native/HTTP 중복, cache, memory, I/O, 시간 및 구조 단순화를 점검하고 근거 없는 완료 선언을 하지 마라.

**이번 첫 응답은 반드시 복원·검증만 수행하라.** GitHub HEAD와 main, 유효 승인 기준, P3-BF까지의 완료·미완료, Actions/실원본/Native 증거의 범위, 핵심 장애, 장·단기 로드맵, 효율적 다음 구현과 권한 제한을 보고한 후 **즉시 중단하고 나의 “진행”을 기다려라.** 첫 응답에서는 코드 수정·commit·Actions·Native·신규 원본 HTTP 수집을 하지 마라. 사용자 별도 지시 없이 main, v003 immutable, 원본 v016, Project UI, 공식 Work OS/Shared State는 변경하지 마라.
~~~

**END — P3-BF 인계 정본. 첫 응답은 복원 보고 후 즉시 중단.**
