# P3 — One-click Environment Builder target architecture (2026-10-31)

**Status: user-approved long-term product direction; architecture contract documented, not yet implemented as a complete one-click flow.** This document does not promote GitHub branch code to Project Sources, Windows release, main, v003, or official Work OS.

## 1. Product outcome

The final product combines three existing responsibilities into one user-visible **Environment Build** action:

1. **Season equipment/source collection DB** — discover current season equipment and option candidates from the approved Blizzard/Wago/SimC/DBC/DB2 source chain.
2. **Source-driven discovery, classification and validation engine** — identify exact IDs, versions, slot applicability, intrinsic options, static CHMV components, non-CHMV components, and SimC-owned spell/proc references; validate provenance and completeness; run only the Native observations needed for an actually selected configuration.
3. **Existing target-profile + SimC optimizer** — generate the internal representative profile and CHMV budget, then hand off to the existing adaptive SimC DPS/SEM/95%/alternative/cache/cancel/resume pipeline.

This is a data/environment preparation and optimizer-entry product. It is **not** a full gear-combination recommendation database, loot planner, or independent effect/proc/DPS calculator.

## 2. Existing code to reuse — do not fork a second engine

| Existing component | Current responsibility | Environment Builder role / gap |
|---|---|---|
| v161–v190 source collectors | API-first season/build and source snapshots, gear/tier/consumable/effect candidates | Reuse collectors and their source artifacts; do not repeat or seed from another project |
| v191_unified_season_data_update.py | Request-scoped, source-pinned thin aggregator; validates build/provenance; emits candidates; Native0 and no UI promotion | Reuse as the season data collection/aggregation stage. It explicitly does not yet produce a fully user-selectable catalog |
| v196_current_season_user_catalog.py + v197 | Versioned UI catalog bridge, slot mapping, effect-family metadata and existing approval boundary | Reuse as the publication/read model; close the source-to-catalog artifact handoff without bypassing approval |
| v211_enchant_source_effect_classification.py | Pinned SimC source classification for 38 permanent enchants | Treat as one source-classifier module/pattern; generalize the same provenance discipline to gems, embellishments, consumables and special gear |
| v098_target_user_scenario_bootstrap.py | Compact user input -> internally generated target-level representative profile for a bounded source-backed archetype set | Reuse as the target-profile assembler; expand coverage to all 26 DPS specs without importing current worn gear as the budget |
| v208_internal_exact_special_L_hydrator.py + v046/v062 | Selected-special exact bare L Native lookup, cache snapshot and L/J/E separation | Reuse only for selected missing exact L; one Native can resolve several selected specials; never perform a blanket item matrix |
| v093/v094/v095 and current adapters | Adaptive SimC candidate execution, DPS/SEM/95%, alternatives, cache, cancellation/resume | Remain the only optimizer/execution engine |

Do not introduce a parallel collector, second profile generator, second adaptive optimizer, or separate effect evaluator.

## 3. One-click Environment Build contract

The future user action is explicit and request-driven (not always-on polling):

1. **Resolve inputs** — current season/game build, pinned SimC revision/binary identity, selected 26-DPS archetype, target ilvl or manual final T, and current approved catalog versions.
2. **Discover/update** — run only missing source collectors for a requested patch/season/expansion event; otherwise reuse exact source snapshots. No new-season assumption from an old artifact.
3. **Compile normalized catalog** — join exact IDs and options across SimC generated data, DBC/DB2, game item metadata, and existing gear/tier/consumable sources. Group by physical slot and applicability. Preserve distinct effects and stat families; collapse only exact same-effect/same-slot variants with comparable verified quality/strength.
4. **Validate** — verify source revision/build/hash, row counts, referential integrity, duplicate/conflicting IDs, slot masks, option identity, missing joins and catalog completeness. Unknown or absent is UNKNOWN/PENDING, never silently zero or silently selectable.
5. **Resolve only selected numeric requirements** — use existing static cache; on exact selected special L miss, reuse v208's explicit Start-time Native lookup; only measure a selected static CHMV enchant E when the exact item/profile Native scope and budget contract require it. SimC owns dynamic effects/procs.
6. **Build target environment** — use existing v098 representative profile and CHMV budget rules, retain full selected gem/enchant/equipment options in the DPS profile, and emit a versioned environment manifest with all source/cache/profile identities.
7. **Report readiness** — READY, READY_WITH_LIMITATIONS, or BLOCKED; show newly discovered/updated/reused entries, unresolved joins, exact blocked reason, Native calls/cache hits, and verification scope.
8. **Start optimizer** — only after explicit user Start, pass the sealed environment unchanged into the existing adaptive SimC engine. Plan/preview remains Native0 unless an already-approved selected-data lookup is explicitly part of Start.

Environment Build is incremental and idempotent: unchanged source identity reuses its prior artifact; changed source identity invalidates only dependent derived artifacts; a SimC revision change alone does not invalidate static season item identity. DPS result cache remains keyed by binary/version, full profile and selected options, candidate, oil, fight conditions and iterations.

## 4. Canonical data model requirements

Each catalog record must retain, where applicable:

- entity kind and exact item/enchant/gem/effect ID; SimC token;
- season/game build, SimC revision, source path, source blob/content SHA and source artifact identity;
- item class/subclass, inventory/slot mask and resolved human-readable slots (unresolved mask is not all-slot permission);
- item level, quality/rank, bonus/redirect/catalyst/context/content-tuning identity and all intrinsic options;
- static CHMV vector and explicit status (MEASURED, SOURCE_CLASSIFIED_ONLY, NOT_MEASURED, UNKNOWN, CONFLICT);
- non-CHMV static components and spell/handler references (description only; SimC calculates behavior);
- applicability evidence and exact Native profile/binary/JSON2 SHA scope;
- selection state and reason, kept distinct from discovery/classification;
- dependency/provenance links to source rows and derived catalog version.

A single record can have multiple compatible slots only when the exact source mask proves it. Category names, localized names, or effect descriptions never substitute for physical slot evidence.

## 5. CHMV and SimC invariants

- Official totals remain T=G+J+F+O, B=G+J+F, T=B+O.
- Oil O is fixed and included exactly once.
- A selected exact special-item bare L is already in G/B and is only a per-stat floor; do not add it again. Gem J and permanent enchant E remain separately attributable and are never folded into bare L.
- For the automatic ilvl reference path, only a selected permanent static CHMV enchant with exact accepted E evidence can adjust the reference B/T under the approved v204 rule. A selected non-CHMV enchant such as 7967 leaves B/T unchanged. Manual final T already includes selected fixed components and is never increased again.
- Trinket static JSON2 absence is not zero. Unknown Native data is not zero.
- SimC owns item effects, spell execution, procs, APL, buffs, damage and DPS. Our code owns source IDs/options, profile construction, budget ownership, static JSON2 consistency, statistics, cache and orchestration.
- Statistical display uses 95% only. Observed highest DPS, statistical superiority and proof of global optimum are separate claims.

## 6. Scope and security boundaries

- Supported product scope is **26 DPS specializations**. Augmentation Evoker, tanks and healers are excluded.
- No gear set/loot acquisition recommendations, no general gear-combination optimizer, no user current-equipment scan as budget, and no independent proc/effect engine.
- Season source update remains explicit/request-driven; no background polling.
- Private user profiles and local credentials must not be copied into public GitHub artifacts.
- This document and isolated-branch code do not change repository visibility, main, immutable v003, original v016, Project Sources/Instructions UI, or official Work OS authority.

## 7. Implementation roadmap and first integration slice

> This section records the initial roadmap baseline. The newer implementation and evidence in §11 supersede its earlier P3-C incomplete statements.

**P3-A — artifact contract and gap closure (v212 first implementation; not full acceptance):**
- **Implemented in v212 v2:** the Environment Manifest now consumes the actual v213 source-to-catalog artifact directly, derives the existing v196 approved UI projection from the same exact file path, and binds both the artifact byte SHA and embedded manifest digest. It no longer accepts three separately supplied v191/v211/v196 JSON documents as independent authorities.
- **Implemented:** exact v191/v211 component SHA and generated SimC source hashes, same game build/40-character SimC revision, v196 projection identity, exact selectable ID **7967 only**, 8025 developer-only, all other 36 locked, and v098 current-season profile identity. The selected 7967 must appear exactly once on the profile ring line and retain static E=0/no CHMV budget increment.
- **Implemented:** normalized v098 semantic identity plus generated profile/scenario/fillers/manifest file hashes; raw bootstrap JSON SHA is intentionally not used because it contains relocation-sensitive absolute paths. Binary SHA and optional static-cache SHA are bound. Selected special rows contribute exact ID/slot/options identity SHA; if present, a static-cache snapshot is required.
- **Partial / still open:** relocation-stable digest and fail-closed source/build/revision/approval checks are tested, but production dependency-graph invalidation/orchestration and a separately serialized v208 Start receipt are not implemented. `unresolved_dependencies` remains a fixed readiness list, not a dynamic missing-join report.

**P3-B — source-to-catalog integration (v213 first implementation: actual source E2E PASS, not full product acceptance):**
- **Implemented:** v191 emits compact gear candidate rows with exact InventoryType/class/subclass masks, all 13 class/65 tier IDs, related-source counts, raw input SHA256, and the three exact SimC generated-table SHA256 values.
- **Implemented:** v211 accepts the v191 artifact directly as its current-season enchant candidate source. The new path does not read the separate pinned 38-row candidate list; it preserves the existing runtime manifest as a compatibility/evidence boundary while recording v191 as the actual candidate-source schema.
- **Implemented:** v213 joins v191 candidate and v211 classification rows by exact enchant ID, SimC token, rank, item class, inventory mask and subclass mask; derives armor-enchant slot groups only from source masks; derives gear groups from exact InventoryType; unknown gear inventory types remain UNKNOWN/PENDING.
- **Implemented:** v196 accepts the versioned v213 artifact by explicit path and v197 consumes its v211 classification rows. Classification is distinct from UI approval; only the pre-existing 7967 approval is selectable, 8025 remains developer-only, and 36 remain locked.
- **Actual artifact E2E:** [Actions #41169754323](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41169754323), artifact [#13031015315](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41169754323/artifacts/13031015315), v213 digest `b888123728097371705c037ae2fc0085cc6735fac870f000b7606b1428d5ced5`. Actual counts: gear 511, tier 13/65, current-season enchant candidates 38/38, food 192, potion 61, embellishment registrations 20, temporary enchant source rows 117, gem properties 2409. Gear inventory groups contain 511 rows and zero unknown slot rows. Enchant groups: boots3/chest4/helm6/ring9/shoulders6/weapon10.
- **Cross-platform regression:** [Ubuntu + Windows #41170184299](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41170184299), 62/62 tests PASS on each OS, including six v213 contract tests and deterministic source-identity digest checks. No Native calls, no SimC binary build, no optimizer/cache mutation.
- **Still limited:** v196's default data path and the Windows beta package do not yet contain the v213 artifact; P3-C now supplies it explicitly in the source-backed CI path. Embellishment registrations do not yet join exact item IDs/slots, temporary enchants do not yet resolve exact hand applicability, and gem-property rows are not gem item IDs.

**P3-C — one-click target environment (first source-backed integration slice PASS; not complete):**
- **Implemented:** exact v213 artifact → v196 approved projection → v212 v2 Environment Manifest. v206/v098/v208 accept an optional exact v213 source path; v113 uses the packaged artifact path when present and otherwise preserves legacy fallback.
- **Actual profile witness:** existing v098 generated a current-season Retribution 334 profile with the already-approved 7967 enchant exactly once, no Native, and no CHMV budget increment. v212 sealed the same source identity and profile hashes.
- **Special-L boundary:** v208 receives the same source path. A cache-hit plumbing probe verifies path propagation with the cache lookup mocked to avoid Native; it does not prove actual cache bytes or a new L observation. Existing v208 Native/cache evidence is reused.
- **Still required:** all-26 profile-supplier readiness, package the v213 artifact in the Windows beta, serialize an exact v208 Start receipt into the environment manifest, connect the sealed profile to the existing optimizer through the production user flow, and implement dependency-aware invalidation/orchestration.

**P3-D — Windows product experience:**
- one-click Build / Start, progress, cancellation/resume, incremental refresh, cache report and downloadable diagnostics;
- targeted Windows Native only for changed physical inputs; no blanket 26×N matrix.

**Acceptance criteria:** same inputs and source identity produce byte-stable manifest; unchanged artifacts are reused; a changed source invalidates only its dependents; unknown joins block only the affected choice rather than erasing unrelated options; plan mode Native0; Start makes only the selected missing static lookups; final profile retains full user-selected options; optimizer/cache/statistics behavior is the existing approved path.

**Current state:** P3-A v212 v2 directly consumes and verifies v213; focused tests pass 23/23 on Ubuntu and 23/23 on Windows. P3-B source-to-catalog remains source-backed and passes. P3-C first actual source-backed integration passed: v213→v196 exact 7967 approval→v098 Retribution 334 profile→v212 manifest, plus v208 source-path propagation through a mocked cache-hit probe; the full pipeline is Native0. The default Windows package still lacks the v213 artifact, the actual v208 Start receipt is not serialized, all-26 profile-supplier readiness remains false, production Build API/UI and optimizer handoff are not complete, dependency invalidation/orchestration is not implemented, and the Windows one-click experience remains incomplete.


## 8. P3-A first implementation — v212 Environment Manifest assembler (2026-10-31; v2 hardening in §10)

**Initial v1 implementation:** v212 first joined separately supplied v191/v211/v196 JSON and a v098 result. The initial [#41160002104](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41160002104) synthetic contract suite passed 9/9 on Ubuntu and Windows, Native0. This historical evidence remains valid for the original v1 contract only.

**Current v2 contract:** v212 now consumes one exact v213 artifact plus a v098 current-season profile result. It calls the existing v196 public-options projection from the same v213 path and verifies the exact 7967-only approval boundary, 8025 developer-only state and all other candidates locked. It binds the v213 raw artifact SHA, embedded manifest digest, v191/v211 source identities, generated SimC source hashes, game build/revision, v098 normalized result identity, generated profile files, binary SHA and optional static-cache SHA. It does not call collectors, APIs, SimC, or the optimizer.

The v212 digest intentionally excludes raw bootstrap JSON bytes because the file contains local absolute paths. Instead, it hashes a stable semantic projection and every generated target file SHA; relocating the same target folder does not change the digest. Selected special rows are represented by exact slot/item/ilevel/options identity SHA and require a bound static-cache snapshot. The manifest records no absolute local path or full user profile.

**Current cross-platform tests:** [#41172225040](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41172225040), **23/23 PASS Ubuntu + 23/23 PASS Windows**, Native0. The tests exercise actual repository source rows through the v213 compiler fixture, exact approval checks, digest tampering, build/revision drift, augmentation exclusion, profile mutation and relocation stability. The actual production artifact/profile integration is recorded separately in §10. The module makes **Native0 and network0**.

**Still open:** the v212 source/catalog contract pins 38 current-season candidates and the current 7967-only approved selection; it is not yet season-agnostic. The v208 Start receipt is not separately serialized in the Environment Manifest, dependency invalidation is not dynamic, and the manifest remains an internal readiness artifact rather than the user-facing Build API/UI.


## 9. P3-B first implementation — v213 source-to-catalog bridge (2026-10-31)

**Code on the isolated branch:**
- `runner/v191_unified_season_data_update.py` now retains 511 source gear candidate rows with exact inventory/class/subclass applicability, 13 class tier contracts/65 piece IDs, related-source counts, raw source input SHA256, and exact SimC generated permanent-enchant/temporary-enchant/gem-property source hashes.
- `runner/v211_enchant_source_effect_classification.py` accepts the v191 artifact directly. The live v191 candidate rows are projected into the existing v211 source contract; the separate pinned 38-row candidate JSON is not read on this path. The old runtime classification manifest remains a compatibility/read-only evidence boundary, not the source of current candidate rows.
- `runner/v213_source_to_catalog.py` creates schema `v213_current_season_source_to_catalog_v1`. It exact-joins candidate/classification identity, derives gear slot groups from InventoryType and enchant slot groups from inventory masks, preserves unknown joins as pending, and emits one deterministic manifest with v191/v211 source hashes.
- `runner/v196_current_season_user_catalog.py` accepts the v213 artifact by explicit path; `runner/v197_enchant_effect_families.py` can consume the v211 rows from that artifact. Existing UI approval is unchanged: only 7967 is selectable after v196's existing evidence check; 8025 remains developer-only and 36 rows remain locked.

**Actual source-backed run:** [Actions #41169754323](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41169754323), commit `29d985a999293adb3132a27c83ecf26602b217c8`, SUCCESS. It reused existing v189/v190 source artifact from run `41017578894`, fetched only the exact pinned SimC source files required for the compiler, generated the v191 artifact, classified its 38 current-season enchant candidates, built v213, then passed the actual v213 artifact through v196. Artifact [`v213-source-to-catalog-41169754323`](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41169754323/artifacts/13031015315), 93,908 bytes compressed, 7-day retention. v213 manifest SHA256: `b888123728097371705c037ae2fc0085cc6735fac870f000b7606b1428d5ced5`.

**Observed catalog scope:** 511 gear rows across 17 exact inventory groups (zero unknown current rows); 13 classes/65 tier IDs; 192 food and 61 potion item candidates; 38/38 current-season enchant classifications; 20 embellishment/effect registrations without resolved item IDs; 117 temporary-enchant source rows; 2,409 gem-property rows without resolved gem item IDs. The 38 enchant slot groups are boots3/chest4/helm6/ring9/shoulders6/weapon10. v213 itself marks all rows nonselectable; v196 applies the existing approval evidence and exposes only 7967.

**Regression evidence:** v191 focused 6 tests PASS within #41169754323; the integrated Ubuntu workflow reports 22 tests PASS. [Catalog integration #41169754402](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41170184299) reports 62 tests PASS on Ubuntu and 62 on Windows, including all six v213 contract tests and deterministic source-identity digest checks. New SimC Native calls: 0; SimC binary builds: 0; optimizer/cache mutation: 0. The workflow fetches pinned source text at the Actions layer; the v191/v211/v213 compilers themselves report network0.

**Important boundary:** v196's default checked-in data path and the Windows beta package are not yet switched to or bundled with v213. P3-C §10 now proves v212 can consume v213 directly when supplied explicitly; the packaged local app still falls back to the legacy catalog because the artifact is not included. This proves a source-backed profile/manifest slice, not the one-click user product, all-26 profile readiness, or a full optimizer run. No main/v003/v016/Project UI/visibility/Work OS change was made.


## 10. P3-C first source-backed environment handoff (2026-10-31)

### 10.1 Implemented code path

- `runner/v212_environment_manifest.py` is now schema `v212_simc_environment_manifest_v2`. Its CLI accepts the exact `--source-to-catalog` v213 artifact, a v098 bootstrap result, and the target folder. It verifies v213's embedded digest and file SHA, derives v196 options from that exact path, checks source/build/revision identity, and binds the exact existing 7967 approval (8025 developer-only; 36 other candidates locked).
- `runner/v206_nonchmv_eagle_selection.py`: `source`, `check_choice`, `apply`, and `admit` accept an optional exact catalog path. The default legacy source remains unchanged when no v213 path is supplied.
- `runner/v098_target_user_scenario_bootstrap.py`: `build` and `run` accept optional `source_catalog_path`; the selected 7967 validation is performed against the supplied v213 artifact when present.
- `runner/v208_internal_exact_special_L_hydrator.py`: `hydrate` forwards the same optional v213 path into its existing v098 static-special pre-budget stage. No new L engine or Native behavior was introduced.
- `runner/v113_local_web_api.py`: detects `data/current_season_source_to_catalog.json` inside a packaged app and, if present, uses that same artifact for the option catalog, Plan and Start/v208 path. If absent, the existing legacy catalog remains the fallback. The current Windows beta does not yet package the v213 file, so its tested runtime still uses that fallback.
- `integration_probes/v214_p3c_v213_v098_v208_handoff.py`: source-backed CI probe using the actual v213 artifact and an existing v098 Retribution 334 scenario; no new profile generator.

### 10.2 Actual end-to-end receipt

- [Source/catalog + P3-C integration #41172423986](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41172423986): SUCCESS, branch commit `1ef1f3f73e619f6b42a95e71cfca0f6d2f864fc7`.
- Artifact [#13031735907](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41172423986/artifacts/13031735907), 103,321 bytes compressed, 7-day retention. It contains the actual v191/v211/v213 components, the v098 bootstrap/profile, v212 Environment Manifest, and v208 path-plumbing receipt.
- v213 artifact raw file SHA256: `55e74d4fb3d4721a56ecbc8e76448360273ddc0181d335fa94d9d9cc4e1619ad`.
- Embedded v213 manifest SHA256: `b888123728097371705c037ae2fc0085cc6735fac870f000b7606b1428d5ced5`.
- v212 Environment Manifest SHA256: `988a0b40f1123ee1271c6f761896bdb21f798ec4c734266a1d8feb7e311ce275`.
- Actual v098 current-season Retribution 334 profile applies the existing approved ring enchant 7967 exactly once. Existing E=0 proof scope is retained; the enchant adds no CHMV budget and does not change B/T. v098 plan is Native0.
- v212 verifies exact 26 DPS contract scope from v143, rejects Augmentation Evoker, binds v213/v196/v098 identities, profile files, binary SHA and the optional static-cache snapshot. `all_specs_ready` remains false; the 26 scope declaration is not a claim that all profile suppliers are ready.
- v208 cache-hit plumbing is exercised with the cache lookup/missing-variant functions mocked to avoid Native. This proves exact v213 path propagation into the existing v208→v098 staging call only. It does **not** prove real cache bytes or a new static-L observation; existing v208 Native/cache receipts are reused.
- Pipeline tests: v191 focused 6 PASS; integrated source/classifier/catalog/v208 suite 29 PASS. [v212 cross-platform contract #41172225040](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41172225040): Ubuntu 23/23 PASS, Windows 23/23 PASS. v098 offline [#41172082190](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41172082190), v113 API Windows+Ubuntu [#41172082178](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41172082178) both SUCCESS. The latest Windows beta [#41172082207](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41172082207) passed 101 tests on Python 3.12 and 3.14, but its 187-file ZIP [#13031975054](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41172082207/artifacts/13031975054) does not yet include v213 data.
- New SimC Native calls: **0**. New SimC binary builds: **0**. Optimizer/cache mutation: **0**. No previous Native/cache receipts were invalidated.

### 10.3 Still incomplete

> Historical status at the first source-backed handoff. Current P3-C status is updated in §11 below.

- Package the generated v213 artifact into the Windows beta and make it the default UI/catalog source. Until then, the new v113 path detection deliberately falls back to the existing source.
- Serialize a verifiable v208 Start receipt (selected special identity, exact cache hit/miss, Native JSON2 source/hash, measured L) into v212. Current v212 binds the selected-special identity SHA and static-cache SHA but not the full v208 receipt.
- Complete readiness/coverage for all 26 DPS profile suppliers; current v098 result reports `all_specs_ready=false` and the source-backed witness is one Retribution 334 profile.
- Implement dynamic dependency invalidation/orchestration, the user-facing Build API/UI, and Windows one-click Build/Start/progress/cancel/resume.
- Do not repeat all-26 Native matrices, build a new optimizer, or promote any additional enchant. Continue with focused source/profile contract work and reuse valid historical receipts.


## 11. P3-C v215 — all-26 plan supplier coverage, dependency-aware identity, and packaged v213 (2026-10-31)

This section supersedes the initial P3-C limitations in §7 and §10.3. It records implementation on the isolated branch; it does not claim the complete Environment Builder or all-26 adaptive Native acceptance.

### 11.1 Profile supplier coverage is now explicit and self-checked

runner/v098_target_user_scenario_bootstrap.py now computes a cached source-supplier registry from the existing modules and current season inputs. For a current-season profile it checks exact set equality against v143_specialization_contracts.CONTRACTS, the v106 user-input routes, v106 starter defaults, the v139 season catalog and the v169 source-first candidate profile map.

- 24 existing legacy source-backed supplier routes + 2 source-independent routes = **26/26 current-season DPS plan suppliers**.
- User input defaults: 26/26; starter defaults: 26/26; season catalog: 26/26; source-first profile suppliers: 26/26.
- Raw gear/tier/budget input SHA256 values are bound to the corresponding v191 source input hashes in the v213 artifact. Supplier contract/composer/session/source-stage code hashes are recorded.
- The current selected specialization must be a member of the exact 26-key supplier set.
- The coverage record is v215_profile_supplier_coverage_v1, includes Native0/network0 and explicitly retains all_specs_ready=false and adaptive_native_evidence_complete=false.

This closes the **plan/profile supplier availability** gap, not the full adaptive-DPS evidence gap. The distinction is intentionally visible in the v113 user response as “프로필 공급원 26/26 (계획 경로; 전체 적응형 Native 미검증)”. Existing 26/26 physical base SimC evidence and prior adaptive receipts remain historical evidence; no blanket Native matrix was repeated.

### 11.2 Dependency graph and session identity

runner/v212_environment_manifest.py now seals a deterministic v212_environment_dependency_graph_v1 with fingerprints for:
- v213 source catalog artifact;
- v191 gear/tier/budget source inputs;
- v196 approved UI projection;
- v098 profile identity and generated files;
- selected-special exact identity and static-item cache snapshot;
- v208 Start receipt;
- Windows package manifest;
- SimC binary SHA and revision.

The graph defines downstream invalidation rules and compare_dependency_graphs() emits a read-only delta against the prior sealed manifest. It never deletes caches or mutates historical sessions. Tests confirm that a v208 receipt change invalidates the Environment Manifest only when the exact selected-special/static-cache identity is unchanged; the static item cache remains preserved.

runner/v106_user_session_controller.py now binds current-season session identity to the raw v213 artifact SHA, embedded manifest SHA, game build, SimC revision and (when present) package-manifest SHA. Local file paths are excluded, so relocating identical bytes preserves identity. Changed source/package bytes create a new session identity rather than reusing a stale current-season session. runner/v113_local_web_api.py checks that the packaged source and package manifest still match the session identity before Start.

This is dependency-aware **identity isolation and invalidation planning**. The full incremental Environment Build orchestrator that fetches changed sources and automatically schedules only affected rebuilds is still not implemented.

### 11.3 Actual regression evidence after the supplier and dependency changes

- [v098 offline #41194394144](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394144): SUCCESS.
- [v187 tier-overlay #41194394156](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394156): 13 tests PASS.
- [v177 current-season product #41194394055](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394055): 12 focused tests + 84 regression tests PASS. Includes source-artifact SHA session identity and relocation-stable path checks.
- [v180 multi-level product #41194394105](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394105): 26 DPS × 5 target-level plan matrix, 3 focused tests + 63 regression tests PASS. Native-six-cases job SKIPPED.
- [v191→v211→v213→v196 #41194394128](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394128): SUCCESS, integrated source pipeline and P3-C source-backed manifest handoff PASS, Native0. Artifact [#13040083134](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394128/artifacts/13040083134), 117,921 bytes; v213 digest  b888123728097371705c037ae2fc0085cc6735fac870f000b7606b1428d5ced5.
- [v113 API #41194394127](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194394127): Ubuntu 24.04 and Windows 2022 each **145/145 PASS**.
- [v181 latest-source Windows package #41194661922](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194661922): Windows Python 3.12/3.14 SUCCESS; 188-file ZIP; actual extracted CMD launcher, v213 package identity, localhost HTTP security, three Plan/restore cases PASS; Native0. Artifact [#13039854689](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194661922/artifacts/13039854689), 744,988 bytes.
- [v182 latest-source UI/package #41194661890](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194661890): Ubuntu and Windows SUCCESS; each OS 76 focused + 67 compatibility + 2 package tests PASS; Windows extracted HTTP/three plans PASS. Artifact [#13040520318](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41194661890/artifacts/13040520318), 744,988 bytes.
- Both v181/v182 workflows now default to the exact latest successful source artifact v213-source-to-catalog-41194394128 (artifact #13040083134), rather than the older #41178704794. Its downloaded GitHub artifact ZIP SHA256 is aada3cf81d0528bdc45674f5979b3bb5189594b83db3d3feca6cb4ecf545423f; the embedded v213 manifest SHA remains b888123728097371705c037ae2fc0085cc6735fac870f000b7606b1428d5ced5.
- New SimC Native calls: **0**. New SimC binary builds: **0**. Optimizer/cache mutations: **0**. v177/v180 opt-in Native jobs were skipped. No main/v003/v016/Project UI/visibility/official Work OS changes.

### 11.4 Current P3 state and next work

| Component | Current state |
|---|---|
| P3-A v212 manifest + exact v213 input + dependency fingerprints | Implemented |
| P3-B v191→v211→v213→v196 source/catalog handoff | Actual source-backed PASS |
| v208 Start receipt serialization and v212 verification | Implemented; existing Native/cache receipts reused |
| v213 packaged Windows catalog and default source selection | Implemented and actual Windows HTTP PASS |
| 26 DPS plan/profile suppliers | **26/26 PASS** |
| Full adaptive Native acceptance across all 26 | Not claimed / incomplete |
| Dependency comparison and session identity isolation | Implemented, read-only/no destructive cache purge |
| Full incremental Build orchestration | Not implemented |
| User-facing Build API/UI for environment refresh | Not implemented |
| Windows one-click Build/Start/progress/cancel/resume integration | Not implemented |

Next:
1. Implement the production incremental Environment Build coordinator around the existing v191/v211/v213/v196/v212 components. Use the dependency graph to reuse unchanged source/cache artifacts and schedule only affected steps; do not delete historical sessions or static item cache.
2. Connect the Build readiness result to the existing user API/UI and show READY / READY_WITH_LIMITATIONS / BLOCKED plus missing joins, supplier coverage, cache hits and Native scope.
3. Connect the sealed v098/v208 target profile to the existing v093/v094/v095 adaptive optimizer; do not add a new optimizer.
4. Complete only the exact missing embellishment item/slot, temporary-enchant hand-applicability and gem-property→item-ID joins. UNKNOWN remains UNKNOWN/PENDING.
5. Add Windows one-click Build/Start progress/cancel/resume and verify the packaged runtime. Do not repeat the 26×N Native matrix; use existing evidence and targeted tests only.

