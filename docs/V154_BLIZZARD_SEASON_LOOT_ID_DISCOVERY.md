# v154 — Blizzard boss-loot ID → existing MID2 item evidence (bounded pilot)

This is a **season-data discovery adapter**, not a new optimizer, a full farmable
item database, a SimC effect evaluator, or a requirement to Native-test every
itemlevel or specialization. Existing v046 static cache, v151 impact advisor,
v094 optimizer and user-session identities are unchanged.

## What this actually proves
- Read the repository's real v047 WEQUIP-derived 395 source records / 394
  distinct item IDs and the separately collected v046 partial-10 patch list.
- Reconcile *explicit* Blizzard Journal encounter item references to those IDs
  without trusting unknown responses as an empty loot pool.
- Preserve known effect-bearing or special-armor tags solely as **candidates**;
  SimC decides actual effects, ilvl scaling, and DPS.
- Count recovered candidate IDs, gaps, and unknown loot endpoints. Never
  turn a missing ID from a selected boss query into evidence that it is not
  season-loot.
- No automatic discovery of the entire active season, Delves, trash drops,
  crafting or BoEs. Do not imply an off-line mock is genuine Blizzard data.

## Commands (standard library only)

To inspect **actual existing data**, no API or secrets:
```powershell
py -3 runner/v154_blizzard_season_loot_index.py --out existing_reference.json
```
The report status is `EXISTING_REFERENCE_ONLY_BLIZZARD_UNQUERIED`.

To compare **saved actual Journal JSON** obtained legitimately from the
Blizzard API, supply a local manifest with exact encounter IDs and types
(`raid`, `mplus`, `delve`). Example:
```json
{"encounters":[{"encounter_id":1234,"instance_id":5678,"kind":"raid"}]}
```
Put a matching `encounter_1234.json` in a chosen directory:
```powershell
py -3 runner/v154_blizzard_season_loot_index.py --encounters selected.json --journal-dir journal --out comparison.json
```
Do **not** present fabricated test examples as real Blizzard IDs.

To attempt live Blizzard Game Data lookups, only with a user-provided
environment `BLIZZARD_ACCESS_TOKEN` from the official authorized OAuth
workflow (never check credentials into GitHub):
```powershell
py -3 runner/v154_blizzard_season_loot_index.py --encounters selected.json --live --region us --out comparison.json
```
At most 48 explicitly selected encounters, once each, 15s timeout each.
No automatic OAuth requests; missing/expired token fails. Ensure encounter
IDs in the manifest are genuinely in the target season before calling.
If `items`/`loot` are absent or API payload changes, report UNKNOWN or
fail closed. Blizzard Journal supports boss-level loot to some extent but
does not guarantee all gear sources, option variants or Dungeon/Delve loot.
Live verification of the response shape is a **remaining evidence gap**.

## Output and cache boundary

`observed_items` references IDs and existing candidate hints; it is not
imported as a new authoritative `v046` static variant. No item or static
L is invented. A candidate with no SimC-native static variant remains a
missing exact L, not zero. When live provider support is confirmed,
the existing `v046.merge_catalog` may be used for metadata-only entries
in a separate opt-in successor, without touching DPS cache or engine.

## Native and acceptance interpretation
No SimC calls, no per-level Native gate. An optional selected provider
response can verify acquisition ID coverage but **does not certify item
effects, availability of modifier variants, or current-season completeness**.

## Optional existing special-effect registry (read-only)

When the original partial WEQUIP export is available locally, do NOT copy
the entire export or archive into the GitHub repository. Add the path to the
existing-file or provider comparison command:

```powershell
py -3 runner/v154_blizzard_season_loot_index.py --special-registry "SPECIAL_EQUIPMENT_EXPORT.json" --out comparison.json
```

The output field `existing_special_registry_crosscheck` counts overlapping
ID metadata. It **does not** turn historical effect metadata into SimC Native
effect support or accurate L, nor does it mean Blizzard recovered the IDs.
