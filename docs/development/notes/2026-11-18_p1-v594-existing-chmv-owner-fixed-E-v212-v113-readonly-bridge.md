# P1 v594 — preserve existing trusted permanent-enchant fixed E across v196 → v212 → v113 (read-only)

Date: 2026-11-18, isolated `probe/chat-cache-v035-20261024`.

## User-approved product scope and STOP

The product finds future target ilvl/default 334 or manual authoritative T **absolute Crit/Haste/Mastery/Versatility ratings** maximizing native SimulationCraft DPS for **26 DPS specs**. It is NOT a current-gear reallocator, equipment recommendation engine, full item database, independent enchant/spell/proc effect simulator, or runtime AI agent. Users select spec/race/talents, trinkets, optional special items, up to two embellishments, verified gems/flask/food/consumables/permanent enchants, weapon oils and combat. Existing `v216/v212` season G/J/F/O, B=G+J+F, T=B+O, manual T, selected L/E/O minima, `v098/v096/v290/v293` original DPS/SEM/95%/cache/cancel/resume remain the sole product execution architecture. **SimC owns effects, proc/spell activation, APL and DPS.** Do not introduce a new effect-activation certification Gate. AI allowed during development, **runtime AI/LLM/model/API dependency strictly prohibited**.

Historical real [v570 one-case Windows Chrome→SimC 64-native E2E](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44074372451) and [v572 real ZIP cancel/resume](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44082378854) remain reusable **scoped** evidence, not re-run here or extrapolated to new enchant/26 specs.

## Actual next P2 gap

Original v593 fixed registration identity for a source-authorized **finger1/finger2** ring family but did NOT provide general user runtime: v196 `prepare_verified_fresh_choices` dropped any **typed fixed E owned by the existing trusted v220 `chmv_budget` receipt**. The v212 published row only retained ID/token/source/quality; v113 could not distinguish an exact proven E from an *absent/unknown* E and correctly displayed a locked registry. **No new proof collection is necessary to preserve a source-owner value already present.** Neither DB absence nor a selected effect spell implies E=0.

## Minimal CONNECT/FIX in existing files

- `runner/v196_current_season_user_catalog.py`: only when all original v220 proof families are eligible **and** the existing highest-quality/use-condition `product_input` is accepted, optional `chmv_budget.fixed_E` (exact four nonnegative integer ratings) is carried as `verified_fixed_E` with the **same existing budget-owner** `evidence_sha256`. Malformed explicitly supplied E is blocked. Absent E remains **absent**; explicit verified zero vector is different from missing. No extra receipt, quality Gate, effect/proc interpreter or Native.
- `runner/v212_environment_manifest.py`: existing prepared and installed option shapes allow precisely the **original historical fields** or original fields plus `verified_fixed_E` and `chmv_budget_receipt_sha256` together, with strict typed vector/sha checks. Existing original v212 manifests without an E field remain valid and unchanged; the original `v212` signed manifest SHA continues to cover any new optional fields.
- `runner/v113_local_web_api.py`: read-only installed policy-A registration projects that exact typed E and receipt hash from **already verified v212** only; it keeps `runtime_selectable=false` and `new_approval_granted=false`. Existing narrow v528-v535 three Survival Hunter ring1 cases are untouched and not generalized.
- `runner/webui/app.js`: installed registration display distinguishes **'고정 E 원본 확인'** from **'고정 E 미확정'**, retaining disabled user choice and no new public admission. Old generic statement that v212 never includes E was corrected.

## Tests/verification boundary

Updated the existing offline suites, without adding a workflow or collecting Native:
- `tests/test_v220_catalog_auto_admission.py`: synthetic trusted four-family receipt + quality source → v196 E shape; absent/zero/malformed states separated, 0 Native/network, no UI publication or independent effect assertion.
- `tests/test_v212_environment_manifest.py`: old option shape and optional typed E + owner SHA; refuses missing paired field, negative, bool, overflow, incomplete vector, invalid SHA.
- `tests/test_v113_local_web_api_offline.py`: existing sealed installed option catalog test now includes old E-absent row AND extra E-bearing row; E appears read-only and runtime disabled.
- `tests/test_v114_local_web_ui_offline.py`: existing actual Node UI suite now checks absent versus proven E text, and that both still disable new user SimC choice. An early test run at [#44256464531](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44256464531) produced **one legitimate expected-text FAIL** after the UI changed; this was fixed in the existing test at commit `17aa0a6da8cf045762b2c4d9b0af1defb82ea063`. Do NOT claim that early CI successful. Recheck the later run for actual all-pass receipts before recording a PASS count.

**No new SimC Native/HTTP/DB2 calls**, no renewed 64 Native baseline, no source DB broad rescan, no new optimizer or runtime AI, no change to baseline G/J/F/O, selected L, Fury G, oils O, manual T, source cache or existing DPS cache identities.

## Remaining product task — not done by this read-only bridge

A generic published v212 option carrying E does **not** yet mean its fixed E is inside/excluded from representative G in the right way for automatic B/T, nor that v113/v106/v098/v096 binds the user's exact finger, physical item, SimC `enchant_id`, user budget floors and durable identity. That connection must use the **same existing installed v212 + trusted CHMV owner**, preserve manual T and add incremental E only once where proven, and reverify the generated original SimC profile **without** inspecting whether SimC actually triggers the spell. New generic UI choices remain locked until the same-scope product runtime is complete. Exact older v529/v531 proofs must not be stretched to all classes/items/seasons without support.

Official 15/78 COMPLETE, `full_product_e2e=PENDING`; policy gate is not completion. Stay on isolated branch; never main merge, mutate immutable v003, claim v016 original integrated, apply Project UI/Work OS or seize ownership from existing main product development chat.
