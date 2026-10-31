# P2 v211 — current-season enchant effect source classification (2026-10-31)

## Purpose and boundaries

v191 already produced the exact 38 highest-source-rank current-season permanent-enchant candidates. Its output intentionally did **not** infer effect magnitudes from names. v211 adds a separate, source-pinned classification layer and exposes that read-only metadata through the existing v196 season catalog.

This is a **classification and provenance task**, not a new enchant simulator, an independent proc engine, a Native acceptance campaign, or permission to enable more user choices.

- Product scope remains 26 DPS specializations; tank/healer and Augmentation remain excluded.
- SimC owns enchant spells, proc timing, stat buffs, damage, APL interaction and DPS. No proc/effect mechanics are reimplemented.
- Only exact Native-measured permanent static CHMV E can affect the automatic reference B/T under the existing v204 contract. Manual inclusive final T remains unchanged. Temporary/proc CHMV buffs are not fixed E.
- Existing T=G+J+F+O, B=G+J+F, oil O once, special fixed L protected in-budget, and cache/session identity contracts are unchanged.
- No Native calls were made in v211. The two existing exact-scope E observations (8025 and 7967) are reused, not repeated.
- No UI selection expansion: 7967 remains the only existing one-scope user choice; 8025 remains developer-only; the other 36 are locked.

## Exact source and deterministic build

Candidate identity is the v191 source list, artifact 12961140046, SimC commit
710c2408bfd3ae4df71b8cd55cdf01f63fd6c926, game build 12.1.5.70575.

The compiler runner/v211_enchant_source_effect_classification.py downloads and verifies these six immutable SimC source files by exact size, Git blob SHA-1 and SHA-256:

| SimC source | Size | Git blob SHA-1 |
|---|---:|---|
| engine/dbc/generated/permanent_enchant.inc | 86,347 | 2321ad985ab4ee960a5a3a80d41b25db9fb2b8af |
| engine/dbc/generated/spell_item_enchantment.inc | 1,093,702 | 7262db77d57d3c041a561de4d3d404431685a7ff |
| engine/dbc/generated/spelltext_data.inc | 3,971,792 | 0197c596fd5dfddbe04a1d7284ec9025d51d3bf3 |
| engine/dbc/data_enums.hh | 75,791 | 23e5af4d5c407aef6092225030019757c9fa3354 |
| engine/player/unique_gear_midnight.cpp | 243,844 | 9bb01bff903f22c3332f9cb6464ed72c0cae27ea |
| engine/item/enchants.cpp | 19,322 | 4876fc816c275844ad6da9be3ca026cdb4a52090 |

The compiler verifies all 38 v191 candidate tokens/ranks/item-class/slot/subclass masks against the exact permanent-enchant source, parses only the 38 target DBC rows, resolves the item-mod enum IDs and spell-text references, and detects direct register_special_effect handlers in the pinned Midnight source. Historical DBC arrays can repeat an enchant ID; exact token/rank/class/mask identity is matched rather than assuming ID alone is unique.

The full source compiler output is retained in Actions artifact 13024719307 (ZIP digest sha256:de051691753e8bd1c3fedee352845a4cbd6fed4287688ef888e7bd5858f70ca0). The compact checked-in runtime projection is data/current_season_enchant_effect_classification.json. Each source compile verifies that the runtime projection exactly matches all 38 compiled source rows, source file hashes, handler names, static-vs-dynamic fields, Native scope and selection boundary.

## Classification result

The source DBC and SimC spell/registration layer classify the 38 entries as follows:

| Source classification | Count | Interpretation |
|---|---:|---|
| Static CHMV rating present | 8 | Four ring rating families, two source strengths each |
| Static non-CHMV stat only or mixed | 19 | Primary, stamina or tertiary (speed/leech/avoidance); four also carry a spell effect |
| DBC spell effects | 15 | Ten weapon effects plus five non-weapon spell effects |
| Existing Native E observations | 2 | 7967 E=0 and 8025 haste E=30, each one exact profile scope |
| Existing user-selectable choice | 1 | 7967 only |
| Developer-only exact scope | 1 | 8025 only |
| Locked | 36 | No new UI choices |

The categories overlap: four items have both static non-CHMV stats and an additional DBC spell effect. The 15 spell rows consist of the ten weapon enchants plus Eagle's Eye, one chest enchant and three empowered helm enchants. Counts must not be added as mutually exclusive bins.

### Static CHMV ring rating

- Mastery: 7965 Amani Mastery; 7969 Zul'jin's Mastery.
- Crit: 7995 Nature's Wrath; 7997 Nature's Fury.
- Haste: 8021 Thalassian Haste; 8025 Silvermoon's Alacrity.
- Versatility: 8023 Thalassian Versatility; 8027 Silvermoon's Tenacity.

These are direct DBC static rating components, not temporary procs. The six IDs other than 8025 have **no exact Native E measurement**. 8025's haste E=30 is reused only for the existing Linux Frost ilvl334 / finger1 / item158366 / exact-profile developer evidence; it remains non-selectable in the normal user UI.

### Static non-CHMV components

- Boots: 8019 speed+stamina; 7963 avoidance+stamina; 7993 leech+stamina.
- Chest: 7957 strength+stamina; 8013 intellect plus mana utility spell; 7985 agility+speed; 7987 hybrid primary stat.
- Helm: 7989 speed; 7991 speed plus travel utility; 7959 leech; 7961 leech plus outdoor-heal utility; 8015 avoidance; 8017 avoidance plus outdoor-movement utility.
- Shoulders: 7973/7971 speed; 8001/7999 avoidance; 8031/8029 leech.

A useful source-level correction: 7963 Lynx's Dexterity has DBC static **avoidance + stamina**, not agility. The English enchant name must not be used to guess the stat.

These static primary/tertiary effects are not CHMV E. This classification does not independently Native-certify all effects or expand user selection.

### Spell and proc effects owned by SimC

The ten weapon spell rows are:

- 7979 Strength of Halazzi — damage proc; custom strength_of_halazzi handler.
- 7981 Jan'alai's Precision — temporary crit rating; custom stat_weapon_enchant.
- 7983 Berserker's Rage — temporary haste rating; custom stat_weapon_enchant.
- 8007 Worldsoul Cradle — healing-triggered target barrier; no dedicated Midnight custom handler found in the pinned registration file.
- 8009 Worldsoul Aegis — defensive barrier / burst effect; no dedicated Midnight custom handler found in the pinned registration file.
- 8011 Worldsoul Tenacity — temporary versatility rating; custom stat_weapon_enchant.
- 8037 Flames of the Sindorei — fire damage-over-time / area damage; custom flames_of_the_sindorei.
- 8039 Acuity of the Rendorei — temporary primary stat; custom stat_weapon_enchant.
- 8041 Arcane Mastery — temporary mastery rating; custom stat_weapon_enchant.
- 8689 Rite of the Hash'ey — adaptive temporary secondary-rating effect; custom rite_of_the_hashey.

The five non-weapon spell rows are:
- 7967 Eyes of the Eagle — critical-strike effectiveness, not static crit rating; custom eyes_of_the_eagle.
- 8013 Mark of the Magister — intellect plus mana-pool utility.
- 7961 Empowered Hex of Leeching — static leech plus outdoor heal utility.
- 7991 Empowered Blessing of Speed — static speed plus travel/skyriding utility.
- 8017 Empowered Rune of Avoidance — static avoidance plus outdoor movement utility.

A missing dedicated custom registration is **not** proof of unsupported or independently accepted behavior. The metadata records the DBC spell path and whether a dedicated Midnight custom handler was found; it does not invent a second effect engine or claim every generic spell was independently Native-accepted. Weapon subclass mask zero is also not a certified all-weapon slot rule.

### Existing Native facts reused, not expanded

- 7967: E={crit:0, haste:0, mastery:0, vers:0}, one Windows Retribution Paladin ilvl334 / finger1 profile. Existing v206/v207 user choice remains exactly that one-scope admission.
- 8025: E={crit:0, haste:30, mastery:0, vers:0}, one Linux Frost ilvl334 / finger1 item158366 exact-profile scope. Developer-only; not general user UI.
- The other six static CHMV ring enchants have source classification but no exact Native E.
- Dynamic weapon CHMV procs are never treated as permanent fixed E. SimC computes their timing and effect during DPS.
- No new Native execution, no 38×26 matrix, no full-season re-collection, no new DPS cache invalidation.

## Implementation and test evidence

- [Source compiler #41155772497](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41155772497): Ubuntu and Windows both SUCCESS; exact six SimC files fetched and SHA-pinned; all 38 rows compiled; compact runtime manifest cross-check PASS; Native 0; no UI promotion.
- [Existing catalog integration #41155959636](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41155959636): Ubuntu and Windows both SUCCESS. v196/v197, exact E budget, Eagle and v202 admission, local HTTP API and UI offline regressions; Native 0.
- [Focused UI regression #41155959593](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41155959593): Ubuntu and Windows both SUCCESS; existing option panel renders the new read-only effect descriptions; only 7967 remains selectable.
- [Windows source beta #41155959570](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41155959570): Python 3.12 and 3.14 jobs both SUCCESS, existing CMD launcher/localhost HTTP path; Native 0. This is not a direct mouse-click test on the user's PC.
- Initial v211 CI attempts had source-parser and workflow issues (historical duplicate DBC IDs, non-target row formats, Windows heredoc shell selection, one incorrect test module name, and a compact static-vs-dynamic manifest mismatch). Each was corrected; final runs above pass. These failures were offline/source-pipeline failures, not Native evidence, and remain in Actions history.

## Current user product behavior and next step

The existing v196 season catalog now attaches a source effect summary to all 38 entries. The existing UI reads effect_description for its read-only list. It still permits **only Eyes of the Eagle 7967** in the current one-scope user path; 8025 is developer-only and all other 36 remain locked. No general permanent-enchant selection or new E budget path is promoted by this work.

Next useful work is **not** a 26-specialization Native rerun. If the user wants additional permanent rating enchants admitted, first select the exact ring ID/slot/profile conditions and perform the minimum exact Native E measurement for the six unmeasured static CHMV variants. Any non-CHMV or spell-only enchant admission requires a separate explicit scope and only the specific acceptance check that is genuinely missing. No blanket 38×26 matrix.

All changes remain on probe/chat-cache-v035-20261024. No main, immutable v003, original v016, Project Sources/Instructions UI, or Work OS promotion.
