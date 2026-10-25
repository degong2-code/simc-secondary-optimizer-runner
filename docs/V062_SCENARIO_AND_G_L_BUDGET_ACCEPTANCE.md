# v061–v062 — General Scenario Contract and Static Native Budget Evidence

**Date:** 2026-10-25; **status:** isolated-branch development PASS, original v015/v016 product merge **not verified**. User confirmed applying Developer Notes **v1.2** and updated Project Instructions. Continue development **in the same chat**.

## v061 P1 generic input contract

- `runner/v061_scenario_contract.py`: class/spec/race/talents/role, profile source, target ilvl or explicit **manual T inclusive of J/F**, four selected tier pieces, two trinkets, up to two crafted embellishments, special user-selected gear, combat setting and bound-iteration budget, full scenario identity hash and revision-sensitive DPS-result identity.
- Unlike v059, native G is **not fabricated** from hard-coded Mage numbers. For target ilvl, `T` stays null pending exact representative gear static G. User manual T is not silently incremented by J/F again.
- **Official v1.2 policy**: `T=G+J+F`, temporary oil fixed rating is **outside official T**, separately passed to SimC. The earlier v059 `G+J+F+O` is a pilot and must not become global policy.
- Selected items passed with exact ID/level/options; supports manual item IDs beyond catalog. SimC owns effects, unique-equipped rules and DPS; the contract checks only physical slot collisions and input shape.
- [v061 first FAIL #40162112120](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40162112120): one test failed because embellishment-on-special returned aggregate count error before specific wrong placement. Recorded as actual FAIL.
- [v061 corrected PASS #40162193520](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40162193520): **277 PASS / 2 SKIP**, 279 tests; 2 canonical portable scenario inputs generated; **0 new Native SimC calls**.

## v062 P2 representative static G/fixed special L

- `runner/v062_static_budget_bridge.py` consumes normalized v061 scenario and explicit remaining 13 essential non-trinket equipment slots, with `main_hand`, optional `off_hand`; no equipment search or auto fill.
- Uses **only exact cached season+item+ilevel+normalized slot+options Native static variants**; missing entries trigger `NEEDS_NATIVE_G_FOR_DERIVED_TARGET` or `NEEDS_NATIVE_SPECIAL_FIXED_L`, not a fabricated 0 or effect-missing claim.
- Special non-trinket L is included in G **once** and locked to each stat, crafted initial 50:50 stat distribution **not locked**. Trinkets are outside G; absent static trinket record **never prevents selection**. Manual T can still progress without complete ordinary G when selected special L is known.
- Native per-gear gem/enchant numeric attribution remains marked for **P3 final JSON2 rating reconciliation**. No proc inspection.
- [v062 offline CI #40162455726](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40162455726): 293 tests **291 PASS / 2 SKIP**, 0 SimC calls. Illustrative `G=1300,T=1603` in CI is a **synthetic fixture, not real gear stats**.

## P2 REAL Native cache reconciliation — no new SimC calls

Existing portable full-season static cache before: **455 catalog IDs, 1759 exact variants**. Existing v059 actual Native JSON2 `case_00/result.json` contains one missing exact head variant (`item_id 271564`, ilvl 334, `gem_id=240967`), while the other 13 emitted JSON2 gear static variants are exact-cache matches; omitted `Mindpiercer's Sigil` trinket1 is **unknown, not proven 0**. Merge:
- 1 new Native variant, 13 reused, 0 overwrite/correction, **1760 exact static variants**, 455 catalog IDs unchanged, 0 new SimC executions.
- Selected actual full 334 Arcane Mage gear non-trinket G from real JSON2 equals exact summed new cache G: **2849** (crit 675 / haste 1034 / mastery 862 / versatility 278).
- Official static budget **arithmetic** for this specific profile: `T=G2849+J138+F165=3152`; external pilot oil `16 crit+16 haste=32` is **not in this official T**. This is **not yet final full-scenario CHMV injection parity**. v059 pilot T=3184 is distinct.
- Portable proof: `SIMC_v062_REAL_NATIVE_CACHE_RECONCILIATION_RECEIPT.json`, `midnight_s2_static_cache_v062_native_reconciled.json` and append-only reproducibility script in `SIMC_SECONDARY_OPTIMIZER_v061_v062_DEVELOPMENT_EVIDENCE.zip`, with SHA/CRC checks.

## Now exact next

1. P3: code a **small numeric injection adapter** for the official `T=G+J+F`, external trinket/oil/enchantment terms and the selected 334 Mage scenario. Use **existing Native JSON2 baseline** to calculate accountable injection offsets, not derived proc behavior. Run bounded 1–2 SimC DPS candidates; compare final JSON2 static target and DPS/SEM. Do not silently reuse v059 pilot oil-inclusive injection coefficients as general facts.
2. Continue generalization to other class/spec/ilvl using scoped representative gear/static Native cache. An actual selected special L must be exact Native static, with no improvised scaling.
3. Locate/verify actual original `v015`–`v016_SCENARIO_CONTRACT` product source and receipt before claiming mainline product merge. Its absence does not prevent isolated development.
4. Reuse existing adaptive engine (once proven) for scout/guided/confirm, result caching, statistical alternatives, resume/cancel/UI. No item proc gates, no WEQUIP runtime dependency.

**No MAIN / Work OS / Project Source modifications.** The user separately applied v1.2 official docs; these experimental code changes are still isolated and do not promote product implementation.
