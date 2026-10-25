# v077 — Profile-neutral first-use readiness and two-witness input planner

Date: 2026-10-25 KST. GitHub isolated branch only. Official Developer Notes v1.2 consulted, product/Work OS promotion not performed.

## Actual verification and limits

- GitHub Actions [40196041065](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40196041065): **SUCCESS**, trigger commit **fd312d31e096c31f142d253ee9561dc747d531a4**.
- Python suite **421 tests, 419 PASS / 2 SKIP**, includes **7 newly added synthetic/offline tests**.
- Artifact ID **12599474931**, name simc-v077-first-use-offline-40196041065, GitHub-reported digest **sha256:0fcaa6ec0eb85265afaf869842bc708124948b47ae78707dc4918a576e48f0b0** (metadata verified; raw artifact ZIP not independently CRC audited).
- The NEW module runner/v077_generic_profile_bootstrap_readiness.py does NOT run SimC. **New Native = 0**. Real newly selected Elemental Shaman, Beast Mastery Hunter, Fury Warrior, Retribution Paladin representative profiles have NOT been assembled, admitted by Native, or confirmed. The Mage/Warrior fixtures in these tests are expressly synthetic. Existing real Rogue/Mage historical evidence is preserved and not relabeled new cross-class acceptance.

## What v077 implements

v077 consumes explicit scenario JSON with exact class/spec/race/talents/role, exact user/standard-sourced whole SimC profile, user-selected precise tier/special/crafted/trinket IDs, a caller-provided complete nontrinket representative filler set, and existing same-season v046 exact Native static cache. It does NOT create a new equipment database, gear recommendation engine, race eligibility resolver, APL/proc gate, or per-class optimizer.

1. v061.normalize validates official scenario. The new input_item_map verifies **ALL** selected + filler equipment rows, exact ID, ilvl and options, profile class/spec/race/talents/role and combat; SimC remains solely responsible for actual item legality and effects.
2. v062.check_filler and compile_static_budget compute **G and fixed L only from genuinely known exact Native variant records**; unknown selected trinket stat rows do not block and are NOT assumed zero. For missing nontrinket variants v077 returns an explicit identity list, not guessed static data or a fabricated readiness PASS. Existing v046 same-season stat cache is NOT invalidated just because SimC revision changes.
3. v077.paired_input generates two 35-iteration **RAW gear_*** numeric witness inputs for the same exact stable profile. A deterministic 50-rating transfer changes distribution, not total raw input rating; JSON2 absolute outputs are not known until a real SimC run and profile-scoped native offset calculation. The two sources preserve all gear IDs/options, race, talents, gems, enchants, conditions and APL bytes; only gear_* rating, iterations and JSON2 destination may differ. The outputs are INPUT FILES, **not Native JSON2 receipts**.
4. If exact static nontrinket variants are present, v064.verify_profile_binding is applied to the real complete static budget. Status READY_FOR_TWO_NATIVE_CALIBRATION_WITNESSES means **preflight readiness to run Native**, never that calibration or DPS has been confirmed. If variants missing, return BLOCKED_EXACT_NATIVE_STATIC_VARIANTS_MISSING, even with a manual T.
5. Existing output files are not silently overwritten. Existing partial/current Native JSON2 or native_receipt in the proposed witness directories causes a blocker, with separate existing real-witness import required.

## Known remaining prerequisites

- The actual 6-case proposed matrix from v076 covers cloth/leather/mail/plate, six physical weapon compositions and six different proposed races. No real profile/source item IDs were invented in v077. The new API requires **caller-supplied exact SimC profile + filler + existing static cache**; this is not a full automatic profile producer yet.
- **v078** should source a real SimC-valid additional DPS archetype, obtain exact representative item IDs/options from explicit standard profile, reuse/hydrate only genuinely missing exact nontrinket static variants, then run two real bounded profile-specific witness measurements and ensure constant observed input-to-JSON2 rating offset. Only THEN call v066.prepare and existing v067 generic execution route; do not copy Mage/Rogue offset or relabel an offline ready manifest Native PASS.
- Profile-specific native bootstrap execution/caching, including handling a witness whose post-calibration total may not match official T, is not implemented in v077. Treat as an open dependency rather than assuming an automatic 2-call completed setup.
- Following user scope guidance, v077 test matrix covers DPS roles only. Original approved v1.2 explicitly still includes tank/heal; no official source/role policy is changed or silently promoted.
- T=G+J+F; oil O outside T; no double-counted special L, crafted 50/50 starter stats are not fixed floors, SimC alone responsible for combat/effects/DPS; no changes to v003, original v015/v016, GitHub main, Work OS, Project Sources, or shared state.
