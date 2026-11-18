# P1 v596 — existing signed v212 E=0 permanent-ring enchant -> final user SimC profile -> original v096/v093 durable entry

Date: 2026-11-18. Isolated branch `probe/chat-cache-v035-20261024`.

## Latest user decision and product responsibility

Static Crit/Haste/Mastery/Versatility **E=0 is common and NORMAL for permanent enchants**. E=0 does **not** imply an ineffective or untriggered effect. Most permanent enchants are not fixed secondary-rating bonuses. **SimC alone** evaluates actual spell/enchant effects, procs, APL and DPS. We supply exact item/enchant IDs, ilvl/slot, representative target gear, target season G/J/F/O and `B=G+J+F`, `T=B+O`, L/E/O fixed minima once, user manual T precedence, existing v290/v291/v293 adaptive SimC/SEM/95%/observed best/near options/cache/cancel/resume. No separate enchant-effect activation certification or new optimizer/gear database/26-spec Native sweep. Product runtime AI/LLM/API/agents = 0 (development AI permitted).

## What was actually connected

Before this turn v595 had ONLY a read-only installed E0 budget preview; v098/v096 accepted only original **three 70783/334 Survival Hunter scoped** finger1 cases, and ordinary UI could not select an otherwise verified original v212 E0 item.

1. `v106.user_scenario` now accepts the **syntax** of one selected `finger1` or `finger2` positive enchant ID; this is NOT item approval. Malformed IDs/multiple selections are denied. Other UI fields are unchanged. v106 keys already include the user selection and the exact v212 installed SHA when a session is source-bound, so different hands/IDs/builds cannot alias previous DPS caches.
2. `v098._selected_installed_E0_on_final_user_item` reuses the original v101-constructed **actual final ring item ID**, the existing `v216→v230→v196/v220` exact selected item source-mask comparison (must be `EXACT_SELECTED_ITEM_SOURCE_MASK_MATCH_UNADMITTED`), and the existing signed `v212.preview_installed_selected_enchant_budget`. Only an original Policy A-published entry with an explicitly verified **four-stat E0** and matched installed game build/target/slot/item is accepted. It applies **exactly once** `enchant_id` to that physical ring's normal SimC option; no spell mechanics are checked. E0 B/T unchanged; manually set final T remains authoritative. Existing v529/v531 narrow cases remain the original route only when actual **historical user + exact build and SimC revision** match; a repeated enchant ID is not a global class/spec or future-season blacklist.
3. Existing `v098._materialize_admitted_season_v096` attaches a small signed installed-E0 final ring identity to its unchanged **original** v096 fresh-season manifest source. This source is **NOT** the old standalone v529 magic-ID proof; it is original v212 four-owner Policy A + v098 final physical item+SimC input. No new manifest schema, optimizer or worker.
4. Original `v096._admitted_fresh_season_source` **independently repeats** the sealed v217/v212 validation and `v212.preview_installed_selected_enchant_budget`, verifies source E0, the same selected hand/item/enchant ID and **one actual `finger*=id=...,enchant_id=...` field** in the final SimC profile. The canonical signed selected E0 identity and CHMV owner receipt enter the existing `season_source_identity.source_input_sha256`; combined with profile SHA, installed manifest SHA, binary and scenario they remain within the original v093/v094 durable cache identity. Only then `v096.source` uses the ordinary v093/v094 DPS path. Positive E values still require the separate proven arithmetic/floor path; unknown E never becomes E0.
5. Original `v113` installed-only option catalog now exposes **only the exact signed published E0 ring subset** as `installed_E0_final_finger_candidates`, separate from the remaining read-only registered E+/unknown rows; it never treats a missing E or a browser-supplied token as a trusted proof. `webui/app.js` renders those E0 options in the existing **finger1** selector while leaving E+/unknown items locked, with server-side rechecks at planning. Original three historical exact options retain their original scope. The current UI is **one ring at a time**; finger2 is accepted by v106/v098/v096 internally, not yet a second UI control or multiple-enchant submission.

## Explicit E0 vs E+ vs unknown policy

- E0: zero stat floor/no incremental G/B/T and full SimC enchant input. This is a real option **only when verified v212 + final user physical mask + SimC profile ID identity** are all present. SimC may compute nonzero combat DPS effects.
- Rare E>0: reserve each stat inside G and avoid double count; manual T never grows. Existing v531 narrowly scoped historic or v222 accounting preview only, **not unlocked generically by v596**.
- Unknown: item-specific PENDING, never substitute 0 and never block otherwise verified base environment.

## Tests, evidence and limits

Existing offline tests augmented, no new workflow:
- `test_v096_unified_product_entry`: normal signed E0 selected ring profile must contain exactly one correct `enchant_id`; incorrect ID/item, duplicated enchant, SHA drift or positive E are blocked. Replays original fresh source identity with a synthetic sealed source loader, not a new Native.
- `test_v098_target_user_scenario_bootstrap`: actual final ring1/2 item ID and original physical mask join to signed v212 source, idempotent exact SimC option, missing/wrong mask blocked.
- `test_v106_user_session_controller`: syntactic choice validation, distinct v106 user session keys for different ring/enchant IDs.
- `test_v113_local_web_api_offline`: installed exact E0 subset from signed source is emitted but E+ and unknown stay locked.
- `test_v114_local_web_ui_offline`: Node checks the original render and actual availability function, only signed E0 enables finger1, malformed/missing E or wrong installed SHA does not.
- `test_v529_one_real_season_eagle_E0`: historical exact witness is not a blanket restriction on all other classes or future game builds.

**Verification scope:** old full real Windows base [v570 #44074372451](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44074372451) and real ZIP cancel/resume [v572 #44082378854](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44082378854) are REUSED, not rerun. Latest v596 CI results must be listed separately from those historical proofs. The new E0 route was tested **offline with simulated registered v212 rows and mock signed receipt loaders**, not actually completed as a new generic item/26-spec real SimC DPS E2E. The default original environment with no Policy A-published E0 rows offers no new choices, and needs no new collection or special effect certification. Zero new Native/Wago/DB2 for this implementation.

A source-only/physical-mask result is **not** itself a Policy A receipt. At runtime the exact signed v212 item and confirmed E0 CHMV owner are also required. This is deterministic input correctness, not independent spell-effect authentication.

## Latest verified offline Actions, no new Native

**The final new code/test commit was `1675ee8d8af7b6701666dd13293776c4808b6c8b`.** Re-run only existing exact-change focused offline CI, not an entire new live SimC test matrix.

- [Original offline focused continuity #44264004427](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44264004427): **SUCCESS** on that exact code/test commit, log `Ran 682 tests`, `OK (skipped=2)` = **680 PASS / 2 SKIP / 0 FAIL**. This includes original v096 signed installed E0 source replay, proper physical-profile ID once, and previous budget/optimizer/cache regressions.
- [Original v401 78-element contract #44264004439](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44264004439): **SUCCESS** on the same exact code/test commit; contract guard only, no full-product acceptance or Native.
- [Web/API Windows+Ubuntu #44263274946](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44263274946): **BOTH SUCCESS** on earlier code commit `f09b5510748e9bcc58f06ceac1462901384a74b2`, each job `Ran 484 tests`, `OK (skipped=1)` = **483 PASS / 1 SKIP / 0 FAIL per OS**. That commit contained the E0 v113+UI+v098/v096 production code; subsequent changes before final focused success were to the synthetic v096 replay test only.
- [UI Windows+Ubuntu #44263274886](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44263274886): **BOTH SUCCESS** on same earlier production code, original **107 + 199 + 4** offline test groups per OS, including the original Node E0 option visibility/installed SHA and continued DK rune behavior.
- [v098 source-only/offline #44263275021](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44263275021): **SUCCESS**, `Ran 506 tests` on that previous head; not a Native DPS E2E.
- Earlier focused #44263509667 and #44263834325 were **FAIL** because of two mistakes in the new synthetic v096 test: missing `simc_revision` in its mocked installed v212 document, then expecting an `EntryBlocked` for a legitimately raised original `v212.EnvironmentBlocked` on a forged ID. Both **test-only** mistakes were corrected, and #44264004427 final focused PASS; never present those intermediate failures as product bugs or as successful receipts.
- **New SimC Native calls: 0.** New network/Wago/DB2 source collection: **0**. Historical [v570 basic Windows Chrome-to-real-DPS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44074372451) and [v572 real ZIP cancel/resume](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44082378854) are *reused historical one-scope evidence*, **not** proofs that the new general E0 permanent enchant input has run through actual SimC Native.

## Still pending

- A **real installed original v212 E0 registered item** meeting the final-user ring mask source on ordinary product hardware should be run through one exact v113→v098→v096 session and observed SimC user result; prefer reuse of identical-scope cached Native, otherwise minimal targeted run, no wholesale Native matrix. Record actual full-profile and persistent resume identity. Do not label the new generic E0 DPS E2E PASS before that receipt.
- General E+ selected rating floor/increment, additional equipped permanent-enchant slots or two rings simultaneously, future-season option availability and 26-spec coverage are not claimed by this scope.
- If `v216` exact physical source evidence is absent, only that optional new enchant remains pending, not base G/J/F/O. DO NOT initiate another effect/proc certification campaign.
- Official **15/78 COMPLETE / full_product_e2e=PENDING** is unchanged. Isolated branch only: no main merge, immutable v003 edits, original v016 integrated assertion, Project UI/Work OS promotion or takeover from the existing main product development chat.
