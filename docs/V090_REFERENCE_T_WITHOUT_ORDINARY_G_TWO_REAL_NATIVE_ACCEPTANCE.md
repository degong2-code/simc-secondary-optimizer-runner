# v090 — Reference T3150 to real SimC DPS candidates without ordinary-item G cache

**2026-10-26 · isolated development only · actual Native 2 runs.**
This completes **one scoped Frost 334 reference-T static-c DPS evaluation connection**. It is NOT an original v015/v016 optimizer merge, a full adaptive search, a globally optimal DPS conclusion, a new proc/effect Gate, an unapproved modification to formal T=G+J+F, or a Work OS promotion.

## 1. Source contracts and lightweight route

Approved developer notes v1.2 and user direction are applied narrowly: ordinary representative items retain precise ID, ilvl334, options, 4 tiers, two trinkets, profile APL, primary stats and weapons, but **their individual static G variant cache is not required** to establish a chosen **reference T=3150**. Selected **special-item fixed L** remains exact Native-only, subtracted as an already-in-T floor, never fabricated. Out-of-T oil O is not added. Source provenance remains `reference_rounded_opt_in`; manually specified totals still take priority in v089 and old native-exact G route remains intact.

Implementation:
- `runner/v090_reference_total_native_candidate.py`: takes verified v089 reference selection and original v061 typed scenario, calls *existing* v062 for all selected/filler gear, missing G tracking and exact special L, reuses *existing* v065.bounds/eligible, v063.static-c input renderer, v064 profile binding and its Native DPS/SEM ingest contract. Native gear G cache entries are NOT faked as 0.
- `runner/v064_adaptive_evaluator_port.py`: when v090 explicitly provides `reference_exact_slot_identity` with bound provenance, include missing ordinary gear **ID/ilevel/options** in the same exact source-profile validation, rather than silently ignoring gear slots absent from the Native G cache. Old exact-G paths remain unmodified.
- v090 candidate proposal now binds **full original SimC profile SHA from prepare to propose**, including APL; profile mutation is blocked. All other v061, v062, v063, v065, v066 and v089 modules untouched. Only two minor reusable changes total (v064 identity extension and v090 adapter).
- `tests/test_v090_reference_total_native_candidate.py`: actual upstream-SHA-pinned v084 Mage Frost source factory, all 16 selected slots and empty ordinary G cache, two targets, candidate SHA cache identity, profile/talent/APL/slot tamper rejection, native-cache fixture for special fixed L, missing L fail-closed, original exact mode not treated as reference. The `test_selected_special_L_requires_actual_Native_static` uses a controlled **unit-test synthetic cache entry**, not evidence of a real special-item Native run in this stage.
- Total 334 target c: `(900,800,800,650)` and `(800,900,800,650)`; selected `F=(165,0,0,0)`; thus SimC `gear_*` raw `(735,800,800,650)` and `(635,900,800,650)`, respectively. The four static-c rating totals equal **3150**. `buffed_stats` are **observed after SimC talents/buffs** and are never inverted into target c.

## 2. CI regressions / failure preserved

- **Failed first [Actions #40254864745](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40254864745)**: new v090 code treated legacy `v065.bounds()` return `(T,lower_tuple,upper_tuple)` as a mapping, yielding 4 errors among 508 tests. Production corrected by calling **existing v065.eligible(tuple, T, low, high)** rather than adding a duplicate eligibility algorithm.
- [Actions #40254982702](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40254982702) SUCCESS: **506 PASS / 2 SKIP**, 2 exact candidate profile inputs emitted, SimC 0 calls.
- Additional one-off SHA safeguard for original profile input, plus one APL tamper test. **Final [Actions #40255443827](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40255443827) SUCCESS: 507 PASS / 2 SKIP out of 509**, `runner/pilot.py check` PASS. Source git object SHA pinned. Final 2 candidate inputs byte-identical to first PASS artifact (A SHA `763cc348...`, B SHA `a4066814...`), and original source input identical. Artifact `simc-v090-reference-static-input-40255443827`, **ID 12622083234**, zip SHA `eae51dae726eec45f12ed4a875e4c8159906538cc4110c465fa4d085d7357f5e`. Historical 2 skips = v037 optional local v036 runtime fixture absent; NOT v090 skipped checks. No Native executed on Actions.

## 3. Actual new SimC real Native, separate from CI

Original CI artifact exact `input.simc` files and **existing pinned SimC ELF** SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e` (revision `7bc10711b5`) were extracted into the working Linux execution environment. Each candidate input was altered in **exactly one line**, solely to point `json2` at a writable local output path. Both binaries returned **exit 0**, JSON2 `report_version=2.0.0`, 35 requested iterations, **34 DPS samples**, 16 gear slot ID/ilvl/options exact input ↔ Native JSON2 match, APL/talent and combat/consumable settings unchanged. **Exactly 2 new SimC calls**.

| Result | Static CHMV target c (CH/H/M/V) | DPS | SEM | Native JSON SHA256 |
|---|---|---:|---:|---|
| A | 900/800/800/650 | 182187.45 | 784.02 | `56ecfc627a2c6aa819c4cc24d76cfb73a82b4c94ec8b5e294e4667efbcf5e841` |
| B | 800/900/800/650 | 178882.07 | 892.32 | `476a36d8f4877bc8d29cd52390f45195fd32796b7edc14479b86492355ebe3c0` |

JSON2 buffed stats A `918/857/816/663` and B `816/964/816/663` are intentionally different from static-c. A minus B DPS = **3305.39**, illustrative approximate independent-SEM 95% difference halfwidth **2328.13**, so these **two bounded candidates appear separated under that approximate criterion**. This alone does NOT prove a global DPS maximum, nor validate all classes or near-optimal alternatives. Warnings from SimC stderr (`Implementation Not Yet Verified` for particular effects and harmless item display-name inconsistencies) are preserved; **no item effect/proc independent certification or extra Gate** introduced.

Portable local artifact `V090_REFERENCE_TOTAL_3150_TWO_REAL_NATIVE_PROOF.zip` SHA256 `737fc55fb32b8259a64d274e13787da1d95dc04283c9b52ac258938fc257e664` contains original/safely path-adjusted input, actual native JSON2, stderr/stdout, all-slot source identity audit, DPS/SEM and JSON2 hashes, CSV. The **compact long-term GitHub proof metadata** is [`integration_probes/data/v090_two_real_native_334_reference_T_receipt.json`](../integration_probes/data/v090_two_real_native_334_reference_T_receipt.json). Do not claim the local ZIP is committed into GitHub; it is an independently delivered user artifact.

## 4. Important integration boundary and exact next

**v090 S1→one static-c DPS candidate path: PASS within Frost 334 / no selected special / no oil / referenced T3150**. The unit-only selected-special L check is fail-closed and preserves exact floors; its real-Native integration with arbitrary selected specials is **OPEN**. Full v066 legacy two-witness preflight still explicitly requires Native full ordinary G, and v090 does not alter it. Other specialist/Fury reference geometry, 0/1/2 oiled weapons' exact external O and final JSON2 reconciliation, complete v065 guided→confirmation→cache/resume operating loop, actual v015/v016 origin-byte product merger, all spec coverage and Windows UX remain unfinished.

The next highest-value work is **v091 actual weapon-count oil policy**, 0/1/2 individual weapons with **per oiled weapon (crit16,haste16,0,0)** external T, strict gear/temporary_enchant identity, cache key and no-double-injection checks, minimal Real Native if necessary. Avoid full ordinary stat database and any new proc gate. In parallel keep full profile exact safety while connecting v090 proposals to the existing v065 scheduler (v092); do not launch a parallel search engine or repeat 158 native reference measurements.

**Main / official Work OS / immutable v003 / original product v015/v016 / project sources unchanged.**
