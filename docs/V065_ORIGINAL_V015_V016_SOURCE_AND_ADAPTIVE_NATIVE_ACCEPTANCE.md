# v065 — Original v015/v016 source verification and bounded adaptive integration

**Date:** 2026-10-25 KST. **Current state:** **PASS for isolated v065 334 Arcane Mage adaptive Native pilot**; not product v016 full merge, global optimum, general specs, general gem attribution, or MAIN/Work OS promotion.

## Source handoff — newly independent checked

User's actual prior-chat package `SIMC_v015_v016_ORIGINAL_SOURCES_HANDOFF(1).zip` was materialized **read-only** and inspected (do NOT modify this ZIP or extracted originals).

- Outer ZIP **2,256,613 bytes**, SHA256 `d2b3b75011c98cdca4ad937f071ac48a6dcf743b5284d6be8a5cb2157705ac16`, 38 entries, ZIP CRC PASS.
- Outer internal Manifest `SIMC_v015_v016_ORIGINAL_MANIFEST.json`: **37/37 actual files size and SHA256 PASS**.
- Four intact inner archives (all CRC PASS):
  - v015 `SIMC_SECONDARY_OPTIMIZER_PILOT_ADAPTIVE_v015.zip` SHA `d7a580f11a8d4ae2687fa529b752645340be872ed177ff586ba6cbe4c9efe3e9`; **10/10 internal manifest entries SHA/size PASS**.
  - v016 `SIMC_SECONDARY_OPTIMIZER_SCENARIO_CONTRACT_v016.zip` SHA `456a217d4b48799d863262c6d047f6e0841b608617f9393caf410e25aebb3761`; **20/20**.
  - v017 lineage `SIMC_SECONDARY_OPTIMIZER_CHMV_ALLOCATION_v017.zip` SHA `da6098e5ffb7ee7e5f9b518b6323e62bdc66c6d578f97c1b7c370486b850d156`; **27/27**.
  - v018 lineage `SIMC_SECONDARY_OPTIMIZER_SIMC_NATIVE_DISCOVERY_v018.zip` SHA `17c2ed616b3ca076ea008ace256da943fe754cddb1a8bff69d13a043a7c880d1`; **46/46**.
- Verified extracted source: v015 `CHMV_ADAPTIVE_v015.py` SHA `a44f73cf232c8204dbe958e79fe50f111e68654ac583a1170a283f16035c0ec3`; v016 `SCENARIO_CONTRACT_v016.py` SHA `7c49d7ca095e8864b673715d70d9851d676b44aeed99f8d769419492fcd14712`.
- Source-status's preservation chain v015→v016 (11 byte-identical), v016→v017 (21), v017→v018 (28), and v015/v016→v018 preserved. No source files changed by current work.
- **Historical only, NOT rerun:** v015 71/71 = offline/mock; v016 104/104 = offline. Original v015 explicitly `real_new_simc_runs=0`, v016 no SimC. No actual v015 Native results receipt was supplied.
- Source-status says v015 actual fixed pilot `BUDGET=3000`, Mage, 60-sec Patchwerk, `+165 haste`, pinned build, only 7 past vectors; no durable cache/resume/cancel. v016 was an **offline-only** input contract; not a Native optimizer nor a completed v015 connection.

## Reuse and exact separation

Reused/ported **v015 policy only**: transfer a step 100/200 across CHMV preserving integer total, reject duplicates/violated floor/cap, raw-DPS search anchor with optional opposite-neighbor ordering only, one new candidate after each measured JSON2, then top-two independent higher-iteration confirmation and SEM-based approximate CI with native seed caution.

**Never import as global facts:** old `BUDGET=3000`, original Mage-only profile, `+165` constant, 60-second Patchwerk, original SimC executable SHA/build. The current pilot `T=2849+138+165=3152`, gear/effects/JSON2 handled exclusively by current v061–v064 contract and the pinned v063 real Native sample. Temporary weapon oil remains **external to official T**, not silently included. This special numeric offset `(0,+165,0,0)` is valid **only for this exact verified profile**.

Original v016 validation and policy should inform **current v061 regression review**, not replace approved v1.2 source or v061 input contract wholesale. No WEQUIP authority. SimC alone models proc, trinket, embellishments, APL, DPS; no independent proc fidelity gate.

## Current implementation and real receipts

**v065 A: source-provenance-golden guided acceptance**
- `runner/v065_original_v015_search_adapter.py`, `runner/v065_v015_guided_once.py`, tests & bounded workflow.
- Direct read-only old v015 `choose_next` example with official 3152 and real v063 observations yielded directed **step200** candidate `400/1108/1115/529`, and v065 new adapter proposed the **same exact CHMV**. One **new** Native SimC sample:
  - [Run #40171255554](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40171255554) **SUCCESS**: 345 tests (343 PASS / 2 SKIP), existing `pilot.py check` PASS, **1 Native new**, 2 prior Native historical input/results reused; actual rating equals `400/1108/1115/529`, DPS **192869.22024971354**, SEM **1100.883329264746**, samples 59. `v065` checkpoint shows scout1 done, confirmation pending, `max_native_calls=2` in this **separate bounded path**.
  - First run #40171134917 **FAIL** due unrelated v065 safety tests using incorrect function argument order; preserved. Fixed safety tests then PASS. Full output archived as GitHub Actions artifact `simc-v065-v015-guided-once-40171255554`, SHA256 `3a222949c8fe37b4e4e9bc390a1029efa3ad69e15d32d61316320dc683da4aeb` (ZIP CRC PASS).
- This single case is **not** a fresh two-candidate confidence confirmation, not an optimum, and not the original v015 program executed unchanged.

**v065 B: bounded 2 scouts + fresh 2 confirmations**
- A second v065 implementation is present in the **same isolated branch**: `runner/v065_v015_scheduler_adapter.py` and `runner/v065_original_scheduler_native_bridge.py`. It likewise ports original v015 decision rules, not the original source runtime. **Two v065 adapter pathways exist** and should be consolidated in a follow-up for structural simplicity and to prevent two competing schedulers. Do not delete evidence or conceal both implementations.
- [Run #40171473855](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40171473855) **SUCCESS**: 345 tests (343 PASS / 2 SKIP); **4 new SimC Native calculations** (2 scout at 60 iterations, 2 separate confirmation at 320 iterations), prior v063 two real Native scenarios reused. Every final JSON2 CHMV = target and each DPS+SEM numeric valid. It **reused all 4 Native results on restart with 0 new calls** (the receipt still reports 4 cumulative attempts from the original run).
  - Scout `500/1108/1115/429` DPS **192341.22593272393**, SEM **1142.3084699802773**.
  - Scout `700/1108/1115/229` DPS **195407.5057323584**, SEM **1330.6223960273117**.
  - Fresh confirm `700/1108/1115/229`: DPS **192644.3811071584**, SEM **563.0488538716795**, SimC seed `11359473648599128320`.
  - Fresh confirm `600/1108/1115/329`: DPS **192445.9620748212**, SEM **519.8403011718842**, SimC seed `16909982673534721718`.
  - Difference first−second = **198.4190323372 DPS**, approximate 95% difference halfwidth **1501.9744459259**; distinct SimC seeds observed; statistically **INCONCLUSIVE**, no global optimum.
  - First 4-call workflow #40171226389 **FAIL** (same test harness defects; retained), retry #40171473855 PASS. GitHub artifact `simc-v065-original-adaptive-two-scout-two-confirm-40171473855`, SHA256 `9e74e1664befc6b3c11151426c72d527d737d022fe714db5dbe89cbd57ca231f`, ZIP CRC PASS.
- A high preliminary 60-iteration scout DPS is **not** a confirmed win: `700` scout scored 195407, but fresh 320-iteration confirmation measured 192644; statistical conclusions use the two fresh confirmations instead.

## Remaining tasks and caution

1. Consolidate the **two distinct v065 guided scheduler pathways into one** canonical v065/v066 scheduler using v015 authentic source policy and current v064 evaluator. Preserve original implementation receipts; avoid duplicated helper modules and implementation drift.
2. Preserve state/cancel/resume: `v065 B` has bounded per-case verified file cache, atomic progress receipts, cancel-file before each new case, and restart with no new Native calls; this is **not yet a universal durable Windows/local production cache**, not cancellation of an already-running SimC process.
3. Show near-performance alternatives with configurable material CHMV distance & statistically honest uncertainty; larger scenario portfolio, other classes/tanks/healers and other target ilvls still require profile-specific measured numeric offsets and exact native G. Source v016 is historical, and no full product or main merge is claimed.
4. Code efficiency: current bounded checks use ~345 tests and tiny 4-vector candidate operations. Do not add effect certification jobs, whole season equip DB or duplicate runtime.
5. Official `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` tracks branch development only. Do not claim official Work OS M0 PASS, immutable v003 overwrite, Github `main` promotion, or original v015/v016 source mutated.

**Current user wants development to continue in this chat, not move chats.**
