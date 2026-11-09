> **2026-11-10 실 P1 일반보석 4종 최초 실환경 Build 성공 (역사 P3-HAV 인계 당시 미실증 교정):** [단일 실제 증거·실험 범위](development/notes/2026-11-10_p1-four-ordinary-real-zero-history-ready.md), [Actions #42664089225](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42664089225) PASS. 새 빈 임시 작업 공간/리테일 12.1.5.70783에서 **원래 v113→v216→v212 → 검증 사용자 프로필** READY, Ret334 G2850 J92 F165 O0 B=T3107, 일반 치명/가속/특화/유연 각1·special 없음, 신규 환경 Native3/원본 missing0/최종 requires0. 미래 새 시즌·네보석 실 DPS·실 개인 Windows GUI까지 검증했다고 주장하지 않는다. **환경 엔진 핵심 구현과 현재 라이브 기본 cold-start 실증 확보**, 새로운 결함/정책 변경 없이 환경 대형 개발 반복 금지; 기존 P2 최적화 품질 개선으로 복귀 가능한 상태. 아래 작성 시점의 과거 '4보석 실환경 미실증' 표기는 본 최신 영수증 우선. main/v003/Project UI/Work OS/주 제품 개발 소유권 변경 없음.

> **2026-11-10 최신 사용자 결정/판정 보충 (기존 P3-HAV 인계 본문은 작성 당시 기록):** 새 채팅은 두 HEAD 독립 조회 후 **[단일 최신 A~G 구현/실증/결함/검증 공백 판정표](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md) 최상단 → [개발 착수 Gate](development/PROTOCOL.md) → [기능 인덱스](development/INDEX.md) → [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md)** 를 먼저 읽는다. 환경 구축 핵심 엔진 **이미 구현**, 검증만 안 된 새 시즌 정상 첫 Build를 **새 엔진 미구현으로 오판 금지**. 실제 필수 경계 최초 Build 한 건 통제 검증, 확인된 blocker만 최소 CONNECT/FIX, 완료하면 **P2 최적화 알고리즘 탐색 품질·효율 개선 복귀**. 최신 사용자 승인 우선이며 본문 기존 로드맵/옛 코드 SHA/미완료 문구보다 이 최신 판정 우선; 정책 v1.4.3, main/불변/Project UI/Work OS/기존 주 제품 개발 채팅 소유권 불변. 직전 격리 코드 17d9fce의 [#42652697431](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42652697431) 524 PASS/2 SKIP은 **offline**, 신규 시즌 실 Native E2E 증명 아님. 이번 보충은 문서 변경만, 실제 소스 수집·SimC 실행·제품 승격 0.

# SIMC SECONDARY OPTIMIZER — P3-HAV 단일 새 채팅 인계 정본 (2026-11-09 KST)

**지위:** 기존 P3-HAU를 교체하는 *최신 진입 포인터*이자 읽기 전용 독립 복원용 인계. 기존 승인 v1.4.3, 역사 인계·기능별 원본/영수증, `main`, v003 immutable, 원본 v016 및 Project UI/Work OS 권한을 변경하지 않는다. **이번 작업은 인계 문서만 갱신**하며 새 제품 코드, Native·실 DPS·원본 수집을 수행하지 않았다. 인계 푸시로 자동 오프라인 Actions가 발생할 수 있어 이것은 별도 상태로 확인한다.

## 1. 기준 HEAD·권한·읽기 순서

- GitHub `degong2-code/simc-secondary-optimizer-runner`; 격리 `probe/chat-cache-v035-20261024`.
- **인계 갱신 전 실제 독립 HEAD:** 격리 `7a89f2d7ef7c10799a17b3d524790a4c9c48e20b`, `main` `07133e0aaf738d6e4816a6486057b1cd49c018de`. 인계 문서 커밋 이후 격리 SHA는 이동하므로 *새 채팅이 각 ref를 독립 조회*하고 최종 커밋/Actions와 대조할 것. 과거 SHA를 최신 코드라고 단정하지 말 것.
- **우선 읽기:** ① 본 P3-HAV → ② [P3-HAI 제품 상태 A~G](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md) **최상단 최신 보충을 역사 표보다 우선** → ③ [개발 PROTOCOL](development/PROTOCOL.md)·[기능 INDEX](development/INDEX.md) → ④ [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) 최상단 최신 기록 → ⑤ [승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) 및 [실행 개발자 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md) + 최신 사용자 직접 결정 → ⑥ [이번 범위별 증거 대사](development/notes/2026-11-09_p3-hav-engine-first-handoff-evidence.md), [최신 P1 영약 선택](development/notes/2026-11-09_p1-installed-verified-flask-ui-reuse.md), [P1 설치 빌드 귀속](development/notes/2026-11-09_p1-pinned-installed-build-session-bridge.md), [P1 기름 O>0 실 E2E](development/notes/2026-11-09_p1-positive-o-real-web-dps-admission.md), [P2 실제 Native 재사용](development/notes/2026-11-09_p2-real-native-ten-case-region-audit.md), 기존 P3-HAU/P3-HAR/P3-HAS/P3-HAO/P2-OPT → ⑦ 관련 **실제 코드, 원본, Actions/Native 영수증 및 캐시**.
- 규범 우선권: **최신 사용자 직접 결정 > v1.4.3 및 비충돌 승인 정책 > 실제 코드·CURRENT·Actions·Native 영수증 > 이전 인계**. 첨부 역사 v1.4.1의 **27 DPS·증강 포함**/과거 보석 6개/79×2·F165·기름16/16의 타 시즌 일반화는 지금 승인 정책이 아니다. **26 DPS(증강·탱커·힐러 제외)**. GitHub 문서가 존재한다는 사실과 ChatGPT Project Sources 실제 UI 등록은 별개의 사실.

## 2. 목적·사용자 계약 — 단 하나의 재사용 엔진

미래 **목표 ilvl(기본 334)** 또는 사용자의 **기름 포함 수동 최종 T**에서 26개 딜러 전문화의 SimC DPS 최대화를 위한 **치명/가속/특화/유연 절대 rating**을 탐색한다. 관측 1순위/예상 DPS·SEM/95% 통계적 우위 여부·스탯 비율·실질적으로 다른 근접 대안/캐시·취소·재개·결과를 제공한다. 관측 우위·선택된 두 후보의 95%·전역 최적 보증은 서로 다르다.

사용자는 직업·전문화·종족·특성, 목표 ilvl 또는 최종 T, 장신구2, 선택 특수장비, 장식 최대2, 검증된 보석·영약·음식·물약·기름/전투조건 등을 지정. **대표 일반 방어구·무기·주능력치·4티어/기본 APL은 프로그램 내부에서 구성**. 선택 SimC 프로필 업로드는 캐릭터·특성 가져오기 목적이며 현재 장비/현재 총량을 목표로 복사하지 않는다. 장비 조합 추천/파밍 경로/전체 시즌 아이템 DB는 **지원 개발 대상이 아님**.

회계 `G`(시즌·목표 ilvl 대표 장비), `J`(검증 보석), `F`(검증 최고 품질 영약), `O`(무기 기름 고정), **`B=G+J+F`**, **`T=B+O`**, `c_final=c_base+o`. 사용자가 최종 T를 지정하면 `B=T−O`; `O`는 gear 쪽에서 한 번만, 자유분배 불가. **L/E** 정확한 소유권과 스탯별 하한 보호, 장신구는 자유 G 외부, 제작 초기 50:50은 L 아님. 현재 승인 각 최종 rating은 **T/2 미만**. 신규 시즌에 지난 시즌 J/F/O/G 값 복사 금지.

일반보석은 사용자가 지시한 **치명·가속·특화·유연 각 1종을 기본 4개 적용**하고 추가 수량은 기존 소켓 계획에 따른다. 특수보석 효과를 자체 식별·효력 판정하려고 개발 확대하지 않는다. 아이템 효과/proc/APL/전투 DPS는 **SimC 자체**가 담당하고 별도 효과 인증 Gate 금지. 품질이 있는 아이템은 **동일 효과·범위·조건과 비열등성을 실제 증명했을 때만** 최고 품질을 일반 사용자에 노출한다. 원본 미확정 선택 항목은 보류하되 검증 기본 환경은 불필요하게 차단하지 않는다.

## 3. A~G: 현재 재사용 가능 범위 vs 아직 완료하지 않은 제품 경로

| 엔진 영역 | 완료 또는 제한된 Native/CI 실증 | 남은 범위 |
|---|---|---|
| **A 원본·자동 시즌 G/J/F/O/정책 A** | `v216/v222/v212/v217` 기반 실 70783 Ret334 `G2850 J92 F165 O0 B=T3107`, [Native3 #42460255527](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42460255527). `v196/v220` 품질·정책 A·선택지 준비/발행 로직 존재 | **첫 설치·아무 시즌 자료 없는 새 시즌**에서 정상 제품 단일 Build가 새로운 원본을 확보해 G/J/F/O·최고 품질·선택지까지 전주기 자동 확정한 범용 사용자 E2E 미증명. 미검증 항목은 자동 승인 불가 |
| **B 26 DPS·대표 프로필** | [26/26 기본 물리 프로필 수용 #40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357), 기존 DK 룬 정확 원본·한정 Native | 26개 전문화의 임의 실제 옵션/시즌/장시간 사용자 웹 Native 완주 미검증. 전체 장비 입력 강제 금지 |
| **C 고정 예산·보석·영약·기름·L/E** | 기름 주무기 Phoenix Oil 품질2 70783 [정적 Native2 #42582755601](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42582755601) 치16/가16 해당 조건만; [실 양의 O v216→v212→사용자 웹 DPS #42598051977](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42598051977) O32, manual T3500→B3468, 실 DPS171141.52 SEM734.76 | 다른 기름·품질·시즌의 O 근거/일부 특수 L/E 선택 연결·고급 옵션, 일반 사용자 전체 최고 품질 카탈로그 미검증 |
| **D 사용자 Build·선택지·입력** | `v113/webui` 정확 시즌 빌드·ilvl·손별 물리 기름 ID·v212 설치 SHA 선택/복원; **검증 설치 기름 목록** 및 최신 **검증 설치 영약 목록(기름 O0에서도)**. [최신 웹 Linux/Windows 각261 PASS #42623497925](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42623497925), [UI 양 OS #42623498001](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42623498001) | 영약 목록은 **이미 검증·설치된 F를 선택**하는 편의이며 처음 설치하는 미검증 새 시즌의 최고 품질 물리 ID 자동 발견/인증을 대신하지 않음. 실제 개인 Windows PC 클릭 미검증 |
| **E 적응형 SimC·통계** | `v290/v291/v063/v094` 재사용; [8×35 scout + 2×320 confirm Native10 #42501052586](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42501052586), 실제 기존 영수증/시드 재대조. 합법적 0 rating 수용, 국소 고갈 시 기존 전역 후보로 fallback; 합성 다봉형 비교는 실 DPS 아님 | 전역 최적, 26 DPS 탐색 충분성, 여러 고점 누락률, 다중선택편향의 보편적 95% 보증 **없음**. 호출·CPU 절약만을 위해 새 엔진 도입 금지 |
| **F 세션·캐시·취소/재개** | v106/v291/v292/v293, 정확 바이너리/프로필/선택 옵션·고정 O·iterations identity. [동일 실제 10건 교차-job 캐시 재사용 Native0 #42504040076](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42504040076). 실 O>0 웹 E2E에서 재개/캐시 전용 경로 PASS | 새 시즌 최초 사용자 장시간 실행의 운영 안정성·사용자 Windows PC 실제 현장 확인 별도 |
| **G 통합 UI/Windows** | 기존 로컬 웹·포장/loopback. [Windows 패키징 #42623497934](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42623497934) 및 제품 관련 오프라인 PASS. 실제 O>0 사용자 HTTP→SimC 단일 사례 성공 | 초보 사용자의 **완전 초기 설치→한 번 Build→정확 선택지→프로필→장기 DPS→결과** 전주기, 실제 Windows GUI 클릭, 품목별 미완료 연결 |

**역사 경계:** [HAR O0 manual T3500 실 DPS2 #42552942329](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42552942329) DPS171497.55 SEM641.55와 [O>0 #42598051977](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42598051977) DPS171141.52 SEM734.76은 **서로 다른 실행 조건**, DPS 우위 직접 비교 금지. [P2 실제10 후보 ZIP 분석](development/notes/2026-11-09_p2-real-native-ten-case-region-audit.md) 선택된 쌍의 95% 근사는 다른 지역의 부재 증명이 아니다. 이전 P3-HAU의 '실 O>0 웹 DPS 미완료' 등은 **인계 당시 역사**이며 이번 최신 사실로 사용 금지.

## 4. 최신 변경·영수증·검증 적용 범위

- **직전 사용자 대화 완료(HEAD `7a89f2d7ef7c10799a17b3d524790a4c9c48e20b`):** 기존 `v113.installed_oil_loadouts`의 읽기 전용 v212/v217 설치·v113 저장 프로필·Manifest SHA 검증을 공유해 `official_F_physical_source` 영약의 `physical_item_id`, `simc_input_token`, `crafting_quality`, `F_rating`를 `verified_flasks`에 공개. **기름 O0 설치본의 영약도 포함**. 웹 `season-verified-flask` 선택 → 기존 `season-selected-flask-id` 자동 설정; 미설치 ItemID·원본 불일치·SHA 변조/충돌은 선택 금지. 정적 F 계산/품질 인증을 새로 만들지 않음. 코드: `runner/v113_local_web_api.py`, `runner/webui/app.js`, `index.html`. [구체 노트](development/notes/2026-11-09_p1-installed-verified-flask-ui-reuse.md).
- 해당 코드 영수증: [focused #42623498384](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42623498384) **522 PASS + 2 SKIP**, ledger PASS, [Web Linux/Windows #42623497925](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42623497925) 각 **261 PASS**, [UI #42623498001](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42623498001) 양 OS SUCCESS, [Windows #42623497934](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42623497934) 양쪽 SUCCESS. 모든 신규 시즌 Native/외부 수집 **0회**.
- **최신 HEAD 문서 보충 #42623963325:** SUCCESS, **524 tests=522 PASS/2 SKIP/0 FAIL**, `DEV_LEDGER_PASS OFFLINE_NO_NATIVE_NO_NETWORK`. 이것은 F 선택 UI **오프라인 정합성** 증거이지 새로운 시즌 최초 구축이나 실 사용자의 GUI에서 전체 품목이 선택된 증거가 아님.
- 그 외 P1: 설치된 빌드가 `installed_season_game_build`로 단기/장기 웹 세션에 전달되며 `fresh_season_build`(원본 수집)와 분리. [노트](development/notes/2026-11-09_p1-pinned-installed-build-session-bridge.md)와 관련 기존 웹 CI 재사용. 사용자 수동 T 및 기름 O0/positive는 기존 v212 봉인 SHA identity 유지. 현재 26 기본 물리 수용을 실제 26개 사용자 웹 장기 실행으로 과장 금지.
- P2: 합법적 rating0 검증/국소 고갈 fallback은 현 코드에 반영, 6형상 synthetic에서는 기존 전략 5 동률·1 우세, 새 전역 빈도 우위0 → 제품 정책 교체 **STOP**. 이전 실제 Native10 ZIP 감사 재사용. 새 Native/SEM 미세정밀화/전수 재현 비용을 요구하지 않음.

## 5. 병목·더 효율적 대안 및 단장기 로드맵

**핵심 병목은 새 아이템 카탈로그의 부재 그 자체보다 '미설치 신규 시즌의 동일 정상 Build 엔진 전주기 제품 입증'과 그 단계별 누락된 source/등록/사용자 연결을 구별하는 일**이다. 검증 설치본 목록 개선은 완료된 *선택 편의*, 신규 시즌 자동 발견의 완성 증거는 아님. `v196/v220/v212/v216`을 새로 만들거나 전체 품목에 효과 Gate를 신설하면 불필요한 반복이다.

- **단기 P1:** INDEX와 실제 코드·기존 v212 영수증을 먼저 보고 **완전 빈 신규 시즌 설치 경로의 G/J/F/O 및 최고 품질/정책 A 자동 등록 → 대표 프로필 → 동일 v113/v293 사용자 DPS**의 부족한 접합부를 확인. **각 단계에서 SOURCE_ONLY/READY/선택지 공개/웹 E2E를 구분**. 원본이 없으면 해당 항목만 안전 보류하고 O0/검증 기본 환경 유지. 필요 시 이미 검증된 현재 시즌에서 최소 한 대표 사용자 E2E, 과거 70783/Ret/O 반복 Native는 금지.
- **중기 P2:** 먼저 P1 완결, 기존 v290/v291 관측·캐시/통계에서 **좋은 조합 누락·다봉형·통계적 선택편향의 실제 증거**가 쌓일 때만 개선. 새로운 알고리즘/SEM 보정/Native 추가 전수는 기본 로드맵 아님.
- **장기:** 동일 엔진을 다른 시즌의 실제 검증 G/J/F/O·대표 장비/무기/티어/선택지로 갱신하고 **26 DPS**에 적용. 첫 설치 빈 시즌 **통제실험은 정상 제품 단일 Build 경로 사용**; 과거 시즌 seed/캐시·정적 값을 시험 입력으로 쓰지 않으나 정상 신규 Wago/Blizzard/WCL/SimC 수집은 허용. 산출물 봉인 후 독립 대조. 사용자 PC의 Windows 원클릭 검증 및 P1 미연결 옵션은 변경된 범위에 맞게 점진 검증. 원본 v016의 사용자 보고 상태를 직접 통합 완료로 승격 금지.

**매 작업 체크:** 먼저 `PROTOCOL/INDEX/CURRENT`의 기능과 원본·Actions/Native·정적/DPS 캐시를 선조회해 `REUSE / CONNECT / EXTEND / REPLACE / NEW / STOP`를 선택. **불필요한 기능인가·범용 시즌/26전문화 재사용 엔진인가·최신 사용자 승인에 어긋나지 않는가**를 명시적으로 자가검증. 독립적인 확인/수정을 묶고, 동일 완료 기준/기존 증거를 재사용, 실제 변경으로 깨진 부분만 최소 CI/Native 검증. 매 코드 변경에 CPU·메모리·I/O·네트워크·Native 횟수/실행시간·캐시 정체성·취소/재개를 점검. 이미 실증된 70783 16/16, G/J/F, Native10, O>0 웹 DPS, DK 단발을 자동 반복하지 않는다.

## 6. 새 채팅 시작 프롬프트 (처음은 읽기 전용 복원·보고 후 STOP)

~~~text
SIMC SECONDARY OPTIMIZER 프로젝트를 **읽기 전용으로 독립 복원**하라.

저장소: degong2-code/simc-secondary-optimizer-runner
격리 브랜치: probe/chat-cache-v035-20261024
최신 단일 인계 정본: docs/CHAT_CONTINUITY_HANDOFF_20261109_P3_HAV_ENGINE_FIRST_RESTORE.md

먼저 격리 브랜치와 main의 실제 HEAD를 각각 독립 조회하고, 인계 준비 전 기준 SHA
격리 7a89f2d7ef7c10799a17b3d524790a4c9c48e20b, main 07133e0aaf738d6e4816a6486057b1cd49c018de 및 이후 인계 문서 커밋과 독립 대조하라.
실제 최신 HEAD·diff·Actions/Native·코드 상태가 인계 기록과 다르면 그 차이를 먼저 보고하라.

자료 읽기 순서: P3-HAV → docs/PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md 최상단+A~G →
docs/development/PROTOCOL.md·INDEX.md → docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md 최상단 →
승인 v1.4.3와 docs/DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md →
P3-HAV 대사 노트, P1 영약 설치 선택/기름 O>0 웹 E2E/정확 설치 빌드, P2 원본10건/HAE/HAF,
이전 P3-HAU/P3-HAR/P3-HAS/P3-HAO/P2-OPT → 실제 원본·코드·Actions/Native·캐시.

최종 제품 목적은 개별 기능 축적이 아니라 **26 DPS를 위한 하나의 재사용 가능한 시즌 Build + SimC DPS 최적화 엔진 완성**이다.
사용자 목표 ilvl(기본334) 또는 수동 최종 T에 대해 치명·가속·특화·유연 절대 rating의
SimC DPS 최대화를 찾고, DPS·SEM·95% 우위 확정/미확정·관측 1순위·실질적 대안·스탯 비율,
캐시/취소/재개/결과를 제공한다. B=G+J+F, T=B+O, 수동 T 우선, 고정 L/E/O 보호,
각 rating<T/2, SimC owns effects/APL/procs/DPS. 증강·탱커·힐러 제외.
전체 장비 선택/장비 추천·조합·획득 경로·전체 시즌 DB/새 효과 인증 Gate 금지.
일반 보석 4종(각 스탯 하나씩) 기본·특수 효과 SimC 위임, 95%만 사용,
시즌 데이터 검증 없이는 다른 시즌 G/J/F/O 및 최고 품질을 복사·승인하지 않는다.

최신 독립 확인(인계 전): 격리 7a89f2d7ef7c10799a17b3d524790a4c9c48e20b, main 07133e0aaf738d6e4816a6486057b1cd49c018de.
최신 GitHub focused #42623963325 522 PASS/2 SKIP·ledger PASS,
웹 Linux/Windows 각261 #42623497925, UI #42623498001, Windows #42623497934 PASS.
이미 확보: 70783 Ret334 O0 G2850/J92/F165/B=T3107 Native3 #42460255527;
manual T3500 O0 실제 웹 DPS Native2 #42552942329;
Phoenix Oil2 주무기 O=치16+가16 전투 전 정적 Native2 #42582755601;
실 positive O 웹→SimC DPS Native2 #42598051977, 사용자 T3500→B3468/171141.52 DPS SEM734.76;
8 scout+2 confirm Native10 #42501052586 및 기존 캐시 재사용 #42504040076.
기름·영약 UI의 정확 물리 ItemID 선택은 **이미 검증 설치된 항목** 한정; 새 시즌 최초 최고 품질 발견 자동 완료는 아니다.
첫 설치부터 동일 정상 Build로 G/J/F/O→정책 A→공개 옵션→대표 프로필→사용자 웹 SimC
전주기 입증·일부 L/E·26개 웹 장기 Native·실 Windows PC 클릭·전역 최적 보증은 미완료.

매 작업 전에 기존 INDEX·개발 기록·원본·GitHub 코드/Actions/Native 영수증·캐시부터 선조회하고
이미 구현된 것과 제품 미연결/증거 부족을 분리하여 REUSE/CONNECT/EXTEND/REPLACE/NEW/STOP 결정.
항상 '왜 필요한가, 최신 정책에 어긋나지 않는가, 26 DPS·미래 시즌 범용 엔진인가'를 검토하라.
독립 작업을 묶고 동일 완료 검증 기준과 기존 증거를 재사용하며 변경된 부분만 최소 검증.
불필요한 신규 Gate, 효과 연구, 26 전문화/전 시즌 전수 Native, 70783 과거 실험/과거 ZIP 전면 재감사,
과도한 SEM 미세보정/새 최적화 알고리즘 신설 금지. 메모리·I/O·CPU·중복 실행·캐시 identity 점검.
main, immutable, Project UI/Work OS 및 주 제품 개발 채팅 권한 불변.

**첫 응답은 복원 결과와 간결한 장·단기 로드맵 보고만 하라.**
최신 실제 HEAD, 최신 승인 정책, A~G 구현/실증/미검증, 병목 및 더 효율적 대안을
독립 대조해 알리고 즉시 중단하라.
사용자가 별도로 **'진행'**이라고 하기 전에는 코드·문서 수정, 테스트/원본 수집,
GitHub Actions/Native 실행, 커밋·병합, Project UI·Work OS·공식 승격을 절대로 시작하지 마라.
~~~
