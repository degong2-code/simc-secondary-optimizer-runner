# SIMC SECONDARY OPTIMIZER — 2026-11-18 최신 제품 완성·영구 마부 우선 인계 (v581 실증 이후)

> **용도:** 새 일반 채팅의 **READ-ONLY 독립 복원 정본**. 프로젝트 재시작·새 엔진 연구·과거 실측 재감사가 아니다.
> **작성 기준 HEAD:** `9bc8fd8952dd416c6277ee37ced9632651fa8f93` (새 문서 작성 직전의 정책 커밋; 인계 후 HEAD는 달라진다). 저장소 `degong2-code/simc-secondary-optimizer-runner`, 격리 브랜치 `probe/chat-cache-v035-20261024`. **항상 실제 최신 HEAD·CURRENT·Actions를 먼저 조회**할 것.
> **최신 직접 결정:** 2026-11-18 정책은 이미 `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 첫머리와 `docs/development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md` 최상단에 기록됐으며, 과거 인계의 PENDING·다음 작업보다 우선한다.

## 1. 프로젝트 취지와 제품 경계

**사용자가 미래 목표 아이템레벨(기본 334) 또는 직접 지정한 최종 CHMV 총량 T를 선택하면, AI 없이 새 시즌 원본·환경을 구축하고 기존 적응형 SimC DPS를 실행하여 치명·가속·특화·유연의 목표 절대 rating을 찾는 Windows 사용자 프로그램**을 완성한다.

- **지원:** 26개 딜러(DPS) 전문화만. 증강 기원사·탱커·힐러 제외.
- **사용자 입력:** 직업·전문화·종족·특성, 목표 ilvl 또는 수동 최종 T, 장신구 2개, 선택 특수장비·장식 최대 2개, 최고 품질 보석·영약·소모품·무기 기름·영구 마부·전투 조건. 전체 현재 장비나 완전 SimC 프로필을 필수 입력받지 않는다.
- **내부 흐름:** 활성 시즌/동일 빌드 원본 자동 발견 → 대표 일반 장비·무기·티어 4pc → G/J/F/O 및 E/L → B/T·정적 하한 → 실제 SimC 프로필 → v290/v291/v293 적응형 DPS/SEM/95% → 관측 1순위·실질적으로 다른 근접 대안·비율·저장/캐시/취소·재개.
- **예산:** `B=G+J+F`, `T=B+O`, `c_final=c_base+o`. 사용자의 **수동 최종 T가 자동 총량에 우선**, `B=T−O`. 고정 L은 G 내 한 번, E는 승인 회계에 따라 한 번, O는 gear_*에 한 번. 장신구 고정 스탯은 자유 G 외부. 고정 하한·무기 손·정확 ID/SHA·중복 방지 필수.
- **SimC의 책임:** 장비·장신구·보석·장식·마부·기름 효과, 발동(proc), APL, 실제 DPS. 프로그램은 정확한 입력·CHMV 회계·정적 rating·통계·캐시 identity를 책임진다. 효과 재구현/효력 인증 Gate는 신설하지 않는다.
- **범위 밖:** 현재 착용 장비 스탯 재분배, 장비 조합/획득 추천, 시즌 모든 장비 DB, 새 최적화 엔진, 게임 내부 효과 재구현, 런타임 AI/LLM 호출. **제품 런타임 AI 판단·호출 0회.**

## 2. 최신 사용자 결정 — 우선권과 완료 판정

1. **ZERO-SOURCE 시즌 범용 구축 엔진 기능은 이미 PASS로 인정한다.** 기존 시즌 정답·완성 DB·캐시를 격리하고 현재 시즌 원본을 실제 자동 발견·수집하여 G/J/F/O→v212 설치→실제 사용자 SimC를 실행한 `v567` 및 실제 Windows Chrome `v570`를 근거로, **아직 출시되지 않은 미래 시즌을 기다리는 재시험을 필수 Gate로 두지 않는다**. 동일 코드가 새 시즌 출시 후 실제 새 ID/빌드/품질/수치를 갱신하는 것은 운영 업데이트다. 신규 시즌 전 분야·선택지까지 사전 실측됐다는 뜻은 아니다. [수락 정책](development/POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md).
2. **영구 마부 전체 자동 구축은 제품의 남은 최우선 필수 기능이다.** Environment Build 엔진이 **해당 시즌에 제품이 지원·노출해야 할 적용 가능한 모든 영구 마부 선택지**를 원본에서 발견하고, 효과·적용 조건이 같은 계열의 **최고 품질만** 선별하고, 정확한 Item/Enchant ID·게임 빌드·부위·무기 유형·SimC 입력 토큰·정적 고정 E와 소유권·하한·사용자 선택/실제 프로필/세션을 연결해야 **영구 마부 전체 구축 성공**이라고 부른다. 일부 아이템 Native PASS 또는 38 source-only 후보를 전체 등록·성공으로 과장하지 않는다. **전체 환경 구축 완료 SUCCESS는 영구마부 전 선택지 완료 전 보류**한다. 단, 사용하지 않는 미검증 마부 하나 때문에 검증된 BASE G/J/F/O 사용자 SimC 실행은 차단하지 않는다. 일반 임시 마부 지원 제외, **무기 기름 O는 별도 지원 유지**.
3. **옴니움 장서(Omnium Folio)·확장팩 전용 특수 시스템은 본 기능 완성 후 별도 선택형 모듈 업데이트로 한다.** 이후 추가·변경되는 시즌 모듈의 ON/OFF 및 잔여 효과·예산·캐시 정합성을 별도로 시험한다. 핵심 제품 인수 Gate나 영구 runtime AI 의존성으로 만들지 않는다.
4. **v290+ 최적화 탐색 자체는 현행 유지.** 새로운 통계 방법/SEM 미세조정/탐색 정책 연구를 제품 완성의 필수 다음 단계로 되살리지 않는다. `v303~v312` 연구는 opt-in/역사 비교이며 기본 엔진 교체의 자동 근거가 아니다.

**우선권:** 최신 사용자 직접 결정 > 최신 승인 정책(특히 2026-11-18 CURRENT/로드맵) > 실제 코드·CURRENT·Actions·Native/SHA 영수증 > 과거 인계/역사 문서. 제품이 **구현한 것**과 **전체 선택지 완료 정책**을 혼동하지 않는다.

## 3. 실제로 통과한 제품 구간 — 실측과 범위를 구분

| 구간 | 실제 증거 | 엄밀한 판정 |
|---|---|---|
| **제로베이스 시즌 구축→사용자 SimC** | [v567 Actions #44046442654](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44046442654), 게임 12.1.5.70783/ilvl334, G2850/J92/F165/O0, B=T3107, 보석 12방향·최고품질 2축·최소 Native 실측, 설치 후 DPS Native6/SEM/95%/cache-only | **현재 ZERO-SOURCE 엔진 기능 합격**; 전 영구 마부 완료 아님 |
| **실제 Windows Chrome 첫 사용자 기본 경로** | [v570 #44074372451](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44074372451), 빈 데이터 시작→원본 Build→v212 설치→장신구2→SimC **DPS64**→결과 화면 | 기본 일반 제품 E2E의 강한 실제 증거; 공식 전체 78 수락 자동 승격 아님 |
| **영구 마부 정확 범위 3종** | [v530 #43905387382](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43905387382) E0 7967; [v532 #43910202520](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43910202520) 가속 E+30 8025; [v533 #43910935776](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43910935776) 특화 E+26 7965; [v534 #43974259684](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43974259684) 양수 E+수동 T | 실제 **생존 사냥꾼 334 반지1·특정 선택 조합만** 사용자 DPS 승인. **영구 마부 전수 선택지 자동 등록은 미완성** |
| **양수 기름 O + 수동 최종 T 연결** | [v578 #44098212428](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44098212428) 실제 물리 기름 O32/설치 SHA/수동 T3500→B3468, [v580 #44106357901](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44106357901) 실제 Chrome 기름 선택·정확 SHA 연결 | 사용자 UI·예산·설치 연결 PASS, 기름 전 종류의 인증은 아님 |
| **실제 기름 포함 DPS·재개·캐시** | [v581 #44110104367](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44110104367): 환경 Native5, DPS Native2, 재개1건, cache-only 추가 Native0; T3500에서 관측 846/995/830/829, DPS169750.54, SEM680.33 | **95% 우위 미확정**, 전역 최적 입증 아님; 종료/재시작 재검증을 자동 차기 필수로 삼지 않음 |
| **Windows 설치·패키지** | [v575 #44088065693](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44088065693) 실제 Windows Python3.12 표준경로 복구·venv 동의 설치; 이후 [ZIP 회귀 #44111028605](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44111028605) | Windows CI PASS. **개인 PC에서 winget Python 첫 설치 성공**은 미검증 |

**절대 재혼동 금지:** v581의 2개 후보만으로 최적 CHMV나 95% 확정을 선언하지 않는다. v570의 DPS64 완료는 특정 1개 기본 사용자 구성의 실제 증거다. 현재 실제 전체 완료 계약은 **15/78 COMPLETE, `full_product_e2e=PENDING`**이며, 이는 구현률 15/78을 의미하지 않는다.

## 4. 2차 스탯 최적화 현재 방식 (v290+)

- `v290_multiscale_adaptive_policy.py`는 총량·스탯별 고정 하한/상한을 지키면서 처음엔 **4차원 스탯 공간 전역을 고르게 확인**(기본 균형 후보, 전역 최대거리 후보), 그다음 **DPS가 좋은 여러 후보 주변을 거친 폭부터 작은 폭까지** 서로 다른 CHMV 절대 rating으로 옮겨 다니며 찾는다. 이미 관측한 DPS와 **SEM을 함께** 보아 유망 후보를 판단하고, 일정 시점에 2후보의 추가 측정을 제안한다.
- `v291_durable_multiscale_native_runner.py`가 기존 `v065` 등 실제 SimC 실행과 JSON2 rating 정합·후보 입력/바이너리/iterations별 SHA 캐시·중단/재개·원본 영수증을 연결한다. 관측상 1순위와 실제 선별 2후보의 **95% 우위 여부**를 분리한다.
- `v293_local_longrun_session.py`가 일반 Windows 장기 세션을 관리한다. **신규 세션 scout iterations 56 / confirm 320**(기존 세션의 기본 35는 영구 호환); 실행 상한·캐시 전용·취소·재개·결과를 이어준다. 실제 결과에는 **절대 rating+비율+DPS+SEM+95% 여부+실질적으로 다른 근접 대안**을 표시한다. 예산 내에서 탐색한 **관측 1순위**이지 전역 수학적 최적해 증명은 아니다.
- **이미 제품 경로에서 동작하므로 새로운 탐색기/전문 고유 APL/전수 Native를 만들지 않는다.** 구현 개선은 실제 사용자에게 재현된 탐색·캐시·결과 오류가 있을 때만.

## 5. 진짜 남은 1순위: 영구 마부 전체 사용자 선택지

**현 구현:** `v211`은 과거 빌드 원본 기준 약 **38개 영구 마부 후보**의 정적/스펠 성격을 source-only로 분류했고, `v113`의 전체 `verified_installed_enchant_registrations`는 기본 `runtime_selectable=false`. 실제 사용자 DPS 범위는 위 생존 사냥꾼·반지1 3개에 국한. **38개 후보 = 38개 모두 등록 완료/최고 품질/적용 부위·수치·실 실행 승인이라는 뜻이 아니다.**

**필요한 제품 연결(기존 자산 우선):**
1. 실제 현 시즌 원본에서 제품에 적용 가능한 **영구 마부 전 선택지와 품질/효과/부위/장착 조건**을 확인한다. 단순 이름·아이템 레벨·핸들러 존재만으로 최고품질·등록 결정하지 않는다. 동일 효과·조건의 품질만 비열등 수치 최고로 묶고 서로 다른 스탯/발동/조건은 별개로 유지.
2. `v211` 분류와 기존 `v216/v222/v212` 시즌 소유권/봉인, `v198/v202/v204/v528/v531~v534` E 회계 및 실측 영수증을 **REUSE/CONNECT**한다. 정확한 정적 CHMV E는 고정 하한/예산 내 **한 번**만, 동적 발동 마부는 정적 E로 잘못 편입하지 않는다. 효과/proc 계산은 SimC에 맡기고 별도 구현하지 않는다.
3. 승인된 모든 해당 시즌 영구 마부가 `v113` 사용자 선택 목록→실제 적용 부위·손·장비 옵션·대표 프로필→SimC 원문 입력→예산/JSON2/캐시로 **정확히 연결**되도록 만든다. 증거가 부족하면 **해당 선택지에 이유가 명확한 PENDING**, 미관측을 0으로 채택하거나 전체 후보를 무단 공개하지 않는다.
4. 전체 목록의 발견·등록·UI 정확성은 구조화된 오프라인 회귀와 **실제로 달라진 효과/계수/분기만 대표 Native**로 검증한다. **38×26 Native 전수·불필요한 효과 재현/별도 Gate 금지**. 완료 뒤 **전 선택지 자동 구축**을 표시할 수 있는지 소스/옵션·등록 수·보류 건을 정직하게 대조한다.
5. 영구 마부 전체 영역 **완료 전에는 전체 Environment Build SUCCESS 금지**. 그러나 특정 영구 마부를 **미선택**한 일반 기본 G/J/F/O 사용자는 그대로 실행 가능. 신규 시즌이 나왔을 때 기존 70783 E값을 다른 빌드의 확정값으로 복사하지 않는다.

**다른 항목:** 추가 5+/6소켓은 실제 소켓 권한·J 증거가 있는 선택만 지원; 미검증은 그 옵션만 PENDING. 26개 DPS의 모든 사용자 선택·개인 PC 설치/전체 계약도 광범위 완료 주장 금지. 본 기능 완료 후 옴니움 장서를 별도 모듈로 갱신하는 것이 **후속 시험**이다.

## 6. 단기 로드맵과 STOP 기준

**다음 작업 1개:** 새 엔진 개발이 아니라 **영구 마부 후보 원본 → 제품의 전 선택지 최고 품질 판정 → 정확 E/SimC 소유권 → 자동 사용자 등록** 중 **처음 끊긴 실제 소비 경계 하나를 찾아 최소 연결·수리**한다.

- 먼저 현 `v211` 원본 38후보·실제 시즌 원본, `v113` 등록 상태 및 영구마부 소비 필드·기존 v528/v532/v533/v534 Native 영수증을 대조한다.
- 전체 선택지가 누락 없이 구축·선별·등록되도록 기존 Environment Build를 확장하되, 별도 영구마부 엔진·전 시즌 장비 DB·독립 효과 판정을 만들지 않는다.
- 변경된 부분에만 focused offline→필요한 소수 Native→실 사용자 경계 E2E 순으로 검증. 기존 v567/570/578/580/581 및 같은 시즌 캐시를 반복 실행하지 않는다.
- **STOP:** 기존 기능/영수증으로 실제 제품에 소비되는 선택지·정적 E·프로필 경계를 정확히 처리하면 추가 연구/정밀 측정 중단. 제품이 소비하지 않는 데이터는 수집하지 않음. 미선택 보류 옵션 때문에 BASE를 중단하지 않음.
- 그다음 M3~M6 남은 **실제 사용자 선택 기능/Windows UX**를 제품별 실제 장애에 맞춰 마무리하고, **M7 공식 전체 수락·78개 계약의 유효한 조건**은 별도 정식 판정으로 수행. 인계 문서 작성으로 공식 수락/원장 COMPLETE를 임의 갱신하지 않음.

**매 변경 전 사용자에게 설명:** 사용자 흐름의 위치·현재 불편/장애·기존 코드 재사용 가능성·불필요한 개발/STOP·추가 Native/HTTP/DB2/CPU/RAM/I/O/캐시 영향. [제품 우선·최소 검증 정책](development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md).

## 7. 최초 읽기 순서·권한

1. 이 문서 → `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 최상단 → `docs/development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md` 최상단.
2. `docs/development/POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md`, `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`, `docs/development/PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md`.
3. `docs/USER_APPROVED_GEM_J_POLICY_20261117.md` **최신 F절**, `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md`, `docs/V211_ENCHANT_EFFECT_SOURCE_CLASSIFICATION_AND_EVIDENCE_20261031.md`.
4. `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json`, `docs/development/INDEX.md`, `FILE_MAP.md`, `EVIDENCE_INDEX.md` 및 현재 실제 코드·Actions·Native 영수증. [v567 과거 인계](CHAT_CONTINUITY_HANDOFF_20261117_V567_ZERO_SOURCE_GEM_MIN_NATIVE_PRODUCT_BRIDGE_READONLY.md)는 **역사 참고**이지 현 우선순위가 아니다.
5. 사용자의 새 직접 결정 > 최신 승인 설계 > 현재 실행 증거 > 역사 문서. 마부가 미완료여도 범용 ZERO-SOURCE 엔진 PASS를 '미래 시즌 미실측'이라는 이유로 취소하지 않는다.

**권한:** 현재 주 제품 개발 채팅이 계속 개발 소유. 새 채팅의 첫 작업은 **읽기 전용 독립 복원 후 STOP**. 사용자 별도 승인 없이 `main` 병합, `v003 immutable` 변경, 원본 `v016` 직접 통합 완료 주장, Project Sources/Instructions UI 적용 주장, 공식 Work OS M0/Shared State 승격, 78요소 COMPLETE 임의 변경 및 주채팅 소유권 이전 금지. 동일 시즌 정적 아이템 캐시는 SimC revision만으로 폐기하지 않으며 DPS 캐시는 실제 바이너리/프로필/전투/iterations identity로 구별.

**첫 보고는 7항목만:**
1. 현 HEAD·최근 Actions PASS/FAIL/CANCELLED/SKIP.
2. 최종 제품 목적과 현재 일반 사용자에게 가능한 범위.
3. 실제 ZERO-SOURCE PASS와 현재 선택형/영구마부 전체 완료 범위의 정확한 차이.
4. v290/v291/v293·실 Native/오프라인 회귀 상태와 95%/전역 최적 판정 경계.
5. 필수 미완료 영구마부 전 선택지 vs 보류 가능한 선택 기능 vs 본 제품 후속 Omnium 모듈.
6. 비용 대비 **다음 작업 딱 하나**(기존 기능 재사용, 제품 경로/비용/STOP 기준).
7. 미확인 영수증·78 공식 상태·GitHub/Project UI/Work OS/주채팅 권한 경계.

**첫 응답에서 코드/문서 수정·Actions·Native·HTTP/DB2 신규 실행을 하지 말고, 7항목 보고 후 STOP.** 사용자 별도 `진행` 지시를 받으면 그 시점의 실제 HEAD와 첫 사용자 장애를 다시 확인하고 최소 변경만 수행한다.
