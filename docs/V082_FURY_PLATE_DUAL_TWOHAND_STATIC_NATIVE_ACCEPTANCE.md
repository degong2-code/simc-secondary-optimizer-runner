# v082 — Dwarf Fury Warrior Plate + Dual Two-Handed Native Acceptance

**2026-10-26 KST — Isolated product development branch only.** No official Work OS, Project Sources, MAIN, shared-state, original v015/v016 or protected main changes. This is a *representative structural engine smoke*, **not** global DPS stat optimization and not item recommendations.

## Scope and source provenance

Upstream SimulationCraft midnight profile pinned to commit `12aa5dc041b03bf9f9fdd1db00dbc8d3ec0cebb7`, `profiles/MID2/MID2_Warrior_Fury.simc`, Git blob **`3225992ed5b754ad5d61e8b785d9d859f1eed1be`**.

- Character: **Dwarf Fury Warrior**, plate, mainhand and offhand each set to a source-backed weapon ID. Main ID **268213** (Maze-roa, Warlord's Fury; two-handed axe); offhand ID **237847** (Blood Knight's Impetus; two-handed polearm). Both weapon IDs are from original source Fury SimC profile; full profile Native PASS confirms input acceptance. Individual type/effect implementation belongs to SimC and was not independently effect-certified.
- ilvl **334** all representative items. Source APL **121 action lines exact preservation**, source talents untouched, original non-ID bonus/options replaced by explicitly declared representative fixture options. Four original source Fury tier items: **head/shoulders/chest/hands**. Crafted representative **wrists + offhand** (actual source item ID; declared `crafted_stats=49/36` is a stat-choice token, not fixed rating floor). Two original source-based trinkets. Total **16 occupied slots**.
- For the controlled test, original source flask was replaced by explicitly declared test **`flask_of_the_blood_knights_2`** with claimed static `F` haste+165 vector. This *scenario-bound input attribution* is not independent universal consumable research. Oil is omitted in this first structural test; official **`T=G+J+F`** and oil O remains outside T even if applied later.
- Gem budget J=138. No embellishment effects selected. No new item DB, equipment recommendation, individual item/proc efficacy gates, or custom Fury APL/effect engine.

## Actual execution and results

[GitHub Actions **40209200603**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40209200603), SUCCESS, run source HEAD `45a45772041d255d926d43568454c39c45adbff5`. Total Python **468 tests, 466 PASS / 2 SKIP** (6 newly added offline/source contract cases). Pinned original SimC ELF SHA256 **`64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`**, revision **`7bc10711b5`**.

At most **4 new actual 35-iteration Native** calls. Exactly **4 succeeded**: one source-backed original Fury initial G fixture, two official static-c witnesses, one existing v015-derived original policy adaptive candidate. All Native DPS collected with **34 usable samples**, SEM and exact input/JSON2 SHA. Both official witnesses enter existing **`v066.prepare_static`** and yield **`READY_STATIC_CHMV_PROFILE_SCOPED`**; the existing v015-local-mirror **`v065`** scheduler proposes the next distinct static target, and existing native executor/evaluator accepts it.

Actual Native exact nontrinket static **`G=3049`**, declared **`J=138`**, **`F=165`**, official static **`T=3352`**. `G` does not double-count the two trinkets, and locked special L was not selected in this fixture. The chosen `F` vector is explicitly declared; no independent flask attribute proof is claimed.

| Case | Static crit | Static haste | Static mastery | Static vers | DPS | SEM | Native JSON2 SHA256 |
|---|---:|---:|---:|---:|---:|---:|---|
| Official candidate A | 838 | 838 | 838 | 838 | **199234.68927356994** | **781.5158019280309** | `12642c570c1d4728deb48d993a19019b3c6d4e15bacd7cfcc24dce3b21410008` |
| Official candidate B | 738 | 938 | 838 | 838 | **199964.15881876418** | **745.1007315542595** | `50e29b8f0587d8fa8cebece4e72b5f15cdf258ffe1bc12dd22194942a5086aee` |
| v015-derived adaptive scout | 638 | 1038 | 838 | 838 | **201291.08642681627** | **899.3241449522894** | `0df35ff31121fe1d259206deb2d5c67cacabec7ca74408d3fc5308f73869eed1` |

For these Fury cases the actual observed `buffed_stats` happened to equal static c for all four displayed ratings, in contrast to Hunter's increased buffed crit. **The engine does not assert this equality as a universal requirement.** Each vector totals T3352; all three official/adaptive results explicitly verify static `c` by **raw injection plus declared F**, retaining SimC's actual buffed rating and DPS separately. The adaptive scout is **not** statistically proven better than alternatives and does not establish global optimum.

The initial Native G-calibration source produced DPS **188004.49399282082**, SEM **730.6525405977657**, Native JSON2 SHA256 **`cc8ac9351a6669a513618cdffbdc207440602a525dea2fee536f0ed16a60e340`**. It was a cache/static-budget bootstrap, not an official T-target DPS candidate.

All four original JSON2 reports were **SHA replayed on cache-only mode** (0 new Native calls), and profile, item IDs/ilvl/options, two weapon slots, exact static cache, source APL, request identity, durable native attempt cap, scenario budget, Native DPS/SEM remain bound. The used Native runner executes SimC per actual source; no gear effects or APL are simulated separately.

Artifact `simc-v082-fury-plate-dual2h-native-40209200603`, ID **12604522727**, GitHub-reported SHA256 digest **`598268a7da79ea5b43c01697eb200e545157e9facae868ef4c6e3184cb780b44`**, size 340615 bytes. Digest metadata verified, not an independent ZIP CRC audit.

## Scope boundary / next efficient validation

- Proven on **three structurally distinct new-ish Native profile paths** since v078: Orc Elemental Shaman (mail, 1H+shield, legacy/buffed semantics), Troll Beast Mastery Hunter (mail, ranged/no offhand, *correct static-c semantics since v080/v081*), and now **Dwarf Fury Warrior (plate, dual two-hand, correct static-c through v066/v065)**. Rogue user fixture and narrower Mage historical evidence exist but do not certify every proposed class/race arrangement.
- Still uncovered in the six-case plan: **Retribution Paladin plate/single two-hand** and **Arcane Mage cloth/one-hand+nonweapon-offhand for the proposed race**; Leather Rogue dual-1H historical evidence must be mapped to the precise six-case contract before claiming full static-c coverage.
- Important latent implementation gaps: **generic profile+consumable F/E attribution** for all scenarios, oil O external fixed input, 0/1/2 embellishments, default scenario spec permutations, main original v015/v016 integration, broader testing and performance/UI. No blanket all-spec Native success or global optimal DPS claim.
- Next efficient branch: add **Paladin Retribution single two-handed** source-backed input as independent weapon slot shape, then cloth/onehand+frill scenario. The same budget/stat/cache/evaluator/scheduler code should be reused with minimum Native calls. Do not add per-class optimizer, complete season equipment database, effect gates or extra Rogue 320-iteration work.
