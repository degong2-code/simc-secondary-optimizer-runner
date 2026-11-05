# SIMC SECONDARY OPTIMIZER — P3-FK 단일 후속 인계 정본 (2026-11-05)

**신분:** GitHub 격리 개발·읽기 전용 새 채팅 복원용. 승인 설계 v1.4.3 교체 / Project Sources 실제 등록 / Work OS 공식 승격 / 원본 제품 v016 직접 통합이 아니다. **최종 목적은 개별 보석·영약 기능이 아니라 다음 시즌과 26 DPS 전체에 재사용되는 단일 Environment Build + DPS 최적화 엔진**이다.

## 0. 읽는 순서·기준 SHA

1. GitHub `degong2-code/simc-secondary-optimizer-runner`의 **격리 `probe/chat-cache-v035-20261024`와 `main` HEAD를 독립 조회**. 본문 작성 직전 격리 `1697512f852f58c6a71eba5ec9816844beb11b9c`, main `07133e0aaf738d6e4816a6486057b1cd49c018de`. **이 문서가 커밋되면 HEAD는 바뀌므로 숫자를 최신값으로 간주하지 말 것.** 마지막 실제 제품 코드 커밋 **`b25d827ef411e437d352b5ef857f45e5c7fa902a`**; 뒤의 `d4aaa559`/`1697512`는 P3-FJ 문서/영수증 반영.
2. **이 문서 → [PROTOCOL](development/PROTOCOL.md) → [INDEX](development/INDEX.md)의 E3/E2/E1 및 C1~C4** (필요 시 A1~A3/B2~B3/D1~D2) → [CURRENT 최상단](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) → [개발자 실행 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md).
3. 최신 [P3-FJ](development/notes/2026-11-05_p3-fj-intrinsic-default-gem-layout-connect.md), [P3-FI](development/notes/2026-11-05_p3-fi-mandatory-special-gem-correction.md), [P3-FH](development/notes/2026-11-05_p3-fh-partial-observed-flask-auto-selection.md), [P3-FG](development/notes/2026-11-05_p3-fg-default-season-install.md), [P3-FD](development/notes/2026-11-05_p3-fd-original-jf-component-install-bridge.md), [P3-FE](development/notes/2026-11-05_p3-fe-v217-original-source-relation-install.md); E3/E2/E1 계약에 필요할 때만 P3-EU/ET/EV. 실제 코드·원본·실 Actions/Native 영수증과 SHA 대조. [기존 P3-EV 인계](CHAT_CONTINUITY_HANDOFF_20261105_P3_EV_ENGINE_INSTALL_RESTORE.md), 과거 [상세 INDEX](development/HISTORICAL_INDEX_20261105_PRE_LIBRARY.md)는 역사 참고만. 이전 연구 전체 재감사 금지.
4. **권위:** 최신 사용자 직접 결정 > 승인 [v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md)의 비충돌 부분 > 실제 GitHub 코드·원본/SHA·Actions/Native > CURRENT/INDEX/이 인계. 최고품질의 **동일 효과군 발견 최고 관측 효과**는 충분; 다른 효과군 혼합 비교 금지, 전체 품질/별도 사용조건 인증 Gate 추가 금지. P3-FH의 '특수보석 없는 일반보석-only 기본 장착' 제안은 [P3-FI](development/notes/2026-11-05_p3-fi-mandatory-special-gem-correction.md)에서 철회됨.

## 1. 최종 제품·현재 완료 Gate

사용자는 직업·전문화·종족·특성, 목표 ilvl(기본 334) 또는 기름 포함 수동 최종 CHMV `T`, 장신구2, 선택 특수장비/장식 최대2, 검증 소모품/보석·전투조건을 설정한다. 일반 장비·주능력치·무기·티어4는 내부 대표 프로필. **현재 장비 스탯 재분배/전 시즌 장비 DB/장비 조합·파밍 추천 아님.** 딜러 **26 전문화**만; 증강·탱·힐 제외. SimC가 APL·효과/proc·DPS를 계산. 결과는 치명/가속/특화/유연 **최적 절대 rating**, 비율, DPS·SEM/오차, **95% 판정**, 관측 1위와 통계적 우위의 구별, 실질적으로 다른 근접 대안, 캐시·취소·재개.

**완료 Gate (아직 미달):** 하나의 일반 웹앱 `v216 Environment Build`가 새 시즌 원본에서 대표 방어구·무기·티어4와 **G/J/F/O 전체**를 검증·구축 → 기존 `v222`의 `B=G+J+F, T=B+O, c_final=c_base+o` (수동 최종 T 우선, L/E/O 중복 방지, 장신구 자유 G 밖) → `v220/v196` 정책 A 검증 최고품질 선택지 발행 → `v212/v217` 버전화 설치·READY/T1. 실제 READY가 확인되면 기존 `v139/v098→v096/v094` 적응형 SimC를 제품 메인 경로에 결합한다. **특수보석 정확히 1개 실제 장착 + 일반보석 N개; J는 일반보석 명목 CHMV 합계만**. 특수보석의 비스탯 효과는 SimC가 처리한다.

**T1 방법:** 현재 시즌을 신규 시즌처럼 **기존 시즌 데이터/캐시/영수증·하드코딩 정답을 입력하지 않는 냉시작**으로 정상 웹앱 하나의 Build를 실행. 시험 전에 실제 신규 시즌 원본 인증 완료라고 주장하지 않는다. 기존 Actions·Native 재사용은 평상시 개발 검증에 허용되지만 이 특별한 cold-start 실험의 입력 증거로 쓰지 않는다.

## 2. Evidence / Integration — 재사용과 실제 결손

| 영역 | 현재 구현·Evidence 및 재사용 | 실제 Integration / 미완료 |
|---|---|---|
| 시즌 장비/G | A1~A3: `v161/v191/v211/v213/v217`; B1~B3 `v229/v230/v232/v251/v277`에서 대표 장비·무기·티어·소켓/기존 exact G 출처 및 봉인/캐시. | 새 시즌 전체 원본과 목표 ilvl의 실제 G는 T1에서 인증 필요. G 참조값은 같은 시즌 검증 범위만; 과거 79×2/334 수치 새 시즌 복사 금지. |
| J / 특수1+일반N | `v221/v266/v268` 물리 보석 ID/명목 rating, `v230` SimC 후보·품질, `v232` 봉인 기본 소켓, `v271.intrinsic_source_plan/arrange`, `v216._fresh_default_intrinsic_gem_layout_from_source`가 **역할별 선택 ID 제공 시** 위치 자동 배치. `P3-FD`는 J owner/소켓 수치의 v222 컴포넌트 연결. | **새 시즌 특수보석 역할/효과의 정확 ItemID 1개 및 동일 효과군 최고 관측 일반보석 N개 자동 source-owner 결정과 `source_selected_gem_roles` 공급 미완료**. P3-FJ synthetic PASS는 실제 J/특수효과/READY 인증 아님. 특수보석 없는 분기 금지. |
| F/O | `v281/v278` 실제 SimC 전/후 F·O 정적 수치·정확 ID 및 봉인 캐시. P3-FH는 **발견된 동일 효과군 중 최고 F** 자동 선택을 웹 opt-in으로 연결. `v222.explicit_no_oil_component`는 **명시적으로 기름 미사용**만 O=0 증명. | 실제 신규 시즌 F/O 영수증과 사용자 선택 일치 필요. 선택 기름 손/무기 조건 검증; 미관측 O를 0으로 단정 금지. F151·Phoenix Oil +16/+17 과거 오염 의심값 새시즌 하드코딩 금지. |
| 예산/설치 | `v222.preprofile_budget`; P3-FD J/F original 컴포넌트와 P3-FG의 **무마부·선택 특수장비 없음/명시 F + O0 기본환경**에서 Python provider 없이 원본 G/J/F가 일치하면 조건부 설치. `v212/v217` 버전화 봉인·재개/무결성 구현. | 합성 설치와 실물 시즌 READY 별개. 유효한 모든 원본/옵션이 없는 경우 STAGED/PENDING 유지. 검증 안 된 G/J/F/O나 신규 시즌의 T1 완료 미증명. |
| 정책 A 선택지 | `v220.decide`의 4-family (`source_relation/simc_input/product_input/chmv_budget`), `v196` 준비, `v212` source identity 검사·조건부 발행. P3-FE는 봉인 `v217 source_relation` 재사용. | 나머지 3-family 실제 적용 근거/제품 UI 등록은 선택 아이템별 미완료; 선택 항목만 보류, 검증된 기본 환경을 막지 않음. |
| 사용자 DPS | `v143/v139/v098` 대표 프로필·26 DPS, `v096/v094` 적응형 DPS/캐시/취소·재개/95% 통계 및 UI 기반. | 실제 새 시즌 READY에서 일반 유저 입력→프로필→DPS→결과까지 단일 제품 end-to-end 미완료. 새 최적화 엔진 금지. |

**판정:** 소켓 배치·영약 자동 선택·예산 산술·조건부 설치 = `REUSE`. **J 특수/일반 보석 source-owner 선택 → v216/프로필 연결 = `CONNECT` 우선**; 실제 역할 원본이 부족한 것만 `EXTEND`, 새 효과 인증기/보석 엔진·전 전문화 전수 Native 반복은 `STOP`. 실제 원본 부재와 기존 원본이 UI/공식 예산에 연결되지 않은 상태를 분리.

## 3. 실제 검증 증거·범위

- **최신 격리 `1697512f852f58c6a71eba5ec9816844beb11b9c`:** [focused #42043523321](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42043523321) **270 PASS/0 FAIL + DEV_LEDGER_PASS**. 마지막 제품 코드 `b25d827`에 대한 [focused #42042650903](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42042650903) **270 PASS/0 FAIL**. [v212 #42042650855](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42042650855) Ubuntu·Windows 각 **452 tests=448 PASS/4 SKIP, Native0**, [v113 #42042650890](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42042650890) 양 OS **217 PASS**, [v181 #42042650914](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42042650914)와 [v182 #42042650773](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42042650773) SUCCESS. 뒤의 문서 커밋은 focused만 자동 수행할 수 있으니 새 채팅에서 exact HEAD별 영수증 재조회.
- **코드 blob SHA (위 격리 HEAD):** `v216=e08dcae75962b68e0834795c2516a38a1e23c35d`, `v271=01be0ad2b510ce3235072fa1a960d10a98972eb0`, `v212=987cee3bc742c9f73a2a1486853b6ff0ca9b3047`, `v222=35a3631cba616df9518ad6cc4c73f07130e5a624`, `v220=1d7e2cd1cf389b56067d27603080c6aef511122a`, `v196=430e9925394c27d5e38f0e20174243aea5c85701`, `v217=d8993b4f6e1af97b6a2149c3b39062660a5579b8`. 최신 HEAD에서 다시 확인.
- **역사 Native(동일 조건 한정):** [P3-BX #41601140696](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41601140696) 보석 입력/소켓 사례 4/4; [F/O #41666305288](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666305288), [#41666925906](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666925906) 기존 pinned SimC·선택 아이템 조건 관측. 모두 GitHub 성공 상태 재확인; 다른 게임 빌드나 신규 T1로 전용 불가. **P3-FJ부터 본 인계까지 새 SimC Native·게임 HTTP 0**, 실제 신규 시즌 READY/T1 0.
- **제품 원본** `v016_SCENARIO_CONTRACT`은 사용자 보고 계보이며 동일 GitHub 격리 코드에 직접 통합된 원본 바이트·영수증으로 확정하지 않음. 코드/합성 테스트 PASS, 역사 Native PASS, 실 신규시즌 인증, 원본 제품 승격의 신분을 구분.

## 4. 다음 과제·속도와 효율

**단기 P1 (최소 묶음):** INDEX C1/C2/C3/C4 → E1/E3를 먼저 조회. 동일 시즌 `v221/v266/v230` + SimC 원본에 이미 **특수보석 역할/정확한 ID** 증거가 있는지 확인해 `REUSE/CONNECT`; 같은 효과군 일반보석 최고 **관측** ID/명목 rating을 선정해 `v232` 실 소켓 + `v271` 기존 자동 배치로 `v216.source_selected_gem_roles` 전달. 부족한 실제 역할 증거만 최소 `EXTEND`; ID 추정·기존 시즌 하드코딩 금지. 필요하면 해당 원본만 좁게 수집/Native 검증하고 기존 영수증/캐시 우선.
 
**단기 P2:** 같은 웹앱에서 위 J를 G/F/O 기본 owner와 연결하고 `v222→v220/v196→v212/v217` 정상 READY 준비. 검증된 기본 환경과 선택형 정책 A 발행의 완료 판정을 분리하고, 필요한 범위의 동결/재개·입력 변조·오류 원문을 최소 focused 회귀. 그 뒤 정식 **cold-start T1**을 수행해 생성된 봉인 원본·예산·선택지·프로필을 검증; 실제 실패는 원문과 missing owner만 명시.
 
**장기:** 실제 환경 READY 이후 `v139/v098/v096/v094` 사용자 26 DPS 최적화/E2E·95% 통계·근접 대안·캐시·취소 재개를 완성한다. 시즌별 숫자 수동 고정·새 프로필/효과/APL/최적화 엔진·전수 장비 DB·SEM 과잉정밀화 금지.
 
**매 작업 자가검증:** “**이 작업이 다음 시즌에도 동일하게 작동하는 하나의 엔진 완성에 기여하는가?**” → 기능 INDEX·코드·SHA·증거 선조회 → Evidence vs Integration 분리 → `REUSE/CONNECT/EXTEND/NEW/STOP` 결정 → 독립 작업 묶기 → 동일 조건 기존 PASS/Native/캐시 재사용 → 추가 HTTP/Native/Actions·메모리/I/O·실행시간·복잡도 평가. 구시즌 데이터로 새 시즌 인증/성공률 보간 금지.

## 5. 이번 인계 실제 반영·미승격/권한

**이 P3-FK는 문서/인계 전용**: PROTOCOL의 현재 단일 진입점, INDEX G1/G2 및 DEV.CONTINUITY, CURRENT 최상단, 개발자 실행 노트 상단, P3-FK 노트와 본 단일 인계 정본을 격리 브랜치에 갱신한다. P3-FJ 제품 코드·소켓 엔진/봉인 원본은 그대로, 기존 인계·실패/Native/Actions는 보존. **신규 코드·Native·게임 HTTP·T1 없음.** 실제 커밋 SHA/인계 문서 CI는 최신 HEAD에서 별도 독립 조회.
 
**미반영·미승격:** 실 J role selector, 전체 시즌 G/J/F/O 원본 인증, 실제 정책 A 항목 발행, 단일 웹 READY/T1, 26 DPS 사용 E2E. `main` 병합·v003 immutable·원본 `v016` 바이트/승인 v1.4.3 수정·Project Sources/Instructions 실제 적용·공식 Work OS M0/Shared State·MAIN/WORK 권한·주 제품 개발 채팅 소유권 변경 전혀 없음. **새 채팅 첫 답변은 읽기 전용 복원 보고 후 STOP**; 사용자 `진행` 전 코드/문서 변경·실행 금지.

## 6. 새 채팅 시작 프롬프트

```text
SIMC SECONDARY OPTIMIZER를 읽기 전용으로 독립 복원하라.

GitHub=degong2-code/simc-secondary-optimizer-runner
격리 브랜치=probe/chat-cache-v035-20261024
최신 단일 인계=docs/CHAT_CONTINUITY_HANDOFF_20261105_P3_FK_ENGINE_FIRST_RESTORE.md

먼저 격리 브랜치와 main 실제 HEAD를 독립 조회한다. 읽기 순서: 위 P3-FK 단일 인계 → docs/development/PROTOCOL.md → docs/development/INDEX.md 기능 E3/E2/E1과 C1~C4(필요할 때만 A/B/D 등 확장) → docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md 최상단 → 개발자 실행 노트 → 최신 P3-FJ/FI/FH/FG/FD/FE 및 필요한 P3-EU/ET/EV → 실제 v216/v271/v221/v266/v230/v232/v222/v220/v196/v212/v217 코드·봉인 원본 SHA·Actions/Native 영수증. 기존 연구 전체를 처음부터 재조사하지 않는다.

최종 목표는 특정 시즌 보석·영약 숫자 확정이나 개별 기능 구현이 아니라 26 DPS 및 다음 시즌에도 공통 작동하는 '하나의 환경 자동 구축·적응형 SimC DPS 최적화 엔진' 완성이다. 기본 334 ilvl 또는 사용자 수동 최종 T에서 미래 CHMV 최적 절대 rating, 95% 판정·관측 1위·근접 다른 대안 및 캐시·취소·재개를 제공한다. 현재 Gate는 정상 웹앱 v216에서 새 시즌 대표 장비·티어 G/J/F/O 검증 → v222 B/T → v220/v196 정책 A 실제 선택지 발행 → v212/v217 설치 READY/T1. 특수보석은 정확히 1개 실제 장착하고 일반보석 N개의 명목 2차 rating만 J에 포함한다. P3-FJ는 이미 역할별 ID가 공급되면 v232/v271로 위치를 자동 배치하지만 새 시즌 역할별 ID 자동 선정과 실제 T1은 미완료다. P3-FH 관측 최대 F는 동일 효과군 한정이다. 실 데이터 미인증을 합성 PASS로 대체하지 않는다.

매 작업 전 INDEX의 기존 자산, 원본 바이트/기존 봉인/Actions/Native/코드 및 캐시를 먼저 조회한다. Evidence와 Integration, 진짜 자료 부족과 기존 소스 미연결, optional 미검증과 core 차단을 구분하고 REUSE/CONNECT/EXTEND/NEW/STOP으로 결론낸다. 독립 작업은 논리적 묶음으로 처리하고 동일 조건의 기존 PASS·Native·캐시를 재사용한다. 중복 HTTP/Native/Actions·메모리/I/O·실행시간·구조 복잡도를 점검한다. 매번 '이 작업이 다음 시즌에도 동일하게 작동하는 하나의 엔진 완성에 기여하는가?'를 자가검증한다. 다른 시즌 정답 하드코딩/기존 환경 영수증을 신규 cold-start 증거로 주입/새 효과 엔진이나 전수 Native 반복 금지.

**첫 응답에는** 실제 양 HEAD, 최신 제품 코드와 SHA, 핵심 Actions/Native의 정확한 적용 범위, 최종 제품 목적과 완료 Gate, Evidence/Integration별 완료·미완료, 현재 최소 병목·더 효율적인 대안, 간결한 단기·장기 로드맵, 미반영·미승격/권한 제한을 보고한다. 보고를 마치면 즉시 STOP한다.

사용자가 명시적으로 '진행'이라고 하기 전까지 개발·코드/문서 수정·GitHub commit/push·신규 수집·CI/Actions/Native/테스트 실행·공식 승격을 절대로 시작하지 않는다. main/immutable v003/원본 v016/Project UI/Work OS·주 개발 채팅의 권한은 바꾸지 않는다.
```
