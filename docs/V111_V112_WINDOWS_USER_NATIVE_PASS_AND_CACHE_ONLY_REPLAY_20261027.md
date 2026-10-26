# v111–v112 — First user Windows real Native PASS and zero-new-Native cache replay control

**Date:** 2026-10-27 (KST). **Authority:** existing isolated development branch only. The user's current product target is **27 DPS specializations** (not tank/healer); six source-backed user scenarios currently implemented. No equipment recommendation, season-long item DB, new solver, or main/v003/Work OS/Project UI changes.

## A. First real Windows user DPS evidence, v111 factual promotion

**Evidence personally supplied by user:** `V094_RESULT.json`, `V094_PROGRESS(1).json`, plus completed Windows GUI final result text after v110 LF/CRLF Native input writer correction. Do not replace these receipts with historical Linux benchmark data.

The user-run V094 progress and result report:

- Both status fields: `PASS_BOUNDED_GENERIC_NATIVE_SEARCH_AND_CACHE`; six `NEW_NATIVE` case observations (seed_00, seed_01, scout_00, material_00, confirm_00, confirm_01). **6/6 completed, progress 100%, native attempts cumulative 6, 0 cache hits during the fresh user run.**
- Class/spec Paladin Retribution, target ilvl334; `B=3150`, `O={crit:16, haste:16, mastery:0, versatility:0}`, `T=3182`; verified actual observed best final absolute rating `{crit:704,haste:804,mastery:787,vers:887}`.
- Observed distinct CHMV candidates: **4**. Observed best from fresh confirmation: **179517.9936773854 DPS, SimC SEM 264.49327569785953**, 319 reported samples. Second confirmation: 178124.55179395032 DPS / SEM 263.07149390133515 / 319 samples. Confirmed selected-pair delta **1393.4418834350945 DPS**, approximate CI95 halfwidth **731.1566872710276**, `pairwise_direction_supported=true`.
- Material alternatives meeting 10% B-move and 1% DPS-loss policy **0 observed**, not a guarantee of absence or of global optimality; `global_optimum_proven=false` and ONLY **95%** decision/display.
- Result `observations[].native_sha256` lists all six Native JSON2 hashes. **But the six underlying raw `result.json` binaries and companion `native_receipt.json` files were NOT uploaded**. Thus user progress/result are consistent and support first Windows end-to-end observed PASS, while **independent byte-parity verification of six individual JSON2 files, on-disk receipt identities, and actual cancellation or cache replay on this Windows session are NOT yet proved.** Existing v105 Linux actual six-call cache replay 6/6 is unrelated historical test proof.
- The first user Windows failure `WRITTEN_SIMC_INPUT_SHA_CHANGED` completed **0 Native**. It was fixed at v110 by exactly preserving LF UTF-8 Native input bytes; this later user run **did** complete 6/6, so the earlier Windows pre-Native blocker is resolved.

## B. v112 cache-only audit in Windows beta UI (no new SimC)

Updated existing `runner/v106_user_session_controller.py` and `runner/v106_windows_simple_gui.py`; no new optimizer or extra caller.

- New UI control: **완료된 결과 캐시 검증 (Native 0회 · 6/6 재사용)**, different from `실행 / 동일 설정 재개`.
- Before starting any worker, calculate the *same* canonical user+binarySHA+revision+optional cache identity and require existing completed `V094_RESULT.json`, `V094_PROGRESS.json`, `V106_USER_RESULT.json`, six `result.json` with six accompanying Native receipts, 100%-equivalent six completed and `6` cumulative Native calls, plus 95%-only user result. **Missing/incomplete cache fails before invoking SimC code**, no new session folder is created by this mode.
- Launch existing `v106` worker with `--cache-only`. The worker calls unchanged `v098→v096→v094` durable evaluator; `v065.execute_one` verifies existing `native_receipt.json` against Native JSON2 bytes and native input SHA, and raises `CACHE_ONLY_REFUSES_NEW_NATIVE` when any case is missing. **No Native subprocess is launched.**
- The worker snapshots SHA256 for six raw Native `result.json` before and after, checks **6/6 cache hits**, cumulative Native still **6**, original 95% user-result values unchanged, and final durable `new_native_attempts` unchanged. If any check fails, do **not** emit a success receipt. Normal cache-only success creates `V112_CACHE_REPLAY_RECEIPT.json` with status `PASS_SIX_VERIFIED_CACHE_RESULTS_ZERO_NEW_NATIVE`, 6 hashes, 0 added Native, DPS/SEM and 95% result scope. **This mode can refresh derived durable progress / summary files, but never needs new Native and checks raw Native result bytes unchanged.**
- Reusing the original session key protects the old run's data; changing character, talents, oil, Omnium, trinkets, binary, revision or static-cache bytes results in a different identity and is blocked in cache-only mode when not already completed.
- Normal GUI launch, actual Native search, previous cancellation mechanics are untouched. Fix GUI status banner not to overwrite PASS/blocker messages every 450ms while idle.

## C. Honest test scope / past failures

- **[Linux CI #40355278595](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40355278595): 213 offline tests PASS / 0 FAIL**, existing focused modules + v112 cache-only mocked six-file success, drift, missing results pre-run refusal; Python GUI compile and baseline pilot PASS. **New SimC Native 0**.
- **[Windows CI #40355278979](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40355278979): 24 offline tests PASS / 0 FAIL** with real Windows Python/Tk import, `msvcrt` lock, v112 cache guards, pilot PASS. **New SimC Native 0**.
- Intermediate #40354832383 and #40354832415 FAIL after initial controller/UI change because *old v106 mocked-cache tests lacked completed durable Native files*. Tests were upgraded to synthetic six-case records for the stricter safe cache-only contract; those intermediate failures are genuine and preserved. These **mock results do not prove a new real cache replay**.
- v111 user file proof (Windows 6 Native real observed) and v112 test proof (24 Windows offline simulated cache-only) must stay separate. Real user Windows **cache-only 6/6** requires one local button click below, **zero new Native calls**. Actual mid-run cancellation remains untested and should not trigger unnecessary expensive Native work just for coverage.

## D. Exact user next action (cost zero)

1. From the existing isolated branch, replace only **`runner/v106_user_session_controller.py`** and **`runner/v106_windows_simple_gui.py`** in the user's previously extracted project copy. Other files and **completed original user session under `%USERPROFILE%\\SIMC_Secondary_Optimizer\\runs\\abca493c00d6ee2599f1`** stay untouched. The v110 Native input one-line fix must remain in place.
2. Reopen Windows GUI. Retain same Paladin Retribution, ilvl334, original source-pinned talents/two trinkets, one oil, source-default consumables, same Windows `simc.exe` and revision `7bc1071`.
3. Click **완료된 결과 캐시 검증 (Native 0회 · 6/6 재사용)**, *not* the regular optimization start button. It should take no new Native. Success banner says cache 6/6 and added Native 0, with local `V112_CACHE_REPLAY_RECEIPT.json`.
4. Send only that compact receipt if PASS, or sanitized GUI error text if BLOCKED. No new 6-call optimization, no deliberate cancellation test and no old cache deletion.

**Remaining P1 work:** actual Windows cache-only replay bytes confirmation from user; then follow-up on UX and six input specs' bounded real scenarios, and only afterward expand toward 27 DPS. Postpone app-vs-HTML-vs-Cloudflare packaging until user wishes.
