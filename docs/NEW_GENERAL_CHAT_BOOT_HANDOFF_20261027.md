# SIMC SECONDARY OPTIMIZER — NEW GENERAL CHAT CONTINUITY BOOT (2026-10-27)

> **Scope:** handoff documentation only. This document does not merge, run SimC, approve Work OS, or apply Project UI settings. Read this and the real GitHub CURRENT before deciding next work.

## 0. Latest authority / immutable baseline for this handoff

- Repository: `degong2-code/simc-secondary-optimizer-runner`
- Isolated development branch: `probe/chat-cache-v035-20261024`
- **Pinned product-source HEAD inspected for the handoff:** `a41740cfbaef170fc01abd2e4bcd0928bee34d59` (the state *before adding this handoff document*).
- Final green WEB2 code/action commit: `341d8795423baa497eb0c0b6510ce8a1d6d143b3`; subsequent three commits up to the pinned source HEAD change **docs only** (GitHub Compare verified).
- [CURRENT](./CURRENT_PRODUCT_DEVELOPMENT_STATE.md) is the actual ongoing development state, not a standalone proof of everything being completed.
- [v114 HTML scope and actual test report](./V114_P1_WEB2_LOCAL_HTML_UI_20261027.md).
- Full **v1.4 user-approved design** `SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4_TARGET_LEVEL_USER_FLOW_PROJECT_SOURCE_REPLACEMENT.md` is in the original Project upload and new portable user handoff ZIP. **Do not infer that the file is registered in the Project Sources UI.**
- **Critical user override later than v1.4:** final product target **27 DPS specs only, including Augmentation**. Tanks/healers EXCLUDED, despite old v1.4 sections stating all specs. User has now **explicitly requested continuity in a NEW GENERAL CHAT**, overriding the earlier instruction not to move without permission. Existing isolated branch development may continue in that new chat, but GitHub main, immutable v003, Work OS M0/Shared State and Project UI changes still need distinct authorization.

## 1. Goal and non-goals

Future **target ilvl** (default 334) or user-entered final absolute total `T` → strongest **absolute rating** allocations Crit, Haste, Mastery, Vers by actual SimulationCraft **DPS**. Show observed best, CHMV absolute values and ratios, DPS, SimC SEM, **95% only** supported comparison, meaningfully distinct near-performing alternatives, progress, cancel/resume, cache. Distinguish observed winner from *proved global optimum*; do not invent alternatives when none observed.

No full current worn-gear selection; no redistribution of current character's total, item combo selector, gear recommendations, season-wide database, independent class APL / proc simulation engine. The user chooses class/spec/race/talents, ilvl/manual final T, two trinkets, optional special gear, <=2 embellishments, gems/flask/consumables/Omnium, weapon oil, raid buffs/combat conditions. Code internally composes a standardized target-ilvl representative, class weapon performance and four-tier equipment. Optional uploaded SimC profile is for character/talent info, **not** overwriting target equipment/budget.

## 2. Budget and SimC responsibilities

- `T=G+J+F+O`, `B=G+J+F`, `T=B+O`, `c_final=c_base+o`.
- Fixed oil `o` is assigned only once via `gear_*` and is **never a freely redistributed stat**. One Phoenix oil gives (Crit+16,Haste+16) → `O=32`, two `O=64`.
- Known fixed nontrinket special equipment `L` belongs to G/B and is protected by lower bounds, **not added a second time**. Craft 50:50 starter stats are NOT locked L. Trinket static CHMV outside freely redistributed gear G; a missing static trinket record isn't 0 or a blocker.
- Representative 334 B=3150 regular, 3350 Fury Titan's Grip; source Native-derived per-ilvl 79×2 rounded reference B is an *approximation* (10-rating rounding), not actual exact G for every equipment/spec. User manual final T overrides. Exact Native G is optional, not a gate to completing UI.
- Existing six-source scenario: J=138; validated source flask F=165; do not expose unmeasured replacement flasks. Source-observed Omnium five-rune WHOLE loadouts; `augmentation` is different from `omnium_talents`. Gem diamonds verified primary-only choices; avoid unproven J changes.
- SimC owns item's effects/trinket proc/embellishments/APL/DPS; our tool owns input ID/slot/ilvl, budgets/L/O/duplicate prevention, static rating from Native JSON2, candidate planning, DPS/SEM/95%, SHA identities, cache/cancel/resume. Real SimC errors should be preserved.

## 3. Product chain & recent milestones (do NOT reimplement/retest indiscriminately)

- Origin latest **user-reported** `v016_SCENARIO_CONTRACT` (original bytes/receipts unverified); isolated GitHub experimental code never claimed integrated into original v016 or authorized merge to main. Historical user portable handoff `SIMC_SECONDARY_OPTIMIZER_CHAT_HANDOFF_V096_20261026(1).zip` includes v092–v095 Native proofs but is **historical**, not the current branch source.
- v092/093/094/095/096/097 developed oil T policy, existing bounded adaptive Native, durable cache/cancel/resume, 95% material-result interpretation, unified user scenario; don't make a new engine.
- v098–v104: source-backed target-ilvl input and internal representative gear/tier/weapon for 6 DPS paths **Fury Warrior, Retribution Paladin, Frost Mage, Beast Mastery Hunter, Subtlety Rogue, Elemental Shaman**. Other 21 DPS paths NOT yet ready.
- v105 original-source Paladin Linux Native 6/6 + cache replay 6/6 historical proof [#40335091679](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40335091679).
- v106–v108 Windows Tk beta GUI, optional exact special gear/embellishments, source-observed food/potion/augmentation/diamond/Omnium, with fixed F=165 and static item L fail-closed.
- v109 user Windows no-Native readiness PASS after bad revision entry correction. Actual Windows binary named `simc-1210.01.7bc1071-win64`; user revision `7bc1071`, executable SHA `b0ea12ee3ac233a4a590609e2a5bd4c4db45c5f8ae6f8994b1b8d0de4d5acff4`. Naming is not standalone binary-provenance verification.
- v110 **real Windows LF→CRLF Native input bug** fixed with `write_bytes(req["input"].encode("utf8"))`; do not reintroduce text-mode Native I/O. Previous attempt `WRITTEN_SIMC_INPUT_SHA_CHANGED` was 0 Native. Also a first Windows CI error failed unittest but appeared green before PowerShell exit-code forwarding fix; preserve negative histories.
- v111 **actual USER WINDOWS** `V094_RESULT.json`/`V094_PROGRESS(1).json`: six new Native SimC jobs, 6/6 complete, 100%, four observed unique allocations; Paladin 334 B=3150/O=32/T=3182; final `704/804/787/887`; observed **179517.9936773854 DPS**, SimC SEM **264.49327569785953**; selected pair 95% direction supported; no material distinct alternative OBSERVED; not global optimum.
- v112 **actual USER WINDOWS** `V112_CACHE_REPLAY_RECEIPT.json`+worker log: 6/6 cache hits, additional Native 0, cumulative Native still 6, same DPS/SEM/95%, 6 stored JSON2 SHA references. User did NOT upload the six raw `result.json`+Native receipts for independent byte verification; user cancellation mid-execution/partial resume NOT actually proven on this Windows session. [evidence docs](./V111_V112_WINDOWS_USER_NATIVE_PASS_AND_CACHE_ONLY_REPLAY_20261027.md).
- v113 P1-WEB-1 **local FastAPI HTTP API** under `runner/v113_local_web_api.py`: GET defaults/health/bootstrap/options, POST plan/start/resume/cancel/cache-only, GET status/result, uses v106 identity and v098→v096→v094 engine. Loopback `127.0.0.1` only; Host/peer/Origin/Sec-Fetch-Site check, temporary token, JSON-only POST, 20-char session ID. No cloud or new engine.
- **LATEST v114 P1-WEB-2 HTML implementation**: `runner/webui/index.html`, `styles.css`, `app.js` served same-origin by v113, 6 class/source defaults, ilvl/T, advanced options, plan without Native, controlled explicit start, progress/cancel/resume, cache-only, 95% result bars. Session ID only kept in localStorage, no external JS/CSS or CDN. CSP/no-store headers. [Windows Python 3.14 / Linux Python 3.12 CI #40415052508](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40415052508): **each 30 PASS/0 FAIL**, Node JS syntax pass and pilot, **new SimC Native calls=0**. CI checks HTML/CSS/JS syntax and HTTP, **NOT actual Edge/Chrome clickable GUI on user's computer**. Subsequent commits to pinned source HEAD were docs-only.

## 4. What should happen NEXT (minimal P1)

**P1-WEB-3 user-assisted real Windows Edge/Chrome zero-new-Native smoke + recoverability/UX hardening.** Download a **fresh entire branch** into a new Windows folder (do not mix hand-copied v106/v109 modules, as that caused `ImportError` previously). Do not touch existing session `%USERPROFILE%\SIMC_Secondary_Optimizer\runs\abca493c00d6ee2599f1` or the existing `simc.exe`. From new repo copy install `requirements-web.txt`, start `py -3 runner/v113_local_web_api.py --port 8765`, open `http://127.0.0.1:8765/`, enter previous session ID and **only click `열기`**. Verify the preserved result (DPS 179518, SEM264.49, T3182 and CHMV704/804/787/887), refresh to check restore; expect **0 new Native**. The user can provide screenshot and exact browser errors. Do not ask user to start optimizer to prove browser; skip deliberate cancellation repro if not otherwise needed.

After that: fix only observed WEB-3 defects (safe status polling, run lifecycle, identity, origin/CSRF, output text); then P1-WEB-4 easy Windows double-click runner, port selection/browser launch and webview packaging if useful, with one cohesive full release artifact. Do not build account/cloud service now. Then optimize six paths/consumer inputs and grow toward the remaining 21 DPS classes where source-backed. Do not wait for Work OS M0 to pass to continue ordinary product tests.

## 5. Mandatory self-verification in new general chat

1. **Confirm the new chat is expressly user-requested handoff** (no unapproved transfer) and preserve main/v003/official authority boundary.
2. Read this document, `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md`, and `docs/V114_P1_WEB2_LOCAL_HTML_UI_20261027.md`; if user attaches handoff ZIP, verify its SHA256 manifest offline with included `VERIFY_HANDOFF.py` first.
3. Query GitHub **latest branch HEAD**; compare to this pinned pre-handoff source commit; if newer, inspect only changes and CURRENT, not restart history or assume no changes.
4. Check real Actions job conclusions AND log `Ran 30 tests ... OK` and Node syntax exit. Distinguish test scopes: Linux/Windows offline UI HTTP PASS ≠ real Windows Edge interaction; user actual v111 Native ≠ v112 cache replay ≠ unseen cancellation.
5. Compare `V094_RESULT.json` 6 `observations[].native_sha256` with `V112_CACHE_REPLAY_RECEIPT.json` map; verify `6/6`, `Native0`, B/O/T and 95% result. These are receipt-level references; don't claim independent six raw JSON2 byte audit.
6. Check the v114 files and the v113 endpoints plus **actual `python -m unittest`/workflow** as appropriate. Avoid extra Native/full season catalogue/SEM microrefinement/new algorithm/new independent proc Gate. Code edits: evaluate Native count, cache, I/O, runtime, memory and structural simplicity.
7. Before any GitHub commit, re-read HEAD and relevant file SHA. Work only isolated branch; do not touch main/v003/Project Sources/Work OS M0 unless distinctly authorized. Update CURRENT with **new implementation/test vs reused history evidence vs unimplemented**, and never auto promote.
8. If unrelated user data inaccessible in new chat, use attached handoff and GitHub; ask only for missing *material* proof. Do not ask users to reupload old session/native logs or repeat entire Native 6/6. Avoid user-local absolute personal paths in public docs.

**Ready state:** next new chat continues **P1-WEB-3**, not from v096 and not by rebuilding the core engine. First local browser test can be performed entirely with prior cached result and 0 additional Native calls.
