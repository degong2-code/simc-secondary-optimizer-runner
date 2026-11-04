# SIMC SECONDARY OPTIMIZER · P3-CV · 2026-11-04 인계 정본

**이 파일은 새 채팅의 단일 진입점이다.** GitHub 실제 격리 브랜치와 main HEAD, 원본 코드, Native/Actions 증거를 **독립 재확인**하라. **첫 답변은 읽기 전용 복원 결과와 단·장기 로드맵만 보고하고 사용자 “진행” 전에는 코드·문서 수정, 신규 데이터 수집, 테스트/Native/Actions 실행, 권한 승격 금지.**

**작성시 코드·증거 기준:** [GitHub 격리 브랜치](https://github.com/degong2-code/simc-secondary-optimizer-runner/tree/probe/chat-cache-v035-20261024) HEAD `cfdaee714d309113e42d400cb3c5d789c95ad14b`, `main` `07133e0aaf738d6e4816a6486057b1cd49c018de`. 최신 실 코드 시험 커밋 `2b427f8cfd42…`, 그 뒤 P3-CU 기록 1회만 추가(실행 코드 변경 없음). **인계 문서 커밋 후 HEAD는 달라지므로 고정 SHA를 현 HEAD로 주장하지 말 것.** 이 인계 자체는 데이터/Native/테스트를 실행하지 않는다.

## 1. 최신 목표와 규칙

- **단일 재사용 엔진**: 26개 DPS 전문화(증강 기원사·탱커·힐러 제외), 미래 목표 ilvl(기본 334) 또는 사용자 수동 최종 T에 대해 치명/가속/특화/유연 **최적 절대 rating**을 SimC DPS로 찾는다. 결과는 관측 1순위, 예상 DPS·SEM·오차·95% 우위(전역 최적 증명 아님), 비율, 실질적으로 다른 근접 대안. 캐시·취소·재개 필수. 장비 추천·파밍 경로·시즌 전수 DB 구축이 아니다.
- **단일 사용자 흐름**: 직업/전문화/종족/특성, 목표 ilvl/최종 T, 장신구 2개, 선택 특수장비, 장식 최대 2개, 보석·영약·별도 기름·음식·전투조건 → 프로그램이 대표 일반 장비·주능력치·무기·4티어와 SimC 프로필 내부 구성 → 기존 적응형 DPS 실행. 업로드한 현 장비/현 rating을 기본 목표 예산으로 복사하지 않는다.
- **시즌 전체 자동 구축**: 같은 시즌 증거의 **G+J+F=B, T=B+O, c_final=c_base+o**. 수동 최종 T 우선(`B=T-O`). O는 비자유분배·`gear_*`에 한 번만, L은 G 안에 이미 포함된 하한, E 중복 방지, 장신구의 고정 스탯은 자유 G 밖, 제작 초기 50:50은 L 아님. 비승인/다른 시즌 79×2 B, J138, F165, 기름 +16/+16을 새로운 시즌의 검증값으로 복사하지 않는다. exact Native G는 선택적 정밀 경로이며 필수 전수 Gate 아님.
- **Policy A**: 정확한 아이템 ID/빌드/사용 조건/SimC 입력/CHMV 소유권이 검증된 선택지만 추가 수동 승인 없이 등록; 동일 효과·적용 범위·모든 수치에서 높은 품질이 열등하지 않음이 입증될 때만 최고 품질로 중복 제거. 일반 임시 마부 제외, **기름은 독립 옵션**; 영구 마부 포함. 시즌 특수 모듈은 별도 ON/OFF. SimC가 효과·proc·APL·DPS를 담당하므로 자체 효과 엔진/독립 효과 인증 Gate를 만들지 않는다.
- **특성 vs 정적 예산**: [v080 Native](V080_STATIC_CHMV_TALENT_SEPARATION_NATIVE_ACCEPTANCE.md)의 톱니날 촉은 gear crit 700→buffed 728, 600→624를 확인. 특성 버프가 static CHMV의 B/T를 초과해도 역산하거나 특성별 `gear_*` 예외를 추가하지 않는다. 사용자가 겨울의 축복을 합리적 +1 원인으로 제기했고 영약 1품질 +1 차이는 **후순위 보류**. 새로 발견하는 필연적 수치 모순은 깊은 재조사 전에 **사용자에게 질문**한다.
- **권위**: 최신 사용자 직접 결정 → [최신 승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md)+비충돌 v1.4 계열 → 실제 코드/원본/Actions·Native → 과거 인계. 오래된 v1.4.1의 “27 DPS(증강 포함)”, 고정 6개 보석/J138/특수보석 위치 등은 새 기준이 아님. 최신 사용자 직접 결정이 엔진 우선·증거 재사용·1pt 후순위를 승인했다.

## 2. 복원 순서 (기존 결과 선조회)

1. GitHub `degong2-code/simc-secondary-optimizer-runner`의 격리 `probe/chat-cache-v035-20261024` **실제 최신 HEAD**, 별개 `main` HEAD 확인. 이 인계 문서→[PROTOCOL](development/PROTOCOL.md)→[기능별 INDEX](development/INDEX.md)→[최신 P3-CU](development/notes/2026-11-04_p3-cu-zero-history-budget-user-target.md) 및 [P3-CT](development/notes/2026-11-04_p3-ct-representative-oil-product-bridge.md), [P3-CN](development/notes/2026-11-03_p3-cn-real-source-integration.md)→[CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md)→[개발자 실행 노트](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md)→[v1.4.3 승인 설계](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) 순으로 읽어라. 이전 [P3-CJ 인계](CHAT_CONTINUITY_HANDOFF_20261103_P3_CJ_ENGINE_EVIDENCE_FIRST_RESTORE.md)는 역사 문맥.
2. INDEX Capability `TIER.SEASON / GEAR.SEASON / G.NUMERIC / J.GEM / F.FLASK / O.OIL / BUDGET.GJFO / SOURCE.SEAL / PRODUCT.E2E`별 최종 note와 **원본 영수증, 실제 코드**를 같은 빌드·옵션·시점 기준으로 대조. 현재 필드의 PENDING/false를 기존 증거 부재로 간주하지 않는다.
3. 주요 연결 코드: `v216` 단일 normal Environment Build·최초 수집/zero-history; `v217` SHA stage/cache; `v190/v280/v281` 물리 ID→use spell→SimC relation; `v285/v286/v232/v167/v274/v191` 대표 무기와 기름 장비 조건·컴파일; `v233/v234/v236/v277` G; `v101/v139/v271/v270` 실제 보석/가변 소켓; `v269/v278` Native F/O 정적 delta; `v222/v262/v091-v093` 회계·O 중복 방지; `v212/v098/v094-v097` 정책 A·대표 사용자·기존 적응형 SimC·캐시·95%·취소/재개. 원본 제품 `v015/v016`은 **사용자 보고 기반**이며 정확한 원본 바이트와 영수증을 확인하기 전 직접 병합 완료로 쓰지 않는다.
4. 아래 Actions는 **역사 영수증**이며 이 인계를 위해 반복 실행하지 않는다. 최신 코드 시험 HEAD와 변경된 문서 HEAD를 별도 표기한다.

## 3. 확립된 구현·원본 증거 / 실제 남은 연결

| Capability | REUSE 가능한 실측·코드와 영수증 적용 범위 | CONNECT / 정말 부족한 증거 |
|---|---|---|
| 원본→단일 Build/대표 티어·G | `v216/v217/v274/v191/v275` cold-start 소스·SHA·원래 컴파일, 시즌별 대표 장비/티어/`v233/v277` G Native pipeline; `v222` 동일 빌드 정적 G nearest-10 회계. P3-CF 13×5 tier **65 물리 후보**는 모든 시즌 G 인증 아님 | 한 새 시즌·목표 ilvl의 실제 대표 G 또는 유효 시즌 참조를 입증해 자동 source → budget evidence로 연결, 전체 제품 신규 설치/EMPTY 상태 E2E 아직 미실행 |
| J 보석 | `v271` 물리 보석·가변 소켓, `v216` 기존 J 연결, 실제 [P3-BX Native #41601140696](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41601140696) **4/4**에서 gem 240906 Crit+16/Haste+8 | Wago 정적+16/+7과 Native+16/+8의 +1; 그대로 J24 공식 인증 금지. 새 시즌 실제 소켓/보석 품질·예산 근거가 필요한 범위만 보완, 사용자 지정 낮은 우선순위 수치 심층조사 유예 |
| F 영약 | 실물 [P3-CN #41661212083](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41661212083): 물리 Flask23, SimC 정확 Item ID16, on-use 일치. [P3-CO Native #41666305288](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666305288): Shattered Sun 품질2 치명+165. [P3-CP Native #41666925906](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666925906): 품질1 치명+151. `v281→v216→v278` 실제 ID-based measurement 연결 | 정적 delta 관측 ≠ 전체 품질 효과·사용조건 동등성 인증. 높은 품질 자동 선택/정확 F 소유권/사용자 옵션 발행 미완성. +1 차이 조사 후순위 |
| O 기름 | P3-CN 임시 마부 exact SimC ID **12는 숫돌 혼재**. [P3-CR 실제 Wago #41732744145](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41732744145): Phoenix/Dawn oil 주문 Class2/InvTypeMask73572352/SubclassMask983039. `v285` source 연결, `v286` 선택 대표무기 `v232/v167` 실제 class/subclass/slot 대조 후 내부 source-only 후보. P3-CP Native Phoenix Oil 품질2 한손 Crit+16/Haste+17, P3-CO Dawn Oil 정적0(비정적 가능). `v091` O를 gear 주입에 한 번만 반영 | **마스크 일치 ≠ 최소 무기 ilvl/실제 손·동일 효과·공식 O 승인**. 냉법 특성으로 증가한 가속 +1을 정적 O 기본값으로 잘못 고정 금지. 무기 1개·쌍수의 실제 효과·예산·선택지 소유권/재사용 아직 source-only |
| B/T → 사용자 | [P3-CU focused #41744042859](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41744042859): `v216` zero-history가 **기존** `v222.preprofile_budget`로 same-build 내부 `same_build_budget_evidence`·사용자 ilvl/수동 `final_T`를 보내고 `preprofile_budget_arithmetic_unadmitted` 반환. `B=G+J+F`, `T=B+O`, 수동 최종 T 우선(`B=T-O`), L/E/O 검증. **178 PASS/0 FAIL**, 합성 증거의 순수 회계와 연결만 입증 | 실제 소스/Native 영수증 **→ 신뢰할 수 있는 같은 시즌 budget evidence 자동 생성/인증** 미완성. P3-CU의 수동 `same_build_budget_evidence` 필드를 사용자에게 요구하지 말고, 산술 후보를 READY로 승격하지 말 것. `v098` 실제 세션 및 `v094` adaptive DPS E2E 미연결 |
| 제품/통계 | `v098` 목표 기반 사용자 프로필, `v094` 기존 적응형 SimC·SEM·95%·실질 대안·캐시/취소/재개 코드 및 과거 범위 시험 재사용 | **정상 1회 사용자 입력→검증된 시즌 환경→등록 목록→내부 프로필→실제 SimC DPS/SEM/95%/대안/재개** E2E 없음. 전 26 DPS Native 전수와 새 엔진은 금지 |

**중요:** 원본 물리 ID/SimC 관계/마스크·개별 Native Delta·회계 함수는 여러 범위에서 **이미 증명**, 새로 만들 항목이 아니다. 진짜 병목은 (A) **증거가 있는 값에서 실제 동일 시즌 G/J/F/O 검증·품질/무기 조건까지 승인 가능한 범위를 좁히기**, (B) 검증된 결과를 기존 `v222`·정책 A·`v098/v094`의 **하나의 사용자 흐름**으로 연결하기. 개별 소모품 효과를 독립 모방하거나 전수 DB/Native를 새로 만들지 않는다.

## 4. 최신 CI·Native 영수증의 범위 구분

- **P3-CU 최종 코드 HEAD `2b427f8cfd42…`**: focused [#41744042859](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41744042859) **178 PASS/0 FAIL, DEV_LEDGER_PASS**. 같은 HEAD [v212 #41744043347](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41744043347) Ubuntu/Windows 각 440 PASS, [API #41744043084](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41744043084) 양 OS 각207 PASS, [UI #41744042990](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41744042990) 양 OS, [Windows #41744043111](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41744043111) 3.12/3.14 각142 PASS. **모두 오프라인 계약/회귀**, 신 시즌 실측/전체 E2E 합격 아님. 해당 CI 후의 HEAD `cfdaee...` 변경은 문서 3개뿐임.
- **실물 원본**: [P3-CN #41661212083](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41661212083) 물리 ID↔SimC 출처, [P3-CR #41732744145](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41732744145) 같은 빌드 무기 마스크(HTTP1, Native0).
- **실 Native**: [P3-CO #41666305288](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666305288)와 [P3-CP #41666925906](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666925906) **두 묶음 총 Native6**, pinned 12.1.5.70575 / SimC `710c2408…` / 대표 Frost Mage 한 프로필에 한정. J [P3-BX #41601140696](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41601140696) Native4/4는 보석·소켓 범위. **다른 시즌·스펙 또는 전체 사용자 경로 자동 인증 아님.**
- P3-CT [focused #41742683870](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41742683870) 172 PASS 및 P3-CS 166 PASS는 **직전 범위/역사**. 이 인계에서 HTTP/Native/Actions/테스트 실행 **없음**.

## 5. 장·단기 로드맵과 작업 효율

- **즉시 P1 (CONNECT, 새 수집기가 아님)**: 기존 `v216/v274`의 실제 봉인 G/J/F/O 소스와 Native 후보에서 정확한 같은-build·목표 ilvl·quality/hand/weapon 조건·L/E/O 소유권이 확인된 **예산 evidence 생성/검증 결과를 기존 `v222`에 자동 연결**. 부족/모순 항목만 source-specific PENDING, 정상 기본 환경을 과도하게 차단하지 않음. 이 시점에서 v098 사용자 프로필을 실제로 만들 때 source-only 후보와 공식 수치를 혼동하지 않는다.
- **즉시 P2**: 검증된 최고 품질 선택지를 기존 `v212` Policy A로 자동 발행, 일반 임시 마부 제외/기름 별도, G/J/F/O·B/T/대표 무기·4티어·기타 고정 효과를 사용자 `v098` 프로필에 주입.
- **단기 P3**: 완결된 동일 시나리오 1개부터 `v094` 적응형 SimC(95%·관측 최고·근접 대안)·정적 JSON2 rating·캐시·취소/재개·로그를 E2E로 실행. 기존 Actions/Native/같은 시즌 캐시를 재사용하고 이 접합부에 한정된 최소 검증, 추가 Native가 정말 필요할 때만 1건부터.
- **장기**: **오직 하나의 정상 v216 Environment Build**를 실제 신설 설치·빈 캐시·과거 수집 증거 없는 통제환경에서 실행하되 Wago/Blizzard/SimC 등 **정상 신규 외부 수집 허용**. 동일 엔진으로 시즌 G/J/F/O→B/T→검증된 선택지→26 DPS 공용 대표 SimC→적응형 최적 DPS/SEM·95%·대안·중단/재개. 새 엔진/전수 Native·SEM 미세 개선/전수 장비 DB는 우선순위 아님.
- **매 작업 비용 통제**: INDEX/코드/원본/영수증 선조회→`REUSE/CONNECT/EXTEND/NEW/STOP` 구분, 독립 작업은 같은 논리 묶음, 1개 노트·INDEX 갱신, 검증 완료의 기준은 **이전에 수행한 동일 범위** 것을 그대로 재사용. 신규 HTTP·Native·CI/중복·I/O/메모리/시간·캐시 무효화·성능을 매번 검토. 정상 제품 통합을 공식 Work OS Gate나 1pt 현상 연구 때문에 차단 금지.

## 6. 실제 반영/권한

- 이번 인계에서 갱신할 것: **이 단일 정본**, `development/PROTOCOL.md` 최신 인계 포인터, `development/INDEX.md`의 `DEV.CONTINUITY`, `development/notes/2026-11-04_p3-cv-continuity-handoff.md`, `CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 상단 포인터, `DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md` 상단 포인터. **제품 코드·승인 v1.4.3 본문은 수정하지 않는다.**
- 인계 파일의 GitHub 커밋이 실제 ChatGPT Project Sources/Instructions 적용, `main` 병합, v003 immutable·제품 원본 v015/v016 승격, 공식 Work OS M0/Shared State·MAIN/WORK 권한 변경을 의미하지 않는다. 새 채팅은 **실제 복원 보고만 하고 “진행” 전 개발 중단**.

## 7. 새 채팅에 그대로 붙여 넣을 시작 프롬프트

SIMC SECONDARY OPTIMIZER 개발을 **읽기 전용 복원**하라. 저장소 degong2-code/simc-secondary-optimizer-runner, 격리 브랜치 probe/chat-cache-v035-20261024와 main의 **실제 최신 HEAD를 각각 독립 확인**하라. 단일 인계는 docs/CHAT_CONTINUITY_HANDOFF_20261104_P3_CV_ENGINE_RESTORE.md 이다. 해당 문서→docs/development/PROTOCOL.md→INDEX.md→P3-CU/P3-CT 최신 노트→CURRENT→개발자 실행 노트→승인 v1.4.3→필요 범위의 코드·원본·Actions/Native 영수증 순으로 선조회하라. 최신 26 DPS(증강 제외), 신 시즌 G/J/F/O 전체 자동 구축, B=G+J+F/T=B+O, 수동 최종 T 우선과 고정 L/E/O 비중복, 가변 소켓·품질·무기 조건·95%·SimC 효과 책임을 적용하라. 기존 P3-CU v216→v222 zero-history 산술은 focused 178 PASS, 과거 실 F/O Native6·P3-CR Wago 무기 mask·P3-BX gem Native4/4는 범위 한정 증거이므로 새 시즌 최종 READY 또는 v098/adaptive E2E로 과장하지 말라. 사용자가 1pt 미세 차이 심층 연구를 후순위로 승인했으므로 특성 buffed rating을 기본 B와 역산하지 말고 새로운 필연적 수치 모순은 깊은 연구 전에 사용자에게 물어보라.

**최종 목표는 개별 아이템/기능 추가가 아니라 26 DPS에서 재사용하는 단일 엔진 완성:** 신규 정상 시즌 Build→검증된 G/J/F/O→B/T→검증된 최고 품질 옵션→사용자 대표 SimC→기존 적응형 DPS·SEM·95%·근접 대안·캐시·취소/재개. 매 작업 전에 개발 INDEX→소스/코드/영수증을 검색해 REUSE/CONNECT/EXTEND/NEW/STOP 분류, 이전 결과/통과 기준과 Native·Actions·캐시를 재사용하고 독립 작업 묶기/중복 HTTP·Native·I/O/메모리/시간 억제. 코드의 PENDING만으로 과거 증거 부재를 단정하지 말라. 새 채팅의 **첫 응답에서는 두 HEAD와 핵심 증거, 완료·미완료·병목·더 효율적인 대안·단/장기 로드맵·권한 경계를 보고하고 중단**해. 사용자가 **“진행”하기 전에는 코드·문서 수정, GitHub 커밋, 신규 수집, CI/Native/Actions/테스트 실행 또는 승격을 하지 마.**
