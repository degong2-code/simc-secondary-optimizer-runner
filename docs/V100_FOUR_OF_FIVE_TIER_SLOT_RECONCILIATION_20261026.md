# v100 — Deterministic four-of-five class-tier slot reconciliation (P1 bounded implementation)

Date: 2026-10-26 KST. **GitHub isolated development only; no main/Work OS/Project Source mutation.**

## Actual code

Implemented in the existing `runner/v098_target_user_scenario_bootstrap.py`, without creating a new optimizer, equipment database, per-spec SimC runner, or Native gate:

- The five **tier-eligible functional slots** are `head, shoulders, chest, hands, legs`. Existing v098 source-backed representative factories supply exactly four functioning class-tier slots; the remaining fifth slot is a verified ordinary item.
- When the user explicitly replaces **one** of the four native tier pieces with a crafted/embellishment item, `reconcile_four_tier()` fills the **exact previously non-tier fifth slot** with a source-identified class-tier item. One user-chosen item occupies one physical slot; tier count remains four, with no silent changes to user-selected slots. This deterministic fulfillment of required tier count is **not** a gear-combination search.
- The fifth tier piece is introduced only when the original fifth slot matches an expected source item ID and has not been separately chosen by the user. Unknown source identity, no available tier position, or an inadmissible fifth tier configuration **fail closed**. Do not invent a fifth class tier from armor-family shared IDs.
- Selected crafted item occupying **two distinct tier-eligible slots** leaves at most three eligible tier slots and is explicitly rejected if four tier contributors cannot remain. Other non-tier selections obey the same rule.
- A selected **catalyst special on the fifth slot** may itself count once as the fourth class-tier piece when another formerly tier slot is occupied by crafted gear, only with the exact fifth **class-specific tier ID**, exact `redirected_base_stats=origin ID`, selected special-tier metadata, and prior exact Native static L. The original item effect semantics and DPS remain owned by SimC; textual source+redirect is not independent proc certification.
- `v055/v061/v062` source-linked identity, exact special-L floor, no double addition, native result cache and user manual-final-inclusive `T=B+O` are unchanged. Newly populated fifth-tier gear uses target ilvl and preserves ordinary fifth-slot gem/enchant metadata where present, but deliberately does not copy its arbitrary `bonus_id`/crafted stats/procs to a different tier item.

## Exact fifth item identities and evidence

| Supported existing factory | Default fifth non-tier slot and item ID | Class-tier ID used when needed | Evidence |
| --- | --- | --- | --- |
| Fury Warrior, plate, dual twohand | legs `271878` | Warrior Greaves of the Jade Warlord `271455` | Original Fury SimC fixture + https://www.wowhead.com/item=271455 |
| Retribution Paladin, plate, single twohand | legs `271878` | Paladin Greaves of the Consecrated Flame `271464` | Paladin original fixture `v083_upstream_mid2_paladin_retribution_reference.simc`, normalized v083 input |
| Frost Mage, cloth, onehand + frill | head `271874` | Mage Crown of the Primal Leywarden `271564` | Pinned original Frost source; normalized v084 replaces original fifth-tier head with `271874` |
| Beast Mastery Hunter, mail, ranged | head `249317` (v086 corrected filler) | Hunter Skulking Viper's Weeping Fangs `271492` | v086 pinned corrected Hunter head + https://www.wowhead.com/item=271492 |

The two sourced web item ID lookups and pinned original profiles establish exact **class-tier item identity**, **not** a newly measured exact Native item variant/stat total. The code maintains the existing rounded reference B vs user manual T distinction. Do not infer 5-piece coverage for other classes or weapon layouts from these four cases.

## Verification

- [GitHub Actions #40317013657](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40317013657) **SUCCESS** on code/test commit `a85f4520f0caa82e1f4685c3343a00829ea1ab99`; 147 offline tests / 0 fail, compile and pilot PASS, **zero new SimC Native executions**.
- Three new v098 regression methods include four archetypes with their correct **real** fifth class-tier IDs, a two-craft-overlap infeasibility case, and a synthetic-cache witness for fifth catalyst-special + first-tier crafted replacement. Existing v089–v099 adjacent offline regressions retained.
- Earlier intermediate workflow runs failed before updated old-rule expectations and tests converged. Preserve their failure status; the final 147/0 evidence is specifically the tested commit above.
- No new proof that switching tier-slot identities leaves DPS exactly unchanged, that arbitrary new target-ilvl combinations are Native legal, or that every special proc is actually present in SimC output. Targeted Native only when real input-source changes warrant it.

## Remaining scope (P1)

1. Common **four armor-family representative slot** catalog + weapon configuration profiles and an explicit class/spec/weapon-eligibility map; replace remaining per-spec factory duplication only after source-backed identity is available.
2. Complete class-specific five-tier item IDs and exact representative ordinary fallback gear where needed; the current automatic fifth swap supports the four archetypes above only.
3. User-configurable gems/flask/food/potion/Omnium, selected gear source eligibility and source-to-catalyst effect serializer; no custom effect-model certification gate.
4. Windows one-click input→Native→95% result, progress, cancel, resume, with precise return of native errors. 
