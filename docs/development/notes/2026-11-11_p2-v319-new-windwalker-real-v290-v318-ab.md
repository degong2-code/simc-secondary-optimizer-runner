# v319 신규 풍운 수도사 프로필 기반 v290/v318 Native A/B — 실행 계약

- **Capability:** `PRODUCT.E2E`, `OPTIMIZER.POLICY`, `DEV.CONTINUITY`.
- **Keywords:** v319, new Windwalker Monk, auto G/J/F/O/T, v216, v212, v098, real Native, v290/v318 35/320.
- **Prior evidence:** [First auto-T Action #42939598332](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42939598332) offline 43 PASS/1 ERROR, Native SKIPPED; [ledger #42939598253](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42939598253) failed.
- **Decision:** `CONNECT` current environmental budget Build to a genuinely new Monk/Windwalker generated profile, share that exact profile between v290/v318; do not insert manual T.
- **Changes:** New case T=null; verification that generated context B/T equal environment G+J+F+O; 64 Native per arm planned, separate exact archives.
- **Verification:** [v319 #42940793935](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42940793935) 44/44 focused PASS, real new environment READY (3 Native, G2850/J92/F165/O0/T3107, original manifest SHA); Web prepare HTTP422 on per-invocation Native request64 > API cap32; no new profile/DPS A/B. Common ledger [#42940793969](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42940793969) SUCCESS.
- **Remaining:** Limit only Web prepare batch to32, preserve v291 direct64/arm, rerun fresh source profile/Native and confirm original 320 DPS/SEM with source SHA.
- **Efficiency:** Reuse valid season source/pinned SimC binary; new user profile per campaign, no old completed profile or DPS cache; main/v290 unchanged.

- **사용자 직접 승인:** 모든 후속 실제 Native 알고리즘 비교에서 새로운 **전문화 사용자 프로필을 환경 구축 엔진 v113→v216/v217→v212→v098으로 직접 생성**한다. 역사 완성 프로필·최고 CHMV·DPS 결과는 입력에 주입하지 않는다. 단일 실험 내 v290/v318은 동일 새 profile SHA 사용.
- **이번 신규 전문화:** `monk/windwalker` (풍운 수도사), v313 4전문화 및 v314 8전문화 어디에도 없는 대상. 인간, ilvl334, **수동 T 미지정(final_T=null)**, 환경 구축에서 계산된 **자동 T=G+J+F+O**, 보석 일반4/특수 없음, Oil0, 치/가/특/유 최종 상한45%, 단일 타깃300초, 기본 제공 특성·장신구. 실제 제품 사용자 source controls 및 검증된 시즌 데이터 사용. 기존 70783 source/Native 프로필 파일 재생·재사용 아님.
- **구현:** [한 번만 실행되는 source-first A/B](../../../integration_probes/p2_v319_new_windwalker_v290_v318_real_once.py); 64 Native/arm, 총128 최대; 각각 35 scout/320 confirm, v316 timing optin. `v291` 별도 seal/cache-only 재생 0 new Native, 각 arm 원본 input·JSON2·journal·timing ZIP 보존 7일. 환경 G/J/F/O 실 Native 상한3, 일치 확인 후 동일 `context` 재사용. current season live build drift·인증정보 미비 시 원문 차단.
- **공정 비교:** 양쪽 Native 호출수 동일과 **실제 총 iterations 동일 여부**를 별도로 검사한다. 상태가 다르면 절대 같은 계산 예산의 우위로 해석하지 않는다. 양쪽 320 최고 DPS±SEM·CHMV·실제 실행시간·원본 SHA·명목95 및 탐색후 최고선택 편향 한계를 보존. 단일 신규 전문화라 26 DPS 일반화/전역 최적/제품 승격 불가. 추가 비교가 필요하면 다음에도 *또 다른 신규 전문화 프로필*을 생성한다.
- **증거 상태:** 코드·시나리오·오프라인 가드 및 push-trigger [Actions 워크플로](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/workflows/p2_v319_new_windwalker_native_ab_once.yml) 등록 예정. 이 노트는 **실제 실행/성공/Native PASS 증거가 아님**. Actions run ID·job 상태·artifact 원본을 조회 후 결과 업데이트.
- **효율:** v290 원형 유지, 추가 120 iterations 단계 없음, 원본 26/1008 전수 재실행 없음. v318 실효성은 선행 focused synthetic PASS + 새 전문화 독립 Real A/B 이후 판정.

- **2026-11-11 사용자 정정(이전 v319 T3450 계획 철회):** 임의로 더한 +343 rating은 실제 시즌·풍운 수도사 예산 근거가 없으므로 자동 실험에서 제거. 프로필과 v291 세션을 만들기 전 `verified_automatic_T()`로 정확한 환경 Build 산출 `G/J/F/O/B/T`를 검증하고, 사용자 controls의 `final_T=null`, 생성 세션 원본 user target도 `null`, 실제 승인 `approved_final_T=env["T"]`와 `base_B=env["B"]`를 반드시 대사. **실제 풍운 수도사 자동 T 숫자는 Build 완료 전 미확정**이며 과거 Ret G2850과 동일하다고 가정 금지. 새 실험 ID `windwalker_monk_4ordinary_auto_T`, 신규 루트·아티팩트로 T3450 과거 계획과 분리. 증거 미확인 시 실 Native PASS 미주장.

- **HTTP422 최소 교정:** v113 `LongRunPrepareRequest.max_new_native_this_invocation`의 정규 상한은32. v319 제품 프로필 준비 요청만 `min(64,32)`로 수정하며, 기존 64 Native/arm 연구 실행 예산 및 사용자 API 상한 자체는 변경하지 않는다. 환경 원본 G2850/J92/F165/O0/T3107은 이번 환경의 대표 장비 기준 관측치이며 전 전문화 정확 G라고 주장하지 않는다.
