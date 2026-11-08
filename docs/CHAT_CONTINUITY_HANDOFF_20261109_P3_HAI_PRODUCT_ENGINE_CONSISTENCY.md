# SIMC SECONDARY OPTIMIZER — P3-HAI 단일 최신 인계 (2026-11-09)

**지위:** P3-HAC의 2026-11-09 *과거 복원 시점*을 대체하는 **최신 GitHub 격리 개발 연속성 인계**. 본문은 제품/정책 승인 문서의 변경, `main`/v003 immutable/Project UI/Work OS 승격이 아니다. 새 채팅은 **첫 응답에서 읽기 전용 복원·검증 보고 후 중단**하고, 사용자가 별도 `진행`이라고 하기 전 코드·문서 수정, CI/Actions/Native/수집, 커밋·병합·승격을 시작하지 않는다.

## 1. 최초 복원할 단일 기준과 순서

- 저장소: `degong2-code/simc-secondary-optimizer-runner`, 격리 브랜치 `probe/chat-cache-v035-20261024`. **작성 직전 실제 HEAD**: 격리 `672891afe458771124b27606b6f92372cf4962ea`; `main` `07133e0aaf738d6e4816a6486057b1cd49c018de`. **이 인계 자체를 커밋하면 격리 HEAD는 새 값**이므로 두 HEAD는 **독립 재조회**한다.
- **읽기 순서:** ① 격리와 main HEAD 독립 확인 → ② 본 최신 인계 → ③ [P3-HAI 단일 제품 판정표](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md) → ④ [PROTOCOL](development/PROTOCOL.md) 최상단·[INDEX](development/INDEX.md)의 A~G/OPTIMIZER.POLICY/PRODUCT.E2E/SOURCE.SEAL·[CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) 상단 → ⑤ [승인 v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md)와 최신 사용자 직접 결정 → ⑥ 이 인계에 나온 코드/영수증만 필요한 범위에 좁혀 확인. 전체 수백 역사 노트/이전 인계 재감사 금지.
- **권위:** 최신 사용자 직접 결정 > 최신 승인 비충돌 v1.4.3/v1.4 계열 > GitHub 실제 코드·Actions·Native/정확 SHA > 과거 CURRENT 항목/옛 인계. 기존 [P3-HAC](CHAT_CONTINUITY_HANDOFF_20261109_P3_HAC_MULTISCALE_ENGINE_RESTORE.md)의 `>6 Native 미실행`·`웹 연결 미완료`는 **그 작성 당시**만 해당. 현재 8+2 Native 실증/웹 오프라인 연결로 갱신됨.

## 2. 목표와 이미 구축된 엔진

**하나의 제품:** 지원 **DPS 26개 전문화**(증강·탱커·힐러 제외)의 목표 ilvl(기본334)/수동 최종 T를 기준으로 SimC DPS가 높은 **CHMV 절대 rating**을 탐색. 사용자 현재 장비 재분배/장비 추천이 아님. 일반 장비·무기·티어4/주스탯/SimC 실행 프로필 내부 생성. 사용자 입력은 캐릭터·특성, 목표, 장신구2, 선택 특수장비/장식 최대2, 보석·영약·기름·소모품/전투·선택 모듈. SimC 프로필 업로드는 캐릭터/특성 읽기용 선택 사항. **SimC가 효과·proc/APL·DPS 책임**, 독립 효과 확인 Gate 없음.

회계 `B=G+J+F`, `T=B+O`; 수동 T 우선, O는 고정·비자유분배, L/E/G 및 장신구/제작장비 이중 계산 방지. 최종 `c_final[s] < T/2` 엄격 적용. 특수1+일반4 보석, 선택 보석 효과 확인은 SimC에 맡긴다. 표시 95%만, 관측 1순위 ≠ 전역 최적 증명. 동일 시즌 정적 캐시와 실제 바이너리/프로필/옵션/iteration별 DPS 캐시 분리.

**현재 2대 핵심 남은 과제:** (1) 일반 사용자 로컬 웹의 **실제** Start/Status/Cancel/Resume/결과 E2E 완결, (2) 기존 다해상도 적응형 최적화의 **동일 CPU/Native 예산 대비 품질·통계·종료 조건 개선**. 시즌 G/J/F/O 환경 구축 엔진은 이미 구현되어 있으므로 신규 독립 대형 엔진 개발로 재시작하지 않는다. 미래 새 시즌에서 기존 원본 공급이 실제 충분한지는 **범위별 별도 실증**이고 필요한 연결만 증분 보완한다.

## 3. 최신 확인된 기능·Actions 증거 한 장

| 구간 | 구현/실증 | 증거 및 **비지원 주장 경계** |
|---|---|---|
| 시즌 Build 및 G/J/F/O→B/T READY | `v216/v222/v212/v217`, 70783/334/Ret **G2850 J92 F165 O0 B=T3107**, G1/F2 환경 Native3 | [실 #42460255527](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42460255527) PASS. 새 시즌 자동 수집 전과정·모든 전문화 READY **미실증** |
| 26 전문화/목표 레벨 대표 프로필 | 26/26 물리 SimC 수용, 26×5=130 offline plan, 별도 6 전문화×6후보 Native36/캐시36 | [실 #40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357), [실 #40980268952](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40980268952). 26/26 장기 탐색 E2E라 주장 금지 |
| 기존 사용자 적응형 v094 | Ret/Enh 현재 시즌 각 6 실제 DPS Native | [Ret #42466284163](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42466284163), [Enh #42472633337](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42472633337) |
| 장기 적응형 v290/v291 | 8 scout(35 iteration) +2 confirm(320 iteration), 4+6 재개, SHA replay0 | [실 HAE #42501052586](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42501052586), 원본 artifact 13625920302 · inner SHA `c53dc09015377ccaf3d53f24bb85950e3999efacecc629be756b9f8856ef5fa9` |
| 선택쌍 95% | Enh 1위 185438.66±280.54 SEM, 확인 상대 182070.77±302.13, 차3367.90/반폭808.08, 실 시드 서로 다름 | [HAF #42501776798](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42501776798). **선택쌍 정상근사만**, 다중선택 편향/전역 최적 미증명 |
| v292 교차 Actions 캐시 이식 | 과거 Native10 재인증하여 **신규 DPS Native0**, 새 환경 G/F Native3 별도 | [실 HAG #42504040076](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42504040076), 영수증 artifact 13627110458. 장기간 여러 ZIP 자동 병합은 별도 |
| v113/v293 로컬 웹 제품 | opt-in 장기 세션 준비/시작/상태/취소/재개/캐시-only/import/result, 기존 6회 UI 보존 | [최신 focused #42506549262](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42506549262) **483 PASS/2 SKIP/Native0**, [HTTP Linux+Windows #42506293553](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42506293553) **각233 tests PASS**. **웹 버튼에서 실제 장기 SimC Native 수행은 아직 미실증** |

## 4. 개발 지속성: 다음에 손댈 파일·회수할 근거

- 환경/정적 owner: `runner/v216_environment_build_coordinator.py`, `runner/v222_season_budget_contract.py`, `runner/v212_environment_manifest.py`(파일명 정확 확인; `v212`에 설치 표시), `runner/v217_stage_execution_engine.py`, `runner/v271_user_socket_gem_layout.py`, 정책 A `v220/v196`. [환경 입력 책임표](development/ENVIRONMENT_BUILD_INPUT_SCOPE_20261104.md).
- 사용자/제품: `runner/v106_user_session_controller.py`, `runner/v113_local_web_api.py`, `runner/webui/index.html`/`app.js`, `runner/v098_target_user_scenario_bootstrap.py`, `runner/v096_unified_product_entry.py`.
- 최적화/캐시: `runner/v290_multiscale_adaptive_policy.py`, `runner/v291_durable_multiscale_native_runner.py`, `runner/v292_portable_native_case_cache.py`, `runner/v293_local_longrun_session.py`, 기존 `v093/v065/v091`.
- 최근 영수증·노트: [HAH](development/notes/2026-11-09_p3-hah-local-longrun-product-web-integration.md), [HAG](development/notes/2026-11-09_p3-hag-exact-portable-native-case-replay.md), [HAE](development/notes/2026-11-09_p3-hae-short-budget-precision-contract.md), [HAF](development/notes/2026-11-09_p3-haf-native-seed-provenance-recovery.md), [HN](development/notes/2026-11-08_p3-hn-real-gjfo-ready-one-case.md). 각 범위의 기존 테스트/Native SHA만 재사용하며 무조건 전수 CI/Native 실행 금지.
- 각 수정: source/정적/Native 호출·중복·메모리·I/O·iterations/CPU-second·캐시 identity를 확인. 실제 SHA·스탯별 하한/최종 <50%·단일 사용자 세션·95% 판단 범위를 유지. 결과는 `IMPLEMENTED`, `OFFLINE_PASS`, `REAL_NATIVE_PASS`, `HISTORICAL_REUSED`, `NOT_TESTED`, `BLOCKED`를 구분해 기록.

## 5. 권한 및 다음 단계 경계

- 기존 **주 제품 개발 채팅**이 일반 제품 구현·실 SimC 시험 소유권 유지. 격리 브랜치의 읽기/승인된 개발은 별도 범위. **`main`, v003 immutable, 원본 제품 v016, 공식 Project UI Sources/Instructions·Work OS M0/Shared State·승격은 승인 없이 변경 금지**. WEQUIP 운영 authority/영구 runtime 의존성 도입 금지.
- 다음 효율 최선: 검증된 동일 시즌 빌드와 기존 프로필/정적 캐시를 활용한 **실 로컬 웹 장기 세션 1건**으로 Start → 4 Native 이내 → Status/Cancel/Resume → replay/cache-only/결과를 점검; 그다음 동일 비용 대비 v290 개선을 측정. **새 시즌 자동 DB 엔진을 다시 만드는 것은 불필요**. 실 실행이 가능한지·실제 변경이 있는지 확인한 뒤 최소 Native만 승인된 범위로 실행.

## 6. 새 채팅 시작 프롬프트 — 그대로 사용

> SIMC SECONDARY OPTIMIZER 프로젝트를 **읽기 전용으로 독립 복원**하라. GitHub `degong2-code/simc-secondary-optimizer-runner` 격리 브랜치 `probe/chat-cache-v035-20261024`. 최신 단일 인계 `docs/CHAT_CONTINUITY_HANDOFF_20261109_P3_HAI_PRODUCT_ENGINE_CONSISTENCY.md`와 최신 판정 `docs/PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md`. **격리/main 실제 HEAD를 각각 독립 조회**하여 문서 작성 직전 기준 및 최종 인계 커밋과 비교하라. 읽기 순서: P3-HAI 인계 → P3-HAI 제품 상태 → PROTOCOL 최상단 → INDEX 기능 A~G/OPTIMIZER.POLICY/PRODUCT.E2E/SOURCE.SEAL → CURRENT 상단 → 최신 승인 v1.4.3·직접 사용자 결정 → 관련 코드·Actions/Native 영수증만 선택 확인. 과거 P3-HAC 이하 작성 당시 PENDING을 최신 상태로 오해하지 않는다. 제품 목표: **26 DPS 전문화·미래 목표 ilvl/수동 T 기준 최종 절대 CHMV**, 자동 시즌 G/J/F/O·B/T·L/E/O 소유권/엄격 각 rating <50%, SimC 효과/DPS 책임, 글로벌/다중 선택 95% 과장 금지. 이미 구현된 시즌 환경 엔진을 다시 시작하지 않으며 남은 두 축은 **실 로컬 웹 E2E 검증·완성** 및 **기존 v290/v291의 Native/CPU 비용 대비 탐색·통계 품질 개선**이다. 이전 10 Native 실측/교차 job 새 DPS0 캐시와 26개 물리 Native 증거를 범위에 맞게 재사용. 첫 응답은 **현재 HEAD, 실증별 완료/미완료, 로드맵·가장 효율적인 다음 작업**을 간결히 보고한 후 중단. **내가 별도로 '진행'이라고 하기 전 코드/문서 수정·수집·Actions/CI/Native/테스트·커밋/병합/공식 승격 금지.** 주 제품 개발 채팅의 소유권과 main/v003/Project UI/Work OS 권한을 보존한다.
