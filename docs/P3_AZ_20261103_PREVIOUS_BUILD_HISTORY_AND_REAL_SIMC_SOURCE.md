# P3-AZ — Prior game build vs locally recorded history; one real full SimC source proof

**Date:** 2026-11-03 KST. **Authority:** newest direct user clarification, DPS26 and v1.4.3, P3-AA original Build engine. **Scope:** isolated branch only; main/v003/v016/Project UI/Work OS unchanged.

## Direct product semantics correction

A new game season, expansion, or update does **not** imply that a prior WoW game build did not exist. Even after an expansion, a prior released build existed; however its equipment, gems, flasks, oils and G/J/F/O budget are **not necessarily applicable** to the new expansion/season. A truly first-install/cleared local application may simply have **no prior build recorded in the product**.

The prior game build value is useful for change detection, incremental cache reuse and anti-replay. It is **not a mandatory prerequisite** to authenticate current-build SimC source files or to determine the target season’s own G/J/F/O. It must never be guessed from an old fixed table, and an unknown local history cannot by itself prove a season transition.

v229’s previously implemented `cold_start` spelling is retained as an **internal compatibility source-collection mode** to preserve existing v229 inventories and stage receipts. It does **not** mean expansion launch or actual absence of a prior WoW build.

### Implementation

- `runner/v216_environment_build_coordinator.py` adds `_simc_source_collection_context(requested_event,previous_game_build)` as a pure, validated mapping:
  - `requested_game_event`: preserves exactly `season_change`, `expansion_change`, or `mid_patch`;
  - `previous_build_record_status`: `NOT_RECORDED` or `RECORDED`;
  - `source_collection_mode`: legacy v229 `cold_start` **only** for unrecorded prior build during season/expansion source acquisition; with a recorded prior build, preserve the original event;
  - explicit `previous_game_build_is_not_a_season_proof:true`.
- Normal `v216` Build emits `simc_source_collection_context` alongside its existing `simc_source_event` compatibility field. It continues the existing v229 verified source-collection path without touching current season G, user equipment or prior static/Native caches. New expansion with **unrecorded** prior build no longer gets rejected solely because v229 had been invoked with `expansion_change`; v229 sees the legacy source-only compatibility mode but the actual game event remains recorded.
- `tests/test_v257_exact_simc_commit_in_build.py::test_game_event_is_not_local_previous_build_history` verifies season versus expansion, both recorded/unrecorded, mid-patch, invalid event and invalid prior-build syntax. No extra HTTP or Native.

## Actual source evidence, new this turn

**One-shot real GitHub Actions #41478919832**: [job and source logs](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41478919832).

- Used existing **same-build historical P3-AT source reference** `game_build=12.1.5.70575`, **exact pinned SimC Git revision** `710c2408bfd3ae4df71b8cd55cdf01f63fd6c926`, a known matching pair — **not an assertion that this is the newest active game build or a verified new-season profile**.
- Actual first-party `v229.collect(include_item_data=True,previous_game_build=None,season_event="cold_start")` succeeds with Git tree/blob authentication and no prior local build record. `item_data.inc` is **26,439,588 bytes** with Git blob SHA-1 `8bba1c090277e1ebb69e76170cce1923151a5806`.
- Existing `v231.select` found 5 SimC physical tier IDs for paladin/retribution, declared `midnight_season_2`: **271463, 271464, 271465, 271466, 271468**. Existing `v232.find_candidate` with **SimC-only** selection produced **13 distinct selected slots** at target ilvl 334.
- The selected 13-slot SimC-only source candidate does **not** establish physical current-season membership: the source may include old/unsupported/plain-effect gear. This real trial did **not** use the new Wago v167 source filter or G Native, and did not prove the active season’s representative gear or stat budget. No actual SimC Native runs or DPS cache mutations.
- Source files were ephemeral in the one-shot Action; logs are the recorded new proof. They were not installed into the product environment. Reusing the exact pinned revision/unchanged seasonal static cache remains preferred.

## Actual focused CI

[GitHub Actions #41478738055](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41478738055): final tested mapping code `74bac86f9aaf52f83cc7c064294cd9fd503481be`, **Ubuntu and Windows each 386 tests / 0 FAIL / 4 SKIP, SUCCESS**, Native0. Other P3-AX/P3-AY offline receipts remain valid for their own earlier code scope; do not claim a new entire-product E2E PASS.

## Continuing priority

Use one **verified current-season** source scope to intersect the actual Wago v167 plain ordinary items/weapons with exact pinned SimC v251/v232 metadata for the user's selected spec. If specific slots are absent or season membership remains ambiguous, return a concrete PENDING slot report, not false successful G or an old PvP substitute. Next calculate valid target-ilvl G via existing optional native/reference method, and automatically establish highest-quality J/F/O and permanent enchant E without copying previous-season constants. Reuse original v222 B/T, profile generator and adaptive SimC for final integration.

This is engine progress; actual fresh-season G/J/F/O and complete user-ready optimization remain **not implemented/verified**.
