# v093 — Inclusive fixed-oil CHMV meets existing v015-derived adaptive Native search

Date: 2026-10-26 KST. **Isolated-bounded acceptance only.** User-approved official T=G+J+F+O; internal allocation B=G+J+F, with O=(32 crit,32 haste,0 mastery,0 vers) fixed for two oiled Fury 2H weapons. B=3350, final T=3414 at ilvl334. Do NOT treat O as freely distributed or double-add it.

## Minimal integration

- New runner/v093_inclusive_adaptive_scheduler_bridge.py reuses existing v065 initial_state, choose_next, accept_scout, confirmation_pair and fresh_confirmation_judgment IN B coordinates. It creates native input via v091/v092 including fixed O exactly once. Native observations are mapped back to B ONLY AFTER full v064 native stat-c, DPS, version, input SHA and oil setting checks; original final T evidence is preserved.
- Existing v065 fresh_confirmation_judgment got a small fail-closed extension for its existing, already-verified static-CHMV Native observation status. No new selection algorithm, statistical formula or SimC effect/proc gate.
- Existing v065_original_scheduler_native_bridge.execute_one handles Native launches and verifies disk cache JSON2 and input SHA, with bounded progress. The actual bounded local driver is in the delivered proof ZIP; it is not the complete Windows product UI.

## CI

[Actions #40262903998](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40262903998): SUCCESS, 529 unittests / 527 PASS / 2 historical SKIP / 0 FAIL. The new search-mapping tests use explicitly synthetic offline observations, not invented Native receipts. Actions new SimC calls 0. Two source-locked initial Native inputs and a portable source bundle were saved, artifact 12625181317, SHA256 3b5d2e4e1a75e2368cc7d27c0e1ab5d1878e4b3dd3a47c91431aa0b50a3da25c.

## Actual SimC Native evidence

Pinned native Linux ELF SHA256 64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e, revision 7bc10711b5, exact source-backed Fury ilvl334 profile, full 16 slot, actual two-weapon oil, unchanged APL/selected gear. Exactly **5 new Native calls** with JSON2. Rating on every case equals requested final T3414.

| Phase | Base B (crit/haste/mastery/vers) | Actual final T ratings | DPS | SEM | Iterations |
|---|---|---|---:|---:|---:|
| Seed A | 838/838/837/837 | 870/870/837/837 | 203205.50 | 977.05 | 35 |
| Seed B | 938/738/837/837 | 970/770/837/837 | 201614.13 | 820.08 | 35 |
| v015-derived scout | 738/938/837/837 | 770/970/837/837 | 203372.06 | 791.86 | 35 |
| Fresh confirmation scout | 738/938/837/837 | 770/970/837/837 | 204529.64 | 522.16 | 80 |
| Fresh confirmation seed A | 838/838/837/837 | 870/870/837/837 | 203843.00 | 486.50 | 80 |

Actual confirmation SimC seeds differ. Existing v065 approximation: 686.64 DPS difference, approx 95% difference halfwidth 1398.78; **NO statistically separated winner**, **NO global optimum proof**, **NO materially distant near-performing alternative proven** (only ~100 rating transferred vs B3350).

## Verified cache/resume and evidence

Exact replay of the identical process returned **5 CACHED_VERIFIED_NATIVE / zero additional SimC calls**, with session-identity check, reread input SHA + Native JSON2 bytes and native observation revalidation. The initial/scout three attempts and two fresh confirmation attempts remained separately persisted. Real Native proof ZIP SIMC_SECONDARY_OPTIMIZER_V093_ADAPTIVE_5_NATIVE_PROOF.zip SHA256 **8fec906c756ef37eccbebe0f960cbedff7191f46b93ac00bcac7af821e1f3382** (38 entries with SHA256 manifest and local replay scripts). Detailed compact git receipt: integration_probes/data/v093_inclusive_B_to_final_T_five_real_native_receipt.json.

## Explicitly still open

Full product v015/v016 original-source integration and universal Windows UI, user progress/cancel/restart, all-specialization & tank/healer coverage, statistically meaningful remote CHMV alternatives and complete convergence are NOT accomplished by v093. The v093 bounded native local driver is diagnostic, not a general product runner. Approved Project Source v1.3 and official external Work OS state changes were authorized but not yet verified applied to the independent UI/Windows source. Work OS M0 status unchanged. GitHub main, immutable v003 and original product bytes unchanged.

Next prioritize robust generic source-bound adaptive runner with durable resume/cancel for full scenarios and material near-alt selection, continuing original v015/v016 provenance checks, while avoiding duplicate SimC work and independent effect certification.