# v053 — Crafted Armor/Weapons + Two Embellishment Static-Data Bridge

**Status:** BOUNDED Native static-data PASS; NOT full recipe catalog or product-integrated DPS optimizer.
**Recorded:** 2026-10-25. Isolated experimental branch only. Developer Notes v1.0 and immutable v003 retained.

## User intent (confirmed in current conversation)

- Representative profile must support craftable **cloth, leather, mail and plate armor, and craftable weapons**, with up to two fixed, user-selected embellishments.
- The crafting choice of two secondary stats determines a roughly half-and-half **initial SimC distribution**; it must **not** be locked as a min-floor for CHMV optimization. Store the actual Native total at exact item level and use it as part of the flexible budget; check rounding with actual Native values.
- SimC processes the selected embellishment's DPS mechanics. A user-selected effect is not merely a display flag.
- Keep crafting list and effect assignment separate from automatic equipment selection. No gear-optimizer scope extension.
- SimC revision is provenance **not** a static cache key. Only add missing item/level/options or perform explicit audited correction.

## Actual implementation

- `integration_probes/catalog/v051_crafted_armor_weapon_reference.json`: 12 grounded crafted IDs (2 cloth, 2 leather, 2 mail, 1 plate, 1 shared cape, 4 crafted weapons), with item ID, slot, family, and actual SimC profile or item-source URL. The slot **template** matrix covers standard armor families and weapon roles; it **does not** claim item IDs for all recipes.
- `runner/v051_crafted_embellishment_bridge.py`: a user-specified two-piece plan must have distinct compatible slots; reserved tier/special-item slots cannot be displaced silently. The original `crafted_stats` pair is an attribute-selector token, **not numeric rating** or a locked optimizer floor. Exact Native data is required to derive a budget; otherwise fail closed. Embellishment effect applicability is still not independently verified on all recorded items.
- `tests/test_v051_crafted_embellishment_bridge.py` and `tests/test_v053_crafted_native_inputs.py`: 219 unittest cases in full suite, **217 PASS / 2 SKIP**.
- `runner/v052_crafted_native_sample.py`: 13 x 1-iteration Native item-only 331-level probes, zero DPS optimization.

## Native evidence

- First attempt v052 run `40154825647` stopped after two successful reads due to a coding error: `KeyError:239656` for shared-cloak `armor_family=any`. Preserve FAIL.
- Successor v053 run [40154940347](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40154940347): **13/13 Native static probes PASS**. Native binary SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`. Artifact SHA256 `9895242d7fa4214466b595bebaf6b4a691edf07a3538b0419034e8656d3097e3`.
- Verified `Martyr's Bindings`, id 239648, ilvl 331:
  - `crafted_stats=49/36`: haste 56, mastery 56, total 112.
  - `crafted_stats=32/49`: crit 56, mastery 56, **total 112**.
  - Thus input stat-pair selection changes the *composition* but not the aggregate static CHMV for this exact item/level; not an empirical proof for every crafted recipe/ilvl.
- Other 331-level Native static CHMV totals: cloak 112; cloth waist 148; leather wrists 112 and feet 148; mail wrists 112 and waist 148; plate wrists 112; crafted offhand/warglaive/1H axe each 100; staff 198 (individual selected reference IDs in catalog).
- Independent offline merge into v050 cache: old 1,747 variants + 11 new + 2 matched/reused = **1,758 variants**; 406 old physical ID catalog + 10 new = **416 ID rows**; **0 static digest conflicts**.
- Portable merged data & independent merge receipt produced outside this repository, not a new Work OS state or GitHub `main` promotion. Provenance preserved.

## Why Mindpiercer's Sigil was BLOCKED

v048 [cross-class diagnostic Run 40152874534](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40152874534) demonstrates item **id 250224** parsed by Native SimC: the stderr recognizes `mindpiercers_sigil` from the ID, process exit = 0, but the player's JSON2 `gear` object is empty in a single-trinket/no-combat probe. All 14 v047 static read variants raised `NATIVE_SLOT_ABSENT`. External item record describes only an equip proc (Shadow damage + temporary Intellect), not base static CHMV. This points toward a **no-static-gear-json2-reporting** limitation, **not** an invalid item ID. This evidence does **not** establish that SimC's proc implementation is supported or unsupported. Keep this trinket unavailable or pending independent effect validation; user allows excluding it.

`Permafrost Essence` (250244) may be excluded in accordance with user direction.

## Remaining work (not falsely completed)

The 12 references are a partial item-ID inventory: full craftable armor slots, full weapon categories, true obtainable crafting levels, offhand/mainhand weapon-DPS attribution, selected embellishment effect applicability and actual two-effect DPS preservation **still need separate verification**. No recommendation of particular equipped crafted pieces is introduced.

`Developer_Notes_v1.1_CANDIDATE` is not official v1.0; no policy promotion was requested. `v016_SCENARIO_CONTRACT` product integration remains unverified. Keep third-party WEQUIP artifact as one-time metadata input only; no runtime dependency.
