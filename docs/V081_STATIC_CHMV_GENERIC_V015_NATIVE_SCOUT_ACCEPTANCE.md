# v081 — Real static CHMV v066 preflight + v015-derived single Native scout

**2026-10-26 KST. Isolated branch development evidence, NOT original v015/v016 product integration or Work OS promotion.**

## Approval and numeric boundary

The authoritative user-approved Developer Notes v1.2 sections 5.1–5.5 distinguish optimization target `c` (static CHMV) from SimC observed buffed JSON2; official `T=G+J+F`; oil O is **external fixed**, not silently added. We do not inspect or model specific traits/talents/proc behavior. SimC owns game effects, APL and DPS. User requests **DPS-only short term test scope**, with conflict against existing approved all-role policy explicitly retained.

The v080 two actual Troll BM Hunter static-target Native results are authoritative *for this exact profile only*:
- profile: Troll Beast Mastery Hunter, ilvl334, mail, ranged mainhand, **no offhand**; source-based MID2 SimC APL preserved;
- `G=2494`, `J=138`, explicitly declared local test flask `F=(0,165,0,0)`; `T=2797`. The F vector is **caller-supplied and bound**, not independently verified as universal flask attribution.
- first source JSON2 SHA256 `74a8cdcd3cd4a8e8fced5595a2f218b3b36248db05d9a817268f3b464cc8ce9f`;
- second source JSON2 SHA256 `c3c4bf8ef49744d21c4478fb890a419bfd712b5cc0f0515f55a0c2d28b7ec4f1`.
- parent: [v080 real Native Actions run 40204450655](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40204450655), successfully validated *static c* distinct from talent-inflated `buffed_stats`.

## v081 implemented changes and actual proof

Changes in shared components, no per-Hunter search algorithm:
1. `v066.prepare_static` validates official exact nontrinket Native static G, source/profile item/option identity and SHA, explicit F vector sum, 2 **actual** independent static-c witnesses with original SimC input and JSON2 bytes/SHA, Native revision, and both targets' exact raw injection replay. It does NOT require observed buffed_stats to equal target c; returns `READY_STATIC_CHMV_PROFILE_SCOPED`.
2. `v066.propose_next_static` directly calls existing `v065_v015_scheduler_adapter.initial_state` / `next_scout`; no duplicated scheduler. Shared v065 scheduler now accepts typed `PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT` rows and selects existing v015-local-mirror neighbor order, enforcing no mixed static and legacy-buffed observational status in proposals and scout acceptance. Historical legacy behavior and fixed-offset-mode cache keys are unchanged.
3. `v081_static_generic_scout_native.py` replays both exact v080 static Native inputs/JSON2 SHA and derives exact static G from Native gear; creates one unseen static-c target, runs at most **ONE** new 35-iteration SimC Native through unmodified v065 executable bridge and v064 typed static-c JSON2 evaluator. Caches are SHA checked and replayed without additional Native calls.
4. Regression tests cover source APL preservation, rejection without real historic Native data, prevention of legacy/static mixing, rejection of unverified static parity and missing exact static G.

[Actions run **40207117543**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40207117543): **SUCCESS**, trigger commit `9a6d7a2bbc263617086013a5623b77792b5bdda3`. Python **462 tests: 460 PASS / 2 SKIP**. Native binary exact SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`, revision `7bc10711b5`.

**New, actual Native scout (35 iterations, 34 DPS samples):**
- static target c: **crit 500, haste 899, mastery 699, vers 699**, total **T2797**;
- SimC injected `gear_*` (G+J): **crit 500, haste 734, mastery 699, vers 699**, total 2632; caller-declared F haste +165 once;
- actually observed Native JSON2 `buffed_stats`: **crit 520, haste 899, mastery 699, vers 699**. Buffed crit +20 retained, NOT inverse-corrected from the controllable static c;
- actual Native DPS **193739.46383180816**, SEM **627.425531493758**, samples **34**;
- new JSON2 SHA256 `1074ece9f3911b547368d427fb43595448513bfe13b990a9d5a545fc12aae11e`;
- v066 `READY_STATIC_CHMV_PROFILE_SCOPED`, v015-local-mirror candidate accepted via unmodified policy/ordering; scout completion 1/2 allowed by policy. It is a *scout* not a proven best or global optimum.
- cache replay 1/1 SHA **PASS, zero further SimC**; durable Native attempts total 1.

Output artifact: `simc-v081-static-generic-v015-native-40207117543`, GitHub artifact ID **12604810119**, provider-reported SHA256 `8aa200e26ac01f1dfe298a9845555d4a4be37dc9dfaf0517e7f5b96e9880b415`. Metadata verified; no independent ZIP download CRC claim.

## What is and is not done

**DONE in isolated scope:** Static CHMV candidate semantics now propagate from v061/v062 through **shared v063/v064 + v066 preflight + v065-v015-guided candidate selection and native execution**; two genuine prior Native source JSON2 anchors and one new actual Native scout prove the path in the single Hunter profile; F is deducted once; buffed stats can differ; cache repeat costs 0 Native.

**NOT DONE / not implied:** other real class/armor/weapon variations; generalized consumable F vector selection and attribution for every user setting; oil O external fixed vector integration; the main v015/v016 original product source integration and UI; full scenario season item ID generation; global optimum or confirmed near-best. No expansion into gear recommendation or effect certificate gates.

**Next bounded work:** with this common static-c path proven, select the next orthogonal physical coverage — **Dwarf Fury Warrior, plate, main+offhand TWO TWO-HANDED weapons** — preserving original SimC APL and exact item ID/options and making only bounded Native calls. Avoid writing a new Fury-specific optimizer; reuse v081 static-c preflight/policy with an explicit observed or user-declared F vector. Keep GJF budget/O policy untouched and report whether F vector is merely declared or actually known from authoritative input.

All source edits and receipts are confined to isolated branch `probe/chat-cache-v035-20261024`; GitHub main, immutable v003, original v015/v016, official Work OS, Project Sources and shared state remain unchanged.
