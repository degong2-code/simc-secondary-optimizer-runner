# v109 — Windows first user-assisted zero-Native readiness gate

**2026-10-27 KST · GitHub isolated branch ONLY.** Scope: user-assisted readiness before exactly one genuine Windows GUI/SimC cancellation–resume test. Product target: 27 DPS specs only; six source-backed DPS profile factories currently enabled. No tank/healer. No new DPS engine, optimizer, item DB or Native call in v109.

## Actual source findings / correction to previous promise

- `runner/v065_original_scheduler_native_bridge.py` currently invokes one SimC child via synchronous `subprocess.run(..., timeout=240)`, and `v094` checks existing `CANCEL` **between** jobs. Thus GUI clicking Cancel during a Native call is **deferred until that ongoing call finishes**; it is not immediate process termination. The UI and user guidance now explicitly state this. Valid cached Native data remain for the next run, and the same session continues from recorded candidate receipts. Immediate mid-SimC kill and rigorous partial-file automatic recovery are **not implemented**; don't silently claim it.
- `runner/v106_windows_simple_gui.py` adds button **“Windows 실행 환경 진단 (Native 0회) · ZIP 생성”**, while leaving existing start, cancel, resume, progress and user options as is. Change Cancel label and message to accurate **between-Native** semantics.
- `runner/v109_windows_readiness_diagnostic.py` does a **zero-Native** existing-source `v106.store_session→v098.build→v096 plan_only` with unchanged SimC exe/revision/cache identity and controlled 6-request max. It checks the presence and Windows `.exe`/MZ header of user's binary, source-backed profile, exactly 4 tier slots, B+O=T, per-spec 15/16 physical slots, total 6-call typed plan and no result dir. It does NOT execute the binary, infer Git revision, assert matching revision, test actual GUI clicks, test cancel/resume or report DPS.
- Diagnostic ZIP `V109_READINESS_<random>.zip` contains only `V109_READINESS_RECEIPT.json` and `READ_ME_FIRST.txt`: no full user settings, talent string, user profile, native JSON2, binary file, absolute personal paths, personal tokens or logs. File automatically placed in `%USERPROFILE%\\SIMC_Secondary_Optimizer\\diagnostics`; attempts to open folder on Windows. The normal complete private profile/session remains local.
- Both READY and BLOCKED give a bounded sanitized code; a **PASS_ZERO_NATIVE_PLAN_ONLY** does not certify real SimC binary functionality, hash/revision matching, or true Native DPS. User-supplied revision still must be consistent with the selected executable. The official SimC nightly download archive filename encodes the git hash; this can help the user populate that field, but the diagnostic cannot assert its identity from external naming alone.

## Actual evidence and preserved negative

- [Linux Actions #40347745139](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40347745139): 208 focused offline tests PASS / 0 FAIL; six source-backed zero-call plan cases, sanitized ZIP, corrupt revision/file, and mocked plan_only boundary.
- [Windows Actions #40348255520](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40348255520): actual Windows 2022 Tcl/Tk import, 19 focused Windows tests **PASS / 0 FAIL**, pilot PASS. **New Native = 0**.
- [Windows preliminary Actions #40347959568](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40347959568) had **a failed unittest** (missing binary reached PE header before missing-file check) but incorrectly showed green because PowerShell did not propagate Python exit code; this is **NOT a PASS** despite its GitHub conclusion. Fixed the actual missing-file detection and changed workflow PowerShell to throw whenever `$LASTEXITCODE != 0`. Final Windows #40348255520 now verifies true test exit status. Negative preserved.
- Historical [v105 Paladin real Native #40335091679](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40335091679): six **Linux** Native JSON2 and a 6/6 cache-only replay PASS. Not a Windows binary/GUI/interactive cancel smoke; v109 never re-runs them.

## Exact user participation requested (minimal and no initial DPS cost)

1. On Windows, download the current isolated branch as ZIP from GitHub, extract into a normal writable folder, install Python 3 with Tkinter. Double-click `START_SIMC_OPTIMIZER_WINDOWS.cmd`.
2. Select **성기사 — 징벌**, ilvl `334`, default source talents/trinkets, default consumables and 1 main-hand oil; no special equipment or embellishments for this first proof. This is the already source-backed Native path; no current-gear import.
3. Browse to the Windows **command-line `simc.exe`** (not `SimulationCraft.exe`, which is upstream's GUI). Supply the matching Git revision hash. Per [SimulationCraft official download guidance](https://www.simulationcraft.org/download.html), the nightly archive filename includes the build's source git commit hash; if uncertain, **send the archive filename before any Native call instead of inventing a revision**.
4. Press **Windows 실행 환경 진단 (Native 0회)** only. The resulting diagnostic ZIP will automatically open in its folder. **Attach this ZIP in the project chat. Do not upload `simc.exe` or full original profile.**
5. On receipt review, conduct exactly one actual Windows interactive start → allow at least one Native complete → press deferred Cancel → click same-settings Resume → verify 95% user result and SHA/cache evidence. Report failures verbatim. No broad 27-spec repetition or extra solver.

## Limitations / next step

The local desktop itself is inaccessible to this chat. Windows Actions can validate headless Tk imports, OS locks, file handling and zero-Native planning, but **cannot truthfully assert actual user mouse clicks or that a proper Windows simc.exe is installed on user's PC**. Do not claim fully delivered Windows Native GUI until the user runs it.

The next authorization is merely **user readiness ZIP with Native 0**, not a request to run repeated full DPS. Keep J138/F165/O/T exact, catalysts L fail-closed, user-selected Omnium existing source whole-loadouts only, and all 95% versus global-optimum distinctions.

**Authority:** isolated branch only; main, immutable v003, official Work OS/M0, Project UI, product origin v016 and main development-chat ownership remain unchanged.
