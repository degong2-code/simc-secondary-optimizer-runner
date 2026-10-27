# SIMC SECONDARY OPTIMIZER — P1/v126 immutable old seed plan replay

2026-10-27, isolated branch `probe/chat-cache-v035-20261024`.

## Observed and inferred evidence — distinguish precisely

After successful v125 **Windows 143/143 focused offline tests**, user clicked **same-session resume** on pre-v124 Rogue/Subtlety `240967` session `04fe21c0e61b180d305f`. Chrome still showed **3/6, 50%, cumulative Native3, cache0** and the previous `InjectionError:STATIC_TARGET_BELOW_DECLARED_FLASK_VECTOR`. **No new `V094_PROGRESS`, `V106_WORKER_STATE`, or worker-log bytes were supplied this turn**, so whether a worker restarted, whether it failed earlier, and the exact *new* underlying reason are NOT confirmed by that screenshot. The front-end rendered `p.error` from the old V094 progress ahead of the newer `p.worker.reason`, masking preflight failures.

## Concrete common resume defect in source

v124 added per-stat F/O search floor, requiring `B[k]>=F[k]-O[k]`; while correct for **new** searches, this changed the deterministic `v098.initial_seeds(B,lower,upper)` outputs because the old floor was typically L/user-only, while the new floor includes Rogue **crit133** (=Fcrit165-Ocrit32). An existing immutable pre-v124 `manifest.json` still holds its *original two seed vectors* and a `V094_SESSION_IDENTITY.json` from the first **three genuine Native candidates**. Rebuilding the same legacy session under v124/v125 can generate a different seed pair and fail at `v098.put_once(manifest.json)` **before reaching v094**, leaving the old progress error and zero current cache hits. This exact condition is a source-level reproducible root cause; user worker log is needed to definitively attribute the screenshot.

## Minimal generic fix, without changing existing session or Native cache

- `runner/v098_target_user_scenario_bootstrap.py`: compute the deterministic seed pair using **new common F/O/L floor** for all new sessions. If an existing manifest is already present, compute exactly TWO known deterministic policies:
  1. current F/O/L constrained seed generator, and
  2. old pre-v124 L/user-only seed generator.
  If the stored pair equals the new pair, proceed unchanged. If it equals the old pair, use it *only if both are still eligible under the new shared F/O/L bounds*. Any other seed pair or newly infeasible old target **blocks** with a specific reason. When a prior `simc_results/V094_SESSION_IDENTITY.json` exists, its sealed `seed_base_targets` MUST agree with the stored manifest: no changed manifest may repoint earlier real Native receipts. Do not silently adopt user-edited seed data; the original `put_once` full byte parity gate remains and all remaining manifest fields are regenerated/comparison-locked.
- This preserves exact v094 seed-session identity, historical case keys and all 3 stored real Native files; no increase in budget/Native calls. Future sessions still use current safe seed generation. Previous failed real material scout is now handled by v124 bounds and v125 correct `B+O-F` runtime input.
- `runner/webui/app.js`: if worker BLOCKED_OR_PARTIAL, render `p.worker.reason` ahead of **stale** V094 `p.error`; during running show current worker state. This is presentation-only, no cache logic change.
- Added 3 `tests/test_v098_target_user_scenario_bootstrap.py` offline tests: create pre-v124 deterministic seed manifest with a patched historical floor, then replay under current bounds and assert original manifest bytes unchanged, Native0 (Rogue and Shaman). Separately tamper with historical seed pair and assert strict block with no file replacement; a synthetic conflicting V094 Native identity also fails closed. Updated v114 UI static regression to check recent worker error precedence.
- JS V8 syntax parsing **PASS** via isolated evaluation. **No new Windows Python/CI run or user Native run after v126 has been observed**. Last 143/143 PASS belongs to v125, not this new source.

## Next focused local verification

Expected original 13 modules **146 tests** (previous 143 plus 3 v098 tests). Windows must use fresh whole-branch ZIP, preserve `%USERPROFILE%\SIMC_Secondary_Optimizer\runs`, test Python offline, then run the server from that same new directory and resume existing session once. Capture **`V106_WORKER_STATE.json` and last lines of `V106_WORKER.log`** if still blocked; these are required to identify new reason and are safer than inferring from stale UI. If past Native3 caches were valid, verify reuse via `cache_hits` and total new Native count, rather than retesting all candidates.

No main, v003 immutable, Project UI/Sources, Work OS M0/Shared State changes; P1 generic runner ownership unchanged.
