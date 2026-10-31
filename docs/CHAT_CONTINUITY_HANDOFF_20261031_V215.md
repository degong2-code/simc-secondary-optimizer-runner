# SIMC SECONDARY OPTIMIZER — 2026-10-31 v215 P3-C 정본 인계

**목적:** v214 이후 원래 개발 채팅에서 이미 진행된 P3-C 변경을 복원하고, 중복 구현 없이 26/26 plan supplier coverage, dependency-aware session identity, 최신 v213 source artifact가 포함된 Windows beta package까지의 실제 증거를 이어간다.

**복원 규칙:** 이 문서는 code baseline cbc2244225f6c99bb57e765ca9b03b591fbc7cce까지의 상태를 정리한다. 이 문서와 관련 설계/CURRENT 갱신 커밋은 그 뒤에 생성되므로, 새 채팅은 반드시 GitHub에서 실제 HEAD/visibility/main/Actions를 다시 확인한다.

## 0. 저장소·브랜치·권한

- Repository: degong2-code/simc-secondary-optimizer-runner
- Branch: probe/chat-cache-v035-20261024
- Code baseline before documentation update: cbc2244225f6c99bb57e765ca9b03b591fbc7cce
- Repository visibility: Public (이번 작업에서 변경하지 않음)
- main HEAD at last read-only check: 07133e0aaf738d6e4816a6486057b1cd49c018de (변경 없음)
- No merge to main; no v003 immutable change; no original v016 change; no Project Sources/Instructions UI application; no official Work OS authority change.
- The branch remains isolated. The user must separately authorize any of those operations.

## 1. Policy authority and product scope

The current approved product scope is **exactly 26 DPS specializations**, excluding Augmentation Evoker, all tanks and all healers. Use the latest direct user decision and Developer Notes v1.4.2. The uploaded v1.4.1 scope-correction note is supplemental historical context; do not revert the 26-DPS boundary.

Product purpose remains target-level CHMV optimization at target ilvl (default 334) or user-entered final T, using existing SimC DPS optimization. It is not a current-worn-gear redistribution tool, loot/gear-set recommender, or a second optimizer.

Preserve:
- T=G+J+F+O; B=G+J+F; oil O is fixed and counted once.
- Special bare L, gem J, enchant E and consumable F remain distinct.
- SimC owns item effects, procs, APL and DPS.
- Statistical display uses 95%; observed top candidate is distinct from statistically confirmed superiority and global optimum.
- 7967 is the only existing user-selectable enchant; 8025 remains developer-only; 36 other current-season enchant candidates remain locked.
- Unknown joins remain UNKNOWN/PENDING, never zero.
- Reuse valid Native/cache receipts; no blanket 26×N Native matrix.

## 2. Already implemented — do not repeat

### 2.1 v191 → v211 → v213 → v196 source/catalog chain

Actual source-backed workflow [#41194394128](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394128) SUCCESS, artifact [#13040083134](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394128/artifacts/13040083134), 117,921 bytes.

- v191 emits season gear/tier/consumable/source identity with raw SHA.
- v211 classifies the 38 current-season enchant candidates from live v191 rows using pinned SimC source.
- v213 exact-joins ID/token/rank/item class/inventory mask/subclass mask and derives slot groups.
- v196/v197 consume the v213 artifact while retaining the old approval boundary.
- v213 embedded manifest SHA256: b888123728097371705c037ae2fc0085cc6735fac870f000b7606b1428d5ced5.
- Downloaded GitHub artifact ZIP SHA256: aada3cf81d0528bdc45674f5979b3bb5189594b83db3d3feca6cb4ecf545423f.
- Actual scope: gear511, tier13/65, enchant38/38, food192, potion61, embellishment registrations20 (exact item ID/slot unresolved), temporary-enchant source rows117 (exact hand applicability unresolved), gem-property rows2409 (not gem item IDs).

### 2.2 v212 Environment Manifest and v208 Start receipt

- v212 schema v2 consumes the exact v213 artifact directly and derives the v196 approved UI projection from the same path.
- Exact 7967 approval, 8025 developer-only, other 36 locked; selected 7967 is checked against the v098 profile ring line.
- v208 selected-special Start receipt is serialized content-addressed per session. v212 verifies selected/bare identity, cache snapshot, source artifact identity, Native JSON2 provenance, SimC binary/revision and cache/Native counts.
- Existing receipt tests used synthetic cache fixtures for plumbing/Native0; existing real v208 Native/cache evidence is reused. Do not describe the fixture as a new physical L observation.
- Earlier cross-platform receipt regression [#41178807936](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41178807936): Ubuntu/Windows each 26/26 PASS, Native0. Dedicated v208 offline [#41178704898](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41178704898) SUCCESS.

### 2.3 v215 profile supplier coverage — 26/26 Plan routes

runner/v098_target_user_scenario_bootstrap.py now computes a cached source-supplier registry and validates:
- 24 legacy source-backed routes + 2 source-independent routes = exact 26 contracts.
- v106 user-input routes 26/26.
- v106 starter defaults 26/26.
- v139 season catalog 26/26.
- v169 current-season source-first candidate profile suppliers 26/26.
- raw gear/tier/budget SHA values match the v191 input SHA values in v213.
- selected specialization must belong to the exact 26-key set.

The emitted schema is v215_profile_supplier_coverage_v1. It explicitly keeps all_specs_ready=false and adaptive_native_evidence_complete=false. **26/26 means Plan/profile supplier availability, not 26/26 adaptive Native/DPS E2E.**

### 2.4 Dependency graph and session isolation

- v212 seals v212_environment_dependency_graph_v1 with v213/v191/v196/v098/v208/package/binary/revision fingerprints.
- compare_dependency_graphs() emits a read-only invalidation delta against a previous valid manifest; it never deletes caches or historical sessions.
- A v208 receipt change invalidates the Environment Manifest only when the exact selected-special/static-cache identity is unchanged; the static item cache remains preserved.
- v106 session identity binds v213 raw artifact SHA, embedded manifest SHA, build, revision and optional package-manifest SHA; absolute paths are excluded.
- v113 Start checks the package/source against the session identity. Changed source/package bytes create a new session identity.
- This is dependency-aware identity isolation and invalidation planning, **not yet the full incremental Environment Build orchestrator**.

### 2.5 Latest Windows package contains the latest v213 artifact

Workflow defaults were corrected from the older source run #41178704794 to the latest successful source artifact #41194394128.

- v181 [#41194661922](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194661922): Windows Python 3.12/3.14 SUCCESS; 188-file package; extracted CMD launcher, packaged v213 identity, localhost HTTP security, Retribution334/Fury321/Frost344 plans and restore PASS; Native0. Artifact [#13039854689](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194661922/artifacts/13039854689), 744,988 bytes, outer artifact SHA256 2e2198d12fd611f2305a70c71ee6d1158a07654c808306531a126c5e107ea3bd.
- v182 [#41194661890](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194661890): Ubuntu/Windows SUCCESS; each OS 76 focused + 67 compatibility + 2 package tests PASS; Windows extracted HTTP/three plans PASS. Artifact [#13040520318](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194661890/artifacts/13040520318), 744,988 bytes, outer artifact SHA256 ac6ebfc30f1dcee5d8e87e5ad9a092e16008e38b781cccc5702ed7a4c6037ab0.

## 3. Exact latest regression evidence

- v098 [#41194394144](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394144): SUCCESS.
- v187 [#41194394156](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394156): 13 tests PASS.
- v177 [#41194394055](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394055): 12 focused + 84 regression tests PASS. Includes the source-catalog SHA session identity/path-relocation test. Native-one-product SKIPPED.
- v180 [#41194394105](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394105): 26 DPS × 5 target-level plan matrix; 3 focused + 63 regression tests PASS. Native-six-cases SKIPPED.
- v191 source pipeline #41194394128: actual source/catalog + P3-C v213→v098→v212 handoff PASS, Native0.
- v113 API [#41194394127](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394127): Ubuntu and Windows each 145/145 PASS.
- v181 latest-source package #41194661922: Windows Python3.12/3.14 PASS; actual extracted HTTP/restore; Native0.
- v182 latest-source UI/package #41194661890: Ubuntu/Windows PASS; actual Windows extracted HTTP/three plans; Native0.

New SimC Native calls during this continuation: **0**. New SimC binary builds: **0**. Optimizer/cache mutation: **0**. v177/v180 opt-in Native jobs were skipped. Existing Native/cache evidence was reused.

## 4. Remaining work and next implementation order

1. Build the actual incremental Environment Build coordinator around existing v191/v211/v213/v196/v212 components. Use the dependency graph to reuse unchanged sources and schedule only affected steps; preserve historical sessions and static caches.
2. Connect Build readiness/dependency delta to user API/UI. Report READY / READY_WITH_LIMITATIONS / BLOCKED, exact unresolved joins, 26/26 plan-supplier coverage, cache hits and Native scope.
3. Connect the sealed v098/v208 profile to the existing v093/v094/v095 adaptive optimizer. Do not add a new optimizer.
4. Resolve only exact missing source joins: embellishment item/slot, temporary-enchant hand applicability, gem-property→gem-item-ID. UNKNOWN remains UNKNOWN/PENDING.
5. Complete Windows one-click Build/Start/progress/cancel/resume integration and user-PC acceptance.
6. Full adaptive Native/DPS acceptance across all 26 is not claimed. Reuse existing 26 physical base receipts and prior adaptive receipts; do not repeat blanket 26×N Native matrices.

## 5. Required reading order

1. Read-only fetch actual branch HEAD, main HEAD, repository visibility, latest Actions and artifact expiry.
2. This handoff in full.
3. docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md top.
4. docs/DEVELOPER_NOTES_v1.4.2_LATEST_USER_POLICY_ADDENDUM_20261030.md, then the user-uploaded v1.4.1 scope correction. Keep exact 26 DPS scope.
5. docs/P3_ENVIRONMENT_BUILDER_TARGET_ARCHITECTURE_20261031.md §§7–11.
6. docs/P3C_V208_START_RECEIPT_AND_WINDOWS_PACKAGE_ACCEPTANCE_20261031.md §6.
7. Inspect only required code interfaces: v098, v106, v113, v191, v211, v212, v213, v196/v197, v208, v181/v182. Reuse the Actions receipts above.

## 6. Start prompt for the next chat

You are continuing the existing SIMC SECONDARY OPTIMIZER product development on the isolated branch probe/chat-cache-v035-20261024.

First restore and verify actual HEAD, visibility, main HEAD and latest Actions; read this handoff, CURRENT top, v1.4.2 policy, P3 architecture §§7–11 and P3-C acceptance §6. Reconcile all work already present before implementing anything. Do not repeat v191/v211/v213 source collection, v208 receipt, v212 dependency graph, 26/26 plan supplier checks, Windows v213 packaging, valid Native/cache evidence, or cross-platform regressions unless a changed dependency actually invalidates them.

The approved scope is exactly 26 DPS specializations excluding Augmentation Evoker, tanks and healers. Preserve CHMV ownership, SimC responsibility, 95% statistics, 7967-only existing approval, Native/cache reuse and UNKNOWN/PENDING semantics.

Continue with the production incremental Environment Build coordinator and user Build API/UI using existing components. Build should be request-driven, reuse identical artifacts, rebuild only changed dependencies, report exact readiness/cache/Native scope, and preserve old sessions/caches. Then connect the sealed profile to existing v093/v094/v095 and complete Windows one-click Build/Start/progress/cancel/resume. No new optimizer, profile generator, collector or effect engine.

Do not change main, v003 immutable, original v016, Project Sources/Instructions UI, repository visibility or official Work OS authority without separate explicit user authorization.

---

**END — V215 continuity handoff. Always re-fetch the actual branch HEAD before continuing.**
