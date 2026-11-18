# P1 v582 — Wago 70783 physical permanent enchant → SimC exact-ID source join (2026-11-18)

**Actual evidence:** [Windows? No: GitHub Ubuntu 26.04 Actions #44211446707](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44211446707), commit `04e9bc826f061651ce54b61f400bc2207540b773`, **SUCCESS**. Five scoped offline tests PASS, **new SimC Native 0**, real Wago source read from build `12.1.5.70783`, expansion `ExpansionID=11`, pinned SimC revision `de11f57df75dda668bae6ac7043a43b98831fa96`. Complete source-only JSON receipt is Actions artifact **14385592815** (`p1-v582-wago-permanent-enchant-item-relation`, 7-day retention). A 38/38 exact source relation is **not** Policy A user admission or a proven complete list of every expansion enchant.

## Why the earlier direct link failed; verified modern Wago join

Historical direct `SpellEffect.Effect=53 → EffectMiscValue_0=permanent enchant ID` returned **0/38**. Relaxing `ItemEffect.TriggerType==0` and including physical Item classes `8`, `0/6`, `0/8` did not solve that identity mismatch. In actual 70783 modern crafted enchants, `SpellEffect.Effect=301` points to a **CraftingData ID**, not to the SimC enchant ID.

The successful exact Wago relationship is:

`Item(ID, ClassID)` + `ItemSparse(ID, ExpansionID, Display_lang)`
→ `ItemXItemEffect(ItemID, ItemEffectID)`
→ `ItemEffect(ID, SpellID, TriggerType)`
→ `SpellEffect(SpellID, Effect=301, EffectMiscValue_0=CraftingDataID)`
→ `CraftingData(ID, Type=3 ENCHANT)`
→ `CraftingDataEnchantQuality(CraftingDataID, ItemID, Rank, SpellItemEnchantmentID)`
→ same-build pinned SimC `permanent_enchant.inc` exact `enchant_id`, token, quality-family and equipment mask.

Use **physical ItemID equality** between `CraftingDataEnchantQuality.ItemID` and the expansion-verified physical item; neither a similar item name nor identical/adjacent rank integers is evidence of exact linkage. `CraftingDataEnchantQuality.Rank=13/14` is **not the same scale** as SimC source `quality_rank=1/2`; highest effect/quality logic must respect the original same-family ordering and noninferiority rule rather than compare these raw ranks numerically.

## Actual counts, exact 70783 evidence

- SimC `enchant_` armor/weapon highest-source-quality candidates: **38**; all 38 exact Wago linked; **0 missing**.
- Including lower SimC rank variants, **76 exact enchant IDs** linked to **76 distinct physical same-expansion ItemIDs**.
- Wago source type-3 crafting enchant quality rows: **399**. `Effect=301` same-expansion apply-spell rows: **44**, yielding **88 quality-item hits**; this intermediate quantity is not 88 unique verified user options.
- Example high source rank 8025 (`enchant_ring__silvermoons_alacrity`) → real physical scroll **244015** (`Enchant Ring - Silvermoon's Alacrity`), while lower rank enchant 8024 → item **244014**. High source rank 7965 (`enchant_ring__amani_mastery`) → item **243955**; 7967 (`enchant_ring__eyes_of_the_eagle`) → item **243957**; weapon 8039 (`enchant_weapon__acuity_of_the_rendorei`) → item **244029**. All are `ExpansionID=11` in these actual same-build rows.
- **Coverage caution:** the artifact also records **33 other Wago permanent enchant IDs** outside the SimC `enchant_` token candidate subset (including spellthread, kit and scope families). The user-supported permanent-enchant scope needs comparison with slot/condition/effect categories; do **not** equate 38 source candidates with all applicable permanent enchant types, or automatically promote 33 unmatched IDs. Some may be outside DPS CHMV-supported options.
- User display can use official ko_KR name *if the exact physical ItemID resolves through existing v335*; otherwise use existing v211 classified `effect_summary`, adding exact stat increase only when proven. Missing Korean display name must not independently block a valid optional item.

## Implemented artifact vs incomplete product integration

Implemented: `integration_probes/p1_v582_wago_permanent_enchant_item_relation_once.py`, `tests/test_p1_v582_wago_permanent_enchant_item_relation.py`, `.github/workflows/p1_v582_wago_permanent_enchant_item_relation_once.yml`. Source-only diagnostic does not publish a product catalog or calculate E. Initial prototype Actions #44210180744 failed one incorrect fixture; subsequent direct 53 attempts passed the code but returned real 0/38; expanding the hypothesis without updating the test CSV schema caused #44210911070 fixture failure. Final exact effect301 path Actions **#44211446707 succeeds**, preserving failed evidence history.

**Next implementation priority:** CONNECT the verified relation in the existing `v216/v217` source-stage pipeline, **reusing** sealed `v161 Item/ItemSparse/CraftingData`, `v254 ItemXItemEffect`, `v280 ItemEffect`, `v281 SpellEffect` and `v275` pinned SimC permanent data, and fetch **only one missing Wago `CraftingDataEnchantQuality` table** when not already sealed. Scope by expansion and same game build; the user explicitly does not require a separate within-expansion season-membership gate. Retain item-identity, exact physical slot/weapon applicability, highest-quality same-effect verification and static E ownership as the necessary facts for existing `v220→v196→v212→v113` product admission; don't build a new effect/Native/optimizer engine. Same-season already pinned Wago static item cache remains reusable across SimC revisions, while a changed season can require remeasurement of selected fixed CHMV E.

**What is NOT done:** full same-expansion supported enchant completeness/quality publication; general weapon applicability; per-option E measurement; automatic Policy A registration; generic user selectable UI/profile/caches for these 38/76; a new general all-enchants E2E PASS. Existing G/J/F/O base, v290 adaptive optimizer and exact v528–v534 three-scope evidence unchanged. **Official 15/78 COMPLETE / `full_product_e2e=PENDING`**, no main/v003/original-v016/Project UI/Work OS promotion or primary product-development-chat ownership change.
