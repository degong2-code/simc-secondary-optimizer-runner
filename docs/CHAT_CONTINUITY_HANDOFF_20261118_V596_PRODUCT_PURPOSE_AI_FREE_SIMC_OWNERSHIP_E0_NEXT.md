# SIMC SECONDARY OPTIMIZER — v596 이후 최신 사용자 제품 완성 중심 독립 복원·일반 채팅 인계

**날짜:** 2026-11-18. **성격:** 새 채팅의 **READ-ONLY 첫 복원** 및 이후 사용자 별도 `진행` 때 최소 개발을 위한 지속성 기록. 본 문서 작성은 코드 수정, 원본 SimC 제품 직접 통합, Project Sources 실제 등록, Work OS 승격 또는 주 제품 개발 채팅 소유권 이전이 아니다.

- 정본 저장소: `degong2-code/simc-secondary-optimizer-runner`
- 격리 브랜치: `probe/chat-cache-v035-20261024`
- **이 인계 작성 전 실제 확인한 HEAD:** `8b3f099f926bd576788a85768bb4dd8be769adbb` (v596 CURRENT 기록까지 반영). 이 SHA는 **역사적 스냅샷**. 새 채팅은 무엇보다 **실제 HEAD를 다시 조회**하고 그 HEAD의 CURRENT·코드·Actions·Native 영수증으로 최신을 재판정해야 한다.
- 직전 상세 역사 인계: `docs/CHAT_CONTINUITY_HANDOFF_20261118_V587_PRODUCT_PURPOSE_REUSE_PERMANENT_ENCHANT_NEXT.md`. v587의 “v230→v220 첫 연결부터 시작” 권고는 **v588–v596에서 이미 구현한 과거 NEXT**이므로 다시 수행하지 않는다.

## 1. 사용자 최종 목적과 제품이 실제로 해야 할 일

이 제품은 **미래 파밍 목표가 될 절대 치명·가속·특화·유연 rating**을 사용자가 선택한 목표 아이템레벨(기본 334) 또는 **수동 최종 CHMV 총량 T**에 대해 **실제 SimulationCraft DPS 최대화**로 구하는 **AI 없는 일반 사용자 프로그램**이다.

- 지원 전문화: **26개 DPS만**. **증강 기원사, 탱커, 힐러 제외**. 첨부 역사 v1.4.1에서 27개/증강 포함이 보이더라도 **후속 최신 사용자 결정과 repo 26-DPS 계약이 우선**이다.
- 사용자 입력: 직업·전문화·종족·특성, 목표 ilvl 또는 최종 T, **장신구 2개**, 필요한 선택 특수장비·제작장비, **장식 최대 2개**, 보석·영약·음식·물약 등 선택 가능한 검증 소모품, **영구 마부**, **별도 무기 기름**, 전투조건. 현재 착용한 일반 장비 전체를 입력하지 않는다. SimC 프로필 업로드는 캐릭터·특성 수집용 선택 기능이며 현재 장비를 최적화 예산으로 가져오지 않는다.
- 내부 실행: 해당 시즌 대표 일반 방어구·무기·주능력치·**티어 4세트** 및 정확한 SimC 프로필 구성. 시즌/확장팩 변경 시 같은 시즌의 출처·빌드에서 **G/J/F/O 모두** 자동 구축·검증해 **B=G+J+F, T=B+O**. 수동 최종 T 우선, `B=T-O`; `c_final=c_base+o`. 실물 특수 장비의 정확한 L, 영구 마부 정적 E, 무기 기름 O의 회계·스탯별 하한·중복 방지 필수. 장신구 고정 스탯은 자유 G 밖; JSON2 미관측은 0 실측이 아니다.
- 기존 적응형 SimC 엔진 `v290+v291+v293`: 분산/다중 스케일 후보→JSON2 실제 rating·DPS·SEM→**95% 통계 판단만**, **관측 최고 DPS와 통계적 확정 분리**, 실질적으로 다른 근접 대안, **절대 rating + 비율** 출력, 캐시·취소·재개. 전역 최적 증명이 없으면 명시한다.
- 제품 범위 **아님**: 기존 착용 장비의 스탯 재분배, 장비 조합/파밍 경로 추천, 시즌 모든 장비 DB, 새로운 최적화 엔진, 자체 APL·주문 발동/효과 모델, 미출시 미래 시즌을 기다리는 반복 Gate, 영구 AI 의존성.

### 개발 AI와 제품 실행 AI를 반드시 구별

**개발할 때는 AI를 적극 활용한다. 하지만 배포 프로그램 실행 중에는 AI·LLM·모델/API 호출·추론 에이전트·AI 서비스 의존성 0이어야 한다.** 런타임은 검증된 출처·정확한 ID·정해진 코드·캐시·실제 SimC만 사용한다.

### SimC 책임 경계 — 최신 사용자 직접 교정

**우리 책임:** 정확한 item ID, enchant ID, 장비 ilvl/옵션, 부위·손, 대표 프로필, 시즌 예산/G/J/F/O·L/E/O, 정적 `gear_*` rating 중복 방지, 선택 품질의 제품 UI 중복 정리, Native JSON2와 입력/결과 정합, 후보 평가·95%·캐시·중단·재개.

**SimC 책임:** 장비/마부/장신구/장식/보석의 **주문 효과·발동·proc·APL·실제 DPS**. **장비를 정확히 입력했는데 그 주문이 실제 효과를 내는지 별도 효과 인증 Gate를 만들지 않는다.** 일부 v584/v585 효과·계수 조사 기록은 역사 자료이지 후속 독립 발동 인증 필수과제가 아니다. 품질 중복제거는 같은 효과/사용조건/범위와 수치 비열등을 출처가 뒷받침할 때만, 실제 효과 발동 실험과 분리한다.

**영구마부 E=0은 정상이며 매우 흔하다.** E는 정적 CHMV rating만 뜻한다. 비정적 주문/발동 마부는 SimC에 정확히 전달해 DPS 효과를 계산하게 하고 **E=0 때문에 차단하지 않는다**. 세 경우 구별: **검증 E0** (예산 추가/하한 0), **드문 검증 E>0** (정확한 스탯별 고정치·1회 포함, 수동 T 불변), **E 미확정** (미관측 수치를 0으로 둔갑시키지 않고 해당 옵션만 보류). 효과 처리 성공 여부 검사를 추가하지 않는다.

## 2. 이미 실제로 PASS한 제품 영역 — 다시 구현하거나 반복 Native하지 않는다

| 구분 | 정확한 역사 영수증과 의미 |
|---|---|
| **ZERO-SOURCE 시즌 자동 구축** | [v567 실제 #44046442654](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44046442654): 현재 기준 빌드 70783/ilvl334, G2850 J92 F165 O0, B=T3107의 원본 환경→실제 SimC 및 후속 단계 PASS. **범용 엔진의 현재 시즌 zero-source 기능 PASS 수용**. 다른 신규 시즌 원본값을 이 숫자로 고정하지 않는다. |
| **Windows Chrome 일반 사용자 E2E** | [v570 #44074372451](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44074372451): 빈 환경→시즌 Build→v212 설치→장신구 270175/270173·생존 사냥꾼334→실 SimC Native DPS **64회**→DPS 약 **179563.61 / SEM316.82**·관측 1순위/대안 표시, 95% 확정 아님. **이 동일 경로 Native 64회를 또 실행하지 않는다**. |
| **ZIP 캐시/중단·재개** | [v572 #44082378854](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44082378854): 실제 Windows ZIP 중단→재시작→재개. 같은 조건에서는 기존 실측/캐시 재사용. |
| **영구마부 좁은 실제 Native** | [v530 E0 #43905387382](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43905387382), [v532 가속 E+30 #43910202520](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43910202520), [v533 특화 E+26 #43910935776](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43910935776), [v534 수동 최종 T #43974259684](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43974259684). **정확한 70783/334 생존 사냥꾼·반지1·장신구·SimC 바이너리 등 범위 한정**, 일반 26 DPS·전부위 마부 승인 아님. |
| **기름 O 및 수동 T** | [v581 #44110104367](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44110104367): Windows Chrome 기름 O32·수동 T3500, 실제 후보/캐시 재개 PASS, 최고 DPS 약 169750.54/SEM680.33, 95% 미확정. |
| **기존 최적화** | `v290/v291/v293` 적응형 실제 SimC DPS/SEM/95%/캐시/취소·재개. 새로운 탐색기·SEM 미세 엔진 불필요. |

**유의:** 기존 개발 성과를 신규 Native PASS로 재포장하지 않는다. 역사 증거의 build/전문화/장비/옵션/바이너리/반복조건과 새 실험이 동일할 때만 캐시·영수증을 재사용한다.

## 3. v587→v596 최신 구현 경과 — 중복 개발을 막기 위한 차이

- **v588**: 기존 v232 G 대표 장비 및 봉인 v230 item metadata ↔ v583 물리 마부 ↔ v196/v220 마스크 source-only **첫 연결**. 미선택 마부 때문에 대형 item_data를 재스캔하지 않음.
- **v589**: `v098` 최종 사용자 장비 적용 **이후** 실제 선택 슬롯·아이템 ID를 `v216/v230/v196/v220`에 연결. G 참조 장비를 사용자 실제 장비라고 착각하지 않음.
- **v590**: 기존 v583/v584 **추가 8계열 후보의 선택 ID 단위 원본**을 source-only 소비. 별도 SimC 주문 발동 인증/품질 우위를 사용자 실행 필수 Gate로 확대하지 않음.
- **v591**: 제품 목적·SimC 책임 경계 재교정. v113의 설치 게임 빌드·기존 원본 스냅샷 참조 누락 연결, 물리 적용조건에서 불필요한 독립 spell 효과 검증 제거.
- **v592**: 과거 v570 일반 Chrome E2E 64 Native **이미 PASS** 발견해 중복 실행 STOP. 최신 Windows/Ubuntu 오프라인 회귀에 선택 마부 마스크/사용자 경로 포함.
- **v593**: 원본 `finger1/finger2`는 **적용 가능한 반지 계열**이지 사용자 손 미확정 오류가 아님. `v216` sealed 원본 영수증→`v196/v220` 4종 Policy A 심사→`v212` 등록에서 그룹 ID 일치. 실제 손은 v098 최종 장비에서 별도로 검증.
- **v594**: 기존 신뢰된 `v220.chmv_budget`의 `fixed_E` 4스탯·SHA를 `v196→v212→v113`에 전달. 명시 검증 E=0과 E 미기재를 구분, UI는 read-only.
- **v595**: 설치된 `v212` E0 또는 양수 E의 **사용자 슬롯별 예산 미리 계산**. E0 B/T 변화 0, 드문 양수 E 자동 참조 G 소유권 확정 시 1회, 수동 T 최우선. 이것은 해당 시점 **예산 단계**였고 실제 SimC 연결은 다음 v596에서 수행.
- **v596 최신**: **신뢰된 `v212` 등록·4스탯 E0·사용자 실제 반지 item ID/부위 마스크·최종 SimC `enchant_id` 정확히 1회**를 `v106→v098→v096→v093/v094` 기존 DPS/프로필/캐시 정체성에 연결. `v096`가 서명된 원본/동일 B/T/E0/정확한 SimC 프로필을 독립 대조. `v113` 설치된 E0 승인 목록을 별도로 제공하고 기존 UI는 **finger1 한 반지** 선택지에 한해 노출. **finger2는 내부 v106/v098/v096에서만 수용**, UI 두 반지 동시 사용 불가; 드문 E>0/미확정 마부 일반 사용자 실행은 아직 잠금. **합성 등록 원본을 활용한 오프라인 PASS만 확인, 새 일반 E0 마부 실제 Native DPS E2E는 아직 미확인.** [v596 자세한 구현 기록](development/notes/2026-11-18_p1-v596-source-verified-E0-user-profile-runtime-bridge.md).

**주의:** v587 참고 인계의 다음 과제(첫 v230→v220 source 연결), v591의 '첫 기본 E2E 신규 64-Native', v594/595의 'E0 실행 경로 미연결'은 **당시 기준 기록**이다. 최신 v596 상태를 덮어쓰지 않는다.

## 4. 최신 검증 증거의 정확한 경계

- **v596 코드/테스트 HEAD**: `1675ee8d8af7b6701666dd13293776c4808b6c8b` (현재 HEAD `8b3f099f...`는 이를 설명하는 후속 docs 포함).
- **최신 코드 집중** [Actions #44264004427](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44264004427): **680 PASS / 2 SKIP / 0 FAIL** (682 tests), 최종 `SUCCESS`. 같은 코드 [78계약 #44264004439](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44264004439) **SUCCESS**, 제품 E2E 아니다.
- **Windows + Ubuntu 웹 API** [#44263274946](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44263274946): 양 OS **483 PASS / 1 SKIP / 0 FAIL**. **UI 두 OS** [#44263274886](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44263274886): 107+199+4 오프라인 그룹 SUCCESS. 후속 최종 집중 작업은 합성 v096 회귀 fixture 수정; 위 두 운영 계층 CI는 earlier production commit `f09b5510...`이며 최신 문서 commit에서 새로 Native 검증했다는 뜻 아님.
- **중간 집중 FAIL은 숨기지 않음**: [#44263509667](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44263509667), [#44263834325](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44263834325) 두 건은 신규 합성 `v096` 테스트 fixture `simc_revision` 누락, 예외 유형 기대 불일치. 최종 집중 `#44264004427`에서 테스트 교정 후 PASS. 오래된 CANCELLED나 작업별 SKIP을 제품 PASS로 세지 않으며, 새 채팅은 해당 시점 최신 각 run의 결과를 다시 확인한다.
- **이번 v588–v596 새 효과 입증 Native 0**으로 기록. 신규 실 SimC 체인 `v596` E0는 아직 **PENDING**이다. `source_only` 마스크 일치, 합성 테스트 승인, 설치 옵션 공개와 Native 실제 DPS는 별개.
- 동일 시즌 정적 아이템 캐시는 SimC revision 변경만으로 폐기 금지; DPS 캐시는 실제 **프로필 전체·바이너리·캐릭터·마부·부위·아이템·T/O·iterations·전투조건** 정체성으로 구분.
- **공식 원장** `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json` 및 생성 결과 `docs/development/78_ELEMENT_STATUS_GENERATED.md`: **15/78 COMPLETE, full_product_e2e=PENDING**. 27/78 일반 범용 PASS 등 서로 다른 축을 합산하지 않는다. `next_review=B10`은 공식 검토 순서이지 다음 사용자가 실제로 못 하는 핵심 개발 명령이 아니다.

## 5. 무엇이 진짜 PENDING인가 — 기본 제품/옵션/모듈 분리

**기본 제품에서 이미 확인:** ZERO-SOURCE 현재 시즌 구축·실제 한 사용자 Windows Chrome DPS64·표준 예산/JSON2/95% 결과·ZIP 재개/캐시의 **각 실제 증거 범위**.

**우선 필수 연결:** (1) **v596 일반 설치 v212 E0 사용자 선택**을 **실제 해당 시즌의 정확 원본 승인된 반지 1개**로 Windows v113→v098→v096→실 SimC DPS 결과까지 최소 1건 입증; **동일 범위 캐시가 있으면 먼저 재사용**. 기본 설치에 해당 E0 등록 항목이 실제 없다면 **그 출처·등록·선택에서 첫 막힌 원인만 조사·수정**, 수치를 임의 생성하지 않음. (2) 이후 **검증된 최고품질 전체 일반 영구 마부의 실제 선택 UI·프로필 및 드문 양수 E 고정 하한·자동/수동 T, 복수 부위/반지2 UI** 범용 연결. 한 사례를 전 부위·26 DPS·미래 시즌 자동 PASS로 과장하지 않음.

**선택형 PENDING:** 미확인 추가 보석 소켓/비정상 J 권한은 해당 옵션만 보류; 정적 마부 E 미관측은 임의 E0 처리 금지; 장신구 정적 JSON2 gear 레코드 미관측은 사용자 선택 차단 사유가 아님. 일반 무마부 BASE는 계속 실행.

**죽음의 기사 룬벼리기:** `v295→v216→v212→v113→v106/v098/v294` 기존 SimC **클래스 원본** 경로를 보존. Wago 룬 아이템 수집·시즌 소속·제작 품질·정적 E 발동 인증을 새 과제로 만들지 않는다. SimC 소스 ID·직업·무기 손·입력·캐시 충돌만 처리. 일반 시즌 영구 마부와 다른 원본 책임.

**옴니움 장서:** 확장팩 한정 선택 모듈로 **일반 제품 필수 기능 완성 이후** ON/OFF와 정확한 SimC 입력·세션 정체성 업데이트. 기본 Environment Build 완료 선행 Gate가 아님.

**이전 원본 제품:** 보고된 `v016_SCENARIO_CONTRACT` 원본 바이트·Native receipt 독립 확인 전 직접 통합 완료라 주장 금지. 격리 개발 진척도와 별도.

## 6. 다음 사용자 `진행` 때 가장 중요한 작업 정확히 하나

**한 건의 현실 사용자 E0 마부 선택→SimC Native DPS E2E 검증**을 위해 먼저 **실제로 봉인 설치된 `v212`에서 하나의 Policy A 승인·고정 E0 반지 항목을 찾는다**. 그 아이템이 선택한 최종 대표 장비의 class/slot/physical item과 일치하는지 기존 `v216/v230/v196/v220`를 재사용해 확인한다.

1. **환경/입력:** 새 원본 수집이 필요한지 확인하기 전 기존 동일 빌드/봉인 v217/v212·v530/570 캐시/Native를 조회. 승인된 E0 항목이 없으면 막힌 **등록 생산자/소비자 하나만** 최소 수정, 미확정 항목을 억지 승인 금지.
2. **실행:** 가능한 실제 사용자 1시나리오에 기존 `v113`에서 한 손을 선택 → 실제 최종 반지에 정확 `enchant_id` **1회** → E0 B/T 변화 0/수동 T 우선 → 원본 `v096/v093/v094` Native JSON2 DPS·SEM·95%·프로필 SHA·캐시 기록 확인. **옵션 발동 자체를 검사하지 않는다**.
3. **비용:** 일치 증거/캐시가 있으면 중복 Native 0. 실제 사용자 경로에 새로운 결함이 있고 기존 실측으로 판정 불가한 항목에만 **최소 한 건 bounded Native**. 시즌 전체 마부×26 전문화 반복, 신규 effect engine/Gate, 중복 Wago/DB2 다운로드·32MB v230 스캔, 기본 v570 DPS64 반복 금지.
4. **STOP:** 한 항목의 실제 사용자 선택/프로필/예산/실 SimC 출력 및 세션 identity가 확인되면 **해당 단계 PASS로 좁게 기록하고 STOP**. 그다음 증거 있는 E>0/다른 슬롯·finger2/동일 시즌 선택지 확장을 검토한다. 실제 등록 item 부재/SimC 오류는 **정확한 원문과 막힌 경계**를 기록하고 기본 정상 G/J/F/O는 차단하지 않는다.

**항상 `STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW`.** 매 코드 변경 전에 추가 Native·HTTP/DB2·메모리·I/O·캐시·기존 Python 구조·실행시간을 검토한다. 이미 PASS한 범위는 재작업하지 않는다.

## 7. 복원 읽기 순서, 권한, 새 채팅 첫 응답

읽기 순서:
1. **이 문서**와 실제 브랜치 HEAD (순서상 HEAD를 먼저 확인해도 무방).
2. `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 최상단, `docs/development/notes/2026-11-18_p1-v596-source-verified-E0-user-profile-runtime-bridge.md`, 이어서 v595·v594·v593·v592·v591의 각 직접 기록. v587 인계는 역사 증거/과거 설계 보존용.
3. `docs/development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md` **최상단 최신 정책**, `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`, `docs/development/POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md`, `docs/development/PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md`.
4. `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md`, `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json` 및 `78_ELEMENT_STATUS_GENERATED.md`. 최신 사용자 직접 결정이 구 버전과 불일치할 경우 위 26DPS/SimC/E0/AI 정책 우선.
5. 실 코드: `runner/v216_environment_build_coordinator.py`, `v230_simc_item_metadata.py`, `v220_catalog_auto_admission.py`, `v196_current_season_user_catalog.py`, `v212_environment_manifest.py`, `v113_local_web_api.py`, `v106_user_session_controller.py`, `v098_target_user_scenario_bootstrap.py`, `v096_unified_product_entry.py`, `v290/v291/v293` 탐색기와 웹 UI. **실 코드 상태와 영수증 우선**.

**권한:** 기존 주 제품 개발 채팅이 구현·일반 SimC 시험 소유. 별도 사용자 지시 없는 주도권 이전 금지. 격리 브랜치 내 문서·코드 개발과 원래 제품 source 직접 병합은 구별. **main 병합, v003 immutable 편집, v016 원본 직접 통합 완료 주장, ChatGPT Project UI/Sources/Instructions 실제 적용 주장, Work OS M0/Shared State 공식 승격, 78요소 COMPLETE 수동 변경**은 승인 없이 금지. WEQUIP 영구 런타임/운영 authority 도입 금지.

### 새 채팅 첫 응답 = READ-ONLY 7항목, 그 뒤 STOP

1. 현재 실제 HEAD·최신 Actions **PASS/FAIL/CANCELLED/SKIP**와 증거 범위.
2. 사용자 제품 목적 26 DPS/AI 없는 런타임/최적 절대 rating, 현재 실제 가능한 실행 범위.
3. ZERO-SOURCE v567/570·기본 원클릭 실제 PASS와 v596 일반 E0 선택의 **오프라인 PASS vs 새 Native E2E 미실증** 구별.
4. 기존 v290/291/293·v530–534·v572·v581 실 Native/95%/캐시/중단·재개 증거.
5. **진짜 미완료**: 전 영구마부 선택·E>0·finger2/두 반지 UI, 옵션 보류, DK SimC-only, Omnium 후순위.
6. 다음 한 작업: **실 설치 승인된 E0 반지 1건의 최소 Windows 사용자→SimC 결과**, 기존 봉인/캐시 재사용 및 STOP 기준; 없으면 첫 생산자/소비자 결함만 찾기.
7. 미확인 증거, 공식 15/78·full_product_e2e=PENDING, 권한/Project UI/Work OS 경계.

**첫 응답 중에는 코드·문서·GitHub 수정, 새로운 Actions 트리거/Native/HTTP/DB2 수집, 영구마부 전수 효과 인증을 하지 않는다. 7항목 보고 후 STOP.** 사용자가 별도로 **`진행`**이라고 지시할 때만 새 채팅의 당시 최신 HEAD/사용자 장애를 다시 확인한 뒤 위 우선순위로 최소 비용 개발한다.

**핵심:** AI 없이 **미래 목표 아이템레벨·총량에서 SimC DPS가 높은 CHMV 절대 rating**을 사용자에게 주는 제품을 완성한다. 기존 엔진·Native 증거를 재사용하고, **SimC 효과를 재구현하지 않으며 정상 E=0 반지의 실제 사용자 선택/프로필/결과라는 첫 미완료 연결**부터 끝낸다.
