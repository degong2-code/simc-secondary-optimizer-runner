# SIMC SECONDARY OPTIMIZER — P3-HAL 단일 최신 채팅 인계 (2026-11-09 KST)

**지위:** 격리 브랜치의 최신 코드·승인 정책·실제 증거를 대조한 새 채팅 복원 정본. [P3-HAI 제품 판정표](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md)를 단일 제품 기능별 상태표로 **재사용**하고, 기능별 원본과 과거 인계는 원시 증거/시점별 이력으로 보존한다. 이 문서가 `main`, v003 immutable, 사용자 원본 v016, ChatGPT Project Sources/Instructions UI, 공식 Work OS를 갱신하거나 승인·승격하지 않는다.

## 1. 독립 복원 순서 및 기준 HEAD

- GitHub repo `degong2-code/simc-secondary-optimizer-runner`; 격리 `probe/chat-cache-v035-20261024`. **인계 작성 직전 독립 실제 HEAD** 격리 `63589d20d32aa7ed053c8ddf50fd686ea0d53bb4` (P3-HAK), `main=07133e0aaf738d6e4816a6486057b1cd49c018de`. **이 문서 커밋 후 격리 HEAD가 변경되므로** 새 채팅은 두 refs를 다시 독립 조회하고 신규 커밋과 diff/Actions를 확인할 것.
- 읽기: **① 두 실제 HEAD → ② 본 P3-HAL → ③ [P3-HAI 단일 상태표](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md) 최신 상단·기능 A~G → ④ [PROTOCOL](development/PROTOCOL.md) 최신 상단 / [INDEX](development/INDEX.md) A~G·기능별 원본 / [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) 최신 상단 → ⑤ [승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md)·비충돌 v1.4.2/최신 사용자 직접 결정·[개발 실행 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md) → ⑥ 다음 표의 필요한 코드와 정확한 Actions/Native JSON2/receipt SHA만 선택 확인**. 전체 역사 문서 재감사/전수 Native 금지.
- 우선순위: **최신 사용자 직접 결정 > 최신 승인 설계 정책 > GitHub 실제 코드·CURRENT·Actions/Native 영수증 > 과거 시점 문서**. 과거 P3-HAC/HM의 “>6 Native 미실행”과 P3-HAI 최초 본문 “웹 아직 시도 안 함”은 **그 날짜의 역사 상태**. 2026-11-09 P3-HAJ는 **실 HTTP 시도 후 422 차단**, P3-HAK은 **source-runtime revision 분리 회귀 PASS**.

## 2. 최종 제품 목표·재사용 가능한 엔진 기준

- **개별 기능 개발이 아닌 매 시즌 재사용 가능한 하나의 최적화 제품 엔진 완성**. 26개 딜러 전문화만(증강 기원사/탱커/힐러 제외), 미래 목표 ilvl 기본334 또는 사용자 수동 **기름 포함 최종 T**에서 **SimC DPS 최대화 목표 CHMV 치명·가속·특화·유연 절대 rating**을 찾는다. 현 장비 재분배기·장비 추천/획득 경로·시즌 전수 장비 DB 아님.
- 일반 사용자 입력: 직업/전문화/종족/특성, 목표 ilvl 또는 수동 최종 T, 장신구2, 선택 특수장비, 장식 최대2, 검증된 보석/영약/소모품/기름·전투조건/선택 시즌 모듈. 일반 장비·무기·티어4·주능력치·SimC 대표 프로필은 **내부 구성**. 선택 업로드 프로필은 주로 캐릭터/특성 용도.
- 시즌 환경 구축 A~D를 다시 새 엔진으로 만들지 않는다. G 대표 비장신구·무기, J 일반 보석, F 영약, O 기름 고정: **B=G+J+F, T=B+O, c_final=c_base+o**. 수동 T 우선, L/E는 적합 예산 내 고정 하한으로 중복가산 금지; 장신구 정적 수치는 자유 G 밖, 제작 50:50 잠금 아님. 최종 각 `c_final[s] < T/2`, 정수 상한 `(T-1)//2`. 특수보석1+일반보석4(각 일반 스탯 방향 하나씩), 필요한 다른 소켓은 시즌 계약대로. 최상품질 동일효과 항목만 사용자에게 노출. **SimC가 proc·효과·APL·DPS 계산 담당**, 독자 효과 인증 Gate/새 스킬 로테이션 엔진 금지.
- 예상 DPS, SEM, **95% 판정만**, 관측 1순위·실질적으로 다른 근접 대안·절대 rating/비율 표시. 선택된 확인 쌍의 명목 95%와 **다중 비교 보정/전역 최적 증명은 다르다**.

## 3. 가장 최근 SimC/게임 빌드 정책 — P3-HAK 반드시 재사용

[정본 근거 P3-AZ](P3_AZ_20261103_PREVIOUS_BUILD_HISTORY_AND_REAL_SIMC_SOURCE.md) · [P3-BB](P3_BB_20261103_ACTIVE_SEASON_SOURCE_AND_NO_PRIOR_BUILD_GATE.md) · [P3-BC](P3_BC_20261103_SAME_SEASON_SIMC_REFRESH_STATIC_ENV_REUSE.md) · [P3-BE](P3_BE_20261103_STATIC_SOURCE_VS_EXECUTING_SIMC_REVISION.md) · [P3-BF](P3_BF_20261103_ENV_BUILD_SESSION_SIMC_REVISION_BRIDGE.md) · [P3-FX](development/notes/2026-11-06_p3-fx-same-season-static-versus-simc-runtime.md) · [최신 P3-HAK](development/notes/2026-11-09_p3-hak-simc-build-identity-and-fresh-source.md).

**서로 다른 네 identity: (1) WoW 클라이언트 빌드/시즌 식별, (2) 검증된 시즌 정적 source/아이템/대표장비·G/J/F/O, (3) 원본 pinned SimC source revision 및 파일/SHA, (4) 현재 실행되는 SimC 바이너리 SHA·revision/APL/전투/iterations와 DPS 캐시.** 같은 시즌의 게임 빌드 번호 또는 SimC nightly 리비전 변경 **그 자체만으로 정적 source를 폐기·재수집하거나 환경 전체를 차단하지 않는다**. 실제 시즌/선택 아이템/스탯 콘텐츠가 바뀌면 **영향 받은 부분만** 재검증한다. 새로운 raw Wago DB2/SimC 소스를 최초 결합할 때의 파일 내부 build·원본 SHA/provenance는 여전히 검증한다. **새 빌드 70575의 베타 배포 원본을 70783의 동일 입력이라고 이름만 바꿔서는 안 되지만**, 두 번호가 다르다는 사실만으로 기존 같은 시즌 정적 캐시가 모두 무효인 것도 아니다. 이전 로컬 빌드 기록 부재는 신규 시즌 진입을 차단하는 Gate가 아니다.

P3-HAK `v096` legacy `v216/v223` source revision vs 실제 실행 SimC revision 강제 동일성, `v098` fresh `v212` source/G revision vs 실행 revision 강제 동일성 오류 교정. `v106/v212`의 선행 분리·원본 source SHA/빌드 및 G/J/F/O 검증과 신규 바이너리별 **별도 DPS 캐시 identity** 유지. [focused #42537286821](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42537286821) **485 PASS/2 SKIP, Native0**, [v098 #42537286782](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42537286782) 379 PASS, [v113 #42537286817](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42537286817) Linux/Windows 각233 PASS. **실 다른 빌드 간 Native 범용 호환이나 현재 웹 E2E 성공을 증명한 것은 아니다**. 최신 HAK 문서 정리 후 [focused #42537553278](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42537553278) **485 PASS/2 SKIP, DEV_LEDGER_PASS/Native0**.

## 4. 기능·증거 상태와 재사용 범위 (세부는 단일 상태표)

| 영역 | 현재 증거/결론 | 잘못 승격하면 안 되는 주장 |
|---|---|---|
| 시즌 환경 엔진 `v161/v191/v211/v213/v229/v242→v216/v222/v212/v217` | 70783/334 Ret, **G2850 J92 F165 O0 B=T3107** 설치 READY, 환경 Native3 [#42460255527](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42460255527)·HAJ 재확인 | 모든 미래 시즌 자동 최초 데이터 수급·전문화를 실증 완료 |
| 26 DPS 표준 대표 프로필 `v143/v167/v169/v230/v232/v098` | 26/26 물리 SimC 수용 [#40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357), 별도 6 전문화×6후보 실 Native [#40980268952](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40980268952) | 26/26 장기 탐색 Native 최적해 증명 |
| 현재 사용자 adaptive `v098/v096/v094` | Ret·Enh 각 DPS Native6 [#42466284163](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42466284163)·[#42472633337](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42472633337) | 일반 웹 장기 Start/Cancel/Resume 실증 |
| v290/v291 장기 후보·정밀화 | [#42501052586](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42501052586) **8×35 +2×320 실제 DPS Native10**, 4+6 재개, 95% 확인 쌍 | 2000회 장기 Native/전역 최적/다중 선택 보정 95% 증명 |
| v292 교차 실행 캐시 | [#42504040076](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42504040076) **옛 DPS Native10건 재인증, 새 DPS Native0**(환경 Native3 별도), 원본 SHA | 새 SimC binary/다른 profile/무조건 다른 빌드 DPS 재사용 |
| v113/v106/v293 로컬 웹 | [#42506293553](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42506293553) Linux/Windows 각233 offline HTTP PASS, UI 준비/시작/취소/재개/cache-only/ZIP SHA import 코드 | 실제 웹 사용자 경로 DPS Native PASS |
| **HAJ 실제 웹 HTTP 시험** | [#42535096763](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42535096763) **v216 fresh 70783 G/J/F/O 설치 READY·환경 Native3**, 그러나 `/api/v1/longrun/prepare`가 **HTTP422 `V216_EXPLICIT_NEW_SEASON_BUILD_REQUIRED`**, **웹 DPS Native0**; [실패 영수증 #13638936573](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42535096763/artifacts/13638936573) | 빌드 불일치 실패 또는 성공한 웹 Start/Cancel/Resume |

**95% 사례 (과거 HAE 실측 재사용):** Enh ilvl334, O0 B=T3107에서 320 iteration 1순위 치1/가1552/특1553/유1 **185438.66 DPS ±280.54 SEM**, 상대 치1388/가165/특1553/유1 **182070.77±302.13 SEM**; DPS 차 3367.90 > 두 확인 후보의 명목 정규근사 95% 반폭 808.08; seed 서로 다름. **선택쌍 비교만**, 전역최적·가족단위 95% 아님. JSON2/receipt/원본 ZIP SHA [HAE inner `c53dc09015377ccaf3d53f24bb85950e3999efacecc629be756b9f8856ef5fa9`](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42501052586/artifacts/13625920302).

## 5. 두 핵심 미완료 축, 실제 병목 및 로드맵

**P1-WEB (단기 가장 우선):** 시즌 엔진 재개발이 아니라 **검증·설치된 fresh `v216/v217/v212` 원본/영수증 → `v113/v106` 사용자 웹 세션 → `v098/v096` 프로필 → `v293/v291` 장기 실행** 연결 어댑터가 빠짐. `v113._seal_environment_manifest`는 원본이 설치됐는데 fresh `v213` source를 일반 `v216.build_environment`로 재진입시켜 새-season-build 요구 422. **이 오류는 SimC 실행 revision mismatch 때문이 아님**. 기존 [HAJ 노트](development/notes/2026-11-09_p3-haj-real-local-web-native-e2e.md)·[HAK 노트](development/notes/2026-11-09_p3-hak-simc-build-identity-and-fresh-source.md), `v098.run_from_verified_environment_build` 실 사례, `v212` 설치 영수증을 재사용. 새 인증 Gate/시즌 크롤러/재구축 없이 `REUSE → CONNECT`; 먼저 **원본 source 설치→웹 plan/prepare Native0 계약 회귀**, 이어 기존 검증된 같은 시즌 조건에서 **최대 1개 세션/최소 Native의 실제 로컬 HTTP Start→Status→Resume/Cancel(관측 여부 구분)→cache-only→DPS/SEM/result**. **GitHub FastAPI TestClient+실 subprocess는 실제 사람의 Windows 브라우저 클릭이 아니다**. HTML 브라우저 UI/Windows 설치 실증은 별도.
  
**P2-OPT (단기 P1 이후):** 기존 `v290/v291`의 전역/국소 탐색 다양성·적응형 precision allocation·종료 판단을 **동일 SimC 바이너리/시나리오/CHMV·CPU-second/신규 Native calls/DPS·SEM**으로 비교. 이미 가진 8+2 측정·캐시·2후보 95% 범위부터 재사용; 개선을 위해 별도 신규 엔진을 만들거나 26 전문화 전수 Native를 수행하지 않는다. 다중후보 선택 불확실성은 보정 근거 전 확정 표시 금지.

**장기 로드맵:** 26 DPS 실제 이용 범위를 증분 확대하고, 새 시즌 전환 시 기존 G/J/F/O 환경·선택지·정적 캐시를 **엔진 그대로** 갱신·증거별 자동 등록하는 재사용성을 유지. 구 시즌 G/J/F/O 숫자를 새 시즌에 복사하지 않으며, 새 시즌 전체 자동 취득·사용자 Windows 설치·전역 수렴을 이미 완료했다고 주장하지 않는다. 실제 발견한 누락에 한해 부품별 수정/최소 Native로 확장.

**효율 대안:** 현 P1 장애 해결에 새 v216 Build/웹 실행기/옵션 DB를 개발하는 것은 중복. 기존 `v098`의 fresh-installed 허용 경로를 `v113` 소유의 session·문서 아답터로 연결하고 v106 단일 잠금/기존 v291 캐시 그대로 활용. 어떤 변경도 Native 횟수·중복 호출·메모리·I/O·시간/구조 단순화를 검토.

**P3-HAL 문서 통합 실제 검증:** [Actions #42538187430](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42538187430) **SUCCESS / DEV_LEDGER_PASS / 487 tests=485 PASS+2 SKIP/0 FAIL / 신규 Native0·네트워크0**. 이 범위는 인계 문서·정적/오프라인 회귀 확인이며 웹 Native E2E 성공·Project UI 반영을 뜻하지 않는다.

## 6. 작업·기록·권한·인계 지속성

- 매 작업 **INDEX 기능 A~G 및 개발 로그/코드/원본/실 Actions/Native 영수증을 먼저 조회**. `REUSE`, `CONNECT`, `EXTEND`, `NEW`, `STOP` 판정. 독립 작업을 묶어 처리하고 **동일한 테스트/Native 완료 판정·이미 확보한 영수증 재사용**. 변경하지 않은 부분을 재실행하지 않는다. 결과는 `IMPLEMENTED / OFFLINE_PASS / REAL_NATIVE_PASS / HISTORICAL_REUSED / BLOCKED / NOT_TESTED`로 분리.
- 변경 시 해당 코드/기능 문서/[CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md)/[INDEX](development/INDEX.md)/[PROTOCOL](development/PROTOCOL.md)/[개발자 실행 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md)를 함께 갱신하고 실제 Actions 상태·영수증 범위 기록. 승인 v1.4.3/v1.4.2 원문은 권한 없이 수정하지 않는다. [P3-HAL 작업 기록](development/notes/2026-11-09_p3-hal-handoff-evidence-reconciliation.md).
- 격리 브랜치 작업만 허용. `main` 병합, v003 immutable, 원본 v016 제품, 공식 Project Sources/Instructions UI 적용, Work OS M0/Shared State/공식 승격은 **별도 사용자 권한·실제 적용 확인**. 현 주 제품 개발 채팅의 제품 소유권 이전을 이 인계 문서만으로 추정 금지. WEQUIP 운영 authority/영구 런타임 의존성 금지.
- **적용 상태:** 이번 인계는 GitHub 문서 갱신 및 해당 범위 오프라인 CI만 대상. 새 기능 코드·실 Native·제품 UI·Project UI·main 변경을 인계 완료라고 주장하지 않는다. 갱신하지 않은 역사 문서(HAI/HAC 등)는 당시 상태의 자료로 남는다.

## 7. 새 채팅 시작 프롬프트 — 그대로 복사

> SIMC SECONDARY OPTIMIZER 프로젝트를 **읽기 전용으로 독립 복원**하라. GitHub 저장소 `degong2-code/simc-secondary-optimizer-runner`, 격리 `probe/chat-cache-v035-20261024`, **최신 단일 인계** `docs/CHAT_CONTINUITY_HANDOFF_20261109_P3_HAL_REUSABLE_ENGINE_WEB_BUILD_RESTORE.md`. **먼저 격리 브랜치와 `main`의 실제 HEAD를 각각 독립 조회**하고 인계 작성 직전 HEAD, 최신 커밋, Actions/Native 영수증과 비교하라. 읽기 순서는 P3-HAL → `docs/PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md`(최신 보충 포함) → `docs/development/PROTOCOL.md` 상단 → `docs/development/INDEX.md` 기능 A~G → `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 상단 → 승인 v1.4.3·비충돌 v1.4 계열/최신 직접 결정 → P3-HAJ/HAK 및 실제 관련 코드/영수증만 확인한다. **최종 목표는 독립 기능의 축적이 아니라 26 DPS를 위한 다음 시즌에도 재사용 가능한 시즌 환경·대표 프로필·CHMV 탐색·SimC DPS·캐시·취소/재개를 연결한 단일 '엔진' 완성**이다. 매 작업 시작 전 기존 개발기록/기능 인덱스/코드/원본/Actions·Native 영수증·캐시를 선조회해 `REUSE/CONNECT/EXTEND/NEW/STOP`를 정하라. 독립 작업은 묶어 처리하고 **동일 기준의 완료 검증과 기존 영수증을 재사용**하며 중복 개발·Native·전문화를 전수 재시험하지 말 것. 실제 완료/오프라인 PASS/실 Native PASS/역사 재사용/미검증/차단을 구분하고 SimC 효과 메커니즘을 재구현하지 않는다. **게임 클라이언트 빌드나 실행 SimC revision 차이만으로 같은 시즌 정적 캐시·G/J/F/O를 자동 차단하지 않는다**. 원본 신규 raw-source 내부 build/SHA/provenance는 별도 검증; 신규 실행 DPS 캐시는 바이너리 SHA별로 구분한다. 현재 P3-HAJ 실 70783 환경 READY Native3 성공 후 `v113 /longrun/prepare` HTTP422(`V216_EXPLICIT_NEW_SEASON_BUILD_REQUIRED`)로 웹 DPS Native0; 이는 **v216 설치원본→v113/v106→v098/v096** 어댑터 누락이며 **SimC 빌드 불일치 실패가 아님**. 남은 두 축은 **P1-WEB 설치증거 전달·실 로컬 사용자 E2E**, **P2-OPT 기존 v290/v291의 CPU/Native 대비 탐색 품질·종료 판단 고도화**. 시즌 G/J/F/O 엔진 새로 만들지 말 것. 먼저 **현재 HEAD, 승인 정책, 완료/미완료·원본 증거, 병목·더 효율적인 대안, 간결한 장·단기 로드맵**을 독립 검증해 보고한 후 **반드시 중단**. 내가 별도로 **'진행'**이라고 하기 전에는 **코드/문서 수정, 테스트/Actions/Native/수집, 커밋·병합·Project UI/Work OS 승격** 등 어떤 개발·실행도 시작하지 말 것. 제품 주도권/격리 브랜치/ `main` 및 원본 불변 자료에 관한 권한을 보존한다.
