# v065 — Authenticated v015 Original Lineage and Sequential Adaptive Native Integration

**Date:** 2026-10-25 (Asia/Seoul). **Official Product Source:** `SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.2_PROJECT_SOURCE_REPLACEMENT.md`. **Execution identity:** isolated GitHub branch; **no change to `main`, Work OS, Shared State or Project Source**.

## Original v015/v016 ZIP: direct independent read-only verification in THIS chat

The user supplied `SIMC_v015_v016_ORIGINAL_SOURCES_HANDOFF.zip`; the current chat read the actual archive bytes and its full internal `SIMC_v015_v016_ORIGINAL_MANIFEST.json` and `SIMC_v015_v016_SOURCE_STATUS.md`:
- Outer ZIP size **2,256,613 bytes**, SHA256 **`d2b3b75011c98cdca4ad937f071ac48a6dcf743b5284d6be8a5cb2157705ac16`**, CRC PASS.
- **38 ZIP entries**, including 37/37 correctly matching internal Manifest entries, byte-size and SHA256 verified.
- Embedded original v015 ZIP SHA **`d7a580f11a8d4ae2687fa529b752645340be872ed177ff586ba6cbe4c9efe3e9`**, CRC PASS, 11 entries.
- Embedded original v016 ZIP SHA **`456a217d4b48799d863262c6d047f6e0841b608617f9393caf410e25aebb3761`**, CRC PASS, 21 entries.
- Preserved v017 ZIP **`da6098e5ffb7ee7e5f9b518b6323e62bdc66c6d578f97c1b7c370486b850d156`**, CRC PASS, 28 entries.
- Preserved v018 ZIP **`17c2ed616b3ca076ea008ace256da943fe754cddb1a8bff69d13a043a7c880d1`**, CRC PASS, 47 entries.
- Independently compared nested archive file bytes: **v015→v016 11/11 identical; v016→v017 21/21; v017→v018 28/28**.
- Exact original `CHMV_ADAPTIVE_v015.py` SHA256 **`a44f73cf232c8204dbe958e79fe50f111e68654ac583a1170a283f16035c0ec3`**, exact original `SCENARIO_CONTRACT_v016.py` SHA256 **`7c49d7ca095e8864b673715d70d9851d676b44aeed99f8d769419492fcd14712`**.
- **Original source bytes never edited**. The historical **v015 71/71 and v016 104/104 are only past offline receipts, NOT current tests and NOT historical Native execution PASS**. v015 original new Native calls recorded 0; historic v015 Native result package not found.

Read-only receipt produced by current chat: `SIMC_v015_v016_READ_ONLY_AUDIT_CURRENT_CHAT.json`, independently verified.

## How authentic source was reused

- `runner/v065_v015_scheduler_adapter.py` ports **only original v015 decision principles** `neighbors` (one-stat to another step transfer preserving T), `choose_next` (pick best observed raw DPS anchor, ignore already measured CHMV, use mirror only for candidate ORDER), `confirmation_pair` (choose top two *distinct CHMV vectors* from observed raw means), `judge` (fresh pair + standard error, no global optimum, seed distinction when claiming directional confidence).
- `runner/v065_original_scheduler_native_bridge.py` connects those choices to the already verified **v061 class+gear Scenario / v062 exact Native static G,L / v063 profile-scoped `gear_*` numeric injection / v064 JSON2 DPS/SEM and SHA validated result-cache port**.
- Current official policy is **T=G+J+F**; selected 334 Mage `G=2849,J=138,F=165,T=3152`, with oil external to T. Profile's measured offset 0/+165/0/0 is strictly its own, **not applied to other classes or profiles**.
- **Do NOT reuse legacy** `BUDGET=3000`, 60-second Mage scenario, SimC 1210-01 7bc1071 Windows binary, old pre-pinned mock-only receipts, historical seven-observation external paths, old sample-specific `make_input` and `parse_result`, or v016's legacy execution-ready assumption. Original code is **not patched/modified or imported in runtime**; it remains historical source.
- Reuse two actual prior v063 Native samples as anchors (not v015 historical samples), scout cap 2 × 60 requested iterations, independently new confirm cap 2 × 320 requested iterations, total new SimC attempt cap 4; each case has exact bound source, receipt and Native JSON2. Restart uses verified SHA-preserved cache and recovered cumulative Native call budget.
- Cancel marker supported before a new case; partial/corrupt cached result causes a **block**, not silent reuse or second SimC invocation. No independent effect support/proc Gate.

## Real Native run evidence

- First direct initial CI attempt [#40171226389](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40171226389) **FAIL**: five new test-harness positional argument errors (binary and case folder swapped), **Native calls zero**. The FAIL is preserved.
- Corrected CI [#40171473855](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40171473855) **SUCCESS** (trigger commit `efaa2db260168d7323837722be9e95d2d34a8009`): **345 current tests run; 343 PASS / 2 SKIP**, plus legacy `pilot.py check` PASS. Historical original v015/v016 tests **not run**.
- Prior v063 Native evidence 2 cases reused, **4 new Native** simulations (2 sequential scouts, then 2 freshly confirmed at 320 requested iterations), 4/4 target-to-final-JSON2 CHMV full rating parity PASS, strict SimC binary `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`.
- Entire CLI invoked again in the same run; **all 4 cases verified from disk receipt + JSON2 SHA256 and no additional Native calls**; cumulative `native_attempts=4` remains intact.
- Real produced outputs:
  - Scout 0 target **500/1108/1115/429**, DPS **192341.22593272393**, SEM **1142.3084699802773**, count 59;
  - Scout 1 target **700/1108/1115/229**, DPS **195407.5057323584**, SEM **1330.6223960273117**, count 59;
  - Fresh confirmation 0 target **700/1108/1115/229**, DPS **192644.3811071584**, SEM **563.0488538716795**, count 319;
  - Fresh confirmation 1 target **600/1108/1115/329**, DPS **192445.9620748212**, SEM **519.8403011718842**, count 319.
- Two distinct SimC seeds observed in fresh confirmations. DPS difference **198.419**, normal-approx confidence halfwidth **1501.974**: statistical direction **NOT** supported. No global optimum claim; the high scout 195407 point regressed upon 320-iteration confirmation as noise can.
- Artifact `simc-v065-original-adaptive-two-scout-two-confirm-40171473855`, SHA256 **`9e74e1664befc6b3c11151426c72d527d737d022fe714db5dbe89cbd57ca231f`**, 24 zip entries, CRC PASS, all prior/on-run inputs, JSON2, stderr/stdout, progressive and full receipts.

## Remaining scope

Original **v015 algorithm decision policy** is now implemented and evaluated using real SimC, but the original source executable is not installed as a permanent runtime dependency; `product_v015_v016_original_directly_merged:false` in receipts is intentional. **v016 original JSON contract is historical comparison/negative test reference**; current official v061/v1.2 has authority. Not yet finished: generic profile numeric calibration across all specs, persistent cross-job candidate search and cache UI, cancellation UX, convergence strategy and near-best alternatives across multiple specs. No cross-spec Native PASS claim.

**Next implementation**: separate new adaptive case execution from the Mage-only bounded bridge; accept v061 normalized scenario + v062 G/L + profile-specific v063 numeric witnesses, with durable bounded candidates / resume and minimal Native calls. Ensure final JSON2 policy parity before allowing broad cross-spec execution.
