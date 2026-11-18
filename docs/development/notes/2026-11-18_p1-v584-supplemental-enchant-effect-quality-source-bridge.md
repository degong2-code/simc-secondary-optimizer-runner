# P1 v584 — Reuse original v191/v211/v213 for additional permanent-enchant effects (2026-11-18)

## Scope, principle, and implementation status

This is a **source-only optional supplement to the original v216 Environment Build** for the eight newly discovered, Wago-verified same-expansion DPS gear enchant families. It **does not** add hardcoded ID selection to product inputs, build a new effect engine, change DPS optimization, certify all effect mechanics, install numeric E, or publish the user catalog. The existing authoritative v191→v211→v213 fresh catalog remains unchanged; this supplement **reuses their parsers and classification/slot conventions**. Canonical v191/v213 catalog consumer promotion is NOT complete.

In the already sealed v583 Wago physical join, original 70783 source showed 33 extra permanent enchant IDs outside the narrow SimC "enchant_" token subset. Existing generic class/mask classification resolved **16 physical gear enchant IDs** representing **8 highest SimC source-rank candidates** (6 leg armor, 2 ranged-weapon). Professional tools 12 and unresolved/non-general gear 5 are excluded from the additional DPS source-classifier worklist.

- New *thin adapter*: \`runner/v584_supplemental_permanent_enchant_classification.py\`, invoked from original \`runner/v583_permanent_enchant_physical_source.py\` inside the existing \`v216.collect_wago_new_season_source\` source stage. All source data and permanent physical ItemID relations come from the sealed v583/v275 sources; no new Wago CSV or SimC Native is initiated. v583 code fingerprint includes original v211/v213 parsers for compact projection invalidation, while build-pinned raw Wago CSV cache is unchanged across SimC/compiler revisions.
- Actual effect and stat classes use **existing v211** \`parse_dbc_rows\`, \`parse_enums\`, \`parse_spelltexts\`, \`parse_custom_handlers\`, \`classify_row\` and \`_fresh_static_quality_source_only\`. Exact SimC raw quality families come from **existing v191** \`parse_generated\`/quality selection. Physical gear slot mapping reuses **v213.ARMOR_ENCHANT_SLOTS**, adding SimC's leg \`InventoryType=7\`. Weapon subclass bits are retained as observed numeric IDs; the correct hand/slot is **not** inferred.
- **Generic unknown forward compatibility:** optional new effect candidates may contain a future ItemMod. \`v211.classify_row(..., unknown_item_mods_pending=True)\` preserves unknown IDs and keeps any noninferiority source claim **PENDING**; its default historical strict parser remains unchanged. Actual pinned SimC enum \`ITEM_MOD_STRENGTH_AGILITY = 72\` is now correctly classified as a **primary-attribute hybrid, not CHMV**; 73/74 sibling hybrids likewise recognized. Pinned \`ITEM_ENCHANTMENT_RESISTANCE = 4\` is classified as source-only non-CHMV resistance-category data, not an independent effect calculation. Existing four CHMV codes remain unchanged.
- The supplemental output is \`supplemental_gear_effects_source_only\` stored in the *existing v583 compact v217 artifact*, with source-provenance, physical ItemIDs, slot masks, SimC DBC effect classes/descriptions, source family rank observations, unknown components, and \`ui_selectable=false\`. Missing/invalid optional source results only in \`SUPPLEMENTAL_DPS_ENCHANT_EFFECTS_PENDING\`; it does not block installed verified G/J/F/O or mutate product cache. Selection is **not** automatically approved.
- \`static_E_source_status\` differentiates recognized source-only absence of a fixed CHMV component, an unresolved static component, and CHMV numeric measurement pending. No fixed rating is double-added or guessed, and no Native is launched to certify proc mechanics.
- This adapter intentionally does not edit original v191/v211/v213 stage artifacts or v003, and does not promote source-only evidence to the four proof buckets required by v220.

## Actual same-build 70783 source findings

[Live pinned Wago + SimC Actions #44219689415](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44219689415) **SUCCESS**. Build \`12.1.5.70783\`, \`ExpansionID=11\`, pinned SimC rev \`de11f57df75dda668bae6ac7043a43b98831fa96\`, **Native 0**; scoped Wago/SimC 38/38 and 76/76 existing source relation retained. v584 classified **8/8** supplemental high-source-rank gear options (6 exact leg-source slot resolved, 2 ranged weapon subclass-mask known but exact hand pending); **no recognized fixed CHMV rating component** in the eight DBC rows. The initial research classifier correctly withheld inference for 3 source components with unrecognized \`ItemMod=72\` (IDs 8159/8161/8163) and \`enchant_type=4\` (ID8163). Subsequent reading of the **exact same pinned SimC \`data_enums.hh\`** identified 72 as \`ITEM_MOD_STRENGTH_AGILITY\` and 4 as \`ITEM_ENCHANTMENT_RESISTANCE\`; these have been added to the general source classifier and verified in offline regression, **without a redundant full Wago/SimC download**.

| Current-build high source-rank enchant ID | Physical ItemID | Observed source class / effect | Fixed CHMV? |
|---|---:|---|---|
| 7935 | 240133 | Legs; intellect + stamina (spellthread) | No |
| 7937 | 240155 | Legs; intellect + SimC spell component, text not resolved | No |
| 7939 | 240157 | Legs; intellect | No |
| 8159 | 244641 | Legs; stamina + strength/agility hybrid | No |
| 8161 | 244645 | Legs; strength/agility hybrid | No |
| 8163 | 244643 | Legs; strength/agility hybrid + resistance-type component | No |
| 8613 | 257748 | Ranged weapon; SimC spell effect, exact hand pending | No |
| 8615 | 257746 | Ranged weapon; SimC spell effect, exact hand pending | No |

**Strict quality result:** Original v211 static noninferiority evaluation returned \`SOURCE_EFFECT_OR_USE_CONDITIONS_PENDING\` or \`UNKNOWN_STAT_COMPONENT_QUALITY_EFFECT_PENDING\` for **all eight**; **zero were certified as same-effect/noninferior**. This is expected because many variants use scaling coefficients or spell components not covered by the existing static-only comparator. Higher source rank or identical token by itself is **not** proof that lower-quality versions are redundant under the user quality policy. Do not register merely because 8 source-rank candidates exist.

## New tests / existing proof boundaries

- [Final focused v584 + v583 + original v240/v216 Actions #44220980912](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44220980912) **SUCCESS**, v583 **8**, v584 **8**, original v240 **20**, original v216 **31** = **67 PASS / 0 FAIL**, Native 0. Includes no hardcoded token names, real existing v211 DBC effect/quality comparisons on synthetic source, leg inventory mask, numeric ranged weapon subclass mask bits, unrelated old/source holdover compatibility, unknown future ItemMod preservation, optional source pending isolation, source SHA drift, known hybrid primary stat and resistance type 4 non-CHMV, no accidental static E.
- [Earlier live v584 #44219689415](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44219689415) used the then-strict v211 parser and produced unrecognized components, which prompted a focused legitimate SimC enum correction. It is **historical real-source evidence**, not a newly rerun per-item Native certification for changed code.
- A separate historical \`v191→v211→v213→v196\` workflow re-run may fail downloading **expired old Actions artifact \`v192-updated-simc-catalog-41017578894\`**, unrelated to v584 code; current original v240 offline 20 PASS covers the same fresh catalog code contracts without that expired artifact. Do not claim all GitHub workflows green based on scoped checks.

## Remaining work and next efficient step

1. Compare **same effect/use scope** for the 8 supplemental families using original pinned SimC DBC scaling/driver spell data. Keep unresolved proc/scaling effects separate; do not duplicate SimC's actual effect mechanics. A source-supported non-inferiority conclusion must include the effective stats/conditions; source rank alone is inadequate.
2. Determine exact weapon hand/weapon subclass applicability for the 2 ranged candidates from existing equipped item profiles/SimC source; do not request entire user gear list.
3. Bind only fully source-verified options through the original v191/v211/v213 / v196 / v220→v212→v113 verified user selection, preserving default G/J/F/O and the budget E precedence. If exact Korean names unavailable, supply verified effect summary, without fabricated localization. Not all 8 are numerically fixed secondary stat enchants; do not run Native E pointlessly.
4. Same expansion/season source records can be reused when unchanged; selected fixed CHMV E requires remeasurement if the season/build modifies its rating. No unconditional 26-spec/all-option Native loop.

**Official full-product status remains \`full_product_e2e=PENDING\`; prior \`15/78 COMPLETE\` ledger unaffected.** No main merge, immutable v003 edit, Project UI/Instructions application, Work OS promotion, or main-product-development-chat ownership change.
