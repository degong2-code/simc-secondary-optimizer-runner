# v162 — Localbots as trusted public season Delve pool provider

2026-10-29 one-time audit: Wowhead NPC `256670` (Zah'ran) comment
by Lazey lists 79 distinct item names (6 jewelry, 18 trinkets,
36 armor/cloaks, 19 weapons/offhand/shield). All **79/79** match the
79 names in `balovich-matje/localbots/data/delve-loot.json`;
missing 0, extra 0. This is a **publisher list vs Wowhead user-comment**
audit, not independent reading of a server loot table. Localbots itself
cites Wowhead and datamining. User explicitly accepts Localbots as
the continuing future-season pool source **without repeated Wowhead
cross-checks**. Do not make 79 a fixed future-season count requirement.

`runner/v162_localbots_delve_provider.py` downloads
`https://raw.githubusercontent.com/balovich-matje/localbots/main/data/delve-loot.json`
and one pinned wago DB2 `ItemSparse.csv` (or consumes saved local files).
- Explicit source IDs are verified for name/slot/expansion against DB2.
- Name-only items are resolved by best-quality and then newest ID, as
  Localbots does. Names not matched exactly stay UNKNOWN, not zero.
- Provider source SHA256 + DB2 build/SHA256 written to JSON output.
- Current 57 ID + 22 name-only **are data findings, NOT code constants**.
- This import is a curated **external source**, not a legacy WEQUIP item
  database and not official Blizzard server drop-table access.
- Source change/new season does not force Wowhead validation; the
  source provider's normal publication/DB2 matching suffices.
- The imported 79 names are not a SimC effect/L certification.
- No new SimC Native, no product runtime HTTP dependency.

One-time audit source:
https://www.wowhead.com/npc=256670/zahran
GitHub:
https://github.com/balovich-matje/localbots/blob/main/data/delve-loot.json

## Actual authenticated/public-source run #40839426417

- Offline regression PASS; opt-in live fetch and DB2 identity PASS.
- Localbots latest JSON: **79 item names, 57 explicit IDs and 22 names only**.
- Retail `12.1.5.70575` ItemSparse resolved **all 79/79 unique items**;
  unmatched/mismatched = **0**.
- Source payload SHA256: `3694f1b536c99d161f3bc8d2d4b124c97ffadf5765ea015536fa0a8c0f6f6d8a`.
- New SimC Native 0; upstream DB direct download after the first Wowhead
  name audit; no future Wowhead check required by user decision.
- `v158` accepts the v162 report as an additive Delve provider with
  separate provenance and unresolved entries; its synthetic CI PASS was
  run #40839426413. Product P1 runtime wiring is not claimed.

Receipt: `integration_probes/catalog/v162_localbots_real_provider_acceptance_20261029.json`.
