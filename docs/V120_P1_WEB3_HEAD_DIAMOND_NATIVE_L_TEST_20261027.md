# P1-WEB-3 v120 — Windows 50-test failure, selected-head diamond fixed-L static provenance

2026-10-27 · isolated `probe/chat-cache-v035-20261024` only.

## Evidence from actual company Windows test

User ran:
```powershell
py -3 -m unittest -q tests.test_v098_target_user_scenario_bootstrap tests.test_v101_common_representative_equipment tests.test_v114_local_web_ui_offline
```
Observed **Ran 50 tests in 2.184s / FAILED (failures=1, errors=1)**, not PASS.

1. `tests.test_v098_target_user_scenario_bootstrap.UserTargetBootstrap.test_new_source_shaman_catalyst_fifth_and_crafted_tier_lock_once`: `ReferenceNativeBlocked: SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT`. The test correctly pins an **undecorated Native static variant** of selected Shaman head catalyst `271483`, ilvl334, `redirected_base_stats=268231`, `bonus_id=13848`, with exact fixed secondary `haste_rating=175`. In the actual assembled user scenario, `v101.apply_user_equipment` now retains the original head gem `240983` while replacing selected head gear. That produces a distinct gemmed item key vs. the ungemmed static cache record. `v062.get_native_secondary` yields missing selected L and v090 correctly blocks. This is unrelated to v104 sorted gear slot order and must NOT be handled by assuming missing fixed L=0.
2. `tests.test_v114_local_web_ui_offline.RealHTTPPageOffline.test_new_plan_does_not_display_previous_specialization_dps`: the assertions stored two literal backslashes before `n` (`\\n`) instead of a real newline escape (`\n`) in Python. Actual JS contains a newline. Product JS status/visibility is not the cause.

## Narrow fix

- `runner/v062_static_budget_bridge.py`: selected *head* with `gem_id=240983` or `240967` and **no other secondary-budget ambiguous modifier** can use the exact Native-observed static variant of the same head item/ilvl/**all other options** without its diamond **only if** an exact gemmed Native record is missing. The two v108 supported head diamonds are primary/effect-only with **zero flat CHMV secondary rating**. This retrieves the selected item fixed L, not gem proc effects, which stay SimC-owned. No generic identity wildcard, no missing-L zero fallback, no transfer across item/ilvl/bonus/catalyst source, no other slots/gems; `get_native_secondary` retains its exact source_kind/static_digest validation. If both records are absent or unsupported modifiers exist, old blocking persists. A fully Native-observed exact gemmed primary-only head variant is still allowed. For ordinary gear or the remainder of static G, no alias added.
- `tests/test_v062_static_budget_bridge.py`: 2 added isolated offline tests covering both supported head diamonds with exact ungemmed Native L, missing Native L refusal, and other gem refusal. Existing test `test_special_with_gem_modifier_needs_numeric_separation_not_proc_gate` (neck secondary ambiguity) remains.
- `tests/test_v114_local_web_ui_offline.py`: replace escaped backslash literals in 2 static JS assertions with actual newline escapes.

No v003/main, SimC Native execution, cache mutation, static revision invalidation, optimizer/B/O/T/95% or proc-mechanics implementation. The exact-pinned Native L value is still part of B/G and protected as an optimization lower bound.

## Verification status and action

- Previous 50-test Windows FAIL preserved as real historical evidence.
- **Changes committed, new Windows 69-test rerun pending**; no claim of PASS yet.
- The next focused run adds `tests.test_v062_static_budget_bridge` to the same previous three modules, for **69 tests** expected (v098 28, v101 11, v114 11, v062 19).
- Continue actual Rogue `240967` SimC test **only when all 69 pass**. Existing company Rogue planned session `04fe21c0e61b180d305f` is untouched, prior successful Paladin Native6/6 + cached6/6 unaffected. Existing Rogue `profile.simc` safety gate stays intact; resuming may invoke new Native candidates.
- GitHub Actions PASS and actual Rogue Native/socket effect validation still unverified.
