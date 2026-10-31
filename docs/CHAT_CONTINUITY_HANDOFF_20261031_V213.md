# SIMC SECONDARY OPTIMIZER — 2026-10-31 v213 P3-B 정본 인계

**문서 목적:** v212 P3-A Environment Manifest 상태에 v213 P3-B 실제 source-to-catalog 구현과 검증 영수증을 이어 붙인다. 과거 전체 재감사나 제품 재시작 없이 P3-C로 진행하기 위한 최소 읽기 순서와 시작 프롬프트를 제공한다.

**인계 상태:** P3-B 코드·테스트·workflow는 격리 브랜치에서 구현 및 실제 source-backed Actions 검증을 통과했다. P3-B는 source-to-catalog bridge이지 사용자 원클릭 Environment Builder 완성이 아니다. main, immutable v003, 원본 v016, Project Sources/Instructions UI, repository visibility, 공식 Work OS authority는 변경하지 않았다. 새 채팅은 복원·검증 보고 후 사용자의 **진행**까지 대기한다.

## 0. 저장소·정책·HEAD

- Repository: degong2-code/simc-secondary-optimizer-runner
- Branch: probe/chat-cache-v035-20261024
- P3-B 구현/검증 당시 HEAD: 29d985a999293adb3132a27c83ecf26602b217c8. 이 인계 문서 커밋은 HEAD를 이동시키므로 새 채팅은 실제 branch HEAD를 다시 읽는다.
- Repository visibility 확인값: Public. 이번 작업에서 변경하지 않았다.
- 확인 당시 main HEAD: 07133e0aaf738d6e4816a6486057b1cd49c018de. main에는 쓰지 않았다.
- 유효한 제품 범위: **DPS 26개 전문화**. 증강 기원사·탱커·힐러 제외. v1.4.1 최초 업로드본의 27개/증강 포함은 범위 오기다. v1.4.2 addendum과 2026-10-31 사용자 직접 결정이 우선한다.
- 목적: 목표 ilvl(기본 334) 또는 사용자 수동 최종 CHMV T 기준으로 미래 파밍 목표가 될 치명/가속/특화/유연 최적 절대 rating을 기존 SimC DPS로 탐색. 현재 장비 재분배나 장비 조합 추천이 아니다.

## 1. 실제 P3-B 구현

### 1.1 데이터 흐름

`v191 → v211 → v213 → v196/v197`의 단일 요청형 workflow를 만들었다.

- v191: 511 gear candidate rows의 exact InventoryType/class/subclass masks, 13 class/65 tier IDs, 192 food/61 potion item candidates, related-source counts, gear/tier/budget/v189/v190 input JSON SHA256, SimC generated permanent-enchant/temporary-enchant/gem-property file SHA256를 보존한다.
- v211: current-season enchant candidates를 별도 고정 38-row JSON에서 읽지 않고 v191 artifact의 38 current-season rows에서 직접 받는다. SimC DBC/spell/handler source로 분류한다. 기존 runtime manifest는 compatibility/evidence boundary로 유지하며 현재 후보 source는 v191이다.
- v213: ID/token/quality rank/item class/inventory mask/subclass mask exact join, source-mask slot derivation, source SHA provenance, deterministic manifest digest를 가진 versioned artifact를 생성한다. Gear slot group은 정확 InventoryType에서만 도출한다. Unknown은 pending으로 남긴다.
- v196/v197: v213 artifact를 명시 path로 읽고 classification rows를 적용한다. Classification과 user approval은 분리한다. 기존 사용자 승인 7967만 selectable, 8025 developer-only, 나머지 36개 locked. 자동 UI promotion 없음.

### 1.2 코드·테스트

- runner/v191_unified_season_data_update.py
- runner/v211_enchant_source_effect_classification.py
- runner/v213_source_to_catalog.py
- runner/v196_current_season_user_catalog.py
- runner/v197_enchant_effect_families.py
- tests/test_v191_unified_season_data_update.py
- tests/test_v211_enchant_source_effect_classification.py
- tests/test_v213_source_to_catalog.py
- tests/test_v196_current_season_ui_catalog.py
- tests/test_v197_enchant_effect_families.py
- .github/workflows/v191_unified_season_data_update.yml
- .github/workflows/v211_enchant_catalog_integration_offline.yml

### 1.3 실제 source-backed 증거

- [P3-B source pipeline #41169754323](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41169754323): SUCCESS, commit 29d985a999293adb3132a27c83ecf26602b217c8.
- [Artifact #13031015315](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41169754323/artifacts/13031015315): v191 source catalog + v211 classification + v213 normalized catalog, 93,908 bytes compressed, 7-day retention.
- v213 manifest SHA256: `b888123728097371705c037ae2fc0085cc6735fac870f000b7606b1428d5ced5`.
- Actual counts: 511 gear rows, zero unknown current gear slot groups; 13 classes/65 tier IDs; 192 food and 61 potion candidates; 38/38 current-season enchant classifications; 20 embellishment/effect registrations (actual item ID/slot unresolved); 117 temporary-enchant source rows; 2,409 gem-property rows (actual gem item IDs unresolved).
- Exact gear slot groups: back12, chest40, feet35, finger18, hands33, head40, legs32, neck11, shoulders33, trinket63, waist34, weapon_off_hand10, weapon_one_hand60, weapon_ranged15, weapon_shield10, weapon_two_hand37, wrists28.
- Enchant groups: boots3, chest4, helm6, ring9, shoulders6, weapon10.
- [Cross-platform catalog integration #41169754402](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41170184299): Ubuntu 24.04 **62/62 PASS**, Windows 2022 **62/62 PASS**, including six v213 contract tests.
- #41169754323: v191 focused **6 tests PASS**, integrated Ubuntu stage **22 tests PASS**, real v191→v211→v213→v196 handoff PASS, existing 7967-only approval boundary PASS.
- New SimC Native calls 0; SimC binary builds 0; optimizer/cache mutation 0. The Actions workflow downloads the existing v189/v190 source artifact and exact pinned SimC source files. v191/v211/v213 compilers themselves are network0.

### 1.4 Scope boundaries and remaining limitations

- v213 marks all candidates nonselectable. v196 applies the existing evidence and exposes only 7967. No new user approval was granted.
- v196 can consume the v213 artifact by explicit path, but its default checked-in data path is not yet switched and the v213 artifact is not yet bundled into the Windows beta.
- v212 Environment Manifest does not yet consume v213 directly.
- Embellishment effect registrations do not resolve exact item IDs/slots; temporary enchants do not resolve exact weapon-hand applicability; gem-property rows are not gem item IDs.
- This is not the user-facing Build API/UI, not all-26 profile assembly, not optimizer E2E, and not a claim that the Environment Builder is complete.
- No new Native or old Native/cache evidence was rerun or invalidated.

## 2. P3-A status and next work

P3-A v212 remains an internal deterministic Environment Manifest assembler. [#41160002104](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41160002104) passed 9/9 tests on Ubuntu and 9/9 on Windows using synthetic fixtures/dummy binary, Native0. It does not yet consume v213 directly. Known hardening gaps remain:
- bootstrap_sha accepted but unused; document or correct normalized provenance.
- selectable_count==1 is checked, but v212 must assert exact approved enchant ID 7967.
- current-season 38 candidate/1 selectable constants remain pinned.
- v208 selected-L receipt is not yet a separate explicit v212 manifest input.
- no production dependency-graph invalidation/orchestrator.

**Next implementation:** connect v213 as an explicit v212 Environment Manifest input, bind exact 7967 approval and source digest, and retain relocation-stable provenance. Then connect the approved catalog selection into v098 representative profile assembly, reuse v208 selected-L acquisition and existing CHMV bridge, and feed the sealed profile to the existing v093/v094/v095 optimizer. Do not build another optimizer or repeat all-26 Native matrices. The 26 DPS suppliers must remain exactly the approved scope.

## 3. Required reading order for the next chat

1. Read-only verify current repository visibility, actual branch HEAD, main HEAD, and latest Actions.
2. This handoff in full.
3. docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md top section.
4. docs/DEVELOPER_NOTES_v1.4.2_LATEST_USER_POLICY_ADDENDUM_20261030.md §1 and latest user-policy sections.
5. docs/P3_ENVIRONMENT_BUILDER_TARGET_ARCHITECTURE_20261031.md §7–9.
6. For P3-B only: v191/v211/v213/v196/v197 code and tests listed above; inspect actual Actions #41169754323 logs/artifact and #41169754402 Ubuntu/Windows logs.
7. For P3-A hardening/P3-C only: runner/v212_environment_manifest.py and its tests/workflow, then only the v098/v208/v046/v062/v093/v094/v095 interfaces required for the exact selected path.

Do not repeat unrelated Native evidence or the entire historical project audit. Distinguish implementation, newly executed PASS/FAIL, reused historical evidence, and unimplemented work.

## 4. Start prompt for a new chat

You are continuing the existing SIMC SECONDARY OPTIMIZER product development on the isolated branch probe/chat-cache-v035-20261024.

First response: restore and verify the actual latest HEAD, repository visibility, main HEAD, and latest Actions; read this handoff, CURRENT top, v1.4.2 policy, and P3 architecture §7–9. Report current P3-A/P3-B implementation and exact evidence, known limitations, and the next P3-C task. **Do not implement, edit files, run Actions, run Native, deploy, merge main, change repository visibility, or modify Project Sources/Instructions until I say “진행”.**

The approved product scope is exactly 26 DPS specializations excluding Augmentation Evoker, tanks, and healers. Reuse existing v191/v211/v213/v196/v197 and existing profile/budget/optimizer components. P3-B actual source-to-catalog E2E is complete for its current-season artifact, but v212 does not yet consume v213; the default UI data path and Windows package are not switched; all-26 profile assembly and Windows one-click Build/Start are incomplete.

Preserve CHMV ownership, SimC effect/proc/APL/DPS responsibility, 95% statistical display, 7967-only existing user approval, and Native/cache reuse. Unknown data is UNKNOWN/PENDING, never zero. Prefer minimal dependency-aware changes and focused cross-platform tests; do not repeat valid source/Native/cache evidence.

No main/v003/original v016/Project UI/official Work OS authority or repository visibility changes without separate user authorization.

---

**END — V213 continuity handoff. Always re-read actual HEAD before continuing.**
