# v057 — Wider Craftable Item Reference + SimC-Owned Effects

**Date:** 2026-10-25
**Result:** offline full regression PASS; one real SimC trial for effect-only/zero-reported-static trinket PASS. Isolated branch, NOT original product integration.

## User instruction clarified

1. **SimC owns item effect semantics and combat DPS.** The CHMV optimizer must not create a pre-admission effect/proc behavior verification gate or independently implement the item's effect. Pass the exact user-selected item ID, level and options to SimC. If SimC later reports an execution error, pass it through honestly.
2. **Mindpiercer's Sigil 250224 is selectable.** Its stand-alone/representative JSON2 may have no gear stat record, but a missing stat record is not evidence of an invalid or unusable item. Treat a missing static record as **unknown/not reported**, not confirmed 0. Trinket static stats always belong outside the freely optimized G budget.
3. Crafted equipment is for **two user-selected embellishments** and correct representative gear/weapon configuration, not gear combination optimization. Crafted 50:50 starting CHMV does not lock optimizer stat floors. SimC handles the selected two item's effects.
4. The prior 12-item Native crafted sample was deliberately bounded, never an exhaustive recipe pool.

## New code

- `runner/v055_simc_item_selection.py`: safely replace selected equipment lines on a full representative SimC input; option permitlist, 1-2 selectable trinkets without a static-cache hit, at most 2 explicit `embellishment` options, optional reserved tier/special slot protection, manually entered uncatalogued crafted item IDs remain selectable, actual static G for non-trinkets must still originate from Native or appropriate separate user-provided T.
- `integration_probes/catalog/v057_crafted_gear_51_recipe_ids.json`: 51 actual recipe-link IDs, using season profession recipe guide sources. Metadata only; no fabricated ilvl or CHMV. Cloth 14, shared cloaks 3, leather 8, mail 8, plate armor 8, shield 1, weapons 7, jewelry 2.
- `tests/test_v055_simc_item_selection.py`: no-trinket-stat admission, manual crafted ID, two embellishments, tier protection, sanitization, budget exclusion.

## Native proof of Mindpiercer 250224

GitHub Actions [v056 #40155908015](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40155908015) **SUCCESS**.
- Full original Mage reference scenario retained with one explicit replacement: `trinket1=selected_250224,id=250224,ilevel=334,source=local`.
- 1 pinned Native SimC call, return code 0; actual JSON2 player exists.
- JSON2 gear trinket1 record absent, which **does not block the selection or run**.
- Full regression **231 pass, 2 skipped (233 total)**. This validates pass-through operation, **not any stat scaling or effect implementation of our own**.
- Artifact `simc-v056-selected-mindpiercer-40155908015.zip`, SHA256 `d9e4d6d1237d31412626ddf89ad6753c635388be119505a55c5372adf605bb1e`.

## 51 crafted recipe ID admission

GitHub Actions [v057 #40156264178](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40156264178) **SUCCESS**.
- ID + slot + source links for 51 recipe records; out-of-catalog user IDs do not block SimC input generation.
- Existing prior v053 1758 Native item variants preserved, with **no** invented stat for any recipe ID not already sampled; output merged in isolated downloaded portable bundle only, not project shared state or GitHub main.
- User-selected static stats are not recomputed merely because the SimC version changes.
- Complete recipe-pool census and itemlevel reachability **not proven** by these links, but no need to wait for a complete list to let users choose a valid item ID.
- Source guide URLs:
  - https://www.wowhead.com/guide/midnight/professions/tailoring-overview-trainer-locations-recipes-tools
  - https://www.wowhead.com/guide/midnight/professions/leatherworking-overview-trainer-locations-recipes-tools
  - https://www.wowhead.com/guide/midnight/professions/blacksmithing-overview-trainer-locations-recipes-tools
  - https://www.wowhead.com/guide/midnight/professions/jewelcrafting-overview-trainer-locations-recipes-tools
  - https://www.wowhead.com/guide/midnight/professions/inscription-overview-trainer-locations-recipes-tools

## Explicit non-goals / boundaries

- **Do not** reintroduce item proc verification as a condition to choose a trinket or embellishment.
- Do not confuse JSON2 gear-report omission with item's proc support. No fabricated 0 stat for missing JSON.
- No WEQUIP runtime dependency. No large gear optimization engine. Manual ID fallback and static Native lazy additions preferred over fetching every level/effect combination.
- Developer Notes v1.0 remains the official baseline. v1.1 CANDIDATE's previous assumption of effect-verification gating must not silently supersede user's later explicit correction. No Work OS, MAIN pointer, CURRENT, Sources, v003 immutable, or GitHub main mutation.
- Product v016 integration is separately unverified. Native/static-catalog prototype branch is not a shipped product.
