# 2026-11-08 P3-HN — original v216 real G/J/F/O→v222→v212/v217 READY, one exact-build case

**Decision:** REUSE original source owners and existing v217 seals; CONNECT the previously missing season nominal J input in the existing live T1 entry. This is one narrow real product Environment Build proof, **not** new-season self-update completion or user DPS E2E.

## Change and triggering evidence

- Isolated branch `probe/chat-cache-v035-20261024`. Code+two targeted tests: `68daa4801709b7c2e03b92e2fb5971ea24020336`. The T1 entry `integration_probes/p3_fr_zero_base_t1_acceptance.py` now passes the existing `v271.load_packaged_season_nominal_source(game_build)` value into original `v216` just as regular `v113` does; missing/other-build source remains PENDING. **No changes** to G/J/F/O source owners, v222 arithmetic, v212 installer or Native effect engine.
- Offline focused [#42460176730](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42460176730): **404 tests=402 PASS/2 SKIP, 0 FAIL, DEV_LEDGER_PASS; Native0**; added two exact-build/no-cross-build T1 tests.
- One-shot request file formatting only `c7fa97894f1fe6404b5cdda09e852e19b1609005`; identical JSON selection/limits. Live actual original v216 [#42460255527](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42460255527) **SUCCESS / ZERO_BASE_T1_PASS**, final current retail `12.1.5.70783` and exact pinned SimC revision `c20e2ad52e4c33711f74272309a5748125175fe8`, binary SHA256 `980ed4640cecc3ed78b34ed0dc0363dbff2ed7d703174e9cc01f09d18570d36b`. Existing binary reused; no new compile.
- Actual live source stage `EXECUTED_AND_SEALED`, compiler missing `[]`, original owner G `EXACT_NATIVE`, J `VALID_SAME_SEASON_SOURCE`, F `EXACT_NATIVE`, numeric J/F source `SELECTED_J_F_NUMERIC_SOURCES_BOUND_UNADMITTED`, quality `SELECTED_J_F_OBSERVED_QUALITY_BOUND_UNADMITTED`, declared full gem profile `J_SIMC_DECLARED_FULL_GEM_PROFILE_SOURCE_ONLY`; original installer executed and cleared requires `[]`. Intermediate source-only labels are expected and **do not override the final installed receipt**.

## Official one-case installed budget

`ilevel=334`, representative paladin/retribution dwarf, selected physical flask item `241324`, special gem `240967`, four ordinary dual-stat types from the exact build, `N=5`, explicitly no oil:

| owner | official | source proof |
|---|---:|---|
| G | **2850** | current exact candidate G Native1, source SHA256 `d32a24587ea574efa5f65b6e0c121dad84d6598e176b78435ed65897925e3837` |
| J | **92** | four ordinary nominal 23 each; original v221/v230/v232+v271 source owner, source SHA256 `ee87a4b510088853e2724ebc86e6cf20c994beef4bc0eb3f188baa93a4f2ad8d` |
| F | **165** | exact selected flask F Native2, source SHA256 `cd8a9e7799fcdf4743c134cc866cbd5759dfd48f556b9de3194cacb757a10c8c` |
| O | **0** | explicitly no oil, v222 source-owner |
| **B** | **3107** | official `G+J+F` |
| **T** | **3107** | official `B+O` |

Actual `p3_fr_zero_base_t1_receipt.json` inside artifact `13608778148` was inspected: `installed_status=FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY`, `environment_ready=true`, `environment_installed=true`, `zero_history_requires=[]`; **3 new Native calls**, all within approved G1/F2/O0. The artifact includes an audit-only Native ZIP, **not** portable runtime cache; retention 7 days. The source SHA values above are scoped to this run, not arbitrary other representative items or future builds.

## Evidence / integration limits and next

1. **Now proven:** one exact-build real G/J/F/O/B/T `v216→v222→v212/v217` installed READY. Earlier [#42332836316](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42332836316) is preserved as prior NOT_READY; not rewritten.
2. **Not proven:** product's `v196/v220` actual *number of verified optional choices* (the T1 compact receipt does not expose `published_verified_option_count`), a persistent end-user web installation, multiple special gem choices, 26-spec or other-ilvl source G, cross-build content-identical incremental reuse, future-season nominal J automatic discovery, and **new READY→user `v098/v096/v094` actual DPS E2E**.
3. **Next CONNECT:** the existing `v098/v096` admitted-season path currently checks old session-scoped `v216.read_receipt` + v223 source; the new fresh `v212` installed manifest is a *different sealed type*. Reuse existing `v216.find_verified_installed_season_environment` and v217 stage receipt recheck to bridge it with no unverified source promotion; then real 1-user DPS 95% test. Do not rerun G/F Native3 just to repeat T1.
4. Same-season static cache and season source evidence reuse; DPS cache keyed separately. Do not use `F=165/J=92/G=2850` as universal constants. SimC owns gem/effect/APL/DPS. No independent effect gate, 26-spec Native sweep, all-item DB, gear recommendation, or new optimizer. No main merge, immutable v003, Project UI/Work OS or original main dev chat authority change.
