# v091 — Explicit per-weapon oil, 0 / 1 / 2, real Native input acceptance

**Date 2026-10-26 KST · isolated user-authorized development · not a Work OS promotion, not an item-effect fidelity gate and not original v015/v016 product integration.**

## Exact user policy and source constraints

The user confirmed the **highest-quality Thalassian Phoenix Oil** provides **+16 Critical Strike and +16 Haste per actually oiled weapon**. Therefore the declared external fixed vector is:
- neither weapon: `O=(0,0,0,0)`;
- one weapon: `O=(16,16,0,0)`, total32;
- main and offhand dual wield: `O=(32,32,0,0)`, total64.

The approved free optimization target **`T=G+J+F`** remains unchanged; none of the above fixed O values may be added to `gear_*` a second time. External O is shown separately from the optimized `c` and the SimC **actually observed** `buffed_stats`. A shield or offhand frill is not a second actual weapon. Per-item effect/proc behavior, even if not numerically visible in the requested JSON2 field, remains SimC's responsibility; no custom mechanics or proc-support Gate.

External sources: [SimulationCraft official character/consumable syntax](https://github.com/simulationcraft/simc/wiki/Characters) documents class-specific default consumables and `temporary_enchant=disabled`; [current item tooltip](https://www.wowhead.com/item=243734/thalassian-phoenix-oil) says crit+16/haste+16. They are source references, not claims of new independent Native effect certification.

## Critical discovery and historical v090 correction

The v090 two actual Frost Native input profiles omitted `temporary_enchant=` altogether. Inspecting **the previously preserved original v090 actual JSON2 (not inferred)** revealed that both players had `temporary_enchant=main_hand:thalassian_phoenix_oil_2`, owing to inherited SimC class default consumables. Thus v090's **real DPS/candidate inputs/statics remain historically true**, but its prior **“no oil” description is WRONG**. Its declared `O=0` was not an exact reflection of the Native-selected temporary enchant, although core `T=3150` and its `gear_*` inputs are unchanged. This v091 work both records that defect and requires **explicit `temporary_enchant=disabled` whenever zero oil is selected**. Do not silently rewrite old v090 JSON2/receipt or present them as genuine oil-free DPS.

## Implemented source

- `runner/v091_weapon_oil_external_adapter.py`: small opt-in wrapper around **v089 reference → v090 static-c**, no new solver. Confirms source-SHA, exact selected profile, APL/equipment immutable apart from precisely one explicit `temporary_enchant` assignment, and corresponding v061 consumable vector O. Supports `disabled`, `main_hand`, `off_hand` and `main_hand/off_hand`. Declared one-weapon layouts reject offhand oil, dual-wield layouts require actual offhand source slot; no independent item effects/type database. The `dual_two_hand` Native representative's weapon source is the previously validated v082 Fury 2×2H source and exact 16 slots.
- `runner/v064_adaptive_evaluator_port.py`: minimal reuse change: in addition to existing main-only and both, permit offhand-only `temporary_enchant` when the slot exists. Actual offhand **weapon eligibility** is controlled by v091's distinct layout/selected hand policy.
- Uses existing **v090 exact full-source SHA and 16-slot Native gear identity**, **v062 exact selected special L floor**, **v063 static c → gear override**, existing `v064.ingest_native` JSON2/DPS/SEM and revision keyed result cache. The source/profile, oil application vector and selection differ across per-hand cases, so stable cache identity differs. Same frozen T3350 c but different O is not the same DPS case.
- `tests/test_v091_weapon_oil_external_adapter.py` uses actual SHA-pinned v082 Fury and v084 Frost sources to prove: 0 explicit disabled, main only, offhand only, both, unchanged formal T and raw gear stat values, unique case keys, frill and duplicate oil rejection, exact source/APL hash firewall, Native oil string mismatch refusal. No production mode default changed.

## CI results (real, corrections preserved)

**[First Actions #40256980718](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40256980718) FAIL**: 517 unittest cases, **514 PASS / 1 FAIL / 2 SKIP**. Test fixture mutated source with duplicate temporary enchant without re-signing the synthetic source SHA, triggering the *correct existing source-SHA safety guard first*. Test was corrected by recomputing the SHA on intentionally malformed input; production semantics unchanged. **[Retry #40257100232](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40257100232) SUCCESS: 515 PASS / 2 SKIP**.

One final metadata refinement avoids a false blanket conclusion that a single JSON2 proves absence of any numerical oil effect; reporting is now `NOT_ESTABLISHED_FROM_SINGLE_JSON2`. **[Final Actions #40257524161](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40257524161) SUCCESS: total 517, 515 PASS / 2 SKIP**, `pilot.py check` PASS. Artifact `simc-v091-oil-external-static-input-40257524161`, ID **12623381668**, SHA256 **`b2e6fe49886478ba76ebabbd549653e9abf6989f2254c4ca5b3da20dc92e9b29`**, 3 exact source-locked Fury 334 `input.simc` with zero new Native calls *inside GitHub Actions*. Same source profile, target, four gear override numbers; oil token and JSON2 file locations are intentionally distinct. Existing 2 historical skips are old v037 tests needing absent optional v036 fixture, NOT oil-mode tests skipped.

## Three actual Native runs, bounded and SHA-preserved

Pinned SimC binary SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`, revision `7bc10711b5`, existing v082 source-backed Dwarf Fury / 2×2H ilvl334. New Native executions from CI-generated `input.simc`: **3**, one for each 0/1/2 configuration; each **35 requested iterations / 34 DPS samples**. Only `json2` output path changed in local execution relative to original CI candidate input. **All three exit code 0, actual JSON2 report 2.0.0, all 16 gear slot IDs+ilvls+options exactly match each input**, original APL, talents and combat scenario unchanged.

All 3 requested **the SAME static target c=(838,838,837,837), T3350**, with F=(0,165,0,0) and raw gear overrides **(838,673,837,837)**, so O is never injected into the free target a second time.

| Oil placement | Declared O crit/haste (outside T) | Native `temporary_enchant` | DPS, SEM | Native JSON2 SHA |
|---|---|---|---|---|
| Explicit none | 0/0 | `disabled` | **201005.22 ±935.87** | `b41f0fa3f1a990faea549178b516590e50fb0e2c4c2c521993a0e097fde4652d` |
| Main hand only | 16/16 | `main_hand:thalassian_phoenix_oil_2` | **200281.51 ±704.01** | `a745953b8ae37445c95f446428a8e2e85fbf80310d0408a823c633d5b3af4f7a` |
| Both weapons | 32/32 | `main_hand:thalassian_phoenix_oil_2/off_hand:thalassian_phoenix_oil_2` | **200352.41 ±753.25** | `0685cb4bec70ed969e2acfd3cb943cf786b722a83c5022d5778bd735fa6d02dc` |

**Important numerical observation limit:** the `buffed_stats.stats` rating vector in all three Native JSON2 records is identically `(838,838,837,837)`. Thus the actual Native JSON2 **proves the selected oil string was accepted and reported, plus DPS/SEM and exact static-c injection**, but does **NOT independently demonstrate** an extra +16/+16 or +32/+32 in the `buffed_stats` field. Whether this reflects gear override/snapshot accounting or SimC effect handling is **NOT diagnosed here**, respecting the user's explicit instruction to trust SimC rather than create effect support/activation research Gates. **DO NOT present `c+O` as verified buffed JSON2 rating.** The user-facing budget panel may show declared O separately, marked as a fixed item-tooltip contribution rather than observed extra Native rating. These noisy 34-sample DPS differences are not causally interpretable and are not proof oil reduces/increases DPS or which configuration is optimal.

Portable full real Native inputs/JSON2/stderr/stdout/CSV/SHA proof: `V091_WEAPON_OIL_0_1_2_REAL_NATIVE_PROOF.zip`, SHA256 `f7d1e47963f9e62e40e78bcfd8fb7ac792c811cc04bf11f294b283121f7aafc3`, 22 entries. Detailed receipt SHA `b60df6115b469d3f3e417d82e1c61fb0657bb26baf90ddab7090061a3eb41609`; long-term compact GitHub [data receipt](../integration_probes/data/v091_oil_per_weapon_real_native_compact_receipt.json). The actual full 22-entry ZIP is user deliverable, not committed to GitHub.

## Acceptance boundaries and exact next

**v091 input wiring and 0/1/2 hand count, T+O separation, SHA profile/gear, real Native oil setting + DPS/SEM: scoped PASS for Fury 334**, frill refusal tested offline. **Oil +16/+16 effective numerical bonus in JSON2: NOT independently observable / unproven**, and no new effect/proc certification is mandated by approved v1.2. **v090 historical no-oil claim: corrected**.

**Next v092:** reuse already integrated v090/v091 Native request+receipt identity and existing v065 adaptive scheduler (scout→guided→confirmation) to execute bounded multi-candidate search with caching/resume, statistical near-alt selection. Do not launch another season-wide stat sweep, item-effect research Gate or new parallel optimizer. Independently obtain original v015/v016 exact source bytes before claiming final product merge. Continue to record original full source/profile SHA, binary/revision, combat and consumed-oil settings in DPS cache identity. Remain on isolated branch, no GitHub main, official Work OS, Project Sources or immutable v003 changes.
