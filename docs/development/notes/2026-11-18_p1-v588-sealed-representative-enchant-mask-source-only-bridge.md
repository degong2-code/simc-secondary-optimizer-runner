# P1 v588 — sealed reference equipment v230→v196/v220 first source-only consumer (2026-11-18)

## Purpose and runtime-AI policy

Development may use AI extensively, but the delivered SIMC SECONDARY OPTIMIZER must run with **zero AI/LLM inference, API calls, hosted model services or AI runtime dependencies**. The runtime remains deterministic Python/source + native SimulationCraft. This change introduces no AI feature.

Do not confuse a one-spec **reference G representative** chosen by Environment Build with the **final user-specific equipped representative**. The ordinary Windows initial-season Build can choose a paladin reference (or Fury source track) independent of the user's specialization. Therefore a reference-mask match is **not** user equipment approval or user-visible enchant selection.

## Changed code, narrowly scoped

1. `runner/v196_current_season_user_catalog.py` now exposes `preview_sealed_representative_enchant_mask`, consuming an internal source-origin scope and the pre-existing `v220.selected_equipment_source_mask_match`. It checks exact build/revision, available v213 candidate ID and class/inventory/subclass/slot mask, returns `source_only`, `reference_representative_not_user_equipment=true`, `ui_selectable=false`, `policy_A_product_input_verified=false`, quality and static E unresolved.
2. `runner/v216_environment_build_coordinator.py` reuses the already staged `v232` selected reference slot→ItemID, its v217-sealed original stage receipt/SHA, same-build v583 Wago physical ItemID→SimC ID join, and existing `v230.from_seed` exact item metadata. One bounded exact candidate is passed to v196→v220; a mask mismatch, incomplete source or SHA drift returns **optional PENDING**, not a fabricated receipt or BASE G/J/F/O failure.
3. **Efficiency correction:** the physical `item_data.inc` metadata parsing can read a large same-build source. It is **off by default**; only an explicit internal development/source inspection `fresh_collection_inputs.source_only_reference_enchant_scope_requested=true` enables it. Ordinary user Environment Build does **not** reparse original item data solely for an unselected enchant. No new Wago/HTTP/DB2/Native request and no new automatic registration.
4. Narrow regression cases added to existing `tests/test_v220_catalog_auto_admission.py` (v196 exact ring scope, wrong slot/build/missing ID) and `tests/test_v216_environment_build_coordinator.py` (missing source PENDING, sealed v232/v583/v230→v196 synthetic integration). These test sources do **not** prove current user's final equipment or live Native. No new workflow or required Gate.

### Commit sequence (isolation branch)

- `5f6a7636b095dae1798b62a402d471c34f2359c5` — v196 source-only consumer
- `73091172a7fecf7fbb5acbe92e655573da2fcf10` — v216 sealed reference producer
- `18f65ff0c8409423e3f2dddd4730175d50bfcb1f` — v196 narrow regression
- `c05bcd859426927f7f8bcd7af37da3138f603ed6` — v216 synthetic producer→consumer regression
- `f1c83100747b53557737f73faeac9148561d581c` — explicit opt-in, BASE I/O zero

## Validation identity and remaining blockers

The branch's v401 78-contract combined status on `f1c8310` is SUCCESS ([Actions #44241335673](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44241335673)); the packaged-app regression context is SUCCESS ([#44241335647](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44241335647)). At time of writing, the new v588 focused v583/v216 test job's exact Actions PASS/FAIL receipt has **not** been independently retrieved: **do not claim 108 PASS or all Actions green**. Previously verified v587 [104 PASS/0 FAIL/new Native 0 #44233373988](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44233373988) is **historical, not a v588 re-test**.

This update **does not yet connect the final user's actual equipped profile into the v196 source mask at runtime**, or finish same-effect/highest-quality evidence, exact selected hand, fixed E ownership, all four Policy A families, v212 publication, v113 selectable options, native user DPS or full product E2E. The additional v583 eight families are still source-only and excluded from the original `enchant_` v196 catalog. Do not turn the optional reference preview into an executable option.

**Next required consumer:** identify the final user's exact representative item after v098 equipment application, reuse same-build v230 provenance to compare selected enchant/slot/hand, then reuse original v220 evidence families and v196→v212→v113 publisher. Only one real selected case first; no blanket enchant×26 DPS Native. Fixed C/H/M/V E alone needs existing bounded E accounting or measurement. SimC owns effects/procs/APL/DPS. Stop after the first genuinely usable approved choice and minimum changed-path validation.

ZERO-SOURCE v567/v570 and v290/v291/v293 scheduler, oil/manual T, historical E Native/95%/cache/restore remain intact and are not newly retested here. Official 78 status remains `15/78 COMPLETE`, `full_product_e2e=PENDING`. No main merge, v003/v016 immutable edit, Project UI/Work OS promotion, or primary development chat ownership transfer.
