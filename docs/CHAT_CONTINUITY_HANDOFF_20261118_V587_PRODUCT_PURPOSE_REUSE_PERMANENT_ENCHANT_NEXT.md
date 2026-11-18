# SIMC SECONDARY OPTIMIZER — 2026-11-18 최신 제품 완성·범용 엔진·최소 검증 인계 (v587 이후)

> **성격:** 새 일반 채팅에서 수행할 **읽기 전용 독립 복원**. 새로운 프로젝트 개시, 과거 Native 전수 재시험, 영구 마부 전 항목의 독립 효과 인증이 아니다. 사용자가 이 인계를 명시 요청했기 때문에 작성했다. **인계용 HEAD 기준:** `a7fd8035688961c3b03492e126c33d9fd2c9c53c` (작성 전 실제 HEAD). 이 문서 자체의 커밋 뒤에는 바뀌므로 반드시 현재 브랜치 HEAD를 새로 확인한다.
> 저장소 `degong2-code/simc-secondary-optimizer-runner`; 격리 브랜치 `probe/chat-cache-v035-20261024`. 권한 있는 주 제품 채팅의 소유권을 인계 기록만으로 옮기지 않는다.

## 1. 프로젝트가 사용자에게 제공할 **단 하나의 핵심 가치**

**새 WoW 시즌·확장팩에서 런타임 AI/LLM 없이 시즌 원본·G/J/F/O 환경을 자동 구축하고, 사용자가 지정한 목표 ilvl(기본 334) 또는 최종 CHMV 총량 T를 기준으로 실제 SimulationCraft DPS를 최대화하는 치명·가속·특화·유연의 미래 파밍 목표 *절대 rating*을 찾는다.**

- 대상 **26개 DPS 전문화만**. 증강 기원사·탱커·힐러 제외. 목표는 전역 최적 수학적 증명이나 장비 조합 탐색이 아니라 실제 SimC로 관측한 최고 DPS의 CHMV 목표 및 실질적으로 다른 근접 대안이다.
- 일반 사용자가 입력: 직업/전문화·종족·특성, ilvl 또는 직접 최종 T, 장신구 2개, 선택 특수장비/제작장비·장식 최대 2개, 최고 품질 보석/영약·소모품/무기 기름·영구 마부, 전투 조건. **현재 착용 장비 전체나 완전한 SimC 프로필을 필수로 받지 않는다**. SimC 프로필 업로드는 주로 특성 등 캐릭터 정보 획득용 선택 기능.
- 제품은 동일 시즌 대표 일반 장비·무기·티어 4pc/주능력치·SimC 프로필을 내부 구성한다. **`G`**=대표 장비·무기 예산, **`J`**=기본 보석, **`F`**=영약, **`O`**=선택 무기 기름 고정 스탯. `B=G+J+F`, `T=B+O`, `c_final=c_base+o`. 수동 최종 **T 우선**, `B=T−O`. `L/E/O` 정적 고정치·하한·중복 방지, 장신구 정적 스탯의 G 외부 소유권을 유지한다.
- SimC가 장비/마부/장신구/장식/보석/기름의 실제 효과·proc·APL·DPS를 책임진다. 우리 제품은 **정확 ID·빌드·부위/손·SimC 입력, 대표 프로필, CHMV 회계·JSON2 rating, DPS/SEM·95% 비교, 후보/캐시·취소·재개/결과 출력**을 책임진다. 통계적으로 95% 우위 미확정이면 관측 1순위와 구분한다.
- **개발 범위 밖:** 현재 장비의 스탯 재분배, 장비 추천/파밍 경로, 시즌 전체 장비 DB, 독립 신규 탐색기, 전문화별 APL 작성, SimC 효과 재구현, 별도 발동 인증 Gate, 영구 런타임 AI 호출.

## 2. 최신 사용자 결정의 우선권 — 오래된 PENDING 해석 금지

우선순위 **최신 사용자 직접 결정 > 승인 v1.4.3 및 비충돌 보충 정책 > 실제 현 코드/CURRENT/Actions/Native·SHA 원본 > 과거 인계/실험**.

1. **ZERO-SOURCE 범용 시즌 환경 자동 구축 엔진 기능은 PASS로 수용**: 실 제로베이스 `v567`, 실제 Windows Chrome `v570`가 현재 시즌에서 증명. *미출시 미래 시즌을 기다렸다 재시험*해야 완료된다는 옛 기준은 폐기. 미래 출시 시 갱신은 정상 운영. 단 **미출시 시즌 모든 옵션이 미리 검증됐다**는 뜻 아님.
2. **필수 P1 = 시즌/확장팩에서 적용 가능한 영구 마부 전체 최고품질·정확 ID·부위/무기·SimC·고정 E/소유권·사용자 선택 자동 구축/연결 완성.** 기존 G/J/F/O가 PASS여도 *전체 Environment Build 최종 SUCCESS*는 모든 필수 영구 마부 선택지 완료 전 보류. **미선택·미검증 항목은 기본 G/J/F/O 실행을 막지 않는다.**
3. **죽음의 기사 룬벼리기는 SimC 클래스 소스 전용 영구 무기강화**, Wago 실물 마부 아이템이 아님. 일반 마부의 Wago/ExpansionID/시즌 소속/제작품질/정적 CHMV E 인증 경로를 적용하지 않는다. 현재 SimC가 지원하는 룬 ID·직업·손·충돌·프로필/캐시만 맞추고 효과는 SimC에 맡긴다.
4. **옴니움 장서 및 확장팩 전용 특수 시스템은 핵심 일반 제품 완성 이후 선택형 모듈로 별도 갱신·ON/OFF 검증.** 본 기능의 선행 Gate 아님.
5. `v290+v291+v293` 현재 적응형 SimC 탐색·실행·캐시·통계를 **유지**한다. `v303~v312`의 새 정책·SEM 미세화·추가 최적화 엔진을 P1 필수로 만들지 않는다.
6. 이름은 공식 한국어가 확보되면 사용, 아니면 **원본으로 확인 가능한 효과 설명** 표시; 모르면 임의 효과/명칭 만들지 않음. 동일 확장팩 소속이면 시즌별 개별 귀속 인증 불필요, 변경된 정적 rating은 해당 실제 선택/빌드에서 필요한 만큼 확인. 최고 품질은 **동일 효과·사용 조건·적용 범위, 비열등 수치**를 증명할 때만 낮은 품질 숨김. 기존 게임 빌드 계수와 새 빌드 값을 무단 복사하지 않음.

## 3. 실증 완료 영역 — 신규 오프라인 PASS와 역사 Native 범위를 섞지 말 것

| 범위 | 증거 및 범위 |
|---|---|
| **시즌 ZERO-SOURCE→사용자 SimC** | [v567 #44046442654](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44046442654) 실제 70783/334 원본 수집·G2850/J92/F165/O0, B=T3107, 보석 최고품질 2축/최소 Native 측정, 설치 후 사용자 DPS6·SEM/95%/캐시. 기능 PASS |
| **실제 첫 Chrome 사용자 기본 환경** | [v570 #44074372451](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44074372451) 빈 환경→시즌 Build→v212 설치→장신구2→SimC DPS64→결과 화면 PASS. 이 1개 기본 시나리오는 전체 26 DPS/선택지 완성 아님 |
| **선택 마부 E와 수동 T** | [v530 E0 #43905387382](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43905387382), [v532 가속 E+30 #43910202520](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43910202520), [v533 특화 E+26 #43910935776](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43910935776), [v534 수동 T와 양수 E #43974259684](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43974259684). **그 exact 생존 사냥꾼·반지1·선택 조합**만 실제 Native PASS; 전체 마부 등록 아님 |
| **기름 O와 사용자 T** | [v578 #44098212428](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44098212428), [v580 #44106357901](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44106357901), [v581 #44110104367](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44110104367) Chrome→T3500/B3468/O32→DPS 실제 2후보·재개·cache-only PASS. 최고 관측 DPS≈169750.54, SEM≈680.33; **95% 우위 미확정**, 전역 최적 증명 아님 |
| **탐색 엔진** | `v290` 전역 분산→실제 DPS/SEM 기준 다중 스케일 탐색·2후보 확인; `v291` Native JSON2/SHA/캐시·취소·재개; `v293` scout56/confirm320 새 세션 기본. 이미 제품 경로에서 사용된 기존 자산 |
| **영구 마부 소스** | [v582 #44211446707](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44211446707) 38/38 원 SimC 고등급 후보↔Wago 실제 물리 아이템 조인, 하위품질 포함 76/76; [v583 추가 소스 #44217110154](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44217110154) 기존 38 외 33개를 **DPS 장비 16(최상위 원본 등급 후보 8) / 전문기술 도구12 / 미확정5**로 소스 분류. **시즌마다 이 숫자를 하드코딩하지 않음** |
| **추가 8계열 효과/품질** | `v584/v585` 기존 v191/v211/v213 재사용. 70783 8계열(다리6·원거리 무기2) 모두 정적 CHMV 증가 관측 없음. **5/8 원본 계수 비감소**는 실제 값 우위 증명이 아님(코드에서 연결된 `id_spell` 평균값을 우선할 수 있음). **8/8 동일 효과·최고 품질 사용자 승인은 미확정**, 다른 등급 주문 효과는 SimC에 맡김 |
| **DK 룬벼리기** | `v295→v216→v212→v113→v106/v098/v294` SimC 전용 기존 구현. [v586 #44225811527](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44225811527) 실제 SimC 소스 7종을 사용한 **84개 집중 오프라인 PASS**(새 Native 0), 신규 SimC ID 동적 반영/손/충돌/직렬화. `v587`은 새 시즌 선택에서 설치 v212 SimC 목록이 없으면 오래된 고정 fallback으로 통과하는 결함 차단. 신규 DK 실제 사용자 Native E2E를 했다는 뜻 아님 |
| **최신 코드 회귀** | [v587 집중 #44233373988](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44233373988) **104 PASS/0 FAIL/신규 Native0**, [v401 78 정합성 #44233716054](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44233716054) **SUCCESS**. 일부 다른 과거 push 워크플로는 CANCELLED·SKIP이 존재하며 모든 Action 무조건 SUCCESS 주장 금지. |

**78 공식 원장:** `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json`과 파생 `78_ELEMENT_STATUS_GENERATED.md`: 개별 제품 통합 **15/78 COMPLETE**, `full_product_e2e=PENDING`. 이는 **제품 기능 구현률**도, 단일 모든 전문화 완료율도 아니다. `next_review=B10`은 원장 검토 순서이지 다음 개발 과제 명령이 아니다.

## 4. 영구 마부의 실제 현재 경계 — 소스는 연결되었고 사용자 선택은 아직 끊김

**검증된 것**:
- `v216→v583`가 기존 v161/v254/v280/v281/v275와 v217 SHA 캐시를 재사용하고, **추가 `CraftingDataEnchantQuality` Wago 테이블 1개만** 새 빌드에서 필요 시 수집. 실제 ItemID↔SimC enchant ID를 조인; `ExpansionID`로 확장팩 소속, 별도 시즌별 인증 없이 지원 가능. 원본은 빌드별 재사용, SimC revision 변경만으로 정적 CSV 폐기 금지.
- `v583→v584` 추가 8계열을 기존 v191/v211/v213의 effect/slot/quality 분석에 연결. 모르는 ItemMod는 원형 보존·보류, 임의 CHMV·효과 만들지 않음. `v585` 동일 계열 원본 스탯 코드·스케일링·계수 비교는 **source-only**.
- `v587` **기존 `v220.selected_equipment_source_mask_match`**는 선택한 *정확한 대표 장비 1개*에 대해 원본 SimC 클래스·InventoryType·subclass와 슬롯/손 관계를 비교하는 재사용 가능한 순수 helper. [v587 기록](development/notes/2026-11-18_p1-v587-exact-selected-enchant-scope-and-dk-source-guard.md). **여기서 반환하는 `matched`는 등록·품질·효과·정적 E 승인 의미가 아니다**. 테스트의 아이템 ID는 합성 예시다.

**아직 미완료**:
- 실제 제품의 **동일 빌드 봉인 `v230` 대표 장비 item metadata**와 위 `v220` 함수를 직접 결합하는 **런타임 producer→consumer** 경계. 현재 helper는 v216/v196 일반 사용자 선택 provider에서 호출하지 않음.
- 검증된 전체 영구 마부의 **같은 효과/사용 조건 최고 품질, 정확 부위·무기·손, 실제 SimC `enchant_id`/프로필, 정적 CHMV E 소유권·중복 방지, v220 기존 필수 `source_relation`/`simc_input`/`product_input`/`chmv_budget` 증거, v196/v212/v113 자동 선택 등록**. 원본 `v216` default receipt map/source-only `v113.runtime_selectable=false` 경계가 남아 있음.
- 공식 한글 이름이 없다면 **확인된 효과 요약**만 보여준다. 이름/품질 등급만으로 동일 효과 인증하거나 잘못된 아이템을 추론하지 않는다.
- 이 완료 전 **영구마부 전 선택지/전체 Environment Build 최종 SUCCESS 금지**. 미선택 추가 옵션 때문에 정상 BASE G/J/F/O 사용자 DPS를 막지 않는다.

**혼동 금지:** `v220`은 이미 코드에 존재하는 Policy A 등록기다. v587 helper는 **그 내부에 있는 미승격 비교 기능**일 뿐 원본 인증 네 축·사용자 UI 등록을 완료한 새 승인 엔진이 아니다. 새 독립 Gate/인증 패키지를 만들지 않는다.

## 5. 차기 개발에서 **가장 중요한 작업 하나**와 경로

**단일 첫 작업:** 기존 대표 장비 1개의 *실제* 봉인 `v230` item metadata와 현재 Wago/SimC source-joined 영구 마부 1개를 기존 `v220.selected_equipment_source_mask_match`의 입력으로 **원본 `v216→v196` 사용자 옵션 생산 경계에서 정확하게 연결**한다. `v230`을 새로 수집·재구현하지 않으며 현재 품질·E/SimC 승인까지 무조건 건너뛰지도 않는다.

**이 작업의 완료 조건:**
1. 동일 빌드·설치 SHA·아이템 메타데이터 출처가 실제 기존 v217/v230에서 인증됨. 목표 대표 장비의 실제 슬롯/손·아이템 ID, 정확한 마부 source class/inventory/subclass가 서로 맞음.
2. 잘못된 부위·무기·손/다른 빌드·미설치 항목은 해당 선택만 정확한 PENDING 또는 거부; **기본 정상 환경은 그대로**.
3. 해당 검증된 범위만 기존 `v220`의 더 큰 `simc_input/product_input/chmv_budget` 증거와 `v196→v212→v113` 소비 지점으로 넘김. 없는 증거를 true로 만들거나 합성 테스트 아이템을 사용자 목록에 추가하지 않음.
4. 새로운 HTTP·DB2·Native 없이 봉인된 소스/최소 focused 테스트로 구현할 수 있는지 먼저 확인. **불가피한 실제 신규 SimC 프로필/정적 E 경계 1건만** 필요할 때 bounded Native를 opt-in 실행; 기존 반지3·기름·제로베이스 실증을 재실행하지 않음.
5. 선택한 첫 실제 사용자 기능이 정확히 동작하면 **STOP**하고 다음 끊김 지점 하나만 검토. 필요 없는 계수·proc 세부 조사, 전 마부×26전문화 반복, 시즌 전수 장비 탐색 금지.

**그다음 짧은 로드맵:** (a) 검증 가능한 동효과 품질 계열/부위만 기존 `v191/v211/v213/v196/v220` 경로 확장 (b) **정적 C/H/M/V가 실제 변하는 마부만** 기존 E 측정·귀속 재사용, 비CHMV 효과는 SimC 입력만 정확히 (c) 최고품질 선택지 자동 공개, 사용자 장비 슬롯·SimC 프로필·캐시 identity·JSON2·DPS 연결 (d) Windows 실제 새 선택 1건 최소 E2E 후 범용 사용자 흐름/M3~M6 마무리, M7/78 공식 수락 별도 (e) Omnium 등 확장팩 고유 모듈은 후속.

## 6. 필수 유지 / 하지 않을 일 — 비용과 증거 판정

**항상 `STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW`**.

- 변경 전 짧게 밝힐 것: **사용자가 어느 화면에서 무엇을 못하는지, 어떤 실제 producer/consumer가 끊겼는지, 기존 함수·Native·캐시로 풀 수 있는지, 추가 HTTP/DB2·Native·CPU/RAM/I/O·패키지/캐시 비용, 어떤 성공 조건에서 STOP할지.**
- **KEEP/REUSE:** 동일 시즌 G/J/F/O/보석 최소 Native/기름 O·수동 T/정적 E·L·예산/JSON2·실제 DPS/SEM/95%/캐시·취소 재개, 이미 봉인된 원본 v217, v290/v291/v293. 변경 내용과 독립적인 과거 Native를 다시 실행하지 않음.
- **FIX/CONNECT:** 실제 소비하는 동일 빌드/일부 사용자 선택에 필요한 정확 ID/슬롯/프로필/고정 수치·SHA. 미확정 *선택*은 fail closed, 미선택 옵션은 BASE 비차단.
- **STOP:** 새 마부 조사 전 모든 주문 효과 메커니즘 재현, 품질 계수 비감소를 런타임 우위 인증으로 과장, 38/76/33/16/8을 다른 시즌 고정치로 적용, 룬벼리기 Wago/품질/CHMV E 인증, 26×전 마부 Native 반복, 전 시즌 장비 DB, 과도한 새 Gate/인증서/새 최적화 엔진/불필요한 SEM 연구. 일반 임시 마부 제외, 기름은 별도 지원.
- **증거 신분을 구별**: 오프라인 PASS ≠ 새로운 Native PASS ≠ 실제 사용자 E2E ≠ 26 DPS 전범위 ≠ 공식 78 원장 승격. 공식 78 검토 순서와 사용자 우선 개발 작업은 다르다.
- 같은 시즌 정적 아이템 캐시를 SimC revision 변경만으로 무효화하지 않음. DPS 캐시는 실제 SimC 바이너리·revision/프로필·옵션·전투·iterations 등을 별도 identity로 구분.

## 7. 복원 읽기 순서 및 권한

1. **본 인계** → `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 첫머리 → **현 브랜치 HEAD**, 현재 최근 Actions, 관련 Native·Wago 원본 영수증. 인계 SHA는 작성 시점 역사 스냅샷.
2. `docs/development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md` 최상단, `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`, `docs/development/PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md`, `docs/development/POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md`.
3. `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md`, `docs/USER_APPROVED_GEM_J_POLICY_20261117.md` 최신 F절, `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json`, `docs/development/78_ELEMENT_STATUS_GENERATED.md`.
4. 최근 실제 소비 경계: `docs/development/notes/2026-11-18_p1-v587-exact-selected-enchant-scope-and-dk-source-guard.md`, `...p1-v586-simc-only-dk-runeforge-and-unnecessary-work-boundary.md`, `...p1-v585-enchant-quality-and-ranged-source-comparison.md`, `...p1-v583-generic-additional-enchant-scope-classification.md`, 그리고 `runner/v216_environment_build_coordinator.py`, `runner/v230_simc_item_metadata.py`, `runner/v220_catalog_auto_admission.py`, `runner/v196_current_season_user_catalog.py`, `runner/v212_environment_manifest.py`, `runner/v113_local_web_api.py`, `runner/v098_target_user_scenario_bootstrap.py`.
5. `docs/development/INDEX.md`, `FILE_MAP.md`, `EVIDENCE_INDEX.md`는 보조 지도. 과거 [v581](CHAT_CONTINUITY_HANDOFF_20261118_V581_PRODUCT_COMPLETION_PERMANENT_ENCHANT_FIRST.md) 인계는 역사·실증 보존용이지 최신 next 작업을 덮어쓰지 않는다.

**권한:** 격리 브랜치 개발은 사용자의 별도 `진행` 지시 이후 허용된 범위 내. 사용자 승인 없이 `main` 병합, `v003 immutable` 변경, `v016_SCENARIO_CONTRACT` 원본 직접 통합 완료 주장, Project Sources/Instructions UI 적용 주장, 공식 Work OS M0/Shared State 승격, 78요소 `COMPLETE` 임의 변경, 주 제품 개발 채팅 소유권 이전 금지.

## 8. 새 채팅 첫 응답 — **READ-ONLY 7항목 후 STOP**

현재 GitHub HEAD·CURRENT·Actions·관련 실제 Native/Wago/SimC 원본을 읽기만 한 후 다음만 보고한다.

1. **실제 최신 HEAD**, 최근 Actions **PASS/FAIL/CANCELLED/SKIP**를 구분 (중단된 오래된 run을 제품 코드 실패로 일반화하지 않음).
2. 최종 26 DPS / 목표 절대 CHMV 제품 목적 및 **지금 사용자에게 실제 가능한 구간**.
3. ZERO-SOURCE v567/v570 엔진 **PASS**와 **영구마부 전체 사용 등록 PENDING**의 차이, 원본 38/76 + 추가33/16/8 source-only 경계.
4. v290/v291/v293 최적화 기능과 실제 Native, 오프라인 104 PASS, 95% 미확정/전역 최적 부정의 신분 구분.
5. **필수 미완료 영구마부 실 소비 경계**, 선택형 PENDING과 Omnium 후순위, DK SimC-only 별도 완료 경계.
6. 비용 대비 가장 중요한 **다음 작업 정확히 하나**, 재사용 기능과 실제 producer/consumer·STOP 기준, 신규 HTTP/Native 필요 여부.
7. 미확인 증거/일반 개인 Windows 설치, 공식 `15/78 COMPLETE`·`full_product_e2e=PENDING`, GitHub·Project UI·Work OS/주채팅 권한.

**첫 응답에서 코드·GitHub 문서 수정, 신규 Actions·Native·HTTP·DB2, 마부 원본 재수집을 하지 않는다. 7항목 보고 후 STOP.** 사용자가 **`진행`**을 명시해야만 그 시점 최신 HEAD와 처음 막힌 진짜 사용자 소비 지점을 재확인해 최소 범위로 구현한다.

**핵심 한 문장:** 사용자가 선택한 목표 환경에서 **AI 없이 SimC DPS를 최대로 만드는 미래 CHMV 절대 rating**을 찾는 일반 프로그램을 완성한다. 이미 성공한 원본·예산·최적화/캐시를 재개발하지 않고 **영구 마부 실제 등록·선택·프로필 연결의 끊긴 첫 지점만** 고친다.
