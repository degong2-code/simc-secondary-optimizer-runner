# v101 — Common representative equipment core: armor family × weapon form × class-tier IDs

Date: 2026-10-26 KST. **Implemented on isolated GitHub branch.** No official Work OS/Project Sources/main changes, no new SimC Native calls, no claim of all-spec support.

## User-approved architectural objective

Avoid permanent *one full representative equipment profile per spec*. Compose future target-ilvl item inputs using (1) four armor-family categories, (2) legal weapon topology and exact weapon IDs, (3) **class-specific** five-tier item-ID set with 4-piece allocation, and (4) active spec/race/talents/APL supplied to SimC. Preserve two selected trinkets, optional specials/catalyst origination, up to two crafted embellishments, fixed L/oil O and target-ilvl/user-final-T policy.

This stage **extracts the shared equipment composition engine** without changing the source-backed four specific APL profiles. It is the first refactor, **not** the completed source-backed season-wide ordinary armor catalog or all-spec generation.

## Code delivered

- `runner/v101_common_representative_equipment.py`: central mapping of 13 classes to `cloth/leather/mail/plate`; seven slot/weapon topologies (dual onehand, dual twohand, onehand + shield, onehand + frill, single onehand, single twohand, ranged); the **exact five class-tier IDs for four source-backed classes** (Warrior/Paladin/Mage/Hunter). This is mapping of armor class/weapon topology only: it does **not** claim legal weapon availability for every class/spec/item.
- `ARCHETYPES` retains the four source-SHA-verified legacy builders (Fury Warrior, Frost Mage, Retribution Paladin, Beast Mastery Hunter). `source_backed_gear` now checks the class/spec, exact armor/tier identity, weapon-slot topology and exact known fifth ordinary source item **before** releveling all physical gear to the requested ilvl.
- `apply_user_equipment` and `reconcile_four_tier` are now class-tier-data-driven generic operations. User-selected trinkets/special/catalyst-origin/embellishments retain their exact item ID and modifiers; one slot is one physical item; a crafted displacement of one default tier is repaired via a source-confirmed fifth class tier; an impossible four-set is rejected. `physical_gear_groups` emits the existing v061 equipment contract and exact special-origin tier L markers.
- `runner/v098_target_user_scenario_bootstrap.py` routes through v101 rather than duplicating user slot overlay, 4-of-5 allocation, source-profile selection and class-tier identification. Retains `ARCHETYPES`, `FIFTH_TIER`, `FIXTURES` imports for callers/tests. It also reports `armor_family` and `weapon_form` as helpful typed status data, with no change to the existing v096 Native runner and no forced new Native preflight.
- The season Native reference budget B (general or Fury TG special track), manual final T including O, exact special L floor, oil only once, static cache append-only provenance and 95% semantics are **not changed**.

## Validated evidence

- **[Final offline GitHub Actions #40323548556](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40323548556) SUCCESS**, tested code/workflow commit `369618cd310a7041689efb299f5a0490fea5c0de`.
- **153 tests / 0 failures** (full focused v055, v061, v062, v089–v098 and six new v101 tests); Python compile PASS; baseline pilot PASS; **0 new SimC Native executions**.
- Existing four representative source profiles still pass and have the same tier count, individual item IDs and weapon slot presence. Tests include class-tier five-item identity checks, all 13 classes partitioned into four armor families, each source-backed weapon form, supported target-level 321, crafted-to-fifth-tier restoration and unsupported spec refusing ungrounded sources. Prior v100 and v099 historical Native/stat evidence is **reused**, not recreated or broadened.
- CI records from previous commits remain as recorded. Passing tests verify shared structure and existing plan-only behavior, **not** arbitrary new Native DPS measurements or universal class/item compatibility.

## Scope boundaries and next direct P1 action

1. **Actual shared ordinary equipment pools** per armor material are still not implemented. The four current source-backed per-spec constructors remain the only suppliers of complete source-validated ordinary gear / APL. Do not mistake the class-to-material mapping for a complete item database.
2. Generalize to a source-backed **minimum representative ordinary item set for each of cloth/leather/mail/plate**, with correct target-ilvl scaling and major primary stats; retain exact ID/variant and source provenance. This pool must not re-import the user's present gear as target and must not simulate item effects.
3. Register verified class-tier actual IDs and chosen spec's legal weapon families/weapon forms (plus correct weapon stats) as *small data tables*, while using SimC class/spec APL and talent information. Do not claim unsupported cases as ready or invent weapon/class compatibility. A single necessary Native smoke can validate newly different input semantics when feasible without retesting all historic classes.
4. User-configurable gems/flask/food/potion/Omnium and Windows one-click progress/cancel/resume/result display are still pending product tasks. The current visible user-entry test plan has 4 runnable **source-backed archetypes only**.
5. Catalyst direct user decision is **all** original special effects preserved for eligible converted items. Source ID, `redirected_base_stats` and relevant actual item options must be transmitted faithfully; exact SimC effect mechanics/DPS stay in SimC with no new separate effect-fidelity Gate. Test plan-only coverage does not prove all source effect procs at Native runtime.

**Performance:** one pass over at most 16 equipped slots, 5 known tier slots and the user-selected items. No new downloads, DB scans, solver, Native calls, or deep gear recombination. Reduces duplicated selector and tier logic while leaving previous cache identities and existing Native engine intact.
