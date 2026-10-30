# v177 — Current-season product input to existing v094 adaptive SimC

**Date:** 2026-10-30 KST. **Development scope:** isolated `probe/chat-cache-v035-20261024` branch only.

## What changed

- **No new optimizer, DPS model, proc or independent effect gate.** Reuse existing `v098 → v096 → v093/v091/v092 → v094/v065/v064` for six Native candidates and the original 95%-only user result, disk cache, cancel, resume.
- `runner/v098_target_user_scenario_bootstrap.py`: optional `current_season_product=True` compiles the verified `v171` 511-item current-season representative gear and `v168` 65 tier pieces for all **26 DPS specs**. It uses the real non-staged v096 manifest, separate from old `pure_stage` physical-only guard. Target ilvl **334 only** for this new mode; previous non-334 and default routes unchanged.
- `runner/v106_user_session_controller.py`: an explicit new product-mode session identity includes full SHA256 of current-season gear DB, tier DB, CHMV consumables budget and source-first base catalog. The original default session key is unchanged byte-for-byte. Worker uses existing lock, progress, cancellation, resume, 6-candidate SHA cache and user result.
- `runner/v113_local_web_api.py` and `runner/webui`: new `current_season_product` choice in HTTP plan/start; target334 new-user UI defaults to current-season selection, with opt-out to historical route. Restore retrieves the session's original choice and does not repoint old receipts. Non334 auto-unchecks the new selection; legacy API clients omit the field and retain historical behavior. The user selects no full ordinary equipment.
- 26-spec preflight, separate session identity, mode restore and web API input tests use **zero Native**. No `main` merge, no Project Sources/Instructions UI update, no `v003` immutable change.

## Verified evidence

1. **26/26 physical SimC base profiles:** existing actual [v176 Actions #40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357), 25 new and one exact v174 Paladin receipt; all PASS, zero failures. This physical evidence is **not 26 optimized user results**.
2. **New current-season user end-to-end, paladin/retribution, ilvl334, default oil main-hand:** actual [v177 Actions #40976501045](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40976501045), exact pinned SimC revision `7bc10711b5`, binary SHA `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`, Native **6/6**, existing stages `SEED_00, SEED_01, SCOUT_00, MATERIAL_00, CONFIRM_00, CONFIRM_01` all PASS.
3. Official `T=B+O`: **B=3150**, **O=32**, **T=3182**. Observed top absolute `{crit:916, haste:766, mastery:750, versatility:750}`; observed DPS mean **182771.77555112448**, SimC SEM **276.0260387384388**. Selected confirmation **95% directional superiority UNRESOLVED**; one measured materially distinct nearby alternative `{crit:601, haste:1081, mastery:750, vers:750}` mean DPS **181478.9**. No global optimum claim.
4. Same exact session and unchanged Native JSON2: existing six SHA-verified receipts **6/6 cache hits, 0 additional Native** and identical semantic user results. [Raw receipt / JSON2 / logs artifact #12943086088](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40976501045/artifacts/12943086088), 7-day retention.
5. Focused offline [v177 Actions #40976403575](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40976403575): **5 new PASS plus 73 established regression PASS**. New UI default and restored old session mode are tested by [v177 Actions #40976798373](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40976798373). Existing [v113 Local Web API Ubuntu/Windows #40976768829](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40976768829): both SUCCESS. No new Native for UI checks.

## Important limits

- This confirms **26/26 representative physical profiles** and one **complete 6-candidate user-adaptive session**, not full optimization across all 26. Individual changed trinket/talent/consumable/special-item conditions remain dependent on actual Native evaluation and exact chosen equipment static L when applicable.
- The new source-first target-334 user path is available in the isolated branch UI (default for **new** local 334 sessions), old sessions and original profile bytes are not migrated or re-keyed, API compatibility defaults are preserved.
- Existing v106 cancel/resume and v094 durable progress are reused and focused offline tests verify routing/cancel flag, but **a new interrupted mid-Native v177 physical resume case was not separately exercised**. Do not claim it was.
- Exact source product `v016_SCENARIO_CONTRACT` original bytes remain unconfirmed integrated. Non-334 source-first mode is not promoted yet. No duplicate full 26-spec physical Native rerun needed unless invalidated.

**Next P1:** finish packaging/operational readiness and verify any genuinely changed input-mode behavior (non334 or selected exact-L), not another optimizer or full Native census.
