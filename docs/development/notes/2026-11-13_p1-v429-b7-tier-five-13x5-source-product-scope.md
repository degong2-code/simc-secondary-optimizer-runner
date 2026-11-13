# v429 — B7 직업별 5부위 원본: 70575·70783 구분과 봉인된 13×5 아이템 ID

- **Capability:** `TIER.SEASON`, `GEAR.SEASON`, `PRODUCT.E2E`.
- **Keywords:** B7, 13 classes, 65 tier pieces, head, shoulders, chest, hands, legs, v168, v245, v250, v251, v261, v276, v274, v191, v417, 70575, 70783.
- **Prior evidence:** [v428 B6](2026-11-13_p1-v428-b6-primary-stat-profile-native-scope.md), [v425 B3](2026-11-13_p1-v425-b3-ordinary-armor-real-native-json2-proof.md), [v417 Windows E2E](2026-11-13_p1-v417-bounded-post-bridge-product-e2e-once.md), [v276 tier bridge](2026-11-03_p3-cf-physical-v251-to-v191-tier.md).
- **Decision:** `REUSE` — B7 **generic/current_source/product_integration/historical PASS, COMPLETE in precise 13×5 source-identity and one actual selected 4pc user consumption scope**. Not a 5pc-equipped requirement; full 26-DPS Native proof; tier proc/loot-route certificate; B8 special/crafted slot reconciliation or B9 catalyst certification.
- **Changes:** 78 JSON/generated MD/tracker, B7 completion regression, current status/INDEX/START_HERE and this note. No season source, product profile, optimizer, SimC or cache code changed.
- **Verification:** [v276 focused #41628248531](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41628248531) tested dadf683c3b495e4c4e18c2891099c0817f59a7d7, 87 PASS/0 FAIL; [v212 both OS #43388059919](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43388059919) tested 0240a1796ba1f0898ec2512e58de8af330571442, each 487 tests/4 SKIP/0 FAIL; [current v417 #43394408756](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756) tested 89d4810baf5e05f1c5c6f355f39a5f35ca9ec4e7, [original ZIP #14021859656](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43394408756/artifacts/14021859656); [v251 #41454624275](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41454624275).
- **Remaining:** Historical data/current_season_tier_itemsets.json is build 12.1.5.70575; never claim that static snapshot has been updated to 70783. Current v417 compact receipt reports tier65 compilation but does not bundle individually auditable 65 item rows. v276 keeps season_membership_verified=false, requiring caution about all raid-season loot provenance. B8 4pc user-selected conflicts and B9 catalyst remain separate PENDING; final 26-DPS E2E PENDING.
- **Efficiency:** Existing v276/v251 sealed source and v417 read-only ZIP; new Native 0, HTTP/DB2 acquisition 0, duplicate source scans 0, product algorithm changes 0.

## 1. Historical versus current tier ID identity

data/current_season_tier_itemsets.json is a 70575 source with 13 class entries and 65 unique IDs. Example Hunter ItemSet2059: head271492, shoulders271490, chest271495, hands271493, legs271491. Those ID values must not silently be declared an independently re-verified 70783 per-item receipt.

Current build source path reuses same-build v245 structural 13×5 DB2 ItemSet/ItemSetSpell candidates, v250 active-raid bonus corroboration, v251 exact class/SetID/five physical ItemIDs/first-party SimC options and v261 sealed reuse. v276 checks actual pinned Wago ItemSparse/Item source SHA, all 65 physical IDs with per-class head/shoulders/chest/hands/legs, slot, class mask, ItemSet, armor and expansion, then hands compiler-compatible result to v274/v191. Changed build/set/slot, wrong ID or absent source fail closed. v276 still explicitly says season_membership_verified=false and does not establish universal acquisition paths.

## 2. Current KR 70783 actual consumption

Current v417 successful Windows run 43394408756 has v191 compiled tier65 after source-driven gear/tier catalog selection and verified installed v216/v212 environment, then Survival Hunter user-level ilvl334 real SimC DPS12/SEM/95% pairwise verdict. Its SHA-sealed original ZIP inner V343_NATIVE_INPUT_JSON2_RECEIPT.zip digest a9c29567577f178120eced8045edfaf5b64c61eb822ca128d0d3fbfd6abfc5be. Exactly 12/12 physical input and JSON2 use tier head271492, shoulders271490, hands271493, legs271491 at ilvl334. Chest268223 is intentionally non-tier. Every input/result original SHA matches. Fifth-tier chest ID is a source-roster option, but it was not equipped in this actual four-piece case.

Current 70783 source compilation counts 13×5=65 by original compiler invariant, while compact output does not supply 65 row-level entries for independent off-run per-ID enumeration. This is B7 source/selected-product scope, not proof that all 26 DPS equip every slot correctly, that 5pc is required or that all gear items are loot-acquirable.

## 3. Regression, limits and next

v276 focused CI 87 PASS includes original v191.compile_catalog actual invocation on synthetic 65 source ID rows, v217 cached receipt reuse without rescanning Item/ItemSparse, bad build/ItemSet/source SHA blocked and v274 integration. Current v417 validates real 70783 compilation and one selected 4pc Native path, not full 13-class Native. Next B8 owns dynamic 4-of-5 when special/crafted gear overlaps; B9 owns catalysts. Existing source cache, session identity and native results are unchanged.
