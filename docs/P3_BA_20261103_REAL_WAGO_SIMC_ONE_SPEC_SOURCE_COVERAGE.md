# P3-BA — Real same-build Wago × pinned SimC source coverage, one DPS (2026-11-03 KST)

## Purpose and authority

Continue P3-AZ from the original normal Environment Build architecture, using a bounded real-source check without adding a parallel loot DB, optimizer, or new Native gate. Product still targets **26 DPS** and future target-ilvl absolute CHMV rating, requires season-authentic G/J/F/O and same-engine SimC optimization, not current equipped gear redistribution.

The actual test's **fixed build `12.1.5.70575` is a reusable *previously observed same-build reference***, **not independently identified as the newest live game build on 2026-11-03**. Results are source physical compatibility only; they are **not** a fresh/current-season G or complete product acceptance.

## Newly executed real Wago and SimC sample

[GitHub Actions #41479710886](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41479710886) — SUCCESS on isolated branch code `0f51abd81292d300d3a0d5e406109beaba7e0d38`:

- Existing `v167` season candidate DB contains **511** user/equipment role candidates, including **328** `plain_representative_candidate` rows. Its `mplus_season_candidate_inclusion.world_state_effectively_resolved` is **false**; includes old-expansion dungeon rotations and Localbots supplement. This is deliberately not an independent season-membership approval.
- Fresh same-build `wago.tools/db2` downloads (not mocked):
  - `Item.csv`: **9,103,685 B**, SHA-256 `f4e8d548e9f8ac2e98e58684521e470c3b50334d365601c82f0571add20ad206`
  - `ItemSparse.csv`: **51,691,672 B**, SHA-256 `f01d63a9a49686df5064042798ee768fdee67a9c42e5ce69299729d9ebbf6ab3`
  - `ItemXItemEffect.csv`: **1,175,163 B**, SHA-256 `568e36454d6bbb8992d250c852cc43e8a8939806d367121ecb57ed97b6112729`
- Checked each of the 328 v167 plain candidate IDs against raw Wago Item class/subclass/inventory, ItemSparse inventory/ItemSet=0 and absence of a direct **Retail ItemXItemEffect record**: **328/328 physically consistent, zero excluded**. This does **not** certify absence of bonus variants or all SimC effects; never reimplement those.
- `v229.collect` downloaded the same pinned SimC first-party full source, exact commit `710c2408bfd3ae4df71b8cd55cdf01f63fd6c926`, generated build `12.1.5.70575`. `v231.select(paladin,retribution,midnight_season_2)` resolved tier ItemSet ID **2062** and five physical tier IDs **271463, 271464, 271465, 271466, 271468**. Independent historic DB2–SimC tier cross evidence remains #41455991413.
- `v232.find_candidate(...,season_gear_db=filtered_v167,target_ilevel=334)` matched SimC and Wago ordinary IDs and created **13 distinct physical slots**:
  - back 193763, chest 159424, feet 159412, finger1 158366, finger2 159459,
  - hands 271466, head 271465, legs 271464, main_hand 249671,
  - neck 249626, shoulders 271463, waist 159418, wrists 159409.
  - Among selected ordinary items, most have `mplus_journal` source kind; **main_hand and neck have `localbots_delve_pool`**. Their physical metadata now matches, but actual season membership remains unproved.
- **New Native calls 0; G/J/F/O/B/T still null; no environment install or v098/v212/adaptive DPS session**. The actual one-shot downloaded SimC and Wago source files in an ephemeral runner temp folder; they were not written to a product user cache or made available as permanent installed runtime. Historical previous build is not used as a G/J/F/O value.

## Improvement to the existing original Build

On the isolated `runner/v216_environment_build_coordinator.py` internal source-only `_one_spec_ordinary_simc_stage`:

- For a candidate success, expose `selected_slot_count`, `source_kinds_by_selected_slot`, and `mplus_world_state_pending` from the **already sealed v232 candidate receipt**, with `season_membership_verified=false` and `G=null`.
- For a physically absent required ordinary/common slot, preserve an exact safe `missing_slot` (such as `waist`) alongside the existing blocked status, rather than truncate the exception detail and force blind resampling.
- `tests/test_v255_one_spec_simc_representative_in_build.py` adds assertions for source kind and missing waist, retaining existing v251/v232 synthetic stage and zero-Native contract.
- [v212 cross-platform CI #41480060220](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41480060220) is the final new-code verification; use real job logs before recording PASS. No source collection should be rerun merely to validate this small diagnostic change.

## Remaining critical path

1. **Current actual active season** must be discovered and authenticated from the allowed Blizzard/WCL/current-build source path, not assumed from this pinned 12.1.5 sample. Reuse season-bound v161/v163/v165/v167 and verify its selected target ilvl, four tier pieces and ordinary/weapon coverage. The `mplus_journal` and Localbots source labels alone are not active season proof.
2. A real representative physical loadout and optional exact Native `G` measurement (or valid same-season reference) can then be linked to existing v222; J/F/O and permanent E must be independently re-verified for the same season, with fixed L and O counted once.
3. Keep existing native SimC effects, proc/APL, adaptive DPS, SEM/95%, cache and cancel/resume. Do not expand to equipment recommendations, every-ilvl Native matrix, new gate, or permanent external dependency.

**Status:** real Wago × SimC one-spec physical source crosscheck succeeded; **season admission, validated G/J/F/O and zero-history user end-to-end optimization remain pending**.
