# SIMC SECONDARY OPTIMIZER — 제품 우선·최소 충분 검증 상시 인계 (v456 단일 복원 정본)

> **2026-11-14 최신 사용자 직접 결정의 인계 진입점.** 정책 정본은 [제품 우선·최소 충분 검증](development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md)이다. 이 인계는 과거 v445 인계의 날짜별 상태와 독립이며, 실제 개발 HEAD/78요소 증거를 덮어쓰지 않는다.
>
> **새 채팅 필수 동작:** 이 정책 → [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) → [START_HERE](development/START_HERE.md) → [78개 기계 정본](development/78_ELEMENT_COMPLETION_CONTRACTS.json) → GitHub 브랜치 HEAD/Actions/Native 영수증 순으로 확인한다. 사용자가 읽기 전용 복원을 요청했다면 확인 후 **STOP**; 명시적 `진행` 전에 코드·문서·시험 실행 금지.

## 제품 목표와 절대 보존 범위

- **26개 DPS만 지원**, 목표 ilvl 기본334 또는 사용자 지정 최종 CHMV T를 기준으로 **치명·가속·특화·유연 최적 절대 rating**을 기존 SimC DPS로 찾는다. 비율/DPS·SEM/95% 판정·관측 1순위·실질적 근접 대안 제공. 전역 최적 증명 금지.
- 사용자는 전문화/종족/특성·목표 ilvl/T·장신구2·선택 특수/제작 장비·장식 최대2·보석/영약/기름/소모품·전투조건만 입력. 일반 장비·무기·티어4pc·주능력치·원본 SimC 프로필은 내부 대표 구성. 현재 착용 장비 재분배·전체 DB·아이템 조합 추천은 범위 밖.
- 새 시즌 **G/J/F/O 자동 구축**, `B=G+J+F; T=B+O; c_final=c_base+o`; 수동 T 우선, 정확 L/E/O 소유권/중복 방지, 옵션별 정확한 정적 rating 검증. SimC가 아이템 효과·proc·APL·DPS 소유. 별도 효과 해석/발동 인증기 불필요.
- 그대로 유지: 기존 v216/v217/v212 환경 원본, v098/v096/v094 USER→적응형 SimC, 95% 판정, 캐시·취소·재개, 동일 시즌 정적 캐시 재사용. 새로운 알고리즘/전수 Native/영구 WEQUIP 의존성 금지.

## 이번 사용자 결정으로 바로잡은 개발 우선순위

**78개 요소는 진척·증거의 정확한 기록이지, 모든 항목을 하나씩 심층 연구해야 하는 개발 순서가 아니다.** `next_review=B10`은 다음 **판정** 위치이며, 선택 기능인 추가 소켓의 내부 효과를 모두 추적한 뒤에야 일반 제품을 만들 수 있다는 뜻이 아니다. 네 증거 축과 COMPLETE/최종 실제 ZERO-SOURCE→USER-E2E 수락 조건은 그대로 유지한다.

매 새 개발 작업은 먼저 **(1) 사용자 결과 경로의 실제 차단 (2) 실제 소비 필드 (3) 기존 코드·영수증 재사용 (4) 비선택 옵션 보류로 BASE 실행 가능 여부 (5) Native/HTTP/DB2·유지비 (6) STOP 기준**을 확인한다. 비선택 미검증 옵션은 그 옵션만 감추거나 차단한다. 이미 검증된 기본 환경이나 다른 사용자 선택까지 막지 않는다. `STOP/REUSE/CONNECT/FIX` 우선, 새 수집기·효과 모델·Gate는 예외다.

## 사실과 한계 (이 문서 작성 시점)

- 저장소 `degong2-code/simc-secondary-optimizer-runner`, **격리 브랜치** `probe/chat-cache-v035-20261024`; 실제 HEAD는 인계 시 반드시 새로 조회. `main`·v003·원본 v016·Project UI·공식 승격은 변경 권한 없음. 현재 주 제품 개발 채팅이 구현을 계속 소유.
- 최신 [78요소 정본](development/78_ELEMENT_COMPLETION_CONTRACTS.json): **15/78 COMPLETE** (generic 27/current_source 27/product 15/historical 13 PASS), B10 generic/current_source/product PENDING, historical PASS, 전체 strict E2E PENDING. 숫자는 작성 시점 기록이며 실제 최신 JSON 우선.
- v445~v451 B10의 보석/물리 ItemID 일관성 방어는 보존. [v452 실제 70783 ItemID→use SpellID](development/notes/2026-11-14_p1-v452-b10-real-70783-on-use-item-source.md), [v454/v455 SpellEffect 원본·봉인된 v281 진단](development/notes/2026-11-14_p1-v454-v455-b10-real-spell-and-sealed-v281-j-source.md)은 **연구 자료**로 남긴다. 실사용 소켓 적용 권한/J 신규 승인은 미증명. **더 이상의 B10 주문 체인/전 품목 검증은 일단 중단**하고 일반 제품의 첫 실제 차단을 우선 확인한다.
- 최근 v098 집중 회귀 **489 PASS/0 FAIL** ([Actions #43570938990](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43570938990)); v401 최신 검사 PASS는 당시 해당 HEAD의 범위에 한정. Reusable Offline 공통 ledger의 역사 오류 198건은 모든 제품 코드 실패가 아니다. 이번 정책·인계 문서 기록 자체로 새로운 Native/DB2/API·사용자 E2E 증거가 생기지 않는다.

## 이미 실행된 다른 DPS 기본 사용자 — 신규 재측정 STOP (2026-11-14 재확인)

- **냉기 마법사**: [2026-11-10 real #42785318578](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42785318578) SUCCESS. ilvl334·일반보석4·특수0·O0, **수동 T3300**, 실제 v216/v212→v098 사용자 프로필→FastAPI/v291 Native2·캐시 재실행 신규0, DPS165226.98/SEM706.33, 95% 우위 미확정. [원본 근거](development/notes/2026-11-10_p2-fresh-four-ordinary-cross-profile.md).
- **풍운 수도사**: [2026-11-11 real #42941245130](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42941245130) SUCCESS. 70783·ilvl334·일반보석4·특수0·O0, **자동 T3107**, 실제 원본 GJFO→새 프로필→SimC. v290 DPS183394.77/SEM259.63. 기존 64+64회는 역사 알고리즘 연구 비용이지 새 기본 제품 실행의 필수 반복량 아님. [원본 영수증](development/research_receipts/p2_v319_windwalker_auto_T_real_v290_v318_compact.json).
- **조화 드루이드**: [2026-11-11 real #42949922419](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42949922419) SUCCESS. 같은 빌드·ilvl334, 일반보석4·특수0·O0, **자동 T3107**, 신규 사용자 프로필·실제 Native. v290 DPS176065.99/SEM271.35. 기존 64+64·추가 N32는 과거 정책 연구이며 신규 필수 Gate 아님. [원본 영수증](development/research_receipts/p2_v324_balance_auto_T_variable_n_32_compact.json).
- 세 실증은 개별 user-like FastAPI/원본/SimC 범위이며 개인 Windows 브라우저 클릭·전체26·미래 시즌·strict ZERO-SOURCE→USER-E2E 제품 전체 PASS는 아니다. v343/v439의 생존 사냥꾼과 다른 전문화임이 실증되어 있으므로 **'다른 DPS 1건' 명목의 새로운 전체 DB2/Native 실행은 STOP**. 오래된 다른 시즌 수치를 미래 시즌에 전용해서도 안 된다.

## 다음 개발 채팅이 해야 할 첫 판단

1. 위 실증 3건을 먼저 확인하고, 이미 입증된 기본 4보석/O0/자동·수동 T/USER→SimC 연결의 재인증을 위한 신규 Native 계획은 **STOP**하라. 실제 UI/API 사용자 경로가 실패하는 **새로운 구체적 장애물**을 찾아 기존 원본·캐시를 사용해 최소 수정하라. 선택지 근거가 없으면 그 선택지만 보류한다.
2. 그 결함의 원본·수치·예산 정확성을 해치지 않는 **최소 CONNECT/FIX**와 변경 범위 집중 회귀를 제안·시행하라. 임의의 B10 연구, 78 ID 숫자 채우기, 외부 자료 전수 다운로드를 자동으로 재개하지 마라.
3. 결과 보고는 사용자 가치·실제 진행도·실행증거와 PENDING 분리·비용/기존 캐시 재사용을 먼저 제시. 다음 채팅에 동일한 [상시 정책](development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md) 링크를 반드시 인계하라.

**새 사용자 직접 결정 > 이 운영 해석 > 비충돌 승인 설계 > GitHub 실제 코드/영수증 > 과거 인계**. 단, 이 문서는 승인 설계/기계 정본의 값이나 실제 개발 상태를 변경하는 근거가 아니다.


---

## v456 기준 단일 인계 정본 — 2026-11-14 실제 GitHub 재조회

> **이 문서가 이 날짜의 최신 단일 독립 복원 진입점이다.** [v445/B10 인계](CHAT_CONTINUITY_HANDOFF_20261114_P1_V445_78ELEMENT_B10_SOCKET_READONLY_RESTORE.md)는 역사 자료. 이 문서 갱신 **직전 코드 HEAD**는 **66e6a24f51fa6272e3cdc9a9b6dc4044082c3c37**이며, 문서 갱신 커밋 후 HEAD는 달라지므로 다음 채팅은 반드시 재조회한다. 저장소 degong2-code/simc-secondary-optimizer-runner, 격리 브랜치 probe/chat-cache-v035-20261024; main HEAD는 당시 07133e0aaf738d6e4816a6486057b1cd49c018de, 이번 인계에서는 수정 금지.

### 1. 공식 상태와 다음 판정

[78개 기계 정본](development/78_ELEMENT_COMPLETION_CONTRACTS.json)을 실제 조회한 결과 **78개 중 공식 COMPLETE 15개**, generic **27 PASS**, current_source **27 PASS**, product_integration **15 PASS**, historical **13 PASS**. COMPLETE ID: **A8, A9, A10, A11, B2, B3, B7, B8, D4, D6, E1, H1, H3, H4, H6**. 다음 **원장 판정 대상** B10은 generic/current_source/product_integration PENDING, historical PASS. B9는 generic/current_source PASS, product_integration PENDING. **전체 strict ZERO-SOURCE→USER E2E는 PENDING**이다. 다음 원장 판정 순서를 제품 구현 순서로 취급하지 않는다.

[v441 78요소 필요성 감사](development/78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md): 54개 수락 조건 범위 축소·정밀화, 24개 유지. 이 검토만으로 PASS는 오르지 않았다. 축별 수락, 기존 영수증 공동 귀속, 공식 COMPLETE 수락은 [v401 정책](development/POLICY_78_ELEMENT_COMPLETION_GATE_V401.md)에 따른다.

### 2. 사용자 승인 최종 목적·정확성

[승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md): **증강 제외 26 DPS 전문화**에서 목표 아이템레벨 기본 334 또는 수동 최종 CHMV T를 기준으로 **SimC DPS 최대화** 치명·가속·특화·유연 **절대 rating**을 찾는다. DPS·SEM·**95%** 확정/미확정·관측 1순위·실질적으로 다른 근접 대안·비율 제공. 전역 최적을 주장하지 않는다.

주 사용자 경로: 전문화/종족/특성·ilvl 또는 수동 T·장신구2·선택 특수/제작 장비·장식 최대2·보석/영약/소모품/기름·전투조건 선택 → 내부 대표 일반 장비/무기/주능력치/티어4pc·SimC 프로필 → 기존 적응형 SimC → 결과/캐시·취소·재개. 현재 장비 재분배·장비조합 추천·시즌 전체 DB는 범위 밖.

새 시즌 **G/J/F/O 전체** 구축, B=G+J+F, T=B+O, c_final=c_base+o; 사용자 수동 최종 T 우선, L/E/O 고정치와 gear 주입 중복 방지·정적 JSON2 rating 검증. 다른 시즌 수치를 새 시즌 검증값처럼 재사용 금지. 최고 품질 검증 선택지 자동 등록, 영구 마부/무기 기름, 일반 임시 마부 제외, 시즌 특수 모듈 분리 정책 유지. **SimC가 proc/효과/APL/DPS 계산**을 소유하고 우리 코드는 그 내부 효과를 재구현하거나 인증 Gate를 만들지 않는다. 세부 정책은 [상시 정책 원문](development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md)을 링크하여 재사용한다.

### 3. 최신 구현과 증거 (역사 실행과 이번 검증 구별)

- **v439**: [생존 사냥꾼 70783 실제 제작머리·티어4pc·DPS](development/notes/2026-11-14_p1-v439-b8-one-real-selected-70783-four-tier-native-e2e.md), [Windows Native #43466966207](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43466966207) **SUCCESS**. 해당 실제 선택 시나리오의 한정된 입증.
- **v440**: [기존 6개 실제 JSON2의 95%·근접 대안 재판정](development/notes/2026-11-14_p1-v440-b8-existing-real-json2-95-material-replay.md), [#43534722801](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43534722801) **SUCCESS**, 신규 Native 0. 전역 최적 증거 아님.
- **v441~v443**: 수락 조건 필요성 전수 감사 및 기존 Native/오프라인 영수증 다중 귀속으로 공식 COMPLETE 15개까지 확대. 새 Native 반복 요구 없음.
- **v444~v451**: 촉매/대표 소켓/보석 J·ItemID·선택 옵션 정합 보강. 실제 선택 촉매 product 및 현재 추가 소켓 게임 적용성은 미확정.
- **v452~v455**: 70783 사용 주문/SpellEffect 연구 결과는 역사 영수증으로 보존. 선택 추가 소켓의 **효과 연쇄 완전 인증은 중단**; SimC gem_id 수용을 실제 게임 소켓 추가 허용으로 취급하지 않는다.
- **v456**: [현재 시즌 음식·물약·증강 룬 UI 선택지 범위 수정](development/notes/2026-11-14_p1-v456-current-season-optional-consumable-ui-scope.md). 역사 v108 파서 토큰을 승인된 신규 시즌 선택지로 노출하던 문제를 v113→v218→v098 실제 수용 범위에 맞춰 수정. 신규 선택은 현재 검증된 source_default→disabled만 제공, 과거 세션 식별/복원은 유지하되 미승인 신규 실행 차단. 전체 최고품질 소모품 등록 완료 아님. [v113 Linux/Windows #43576570601](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43576570601) **각 360 PASS/0 FAIL**, [v182 UI #43576570579](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43576570579) **SUCCESS**, [v181 Windows/Loopback HTTP #43576570570](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43576570570) **SUCCESS**. 해당 CI는 오프라인/API/UI/패키지 범위이며 신규 Native E2E 아님.
- 문서 수정 **직전 HEAD** [v401 78 계약 #43576856813](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43576856813) **SUCCESS**. [Reusable Offline #43576856843](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43576856843) **FAILURE**: 실패 단계는 developer ledger 검사, 실제 job 로그의 DEV_LEDGER_FAIL **198건**. 기존 역사 ledger 문제를 새로운 SimC 실패로 자동 해석하지 않는다. 이번 문서 변경이 새 ledger 오류를 만들면 별도 판정.

### 4. 다른 DPS 실측·캐시 재사용

- [냉기 마법사 수동 T3300](development/notes/2026-11-10_p2-fresh-four-ordinary-cross-profile.md) [#42785318578](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42785318578) SUCCESS.
- [풍운 수도사 자동 T3107](development/notes/2026-11-11_p2-v319-new-windwalker-real-v290-v318-ab.md) [#42941245130](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42941245130) SUCCESS.
- [조화 드루이드 자동 T3107](development/notes/2026-11-11_p2-v324-new-balance-continuous-n.md) [#42949922419](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42949922419) SUCCESS.

다전문화 실제 원본 G/J/F/O→사용자별 대표 프로필→SimC 결과가 위 조건에서 실증됐으며, 26개 전문화 전체·모든 선택 옵션·미래 시즌·최종 strict E2E 보증은 **아니다**. 같은 시즌 정적 아이템 캐시는 SimC revision만으로 무효화하지 않는다. DPS 캐시는 바이너리/프로필/장비·옵션/CHMV 후보·O/전투조건/iterations별 분리. 기존 저장·중단·재개·캐시·Native JSON2 영수증은 계속 재사용한다.

### 5. 구현·미실증·미구현 구분과 첫 실제 장애

이미 있는 기능군: [FILE_MAP](development/FILE_MAP.md)과 실제 코드에서 v216/v217/v212 환경 설치, v222 B/T, v098/v096 사용자 시나리오·실행, v113 웹 API, v094/v106 세션·결과, v290/v291 기존 탐색, v292/v293 캐시·재개, v232/v271 대표 장비·소켓, v190/v280/v281 시즌 소스·기존 진단을 확인한다. **파일명 목록을 새 구현 대상 목록으로 오해하지 않는다.**

**현재 첫 신규 사용자 장애는 이 읽기 전용 인계 조사만으로 특정되지 않았다.** 다음 개발은 기존 사용자 UI→현재 승인 선택지→시즌 예산 B/T→대표 프로필→SimC 실행→95%/대안 결과→캐시·취소·재개의 실제 연결에서 **첫 번째 확인 가능한 실패 경계**를 찾아 REUSE/CONNECT/FIX로 최소 수정한다. 결함을 못 찾으면 증거가 보장한 범위와 미실증 범위만 보고한다. 실제 선택한 필수 필드 원본/예산이 미확정이면 해당 시나리오만 fail-closed; 미선택 추가 소켓/촉매/시즌 모듈/소모품은 해당 옵션만 PENDING으로 보류한다.

**STOP 사례:** 추가 소켓 모든 SpellEffect 연쇄 조사, 26 DPS Native 전수, 전체 DB2/품목 수집, 독립 proc·APL 인증 Gate, SEM 0 달성, 다음 B10 번호 때문에 제품 기능을 중단하기, 기존 같은 시즌 증거 재실행, 새 탐색 엔진 만들기. 매 작업 시작/종료마다 [상시 정책](development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md)의 여섯 질문과 STOP/REUSE/CONNECT/FIX/EXTEND/REPLACE/NEW를 적용한다.

### 6. 초단기·단기·장기 로드맵

- **초단기**: 기존 CURRENT·FILE_MAP·실 코드·사용자 UI/제품 선택지의 연결을 읽기 전용으로 추적하여 가장 비용이 낮은 **실제 첫 장애** 확인. 확인 전 신규 연구·Native·DB2 중단.
- **단기(다음 채팅 사용자의 별도 진행 승인 후)**: 첫 확인 장애만 기존 구현을 재사용해 최소 수정, 변경 범위 집중 회귀 및 필요할 때만 최소 Native, 사용자 선택지·프로필·G/J/F/O/B/T·정적 rating·95%·캐시 정합 유지.
- **장기**: 26 DPS와 새 시즌의 실제 사용·변경 범위에서 미실증 경계를 증분 검증. 마지막에 strict ZERO-SOURCE→USER E2E와 출시 수락을 판단. 원본 v016_SCENARIO_CONTRACT의 실제 바이트/영수증 확인 전 직접 통합 완료라 주장 금지.

### 7. 권한·다음 읽기 순서·STOP

기존 주 제품 개발 채팅의 제품 구현/일반 SimC 시험 소유권은 그대로다. **이번 인계에서는 문서만 수정**하며 제품 코드·78 JSON·Native/API/DB2 수집·테스트·사용자 캐시/결과 변경 없음. main 병합, v003 immutable, 원본 v016 변경, Project Sources/Instructions UI 실제 적용, Work OS M0·Shared State·공식 승격은 사용자 별도 승인. GitHub 문서 기록은 Project UI 적용 증거가 아니다.

다음 채팅은 다음 순서로 읽는다.

1. [제품 우선 상시 정책](development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md)
2. **본 단일 인계 정본** (기존 v445 역사 인계와 구별)
3. [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md)
4. [START_HERE](development/START_HERE.md)
5. [INDEX](development/INDEX.md)
6. [FILE_MAP](development/FILE_MAP.md)
7. [v1.4.3 승인 설계](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md)
8. [v441 필요성 감사](development/78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md)
9. [78 기계 정본](development/78_ELEMENT_COMPLETION_CONTRACTS.json)과 [v401 정책](development/POLICY_78_ELEMENT_COMPLETION_GATE_V401.md)
10. [78 자동 상태표](development/78_ELEMENT_STATUS_GENERATED.md)·[상세 추적표](development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md)
11. v439~v456 실제 관련 코드·노트·Native/Actions 영수증, 캐시
12. **실제 최신 브랜치 HEAD와 Actions 재조회** 후 읽기 전용 독립 복원 보고.

**다음 새 일반 채팅의 첫 응답은 읽기 전용 복원 보고만 수행하고 STOP. 사용자가 별도 ‘진행’이라고 승인하기 전에는 코드·문서·JSON 수정, 테스트/Actions 실행, Native/API/DB2 수집, 커밋·병합·공식 승격을 시작하지 않는다.**
