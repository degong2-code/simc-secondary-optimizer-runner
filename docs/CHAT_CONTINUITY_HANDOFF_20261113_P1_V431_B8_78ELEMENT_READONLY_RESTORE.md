# SIMC SECONDARY OPTIMIZER — v431 / B8 78요소 단일 인계 정본 (2026-11-13)

> **신분:** 다음 개발 채팅의 독립 복원 정본. 본 문서는 코드 변경·새 Native 실행·78요소 PASS 승격이 아니다. **상태 판정의 유일한 정본은 [78 JSON](development/78_ELEMENT_COMPLETION_CONTRACTS.json)**이다. 과거 [v420 A10 인계](CHAT_CONTINUITY_HANDOFF_20261113_P1_V420_A10_78ELEMENT_READONLY_RESTORE.md)는 역사. 최근 v429~v431의 더 새로운 증거가 우선한다.
>
> **기준 격리 repo/branch:** `degong2-code/simc-secondary-optimizer-runner` / `probe/chat-cache-v035-20261024`. **이 문서를 작성할 때 검증한 소스 기준 HEAD `c512ff15042013f479b659f052393979cdf10e49`**. v431 제품 코드 커밋 `922bdb84393db4684f6850a1c50b9faf3209ae9c`, 이어진 기록 커밋 `c512ff15042013f479b659f052393979cdf10e49`. **인계 문서 커밋은 별도 SHA이며, 새 채팅은 브랜치 실제 HEAD를 독립 재조회해야 한다.** 문서 안에 자기 자신의 최종 HEAD가 기록돼 있다고 가정하지 않는다.

## 1. 제품 목적·최신 승인·권한

26개 **DPS** 전문화만(증강 기원사·탱커·힐러 제외). 사용자는 목표 ilvl(기본 334) 또는 직접 입력한 최종 CHMV 총량 `T`를 설정한다. 프로그램은 미래 파밍 목표인 치명/가속/특화/유연 **최적 절대 rating**을 SimC DPS 최대화로 탐색한다. 사용자가 일반 장비 전체를 고르지 않으며, 내부가 대표 일반 장비/무기/티어 4pc/프로필을 구성한다. 장신구 2개, 특수장비, 장식 최대 2개, 캐릭터/전투/소모품 입력은 사용자 선택.

공식 회계: `G` 목표 ilvl 대표 비장신구 예산, `J` 검증 보석, `F` 검증 영약, `O` 고정 기름; **`B=G+J+F; T=B+O; c_final=c_base+o`**. 새 시즌마다 **G/J/F/O 모두** 같은 시즌 검증 원본으로 자동 구성하며, 사용자의 수동 최종 T 우선. 특수장비 정확 `L`은 G에 포함돼 **다시 더하지 않는다**. 제작 초도 50:50은 잠금 L이 아니며, 장신구 정적 스탯은 자유 G 밖. 정적 마부 E, O는 허용 회계에 따라 한 번 반영하고 중복 금지. 장신구 정적 JSON2 미관측은 0이 아니며 선택 차단이 아니다.

SimC가 아이템 효과/프로크/APL/무기 피해/DPS를 책임진다. 우리 쪽은 정확한 ID/ilvl/옵션/CHMV 고정치/JSON2 rating, 후보·캐시·취소·재개·95% 통계·저장 결과/Windows UI를 담당한다. 관측 DPS 1순위와 95% 확정·전역 최적 주장을 구분한다. 아이템 조합 추천, 파밍 경로, 시즌 전 품목 DB, 신규 최적화 엔진, 별도 SimC 효과 인증 Gate를 만들지 않는다.

최신 사용자 직접 결정 > 승인 설계 > 실제 GitHub CURRENT/Actions/Native > 과거 인계. 과거 v1.4.1의 27 DPS·증강 포함, 예전 시즌 G/J/F/O 정액, SimC↔게임 빌드 번호 정확 일치 Gate, SimC 소스→바이너리 독립 계보 Gate를 복구하지 않는다. WSE는 비차단 진단. 동일 시즌 정적 아이템 캐시는 SimC revision 변경만으로 폐기하지 않고, DPS 캐시는 실제 실행 바이너리/프로필/후보·장비 옵션/O/전투/iterations로 분리. 기존 `V106_USER_RESULT.json`/`V291_RESULT.json` 스냅샷 조회에 Native 재실행 금지.

격리 브랜치 기록·검증 이외 `main` 병합, `v003` immutable 변경, ChatGPT Project UI Sources/Instructions 실제 적용, 공식 Work OS M0/Shared State 승격, WEQUIP 영구 런타임 의존성 도입은 사용자 별도 권한 없이는 금지. 주 제품 개발 소유권을 임의 이전하지 않는다.

## 2. 78개 완료 계약 — 지금 실제 확인한 스냅샷

- 유일 상태 정본: [JSON](development/78_ELEMENT_COMPLETION_CONTRACTS.json) → [기계 생성표](development/78_ELEMENT_STATUS_GENERATED.md) → [78개 상세 추적표](development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md) → [v401 정책](development/POLICY_78_ELEMENT_COMPLETION_GATE_V401.md).
- 기준 HEAD `c512ff15042013f479b659f052393979cdf10e49`: `generic 18/78`; `current_source 18/78`; `product_integration 7/78`; `historical 12/78`; 3필수 축 COMPLETE **7/78** = **A8/A9/A10/A11/B2/B3/B7**; `next_review=B8`; `full_product_e2e=PENDING`.
- **B8** `generic=PENDING/current_source=PENDING/product_integration=PENDING/historical=PASS`; historical 증거 **v187 + v431**. B4·B5·B6 제품 축 PENDING, B1 전 26전문화 제품 통합 PENDING. B7은 13직업×5 원본 공급과 확인된 생존 4pc 소비 범위만 COMPLETE이고 B8 선택 충돌/촉매 B9까지 완료됐다는 뜻이 아니다.
- PASS 숫자는 인계 당시 스냅샷이다. 다음 채팅은 **항상 최신 GitHub JSON에서 재산출**하고 자동 표/상세 표와 정합 확인한다. 문서 인계를 위해 완료 수치를 수정하지 않는다.

## 3. 재사용할 실제 제품·원본·검증 증거

- **v417 실제 Windows P1 성공:** [Actions #43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756), [Native artifact #14021859656](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756/artifacts/14021859656), tested `89d4810baf5e05f1c5c6f355f39a5f35ca9ec4e7`. KR Retail `12.1.5.70783`, 생존 사냥꾼 목표334, **G2850/J92/F165/O0, B=T3107**; 환경 Native3·DPS Native12; CHMV **373/1078/1491/165**, DPS **178334.86**, SEM **298.61**, 95% 선택쌍 방향 지지와 저장 결과 재조회. **선택 특수장비/장식 0**인 기본 4pc 증거로, B8 선택 충돌·26개 전수·최종 제품 완성 증거가 아니다.
- 기존 70783 동빌드 원본 수집과 v217 봉인, v191 컴파일/티어65, v216/v212 설치, v222 G/J/F/O, v098/v096/v293 실 실행·결과, v290/v291 탐색, v292/v293/v106 캐시·취소·재개, v113 UI는 **현재 코드/기존 영수증 우선 재사용**한다. 기존 v180 비334, v185/v186 교정 무기, v187 티어 회귀, v414/v415 특수 L·설치 SHA 연결을 실증 범위에 맞게 재사용한다.
- **v431 코드·focused CI:** [코드 커밋 922bdb8](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/922bdb84393db4684f6850a1c50b9faf3209ae9c), [v431 노트](development/notes/2026-11-13_p1-v431-b8-sealed-season-injection-code-offline.md), [v187 #43428273777](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43428273777) **16/16**, 연관 v106/v169/v172 **36/36**, [v098 #43428273723](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43428273723), v177/v180 offline, Windows v181/v182 모두 SUCCESS. 가상 테스트 빌드 `12.1.5.79999`는 **합성**으로 실제 70783 원본/native가 아니다. 신규 Native0·외부 DB2 0.
- 기준 HEAD [78개 계약 #43429003461](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43429003461) **SUCCESS**. [범용 focused #43429003390](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43429003390) **FAIL**은 개발 장부의 기존 이력 형식 **198건**, v431 추가 오류0. 이는 제품 Native 결함을 의미하지 않지만 CI 전체 SUCCESS로 보고할 수도 없다.

## 4. v430 → v431에서 실제 해결한 것과 남은 것

**v430에서 찾은 원인:** 오래된 v101의 선택 슬롯 검증/촉매 overflow는 내부 `v167.read()`·`v169.load_tier()`의 **70575 포장 자료**를 다시 읽었으며, v098의 새 시즌 `season_profile_inputs` 경로는 선택 특수장비·장식을 금지했다. 기존 v101 4-of-5 알고리즘 및 v187 26 DPS 오프라인 성공을 최신 70783 사용자 선택 성공으로 간주할 수 없었다.

**v431에서 수정 완료 — 재구현 금지:**
1. `runner/v101_common_representative_equipment.py`: `_selected_current_season_sources`가 호출자 제공 gear/tier **두 문서 모두**와 동일 빌드·직업 5개 티어 ID/마스크를 검사하고, 둘 중 하나만 전달되면 fail-closed. `validate_current_season_selected_slots`, `reconcile_current_season_five_tier`, `apply_user_equipment`는 이 소스를 재사용. 촉매 5개→4개 시 **70575 재조회 금지**.
2. `runner/v098_target_user_scenario_bootstrap.py`: 기존 원본 SHA 결합 `season_source_bundle["gear"/"tier"]`을 v101 `apply_user_equipment`에 전달. no-selection 기존 경로와 캐시를 불필요하게 변경하지 않음.
3. `tests/test_v187_current_season_tier_overlay.py`: 가상 다른 빌드 전용 crafted head ID, source pair/빌드 drift, catalyst 5→4의 3가지 신규 회귀 통과. 새 4-of-5 알고리즘 없음.

**남은 정확한 병목:** `runner/v098_target_user_scenario_bootstrap.py::build`의 `season_profile_inputs` 수락 조건에서 **`not user["special_items"] and not user["embellishments"]`** 유지. 현재 v431 주입은 호출자 원본을 4pc 코드에 전달하는 1단계일 뿐 **선택 교체 장비의 exact 정적 G/L 예산·물리 프로필·v212 설치 manifest·J/F/O/B/T·세션 SHA의 전체 연결**을 아직 승인하지 않았다. 이 차단을 단순 삭제하면 다른 원본·구 G·특수 L 중복/제작잠금/캐시 혼용 위험. **B8의 generic/current_source/product 축은 아직 PENDING**.

확인된 계층: `v216/v217` 원본/봉인 → `v191/v276` 티어·대표 장비 → `v222` 현재 G/J/F/O·`v212` 설치 → `v098` 검증된 source & 선택 교체 물리 row → 기존 `v101` 4pc 재배치 → 정확 special L/free crafted, B/T/O·세션SHA → `v096/v293` 실제 Native DPS/SEM/95% 및 결과. **v414/v415 exact L·원본 설치 SHA 경로를 먼저 재사용**한다.

## 5. 다음 작업과 최소 검증 — 사용자가 '진행' 후

1. **REUSE:** v431 diff와 v101/v098 함수 및 v212·v222·v414/v415 budget/installed source identity를 재확인. 현재 70783 원본에 실제로 선택할 수 있는 특수·제작 정확 ID/slot/variant/L의 검증 범위, 미확정과 이미 구현된 부분을 분리.
2. **CONNECT:** 검증된 선택 장비 ID/ilvl/옵션·원본 SHA가 v098의 실제 물리 row 교체, v101 4-of-5 배치, G(교체 반영)·special L(이미 G에 포함), crafted 자유 분배, J/F/O/E 및 수동 T 변환/중복 방지, 세션·DPS 캐시에 **동일 조건으로** 전달되게 최소 연결. 값이 실제 미확정일 경우 그 선택 변형만 보류·기존 exact 캐시/선택적 최소 Native 사용; 기본 환경 차단·전체 DB 재구축 금지.
3. **TARGETED OFFLINE:** 티어 외 부위 특수 선택 → 기본4 유지; 티어 머리 제작/특수 선택 → 가슴 티어 복원; 두 티어 부위 점유 → 명시 차단; 촉매 1회; build/source SHA/역할 불일치 차단; 교체 G/L/J/F/O/B/T와 대표 물리 profile 일치; 변경된 세션 SHA와 구 캐시 불변. 변경에 영향을 받은 테스트만 실행.
4. **MINIMUM NATIVE:** 오프라인 정합이 입증된 실제 70783 사용자 선택 변형 **1개**로 필요한 실제 SimC/profile/JSON2 rating, DPS/SEM/95%·저장/재개 확인. 기존 v417 기본4pc·26 DPS 전수 반복 금지. 실제 결과가 부적합이면 첫 위반 경계와 원문 오류 기록.
5. **78 계약:** generic/current_source/product_integration 증거를 별도 수락조건으로 판정하고 JSON → v401 `--write/--check` → Actions/상세 추적표 최소 정합으로 기록. **B8 COMPLETE 이전에는 B9로 단순 넘어가지 않는다**. B4/B5/B6/B1 미완료 축 보존.

장기: 시즌별 G/J/F/O 자동 원본 구축과 최고품질 UI 목록, 대표/선택 장비·티어·무기/주능력치, 캐시/취소/재개, 적응형 최적화/통계, Windows 사용자 실행 범위를 **실제 소비 경로**에서 26 DPS로 확장. 마지막 **ZERO-SOURCE→USER-E2E**는 별도 PASS 필요. 78개 새 Gate/전수 Native, 시즌 DB·효과 엔진 재구현 금지.

## 6. 탐색·권한·인계 사용 절차

필독 순서: [START_HERE](development/START_HERE.md) → [INDEX](development/INDEX.md) → [FILE_MAP](development/FILE_MAP.md) → **[JSON](development/78_ELEMENT_COMPLETION_CONTRACTS.json)** → [생성표](development/78_ELEMENT_STATUS_GENERATED.md) → [상세 추적](development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md) → [v401 정책](development/POLICY_78_ELEMENT_COMPLETION_GATE_V401.md) → [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) → **본 단일 인계** → [v430](development/notes/2026-11-13_p1-v430-b8-four-of-five-new-season-source-bridge-gap.md)/[v431](development/notes/2026-11-13_p1-v431-b8-sealed-season-injection-code-offline.md) → [PROTOCOL](development/PROTOCOL.md)/[DECISIONS](development/DECISIONS.md)/[EVIDENCE_INDEX](development/EVIDENCE_INDEX.md). 해당 함수·실 CI 증거만 필요 최소 대조.

**새 채팅 첫 응답은 반드시 읽기 전용 복원 보고 후 STOP.** HEAD·네 축의 현재 JSON 상태/COMPLETE, v417의 한정 실제 성공, v431 완료 diff, B8 G/L 병목, 재사용 코드/영수증·우선순위·권한 제한을 간결히 보고한다. 사용자가 별도로 `진행`을 승인하기 전 **코드/문서 수정, GitHub commit, Actions/Native/API 원본 수집, 대규모 테스트, main 병합·공식 승격을 실행하지 않는다.**

## 7. 새 채팅에 붙일 최소 독립 복원 프롬프트

> # SIMC SECONDARY OPTIMIZER — v431/B8 78개 요소 독립 복원 (첫 응답 읽기 전용)
>
> GitHub `degong2-code/simc-secondary-optimizer-runner`, 격리 브랜치 `probe/chat-cache-v035-20261024`. 인계 전 소스 HEAD `c512ff15042013f479b659f052393979cdf10e49`는 **문서 커밋 이전 참조값**이다. 가장 먼저 GitHub 실제 최신 HEAD를 조회하고, **최신 단일 인계 `docs/CHAT_CONTINUITY_HANDOFF_20261113_P1_V431_B8_78ELEMENT_READONLY_RESTORE.md`**와 현재 `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json`을 독립 확인하라.
>
> `docs/development/START_HERE.md` → `INDEX.md` → `FILE_MAP.md` → 78 계약 JSON → 자동 생성표 → 상세 추적표 → v401 정책 → `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` → 인계 정본 → v430/v431 노트와 **v431 code commit `922bdb84393db4684f6850a1c50b9faf3209ae9c`**, 관련 Actions 순서로 필요한 범위만 읽어라. 새 인계 정본/JSON 우선, v420/A10의 과거 숫자는 현재로 사용하지 말라.
>
> 제품: **26 DPS(증강·탱커·힐러 제외)**, 목표 ilvl334 또는 수동 최종 T, SimC DPS 최적 **CHMV 절대 rating**; G/J/F/O 시즌별 자동, `B=G+J+F`, `T=B+O`, `c_final=c_base+o`. 특수 고정 L은 G 내 1회, 제작 초도 배분 자유, 장신구 자유 G 밖. 내부 대표 장비/무기/티어4/프로필, 실 DPS·SEM·95%·관측1순위·근접 대안 및 기존 캐시/취소·재개/Windows UI. SimC 효과/APL/proc/DPS 책임, 새 최적화 엔진·장비 추천·전체 DB/별도 인증 Gate 금지.
>
> 인계 전 계약은 generic18/current_source18/product7/historical12, COMPLETE **A8·A9·A10·A11·B2·B3·B7(7/78)**, 다음 **B8**, 전체 E2E PENDING. 실제 GitHub JSON에서 다시 계산하라. **B8 historical PASS, generic/current/product PENDING**. v417 KR70783 Survival Hunter 기본 4pc 제품 SimC Native3+12 성공([#43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756)), G2850/J92/F165/O0/T3107, DPS178334.86/SEM298.61; **선택 특수·장식 충돌 실증 아님**.
>
> v431은 이미 **v101의 같은 시즌 gear+tier source 두 문서 주입 및 v098의 SHA 결합 source 전달, catalyst 5→4 시 구 70575 fallback 차단**을 실제 구현. [v187 #43428273777](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43428273777) 16PASS·관련36PASS, 신규 Native0. **재구현 금지**. 현재 `v098.build`는 `season_profile_inputs`에서 nonempty special_items/embellishments를 여전히 차단한다. 선택된 물리 장비·exact G/L/J/F/O/B/T/프로필/installed SHA·캐시 identity를 연결하기 전 차단을 해제하지 말라. B8 G/L 연결과 최소 오프라인·실제 1개 사용자 선택 Native만 다음 `진행` 이후. 새 시즌 원본·과거 70575 합성/실 70783 혼동 금지.
>
> 먼저 **최신 HEAD, 네 축 PASS/COMPLETE, v417 실증 범위, v431 실제 구현/CI, B8 정확 병목, 기존 기능·캐시/영수증 재사용, 단기·장기 순서, 미확인/권한**만 보고하고 **STOP**. 별도 `진행` 전 코드·문서 수정/커밋/Actions/Native/API 수집/공식 승격 금지. `main`·v003 immutable·Project UI/Work OS/WEQUIP 권한 제한 보존.

**END — 인계 기록만 작성, B8 구현·완료 판정 및 Native 추가 없음.**
