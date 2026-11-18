# P1 v583 follow-up — Generic additional permanent-enchant scope classification (2026-11-18)

## Objective and original boundaries
Build a **reusable expansion-agnostic discovery and triage capability**, not an ID whitelist or a new effect/optimizer engine. This is within the original `v216` Environment Build source phase: Wago physical item → `CraftingDataEnchantQuality` → exact SimC `permanent_enchant.inc` ID. It does not change original v161/v254/v280/v281/v275 receipts, G/J/F/O, any base product runtime, official UI, caches, or Policy A.

Previous `v191` source candidates only included SimC `simc_token.startswith("enchant_")` and `item_class in (2,4)`. This is **not** sufficient coverage of permanent equipment effects: legitimate leg spellthreads, armor kits and ranged-weapon enhancements have different SimC token prefixes. The additional 33 actual Wago ID group came from the same-build physical evidence, not a season membership claim.

## Implemented scope rules (no hand-curated IDs)

In `runner/v583_permanent_enchant_physical_source.py`:
1. Retain all **other exact Wago→SimC permanent effect IDs** outside the previous `enchant_` subset, including ID-linked physical ItemID, English Wago label, Wago class/subclass, rank, exact `SpellEffect`/CraftingData/ItemEffect and **all** original SimC `permanent_enchant.inc` rows where present.
2. Classify by **source item class and applicability masks**, NOT `enchant_` token or English names:
   - SimC `item_class=4` and nonzero inventory-type mask → `DPS_EQUIPMENT_PERMANENT_CANDIDATE_UNADMITTED` (armor).
   - SimC `item_class=2` and nonzero weapon subclass mask → same status (weapon); exact hand/subclass acceptance remains pending.
   - SimC `item_class=19` → `PROFESSION_TOOL_OUTSIDE_DPS_EQUIPMENT`.
   - No SimC permanent source row → `SIMC_PERMANENT_EQUIPMENT_SCOPE_UNRESOLVED`. Mixed/other masks → conservative pending.
3. Compute source-only highest **SimC rank** per exact token+armor class+inventory mask+weapon subclass mask with existing `v191.highest_known_quality`. Report **distinct ID counts** and upper-rank ID list, but do not claim same-effect dominance, numeric potency, correct slot/hand, or publication from rank alone.
4. Preserve original 38/76 matched `enchant_` source facts separately. Original legacy `other_wago_enchant_ids_not_in_simc_source` field name historically means *not in the narrow `enchant_` candidate subset*, **not** absence from the full SimC generated file. The new `additional_enchants_unadmitted` contains raw SimC rows for precise interpretation.
5. Persist the new compact classification in the preexisting optional v583 **v217 projection** and report counts in `fresh_permanent_enchant_item_source`; no extra Wago download or SimC Native. Same build static raw CSV preserved even when SimC revision or classifier code changes; small projection can regenerate safely.

## Actual exact same-build results

[Live Wago + SimC v582/v583 classification Actions #44217110154](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44217110154) **SUCCESS**, build `12.1.5.70783`, expansion `11`, SimC pinned `de11f57df75dda668bae6ac7043a43b98831fa96`; **new Native 0**. Reused identical Wago downloaded bytes to cross-check current production v583 with the existing v582 original matcher: original **38/38** high-rank candidates matched and **76/76** source ItemID–enchant ID pairs identical. Exact **33** additional IDs classified:
- **16** source-grounded DPS equipment permanent candidate **IDs**, eight highest-source-rank candidate **IDs** (three leg-spellthread families, three armor-kit families, two ranged-weapon enhancement families); all **UNADMITTED** pending proper effects/strength and application checks.
- **12** professional tool enchant IDs, source `item_class=19`, outside DPS gear selections.
- **5** with no applicable SimC permanent table row: one physical fishing-line item (not normal DPS gear) and four ancient battle-art items; the latter may belong to an expansion-specific optional system and **must not be silently promoted into the core permanent-enchant catalog** without actual module semantics.
- This classification is an exact current-build observation, **not** a universal expectation of 33 IDs or proof that source item classes/DB2 schema never change across expansions. Classification rules themselves are source-driven; unknown source fields remain PENDING rather than inferred from translated names.

[Offline v583 + original v216 focused Actions #44216942645](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44216942645) **SUCCESS**: v583 **8 PASS**, v216 **31 PASS**, Native 0. Additional offline test confirms a non-`enchant_` armor source enters the non-selectable source-only candidate list; generic armor/weapon/profession/unknown status is token/name independent.

## Next minimal integration

**Do not create a second independent selection/classifier engine.** Reuse **v211 DBC effect/stat and spelltext classification**, **v213 source slot masks**, **v191/v196 same-effect quality/noninferiority**, existing selected Native static E budget ownership only when needed, **v220→v212→v113 verified option path**. In the original `v216` source compiler, carefully extend the exact candidate source for all 8 additional current-build gear families **via the authenticated Wago↔SimC relation**, not by broadening the unfiltered 1062-record SimC historical table. Correct item_class=19 excludes profession tools. Unknown 5 remain separate optional/non-DPS review; a battle-art season module is not generic equipment enchant by default. Missing optional enchant cannot block verified G/J/F/O base.

Do not silently add IDs, English name heuristics, or unvalidated numeric E. Do not infer optional registration or end-to-end success from the source-only relation. Main merge, immutable v003, official product certification, Project UI changes, existing primary development chat ownership remain outside this branch's authority; 15/78 official checklist and `full_product_e2e=PENDING` remain unchanged.
