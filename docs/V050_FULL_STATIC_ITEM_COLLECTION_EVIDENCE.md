# v050 — Season 2 bounded static item cache collection (independent evidence)

**Result:** 1,736 / 1,764 requested item/level pairs have actual pinned SimC Native static item data, **28 remain explicitly unresolved**. **124 / 126 scoped item IDs have all 14 proposed levels observed**. This is a bounded metadata+static-stat collection, **not complete current-season crafting/eligibility/gear-effect proof**.

## Provenance

- Scope: Midnight Season 2, candidate itemlevels `292,295,298,302,305,308,311,315,318,321,324,328,331,334`. These were historical comparison levels and **are not proof those levels can actually be obtained** for every item.
- Historic WEQUIP Master inventory, read-only: `midnight_s2_master_gear_db_20260920_174943_optimizer_slots.json` (snapshot 2026-09-20), **395 source-qualified records, 394 distinct IDs**. Extracted `integration_probes/catalog/v047_wequip_20260920_395_metadata_only.json`; stat scaling fields intentionally not imported.
- Known patch 12.1.5 additions: 10 item IDs from source transfer (not a complete live patch gear list).
- Known representative crafting IDs: `239648` and `239656`, profile-derived, `crafted_stats=49/36` only; **the complete crafted template/source catalog was not available**. Historic WEQUIP has a separate 28-template craft-rule DB, but its raw bytes were not accessible here. Do not claim full crafted scope.
- Merged metadata catalog: **406 unique IDs** from **407 source-qualified rows**; most metadata-only IDs do not yet have Native stats. Selected coverage: **126 distinct IDs** after combining 34 provisional armor representatives, 60 historic trinkets, 80 spell-bearing effect candidates, 10 patch delta items and 2 known crafted items (overlapping sets).
- SimC source `7bc10711b5a4514066fa402ca0a71c9ba4b7c9dd`; pinned no-network binary SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`.
- Static cache does **NOT** invalidate automatically on SimC version changes. New static conflicts block and require explicit user-requested corrections. Separate SimC-version-bound **DPS result** caching policy unchanged.

## Execution / independent merge

1. v047 pilot Run [40152488928](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40152488928): 12/12 Native static queries PASS.
2. v047 full 9-batch matrix Run [40152599196](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40152599196): **1,764/1,764 indexes enumerated**; **1,272 newly saved + 16 exact cached + 476 blocked**, all nine ZIPs CRC PASS, no same-key conflicting static digests.
3. v048 controlled class diagnostic Run [40152874534](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40152874534): correctly paired plate=warrior, leather=druid, mail/bow=hunter Native successes. The mage-class probe correctly failed plate head with `Invalid type`. Two trinket IDs `250224`, `250244` absent from Native player gear despite process success, so they are not silently cached.
4. v049 first recovery Run [40153041910](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40153041910) was **FAIL_ENV_CACHE_MISS**; no restoration falsely credited.
5. v050 source-pinned binary restore/build + three class-specific recovery batches Run [40153209773](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40153209773): 448/448 previously blocked armor/bow Native static pairs recovered; binary SHA gate and offline regression PASS.
6. Independently downloaded and checked 9+3 batch ZIP CRCs; each of 1,764 requested indices covered once, 448 recovery indices covered once, same-identity static conflicts **0**. Merged artifact `SIMC_MIDNIGHT_S2_STATIC_NATIVE_COLLECTION_v047_v050.zip` SHA256 **`569ebb4be745c0a86c41426c0e68a90b2c7cf329e24dcc711167779c1c58e026`**; contains original 9+3 zipped receipts, combined cache, per-item coverage, unresolved rows, and independent merge code.

**Final coverage:** 1,736/1,764 = 98.41% static pairs observed; 124/126 IDs full 14-level observation. **Only 28 unresolved**: `250224 Mindpiercer's Sigil`, `250244 Permafrost Essence`, 14 proposed levels each. This is not evidence that the trinkets have zero rating or lack a proc.

**Combined cache:** 1,747 distinct Native static variant records (includes earlier exact decorated variant evidence), 406 identity-only catalog entries, zero manual corrections.

## Critical boundaries

- All data came from actual SimC output, not WEQUIP's `scaled_stats`. Item ID, slot, source are historic catalog metadata only; no spell effect magnitude calculations.
- A v046 static variant includes its full literal modifier/options identity. Do not treat decorated variants (enchants, gems, embellishments) as independently attested *bare* stats. Do not mix static item gear sums with J=138, F=165, or +16/+16 oil without injection reconciliation.
- Some weapon outputs may not expose complete weapon damage fields in JSON2; do not claim those have been fully certified merely because CHMV ratings are present.
- No claim that selected items, itemlevels, bonus IDs, crafted options or sources are current live-game/reachable. No claim that the 80 spell-bearing items are all supported by SimC effects. No item recommendation or full gear optimization.
- **Legacy official v1.0 policy untouched**. An uploaded v1.1 candidate may propose other treatment of oil but must not be auto-promoted. v016 product lineage/integration not yet verified.
- Product code integrated: **false**. Work OS official M0, protected Developer Notes v1.0, WEQUIP runtime and immutable v003 unchanged.

## Independent self-audit

This batch directly enables bounded static gear-budget queries at target ilvls with a native-proven source, keeps version-independent static cache immutable by default, retains errors instead of fabricating data, and avoids unnecessary SimC proc research. Cost: 9 concurrent batches + 3 recovery batches of 1-iteration local Native lookups with no network. The next bounded work is **missing crafted templates + current-season source completeness + two unsupported trinkets**, not broad re-simulation of already cached stat rows.