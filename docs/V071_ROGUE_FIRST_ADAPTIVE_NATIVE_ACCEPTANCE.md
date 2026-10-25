# v071 — One authentic v015-guided Subtlety Rogue adaptive Native CHMV scout

**Date:** 2026-10-25 KST. **Authority:** user-applied v1.2 Project Source. Scope is one selected, exact 334 Void Elf Subtlety Rogue profile from user. **No original v015/v016 bytes, Work OS, Project Source, or GitHub main are changed.**

## Existing actual Native evidence reused

- Exact user profile from `runner/v068_rogue_user_profile.py`: `void_elf`, custom `talents=CUQAAAAAAAAAAAAAAAAAAAAAAAgx2MAAAAAwsMGLTMbLjxMjZgZmZGzMbzYGbLzMzMzMjBjZ2GAAAAGMGwYWMMwAzCL0iNMDYmBzYA`; 334 target, head ID `271875` Gaze, main_hand ID `271093` Zatha'tek, crafted off_hand `237837` + `hunters_ritual_stone`, wrists `244576` + `arcanoweave_lining`, 4-slot Rogue tier shoulders `271508` / chest `271513` / hands `271511` / legs `271509`, two fixed trinkets `270175` and `281215`, special gem `240967`, and the named Omnium mastery `rune_of_masterful_cunning`. The SimC original APL is passed, **not recomputed or effect-gated**.
- Prior real Rogue numeric witnesses from [v069 archived run #40181981240](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40181981240) provide two same-profile 35-iteration JSON2 observations and measured offset `(+165 crit,0 haste,0 mastery,0 vers)`. That GitHub run itself is **FAIL** at the later stage; only its separately verified actual native witnesses are reused, never its overall FAIL as PASS.
- Earlier separate full [v070 Native PASS #40182313167](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40182313167) produced **one official-T Rogue seed**: `G=2847,J=138,F=165,T=3150`, locked special-L `(100,201,0,0)`, vector `(813,913,712,712)`, DPS `224891.7284485047` / SEM `1006.0069671134694` / 34 samples, final JSON2 CHMV exact. `G` attribution still has 5 gem/enchant-containing gear rows reported as ambiguous; numeric injection / external oil remain separately scoped.
- This v071 does not re-run either of those three existing Native cases or claim any of those are *global* optimum.

## Actual new v071 implementation / bounded Native

- `runner/v071_rogue_adaptive_first_scout.py`: existing `v069.prepare` rebuilds official P1/P2/P3 from two actual Native witness inputs. New code reads the unchanged v070 official input, receipt and actual JSON2 bytes, validates original SHA, source stable profile/override, iterations 35 and full `v064.ingest_native` JSON2 rating/DPS/SEM. It supplies **only the one real official-T vector** to the existing `v065_v015_scheduler_adapter.initial_state`. Crucially old raw numeric-witness vectors are **NOT** falsely treated as official-T exploration samples.
- Existing v015-derived `next_scout` selects a distinct `100`-rating transfer. It chose **`(713,913,712,812)`** (move 100 crit to versatility), sum 3150 and preserves static L. The new request goes through existing `v064.make_request` profile-bound numeric injection and existing `v065.execute_one` bounded Native/cached executor. **Exactly one new SimC Native call at 35 requested iterations.**
- Native v071 new scout: JSON2 final rating **`(713,913,712,812)`**, DPS **`223167.25452500978`**; SEM **`1185.805253415554`**, samples **34**. Candidate GJF/floor/stat-source/profile constraints PASS. New v071 JSON2 SHA256 **`6db7cad804a2c01bb855d3063b9c3e6f71653d4484d853c380c4a541649b95b4`**.
- Old A vs new B: **new minus old -1724.4739 DPS**, independent-normal approximate 95% CI *halfwidth* **3047.8443 DPS**, statistically **unresolved**; no winner or global optimum, and new scout does not replace 2 fresh high-iteration confirmations.
- In the same successful run, a second CLI call used `--cache-only` and SHA-verified Native receipt: **0 new SimC calls**, correct result, all bytes protected.

## Current independent CI audit

- First [v071 run #40183866776](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40183866776) **FAIL** in new test harness only: mistakenly compared *dummy synthetic* `SIMC_SHA='aaaa...'` with exact production binary `64089f...`. **Zero Native calls**; failure receipt remains.
- Corrected [v071 run #40183940144](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40183940144) **SUCCESS**. **388 current tests run: 386 PASS, 2 SKIP**. Exact source identity, pre-existing witness reuse, new candidate planning, one actual Native, final JSON2, 0-call SHA-verified cache resume all PASS. Historical v015 **71/71** and v016 **104/104** are archival records, **not** rerun.
- Artifact `simc-v071-rogue-one-adaptive-scout-40183940144.zip`: SHA256 `69639148d964dc5f4baf92c30550bce6cd9c4fec6fd46d64bc225c9e93e3200c`, 8 entries, CRC PASS. Contains offline and Native receipts, actual Native JSON2 and exact SimC input, stdout/stderr plus verified native receipt.

## Precisely what's left

**PASS** limited to **one new adaptive scout** for real Rogue scenario and correct exact JSON2 rating. **NOT complete:** complete adaptive exploration, tuned local convergence, fresh 320-iteration or scenario-selected high-iteration confirmations for Rogue, meaningful near-best differentiated alternatives, all-specialization Native acceptance, UI production integration. A fresh two-candidate confirmation and better dynamic iterations need a later separate bounded step; repeated noisy scouts must not be called statistical optimization conclusion.

**Efficiency:** reused 3 prior actual SimC results, 1 new Native call, subsequent cache HIT; no new parser or scheduler duplication, zero item proc/effect internal verification. The original product source/Work OS and season static cache preservation policies remain intact.
