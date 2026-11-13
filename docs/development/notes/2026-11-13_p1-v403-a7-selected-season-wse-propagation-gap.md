# v403 — A7: 레이드 WSE 미확정 아이템의 사용자 목록 오승격 차단, 원본 A7 인수는 보류

> **상태: A7 `generic=PENDING / current_source=PENDING / product_integration=PENDING` 유지.** 이번에 실제로 수정한 것은 `v163`의 WSE 조건부 표식이 `v165`의 레이드 출처 분류에서 잊히는 **소스→선택 후보 연결 오류**다. 현재 70783 특정 사용자 선택 아이템마다 원본 조건을 새 코드로 실물 대조하거나 실 사용자 장비/SimC 실행을 했다는 뜻이 아니다. 이전 A1~A6의 범용/실 원본 PASS 범위 불변.

## 1. 원인과 재현

- `runner/v163_zero_seed_db2_join.py::classify_era`는 `WorldStateExpressionID>0`인 레이드·M+ 저널 아이템을 `UNKNOWN_WORLD_STATE_EXPRESSION`으로 정확히 보류하고 `DisplaySeasonID`가 다른 아이템을 `UNKNOWN_OTHER_DISPLAY_SEASON`으로 분류한다. malformed/미관측 필드를 `0`으로 치환하지 않는다.
- 그러나 **`runner/v165_current_season_gear_pool.py`**는 `raid="raid_journal" in source_names`라는 **출처 존재 여부 하나만으로** `season_eligible`을 True로 만들었다. 같은 확장팩(예: 11)에서 WSE가 양수이거나 다른 DisplaySeasonID가 붙은 레이드 아이템도 `v166.current_candidates`와 `v167` 사용자 선택 목록에 잘못 도달할 수 있었다.
- 조건이 없는 레이드·M+ 아이템까지 모두 차단하면 필요한 현재 대표 장비나 장신구 선택이 불가능해지므로, 전 품목/전 시즌 WSE 인증 Gate가 아닌 **해당 선택 소스의 정확한 저널 행 증거**로 판단해야 한다.

## 2. 최소 코드·검증 변경

- `v165._journal_origin_current(row,display_season,raid=...)`: 실제 `v163`가 남긴 **정확 `display_season_id`·`world_state_expression_id=0`·positive journal encounter/instance ID**만 현재 획득 출처로 간주한다. 레이드는 이미 `v163`이 실제 활성 raid zone과 DB2 tier를 선택한 조건에서 `UNKNOWN_UNSCOPED_JOURNAL+season0+wse0` 또는 `DB2_DISPLAY_SEASON_MATCH+선택 season+wse0`를 허용. M+는 **선택된 DisplaySeasonID의 명시적 일치+WSE0**만 허용. WSE 양수·잘못된 시즌·손상/누락 조건은 조건부 보류로 남긴다.
- 하나의 아이템에 양의 WSE 레이드 획득 출처가 있더라도 **별도 검증된 같은 시즌 무조건부 M+ 출처**가 존재하면 그 경로를 독립적으로 인정한다. 존재하는 진짜 source를 무시하거나 WSE 값을 코드에서 자체 평가하지 않는다.
- `tests/test_v165_current_season_gear_pool.py`의 레이드 fixture를 정확한 `display_season_id=0, world_state_expression_id=0, journal ids`로 갱신하고, **레이드 WSE>0 / 다른 시즌 / WSE 미관측 / journal ID 오류 / M+ unscoped / 독립 M+ 무조건부 복구 / 가상 다른 현재 시즌**을 확인.
- 신규 `tests/test_v403_a7_selected_season_wse_pipeline.py`는 가상 시즌/빌드 `13.0.0.88888`, DisplaySeason83의 **다섯 item**을 `v165→v166→v167.public_options`로 실제 연결: 무조건부 raid·M+ 2개와 조건부 raid+독립 승인 M+ item 1개는 USER trinket list, WSE 조건부 raid 1개는 비노출, 조건부 M+ 일반 wrist 1개는 **INTERNAL_ONLY**. 기존 `v167` 사용자 장비 선택/SimC 효과 엔진은 변경하지 않음.
- `tests/test_v167_product_season_gear_adapter.py`: 독립 unittest 환경에서 이미 실행되는 실제 `v167.public_options`의 선택형 `v332` import가 `runner/` 경로를 못 찾는 문제만 테스트에서 교정. 제품 소스 자체에는 언어/표시명 규칙 변경 없음.

## 3. CI 결과 및 실 원본 범위

- **첫 Actions #43370681444 실패를 숨기지 않음:** A7 `v165` 새 분류 8 PASS 범위는 통과. 뒤이어 처음 추가한 역사 `v167` 단독 테스트 4개에서 `ModuleNotFoundError: v332_blizzard_ko_item_labels`; 제품 WSE 결함과 별도 **테스트 import 경로** 문제.
- [교정 후 Actions #43370809434](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43370809434) 성공. 이후 전체 연결 시험 추가.
- **최종 실 GitHub focused Actions [#43371062757](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43371062757)** tested HEAD `1be01fa6269a598b2b143f44b4883d6b7e29ce1d`, Ubuntu Python3.12: **137회 시도 / 134 PASS / 3 조건부 SKIP / 0 FAIL**. A7 `v165` 8시도(7 PASS/1 SKIP), `v166` 8 PASS, `v167` 10시도(9 PASS/1 SKIP), 신규 전체 경로 1 PASS. 다른 suite A1/A2/A4/A5/A6/v113/v181 회귀도 통과. SKIP은 외부 saved v163/v166 원본 별도 mount와 v163 DB2 full snapshot를 필요로 하는 선택 테스트.
- **엄격한 원본 구분:** 실제 현재 공식 Blizzard/WCL/Wago 70783·10 DB2 CSV 62,280,767B·WCL 활성 레이드/M+ 유일 조인은 기존 [#43357639329](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357639329) 증거이며 이번에는 재수집하지 않음. 이번 수정 뒤 **실 현재 selected item id의 v165/v166/v167 source chain 실행·source SHA/영수증은 새로 취득하지 않았다**. 합성 시나리오를 실제 시즌 선택 UI 검증으로 승격하지 않는다. 실 DB2 source receipts와 국소 WSE 논리 수정은 서로 보완적인 증거이지 동일 실물 통합 성공이 아니다.
- **자원:** 신규 Native0, Wago 62MB 재다운로드0, 새 인증 API 호출0, 새 아이템 효과/조건 해석기0, 기본 최적화·캐시/취소·재개·수치식 변경0. `v217` code fingerprint가 실제 변경된 단계만 재확인하는 기존 원칙 유지.

## 4. A7 남은 작업과 판정

- **범용 기능:** 다른 시즌/빌드·WSE와 raid/M+ 다출처 조건 회귀는 추가됨. 하지만 현재 실물 제로베이스의 **선택된 항목 조건**과 연결하지 않은 상태이므로 A7 전체 `generic=PASS`를 선언하지 않는다.
- **현재 원본:** 실제 사용 아이템(대표 일반 장비, 선택 장신구/특수장비)의 정확한 `item_id`, `DisplaySeasonID`, `WorldStateExpressionID`, 해당 근거 저널/SimC·같은빌드 source SHA를 **필요한 선택 범위만** 확인. WSE 양수는 독립 원본으로 입증하지 않는 한 `PENDING` 유지. 선택하지 않은 모든 아이템·외부 전체 시즌 WSE 완성은 Gate가 아니다.
- **제품 통합:** 해당 selected 아이템 증거가 `v216` 내부 대표 gear·`v167` 공개 후보·사용자 SimC 프로필 및 환경 설치에서 실제로 소비되는지 확인, 다르면 최초 누락 필드만 수정. SimC 수치·DPS/SEM/95%/전역 최적을 A7 원본 판정으로 자동 승인하지 않는다.
- **정본 상태:** [`78_ELEMENT_COMPLETION_CONTRACTS.json`](../78_ELEMENT_COMPLETION_CONTRACTS.json)의 A7 세 축 `PENDING` 및 `next_review=A7`, [자동 생성 상태표](../78_ELEMENT_STATUS_GENERATED.md)를 유지. GitHub Actions 정책 검사 [v401 gate](../../../integration_probes/v401_completion_contract_gate.py) PASS라도 진짜 A7 item source/제품 E2E 근거를 대신하지 않는다. 다음 작업은 **현재 동시즌 봉인 source에서 실제 선택 아이템·WSE 조건만 최소 조사**.
- **권한:** 격리 브랜치만, main/v003/Project UI/공식 승격·주 제품 채팅 소유권 변경 없음.
