# v037 — 수동 CHMV 총량·후보 최소치 Native Pilot

**상태:** 사용자 승인 범위의 일반 제품 시험 전용. 공식 M0 / Project Sources / Developer Notes / CURRENT / Shared State 변경 또는 승격 아님.

## 목적과 한계

- v032 원본 17개 모듈과 v036 실측 근거를 보존하면서, 기존에 `3184`로 고정됐던 **탐색 후보의 CHMV 총량을 별도 수동 설정값으로 바꾸어** Native SimC 검증한다.
- 예시 **3284 rating**은 `v031R3` 비전 마법사·드워프·기존 고정 장비 시나리오에 대해 `+100`을 지정한 *시험용 수동 총량*이다. 이 수치를 새로운 목표 아이템레벨의 실제 장비 예산 또는 표준화 장비 총량으로 주장하지 않는다.
- 최소치 `치명 600 / 가속 200 / 특화 100 / 유연 100`은 **사용자 지정 후보 허용 구역**이다. 특수효과 장비의 실제 고정 벡터를 자동 추출·보증한 것은 아니며, 특수효과 장비·장신구 스탯 정책은 이전 승인을 유지한다.
- 기존 **기름 +16 치명/+16 가속**의 하한, 원본의 **스탯별 50% 상한** 및 영약 **총량 165**을 보존한다. 룬은 치명타 하나로 고정하며 장비·4세트·장신구·장식·APL·300초 Patchwerk 시나리오를 변경하지 않는다.
- 6개 탐색(5개 고유 초기값 + 기존 v032 선형 회귀 기반 유도 1개), 2개 정밀 독립 재시험. `scout_iterations=120`, `confirm_iterations=320`, 한 요청당 Native 호출 **최대 8회**. 탐색 후보는 동일 `(CHMV, iterations)` 조합을 중복 호출하지 않는다. 고의적인 320-iteration 독립 재시험은 120-iteration 초기 탐색과 중복으로 취급하지 않는다.
- `v032` 탐색 핵심 함수 `native_source`, `make_profile`, `choose_guided`, `confirm_seeds`, `run_case`를 원본 바이트 그대로 호출한다. v037은 별도 요청 검증·예산 투영·하한 처리·중복 검출·완료 영수증을 소유한다. **일반화된 제품 입력이나 전 전문화 성능 지원은 미검증.**

## 안전한 실행 계약

`runner/v037_request.json`은 검증용 고정 시험 요청이다. 운영 중에는 같은 스키마로 명시적 사용자가 요청한 시나리오만 지원 범위를 넓혀야 한다.

- `scenario`: `v031r3_dwarf_arcane_fixed_gear`
- `budget_origin`: `MANUAL_TEST_TOTAL_NOT_ITEM_LEVEL_PROVEN`
- `target_total_rating`: `3284`
- `minimum_target_rating`: `{crit_rating:600, haste_rating:200, mastery_rating:100, versatility_rating:100}`
- `omnium_rune`: `crit`
- Native 상한: `8` (`6 × 120` + `2 × 320`)

불가능한 하한, 초과 총량, 알 수 없는 장비/전문화/룬, 다른 반복 횟수, 잘못된 스키마, 잘못된 SimC 바이너리 SHA는 즉시 BLOCKED. 결과에 *실제 적용 CHMV*와 요청 목표, 선택 룬 버프, DPS·SEM·근사 CI, 후보 rating 거리를 기록한다. **평균의 95% 근사 CI가 겹친다는 이유만으로 두 후보가 완전히 동등하다고 단정하지 않는다.** 최적해/수렴/전문화 일반화는 보증하지 않는다.

## 증거 분리

1. v032 원본 ZIP 독립검사(Manifest `191/191`, 오프라인 테스트 `429/429`) = 역사적 원본 검증.
2. v036 기존 `3184` 고정 시나리오 실제 탐색 성공 = 원본 엔진 Linux Native 검증.
3. v037 `3284` **수동 총량** 오프라인 29개 검사 및 별도 Linux Native 검증 = v037에서만 확인 가능한 신규 범위.
4. GitHub `actions/cache/restore@v4`는 바이너리 캐시이므로 **동일 Native DPS 결과 재사용을 의미하지 않는다.** v035 시험 브랜치에 한정된 cache key 재사용은 사전에 HIT와 SHA를 검증해야 한다.

GitHub의 `main`·기존 v003 immutable·공식 Work OS M0는 변경하지 않는다. 이 시험은 범용 UI/설치형 제품을 구현한 것으로 표시하지 않는다.
