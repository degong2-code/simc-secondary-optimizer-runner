# SIMC SECONDARY OPTIMIZER — New Chat Continuity 2026-10-29 / v162

**Purpose:** transfer this existing development conversation after chat-length limit. It does not merge `main`, change v003 immutable, apply Project Sources, or grant MAIN/WORK authority. **Prior HEAD before this handoff:** `2aad2878bfaa48c8be2f92eb38a84fd739aaf3dc`. Fetch actual branch HEAD when resuming.

## Authority and product goal

- Latest direct user decision > approved policies > actual branch CURRENT/code/Actions/Native evidence > history. User explicitly requested *this* conversation handoff; old "stay in same chat" instructions are historical.
- The newer actual user/CURRENT scope is **26 DPS specializations excluding Augmentation Evoker**, ilvl **266–344** default **334**, tank/healer excluded. IMPORTANT: uploaded Developer Notes v1.4.1 document retains the **27 DPS / Augmentation included** historical wording. Do not restore 27 from that file. Project Source UI application of v1.4.1 is not verified.
- Goal: optimize **absolute crit/haste/mastery/vers rating** at target ilvl or manual T by SimC DPS, reporting ratio, DPS, SEM, **95% only**, observed winner vs confirmed 95% advantage, and materially distinct near-optimal alternatives. No gear-combination/loot-route recommendation or user full-geared profile requirement.
- User picks class/spec/race/talents, ilvl or T, two trinkets, optional special-effect pieces, up to two embellishments, consumables and fight settings. Standard gear, weapons, 4-piece set and stats are internally assembled.
- `T=G+J+F+O`; `B=G+J+F`. Fixed oil O appears exactly once in gear_*, never a free budget. Fixed special gear L already inside G/B, protected as per-stat lower bounds; do not add again. Trinket fixed stats outside free G, missing JSON gear record means *unknown*, not zero or unsupported. Crafted 50:50 initial secondary allocation is not locked L. 79×2 B reference is rounded approximation, not full exact Native census. SimC handles APL, equipment effects, trinket/embellishments, DPS. No independent effect-support Gate.

## Actual development state and test receipts

Repository `degong2-code/simc-secondary-optimizer-runner`, branch `probe/chat-cache-v035-20261024`; owner product original `v016_SCENARIO_CONTRACT` reported but byte-level verified full integration is NOT established. Focused historical CI != product completion. GitHub connector and Actions work; native Windows/SimC/GUI experiments remain opt-in, cost-minimized.

- v155 [Actions 40826278881](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40826278881): Blizzard+WCL authenticated, current Midnight S2, WCL **8 M+ dungeons + 10 raid/lair bosses**. Blizzard current season id 18, DB2 display season id 37 are distinct ID systems.
- v156 [40827019159](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40827019159): **Nek'zali 16 item IDs** through actual Blizzard journal. It is one boss, not 10/10 journal API certification.
- v157 [40831726530](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40831726530): zero-seed Midnight Tailoring **92 recipe IDs/names**, 3 detail samples lack explicit output IDs. Recipe naming can be resolved more directly via DB2 `CraftingData` + `ItemSparse`.
- v159 [40832497636](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40832497636): Delve REST candidates 404, Journal index cannot identify whole Delve loot. This does not deny client/other sources.
- v160 [40836140708](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40836140708): pinned `12.1.5.70575` wago DB2 **9/9 CSV fields** confirmed.
- v161 [40836955761](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40836955761): pinned build **10 full CSV tables** downloaded with SHA; **one-time external analysis (not yet a reusable repo runner)** matched **10/10 raid/lair bosses** (Nymrissa 2849, Kith'ix 2896 in separate instances), **8/8 M+ dungeons**, raid raw 144/equippable candidate 105, M+ raw 247/equippable candidate 223 **before WorldState seasonal filtering**, selectable craft candidates 106 (104 without known built-in embellishment limit codes). These are preliminary item references, not certified current loot pools.
- v162 [40839426417](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40839426417): Wowhead Zah'ran public user list vs Localbots source **79/79 matching names**, 0 missing/extra. Historical audit is not an official server-table certification and sources are not independent. **User approved Localbots as the trusted future-season Delve pool provider without repeated Wowhead comparisons.** Actual latest Localbots data 57 explicit IDs + 22 name-only → exact build ItemSparse **79/79 resolved**, unresolved0, new Native0. Source SHA `3694f1b536c99d161f3bc8d2d4b124c97ffadf5765ea015536fa0a8c0f6f6d8a`.
- v158 [40839766340](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40839766340): latest offline CI PASS for source-first season index accepting `v162`; **real multi-source full P1 runtime integration not done**.

Read `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` *from top* and `docs/V161_WAGO_DB2_ZERO_SEED_ACTUAL_FINDINGS_20261029.md`, `docs/V162_LOCALBOTS_DELVE_SOURCE_ACCEPTANCE_20261029.md`, `integration_probes/catalog/v162_localbots_real_provider_acceptance_20261029.json`.

## Data collector operating policy

**Start new season with 0 preloaded gear data**. Do NOT use WEQUIP/v047/v057/old 404 or 51 as item seeds, overlap tests or completion metrics. Blizzard/WCL selects current content, **wago.tools DB2 CSV pinned to the same actual game build** provides raid/M+, item identity and craft `CraftingData.CraftedItemID` + `ItemSparse` optional secondary 24/25 classification. Localbots public `balovich-matje/localbots/data/delve-loot.json` provides Delve gear-pool membership, DB2 verifies IDs/names; **no recurring Wowhead validation or fixed count=79**. SimC receives verified item IDs/slots *once for batch classification*, not API-SimC item-by-item loops. Sources are fetched during seasonal index compilation, never every product optimization.

## Next implementable work (do not research from scratch)

1. **v163** lightweight reusable DB2 Join from already downloaded 10 CSV snapshot and v155 active WCL data. Emit minimal `item_id/slot/source/season evidence/UNKNOWN` for 10 bosses, 8 M+ dungeons, selectable-stat crafted items. Parse `WorldStateExpressionID` carefully for returning dungeons; do not silently adopt previous-season loot from Journal. This Join was only executed as a standalone analysis; **repo runner is still missing**.
2. Ingest current real v162 output into v158 for one actual minimal multi-source season index smoke; current v162 direct success + v158 synthetic PASS must not be conflated with full real E2E.
3. Batch SimC classification of selected IDs (effect/default crafted design/CHMV static) using existing cache and minimum selected-variant Native calls; then priority P1 user flow `user input → representative profile / B/L/O → existing adaptive SimC → 95% results/cache/cancel/resume/UI`. Original v016 integration remains evidence-gated only where needed.

## Efficiency and safety rules

- Examine actual branch HEAD/CURRENT and affected modules. Reuse successful Actions, receipts, v161 raw snapshot and analysis instead of rerunning old API/CSV downloads, 79/79 Wowhead audit, previous Native or 26×79 levels. Separate committed code / fresh PASS / reused historical evidence / unimplemented.
- Keep changes narrowly scoped, offline focused CI for structural changes; Native only if truly necessary. Inspect call budget, cache, duplicate requests, CSV memory/I/O, runtime, complexity per code change.
- Never add independent proc/APL simulation, unnecessary Gates, huge season DB, full-gear UI or exact-per-ilvl Native requirements.
- Cache: same-season static item identity survives SimC revision; correct only by explicit user instruction; DPS cache keys include binary/profile/items/options/O/fight/iterations.
- **No unapproved main merge, v003 immutable edits, Project Sources/Instructions/UI operations, Work OS M0/Shared State elevation. WEQUIP never an ongoing runtime dependency.**
- Don't write commit messages with `[api-probe]`, `[wago-full]`, `[wago-probe]`, `[localbots-probe]` unless deliberate live queries are required.

**First new chat turn:** verify HEAD once, summarize actual status and exact next code file/tests, then implement the next narrow step; do not ask user to repeat settled constraints.
