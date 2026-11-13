# v425 — B3 대표 일반 방어구: 기존 KR 70783 실 Native 입력·JSON2 개별 슬롯 대조

- **Capability:** `GEAR.SEASON`, `CHARACTER.PROFILE`, `ENVIRONMENT.WEB`.
- **Keywords:** B3, v167, v169, v232, v230, current gear, armor subclass, 15 equipment slots, ilvl334, item ID, JSON2, raw SHA, 26x5, WSE.
- **Prior evidence:** [v423 B1 제한 범위](2026-11-13_p1-v423-b1-26dps-contract-scoped-evidence.md), [v424 B2 목표 ilvl](2026-11-13_p1-v424-b2-target-ilvl-existing-native-scope.md), [v417 Windows 실 제품](2026-11-13_p1-v417-bounded-post-bridge-product-e2e-once.md), [v405 인증된 실제 후보](2026-11-13_p1-v405-a7-automated-current-source-selection-verified.md).
- **Decision:** `REUSE` — **B3 generic/current_source/product_integration PASS; historical PASS, 요소 COMPLETE**. 현재 한 전문화의 부위별 정확 물리 ID·클래스/타입 필터와 목표 ilvl의 실 SimC 소비를 범위 한정 입증. 시즌 전체 획득 가능성, 26 DPS 모든 장비의 현재 빌드 Native, exact G, 일반 장비 사용자 선택지 등록은 **별개이며 미승격**.
- **Changes:** 78 JSON/자동 생성표/78 상세 추적표, B3 회귀 단언, 개발상태·INDEX/START_HERE 및 본 근거 노트만 변경. **제품 실행 코드0, 새 gear DB0**.
- **Verification:** 현재 v417 실 Windows [#43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756), tested `89d4810baf5e05f1c5c6f355f39a5f35ca9ec4e7`, [원본 ZIP #14021859656](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756/artifacts/14021859656); 기존 v212 양 OS [#43388059919](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43388059919) 각 **487 tests/4 SKIP/0 FAIL**, [v405 current source #43375839959](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43375839959), [v180 다중 ilvl #40980268952](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40980268952).
- **Remaining:** B4 무기 형태/손 정확성, B5 성능 및 이후 B11/B12 G 예산 별도; A7/B1의 26개·시즌 개별 품목 제품 통합 PENDING, 전체 ZERO-SOURCE→USER-E2E PENDING.
- **Efficiency:** 오직 기존 artifact ZIP 1회 읽기와 Python ZIP/JSON 해시·기존 GitHub 원본 대조. 신규 게임 HTTP/DB2 수집0, Native0, SimC 컴파일0, 전체 시즌 DB 구축0, 캐시/원본 변조0.

## 1. 원본 데이터 검증·범용 규칙

`v167`는 `v163→v165/v166`에서 동일 시즌 원본을 소비해 내부 `plain_representative_candidate`의 item_id, inventory_type, ClassID/subclass, allowed_class_mask, 출처 영수증을 관리한다. 일반 장비를 사용자 전체 착용 장비 선택 메뉴로 승격하지 않고, 조건 미확정 후보는 내부로 한정한다. `v169.available_plain`은 일치하는 부위·방어구 계열(천/가죽/사슬/판금)·직업 마스크를 선택하고 중복 ID·동일 빌드 차이를 거부한다. `v232.find_candidate`는 같은 `v230` 단일 SimC 소스 패스에서 각 필요 슬롯을 구성하고, 선택 부위의 주능력치, tier 정확 ID/부위/비전투 소스 ilvl·품질, neck/finger 부족, 실 출처/미확정 WSE를 구분하며 `selected_G_source_candidate_not_approved=True`를 유지한다. 원본 소스 ilvl은 **목표 레벨 scaling 증명이 아니다**.

**GENERALIZATION_REGRESSION:** [#43388059919](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43388059919)의 Linux/Windows 각 487 PASS/4 SKIP에는 `test_v232_simc_only_ordinary_representative`의 필수 부위 누락·부위 타이핑/1 spec 13물리 슬롯·잘못된 주능력치·다른 목표 ilvl 단순 환산 방지·잘못된 tier 품질/ilvl·손상 source SHA 차단 및 `v167` 내부 일반 슬롯/미인증 후보 차단, `v254` 다른 확장팩/빌드 차단이 포함된다. [v405 원본 #43375839959](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43375839959)는 실제 KR `12.1.5.70783` WCL/DB2 item 원본434→현 시즌 source-selected 후보209→사용자 선택134(일반 장비는 공개 메뉴 제외)를 감사한다. **209개 후보를 대표 12개 부위의 독립 시즌 획득 완전 인증으로 오해하지 않는다**.

## 2. 현재 원본·제품 실 물리 장비 SHA 검증

**CURRENT_SOURCE_REAL / PRODUCT_INTEGRATION_REAL:** [v417 실 Windows #43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756), 현재 KR `12.1.5.70783`, pinned SimC revision `de11f57df75dda668bae6ac7043a43b98831fa96`, 목표 ilvl334, `v216/v212` 실 환경 설치→Survival Hunter SimC 실제 DPS12. 원본 [artifact #14021859656](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756/artifacts/14021859656)에서 `V343_NATIVE_INPUT_JSON2_RECEIPT.zip`를 **직접 재독**했고 inner ZIP SHA-256 `a9c29567577f178120eced8045edfaf5b64c61eb822ca128d0d3fbfd6abfc5be`가 audit summary `raw_evidence_sha256`와 일치함을 확인했다.
- **12/12 원시 `input.simc` SHA** = 각 `native_receipt.input_sha256`, **12/12 원시 SimC JSON2 SHA** = 각 `native_receipt.native_json_sha256` = summary의 순서별 SHA. 총 **12×15개** 장비 슬롯 모두 input `id=.../ilevel=334`와 JSON2 `sim.players[0].gear[slot].encoded_item/ilevel` 일치, 누락/불일치 **0**, 전체 12후보 간 장비 ID 세트 **1개**(스탯 재분배 후보끼리 장비 베이스 동일).
- 실제 B3 방어구·공통 12슬롯 물리 ID: `head=271492, shoulders=271490, chest=268223, hands=271493, legs=271491, wrists=268217, waist=268216, feet=268233, back=268248, neck=251142, finger1=268266, finger2=251136`. 무기 `main_hand=268215`와 장신구 `270175/270173`는 이번 input 교차검증에는 들어가지만 각각 B4/B7 등 별도 계약이다. **12개 방어구/공통 슬롯의 ClassID/Subclass 물리 source 전체 레코드를 이번 ZIP이 직접 포함하지는 않는다**: 타입 적합성은 `v167/v169/v232`의 기존 원본·필터 검증 범위를 통해 지지하며 실 Native JSON2는 ID·착용 슬롯·ilvl 소비 증거이다.

## 3. 역사 다중 ilvl 및 독립 미완료

**HISTORICAL_SCOPED:** [v180 #40980268952](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40980268952), tested `4eaa5e2554e695527d96234e6f5236e644134696`: 26 DPS×ilvl 266/300/321/340/344 **130개** 고정 대표 프로필은 모든 장비 `ilevel` 일치, 4티어 및 분리 session identity 오프라인 검증, 서로 다른 6 전문화×6 ilvl **실 Native36/캐시36** 성공. **현재 70783의 26 DPS 모든 방어구 부위/시즌 인증이 아니다.**

B3의 완료 범위는 대표 일반 장비 부위별 물리 ID/타입 차단 및 현재 실 SimC 입력·JSON2에 나타난 **목표 ilvl334 소비**이다. 시즌 획득 provenance 불명확한 후보를 사용자 gear 선택지로 새로 노출하지 않으며, v232의 `same_season_membership_not_proven`/정확 G 미승격은 보존한다.
