# SIMC SECONDARY OPTIMIZER — v420 이후 단일 인계 정본 · A10 복원 (2026-11-13)

> **신분:** 기존 주 개발 채팅의 78요소 검토를 새 채팅에서 이어가기 위한 **개발 연속성 문서**. 제품 완성·새로운 Native 검증·공식 Project UI 적용/Work OS 승격 아님. **새 채팅 첫 응답 읽기 전용, 이후 STOP.** 별도 사용자 명시적 \`진행\` 전 코드·문서·Actions·Native 수정/실행 금지.
>
> **정본:** 실제 GitHub 격리 브랜치 \`probe/chat-cache-v035-20261024\`의 \`docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json\`과 자동 생성 상태표. 본 문서는 문서 작업 **직전 소스 HEAD \`0a80a972d5a22cde018aa8e07d7305dff04fc85b\`**를 기준으로 작성했다. 문서 커밋 이후 실제 HEAD는 반드시 GitHub ref에서 재조회해야 한다. 당시 \`main\` HEAD는 \`07133e0aaf738d6e4816a6486057b1cd49c018de\` (변경하지 않음).
>
> **기존 인계:** [v406 A8 인계](CHAT_CONTINUITY_HANDOFF_20261113_P1_V406_A8_78ELEMENT_READONLY_RESTORE.md)는 역사 스냅샷. 과거 7/7/0·A8 대기 표기를 최신 판정으로 복원하지 않는다.

## 1. 최종 제품 및 현재 개발 위치

- WoW **26개 DPS 전문화만** 지원: 증강 기원사·탱커·힐러 제외. 목표 ilvl 기본 334 또는 사용자 수동 최종 CHMV \`T\`에서 SimC DPS를 최대화하는 **치명·가속·특화·유연의 최적 절대 rating**과 비율, DPS, SEM, **95%만** 쓰는 통계 판정, 관측 1순위, 실질적으로 다른 근접 대안을 제공. 전역 최적 증명과 관측 최고를 혼동하지 않는다.
- \`G\` 대표 일반 장비/무기, \`J\` 기본 보석, \`F\` 최고 품질 영약, \`O\` 기름 고정 벡터. \`B=G+J+F\`, \`T=B+O\`, \`c_final=c_base+o\`. 새 시즌 G/J/F/O **모두** 출처·실증에 따라 자동 갱신. 수동 T 최우선; L은 G 안에서 고정 하한, E/O 포함 규칙과 중복 가산 금지; 장신구 정적 미관측을 0이라고 단정하지 않는다.
- 일반 사용자는 전체 장비를 고르지 않는다. 직업·전문화·종족·특성, ilvl/T, 장신구 2개, 선택 특수효과 장비, 장식 최대 2, 보석/영약/기름/전투조건 등을 입력한다. 대표 일반 장비·무기·티어 5부위 원본 중 충돌 없는 4pc·SimC 프로필은 내부 구성. 업로드 현재 SimC 프로필은 캐릭터 정보 추출 편의 기능이며 현재 착용 CHMV를 목표로 복사하지 않는다.
- 효과/proc/APL/DPS는 SimC 책임. 사용자 프로그램은 원본 출처, 아이템 ID/옵션, 예산·고정 하한·스탯 숫자 주입/JSON2 정합, 기존 적응형 SimC, 캐시/취소·재개, 저장 스냅샷, Windows UI·결과 조회를 연결. 장비 조합/파밍 경로/전체 시즌 장비 DB, 독자 APL·효과 엔진, 새 최적화 엔진, 별도 효과 인증 Gate를 추가하지 않는다.
- 최종 제품 원본 \`v016_SCENARIO_CONTRACT\`은 **사용자 보고 원본 기준**으로 취급; 실제 원본 바이트·제품 직접 병합 완료와 GitHub 격리 실험을 동일시하지 않는다.

## 2. 검증한 실제 HEAD · 78개 계약

- 확인된 문서 작업 전 HEAD: [0a80a972](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/0a80a972d5a22cde018aa8e07d7305dff04fc85b), 마지막 커밋은 v420 A9 실제 v417 tested SHA 정정.
- 정본: [완료 계약 JSON](development/78_ELEMENT_COMPLETION_CONTRACTS.json) / [생성표](development/78_ELEMENT_STATUS_GENERATED.md); 2026-11-13 [검사 Actions #43397813266](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43397813266) \`completion-policy=success\`, 해당 HEAD에서 실행.
- 78개 중 축별 \`generic=9/78\`, \`current_source=9/78\`, \`product_integration=2/78\`, \`historical=4/78\`; 필수 세 축을 모두 PASS한 **COMPLETE 2/78 = A8, A9**. \`next_review=A10\`, \`full_product_e2e=PENDING\`.
- A1~A7: generic/current_source PASS, 각각 product_integration PENDING. A8: 세 필수 축 PASS 및 역사 PASS. A9: 세 필수 축 PASS, historical PENDING. A10: historical만 PASS, generic/current_source/product_integration PENDING. A11 및 G2도 historical 범위 PASS. 이 숫자는 미구현 기능 개수가 아니며 통합 범위가 좁다는 뜻이다.
- 최신 JSON/CI를 다시 조회해 상태를 갱신할 것. 오래된 [78개 상세 추적표](development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md) 상단의 v402/6개 통계 등은 **시점별 이력**이며 현재 상태가 아니다. 생성표 직접 수정 금지.

## 3. v417 P1 실제 Windows 사용자 실행과 A8·A9 완료 범위

- [v417 원본 노트](development/notes/2026-11-13_p1-v417-bounded-post-bridge-product-e2e-once.md), [성공 Actions #43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756), [Native JSON2/input/receipt artifact #14021859656](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756/artifacts/14021859656). **tested SHA \`89d4810baf5e05f1c5c6f355f39a5f35ca9ec4e7\`**; KR Retail 12.1.5.70783, Survival Hunter ilvl334/일반 보석4/O0, 시즌 **G2850/J92/F165/O0 → B=T3107**, 환경 Native3 + 실제 DPS Native12, 최종 관측 CHMV **373/1078/1491/165**, DPS **178334.8563**, SEM **298.6111**, 선택된 쌍의 명목95% 방향 지지, 전역 최적 미증명. 실제 사용자 세션→대표 프로필→기존 v098/v096/v293 실행→저장 결과 조회. 64회·26개 전문화 전수 아님.
- v417 첫 Windows 시도 [#43393206562](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43393206562)는 Windows 8.3 Temp 경로 오프라인 테스트 오류, 두 번째 [#43393505225](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43393505225)는 구 시험 입력의 설치 시즌 build 누락으로 DPS 전 차단. 수정 후 마지막 성공과 구분하며 실패 회차의 실제 실행량을 성공 15회라고 축소 합산하지 않는다.
- **A8** [v419](development/notes/2026-11-13_p1-v419-a8-runtime-sha-cache-snapshot-evidence.md): 실 바이너리 SHA/버전, 정확 DPS 캐시 identity, 기존 저장 결과/스냅샷 재조회. v417 + [v113 다중 OS 회귀 #43391249405](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43391249405) 재사용. SimC↔게임 빌드 번호 일치 또는 컴파일 계보 인증 Gate **폐기**. 과거 스냅샷 조회에 동일 SimC 재설치/재실행 요구 금지.
- **A9** [v420](development/notes/2026-11-13_p1-v420-a9-simc-source-bytes-scope.md): 기존 v229/v275의 SimC DBC/generated·효과/마부 필수 소스 및 실제 소비 범위를 [v409 60 PASS #43386905854](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43386905854), [v410 80 PASS #43387395448](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43387395448), v417 실 실행으로 재사용. v191 장비후보209/티어65/마부후보772; 후보 수는 품목 전수 승인 아님. 신규 Native/DB2/원본 수집 없이 기능 범위 COMPLETE.
- 과거 결과 스냅샷 \`V106_USER_RESULT.json\`, \`V291_RESULT.json\`/기존 캐시를 재사용한다. WSE는 진단 전용; 시즌 소속은 Blizzard/WCL/활성 raid/M+·동일 빌드 DB2 관계로 자동 판정. 동일 시즌 정적 아이템 캐시는 SimC revision 변경만으로 폐기하지 않고, DPS 캐시는 실제 binary/프로필/장비/후보/O/전투/iterations identity로 구분한다.

## 4. 정확한 다음 검토 A10 — 기존 통합 컴파일

**A10 계약:** \`원본 통합 컴파일\`, 수락 대상 \`v191/v211/v213\`의 필요한 입력·검증·카탈로그 결과. 현 원장 **historical PASS**, 나머지 필수 세 축 PENDING. \`REUSE\`로 시작하고 근거가 부족한 실제 연결만 \`CONNECT\`하거나 최소 \`EXTEND\`. 인계 시 A10을 새로 구현/실행하지 않는다.

- [코드 지도](development/FILE_MAP.md)에서 **\`runner/v274_zero_history_source_compiler_wiring.py\`**를 우선 읽는다. \`NEEDED\` 9항목: \`GEAR_V167\`, \`TIER_V168\`, \`V189\`, \`V190\`, \`GENERATED_PERMANENT\`, \`GENERATED_TEMPORARY\`, \`GENERATED_GEM\`, \`SIMC_V211_SIX_SOURCE_FILES_AND_MANIFEST\`, \`PINNED_SIMC_REVISION\`. \`COMPILER_INPUT_OWNER\`/ \`compiler_input_impact\`는 정확 공급자·컴파일 전용 결손을 표시하며 **각각의 G/J/F/O 수치 검증은 아니다**. [v380 상세](development/notes/2026-11-13_p1-v380-catalog-vs-required-budget-inputs.md).
- 원본 공급은 \`v275_pinned_simc_compiler_inputs.py\`(v229·v189 pinned Git tree/blob·이미 봉인된 6원본+generated 파일 재사용), \`v216_environment_build_coordinator.py::collect_wago_new_season_source\`, \`v276\` 티어, \`v274.discover\`. \`v274.compile_collected\` → **\`v241_fresh_source_stage_adapter.py\`** → \`v191_unified_season_data_update.py::compile_catalog\` → \`v211_enchant_source_effect_classification.py\` → \`v213_source_to_catalog.py::compile_catalog/verify_catalog\`.
- \`v241.source_inputs\`는 동일 game build/SimC revision, 6개 소스 파일 byte SHA/manifest, 역사 J/F budget 혼입 방지를 확인한다. \`v191\`은 source-first 후보, \`v211\`은 비전투 효과 **메타데이터 분류**, \`v213\`은 원본 결합·SHA/시즌/후보 관계 검증이며 **자동 승인·Native·UI READY가 아니다**. \`v216.preflight_new_season_source\`와 이후 \`v212.compile_fresh_installed_environment\`의 \`v213.verify_catalog\`, 설치·예산 소비를 차례로 확인한다.
- **역사적 A10 PASS:** [v383 재확인](development/notes/2026-11-13_p1-v383-a10-a11-g2-archived-native-receipt-reuse.md), [v344 Windows #43114134208](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43114134208) 실 UI \`FRESH_V191_V211_V213_COMPILED_UNADMITTED\` 및 v212 설치, [v343 #43049564271](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43049564271), v417 현재 E2E. **당시 조건 컴파일 성공**은 현재 새 사용자/다른 시즌 9개 모든 파일 SHA/일반성 PASS를 자동 보장하지 않는다.
- **첫 작업:** (1) A9의 확보 원본 범위를 9입력에 매핑 (2) 기존 \`v191/v211/v213\` 테스트와 v241/v274/v216 회귀, v344/v417 stage/manifest 소비 증거를 **테스트 SHA/소스/빌드/옵션 단위** 대조 (3) generic/current_source/product_integration 각 축에서 **확실한 부분·결손** 분리 (4) 불충분한 정확 경계에만 작은 offline 회귀 또는 필요한 최소 실증 (5) JSON 정본 → v401 --write 생성 → v401 --check/필요 최소 CI → 다음 A11. **현재 사용자의 \`source_compilation.missing\`을 확인하지 않았으므로 존재하는 버그/결손을 창작 금지.**
- 실수 방지: 선택하지 않은 임시 마부 전수/효과 인증/모든 26전문화 Native를 새로운 필수 Gate로 삼지 않는다. 완전 catalog 컴파일 의존이 BASE 수치/선택품질과 같은 뜻은 아니며, 실제 필수 연결 결함이 관측된 경우에만 범위를 축소하거나 연결을 보완한다.

## 5. 재사용할 구현·검증, 병목과 순서

- 사용자 입력 \`v113\` → 시즌 자동 소스/Build \`v216/v217\` → 실제 G/J/F/O·B/T \`v222\` → 개인 선택·설치 \`v212\` → 대표 프로필 \`v098/v139\` → SimC \`v096/v094\` → 적응형 \`v290/v291\` → 캐시·중단·재개·스냅샷 \`v292/v293/v106\` → Windows UI. v410~v415의 설치 SHA/선택 특수 L/최종 DPS 정확한 소스 연결을 **재사용**. 실제 v417 범위만 성공으로 표시하고 다른 기능 존재는 미구현으로 되돌리지 않는다.
- **단기:** A10 정확 증거 판정 → A11 단계별 출처·영수증 → B1~ 순차 78요소 증분 검토. 문서 자체 통과 숫자를 채우기 위해 추가 Gate 또는 전수 Native를 만들지 않는다.
- **장기:** 26 DPS 공통 사용자 입력, 시즌 G/J/F/O 자동 갱신, 대표 5티어 중 4pc/무기/주능력치, 최고 품질·선택형 모듈, 수동 T/L/E/O, 저장/캐시·취소/재개, 95%·근접 대안·Windows 실 UI의 실제 연결을 범위별로 완료; 마지막에 별도 엄격 \`ZERO-SOURCE→USER-E2E\` 검증을 통과해야 전체 제품 완성. 미공개 미래 시즌의 원본 수치를 미리 요구하지 않는다.
- **개발 비용:** 동일 시즌 원본 SHA·정적 캐시·Native·Actions·프로필/시나리오 영수증 선조회. 어떤 수정도 중복 API/DB2, Native/캐시, CPU/메모리/I/O/실행시간에 미치는 영향을 검토. 확인된 무효화 범위만 재검증.
- **권한:** 격리 브랜치 문서·허용 개발만; \`main\` 병합, v003 immutable 수정, Project Sources/Instructions 실제 UI 적용, 공식 Work OS M0/Shared State·승격, WEQUIP 런타임 authority, 다른 주 제품 개발 채팅의 소유권 변경 금지.

## 6. 새 채팅의 문서 탐색 순서

1. [START_HERE](development/START_HERE.md) → [INDEX](development/INDEX.md) → [FILE_MAP](development/FILE_MAP.md).
2. **[78 JSON 정본](development/78_ELEMENT_COMPLETION_CONTRACTS.json) → [생성표](development/78_ELEMENT_STATUS_GENERATED.md) → [상세 78 추적표](development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md) → [v401 정책](development/POLICY_78_ELEMENT_COMPLETION_GATE_V401.md)**.
3. [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) → 본 인계 및 v417/v419/v420 → [PROTOCOL](development/PROTOCOL.md)/[DECISIONS](development/DECISIONS.md)/[EVIDENCE_INDEX](development/EVIDENCE_INDEX.md).
4. 실제 A10와 관련된 \`v191/v211/v213/v241/v274/v275/v216/v212\` 함수·테스트·이전 Windows Actions만 집중 열람. 옛 문서/원본/Native 전수 재감사 금지.

## 7. 새 채팅에 그대로 붙여넣는 읽기 전용 독립 복원 프롬프트

> **SIMC SECONDARY OPTIMIZER — 78개 요소 개발 독립 복원 (첫 응답 읽기 전용).**
>
> 정본 GitHub \`degong2-code/simc-secondary-optimizer-runner\`, 격리 브랜치 \`probe/chat-cache-v035-20261024\`. 인계 작성의 소스 기준 HEAD \`0a80a972d5a22cde018aa8e07d7305dff04fc85b\`는 **문서 반영 전 값**이므로 먼저 GitHub에서 **실제 최신 HEAD**를 독립 조회하라. **최신 단일 인계:** \`docs/CHAT_CONTINUITY_HANDOFF_20261113_P1_V420_A10_78ELEMENT_READONLY_RESTORE.md\`.
>
> 순서대로 \`docs/development/START_HERE.md\`, \`INDEX.md\`, \`FILE_MAP.md\`, \`78_ELEMENT_COMPLETION_CONTRACTS.json\`(유일 상태 정본), \`78_ELEMENT_STATUS_GENERATED.md\`, \`ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md\`, \`POLICY_78_ELEMENT_COMPLETION_GATE_V401.md\`, \`docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md\`, 이 최신 인계, v417/v419/v420 노트, 관련 \`PROTOCOL/DECISIONS/EVIDENCE_INDEX\`를 읽고 해당 코드·Actions와 필요한 만큼 독립 대조하라.
>
> 제품 목적: **26 DPS(증강/탱커/힐러 제외)**, 기본 목표 ilvl334 또는 수동 최종 T에서 SimC DPS로 최적 **CHMV 절대 rating** 탐색. \`G/J/F/O\` 모두 시즌별 자동 구축, \`B=G+J+F\`, \`T=B+O\`, \`c_final=c_base+o\`, 정확 L/E/O 중복 방지. 사용자에게 전체 현재 장비를 요구하지 않으며 대표 일반 장비·무기·티어 4세트/프로필을 내부 작성. 장신구2·특수효과 장비·장식 최대2·소모품과 전투조건 선택. 결과 rating·비율·DPS·SEM·**95%**·관측1순위·실질 다른 근접 대안, 캐시/취소·재개/저장 스냅샷/Windows UI. SimC가 proc/APL/효과/DPS 책임. 장비 조합 추천·파밍 경로·전품목 DB·새 최적화 엔진·별도 인증 Gate 금지.
>
> **검증 기준(인계 소스 HEAD):** 78개 중 generic **9**, current_source **9**, product_integration **2**, historical **4**; COMPLETE **A8·A9 두 개**, 다음 **A10 원본 통합 컴파일**, 전체 최종 USER-E2E **PENDING**. 최근 [78 계약 CI #43397813266](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43397813266) success. A1~A7 generic/current_source PASS이지만 제품 통합 PENDING; A10 역사 PASS만 유지. 수치는 최신 GitHub JSON과 대조 후 수정하라.
>
> **P1 v417 실제 Windows** [#43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756) / [Native artifact #14021859656](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756/artifacts/14021859656): tested \`89d4810baf5e05f1c5c6f355f39a5f35ca9ec4e7\`, KR70783 Survival Hunter ilvl334 일반보석4/O0, G2850 J92 F165 O0 T3107, 환경 Native3/DPS Native12, 178334.86 DPS·SEM298.61·관측 CHMV373/1078/1491/165·95% 확인쌍 방향 지지, 저장 조회 성공. 전역 최적·26전문화 전수·전체 제품 완료 증명이 아님. A8은 실제 바이너리 SHA·DPS 캐시/결과 스냅샷, A9는 원본 DBC·generated/마부·효과 파일을 기존 v229/v275·v409/v410/v417 증거로 검토 완료.
>
> 최신 정책: SimC↔게임 빌드 번호 완전 일치/소스-바이너리 컴파일 계보 인증 Gate **폐기**, 저장 스냅샷 우선, WSE는 비차단 진단 전용. 시즌별 G/J/F/O와 정확 사용자 설치 SHA, 정적 캐시 시즌 독립·DPS 실행 정체성 분리를 유지. 과거 27 DPS·증강 포함 문구를 사용하지 말라.
>
> **A10 첫 개발 위치(별도 \`진행\` 이후):** 기존 \`runner/v274_zero_history_source_compiler_wiring.py::NEEDED/COMPILER_INPUT_OWNER/discover/compile_collected\`의 9 컴파일 입력 → \`v275\` source → \`v241\` adapter → \`v191/v211/v213\` 원본 카탈로그 → \`v216.preflight_new_season_source\` → \`v212\` 설치 소비를 추적. [v383 과거 #43114134208](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43114134208) 컴파일 실제 실행, v417 제품 성공 및 기존 tests를 재사용해 A10 각 축 generic/current_source/product_integration을 **서로 독립 판정**. 추가 Native/재수집/새 프레임워크가 아니라 정확 결손만 \`REUSE/CONNECT/EXTEND/REPLACE/NEW/STOP\`로 다루고 다음 A11로 진행. 78개 독립 Gate/전수 Native 금지.
>
> **첫 응답:** 실제 HEAD, 78개 네 축/완료·다음 A10, v417 실제 범위, 구현과 미실증·미구현 차이, 최근 사용자 결정, 기존 코드·원본·Native/캐시 재사용, A10 정확 첫 단계, 단기·장기 로드맵 및 권한 제한을 **읽기 전용 복원 보고**로 작성하고 **STOP**. 사용자가 별도 \`진행\`을 지시하기 전에는 코드·문서 변경, GitHub 커밋, Actions/Native/API·외부 원본 수집, 대규모 테스트, main/Project UI/Work OS 승격을 하지 말라. 주 제품 개발 소유권을 임의 변경하지 말라.

**END — 인계 정본; 실제 개발/통합 PASS 추가 없음.**
