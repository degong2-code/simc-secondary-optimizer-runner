# SIMC SECONDARY OPTIMIZER — 2026-11-14 v441 / 78요소 수락조건 재정비 이후 단일 인계 정본

> **지위:** 다음 개발 채팅이 기존 대화 없이 상태를 복원하기 위한 최신 단일 인계 정본. 요소별 실제 상태의 **유일한 기계 판독 정본**은 [78개 JSON](development/78_ELEMENT_COMPLETION_CONTRACTS.json). 이 인계 문서 자체는 구현·검증·PASS 승격·Project UI 적용을 뜻하지 않는다. [v431 인계](CHAT_CONTINUITY_HANDOFF_20261113_P1_V431_B8_78ELEMENT_READONLY_RESTORE.md)는 직전 역사 스냅샷이며, 그 문서의 “B8 아직 선택 입력 차단/G-L 미연결”은 **v432~v439에서 후속 연결·실제로 검증한 이후 현재 상태가 아니다**.
>
> **인계 작성 전 독립 확인 (2026-11-14 KST):** private GitHub `degong2-code/simc-secondary-optimizer-runner`, 실제 작업 브랜치 `probe/chat-cache-v035-20261024` **HEAD `ee6fe41675938b34cee98da1238fa4558a3a32a3`** (v441), `main` **HEAD `07133e0aaf738d6e4816a6486057b1cd49c018de`**. 문서 갱신 커밋 이후에는 branch HEAD가 달라진다. 신규 채팅에서 반드시 **실제 브랜치 HEAD를 다시 읽어** 이 스냅샷을 대체한다. `main` 병합·원본 변경·공식 승격은 수행하지 않는다.

## 1. 제품 목표와 최신 사용자 정책

- **26개 DPS 전문화**만 지원; 증강 기원사, 탱커, 힐러 제외. 기본 목표 ilvl 334 또는 사용자가 직접 입력하는 **최종 CHMV T**에서, 미래 파밍 목표가 될 치명/가속/특화/유연 **절대 rating**을 SimulationCraft의 DPS 최대화로 탐색한다. 기존 착용 장비의 스탯 재분배, 일반 전체 장비 사용자 선택, 장비/파밍 경로 추천, 전 시즌 아이템 DB, 새로운 자체 APL/효과 엔진은 범위 밖이다.
- 사용자는 직업·전문화·종족·특성, 장신구 2, 선택 특수장비, 제작/장식 최대 2, 보석/영약/무기 기름/영구 마부·전투 조건 등을 정한다. 내부가 대표 일반 장비·무기·티어 4pc·주능력치·실제 SimC 프로필을 구성한다. SimC 프로필 업로드는 선택이며 현재 장비를 최적화 기본 예산으로 복사하지 않는다.
- 공식 회계는 **`G`=해당 시즌 목표 ilvl 대표 일반장비·무기 예산; `J`=검증 보석; `F`=검증 최고 품질 영약; `O`=선택 무기 기름 고정 예산; `B=G+J+F`, `T=B+O`, `c_final=c_base+o`**. 시즌 갱신 때 **G까지 포함하여** 새 시즌 원본으로 자동 산출·검증하고 B/T 통합 갱신. 수동 최종 T 최우선, B=T-O로 정확 변환. 선택 고유 특수장비의 고정 L은 G 안에 1회 반영·하한 보호; 제작 초기 50:50은 L로 잠그지 않는다. E·O 중복 가산 금지, 장신구 고정 CHMV는 자유 G 밖, 누락 정적 gear 레코드를 0으로 단정하지 않는다. 같은 시즌 참조 G 근사와 전체 Native exact G 혼동 금지.
- SimC가 아이템 발동/효과·APL·무기 피해·DPS를 책임진다. 우리 코드가 ID·slot·ilevel·options, G/J/F/O/L/E, 중복 방지, JSON2 정적 rating, 탐색, 오차·**95%** 비교, 관측 1순위/실질적으로 다른 근접 대안, 캐시·취소·재개·결과·Windows UI를 담당한다. 관측 1순위≠전역 최적해 보장. 추가 독립 효과 인증 Gate/새 최적화 엔진 금지.
- 승인 정책 원본: [v1.4.3 2026-11-02](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) 및 충돌 없는 v1.4 계열; 최신 사용자 직접 수정이 우선한다. **2026-11-14 직접 결정:** “78요소”는 제품 전체가 거의 완성되도록 모든 기능을 빠짐없이 검증하고 문제를 빨리 찾기 위한 관리 체계다. **엄격한 수락 조건 자체도 필수성 심사 대상**이다. 목적에 불필요한 조건은 적극 완화/제거하고, 여러 요소의 범용 검증·공통 증거·통합 E2E는 묶어 재사용하되 78개 각각의 실제 소비/실패 경계와 기록을 보존한다. 이 최신 결정은 이미 v441 코드/계약/문서에 반영됐다. **v441을 다시 구현하거나 새 검사 프레임워크를 만들지 않는다.**
- 정책 적용·개발 진척·공식 권한 구분: Project UI Sources/Instructions 실제 적용 여부 **미확인**. GitHub 문서 기록/사용자 승인과 ChatGPT Project UI 등록은 다르다. 사용자 보고 기준 원본 제품 `v016_SCENARIO_CONTRACT`의 직접 원본 바이트·최종 통합 receipt 확인 역시 미완료.

## 2. 현재 78개 진행도 — 2026-11-14 v441 HEAD 실 조회

정본 경로: [78 JSON](development/78_ELEMENT_COMPLETION_CONTRACTS.json) → [v441 개별 수락조건 전수 감사](development/78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md) → [v401 정책](development/POLICY_78_ELEMENT_COMPLETION_GATE_V401.md) → [자동 생성 상태표](development/78_ELEMENT_STATUS_GENERATED.md) → [78요소 상세 추적표](development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md).

- 총 **78요소**; `generic 18 PASS`, `current_source 18 PASS`, `product_integration 7 PASS`, `historical 12 PASS`.
- 3필수축 기준 **COMPLETE 7/78**: `A8, A9, A10, A11, B2, B3, B7`. `B8`: generic/current_source/product_integration는 모두 **PENDING**, historical만 PASS. `next_review=B8`, `full_product_e2e=PENDING`. 역사 PASS는 3필수 완료 산식에 들어가지 않는다.
- v441은 **78/78 수락 조건 필수성 재검토**, **54개 과잉 문구 완화/범위 정밀화**, **24개 필수 조건 보존**. 78개 상태값 **PASS/N/A 변경 0개**. 구현률이 7/78인 것이 아니라 *공식 수락 계약* 7/78이다. 증거 부재만으로 미구현/결함이라 주장하지 않는다.
- 시즌 독립 RUN의 current_source N/A는 **정말 원본이 필요 없을 때만**: 구체적 ≥40자 사유, Actions·정책 근거, generic 결정론적 회귀 필요. `product_integration`에 빈 N/A는 사용하지 않으며 실제 소비·오류 경계 증거가 필요하다. 실사용 항목만 시즌 자료 검증. 비선택 항목 미확정은 검증된 기본 READY를 막지 않는다.
- 하나의 유효한 v439 실제 제품 E2E·기존 v417 실증·기존 Actions·SHA/캐시가 **여러 요소**의 수락 조건을 직접 입증하면 78 JSON evidence `supports` 및 각 축에 공동 귀속한다. **미관측 선택 옵션이나 다른 25전문화를 증명했다고 자동 확대하지 않는다.**
- 새 채팅의 첫 개발 과제는 v439/v440 증거를 `B8, D4, D6, E1, E2, E7, E9, F7, G4, G5, H1, H3, H4, H6` 등 **현재 해당 조건을 직접 지지하는 요소**에 *실제 재귀속 가능성*부터 심사하는 것이다. v441 [78개 감사](development/78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md)의 공통 검증 묶음 사용. 단 하나의 요소 B8에서 파생 Gate를 계속 늘리지 말고 78개 전체를 병렬 증거 평가한다. 단, JSON의 `next_review`는 현재 B8로 유지하고 근거 없이 다음 요소 COMPLETE로 건너뛰지 않는다.

## 3. 실제 최근 구현과 검증 — 역사/모의/실제 구별

| 계층·커밋/코드 | 달성한 범위 | 검증·한계 |
|---|---|---|
| **v431** `v101_common_representative_equipment`·`v098` | 같은 시즌 gear+tier 두 소스 봉인·주입; 5개 티어 중 4개 재배치, 70575 구 자료 fallback 차단 | [v187 #43428273777](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43428273777) 집중 16PASS + 연관36PASS, 합성 입력; 당시 선택 G/L 실 통합 미완료(이후 해결) |
| **v432~v434** `v432_selected_4pc_budget_bridge`·`v098`·`v096` | 선택 장비의 변경 슬롯 exact 정적 delta, G/고유 L·제작 자유, 물리 프로필, F/O·B/T, 원본 SHA, v091/v090/v062/v065 비실행 검증 연결 | v434 [#43450560916](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43450560916) **100PASS**(집중+연관+v415), Native0; 실 승인 전 preflight |
| **v435~v437** `v096`·`v098`·`v106_user_session_controller`·`v113_local_web_api` | 정적 캐시 raw SHA·최종 프로필 ID·binary/iterations 분리 키, 원본 재생 v096 manifest, 웹 사용자 계획/세션/작업자 → 기존 v094 적응형 실행 연결 | v437 [#43459397096](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43459397096) **148PASS/0FAIL**, 웹 Linux+Windows [#43458963286](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43458963286) SUCCESS; 범용 코드/오프라인 범위 |
| **v438** `v113_local_web_api` | 선택 manifest에서 웹 start/resume의 v212 설치·v217 원본 재검증 누락 수정, v435 세션 SHA 확인 | 웹 양 OS [#43461108968](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43461108968) 각각 354PASS/1SKIP, Native0 |
| **v417 실제 기본 4pc** | KR Retail 12.1.5.70783 생존 사냥꾼 ilvl334, **선택 장비 없음**, G2850/J92/F165/O0→B=T3107; DPS **178334.86**, SEM298.61 | 실제 Windows [#43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756) 환경 Native3/DPS12 및 JSON2/캐시 영수증. 선택 제작 충돌 증거로 확대 불가 |
| **v439 실제 사용자 선택 4pc** | 생존 사냥꾼 334, 제작 사슬 머리 item **244579** 선택해 가슴 티어 복원; **4pc 유지**, G2849+J92+F165/O0→B=T3106; 관측 절대 CHMV **736/735/735/900**, DPS **173604.78**, SEM **310.81**. 환경3+변경 슬롯 정적4+DPS6 **총 Native13**; 캐시 6 hit/추가 Native0 | 실제 Windows [#43466966207](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43466966207), [원본 숫자·SHA](development/research_receipts/p1_v439_windows_70783_selected_four_tier_actual_native_compact.json), [실측 노트](development/notes/2026-11-14_p1-v439-b8-one-real-selected-70783-four-tier-native-e2e.md). **단일 실제 케이스, 26전문화/모든 선택지 완료 아님**. G는 같은 시즌 대표 근사 참조 + changed-slot delta, 전 부위 정밀 Native G 아님 |
| **v440 기존 6 JSON2 통계 재사용** | v439 input/JSON2/native receipt 각6 SHA 대조; 기존 `v065`·`v094`로 서로 다른 확인 seed 2개, DPS 차 **1091.06** > 95% 경계 **827.40**, 방향성 지지; 고유 관측 후보4, 기준 충족 근접 대안 **0** | 새 Native **0**. [CI #43534722801](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43534722801) SUCCESS, [파생 원본 근거](development/research_receipts/p1_v440_v439_existing_six_json2_95_material_compact.json). 0은 관측 범위 한정, 전역 최적/대안 부존재 증거 아님 |
| **v441 78수락조건 개정** | 전 78개 제품 필수성 심사·54조건 완화·24유지, 검증 묶음/증거 공유, 실제 시즌 원본 필요한 것과 시즌 독립 RUN 분리. 기존 v401 검사기와 테스트 최소 개정 | [커밋 ee6fe416](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/ee6fe41675938b34cee98da1238fa4558a3a32a3), [v401 #43537849668](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43537849668) **34PASS/0FAIL**; 새 Native/API/DB2 0; **완료 7/78 불변** |

- [범용 오프라인 CI #43537849818](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43537849818) **FAIL**, 개발 기록 ledger의 **역사적 198 `DEV_LEDGER_FAIL`**; v441 새 오류 없음. 이 실패는 실 SimC Native 실패가 **아니지만**, 전체 CI가 성공했다는 뜻도 아니다. 불필요한 과거 파일 전수 수정으로 현재 제품 개발을 지연시키지 않는다.
- 일반 제품 통합 경로의 **실제 선택된 1케이스 정상 동작**은 증거가 있으나 **제품 전체 26 DPS·모든 소모품/특수옵션·새 시즌 무이력 최종 E2E 완료는 아님**. 초기에 사용자가 보고한 원본 v016 바이트와 현재 격리 연구 제품의 직접 병합 완료도 미확인이다.
- **재현된 결함**: v430 구 70575 원본 혼용과 선택 G/L 미연결(v431~v437 교정), v438 선택 manifest의 웹 시작·재개 환경 검증 누락(교정), v435 raw SHA보다 느슨했던 출처 확인(강화). **현재 잔여 설계 효율 위험**: v106 선택 세션 키가 static-cache 파일 전체 SHA를 사용하므로 무관한 변형 추가만으로 새 세션을 만들 수 있음. 캐시 안전성은 유지하되 관련 변형-only identity로 줄일 필요성은 추후 실제 빈도·위험을 평가한 다음 결정한다. 지금 신규 출시 Gate가 아니다.

## 4. 코드·기능·재사용 진입점

새 채팅은 [FILE_MAP](development/FILE_MAP.md)과 [INDEX](development/INDEX.md)를 먼저 이용한다. 필요한 함수만 열고 과거 코드/원본을 재작성하지 않는다.

1. 시즌 자동 원본/환경: `runner/v191_...` 계열 원본 구성, `v216_environment_build_coordinator`·`v217` 설치 검증, `v222` 시즌 G/J/F/O 및 `v212` 설치 manifest. 정확한 파일명·함수는 FILE_MAP에서 확인. v1.4.3 최신 사용자 승인 아래 새 시즌 G/J/F/O 전체 구축이 필수; **이미 검증한 동일 시즌 캐시 재활용**, 신규 시즌 G/J/F/O를 과거 고정값으로 복사 금지.
2. 대표 장비/선택 충돌: `runner/v101_common_representative_equipment.py`, `runner/v432_selected_4pc_budget_bridge.py`, `runner/v098_target_user_scenario_bootstrap.py`, `runner/v046_static_item_cache.py`, 기존 `v414/v415` 정확 특수 L/설치 SHA.
3. 내부 SimC 진입·검증: `runner/v096_unified_product_entry.py` → `v091/v090/v062/v065` 정적 예산·기름·제약 → `runner/v094_durable_inclusive_adaptive_runner.py`, `v093`; 최적화·통계 `v290/v291`, 캐시·재개 `v106/v292/v293` (현재 실제 함수 호출은 코드 검증).
4. 사용자 웹/Windows: `runner/v113_local_web_api.py`, `runner/v106_user_session_controller.py`, Windows 패키지 `integration_probes/v181_windows_beta_packager.py`, [패키지 파일 registry](development/APP_PACKAGE_FILE_REGISTRY_20261113.md). 성공한 CI/베타 패키지를 최종 Windows 배포 검증 완료로 오인 금지.
5. 통계 원 정책/증거: `runner/v065_v015_scheduler_adapter.py::fresh_confirmation_judgment`, `runner/v094_durable_inclusive_adaptive_runner.py::_candidate_summary`; `runner/v440_b8_existing_native_statistics_audit.py`(read-only). 기존 v439 ZIP을 다시 Native 실행하지 않는다.
6. 상태/검사/증거: `development/78_ELEMENT_COMPLETION_CONTRACTS.json`(유일 상태 정본), `development/POLICY_78_ELEMENT_COMPLETION_GATE_V401.md`, `development/78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md`, `integration_probes/v401_completion_contract_gate.py`, `tests/test_v401_completion_contract_gate.py`, [EVIDENCE_INDEX](development/EVIDENCE_INDEX.md), [PROTOCOL](development/PROTOCOL.md), [DECISIONS](development/DECISIONS.md).

## 5. 다음 작업: REUSE → CONNECT → 필요할 때만 EXTEND / STOP

**최우선은 새 Gate 개발이 아니라 v441의 완화된 78요소 정본에 기존 증거를 실제 귀속하여 제품 완료도를 정확히 진전시키는 것.** B8만 무기한 붙잡지 않는다.

1. **REUSE**: 실제 최신 HEAD/78 JSON/자동 상태표와 v441 수락조건을 읽는다. [v439](development/research_receipts/p1_v439_windows_70783_selected_four_tier_actual_native_compact.json) + [v440](development/research_receipts/p1_v440_v439_existing_six_json2_95_material_compact.json) + v417, v431~v438 Actions·회귀를 첫 증거 묶음으로 선택. 이미 PASS 증거를 반복 실행하지 않는다.
2. **CONNECT**: 첫 증거 공유 묶음 `B8/D4/D6/E1/E2/E7/E9/F7/G4/G5/H1/H3/H4/H6`의 **각 요소·각 축**에 대해 수락조건→증거 SHA/실행 링크→실제 소비/오류 반례를 1:1 점검한다. 이미 충분하면 기존 `supports`와 원장의 generic/current_source/product 상태를 공동 갱신할 수 있지만 **자동 PASS 금지**. 특정 물리 옵션을 쓰지 않은 기존 영수증은 해당 옵션을 미입증으로 둔다. v441 묶음 계획(시즌 소스, 장비 충돌, CHMV, RUN, 선택 옵션)을 순차/병렬 적용한다.
3. **EXTEND 최소**: 근거로 부족한 부분만 정상·부정 회귀 1~소수 건. B8의 다른 티어 점유/두 티어 슬롯 불가능/촉매 중복, 고정 L(특수)과 제작 자유의 구분, 캐시 키·수동 T/O/E, 결과·취소 재개 중 실제 누락된 경계만 검증. **코드를 읽고 기존 테스트가 이미 갖춘 반례면 재검증만**. 기능이 없다는 추정으로 새 엔진/전체 Native를 시작하지 않는다.
4. **승격은 원래 계약대로**: JSON의 해당 축만 검증된 `PASS` 또는 실제 적용 불필요한 경우 엄격히 근거된 `NOT_APPLICABLE`로 변경; 원본 SHA·Actions·기존 Native·`supports` 포함. `v401 --write/--check`와 focused test/Actions 결과를 확인. `full_product_e2e`를 7/78 상태에서 임의 PASS하지 않는다. v441 정책 완화 자체를 54개 PASS로 간주하지 않는다.
5. **효율**: 관련 item static cache는 동일 시즌 SimC revision 바뀌어도 폐기하지 않는다; DPS cache는 실제 binary SHA·profile/item options/기름/전투/iterations 분리. 동일 날짜·같은 input의 26전문화/전 ilvl Native 재실행 금지. 필요하면 첫 실패 경계의 최소 변경된 슬롯만 Native 측정. 전체 UI·배포 성공 주장 대신 실제 제품 소비 경계 확인.

**단기 로드맵**: (i) v441 78계약-기존 증거 다중 귀속 후보 매트릭스, (ii) B8+연계 D/E/F/G/H의 충분/불충분 판정 및 최소 반례, (iii) 시즌 자동 G/J/F/O·최고 품질 등록·사용자 대표 프로필을 각각의 계약과 함께 공통 검증, (iv) Windows 사용자 캐시/취소 재개·실제 결과의 95%·근접 대안과 결함 경계 확인. **장기**: 총 78요소 유효 COMPLETE+별도 무이력(과거 시즌 값 격리, 정상 외부 수집 허용) 현 시즌 ZERO-SOURCE→USER-E2E 영수증, 26 DPS 실제 지원 범위를 제품 계약으로 완성. 새 시즌 공개 전에도 현시점 범용 엔진은 현 시즌으로 확인 가능하며 아직 존재하지 않는 미래 시즌의 수치를 지금 인증하지 않는다.

## 6. 소유권·정본·인계 실행 제한

- 확인된 실제 격리 작업 브랜치 **`probe/chat-cache-v035-20261024`**. 기준 브랜치 `main`은 별도이며 **병합/변경하지 않는다**. 원본 `v003` immutable, 미확인 원본 `v016`, Project Sources/Instructions UI, Work OS M0/Shared State 공식 승격, WEQUIP 영구 의존성 등은 기존 권한 밖. 현재 주 제품 개발 채팅의 소유권을 새 채팅이 임의로 대체하지 않는다. 본 인계는 사용자가 지시한 개발 연속성 복원용.
- 새 채팅은 실제 HEAD/기계 판독 78 JSON/Actions/Native artifact를 **독립 읽기 전용 검증**한다. 최초 응답에서 구현·역사 증거·미검증을 나눠 보고하고 **STOP**. 별도 사용자 **‘진행’** 전 코드/문서 변경·커밋·GitHub Actions 실행·외부 API/DB2/Native 수집·고비용 검사·공식 승격 금지.
- 읽는 순서: 본 단일 인계 → [START_HERE](development/START_HERE.md) / [INDEX](development/INDEX.md) / [FILE_MAP](development/FILE_MAP.md) → [v1.4.3 승인 정책](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) → [v441 78개 전수 판단](development/78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md) → [78 JSON](development/78_ELEMENT_COMPLETION_CONTRACTS.json) → [v401 정책](development/POLICY_78_ELEMENT_COMPLETION_GATE_V401.md) 및 생성표/상세 추적표 → [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) 첫 최신 부분 → [v439/v440 영수증](development/research_receipts/p1_v439_windows_70783_selected_four_tier_actual_native_compact.json), [v440](development/research_receipts/p1_v440_v439_existing_six_json2_95_material_compact.json) → 관련 함수/Actions 일부. 전체 역사 재감사하지 않는다.

## 7. 새 채팅 첫 메시지 복원 프롬프트 (첫 응답 읽기 전용)

~~~text
# SIMC SECONDARY OPTIMIZER — 2026-11-14 v441/78요소 최종 인계 독립 복원

저장소: degong2-code/simc-secondary-optimizer-runner (private)
격리 개발 브랜치: probe/chat-cache-v035-20261024
이번 인계 원본 개발 HEAD: ee6fe41675938b34cee98da1238fa4558a3a32a3
기준 main HEAD: 07133e0aaf738d6e4816a6486057b1cd49c018de
최신 단일 인계 정본: docs/CHAT_CONTINUITY_HANDOFF_20261114_P1_V441_78_REVIEW_PRODUCT_CONTINUITY.md
주의: 위 SHA는 인계 문서 작성 전 기준이다. 먼저 GitHub 실제 HEAD를 독립 확인하고 최신 JSON/Actions를 우선한다.

반드시 인계 정본 → docs/development/START_HERE.md·INDEX.md·FILE_MAP.md → 최신 승인 v1.4.3 → v441의 78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md → 78_ELEMENT_COMPLETION_CONTRACTS.json → POLICY_78_ELEMENT_COMPLETION_GATE_V401.md → 생성/상세 상태표 → CURRENT 최신 부분 → v439/v440 실제 영수증을 순서대로 필요한 범위만 읽어라.

최종 목표는 26 DPS의 목표 ilvl334 또는 수동 최종 T에서 SimC DPS 최대화로 치명/가속/특화/유연의 미래 목표 절대 rating 탐색이다. 시즌별 대표 장비/티어/무기·G/J/F/O 자동 구성, B=G+J+F, T=B+O, L/E/O 정적 고정치 중복 방지, SimC 담당 효과/APL/실 DPS, 관측 DPS·SEM·95% 판정·실질 근접 대안·캐시/취소/재개/Windows UI를 보존한다. 증강/탱/힐·장비 추천/전 시즌 DB/자체 효과 엔진은 범위 밖이다.

가장 최근 사용자 결정의 핵심은 78요소 자체를 제품 완성·결함 조기 검출을 위한 지도와 수락 계약으로 삼는 것, 엄격한 수락 조건 자체의 제품 필수성 재심사, 과잉 Gate 적극 완화, 관련 요소 공통 증거 재사용이다. 이는 이미 v441에서 78/78 조건 재검토·54개 완화·24개 유지로 반영됐다. 검증 완화=자동 PASS가 아니다. 각 요소의 실제 사용 조건·증거·실패 경계는 보존한다. 시즌 독립 RUN은 무의미한 새 시즌 인증/전수 Native를 요구하지 않는다.

인계 전 78 JSON: generic18/current_source18/product7/historical12 PASS, COMPLETE7/78(A8,A9,A10,A11,B2,B3,B7), next B8, B8 세 필수 축 PENDING/historical PASS, full_product_e2e=PENDING. 가장 최근 v439은 70783 생존 사냥꾼 제작 머리244579→가슴 티어 교체4pc 실제 Windows Native13(환경3+정적4+DPS6), 캐시6히트/추가 Native0, G2849+J92+F165/O0/T3106, 관측 DPS173604.78 SEM310.81 실증. v440은 같은 실측 6 JSON2의 독립 확인 seed 및 95% 차1091.06>경계827.40, 관측 근접 대안0/고유4 재검증; 신규 Native0. v441 78 정책 회귀 34 PASS, 범용 ledger CI는 역사 오류198건으로 FAIL. 실제 코드와 영수증의 신분을 구별해라. v439 하나로 모든 26전문화·모든 옵션·전체 제품 완료를 주장하지 마라.

다음 개발 시작점은 v439/v440와 기존 v417/v431~v438 근거를 B8/D4/D6/E1/E2/E7/E9/F7/G4/G5/H1/H3/H4/H6 등 관련 요소의 각 검증 축에 함께 귀속 가능한지 심사하는 작업이다. 누락된 반례만 최소 회귀, 실제 빠진 exact 변형만 최소 Native. 기존 캐시·SimC 엔진·v101/432/098/096/106/113 경로를 재사용하고 새 Gate·26전문화 Native 전수·과거 원본 재감사·불필요한 문서 중복을 금지한다. 새 채팅에서 각 증거의 재사용 가능성, 정확히 남은 수락 조건, 효율, 현재 병목, 단기·장기 로드맵을 보고해라.

첫 응답은 GitHub/정책/JSON/실제 증거를 읽기 전용으로 독립 복원한 보고만 수행하고 STOP. 사용자가 별도로 '진행'이라고 말하기 전 코드·문서·테스트·Actions·Native/API/DB2·커밋/병합·공식 승격을 시작하지 마라. main·불변 v003·Project UI·Work OS/Shared State·원본 v016·주 제품 개발 채팅 권한을 그대로 보존하라.
~~~

**END — 새 채팅 첫 응답은 READ ONLY + STOP. 인계 문서만으로 요소 PASS/실 제품 전부 완료가 아니다.**
