# P1 v679 — 음식·물약 실제 SimC 적용 상태 가시화, 미승인 자동 사용 방지

2026-11-23 KST · 격리 브랜치 `probe/chat-cache-v035-20261024` · 현재 사용자 PC 시험 보류 결정 유지.

## 제품 흐름과 실제 장애

사용자 음식·물약 선택 → 현재 시즌 검증 선택지 → 내부 대표 프로필의 `food=`/`potion=` → 실제 SimC DPS/SEM/95% 결과. 
원래 사용자 요청은 음식·물약을 실제 사용하도록 하고, 동일 효과·조건일 때 최고 품질만 노출하는 것.

현재 `v113.options()`는 신규 시즌 `current_season_product_choices.food/potion=["source_default"]`만 사용자에게 승인한다. `v218._verified_fresh_season_consumables`는 `source_default`를 실제 SimC `disabled`로 변환한다. UI는 예전부터 기본값을 `미사용 (이번 시즌 기본)`으로 표시했지만, 그로 인해 **실제 DPS에서 해당 효과가 빠진다는 것**을 선택칸 및 최종 계산 확인 단계에서 충분히 확인하기 어려웠다.

## 확인한 재사용 가능 원본, 그리고 한계

- 기존 `v108`, `v098._season_settings_from_v216`, `v218`은 **정확한 SimC 토큰을 현재 실행 프로필에 전달할 수 있는 엔진**을 이미 보유한다. 새 소모품 효과 엔진은 불필요.
- [P3-HU 실제 Native 영수증](2026-11-08_p3-hu-applicable-full-consumables-no-enchants.md)은 한 고양 주술사 조건에서 `food=harandar_celebration`, `potion=potion_of_recklessness_2`, `augmentation=void_touched`를 SimC 실행·JSON2에서 관측했다. 이것은 **그 시험의** 실제 사용 성공이다. 해당 항목 전체의 정확한 물리 ID/품질/동일 효과·조건 및 현재 설치 `70961`과의 정합을 자동 입증하지 않는다.
- `v484_exact_optional_consumable_source_join`은 기존 `v190/v217` 원본과 핀 고정 SimC `v230`의 선택 물리 ItemID·종류·제작품질 후보를 결합할 수 있지만 `source_only`, `policy_A_eligible=false`, `simc_token_native_verified=false`, `same_effect_quality_group_verified=false`, `use_conditions_verified=false`를 명시한다. 테스트는 합성 빌드 `70575`로 실제 `70961` 등록 근거 아님.
- 역사 `data/current_season_chmv_consumables.json`도 `12.1.5.70575` 예산 원본이므로 현재 `70961` 음식·물약 인증으로 승격 금지.
- 현재 정확한 시즌/빌드·효과·최고 품질·SimC token 등록이 없는 상태에서 기존 `source_default`를 과거 영문 토큰으로 교체하면 허위 사용자 선택지 및 부정확 DPS를 만든다.

## 최소 기능 변경

- `runner/webui/index.html`: 음식/물약 선택기 바로 아래 **실제 SimC 적용 상태**를 각각 표시하는 짧은 `role=status` 안내와 `aria-describedby` 연결. 승인 기존 UI 구성 유지.
- `runner/webui/app.js`: 기존 `current_season_product_choices`의 **정확한 서버 계약**에 따라 기본값이면 `SimC 미사용 · 현재 시즌 음식/물약 ID·품질 미등록` 표기. 과거 세션의 미승인 선택값은 `이번 시즌 신규 최적화에 적용 불가`, 소스 응답이 없으면 미확정. 이후 검증된 선택지가 생기더라도 UI 그 자체로 Native 적용/등록 완료를 인증하지 않는다.
- 같은 상태를 시작 확인창에 `음식·물약은 SimC 미사용, 해당 효과를 제외한 DPS 조건`으로 명시. **일반 BASE는 계속 사용 가능**. 사용자가 실제로 `disabled` 실행에 동의하기 전 경고를 받지만 계산을 자동 시작하거나 추가 확인 API를 호출하지 않는다.
- `runner/webui/styles.css`: 기존 폼 색상·글꼴에 맞춰 모바일에서 상태 줄바꿈만 보강. 불필요한 안내 박스·새 페이지·새 Gate 없음.
- `tests/test_v456_current_season_optional_consumable_ui_scope.py`: 실제 생산 JS 소스의 기본 미사용, 역사 세션, 누락 서버 원본, 향후 등록 표시 범위를 검사. 기존 `v113/v181` 오프라인 회귀에 연결. 기타 정적 UI/분리 클릭 핸들러 회귀 기대 문구를 실제 변경한 사용자 계약에 맞게 국소 유지.
- 원래 `v212/v216/v218` 시즌 G/J/F/O 회계, 임의 최고 품질 추정 금지, 원본 소모품 지원 범위, 세션/캐시 SHA, adaptive SimC/95%·장신구·Oil/L/E/O 처리 모두 불변.

## 현재 확인한 기능과 남은 정확한 경계

**실제 음식·물약 기본 사용 등록은 아직 미구현**이다. 이번 변경은 근거 부족으로 미등록된 선택의 **실제 SimC 미사용과 DPS 제외 조건을 일반 사용자에게 명확히 알리는 수정**이다. UI 표시 개선/오프라인 PASS를 음식·물약 DPS 활성화 또는 최고 품질 등록으로 승격하면 안 된다.

다음 **필요 충분한 제품 단위**: 사용자가 실제 선택할 현재 설치 빌드의 음식·물약 물리 ItemID/품질/동일 효과·사용 조건 및 SimC token을 기존 `v190/v217/v230/v484` 소스·이미 보존된 Native 영수증에서 가능한 만큼 재사용해 **선택한 항목만** 인정. 검증된 정확한 선택지를 기존 `v212/v218/v113` 경로에 연결한 뒤 기존 대표 프로필과 DPS 캐시·실제 SimC 입력의 일치를 최소 검증. 모든 192 음식/61 물약 원시 후보나 26전문화 무조건적 Native 전수를 요구하지 않는다. 기존 설치 `70961`과 실제 현재 KR Live 호환성 검증은 별도.

## QA / 비용 / 권한

- 아래 실제 CI 완료·PASS는 별도로 확인한다: `v113_local_web_api_offline`, `v181_windows_beta_packaging`, `v182_simple_user_input_ui`, `v180_multilevel_season_product`. 기존 사용자를 위한 v114/v568 테스트의 고정 UI 문구는 변경 후 사용자 의미대로 국소 갱신했다.
- 새 user PC 시험 0, 신규 SimC DPS/G/F Native 0, DB2/Wago 실수집 0, 새 외부 API 기능 0, 정적 캐시/세션 삭제 0. P3-HU Native는 역사 재사용.
- main/v003 불변/v016 원본/Project UI/Work OS/공식 78계약·주 제품 채팅 소유권 불변. `full_product_e2e=PENDING`; v677 PC 자동 T 확인은 사용자가 PC 가능한 때까지 보류.
