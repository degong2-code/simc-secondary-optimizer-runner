# SIMC SECONDARY OPTIMIZER — 2026-11-14 v445 / 78요소 B10 인계 단일 정본

> **지위:** 기존 개발을 새 채팅에서 정확히 이어가기 위한 최신 인계 정본. 과거 [v441 인계](CHAT_CONTINUITY_HANDOFF_20261114_P1_V441_78_REVIEW_PRODUCT_CONTINUITY.md)는 당시 7/78의 역사 스냅샷이다. 최신 요소 상태의 **유일한 기계 판독 정본**은 [78_ELEMENT_COMPLETION_CONTRACTS.json](development/78_ELEMENT_COMPLETION_CONTRACTS.json)이며, 인계 문서 자체가 제품 구현·실측·PASS·Project UI 등록을 변경하지 않는다.
>
> **인계 작성 직전 GitHub 독립 확인(2026-11-14):** 비공개 저장소 `degong2-code/simc-secondary-optimizer-runner`, 격리 브랜치 `probe/chat-cache-v035-20261024`의 작업 원본 HEAD `28b6b435a67b594852691792725e4c1f87e50a21`(v445), `main` HEAD `07133e0aaf738d6e4816a6486057b1cd49c018de`. **인계 커밋으로 브랜치 HEAD가 바뀌므로 새 채팅은 실제 최신 HEAD를 다시 조회**한다. 인계 준비용 문서 변경 외 코드·Native·API·DB2·계약 상태 변경은 없다.

## 1. 제품 목표와 최신 정책

- 지원 대상은 **26개 DPS 전문화**이며 **증강 기원사·탱커·힐러는 제외**한다. 미래 파밍 목표인 ilvl 기본 334 또는 사용자가 직접 지정하는 최종 CHMV 총량에서 SimC DPS를 최대화하는 **치명·가속·특화·유연의 절대 rating**을 찾는다. 비율·DPS·SEM·95% 판정·관측 1순위·실질적으로 다른 근접 대안을 표시하되 전역 최적해를 증명했다고 주장하지 않는다. 현재 착용 장비 재분배·아이템 조합/획득 추천·시즌 전체 아이템 DB·자체 APL/효과 엔진은 범위 밖이다.
- 일반 사용자는 직업·전문화·종족·특성, 목표 ilvl/수동 최종 T, 장신구 2개, 선택 특수장비·장식 최대 2개, 보석/영약/음식/소모품/기름·전투 조건을 선택한다. 내부 엔진이 대표 일반 장비·무기·4pc 티어·주능력치·SimC 프로필을 구성한다. 업로드 SimC 프로필은 선택적인 캐릭터 정보/특성 읽기 입력이며 현재 장비·스탯을 목표 예산으로 복제하지 않는다.
- 공식 예산은 `G`=같은 시즌·ilvl의 대표 일반 장비·무기 CHMV, `J`=검증된 기본 보석, `F`=검증된 최고 품질 영약, `O`=선택 기름의 고정 CHMV, `B=G+J+F`, `T=B+O`, `c_final=c_base+o`. 사용자가 수동 **최종 T**를 정하면 자동 총량보다 우선하고 `B=T-O`로 변환한다. 고유 특수장비의 exact L은 G 안에 한 번만 포함·하한 보호; 제작 초기 50:50은 잠그지 않는다. 정적 E/O 중복 계상 금지; 장신구 고정치는 자유 G 밖이며 미출력 정적 gear 수치를 0 실측이라 단정하지 않는다. G 근사 참조값과 전부위 exact Native G를 구분한다.
- **새 시즌마다 G/J/F/O 전체를 해당 시즌 실제 원본으로 자동 구축·검증**하여 B/T를 갱신한다. 예전 시즌의 79×2 예산표, F/J/O 수치를 새 시즌 검증값으로 복사하지 않는다. 같은 시즌·동일 조건의 봉인된 원본/정적 캐시를 재사용한다. 최고 품질 선택지는 실제 동일 효과·조건·범위·비열등성이 입증될 때만 일반 사용자에 노출; 정책 A의 검증 완료 항목 자동 등록. 영구 마부 대상, 일반 임시 마부 제외, 무기 기름은 별도 지원. Omnium 같은 시즌 특수 콘텐츠는 선택형 모듈로 분리.
- SimC가 APL·아이템/장식 효과·proc·DPS를 책임진다. 우리 프로그램은 정확한 ID/ilvl/슬롯/옵션, 소켓·고정치·예산, 최종 JSON2 정적 rating, 후보 탐색, 95% 통계, 캐시/취소/재개·사용자 출력의 책임을 맡는다. 새로운 효과 인증 Gate·불필요한 Native 전수·SEM 미세 정밀화·새 최적화 엔진은 만들지 않는다.
- **정책 우선순위:** 최신 사용자 직접 결정 > 승인된 [v1.4.3 시즌 G/J/F/O 정책](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) 및 비충돌 v1.4 계열 > 실제 코드/CURRENT/Actions/Native 증거 > 과거 인계·역사 문서. 승인 정책과 실제 구현·사용자 UI 반영·공식 승격은 구분한다.

## 2. 78요소 검증의 목적·완화 정책(v441)과 최신 수락 상태(v445)

- 78개 요소는 **제품 기능 전체를 관리하고 오류를 조기에 발견하기 위한 지도**이지 수락 조건 자체가 개발 목적은 아니다. [v441 전수 필수성 감사](development/78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md)에서 **78/78개 검토, 54개 과잉 조건 완화/명료화, 24개 필수 조건 유지**를 이미 반영했다. 다시 개발하거나 과잉 Gate를 생성하지 않는다.
- [v401 정책](development/POLICY_78_ELEMENT_COMPLETION_GATE_V401.md): 각 요소는 `generic` / `current_source` / `product_integration` / `historical` 네 축으로 분리된다. 세 필수축의 증빙된 PASS(또는 엄격히 증빙된 N/A)가 `COMPLETE`이며 역사 PASS만으로 완료가 아니다. 동일한 정상·실패 회귀/원본 SHA/Native/Actions가 여러 요소의 **실제 수락 조건**을 지지하면 `evidence.supports`로 공유하지만 미관측 선택 옵션·다른 시즌·다른 전문화를 자동 PASS하지 않는다. 시즌 독립 RUN 통계·산술을 매 시즌 따로 Native 인증하지 않는다.
- **2026-11-14 실제 v445 JSON:** `generic 27/78 PASS`, `current_source 27/78 PASS`, `product_integration 15/78 PASS`, `historical 13/78 PASS`, **공식 COMPLETE 15/78**: `A8 A9 A10 A11 B2 B3 B7 B8 D4 D6 E1 H1 H3 H4 H6`. `policy.next_review=B10`, `policy.full_product_e2e=PENDING`. 이 수치는 모든 코드 구현률이 아니라 해당 증거·수락 범위의 공식 요소 완료 건수다.
- **B9 촉매:** `generic=PASS`, `current_source=PASS`(기존 **12.1.5.70575** 동일 시즌 카탈로그·회귀에 한정), `product_integration=PENDING`, `historical=PENDING`. 정확한 선택 촉매 정적 L 부재 시 실행 차단을 유지한다. **B10 대표 소켓:** `historical=PASS`(과거 Native의 SimC 파서 대비만), `generic/current_source/product_integration=PENDING`. 다음 검토 **B10 유지**.
- 유효한 전체 제품 COMPLETE는 78개의 실제 유효한 COMPLETE뿐 아니라 **단일 실제 신규 설치 ZERO-SOURCE→Environment Build→사용자 설정→SimC→결과의 독립 E2E 영수증**도 필요하다. 새 설치에서 **기존 과거 시즌 입력/답안은 격리하되 정상 제품의 Wago DB2/Blizzard/WCL/공개 GitHub/SimC 외부 수집은 허용**한다. 전체 E2E가 아직 미확정이라는 이유로 이미 승인된 일반 제품 개발을 정지시키지 않는다.

**공식 파일:** [JSON 상태](development/78_ELEMENT_COMPLETION_CONTRACTS.json) → [자동 생성 상태표](development/78_ELEMENT_STATUS_GENERATED.md)(직접 수동 편집 금지) → [상세 추적표](development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md) → [v401 검사기](../integration_probes/v401_completion_contract_gate.py)/[정책 테스트](../tests/test_v401_completion_contract_gate.py). [START_HERE](development/START_HERE.md)·[INDEX](development/INDEX.md)·[FILE_MAP](development/FILE_MAP.md) 및 [CURRENT 최신 부분](CURRENT_PRODUCT_DEVELOPMENT_STATE.md)에서 탐색.

## 3. v439~v445 최근 개발·영수증: 새로운 PASS와 실제 영수증 범위를 혼동하지 말 것

| 단계 | 실제 확인한 범위 | 실증/제한 |
|---|---|---|
| **v417** | 생존 사냥꾼 70783, 기본 4pc의 제품 Native | [실제 #43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756); 사용자 선택 제작 머리 충돌 증거는 아님 |
| **v439** | 실제 70783 생존 사냥꾼 ilvl334, 선택 제작 머리 item **244579**, 옵션 `crafted_stats=32/36`와 `arcanoweave_lining`, 머리 대신 가슴·어깨·손·다리 티어 4pc; **G2849+J92+F165+O0→B=T3106**, 관측 절대 rating 736/735/735/900, DPS173604.78, SEM310.81. 환경 Native3+변경 슬롯 정적4+DPS6=13, 이후 캐시6 hit/추가 Native0 | [Windows Native #43466966207](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43466966207), [봉인 수치](development/research_receipts/p1_v439_windows_70783_selected_four_tier_actual_native_compact.json). **G는 같은 시즌 근사 참조+exact 변경 슬롯 delta**, 전부위 exact Native G 아님. 이 1개 선택 시나리오는 전 전문화·모든 옵션의 통합 인증 아님 |
| **v440** | v439의 기존 6개 실제 input/JSON2/receipt SHA 검증 후 95%·material 재판정. 두 독립 확인 후보 DPS 차 **1091.06** > 95% 경계 **827.40**, 고유 관측 후보4·실질적 근접 대안 관측0, 신규 Native0 | [#43534722801 SUCCESS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43534722801), [파생 숫자](development/research_receipts/p1_v440_v439_existing_six_json2_95_material_compact.json). **일부 후보 사이 방향성**만 지지, 전역 최적해 증명/대안 비존재 증명 아님 |
| **v441** | 78/78 수락 필수성 감사, 54개 완화·24개 유지; 당시 상태 7/78 불변 | [정책 감사](development/78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md), [v401 #43537849668](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43537849668) SUCCESS |
| **v442** | v439 실측 + v187/v432 충돌·불가능 회귀를 B8/D4/D6/E1의 세 필수축에 공유 귀속: COMPLETE **7→11**. 기존 v401 하드코딩 상태 테스트와 노트 8필드 ledger 신규 오류 교정 | [증거 노트](development/notes/2026-11-14_p1-v442-existing-proof-shared-attribution-b8-d4-d6-e1.md), v401 [#43540628754](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43540628754) SUCCESS |
| **v443** | 기존 v094/v095/v113 회귀+v439/v440 실제 6 JSON2·95%·웹 결과를 H1/H3/H4/H6에 재귀속: COMPLETE **11→15**. B9는 후속 검토로 유지 | [증거 노트](development/notes/2026-11-14_p1-v443-real-native-95-material-user-result-reuse.md), v401 [#43542102773](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43542102773) SUCCESS |
| **v444 B9** | `runner/v101_common_representative_equipment.py` 촉매 변환 원본이 동일 시즌 카탈로그 item ID·부위·방어구 타입/클래스 마스크·주능력치·중복 슬롯 조건을 만족하는지 검증 강화, `tests/test_v187_current_season_tier_overlay.py` 26 DPS 포함 오프라인 회귀·v098 선택 입력·exact L 미확정 차단 | [v187 #43550242720 SUCCESS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43550242720)(109+36+7 PASS), [v182 양 OS #43550242725 SUCCESS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43550242725). [v444 기록](development/notes/2026-11-14_p1-v444-b9-current-catalyst-source-bounded-review.md). **70575 실원본의 입력·회귀 증거**이지 **70783 촉매 사용자 선택 Native/정확 L·DPS 제품 E2E 증거 아님**; product PENDING |
| **v445 B10** | 기존 v270 **Native 4/4 성공**으로 SimC가 `gem_id`를 소켓 없이도 적용할 수 있음을 관측. SimC 보석 적용 성공만으로 인게임 물리 소켓 또는 사용자 추가 소켓 적법성을 증명할 수 없다는 **부정 범위** 확정, B10 historical만 PASS | [v270 #41601140696 SUCCESS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41601140696), [v445 감사](development/notes/2026-11-14_p1-v445-b10-socket-native-negative-boundary-audit.md). 신규 Native0, B10 필수 3축 PENDING |

- **최신 v445 계약 CI:** [v401 #43552516887](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43552516887) **SUCCESS**, tested HEAD `28b6b435a67b594852691792725e4c1f87e50a21`. [Reusable Offline #43552516848](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43552516848)은 **기존 개발 ledger 누적 198건 오류**로 FAILURE(후속 테스트 중단). 이것은 이번 제품 Native 실패나 모든 focused 회귀 실패가 아니다. v444/v445 신규 노트 메타데이터 누락은 교정됐고 당시 ledger에서 신규 노트 오류 0. **인계 후 push CI는 해당 커밋에서 별도 확인해야 하며 성공을 선행 주장하지 않는다.**
- v444/v445에서 과거 촉매 실험(v040~v042)·보석 파서 Native(v270)를 **현재 실제 선택 제품 E2E**로 오판하지 않았다는 점이 핵심이다. 정확한 소켓/시즌/선택 장비 소유권이 없는 경우에만 그 축을 PENDING으로 둔다.

## 4. 실제 구현 구성요소·코드 탐색 최단 경로

1. 시즌 원본·자동 Build: `runner/v216_environment_build_coordinator.py`/`v217_stage_execution_engine.py` → `v222_season_budget_contract.py` → `v212_environment_manifest.py`. 시즌별 G/J/F/O 자동 구축·검증이 승인 정책이며 최종 fresh 설치 통합은 PENDING.
2. 장비·티어/촉매: `runner/v101_common_representative_equipment.py`(B9 입력 교정), `runner/v432_selected_4pc_budget_bridge.py`(선택 exact 슬롯 delta·G/L), `runner/v046_static_item_cache.py`(정적 캐시), `runner/v098_target_user_scenario_bootstrap.py`(사용자 프로필).
3. 소켓/보석(다음 B10): `runner/v232_simc_only_ordinary_representative.py`(intrinsic 소켓 수의 source-only 후보)와 `runner/v271_user_socket_gem_layout.py`(선택형 소켓/보석 배치; 실 소켓 허용 인증 아님), `runner/v216_environment_build_coordinator.py` 내 `additional_socket_proof_required_by_slot`·`J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING`, `v212/v098` 소비 경로. 실제 최신 함수·파일명은 FILE_MAP 또는 GitHub 코드 재조회로 검증한다.
4. 내부 SimC: `runner/v096_unified_product_entry.py` → 기존 `v094_durable_inclusive_adaptive_runner.py`/`v065` 통계, `v290/v291` 탐색, `v106_user_session_controller.py`·`v292/v293` 캐시/취소·재개. 사용자 웹 API/Windows 경로 `runner/v113_local_web_api.py`, 패키지 후보 `integration_probes/v181_windows_beta_packager.py`. Windows 최종 설치/실클릭·배포 인수는 별도 미완료.
5. 원본 v016_SCENARIO_CONTRACT는 사용자 보고상 제품 계보 기준이며 **원본 바이트·영수증 직접 통합 확인 미완료**. 이 때문에 기존 격리 개발/일반 제품 SimC 시험을 중단하지 않는다. 옛 v097 등 역사 기록을 현재 구현 스냅샷으로 덮어쓰지 않는다.

## 5. 다음 검토 B10 — 정확한 시작점·미완료 조건

**현재 계약:** `B10 = 부위별 기본 소켓과 사용자별 변경/추가 소켓을 구분한다`. 역사 v270 실 Native는 `SimC가 gem을 소비했다`는 증거일 뿐 **게임상 실제 소켓 허용·사용자 추가 슬롯·J 예산·정확한 최종 프로필 소비**의 증거가 아니다.

1. `REUSE` — [v445 노트](development/notes/2026-11-14_p1-v445-b10-socket-native-negative-boundary-audit.md) → [P3-BX v270 영수증](development/notes/2026-11-03_p3-bx-simc-socket-native-contrast.md) → 기존 `v232` intrinsic 기본 소켓 봉인 및 `v271` 사용자 선언/추가 소켓/`v216` fail-closed → [v417 실 E2E](development/notes/2026-11-13_p1-v417-bounded-post-bridge-product-e2e-once.md)를 **각 범위만** 읽는다.
2. `CONNECT` — 실제 사용 대표 장비의 같은 시즌/빌드 ID·슬롯별 **기본 소켓/추가 가능 부위·조건·사용자 선언 소켓** 근거를 분리한다. 기본 소켓이 아이템 원본에 존재하는지, 추가 소켓이 인게임 허용 규칙에 부합하는지, 선택 보석 ID/색상·소켓 수→**J = 실제 적용 가능한 일반 보석 수 × 검증 rating**으로 연결되는지 확인한다.
3. `VERIFY` — 검증된 소켓 구성이 `v216→v212→v098 사용자 프로필→SimC`에 실제 반영되는지 확인. v232와 v271을 합산하면서 중복하거나 원본 출처 누락을 무시하지 않는지, 과다/잘못된 슬롯·변경·빌드·고정 J 불가능 조건의 기존 **정상·실패 회귀**를 먼저 찾는다. 실제 UI 미선택 추가 소켓의 전수 인증은 필수 Gate가 아님.
4. `MINIMAL EXTEND` — 기존 정확한 원본·캐시·오프라인 회귀로 충분하지 않은 **정확 한 부위/옵션의 소켓 증거만** 보완. Native에서 gem 효과가 보였다는 이유로 인게임 물리 소켓 승격 금지. 미확정 항목은 해당 축만 PENDING. 시즌 전체 장비 DB·보석 proc 인증·26 DPS Native 전수·새 소켓 엔진 금지.
5. `ACCEPT` — 증거 범위가 필수 수락 조건을 충족할 때만 JSON의 개별 축에 원본 SHA·Actions·supports를 귀속하고 생성표/상세 추적표를 동기화. 새 채팅 **최초 응답은 이 검증/변경을 시작하지 않고 읽기 전용 보고 후 STOP**.

**B9 후속 보류:** 사용자 선택 촉매의 70783 해당 옵션 exact 정적 L·사용자 프로필·G/B/T·DPS 실제 소비 미관측. 선택하지 않은 촉매 때문에 기본 환경 전체를 차단하거나 v040~v042 진단을 인증으로 승격하지 않는다.

**같이 묶어 볼 후속 범위:** B11/B12 G, C2 J, E2 기름 O의 `T=B+O`/중복, E7 분배가능성, E9 정적 JSON2·buffed 분리, F7 실제 장신구·소켓·소모품·특수장비 사용자 프로필, G4 시즌 정적 캐시, G5 DPS/environment identity. 근거가 충분한 것은 묶어 귀속하고 무관한 신규 Gate·Native 반복 금지.

## 6. 현 병목·품질 경계·로드맵

- **현재 병목:** B10의 *같은 시즌 실제 소켓/추가 허용 규칙 원본→J 예산→사용자 프로필* 근거가 아직 연결되지 않았다. 이전의 물리 소켓 없는 SimC 보석 적용 결과는 **오히려 추가 인증 필요성을 보여 주는 음성 증거**다. B9는 선택 촉매 정확 L 제품 실행이 별도 PENDING.
- **구현≠검증≠공식 수락.** 코드가 있어도 선택되지 않은 옵션/실 원본 소유권은 미관측일 수 있고, 반대로 증거 미첨부를 미구현으로 단정하지 않는다. 같은 시즌 정적 캐시는 SimC revision만으로 폐기하지 않고 사용자 요청의 정확 교정만 허용. DPS 캐시는 실제 SimC 바이너리·프로필·소스·장비/옵션·후보·O·전투·iterations identity를 분리한다. 모든 변경에서 CPU·메모리·I/O·Native 호출·중복·캐시/시간을 확인한다.
- **단기:** (i) B10 소켓 원본·개인 변경·J·사용자 프로필의 기존 증거 충분/부족 판단, (ii) B9 정확 L 사용 조건 및 B11/C2/E2/E7/E9/F7/G4/G5 공통 증거 재귀속, (iii) 누락된 실제 사용자 선택의 최소 검증, (iv) v401 수락 계약·자동 상태표/실제 에러 경계 일치 및 CI 확인. B10 고립 검사로 P1 완성을 늦추지 않는다.
- **중기:** 시즌 자동 G/J/F/O→B/T·정책 A/최고 품질 선택지→대표 사용자 프로필→기존 적응형 SimC→95%·대안·세션·캐시·취소/재개·Windows 사용자 UI까지 **실제 제품 경로**의 결함과 미완료 연결을 해소.
- **장기:** 78개 요소 각각의 유효 수락 완료와 **별도 신규 설치 ZERO-SOURCE→USER-E2E** 완료 영수증; 26 DPS 지원·범위 내 대표 전투/무기·정확 사용자 선택·시즌 갱신 검증. 기존 역사 영수증을 폐기하거나 동일 시즌·전 전문화 Native 전수 반복하지 않으며 최종 제품이 아닌 베타/부분 PASS는 그대로 구분한다.

## 7. 인계·개발 권한과 새 채팅의 실행 제한

- 기존 주 제품 개발 채팅이 일반 구현·실제 SimC 시험을 소유한다. **사용자가 요청한 채팅 분기는 연속성 확보이지 MAIN/WORK 또는 다른 주체의 무단 개발 주도권 이전이 아니다.**
- 격리 브랜치 작업만 허용하며 `main` 병합, `v003` immutable, 원본 `v016` 변경, Project Sources/Instructions UI 직접 적용, Work OS M0/Shared State 공식 승격, WEQUIP의 영구 runtime 의존성은 승인 없이 금지.
- 새 채팅은 실제 GitHub 최신 HEAD를 다시 확인하고 이 단일 인계 → [START_HERE](development/START_HERE.md)·[INDEX](development/INDEX.md)·[FILE_MAP](development/FILE_MAP.md) → [v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) → [v441 감사](development/78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md) → [JSON](development/78_ELEMENT_COMPLETION_CONTRACTS.json)/[v401 정책](development/POLICY_78_ELEMENT_COMPLETION_GATE_V401.md)/생성 상태표·상세 추적표 → [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) 최신 부분 → [v444/B9](development/notes/2026-11-14_p1-v444-b9-current-catalyst-source-bounded-review.md)·[v445/B10](development/notes/2026-11-14_p1-v445-b10-socket-native-negative-boundary-audit.md)·필요한 실제 Actions/코드를 순서대로 읽는다. 역사 전체 전수 조사·새 Native는 복원에 불필요.
- **첫 응답은 읽기 전용 복원 보고만 수행하고 STOP.** 사용자가 별도로 **“진행”**이라고 승인하기 전에는 코드·문서·JSON 상태 변경, 테스트/Actions 실행, Native/API/DB2 수집, 커밋/병합, 공식 승격을 수행하지 않는다.

## 8. 새 채팅 시작 프롬프트(인계 커밋 SHA는 새 채팅이 실제 조회)

~~~text
# SIMC SECONDARY OPTIMIZER — v445 / 78요소 B10 읽기 전용 독립 복원

저장소: degong2-code/simc-secondary-optimizer-runner
격리 개발 브랜치: probe/chat-cache-v035-20261024
인계 작성 전 개발 HEAD: 28b6b435a67b594852691792725e4c1f87e50a21
main HEAD: 07133e0aaf738d6e4816a6486057b1cd49c018de
최신 단일 인계 정본: docs/CHAT_CONTINUITY_HANDOFF_20261114_P1_V445_78ELEMENT_B10_SOCKET_READONLY_RESTORE.md
주의: 인계 커밋으로 브랜치 HEAD가 변경되므로 반드시 실제 GitHub 최신 HEAD를 먼저 다시 확인한다.

읽는 순서: 본 단일 인계 → docs/development/START_HERE.md·INDEX.md·FILE_MAP.md → 승인 v1.4.3 → v441 78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md → 78_ELEMENT_COMPLETION_CONTRACTS.json + POLICY_78_ELEMENT_COMPLETION_GATE_V401.md → 자동/상세 상태표 → CURRENT 최신 부분 → v444/B9·v445/B10 증거 및 v439/v440/v270 실제 영수증/관련 코드. 모든 역사를 전수 감사하지 않는다.

제품 목표는 26 DPS(증강/탱/힐 제외)의 목표 ilvl334 또는 수동 최종 T에서 SimC DPS 최대화 CHMV 절대 rating, 통계적 95% 판정·실질 대안·캐시·취소/재개·Windows 결과다. 시즌마다 대표 장비·무기·티어, G/J/F/O 전체를 검증된 원본으로 자동 구축하고 B=G+J+F, T=B+O, c_final=c_base+o를 유지한다. L/E/O 중복 금지, 제작 초기50:50 미잠금, SimC 담당 효과/APL/DPS. 장비 추천·시즌 전체 아이템 DB·자체 효과 Gate/새 엔진은 범위 밖.

v441에서 78개 요소 수락조건 자체의 제품 필수성 78/78를 전수 감사해 54개 완화·24개 유지가 이미 구현됐다. 78개는 실제 제품 완성/결함 발견을 위한 계약이며, 과잉 검증/Native 전수 금지. 기존 유효 CI/Native/SHA를 관련 요소에 공유 귀속하되 실제 소비·실패 경계와 generic/current_source/product_integration/historical 축을 분리한다.

인계 작성 전 v445 JSON: generic 27/current_source 27/product 15/historical 13, 공식 COMPLETE 15/78(A8 A9 A10 A11 B2 B3 B7 B8 D4 D6 E1 H1 H3 H4 H6), next B10, 전체 제품 E2E PENDING. v442·v443에서 이미 B8/D4/D6/E1/H1/H3/H4/H6을 기존 실제 Native/오프라인 증거로 재귀속했다. v444 B9는 현재 동일 시즌 입력·범용 PASS지만 정확 L 미실측 촉매 사용자 제품 통합 PENDING. v445 B10은 v270 Native4의 'gem 소비≠실제 소켓 적법성'을 역사 증거로만 PASS, 나머지 세 축 PENDING.

최신 v445 계약 CI #43552516887 SUCCESS, 전체 재사용 오프라인 #43552516848는 기존 개발 ledger 198건 오류로 중단; 신규 v444/v445 노트 오류는 없음. v439 70783 제작 머리244579·티어4pc 단일 Native13(환경3+정적4+DPS6), G2849+J92+F165/O0=B=T3106, DPS173604.78/SEM310.81, 캐시 6회 재사용. v440은 같은 JSON2의 95% 1091.06>827.40/근접 대안 관측0을 Native0으로 재판정. v444 26DPS 회귀·촉매 소스 원본 PASS, v445 v270 보석 파서 Native4는 물리 소켓 증명 아님. 모든 전문화·선택지·전역 최적해로 과장하지 않는다.

다음 개발 작업은 B10 대표 소켓: v232 intrinsic/기본 소켓과 v271 추가/사용자 선언 소켓의 실제 같은 시즌·부위/아이템 원본을 분리한 뒤 J 예산과 v216→v212→v098→SimC 사용자 프로필 실제 소비·실패 경계를 기존 증거로 대조한다. 부족한 특정 조건만 최소 증거/회귀. B9 정확 선택 촉매 L·E2/E7/E9/F7/G4/G5 및 G/J 환경 자동 Build는 공통 검증 묶음으로 관리. 기존 v046/v096/v098/v101/v106/v113·v417/v439/v440/v270와 캐시를 재사용, 새 Gate·효과 인증·26전문화 Native 전수는 금지한다.

이번 새 채팅의 **첫 응답은 읽기 전용 복원 보고만** 수행하라. 보고에는 실제 HEAD·제품 목적·78개 상태·v439~v445 최근 실증/수정·B9/B10 미완료 경계·증거 재사용·현재 병목·단기/장기 로드맵을 포함한다. **사용자가 별도로 '진행'이라고 승인하기 전에는 코드/문서/JSON 수정, 테스트/Actions/Native/API/DB2 실행, 커밋/병합/공식 승격을 하지 않고 STOP**. main·v003 immutable·v016 원본·Project UI·Work OS·주 제품 개발 권한을 보존하라.
~~~

**END — 이 인계는 개발/검증 자체가 아니라 최신 상태의 연속성 보존이다.**
