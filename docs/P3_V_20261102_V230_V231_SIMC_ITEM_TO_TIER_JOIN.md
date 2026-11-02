# P3-V — v230/v231: SimC-generated item metadata → physical tier candidate (2026-11-02)

**Scope:** isolated `probe/chat-cache-v035-20261024`; no main merge, Project UI update, official Work OS promotion, v003 modification or v016 original integration claim. This is an incremental reusable *season environment engine* capability, **not** a new optimization algorithm or complete season database.

## 1. Why this step

Previous v229 acquired immutable SimC-generated source including all historical item sets and optionally `item_data.inc`, but could not connect a class's exact tier item IDs to actual physical armor slots/stat type. Existing v169 consumes v167/v168 compact sources. A new-season cold start must obtain a real, same-build representative set before Native G can be measured; copying installed 79×2 references, old tier IDs, J138/F165, oil 16+16 or previous caches is prohibited.

The pinned SimC generator (same `simulationcraft/simc` upstream) emits each `item_data.inc` record in the fields defined by `engine/dbc/item_data.hpp`: ID, base ilvl, quality, inventory type, item class/subclass, class mask, pointer into shared stat types and item set ID. The **source-generation layout**, rather than a guessed wowhead JSON shape, is used as the parsing contract.

## 2. v230: exact generated item metadata parser

New `runner/v230_simc_item_metadata.py` takes v229's saved seed source + byte and receipt checks, and parses **only requested item IDs** from the 28-column generated C++ rows:

- exact generated game build and bounded bytes, stat array count/index, chunk declarations and physical row count; reject row format drift, malformed C++ or missing IDs;
- ID, name, item base ilevel, quality, inventory type/class/subclass, allowable class mask, stat type codes, item set ID;
- reuses the original `v229.simc_seed_receipt.json` + `item_data.inc` SHA-256 and Git blob SHA. No old data files, existing item DB, API secret or prior Native receipt is needed;
- no numerical rating calculation from stat type allocation, no simulated game effects, no Native call and no assumption that a base ilvl proves current-season availability.

The full upstream `item_data.inc` source may be large, so fetching it is explicitly opt-in and only the selected ID rows are retained in the compact output; this is not a whole-season persistent gear DB.

## 3. v231: exact class tier set link

New `runner/v231_simc_tier_item_join.py` consumes only v229's immutable source seed and v230's selected item metadata. It takes a class, specialization and exact `set_option` whose **current-season origin has yet to be independently authenticated**. It:

- checks supported 26 DPS-only spec from v143/v169 contracts;
- rederives set-bonus candidate groups from the actual pinned `item_set_bonus.inc` bytes, not a mutable grouped receipt;
- requires one unambiguous class + option + set ID group with both 2pc and 4pc and **exactly five unique item IDs**;
- cross-checks each requested item against source `item_data.inc`: five distinct head/shoulders/chest/hands/legs physical slots, correct class armor subclass, exact class mask and consistent set ID;
- produces a deterministic five-slot candidate + four-tier slots and hashes, with `G/J/F/O/B/T=null`, `environment_ready=false`, no Native, and `season_set_option_source_authentication=NOT_PROVED_BY_SIMC_TABLE_ALONE`.

Because SimC includes historical sets, merely choosing the largest set ID, highest item ID or lexicographically newest option is prohibited. The `set_option` is a **development environment source selection input**, not an ordinary user's gear selection. External authoritative season identification or independently verified SimC season metadata is still needed before certifying the active set.

## 4. Real environment acquisition and no-old-data testing

`.github/workflows/v229_simc_only_source_seed.yml` is still **manual-only** and does not run a Native binary. Its sparse checkout has only the required v191/v229/v230/v231/v143/v167/v169 engine code and synthetic tests, then copies that allowlist into a temporary workspace without historical `data/`, `integration_probes/` or `.git`. This offers a preliminary source-independence test, **not a cryptographic guarantee of full zero-base sandbox isolation**.

Its optional `--include-item-data` path fetches the true pinned raw data; when caller additionally supplies `tier_set_option`, `tier_class`, `tier_spec` it executes v231 to create a source-backed tier candidate **without declaring current-season or G ready**. Without those exact inputs it only creates the immutable v229 source seed.

No actual new-season manual workflow dispatch, large item_data download, or Native measurement was performed in this increment.

## 5. Exact tests and evidence

- [v212 #41390405724](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41390405724): Ubuntu/Windows **220 PASS each**, v230 synthetic C++ stat tables, generated build, exact item identity, pointer offset, class mask, source hash and missing ID handling. Native 0.
- [v212 #41390689160](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41390689160): Ubuntu/Windows **227 PASS each**, added v231 selected set 2pc+4pc and five physical slots, wrong armor/mask/slot/set option, old source byte drift and non-DPS denial. Native 0.
- The real SimC pin layout was examined from the upstream `dbc_extract3/dbc/generator.py` and `engine/dbc/item_data.hpp`, but the actual optional large `item_data.inc` file has **not been parsed in CI**. Synthetic PASS only proves the identified structural contract, not real future-season physical readiness.

## 6. Remaining critical engine gap and next work

1. **Automatic current-season identification and *ordinary* representative gear/weapon candidate discovery** from same-build SimC item data, excluding effects/special equipment where source proof permits. Only then can v169 select a full physical baseline. Direct item-effect absence is not a full SimC proc certification; SimC remains the mechanics owner.
2. **Real item-data parsing**, actual SimC source discovery and targeted Native JSON2 with binary/profile/game-build provenance; v226/v227/v228 can then certify an exact G where adequately attested. Do not run 26×all-level Native sweeps by default.
3. New-season J/F/O exact quality, effect and applicability source joins, E/L/O accounting, final B/T and manual T -> existing v222/v216/v098/v106/adaptive SimC. The 95% outcome semantics, cache/resume and DPS ownership remain unchanged.
4. **Strict final zero-base experiment AFTER engine completion**, following P3-U: filesystem and credentials isolate forbidden old sources/caches/receipts and first seal independent generated outcome. Under SimC-only mode, report missing provenance instead of silently gaining Blizzard/Wago access.

The new work only stages one concrete class-set relation. It does not claim production 26-class tier discovery, all 26 Native physical acceptance, verified G or finished Environment Build.
