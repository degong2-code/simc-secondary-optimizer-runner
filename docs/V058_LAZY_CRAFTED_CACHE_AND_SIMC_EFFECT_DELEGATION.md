# v058 — One-Query Native Static Cache for Selected Crafted Equipment

**Recorded:** 2026-10-25. **Status:** bounded isolated prototype, real Native case **PASS**.

## User-approved functional separation

- The program handles **item selection, representative gear compatibility, CHMV budget and fixed floors**.
- **SimC alone handles trinket/embellishment/proc semantics and DPS.** Item effect verification is NOT a pre-admission gate. Pass user-selected ID/ilevel/options into SimC.
- A trinket with no JSON2 static entry is **not an invalid trinket**, nor an empirically proven 0 stat. It is excluded from freely optimizable G by policy; it remains selectable and runs.
- Expanded craftable gear reference: `integration_probes/catalog/v057_crafted_gear_51_recipe_ids.json`, 51 source-qualified recipe IDs (cloth 14, shared cape 3, leather 8, mail 8, plate 8, shield 1, weapons 7, jewelry 2); remaining craft recipe pool is not attested.
- For missing selected nontrinket rating/ilvl, **one on-demand Native static query** populates a version-stable seasonal static cache, instead of bulk pre-simulating every crafted variant. Static cache key: season, item ID, ilvl, slot, exact options. SimC revision recorded only as provenance.

## Implemented files and scope

- `runner/v055_simc_item_selection.py`: an effect-agnostic SimC profile selector and independent stat-budget lookup. Supports explicit user ID even if not in 51-recipe catalog, two embellishments, reserved tier/special slots, trinket cache-miss selection.
- `runner/v058_lazy_crafted_native.py`: exactly one SimC Native call for a cache-missing selected nontrinket; 0 calls for cached variants and all selected trinkets. Full source/options/slot/level identity verified before caching; fail closed on unsupported item or Native slot mismatch. No effect simulation implemented.
- `tests/test_v055_simc_item_selection.py` and `tests/test_v058_lazy_crafted_native.py`: unit tests for unknown/manual IDs, missing static record, no effect gate, no requery if cached, source guard.
- All native numbers from SimC; the Wowhead and archived WEQUIP lists provide only metadata.

## Actual evidence (independent run)

- [v056 selected Mindpiercer Run #40155908015](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40155908015): 1 SimC Native run succeeded with `trinket1=selected_250224,id=250224,ilevel=334,source=local` in the intact representative mage profile. The trinket's JSON2 gear record was absent, but selection and SimC execution were **not blocked**. This is not an independent model of item effect behavior.
- [v057 51 recipes Run #40156264178](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40156264178): full offline regressions **233 pass, 2 skipped**; 51 item IDs unique.
- [v058 one missing crafted lookup Run #40156636301](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40156636301): **242 PASS / 2 SKIP**; exactly 1 native static query for `Martyr's Crown` id **239652**, ilvl **331**, option `crafted_stats=49/36`. Native summed static secondary = **198 rating**; one new exact variant recorded. The second request for an existing variant is served from cache with zero new Native calls (offline unit test).
- Independently merged outside GitHub repository: old 1,758 Native variants + 1 new = **1,759** static variants; catalog from 416 item IDs + 39 previously absent crafted ID records = **455 IDs**; no altered old variants, no invented numeric stat, no cache purge based on SimC version. Bundle `SIMC_S2_v058_CRAFT_AND_EFFECT_SELECTION_PACKAGE.zip` includes source Native evidence, merged JSON and reconciliation receipt.

## Boundaries and open integration

- The 51 is **not** a whole-season exhaustive crafted-item inventory; an unknown item can be selected by ID, with an explicitly provided compatible class/spec/role for stat lookup.
- Full v015/v016 product solver adapter, selected 2 embellishments in complete DPS scenario and all itemlevel recipes need actual product integration. No Work OS or shared state change, main merge, Developer Notes promotion or WEQUIP runtime dependency.
- When original product code is integrated, do NOT reinstate a proc gate from older v051 response fields; v055/v058 supersede that requirement at the item selector interface.
