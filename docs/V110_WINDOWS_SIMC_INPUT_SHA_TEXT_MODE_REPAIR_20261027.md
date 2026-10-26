# v110 — Windows exact Native SimC input SHA fix; user real-run blocker

**2026-10-27 KST · isolated development branch.** This is a **minimal bug fix** to an existing Native input writer, not an optimizer, new item/SimC ability, gear database, Native retry sweep, or new session.

## User evidence and diagnosis

The user submitted `V094_PROGRESS.json`, `V094_SESSION_IDENTITY.json` and GUI worker log from the **first actual Windows Run / Resume**. The durable progress reported `PARTIAL_OR_BLOCKED`, `PipelineBlocked:WRITTEN_SIMC_INPUT_SHA_CHANGED`, `completed_jobs=0`, `new_native_attempts=0`, `cache_verified_hits=0`, `progress_percent=0.0`. Identity binds to actual local Windows binary SHA `b0ea12ee3ac233a4a590609e2a5bd4c4db45c5f8ae6f8994b1b8d0de4d5acff4`, Git revision user `7bc1071`, default Paladin `B=3150`, oil `O=crit16+haste16`, `T=3182`, six planned calls. **No Native SimC invocation occurred.** The original `V109_READINESS_12b374bfca.zip` was correctly PASS PLAN ONLY, and did not exercise this input writer.

The source of failure was **`runner/v065_original_scheduler_native_bridge.py`**, `execute_one`: `source_file.write_text(req["input"],encoding="utf8")` followed by strict binary byte SHA check against `req["input_sha256"]`. Windows text-mode I/O writes CRLF while request SHA is over exact `req["input"].encode("utf8")` LF bytes, so it fails *before* Native launch. This is not a SimC damage model/CHMV budget bug or evidence that the user Windows executable is invalid. Preserve exact-SHA failure policy and original SimC source inputs.

## Minimal implementation

Changed **one production line** to `source_file.write_bytes(req["input"].encode("utf8"))`. This guarantees identical hashed input bytes on Windows, does not alter the generated SimC semantics, strict SHA verification, Native budget, cache, stats, B/O/T, oil mechanics, 95% interpretation, or source-pinned upstream fixture files.

A failed prior run may have left `search/seed_00/input.simc` with CRLF but no `result.json` or `native_receipt.json`. Existing `execute_one` already checks for a genuine Native cache before the writer and **overwrites input-only** on retry, so **do not delete or rename the durable user session**. Existing real Native JSON2 and receipts, if present, still demand unchanged byte hashes and cannot be rewritten as an unverified cache.

Added `tests/test_v110_windows_exact_simc_input_bytes.py`: exercise actual `execute_one` with old CRLF input-only artifact, compare written bytes with SHA-pinned request, mock subprocess before it starts any executable, confirm zero real Native, and separately confirm cancel flag prevents writer and any subprocess. Hooked into existing P1 Linux and real Windows CI with strict Python exit propagation.

## Verified

- [Linux Actions #40353033880](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40353033880) **211 offline tests / 0 FAIL**, pilot and py compile PASS; **new Native 0**.
- [Windows Actions #40353069849](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40353069849) **22 Windows tests / 0 FAIL**, Windows 2022 Python, SHA-matching CRLF old input corrected before simulated subprocess, old durable v106 lock/cancel and six-source preflight; **new Native 0**. This is a simulated Native *input* path (mocked process), not a true Windows SimC DPS execution.
- Initial blocked user live Windows run **0 Native**, and the previous v105 real SimC [#40335091679](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40335091679) is a distinct Linux reference profile/binary; do not conflate.

## Exact next user step

**No new v109 zero-Native diagnostic and no version update needed.** In user's existing unpacked project directory, replace **only `runner/v065_original_scheduler_native_bridge.py`** with the latest isolated branch file (or update the branch in place); do **not** touch `%USERPROFILE%\\SIMC_Secondary_Optimizer\\runs\\abca493c00d6ee2599f1`, old `generated/manifest.json`, Native ledger, config or selected `simc.exe`. Close/relaunch the GUI to load the updated Python module; set the same Paladin 334/default user selections, binary and revision `7bc1071`, click **실행 / 동일 설정 재개** once. The stale CRLF `input.simc` gets safely overwritten if it lacks verified Native output. If new SimC errors appear, capture the **unmodified V106_WORKER.log and/or stdout/stderr from only the relevant case** and stop rather than repeatedly re-execute; don't demand full char profile or any credential. If the run completes before Cancel, it is a valid Windows Native integration smoke, no extra cancellation run needed.

**Remaining:** actual Windows Native completion/95%-output and interactive cancellation/resume **not yet proven** by this fix. Deployment app vs HTML/Cloudflare deferred per user's request. Product target **27 DPS** only; tank/healer excluded. No main merge, immutable v003, official Work OS or Project UI modifications.
