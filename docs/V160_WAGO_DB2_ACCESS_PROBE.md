# v160: zero-seed wago.tools DB2 reachability before bulk download

Live probe pins public RETAIL `12.1.5.70575` as of 2026-10-29.
Source `https://wago.tools/db2/{Table}/csv?build=12.1.5.70575&locale=enUS`.
No API token, no old IDs, no local SimC, no unbounded broad downloads.

9 schema probes (first 32 KiB only; timeout 9s each): raid
`JournalTierXInstance`, `JournalInstance`, `JournalEncounter`,
`JournalEncounterItem`; Mythic+
`MythicPlusSeasonTrackedMap`, `MapChallengeMode`, `Map`;
craft `CraftingData`, `ItemSparse`.

Only a genuine HTTP200 text CSV with the required fields is VERIFIED.
Cloudflare 403, timeout, HTML 200, missing columns are recorded as failures
not treated as an empty item pool.

If the headers are accessible, a separate bounded phase can download just
required CSV tables, cache by exact build/locale/content sha256, perform DB2
joins with zero legacy seeds, and emit a compact item ID list by content type.
No full data import into the P1 runtime. Under no circumstances equate
`ItemSparse` class/ExpansionID alone with a complete DELVE reward pool.
Server-side Zah'ran inventory isn't known to be in client DB2.

Commit `[wago-probe]` triggers one limited workflow. Ordinary code commits
skip the live HTTP requests.
