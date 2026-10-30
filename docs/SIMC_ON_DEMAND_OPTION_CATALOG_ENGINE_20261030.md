# SIMC Secondary Optimizer — 사용자 요청형 음식·물약·장식 카탈로그 수집 절차

**상태 2026-10-30:** v189·v190 실제 구현/오프라인 시험 PASS. 아래의 전체 UI 승격까지 완료된 엔진이라는 뜻이 아니다. 본 문서는 구현과 미완료 조건을 구분한다. 최신 사용자 의도: *새 시즌/SimC 교체 또는 사용자가 요청했을 때 재수집*, 자동 버전 탐지/상시 모니터링/별도 최적화 엔진 생성 금지.

## 기존 방식의 결함

- `v108_native_consumable_inputs.SUPPORTED`: 기존 MID2 SimC 대표 프로필에서 관측한 **음식 4개 토큰 + disabled**, **물약 3개 토큰 + disabled**. 이번 시즌 전체 아이템 검증 목록이 아님.
- `v188_user_choice_metadata`: UI 설명용 이름과 현재 증거 있는 **방어구 안감 2개**만 허용. 지원되지 않는 목걸이·반지·무기 장식을 자동으로 추측하지 않기 위한 보수적 제한일 뿐, SimC 전체 장식 구현 목록과 동등하지 않음.
- 공식 SimC `engine/player/consumable.cpp`: 음식/물약은 이름·품질 접미사를 **컴파일된 DBC 아이템 기록에서 탐색**, 아이템 효과로 버프·액션을 구성함. 그러므로 `unique_gear_midnight.cpp` 등록 함수 목록과 대표 프로필에서 관측한 토큰을 합쳐도 전체 소비재 인식 목록이라고 단정할 수 없음.
- SimC는 복잡한 아이템 효과·APL·DPS를 소유한다. 본 프로그램이 게임 내 장식 효과 메커니즘이나 음식/물약 buff 로직을 재구현하지 않음.

## 단계별 단일 요청형 수집 절차

| 단계 | 기준 입력과 책임 | 현 상태 |
|---|---|---|
| 1. SimC 핀과 소스 효과 등록 탐색 | 정확한 **40자리 SimC 커밋**, `unique_gear_midnight.cpp` 원본 SHA. 함수 등록 ID·핸들러·비활성·최소 게임 버전·주석 이름까지 수집, **후보**만 출력 | **v189 구현/실제 pinned source PASS** |
| 2. 같은 빌드 게임 DB의 아이템 후보 분류 | 기존 v161 Wago DB2 스냅샷 **Item + ItemSparse**의 원본 SHA를 확인해 소비재 class0/food subclass5, potion subclass1, ExpansionID 필터 후 아이템 ID·enUS 이름 확보 | **v190 구현/기존 v161 artifact 재사용 PASS** |
| 3. SimC 실제 소비재 수용 ID/품질·스펠 연결 | 같은 바이너리의 **컴파일 DBC**, 등급별 아이템 이름/token, ItemXItemEffect → ItemEffect → SpellID와 v189 등록 핸들러 대조. 소스 등록 없는 일반 DBC 효과도 유효하게 분류. 버전·누락·동명이인·미지원 명시 | **미구현. 단계 1·2는 이 부분을 인증하지 않음** |
| 4. 장식 유형/실제 제작 호환성 | **사전에 장식이 붙은 제작 완제품**과 **추가 재료**와 **효과 등록만 된 spell**을 구분. 게임 제작 레시피/선택 재료 부위 제약과 정확한 제작 item/bonus/embellishment 옵션의 대응 확인. 방어구·목/반지·무기를 종류별 판정 | **미구현. 이름으로 착용 부위·효과 추측 금지** |
| 5. 표시 정보 | 동일 item ID의 이름(koKR 출처/locale), 툴팁 효과 요약, 품질과 실제 SimC 토큰/효과 ID 분리. 수치·상호작용은 SimC/D BC 근거 없는 경우 UNKNOWN | **v188 일부 수동 표시. 자동 소스 연결 미구현** |
| 6. 사용자 목록 안전 승격 | 식별된 특정 신규 옵션만 기존 입력의 source-default·F/J/O/CHMV 계약과 스탯 정합, 최소 Native 수용 시험, 불가 항목 fail-closed. 버전된 카탈로그에 `SUPPORTED`/UI 매핑, `v151` 변경 영향 및 `v106` 세션 identity 분리 | **미구현. 현재 UI·기존 v108 허용 값 불변** |

## 실제 확인된 코드/DB 후보 규모 (미승격)

SimC `7bc10711b5a4514066fa402ca0a71c9ba4b7c9dd`:
- **음식 효과 등록 37건**. 하나의 spell이 여러 음식 이름에 쓰일 수 있고, 일반 DBC 음식 구현이 등록 함수 없이도 가능하므로 **음식 아이템 37종이라는 뜻이 아님**.
- **물약 전용 효과 핸들러 5건**. 일반 DBC 물약(예: 기존 `lights_potential_2`)은 직접 등록이 없어도 SimC가 인식할 수 있으므로 전체 물약 숫자가 아님.
- **장식 및 다크문 관련 등록 20건 중 DISABLED 1건**, 기타 사전 장식 완제품·선택 재료·다크문 복합 spell 포함. **선택 가능한 장식 19종이라는 뜻이 아님**.
- [#41014319837](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41014319837) `v189` 공식 pinned C++ 원본 다운로드 및 정확 구역 구조 파서·버전·SHA·후보 영수증 PASS, Native 0.
- 기존 [v161 Wago 스냅샷 #40836955761](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40836955761)의 원본 **Item/ItemSparse SHA**를 그대로 재사용. Wago 새 수집 없음. `game build=12.1.5.70575`, `ExpansionID=11`. `v190` [#41014544715](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41014544715) **음식 원본 아이템 후보 192개, 물약 원본 아이템 후보 61개** 추출·감사 PASS, Native0. 이 숫자에는 당장 DPS 사용자에게 선택을 허용하기 어려운 것들이 포함될 수 있으며 SimC/레시피/실제 사용성을 **확인하지 않은 raw 후보 수**다.
- 게임 DB2 빌드 `12.1.5.70575`와 핀 SimC의 **컴파일 DBC 실물 빌드 동일성은 아직 별도 검증하지 않음**. 소스 C++ 핸들러의 존재도 그 바이너리·게임 아이템의 실제 발동 증거가 아니다.

## 다시 실행하는 방법

동일한 현재 사용 SimC 리비전 원본을 요청 시 수집:

```bash
python runner/v189_simc_consumable_embellishment_discovery.py \
  --simc-commit 7bc10711b5a4514066fa402ca0a71c9ba4b7c9dd \
  --out out/v189_simc_effect_candidates.json
```

**기존** 같은 빌드 v161 CSV 스냅샷이 있을 때만, 다운로드 없이 기존 파일 재사용:

```bash
python runner/v190_consumable_item_snapshot_join.py \
  --v189 out/v189_simc_effect_candidates.json \
  --db2-folder path/to/existing-v161-csv \
  --expected-build 12.1.5.70575 --expansion-id 11 \
  --out out/v190_db2_consumables.json
```

Actions `v189_simc_consumable_embellishment_discovery.yml` 및 `v190_consumable_db2_reused_snapshot.yml`에 `workflow_dispatch`를 지원. 정확한 소스 리비전, 정확한 기존 스냅샷 run ID·빌드·expansion을 직접 입력하며, 자동 “latest” 해석/주기 실행은 없다. 보관기간 만료 시 이전 스냅샷을 허위 재사용하지 않고 동일 기존 v161 절차로 새 요청 시에만 취득한다.

모든 중간 파일은 작은 영수증/후보 목록을 Actions artifact로 제공하며 리포지토리에 대형 CSV/SimC 바이너리를 영구 저장하지 않는다. 기존 검증 영수증은 읽기/재사용하되 수정·삭제하지 않는다. 새 SimC Native·전체 26×6 재계산·독립 효과 인증 Gate는 하지 않는다.

## 다음 실무 과제

**v191(신규 최적화 엔진 아님)**: SimC 컴파일 DBC와 같은 빌드의 ItemEffect/ItemXItemEffect를 기존 source-first 저장물과 대조하여 음식·물약의 정확한 등급·SimC 토큰·효과 spell을 확정. 이어서 장식 원본에 대해 CraftingData/선택 재료/레시피 등 **정확한 실제 호환 원본**을 연결하고, 서로 다른 장식 유형의 표적 Native를 최소 실행해 UI 전체 선택 목록을 승격한다. 출처가 모호한 항목은 UNKNOWN/선택불가로 유지한다. 핵심 목표는 사용자가 모든 소비재와 장식 중 유효한 것을 **설명과 함께** 선택하도록 하는 것이며, 현재 2개 안감만 허용하는 UI를 최종 상태라고 판단하지 않는다.
