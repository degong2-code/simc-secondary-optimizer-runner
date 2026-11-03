# 개발 성과 재사용 인덱스 · 2026-11-03

**사용 전:** [필수 선조회·작업 노트 규약](PROTOCOL.md). 이 표는 **동일 문제 재개발 방지용 색인**이며 진실 출처는 링크된 실제 원본·코드·CI/Native 영수증이다. `Evidence`(확립된 사실)와 `Integration`(제품 연결)를 혼동하지 않는다. 키워드 검색 → 해당 evidence 문서 확인 → 최소 변경 결정 순서.

| Capability | Keywords (한·영) | Evidence | Integration | Prior evidence | Last note / next smallest gap |
|---|---|---|---|---|---|
| `TIER.SEASON` | tier, 티어, 시즌구분, season, base ilvl, ItemSet, bonus tree, 197, 219 | `SOURCE_CORROBORATED` | `PARTIAL` | [P3-AQ](../P3_AQ_20261102_TIER_TOKEN_BASE_ILVL_SOURCE_PROOF.md), [P3-AR](../P3_AR_20261102_RAID_BONUS_TREE_TIER_SEASON_CORROBORATION.md), [P3-AT](../P3_AT_20261102_NORMAL_SIMC_SOURCE_INTEGRATION.md) | [P3-BR](notes/2026-11-03_p3-br-tier-evidence-reuse.md): 197/219×65, active-raid 101/118, exact SimC 13×5 재사용; v250/v251 봉인 후보 → v216 정상 대표 출처 연결 진행; 원본 확인과 G는 분리 |
| `GEAR.SEASON` | 장비, 시즌 파밍, WSE, source provenance, 대표 무기 | `SOURCE_PARTIAL` | `PARTIAL` | [P3-BI](../P3_BI_20261103_SELECTED_GEAR_SEASON_PROVENANCE_AND_G_PENDING.md), [P3-BK](../P3_BK_20261103_REAL_WAGO_WORLDSTATE_LOOT_ROW_RESEARCH.md) | [P3-BQ](notes/2026-11-03_p3-bq-continuity-correction.md): 선택 부위만 소스 미확정 여부 확인; WSE 전수 조사 재개 금지 |
| `G.NUMERIC` | G, 대표장비 예산, rating, 334, Native static | `SOURCE_PARTIAL` | `PARTIAL` | [P3-BL](../P3_BL_20261103_ONE_SPEC_V233_G_PROFILE_IN_ORIGINAL_ENVIRONMENT_BUILD.md) | [P3-BS](notes/2026-11-03_p3-bs-standardized-g-budget.md): raw v234 G→nearest10 standard preview, per-ilvl measured-only rows; 실제 시즌 G 출처/실측 미확정 |
| `J.GEM` | 보석, gem, J, gem property, highest quality | `SOURCE_PARTIAL` | `NOT_INTEGRATED` | [P3-BH](../P3_BH_20261103_FRESH_SEASON_GEM_SOURCE_JOIN_IN_NORMAL_BUILD.md) | [P3-BQ](notes/2026-11-03_p3-bq-continuity-correction.md): 최고 품질·소켓/정적 J만 보완 |
| `F.FLASK` | 영약, flask, F, consumable, quality | `SOURCE_UNVERIFIED` | `NOT_INTEGRATED` | [P3-BO](../P3_BO_20261103_PINNED_SIMC_V189_WAGO_V190_CONSUMABLE_STAGE.md) | [P3-BQ](notes/2026-11-03_p3-bq-continuity-correction.md): 음식/물약 후보만 있으므로 영약 F 실제 증거 필요 |
| `O.OIL` | 무기 기름, oil, O, temporary_enchant, hands | `SOURCE_UNVERIFIED` | `NOT_INTEGRATED` | [설계](../SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) | [P3-BQ](notes/2026-11-03_p3-bq-continuity-correction.md): 실제 옵션/적용 손/고정 O 확인, 일반 임시 마부 제외 |
| `BUDGET.GJFO` | GJFO, CHMV, B, T, v222, budget, L, E | `CODE_ONLY` | `PARTIAL` | [P3-BG](../P3_BG_20261103_PREPROFILE_GJFO_ACCOUNTING_BRIDGE.md) | [P3-BS](notes/2026-11-03_p3-bs-standardized-g-budget.md): v222 총합 G 반올림과 J/F/O·L/E·수동 T 계약 연결; 신규 시즌 검증값 및 실제 설치 미완료 |
| `SOURCE.SEAL` | SHA, DB2, v217, 캐시, 중복 해시, source integrity | `CODE_ONLY` | `PARTIAL` | [P3-BP](../P3_BP_20261103_ONCE_ONLY_SOURCE_SEAL_REUSE.md) | [P3-BQ](notes/2026-11-03_p3-bq-continuity-correction.md): 코드 커밋됨; 변경 후 CI 결과 미확인 |
| `PRODUCT.E2E` | 제품 완성, READY, policy A, DPS, SEM, 95%, session | `CODE_ONLY` | `NOT_INTEGRATED` | [P3-BO 인계](../CHAT_CONTINUITY_HANDOFF_20261103_P3_BO_ENGINE_GJFO_NEXT.md) | [P3-BS](notes/2026-11-03_p3-bs-standardized-g-budget.md): 새 표준 G/B 표준화 연결은 코드만, 실제 시즌 READY/26DPS DPS E2E 미완료 |
| `DEV.CONTINUITY` | 인계, handoff, 기억, 중복 개발, 재검증, 개발자 기록 | `POLICY_DOCUMENTED` | `PARTIAL` | [규약](PROTOCOL.md) | [P3-BR](notes/2026-11-03_p3-br-tier-evidence-reuse.md): P3-BR 기존 증거 선조회 후 CONNECT 기록; CI는 별도 확인 |

**기존 증거 판정 주의:** `TIER.SEASON`의 원본 연관성은 강하지만 기존 코드의 `season_membership_verified=false`를 실제 제품 인증 PASS로 바꾸었다는 뜻이 아니다. 추가 *전용* 증거 수집이 기본 선행 과제인지부터 평가하고, 기존 증거/선정 결과 재사용을 우선한다. 과거 P3 문서의 당대 미완료 문구는 당시의 통합 상태를 기록한 것이며 그 자체로 원본 조사 재시작 명령이 아니다.
