# v094 — Generic durable Native runner on approved B+fixed O

**2026-10-26 KST · isolated bounded product development.**

## Contract and capability

User-approved final total **T=G+J+F+O**. Existing base scheduler **B=G+J+F** selects freely distributable CHMV, and O is a fixed per-oiled-weapon vector (crit16/haste16 per actual oiled weapon). Exact source/gear/options, primary and weapon values, tier effects/APL, selected trinkets remain SimC-supplied. **No independent item or proc effect model.**

Implemented a new common **`runner/v094_durable_inclusive_adaptive_runner.py`**. It accepts the existing **v093 prepared context** (from v090/091 with exact user source and special L), two initial base-rating anchors, flask F vector, pinned SimC binary and an output folder. It uses **v093/v065 v015-derived original scout and confirmation selection**, **v091/v092 numeric final T**, and **v065_native execute_one + v064 verified JSON2 SHA disk cache**. It is not a new optimizer. A source-bound CLI accepts `--context-json --seeds-json --flask-json --simc --output [--scouts] [--step] [--max-native] [--cache-only] [--cancel-file]`. On Windows, the output folder is opened at the end when requested; failure to open does not change the calculation status. This is a **prepared-context runner**, NOT a full one-click user-facing Windows GUI.

Durability/safety:
- Session seal protects exact source, scenario, gear identity, binary/revision, oil selection and final B/T, seed anchors, F, scout count, step and **actual Native call budget**. Changing them cannot silently resume old progress.
- New Native attempts are persisted **before** launch via the existing v065 atomic `V065_PROGRESS.json`, recovered after interruption; a native output without an exact verified receipt is a fail-closed partial requiring explicit recovery, never auto-deleted.
- Total Native call limit **cannot exceed the typed scenario's `max_native_calls`**. A fresh session with fewer than `2 anchors + scouts + 2 fresh confirmations` authorized calls is blocked *before* spending Native requests. v065's per-phase cap (4) is also preserved.
- Exact native JSON2/receipt and input SHA256 reread on each cache hit, including oil setting equality with native JSON2, final static T validation, binary SHA and revision. Cancellation file is checked **between** Native requests; interrupting an in-progress SimC process is not yet provided.
- Result includes stage-by-stage progress percentage, input/JSON2 SHA, DPS/SEM and observed candidates. Duplicate base-target observations retain the **higher-iteration confirmation** for reporting instead of misleadingly treating an early scout as a separate allocation.
- Material alternative reporting is filtered only from *measured* candidates: at least 10% of B moved and at most 1% observed DPS drop. These thresholds are experimental and no new far-away candidate is fabricated. No global optimum is asserted.

## Confidence policy (97% consideration)

The user raised **97% as a possible future confidence level**, not an instruction to replace the existing statistical decision. The v065 original 95%-normal-approximation + independent-seed comparison remains authoritative. This runner additionally shows **97% comparison-only** using z≈2.17009 rather than z≈1.95996. At identical SEM, the 97% interval is *wider*, not a reduction in simulation error. No new product-wide confidence threshold is silently promoted.

## CI and four actual Native measurements

Final [GitHub Actions #40266550555](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40266550555) **SUCCESS, 534 tests / 532 PASS / 2 historical SKIP / 0 FAIL**, `runner/pilot.py check` PASS. First v094 Actions #40266278968 also PASS with the same test count; a subsequent formatting/status correction reset per-invocation cache HIT and separated zero-scout reporting from actual guided scouts. Final artifact ID **12627030127**, SHA256 **`1bdb4e3c9f8cb492672725c07d1481e24c6950dde9b06b960c4de286d2abc92e`**. GitHub Actions performed **zero SimC calls**.

Separate actual Native on exact source-backed **334 Fury, two 2H weapons with two Phoenix oils**, SimC binary SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`, revision `7bc10711b5`, B=3350, fixed O=(32,32,0,0), final T=3414. **User scenario caps new calls at 4.** Consequently this v094 run executed **two source anchors + two independent confirmations, with NO new scout**; a request for 1 new scout + 2 confirmations is rejected before Native under this 4-call limit. One actual v015-derived scout was separately verified in **v093** with its own five-call evidence; do not attribute that scout to this v094 test.

| Phase | Final CH/H/M/V | Native DPS | SEM | Iterations |
|---|---|---:|---:|---:|
| Seed A | 870/870/837/837 | 202770.64 | 843.76 | 35 |
| Seed B | 970/770/837/837 | 202668.13 | 870.82 | 35 |
| Fresh confirmation A | 870/870/837/837 | **202725.62** | 544.77 | 80 |
| Fresh confirmation B | 970/770/837/837 | **200681.01** | 579.55 | 80 |

Distinct confirmation seeds present; actual Native JSON2 static rating and selected oils were confirmed by existing v064/v091. Two confirmed candidates differ by **2044.61 DPS**; normal-approximate 95% halfwidth **1558.95**, informational 97% halfwidth **1726.08**. Both exclude zero in *this limited comparison*. These two candidates are separated by only 100 rating moved, **not sufficiently distinct to claim a material alternative**; no global optimum proven.

Replaying the unchanged session returned **4 verified cached Native results / zero additional calls**, with progress 100% and no historical error carried over. Freshly authored offline regression contains 5 tests for cap preflight, cancel/cache-only, session mutation, corrupted attempt counter and 95/97/material alternative reporting. Synthetic test observations are labeled offline-only and are **never** treated as real DPS proof.

Portable user bundle **`SIMC_SECONDARY_OPTIMIZER_V094_DURABLE_NATIVE_4_PROOF.zip`**, SHA256 **`a1607620f9f8d82ceeb4829b3aaacbe88cf0a40e69471e39716efdbdb837140a`**, 32 entries: original actual four JSON2, inputs, receipts, logs, session/progress and replay report, local bounded driver source/tests, prior portable source bundle and per-entry SHA256 manifest. The **locally executed source is validated functionally but its bytes are not asserted identical to the isolated GitHub blob**; GitHub implementation independently passed pinned-source CI. GitHub compact receipt: [v094 Native proof data](../integration_probes/data/v094_durable_inclusive_four_real_native_receipt.json).

## Scope still open

- This is a **generic source-prepared, bounded Native executor**, not original v015/v016 complete product integration, all specialization coverage, mature Windows UI, full cancellation of an active subprocess or deep adaptive exploration/convergence.
- SimC defaults, item properties and talent effects are delegated to SimC, no new fidelity gates. APT cannot be modified silently.
- User-approved Project Source v1.3 / external official Windows Work OS apply remain **not independently accessible or verified** here, and its M0 Gate is **not** asserted passed.
- GitHub `main`, original v015/v016 and immutable v003 remain untouched.

**Exact next:** integrate material-near-alternative *search* (not mere filtering) and adaptive iteration budget escalation in a scenario-authorized Native call budget; improve Windows input UI and progress/cancel semantics, but retain original v015 decision policies and exact cache integrity, with no unnecessary re-simulation of already verified candidates.
