# v075 Rogue — further bounded coarse-CHMV Native probes

2026-10-25 (KST). All changes isolated to probe/chat-cache-v035-20261024.

## Exact GitHub evidence

- First Actions run [40190557440](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40190557440) **FAIL** at prior Native input archive-relocation check, before new SimC calls. Full suite **407 PASS / 2 SKIP**. The original SimC input embeds an absolute JSON2 destination; regenerate-after-relocation has a different full input SHA. Corrected comparison authenticates original exact input SHA against original native receipt and published v074 summary, and separately verifies relocated stable profile and gear injection. Initial FAIL retained.
- Corrected run [40190657735](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40190657735) **SUCCESS**, trigger HEAD 2b99d070831c278fc0ae419ed7e848794036288d. **409 tests, 407 PASS / 2 SKIP**.
- Actual prior **nine** Native results checked/reused (v069 two calibration numeric witnesses, v070 one official, v071 one scout, v072 two 320 confirmations, v073 two 60 scouts, v074 one 320 D confirmation). v069 overall historical workflow FAIL remains unchanged.
- Actual **two new 60-iteration SimC runs**, **59 valid DPS samples each**, exact final JSON2 CHMV rating, two distinct seeds, then **2/2 SHA-verified cache hits, zero additional Native calls**.
- GitHub artifact ID 12598060958, name simc-v075-two-coarse-scouts-40190657735, reported digest **sha256:29232dfc009fe4dc5dc76a86b8905dc969df5ff9914d1ad2e023e3a40aface10**, 176551 bytes. Digest reported by GitHub metadata, ZIP not separately downloaded or CRC audited here.

## Original user-approved contract preserved

Void Elf Rogue Subtlety, target ilvl334, exact user-selected talents, two trinkets and two independent embellishments, special weapon/armor and tier4, Omnium fourth UI choice Mastery, special gem B, Patchwerk single-target 300s, raid buffs ON. Native SimC owns effects/APL/procs/DPS, optimizer handles exact input and numeric stat budget only.

G2847 + J138 + F165 = **T3150**. Fixed special L=(100 crit,201 haste,0 mastery,0 versatility); calibrated profile offset=(165 crit,0,0,0); oil outside T. Missing trinket static rows are not assumed zero. Craft initial 50/50 split is not locked.

Existing v015-derived v065 scheduler used without a third optimizer: two 60-iteration scouts use **350 rating transfers** (11.11% of total T) and a hard two-Native-call cap. Critical historical dedup: the 59-sample v073 exploratory D has the same CHMV as the v074 independently confirmed 319-sample D. Scheduler receives **confirmed D** for that target and retains the old exploratory D ONLY as authenticated provenance; it cannot shadow the high-precision measurement.

## Actual DPS, JSON2 SHA

| Item | D (v074 independent 320) | E (v075 new 60) | F (v075 new 60) |
|---|---:|---:|---:|
| Crit | 1163 | 1513 | 813 |
| Haste | 913 | 913 | 913 |
| Mastery | 712 | 712 | 1062 |
| Vers | 362 | 12 | 362 |
| T | 3150 | 3150 | 3150 |
| Mean DPS | 224438.67880885603 | 223990.08400132472 | 227079.55524644855 |
| SEM | 365.5631654816179 | 719.9689625507632 | 895.9370011237976 |
| Samples | 319 | 59 | 59 |
| Seed | 8421873418601877966 | 13298169343504398826 | 13564383924807501855 |
| JSON2 SHA256 | f3b88669b208ac5a7d172b3656e024e26629c6cd54f6be675edd9dd56e2b5cd6 | c1732d5672f174919ba254cc835639ca9a94ff3db97bdf7ebbda4263bcdea44f | 0aef1063bc73ef35a4667a670a13e4438c2a1d3d6492b4be296a7c1b7934ffcf |

E−D −448.5948075313063 DPS; descriptive unadjusted 95% approximate CI [−2031.1874283935852, +1133.9978133309726]. F−D +2640.876437592524 DPS (+1.18%); descriptive unadjusted 95% approximate CI [+744.3243607068825, +4537.428514478165]. **F is selected among adaptively sampled low-iteration scouts**; naive confidence intervals omit multiplicity/selection uncertainty. Its higher low-iteration mean is NOT proof of better optimized CHMV.

## Policy and next

- Coarse candidate step remains **350** as experimental, *not an approved permanent optimizer step*. The v075 advisor can *propose* 100 rating only if no unvisited 350-step neighbors remain; automatic future policy and stopping criterion are unproven. Current v015 derived next advisory is 463/913/1412/362 with 350-step. This next proposal is driven by partly noisy scout evidence, not high-precision optimality.
- The experiments have not proved global convergence or confirmed a globally best material-distance alternative. Existing high-iteration confirmed A, B, D results remain isolated and preserved.
- **v076 next:** verify F independently with 320-iteration Native confirmation, compare against already independent D/A, prohibit pooling F's exploratory 59 samples with fresh 319 samples, then weigh additional 350-step coverage versus local step reduction.
- No changes to original v015/v016 product files, Work OS, Project Sources, GitHub main or protected v003. No game proc/effect gate or equipment recommendation system added.
