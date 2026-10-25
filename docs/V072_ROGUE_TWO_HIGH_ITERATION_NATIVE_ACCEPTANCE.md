# v072 — Rogue two fresh high-iteration Native confirmations

Date 2026-10-25 KST. Isolated development branch probe/chat-cache-v035-20261024.
Actual Actions: https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40185708187
Run HEAD f9d13dda6605f5b22b214ceb98e5918fa7ae2571. **SUCCESS**, **394 tests = 392 PASS / 2 SKIP**.
Artifact ID 12596202083, name simc-v072-rogue-two-high-confirm-40185708187.
GitHub-reported artifact digest sha256:a54fd50752cd7fd2519e442853a64c358ba347d02e445139bfa458beaf7aa0e4; separate download / ZIP-entry audit in this chat was not done.

## Proven provenance / reuse

- v069 two independent actual numeric Native witness JSON2 files from Actions 40181981240. The **overall v069 workflow was FAIL**; only separately validated witness bytes are reused.
- v070 official T3150 seed from Actions 40182313167, 35 requested iterations.
- v071 one v015-derived adaptive scout from Actions 40183940144, 35 requested iterations; original JSON2 SHA256 6db7cad804a2c01bb855d3063b9c3e6f71653d4484d853c380c4a541649b95b4.
- Total historical Native cases reused: **four** (two calibration, one official-T seed, one official-T scout); NOT four official-T optimization samples.
- Runner v072_rogue_high_iteration_confirm.py attests historical input/rating/stable-profile/JSON2/receipts, using v071.verified_anchor and existing v064 evaluator. Archive relocation changes the json2 destination; it is not falsely asserted to preserve fully re-rendered input bytes across relocated paths.

## v072 implementation, boundaries

- Uses existing v015-derived v065_v015_scheduler_adapter.confirmation_pair; existing v061 normalize, v062 official static budget, v069 profile-specific calibration, v064 candidate evaluation, v065 execute_one Native+SHA cache. No new scheduler, proc/APL/embellishment model, or effect Gate.
- Runtime envelope alone changed to confirm_iterations=320 and max_native_calls=2, with scout_iterations=35. New P1 digest / P2 recalculation / DPS cache keys; original user character/gear IDs/options/talents/omnium mastery/gem B/APL/Patchwerk 300s and raid buffs unchanged. Original v015/v016 immutable.
- Formula **T=G2847+J138+F165=3150**. Special L=(100 crit,201 haste,0 mastery,0 versatility). Profile-local offset=(165 crit,0,0,0). Oil outside T; trinket static unobserved is unknown, not zero. Five gem/enchant gear rows remain source-attribution ambiguous.
- Resume contract identity, 2-attempt cap, cancellation file, atomic progress, refusal of partial/modified cached output. Cache receipt/input/native SHA and final JSON2 numerical ratings checked.
- New Native executions: **2**, both 320 requested iterations, 319 DPS samples. SHA-verified exact rerun cache hits: **2**, additional Native: **0**.
- Six newly added scoped offline safety tests; current complete regressions 394 total, 392 PASS, 2 SKIP.

## Two actual Native results

| Measurement | A official seed | B adaptive scout |
|---|---:|---:|
| Critical strike | 813 | 713 |
| Haste | 913 | 913 |
| Mastery | 712 | 712 |
| Versatility | 712 | 812 |
| Actual DPS | 223489.6739647237 | 222956.3135273344 |
| SEM | 367.8797924393748 | 371.26203623071905 |
| DPS samples | 319 | 319 |
| Observed seed | 7721403478798083602 | 2876150209437632550 |
| JSON2 CHMV rating exact | PASS | PASS |
| Input SHA256 | 1b4bcc7dd27b1df7b019e7d764e9f03a4dcccc14a19c4225b6a846bc70b8f3cd | 86e3486be97430fc03ebc43734c6805ec7edd14aebdbb5dface134267c7a3c71 |
| JSON2 SHA256 | 92bf0aee6ac60916cfb16c3d014405ca4fa742c7b59ad2a4f90eb40499492f89 | cbf10f3ecf681c794583b3a084f866f433a7bf029b26ce25351a533ba770c031 |
| Native receipt SHA256 | 61f1065d2a65d25a559dc387cd4a67f9e86826bccf96bea7412fd0e56a5a34b9 | ffa8db15b0b71b1a2e551211c8a99649122009c83ac256f92d824ac43b5e522e |

A−B observed mean DPS difference +533.3604373893177. Independent-normal approx 95% halfwidth ±1024.3902121835533, CI [−491.02977479423566, +1557.750649572871].
Distinct actual SimC seeds observed. **STATISTICAL DIRECTION UNRESOLVED**, since CI includes zero. No best/global optimum/convergence claim.

Candidate difference is 100 transferred rating / T3150 = 3.17%, below provisional 10% material stat-distribution difference. No verified meaningfully different near-best alternative yet.

## Next bounded product development

Use existing v065 scheduler, v064 exact scenario cache and this pair to expand promising CHMV regions with small capped scout calls, prioritizing substantially different stat allocations while preserving numeric/SimC-source controls. Do not spend more high-repeat confirmations blindly. Then generalize to other specs, user input/UI and cancellation/progress. SimC owns all effects, gear, procs, APL and DPS. No new engine or equipment recommendation DB.

All official Project Sources, GitHub main, Work OS CURRENT/Shared State, v003 immutable and original v015/v016 source bytes remain untouched.
