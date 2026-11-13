# v404 — 최신 사용자 승인: A7 WSE 비차단, 실제 소스 기준의 시즌 후보 엔진

> **최신 직접 결정이 이전 v403 WSE 차단 실험보다 우선한다.** 목표는 26개 DPS 전문화의 목표 ilvl/수동 T 기준 SimC 절대 CHMV 최적화이며, 시즌별 전체 아이템 획득 경로·WSE 해석 엔진이 아니다. **WSE가 양수·0·없음·형식 오류라는 사실만으로 현재 시즌 사용자 후보나 내부 대표 장비를 승인/차단하지 않는다.** WSE 원문/정수값은 진단 정보로만 유지한다. 현재 시즌 근거는 정상 인증 Blizzard/WCL 현재 raid·M+ 출처와 동일 게임 빌드 Wago DB2 정확 itemID/장비 부위/ExpansionID/DisplaySeasonID/Journal 매핑, 이후 제품에 소비되는 정확 SimC 항목에 있다. 이 정책은 영구 사용자 선택지에 미증명/다른 시즌 항목까지 무조건 올리라는 뜻이 아니다.

## 1. 설계 기준/역사적 실패의 원인

- 이전 v403은 `WorldStateExpressionID>0` 또는 미관측을 만난 레이드/쐐기 아이템을 조건 불명으로 처리해, 출처와 DisplaySeasonID가 일치하는 아이템도 공개 후보에서 누락시켰다. 이는 **WSE 조건식 자체를 추가로 확인해야 한다는 불필요한 Gate**였다. 사용자는 관련 아이템의 획득 목록 구축이 아니라 SimC DPS 최적화를 원한다.
- `WSE=0`이 아이템의 현재 시즌 소속을 독립 증명하는 것도 아니다. `WSE>0`이 아이템의 시즌 제외를 독립 증명하는 것도 아니다. WSE 해석/모든 아이템 WSE 확인/GPT 수동 ID 확인 과제를 새 P1 Gate로 만들지 않는다.
- **현재 유효한 출처를 정확히 구분**한다: `v155` WCL active raid/dungeon과 `v163` same-build JournalEncounter/Item/ItemSparse/MapChallengeMode unique join, `v165` 각 획득 출처의 장비 expansion/DisplaySeasonID 및 저널 encounter/instance 관계, `v166` 출처 조건 보존/내부 물리 후보 분리, `v167` 사용자 공개 선택. 현재 레이드는 WCL/DB2 선택된 활성 zone의 저널 항목이고, Journal `DisplaySeasonID=0`(레이드 쪽 unscoped) 또는 발견한 현 시즌 `DisplaySeasonID`면 후보 가능. 현재 쐐기는 발견한 **정확** DB2 DisplaySeasonID가 맞는 저널 출처만 후보. **다른 시즌 ID·불명확한 Item/Map/Zone 관계는 계속 보류**. 추가로 선택한 현재 장비의 SimC 입력/효과는 별도 검증.
- **내부 표준 일반 장비**는 사용자에게 장비 조합을 선택시키지 않는 별도 역할이다. 같은 빌드·장비정보/스탯/SimC 가능성을 확인하며 반드시 현재 획득 가능 장비인지 여부를 요구하지 않는다. 원본 DB2에서 발견한 미선택 전체 시즌 아이템/조건은 별도 검증 Gate가 아니다.

## 2. 최소 엔진 수정

- `runner/v163_zero_seed_db2_join.py`: `classify_era`는 `DisplaySeasonID`로만 출처 시즌 표시, WSE 인자를 평가하지 않는다. `WorldStateExpressionID` 유효 비음수 정수는 원래대로 저장. **누락/잘못된 값은 0으로 간주하지 않고 `None`, 원문 문자열이 있으면 `world_state_expression_raw` 진단으로 저장**, 잘못된 WSE가 아이템 후보 수집 전체를 차단하지 않음. `unverified_world_state_expressions`는 별도 diagnostics. `world_state_expression_membership_gate=False`, `full_season_completeness_confirmed=False` 유지.
- `runner/v165_current_season_gear_pool.py`: `_journal_origin_current`의 필수 `wse==0` 검사 제거. **활성 raid 저널 출처 + 정확 journal encounter/instance IDs + current/unscoped DB2 DisplaySeasonID** 또는 **활성 M+ 저널 출처 + 정확 현 DisplaySeasonID + journal IDs**를 검사. 구 봉인 `v163`의 `UNKNOWN_WORLD_STATE_EXPRESSION` 표시도 현 DisplaySeasonID가 맞으면 수락해 기존 캐시를 소급 차단하지 않는다. WSE 없는/양수/불형식 diagnostics가 후보 상태에 영향 없음. 서로 다른 획득 출처는 독립 검사; 불명확한 소속의 아이템은 보류.
- `runner/v166_compact_product_gear_db.py`, `runner/v167_product_season_gear_adapter.py`: 레거시 **INTERNAL_ONLY** M+ 후보의 정확 저널과 DisplaySeasonID 검사에 `WSE>0` 필수 조건 제거. `provisional_mplus_world_state_only` 등 기존 봉인 스키마 표시 필드는 이전 source/output 호환으로 유지하지만 **WSE가 필수이거나 진입 Gate라는 뜻은 아님**. `v166`은 실제 WSE 정수/None을 `source_evidence`로 전달하고 사용자 선택 여부는 시즌 출처로만 판단. 잘못된 표시명/SimC 효과의 독립 인증이나 새 DB는 도입하지 않음.
- 구조 단순화: 새 GraphQL/Wago/Blizzard 요청 **0**, Native **0**, WSE 데이터 테이블·독립 evaluator **0**, 62MB 전체 DB2 반복 수집 **0**. 동일 시즌 cache는 SimC revision만으로 폐기하지 않는 정책 보존. WSE 입력의 미관측과 시즌 출처 미검증은 완전히 다른 상태로 기록.

## 3. 실제 CI 및 증거 범위

- [최종 검증 시점의 focused GitHub Actions **#43373512035**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43373512035): tested HEAD `ae44502e0c94272f84f2153475cb5e944f50909e`, Ubuntu3.12 **137 테스트 시도 / 134 PASS / 3 별도 원본 마운트 SKIP / 0 FAIL**. A7 `v163`의 WSE 상태 비차단/원시 값 보존, `v165`의 같은 시즌 WSE 양수·누락·비정상 값 수락/다른 시즌 reject, `v166`·`v167`의 내부/공개 분리, `v403`의 7개 가상 아이템까지 full consumer chain, A1/A2/A4/A5/A6/v113/v181 회귀를 함께 검증. 신규 v166/v167 WSE 미필수 추가 테스트는 다음 focused run으로 동일 범위 검증.
- [정책 CI #43373512017](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43373512017): 78개 JSON/표 상태 정합 검사, 기존 14개 부정 테스트. **이 테스트 자체는 진짜 현 시즌 선택 아이템의 same-build/SimC Native 원본을 발급하지 않는다.**
- 이번 실제 70783 source는 기존 [A1~A6 0-seed real #43357639329](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357639329)의 10 Wago CSV /62,280,767 bytes/Blizzard·WCL 실 소스를 재사용. **v404 새 제품/현재 item ID 실제 A7 단계 실물 전 구간은 실행하지 않았다.** 새로운 최종 DPS/SEM/95% 결과 PASS라고 하지 않는다.

## 4. 다음 검증과 완료 계약

- [78개 구조화 완료 계약](../78_ELEMENT_COMPLETION_CONTRACTS.json) A7 `generic/current_source/product_integration = PENDING` 유지. **WSE 전체/모든 item의 조건 확인을 요구하지 않는다.** A7 `acceptance`: `현재 레이드·쐐기/동일 빌드 DB2가 자동 제공하는 실제 소비 아이템의 출처·시즌 소속 관계; WSE는 비차단 원본 진단`.
- **A7 범용 기능 판정:** 미래 시즌의 발매를 기다리지 않고 다른 시즌/빌드·출처·다른 DisplaySeasonID/잘못된 WSE의 회귀를 통과하면 이 축의 코드를 검증할 수 있다. 현재 빌드 원본과 실제 제품 item 소비 연결이 추가 검증 필요하면 해당 축은 각각 PENDING; 하나만 통과해도 78개 요소 COMPLETE 금지.
- 제품 향후 운영은 엔진이 정상 API/DB2/SimC로 자동 후보를 발견·분류하고, 원본이 실제로 누락된 경우에만 해당 선택 항목을 보류한다. **GPT가 매 새 시즌 각 아이템의 WSE를 직접 판단하거나 영수증을 수동 선별해주어야 제품이 작동하는 구조는 금지.** 필요한 최소 원본 예외만 오류로 노출. 별도 WSE 해석기·전 시즌 DB·장비 획득 경로 확대 금지.
- 최신 사용자 직접 결정 > v1.4/v1.4.1 비충돌 기존 정책 > 실 코드/영수증 > v403 차단 경로 역사. 격리 `probe/chat-cache-v035-20261024`만 변경; main/v003/Project UI/Work OS 공식 승격·기존 주 제품 개발 채팅 권한 변화 없음.
