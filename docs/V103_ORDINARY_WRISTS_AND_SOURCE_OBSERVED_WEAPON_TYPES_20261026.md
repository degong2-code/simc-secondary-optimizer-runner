# v103 — Source-backed ordinary wrists and exact weapon subtype identity

Date: 2026-10-26 KST. **Implemented in isolated GitHub development branch, not on main.** No new SimC Native call, no Work OS promotion or Project UI modification. Supersedes v102 seed-count notes **only** in current development state; v102 original artifacts remain historical.

## Actual P1 delivery

**Four-family ordinary item pool:** v102's former 11 grounded ID/slot entries now contain **14**, after three additional actual fixed-secondary Midnight 12.1 ordinary wrists were verified from current public item records:

| Armor family | New slot | New item ID | Observed identity/effect attributes | Public item reference |
| --- | --- | --- | --- | --- |
| Leather | wrists | `268240` | Restless Spirit Shackles; Agility or Intellect; Crit/Haste; no equip proc | https://www.wowhead.com/item=268240 |
| Mail | wrists | `273775` | Hydra Scale Wristguards; Agility or Intellect; Versatility/Mastery; no equip proc | https://www.wowhead.com/ptr/item=273775 |
| Plate | wrists | `268239` | Shellbound Bracers; Strength or Intellect; Crit/Mastery; no equip proc | https://www.wowhead.com/ptr/item=268239 |

- Source classification `web_live` is distinct from `SOURCE`'s pinned original SimC blobs or v086 real Native Hunter stat evidence. No new item-season Native variant has been measured for these three `options={}` target-ilvl rows; the source confirms ID/armor/slot/stat-kind, **not exact SimC numeric data across 266–344**.
- Source provenance has exact item URL, material and slot. `verify_pool()` checks field consistency once per immutable process. No season-wide item DB/download or case explosion. `v098` status correctly shows available **cloth 3 / leather 4 / mail 4 / plate 3** ordinary piece IDs. The four existing verified specializations are not silently re-geared or their existing reference B recalculated.

**Exact source-observed weapon subtypes:** New `runner/v103_source_observed_weapon_types.py`, read-only six specialization profile witness table using exact original **Git blob SHA-pinned SimC** source fixtures and externally corroborated real item subtypes.

| Specialization | Weapon form | Exact observed item/type | Product execution |
| --- | --- | --- | --- |
| Warrior Fury | Dual two-hand | `268213` 2H axe + `237847` 2H polearm | Existing four-spec build, source-checked |
| Paladin Retribution | Single two-hand | `268213` 2H axe | Existing four-spec build, source-checked |
| Mage Frost | Dagger and held-offhand frill | `271092` 1H dagger + `245769` held offhand | Existing four-spec build, source-checked |
| Hunter Beast Mastery | Ranged | `268207` bow | Existing four-spec build, source-checked |
| Rogue Subtlety | Dual one-hand | `271093` 1H dagger + `237837` 1H dagger | **Source observed only; not executable from v098** |
| Shaman Elemental | One-hand shield | `271092` 1H dagger + `268262` shield | **Source observed only; not executable from v098** |

- **Crucial distinction:** these are verified source-equipped weapon **shapes** and subtype identities. They are **not** the complete list of weapon subtypes a class/spec is allowed to equip. A rogue holding daggers does not prove that other weapons are forbidden, and a Mage equipped with a frill does not rule out staves. The separate all-spec weapon legality matrix and all-spec APL/tier assembly remain pending.
- The v101 common equipment composer now checks the original 4 currently executable specialization weapon items/types via v103. This protects weapon form, hand count, primary-stat plausibility and exact source identity without adding proc logic, new Native gating or extra optimizer work. The two historical Rogue/Shaman shapes do **not** become product-ready from this metadata.
- `v102.verify_pool` and `v103.verify_observed` are one-time fixture checks per Python process (`lru_cache(maxsize=1)`); subsequent candidate iterations never reread profiles. Exact SimC item options, Native revision and DPS cache separation remain unchanged. Cached same-season Native static records are not mutated.

## CI / tests

- **Final [Actions #40327461959](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40327461959) SUCCESS** at code/test HEAD `1ffe4bd6798b610fb846e802d1bdbda07e80df75`: Python compile PASS, baseline pilot PASS, **169 offline tests / 0 FAIL**, new Native **0**.
- New six-test weapon module verifies six exact original source fixtures, source equipment identity, type, only four executable, wrong weapon ID/form refusal. Revised v102 tests confirm 14 real IDs and new wrists, exclude crafted/random-stat item substitutions, source provenance, unchanged Native cache stat identity. v098 regression adjusts available material count.
- Intermediate CI failures [#40327008095](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40327008095), [#40327268265](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40327268265), [#40327379637](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40327379637) were **failed** runs on intermediate source or stale old expected counts and remain on record. They are not silently relabelled PASS.
- This is **offline input consistency evidence**, not SimC DPS, Native primary/weapon performance, all-special-effects activation certification or a global optimization guarantee.

## Next P1: stop over-investing in catalog expansion

1. User goal remains **complete target-ilvl user flow**, not an inventory DB. The new 14 source-checked ordinary material seeds are a partial reusable pool, **not complete material gear sets**.
2. Extend actual class-tier five-ID sets and APL/source-enabled profiles beyond four current cases (Rogue and Shaman already have pinned original and past Native evidence) using v101/v103 core, **not a copied whole-profile factory per spec**. Verify that class-set identity, filler non-random secondary stat and weapon performance are correct, with minimal new Native only where a changed input warrants it.
3. Assemble the primary-stat-aware ordinary filler set as needed for those new classes; avoid inferring fixed numeric rating or treating a crafted/default proc item as ordinary.
4. Close the P1 user interface and configurable gems/consumables to existing SimC DPS+SEM+95% result/cache/cancel/resume; retain inclusive manual T and fixed oil O and exact selected L. Do not invent user fields for APL/full filler/seed.
5. Maintain **latest direct user decision**: catalyst conversion inherits all source special effects and static L. Correct SimC converted-tier + source variants carry those through; no independent effects certification gate.

**Authority unchanged:** primary existing product-development chat remains owner. GitHub isolated branch is a permitted implementation area; no main merge, v003 change, official Work OS promotion, Project Source or Project Instruction application.
