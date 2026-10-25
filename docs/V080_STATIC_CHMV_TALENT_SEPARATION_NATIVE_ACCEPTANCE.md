# v080 — Static CHMV before Hunter talents: corrected real Native contract

Date: 2026-10-25 KST. Isolated GitHub development branch only. Approved Developer Notes v1.2 sections 5.1–5.5: T=G+J+F, source-locked special L already included in G, external fixed E separate, talents and item effects delegated to SimC, no standalone effects/proc/APL research or certification.

## Context: preserve earlier failure and user correction

v079 first real Troll Beast Mastery Hunter numeric witness failed CLOSED on `NONCONSTANT_NUMERIC_INJECTION_OFFSET`: input crit 700→JSON2 buffed728, input 650→buffed676. The real JSON2 was correctly detected, but the prior v079B response overinterpreted this as requiring an inverse affine mapping **to make the talent-inflated JSON2 buffed field equal the official optimization target**. This interpretation does **not** implement the user's target `c` (static CHMV from gear+ordinary gems+flask). v079B's six real Native runs, DPS/SEM/sha evidence and cached replay remain valid *as actual simulations*, not as official static-c parity. Original v079/v079A/v079B receipts remain untouched, with correction annotations in CURRENT and v079 report.

The confirmed scope is **Orc? NO — Troll Beast Mastery Hunter**, 334 mail/ranged-mainhand/no-offhand, original pinned SimC MID2 Hunter APL untouched. Explicitly declared test flask contribution `F=(0,165,0,0)` under the test scenario `flask_of_the_blood_knights_2`; no general spell-effect validator or universal consumable allocation is claimed. `G=2494, J=138, F=165`, official `T=2797`. Oil O was not selected in this test and remains outside official T even when used.

## Corrected numerical boundary

New `v063.render_static_chmv_candidate` takes target **static `c`**, scenario-declared flask **F vector**, and original full SimC source. It calculates `gear_* raw = c − F_declared`; raw values therefore sum to **G+J = 2632**, c sums to **T=2797**. Exact stable SimC profile hash, original action lines/gear/talents, execution iterations and destination identity are verified.

New `v063.validate_static_native` checks that exact injected `raw + F_declared == c`, extracts actual JSON2 `buffed_stats` as a **separate observational field**, and independently verifies Native JSON2 version, SimC revision, positive DPS, SEM and sample count. It does **not** require `buffed_stats == c`; talent-induced gains are NOT inverted away. No claim is made that `buffed_stats` is itself an unmodified pre-talent static rating measure or that manual F attributions are automatically verified from Native.

New `v064.make_static_chmv_request` invokes existing scenario-budget checks (`T`, fixed L, requested candidate bounds) and the existing exact profile/gear/consumable binding. The static `STATIC_CHMV_C_V1` request uses a **distinct DPS cache identity** from former buffed-target/affine attempts. `v064.ingest_native` and `verify_disk_cache` accept the explicitly typed static result without changing historical legacy-mode identity or past real Native JSON2. v065 `execute_one` remains unmodified and does bounded Native runs with persisted attempts and SHA-verified replay.

In this initial correction, the F=165 haste vector was declared explicitly for this particular fixture and checked against the scenario F budget. A complete generic consumer that obtains F vectors from arbitrary consumable selections and handles other E vectors remains future work; this is not a universal correction for all profiles. The original v066 preflight and v065 guided-choice scheduler still use their legacy buffed-target result semantics; the static typed route has **not** been integrated into those original guided-choice boundaries, nor the original v015/v016 product implementation.

## Actual Native evidence

[GitHub Actions run **40204450655**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40204450655): **SUCCESS**, trigger commit `6de8144b8b393783696536cb795f6507388136bd`; full offline regression **446 total, 444 PASS / 2 SKIP**, including five additional static-target / talent-buffed distinction tests. Exact Native pinned SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`, revision `7bc10711b5`. Two original v079 failed-run actual Native JSON2 witnesses were SHA verified and reused **with zero new calls** for exact item static G. Exactly **two new 35-iteration (34 DPS samples each) real Native** were executed under the corrected target semantics.

| Native candidate | Static c crit | Static c haste | Static c mastery | Static c vers | Injected raw G+J | Actual Native buffed crit | Native DPS | SEM | Native JSON2 SHA256 |
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| A | 700 | 699 | 699 | 699 | 700/534/699/699 | **728** | **191011.61553028802** | **581.7414103689254** | `74a8cdcd3cd4a8e8fced5595a2f218b3b36248db05d9a817268f3b464cc8ce9f` |
| B | 600 | 799 | 699 | 699 | 600/634/699/699 | **624** | **192517.7436282334** | **533.22163760484** | `c3c4bf8ef49744d21c4478fb890a419bfd712b5cc0f0515f55a0c2d28b7ec4f1` |

Both c vectors sum to 2797; raw stat vectors each sum to G+J=2632. Buffed crit 728 and 624 are separately reported, not equated to static c crit 700 and 600. Positive DPS/SEM and exact source/cached SHA handling pass. Two SHA-checked cached replays **HIT, zero extra SimC calls**.

Artifact `simc-v080-static-rating-talent-separated-40204450655`, GitHub artifact ID **12602714785**, GitHub metadata digest **sha256:ce1bd916f25fd3f9dd7a40e6ddd9c8a6cf33f25c4bb8acb23ae3508e24a33f78** (metadata confirmed; no independent raw ZIP CRC audit).

## Status and next bounded work

- **PASS:** Distinct typed static CHMV c and talent-inflated buffed JSON2, official GJF arithmetic, full profile/input identity, two actual Native DPS+SEM cases, original v065 execution/sha-cache, legacy suite regression.
- **NOT YET VERIFIED:** Automatic general per-scenario F/E vector attribution; selected weapon oils (O remains outside official T); additional armor/weapon combinations; generic v066 static-mode preflight + v015-derived scheduler integration; statistical convergence or global optimum; original v015/v016 product integration.
- **Next preferred:** Integrate STATIC_CHMV_C_V1 into the existing generic v066/v065 candidate search interfaces **without silently promoting old buffed rating assumptions or appending class-specific effect rules**. Then proceed Fury Warrior plate/dual-two-handed and Retribution Paladin plate/two-handed tests. Keep no repeated Hunter 320-iteration optimal DPS search.
- User-directed DPS-only short-term scope remains distinct from current approved v1.2 formal all-role policy; no change to Project Sources, GitHub main, Work OS, immutable v003, original v015/v016.
