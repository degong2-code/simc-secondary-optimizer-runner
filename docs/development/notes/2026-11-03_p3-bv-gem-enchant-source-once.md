# 2026-11-03 · P3-BV · 보석 J의 실제 정적 효과점 원본만 최소 보완

- **Capability:** `J.GEM`, `BUDGET.GJFO`, `PRODUCT.E2E`
- **Keywords:** J, gem, GemProperties, enchant_id, SpellItemEnchantment, 효과점, quality, highest, v221, v161, v216
- **Prior evidence:** [P3-BH](../../P3_BH_20261103_FRESH_SEASON_GEM_SOURCE_JOIN_IN_NORMAL_BUILD.md) 기존 `v221` 동일빌드 GemProperties→ItemSparse 물리 보석·enchant_id 연결, [P3-BT](2026-11-03_p3-bt-normal-build-standard-budget-link.md) v216 기존 v222 B/T 통합, [P3-BO](../../P3_BO_20261103_PINNED_SIMC_V189_WAGO_V190_CONSUMABLE_STAGE.md) 기존 v189/v190는 **음식·물약 후보**, 영약 F/기름 O의 정적 수치 원본이 아님.
- **Decision:** `EXTEND` — J에서 실제 누락된 것은 보석 마부 ID의 정적 보조능력치 효과점이다. 기존 Wago 10표 전체를 다시 수집하지 않고 **같은 빌드 SpellItemEnchantment 원본 한 표만 별도 v217 캐시**하여 `v221`의 정확한 enchant_id와 합친다. SimC 원본 enum crit32/haste36/vers40/mastery49와 직접 비교하고, 정적 순수 효과와 스케일링·복합 효과를 구분한다. 효과점 후보를 최고 품질 J·유저 등록/READY로 자동 승격하지 않는다.
- **Changes:** 새 경량 원본 parser `v266`, 기존 `v216`의 시즌 source 경로에서 선택형 1회 다운로드/원본 봉인과 `v221` 로컬 증거 연결, 합성 회귀 및 INDEX/CURRENT 갱신. 기존 `v161` 10표 receipt/캐시는 수정하지 않고 추가 표만 독립 캐시.
- **Verification:** 신규 CI 실제 PASS/FAIL `NOT_VERIFIED`; 이전 v221/SimC 등 확인 내용은 범위 내 `REUSED_HISTORY`. 신규 원격 호출/Native는 이 개발 채팅에서 실행하지 않는다.
- **Remaining:** 각 정적 효과점의 실제 SimC 적용 수치·최고 제작 품질 효과 비교·유효 소켓/정확 J 합산은 여전히 확인해야 함. F 영약/O 기름의 정확한 수치도 별도 기존 정적 SimC/DB2 경로에서 확인 필요. 불명확하면 해당 선택지만 보류하고 기본 환경을 임의 숫자로 채우지 않는다.
- **Efficiency:** 기존 10개 Wago 표/SimC 파일·v221 source join 재사용, 보완 원본 1개만 해시·봉인·캐시; Native0, 26특성/79ilvl 전수 반복0. 실제 실행시간·I/O 개선 미측정.
