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

**P3-A — artifact contract and gap closure (v212 first implementation; not full acceptance):**
- **Implemented in v212:** one versioned Environment Manifest references the existing v191 source aggregation, v211 effect-classification manifest, v196 approved UI catalog and v098 target-profile result without copying full profiles or absolute paths. v208 is **not yet a separate manifest input**; only the optional static-cache file referenced by the v098 target manifest is hashed.
- **Implemented in v212:** exact schema/build/SimC-revision checks, source JSON SHA references, profile/scenario/fillers/manifest file identities, binary SHA, deterministic digest, fail-closed mismatches and Native0 manifest compilation.
- **Partial / still open:** changed inputs alter the digest, but there is no production dependency-graph invalidation/orchestrator yet. The current fixed `unresolved_dependencies` list is not a dynamic missing-join report.
- Keep existing UI selection approvals unchanged; the current manifest checks `selectable_count == 1` but does not itself assert that the sole selected enchant ID is exactly 7967.

**P3-B — source-to-catalog integration (v213 first implementation: actual source E2E PASS, not full product acceptance):**
- **Implemented:** v191 emits compact gear candidate rows with exact InventoryType/class/subclass masks, all 13 class/65 tier IDs, related-source counts, raw input SHA256, and the three exact SimC generated-table SHA256 values.
- **Implemented:** v211 accepts the v191 artifact directly as its current-season enchant candidate source. The new path does not read the separate pinned 38-row candidate list; it preserves the existing runtime manifest as a compatibility/evidence boundary while recording v191 as the actual candidate-source schema.
- **Implemented:** v213 joins v191 candidate and v211 classification rows by exact enchant ID, SimC token, rank, item class, inventory mask and subclass mask; derives armor-enchant slot groups only from source masks; derives gear groups from exact InventoryType; unknown gear inventory types remain UNKNOWN/PENDING.
- **Implemented:** v196 accepts the versioned v213 artifact by explicit path and v197 consumes its v211 classification rows. Classification is distinct from UI approval; only the pre-existing 7967 approval is selectable, 8025 remains developer-only, and 36 remain locked.
- **Actual artifact E2E:** [Actions #41169754323](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41169754323), artifact [#13031015315](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41169754323/artifacts/13031015315), v213 digest `b888123728097371705c037ae2fc0085cc6735fac870f000b7606b1428d5ced5`. Actual counts: gear 511, tier 13/65, current-season enchant candidates 38/38, food 192, potion 61, embellishment registrations 20, temporary enchant source rows 117, gem properties 2409. Gear inventory groups contain 511 rows and zero unknown slot rows. Enchant groups: boots3/chest4/helm6/ring9/shoulders6/weapon10.
- **Cross-platform regression:** [Ubuntu + Windows #41169754402](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41169754402), 62/62 tests PASS on each OS, including six v213 contract tests. No Native calls, no SimC binary build, no optimizer/cache mutation.
- **Still limited:** v196's default data path has not been switched to a packaged v213 artifact; the artifact is explicitly consumed by the P3-B CI path. Embellishment registrations do not yet join exact item IDs/slots, temporary enchants do not yet resolve exact hand applicability, and gem-property rows are not gem item IDs. P3-B is a source/catalog bridge, not a user-facing Environment Build.

**P3-C — one-click target environment:**
- connect approved catalog selections to v098 profile assembly for all 26 DPS specializations;
- reuse v208 exact selected-L acquisition and existing CHMV budget bridge;
- create sealed profile/manifest and hand off to existing optimizer.

**P3-D — Windows product experience:**
- one-click Build / Start, progress, cancellation/resume, incremental refresh, cache report and downloadable diagnostics;
- targeted Windows Native only for changed physical inputs; no blanket 26×N matrix.

**Acceptance criteria:** same inputs and source identity produce byte-stable manifest; unchanged artifacts are reused; a changed source invalidates only its dependents; unknown joins block only the affected choice rather than erasing unrelated options; plan mode Native0; Start makes only the selected missing static lookups; final profile retains full user-selected options; optimizer/cache/statistics behavior is the existing approved path.

**Current state:** P3-A has the v212 Native0 Environment Manifest assembler with 9/9 tests on Ubuntu and Windows. P3-B now has a real v191→v211→v213→v196 source/catalog artifact path and a real source-backed Actions receipt. However, v212 does not yet consume v213 directly, the one-click production orchestration and user Build API/UI do not exist, all-26 target-profile assembly is not yet connected to this catalog, v208 selected-L receipt integration remains separate, dependency invalidation is not implemented, and the Windows one-click experience remains incomplete.


## 8. P3-A first implementation — v212 Environment Manifest assembler (2026-10-31)

**Implemented on the isolated branch:** `runner/v212_environment_manifest.py` is a deterministic, no-Native artifact join. It consumes existing v191 season-candidate JSON, v211 enchant-classification JSON, v196 approved UI-catalog JSON, v098 preparation result, and the v098 target folder. It does not call any collector, API, SimC binary, or optimizer.

It validates:
- exact v191/v211/v196/v098 schema contracts;
- same season/game build and exact 40-character SimC revision across v191, v211 and v196;
- 38 enchant rows and current selectable-count boundary of exactly one;
- source candidate/classifier Native0 and no automatic UI promotion;
- v098 plan-ready status, target archetype/ilvl/B/T, generated profile manifest and the four exact generated files;
- target SimC binary SHA, optional static-cache SHA, and profile/scenario/fillers/manifest SHA;
- target manifest revision and existing adaptive Native limit 6.

The resulting manifest references the source component hashes and profile identities without copying the full user profile or emitting local absolute paths. Its digest is deterministic for the same inputs. It reports `READY_WITH_LIMITATIONS` while 26-spec profile coverage and final profile/optimizer handoff are incomplete. P3-B now produces a separate v213 source/catalog artifact, but v212 does not yet consume that artifact directly. A changed profile file changes the environment digest. Source/build/revision/approval/path mismatches fail closed. The module makes **Native0 and network0**.

**New tests:** `tests/test_v212_environment_manifest.py`, 9 tests built from synthetic JSON fixtures and a dummy binary. The final run [Ubuntu + Windows focused #41160002104](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41160002104): **9/9 PASS on each OS**, compile PASS, Native0 marker PASS. This includes relocation stability: the same profile/source identity in a different local target directory yields the same Environment digest. This is contract testing, **not** a real v191→v211→v196→v098 end-to-end run. No previous Native/cache evidence was rerun or invalidated.

**Code-review gaps to close before treating the manifest as a sealed production contract:**
- The v212 input `bootstrap_sha` is accepted but currently unused. The output hashes a normalized subset of v098 identity plus its generated files; it does not include the raw bootstrap-result file SHA. Preserve relocation invariance, but make this normalized provenance contract explicit or correct it.
- The current approval check validates only one selectable enchant by count, not the exact authorized ID 7967. v196's own tests separately assert 7967, but v212 should bind the exact approved identity.
- Current-season constants `38` candidate rows and `1` selectable choice are pinned to this season; do not present v212 as season-agnostic until the versioned source contract makes those counts data-driven.

**Not yet implemented:** automatic production invocation of v191/v211/v213/v196/v098 into one user Build command; actual user Build button/API; all-26 DPS representative profile suppliers connected to the catalog; selected L/E lookup integration beyond existing v208; dynamic dependency invalidation; Windows one-click progress/cancel/resume. The current v212 CLI is still an internal manifest assembler that requires its input artifacts to have already been produced. It does not make the product Environment Builder complete.


## 9. P3-B first implementation — v213 source-to-catalog bridge (2026-10-31)

**Code on the isolated branch:**
- `runner/v191_unified_season_data_update.py` now retains 511 source gear candidate rows with exact inventory/class/subclass applicability, 13 class tier contracts/65 piece IDs, related-source counts, raw source input SHA256, and exact SimC generated permanent-enchant/temporary-enchant/gem-property source hashes.
- `runner/v211_enchant_source_effect_classification.py` accepts the v191 artifact directly. The live v191 candidate rows are projected into the existing v211 source contract; the separate pinned 38-row candidate JSON is not read on this path. The old runtime classification manifest remains a compatibility/read-only evidence boundary, not the source of current candidate rows.
- `runner/v213_source_to_catalog.py` creates schema `v213_current_season_source_to_catalog_v1`. It exact-joins candidate/classification identity, derives gear slot groups from InventoryType and enchant slot groups from inventory masks, preserves unknown joins as pending, and emits one deterministic manifest with v191/v211 source hashes.
- `runner/v196_current_season_user_catalog.py` accepts the v213 artifact by explicit path; `runner/v197_enchant_effect_families.py` can consume the v211 rows from that artifact. Existing UI approval is unchanged: only 7967 is selectable after v196's existing evidence check; 8025 remains developer-only and 36 rows remain locked.

**Actual source-backed run:** [Actions #41169754323](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41169754323), commit `29d985a999293adb3132a27c83ecf26602b217c8`, SUCCESS. It reused existing v189/v190 source artifact from run `41017578894`, fetched only the exact pinned SimC source files required for the compiler, generated the v191 artifact, classified its 38 current-season enchant candidates, built v213, then passed the actual v213 artifact through v196. Artifact [`v213-source-to-catalog-41169754323`](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41169754323/artifacts/13031015315), 93,908 bytes compressed, 7-day retention. v213 manifest SHA256: `b888123728097371705c037ae2fc0085cc6735fac870f000b7606b1428d5ced5`.

**Observed catalog scope:** 511 gear rows across 17 exact inventory groups (zero unknown current rows); 13 classes/65 tier IDs; 192 food and 61 potion item candidates; 38/38 current-season enchant classifications; 20 embellishment/effect registrations without resolved item IDs; 117 temporary-enchant source rows; 2,409 gem-property rows without resolved gem item IDs. The 38 enchant slot groups are boots3/chest4/helm6/ring9/shoulders6/weapon10. v213 itself marks all rows nonselectable; v196 applies the existing approval evidence and exposes only 7967.

**Regression evidence:** v191 focused 6 tests PASS within #41169754323; the integrated Ubuntu workflow reports 22 tests PASS. [Catalog integration #41169754402](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41169754402) reports 62 tests PASS on Ubuntu and 62 on Windows, including all six v213 contract tests. New SimC Native calls: 0; SimC binary builds: 0; optimizer/cache mutation: 0. The workflow fetches pinned source text at the Actions layer; the v191/v211/v213 compilers themselves report network0.

**Important boundary:** v196's default checked-in data path and the Windows beta package are not yet switched to or bundled with v213. The actual v196 consumer test passes when the v213 artifact path is supplied explicitly. v212 does not yet bind v213 as an Environment Manifest input. This proves the source-to-catalog bridge, not the one-click user product, the 26-spec profile assembly, or a full optimizer run. No main/v003/v016/Project UI/visibility/Work OS change was made.
