# v550 — 사용자 승인 보석 선택 및 SimC/Wago ItemID 자동 발견 경로 검토

**2026-11-17 · 격리 브랜치 `probe/chat-cache-v035-20261024` · code `b1a948b6b149a44b1bbe6b3e56127650cee6576a`**

## 최신 사용자 직접 결정

- 대표 스탯 **C/H/M/V**가 같은 다중스탯 보석은 partner secondary가 C-H/C-M/C-V 등으로 달라도 모두 같은 대표 종류 후보. 최고 **제작품질(crafting_quality)** → 해당 보석의 두 secondary 합계 내림차순 → **작은 ItemID** 순으로 기본 한 종류를 선택한다.
- C/H/M/V 대표 일반 다중스탯 보석을 각 하나씩 쓰고, 사용자가 총 소켓을 4개 초과 선택하면 `C→H→M→V` 순으로 반복. 특수 보석은 별도 슬롯을 차지하고 **J 합산에 포함하지 않음**. `v271.ordinary_four_stat_default`, `v271.arrange`, `v271.reconcile_observed_J`가 기존에 지원.
- 일반/특수 분류: Primary Stat 포함은 특수, secondary-only는 일반, 1종 secondary-only 제외, 정확히 2종 secondary 상승일 때 일반 다중스탯 후보. 두 값이 동률인 경우 대표 스탯은 별도 사용자 결정 전 PENDING. 특수 효과는 SimC에 맡김.

## 실제 원본에서 ItemID를 어디서 찾을 수 있나

1. **Wago DB2 이미 구현됨:** `v161`의 동일 빌드 `Item.csv`와 `ItemSparse.csv`에서 `Item.ClassID=3 (Gem)`인 실제 아이템 ItemID를 얻고, `ItemSparse.Gem_properties`를 `v191` SimC `gem_data.inc`의 GemProperty ID와 조인함. `ItemSparse.ExpansionID`를 기준으로 시즌/확장팩 후보까지 좁히는 `v221.join`이 존재. 현재까지 역사 70783 원본 **75개 물리 보석 후보** 확인. 현장 75개 자체는 사용자 승인 C/H/M/V 4종이 아니라 소스 ID 후보.
2. **SimC 자체에서 ItemID를 읽는 경로가 실제로 존재함:** 공식 `simulationcraft/simc` `midnight`의 `engine/dbc/item_data.hpp`에서 `dbc_item_data_t`에 `id`, `item_class`, **`gem_properties`**, `quality`, `crafting_quality` 필드가 있음을 확인. 실제 생성 파일은 `engine/dbc/generated/item_data.inc`이며, 기존 `v230.parse_exact`도 동일 포맷(28필드)을 한 번 스트리밍하며 **전체 행 candidate_filter 모드**를 지원. `gem_properties`는 생성 C++ 필드 index 22(0-base), `item_class`는 index 11. 그러므로 **기존 한 번의 파싱으로 SimC의 Gem 클래스 ItemID+GemProperty+품질을 직접 발견할 수 있는 소스 경로**가 있음.
3. **하지만 SimC 단독의 '이번 시즌' 경계는 별개:** `v230` 결과에는 현재 `gem_properties` index22를 아직 투영하지 않고 있고, SimC generated item_data의 이 스키마에는 Wago `ItemSparse.ExpansionID` 필드가 없다. 이 때문에 **SimC-only ItemID 추출이 가능해 보여도** 전체 옛 시즌 Gem IDs를 자동으로 이번 시즌으로 판단하면 안 된다. Wago `ExpansionID`가 있는 기존 v221이 현재 가장 정확하고 저비용인 신규 시즌 경로이며, SimC ID 직접 추출은 동일 빌드 교차 대조 또는 Wago가 없는 경우 선택 대안으로 검토.
4. `v191` `gem_data.inc` 자체는 `GemPropertyID → EnchantID/ColorMask/MinimumIlevel` 정보이고, 물리 ItemID 자체가 없다. 이 파일 하나만으로 ID를 만들어내지 말 것. `v230`의 item_data 품질, `v275/v296`의 enchant 정적 rating 및 필요한 경우 기존 `v269/v278` Native를 동일 시즌 ItemID에 결합하면 됨.
5. `v221` Wago 원본 수집 이후 ItemID 발견 자체는 새 기능이 아니다. 과거의 **근본 결손은 발견된 다수 ID를 `Primary vs Secondary`, 1 vs 2 secondary, C/H/M/V main, 최고 품질+J tie-break로 정리해서 기존 공식 J owner까지 전달하지 못한 부분**이다.

## 이번 실제 코드 및 테스트

- `v216._fresh_pinned_dbc_ordinary_gem_j_source`의 대표스탯별 **정확히 1개 효과군** 제한을 제거. 2 secondary가 검증된 후보를 대표 C/H/M/V 네 분류에 나누고, 동일 대표스탯의 C-H/C-M/C-V 조합을 모두 수용. 기존 `v296` 순수 정적 secondary 효과 검출 그대로 사용하고 Primary/1 secondary/동률/스케일링은 승인 없이 PENDING/제외.
- 각 대표스탯 안에서 `crafting_quality DESC, sum(two secondary) DESC, item_id ASC` 선택; 동일 효과·사용 조건 그룹 내 열등한 높은 품질 수치는 기존 보류 유지. **실 시즌 확정/공식 J 승인은 여전히 기존 소유권 계약에 따라 별개.**
- 회귀: `tests/test_v216_environment_build_coordinator.py::test_v549_reuse_original_v296_dbc_for_static_four_stat_j`에 동일 C 대표 + 다른 partner, 합계 큰 값 선택(23→24), 동점 시 작은 ItemID(330003) 검증 추가. [v212 Windows·Ubuntu #44024180899](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44024180899) 각 **500 tests·496 PASS/4 SKIP/0 FAIL**, [집중 오프라인 #44024180915](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44024180915) **679 tests·677 PASS/2 SKIP/0 FAIL**. **신규 실제 Native / Wago 다운로드 0회**, 합성 회귀 결과이지 실 시즌 자동 ItemID 선별 완료/실 J 승인 아님.
- `v548._fresh_four_stat_simc_observed_j_preview`가 **효과군 수 정확히 4개**를 요구하는 기존 Native fallback 불일치는 그대로 남음. 이것은 Primary/2 secondary 대표 보석 선택 기준과 다른 잘못된 제한으로, 다음 국소 교정 대상. N개 J 소비·소켓 기능은 이미 구현돼 있으므로 중복 개발하지 않음.

## 다음 최단 작업

1. 신규 시즌 `v221` ID 목록은 이미 존재하므로, 정상 Build에서 원본 `v275/v296` 또는 필요시 `v269/v278`로 **그 ID들의 실제 secondary vector**를 추출해 C/H/M/V 4종으로 분류하고 최신 승격 정책만 연결.
2. SimC 단독 원본을 시도할 필요가 있으면 **기존 v230 candidate_filter**에서 `item_class=3 && gem_properties>0`만 읽고 index22 투영한 선택 자료를 **동일 Wago 시즌 소속 / 동일 SimC 빌드와 대조**. 계절성이 없는 전체 SimC Gem DB를 '이번 시즌'이라고 과장하지 않음.
3. 75개 전수 Native 금지; 인증된 정적 원본 범위와 최대 4종 선정이 성공하면 추가 Native0로 기존 `v271 J → v216 original J owner → v222 B/T → v212` 연결. 새로운 독립 검증 Gate·보석 효과 재구현·캐시 초기화 없이 수행.
4. 공식 78 계약 **15/78 COMPLETE / full_product_e2e=PENDING**, 기존 제품 주 개발 채팅 소유·격리 브랜치 권한 유지.

**원본:** [SimulationCraft item_data.hpp](https://github.com/simulationcraft/simc/blob/midnight/engine/dbc/item_data.hpp) · [SimC gem_data.inc](https://github.com/simulationcraft/simc/blob/midnight/engine/dbc/generated/gem_data.inc). 실제 소스 파일을 읽어 구조를 확인했지만 신규 시즌 물리 보석 ItemID 목록 4종을 새로 실 수집했다고 주장하지 않는다.
