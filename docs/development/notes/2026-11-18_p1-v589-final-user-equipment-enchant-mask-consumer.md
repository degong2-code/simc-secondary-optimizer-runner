# P1 v589 — actual FINAL user equipment enchant mask consumer (2026-11-18)

## Purpose and user-visible boundary

The product is an **AI-free at runtime** 26-DPS target-ilvl/manual-final-T SimC absolute CHMV optimizer. AI may be used extensively **during development**, but the shipped program must have **no LLM, AI API, external AI service, or inference runtime**. This change adds none.

v588 only compared the reference G representative. This can belong to a DIFFERENT specialization (e.g. the default paladin general G track), so a reference item match can never approve a final user enchant. The first genuine consumer gap was the final `v098` user-selected gear/slot after `common.apply_user_equipment`.

## Minimal CONNECT/FIX (no new engine)

- `runner/v216_environment_build_coordinator.py::_fresh_first_sealed_representative_enchant_mask_preview` now optionally accepts ONE exact internally supplied `selected_user_item={slot,item_id}` and `selected_enchant_id`. It reuses the same v217-sealed v232 representative and v583 Wago↔SimC physical relation, original exact pinned v230 item_data metadata, and v196→v220 class/inventory/subclass/hand predicate. Source SHA/build/revision checks remain. It returns an explicitly **final-user-equipment source-only** result, not a Policy A product_input receipt. If the selected enchant is absent from the sealed v583 physical relation, it returns optional PENDING **before reparsing up to 32 MB item_data.inc**.
- `runner/v098_target_user_scenario_bootstrap.py` passes an **internal Python callable** from the existing `preview_from_environment_build` v216 source owner only when a new-season installed v212 and an already user-selected `selected_season_enchants` exist. `build` calls the pure `_final_user_enchant_source_mask` **AFTER applying user special/crafted gear** but before injecting a selected enchant or writing the runnable SimC manifest. It checks exact current `rows[slot].item_id`, source match, and no accidental `ui_selectable`/Policy A or Native claims. A source-verified **mask/hand mismatch** fails before Native; an optional missing source returns PENDING, preserving the original tightly scoped v528/v529/v531 Native-witnessed 7967/8025/7965 behavior.
- Source-only comparison is attached only to the returned diagnostic result; existing v212 manifest, v096 session/cache identity, G/J/F/O, B/T, L/E/O accounting, oil, 95% statistics, adaptive v290/v291/v293 and SimC-owned effects/DPS remain unchanged. Unenchanted sessions pay no added I/O. A selected and source-linked enchant may incur one bounded v230 read for the exact item; no Wago/DB2/HTTP or SimC Native call is launched.
- **The existing actual executable range is STILL the three exact one-user ring cases.** This does **not** make all v583 additional eight families, other 38 source candidates, or any different spec/item/hand selectable. Highest-quality same-effect/noninferiority, fixed-E scope and generic SimC profile binding are still missing for general publication. Source-mask success is NOT permission to execute an item.

## Focused regression

- `tests/test_v098_target_user_scenario_bootstrap.py::FinalUserEnchantMaskSourceTests`: no selection=no extra source; actual slot and exact item; mismatch and fake Policy A/UI admission fail; optional unavailable source is PENDING.
- Existing `tests/test_v216_environment_build_coordinator.py::FirstSealedEnchantScopeBridgeTests`: original ref item versus DIFFERENT final user item, wrong slot blocked, missing enchant skips second v230 scan.
- Existing offline `.github/workflows/p1_v583_permanent_enchant_source_integration.yml` reuses the original v583/v584/v220/v585/v586/v216 suites and adds ONLY the new v098 test class; no new workflow, Native, or external collection requested.

At documentation time, **do not assert a new full focused PASS count** unless an actual post-change job conclusion/log is retrieved. The earlier v587 104 PASS / 0 FAIL / Native 0 is historical. The v401 78-contract [#44243926082](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44243926082) is SUCCESS on workflow-change HEAD `addb346c02a3342912e354dd4d220bd96b4f80a5`; it is not the focused mask regression itself.

## Next single real product boundary and STOP

For supported physical permanent enchants, reuse original v211/v213 plus actual SimC-spell effect/quality evidence to establish same-effect, same-use, highest-quality/noninferior candidates. For fixed CHMV components only, reuse bounded existing E/accounting and historical Native when same-scope valid. Then use the original v220 four receipt families → v196/v212 publication → v113/v098 executable user selection; **first one verified new selection, not a whole season×26 Native matrix**. Missing optional items remain PENDING and do not block base G/J/F/O. The DK SimC-only runeforge path and Omnium optional module remain separate. No main merge, immutable v003 change, v016 direct integration claim, Project UI/Work OS promotion, primary development chat ownership transfer or 78-element manual promotion.

Official historical state: **15/78 COMPLETE** and `full_product_e2e=PENDING` (not implementation percentage).
