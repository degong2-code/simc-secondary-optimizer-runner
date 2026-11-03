# P3-BI — Selected ordinary gear season provenance through the ONE Environment Build
2026-11-03 · isolated implementation record

## Authority / what this work is
Current approved v1.4.3 seasonal G/J/F/O automatic environment engine, 26 DPS only, P3-AA single normal Build. Implements **one missing dataflow link**, NOT a new optimizer or second season/SimC engine. Production Environment Build remains PENDING mandatory authenticated G/J/F/O, no user READY or automatic item admission.

## Concrete defect and existing owner components
- `v163_zero_seed_db2_join.build_index` already preserves acquisition source `raid_journal`, `mplus_journal`, `selectable_stat_craft` and original conditions `DisplaySeasonID`, `WorldStateExpressionID`, encounter/instance IDs.
- `v165_current_season_gear_pool.compile_pool` passes `acquisition_sources` forward, and `v166_compact_product_gear_db` previously collapsed them to just `source_kinds`. The `v167` catalog and `v232` selected profile therefore could not tell a direct DB2 display-season match apart from unscoped raid, unresolved world state or Localbots-only source. `v169` pure selector sorted many candidates by ID, allowing unverified low-ID source to displace an explicitly matching source.
- Neither WCL live zone nor a source-kind label proves a particular selected item variant is part of the active season. Avoid asserting season certification just because Wago/SimC physical item identity matches.

## Code in this branch
Code/test SHA **`dbffb062319bacb81b92370d7ff6c4ac2cad118d`**; initial implementation `6537ec32aa970ad1a74fc94f00fe3cabadb956a3`; test fixture correction `a6e4aa19c98863f88bd15edaeef721f43cf13268`.

1. **v166:** Retain a small allowlisted, structured `source_evidence` per candidate (source, DB2 season and world-state, encounter/instance IDs, etc), rather than full WCL names or duplicate large DB2 sources. `v167` forwards and validates preserved source kinds; legacy v166 catalogs containing *only* kinds remain valid and stay status UNKNOWN. This propagation is source identity, not source authentication.
2. **v232:** Classify each selected non-tier slot as explicit same-display-season / no-world-state **candidate**, unresolved world-state, unscoped raid, unmatched M+, expansion craft, Localbots supplementary or lacking source condition. Prefer exact display-season candidates for ordinary and common slots. Reuse `v169.shape_weapons` for a complete physically compatible explicit-source weapon form if present; otherwise use the existing full physical pool and report missing source evidence. Do not change SimC primary stat/weapon-form logic.
3. **v232/v216:** Seal per-selected-slot `selected_ordinary_source_provenance`, `selected_non_tier_season_condition_pending_slots` and explicit-source count in existing v217 one-spec source receipt. Every provenance row explicitly has `season_membership_authenticated:false` and `G_source_approved:false`. Tier remains unproven. `G/J/F/O/B/T=null`, `environment_ready=false`, zero Native. The normal `v216.collect_wago_new_season_source` one-spec response returns these diagnostics for the very same Build/source stage; no extra HTTP.
4. Reuse the installed season static source and DPS cache policy unchanged. v217 fingerprints code changes and receipt input identities; no historical cache deletion or redundant per-specialization measurement. This keeps source origin and candidate selection separate from G numerical proof.

## Actual CI verification
At **exact tested code SHA `dbffb062319bacb81b92370d7ff6c4ac2cad118d`**:
- [v212 contract Actions #41550381207](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41550381207): Ubuntu/Windows each **420 tests, 0 FAIL, 4 SKIP**, SUCCESS. Direct new focused tests `test_selected_sources_prefer_explicit_db2_season_and_keep_unknowns_pending` and `test_exact_source_conditions_reach_compact_candidates` PASS; `V212_ENVIRONMENT_MANIFEST_NATIVE0_PASS` on both systems.
- [v182 UI regression #41550381202](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41550381202): Ubuntu and Windows both SUCCESS, 92+81+focused2 tests per runner. No live Native; packaged HTTP plan remains zero Native.
- [v167 focused #41550381213](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41550381213): **13 tests, 0 FAIL, 1 SKIP**, SUCCESS.
- [v166 focused #41550275029](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41550275029): after test fixture correction at `a6e4aa19c98863f88bd15edaeef721f43cf13268`, SUCCESS; no later changes to v166 code.
- Initial CI on `6537ec32aa970ad1a74fc94f00fe3cabadb956a3` **failed** due to a newly added v166 test calling a nonexistent fixture and v167 falsely rejecting old source-kind-only catalogs; keep original Actions FAIL #41550204191 / #41550204428 / #41550204347. Subsequent fixes addressed both.
- **Actual new Wago/Blizzard/WCL/SimC remote downloads this turn: 0. Native actual calls: 0.** Evidence is offline/synthetic source and physical selection testing, not actual live-source season certification. No actual G measured; no readiness promotion.

## Next execution slice, same engine only
1. Use newly preserved per-slot season IDs/WorldState IDs plus the exact existing `v163/v245/v250/v251` tier provenance to resolve actual current-season item membership. When display-season 0 on raid or world-state expression nonzero, obtain authoritative interpretation **only for the selected 13/14 IDs**, not rebuild all DB2/26 specs; prefer a complete valid alternative without extrapolating.
2. When all selected representative slots and tier can be justified for the active season, reuse existing `v233/v234` or `v226/v227/v228` and same-season static cache for **minimal one-spec target334 G** observation; never promote old PvP/Localbots-only `G=2847`.
3. Independently quantify highest-quality same-season J/F/O and eligible weapon oil/enchants E using existing exact physical source join (v221, v189-v191, etc). Then plug authenticated receipts into `v222.preprofile_budget` from P3-BG, followed by v098/reconcile/v212 and existing Policy A. Preserve P3-AA cold-history single-engine final acceptance.

**Not done:** numerical G/J/F/O, exact active season/tier membership, policy A options, normal ready Build and optimizer DPS E2E. User's main product chat remains owner. No merges/main changes, v003 immutable, v016 original, Project UI, Work OS, official shared state or WEQUIP authority changes.
