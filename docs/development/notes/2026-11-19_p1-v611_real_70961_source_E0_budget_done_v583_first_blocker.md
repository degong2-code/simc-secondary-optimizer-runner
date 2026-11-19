# v611 — 실 게임 빌드 12.1.5.70961: G/J/F/O 설치 PASS / 영구마부 v583 증거 미충족 (2026-11-19 KST)

**출처와 정확한 실행:** [Actions #44425813732](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44425813732) 실제 Windows 2022 M1/M2, compact artifact **14484258310** `V611_REAL_70961_ENCHANT_ADMISSION_ONE_BUILD.json` 실제 다운로드/내용 확인. `simulationcraft/simc` 공식 소스 정확 SHA **9933ffb946fb55b1fa66657b848f519ac19006e1** ([live] Game data update Build 70961), Windows MSVC+Ninja GUI 제외 CLI 컴파일 **PASS**, 실제 새 바이너리 관측 SHA256 **7b09a251b81d3789d1d00f101bdfc9c727210551a2b734da7c8b9827085b3ee3**. 사전 배포 바이너리 서명이나 기존 70783 binary 재사용이라고 주장하지 않음.

**실 검증:**
- 실제 현재 retail **12.1.5.70961**, M1 현재 빌드의 Myth 목표 **ilvl334** 검증. `original_v161_receipt_sha256=50a2718463cc19b79f8a3a7a85f1d857a207b95dc79e6f633cdc30abb088d156` (독립 원본 빌드 확인).
- 정상 원래 `v113.LocalJobs.build_season_environment → v216/v217/v212` **`environment_ready=true`, `environment_installed=true`, `full_environment_installed_verified_by_v212=true`**. 검증된 해당 실행의 G=**2850**, J=**92**, F=**165**, O=**0**, B=T=**3107**, 원본 installed `manifest_sha256=401e1cbabeca9e639e4d7cadb543f17108adb8280ceebe727332329182478767`; 새로운 G/J/F/O 검증 70961 스코프이며 과거 70783 수치를 신규 시즌 증거라고 복사한 게 아님. M1/M2 환경 Native **6회**, 사용자의 신규 마부 DPS Native **0회**.
- 실제 원래 봉인 `v191/v211/v213` catalog 후보 38건, `source_relation=38`, `simc_input=38`, `chmv_budget=30` (정적 E0 가능한 케이스), **`product_input=0`**. 원래 `v583` = `PERMANENT_ENCHANT_SOURCE_PENDING`, 원본 quality 연결 proof 미생산; `four_family_eligible_ids=[]`, `published_verified_options=[]` (**실 등록 0건**). 현재 첫 차단은 **v583 실제 원본 생산 경로**, 기존 v607/608 effect/품질 numeric 동등성 Gate 아님.
- 38 후보 중 `EXACT_PHYSICAL_SLOT_OR_HAND_RELATION_NOT_VERIFIED=19`, `EVIDENCE_MISSING:chmv_budget=8`, `EVIDENCE_MISSING:product_input=38`. E0 30건이 준비돼도 `product_input`을 대체하지 못함. 무기·반지의 물리 적용은 선택 최종 item/hand와 별도 판정 유지.
- 실행 결과 **`PENDING_REAL_SEASON_ENCHANT_PRODUCT_A_OR_E`**, Actions 전체 workflow FAIL은 테스트의 예상 PENDING 종료 코드(실 환경 M1/M2/SimC 컴파일 성공과 분리). 기본 G/J/F/O의 성공을 마부 등록 0건으로 덮어쓰지 않는다. `full_product_e2e=PENDING`, 공식 원장 **15/78 COMPLETE**.

## 코드 연결상 가능한 첫 원인 — 아직 확인 불가

`runner/v216_environment_build_coordinator.py`의 `v583.collect`는 `wago_stage`, `fresh_gear`, `fresh_item_spell(v280)`, `simc_consumable_relation(v281)`, `pinned_classifier(v275)`, 유효한 `season_join.auto_source_scope.expansion_id`의 봉인 stage를 필수로 읽고, 마지막에 한 개 추가 Wago `CraftingDataEnchantQuality`를 수집한다. 실제 v611 compact receipt에 **`fresh_permanent_enchant_item_source.reason`가 포함되지 않아**, `V583_EXISTING_SEALED_SOURCES_OR_EXPANSION_PENDING`, 소스 누락, `V281...`, 추가 Wago CSV 실패 중 **어느 것인지 결정할 증거가 없음**. 소비품 전용 `v281`은 온유즈 SpellID·전체 SimC item 데이터도 요구하므로, 영구마부용 원본 join을 부당하게 종속시키는지 확인할 가치는 있지만 **원인을 확정하기 전 분리·품질 승인 완화 금지**.

## 다음 최소 작업

1. **Native 없이**, 실제 같은 70961 시즌에서 `v216.collect_wago_new_season_source`의 원래 단계 상태를 추적해 `v583.reason`와 상위 5개 stage 상태를 bounded 영수증으로 남긴다. 원래 데이터/봉인 SHA/출처를 재사용하고 필요한 수집만 실행한다. 원래 stage 전체가 없으므로 동일 시즌 Wago DB2를 다시 요청할 경우 새 요청 비용을 명시한다.
2. 정확한 최초 누락 `v281`·expansion ID·quality table/other가 식별되면 원래 `v583` 물리 join만 좁게 FIX. **완전하고 참인 original source receipts** 없이는 `product_input` 증거를 생성하지 않음.
3. 수정 뒤 실제 70961 source→4 receipt→v212 신규 게시 1건 → 최종 사용자 ItemID→SimC DPS·SEM·95%/캐시·재개는 해당 새 스코프 최소 Native만. 26 DPS 전수/효과 인증/새 엔진 금지.

**권한:** 격리 브랜치만; main/v003/v016/Project UI/M0/Shared State/주 제품 개발 채팅 소유권 불변.
