# P3-BC — Same-season SimC balance updates do not rebuild the static environment

2026-11-03 KST. Direct user policy clarification (latest authority). Isolated branch only; `main`, v003 immutable, original v016, Project UI and Work OS promotion unchanged.

## Product rule

**Season identity and static source content are NOT SimC executable revision nor the WoW client build number.** SimC balance/APL updates are frequent even while season gear, tier, gems, flasks, oils, permanent enchants and their static CHMV data remain unchanged. A new SimC revision/binary does not by itself invalidate same-season static item snapshots, existing independently verified G/J/F/O, item IDs, or user-visible choices. Do not rebuild the entire environment or repeat bulk Wago+Native just because the binary was updated.

At an ordinary SimC update:
- Read locally available season ID / expansion ID and retained verified source/selected option fingerprints and compare against the previous verified environment. This is a **cheap read-only check**; no new full Wago snapshot, no 26-specialization Native run, no proactive regeneration of `item_data.inc` per nightly. No silent assumption that the remote source is unchanged merely because local hashes match; if remote status is unknown, record it as unknown.
- If season identity is unchanged and the relevant STATIC sources remain verified, **reuse** representative gear, weapons, tier, selected option identity and same-season static item cache. Keep full actual source revision/build metadata for provenance. If only a client build number changed, it is a change-detection hint, **not** a mandatory blocker.
- If a reliable season identity changes, a new item is reported/observed, or relevant source content actually changes, validate only affected source records (item IDs, static stats, tier, selected gems/flasks/oils/permanent enchants) and recalculate the impacted G/J/F/O, B/T. Do not copy old-season budgets into a new one. Unknown or conflicting identity is a scoped PENDING, never a false ready state.
- The SimC binary SHA/version/revision and actual profile/APL/combat/iterations remain part of the **DPS** cache identity. An updated binary must never silently reuse stale DPS as new-version results. Old historical cached runs are retained for their original identity. On a new SimC build, Native item-related checks should be limited to an observed incompatibility or actual static/effect/scaling change; avoid a new approval gate that separately reimplements SimC effects.

## Scope of code correction

`runner/v229_simc_only_source_seed.py`: source-only candidate collection no longer requires `previous_game_build != expected_build` in `season_change` / `expansion_change`. An absent local previous build is accepted even under the real game event (with `cold_start` retained as legacy source-only receipt compatibility). Previous-build record syntax is checked, but it never proves the new season. **The actual generated SimC source files MUST still agree with their own declared build**, and immutable Git tree/blob, selected physical gear, G source proof remain separate. This does **not** make a new-version SimC generated source compatible with old-build Wago gear automatically.

`tests/test_v229_simc_only_source_seed.py` covers a new season/expansion at the SAME client build, no-history real season event, malformed prior build and mismatching generated item/gem builds. Exact source-only receipt remains G/J/F/O/B/T=null, environment_ready=false.

## Existing infrastructure to reuse; no duplicate refresh engine

- `runner/v193_simc_local_updater.py` already updates the managed local SimC binary without changing its installed season DB. It records actual local binary SHA and short nightly revision.
- `runner/v151_season_catalog_impact.py` already compares season catalog inputs in memory to give scoped physical vs DPS review recommendations, with `same_season_static_records_always_invalidated=false`.
- `runner/v212_environment_manifest.py` already models binary/revision dependency effects separately from static item cache and differentiates adaptive DPS cache identity.
- **Known remaining integration issue:** `v212.compile_manifest` currently demands `v098.native_revision == v213.simc_revision` even where static item data is valid for the same season. This must be decoupled with an explicit **static source identity vs actual executing SimC revision** contract and tested before claiming the whole user workflow can run after independent SimC nightly upgrades. Do not simply delete revision checks: the binary's actual revision and profile compatibility still matter, and historical receipts must remain immutable.
- The present P3-BC change is one targeted source-acquisition correction, not a new static-delta automation or final product completion. Incremental remote item-change checks, if added, should use existing providers and observed IDs instead of a new whole-season crawler, and are not required at every SimC nightly.

## Verification

Offline tests through existing `.github/workflows/v212_environment_manifest_offline.yml` only, zero newly executed Native. Preserve exact Actions result and scope in CURRENT after CI.

**Pending:** real different-build old-season Wago vs newly updated SimC acceptance, season-scoped G/J/F/O reconciliation and complete adaptive SimC E2E.
