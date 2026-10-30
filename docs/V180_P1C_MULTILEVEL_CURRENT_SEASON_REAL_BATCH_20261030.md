# v180 P1-C — Current-season target ilvl 266–344, multi-level Native batch

**2026-10-30 KST** · P1-C bounded current-season product integration in isolated `probe/chat-cache-v035-20261024` only.

## Product changes (no new optimizer)

- `runner/v098_target_user_scenario_bootstrap.py`: `current_season_product=True` now uses the **existing v169 source-first current-season** 511-item candidate equipment / tier 4pc catalog with **existing v139/v153 level preview** at arbitrary target ilvl **266–344**, including 334. This keeps all original `v096→v094` native candidate, 95% statistics, consumables, `T=B+O`, exact special L fail-closed and cancellation/resume code unchanged. `source_first_stage` remains a separate physical-only pilot and cannot be combined with product mode.
- `runner/v106_user_session_controller.py`: previous `current_season_product` session identity SHA and four season data SHA hashes unchanged; target ilvl is already part of user identity, so each level gets a distinct session. Original v177 **334 session key bytes are preserved**; pre-v177 old non334 `independent_target_level=True` session IDs still distinct.
- `runner/v113_local_web_api.py`: non334 plans truthfully report `non334_physical_native_not_yet_observed=True` (the preexisting per-profile boolean means no physical proof *for the specific newly planned input*); `v176_26_of_26_base_physical_native` only at 334.
- `runner/webui/app.js`, `index.html`: latest-season target level **266–344** remains selected by default for newly composed user scenarios, non334 no longer silently switches to old route. Users can explicitly uncheck the option for historical independent non334. Saved legacy sessions restore exact saved profile route. The 334 prior v176 evidence is not described as proof for any other level.
- No changed item IDs/SimC logic/optimizer/disk cache, no repeated all-26 current-season physical Native census, no requirement to obtain exact G prior to using same-season rounded ilvl reference B.

## Verified actual evidence — multi-scenario batch

**Actual [GitHub Actions #40980268952](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40980268952) SUCCESS, 2026-10-30 KST.**

### Offline (0 Native)

- **26 DPS × 5 distinct levels (266, 300, 321, 340, 344) = 130 product profiles** compiled independently via the current-season equipment data. The tests compared real internal item ilvl, 4 tier pieces, reference B (normal vs Titan's Grip), exact T=B+O, complete original six-candidate v096 manifest and distinct session IDs.
- Includes 334 original session, old non334 independent mode and current-season mode strict identity separation, API non334 plan and read-only session restored mode, invalid out-of-range level fail-closed and browser script parsing.
- CI **3 new tests PASS + 47 prior tests PASS = 50 PASS / 0 FAIL**. Focused [v113 local browser Windows/Ubuntu #40980154086](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40980154086) both SUCCESS after updating the former 334-only note assertion. Initial older test run failure reflected outdated expected UI text/333 prohibition rather than Native functionality; prior failures preserved as GitHub history.

### Real Native (36 new SimC calls, 6 user sessions)

Single explicit request commit `4eaa5e2554e695527d96234e6f5236e644134696`, exact existing SimC Linux CLI revision `7bc10711b5` and SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e` cached; no new build.

| Spec | Target ilvl | Diverse condition | Native adaptive | Cache-only SHA replay | Observed DPS mean | SimC SEM |
|---|---:|---|---:|---:|---:|---:|
| warrior/fury | 266 | Dual 2h Titan's Grip lower edge | 6/6 PASS | 6/6 PASS | 108193.75335113202 | 133.98 |
| hunter/beast_mastery | 300 | Ranged weapon | 6/6 PASS | 6/6 PASS | 153714.11323905367 | 164.80 |
| paladin/retribution | 321 | Two-hand + manual final T=3500 | 6/6 PASS | 6/6 PASS | 175141.92151923617 | 269.45 |
| rogue/outlaw | 330 | Two targets, 180s duration, dual wield | 6/6 PASS | 6/6 PASS | 265399.6226599006 | 1155.00 |
| evoker/devastation | 340 | Caster, no weapon oil (O=0) | 6/6 PASS | 6/6 PASS | 180457.70892517173 | 197.40 |
| mage/frost | 344 | Caster upper edge | 6/6 PASS | 6/6 PASS | 175646.11954039306 | 247.49 |

- **Six out of six new user sessions full original v094 Native adaptive optimizer PASS** (two seed, scout, material scout, two confirmations each). **36/36 newly executed Native; 36/36 original JSON2 exact SHA cache replays; additional Native 0**.
- Original JSON2, stdout/stderr, per-case Native receipts, session IDs, progress, user result, 95% decision and batch summary are archived in [Actions artifact #12943484210](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40980268952/artifacts/12943484210), **7-day retention**.
- These 35/320 iteration SimC sample DPS means are **not cross-spec rankings**, statistical superiority is a per-session 95% decision only, not global optima. The test does **not** show that every possible item/talent or level-spec combination is Native accepted.

## Status and next

- **P1-C core route complete for target ilvl266–344.** All 26 specs planned at five representative non334 levels, six distinct weapon/class and edge-level cases end-to-end SimC observed, no previous native rework.
- **Next P1-D:** Windows local executable/user journey/installer or one-click launch, web UX, realistic saved sessions, native runtime path and actual platform-specific reliability; prioritize no new optimizer and only minimal native smoke if needed. Carry forward exact-L special variants and crafted edge cases as narrow P1-B issues only if they block real user needs.
- `main`, immutable `v003`, original `v016`, Project Sources/Instructions UI and official Work OS governance **not changed**.
