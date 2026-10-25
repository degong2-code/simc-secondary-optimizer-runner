# v076 — Generic DPS engine source boundaries and six-archetype coverage audit

Date 2026-10-25 KST. This is isolated GitHub branch evidence, not an official Work OS promotion, v015/v016 original integration, or cross-spec Native acceptance.

## Exact execution

- [GitHub Actions run 40194330151](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40194330151): **SUCCESS**, trigger HEAD 72390bb4e592ad97de052420c8acf1ea8bc26a9e.
- Existing full regression suite: **414 tests; 412 PASS / 2 SKIP**. Five new offline v076 unit checks.
- Actual Native SimC calls during this audit: **ZERO**. The output contains source SHA256 records for nine inspected modules, one 6-case matrix, and 6 OPEN gaps.
- Artifact: simc-v076-genericity-offline-40194330151, ID **12598923240**, GitHub metadata digest **sha256:f6e5d290c468a70d692612c6aff6449563725928917b7835ea7c6758e33918a3** (metadata confirmed; full ZIP download/CRC independent audit not claimed).

## What the inspection actually shows

Shared v061 scenario normalization, v062 static budget, v063 per-profile measured numeric offset, v064 native evaluator / SHA verification, v065 borrowed-v015 scheduler/executor, v066 neutral preflight and v067 generic route are isolated from the v068/v069/v070-v075 Rogue-only acceptance fixture modules by their **direct import relationships**. This does not prove the common route is fully usable across classes. v068 specific gear IDs, offset and official budget are confined to a separate user-profile test fixture. No existing historical results were falsely repeated as independent cross-spec Native proof.

Six planned DPS-only representative cases (item IDs and real class/race legal combinations must be validated before Native execution):

| Class/spec | Armor | Weapon archetype | Race | Main stat | Evidence |
|---|---|---|---|---|---|
| Rogue Subtlety | Leather | one-hand dual wield | Void Elf | Agility | historical actual Rogue Native, exact fixture only |
| Mage Arcane | Cloth | one-hand + nonweapon offhand | Human | Intellect | historical narrower Mage native evidence; this planned human case unverified |
| Shaman Elemental | Mail | one-hand + shield | Orc | Intellect | no Native proof yet |
| Hunter Beast Mastery | Mail | ranged weapon | Troll | Agility | no Native proof yet |
| Warrior Fury | Plate | dual two-handed weapons | Dwarf | Strength | no Native proof yet |
| Paladin Retribution | Plate | one two-handed weapon | Blood Elf | Strength | no Native proof yet |

These cases span 4/4 armor types, 6/6 planned weapon-form archetypes, 3/3 primary stat types and six distinct planned races. These are test DESIGN facts, not gear item-type Native attestations. There is no item-ID database assembled and no invented real-simulation PASS.

## Six source-grounded blockers/open gaps

1. **Generic profile producer missing from v067**. Generic route expects caller-supplied full SimC profile, per-slot filler and static cache. The current specific v068 Rogue constructor is not a generic season profile assembler.
2. **Exact static non-trinket item variants**. v066 fails closed when exact non-trinket static rows are missing; cannot silently copy Rogue static G/T to Warrior or Shaman. Reuse existing same-season static cache where variant identity matches; request only genuinely missing exact items.
3. **Two real numeric witnesses are prerequisites to v066**. Their input/JSON2 must belong to the exact target profile/SimC binary. Do not import Rogue or Mage +165 offset. A new Native bootstrapping process is necessary before v067 can run automatically from scratch. Full number of required SimC calls for new profiles is not fixed: witness results also need to be compatible with v066 official-budget candidate checks.
4. **Weapon archetype not carried as semantic type in v061/v062**. Slots and exact ID are bound, but the native validity of shield vs nonweapon offhand vs two-handed offhand is NOT implied by off_hand slot presence; validate with actual correct SimC input, do not create proc/effect certification gates.
5. **Class/spec/race legality unverified at scenario token-validation layer**. v061 knows class tokens but does not claim a complete race/class/spec compatibility database. Do not claim proposed new cases pass Native before real JSON2.
6. **User's new DPS-only product preference conflicts with approved Developer Notes v1.2 chapter 10** (which still includes tank/heal DPS), while v061 still accepts both roles. Restrict this development **test matrix** to DPS. The official role/support contract must not be changed through Project Sources/Work OS without the user's authorized promotion path.

## Efficient next development

- **v077:** implement a minimum viable reusable representative profile / exact item-variant readiness + two profile-scoped Native numeric witness bootstrap, based on existing v055 and v061-v067 contracts. Prioritize genuine blockers; do not make complete season gear DB or game effect certification.
- **v078:** use four additional structurally diverse DPS profiles for minimal real Native smoke and JSON2 stat parity, with budgeted independent setup/calibration and cache identity. Existing Rogue and narrow Mage evidence are reusable only when the exact case matches.
- **v079:** metamorphic input conditions (0/1/2 embellishments, manual T vs ilvl-derived, offhand present/absent, selected trinket missing static gear row, resumption/caching) mostly offline, targeted Native only if actually necessary.
- Keep full global search or 320-iteration repeat runs of Rogue **paused**; no claimed global optimum, no all-spec validation, no extra effect/APL models.
- Preserve formula T=G+J+F, O outside T, no duplicate fixed L, unknown trinket not zero, crafted 50/50 not locked, immutable v003, GitHub main, approved Project Sources and Work OS.
