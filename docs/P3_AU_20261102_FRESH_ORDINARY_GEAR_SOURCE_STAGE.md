# P3-AU — Normal Build same-season ordinary gear source stage (2026-11-02)

## Purpose and authorized scope

Continue P3-AT without redoing Wago↔SimC tier identity or creating a parallel collector/optimizer. A *normal Environment Build* must derive a source-backed ordinary equipment and weapon candidate set from authenticated same-build raid/M+ provenance before G can be attempted. This is **candidate preparation only**, not current-season representative approval or target-ilvl G verification.

Latest authority: approved v1.4.3, DPS26, P3-AA single Build engine, P3-AT handoff. No main, immutable v003, original v016, Project UI, Work OS or authority promotion.

## Isolated implementation (P3-AU code)

1. `runner/v165_current_season_gear_pool.py`: authenticated v163 Wago raid/M+ source can now be classified when optional v162 Localbots source is not collected (`delve=None`). Missing Localbots is stated as `OPTIONAL_SOURCE_NOT_COLLECTED`, not counterfeited as an authenticated source. Existing explicit Localbots build/expansion checks remain. **Only the fresh caller provides `budget_source=None`**, so installed J/F are never read.
2. `runner/v216_environment_build_coordinator.py`: new `_fresh_ordinary_gear_source_stage` uses the existing v163 report, same-build Wago ItemSparse/Item and a single additional `ItemXItemEffect` source relation. It invokes existing **v165 → v166 → v167** (no new catalog algorithm), preserves exact source-build identity, SHA-seals the stage with existing v217, and reports conditional/ordinary equipment candidates. On an identical sealed rerun, stage outputs can be reused with **0 HTTP**.
3. The original `collect_wago_new_season_source` includes `fresh_ordinary_gear` in its result and network accounting. A custom injected base Wago transport without an explicit `gear_transport` returns `FRESH_GEAR_INJECTED_SOURCE_EFFECT_TRANSPORT_PENDING` without mixing synthetic base rows with live effect sources. Production default source uses the actual Wago URL.
4. New `tests/test_v254_fresh_ordinary_gear_in_build.py` adds four **synthetic-only tests**: source-backed candidate + second-run 0 HTTP, wrong-build/old-expansion fail-closed, a trinket-only pool remaining PENDING, and missing authenticated raid join 0 HTTP. Existing v216/v165 tests must continue passing.

## Evidence classification at this handoff

- **Implemented in isolated GitHub commits:** v165 optional supplement, v216 normal Build source-only candidate stage, and four source-stage regression tests (the fourth prevents a trinket-only inventory from being misreported as an ordinary gear pool).
- **Existing real source evidence reused, not newly executed:** P3-AT Wago↔SimC 13x5 exact IDs [#41455991413](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41455991413); v229 immutable source seven HTTP then zero [#41457632768](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41457632768).
- **Existing synthetic regression (prior code only):** Ubuntu and Windows each 360 tests / 0 FAIL / 4 SKIP [#41457357814](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41457357814).
- **New P3-AU synthetic + existing regression, now EXECUTED:** [Actions #41472967647](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41472967647) on code SHA `bcb4f18cfc09f99a453e4645aa75df00e284b09f`, actual Ubuntu and Windows job logs: **364 tests each / 0 FAIL / 4 SKIP, SUCCESS**, `V212_ENVIRONMENT_MANIFEST_NATIVE0_PASS`. Four new tests verified included. An earlier focused run [#41472617718](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41472617718) for 3 tests: each OS 363 / 0 FAIL / 4 SKIP. **These are synthetic transport tests**, not a real Wago ItemXItemEffect receipt, full season, or Native G. No new real Wago HTTP or SimC Native was invoked.
- **Environment/product:** uninstalled, `G/J/F/O/B/T` not newly verified, `source_season_verified=false`, `season_representative_verified=false`, no 26-DPS adaptive E2E. Newly classified plain gear is not a promoted profile nor a certified SimC variant.

## Efficiency and remaining work

- Extra network budget: **at most one** same-build ItemXItemEffect HTTP attempt when the v163 source is authenticated and no matching sealed output exists; no requests when unauthenticated, source incomplete, or an injected transport lacks its matching effect source.
- Memory: bounded streamed chunks are collected up to 12 MB for the extra CSV (not an unbounded table dump); remaining ItemSparse/Item passes reuse their existing streaming CSV parsers. The v165 and v166 parsers each read some shared DB2 columns, which is a later I/O optimization opportunity but not grounds to fork another parser.
- Cache: v217 source stage depends on exact build, upstream v163 report SHA/receipt, and existing classifier code digest. No static item cache or DPS cache invalidation; no Native.
- The focused and affected offline regression verification is complete on both OS at SHA `bcb4f18c…`. Next meaningful verification is one **bounded real source-backed build** with the existing Wago DB2 snapshot + exact same-build ItemXItemEffect input to check candidate coverage and cached reuse; do not convert this into a new Native matrix.
- Next implementation after validated code: bind provenance-preserving candidate IDs into existing v169/v226/v232 representative selection, reject old PvP or nonseason sources, acquire the exact valid SimC item metadata for one target archetype, and verify G using existing optional Native/caches. In parallel, validate new same-build highest-quality J/F/O and E options; then use existing v222 B/T and v212/v098/optimizer. Do **not** re-fetch the already proven 13x5 tier identity or run a blanket Native matrix.
