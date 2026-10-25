# v078 / v078B — Elemental Shaman Real Native Cross-Class Genericity Acceptance

Date: 2026-10-25 KST. Product-development isolated branch only. **This is not all-spec certification or original v015/v016 integration.** User requested six representative DPS archetypes; this is the first NEW non-Rogue Native archetype (Mail / Orc / Intellect / one-hand weapon + shield).

## Official source and scope

Use approved SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.2_PROJECT_SOURCE_REPLACEMENT.md (T=G+J+F, not unapproved oil-in-T proposal). SimC alone owns talents/APL, set bonuses, items, trinkets, proc mechanics, DPS. User selected-gear recommendation and new effect/per-proc gates are out of scope.

Pinned upstream APL/gear reference: simulationcraft/simc branch midnight, commit **12aa5dc041b03bf9f9fdd1db00dbc8d3ec0cebb7**, profiles/MID2/MID2_Shaman_Elemental.simc, Git blob **c92d111e37bd684647e4637dcfef3ccb92864cde**. The 82 action/APL lines are preserved exactly. Pilot test character was explicitly changed from source Tauren to **Orc**. Controlled selected item fixture uses source-backed IDs with each item explicitly normalized to **ilvl334**, not the original upstream assorted 330–340 levels or original bonus options. Four Shaman tier slots shoulder/chest/hands/legs, source-based crafted wrists/feet with starting stat choices, source trinkets 270164 and 273796, one-hand weapon 271092 + actual shield slot 268262. A fifth Shaman tier slot (helm) was replaced by hunter-reference mail head ID **271441** so only four Shaman tier items remain. All item legality and effects remain solely SimC responsibility; representative fixture gear choices are not DPS recommendations or a complete item DB. No optional embellishment effects were selected for this first structural cross-class smoke; later variant tests still required. Test oil was omitted; official T excludes external oil regardless.

## Actions run A — first numeric witnesses and exact static G

[GitHub Actions run **40198642691**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40198642691) **SUCCESS**, trigger commit **e3cff2124f30ac6f02f5d4fc9b3470bc3412b971**. Full Python regression **426 total, 424 PASS / 2 SKIP**, newly added 5 offline tests. Actual pinned SimC SHA256 **64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e**, native revision **7bc10711b5**. Exactly **two** fresh 35-iteration Native raw rating witness executions (34 DPS samples each), exact per-profile numeric offset observed independently and equal **+165 crit / +0 haste / +0 mastery / +0 vers**. This numeric outcome is measured on Shaman and NEVER copied from Rogue or Mage.

Original raw witnesses (both 2,800 input rating with distinct allocations) yielded JSON2 final absolute CHMV total **2,965** (including observed +165). DPS means: **198376.28740085344 ± SEM791.3731547545066**, and **200022.8028166571 ± SEM1099.9229716819134**. These two are calibration points, NOT official target-T candidates.

Actual Native JSON2 supplied exact non-trinket static records for all required parts. Native static **G=2645**, scenario **J=138**, **F=165**, hence official target **T=2948**. Status changed from exact-static-cache MISSING to **READY_FOR_TWO_NATIVE_CALIBRATION_WITNESSES**. This did NOT itself satisfy v066's official-T witness requirement because 2965 != 2948; this discrepancy was accurately reported, not masked. Two cached result SHA replays gave zero further Native calls.

Native raw JSON2 SHA256s:
- First **6b19601def22d3bcfe74bf92b763060dda3fdebc7462e197969fd1ebac1c5375**
- Second **43c62c7edeaca2b0992cfcd6fadbb8be891685c5fbc3b35897284b774f9e1579**

Run A artifact **simc-v078-real-elemental-two-native-40198642691**, id **12600019390**, GitHub-reported SHA256 digest **c01c75cd5d636109ebfb8b0d496a39b7dbe4907bba678943871deff853323ef2**.

## Actions run B — official T and real v066/v065 generic Native route

[GitHub Actions run **40199040044**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40199040044) **SUCCESS**, trigger commit **fc2010b8e6ca61815d990c62502d8052d37a6efe**. Full regressions **430 total, 428 PASS / 2 SKIP**. Historical two actual witness source+Native SHA and static cache are independently replayed (not called a fresh Native re-run). Official CHMV target T2948 derived from exact real Native static cache, numeric offset from Shaman's own two witnesses.

**Exactly three** NEW 35-iteration native evaluations, 34 DPS samples each:

| Type | Crit | Haste | Mastery | Vers | Actual mean DPS | SEM | Native JSON2 SHA256 |
|---|---:|---:|---:|---:|---:|---:|---|
| Official A | 737 | 737 | 737 | 737 | 199583.4219411567 | 760.8199656182607 | 705a1f5aa05c30c79b321f44a844c10a85bed8a0721a1733445bb7b35b6aa0c3 |
| Official B | 637 | 837 | 737 | 737 | 197285.9367759424 | 915.8972259217846 | fa23a8c8d98c15939da53bb12a55b2e629d6c73d9a6556e8d06c37672d275887 |
| v015-derived adaptive scout | 837 | 637 | 737 | 737 | 197233.2912971145 | 1068.6226799470808 | c7fbd078e0714c1bba8ee5f1879c2d020edb7327f9eb06bfb103bd31f708fe38 |

All **five** Shaman cases (two first-use calibration, two official, one adaptive) are actual Native results. All three official/adaptive cases report JSON2 absolute CHMV **exactly matching the requested rating vector** with total T2948. The two real official results feed **unmodified v066.prepare** and yield **READY_NUMERIC_PROFILE_SCOPED**. The v015-derived existing v065 scheduler proposes an unseen third target; original v065.execute_one and v064 ingest verify the actual Native JSON2 rating/DPS/SEM. A/B/scout are not independently high-iteration optimized or a proven winner; **global optimum/proper near-best alternatives remain unproven**.

SHA-verified cache replay: **3/3 verified HIT, zero further Native calls**. Maximum three-call bound and durable progress/identity used. No unverified Native acceptance or falsely reused profile offset. SimC stdout/stderr, full exact inputs/JSON2, receipts and source are preserved.

Run B artifact **simc-v078b-real-elemental-generic-40199040044**, id **12601146170**, GitHub-reported artifact digest **sha256:2bd2c8063a3714f297dbd2bbfc28550498f9c08f5458a2ab11e8b4c7498cb103**. Artifact metadata was verified through GitHub, not an independent ZIP CRC download.

## Product conclusion, limitations and efficient next work

This is the **first verified cross-class real generic pathway** beyond Rogue and historical narrower Mage experiments. It proves one specific **Orc Elemental Shaman, ilvl334, mail, 1H+shield** representative APL/gear selection can traverse input generation → two raw Native numeric witnesses → exact static GJF → two official candidate Native JSON2 → v066 profile-scoped preflight → existing v015-derived v065 adaptive candidate → Native DPS/SEM/absolute rating exactness → SHA cache replay. It **does not** prove full weapon/armor/race coverage or global optimizer convergence.

Open coverage types: Hunter ranged/mail, Warrior Fury double two-handed/plate, Paladin Retribution two-handed/plate, exact Mage one-hand+nonweapon-offhand/cloth proposed race, revised Rogue evidence scope; variant changes with 0/1/2 embellishments, user manual T, external temporary oils and full profile builder automation also remain. Real original sources plus exact ID/item options should be used, not invented; targeted static item cache by exact variant, no complete DB or extra per-proc gates.

No official tank/heal role policy change was made. The user-directed **DPS-only test scope** conflicts with old approved Source chapter 10's all-role plan, and must be treated as a user-requested product scope change pending authorized document process. Official Project Sources, MAIN, Work OS, shared state, immutable v003, original v015/v016 and GitHub main remain untouched.
