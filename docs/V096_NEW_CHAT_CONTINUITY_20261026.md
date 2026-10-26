# SIMC SECONDARY OPTIMIZER — v096 new-chat verified continuity (2026-10-26 KST)

> **HISTORICAL SNAPSHOT — DO NOT REUSE AS CURRENT NEXT-P1 INSTRUCTION.** This dated v088/v096 report and its CI/Native evidence are preserved. Later user clarification states that the product optimizes **future target-ilvl CHMV rating goals** with internally generated representative equipment and optional imported SimC character information, **not** users' entire currently equipped gear. The latest base budget may use the native-derived rounded ilvl table or manual final T; exact representative Native G is an optional precise path, not a prerequisite for the standard user entry. See [current user-flow policy](./CURRENT_PRODUCT_PURPOSE_AND_USER_ENTRY_20261026.md) and [current development state](./CURRENT_PRODUCT_DEVELOPMENT_STATE.md). This annotation does not retroactively change historical evidence.

**Purpose:** Resume the same user-authorized product development in a NEW ChatGPT chat inside project SSfindout. **Not** a new branch, a new optimizer, a Work OS M0 pass, or a product release. This file was authored after the original chat hit its length limit. It is not itself an executable validation receipt.

## Exact GitHub baseline

- Repository: `degong2-code/simc-secondary-optimizer-runner`.
- **Isolated development branch:** `probe/chat-cache-v035-20261024`. **Pre-handoff code-state commit:** `acaba244d925bf38a8e84526cf9164d14a914648`. Later commits that only add chat-handoff documents do **not** replace the code-state verification; inspect `git diff`.
- **Protected main:** `07133e0aaf738d6e4816a6486057b1cd49c018de` when checked; do not overwrite/merge without explicit user authorization.
- **Authoritative moving development tracker:** [`docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md`](./CURRENT_PRODUCT_DEVELOPMENT_STATE.md). Read the beginning AND inspect actual code, exact Actions receipt and any conflicting claims. Do not report unobserved tests as verified.
- **v096 development baseline audit:** [`docs/V096_PRODUCT_BASELINE_DRIFT_ROOT_CAUSE_AND_UNIFIED_ENTRY_ACCEPTANCE.md`](./V096_PRODUCT_BASELINE_DRIFT_ROOT_CAUSE_AND_UNIFIED_ENTRY_ACCEPTANCE.md).
- **v096 source:** [`runner/v096_unified_product_entry.py`](../runner/v096_unified_product_entry.py); [`tests/test_v096_unified_product_entry.py`](../tests/test_v096_unified_product_entry.py). They are not a rewrite of existing search, a complete GUI or direct merge of original v015/v016.
- **Last independently confirmed v096 Actions:** [#40271512368](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40271512368) **SUCCESS**, 545 tests = **543 PASS / 2 historical SKIP / 0 FAIL**, existing pilot PASS; **0 fresh Native** in this v096 CI; artifact ID **12628432935**, sha256 `b9dd47bca288f07c32840e9d6ac734f0712cae893986c71c95bcee168917f41f`. Verify any newer run rather than automatically treating it as PASS.
- Core prior real Native proofs: [v095](./V095_95_ONLY_MATERIAL_NEAR_ALTERNATIVE_FIVE_NATIVE_ACCEPTANCE.md) with 5 Native and 5 verified disk-cache hits; v094 4 Native; v093 5 Native; v092 oil0/1/2 exact static rating in native. DO NOT reinterpret these as a new v096 Native proof.

## Critical design and precedence

**User explicitly approved on 2026-10-26** the new *official final* formula **`T=G+J+F+O`**, with legacy base allocation **`B=G+J+F`**, fixed non-fungible `O` included once in `gear_*`, and `c_final=c_base+o`. At ilvl334 common reference B3150 → one weapon oil T3182, both T3214; Fury 2x twohand B3350 → oil2 T3414. Oil per weapon chosen in the bounded test contributes +16 crit/+16 haste. Maintain appropriate special exact static L floors and no duplicate stat injection.

User **settled on 95% confidence ONLY**, and explicitly rejected continued 97% comparison display. Observed mean DPS ranking may prefer higher observed candidate even if 95% superiority is not established. SEM auto-escalation, exhaustive precision or convergence is NOT the immediate milestone.

User approved v1.3 developer-notes *content* and authorized Project Sources/Instructions and official Work OS formula-policy changes without repeating MAIN approval for this specific action. However **actual ChatGPT Project Source v1.3 UI replacement, Project Instructions v1.2→v1.3 edit, and official external Windows Work OS Shared State/CURRENT mutation have NOT been independently applied or verified**. The uploaded portable `SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.3_APPROVED_OIL_INCLUSIVE_PROJECT_SOURCE_REPLACEMENT.md` SHA256 `3dc258d59acd286dc6a2b79755b57712054238d08d5f3c9fd19679b3d6630bc9` is the user-approved replacement text; it includes stale v059/v092 development-history statements. **Treat v1.3 as DESIGN policy only, GitHub CURRENT+actual receipts as DEVELOPMENT status.** Earlier v1.2 is historical except where unaffected policies are inherited. If exact official UI/Work OS bytes cannot be read or modified, say NOT APPLIED; no invented PASS.

The product is a **SimC-controlled absolute CHMV-rating DPS optimizer**, all specs including tank/heal in goal. Not gear or farming recommendation, all-season equipment database or independent item/trinket/oil/embellishment/proc/APL simulator. Our code ensures exact IDs/ilvl/options/combat, fixed L, static G/J/F/O sum, final JSON2 request semantics, candidate search, DPS+SEM, cache and resume. Trinket missing static gear rows are neither interpreted as zero nor used as refusal; representative crafted initial 50:50 is not fixed floor. Preserve same-season static item cache across SimC revision changes (explicit correction only), while DPS cache is source/candidate/SimC/combat/oil scoped.

Operational Work OS `M0_STAT_INJECTION_FEASIBILITY` is a separate *environment* Gate, not a reason to discard validated product code or prevent user-approved normal SimC tests. Preserve v003 immutable, original v015-v016 sources, Github main, existing MAIN/WORK ownership outside the specifically user-approved policy edit. No durable WEQUIP runtime dependency.

## What the prior chat actually accomplished

Existing **real** multiclass/native archetype evidence: v071 Subtlety Rogue; v078 Elemental Shaman (mail, one-hand+shield); v079-v081 + v086 BM Hunter (ranged no offhand; buffed crit talent difference corrected to static-c semantics and random-secondary gear corrected); v082 Fury Warrior (plate dual twohand); v083 Retribution Paladin (plate one twohand); v084 Frost Mage (cloth onehand+frill). Existing typed budget, source-backed SimC APL, selected equipment, static-c candidate, adaptive v015-derived scout, actual JSON2 DPS/SEM and SHA cache were exercised across many, not just Fury. These are bounded tests, NOT every-spec proof. Do not restart multiclass Native testing from scratch.

The latest v096 `runner/v096_unified_product_entry.py` accepts a **single manifest** of exact source profile, typed scenario, fillers, optional static item cache, oil hands/weapon layout, F, two base B targets, binary+rev, calls and output directory; delegates to existing v091/v093/v094/v095. `--plan-only` makes **0 Native**; `--cache-only` uses SHA-verified receipts only. It passed source-backed preflight on actual old Fury (B3350/O64/T3414) and Frost (B3150/O32/T3182) fixtures, with no new Native. It is currently **reference B opt-in**: exact G and user-entered inclusive manual T paths, original product v015/v016 source-byte integration, GUI/one-click end-to-end, entire all-spec production remain open.

## Why the old conversation lost development orientation

1. **Project Instructions reference still pointed at v1.2**, while v1.3 content was approved but not actually applied in project UI.
2. **Developer notes v1.3 status tables are stale static snapshots**, while GitHub CURRENT reached v096; mixing design policy and current progress caused outdated reading.
3. The assistant followed latest single Fury experiment's optional SEM follow-up instead of synthesizing multiple real multiclass Native receipts and product integration.
4. GitHub isolated experiments with PASS were repeatedly conflated with completion/merge of original product v015/v016.
5. The old chat hit its **conversation length limit** while responding; text stopping midstream does not imply code lost. GitHub commit and receipt are truth.

## Exact next step; STOP speculative scope growth

**P1 now:** consolidate previously verified functionality into the actual product user input → approved B/fixed O/final T plus exact gear/combat → existing v015-derived candidate scheduler → SimC DPS/SEM → higher observed candidate & 95% confidence labels → cache/resume → useful output. Use v096 unified entry as starting point and eliminate redundant glue; **do not add new optimizer**. Reconcile original v015/v016 only after obtaining original bytes+receipts; clearly label partial integration. Prefer bounded offline checks and reuse multiclass evidence, new SimC only for a genuinely changed correctness-critical path or missing representative structure. Code review for memory/I-O, duplicate Native, cache and complexity on each change.

**P2:** explicit user manual *final-inclusive* T and exact-G Native path, special crafted L, cancel/progress and Windows one-click flow, using existing v090-v096 code. Preserve user source/role/ilvl controls, all tank/heal roadmap. Do not quietly mutate budget policy.

**P3 later:** deeper fine-grained CHMV search, SEM precision adaptive reruns and broad per-spec production evaluation. 95% remains the sole displayed confidence level.

**For the new chat:** read this file, v1.3 uploaded as attachment or Project Source if truly installed, then GitHub CURRENT, v096 design report, actual v096 code/tests, Actions run, core earlier Native receipts. Report the frozen confirmed baseline before edits, proceed to P1, update GitHub CURRENT with real proofs. Do not request another MAIN approval for the already user-approved oil-inclusive policy and normal product SimC trials. Do not create an extra branch or change main by default.

**No further v096 code changes were made as part of this handoff document.**