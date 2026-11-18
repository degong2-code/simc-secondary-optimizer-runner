# P1 v595 — E=0 is NORMAL for most non-static permanent enchants; reuse installed v212 CHMV accounting

Date: 2026-11-18. Isolated branch `probe/chat-cache-v035-20261024`.

## Binding latest user decision

**Static CHMV E=0 is ordinary, not a failure or absence of an enchant effect.** Most permanent enchants do not directly contribute fixed crit/haste/mastery/versatility rating. Some have combat spell/proc/damage/defensive or other effects; **SimC owns all mechanics, execution, procs, APL and DPS**. Our program only enters exact item/enchant IDs, handles one-time static CHMV ownership, selected physical item/slot and the original adaptive SimC runtime. No separate activation/handler effectiveness test or whole-set Native repetition.

Three independent cases MUST NOT be conflated:
- **Verified E=0**: four-stat ZERO from the ORIGINAL authenticated `chmv_budget` owner (or independently verified exact static-stat-source determination). Valid user option; E adds 0 to G/B/T and causes no new E stat floor. SimC enchant remains in selected equipment input and cache profile identity.
- **Verified E>0**: rare true static CHMV; per-stat fixed E included in G once, protected as floor. If the representative unenchanted G explicitly excludes this E, only automatic ilvl reference adds once; manual final T never increases.
- **Unknown E**: missing/insufficient static CHMV accounting evidence, which is **NOT E=0**; only that optional candidate remains pending, never block verified core G/J/F/O.

Highest-quality UI dedup uses source-based same effect/use/numerical noninferiority; this is NOT independent proof that a spell fires. Never construct a separate SimC effect certification Gate. 26 DPS, target ilvl334/manual final T, no current gear redistribution/full season gear DB, development AI allowed but product runtime AI/API/LLM=0. Existing v290/v291/v293 and 95%, cache/cancel/resume stay sole execution owners.

## Concrete minimal code changes (no new source/Native)

1. `runner/v212_environment_manifest.py::preview_installed_selected_enchant_budget`: **pure, non-executable selected user slot/item + budget projection** on the existing sealed v212 installed manifest. Calls existing `verify_fresh_installed_environment`, selects exactly ONE installed verified registration and its authenticated `verified_fixed_E` + budget-owner digest. Source group `finger1/finger2` permits final selected finger1 or finger2, without presuming its physical item is already source-verified. E0 automatically keeps the B/T unchanged, even when explicitly selected; no SimC effects are inspected. For rare E>0, auto ilvl B/T includes E only with explicit original `G_reference_excludes_selected_E=True`; manual T overrides and retains T exactly; existing fixed L/J/F/O capacity is checked once using the v222 arithmetic. Distinct selected hand, real item ID, enchant ID, verified E, manual T and installed SHA form a separate SHA256 identity to prevent unintended cache reuse **when subsequently connected to v106**. Output is clearly marked `runtime_selectable=False`, `user_physical_item_and_simc_profile_binding_pending=True`. This is **not yet called by ordinary v113→v098→v096 session creation**, and does not assert new runtime admission.
2. `runner/webui/app.js`: read-only installed catalogue distinguishes **'정적 CHMV E=0 (정상, 효과는 SimC 처리)'**, positive E source observed, E unverified. E0 does NOT unlock generic user choice.
3. Existing tests `tests/test_v212_environment_manifest.py`: synthetic previously validated v212 boundary exercises E0 auto 3107/3107, manual 3300 unchanged, changed finger+item SHA differs; positive E30 auto once 3137, manual T3500 unchanged; rejects wrong final slot/ID, missing E and unknowable positive G ownership. Uses mock for the *independently already tested* original signed v212 verifier; **not live current-season source verification**.
4. Existing real Node UI test `tests/test_v114_local_web_ui_offline.py`: four normal stages missing E / positive E / E0 / wrong install SHA; E0 text present and generic SimC choice disabled. Existing test render counter reflects the additional E0 case.

## CI and costs

Latest changed code+test head `a07b1448e70f754b9a8ffbcdc145a586eb5ec542`:
- [v113 Windows+Ubuntu offline #44258993076](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44258993076): BOTH SUCCESS, **482 tests, 481 PASS / 1 SKIP / 0 FAIL per OS**.
- [v182 UI Windows+Ubuntu #44258993074](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44258993074): BOTH SUCCESS; each OS ran existing 107+199+4 test groups with successful job conclusions, including new E0 read-only actual Node UI test.
- [offline focused continuity #44258993091](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44258993091): SUCCESS, **680 total / 678 PASS + 2 SKIP**.
- [original v401 78-contract #44258993135](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44258993135): SUCCESS, **contract scope only**.
- [v212 Windows+Ubuntu #44258860024](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44258860024) at prior code head `b120f651`: BOTH SUCCESS, **522 tests / 518 PASS + 4 SKIP per OS**. This exact earlier head already included selected E0 budget projection tests. Subsequent HEAD a07b changed only the read-only UI and its test; do not pretend v212 was rerun on final UI head.
- One earlier v212 test fixture failed from duplicate Python kwargs on `511ee959` head; corrected at `b120f651` and Windows/Ubuntu PASS proven. Historical FAIL not silently erased.

**New actual SimC Native=0; new network/Wago/DB2 source collection=0; no repeated historical v570 64 Native, v572 ZIP run, product optimizer or effect/certification Gate.** Same-season static cache/old immutable receipts unchanged.

## Next real product work and evidence boundary

This v595 step brings **signed installed selected E0/E>0 numeric accounting and future user/session SHA**, not the actual v113 user option → v098 equipment `enchant_id` → v096/v093 DPS session. Connect the already-proven registered option's exact final physical item and SimC profile next, and reuse v065 fixed-E per-stat floors plus v106 selected control identity. Do not unlock generic user UI or claim product E2E until exact selected original v212 E owner and final profile+cache are bound with no double counting. An E0 static budget is normally valid even if the spell/proc effect is nonzero (SimC owns it). Existing narrow v528-v535 user case and real [v570 Windows Chrome→64 SimC Native E2E](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44074372451) remain historical, not general-enchant completion.

Official **15/78 COMPLETE**, `full_product_e2e=PENDING`. No main merge, immutable v003 edits, claimed original v016 integration, Project UI/Work OS promotion or takeover of main product development chat.
