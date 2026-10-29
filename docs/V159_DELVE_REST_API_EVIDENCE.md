# v159 — Delve REST lookup: bounded reality check (zero-seed)

Goal: determine whether Blizzard **Game Data REST** exposes a current Delve
season list or loot IDs. This is NOT a Delve item DB or new gameplay engine.

Three fixed GETs against Blizzard KR, plus at most one Journal detail
if a Delve instance is **explicitly typed or named** in the official index:
- `journal-instance/index` (documented, previously used for raids)
- `delve/index` (UNCONFIRMED candidate, not a documented guarantee)
- `delve/season/index` (UNCONFIRMED candidate)

A 404 means only that **that route** was not found in this namespace. It does
not prove no Delve data exist elsewhere in the game or that a whole-season pool
is impossible to derive from other sources.

Source of names is only the responses themselves, not a curated prior Delve
or item list. Independent API calls are protected by
`SIMC_ALLOW_SEASON_API_PROBE=true` AND the `[api-probe]` marker.
No native SimC calls. No item ID supplementation.

User's product requirement: find a **single seasonal Delve gear pool**,
without organizing actual drop locations (chests, vault, vendors).
If the public REST API lacks that list, leave pool unidentified and explore
season-scoped client-data acquisition, not legacy item DB matching.
