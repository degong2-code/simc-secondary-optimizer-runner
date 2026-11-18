# P1 v608 — SimC 주문/발동 마부도 정적 CHMV E0 허용 + 기존 Policy A 등록 경로 연결 (2026-11-19 KST)

## 정책·제품 소유권

최신 사용자 결정: 정상 영구 마부의 동일 제작 계열 최고 품질·실제 부위·정적 CHMV 소유권만 확인한다. 마부에 **주문 효과·proc·사용자 DPS가 있는지**를 별도 승인 기준으로 삼지 않는다. `E`는 영구 마부로 인한 **정적 치명/가속/특화/유연 gear rating**만 의미하며, 동적 스탯 변화와 proc/APL/DPS는 SimC가 책임진다. `E0`는 효과 없음이 아니라 네 고정 스탯의 명시적인 0 벡터다.

사용자 목표는 **26 DPS 미래 ilvl(기본 334)/수동 T의 CHMV 절대 rating을 SimC DPS로 최적화**하는 일반 제품이다. 시즌 G/J/F/O, B=G+J+F, T=B+O, manual T 우선, 선택 L/E/O 중복 방지, 95% 통계, 캐시·취소·재개/Windows 사용자 흐름 보존. 일반 임시 마부 제외·무기 기름 O 별도. 전체 장비 조합 추천·AI 런타임 없음.

## 최초 생산자→소비자 차단과 수정

**최초 실제 코드 차단:** 기존 `runner/v216_environment_build_coordinator.py::_v217_policy_A_source_relation_receipts`는 원본 `v211` 분류의 `effect_family=static_nonchmv_item_mod`, `bool(static_components)`, `spell_effects=[]`, `dynamic_chmv_proc_roles=[]`, `simc_custom_handlers=[]`을 한꺼번에 요구해 **순수 SimC spell 마부 및 비CHMV+SimC spell 마부**를 E0로 통과시키지 않았다. 이 조건은 정적 E 회계보다 훨씬 넓은 전투 효과 조건이어서 최신 정책과 불일치했다.

**코드 `fffae67a`:** 기존 sealed v211 classification 및 SimC `ITEM_ENCHANTMENT_STAT`/spell 구분은 그대로 사용하고, `static_chmv_rating_present_in_dbc=False`, `static_chmv_stats=[]`, `unknown_components=[]`, 모든 알려진 static components가 nonCHMV 범위에 속함, `spell_effects`가 정상 positive original spell ID 구조, 정확한 새 시즌 source identity, 설치 전 `native_E_evidence=NOT_MEASURED_NEW_BUILD`, SimC owner 등만 확인. **정적 컴포넌트 0개/SimC spell 1개 이상도 E0**. spell/proc/dynamic CHMV flags/custom handler 존재는 E0 차단 이유가 아님. 실제 효과 활성화/피해량/등급별 강도를 검증하거나 계산하지 않음. `fixed_E`는 기존 v220/v212가 검증하는 정확 4-stat zero 벡터이고 `gameplay_or_native_effect_attested=false` 유지; 주문 ID 개수는 회계 evidence 참고용이며 DPS 인증 아님.

**기존 재사용:** v607 `v191+v583` 봉인 제작 품질 계열 → `v216` 네 receipt(`source_relation`, `simc_input`, `product_input`, `chmv_budget`) → `v220` Policy A → `v196` 기존 versioned installer input → `v212` 등록/설치 및 `v113/v106/v098/v096` 사용자 프로필 경로. 새 engine/Gate 없음.

**테스트 수정 및 추가:**
- `32d7bad8`: 기존 v606 focused test에 SimC-owned spell/동적 proc·static+spell·spell-only E0 양성, malformed spell/unknown static CHMV/양수 정적 CHMV 음성 추가.
- `9e4fd73e`: 기존 `v240` fresh source test는 더 이상 `chmv_budget` 항상 PENDING을 기대할 수 없음. 정적 E0 증거가 있어도 `v583` 제작계열 근거가 없으면 **`product_input`만 PENDING**이며 사용자 등록 없음. 최소 조건 변경만 반영.
- `6e3a4839`: v607 sealed source join synthetic integration에서 **SimC spell+비CHMV 정적 컴포넌트**, 올바른 v191/v583 stage receipt/SHA, 네 Policy A receipt → 기존 `v196.prepare_verified_fresh_choices`의 **정확히 1개 준비됨 / 0개 공개됨**을 함께 확인. 연결 여부를 기능 단위에서 검증했으며 합성 테스트를 실제 시즌 Native E2E로 표시하지 않음.

## 실제 동일 빌드 원본 확인 (신규 수집 없이 기존 영수증 재사용)

기존 2026-11-18 실제 Wago↔SimC 소스 Actions [#44217110154](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44217110154) artifact **14389266267** `p1-v582-wago-permanent-enchant-item-relation` (게임 빌드 **12.1.5.70783**, SimC `de11f57df75dda668bae6ac7043a43b98831fa96`)의 원본 76 `matches`를 다시 읽어 계열(token, item class, inventory/subclass mask)별로 교차 계산. **38개 계열/76개 원본 마부 ID 전부** 동일 `CraftingDataID`, SimC rank 1→2, Wago rank 13→14, 각각의 정확한 물리 아이템 ID 조건을 충족. **38/38 출처 계열·최고 품질 연결 관측**은 기존 실제 원본의 검산이며, **새 빌드 38개 중 자동 등록 개수 또는 정적 E0 개수 확인은 아님**. 보존된 artifact는 v191/v211/v583/v212 full stage 원본/설치 결과를 포함하지 않으므로 현 세션에 존재하지 않는 서명과 설치/Native 증거를 만들지 않음.

## CI·비용·증거 경계

- [#44341446561](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44341446561) v212 Windows/Ubuntu 양쪽 **526 tests / 4 skips / 0 fail**.
- [#44341446576](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44341446576) fresh classification bridge **SUCCESS**, [#44341446554](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44341446554) 공통 offline **SUCCESS**. 이 CI 결과는 마지막 소스 test-only commit `6e3a4839` 직전 `9e4fd73e` 코드 SHA 증거.
- 최신 연결 통합 테스트 [#44342593298](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44342593298) **SUCCESS**, 신규 원본 품질 테스트 7 PASS와 기존 v583/v584/v220/v240/v216 등 PASS. 마지막 `6e3a4839`의 추가 테스트는 합성 동일 스코프, Native 미실행.
- 초기 `fffae67a`/중간 `32d7bad8` workflow FAIL은 E0 정책 변경 후 구형 테스트가 spell-only/E0 미승격을 기대해서 발생. `9e4fd73e` 테스트 계약 갱신 이후 v212/공통 CI PASS. 기존 역사 source-to-catalog workflow의 만료 artifact 다운로드 FAIL은 별개.
- **이 작업에서 신규 SimC Native 0회, 게임 Wago HTTP/DB2 수집 0회, DPS 캐시/동일 시즌 정적 아이템 캐시 무효화 0회**. 기존 별도 v570 실제 Windows SimC E2E·v572 재개 Native 증거는 재사용하되 이 변경의 새 마부 실행 PASS로 전용하지 않음.

## 남은 최소 제품 작업

1. 실제 시즌 **봉인 원본 전체 v191/v211/v583, 예산 G/J/F/O와 v212 설치 source가 동일한 stage root**에 존재하는 사용자 환경에서 기존 v608 producer를 실행해 새 `published_verified_options` 실제 승인 수와 최초 등록 ID 기록. 지금 보존된 것은 역사적 compact v582 source이지 정상 v212 전체 설치가 아님.
2. 승인 선택지가 있으면 기존 실제 사용자 대상 부위·ItemID·정확 `enchant_id` 단 1회, 정적 E/T 예산, 프로필/캐시를 확인하고 **기존 증거가 정확히 같은 identity가 아닐 때만 최소 새 Windows SimC DPS**를 실행. 결과 DPS/SEM/95%·취소/재개가 실제로 귀속됐는지 확인.
3. 실 설치에서도 0개라면 **실제 `product_input`/정적 E/물리 슬롯/사전 소스 stage 중 최초 누락 조건**만 기록하고 그 코드 구간부터 수정. 효과/proc 수치 비교 Gate 복원 금지.
4. 범용 정적 E>0·복수 부위·손/무기 선택은 이 1건 실 증명 후 기존 예산/프로필 소비자 확장으로 해결.

**공식 승인/권한:** 격리 브랜치만 수정, main·immutable v003·원본 v016·Project UI·공식 M0/Shared State·기존 주 제품 개발 채팅 소유권 변화 없음. **15/78 COMPLETE, full_product_e2e=PENDING** 유지.
