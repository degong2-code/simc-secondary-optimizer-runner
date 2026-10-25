# v064 — External adaptive proposal → Native SimC evaluator integration port

**Executed:** 2026-10-25 (KST). **Status:** OFFLINE_REAL_NATIVE_JSON2_REPLAY_PASS, original v015/v016 integration **NOT DONE**. Development continues in the **current chat**.

## Exact scope and design

- Official Project Source v1.2 remains authoritative: **`T=G+J+F`**, oil and trinket static ratings external to T, selected special nontrinket L included in G once. Never elevate v059 oil-inclusive experimental T3184 to product policy.
- SimC models all trinket, equipment, embellishment, gem and proc mechanics, default class APL, DPS. No independent proc support gate or effect emulator.
- Added `runner/v064_adaptive_evaluator_port.py` as a *small reusable boundary for an existing adaptive scheduler*. A future scheduler proposes exact `{target CHMV vector, iterations}`; this module:
  1. Verifies v061 scenario identity and v062 static native G/L/official T.
  2. Verifies SimC baseline class, race, spec, talents, role, fight time, targets, buffs and selected consumables.
  3. Verifies **every selected original SimC item ID, itemlevel, option and physical slot, including BOTH trinkets**, against the v061 scenario and exact v062 cached gear identities. Missing trinket static record is allowed; the *actual selected trinket input* must still be present.
  4. Uses exact v063 two-real-Native-witness numeric offset, scoped to the unchanged profile and pinned SimC revision. Re-rendered input preserves all SimC effect-bearing lines.
  5. Produces scenario/binary/version/candidate/iterations-identified stable evaluation key, removing filesystem `json2` destination from result cache identity.
  6. Accepts the actual Native JSON2, validates four requested final ratings, reads DPS mean, SEM, count, and only reuses cached results with intact JSON2 bytes + receipt SHA/case identity and consistent observed statistics.
  7. Returns an observed-best rating without pretending a global optimum and only flags materially different near-performing alternatives (pilot default at least 10% transferred rating and observed loss no more than 1%; both remain configurable; do not assert confidence separation without sufficient samples).
- Added `runner/v064_replay_v063_native.py` for zero-new-SimC replay of **two existing real v063 Native result.json files**. It verifies original input's stable profile and four `gear_*` numeric override values match generated replay candidates before using outputs. No new numerical DPS is fabricated.
- Added `tests/test_v064_adaptive_evaluator_port.py`: cross-profile rejection, selected item and flask drift rejection, budget/floor/cap refusal, binary version-dependent cache identity, JSON2 tampering refusal, numeric output and SEM, duplicate proposals, alternate stat-distance behavior and no forced near alternative.
- **Not implemented:** original v015/v016 source integration, actual adaptive candidate-generation policy, bounded multi-stage scout/guided/confirm search on new conditions, cross-class Native profile calibration, general source attribution of gem/enchants to G. Those remain future product work, not reasons to research SimC proc mechanics.

## Verified GitHub Actions and acceptance

- [v064 Actions Run #40167043876](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40167043876) **SUCCESS**.
- Trigger commit `b29a8043a38d9d1ceeb282dbd6d67f017d90b001`, path `.github/workflows/v064_adaptive_port_replay.yml`; exact source SHA and bounded request verified.
- Full regression **317 tests: 315 PASS, 2 SKIP**, plus pre-existing `pilot.py check` PASS.
- Reused [v063 true Native run #40165729165](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40165729165), two source `input.simc` / `result.json` case pairs; **0 additional Native SimC calls**.
- Artifact name `simc-v064-adaptive-port-zero-native-40167043876`, ZIP SHA256 `639b1909cc71b846f0c51940c6c3743ab69a922ae9ee849740bb5381ef65f39b`; CRC PASS. Contains `V064_REPLAY_RECEIPT.json`, two exact port requests and observations.
- Official pilot static `G=2849,J=138,F=165,T=3152`, previously measured net numeric `gear_*`→JSON2 offset crit0 / haste+165 / mastery0 / vers0 **specific to the 334 Arcane Mage profile**.
- Replayed actual:
  - A `600/1108/1115/329`, observed DPS 192374.47259241965 ±SEM 951.0125458611038.
  - B `750/958/1115/329`, observed DPS 192109.85803892397 ±SEM 1300.0174867656742.
  - Observed-best A; **statistically inconclusive A vs B**. Transferred stat rating 150/3152 (~4.76%), so zero 'materially distinct 10%+' near-performance alternatives. No global optimum.
- Real replay output retains `external_scheduler_attached:false` and `original_product_v015_v016_merged:false` deliberately.

## Exact next work

**Primary blocker for actual existing optimizer merging:** obtain byte-identical *original* v015–v016 scheduler, source identity and receipts; source was not found in the isolated repo or inspected current local test handoff ZIPs. Prior `v037_manual_budget_adapter.py` refers to v032 `v036_cloud_bridge` archived runtime, which is not present here as inspectable mainline source. Do not recreate an entirely different adaptive optimizer and pretend it reuses v015.

**Parallel tasks permitted without waiting for those original files:**
- Widen calibrated numeric offset protocol to more real character/spec/ilevel profiles, every one with its own two controlled Numeric CHMV witness outputs. Same hash scope, no effect gate.
- Adapt result-port cancellation, durable cache/resume, bounded search budget to an actual external scheduler once its source identity is verified. Prefer minimal code and no unnecessary Native evaluations.
- Examine **numeric** G/J/F separation from gem/enchant-laden static JSON2 fields without studying effect internals; avoid overclaiming single-profile rating parity as across-profile contribution proof.

No GitHub `main`, MAIN, Project Source, Work OS or Shared State change was made.
