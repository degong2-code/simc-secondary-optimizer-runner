# 핵심 코드 → 기능 → 테스트 대응 지도

> [START_HERE](START_HERE.md) · [INDEX](INDEX.md). 아래는 **기본 진입점**이며 전수 파일 목록은 [FILE_INVENTORY](FILE_INVENTORY.md). 테스트 링크는 실행/PASS를 입증하지 않는다. 각 소스의 실제 호출·영수증은 별도 확인한다.

## 책임 흐름 (개념적, 함수 단위 trace 아님)

`웹 사용자 입력 v113 → 시즌 source/Build v216·v217 → B/T v222 → 설치 v212 → 프로필 v098·v139 → SimC v096·v094 → 탐색 v290·v291 → 캐시·재개 v292·v293 → 웹 UI`

| 기능 | 소스 파일 | 용도 | 같은 이름/기존 연관 테스트 검색 진입 |
|---|---|---|---|
| A | [v161_wago_db2_snapshot.py](../../runner/v161_wago_db2_snapshot.py) | 시즌 DB2 원본 | [테스트 전체](FILE_INVENTORY.md) |
| A | [v229_simc_only_source_seed.py](../../runner/v229_simc_only_source_seed.py) | SimC source identity | [테스트 전체](FILE_INVENTORY.md) |
| A | [v191_unified_season_data_update.py](../../runner/v191_unified_season_data_update.py) | 시즌 원본→후보 | [test_v191_unified_season_data_update.py](../../tests/test_v191_unified_season_data_update.py) |
| A | [v213_source_to_catalog.py](../../runner/v213_source_to_catalog.py) | 원본·선택지 조인 | [test_v213_source_to_catalog.py](../../tests/test_v213_source_to_catalog.py) |
| A | [v217_stage_execution_engine.py](../../runner/v217_stage_execution_engine.py) | 봉인·재개·SHA | [test_v217_stage_execution_engine.py](../../tests/test_v217_stage_execution_engine.py) |
| B | [v167_product_season_gear_adapter.py](../../runner/v167_product_season_gear_adapter.py) | 대표 장비 | [test_v167_product_season_gear_adapter.py](../../tests/test_v167_product_season_gear_adapter.py) |
| B | [v230_simc_item_metadata.py](../../runner/v230_simc_item_metadata.py) | ItemData 파싱 | [test_v230_simc_item_metadata.py](../../tests/test_v230_simc_item_metadata.py) |
| B | [v232_simc_only_ordinary_representative.py](../../runner/v232_simc_only_ordinary_representative.py) | 일반 대표 장비·소켓 | [test_v232_simc_only_ordinary_representative.py](../../tests/test_v232_simc_only_ordinary_representative.py) |
| B | [v251_db2_raid_tier_simc_bridge.py](../../runner/v251_db2_raid_tier_simc_bridge.py) | 티어 물리/SimC 조인 | [test_v251_db2_raid_tier_simc_bridge.py](../../tests/test_v251_db2_raid_tier_simc_bridge.py) |
| B | [v277_zero_history_native_G_stage.py](../../runner/v277_zero_history_native_G_stage.py) | 선택적 정확 G Native | [test_v277_zero_history_native_G_stage.py](../../tests/test_v277_zero_history_native_G_stage.py) |
| C | [v221_gem_item_db2_relation.py](../../runner/v221_gem_item_db2_relation.py) | 보석 물리 소스 | [test_v221_gem_item_db2_relation.py](../../tests/test_v221_gem_item_db2_relation.py) |
| C | [v266_gem_enchant_raw_stat_source.py](../../runner/v266_gem_enchant_raw_stat_source.py) | J 명목 스탯 | [테스트 전체](FILE_INVENTORY.md) |
| C | [v271_user_socket_gem_layout.py](../../runner/v271_user_socket_gem_layout.py) | 소켓/보석 배치 | [test_v271_user_socket_gem_layout.py](../../tests/test_v271_user_socket_gem_layout.py) |
| D | [v281_consumable_simc_relation.py](../../runner/v281_consumable_simc_relation.py) | 영약 F 아이템/SimC | [test_v281_consumable_simc_relation.py](../../tests/test_v281_consumable_simc_relation.py) |
| D | [v278_sealed_simc_consumable_native_pair.py](../../runner/v278_sealed_simc_consumable_native_pair.py) | 영약 Native 실측 | [test_v278_sealed_simc_consumable_native_pair.py](../../tests/test_v278_sealed_simc_consumable_native_pair.py) |
| D | [v285_consumable_weapon_source.py](../../runner/v285_consumable_weapon_source.py) | 무기 기름 대상 | [test_v285_consumable_weapon_source.py](../../tests/test_v285_consumable_weapon_source.py) |
| D | [v286_representative_oil_source_binding.py](../../runner/v286_representative_oil_source_binding.py) | O 손별 대응 | [test_v286_representative_oil_source_binding.py](../../tests/test_v286_representative_oil_source_binding.py) |
| D | [v295_season_runeforge_source.py](../../runner/v295_season_runeforge_source.py) | DK 룬 소스 | [test_v295_season_runeforge_source.py](../../tests/test_v295_season_runeforge_source.py) |
| D | [v296_pinned_oil_static_rating_source.py](../../runner/v296_pinned_oil_static_rating_source.py) | 기름 정적 rating | [test_v296_pinned_oil_static_rating_source.py](../../tests/test_v296_pinned_oil_static_rating_source.py) |
| E | [v222_season_budget_contract.py](../../runner/v222_season_budget_contract.py) | GJFO·B/T 공식 회계 | [test_v222_season_budget_contract.py](../../tests/test_v222_season_budget_contract.py) |
| E | [v220_catalog_auto_admission.py](../../runner/v220_catalog_auto_admission.py) | 정책 A 등록 | [test_v220_catalog_auto_admission.py](../../tests/test_v220_catalog_auto_admission.py) |
| E | [v196_current_season_user_catalog.py](../../runner/v196_current_season_user_catalog.py) | 검증된 선택지 | [테스트 전체](FILE_INVENTORY.md) |
| E | [v212_environment_manifest.py](../../runner/v212_environment_manifest.py) | 환경 설치/READY | [test_v212_environment_manifest.py](../../tests/test_v212_environment_manifest.py) |
| E | [v216_environment_build_coordinator.py](../../runner/v216_environment_build_coordinator.py) | 시즌 Build 조정 | [test_v216_environment_build_coordinator.py](../../tests/test_v216_environment_build_coordinator.py) |
| F | [v143_specialization_contracts.py](../../runner/v143_specialization_contracts.py) | 26 DPS 계약 | [테스트 전체](FILE_INVENTORY.md) |
| F | [v139_pure_target_profile_composer.py](../../runner/v139_pure_target_profile_composer.py) | SimC 프로필 | [test_v139_pure_target_profile_composer.py](../../tests/test_v139_pure_target_profile_composer.py) |
| F | [v098_target_user_scenario_bootstrap.py](../../runner/v098_target_user_scenario_bootstrap.py) | 사용자 시나리오 | [test_v098_target_user_scenario_bootstrap.py](../../tests/test_v098_target_user_scenario_bootstrap.py) |
| F | [v096_unified_product_entry.py](../../runner/v096_unified_product_entry.py) | SimC 제품 진입 | [test_v096_unified_product_entry.py](../../tests/test_v096_unified_product_entry.py) |
| F | [v094_durable_inclusive_adaptive_runner.py](../../runner/v094_durable_inclusive_adaptive_runner.py) | 기존 Native 평가 | [test_v094_durable_inclusive_adaptive_runner.py](../../tests/test_v094_durable_inclusive_adaptive_runner.py) |
| F | [v290_multiscale_adaptive_policy.py](../../runner/v290_multiscale_adaptive_policy.py) | 기본 안정 정책: B 비율 다중해상도/경계 clipping. 기본 결과 정책은 무변경 | [test_p3_hw_multiscale_policy.py](../../tests/test_p3_hw_multiscale_policy.py) |
| F | [v298_adaptive_percent_grid.py](../../runner/v298_adaptive_percent_grid.py) | 기존 선택형 백분율 grid·bounded 비례 배분·정수화·중복; **기존 source SHA 보존/기본 미승격** | [test_v298_adaptive_percent_grid.py](../../tests/test_v298_adaptive_percent_grid.py) |
| F | [v300_multiregion_throughput_resolution.py](../../runner/v300_multiregion_throughput_resolution.py) | 신규 v299 전용 실측 NEW_NATIVE scout·confirm iterations·wall-time 기반 11→22/31/41 해상도 | [test_v300_multiregion_throughput_resolution.py](../../tests/test_v300_multiregion_throughput_resolution.py) |
| F | [v299_multiregion_percent_policy.py](../../runner/v299_multiregion_percent_policy.py) | 선택형 역사 다중영역 후보 정책: 초기 전역 분산 → 복수 유망 영역과 대각선 비율 이동 | [test_v299_multiregion_percent_policy.py](../../tests/test_v299_multiregion_percent_policy.py) |
| F | [v301_nested_multiregion_policy.py](../../runner/v301_nested_multiregion_policy.py) | **신규 선택형** 정확 최종 정수 CHMV 중첩 m6⊂m11⊂m21⊂m41 + 원래 v299 지역 정책; 실 Native100에서 기본 v290 우세, 자동 승격 보류 | [test_v301_nested_multiregion_policy.py](../../tests/test_v301_nested_multiregion_policy.py) |
| F | [v302_weak_multiregion_zoom.py](../../runner/v302_weak_multiregion_zoom.py) | **선택형 pure geometry/selector**: 4방향 exact-residual m11/21/41, loose 3%+SEM shortlist, 최대8 영역, local m6·radius 후보 생성; v291/제품 실행기·웹 미연결, GP 의존성 없음 | [test_v302_weak_multiregion_zoom.py](../../tests/test_v302_weak_multiregion_zoom.py) |
| F | [p2_nested_real_simc_timing_once.py](../../integration_probes/p2_nested_real_simc_timing_once.py) | historical 70783 Enhancement 프로필·exact binary/receipt 재사용한 실제 SimC 100 Native 속도·발견 비교, 최초 일회성 | [실험 결과 노트](notes/2026-11-10_p2-real-simc-nested-11-21-48case-comparison.md) |
| F | [v291_durable_multiscale_native_runner.py](../../runner/v291_durable_multiscale_native_runner.py) | 영속 Native/95%; 별도 percentage grid·multi-region·nested11/21 opt-in, 실제 NEW_NATIVE wall-time과 각 코드 SHA 봉인/레거시 세션 유지 | [test_p3_hx_durable_longrun_offline.py](../../tests/test_p3_hx_durable_longrun_offline.py) |
| F | [v292_portable_native_case_cache.py](../../runner/v292_portable_native_case_cache.py) | cross-job case 캐시 | [test_p3_hag_portable_native_case_cache.py](../../tests/test_p3_hag_portable_native_case_cache.py) |
| F | [v293_local_longrun_session.py](../../runner/v293_local_longrun_session.py) | 취소/재개 장기 세션 | [test_p3_hah_local_longrun_product_offline.py](../../tests/test_p3_hah_local_longrun_product_offline.py) |
| F | [v113_local_web_api.py](../../runner/v113_local_web_api.py) | 로컬 웹 API | [test_v113_local_web_api_offline.py](../../tests/test_v113_local_web_api_offline.py) |
| F | [v106_user_session_controller.py](../../runner/v106_user_session_controller.py) | 사용자 세션 | [test_v106_user_session_controller.py](../../tests/test_v106_user_session_controller.py) |
| G | [v289_retail_live_build_source.py](../../runner/v289_retail_live_build_source.py) | 현재 게임 build | [test_v289_retail_live_build_source.py](../../tests/test_v289_retail_live_build_source.py) |

## 구현 근거·역사 결정의 역방향 검색

- 환경: [승인 v1.4.3](../SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) · [실 무이력 Build](notes/2026-11-10_p1-four-ordinary-real-zero-history-ready.md) · [일반 4보석 변경](notes/2026-11-10_p1-ordinary-only-default-engine-bridge.md) · [프로필 보석 SHA 재사용](notes/2026-11-10_p1-gem-variant-install-reuse-identity.md).
- P2: [실 SimC **전역21·지역6/GP** 관측](notes/2026-11-10_p2-real-simc-global21-local6-gp-comparison.md) · [기존 실제 SimC100·중첩11/21 비교](notes/2026-11-10_p2-real-simc-nested-11-21-48case-comparison.md) · [정확 중첩 설계/코드](notes/2026-11-10_p2-nested11-21-41-real-simc-pilot.md) · [역사 적응형22점·복수영역 시험](notes/2026-11-10_p2-multiregion-throughput22-opt-in.md) · [선택형 격자 실험 구현](notes/2026-11-10_p2-percentage-grid-opt-in-engine.md) · [최신 승인 적응형 격자·비례 정규화 설계](notes/2026-11-10_p2-percentage-grid-proportional-normalization.md) · [사용자 지정 60% 기본 상한](notes/2026-11-10_p2-user-configurable-final-stat-cap-and-grid-study.md) · [비율 경계 적응형 후보 변경](notes/2026-11-10_p2-fractional-bounded-neighbor-proposals.md) · [신뢰성·알고리즘 비고정](notes/2026-11-09_p2-opt-reliability-first-open-search-policy.md) · [실 Native10 한계](notes/2026-11-09_p2-real-native-ten-case-region-audit.md) · [합성 다봉형](notes/2026-11-09_p2-multimodal-equal-count-offline-audit.md).
- 작업 시 source의 해당 함수와 실제 test import를 확인한다. **유사한 이름의 테스트를 자동으로 진짜 관련 테스트나 PASS로 간주하지 않는다.**
