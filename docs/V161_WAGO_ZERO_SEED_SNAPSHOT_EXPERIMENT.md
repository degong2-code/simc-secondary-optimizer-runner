# v161 Zero-Seed Real CSV Snapshot (one-off evidence)

After v160 verified 9/9 table headers HTTP200, download **only 10**
specified CSV tables from pinned Retail build `12.1.5.70575`:
JournalTierXInstance, JournalInstance, JournalEncounter,
JournalEncounterItem, MythicPlusSeasonTrackedMap, MapChallengeMode, Map,
CraftingData, ItemSparse, Item. Each is unmodified from the response and
hashed with SHA256. Max 210MB per file and 320MB total, no other URLs.

This is a **one-time source experiment**, not an always-on item catalog or
new runtime dependency. Artifact retention 2 days, old item DBs unused.
The next offline operation can join same-build client rows with today's
live WCL season2 metadata, test raid/lair/M+ coverage, and derive
selectable-stats craft candidates from 24/25 + CraftingData + ItemSparse.
It must not infer Zah'ran's server-side merchant inventory from unrelated
client items. Delve remains UNKNOWN without a source-specific full pool.
