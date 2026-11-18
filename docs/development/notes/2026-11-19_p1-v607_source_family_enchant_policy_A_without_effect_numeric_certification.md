# P1 v607 — 영구 마부 최고 품질 등록 기준 간소화 (2026-11-19 KST)

## 사용자 직접 정책 결정과 판단

2026-11-19 직접 지시: “등급별 효과 수치·동등성 증거”가 정말 필요한지 확인하고 진행. 2026-11-18 직접 의견: 마부에 관한 독립 효과 통과/비통과 심사 및 E0 반복 인증을 중단하고, 실제 유효 장비 부위·시즌 최고 품질·정적 CHMV rating만 확인하며 발동·효과·DPS는 SimC에 위임한다.

**검토 결론:** 같은 원본 제작/마부 계열의 **최고 품질 선택 자체**에 등급별 주문 효과 수치 우위·`id_spell` 동일성·proc 발동을 별도 증명할 필요가 없다. `CraftingDataEnchantQuality`의 실제 `CraftingDataID` 동일성, Wago 물리 ItemID→정확 `SpellItemEnchantmentID`, 같은 빌드 SimC generated enchant의 토큰/클래스/부위 마스크 및 계열 내 품질 순서를 확인하면 **출처 기준 최고 품질 선택**이 가능하다. Wago 품질 순위 13/14와 SimC rank 1/2는 같은 숫자여야 하지 않으며 각 계열 내 순서로 검증한다. 이름이 비슷한 서로 다른 제작 계열·적용범위는 합치지 않는다.

이 정책은 **영구 마부 사용자 선택지의 출처 기준 최고 품질 인증에 한정**한 최신 사용자 직접 결정이다. 이전 v1.4.3 및 v371의 동일 효과·모든 실제 효과 수치 비열등성 인증 요구는 이 범위에서 대체된다. 보석·영약·음식·다른 선택지의 기존 품질 정책을 일괄 변경하지 않는다. 마부 실제 효과 활성화/등급별 실측 DPS/효과 강도는 SimC 책임이며, 이 코드가 성능 우월성을 보장한다고 표시하지 않는다.

## 구현 (실제 GitHub 격리 브랜치)

- `runner/v196_current_season_user_catalog.py` — 기존 `product_input` 네 가족의 승인·정확한 품질 rank/SHA·원본 슬롯·정적 E 벡터 요구를 유지하면서, 출처가 봉인한 `source_quality_family_verified + same_build_physical_join_verified`를 원래 효과 수치 비열등성 두 플래그의 **대체 승인 경로**로 수락. 기존 신뢰된 레거시 효과/비열등성 receipt는 그대로 허용.
- `runner/v216_environment_build_coordinator.py::_v607_sealed_highest_crafting_quality` — 기존 `v191` 생성 원본의 **모든 계열 rank**와 `v583` 봉인 Wago 물리 ItemID→`CraftingDataID`→SimC `enchant_id` 매핑을 교차 검증. 같은 마스크/토큰과 최고 SimC rank, 동일 CraftingDataID, 서로 다른 물리 등급 아이템, 증가하는 Wago rank, **Wago의 해당 제작계열 전체와 SimC 계열 완전 일치**가 있을 때만 내부 품질 출처 SHA 생성. 주문 spell ID/실제 효과 계수와 비교하지 않음.
- `_v217_policy_A_source_relation_receipts`에 선택적 **기존 sealed v583 원본** 소비 연결. 실제 stage receipt + SHA + 빌드/SimC revision 검증 후 기존 `product_input` 증거를 생성. `preflight_new_season_source`의 원래 Build 경로가 기존 `collected.fresh_permanent_enchant_item_source`를 전달하며, `_fresh_source_owner_merge_policy_A_original_source_relation`은 기존 v220/v212 인증 흐름에서 provenance를 보존해 합병한다. 원본 누락·변조·불확실한 rank 계열은 **그 선택지 품질만 PENDING**, verified core G/J/F/O는 유지.
- `v220` 4-family 승인, `v212` 버전 설치, v113 UI/SimC profile 사용자 경로, 기존 E0 v606, 양수 E 회계·선택 슬롯 검증·SimC·95% 엔진은 변경하지 않음.
- 새로운 효과 인증 Gate/엔진, 임시 마부·전체 장비 DB/전체 장비 picker, 별도 AI runtime, SimC Native/HTTP/DB2 호출 **없음**.

변경 commits: `a31462c1`(v196), `3d8c9cb4`(v216 producer), `1e1e772c`(원본 전체 rank 교차검증), `1ed98ca9`/`489e95d6`/`e2d8f03d`(테스트), `1eb80514`(기존 v583 CI에 테스트 추가).

## 테스트와 증거 경계

- 현재 v607 오프라인 Actions [#44333997125](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44333997125) **SUCCESS**. 신규 `tests/test_v607_sealed_crafting_enchant_quality.py` **7 PASS / 0 FAIL**: 정확한 제작계열 최고 rank 양성, 등급 간 Wago/SimC 순위 차이 허용, CraftingDataID 불일치·원본 mask drift·하위 rank 누락·빌드/revision 변조 거부, v196 경로, 원래 v216 stage receipt→네 receipt 생성 및 선택적 v583 SHA 변조 시 품질만 보류. 기존 v583/v584/v220/v585/v240/v216 등 호환 테스트도 같은 workflow에서 PASS.
- 최초 새 test 실패 [#44333274700](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44333274700)은 낮은 품질이 다른 source-mask 가족으로 옮겨도 상위 품질을 승인하던 결함을 발견; `1e1e772c`의 **전체 Wago 제작계열 coverage 검증**으로 해결. 둘째 신규 test fixture 실패 [#44333782017](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44333782017)은 실제 v213 v196 projection에 존재하는 `quality_rank`를 합성 fixture에서 빠뜨린 탓; `e2d8f03d`에서 수정하고 정상 CI PASS.
- 이 변경은 **봉인된 실제 Wago 70783 데이터와 새 생산자 사이의 신규 live 전체 Build 실행, 신규 실물 사용자 옵션 등록 개수, Windows Native DPS E2E를 증명하지 않음**. 전자는 역사 v582 38/38·76/76 exact Wago join 증거를 재사용하고, 새 코드는 합성·기존 regression 범위까지 시험했음. 실제 등록 마부 0이던 v606 상태를 새로운 측정 승인 건수로 승격하지 않는다.
- 이전 `v191→v211→v213→v196` 워크플로의 일부 historical 실패 [#44332503281](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44332503281)는 만료된 Actions artifact `v192-updated-simc-catalog-41017578894` 다운로드 실패. v607 코드 품질 FAIL 증거가 아니며 전체 CI 100% green 주장 금지.

## 다음 최소 제품 작업

1. 검증된 **현재 시즌 봉인 Build/이미 있는 v583 source**가 다시 연결되는 실제 환경 설치에서 `source_quality_family_verified` 및 현재 E0/정적 E가 모두 충족된 정확 ID를 확인. 모든 옵션을 강제 재수집하지 않음.
2. 실제 자동 등록 항목이 0이면 첫 미해결 조건을 **source family / static E / slot / original v196/v212** 중 하나로 나눠 보고. 효과 수치/발동이라는 새로운 Gate를 재도입하지 않음.
3. 최초 등록 1건은 기존 v212→v113→v106→v098→v096 → SimC DPS/SEM/95%·캐시·재개를 검증; 기존 identical-scope Native 영수증을 재사용하고 변경 경로에서 부족한 최소 Native만 실행.
4. 후속 E>0·복수 장비 슬롯·손/무기 마부는 기존 CHMV와 프로필 경로를 **확장**, 별도 마부 효과 계산기는 만들지 않는다.

**권한:** 격리 브랜치만 수정. main 병합/v003 불변/v016 원본/Project UI 등록/Work OS 공식 승격/기존 주 제품 개발 채팅 소유권 변경 없음. 공식 기존 기록 15/78 COMPLETE, `full_product_e2e=PENDING` 유지.
