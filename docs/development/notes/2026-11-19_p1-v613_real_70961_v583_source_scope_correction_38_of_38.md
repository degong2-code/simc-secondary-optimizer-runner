# P1 v613 — 70961 실제 Wago/SimC 영구 마부 원본 38/38 회복 (2026-11-19 KST)

## 실제 최초 차단과 최소 수정

- 이전 [실 v612 원본 #44427767262](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44427767262), compact artifact **14485107707**의 실제 결과: `v254/v280/v281/v275/v256` 모두 **EXE­CUTED_AND_SEALED**, 그러나 `v583.reason=V583_EXISTING_SEALED_SOURCES_OR_EXPANSION_PENDING`, 직접 전달받은 `expansion_id=None`, v583 HTTP0·Native0. 따라서 소비품 `v281` 설계를 제거하거나 새로운 효과 인증 Gate를 만들 이유가 없었다.
- 원본 `runner/v216_environment_build_coordinator.py::_join_authenticated_season_source`는 실제 `v163`에서 검증한 `scope`를 **외부의 `source_scope`**로 내보내고, 봉인된 내부 v163 JSON의 필드만 `auto_source_scope`이다. 기존 v190 소모품 단계도 `linked.get("source_scope")`를 사용한다. **v583 호출 한 군데만 존재하지 않는 외부 `auto_source_scope`를 읽어 확장팩을 누락**했다.
- **코드 `59e5ab545cef2d8e12b50eaec8db63a2c5137317`:** 이 원본 속성만 `_original_v163_enchant_expansion_id(linked)`를 통해 v583에 전달. 하드코딩 확장팩 ID, 수동 원본 증명, 인증·예산·시뮬레이션 정책 변경 **없음**.
- **테스트 `47c8f71b07f93f8c94166dc25484a8e8beeb7fd4`:** 기존 `tests/test_v216_environment_build_coordinator.py`에 원래 public source_scope=11을 사용하고 내부 auto_source_scope=999와 혼동하지 않으며 missing scope는 None 반환하는 focused 회귀 추가. 기존 [v583 offline #44428330050](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44428330050) **SUCCESS**.
- compact 진단 출력도 실제 외부 source_scope를 읽도록 `integration_probes/p1_v612_v583_original_source_first_blocker.py`를 별도 교정(`3ccf77c3`). 이 출력 수정은 v583 source/proof 승인 로직에 영향을 주지 않는다.

## 동일 빌드 실제 원본 검증 성공

- 수정 후 **실 Wago 12.1.5.70961 + 정확 SimC source SHA `9933ffb946fb55b1fa66657b848f519ac19006e1`**를 사용하여 [v613 실제 source-only run #44428472283](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44428472283) **SUCCESS**, compact artifact **14484739115**를 다운로드해 실제 JSON 확인.
- `v583.status=PERMANENT_ENCHANT_EXACT_WAGO_SIMC_SOURCE_ONLY`, `v583_first_blocker=null`, 정상 봉인 `stage_status=EXECUTED_AND_SEALED`, stage receipt SHA `20cbe7a7032a824c736a4aebad7e7e30ae0bc7b7eaf828ec15e96eef01dc7a08`.
- **최고 품질 SimC 마부 계열 38/38** 정확 Wago 물리 ID 연결, **원본 품질별 마부 ID 76/76**, 물리 item IDs **76**, `highest_simc_candidate_missing_ids=[]`. 추가 SimC 토큰 비-기본 후보 8계열은 별도 unadmitted source-only 유지.
- 신규 원본 source collector 네트워크 호출 단계 계수 **52**, **Native 0회**, 사용자 DPS **0회**, `actual_enchant_ui_promotion=false`. v583 실제 original *source-only* PASS와 제품 Policy A 최종 `product_input`·v212 설치·사용자 SimC DPS 검증은 반드시 구분.

## 이어지는 제품 검증

- [v614 정식 실제 70961 Windows M1/M2·v212 자동 마부 등록 #44428820907](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44428820907)은 정확 원본 CLI를 빌드하여 70961 G/J/F/O와 새 v583 실물 품질 근거를 **정식 설치 경로로 전달**하는 1회 범위 실행. 이 문서 작성 시 등록 건수/성공 여부는 미확정이므로 과장 금지.
- 등록 PASS 시 정확 선택 부위·final item ID·SimC `enchant_id` 1회·새 사용자 DPS/SEM/95%/캐시만 후속 확인. 사용자 목적은 26 DPS 미래 절대 rating 최적화, 마부 효과 인증·장비 DB 개발이 아님.

**권한·통계:** 격리 브랜치만 수정; 기존 `15/78 COMPLETE`, `full_product_e2e=PENDING`, main/immutable/Project UI/공식 Work OS/기존 주 제품 개발 채팅 권한 불변.
