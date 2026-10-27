# v132 — 27 DPS scope: exact MID2 source corpus + bounded multi-spec smoke

2026-10-27. Isolated P1 development branch `probe/chat-cache-v035-20261024`. **NO new real SimC Native was run in GitHub Actions.** Product purpose remains target ilvl/total absolute CHMV optimized with SimC DPS, 95% only.

## Official source discovery and coverage

Pinned official SimulationCraft upstream MID2 repo commit `426ad85ecb1c5d9a1af166931478dabf29b42fdd` (not an unversioned floating URL). That commit has **24 base DPS MID2 profile files**. Seven were already locally pinned/source-connected (Fury, Retribution, Frost Mage, Beast Mastery, Subtlety, Elemental, new Outlaw). Additional **17 complete original source profiles** were copied by exact Git blob bytes and name into `integration_probes/fixtures/v132_MID2_*.simc`: Frost/Unholy DK, Devourer/Havoc DH, Feral Druid, Marksmanship/Survival Hunter, Arcane/Fire Mage, Windwalker Monk, Shadow Priest, Assassination Rogue, Enhancement Shaman, Affliction/Demonology/Destruction Warlock, Arms Warrior.

Three DPS specs **do not have a base MID2 profile at this pinned upstream commit**: Balance Druid, Devastation Evoker and Augmentation Evoker. MID1 has a Balance and Devastation profile but those are **not MID2-season-exact** and must not be relabeled as new official MID2 or optimized target 334 inputs. Augmentation cannot be invented. Exact user-friendly 27/27 integration therefore remains INCOMPLETE.

This adds **raw source supply for 24/27**, but **the P1 target-level representative UI/optimizer still exposes only the seven source-backed producer entries** and **only Retribution, Subtlety, Elemental have user-confirmed full Windows Native6/6**. Do not conflate source existence, offline acceptance, raw Native smoke, or target-ilvl optimizer completion.

## Shared no-fork smoke implementation

`runner/v132_dps_source_batch_smoke.py` is one shared, original-source smoke route for all 17 not-yet-source-connected MID2 DPS:
- `--audit` SHA-verifies the actual upstream Git blob for **each** stored original source, original class/spec/race/talents/role/APL and exact equipped 15/16 slots/trinkets, Native0.
- `--simc <local_binary>` runs **one bounded Native each, not six DPS optimization candidates**, max new 17; `iterations=35`, `threads=1`, each own `json2=result.json`. Original APL/equipment remains byte-preserved except those three explicitly generated runtime output directives.
- A successful result requires actual SimC exit 0 and valid JSON2 `sim.players`, not merely stdout/log text. Native errors/timeout become explicit per-spec FAIL status with native log in that case directory. A success receipt stores source SHA, binary SHA, full input SHA, iteration identity, JSON2 SHA. On future runs identical completed receipts are SHA-verified and reused; attempted FAIL not retried unless user explicitly supplies `--retry-failed`. `--max-new` bounds one invocation and defers unattempted cases without writing orphan inputs. Native results are **independent raw source smoke**, not v094 cached optimized DPS; no static cache or historical target gear is invalidated or rewritten.
- Summary saved in `%USERPROFILE%\\SIMC_Secondary_Optimizer\\batch_smoke_v132\\V132_BATCH_SMOKE_SUMMARY.json`, Windows completion opens the result directory. Individual case JSON2/log retained.
- Single command from ZIP project root: `py -3 runner/v132_dps_source_batch_smoke.py --audit`; then `py -3 runner/v132_dps_source_batch_smoke.py --simc "C:\\PATH\\TO\\simc.exe" --max-new 17`. Real --simc path must be the user's actual binary; no guessed filename.

## Exact automatic CI evidence

New push workflow `.github/workflows/v132_mid2_sources_batch_offline.yml` uses Windows 2022/Python 3.14 and Ubuntu 24.04/Python 3.12, no dependency install, **Native0**. Run [#40483323416](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40483323416) **SUCCESS on both OS**, each `Ran 4 tests ... OK`. Tests cover all 17 actual SHA/slots/APL, all original APL/gear retained when rendering standalone single-run input, at-most-one fake subprocess invocation with SHA verified cache replay and deferred cap/failed cases; fake subprocess output is clearly synthetic unit test, not Native receipt.

v130 user Windows 92/92 PASS and v131 Actions 252/252 plus Windows/Linux web 40/40 are earlier separate evidence. No new real Native result has been received.

## Next actual product P1

Use those Native smoke receipts to identify only invalid original profiles, while separately mapping the **24 source-provided class/spec/weapon/tier/consumable variations** through the already shared v127–v130 registry/parser/emitter, v101 representative gear, v122 runtime and v094 adaptive engine. This completes source discovery without class-specific new optimizer forks. Three missing MID2 official fixtures need their season-appropriate source, but don't block progressing 24 available. Reuse all prior Native evidence, no full expensive Native 6×27 campaign or global-optimum claim.

main, immutable v003, Project UI/Source membership, Work OS/Shared State unchanged.
