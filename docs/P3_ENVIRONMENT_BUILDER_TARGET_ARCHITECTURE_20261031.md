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

**P3-B — source-to-catalog integration:**
- make v191-derived season candidates and v211 source classifications flow into v196 through a single versioned artifact contract; avoid hand-maintained duplicate candidate lists;
- generate slot-grouped options from exact masks and item joins, with selection state separate from classification.

**P3-C — one-click target environment:**
- connect approved catalog selections to v098 profile assembly for all 26 DPS specializations;
- reuse v208 exact selected-L acquisition and existing CHMV budget bridge;
- create sealed profile/manifest and hand off to existing optimizer.

**P3-D — Windows product experience:**
- one-click Build / Start, progress, cancellation/resume, incremental refresh, cache report and downloadable diagnostics;
- targeted Windows Native only for changed physical inputs; no blanket 26×N matrix.

**Acceptance criteria:** same inputs and source identity produce byte-stable manifest; unchanged artifacts are reused; a changed source invalidates only its dependents; unknown joins block only the affected choice rather than erasing unrelated options; plan mode Native0; Start makes only the selected missing static lookups; final profile retains full user-selected options; optimizer/cache/statistics behavior is the existing approved path.

**Current state:** architecture contract plus the v212 P3-A first manifest assembler. Its 9×2 tests use synthetic fixtures, not actual production v191/v211/v196/v098 artifacts. The production source-to-catalog chain, real artifact end-to-end manifest, all-26 profile coverage, explicit v208 selected-L receipt integration, dependency invalidation/orchestration, and final Windows one-click experience remain incomplete.


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

The resulting manifest references the source component hashes and profile identities without copying the full user profile or emitting local absolute paths. Its digest is deterministic for the same inputs. It reports `READY_WITH_LIMITATIONS` while 26-spec profile coverage and source/catalog handoff are incomplete. A changed profile file changes the environment digest. Source/build/revision/approval/path mismatches fail closed. The module makes **Native0 and network0**.

**New tests:** `tests/test_v212_environment_manifest.py`, 9 tests built from synthetic JSON fixtures and a dummy binary. The final run [Ubuntu + Windows focused #41160002104](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41160002104): **9/9 PASS on each OS**, compile PASS, Native0 marker PASS. This includes relocation stability: the same profile/source identity in a different local target directory yields the same Environment digest. This is contract testing, **not** a real v191→v211→v196→v098 end-to-end run. No previous Native/cache evidence was rerun or invalidated.

**Code-review gaps to close before treating the manifest as a sealed production contract:**
- The v212 input `bootstrap_sha` is accepted but currently unused. The output hashes a normalized subset of v098 identity plus its generated files; it does not include the raw bootstrap-result file SHA. Preserve relocation invariance, but make this normalized provenance contract explicit or correct it.
- The current approval check validates only one selectable enchant by count, not the exact authorized ID 7967. v196's own tests separately assert 7967, but v212 should bind the exact approved identity.
- Current-season constants `38` candidate rows and `1` selectable choice are pinned to this season; do not present v212 as season-agnostic until the versioned source contract makes those counts data-driven.

**Not yet implemented:** automatic production invocation of v191/v211/v196/v098 into one command; a v191→v211→v196 source artifact pipeline; actual user Build button/API; 26 DPS representative profile suppliers; selected L/E lookup integration beyond existing v208; Windows one-click progress/cancel/resume. The current v212 CLI is an internal manifest assembler that requires its input artifacts to have already been produced. It does not make the product Environment Builder complete.
