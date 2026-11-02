# P3-R — Season Environment Source Standard: identity, data ownership and G/J/F/O lineage
Date: 2026-11-02 | Engine-first isolated branch | Implementation scope v225

## 1. What the product will trust — three separate gates

1. **Source identity / provenance.** Which actual game build, season and SimC commit? What were the exact original bytes, item IDs, tables, retrieval origin and SHA256? A path or record ID alone is not proof.
2. **Semantic/rating proof.** Do exact item→gem-property/effect, consumable effect, quality and weapon-hand conditions actually prove each **numeric** G/J/F/O? A SimC handler, game DB2 row, source URL, sealed hash, or self-declared 'verified' field is **not** sufficient.
3. **Product acceptance.** Only after the relevant proofs do v222 reconciled B/T, v216 Build, v098 generated representative profile and v106 source/SimC/profiler/cache identity match. Existing v220 Policy A can then admit verified UI options automatically without a redundant manual approval step.

Do not set Environment READY when any required G/J/F/O proof is missing. Optional unsupported items do not block a verified base environment. All verification codes are fail-closed. User manual final T overrides automatic T, with B=T-O and L/E/fixed floors verified.

## 2. Exact source ownership and authoritative vs corroborating data

### G — representative ordinary gear, weapon and tier
- Discover exact season/build weapon, ordinary slot and class tier IDs from the authorized Blizzard WoW Game Data API and build-pinned retail DB2 tables. Item/item-sparse/bonus/slot class records establish identities and allowed equipment structure, not absolute G.
- Build a versioned standard *representative* loadout internally at target ilvl and correct weapon layout (especially two-hand dual-wield Fury). Exclude trinket static ratings from free G; protect selected special L already inside G and account E according to whether the reference includes it.
- Prove aggregate secondary rating by same-season, same-scope existing Native reference/calculation or a narrowly requested Native measurement if missing. The existing Midnight S2 ilvl 266–344, 79×2 **rounded-to-10** reference is usable **only** in its season; never copy its G or reference values into a new season. Exact Native G is optional and is not a mandatory universal/per-spec sweep.

### J — gems
- Exact gem item ID and its property/effect via build-pinned item/GemProperties/SpellItemEnchantment relationships (where necessary join item to effect), validated socket count and selected scope. A GemProperties record does NOT alone identify a gem item.
- Compare quality tiers **only within proven identical effects and conditions**. A higher tier can suppress a lower one only when no relevant numeric stat is smaller. Otherwise retain distinct candidates separately until authenticated. Sum the validated stat rating per actual standard socket count into J. No default 138 carryover.

### F — highest-quality flasks
- Join exact item ID from Game Data/DB2 and relevant spell/effect rows to SimC `flask=...` token and selected conditions. Confirm effect magnitude/scaling and highest-quality same-effect comparison. The item's name, rank, or handler alone does not prove its F rating. No 165 carryover.

### O — weapon oils only
- Join exact oil item ID/effect to pinned SimC temporary_enchant token, verify allowed weapon subclass and selected main/off hands and the four-stat vector. In the Native static override O is fixed, applied **once**, outside free B; the user's display T includes O.
- SimC may encode an oil as `temporary_enchant=main_hand:token/off_hand:token`; this is **not** authorization to add general temporary enchant product options. Permanent enchants are separate and their static E is counted once.

### Other
- Food, potions and permanent enchant/embellishment options retain correct item/effect and highest-quality policy; they must not silently contaminate J/F/O. Omnium/season-specific systems are optional modules with their own identity and explicit on/off budget effects. SimC, not this program, executes proc/APL/effect mechanics.

## 3. Source URLs and lineage conventions

Default authorized or corroborating origin classes (source host matching is enforced in v225 for recorded locators; **download response authenticity is a later independent step**):

- Blizzard game-data API, `https://{region}.api.blizzard.com/data/wow/...` with OAuth client credentials where required, namespace and region retained. Validate item ID, inventory type, eligibility and build evidence; an API item response by itself may not expose every effect magnitude.
- Build-specific DB2 CSV snapshots, `https://wago.tools/db2/{Table}/csv?build={game_build}`. At minimum use only necessary item, item relation, effect, gem, enchant and tier tables; not the entire season gear catalog. Preserve table and snapshot build and original bytes.
- SimC pinned Git commit `https://raw.githubusercontent.com/simulationcraft/simc/{40hexcommit}/...` and compiled DBC records (e.g. `engine/dbc/generated/{permanent_enchant,temporary_enchant,gem_data,spell_item_enchantment}.inc` where the pinned tree provides them). The runtime binary SHA and effective SimC revision remain additional acceptance/cache identities. A mismatching generated-source game build is an explicit limitation, not silently reinterpreted as the game build.
- WoWHead item/spell pages may corroborate quality/tooltip behavior when justified; they are not independently authoritative for build-pinned item stats or SimC rating proof.

The game build and expansion/season identity control **static source** reuse. SimC revision alone does not invalidate an otherwise correct same-season item snapshot. DPS cache identity still includes binary SHA, actual profile/options, O, combat, iterations and environment; never carry results across changed input identities.

## 4. New v225 implementation and exact request path

Source archive (GitHub Actions artifact from a specifically selected source collection run, not a user-supplied arbitrary web URL):

```text
source_manifest.json          # v225_season_core_source_bundle_v2
gear.json                     # v167 build-specific candidate equipment
tier.json                     # v168 13-class source tier list
budget.json                   # v165 structured candidate consumable evidence
```

Manifest is internal evidence, **not** final-user input. It records event, prior/new game builds, expansion_id, season name, 40-hex SimC revision, exact fixed filenames and SHA256, and each file's origin system, HTTPS URL, build and retrieval receipt SHA. **Separate component_origins.G/J/F/O** record their source-file routes, candidate item IDs and source declarations, even though J/F/O all read the composite `budget.json`. One consumable source must never implicitly certify the other two.

Path and code flow:

```text
Explicit season_change/expansion_change request
  → GitHub Actions v191 workflow new-season-core job
  → exact chosen same-repo source-run ID + artifact name
  → v225 fixed-file SHA/build/origin/ID validation
  → v224 core-only new-build G/J/F/O provenance/missing evidence
  → small read-only receipt (all numeric ratings null; ready=false)
  → [FUTURE] independent source/value validators G/J/F/O
  → [FUTURE] source-pinned v191/v213 general season joins
  → [FUTURE] v222 B/T and v216/v098/v106 environment/profile/cache acceptance
  → [EXISTING] adaptive SimC DPS execution, cancel/resume, 95% statistics
```

Regular mid_patch still follows **the original v191→v211→v213→v196** path; the new-season route does **not** download/relabel the old default artifacts or run the current-season hardcoded 38-enchant classification as an implicit prerequisite. Source-schema and provenance validations never authorize new UI choices by themselves. v225 is *read only* and verifies no real remote content or numerical G/J/F/O, hence **no full Environment READY claim**.

## 5. Verified changes versus not-yet-implemented

Implemented: `runner/v225_season_source_bundle_intake.py`, `tests/test_v225_season_source_bundle_intake.py`, branch-isolated conditional new-season job in `.github/workflows/v191_unified_season_data_update.yml`; mainline v191 current-season behavior preserved, redundant source-fetch on validator-only commits removed. v225 validates immutable file names, SHA, allowed origin hosts and explicit DB2 build, season/expansion request, per-component source identifiers and stale/mixed game build. Receipts are small, no Native, no new item collector, no static cache mutation.

Verification:
- Initial focused CI failures were expectation/assertion mismatches in the synthetic stale-season tests, corrected without changing source provenance policy.
- [v212 144/144 each Ubuntu and Windows PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41381760593), no Native.
- [v191→v213 real current-season pipeline PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41381448672) after package-import fix. New-season-core was intentionally SKIPPED because this was a push/mid_patch run, not an authorized new-season source artifact request.

NOT implemented/validated: automatic new-season original-data acquisition, independent content authenticity of artifact source locators, exact G/J/F/O rating evidence, quality/effect equivalence admission, new-season general v211/v213 UI publishing, B/T dynamic replacement or actual user-PC Native end-to-end on a new season. The code deliberately reports this, rather than guessing.

Rights unchanged: isolated branch only, no main merge, v003/v016 immutable, no Project UI or official Work OS promotion. Current prior state documents were not rewritten; this report is an addendum.
