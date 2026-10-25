# v079 / v079A / v079B — BM Hunter Ranged/No-Offhand Generic Native Validation

> **CORRECTION — 2026-10-25, user-identified Hunter critical-strike talent effects:** The original real Native measurements (700 raw input crit→728 buffed; 650→676) are genuine, but class talents can inflate JSON2 buffed_stats. The product optimizes **static pre-talent CHMV allocation c**, with official **T=G+J+F** (gear + standard gems + flask); other fixed effects are separate. v079B's empirical ×1.04 inverse forced buffed crit to a nominal target such as 700 by injecting a lower pre-talent input; that is **NOT evidence** that the intended *static* crit target was 700. **Withdraw prior v079B claim of correct static CHMV target A/B/adaptive, pending corrected validation.** Actual Native executions, DPS, SEM, JSON2 input/result bytes, SHA, and cache replay evidence remain valid observations. The 439 PASS/2 SKIP regression result verifies the *previous code contract*, not revised target semantics. Do not promote affine inverse or build per-talent effect/proc certification as default. Separate exact input + static budget attribution from observed Native buffed_stats; SimC alone handles talents/effects and DPS. Per approved v1.2 notes, selected weapon oil O applies to SimC but remains external to T until explicit policy approval. This is an evidentiary annotation only; **v063/v064/v066 runtime has not yet been rewritten for corrected target semantics**, and generic Hunter static-target compliance remains unverified.

Date 2026-10-25 KST. Repo degong2-code/simc-secondary-optimizer-runner, branch probe/chat-cache-v035-20261024. **Isolated product-development evidence, not original v015/v016 integration, all-spec acceptance, or Work OS promotion.**

## Why we ran it

The user requested a compact structural coverage matrix for DPS specs: 4 armor types and 6 weapon compositions with different races/primary stats. Following real v078 Elemental Orc Shaman mail one-hand+shield, this adds a **Troll Beast Mastery Hunter, mail, ranged mainhand with NO offhand slot, agility/pet APL**. The point is shared CHMV engine generality, NOT more Rogue optimizer convergence or a Hunter stat recommendation.

Source profile is SimulationCraft midnight upstream branch commit 12aa5dc041b03bf9f9fdd1db00dbc8d3ec0cebb7, file profiles/MID2/MID2_Hunter_Beast_Mastery.simc, exact Git blob **fd9399a7ee0c9c39a362ba31a0d8308e3e000490**. Original SimC action lines including `actions.precombat=summon_pet` are preserved byte-for-byte; the profile's source-derived exact item IDs are normalized into a designated **ilvl334 representative test fixture** (original bonus options replaced explicitly, not assumed identical). Hunter tier four shoulders/chest/hands/legs, trinkets two, starter crafted wrists/waist, no extra item-effect/APL code, no temporary weapon oil in first smoke. This is NOT gear recommendation or a full gear DB.

## First native attempt: actual fail closed

[Actions 40199924239](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40199924239): **FAIL after 2 new real Native 35-iteration cases**, due to `InjectionError:NONCONSTANT_NUMERIC_INJECTION_OFFSET`. Full regressions **436 total, 434 PASS / 2 SKIP**, original real Native JSON2 and source/stdout/stderr preserved in artifact `simc-v079-hunter-ranged-native-40199924239`, id **12601137572**, GitHub metadata SHA256 `3c840cd9ea7ffbae1034f588f74561de48338a0cf526665b5957ac57fa8785d8`. The original v063 two-witness constant-additive calibration correctly REFUSED this input; not labeled acceptance.

[Actions 40200054326](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40200054326): read-only original JSON2 SHA and numeric difference diagnostic **SUCCESS**, **zero additional SimC**. Same exact stable profile and native revision 7bc10711b5:

| Original actual raw witness | Input crit | JSON2 crit | Input haste | JSON2 haste | Crit difference | Haste difference |
|---|---:|---:|---:|---:|---:|---:|
| Original raw 0 | 700 | 728 | 700 | 865 | +28 | +165 |
| Original raw 1 | 650 | 676 | 750 | 915 | +26 | +165 |

Mastery and Vers stayed 700 in both witnesses. Raw JSON2 SHA256s: **00aa895eb3c96c70163c5a7939372942166280912c3ed4e56ee84e5daa24fd96**, **43f32a6add8fb11c53d7c653fc1a77ddf6e6aab9d7be2fee57e8fecaf64cd19e**. Crit changes by **52** for **50** injected raw change. A simple static additive offset is invalid even though haste was consistently +165. This is an **input-to-output numeric observation**, NOT a separate classification/implementation of a Hunter talent, aura, flask mechanism or proc.

## Correction: empirical, profile-specific numerical transfer

Added a backward-compatible branch to existing **v063**: `calibrate_affine` requires at least 3 ACTUAL identical-profile / identical-SimC-revision Native witnesses with TWO distinct injected raw values for EACH of the four stat axes; measures per-stat affine coefficients using only observed raw gear-rating and final JSON2 numbers. No gameplay/mechanics simulation. A candidate's raw injection is the measured inverse **but must still pass exact final Native JSON2 requested-rating parity** (so interpolation/extrapolation is not proof and unsupported targets fail closed). 

Kept `calibrate` strict for old 2-witness constant-offset scenarios; existing constant-offset receipts, semantics and cached result identity remain byte-identical. **v064** adds coefficient keys only for affine calibration to separate DPS cache identity without invalidating old constant cases. **v066** optionally accepts the >3-real-witness profile-specific calibration but still requires TWO REAL official-T JSON2 candidate replay and independent item/profile/hash/budget verification. No original product v015/v016 sources modified.

Reused the TWO original real v079 Native cases; executed only ONE new 35-iteration witness shifting mastery -50 and vers +50, giving empirical mapping from this actual profile:

- Crit input→JSON2: **scale 26/25 = 1.04**, intercept 0
- Haste input→JSON2: **scale 1**, intercept +165
- Mastery input→JSON2: **scale 1**, intercept 0
- Versatility input→JSON2: **scale 1**, intercept 0

These coefficients are MEASURED from this profile and three witness cases; they are **not universal game-mechanics rules** or independently verified across every profile/rating range. All later actual Native exact JSON2 target validations passed, including tested targets outside the initial measured crit interval.

## Independent corrected Native acceptance

[Actions 40200799982](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40200799982): **SUCCESS**. Full suite **441 total / 439 PASS / 2 SKIP**. Trigger commit **50e7ad9db1652c7cf33c76773624c31e9b56dfbf**. Prior 2 actual JSON2 SHA verified and REUSED, not reexecuted. Exactly **4 NEW native 35-iteration calls** (1 extra numeric witness + 2 official candidates + 1 adaptive scout), combined scenario actual evidence total **6 Native calls**, all with 34 DPS samples per case. Separate durable attempt ledger/sha verified replay, hard new-four bound.

Actual exact nontrinket Native static **G=2494**, **J=138**, **F=165**, official **T=G+J+F=2797**. Oil excluded. No unseen trinket static row inferred zero. Actual profile-specific empirical calibration and static cache used.

| Case | Crit | Haste | Mastery | Vers | Exact total | Real DPS mean | SEM | Actual JSON2 SHA256 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Official A | 700 | 699 | 699 | 699 | 2797 | 190817.8176403105 | 707.4060516295324 | 2ba524029395f9c41d643838ed0d3323d195d0576a20cc4fbf711b98bc99f826 |
| Official B | 600 | 799 | 699 | 699 | 2797 | 192755.51183797725 | 516.8978554330117 | da57e3764e1117f51a7000b4653c9b771c592abf40783f955cc12f79e381c1c0 |
| Existing v015-derived adaptive scout | 500 | 899 | 699 | 699 | 2797 | 192891.11393542725 | 511.0837816343482 | 96d23b13306d6cafa142f95f26d3f4fefa750745e0cfa554c14ba884b0f5c540 |

All three candidate Native JSON2 final buffed rating exactly equals requested four integers and all DPS/SEM/samples parsed successfully. **v066.prepare** real official Native profile preflight **READY_NUMERIC_PROFILE_SCOPED**. Existing v015-derived v065 adaptive selection produces a distinct new target; no duplicate or special Hunter search engine. No statistically supported ranking or global optimum from this 35-iteration smoke.

One cache-only repeat verified **all four new Native JSON2 SHA** plus original 2 historical witnesses and completed with **zero additional Native calls**. Artifact `simc-v079b-hunter-affine-native-40200799982`, id **12601797316**, GitHub-reported SHA256 `1d04806d12344cc4947556dbda5a5d5a27a7776770c4b9e6e2e9e270bce16beb`, size 352485 bytes. Artifact SHA is GitHub metadata, no independent ZIP CRC audit here.

## Scope and next structural step

**Verified now**: two distinct new physical/role cases beyond the Rogue user fixture: Orc Elemental 1H+shield and Troll BM Hunter one ranged weapon/no offhand, using the same general budget/numeric-adaptation/scout evaluator contracts. Hunter uncovered a genuine new numerical transfer mode. All other weapon forms, armor families, exact source classes/races still require actual evidence; 6 planned cases are a design matrix, NOT 6 completed tests.

**v080 recommended:** Fury Warrior (plate + dual TWO-HANDED main/off hand, Dwarf, strength), or Retribution Paladin (plate, one TWO-HANDED mainhand, different race). Reuse newly extended numeric calibration, catch exact static item cache and profile issue without inventing gear support gates. Improve reusable source-backed profile producer rather than adding one per class per test. Keep Native run count 2+1+2+1 only when affine branch truly needed, or 2+2+1 when constant offset works.

Remaining limitations: empirical affine slopes may not hold outside measured input region or for other profiles; SimC remains the final authority and exact JSON2 result is always validated. Some integer target CHMV vectors may not have a representable raw injection; fail explicitly or choose nearby *distinct candidate* within unchanged T, never silently alter accepted user goal. General UI, original v015/v016 direct product integration, full role/specialization and 0/1/2 embellishment variants are NOT finished. Latest user DPS-only scope conflicts with approved Developer Notes v1.2 chapter 10 and is restricted to short test scope; official Project Sources/Work OS/main/immutable v003 left untouched.
