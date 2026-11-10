# 코드/테스트 전체 파일 인벤토리 — 2026-11-10 격리 SHA 스냅샷

> 스냅샷 기준 `1b59ec52af9658218e90fd5ce652d99cd1d304fc`. 실제 트리의 runner 최상위 파일 175개와 tests Python 237개를 전부 기재. 아래 연관 테스트는 **이름/버전명 후보**로만 표시하며 실제 import·완료·PASS 증거가 아니다. [핵심 FILE_MAP](FILE_MAP.md)과 [증거 지도](EVIDENCE_INDEX.md)를 함께 본다. 새 HEAD 파일은 실제 Git 트리로 다시 조회해야 한다. 2026-11-10 P2 v298–v303 추가 파일은 아래 delta 섹션에 보충하며, 위 역사 스냅샷 수량을 현재 전체 수량으로 해석하지 않는다.

## Runner 파일 전체

| 파일 | 테스트 후보 (이름 기준·최대 3) |
|---|---|
| [pilot.py](../../runner/pilot.py) | [test_pilot.py](../../tests/test_pilot.py) |
| [v037_manual_budget_adapter.py](../../runner/v037_manual_budget_adapter.py) | [test_v037_manual_budget_adapter.py](../../tests/test_v037_manual_budget_adapter.py) |
| [v037_request.json](../../runner/v037_request.json) | [test_v037_manual_budget_adapter.py](../../tests/test_v037_manual_budget_adapter.py) |
| [v038_fixed_gear_floor.py](../../runner/v038_fixed_gear_floor.py) | [test_v038_fixed_gear_floor.py](../../tests/test_v038_fixed_gear_floor.py) |
| [v038_native_floor_probe.py](../../runner/v038_native_floor_probe.py) | [test_v038_fixed_gear_floor.py](../../tests/test_v038_fixed_gear_floor.py) |
| [v039_tier_effect_probe.py](../../runner/v039_tier_effect_probe.py) | [test_v039_tier_effect_probe.py](../../tests/test_v039_tier_effect_probe.py) · [test_v039_venomkeeper_bare_probe.py](../../tests/test_v039_venomkeeper_bare_probe.py) |
| [v039_venomkeeper_bare_probe.py](../../runner/v039_venomkeeper_bare_probe.py) | [test_v039_venomkeeper_bare_probe.py](../../tests/test_v039_venomkeeper_bare_probe.py) · [test_v039_tier_effect_probe.py](../../tests/test_v039_tier_effect_probe.py) |
| [v040_catalyst_redirect_probe.py](../../runner/v040_catalyst_redirect_probe.py) | [test_v040_catalyst_redirect_probe.py](../../tests/test_v040_catalyst_redirect_probe.py) |
| [v041_catalyst_gem_proc_probe.py](../../runner/v041_catalyst_gem_proc_probe.py) | [test_v041_catalyst_gem_proc_probe.py](../../tests/test_v041_catalyst_gem_proc_probe.py) |
| [v042_catalyst_evidence_firewall.py](../../runner/v042_catalyst_evidence_firewall.py) | [test_v042_catalyst_evidence_firewall.py](../../tests/test_v042_catalyst_evidence_firewall.py) |
| [v043_spell_data_probe.py](../../runner/v043_spell_data_probe.py) | [test_v043_spell_data_probe.py](../../tests/test_v043_spell_data_probe.py) |
| [v044_static_budget_attribution.py](../../runner/v044_static_budget_attribution.py) | [test_v044_static_budget_attribution.py](../../tests/test_v044_static_budget_attribution.py) |
| [v045_native_budget_candidate.py](../../runner/v045_native_budget_candidate.py) | [test_v045_native_budget_candidate.py](../../tests/test_v045_native_budget_candidate.py) |
| [v046_static_item_cache.py](../../runner/v046_static_item_cache.py) | [test_v046_static_item_cache.py](../../tests/test_v046_static_item_cache.py) |
| [v047_full_scope_collector.py](../../runner/v047_full_scope_collector.py) | [test_v047_full_scope_collector.py](../../tests/test_v047_full_scope_collector.py) |
| [v048_class_compatible_probe.py](../../runner/v048_class_compatible_probe.py) | — |
| [v049_class_compatible_recovery.py](../../runner/v049_class_compatible_recovery.py) | [test_v049_class_compatible_recovery.py](../../tests/test_v049_class_compatible_recovery.py) |
| [v051_crafted_embellishment_bridge.py](../../runner/v051_crafted_embellishment_bridge.py) | [test_v051_crafted_embellishment_bridge.py](../../tests/test_v051_crafted_embellishment_bridge.py) |
| [v052_crafted_native_sample.py](../../runner/v052_crafted_native_sample.py) | — |
| [v055_simc_item_selection.py](../../runner/v055_simc_item_selection.py) | [test_v055_simc_item_selection.py](../../tests/test_v055_simc_item_selection.py) |
| [v056_selected_mindpiercer_native.py](../../runner/v056_selected_mindpiercer_native.py) | — |
| [v058_lazy_crafted_native.py](../../runner/v058_lazy_crafted_native.py) | [test_v058_lazy_crafted_native.py](../../tests/test_v058_lazy_crafted_native.py) |
| [v059_candidate_runner_bridge.py](../../runner/v059_candidate_runner_bridge.py) | [test_v059_candidate_runner_bridge.py](../../tests/test_v059_candidate_runner_bridge.py) |
| [v061_scenario_contract.py](../../runner/v061_scenario_contract.py) | [test_v061_scenario_contract.py](../../tests/test_v061_scenario_contract.py) |
| [v062_static_budget_bridge.py](../../runner/v062_static_budget_bridge.py) | [test_v062_static_budget_bridge.py](../../tests/test_v062_static_budget_bridge.py) |
| [v063_numeric_injection.py](../../runner/v063_numeric_injection.py) | [test_v063_numeric_injection.py](../../tests/test_v063_numeric_injection.py) |
| [v063_official_T_two_native.py](../../runner/v063_official_T_two_native.py) | [test_v063_numeric_injection.py](../../tests/test_v063_numeric_injection.py) |
| [v064_adaptive_evaluator_port.py](../../runner/v064_adaptive_evaluator_port.py) | [test_v064_adaptive_evaluator_port.py](../../tests/test_v064_adaptive_evaluator_port.py) |
| [v064_replay_v063_native.py](../../runner/v064_replay_v063_native.py) | [test_v064_adaptive_evaluator_port.py](../../tests/test_v064_adaptive_evaluator_port.py) |
| [v065_original_scheduler_native_bridge.py](../../runner/v065_original_scheduler_native_bridge.py) | [test_v065_native_pipeline_safety.py](../../tests/test_v065_native_pipeline_safety.py) · [test_v065_original_v015_search_adapter.py](../../tests/test_v065_original_v015_search_adapter.py) · [test_v065_v015_scheduler_adapter.py](../../tests/test_v065_v015_scheduler_adapter.py) |
| [v065_original_v015_search_adapter.py](../../runner/v065_original_v015_search_adapter.py) | [test_v065_original_v015_search_adapter.py](../../tests/test_v065_original_v015_search_adapter.py) · [test_v065_native_pipeline_safety.py](../../tests/test_v065_native_pipeline_safety.py) · [test_v065_v015_scheduler_adapter.py](../../tests/test_v065_v015_scheduler_adapter.py) |
| [v065_v015_guided_once.py](../../runner/v065_v015_guided_once.py) | [test_v065_native_pipeline_safety.py](../../tests/test_v065_native_pipeline_safety.py) · [test_v065_original_v015_search_adapter.py](../../tests/test_v065_original_v015_search_adapter.py) · [test_v065_v015_scheduler_adapter.py](../../tests/test_v065_v015_scheduler_adapter.py) |
| [v065_v015_scheduler_adapter.py](../../runner/v065_v015_scheduler_adapter.py) | [test_v065_v015_scheduler_adapter.py](../../tests/test_v065_v015_scheduler_adapter.py) · [test_v065_native_pipeline_safety.py](../../tests/test_v065_native_pipeline_safety.py) · [test_v065_original_v015_search_adapter.py](../../tests/test_v065_original_v015_search_adapter.py) |
| [v066_profile_neutral_preflight.py](../../runner/v066_profile_neutral_preflight.py) | [test_v066_profile_neutral_preflight.py](../../tests/test_v066_profile_neutral_preflight.py) |
| [v067_generic_adaptive_native_route.py](../../runner/v067_generic_adaptive_native_route.py) | [test_v067_generic_adaptive_native_route.py](../../tests/test_v067_generic_adaptive_native_route.py) |
| [v068_rogue_two_native_probe.py](../../runner/v068_rogue_two_native_probe.py) | [test_v068_rogue_user_profile.py](../../tests/test_v068_rogue_user_profile.py) |
| [v068_rogue_user_profile.py](../../runner/v068_rogue_user_profile.py) | [test_v068_rogue_user_profile.py](../../tests/test_v068_rogue_user_profile.py) |
| [v069_rogue_official_budget_native.py](../../runner/v069_rogue_official_budget_native.py) | [test_v069_official_rogue_budget.py](../../tests/test_v069_official_rogue_budget.py) |
| [v071_rogue_adaptive_first_scout.py](../../runner/v071_rogue_adaptive_first_scout.py) | [test_v071_rogue_adaptive_first_scout.py](../../tests/test_v071_rogue_adaptive_first_scout.py) |
| [v072_rogue_high_iteration_confirm.py](../../runner/v072_rogue_high_iteration_confirm.py) | [test_v072_rogue_high_iteration_confirm.py](../../tests/test_v072_rogue_high_iteration_confirm.py) |
| [v073_rogue_material_adaptive_scout.py](../../runner/v073_rogue_material_adaptive_scout.py) | [test_v073_rogue_material_adaptive_scout.py](../../tests/test_v073_rogue_material_adaptive_scout.py) |
| [v074_rogue_selected_D_high_confirmation.py](../../runner/v074_rogue_selected_D_high_confirmation.py) | [test_v074_rogue_selected_D_high_confirmation.py](../../tests/test_v074_rogue_selected_D_high_confirmation.py) |
| [v075_rogue_coarse_continuation.py](../../runner/v075_rogue_coarse_continuation.py) | [test_v075_rogue_coarse_continuation.py](../../tests/test_v075_rogue_coarse_continuation.py) |
| [v076_generic_dps_scope_audit.py](../../runner/v076_generic_dps_scope_audit.py) | [test_v076_generic_dps_scope_audit.py](../../tests/test_v076_generic_dps_scope_audit.py) |
| [v077_generic_profile_bootstrap_readiness.py](../../runner/v077_generic_profile_bootstrap_readiness.py) | [test_v077_generic_profile_bootstrap_readiness.py](../../tests/test_v077_generic_profile_bootstrap_readiness.py) |
| [v078_elemental_first_native.py](../../runner/v078_elemental_first_native.py) | [test_v078_elemental_first_native.py](../../tests/test_v078_elemental_first_native.py) |
| [v078b_elemental_official_generic_native.py](../../runner/v078b_elemental_official_generic_native.py) | [test_v078b_elemental_official_generic_native.py](../../tests/test_v078b_elemental_official_generic_native.py) |
| [v079_hunter_ranged_generic_native.py](../../runner/v079_hunter_ranged_generic_native.py) | [test_v079_hunter_ranged_generic_native.py](../../tests/test_v079_hunter_ranged_generic_native.py) |
| [v079b_hunter_empirical_affine_recovery.py](../../runner/v079b_hunter_empirical_affine_recovery.py) | [test_v079b_hunter_empirical_affine_recovery.py](../../tests/test_v079b_hunter_empirical_affine_recovery.py) |
| [v080_static_chmv_corrected_native.py](../../runner/v080_static_chmv_corrected_native.py) | [test_v080_static_chmv_corrected_native.py](../../tests/test_v080_static_chmv_corrected_native.py) |
| [v081_static_generic_scout_native.py](../../runner/v081_static_generic_scout_native.py) | [test_v081_static_generic_scout_native.py](../../tests/test_v081_static_generic_scout_native.py) |
| [v082_fury_plate_dual_twohand_native.py](../../runner/v082_fury_plate_dual_twohand_native.py) | [test_v082_fury_plate_dual_twohand_native.py](../../tests/test_v082_fury_plate_dual_twohand_native.py) |
| [v083_paladin_single_2h_native.py](../../runner/v083_paladin_single_2h_native.py) | [test_v083_paladin_single_2h_native.py](../../tests/test_v083_paladin_single_2h_native.py) |
| [v084_frost_cloth_1h_frill_native.py](../../runner/v084_frost_cloth_1h_frill_native.py) | [test_v084_frost_cloth_1h_frill_native.py](../../tests/test_v084_frost_cloth_1h_frill_native.py) |
| [v085_shaman_real_static_replay.py](../../runner/v085_shaman_real_static_replay.py) | [test_v085_shaman_real_static_replay.py](../../tests/test_v085_shaman_real_static_replay.py) |
| [v086_hunter_fixed_mail_representative.py](../../runner/v086_hunter_fixed_mail_representative.py) | [test_v086_hunter_fixed_mail_representative.py](../../tests/test_v086_hunter_fixed_mail_representative.py) |
| [v089_ilvl_chmv_budget_selector.py](../../runner/v089_ilvl_chmv_budget_selector.py) | [test_v089_ilvl_chmv_budget_selector.py](../../tests/test_v089_ilvl_chmv_budget_selector.py) |
| [v090_reference_total_native_candidate.py](../../runner/v090_reference_total_native_candidate.py) | [test_v090_reference_total_native_candidate.py](../../tests/test_v090_reference_total_native_candidate.py) |
| [v091_weapon_oil_external_adapter.py](../../runner/v091_weapon_oil_external_adapter.py) | [test_v091_weapon_oil_external_adapter.py](../../tests/test_v091_weapon_oil_external_adapter.py) |
| [v092_approved_inclusive_CHMV_policy.py](../../runner/v092_approved_inclusive_CHMV_policy.py) | [test_v092_approved_inclusive_CHMV_policy.py](../../tests/test_v092_approved_inclusive_CHMV_policy.py) |
| [v093_inclusive_adaptive_scheduler_bridge.py](../../runner/v093_inclusive_adaptive_scheduler_bridge.py) | [test_v093_inclusive_adaptive_scheduler_bridge.py](../../tests/test_v093_inclusive_adaptive_scheduler_bridge.py) |
| [v094_durable_inclusive_adaptive_runner.py](../../runner/v094_durable_inclusive_adaptive_runner.py) | [test_v094_durable_inclusive_adaptive_runner.py](../../tests/test_v094_durable_inclusive_adaptive_runner.py) |
| [v095_material_precision_policy.py](../../runner/v095_material_precision_policy.py) | [test_v095_material_precision_policy.py](../../tests/test_v095_material_precision_policy.py) |
| [v096_unified_product_entry.py](../../runner/v096_unified_product_entry.py) | [test_v096_unified_product_entry.py](../../tests/test_v096_unified_product_entry.py) · [test_v096_manual_final_inclusive_entry.py](../../tests/test_v096_manual_final_inclusive_entry.py) |
| [v098_target_user_scenario_bootstrap.py](../../runner/v098_target_user_scenario_bootstrap.py) | [test_v098_target_user_scenario_bootstrap.py](../../tests/test_v098_target_user_scenario_bootstrap.py) |
| [v101_common_representative_equipment.py](../../runner/v101_common_representative_equipment.py) | [test_v101_common_representative_equipment.py](../../tests/test_v101_common_representative_equipment.py) |
| [v102_ordinary_armor_seed_pool.py](../../runner/v102_ordinary_armor_seed_pool.py) | [test_v102_ordinary_armor_seed_pool.py](../../tests/test_v102_ordinary_armor_seed_pool.py) |
| [v103_source_observed_weapon_types.py](../../runner/v103_source_observed_weapon_types.py) | [test_v103_source_observed_weapon_types.py](../../tests/test_v103_source_observed_weapon_types.py) |
| [v104_shared_pinned_rogue_shaman_composer.py](../../runner/v104_shared_pinned_rogue_shaman_composer.py) | [test_v104_shared_pinned_rogue_shaman_composer.py](../../tests/test_v104_shared_pinned_rogue_shaman_composer.py) |
| [v106_user_session_controller.py](../../runner/v106_user_session_controller.py) | [test_v106_user_session_controller.py](../../tests/test_v106_user_session_controller.py) |
| [v106_windows_simple_gui.py](../../runner/v106_windows_simple_gui.py) | [test_v106_user_session_controller.py](../../tests/test_v106_user_session_controller.py) |
| [v107_optional_items_dialog.py](../../runner/v107_optional_items_dialog.py) | [test_v107_optional_equipment_inputs.py](../../tests/test_v107_optional_equipment_inputs.py) |
| [v108_native_consumable_inputs.py](../../runner/v108_native_consumable_inputs.py) | [test_v108_user_consumables.py](../../tests/test_v108_user_consumables.py) |
| [v108_user_consumable_dialog.py](../../runner/v108_user_consumable_dialog.py) | [test_v108_user_consumables.py](../../tests/test_v108_user_consumables.py) |
| [v109_windows_readiness_diagnostic.py](../../runner/v109_windows_readiness_diagnostic.py) | [test_v109_windows_readiness_offline.py](../../tests/test_v109_windows_readiness_offline.py) |
| [v113_local_web_api.py](../../runner/v113_local_web_api.py) | [test_v113_local_web_api_offline.py](../../tests/test_v113_local_web_api_offline.py) |
| [v122_common_profile_format.py](../../runner/v122_common_profile_format.py) | [test_v122_common_profile_format.py](../../tests/test_v122_common_profile_format.py) |
| [v127_dps_source_metadata.py](../../runner/v127_dps_source_metadata.py) | [test_v127_dps_source_metadata.py](../../tests/test_v127_dps_source_metadata.py) |
| [v128_common_source_profile_emitter.py](../../runner/v128_common_source_profile_emitter.py) | [test_v128_common_source_profile_emitter.py](../../tests/test_v128_common_source_profile_emitter.py) |
| [v129_common_source_fields.py](../../runner/v129_common_source_fields.py) | [test_v129_common_source_fields.py](../../tests/test_v129_common_source_fields.py) |
| [v130_source_identity_contract.py](../../runner/v130_source_identity_contract.py) | [test_v130_source_identity_contract.py](../../tests/test_v130_source_identity_contract.py) |
| [v132_dps_source_batch_smoke.py](../../runner/v132_dps_source_batch_smoke.py) | [test_v132_dps_source_batch_smoke.py](../../tests/test_v132_dps_source_batch_smoke.py) |
| [v133_mid2_target_representative_preview.py](../../runner/v133_mid2_target_representative_preview.py) | [test_v133_mid2_target_representative_preview.py](../../tests/test_v133_mid2_target_representative_preview.py) |
| [v134_shared_mid2_profile_adapter.py](../../runner/v134_shared_mid2_profile_adapter.py) | [test_v134_shared_mid2_profile_adapter.py](../../tests/test_v134_shared_mid2_profile_adapter.py) · [test_v134_user_plan_new_mid2.py](../../tests/test_v134_user_plan_new_mid2.py) |
| [v135_source_gem_colors.py](../../runner/v135_source_gem_colors.py) | — |
| [v136_target334_single_smoke.py](../../runner/v136_target334_single_smoke.py) | [test_v136_target334_single_smoke.py](../../tests/test_v136_target334_single_smoke.py) |
| [v137_leather_feet_isolated_variant.py](../../runner/v137_leather_feet_isolated_variant.py) | [test_v137_leather_feet_isolated_variant.py](../../tests/test_v137_leather_feet_isolated_variant.py) |
| [v139_pure_target_profile_composer.py](../../runner/v139_pure_target_profile_composer.py) | [test_v139_pure_target_profile_composer.py](../../tests/test_v139_pure_target_profile_composer.py) · [test_v139_v098_pure_plan_bridge.py](../../tests/test_v139_v098_pure_plan_bridge.py) |
| [v141_verified_pure_native_pilot.py](../../runner/v141_verified_pure_native_pilot.py) | [test_v141_verified_pure_native_pilot.py](../../tests/test_v141_verified_pure_native_pilot.py) |
| [v143_specialization_contracts.py](../../runner/v143_specialization_contracts.py) | [test_v143_contract_season_compiler_offline.py](../../tests/test_v143_contract_season_compiler_offline.py) |
| [v148_local_batch_results.py](../../runner/v148_local_batch_results.py) | [test_v148_local_batch_results_offline.py](../../tests/test_v148_local_batch_results_offline.py) |
| [v151_season_catalog_impact.py](../../runner/v151_season_catalog_impact.py) | [test_v151_season_catalog_impact_offline.py](../../tests/test_v151_season_catalog_impact_offline.py) |
| [v154_blizzard_season_loot_index.py](../../runner/v154_blizzard_season_loot_index.py) | [test_v154_blizzard_season_loot_index_offline.py](../../tests/test_v154_blizzard_season_loot_index_offline.py) |
| [v155_season_api_probe.py](../../runner/v155_season_api_probe.py) | [test_v155_season_api_probe_offline.py](../../tests/test_v155_season_api_probe_offline.py) |
| [v156_one_blizzard_journal_loot_smoke.py](../../runner/v156_one_blizzard_journal_loot_smoke.py) | [test_v156_one_blizzard_journal_loot_smoke_offline.py](../../tests/test_v156_one_blizzard_journal_loot_smoke_offline.py) |
| [v157_blizzard_craft_probe.py](../../runner/v157_blizzard_craft_probe.py) | [test_v157_blizzard_craft_probe_offline.py](../../tests/test_v157_blizzard_craft_probe_offline.py) |
| [v158_source_first_season_catalog.py](../../runner/v158_source_first_season_catalog.py) | [test_v158_source_first_season_catalog_offline.py](../../tests/test_v158_source_first_season_catalog_offline.py) |
| [v159_blizzard_delve_rest_probe.py](../../runner/v159_blizzard_delve_rest_probe.py) | [test_v159_blizzard_delve_rest_probe_offline.py](../../tests/test_v159_blizzard_delve_rest_probe_offline.py) |
| [v160_wago_db2_access_probe.py](../../runner/v160_wago_db2_access_probe.py) | [test_v160_wago_db2_access_probe_offline.py](../../tests/test_v160_wago_db2_access_probe_offline.py) |
| [v161_wago_db2_snapshot.py](../../runner/v161_wago_db2_snapshot.py) | — |
| [v162_localbots_delve_provider.py](../../runner/v162_localbots_delve_provider.py) | [test_v162_localbots_delve_provider_offline.py](../../tests/test_v162_localbots_delve_provider_offline.py) |
| [v163_zero_seed_db2_join.py](../../runner/v163_zero_seed_db2_join.py) | [test_v163_db2_zero_seed.py](../../tests/test_v163_db2_zero_seed.py) · [test_v163_index_bridge.py](../../tests/test_v163_index_bridge.py) |
| [v164_saved_evidence_season_acceptance.py](../../runner/v164_saved_evidence_season_acceptance.py) | [test_v164_saved_evidence_acceptance.py](../../tests/test_v164_saved_evidence_acceptance.py) |
| [v165_current_season_gear_pool.py](../../runner/v165_current_season_gear_pool.py) | [test_v165_current_season_gear_pool.py](../../tests/test_v165_current_season_gear_pool.py) |
| [v166_compact_product_gear_db.py](../../runner/v166_compact_product_gear_db.py) | [test_v166_compact_product_gear_db.py](../../tests/test_v166_compact_product_gear_db.py) |
| [v167_product_season_gear_adapter.py](../../runner/v167_product_season_gear_adapter.py) | [test_v167_product_season_gear_adapter.py](../../tests/test_v167_product_season_gear_adapter.py) · [test_v167_local_gear_catalog_api.py](../../tests/test_v167_local_gear_catalog_api.py) |
| [v168_current_season_tier_discovery.py](../../runner/v168_current_season_tier_discovery.py) | [test_v168_current_season_tier_discovery.py](../../tests/test_v168_current_season_tier_discovery.py) |
| [v169_source_first_representative_stage.py](../../runner/v169_source_first_representative_stage.py) | [test_v169_source_first_representative_stage.py](../../tests/test_v169_source_first_representative_stage.py) · [test_v169_local_physical_preview_api.py](../../tests/test_v169_local_physical_preview_api.py) |
| [v171_current_mplus_inclusive_gear.py](../../runner/v171_current_mplus_inclusive_gear.py) | [test_v171_current_mplus_inclusive_gear.py](../../tests/test_v171_current_mplus_inclusive_gear.py) |
| [v188_user_choice_metadata.py](../../runner/v188_user_choice_metadata.py) | [test_v188_user_choice_labels_and_slots.py](../../tests/test_v188_user_choice_labels_and_slots.py) |
| [v189_simc_consumable_embellishment_discovery.py](../../runner/v189_simc_consumable_embellishment_discovery.py) | [test_v189_simc_choice_discovery.py](../../tests/test_v189_simc_choice_discovery.py) |
| [v190_consumable_item_snapshot_join.py](../../runner/v190_consumable_item_snapshot_join.py) | [test_v190_consumable_item_snapshot_join.py](../../tests/test_v190_consumable_item_snapshot_join.py) |
| [v191_unified_season_data_update.py](../../runner/v191_unified_season_data_update.py) | [test_v191_unified_season_data_update.py](../../tests/test_v191_unified_season_data_update.py) |
| [v193_simc_local_updater.py](../../runner/v193_simc_local_updater.py) | [test_v193_simc_local_updater.py](../../tests/test_v193_simc_local_updater.py) · [test_v193_local_web_simc_update_api.py](../../tests/test_v193_local_web_simc_update_api.py) |
| [v196_current_season_user_catalog.py](../../runner/v196_current_season_user_catalog.py) | [test_v196_current_season_ui_catalog.py](../../tests/test_v196_current_season_ui_catalog.py) |
| [v197_enchant_effect_families.py](../../runner/v197_enchant_effect_families.py) | [test_v197_enchant_effect_families.py](../../tests/test_v197_enchant_effect_families.py) · [test_v197_verified_effect_budget.py](../../tests/test_v197_verified_effect_budget.py) |
| [v197_verified_effect_budget.py](../../runner/v197_verified_effect_budget.py) | [test_v197_verified_effect_budget.py](../../tests/test_v197_verified_effect_budget.py) · [test_v197_enchant_effect_families.py](../../tests/test_v197_enchant_effect_families.py) |
| [v202_one_enchant_admission.py](../../runner/v202_one_enchant_admission.py) | [test_v202_one_enchant_admission.py](../../tests/test_v202_one_enchant_admission.py) · [test_v202_enchant_scheduler_floor.py](../../tests/test_v202_enchant_scheduler_floor.py) |
| [v204_selected_enchant_reference_budget.py](../../runner/v204_selected_enchant_reference_budget.py) | [test_v204_selected_enchant_reference_budget.py](../../tests/test_v204_selected_enchant_reference_budget.py) |
| [v206_nonchmv_eagle_selection.py](../../runner/v206_nonchmv_eagle_selection.py) | [test_v206_nonchmv_eagle_user_path.py](../../tests/test_v206_nonchmv_eagle_user_path.py) |
| [v208_internal_exact_special_L_hydrator.py](../../runner/v208_internal_exact_special_L_hydrator.py) | [test_v208_special_L_hydration_offline.py](../../tests/test_v208_special_L_hydration_offline.py) |
| [v211_enchant_source_effect_classification.py](../../runner/v211_enchant_source_effect_classification.py) | [test_v211_enchant_source_effect_classification.py](../../tests/test_v211_enchant_source_effect_classification.py) |
| [v212_environment_manifest.py](../../runner/v212_environment_manifest.py) | [test_v212_environment_manifest.py](../../tests/test_v212_environment_manifest.py) |
| [v213_source_to_catalog.py](../../runner/v213_source_to_catalog.py) | [test_v213_source_to_catalog.py](../../tests/test_v213_source_to_catalog.py) |
| [v216_environment_build_coordinator.py](../../runner/v216_environment_build_coordinator.py) | [test_v216_environment_build_coordinator.py](../../tests/test_v216_environment_build_coordinator.py) |
| [v217_stage_execution_engine.py](../../runner/v217_stage_execution_engine.py) | [test_v217_stage_execution_engine.py](../../tests/test_v217_stage_execution_engine.py) |
| [v218_v098_profile_stage_adapter.py](../../runner/v218_v098_profile_stage_adapter.py) | — |
| [v220_catalog_auto_admission.py](../../runner/v220_catalog_auto_admission.py) | [test_v220_catalog_auto_admission.py](../../tests/test_v220_catalog_auto_admission.py) |
| [v221_gem_item_db2_relation.py](../../runner/v221_gem_item_db2_relation.py) | [test_v221_gem_item_db2_relation.py](../../tests/test_v221_gem_item_db2_relation.py) |
| [v222_season_budget_contract.py](../../runner/v222_season_budget_contract.py) | [test_v222_season_budget_contract.py](../../tests/test_v222_season_budget_contract.py) |
| [v223_installed_season_budget_source.py](../../runner/v223_installed_season_budget_source.py) | [test_v223_installed_season_budget_source.py](../../tests/test_v223_installed_season_budget_source.py) |
| [v224_season_gjfo_evidence_inventory.py](../../runner/v224_season_gjfo_evidence_inventory.py) | [test_v224_season_gjfo_evidence_inventory.py](../../tests/test_v224_season_gjfo_evidence_inventory.py) |
| [v225_season_source_bundle_intake.py](../../runner/v225_season_source_bundle_intake.py) | [test_v225_season_source_bundle_intake.py](../../tests/test_v225_season_source_bundle_intake.py) |
| [v226_representative_native_g_work_order.py](../../runner/v226_representative_native_g_work_order.py) | [test_v226_representative_native_g_work_order.py](../../tests/test_v226_representative_native_g_work_order.py) |
| [v227_cached_native_g_observation.py](../../runner/v227_cached_native_g_observation.py) | [test_v227_cached_native_g_observation.py](../../tests/test_v227_cached_native_g_observation.py) |
| [v228_source_native_g_reconciliation.py](../../runner/v228_source_native_g_reconciliation.py) | [test_v228_source_native_g_reconciliation.py](../../tests/test_v228_source_native_g_reconciliation.py) |
| [v229_simc_only_source_seed.py](../../runner/v229_simc_only_source_seed.py) | [test_v229_simc_only_source_seed.py](../../tests/test_v229_simc_only_source_seed.py) |
| [v230_simc_item_metadata.py](../../runner/v230_simc_item_metadata.py) | [test_v230_simc_item_metadata.py](../../tests/test_v230_simc_item_metadata.py) |
| [v231_simc_tier_item_join.py](../../runner/v231_simc_tier_item_join.py) | [test_v231_simc_tier_item_join.py](../../tests/test_v231_simc_tier_item_join.py) |
| [v232_simc_only_ordinary_representative.py](../../runner/v232_simc_only_ordinary_representative.py) | [test_v232_simc_only_ordinary_representative.py](../../tests/test_v232_simc_only_ordinary_representative.py) |
| [v233_source_only_G_probe_profile.py](../../runner/v233_source_only_G_probe_profile.py) | [test_v233_v234_source_native_G.py](../../tests/test_v233_v234_source_native_G.py) |
| [v234_source_only_one_native_G.py](../../runner/v234_source_only_one_native_G.py) | — |
| [v236_sealed_one_native_G.py](../../runner/v236_sealed_one_native_G.py) | [test_v236_sealed_one_native_G.py](../../tests/test_v236_sealed_one_native_G.py) |
| [v241_fresh_source_stage_adapter.py](../../runner/v241_fresh_source_stage_adapter.py) | — |
| [v242_authenticated_season_source_stage.py](../../runner/v242_authenticated_season_source_stage.py) | — |
| [v243_fresh_tier_anchor_intake.py](../../runner/v243_fresh_tier_anchor_intake.py) | [test_v243_fresh_tier_anchor_intake.py](../../tests/test_v243_fresh_tier_anchor_intake.py) |
| [v245_db2_first_tier_discovery.py](../../runner/v245_db2_first_tier_discovery.py) | [test_v245_db2_first_tier_discovery.py](../../tests/test_v245_db2_first_tier_discovery.py) |
| [v250_raid_tier_bonus_corroboration.py](../../runner/v250_raid_tier_bonus_corroboration.py) | [test_v250_raid_tier_bonus_corroboration.py](../../tests/test_v250_raid_tier_bonus_corroboration.py) |
| [v251_db2_raid_tier_simc_bridge.py](../../runner/v251_db2_raid_tier_simc_bridge.py) | [test_v251_db2_raid_tier_simc_bridge.py](../../tests/test_v251_db2_raid_tier_simc_bridge.py) |
| [v258_simc_update_source_delta.py](../../runner/v258_simc_update_source_delta.py) | [test_v258_simc_update_source_delta.py](../../tests/test_v258_simc_update_source_delta.py) |
| [v261_tier_source_evidence_reuse.py](../../runner/v261_tier_source_evidence_reuse.py) | — |
| [v262_standardized_ilevel_budget_rows.py](../../runner/v262_standardized_ilevel_budget_rows.py) | [test_v262_standardized_G_native_bridge.py](../../tests/test_v262_standardized_G_native_bridge.py) |
| [v266_gem_enchant_raw_stat_source.py](../../runner/v266_gem_enchant_raw_stat_source.py) | [test_v266_v268_gem_enchant_source_reuse.py](../../tests/test_v266_v268_gem_enchant_source_reuse.py) |
| [v267_gem_enchant_one_csv_fetch.py](../../runner/v267_gem_enchant_one_csv_fetch.py) | — |
| [v268_gem_enchant_existing_source_stage.py](../../runner/v268_gem_enchant_existing_source_stage.py) | — |
| [v269_simc_chmv_effect_snapshot.py](../../runner/v269_simc_chmv_effect_snapshot.py) | [test_v269_simc_chmv_effect_snapshot.py](../../tests/test_v269_simc_chmv_effect_snapshot.py) |
| [v271_user_socket_gem_layout.py](../../runner/v271_user_socket_gem_layout.py) | [test_v271_user_socket_gem_layout.py](../../tests/test_v271_user_socket_gem_layout.py) |
| [v274_zero_history_source_compiler_wiring.py](../../runner/v274_zero_history_source_compiler_wiring.py) | [test_v274_zero_history_source_compiler_wiring.py](../../tests/test_v274_zero_history_source_compiler_wiring.py) |
| [v275_pinned_simc_compiler_inputs.py](../../runner/v275_pinned_simc_compiler_inputs.py) | [test_v275_pinned_simc_compiler_inputs.py](../../tests/test_v275_pinned_simc_compiler_inputs.py) |
| [v276_sealed_tier_compiler_source.py](../../runner/v276_sealed_tier_compiler_source.py) | [test_v276_sealed_tier_compiler_source.py](../../tests/test_v276_sealed_tier_compiler_source.py) |
| [v277_zero_history_native_G_stage.py](../../runner/v277_zero_history_native_G_stage.py) | [test_v277_zero_history_native_G_stage.py](../../tests/test_v277_zero_history_native_G_stage.py) |
| [v278_sealed_simc_consumable_native_pair.py](../../runner/v278_sealed_simc_consumable_native_pair.py) | [test_v278_sealed_simc_consumable_native_pair.py](../../tests/test_v278_sealed_simc_consumable_native_pair.py) |
| [v280_consumable_item_use_spell_source.py](../../runner/v280_consumable_item_use_spell_source.py) | [test_v280_consumable_item_use_spell_source.py](../../tests/test_v280_consumable_item_use_spell_source.py) |
| [v281_consumable_simc_relation.py](../../runner/v281_consumable_simc_relation.py) | [test_v281_consumable_simc_relation.py](../../tests/test_v281_consumable_simc_relation.py) · [test_v281_physical_native_item_binding.py](../../tests/test_v281_physical_native_item_binding.py) |
| [v285_consumable_weapon_source.py](../../runner/v285_consumable_weapon_source.py) | [test_v285_consumable_weapon_source.py](../../tests/test_v285_consumable_weapon_source.py) |
| [v286_representative_oil_source_binding.py](../../runner/v286_representative_oil_source_binding.py) | [test_v286_representative_oil_source_binding.py](../../tests/test_v286_representative_oil_source_binding.py) |
| [v289_retail_live_build_source.py](../../runner/v289_retail_live_build_source.py) | [test_v289_retail_live_build_source.py](../../tests/test_v289_retail_live_build_source.py) |
| [v290_multiscale_adaptive_policy.py](../../runner/v290_multiscale_adaptive_policy.py) | — |
| [v291_durable_multiscale_native_runner.py](../../runner/v291_durable_multiscale_native_runner.py) | — |
| [v292_portable_native_case_cache.py](../../runner/v292_portable_native_case_cache.py) | — |
| [v293_local_longrun_session.py](../../runner/v293_local_longrun_session.py) | — |
| [v294_dk_runeforge_selection.py](../../runner/v294_dk_runeforge_selection.py) | [test_v294_dk_runeforge_selection.py](../../tests/test_v294_dk_runeforge_selection.py) |
| [v295_season_runeforge_source.py](../../runner/v295_season_runeforge_source.py) | [test_v295_season_runeforge_source.py](../../tests/test_v295_season_runeforge_source.py) |
| [v296_pinned_oil_static_rating_source.py](../../runner/v296_pinned_oil_static_rating_source.py) | [test_v296_pinned_oil_static_rating_source.py](../../tests/test_v296_pinned_oil_static_rating_source.py) |
| [v297_sealed_simc_oil_gear_delta.py](../../runner/v297_sealed_simc_oil_gear_delta.py) | [test_v297_sealed_simc_oil_gear_delta.py](../../tests/test_v297_sealed_simc_oil_gear_delta.py) |

## Tests Python 파일 전체

| 파일 | 파일 | 파일 |
|---|---|---|
| [test_p1_oil_positive_bridge_offline.py](../../tests/test_p1_oil_positive_bridge_offline.py) | [test_p2_multimodal_quality_audit.py](../../tests/test_p2_multimodal_quality_audit.py) | [test_p3_co_actual_flask_oil_native.py](../../tests/test_p3_co_actual_flask_oil_native.py) |
| [test_p3_fs_simc_image_revision.py](../../tests/test_p3_fs_simc_image_revision.py) | [test_p3_ft_season_scope_diagnostic.py](../../tests/test_p3_ft_season_scope_diagnostic.py) | [test_p3_fz_existing_simc_binary_identity.py](../../tests/test_p3_fz_existing_simc_binary_identity.py) |
| [test_p3_ga_raid_loot_expansion_diagnostic.py](../../tests/test_p3_ga_raid_loot_expansion_diagnostic.py) | [test_p3_gj_existing_native_case_archive.py](../../tests/test_p3_gj_existing_native_case_archive.py) | [test_p3_gk_f_j_diagnostic_receipt.py](../../tests/test_p3_gk_f_j_diagnostic_receipt.py) |
| [test_p3_gl_highest_quality_flask_measurement.py](../../tests/test_p3_gl_highest_quality_flask_measurement.py) | [test_p3_gm_exact_f_t1_selected_mode.py](../../tests/test_p3_gm_exact_f_t1_selected_mode.py) | [test_p3_gn_default_flask_environment_engine.py](../../tests/test_p3_gn_default_flask_environment_engine.py) |
| [test_p3_gq_original_gjf_one_shot.py](../../tests/test_p3_gq_original_gjf_one_shot.py) | [test_p3_gr_future_five_sockets_source_only.py](../../tests/test_p3_gr_future_five_sockets_source_only.py) | [test_p3_gs_real_five_socket_layout_stage.py](../../tests/test_p3_gs_real_five_socket_layout_stage.py) |
| [test_p3_gt_reuse_existing_socket_item_use_source.py](../../tests/test_p3_gt_reuse_existing_socket_item_use_source.py) | [test_p3_gu_j_socket_source_no_native.py](../../tests/test_p3_gu_j_socket_source_no_native.py) | [test_p3_gw_declared_full_sockets.py](../../tests/test_p3_gw_declared_full_sockets.py) |
| [test_p3_hab_strict_final_half_cap.py](../../tests/test_p3_hab_strict_final_half_cap.py) | [test_p3_had_eight_native_one_shot_guard.py](../../tests/test_p3_had_eight_native_one_shot_guard.py) | [test_p3_hae_ten_native_one_shot_guard.py](../../tests/test_p3_hae_ten_native_one_shot_guard.py) |
| [test_p3_hag_portable_native_case_cache.py](../../tests/test_p3_hag_portable_native_case_cache.py) | [test_p3_hag_portable_one_shot_guard.py](../../tests/test_p3_hag_portable_one_shot_guard.py) | [test_p3_hah_local_longrun_product_offline.py](../../tests/test_p3_hah_local_longrun_product_offline.py) |
| [test_p3_hah_local_longrun_worker_offline.py](../../tests/test_p3_hah_local_longrun_worker_offline.py) | [test_p3_haj_local_web_real_one_shot_guard.py](../../tests/test_p3_haj_local_web_real_one_shot_guard.py) | [test_p3_ham_fresh_v212_web_profile_bridge_offline.py](../../tests/test_p3_ham_fresh_v212_web_profile_bridge_offline.py) |
| [test_p3_ho_fresh_v212_user_bridge.py](../../tests/test_p3_ho_fresh_v212_user_bridge.py) | [test_p3_ht_observe_existing_dps_native.py](../../tests/test_p3_ht_observe_existing_dps_native.py) | [test_p3_hu_applicable_consumables.py](../../tests/test_p3_hu_applicable_consumables.py) |
| [test_p3_hv_axis_coverage_offline.py](../../tests/test_p3_hv_axis_coverage_offline.py) | [test_p3_hw_multiscale_policy.py](../../tests/test_p3_hw_multiscale_policy.py) | [test_p3_hx_durable_longrun_offline.py](../../tests/test_p3_hx_durable_longrun_offline.py) |
| [test_p3_hy_longrun_native_one_shot_guard.py](../../tests/test_p3_hy_longrun_native_one_shot_guard.py) | [test_pilot.py](../../tests/test_pilot.py) | [test_v037_manual_budget_adapter.py](../../tests/test_v037_manual_budget_adapter.py) |
| [test_v038_fixed_gear_floor.py](../../tests/test_v038_fixed_gear_floor.py) | [test_v039_tier_effect_probe.py](../../tests/test_v039_tier_effect_probe.py) | [test_v039_venomkeeper_bare_probe.py](../../tests/test_v039_venomkeeper_bare_probe.py) |
| [test_v040_catalyst_redirect_probe.py](../../tests/test_v040_catalyst_redirect_probe.py) | [test_v041_catalyst_gem_proc_probe.py](../../tests/test_v041_catalyst_gem_proc_probe.py) | [test_v042_catalyst_evidence_firewall.py](../../tests/test_v042_catalyst_evidence_firewall.py) |
| [test_v043_spell_data_probe.py](../../tests/test_v043_spell_data_probe.py) | [test_v044_static_budget_attribution.py](../../tests/test_v044_static_budget_attribution.py) | [test_v045_native_budget_candidate.py](../../tests/test_v045_native_budget_candidate.py) |
| [test_v046_static_item_cache.py](../../tests/test_v046_static_item_cache.py) | [test_v047_full_scope_collector.py](../../tests/test_v047_full_scope_collector.py) | [test_v049_class_compatible_recovery.py](../../tests/test_v049_class_compatible_recovery.py) |
| [test_v051_crafted_embellishment_bridge.py](../../tests/test_v051_crafted_embellishment_bridge.py) | [test_v053_crafted_native_inputs.py](../../tests/test_v053_crafted_native_inputs.py) | [test_v055_simc_item_selection.py](../../tests/test_v055_simc_item_selection.py) |
| [test_v058_lazy_crafted_native.py](../../tests/test_v058_lazy_crafted_native.py) | [test_v059_candidate_runner_bridge.py](../../tests/test_v059_candidate_runner_bridge.py) | [test_v061_scenario_contract.py](../../tests/test_v061_scenario_contract.py) |
| [test_v062_static_budget_bridge.py](../../tests/test_v062_static_budget_bridge.py) | [test_v063_numeric_injection.py](../../tests/test_v063_numeric_injection.py) | [test_v064_adaptive_evaluator_port.py](../../tests/test_v064_adaptive_evaluator_port.py) |
| [test_v065_native_pipeline_safety.py](../../tests/test_v065_native_pipeline_safety.py) | [test_v065_original_v015_search_adapter.py](../../tests/test_v065_original_v015_search_adapter.py) | [test_v065_v015_scheduler_adapter.py](../../tests/test_v065_v015_scheduler_adapter.py) |
| [test_v066_profile_neutral_preflight.py](../../tests/test_v066_profile_neutral_preflight.py) | [test_v067_generic_adaptive_native_route.py](../../tests/test_v067_generic_adaptive_native_route.py) | [test_v068_rogue_user_profile.py](../../tests/test_v068_rogue_user_profile.py) |
| [test_v069_official_rogue_budget.py](../../tests/test_v069_official_rogue_budget.py) | [test_v071_rogue_adaptive_first_scout.py](../../tests/test_v071_rogue_adaptive_first_scout.py) | [test_v072_rogue_high_iteration_confirm.py](../../tests/test_v072_rogue_high_iteration_confirm.py) |
| [test_v073_rogue_material_adaptive_scout.py](../../tests/test_v073_rogue_material_adaptive_scout.py) | [test_v074_rogue_selected_D_high_confirmation.py](../../tests/test_v074_rogue_selected_D_high_confirmation.py) | [test_v075_rogue_coarse_continuation.py](../../tests/test_v075_rogue_coarse_continuation.py) |
| [test_v076_generic_dps_scope_audit.py](../../tests/test_v076_generic_dps_scope_audit.py) | [test_v077_generic_profile_bootstrap_readiness.py](../../tests/test_v077_generic_profile_bootstrap_readiness.py) | [test_v078_elemental_first_native.py](../../tests/test_v078_elemental_first_native.py) |
| [test_v078b_elemental_official_generic_native.py](../../tests/test_v078b_elemental_official_generic_native.py) | [test_v079_hunter_ranged_generic_native.py](../../tests/test_v079_hunter_ranged_generic_native.py) | [test_v079b_hunter_empirical_affine_recovery.py](../../tests/test_v079b_hunter_empirical_affine_recovery.py) |
| [test_v080_static_chmv_corrected_native.py](../../tests/test_v080_static_chmv_corrected_native.py) | [test_v081_static_generic_scout_native.py](../../tests/test_v081_static_generic_scout_native.py) | [test_v082_fury_plate_dual_twohand_native.py](../../tests/test_v082_fury_plate_dual_twohand_native.py) |
| [test_v083_paladin_single_2h_native.py](../../tests/test_v083_paladin_single_2h_native.py) | [test_v084_frost_cloth_1h_frill_native.py](../../tests/test_v084_frost_cloth_1h_frill_native.py) | [test_v085_shaman_real_static_replay.py](../../tests/test_v085_shaman_real_static_replay.py) |
| [test_v086_hunter_fixed_mail_representative.py](../../tests/test_v086_hunter_fixed_mail_representative.py) | [test_v089_ilvl_chmv_budget_selector.py](../../tests/test_v089_ilvl_chmv_budget_selector.py) | [test_v090_reference_total_native_candidate.py](../../tests/test_v090_reference_total_native_candidate.py) |
| [test_v091_weapon_oil_external_adapter.py](../../tests/test_v091_weapon_oil_external_adapter.py) | [test_v092_approved_inclusive_CHMV_policy.py](../../tests/test_v092_approved_inclusive_CHMV_policy.py) | [test_v093_inclusive_adaptive_scheduler_bridge.py](../../tests/test_v093_inclusive_adaptive_scheduler_bridge.py) |
| [test_v094_durable_inclusive_adaptive_runner.py](../../tests/test_v094_durable_inclusive_adaptive_runner.py) | [test_v095_material_precision_policy.py](../../tests/test_v095_material_precision_policy.py) | [test_v096_manual_final_inclusive_entry.py](../../tests/test_v096_manual_final_inclusive_entry.py) |
| [test_v096_unified_product_entry.py](../../tests/test_v096_unified_product_entry.py) | [test_v097_user_result_offline.py](../../tests/test_v097_user_result_offline.py) | [test_v098_target_user_scenario_bootstrap.py](../../tests/test_v098_target_user_scenario_bootstrap.py) |
| [test_v101_common_representative_equipment.py](../../tests/test_v101_common_representative_equipment.py) | [test_v102_ordinary_armor_seed_pool.py](../../tests/test_v102_ordinary_armor_seed_pool.py) | [test_v103_source_observed_weapon_types.py](../../tests/test_v103_source_observed_weapon_types.py) |
| [test_v104_shared_pinned_rogue_shaman_composer.py](../../tests/test_v104_shared_pinned_rogue_shaman_composer.py) | [test_v105_paladin_user_e2e_contract.py](../../tests/test_v105_paladin_user_e2e_contract.py) | [test_v106_user_session_controller.py](../../tests/test_v106_user_session_controller.py) |
| [test_v107_optional_equipment_inputs.py](../../tests/test_v107_optional_equipment_inputs.py) | [test_v108_user_consumables.py](../../tests/test_v108_user_consumables.py) | [test_v109_windows_readiness_offline.py](../../tests/test_v109_windows_readiness_offline.py) |
| [test_v110_windows_exact_simc_input_bytes.py](../../tests/test_v110_windows_exact_simc_input_bytes.py) | [test_v113_local_web_api_offline.py](../../tests/test_v113_local_web_api_offline.py) | [test_v114_local_web_ui_offline.py](../../tests/test_v114_local_web_ui_offline.py) |
| [test_v122_common_profile_format.py](../../tests/test_v122_common_profile_format.py) | [test_v124_fixed_component_candidate_bounds.py](../../tests/test_v124_fixed_component_candidate_bounds.py) | [test_v127_dps_source_metadata.py](../../tests/test_v127_dps_source_metadata.py) |
| [test_v128_common_source_profile_emitter.py](../../tests/test_v128_common_source_profile_emitter.py) | [test_v129_common_source_fields.py](../../tests/test_v129_common_source_fields.py) | [test_v130_source_identity_contract.py](../../tests/test_v130_source_identity_contract.py) |
| [test_v131_rogue_outlaw_source_candidate.py](../../tests/test_v131_rogue_outlaw_source_candidate.py) | [test_v132_dps_source_batch_smoke.py](../../tests/test_v132_dps_source_batch_smoke.py) | [test_v133_mid2_target_representative_preview.py](../../tests/test_v133_mid2_target_representative_preview.py) |
| [test_v134_shared_mid2_profile_adapter.py](../../tests/test_v134_shared_mid2_profile_adapter.py) | [test_v134_user_plan_new_mid2.py](../../tests/test_v134_user_plan_new_mid2.py) | [test_v136_target334_single_smoke.py](../../tests/test_v136_target334_single_smoke.py) |
| [test_v137_leather_feet_isolated_variant.py](../../tests/test_v137_leather_feet_isolated_variant.py) | [test_v139_pure_target_profile_composer.py](../../tests/test_v139_pure_target_profile_composer.py) | [test_v139_v098_pure_plan_bridge.py](../../tests/test_v139_v098_pure_plan_bridge.py) |
| [test_v140_pure_profile_physical_native_smoke.py](../../tests/test_v140_pure_profile_physical_native_smoke.py) | [test_v141_verified_pure_native_pilot.py](../../tests/test_v141_verified_pure_native_pilot.py) | [test_v142_verified_partial_native_recovery.py](../../tests/test_v142_verified_partial_native_recovery.py) |
| [test_v143_contract_season_compiler_offline.py](../../tests/test_v143_contract_season_compiler_offline.py) | [test_v145_targeted_pure_physical_native_offline.py](../../tests/test_v145_targeted_pure_physical_native_offline.py) | [test_v145_v141_exact_receipt_bridge_offline.py](../../tests/test_v145_v141_exact_receipt_bridge_offline.py) |
| [test_v147_all_dps_targeted_native_batch_offline.py](../../tests/test_v147_all_dps_targeted_native_batch_offline.py) | [test_v148_local_batch_results_offline.py](../../tests/test_v148_local_batch_results_offline.py) | [test_v149_target334_independent_product_offline.py](../../tests/test_v149_target334_independent_product_offline.py) |
| [test_v150_local_saved_session_index_offline.py](../../tests/test_v150_local_saved_session_index_offline.py) | [test_v151_season_catalog_impact_offline.py](../../tests/test_v151_season_catalog_impact_offline.py) | [test_v152_windows_local_web_launcher_offline.py](../../tests/test_v152_windows_local_web_launcher_offline.py) |
| [test_v153_non334_independent_product_offline.py](../../tests/test_v153_non334_independent_product_offline.py) | [test_v154_blizzard_season_loot_index_offline.py](../../tests/test_v154_blizzard_season_loot_index_offline.py) | [test_v155_season_api_probe_offline.py](../../tests/test_v155_season_api_probe_offline.py) |
| [test_v156_one_blizzard_journal_loot_smoke_offline.py](../../tests/test_v156_one_blizzard_journal_loot_smoke_offline.py) | [test_v157_blizzard_craft_probe_offline.py](../../tests/test_v157_blizzard_craft_probe_offline.py) | [test_v158_source_first_season_catalog_offline.py](../../tests/test_v158_source_first_season_catalog_offline.py) |
| [test_v159_blizzard_delve_rest_probe_offline.py](../../tests/test_v159_blizzard_delve_rest_probe_offline.py) | [test_v160_wago_db2_access_probe_offline.py](../../tests/test_v160_wago_db2_access_probe_offline.py) | [test_v162_localbots_delve_provider_offline.py](../../tests/test_v162_localbots_delve_provider_offline.py) |
| [test_v163_db2_zero_seed.py](../../tests/test_v163_db2_zero_seed.py) | [test_v163_index_bridge.py](../../tests/test_v163_index_bridge.py) | [test_v164_saved_evidence_acceptance.py](../../tests/test_v164_saved_evidence_acceptance.py) |
| [test_v165_current_season_gear_pool.py](../../tests/test_v165_current_season_gear_pool.py) | [test_v166_compact_product_gear_db.py](../../tests/test_v166_compact_product_gear_db.py) | [test_v167_local_gear_catalog_api.py](../../tests/test_v167_local_gear_catalog_api.py) |
| [test_v167_product_season_gear_adapter.py](../../tests/test_v167_product_season_gear_adapter.py) | [test_v168_current_season_tier_discovery.py](../../tests/test_v168_current_season_tier_discovery.py) | [test_v169_local_physical_preview_api.py](../../tests/test_v169_local_physical_preview_api.py) |
| [test_v169_source_first_representative_stage.py](../../tests/test_v169_source_first_representative_stage.py) | [test_v171_current_mplus_inclusive_gear.py](../../tests/test_v171_current_mplus_inclusive_gear.py) | [test_v172_current_season_v098_stage.py](../../tests/test_v172_current_season_v098_stage.py) |
| [test_v175_first_rating_native.py](../../tests/test_v175_first_rating_native.py) | [test_v176_all_26_source_first_physical_native.py](../../tests/test_v176_all_26_source_first_physical_native.py) | [test_v177_current_season_product_flow.py](../../tests/test_v177_current_season_product_flow.py) |
| [test_v178_real_user_cancel_resume_offline.py](../../tests/test_v178_real_user_cancel_resume_offline.py) | [test_v179_current_season_input_paths_offline.py](../../tests/test_v179_current_season_input_paths_offline.py) | [test_v180_multilevel_current_season_product_offline.py](../../tests/test_v180_multilevel_current_season_product_offline.py) |
| [test_v181_windows_beta_package_offline.py](../../tests/test_v181_windows_beta_package_offline.py) | [test_v182_simple_user_inputs_offline.py](../../tests/test_v182_simple_user_inputs_offline.py) | [test_v187_current_season_tier_overlay.py](../../tests/test_v187_current_season_tier_overlay.py) |
| [test_v188_user_choice_labels_and_slots.py](../../tests/test_v188_user_choice_labels_and_slots.py) | [test_v189_simc_choice_discovery.py](../../tests/test_v189_simc_choice_discovery.py) | [test_v190_consumable_item_snapshot_join.py](../../tests/test_v190_consumable_item_snapshot_join.py) |
| [test_v191_unified_season_data_update.py](../../tests/test_v191_unified_season_data_update.py) | [test_v193_local_web_simc_update_api.py](../../tests/test_v193_local_web_simc_update_api.py) | [test_v193_simc_local_updater.py](../../tests/test_v193_simc_local_updater.py) |
| [test_v196_current_season_ui_catalog.py](../../tests/test_v196_current_season_ui_catalog.py) | [test_v197_enchant_effect_families.py](../../tests/test_v197_enchant_effect_families.py) | [test_v197_verified_effect_budget.py](../../tests/test_v197_verified_effect_budget.py) |
| [test_v198_targeted_enchant_native_rating.py](../../tests/test_v198_targeted_enchant_native_rating.py) | [test_v202_enchant_scheduler_floor.py](../../tests/test_v202_enchant_scheduler_floor.py) | [test_v202_one_enchant_admission.py](../../tests/test_v202_one_enchant_admission.py) |
| [test_v203_enchant_cross_feature_policy.py](../../tests/test_v203_enchant_cross_feature_policy.py) | [test_v204_selected_enchant_reference_budget.py](../../tests/test_v204_selected_enchant_reference_budget.py) | [test_v206_nonchmv_eagle_user_path.py](../../tests/test_v206_nonchmv_eagle_user_path.py) |
| [test_v208_special_L_hydration_offline.py](../../tests/test_v208_special_L_hydration_offline.py) | [test_v211_enchant_source_effect_classification.py](../../tests/test_v211_enchant_source_effect_classification.py) | [test_v212_environment_manifest.py](../../tests/test_v212_environment_manifest.py) |
| [test_v213_source_to_catalog.py](../../tests/test_v213_source_to_catalog.py) | [test_v216_environment_build_coordinator.py](../../tests/test_v216_environment_build_coordinator.py) | [test_v217_stage_execution_engine.py](../../tests/test_v217_stage_execution_engine.py) |
| [test_v220_catalog_auto_admission.py](../../tests/test_v220_catalog_auto_admission.py) | [test_v221_gem_item_db2_relation.py](../../tests/test_v221_gem_item_db2_relation.py) | [test_v222_season_budget_contract.py](../../tests/test_v222_season_budget_contract.py) |
| [test_v223_installed_season_budget_source.py](../../tests/test_v223_installed_season_budget_source.py) | [test_v224_season_gjfo_evidence_inventory.py](../../tests/test_v224_season_gjfo_evidence_inventory.py) | [test_v225_season_source_bundle_intake.py](../../tests/test_v225_season_source_bundle_intake.py) |
| [test_v226_representative_native_g_work_order.py](../../tests/test_v226_representative_native_g_work_order.py) | [test_v227_cached_native_g_observation.py](../../tests/test_v227_cached_native_g_observation.py) | [test_v228_source_native_g_reconciliation.py](../../tests/test_v228_source_native_g_reconciliation.py) |
| [test_v229_simc_only_source_seed.py](../../tests/test_v229_simc_only_source_seed.py) | [test_v230_simc_item_metadata.py](../../tests/test_v230_simc_item_metadata.py) | [test_v231_simc_tier_item_join.py](../../tests/test_v231_simc_tier_item_join.py) |
| [test_v232_simc_only_ordinary_representative.py](../../tests/test_v232_simc_only_ordinary_representative.py) | [test_v233_v234_source_native_G.py](../../tests/test_v233_v234_source_native_G.py) | [test_v236_sealed_one_native_G.py](../../tests/test_v236_sealed_one_native_G.py) |
| [test_v238_fresh_product_gear_chain.py](../../tests/test_v238_fresh_product_gear_chain.py) | [test_v239_v211_fresh_season_dynamic_classifier.py](../../tests/test_v239_v211_fresh_season_dynamic_classifier.py) | [test_v240_v211_v213_fresh_catalog_handoff.py](../../tests/test_v240_v211_v213_fresh_catalog_handoff.py) |
| [test_v243_fresh_tier_anchor_intake.py](../../tests/test_v243_fresh_tier_anchor_intake.py) | [test_v245_db2_first_tier_discovery.py](../../tests/test_v245_db2_first_tier_discovery.py) | [test_v250_raid_tier_bonus_corroboration.py](../../tests/test_v250_raid_tier_bonus_corroboration.py) |
| [test_v251_db2_raid_tier_simc_bridge.py](../../tests/test_v251_db2_raid_tier_simc_bridge.py) | [test_v254_fresh_ordinary_gear_in_build.py](../../tests/test_v254_fresh_ordinary_gear_in_build.py) | [test_v255_one_spec_simc_representative_in_build.py](../../tests/test_v255_one_spec_simc_representative_in_build.py) |
| [test_v256_lazy_full_pinned_simc_in_build.py](../../tests/test_v256_lazy_full_pinned_simc_in_build.py) | [test_v257_exact_simc_commit_in_build.py](../../tests/test_v257_exact_simc_commit_in_build.py) | [test_v258_simc_update_source_delta.py](../../tests/test_v258_simc_update_source_delta.py) |
| [test_v259_v217_source_seal_reuse.py](../../tests/test_v259_v217_source_seal_reuse.py) | [test_v260_development_ledger_guard.py](../../tests/test_v260_development_ledger_guard.py) | [test_v262_standardized_G_native_bridge.py](../../tests/test_v262_standardized_G_native_bridge.py) |
| [test_v263_standardized_ilevel_budget_rows.py](../../tests/test_v263_standardized_ilevel_budget_rows.py) | [test_v264_environment_standard_budget_integration.py](../../tests/test_v264_environment_standard_budget_integration.py) | [test_v266_v268_gem_enchant_source_reuse.py](../../tests/test_v266_v268_gem_enchant_source_reuse.py) |
| [test_v269_simc_chmv_effect_snapshot.py](../../tests/test_v269_simc_chmv_effect_snapshot.py) | [test_v271_user_socket_gem_layout.py](../../tests/test_v271_user_socket_gem_layout.py) | [test_v272_normal_build_gem_j_bridge.py](../../tests/test_v272_normal_build_gem_j_bridge.py) |
| [test_v273_zero_history_normal_build_engine.py](../../tests/test_v273_zero_history_normal_build_engine.py) | [test_v274_zero_history_source_compiler_wiring.py](../../tests/test_v274_zero_history_source_compiler_wiring.py) | [test_v275_pinned_simc_compiler_inputs.py](../../tests/test_v275_pinned_simc_compiler_inputs.py) |
| [test_v276_sealed_tier_compiler_source.py](../../tests/test_v276_sealed_tier_compiler_source.py) | [test_v277_zero_history_native_G_stage.py](../../tests/test_v277_zero_history_native_G_stage.py) | [test_v278_sealed_simc_consumable_native_pair.py](../../tests/test_v278_sealed_simc_consumable_native_pair.py) |
| [test_v280_consumable_item_use_spell_source.py](../../tests/test_v280_consumable_item_use_spell_source.py) | [test_v281_consumable_simc_relation.py](../../tests/test_v281_consumable_simc_relation.py) | [test_v281_physical_native_item_binding.py](../../tests/test_v281_physical_native_item_binding.py) |
| [test_v285_consumable_weapon_source.py](../../tests/test_v285_consumable_weapon_source.py) | [test_v286_representative_oil_source_binding.py](../../tests/test_v286_representative_oil_source_binding.py) | [test_v287_zero_history_v222_user_budget_bridge.py](../../tests/test_v287_zero_history_v222_user_budget_bridge.py) |
| [test_v288_no_redundant_g_native.py](../../tests/test_v288_no_redundant_g_native.py) | [test_v289_retail_live_build_source.py](../../tests/test_v289_retail_live_build_source.py) | [test_v294_dk_runeforge_selection.py](../../tests/test_v294_dk_runeforge_selection.py) |
| [test_v295_season_runeforge_source.py](../../tests/test_v295_season_runeforge_source.py) | [test_v296_pinned_oil_static_rating_source.py](../../tests/test_v296_pinned_oil_static_rating_source.py) | [test_v297_sealed_simc_oil_gear_delta.py](../../tests/test_v297_sealed_simc_oil_gear_delta.py) |

## 2026-11-10 P2 experimental delta (not included in historical counts)

| Runner | Role |
|---|---|
| [v298_adaptive_percent_grid.py](../../runner/v298_adaptive_percent_grid.py) | Adaptive percentage-grid candidate generation |
| [v299_multiregion_percent_policy.py](../../runner/v299_multiregion_percent_policy.py) | Multi-region percentage policy |
| [v300_multiregion_throughput_resolution.py](../../runner/v300_multiregion_throughput_resolution.py) | Throughput/resolution research |
| [v301_nested_multiregion_policy.py](../../runner/v301_nested_multiregion_policy.py) | Nested 11→21→41 candidate policy |
| [v302_weak_multiregion_zoom.py](../../runner/v302_weak_multiregion_zoom.py) | Global shortlist and local-six geometry |
| [v303_adaptive_region_resource_policy.py](../../runner/v303_adaptive_region_resource_policy.py) | Adaptive radius/scout allocation and fair-comparison contract |
| [v305_grid_pairwise_adaptive_hybrid.py](../../runner/v305_grid_pairwise_adaptive_hybrid.py) | v302 six-grid + v290 pairwise, v304 resource/radius, opt-in | 
| [v304_v303_durable_adapter.py](../../runner/v304_v303_durable_adapter.py) | Durable stage/region adapter for v291 opt-in |
| [p2_new_profile_product_e2e_once.py](../../integration_probes/p2_new_profile_product_e2e_once.py) | Fresh v113/v216/v212/v098 normal 4-gem E2E pilot |
| [p2_real_hybrid_v305_once.py](../../integration_probes/p2_real_hybrid_v305_once.py) | Scoped real SimC hybrid equal-iterations replay, exact historical SHA | 
| [p2_real_equal_v304_once.py](../../integration_probes/p2_real_equal_v304_once.py) | Bounded one-shot historical-SHA real Native comparator (integration_probes) |

| Tests | Coverage |
|---|---|
| [test_v298_adaptive_percent_grid.py](../../tests/test_v298_adaptive_percent_grid.py) | Existing v298 regression |
| [test_v299_multiregion_percent_policy.py](../../tests/test_v299_multiregion_percent_policy.py) | Existing v299 regression |
| [test_v300_multiregion_throughput_resolution.py](../../tests/test_v300_multiregion_throughput_resolution.py) | Existing v300 regression |
| [test_v301_nested_multiregion_policy.py](../../tests/test_v301_nested_multiregion_policy.py) | Existing v301 regression |
| [test_v302_weak_multiregion_zoom.py](../../tests/test_v302_weak_multiregion_zoom.py) | Existing v302 regression |
| [test_v303_adaptive_region_resource_policy.py](../../tests/test_v303_adaptive_region_resource_policy.py) | New adaptive resource/budget-contract regression |
| [test_v305_hybrid_durable_offline.py](../../tests/test_v305_hybrid_durable_offline.py) | v305 durable/geometry/cancel/resume regression | 
| [test_v098_cross_spec_installed_G_source.py](../../tests/test_v098_cross_spec_installed_G_source.py) | Cross-spec source seal, same-spec retention, different-spec fallback |
| [test_p2_fresh_user_profile_case_offline.py](../../tests/test_p2_fresh_user_profile_case_offline.py) | New independent-spec case selected no-Native preflight |
| [test_p2_v305_hybrid_offline.py](../../tests/test_p2_v305_hybrid_offline.py) | v305 32+32+4 real pilot pure offline preflight | 
| [test_v304_v303_v291_bridge_offline.py](../../tests/test_v304_v303_v291_bridge_offline.py) | New opt-in Native-fake integration / cancel / resume / pending guard |
| [test_p2_real_equal_v304_offline.py](../../tests/test_p2_real_equal_v304_offline.py) | New no-Native 32+32+4 comparator preflight |

## 역사 원문 찾기

기존 날짜별 메모는 [개발 노트 디렉터리](notes/), 인계는 [docs 디렉터리](../), 길어진 상태는 [원본 CURRENT](../CURRENT_PRODUCT_DEVELOPMENT_STATE.md), 이번 정리 전 전체 기능 표는 [역사 INDEX](HISTORICAL_INDEX_20261110_PRE_KNOWLEDGE_LAYER.md)에서 검색한다.

**원본 코드·테스트의 연관성은 실제 import/호출·receipt를 확인해야 확정된다.** FILE_INVENTORY를 별도 증명 Gate로 삼거나 매 변경 시 전수 재생성을 강제하지 않는다.
