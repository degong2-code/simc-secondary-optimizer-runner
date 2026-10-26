# v092 — User-approved policy promotion and implementation receipt

**2026-10-26** — The user explicitly approved replacing the prior *official* total formula with **`T=G+J+F+O`**, and explicitly authorized Project Sources and Work OS policy updates without asking for another MAIN approval for **this change**. This is a user **policy decision**, not a self-authorizing experimental suggestion.

## Fixed, nonfungible budget

- Preserve `B=G+J+F` as the **underlying optimization allocation budget**, with per-ilvl reference table **unchanged** (334 common `B=3150`, Fury dual 2H `B=3350`).
- `o` fixed per oilable weapon: `(crit=16,haste=16,mastery=0,versatility=0)`.
- Official **final** `T=B+sum(o)`; `c_final=c_base+o`, `sum(c_base)=B`, `sum(c_final)=T`. **Do not make `O` fungible or double-add it to gear ratings.** Retain exact selected special static `L` constraints within B.
- At 334: common no/one/both `3150/3182/3214`; Fury dual-twohand `3350/3382/3414`.
- Existing typed v061/v062, v089/v090 internal fields named `T` or `T_official` **still carry B for backward compatibility**, and must not be presented as new final T. New v092 `approved_total`, `final_T`, `target`, `official_total` in v091 Native request are **the actual new final T**; a manual final T is explicitly mapped through legacy B in the new v092 adapter, not silently reinterpreted.

## Observed real SimC input problem and fix

Prior v091 Native main/both oil selection was accepted as a `temporary_enchant` value but `gear_*` overrides erased numeric oil rating; no-oil and 2-oil `buffed_stats` were identically B. Separately bounded six one-iteration tests proved that without the override, native oil count adds 16 crit and 16 haste per weapon. With adjusted gear values, observed JSON2 crit/haste increased by exactly that count. **No special effect/proc Gate has been added**.

New `runner/v092_approved_inclusive_CHMV_policy.py` is the official central total accounting and Native-input bridge. Existing `v091_weapon_oil_external_adapter.py` calls this after v090's **B-budget floor/cap validation**. In the final result `gear_*_final=gear_*_base+o`, while F attribution is preserved exactly once; recomputes SimC candidate full input SHA and cache case key. Original APL, gear IDs/ilvl/options and profile SHA preserved. The revised v091 Native ingest returns B and inclusive T separately. New user final-manual-total scope: `INCLUDES_G_J_F_O` (converted to legacy B with explicit SHA/scenario normalization).

## Actual CI and Native scope

- Initial [v092 offline CI run #40259913081](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40259913081) **SUCCESS**, **522 PASS / 2 SKIP (524 tests)**. Three exact source-backed Fury 334 input `input.simc` files output at B3350 and final T3350/3382/3414. GitHub Actions artifact `v092-approved-inclusive-total-inputs-40259913081`, ID `12623632220`, SHA256 `1188d55f3ec334f2c81e22871d2b594468e6897c5ee11a60dda8fe33018d73bc`; zero SimC calls in this CI.
- **Independent new actual Native numeric run:** same pinned binary SHA `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e` / SimC rev `7bc10711b5`; 3 × **1 iteration** in local execution, input output-path and iteration count adjusted for numeric-only verification. `none`: JSON2 `(838,838,837,837)` sum3350, explicit `disabled`; `one`: `(854,854,837,837)` sum3382, main-hand oil; `two`: `(870,870,837,837)` sum3414, main+offhand oil. All returncode 0, JSON2 report2.0.0, correct SimC reported enchant settings. This is **numeric input verification**, not a new optimum/DPS superiority claim.
- 2 previous SKIP are old optional v037 source tests with absent local v036 fixture, not v092 skipped tests.

## Formal Project Sources / Work OS application status

The uploaded v1.2 replacement document was labeled **not yet proven applied in ChatGPT Project UI**. User authorizes official promotion, but **there is no verified tool in this chat for mutating Project Sources membership, Project Instructions, or the separate authoritative local Windows Work OS Shared State/CURRENT**. Therefore **do not assert those product surfaces have been updated**. Local **fully revised v1.3 entire Project Source replacement** (not a mere supplement) has been created:

`SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.3_APPROVED_OIL_INCLUSIVE_PROJECT_SOURCE_REPLACEMENT.md`
SHA256: `3dc258d59acd286dc6a2b79755b57712054238d08d5f3c9fd19679b3d6630bc9`.

Official state mutation pending access/actual apply. Do NOT modify v003 immutable or invent Work OS M0 PASS: policy approval does not mean operating Gate was executed. GitHub code/documentation commits in the *isolated branch* are real; direct Project UI/Windows Work OS application is not.

## Exact next (after this approval)

1. Apply/source-replace v1.3 into actual Project Sources and set Project Instructions reference via an authorized Project UI/editor, then record actual verification. For official Work OS Shared State / CURRENT, inspect actual latest file and update only the approved **formula policy**; keep operational Gate status unchanged. **No additional MAIN approval is required for this specific user-approved change.**
2. Complete separate source/CI/Native evidence and update isolated GitHub CURRENT; do not claim original v015-v016 optimizer integration until original bytes are independently available.
3. Ensure any future v092+ adaptive scheduler consumes B for free allocation but reports T and c_final with O locked; preserve existing cache split and SimC effect ownership.

**Approval status: APPROVED. GitHub code status: implemented + scoped CI/Native numeric PASS. Project UI / official Work OS apply: not independently performed/verified.**
