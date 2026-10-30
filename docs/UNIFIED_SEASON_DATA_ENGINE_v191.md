# SIMC Secondary Optimizer — 통합 시즌 데이터 갱신 엔진 v191

**상태: 실제 SOURCE-FIRST 후보 카탈로그 실행 PASS. 제품 UI 전체 적용은 아직 아님.** 사용자 직접 결정(2026-10-30): 시즌 중간 패치·시즌 변경·확장팩 변경에 **요청형으로 한 번** 조사하고, 품질 단계가 있는 동일 효과는 확인 가능한 최고 등급만 사용한다. 같은 최상위 품질 안에서 수치가 다르더라도 **동일 효과·동일 적용 부위의 검증된 효과 강도만 비교**한다. 치명/가속/특화/유연, 서로 다른 공격·발동 기전, 적용 부위가 다른 장비를 하나로 잘못 합치지 않는다. 새 시즌 감시·정기 수집 기능 없음.

## 목표: 분산 탐색을 하나의 갱신 계약으로

`v191_unified_season_data_update.py`는 기존 `v161`(DB2 원본), `v163/v165/v166/v167`(장비 분류), `v168/v169`(13직업×5티어·26전문화 대표장비), `v189`(SimC Midnight 효과 등록), `v190`(DB2 음식/물약 후보)와 기존 `v151` 변경 영향 판정 체계를 **교체하지 않고 재사용**한다. 이미 추출된 출처·SHA·Item IDs/옵션의 사전검증된 조각을 하나의 보고서에 묶는 얇은 orchestrator다.

**반드시 포함해야 할 데이터:**
- 장비: 대표 일반 방어구/무기/반지·목/방패·보조장비, 장신구, 사용자 선택 특수효과 장비, 제작 가능 장비와 부위별 ID; 직업/전문화/주능력치/티어 스탯·무기 성능.
- 클래스 티어: 13직업×5개 실제 ID, 프로그램이 사용자 선택 특수·장식과 겹침을 해결해 4세트 유지, SimC 효과는 SimC 소유.
- **장식:** SimC 구현 효과 등록 전체를 발견 후보로 사용한다. Disabled 효과와 실제 구현은 구분하지만, 별도 사용자 정의 효과 인증 Gate를 만들지 않는다. 장비 DB·아이템/마부/제작 원본에서 사용 가능한 장비 유형(방어구/목/반지/무기)과 정확한 옵션/ID를 이어서 사용자 선택을 구성한다. SimC 문서상 `embellishment=` 파서는 부위제한이 없으므로 *실제 부위는 아이템 데이터로 결정*한다.
- **영구 마법부여:** SimC `engine/dbc/generated/permanent_enchant.inc`의 `enchant_id`, `rank`, `item_class`, `mask_inventory_type`, `mask_item_subclass`, `tokenized_name`. 정확한 슬롯/재질/무기 유형 검증 후 **각 장비 부위별** 사용자 선택. SimC `find()`는 `1 << inv_type` 비트로 판단. 비트 0은 전 부위 허용 인증이 아닌 제한 정보 미확정이다.
- **임시 무기 강화:** `temporary_enchant.inc`의 효과 spell ID와 quality rank, 한손/양손/원거리 장착 가능 슬롯에 따라 별도 처리. 기존 기름 O=고정치 중복계산 방지 유지.
- **보석/특수 다이아몬드:** `gem_data.inc`만으로 실제 보석 item ID를 추정하지 않음. `ItemSparse`/아이템 효과/보석 속성/소켓 유형과 연결해 최고 품질·사용 가능 색/특수 슬롯과 정확한 J/주능력치/비정적 효과를 구분.
- **음식·물약·영약/플라스크·증강룬:** SimC 컴파일 DBC 아이템과 동일 시즌 DB2 아이템(정확 ID·이름·품질·효과 ID)의 동등 관계 확보. `v189` 효과 등록은 필요하지만 일반 DBC 효과 구현이 있을 수 있으므로 전체 아이템 판정의 단독 출처가 아님.
- 이름/설명: koKR 게임 아이템명 또는 명시된 신뢰 가능한 locale, 발동·효과 수치 등은 SimC/item metadata 기반. 미관측은 0으로 바꾸지 않음.
- 사용자 정적 budget B/T/L/O의 우선권: 플라스크 F, 보석 J, 고정 특수효과 L, 기름 O를 새 카탈로그에서 무심코 중복·재가산하거나 강제 제로 처리하지 않음.

## 중복 제거와 최고 등급 정책

1. **동일 효과군**은 식별 가능한 spell/enchant ID 계열과 효과 지문(스탯 종류, proc, buff, 수치 규칙, 지속시간)으로 묶는다. 품질 rank 1/2/3 등은 최고 유효 rank만 남긴다. `permanent_enchant`와 `temporary_enchant`에서 토큰+물리 호환성 마스크 단위로 우선 정확한 최고 rank 레코드를 만드는 기능은 **v191 구현 완료**.
2. 비교 가능한 동일 효과·동일 적용부위의 최고 rank 레코드가 여러 개라면 실제 같은 기준으로 얻은 수치가 가장 큰 품목을 남긴다. 수치나 효과의 비교 가능성이 불명확하면 **모두 보존/미검증**한다. '높은 ilvl=무조건 강함', '주능력치=보조능력치보다 우수' 등 추정 금지.
3. **치명/가속/특화/유연 등 서로 다른 선택 목적**, 공격·방어·발동 조건이 다른 효과, 적용 가능한 부위가 다른 마부는 각각 유지한다. 1등/2등 효과를 DPS 시뮬레이션 없이 AI 추측으로 제거하지 않는다.
4. 디버깅/호환성용 `source_default`·`disabled` 값은 기존 세션의 원본 의미를 보존한다.

## 이번 실제 실행 결과

- SimC `7bc10711b5a4514066fa402ca0a71c9ba4b7c9dd`, `unique_gear_midnight.cpp` → `v189` 실제 37 음식 등록 / 5 물약 등록 / 20 장식·다크문 등록(1 비활성).
- DB2 `12.1.5.70575` 기존 v161 스냅샷 재사용 → `v190` 실제 음식 아이템 후보 192 / 물약 후보 61 (아직 SimC 실제 수용과 1:1이라고 판정하지 않음).
- SimC 정확 리비전의 `permanent_enchant.inc`, `temporary_enchant.inc`, `gem_data.inc` 3종을 **새 소스 핀으로 추가 확인**, 파일 SHA를 영수증으로 기록. 게임 데이터 빌드는 `12.1.5.70448`이며 기존 Wago 빌드 `12.1.5.70575`와 **차이를 명시적으로 경고**.
- `v191` 실제 통합: **대표 장비 511개·티어 65ID**, SimC 영구 마부 원본 **1062 entries**(같은 토큰+장착 형태의 최고 rank 정리 후 **772개 후보**), 임시 강화 원본 117, 보석 속성 원본 2409. 772는 **현재 시즌 최종 마부 추천 수가 아님**, 과거 모든 확장팩 기록을 포함한 생성 배열의 미승격 후보 수다.
- [v191 통합 오프라인·원본 검증 Actions #41016126265](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41016126265) **단위 5 PASS/0 FAIL, 실제 3종 SimC 원본+기존 v190 영수증·제품 DB 결합 SUCCESS, Native 0**. 결과 [artifact #12959876351](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41016126265/artifacts/12959876351), 보존기간 7일. 결과 JSON은 `automatic_ui_promotion=false`.

## 완료·미구현을 구분하는 기준

| 작업 | 완료 |
|---|---|
| SimC/DB2의 실제 출처 파일·SHA·빌드 연결, 기존 대표 장비/티어 카탈로그 일괄 집계 | **v191 구현+실행 PASS** |
| 생성된 영구·임시 마부 ID/품질/적용 비트마스크 추출·최고 rank 후보 추림 | **v191 구현+실행 PASS** |
| 음식·물약 실제 아이템 ID 후보 및 원본 이름 수집 | **v190 구현+실행 PASS**, SimC 인식은 미확정 |
| 장식 전체 SimC 등록 발견 | **v189 구현+실행 PASS**, 실제 적용 부위별 원본 연결 미완 |
| 모든 음식·물약·보석·영약·증강룬·장식의 **동일 효과 판정과 최고 실제 효과 품질** | **미구현. 실제 DBC item/effect joins 필요** |
| '현재 시즌에만' 쓰이는 마부·장식·소비재와 과거 확장팩 기록의 정확한 선별 | **미구현. 시즌 source link 필요** |
| 게임별 한국어 명칭/tooltip과 부위별 사용자 선택 UI 자동 생성 | **미구현** |
| 새 선택 품목의 정적 G/B/L/O/J 중복 검증, 최소 Native 실수용·캐시 identity 적용 | **미구현. 제품 적용 전 표적 확인 필요** |

## 실제 사용 호출

기존 **요청형** workflow `v189` → `v190` (이미 확보한 영수증/동일 빌드 CSV 재사용) → `v191`로 실행한다.

```bash
python runner/v191_unified_season_data_update.py \
  --gear data/current_season_product_gear_db.json \
  --tier data/current_season_tier_itemsets.json \
  --budget data/current_season_chmv_consumables.json \
  --v189 out/v189_source_handler_candidates.json \
  --v190 out/v190_source_first_food_potion_item_candidates.json \
  --simc-generated-folder out/pinned-simc-generated \
  --event mid_patch --out out/unified_season_candidates.json
```

**버전 변경 때는 정확히 대응하는 신규 source artifacts로 바꾸고 요청 실행**한다. 현재 `v191` Actions의 디폴트는 *이미 고정된 기존 2026-10-30 출처*를 읽는 역사/기준 검증이다. `season_change`/ `expansion_change`라고 선택하는 것만으로 신규 시즌 DB를 확보하지 않는다. 대형 CSV/SimC 바이너리를 제품 저장소에 보관하지 않으며 실측 이전 DPS 영수증은 불변.

**다음 최소 작업:** 연결 데이터 기준으로 새 시즌 사용 가능한 실제 아이템 등급·효과 ID·부위를 완성하고, 비교 가능한 같은 효과만 최고 품질로 줄인다. 이 확인으로 만들어진 하나의 버전된 배포 카탈로그를 UI `/api/v1/options`와 기존 대표 장비 빌더에 바인딩한다. 바뀐 부분만 표적 Native로 수용 확인하며 새 최적화 엔진을 만들지 않는다.
