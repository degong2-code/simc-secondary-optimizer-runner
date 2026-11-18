# P1 v585 — Generic permanent-enchant source quality / ranged-weapon applicability (2026-11-18)

## Outcome and authority

Within the existing P1 `v216 → v583 → v584` optional Environment Build source stage, extend **existing `v211` quality comparison** instead of adding a new qualifier/Native gate. Keep strict quality policy: only hide lower quality if **same effect, same conditions and noninferior actual effect** are evidenced. DBC coefficients alone do **not** prove real SimC values. The new data is always `source_only`, `ui_selectable=false`, `policy_A_product_input_verified=false`; no new runtime choice, optimized budget, cache invalidation or unrequested Native.

## Source-grounded generic implementation

1. `runner/v211_enchant_source_effect_classification.py::source_rank_component_comparison` now compares **all original same-token/class/inventory mask/weapon-subclass quality ranks** by exact generated enchant ID and pinned DBC. Records:
   - exact `ench_type` / `ench_prop` shape for every rank (no translation/name guessing);
   - the same `id_gem`, `id_scaling`, min/max level, min/max ilvl, crafting skill requirement;
   - component-wise raw `ench_amount` and `ench_coeff` directional comparison (all known static `ITEM_ENCHANTMENT_STAT` or `ITEM_ENCHANTMENT_RESISTANCE`; unknown stats and spell drivers fail closed);
   - `id_spell` differences, observed driver IDs and per-rank component records, provenance hash;
   - separate explicit `quality_noninferiority_runtime_verified=false` and `same_effect_and_use_conditions_verified=false`. No zero/one/double E claim or direct UI approval from ranking.
2. **Critical discovered SimC execution precedence:** pinned official [`engine/dbc/sc_item_data.cpp`](https://github.com/simulationcraft/simc/blob/de11f57df75dda668bae6ac7043a43b98831fa96/engine/dbc/sc_item_data.cpp) `item_database::item_enchantment_effect_stats(player,...)` first tries the linked `id_spell`'s `E_ENCHANT_ITEM` spell-effect average; **only when zero** falls back to DBC `ench_amount` or `spell_scaling × ench_coeff`. Therefore higher DBC coefficient, even with identical source stat kinds and restrictions, is only **raw source direction**, not a proven live DPS/primary/tertiary stat increase. The v211 result explicitly documents `simc_spell_value_may_override_raw_coefficient`; no effect mechanism reimplementation is introduced.
3. `runner/v584_supplemental_permanent_enchant_classification.py` attaches the same v211 evidence to the Wago↔SimC verified extra combat-gear family candidates. No new DB2 download; original v583 compact v217 projection contains the result, changes to reused v211/v213 source-parser code reproject only the small identity-specific output. An unknown source stat remains PENDING, never mapped to CHMV by guess.
4. Ranged weapons: parse the **actual pinned SimC `ITEM_SUBCLASS_WEAPON_*` enum**, not an ID/name whitelist. For current build the original mask bits are **2 BOW, 3 GUN, 18 CROSSBOW** (source `data_enums.hh`), preserving raw bit IDs, exact source names, and a derived `source_ranged_weapon_types_only=true`. Pinned [`permanent_enchant.cpp`](https://github.com/simulationcraft/simc/blob/de11f57df75dda668bae6ac7043a43b98831fa96/engine/dbc/permanent_enchant.cpp) checks item class, inventory and subclass masks against the chosen actual item; this is the relevant original applicability predicate. **Representative gear slot/main-hand vs off-hand validation remains pending**; subclass proof alone is not hand proof. The supplemental row keeps `WEAPON_SUBCLASS_PENDING_EXACT_HAND_APPLICABILITY`, not user-selectable.

## Exact historical 70783 observations — reusable offline source fixture

The 16 already observed physical Wago-linked IDs / eight highest-rank families from [real Wago source Actions #44217110154](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44217110154) are supported by a new *test-only* 6 KB excerpt, `tests/fixtures/p1_v585_70783_linked_enchant_quality_pinned_source_excerpt.json`: exact raw 16 lines of pinned `permanent_enchant.inc` and 16 corresponding raw lines of pinned `spell_item_enchantment.inc`, revision `de11f57df75dda668bae6ac7043a43b98831fa96`, build `12.1.5.70783`. Runtime code contains **no fixed list of these item/enchant IDs**. This tiny historical regression uses **zero Wago/SimC GET and zero Native** on repeated runs.

| Source-only observed family | High enchant ID | Result |
|---|---:|---|
| Sunfire Silk spellthread | 7935 | Same static stat component IDs (intellect + stamina), higher DBC coefficients |
| Bright Linen spellthread | 7939 | Same static stat component ID (intellect), higher DBC coefficient |
| Forest Hunter armor kit | 8159 | Same stamina + strength/agility composite components, higher coefficients |
| Thalassian Scout armor kit | 8161 | Same strength/agility composite stat component, higher coefficient |
| Blood Knight armor kit | 8163 | Same bonus-armor/resistance-type + strength/agility components, higher coefficients |
| Arcanoweave spellthread | 7937 | Different source equipment spell driver IDs by rank; equality not certified |
| Smuggler's Lynxeye | 8613 | Different source spell driver IDs; exact ranged subclass source known, hand pending |
| Farstrider's Hawkeye | 8615 | Different source spell driver IDs; exact ranged subclass source known, hand pending |

All eight quality families have identical **source DBC use/scaling restrictions** within their rank pair but **different `id_spell` across ranks**. Of eight, **5/8** are componentwise nondecreasing in *raw DBC* static components and **3/8** require separate spell-driver equivalence analysis; **0/8 runtime quality dominance or same-effect user filter is certified** by this work. None of these eight source candidates carries a static C/H/M/V component in pinned DBC; do not execute redundant fixed-E Native just to confirm a missing CHMV stat. Do not apply this historical result automatically to a different season/build.

## Tests and previous limitations

[Focused GitHub Actions #44224413528](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44224413528) **SUCCESS**: v583 **8 PASS**, v584 **11 PASS**, v585 pinned source excerpt **2 PASS**, original v240 **20 PASS**, original v216 **31 PASS**, total **72 PASS / 0 FAIL / 0 new Native**. Includes highest coefficient directional test, weaker-high-rank counterexample, diverging driver spell ID, mismatch use restrictions, unknown weapon subclass, raw source vs runtime non-equivalence, next expansion generic enum parsing, old v211/v213 regressions. The v211 pure comparator has no new HTTP or runtime effect logic. Historical other workflow `v191→v196` may separately fail due an **expired GitHub artifact `v192-updated-simc-catalog-41017578894`**: not an observed code regression, and not grounds to claim all Actions green.

## Next real product integration

- Use actual **representative equipped weapon's** class/subclass/inventory type and intended slot from the original internal generated SimC profile to finalize hand applicability for the two ranged options. Do not collect the user's entire currently equipped gear.
- For same-effect/noninferiority, prioritize **existing exact linked SimC enchant-spell source evidence** for these few affected families; use *small selected* Native checks only if that source cannot disambiguate the actual effect/rating. Do not certify independent proc mechanics.
- Once exact effect/use/quality is proven, bind physical ItemID/SimC input to existing `v220→v196→v212→v113` registration and user selection, respecting Policy A automatic admission with no extra manual approval. Keep stat E ownership and no duplicate gear O/L/E constraints.
- Product authority remains `full_product_e2e=PENDING` and historical official ledger `15/78 COMPLETE`; no main merge, immutable file or Project UI update, no main product chat owner change.
