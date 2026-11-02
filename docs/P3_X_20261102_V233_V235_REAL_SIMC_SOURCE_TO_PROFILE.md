# P3-X — Actual pinned SimC source → physical 14-slot profile, plus one-native execution adapter

Date: 2026-11-02 KST. Isolated development only; do not merge main, promote original v016, rewrite immutable v003, update Project UI, or transfer main product-chat authority.

## Engine purpose

Continue the user-approved **season-specific G/J/F/O → B/T → representative 26-DPS user profile → existing adaptive SimC** engine. Current equipment redistribution and season gear recommendations remain out of scope. Later, **only after engine completion**, perform the user's strict SimC-only **zero-base experiment** where all existing source catalogs, caches, historical G references and Native evidence are forbidden and access is audited.

## Implementation

- `runner/v233_source_only_G_probe_profile.py`: rederives the exact v232 source-only candidate from v229 source bytes + v231 tier receipt; rejects tampered candidate and unsupported DPS/race/talent syntax. Generates deterministic bare 13/14-slot SimC physical input with no trinket, gem, flask, oil, historical gear total or artificial `gear_*` ratings. SHA-256 receipt binds the source candidate, build, selected slots and actual profile bytes; status remains NOT EXECUTED, with all G/J/F/O/B/T null.
- `runner/v234_source_only_one_native_G.py`: **explicit one-shot Native runner** with `--max-new=1`, binary SHA256 pin, generated source-only profile and immutable new output directory. Stream SimC errors to disk, preserve original failed receipt and raw JSON2 if emitted. Reuse `v046.native_records`, its bare variant invariants and `selected_gear_sum` for static G; require 13/14 exact item IDs, slot aliases, level, no extra equipment/modifiers and matching SimC git revision. It returns an **observed G vector only**; final G/J/F/O/B/T remain null without independently verified compiled game build, active-season origin and other accounting. Default `--max-new=0` prepares but does not execute.
- `tests/test_v233_v234_source_native_G.py`: synthetic 13-slot paladin and 14-slot Fury, tamper/slot/unknown/SimC revision failures, explicit binary SHA, plan-only zero Native, mocked subprocess success/failure and preserved SimC log. **Mocked calls are not real Native evidence.**
- Manual `.github/workflows/v229_simc_only_source_seed.yml` now permits `probe_race` and `probe_level` to generate v233 input from successful v229/v231/v232 without executing a native binary. Its optional steps fail closed at that stage; initial immutable source acquisition remains independently preservable.

## Real upstream source compatibility evidence

Source commit pinned for this *historical same-build compatibility check*: `simulationcraft/simc@710c2408bfd3ae4df71b8cd55cdf01f63fd6c926`, generated WoW build `12.1.5.70575`.

- Real attempt [#41393439757](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41393439757) exposed a v229 bug: `item_data.inc` game-build header appears after the large stat table, not in first 512 bytes. Corrected.
- Next attempt [#41393622988](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41393622988) fetched and hash-verified four genuine SimC generated source files, identifying 415 set bonus candidate groups; v230 rejected real `0.000000f` C++ float suffix. Corrected to parse the generated form and keep bounded offending-row diagnostics.
- Final genuine source run [#41393829968](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41393829968): **success** across actual v229 collection, v231 mage/frost set ID 2060 5pc physical join, v232 exact 14 G-slot representative candidate and v233 real-source bare physical profile creation. Native **0**, G/J/F/O/B/T **not computed**. One compact GitHub artifact `v235-pinned-simc-source-compatibility-41393829968`, artifact id `13118382601`, GitHub artifact digest `sha256:13116fde14f793e815f978849991831b3e9cb7db24ad93ccb31752b31a84febd`, size 10,738 bytes. Large raw item_data data was *not archived*. Artifact retention is two days, not a permanent runtime dependency.
- Latest offline test [#41393789606](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41393789606): Ubuntu 260 PASS, Windows 260 PASS, 0 real Native. Earlier synthetic test [#41393210218](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41393210218): 259 PASS each. Tests and real source evidence apply **only** to their stated scope.

## Remaining P1 work

1. Active-season tier/ordinary gear provenance must be sourced/authenticated independently; SimC's generated item records contain historical sets and same-ilvl candidates. The source-only heuristic remains a **candidate**, not a confirmed new-season representative item pool.
2. Execute one exact pinned-binary Native physical observation only where it fills a genuine evidence gap. The v234 runner exists but **has not been invoked with a real SimC executable**. Its existing standard mode requires the already pinned source files at execution time and records binary/profile/JSON2 SHA without claiming compiled-build attestation. Avoid treating a GitHub artifact or synthetic JSON as execution proof.
3. Determine J/F/O highest-quality exact same-effect item IDs/ratings and weapon applicability, permanent E and special L accounting, then recompute B=G+J+F and T=B+O with manual T authority. Connect to v216/v222/v098 and the existing adaptive engine and 95%-only reporting.
4. For true zero-base final acceptance, use an actually restricted clean VM/FS/network, not merely the development job's sparse checkout. Seal new results before consulting old evidence.

Status: **real upstream source → valid physical candidate → generated SimC input verified; actual Native static G, full new-season environment and full optimizer integration pending**.
