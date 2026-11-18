# P1 v586 — DK runeforging as SimC-only permanent weapon effects; prevent unnecessary work (2026-11-18)

## User decisions (latest)

1. The project optimizes **future absolute C/H/M/V rating at target ilvl or user final T** for 26 DPS specializations by **SimC DPS**. Enchant/consumable/item features are only needed insofar as they influence a chosen SimC profile or its fixed CHMV accounting. Do **not** build duplicate effect engines, all-equipment suggestion/season DB, unnecessary item/season certification, broad per-spec Native runs, or independent proc certification.
2. DK **룬벼리기 (runeforging)** is a **permanent weapon enhancement, not an enchantment consumable/scroll item**. Its authoritative option set is the **current pinned SimC DK class module**; Wago item ID, ExpansionID, crafting rank, highest-quality item, Wago source coverage and season membership are **not** acceptance prerequisites. There is no separately modeled fixed secondary-stat E for these existing runes. SimC owns their effects and DPS.
3. Normal physical permanent enchants remain a distinct source path: Wago physical ItemID→CraftingDataEnchantQuality→SimC enchant ID with verified source-quality/slot/hand/E where genuinely needed. Do not transfer those physical-item checks to runeforges. Weapon oils remain a separate optional temporary effect and fixed O budget owner.

## What ALREADY existed; no new duplicate engine

- `v295_season_runeforge_source`: extracts every `RUNEFORGE_ID_*` from the **revision-pinned SimC `engine/class_modules/sc_death_knight.cpp`**, checks its original Git blob SHA and seals the compact result via existing v217; no Wago, no independent effects, no Native. Missing optional rune source does **not** block the verified base G/J/F/O.
- `v216.collect_wago_new_season_source` **already** calls `v295.collect` after the original v191-v213 compilation. `v216` and `v212` already attach `verified_DK_runeforges` to the same installed environment identity. The API `v113` exposes the installed options as `verified_weapon_enhancements.dk_runeforges`.
- `v113` + `runner/webui/index.html` + `runner/webui/app.js` **already** show class-conditional main/off-hand selectors and only accept ids from the installed source. `v106` retains the explicit `runeforge_by_hand` in the user/session identity. `v098` reads the installed v212 SHA and uses its **dynamic, SimC-originated ID list** when starting a new season build; v294 installs the selected rune solely as the selected weapon's `enchant_id`. The original `v294.RUNE_IDS` is a *historical-session fallback*, NOT the authoritative catalog for new season builds. It does not mutate B/T, G/J/F/O, or create a separate enchant E.
- Source pin `de11f57df75dda668bae6ac7043a43b98831fa96` (build 12.1.5.70783) has exactly **7** runeforge IDs: `3368,3370,3847,6241,6242,6244,6245` (actual `sc_death_knight.cpp` enum). An earlier independent `c20e2ad...` pinned-source proof workflow existed, but it is not counted as a newly executed v586 Native/Windows E2E.

## Actual minimal new changes

1. `tests/fixtures/p1_v586_pinned_simc_dk_runeforge_enum_70783.txt` saves **only the 7 actual enum source rows** (not a user-visible static option catalog) for a deterministic regression.
2. `tests/test_v586_pinned_dk_runeforge_environment_integration.py` tests, using existing v295/v212/v294/v055: seven real-source options, source validation, no Wago, no Native, per-rune mainhand serialization, dual-wield two-hand isolation and class/conflicting-enchant rejection, plus a synthetic future SimC rune ID not present in historical v294 `RUNE_IDS`. Tests are pure offline, do **not** claim actual in-game UI-click or new SimC DPS.
3. The **existing** `.github/workflows/p1_v583_permanent_enchant_source_integration.yml` now also runs the v586 regression and the original v294/v295 offline tests; no new workflow, no Native, no full-matrix re-execution.
4. Only user-facing language in `runner/webui/index.html` and `runner/webui/app.js` was revised to say **current installed SimC-sourced DK rune** rather than suggesting a Wago seasonal item quality approval. The existing exact-source selection condition, class/hand layout, available user controls and session identity remain unchanged; the existing UI test expectation is updated.

## Validation/remaining product boundary

[Focused Actions #44225811527](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44225811527) **SUCCESS**, existing v583 8 + v584 11 + v585 2 + new v586 4 + existing v294 4 + existing v295 4 + existing v240 20 + original v216 31 = **84 PASS / 0 FAIL / 0 newly requested SimC Native**, no new Wago source or independent effect Gate. Later UI-only wording checks run in existing v113/v114/v180 offline workflows; record those results separately if available. No complete 26-DPS/product E2E or Windows DK fresh character run is newly claimed.

### Necessary vs unnecessary next work

| Required for actual product | Explicitly unnecessary / forbidden scope expansion |
|---|---|
| Installed exact SimC rune IDs, DK-only/weapon/hand selection, conflict safety, correct `enchant_id` profile, cache/session identity | Wago runeforge items, crafting recipes, expansion/season membership, rank/quality filtering, Native CHMV E measurement for current runes |
| User-facing selections of genuine supported physical permanent enchants with effect/use conditions and only applicable slot/hand, E measured only for **fixed C/H/M/V** | Reimplementing SimC rune or proc mechanics; verifying proc activations with a separate mandatory certification Gate |
| Existing representative profile and internal adaptive SimC to user DPS+SEM+95% outcome | Full equipped inventory UI, item acquisition recommendations, 26-spec×all-enchants blanket Native, rerun old same-build source evidence |
| Optional unresolved item/rune stays PENDING without invalidating base G/J/F/O | Requiring optional rune evidence or unverified enchant quality to complete G/J/F/O |

For the existing ordinary permanent-enchant source, previous v585 **5/8 raw coefficients nondecreasing** do **not** prove actual amount or highest-quality same effect because SimC may obtain the amount from the linked `id_spell`. Only resolve this for a selected supported enchant when it would actually change a displayed choice/CHMV accounting; do not establish a new blanket scaling-certification phase. Preserve original 15/78 full-product completion status and `full_product_e2e=PENDING`.

No main merge, v003 modification, Project UI application, official Work OS promotion, or product-development-chat ownership change.
