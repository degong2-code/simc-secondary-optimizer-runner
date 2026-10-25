# SIMC SECONDARY OPTIMIZER — CURRENT DEVELOPMENT STATE (지속 갱신)

> **2026-10-25 v076 최신 — DPS 범용 엔진 구조/대표 6조합 감사 PASS (Native 0):** [GitHub Actions #40194330151](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40194330151) SUCCESS, **전체 회귀 412 PASS / 2 SKIP(414건)**. 사용자 지시에 따라 잠행 도적 최적화 반복(v076 F 320 포함)은 **보류하고 범용성 검증으로 우선순위 전환**. 현재 v061~v067 공통 엔진 경로에서 잠행 전용 v068~v075 시험 코드의 **직접 import 의존 없음**을 오프라인 AST로 확인했으나, 전 전문화 Native 범용 동작이 입증됐다는 주장은 금지. 가죽/천/사슬/판금 **4종**, 한손 쌍수/한손+비무기 보조/한손+방패/원거리/양손 쌍수/양손 단일 **6무기 형태**, 민첩/지능/힘 **3주능력치**, 서로 다른 6종족을 포괄하도록 **잠행 도적·비전 마법사·정기 주술사·야수 사냥꾼·분노 전사·징벌 성기사** 대표 시험 매트릭스 설계. 기존 잠행 Native는 증거 재사용, 기존 비전 Mage 자료는 정확한 새 제안 종족/무기 일치가 미확인인 *과거 제한 범위* 증거, 신규 4종은 실제 Native 미실행. 구조 확인으로 **미완료 항목 6건** 기록: (1) v067 외부 프로필 의존/범용 대표 프로필 준비, (2) exact 아이템 정적 variant 선행, (3) v066 프로필당 실제 수치보정 Native 증인 2건 부트스트랩, (4) 무기 형태 자체의 Native 유효성 미검증, (5) 클래스·종족·전문화 조합의 SimC 적합성 미입증, (6) 사용자 최신 탱커·힐러 제외 지시와 승인 Developer Notes v1.2 10장(탱커·힐러 포함)의 제품 정책 충돌. **현재 단기 시험은 DPS 전문화만**, 공식 제품 지원 역할·Project Sources/Work OS 임의 변경 없음; 기존 v061 역할 수용 범위 불변. **다음 v077:** 기존 v055/v061~v067 재사용, 범용 프로필/정적 캐시 readiness/수치보정 최초 Native 연결 경로를 최소 구현, 완전 DB·효과 Gate 금지. [v076 실제 코드·결과·갭 분류](./V076_GENERIC_DPS_ARCHETYPE_SOURCE_AUDIT.md). v075 2 scout PASS는 과거 증거로 보존; 제품 본체 v016 통합·전 전문화 실증·글로벌 최적화는 미완료. 원본 v003/v015/v016·main·Project Sources·Work OS 불변.


> **2026-10-25 v075 최신 — 350 rating 대간격 탐색 재개 및 2후보 실제 Native 검증 PASS:** 첫 [CI #40190557440](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40190557440)은 과거 SimC 출력 절대경로 relocation 증명 오류로 오프라인 단계 FAIL(**Native 0**), 역사 증거 원본 SHA와 경로 독립 stable profile/gear SHA를 분리해 교정. 이후 [Actions #40190657735](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40190657735) **SUCCESS, 전체 회귀 407 PASS / 2 SKIP(409건)**. 사용자 Rogue/Subtlety334·정확한 특성·아이템/장신구2/장식2·Omnium mastery·보석B·Patchwerk300초 원래 계약 유지. **G2847+J138+F165=T3150**, 고정 L=(100,201,0,0), 프로필 수치 보정=(165,0,0,0), 기름 T 외부. 과거 v069~v074 **실제 Native 9결과 SHA 검증 재사용**, 특히 **동일 CHMV인 v073 D 59표본 탐색값 대신 v074 D 319표본 정밀값을 스케줄러 대표로 유지**. 기존 v015 기반 v065 탐색 정책만 재사용하여 350 rating 이동(11.11% T) **신규 SimC 2회(각 60회/59표본)**: E=**1513/913/712/12, DPS 223990.08 ±SEM719.97**; F=**813/913/1062/362, DPS 227079.56 ±SEM895.94**. 정밀 D=1163/913/712/362, DPS224438.68±SEM365.56(319표본) 대비 F 평균 +2640.88 DPS(+1.18%)이나, F는 후보 선택된 **저반복 탐색 값이라 우위 통계 확정 아님**. 2/2 JSON2 정합, 재실행 SHA 캐시 HIT 2/2, 추가 SimC 0. **다음 탐색 간격 권고는 350 유지**(아직 미방문 대간격 후보), 향후 100으로 줄이는 조건은 실험용 제안만 생성하고 사용자 확정 제품정책으로 승격하지 않음. [v075 상세 영수증·수치·교정/한계](./V075_ROGUE_COARSE_CONTINUATION_NATIVE_ACCEPTANCE.md). **다음 v076:** 새 F만 독립 320회 정밀 확인하고 기존 A/D 재실행 없이 비교; 이후 탐색 계속/국소 세분화 결정. 전체 최적해 및 전 전문화 범용화 미완료. GitHub main/공식 Work OS·Project Sources/v003/원본 v015-v016 불변. 사용자 신규 입력 필요 없음.


> **2026-10-25 v074 최신 — 잠행 도적 v073 유망 D후보 독립 320회 Native 정밀 재확인 PASS:** [실제 GitHub Actions #40188874909](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40188874909) **SUCCESS, 회귀 402 PASS / 2 SKIP(404 tests)**. 이전 v069 증인 2건(해당 run 전체 FAIL 보존), v070 공식 1건, v071 첫 scout 1건, v072 독립 320회 A/B 2건, v073 소재가 다른 C/D 두 scout 2건 **총 8개 실제 Native 증거**(원본 source/JSON2/영수증 SHA, 시나리오·SimC identity 검증) 재사용. 공식 **G2847+J138+F165=T3150**, 고정 L=(100,201,0,0), 오프셋=(165,0,0,0), 기름 T 외부, 사용자 Rogue/Subtlety ilvl334 지정 선택·전투 조건 모두 유지. 기존 v015 유래 v065 후보 선택 경로를 재생하여 D가 v073 신규 60회 후보였음을 증명한 뒤 **오직 D 1163/913/712/362만 신규 SimC 320회 1번**, JSON2 최종 4 rating 일치, **DPS 224438.68 ±SEM365.56(319 samples)**, Native seed 8421873418601877966. v072의 기존 A 813/913/712/712 **DPS 223489.67 ±SEM367.88(319 samples)**는 재호출 없음. **D−A +949.00 DPS(+0.425%)**, 독립정규 근사 95% CI **[−67.48,+1965.49]**, **우열 통계적 미확정**; 기존 v015 유래 판정 pairwise_direction_supported=False. 후보 분배 차이 **350 rating(11.11% T)**, 실질적으로 다른 근접 경쟁 후보지만 전역 최적·근접 최적 대안 인증 아님. 탐색에 사용한 v073의 D 59표본을 고반복 319표본에 섞지 않음. 기존 v064/v065 캐시를 SHA 검증해 **재실행 1/1 HIT, 추가 Native 0**, 세대별·입력별 캐시 격리와 1회 신규 Native 상한 유지. [v074 상세 원본·통계·SHA·다음 작업](./V074_ROGUE_SELECTED_D_320_NATIVE_ACCEPTANCE.md). **다음: v075 기존 v015 스케줄러 기반 탐색 영역·종료/대안 정책 보강; 같은 A/D 무의미한 반복 금지.** main, Work OS, Project Sources, v003, 원본 v015-v016 무변경. 사용자 신규 입력 필요 없음.


> **2026-10-25 v073 최신 — 잠행 도적 CHMV 분배 차이가 큰 실제 적응형 2후보 Native 탐색 PASS:** 최초 [CI #40186665980](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40186665980)은 신규 테스트 문법 오류로 FAIL(실제 Native 0), 교정된 [Actions #40186754387](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40186754387) **SUCCESS, 회귀 397 PASS / 2 SKIP(399건)**. 기존 v069 개별 숫자 증인 2건(해당 전체 run FAIL은 유지), v070 공식 T3150 seed, v071 첫 적응형 scout, v072 실제 320회 독립 재확인 2건 = **총 6 Native 증거 원본/JSON2/영수증 SHA 검증 재사용**. 공식 **G2847+J138+F165=T3150**, 특수 L=(100,201,0,0), 해당 프로필 오프셋=(165,0,0,0), 사용자 지정 잠행 도적 334 아이템·특성·장식2·장신구2·옴니움 mastery·보석B·전투설정 모두 유지. 기존 v015 유래 **v065 정책의 350 rating 이동(총량 11.11%)**으로 서로 다른 두 신규 후보를 자동 선택해 **신규 SimC 2회(각 60 iterations, 59 samples)** 실행: C **463/913/712/1062, DPS 222293.34 ±SEM782.02**; D **1163/913/712/362, DPS 225788.44 ±SEM843.95**. 정밀 기존 A **813/913/712/712, DPS 223489.67 ±SEM367.88(319 samples)** 대비 C−A −1196.33, D−A +2298.76 DPS 관측. 새 후보 모두 스탯 이동 350/T=11.11%, JSON2 정확 정합 PASS. **D는 탐색 2후보 중 선택된 저반복 실측이므로, 단순 95% 구간이 0을 제외하더라도 다중 비교/선택 편향 및 새 정밀 검증 부재로 우월성 확정 금지.** 기존 v065 SimC 실행기를 재사용, 탐색기 신규 중복 없음; SHA 검증 재실행 두 건 캐시 HIT **Native 0**. 신규 정밀 확인·확정 근접 대안·전역 수렴/전문화 범용화는 미완료. [v073 원본·수치·근거](./V073_ROGUE_MATERIAL_ADAPTIVE_NATIVE_ACCEPTANCE.md). **다음은 v074 D 독립 320회 Native 재확인(기존 A 재호출 불필요), 통계적 불확실성 명시**. official Project Source·main·Work OS·v003·원본 v015/v016 불변; 추가 사용자 입력 불필요.


> **2026-10-25 v072 최신 — 잠행 도적 2후보 독립 320회 Native 정밀 확인 PASS:** [GitHub Actions #40185708187](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40185708187) SUCCESS, 현재 회귀 **392 PASS / 2 SKIP** (394 tests). v069 개별 숫자 증인 2건(해당 workflow 전체 FAIL 유지), v070 공식 T3150 실측 1건, v071 적응형 scout 1건 **총 4건 실제 Native 기존 증거를 검증하여 재사용**. 사용자 입력 Rogue/Subtlety/Void Elf/ilvl334·아이템/2장식·Omnium mastery·특수보석B·Patchwerk 300초 불변. 공식 **T=G2847+J138+F165=3150**, 고정 L=(100,201,0,0), 해당 프로필 오프셋=(165,0,0,0), 기름 T 외부. 기존 v015 유래 **v065 confirmation_pair**와 v064 평가기를 재사용하며 실행 정책만 **320 iterations × 2후보**로 명시 확장, 별도 시나리오·DPS 캐시 identity. 신규 SimC **2회**, 각각 319 표본, 최종 JSON2 CHMV 완전 일치. **A 813/913/712/712: DPS 223489.67 ± SEM367.88; B 713/913/712/812: DPS 222956.31 ± SEM371.26**. A−B +533.36 DPS, 독립정규 근사 95% 구간 **[−491.03, +1557.75]** — **통계적 우열 미확정**, 전체 최적해 주장 없음. 실제 서로 다른 Native seed 확인; 결과 SHA 검증 **2/2 캐시 HIT, 추가 Native 0**. 대안 스탯 이동 100/T3150=3.17%로 실질 차별화 대안 미달. [실제 v072 수치·SHA·제한·다음 작업](./V072_ROGUE_TWO_HIGH_ITERATION_NATIVE_ACCEPTANCE.md). GitHub 격리 브랜치에서만 변경; 공식 Work OS / Project Sources / main / v003 / 원본 v015·v016 불변. **다음 구현:** v065 기존 탐색기로 소규모 추가 영역 탐색과 분배가 크게 다른 근접 대안 선별(중복 SimC·과도한 고반복 금지). 사용자 신규 입력 필요 없음.


> **2026-10-25 v071 최신 — 사용자 실제 잠행 도적 334 CHMV 적응형 첫 Native 탐색 PASS:** 신규 코드는 기존 [v068~v070 실제 Rogue 증인 2건·공식 GJF 후보 1건](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40182313167)을 **재사용**. `void_elf/subtlety`, 사용자 지정 특성, 장신구 270175/281215, 장식 hunter_ritual_stone/arcanoweave_lining, 특수장비 271093/271875, 옴니움 4열 mastery, 특수보석 B, Patchwerk 300초 원본 프로필 유지. 공식 총량 **G2847+J138+F165=T3150**, 고정 특수 L=(100치명,201가속,0,0), 정확한 프로필 Native 주입 오프셋=(165치명,0,0,0). 이전 공식 후보 (813/913/712/712) DPS **224891.73 ± SEM1006.01**(34 samples); **v015-derived 기존 v065 스케줄러가 신규 후보 (713/913/712/812) 자동 선택**, [v071 실제 Native #40183940144](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40183940144) **386 PASS/2 SKIP**, 새 SimC **1회**, 최종 rating 3150 정확, DPS **223167.25 ± SEM1185.81**(34 samples). 차 -1724.47 DPS, 근사 95% CI 반폭 3047.84로 **우열 미확정**, 전역 최적화 미달. 재호출은 실제 JSON2 SHA 확인된 캐시 HIT(추가 SimC 0). 초기 CI #40183866776의 합성 테스트용 가짜 바이너리 SHA 오비교 FAIL 보존(신규 Native 0). 장신구 static 0 단정 없음; 5개 gem/enchant 장비 레코드 attribution 미확정, 외부 기름 숫자 별도. **v068~v070 출처는 격리 브랜치 실측이며 별도 전 전문화 인증 아님.** 2후보 별도 고반복 재확인, 고정 T 범위 탐색, 근접 대안·UX는 미완료. [자세한 영수증](./V071_ROGUE_FIRST_ADAPTIVE_NATIVE_ACCEPTANCE.md). main/Work OS/Project Source/v015-v016 원본 불변.



> **2026-10-25 사용자 승인 UX 추가(설계 기록, v068 구현/PASS 아님):** 장식은 **기본 2개 선택**, **장식 1/장식 2 효과를 사용자가 각각 선택**. 백엔드 최대 2개 한도 및 사용자 고급 설정의 0–1 가능성은 보존. **옴니움 장서 4번째 UI 열**은 치명·가속·특화·유연 중 **사용자 명시 1개 선택**. 고정된 해당 선택은 단일 CHMV 탐색의 시나리오와 SimC 입력/DPS 캐시 identity에 포함, 자동 5번째 분배변수나 공식 T=G+J+F 가산 항목으로 승격하지 않음. 옛 `omnium_talents` 문자열의 **4번째 토큰=4번째 UI 열이라고 가정하지 않으며** 네 선택의 정확한 SimC ID 매핑은 구현 전 확인. [사용자 승인 UX 결정 기록](./V068_USER_INPUT_UX_DECISIONS_20261025.md). 공식 Project Sources·Work OS·GitHub main 미변경, 기존 v067 Native PASS 상태 불변.


> **2026-10-25 v067 최신 — 프로필 중립 입력 → 단일 기존 v065 적응형 실행기 연결 PASS:** `v066_profile_neutral_preflight.py`는 외부 v061 시나리오·정확한 비장신구 표준장비·v046 Native 정적 캐시·SimC 전체 프로필·해당 프로필의 실제 Native JSON2 두 수치 관측·SimC 바이너리 SHA를 받으며, **마법사 전용 상수 없이 T=G+J+F 및 G/L·오프셋·프로필/아이템 ID·버전 정합을 검사**. [v066 #40174975829](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40174975829) **355 PASS / 2 SKIP**, 신규 Native 0회. `v067_generic_adaptive_native_route.py`는 탐색기를 복제하지 않고 **동일 v065 스케줄러에 준비된 입력을 전달**. [v067 #40175621237](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40175621237) **362 PASS / 2 SKIP**, 과거 실제 v063 2건+v065 4건 재사용, `--cache-only`로 Native 추가 실행 **0회**, 기존 4개 실제 JSON2 바이트 불변 및 누적 4회 예산 유지. 첫 2회 v066 FAIL(테스트 반복설정·예외 예상 클래스)과 v067 첫 FAIL(구형 v065 영수증의 신설 scoped-binary-hash 필드 부재) 보존; 호환은 **4건 전부 SHA 확인되는 cache-only 모드**에 한해 허용. **다른 전문화는 아직 합성 스키마 테스트만 PASS**, 실제 SimC 장비·DPS Native 검증 아님. 자동 신규 프로필용 두 수치 증인 생성 및 전 전문화 연결, 유연한 반복 횟수는 다음 작업. 과거 v015 71/71·v016 104/104는 역사 기록 그대로. [상세 v067 검증](./V067_GENERIC_PREPARED_ADAPTIVE_ROUTE_ACCEPTANCE.md). GitHub main/Work OS/원본 불변, 이 채팅에서 개발 계속.



> **2026-10-25 v065 원본 계보·적응형 Native 통합 최신:** 사용자 제공 원본 ZIP 내부 37/37 Manifest SHA/크기, ZIP/4개 원본·계보 ZIP CRC, v015→v016→v017→v018 바이트 보존 PASS; 과거 71/71·104/104는 과거 오프라인 기록으로만 표시. v015 본원 SHA `a44f73c...`, v016 본원 SHA `7c49d7c...`, 원본 불변. v015의 neighbors·choose_next·confirmation_pair·judge **결정 원칙만 신규 v065 어댑터로 포팅**, 현재 v061~v064 주입/JSON2 평가에 연결. [v065 2-scout + 2-fresh-confirm 실제 Native PASS #40171473855](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40171473855): 현행 테스트 **343 PASS / 2 SKIP**, 신규 SimC 4회, 기존 Native 2건 anchor 재사용, 전체 4후보 최종 CHMV 3152 정합; 재시작 후 모든 Native 검증 캐시 HIT(신규 0회). scout 최고 DPS 195407.5가 새 정밀 확인에서 192644.4로 낮아졌고, 다른 confirm 192446.0 대비 **DPS차 198.4 ± CI95 halfwidth1502**로 통계적 우열 미확정. 초기 시험의 테스트 인자 순서 FAIL #40171226389 보존. **실제 원본 v015/v016 소스 자체를 그대로 실행하거나 제품 전체 통합·전역 최적해 달성으로 보고하지 않는다**. [상세 검증](./V065_AUTHENTIC_V015_ADAPTIVE_NATIVE_INTEGRATION.md). 현재 채팅 계속 개발; GitHub main/Work OS 불변.



> **2026-10-25 v065 최신(원본 독립 검증 + P4 실제 적응형 탐색):** 사용자 제공 v015·v016 원본 인계 ZIP `SIMC_v015_v016_ORIGINAL_SOURCES_HANDOFF(1).zip`를 독립 감사했다. **외부 Manifest 37/37 크기·SHA PASS**, ZIP CRC, 내부 v015/v016/v017/v018 Manifest **10/10·20/20·27/27·46/46 PASS**. v015 원본 SHA `a44f73cf...`, v016 SHA `7c49d7ca...`; 보존본 수정 없음. **과거 71/71·104/104는 역사 기록이며 이번에 원본 테스트는 재실행하지 않았다.** v015 이웃 rating 제안·순차 재계획·상위 2후보 정밀 확인 정책만 v061~v064와 연결했다. [v065 1 Native guided run #40171255554](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40171255554) **343 PASS/2 SKIP, 신규 Native 1회**; 별도 [v065 2 scout+2 fresh confirmation run #40171473855](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40171473855) **343 PASS/2 SKIP, 신규 Native 4회**, 재실행 4건 전부 SHA 확인된 Native 결과 캐시 재사용. 공식 `T=G2849+J138+F165=3152` 유지. 고반복 확인 대상 700/1108/1115/229(DPS 192644.38±SEM563.05) 및 600/1108/1115/329(DPS 192445.96±SEM519.84); 차이 약 198.42 DPS, 95% 근사 반폭 1501.97로 **우열 미확정**. 첫 2개 v065 검증 FAIL은 신규 기능 결함이 아니라 테스트 harness 함수 인자 순서 오류, 증거 보존 후 수정. **v065 후보 스케줄러 구현 2갈래가 현재 격리 브랜치에 존재**하므로 구조 경량화를 위해 1개로 통합 필요. 해당 PATH 실증 외 전 전문화/시나리오 일반화와 원본 제품 v015~v016 코드 완전 통합은 미완료. [상세 인계·영수증](./V065_ORIGINAL_V015_V016_SOURCE_AND_ADAPTIVE_NATIVE_ACCEPTANCE.md). 계속 이 채팅에서 개발.



> **2026-10-25 v064 최신 상태 (P4 평가 포트 검증):** 사용자 적용 공식 Source **v1.2** 기준. `runner/v064_adaptive_evaluator_port.py`에 외부 탐색 엔진의 후보/iterations 제안을 기존 v061 시나리오·v062 정적 예산·v063 프로필별 숫자 주입/JSON2 DPS·SEM 평가와 연결하는 포트를 구현했다. 선택된 **15개 SimC 아이템 ID/레벨/옵션, 소모품, 캐릭터/전투 조건** 일치를 검사하고, SHA 검증된 Native JSON2 영수증만 결과 캐시로 재사용한다. [GitHub Actions #40167043876](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40167043876) **315 PASS / 2 SKIP**; v063 기존 실제 Native 두 결과 독립 재생 PASS, **새 SimC 0회**. 공식 T=3152에서 A192374.47 vs B192109.86 DPS 관측, 차이 통계적 미확정, 후보 간 rating 150 이동은 시범 10% 차이 기준 미달이라 대안 0건. **기존 v015/v016 원본 자동후보 생성 알고리즘·제품 통합은 아직 확인/연결되지 않았다**. [v064 근거·정확한 다음 작업](./V064_ADAPTIVE_EVALUATION_PORT_ACCEPTANCE.md). 새 채팅 이동 없이 이 채팅에서 개발 계속.



> **2026-10-25 최신 개발 갱신 v063 (P3 Native):** 공식 v1.2 `T=G+J+F`를 사용한 334 Arcane Mage 단일 프로필의 2후보 **실제 SimC 주입 및 DPS 수집 PASS** — [Actions 40165729165](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40165729165), 전체 회귀 **304 PASS / 2 SKIP**, Native 신규 실행 2회. 기존 v059 Native 2후보의 정적 수치 차이로 net gear→JSON2 offset `(0,+165,0,0)`를 같은 프로필에서만 보정했고, 공식 총량 **G2849+J138+F165=T3152**, 무기 기름 `(16,16,0,0)`은 **T 외부**다. 후보 A 600/1108/1115/329 (DPS 192374.47±SEM951.01), 후보 B 750/958/1115/329 (DPS 192109.86±SEM1300.02) 모두 최종 rating 정확히 일치, 통계적 우열 미확정. **9개 gem/enchant 포함 gear 레코드의 정적 수치 출처 완전 분해는 미입증**; 이를 모든 전문화 예산 중복 가산 제거 완료로 승격하지 않는다. 원본 v015~v016 제품 통합도 미완료. [상세 실측·미완료사항](./V063_OFFICIAL_GJF_NATIVE_NUMERIC_RECONCILIATION.md). 다음 작업은 **범용 프로필별 숫자 주입 오프셋 및 실제 제품 적응형 엔진 연결**. 개발은 이 채팅에서 계속.



> **2026-10-25 최신 개발 갱신 v062:** 사용자는 Project Source v1.2 및 Project Instructions 적용을 완료했다고 보고했다(프로젝트 UI 직접 대조는 별개). **개발은 이 채팅에서 계속한다.** 격리 제품 시험은 [v061 입력 계약 PASS 40162193520](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40162193520) **277 PASS / 2 SKIP**(초기 FAIL 40162112120 보존), [v062 정적 예산 컴파일 PASS 40162455726](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40162455726) **291 PASS / 2 SKIP**. 기존 v059 Native JSON2 증분 재사용으로 334 Mage exact 정적 G=2849, Native cache 1759→1760 (0 신규 SimC 호출·기존 값 교정 0). 공식 v1.2 기본 T=G+J+F=3152 산술 예시이며 v059 기름 포함 실험 T=3184와 구분. **P3 최종 numeric rating 주입 정합/원본 v015–v016 통합은 아직 미완료**. 상세: [V062_SCENARIO_AND_G_L_BUDGET_ACCEPTANCE.md](./V062_SCENARIO_AND_G_L_BUDGET_ACCEPTANCE.md).



**문서 목적:** 같은 채팅에서 구현을 이어가면서, 필요한 경우 어느 일반 채팅에서도 동일한 제품 기준·증거·실제 차단 사항을 복원할 수 있도록 보존한다. **새 채팅 전환을 요청하지 않는다.**

**적용 범위:** 개발 격리 브랜치의 현재 작업 기록. 공식 Project Instructions/Project Sources나 Work OS CURRENT의 자동 승격은 아니다.

## 0. 읽는 순서·상태 신분

1. 사용자가 2026-10-25 적용 완료를 보고한 Project Sources의 공식 **`SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.2_PROJECT_SOURCE_REPLACEMENT.md`**를 제품 정책 최상위 문서로 읽는다. 이 문서의 역사적 v1.0·v1.1_CANDIDATE 언급은 과거 근거와 미승격 충돌의 설명이며 현재 활성 권한을 뜻하지 않는다.
2. `docs/DEVELOPER_NOTES_CURRENT_POLICY_ADDENDUM_20261025.md`는 **v1.2 생성 전 이력 및 충돌 기록용**으로 참조한다. 현재 실제 사용자 적용된 v1.2 Source와 충돌할 경우 사용자가 승인한 v1.2가 우선하며, 자동 정책 변경 없이 충돌을 보고한다.
3. 이 문서에서 최신 개발/시험 사실 및 정확한 다음 구현 지점을 복원한다.
4. `docs/V059_NATIVE_CANDIDATE_BRIDGE_ACCEPTANCE.md`와 [실제 GitHub Actions #40157655114](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40157655114)를 대조한다. 각 후속 버전은 그 버전의 증거를 추가한다.
5. `Developer_Notes_v1.1_CANDIDATE.md`는 **후보**이고 전체 승격 불가. 개발자 노트 v1.0, v003 immutable, MAIN 운영 계약을 기계적으로 덮어쓰지 않는다.

## 1. 지금 진행 중인 채팅이 개발을 계속 소유함

- 사용자는 2026-10-25 기존 채팅에서 작업을 이어가겠다고 명시했다. **'새 일반 채팅에서 바로 시작하라'는 인계 절차는 현재 작업 요청이 아니다**.
- 새 채팅용 복원 가능성은 지속 상태 문서의 품질 기준일 뿐이다.
- 현재 개발 방식은 GitHub 연결 API/Actions 사용. 로컬 PyCharm 환경 재구축·Work 모드 전환을 요구하지 않는다.
- branch: `degong2-code/simc-secondary-optimizer-runner@probe/chat-cache-v035-20261024`. HEAD는 반드시 재조회; 커밋 해시는 고정 버전 증거로만 취급. GitHub `main`을 시험 branch와 혼동하지 않는다.

## 2. 최신 제품 개발 상태 vs 시험 브랜치

| 구분 | 현 상태 | 근거/제한 |
|---|---|---|
| 사용자 보고 원본 제품 | **v016_SCENARIO_CONTRACT** | 이 repo에서 해당 제품 소스 바이트 및 receipt를 독립 확보·검증하지 못함 |
| 옛 적응형 탐색 파일럿 | v015 구현 보고/오프라인 71/71 PASS | 원본 제품 계보 및 당시 실 Windows 시험 미확보 |
| GitHub 시험 런타임 | v032 byte-preserved 연구 실행 파일 존재, v037 메모리 내 적응형 연결 | 원본 v015/v016과 일치한다고 단정 금지 |
| 정적 아이템 캐시 | v046~v058, 455 item IDs / 1759 Native stat variants snapshot | 시즌 전수 DB, full crafted recipes, 모든 ilvl 검증 완료 아님 |
| 장비 선택 | v055, Mindpiercer 트링켓 JSON2 static miss 허용 | v056 1회 Native PASS, SimC 효과는 SimC가 처리 |
| CHMV 후보 평가 | **v059, 2후보 실제 SimC PASS** | **적응형 전역 최적화 완료 아님**, 단일 334 Mage 실험 |
| MAIN/공식 Project Sources | **변경/승격 미완료** | 별도 기존 MAIN 승인 절차 및 실제 적용 기록 필요 |

## 3. 보존할 실제 v059 Native 증거

- Workflow: `.github/workflows/v059_candidate_two_native.yml`
- Actions [run 40157655114](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40157655114) SUCCESS.
- Git commit: `08c309ef31fb1a9119252b633d1d34cb34e36c4f`, SimC Linux binary SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`.
- 258 regression tests: 256 passed + 2 skipped.
- Artifact: `simc-v059-two-candidate-DPS-40157655114`, SHA256 `56002f118cb85cbc7e32aa1c0fc3a0149e7bd7ca0e96b1b96b586b3ddf836288`. Artifact retention may expire; portable ZIP from the prior conversation is alternative, its integrity must be independently checked on reuse.
- v059 334 Arcane Mage, one fixed selected trinket `250224`; selected two Arcanoweave embellishments unchanged; v059 **trial only** budget `T=G2849+J138+F165+O32=3184`.
- Target A `600/1140/1115/329`: DPS 192324.1023, SEM 1379.5784. Target B `750/990/1115/329`: DPS 191574.5434, SEM 1285.6370. Both target/observed four rating numbers match. Difference statistically inconclusive; no optimum declaration.
- Base v1.0 policy `T=G+J+F` is still authoritative; v059's oil vector is **bounded test**, not generalized product rule.

## 4. 구현 순서 — 다음 실제 작업

**P0 · 계보 확인 — 우선 작업이지만 격리 개발 중단 사유 아님.** 원본 `v015`/`v016_SCENARIO_CONTRACT` 파일 위치/바이트/영수증 확인. 기존 탐색 기능(후보 생성, 통계 비교, 실행 예산, 중단/재개)을 재활용할 수 있는지 판단. 미확보이면 '원본 제품 통합 증거 없음' 유지하면서 다음 격리 기능 구현 진행.

**P1 · 범용 Scenario Contract** — 고정 Mage/334 값 제거. 직업/전문화/종족/특성, 선택 장비·장신구 2개·장식 2개, 4pc, 목표 ilvl/수동 T, 보석/영약/소모품, 전투 시나리오, 스탯 상하한, SimC 실행 예산을 정형 입력으로 연결. 장비 조합 자동선택, 자체 효과 계산 금지.

**P2 · 대표 장비·정적 예산** — 실제 Native stat cache 기반 G/특수장비 locked floors/제작 자유배분, J/F를 구성. 목표 ilvl에 맞는 주능력치/무기 성능/기본 티어4셋 유지. 장신구는 G 밖. Native cache miss는 선택된 비장신구에 한해 1회 지연 조회, 같은 변형 재사용.

**P3 · 범용 SimC CHMV 주입** — gear_* override와 실제 출처별 외부 가산을 숫자로 정확히 조정. 같은 스탯의 중복 가산/누락을 막고 **요청 목표 vs Native JSON2 정적/적용 rating** 확인. 아이템 proc/효과 검사를 선행 Gate로 추가하지 않는다.

**P4 · 원본 적응형 탐색 접합** — v059 `plan / compose_input / observe_result / compare` 인터페이스와 출처 확인된 기존 탐색 루프 연결. scout→guided→confirmation iterations, 고유 후보 캐시, 오차 범위 내 미확정 처리, 근접 대안 산출.

**P5 · 범용화 실측** — 우선 별도 전문화, 탱커/힐러까지 기존 SimC APL로 DPS 시험, 사용자 설정 전투 환경 반영. '전체 전문화 PASS'는 증거가 쌓일 때만.

**P6 · 실사용 UI/내구성** — 원클릭, 진행도, 취소, 자동 재개, 오류·JSON2·출력해시·실행 폴더 열기, 절대 rating·비율·DPS·SEM·실질적으로 다른 대체 목표 표시.

## 5. 환경/정책 조건의 정확한 판정

- **격리 브랜치 개발 시작**: READY. GitHub 수정·workflow 실행·SimC 재사용·artifact 검색이 현재 채팅에서 실제 작동했다.
- **원본 v015/v016에 최종 합치기**: PENDING_SOURCE_BYTES. 원본 출처·SHA·회귀 계약 없이는 '통합 완료' 선언 불가.
- **공식 Project Instructions/Sources 갱신**: PENDING_MAIN_APPLY. 이 채팅 연결 도구에는 Project Settings/Project Source를 직접 수정하는 API 없음. 사용자가 승인한 결정은 정책 부록에 기록되었지만 공식 설정 적용 여부를 추정하면 안 된다.
- **공식 Work OS M0 환경 Gate**: 제품 실험/개발 허가와 분리, MAIN 소유. 미통과로 정상 제품 시험을 금지하지 않는다.
- **WEQUIP runtime**: 런타임 의존성 도입 금지. 일회성 정적 metadata 입력까지만.
- **Developer Notes v1.0 및 v003 immutable**: 보존.

## 6. 문서 유지 규칙

새 버전을 개발할 때마다 *실제 실행된 Run ID, SHA, PASS/FAIL, 남은 불확실성과 정확한 다음 작업*만 추가한다. 미실행 시험이나 이전 문서의 자기 보고를 독립 검증 완료로 바꾸지 않는다. “인계 준비”를 개발 중단이나 새 채팅 이동 요청으로 해석하지 않는다.
