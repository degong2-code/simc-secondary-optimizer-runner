# SIMC SECONDARY OPTIMIZER — 2026-10-31 v216 새 채팅 인계

## 목적과 판정 규칙

기존 제품 개발을 이어간다. 프로젝트를 재시작하거나 과거 증거를 전면 재감사하지 않는다. 이 문서는 v215 인계 이후 실제 HEAD에 반영된 v216 구현과 최신 Actions를 기록한다. 새 채팅은 반드시 실제 HEAD/visibility/main/Actions를 다시 조회하고, 아래 읽기 순서대로 복원한 뒤 사용자에게 복원 결과를 보고하고 **사용자의 “진행”을 기다린다.** 보고 전 코드 변경·Actions 재실행·Native 실행을 하지 않는다.

## 0. 저장소와 권한

- Repository: degong2-code/simc-secondary-optimizer-runner
- Branch: probe/chat-cache-v035-20261024
- Branch HEAD: always re-fetch the live ref; subsequent handoff commits are documentation-only.
- Code baseline: 547811e8ffb7d25eb9ad45bb416b0b75dd5458c3
- Code commit: feat(p3): add incremental environment build coordinator and local API
- Code commit parent: 0af0955e25d599487210dfa19fe18f424bb462d4
- Latest docs-only change: docs(handoff): clarify code and documentation HEADs
- Visibility: Public
- main HEAD: 07133e0aaf738d6e4816a6486057b1cd49c018de (unchanged)
- No merge to main; no v003 immutable or original v016 change; no Project Sources/Instructions UI update; no official Work OS/M0 authority change.

The v215 handoff remains historical context. Its statements that the coordinator and Build API/UI were not implemented are superseded by v216.

## 1. Approved product purpose and policy

Exactly 26 DPS specializations are supported. Augmentation Evoker, all tanks and all healers are excluded.

The product finds optimal absolute CHMV rating for a future farming target at the chosen target ilvl (default 334) or user-entered final T. It is not a current-worn-gear redistribution tool, gear-set recommender or loot/farming-route planner.

Preserve:
- T=G+J+F+O; B=G+J+F; T=B+O; c_final=c_base+o.
- Oil O is fixed and counted exactly once.
- Selected special bare L is already inside G/B and is only a per-stat floor.
- Trinket static JSON2 absence is UNKNOWN, not zero.
- SimC owns item effects, procs, APL and DPS.
- Our code owns exact IDs/options, profile/CHMV budget, static JSON2 rating reconciliation, candidate orchestration, cache and result statistics.
- 95% statistics only; observed first choice, confirmed statistical superiority and global optimum proof are distinct.
- Existing user-selectable enchant remains 7967 only; 8025 is developer-only; 36 others locked.
- Reuse valid Native/cache receipts. Do not run blanket 26×N Native matrices.

Policy authority: latest direct user decision, approved v1.4 design, v1.4.2 addendum and 26-DPS correction. The uploaded 20261029 v1.4.1 copy SHA 752641f0... contains obsolete 27/Augmentation wording. The corrected full replacement is docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.1_DPS_ONLY_SCOPE_CORRECTION_20261031.md SHA e4513776f1a225394e404601532dfea61f066dd5e7f23149c7af355d6e43e0d3. Project UI application remains manual/pending.

## 2. Long-term product goal and roadmap

The final product is one user-facing Environment Build flow combining:
1. Season equipment/source DB from approved Blizzard/Wago/SimC/DBC/DB2 source chain.
2. Source-driven discovery/classification/applicability/completeness self-validation with exact provenance and selected-only Native lookups.
3. Existing representative profile + CHMV budget + existing adaptive SimC optimizer.

Do not build a second optimizer, collector, profile generator, APL/proc/effect engine, gear recommender or full gear-set database.

Roadmap:
- P3-A: v212 manifest + exact v213 artifact + dependency graph.
- P3-B: v191→v211→v213→v196 source/catalog pipeline.
- P3-C: v208 Start receipt, Windows package, 26/26 profile plan suppliers, source/session identity.
- P3-D first slice: v216 installed-artifact Build coordinator, v113 Build API/status, user UI status, Windows package inclusion.
- Remaining P3-D: real cross-session invalidation acceptance, request-driven source refresh, sealed environment→existing v093/v094/v095 Start handoff, Windows user-PC Build/Start/progress/cancel/resume acceptance.

## 3. Already implemented — do not repeat

### 3.1 Source/catalog and plan suppliers
- v191/v211/v213/v196 existing source-to-catalog chain is already source-backed.
- Current artifact: source pipeline #41194394128; artifact #13040083134; v213 embedded manifest SHA b888123728097371705c037ae2fc0085cc6735fac870f000b7606b1428d5ced5; downloaded outer ZIP SHA aada3cf81d0528bdc45674f5979b3bb5189594b83db3d3feca6cb4ecf545423f.
- v215 profile supplier coverage: 24 legacy source-backed + 2 source-independent = 26/26 plan suppliers. This is profile/Plan readiness, not adaptive Native/DPS completion. all_specs_ready=false remains.
- Current-season source rows include gear511, tier13/65, enchants38, food192, potion61, embellishment registrations20 (item/slot unresolved), temporary-enchant rows117 (hand applicability unresolved), gem properties2409 (not gem item IDs).

### 3.2 v208/v212 and Windows package
- v208 selected-special Start receipt is content-addressed and v212 binds exact receipt/source/profile/cache/binary identities.
- Exact 7967 user approval only; 8025 developer-only; other 36 locked.
- v181/v182 packages include the latest v213 source catalog. Prior source package runs #41194661922/#41194661890 are historical; the latest package is from #41200816597/#41200816611.

### 3.3 v216 implementation on current HEAD
- New runner/v216_environment_build_coordinator.py and tests/test_v216_environment_build_coordinator.py.
- v113 adds POST /api/v1/environment/build (current-season only) and GET /api/v1/environment/{session_id}. Existing session status returns the v216 receipt summary.
- UI Build button calls the new endpoint; status displays readiness, reuse/rebuild/change counts, v213 artifact hits and plan supplier coverage with adaptive Native incompleteness.
- v181 package includes v216 runtime module; v113/v212/v181/v182 workflows include v216 tests and path triggers.
- v191 workflow path triggers were narrowed to source acquisition/catalog dependencies to avoid unrelated profile/API changes triggering source refresh work.

### 3.4 Exact v216 behavior and limits
- Explicit user Build request only. Consumes installed, versioned v213 artifact. Source mode is INSTALLED_VERSIONED_ARTIFACT_ONLY; refresh_performed=false.
- v191/v211 provenance is reused from the installed artifact; v213 is reused as the package artifact. No collector/network refresh occurs.
- Scope identity is canonical user-scenario SHA, intentionally excluding dependency versions so v212 can compare changes. Previous lookup scans at most 128 recent session folders for valid self-digested v216 receipt + v212 manifest.
- v216 passes a valid previous manifest into existing v212 dependency graph comparison; writes a receipt with source identity, step status, changed inputs, invalidated/reused components, readiness, Native/network/cache mutation counts and historical-session preservation.
- v216 requires Native0/network0/cache_mutations0 and historical_sessions_preserved=true.
- Same-session repeated Build verifies byte-identical manifest reuse and receipt readback. The test intentionally sees dependency_change.status=INITIAL_ENVIRONMENT because previous-session lookup excludes the current folder. It is not cross-session invalidation proof.
- Prior-session lookup validity is tested separately, but a two-session API E2E proving a changed v213/source dependency invalidates only downstream components while preserving the old session/cache is still missing.
- The coordinator is not a full source scheduler. It consumes installed source artifact; it does not run v191/v211/v213.
- The plan route builds the v098 target profile before the coordinator. The current evidence does not prove unchanged v098 profile generation/I/O was skipped. Do not claim measured profile-stage incremental execution without a dedicated test.
- Build→Start→existing adaptive worker end-to-end identity is not yet accepted. Existing /sessions/start and v093/v094/v095 remain the optimizer path; do not replace them.

## 4. Latest Actions evidence on HEAD 547811e8

| Run | Actual result |
|---|---|
| v212 #41200816574 | Ubuntu 36/36 PASS; Windows 36/36 PASS; four v216 tests included; Native0 |
| v113 #41200816595 | Ubuntu 150/150 PASS; Windows 150/150 PASS; includes local HTTP Environment Build API test; Native0 |
| v181 #41200816597 | Windows Python 3.12 and 3.14 each 118 regression tests + 2 package tests PASS; extracted CMD/HTTP security/3 Plans/restore PASS |
| v182 #41200816611 | Ubuntu and Windows each 76 focused + 68 compatibility + 2 package tests PASS |
| v169 #41200816572 | 13 PASS; 26-spec source-first physical candidate preview only; Native0 |
| v177 #41200816573 | 12 focused + 85 regression PASS; Native-one-product SKIPPED |
| v180 #41200816659 | 3 focused + 64 regression PASS; Native-six-cases SKIPPED |
| v167 #41200816594 | SUCCESS |

New SimC Native: 0. New SimC binary build: 0. Optimizer/DPS/static-item cache mutation: 0. Existing Native/cache evidence reused.

Windows artifacts:
- v181 artifact #13042157651, 750,209 bytes, expires 2026-11-07T12:23:22Z.
- v182 artifact #13042686292, 750,209 bytes, expires 2026-11-07T12:23:10Z.
- Each packaged inner ZIP contains 189 files; SimC binary and user cache are excluded.
- These are CI-extracted Windows runtime checks, not a claim that the user's PC was updated or manually GUI-clicked.

## 5. Remaining blockers and next work

1. **Two-session invalidation E2E:** create two sessions for the same user scenario with different source artifact identities. Verify a new session identity, exact changed_inputs/invalidated components, and byte-identical old session/receipt/manifest/static/DPS caches.
2. **True reuse accounting:** determine whether v098 profile generation and other stages can safely skip unchanged work. Only label a component REUSED if work was actually skipped; measure I/O/time.
3. **Request-driven source refresh:** connect the existing v191→v211→v213 source pipeline for an explicit season/patch refresh request. Reuse unchanged versioned artifacts; no background polling or duplicate collector.
4. **Existing optimizer handoff:** verify the exact sealed v098/v208 environment/profile consumed by existing v093/v094/v095 Start/worker. No new optimizer.
5. **Windows user acceptance:** packaged Build, Start, progress, cancel, resume and restore on the user's PC. CI extraction is not manual PC acceptance.
6. **Unresolved source joins:** embellishment item/slot, temporary-enchant hand applicability, gem property→gem item ID. UNKNOWN/PENDING, never zero.
7. Full adaptive Native/DPS acceptance across 26 remains incomplete. Do not repeat blanket 26×N Native matrix.

## 6. Required reading order

1. Read-only verify actual branch HEAD, main HEAD, visibility, latest Actions, artifacts and expiration.
2. Read this V216 handoff in full.
3. Read docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md top and its P3-D v216 section.
4. Read docs/DEVELOPER_NOTES_v1.4.2_LATEST_USER_POLICY_ADDENDUM_20261030.md.
5. Read docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.1_DPS_ONLY_SCOPE_CORRECTION_20261031.md and docs/DPS26_SCOPE_CORRECTION_20261031.md. Do not use the obsolete 20261029 upload copy as current 26-DPS source.
6. Read docs/P3_ENVIRONMENT_BUILDER_TARGET_ARCHITECTURE_20261031.md §12 and docs/P3C_V208_START_RECEIPT_AND_WINDOWS_PACKAGE_ACCEPTANCE_20261031.md §7.
7. Inspect only changed interfaces as needed: v216 coordinator/tests; v113 plan/status/Build API; webui app.js/index.html; v212 dependency comparator; v098 bootstrap; v106 session identity; v191/v211/v213/v196; v208; v181 packager. Reuse above Actions receipts.

## 7. Start prompt for the next chat

You are continuing the existing SIMC SECONDARY OPTIMIZER project. Do not restart or rebuild old work.

First, read docs/CHAT_CONTINUITY_HANDOFF_20261031_V216.md in full. Then verify actual GitHub branch HEAD, visibility, main HEAD and latest Actions; read CURRENT top, v1.4.2 policy addendum, corrected v1.4.1 full note, DPS26 scope correction, P3 architecture §12 and P3-C §7. The known code baseline is branch probe/chat-cache-v035-20261024 at code commit 547811e8ffb7d25eb9ad45bb416b0b75dd5458c3; subsequent commits in the handoff sequence are documentation-only. Re-fetch the live branch HEAD before any work. main was 07133e0aaf738d6e4816a6486057b1cd49c018de and repository visibility Public at handoff verification. If actual state differs, report the difference and use actual GitHub evidence.

Restore the exact product purpose and policy: 26 DPS only, Augmentation/tanks/healers excluded; target-level absolute CHMV; T=G+J+F+O; oil once; special bare L floor; SimC owns effects/procs/APL/DPS; 95% only; 7967 only selectable; UNKNOWN/PENDING not zero.

Reconcile v216 before changing code. Do not repeat v191/v211/v213 source collection, v212/v113/v181/v182 CI, v169/v177/v180 tests, valid Native/cache receipts or the 26-spec supplier matrix unless a changed dependency invalidates them. Native jobs #41200816573 and #41200816659 were skipped; do not call them Native PASS.

Next implementation candidates are: (1) two-session changed-dependency API E2E with byte-preservation assertions; (2) measured idempotent profile/manifest reuse; (3) request-driven source refresh using existing collectors; (4) exact environment→existing adaptive worker handoff; (5) Windows user-PC acceptance. Keep these in dependency order and combine independent offline work. Reuse the same acceptance contract and regression evidence. Review Native count, cache reuse, memory, I/O, runtime and structural simplicity for every change.

Do not create a new optimizer, collector, profile generator or effect engine. Do not alter main, v003 immutable, original v016, Project Sources/Instructions UI, repository visibility or official Work OS authority without separate explicit user authorization.

**First response: report restored state, verified evidence, completion, limitations and the next exact task. Then stop and wait for the user's “진행” before implementation.**

---

**END — V216 continuity handoff. Actual GitHub HEAD must be re-fetched on every new chat.**