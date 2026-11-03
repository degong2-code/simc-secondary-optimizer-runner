# P3-BK — Real Wago JournalEncounterItem world-state conditional loot audit (research, Native0)
2026-11-03 · isolated branch `probe/chat-cache-v035-20261024`

## Why this is in the main engine sequence
After P3-BI preserves acquisition-row conditions in v166/v167 and P3-BJ retains same-display-season WSE>0 plain gear internally, we need to know whether conditional world-state rules actually affect the 13/14 **selected representative gear IDs** or whether such conditions are mostly unrelated historical/miscellaneous loot. No independent WorldStateExpression interpreter, universal items DB, new Gate, optimization engine or 26-spec Native sweep is authorized. Existing product G/J/F/O → B/T → existing SimC remains the priority.

## Authenticated exact public physical source acquired
- One-shot GitHub Actions `41554064378`, job `125648493349`, functional research-only commit `4d5e222c866adb4b9f856a2ef6aa29cedbaf50e6`, completed SUCCESS.
- Exact pinned (prior proven physical reference, **not asserted latest live game build**): `12.1.5.70575`, Wago `https://wago.tools/db2/{table}/csv?build=12.1.5.70575&locale=enUS`.
- `JournalEncounterItem.csv`: 689,808 bytes, SHA256 `5203576d974e31df9ce4c02d05e8a45902b81a4ae91853834ffb48a25debe787`
- `JournalEncounter.csv`: 387,654 bytes, SHA256 `a1ea294c56801ee05fc5183f355c91b0fdd92ec93f9b9e41fb304a26d577b954`
- `JournalInstance.csv`: 86,213 bytes, SHA256 `86fa8069ef8454b90826f27581a2b0ce705295083a1f5374bb733abc051c7840`
- Bounded standard-library-only GET; no secrets, no actual Native, no historical cache invalidation. Counts include all `ItemID>0` journal rows in this build, including non-equipment and old expansions, and are NOT current-season obtainable-gear counts.

## Direct physical measurements
- Journal item loot rows: **23,991**; `WorldStateExpressionID=0`: **23,385**; `>0`: **606 (2.53%)**; unique positive WSE IDs: **10**. There are 19,086 unique ItemIDs in the table.
- By `DisplaySeasonID` (zero / positive): **0: 23,322 / 594**, **23: 63 / 0**, **34: 0 / 9**, **37: 0 / 3**.
- **514** distinct ItemIDs have different observed WSE IDs in one or more loot rows, **511** of these have both `WSE=0` and `WSE>0` rows; e.g., 49801, 49802 etc in historical encounter IDs. A positive WSE is attached to a **loot relation** and must not be blindly projected to all item variants/encounters. This does not mean either row is actually currently active.
- Highest `WSE>0` instance row counts: Skyreach 230, Tazavesh the Veiled Market 61, Grim Batol 56, Pit of Saron 49, Halls of Atonement 45, The Necrotic Wake 36, Mists of Tirna Scithe 33, Seat of the Triumvirate 23, Temple of Sethraliss 15, Kings' Rest 15, Siege of Boralus 14, Ruby Life Pools 3. These aggregate **all-era** loot rows, not modern M+ drop rates.
- Observed exact `DisplaySeasonID=37` `WSE=51455`: Ula'tek, `The Venomous Abyss`, ItemIDs **279125, 279127, 279129**. Separate item sources that state they mirror Blizzard Game Data API identify these as **Aureate / Argent / Gleaming trophy housing decorations, not equippable gear**:
  - https://guildloot.de/en/item/retail/279125-the-venomous-abyss-aureate-trophy/
  - https://guildloot.de/en/item/retail/279127-the-venomous-abyss-argent-trophy/
  - https://guildloot.de/en/item/retail/279129-the-venomous-abyss-gleaming-trophy/
  This class-specific observation does NOT establish that the selected 13/14 representative gear or every current M+ loot item has no conditions. Actual item class is backed by the published API-mirror item pages, not a new Wago Item/ItemSparse fetch in this small experiment.
- `DisplaySeasonID=34` WSE positive 9 rows at Crown of the Cosmos / Chimaerus / Midnight Falls; no independent equipment type conclusion was proven for those nine.

## Engine impact / efficiency decision
1. Preserve prior P3-BI/BJ logic: source row conditions and unknown WSE candidates are retained, `G`, `J`, `F`, `O`, `B`, `T` remain null on unproven new seasons. Do not turn `WSE>0` into unconditional exclusion or `WSE=0` into proof of active seasonal availability.
2. WSE checks belong on **selected item + selected encounter/reward relation**, not a global item-level binary. 511 mixed items make item-only WSE blocking incorrect.
3. First apply existing `v163→v165→v166→v167→v232` source identities and `v245/v250/v251` exact tier identities to the requested DPS representative slots. Filter non-equippable rows using existing physical Item/ItemSparse checks. Only if an actually selected G source remains conditional, inspect its WSE separately; do not implement full WoW worldstate parser, source sweep or added certification Gate.
4. Continue **existing `v233/v234` or `v226/v228` minimal one-spec G** once actual season membership/tier are authenticated, then J/F/O/E and v222/v212/adaptive SimC. Selected items' exact current condition and numeric G are NOT resolved in this study.

## Completion / limitations
**Research completed with real pinned DB2 and browser-verified API-mirror examples.** No product-code modification, new Native, numerical G/J/F/O, current active seasonal membership proof, or optimizer E2E. This is an evidence-scoped investigation, not an Environment Build READY certificate. No main merge, v003/v016 edits, Project UI/Sources updates, Work OS/shared-state promotions, or WEQUIP dependencies.
