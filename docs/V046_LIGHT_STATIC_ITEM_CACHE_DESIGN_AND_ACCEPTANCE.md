# v046 — Lightweight Static Item Cache (development-only)

**Status:** isolated GitHub pilot PASS; product code not integrated; official policy not promoted.  
**Approved user clarification (2026-10-25):** do **not** automatically discard static gear stats just because SimC updated. Item stats rarely change mid-season; add new items incrementally and apply changes to existing cached stats only after an explicit user-requested correction. A new season has a separate cache namespace. This is a user-specified handling rule, **not** a rewrite of Developer Notes v1.0.

## Boundaries

- **What is cached:** a resolved item's static CHMV, primary/other numbers present in a Native JSON2 gear slot, and its exact season/ID/itemlevel/modifier options; identity and source attribution. Entries with gems/enchant/embellishment are exact **resolved variants**. Their values are *not* authorized for other unmodified/bare variants.
- **Metadata catalog:** old WEQUIP master JSON and new patch-delta JSON supply IDs/names/slots/armor/source hints **only**; never import or promote their scaled secondary stat estimates as Native truth. WEQUIP is a one-time optional file input, **not** authority or a runtime dependency.
- **What is NOT cached:** SimC computed DPS, APL, proc magnitudes, trigger timings, dynamic buffs, new item selection decisions or automatic best-gear suggestions. Missing stats are not treated as zero.
- **Key:** `season + item_id + itemlevel + normalized slot + exact static-affecting modifiers` (including bonus IDs, redirects, crafting stats, gems, enchants). **SimC revision excluded.** Native SimC revision and JSON2 SHA remain in provenance.
- **No silent overwrites:** re-import with identical identity and identical values returns REUSED; differing static values returns BLOCKED and does not write cache; explicit `correct` command requires matching prior digest, user request and a reason. New seasons cannot reuse previous season's values.
- **Crucial separation:** This rule applies to the **static equipment cache only**. Actual DPS result caches still distinguish SimC revision/APL and combat conditions under the approved Developer Notes v1.0 §13.3.
- **Budget policy unchanged:** `T=G+J+F`, `J=138` and `F=165`. Existing limited tests of oil +16 crit / +16 haste are preserved as bounded trials, not a general policy promotion. A resolved-variant sum may contain gem/enchants; summing `G` then independently adding `J/F` without scenario attribution remains **not admitted**.

## One-time initial seed

Run [GitHub Actions 40151392965](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40151392965), `simc-v046-static-cache-40151392965.zip`, independent ZIP SHA256:
`e06bb795453c0b4b04acfbd57a7296be6bbca90c6a8dc3dfae6f9a9046a35b18`.

- 15 resolved ilvl334 item variants from pinned v045 single-player JSON2; **only one Dwarf Arcane Mage test scenario**, not full armor classes.
- 10 Patch 12.1.5 Kith'ix item identities (3 trinkets, 7 special nontrinket items) from partial transfer source, **catalog-only, no invented Native stats**, not complete season collection.
- Native SimC runs **0**; full regression **189 total, 187 passed, 2 skipped**; double-import of the 15 variants produces zero new records, 15 cache hits; ZIP checksum/CRC independently verified. JSON cache 25,185 bytes; ZIP 4,464 bytes. Independent receipt: `V046_RECEIPT.json` in ZIP.
- Hash-pin check on the original v045 result.json `6ce1b02ae56667d023e4e049ad978c64bd52d8094c5795e542c532399eaf79c4`.
- The historical WEQUIP Master was discoverable as an indexed Project file (382 equipment IDs / 395 source entries / 14 ilvl rows declared in 2026-09-20 snapshot), but its **whole raw bytes could not be materialized for programmatic import in this session**; do not claim the whole 382+ metadata or ilvl scaling was imported. The old snapshot is not patch-complete.

## Local Windows usage (offline; Python stdlib only)

The command takes a cache JSON path and operates without SimC or WEQUIP runtime.

```powershell
python runner/v046_static_item_cache.py --cache cache/midnight_s2.json import-catalog --input path/to/exported_master_or_patch_catalog.json
python runner/v046_static_item_cache.py --cache cache/midnight_s2.json import-native --input path/to/Native_result.json --artifact-id LOCAL_CAPTURE
python runner/v046_static_item_cache.py --cache cache/midnight_s2.json summary
```

For ZIP evidence input, `import-native --input path/to/proof.zip --zip-member native/result.json`. Each Native import is append-only; no network calls, no combat simulation, no duplicate recomputation. Cache is atomically replaced, with fail-closed identity/stat checks.

To correct an existing stat **when the user explicitly asks**:

```powershell
python runner/v046_static_item_cache.py --cache cache/midnight_s2.json correct --request path/to/approved_correction.json
```

The request must contain the exact `identity`, `expected_static_digest`, `new_static`, an explanatory `reason` (12+ chars), and `user_requested:true`; the prior digest must match. This is a local correction workflow, not a change to the Project Sources.

## Next core development, not yet done

1. Import the actual current item catalog when the raw export is available: representative armor bases for cloth/leather/mail/plate, crafted templates, known special-effect items and user-selectable trinkets. Preserve source and category classification, do **not** import WEQUIP projected stat amounts.
2. Use real Native data for the chosen **valid** ilvl/bonus/crafted variant, with a bounded batch query when first missing, then persist the resolved static values. Do not treat test-only 334 bonus assignments as game-proven.
3. Distinguish gear-only static `G` from effects/gems/consumable allocations when building the CHMV scenario; preserve user-locked special equipment floors and existing oil 16/16 semantics without double-counting.
4. Reconnect to the actual v016 product/adaptive optimizer only after independently validating original code lineage and missing source receipts. No Work OS M0, CURRENT, Project Sources/Instructions, or immutable v003 changes here.

## Three-axis acceptance

- **Test success:** PASS for cache contract and one prior Native JSON2 import. Does **not** mean itemlevel-wide or all-armor-class Native coverage.
- **Product code integrated:** FALSE.
- **Official policy promoted:** FALSE.
- **Runtime authority:** SimC for DPS/effects; this derived cache is offline static reference only.
