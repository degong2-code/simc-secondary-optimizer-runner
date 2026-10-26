# v089 — Opt-in S2 per-ilvl CHMV budget selector, native/exact/manual legacy preserved

**Date:** 2026-10-26 KST. **Scope:** isolated product-development adapter and regression, not original v015/v016 product integration or official Work OS gate/promotion.

## Task and policy

User approved reference table for common specs and dual-two-hand Titan's Grip Fury Warrior; default 334 anchors respectively 3150/3350. User manual total must override table. 5–10 rating representative deltas are acceptable. Preserve original approved formula **T=G+J+F** and keep per-oiled-weapon fixed O **OUTSIDE T**. Special fixed CHMV L requires source-backed exact Native input, is already inside T and must not be invented or added a second time. SimC owns all item/APL/proc/combat mechanisms.

## Actual implementation

1. `runner/v089_ilvl_chmv_budget_selector.py` provides **one small opt-in adapter**, no parallel optimizer, no new item database or SimC work. It reads existing proven source table `integration_probes/data/midnight_s2_ilvl_chmv_reference_v1.json` and validates schema, season, approved GJF/J138/F165 semantics, 79 ordered 266..344 integer rows, rounding, monotonicity and 334 native-based anchors. Unsupported ilvl **blocks**, no linear extrapolation.
2. The caller chooses `mode="reference_rounded_opt_in"` explicitly, or leaves original `mode="exact_native_G"`. `weapon_layout` is explicitly supplied (e.g. one_hand_frill, ranged, single_two_hand, dual_one_hand, dual_two_hand). Fury `class=warrior, spec=fury` requires explicit **dual_two_hand** to select its independent table; other specs cannot silently use Fury dual-2H budget. Caller layout remains **caller-declared**, not separately proven from Native weapon IDs by this adapter.
3. **Actual user `target.mode="manual_total"` takes priority** without even reading the reference file, retains exact total and v061 scope `INCLUDES_G_J_F_EXCLUDES_EXTERNAL`.
4. A reference-mode derived-ilvl scenario is **copied** to an effective v061 **manual_total target** set to the rounded reference T, then re-normalized using existing scenario validations and hash. This is a deliberate **adapter encoding** of the table value, *not* a claim that the user manually supplied it; provenance states `source_mode=reference_rounded_opt_in`, reference-row SHA and `READY_OPT_IN_REFERENCE_TOTAL_NOT_FULL_P3`. Original `v061.py` and `v062.py` were **NOT edited**.
5. The output includes normalized typed scenario plan, ref SHA, selected track, T, explicit O unchanged, and special L required marker. No product mode defaults or formula changes. Reference guard also rejects non-v087 J/F combination, so hypothetical other consumable budgets cannot be silently treated as verified equivalent.

## Exact scope of testing and results

[First v089 Actions run #40252986059](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40252986059): **FAIL**, full regression **502 tests: 499 PASS / 1 FAIL / 2 SKIP**, Native **zero**. Newly added malformed-registry test attempted to trigger the `REFERENCE_STATS_NOT_MONOTONIC` safeguard using `3`, which violates the separate “nearest ten” validator before the monotonic check; the safe reject behavior itself worked. Fixed **test fixture only** from `3` to `3000`, keeping 10-rating granularity while violating actual monotonicity, without changing production logic or original v087 reference.

[Corrected v089 Actions run #40253087237](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40253087237) **SUCCESS**: full suite **502 tests: 500 PASS / 2 SKIP**, `runner/pilot.py check` PASS, exact source/test/table git object hashes pinned and verified, and 8 real typed-scenario receipts emitted at ilvl **266/321/334/344 × common/Fury**. Native calls **0** in both runs. Output artifact **`simc-v089-ilevel-budget-selector-40253087237`**, artifact ID **12621009482**, provider SHA256 **`19b704ce841323c929e794ebc91fc57f6a43f2e706f4febd50ea12f3dcda1f7e`**.

New tests include: common 334 T3150 with single-oil O16/16 outside T; Fury 334 T3350 and Fury321 T3170 vs common321 T2980 (difference 190 rather than a hardcoded +200); user manual 3000 precedence with missing reference; original exact G mode remains WAIT_NATIVE_G; 265/345 fail; wrong Fury geometry fail; J/F drift fail; corrupted registry anchor and monotonicity separately fail; exact special L170 from selected Native cache persists while ordinary G is unknown, missing special is never fabricated; absent trinket static output remains nonblocking.

## Limitation and next step

**This is S1 input-budget selection acceptance, NOT full P3 SimC static-c candidate evaluation with ordinary item G cache missing.** The original v062 still exposes `missing_nontrinket_static`; original v063/v064/v066 full Native preflight enforces stricter completeness before SimC P3. It is technically correct to say **typed reference T resolved** and **special L preserved**, but NOT yet truthful to say “the reference-only profile runs full adaptive DPS without needing ordinary gear G”. Achieving user's intended lightweight baseline requires a *separate minimal compatible budget/exact-identity adapter* for reference T that carries exact all-slot ID/level/options and exact selected L, without treating unknown ordinary CHMV as 0 in gear records, and targeted Native static-c parity. Preserve v062 exact G mode, v003 and v015/v016 lineage.

Also open: user's separately clarified selected weapon oil per weapon **O=(16crit,16haste,0,0)** one hand, **O=(32,32,0,0)** two genuinely oiled weapons, **0** none. The existing v061 policy and v064 temporary enchant string check are present; full numeric 0/1/2 weapon/oil applicability, cache and Native validation are NOT claimed by v089. Shield/frill do not count as second weapons.

No changes to main, official Project Sources/Work OS/Shared State, immutable v003, original product v015/v016; original v016 source bytes still not independently integrated. The current primary product chat retains ownership; this document is an optional future general-chat continuity record.
