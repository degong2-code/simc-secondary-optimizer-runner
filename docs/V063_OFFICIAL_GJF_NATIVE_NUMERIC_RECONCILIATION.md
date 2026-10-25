# v063 — Official G+J+F numeric SimC injection, scoped 334 Mage Native PASS

**Execution date:** 2026-10-25 (Asia/Seoul). **State:** isolated development PASS only, **not** original v015/v016 product integration, full cross-spec CHMV accounting, or a global optimum.

## Policy / responsibilities

Project Sources Developer Notes **v1.2** applied by the user. Formula **T=G+J+F**. From prior real v059 output, selected 334 Arcane Mage sample Native nontrinket gear static **G=2849**, J138 and F165 → target **T3152**. The selected weapon oil's 16 crit + 16 haste is **external to official T** and remains in unchanged SimC profile; the previous v059 **T3184** was a bounded oil-inclusive experiment, NOT the general product rule.

**SimC alone** computes item/trinket/embellishment/gem effects, spec APL and DPS. This code does not inspect effect activation, emulate proc behavior, or require a trinket static JSON2 gear row to admit a selected item. A missing trinket static row remains **unknown**, not verified zero.

## Source & method

- `runner/v063_numeric_injection.py`: two previous successful Native simulations (v059 case_00/case_01) supply **numeric input→JSON2 rating** offsets for an exactly unchanged profile. Normalize by removing only `gear_{stat}_rating`, `iterations` and `json2` lines from source. Require the same SHA256 of every other SimC line and identical offsets in both independent target witnesses. Different profile or SimC revision: remeasure the numeric offset, do not reuse the old one.
- Native v059 common observed offset: crit **0**, haste **+165**, mastery **0**, vers **0**. **This is the net observed numeric difference, not an independent proof of which consumed item caused it**.
- `runner/v063_official_T_two_native.py`: assemble v061 normalized input from exact previous SimC profile, use v046 Native JSON2 static records and v062 exact G/L budget, preserve 4 tier gear items and exactly 2 crafted embellishments, select `Mindpiercer's Sigil` id 250224 as trinket1, full profile identity and 13 nontrinket gear entries intact. No new stat DB or unrelated effects research.
- Two candidates each 60 requested iterations, `gear_*_rating = expected JSON2 rating − measured net offset`, then verify `sim.players[0].collected_data.buffed_stats.stats` four final rating fields equal desired candidate, as well as DPS mean, standard error and sample count.
- Full input/source and output JSON2 preserved, SimC error stderr/stdout passed through; no effect fidelity gate.
- Basic duplicate result caching is identity-verified for the same scenario, SimC binary revision, candidate and iterations before use.

## Actual GitHub receipt

- [Native Actions run #40165729165](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40165729165): **SUCCESS**.
- Trigger commit `c09ed5eecf18144dd56eb31a5d0bae6e1d1e623b`.
- 306 regression tests: **304 pass, 2 skip**. Existing `pilot.py check` PASS.
- Two previous v059 Native JSON2 reused for calibration (0 extra calls); two **new** Native SimC DPS calculations.
- SimC binary SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`, JSON2 git revision `7bc10711b5`.
- Artifact: `simc-v063-official-GJF-two-40165729165`; ZIP SHA256 `8df105db3d4758a1e9313093e960fd479f1cae0a6c0526416a1747a2b17009af`; archive CRC PASS; output includes input.simc, result.json and stdout/stderr for both cases, offline/calibration and Native receipts.

| Field | Candidate A | Candidate B |
|---|---:|---:|
| Target crit rating | 600 | 750 |
| Target haste rating | 1108 | 958 |
| Target mastery rating | 1115 | 1115 |
| Target versatility rating | 329 | 329 |
| Official T | 3152 | 3152 |
| Native actual four rating fields | **exactly match target** | **exactly match target** |
| Raw `gear_haste_rating` | 943 | 793 |
| DPS mean | 192374.47259241965 | 192109.85803892397 |
| DPS SEM | 951.0125458611038 | 1300.0174867656742 |
| SimC samples in JSON2 | 59 | 59 |

DPS(B−A) = **−264.6145534956886**. Approx independent 95% difference halfwidth = **3157.0424788284367**. **Not distinguishable**. No global optimum claim.

## Limitations and exact next

**Numerical rating parity for this one representative profile is now proven.** Numeric cause/source attribution is **NOT** automatically proven. In particular nine Native `gear` rows carry gem and/or enchant modifiers (head, chest, legs, wrists, neck, waist, finger1, finger2, main_hand). Their Native `secondary` values may need numeric source attribution before declaring generalized **J/F/G separation** across all profiles; do not infer detailed mechanics or reimplement effects. The existing gear static total is a measured number, not proof of independent gem contribution. Record `numeric_injection_not_all_external_attribution_proof=true`.

Upcoming work:
1. P3 follow-up: make the measured-offset injection calibration configurable for other profiles/ilvl/specs, while retaining honest external component status. Prefer reused reference/evidence and bounded SimC numeric tests. Item proc support is not our work.
2. P4: locate and verify actual **original v015~v016 product adaptive scheduler source and receipts**, then wire its exploration and cache loop to the proven v063 injection+result interface. The source is still absent from this isolated repo; do not fabricate provenance.
3. Later: candidate statistical refinement, materially different near-best CHMV alternatives, persistent resume, UI, tank/healer support.

**No GitHub main, Work OS, Project Source, MAIN ownership or current chat transition.**
