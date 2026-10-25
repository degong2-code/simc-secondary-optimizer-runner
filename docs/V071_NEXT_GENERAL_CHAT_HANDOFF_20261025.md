# SIMC SECONDARY OPTIMIZER — v071 → Next General Chat GitHub-only Handoff

**Prepared:** 2026-10-25 KST.  
**Purpose:** A newly opened **ordinary ChatGPT chat inside the same SSfindout Project** takes over the **main product development work** because the prior chat reached its maximum length. This is **explicit user-authorized chat migration**. No ZIP transfer or Work mode switch is required if the ChatGPT GitHub connection remains available.

> This file is a **portable development handoff**, not a Work OS update, a Project Source replacement, production merge, policy promotion, SimC result, or permission to edit GitHub \`main\`.

## 1. Authoritative policy; read before implementation

- Source of authority: Project Sources / uploaded full \`SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.2_PROJECT_SOURCE_REPLACEMENT.md\`, already confirmed applied by the user in the Project context. Read it **in full** in the new chat. The file originally described v059 as the then-current GitHub state; **that historical paragraph is superseded on development progress (not on policy) by current branch receipts up to v071**.
- Official goal: optimize the **absolute rating** vector CHMV (critical strike / haste / mastery / versatility) that maximizes **DPS**, for all specializations including tanks/healers, default target ilvl **334**, reporting DPS, SEM, percentages, and truly different near-best alternatives. Do NOT turn this into equipment combinations, item recommendation/farming, or comprehensive season gear/recipe database.
- Official budget is **T=G+J+F** (typical 6 standard gems J=138; F=165 in current proven profiles but NOT indiscriminately for every scenario). No \`+O\` oil in the official T without explicit new approval. For special item locked vector L, L is already inside G and is not added twice. Trinket static secondary stays **outside G**, not silently 0 if JSON2 lacks static trinket record. Crafted 50:50 starting secondary split is NOT a fixed floor.
- SimC owns all item/trinket/embellishment/gem effects, procs, APL and DPS. Our software owns exact IDs, levels, options, stable combat conditions, static CHMV budget, locked floors, input-to-final JSON2 numeric reconciliation, bounded adaptive search, DPS/SEM, caching and resume. No separate item-effect/proc implementation, gate or certification.
- Same-season static item variant cache must NOT be automatically discarded for a SimC revision change; exact-key DPS cache IS revision/input/scenario-sensitive. Every code change must evaluate runtime, SimC calls, duplicate work, cache, memory, I/O and simplicity.
- User-reported source-product baseline v016 is distinct from GitHub-isolated experiments and later actual test proofs. Original v015/v016 archived bytes were separately verified in the prior chat (37/37 outer manifest SHA/size, 4 internal ZIPs). Historical **v015 71/71** and **v016 104/104** are original OFFLINE historical receipts, NOT current tests. Never modify original source bytes; do not misrepresent GitHub adapter as full original executable integration.
- Protected authority: leave GitHub \`main\`, official Project Instructions/Sources, Work OS \`CURRENT\` / Shared State, \`v003\` immutable and MAIN/WORK official M0 alone unless independently authorized by the original contract. Work OS M0 does NOT block normal user-approved product SimC tests. No permanent WEQUIP operating/runtime authority.

## 2. GitHub restore coordinates (single source of development evidence)

- Repo: **\`degong2-code/simc-secondary-optimizer-runner\`**.
- Isolated product-development branch: **\`probe/chat-cache-v035-20261024\`**.
- Last pre-handoff, independently observed HEAD: **\`2bfc4f076d72407034f6c792021e52165602d8e8\`**. Re-query branch HEAD on entry (this handoff doc creation itself advances it).
- GitHub \`main\` observed at handoff: **\`07133e0aaf738d6e4816a6486057b1cd49c018de\`**, untouched by this work.
- First read **\`docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md\`** (latest top section v071); then **\`docs/V071_ROGUE_FIRST_ADAPTIVE_NATIVE_ACCEPTANCE.md\`**; then **\`docs/V068_USER_INPUT_UX_DECISIONS_20261025.md\`** and **\`docs/V067_GENERIC_PREPARED_ADAPTIVE_ROUTE_ACCEPTANCE.md\`** as needed. This file is the stable handoff map, not a replacement for source code.
- Read exact actual workflow implementation: \`.github/workflows/v071_rogue_first_adaptive_native.yml\`; and sources \`runner/v068_rogue_user_profile.py\`, \`runner/v068_rogue_two_native_probe.py\`, \`runner/v069_rogue_official_budget_native.py\`, \`runner/v071_rogue_adaptive_first_scout.py\`.
- Reuse rather than duplicate: \`runner/v061_scenario_contract.py\`, \`runner/v062_static_budget_bridge.py\`, \`runner/v063_numeric_injection.py\`, \`runner/v064_adaptive_evaluator_port.py\`, \`runner/v065_v015_scheduler_adapter.py\`, \`runner/v065_original_scheduler_native_bridge.py\`, \`runner/v066_profile_neutral_preflight.py\`, \`runner/v067_generic_adaptive_native_route.py\`.
- No full season equipment recommendation DB and no new independent SimC-effects preflight.

## 3. User-selected real validation scenario (ALL inputs already collected)

Keep this exact user selection; **do not ask user to re-enter it**:

| Setting | User selected | Observed real SimC fixture |
|---|---|---|
| Class / spec | Rogue / Subtlety | \`rogue\` / \`subtlety\` |
| Race | Void Elf | \`void_elf\` |
| Target ilvl | **334** | Representative scenario |
| Custom talent string | \`CUQAAAAAAAAAAAAAAAAAAAAAAAgx2MAAAAAwsMGLTMbLjxMjZgZmZGzMbzYGbLzMzMzMjBjZ2GAAAAGMGwYWMMwAzCL0iNMDYmBzYA\` | Preserve exactly |
| Trinket 1 | Voracious Heart of Ula'tek | ID **270175** |
| Trinket 2 | Twisted Horror's Tendril | ID **281215** |
| Embellishment 1 | Hunter's Ritual Stone | \`hunters_ritual_stone\` on crafted **off_hand ID 237837** |
| Embellishment 2 | Arcanoweave Lining | \`arcanoweave_lining\` on crafted **wrists ID 244576** |
| Selected special weapon | Zatha'tek, Breath of Corruption | **main_hand ID 271093** |
| Selected special armor | Gaze of the Coiled Watcher | **head ID 271875** |
| 4-set tier | Default with head replaced by selected special | shoulders **271508**, chest **271513**, hands **271511**, legs **271509** |
| Omnium tome | **4th UI column: Mastery** | SimC name \`rune_of_masterful_cunning\`; don't assume 4th UI column = \`split('/')[3]\` without mapping |
| Special gem | Type B | ID **240967**, real gem color/equipment options preserved |
| Fight | Patchwerk, 1 target, **300s**, raid buffs ON | Other options per actual valid fixture |

Authentic source fixture: \`runner/v068_rogue_user_profile.py\` with SHA-pinned upstream Rogue APL fixture \`integration_probes/fixtures/v068_upstream_mid2_rogue_subtlety_reference.simc\`. User should not need to pick ordinary equipment slots. Input interface UX: **two embellishments selected independently, default 2**, **two separate trinkets**, **Omnium 4th column CHMV chosen by user**; specialized source choice held fixed throughout optimization. Specialized crafting IDs are representative effect-carrier equipment, NOT a gear recommendation optimization.

## 4. Exact real Native proof, status and statistical interpretation

1. **v068**: [Actions #40181018874](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40181018874) SUCCESS for actual user Rogue profile two Native witnesses (see actual receipts).
2. **v069 numeric witnesses**: [Actions #40181981240](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40181981240) overall **FAIL at a later step**, BUT preserved two **individually independently checked actual 35-iteration SimC JSON2 numeric observations** are reused. Never relabel whole run PASS.
3. **v070 official target**: [Actions #40182313167](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40182313167) **SUCCESS**. Numeric calibration from real same-profile observations **offset (+165 crit, 0 haste, 0 mastery, 0 vers)**. Official static budget **G=2847, J=138, F=165, T=3150**. Locked special L=(100 crit,201 haste,0 mastery,0 vers). Candidate CHMV=(**813,913,712,712**). Exact 3150 final JSON2 rating PASS, DPS **224891.7284485047**, SEM **1006.0069671134694**, 34 samples.
4. **v071 current latest**: [Actions #40183940144](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40183940144) **SUCCESS**. **388 tests: 386 PASS, 2 SKIP**. Reuses three old actual Native cases (two numeric witnesses + v070 official target), **one and only one new** v015-derived candidate selected by existing v065 scheduler: move 100 crit→vers, CHMV=(**713,913,712,812**), T=3150, exact final JSON2 rating PASS; DPS **223167.25452500978**, SEM **1185.805253415554**, 34 samples. New Native JSON2 SHA256 **\`6db7cad804a2c01bb855d3063b9c3e6f71653d4484d853c380c4a541649b95b4\`**. Exact receipt SHA-verified cache replay PASS **0 additional Native calls**.
5. Candidate comparison: new-minus-original DPS **−1724.4739**, normal-approx independent 95% difference CI halfwidth **3047.8443**. **No statistically established winner**, no converged global optimum; 35-iteration scout is noisy. Do NOT report v071 as completed optimization, finished best stats or meaningful near-best alternatives. Full two-candidate high-iteration confirmation still pending.
6. Historical CI [v071 #40183866776](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40183866776) **FAIL** because a new synthetic test compared dummy binary SHA to actual fixed binary hash; Native **0**. Preserve this failure evidence instead of erasing it.
7. Artifact \`simc-v071-rogue-one-adaptive-scout-40183940144\`, artifact ID **12595416186** (at handoff **not expired**), ZIP SHA256 **\`69639148d964dc5f4baf92c30550bce6cd9c4fec6fd46d64bc225c9e93e3200c\`**, 8 entries CRC PASS according to acceptance. v070 artifact ID **12594143931**, digest \`549ce2ec61ee7ae9b25cfc426526b901b9a50036959212cb774661a8c364e0ed\`, not expired at handoff. Download from Actions as needed and recheck exact bytes/JSON2 before new claims.
8. Pinned test Linux SimC binary SHA256 **\`64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e\`**. Do not assume that version-independent cache behavior applies to DPS.

## 5. What is real, what is incomplete

**Proven:** One real Subtlety Rogue exact selected-item Native profile; two same-profile numeric witnesses and official P1–P3 budget/calibration; one official baseline DPS; one *new* v015-derived adaptive Native scout; exact CHMV JSON2 matching; one-case verified cache reuse. Previous Arcane Mage Native adaptive 2 scouts + 2 fresh confirmations and profile-neutral adapter paths were also proven in earlier, *different* runs.

**Unproven/not done:** High-repeat independent confirmation for BOTH Rogue candidates; full adaptive optimization, broader candidate exploration, well-separated near-best DPS alternatives and rigorous convergence; other classes/tank/healer real Native; full general UI and end-to-end arbitrary new user scenario assembly; individual gem/enchant numeric source split for **5 native static gear rows**; global optimum. Oil fixed rating stays **outside T**. No missing trinket static record counted as 0. Never conflate historical v016 report with fully integrated original product.

## 6. The FIRST concrete next work in new general chat — v072

**Continue product development, not merely summarize.**

- Re-check GitHub current HEAD, v071 \`CURRENT\` and code; verify exact v069/v070/v071 artifacts/receipts and pin same SimC revision.
- **Implement a small, bounded, durable v072 2-candidate FRESH HIGH-ITERATION Native confirmation** for *exactly* the two **3150** Rogue vectors (813/913/712/712 and 713/913/712/812), while preserving exact existing user profile, item IDs/options, Omnium mastery, gems, combat scenario and cached prior scouts. Use an existing v065/v064 evaluator + existing calibrated v069 profile. Use **at most 2 new Native candidate evaluations** and appropriately higher scenario-consistent iterations (e.g. 320 only after verifying actual runtime policy and source/profile cache identity; don't silently break v061/v064 checks). This is a suggested bounded next task, not prior PASS.
- Return rating / DPS / SEM / samples / differences / approximate statistical uncertainty, explicitly distinguish observation from supported winner; if uncertain leave tie unresolved. Preserve full JSON2, source input, stderr/stdout, SHA provenance, budget and scenario identities, bounded retry/cache and cancellation.
- Then iteratively expand adaptive search and genuinely different near-best alternatives using the **same v065 policy** rather than implementing a third scheduler. Avoid broad/prohibitively expensive multi-class Native runs until one exact end-to-end contract works. Move to general spec bootstrap afterward.
- Optimize total Native calls, reuse caches, avoid extra effect validation and duplicate parsers/engine. Tests/CI PASS and actual Native PASS are different evidence categories.
- Keep implementation confined to isolated branch; update only **product-development documentation** on that branch (e.g. \`docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md\`) with demonstrated results and exact next step; do not modify official Work OS shared state, original immutable files, main, or project sources.

## 7. Safe migration rules

- User's previous directive “stay in current primary product development chat” is NOW explicitly superseded **only for the chat session location** because the old chat hit its size limit. This new general chat inside SSfindout is the owner for continuing ordinary product implementation/tests. This is NOT a transfer of Work OS MAIN/WORK authority.
- Do **not** demand that the user reattach the old ZIP, repeat the already supplied scenario, manually rebuild the local Windows environment, switch to Work mode, or obtain repeated MAIN authorization for already user-approved ordinary product SimC tests. GitHub connection + Project Source v1.2 + this handoff + actual Actions suffice. If GitHub is temporarily inaccessible, state that specifically and use any available user-supplied fallback evidence; do not fabricate verification.
- If a new chat's Project Source v1.2 is accessible but says \`v059\` in historical header, treat that as the dated document's report, **not** a rollback from newer receipts. Never silently alter official formula or user decisions.
- Respect full original v015/v016 ZIP immutability. Native effect/APl/proc success is SimC's responsibility; capture SimC actual errors exactly if encountered.
- Reporting: state precise PASS/FAIL/boundaries, historical vs reexecuted, expected user action (often none), and next bounded task. Prefer less SimC with reproducible quantitative evidence.

**Handoff integrity record:** At authoring, independently read repository current state (v071) and verified actual GitHub Actions status/artifact metadata; this handoff document itself contains no new Native execution. The original user-supplied progress text states v071 head \`2bfc4f07\`, which matched the GitHub branch before this documentation commit. This document exists solely to let the next chat resume quickly.
