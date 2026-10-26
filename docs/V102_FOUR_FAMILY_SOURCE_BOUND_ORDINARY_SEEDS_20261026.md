# v102 — Four armor-family source-backed ordinary seed pool (partial P1 delivery)

**Date:** 2026-10-26 KST. **Authority:** isolated GitHub branch development only. This is actual implemented code + offline tests, not a completed all-specialization profile generator, official Work OS/Project Source edit, or a new SimC Native measurement.

## What changed

- New `runner/v102_ordinary_armor_seed_pool.py`: minimal, source-backed **11 item IDs** distributed across all four armor categories. Explicit exact physical slots and source names are verified against Git blob SHA-pinned MID2 SimC source files or the previously Native-corrected v086 Hunter replacement; original crafted/random-stat/tier/proc-specific options are **never silently carried onto ordinary default fillers**. External item pages corroborate armor material and physical item slot; they do not authorize precise static rating at every target ilvl.
- Existing `runner/v101_common_representative_equipment.py` exposes `ordinary_armor_seed(material,slot,ilevel)` and `available_ordinary_seed_slots(material)`, and one-time pinned-source readiness validation. Unsupported armor family/slot/ilevel **fail closed**. This provider returns a typed `{slot,item_id,ilevel,options:{}}` ordinary candidate row. It does **not** silently replace the source-pinned full representative pieces already validated for the four v098 archetypes.
- The `v098` user-entry status now lists `ordinary_armor_seed_slots_available` and explicitly `ordinary_armor_seed_pool_partial_not_full_set=true`. Reference B (334 general 3150; Fury dual-twohand 3350), final inclusive T and O/L handling remain unchanged.
- `verify_pool()` is memoized for one immutable source-read per Python process (fixed-size max=1), and normal execution adds no full-item DB I/O, SimC, network, cache reset or duplicated optimization search.

## Real registered IDs and source-grade distinctions

| Armor | Physical slot | Item ID | Kind and evidence |
| --- | --- | ---: | --- |
| Cloth | Wrists | 251154 | Winter's Embrace Bracers, observed original Frost Mage MID2; https://www.wowhead.com/item=251154 |
| Cloth | Waist | 268257 | Caustic Chain-Wrapped Sash, observed pinned Fire Mage non-tier head fixture; https://www.wowhead.com/item=268257 |
| Cloth | Feet | 268255 | Cackling Soultreads, observed Frost Mage MID2; https://www.wowhead.com/item=268255 |
| Leather | Chest | 251159 | War Trial Vestments, observed Rogue MID2; https://www.wowhead.com/item=251159 |
| Leather | Waist | 268256 | Sash of the Forlorn Vessel, observed Rogue MID2; https://www.wowhead.com/item=268256 |
| Leather | Feet | 159304 | Goldfeather Boots, observed Rogue MID2 **legacy reference**: pre-Midnight original item; NOT advertised as new S2 drop or proof of Native stats at all ilvl; https://www.wowhead.com/item=159304 |
| Mail | Head | 249317 | Frenzy's Rebuke, previously real Native-corrected Hunter filler from v086, **legacy fixed representative** (original item from prior season); https://www.wowhead.com/item=249317 |
| Mail | Waist | 268254 | Serpentine Mixing Belt, observed Shaman MID2; https://www.wowhead.com/item=268254 |
| Mail | Feet | 249320 | Sabatons of Obscurement, previously real Native-corrected Hunter filler from v086, **legacy fixed representative**; https://www.wowhead.com/item=249320 |
| Plate | Waist | 268259 | Girdle of Toxic Regret, observed Fury Warrior MID2; https://www.wowhead.com/item=268259 |
| Plate | Feet | 268260 | Scaled Fiend's Warboots, observed Fury Warrior MID2; https://www.wowhead.com/item=268260 |

**Not counted as generic ordinary pieces:** class-restricted Rogue wristguards `271506`, crafted/random-stat plate `237834`, crafted/random-stat mail `244584`, original unclassified Hunter head `271441`/feet `271440`, user-selected catalyst-special and trinket effects. Do not conflate optional crafter fillers with a proven fixed-secondary ordinary armor pool.

**Remaining gaps:** the seed pool deliberately does **not** provide an ordinary candidate for every physical armor slot; `wrists` for Leather/Mail/Plate are not registered here, and tier-eligible slots are generally the **class-specific tier assembly's** responsibility. This is partial but concrete common-source coverage, not four fully executable general profiles or all-13 class Native approval. Additional ID coverage must be source checked. Prior v086 real Native observations are for exact **options at ilvl334**; arbitrary row with empty options or different ilvl is not the same Native static cache identity and must not reuse measured stats.

## Tests and accounting

- [CI v102 #40325800900](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40325800900) **SUCCESS**, code/workflow head `1ac234d9bd4a5f3580c2ea01912ad0b9ef458691`, 161 offline tests / 0 fail, Python compile and existing pilot PASS, **Native 0**.
- Follow-up user-visible report test on `v098` checks that four existing classes report correct partial material slot coverage and unchanged 334 B; its CI is separate and must be checked before claiming its test success.
- Source validation verifies actual original Git blob SHA and item ID/slot, corrected mail IDs against the v086 `REPLACEMENTS` declaration, duplicate item exclusion, target-ilvl bounds, non-existent slots failing closed, and different source variant/cache keys for same ID at changed target ilvl. Synthetic tests **do not** populate production caches and do not re-audit historical Native effects.

## Exact next P1

1. Fill remaining **minimal common ordinary armor slots**, prioritizing current-season fixed-secondary wrist candidates for Leather/Mail/Plate and a safe four-of-five ordinary fallback. Avoid season-wide gear DB and quantity scaling.
2. Add class-specific five tier IDs and valid weapon **type/subtype** legal maps as small data contracts, joining the existing weapon-topology table. The four existing source-backed specs remain the only current selectable users until exact class/spec APL/tier/weapon inputs are available.
3. Retain v1.4 input simplicity and prioritize eventual one-click Windows input → internal full representative → same adaptive Native simulator → 95%-only results/cache/progress/cancel/resume. Exact Native G is optional, not new mandatory gate.
4. For eligible catalyst-converted user-selected special gear, user policy remains that ALL source effects and fixed L are preserved in correct SimC input and SimC evaluates actual mechanics; do not build separate proc-certification gate.

**No changes** to GitHub main, protected v003, primary product chat ownership, official Project UI or Work OS.
