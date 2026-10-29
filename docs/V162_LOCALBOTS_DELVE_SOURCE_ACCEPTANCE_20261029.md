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
