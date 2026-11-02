# P3-AS — DB2-first correlated tier → first-party SimC exact-identity candidate bridge

Date: 2026-11-02. Isolated branch only; no main/immutable/project-UI promotion.

## Contract and intent

Goal is a complete 26-DPS optimizer for **future absolute CHMV** at target ilvl (default 334) or manual final T, using adaptive SimC DPS. This work supplies internal source-only 13-class physical tier candidate evidence, not loot-location recommendations or current-gear redistribution. The latest policy still requires fresh-season G/J/F/O verification, `B=G+J+F`, `T=B+O`, fixed E/L/O accounting, highest-quality option admission after evidence, one representative profile per DPS spec, and adaptive SimC/cache/95% results.

## Observed source chain reused

- Previously sealed same-build Wago original [#41446821338](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41446821338): 13 × 5 tier pieces at ItemSparse base ilvl 197 and a second 13 × 5 at 219 (this is **build-local**), no tier publisher names required.
- Active raid ↔ bonus fingerprint original [#41451457316](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41451457316): the previously authenticated active raid's 118 journal loot IDs include 101 intersecting bonus group IDs 614–618, while recent 65 physical tier pieces share 614–618 and old 65 share 608–612. Groups may occur outside the active raid, so the relation is strong corroboration **NOT a current-season flag**.
- v245 physical candidate → v250 active-raid source corroboration already integrated into normal v216 Environment Build, with v217 stage caching and bounded HTTP. No new source retrieval added in v251.

## Implementation in this change

- `runner/v251_db2_raid_tier_simc_bridge.py`: takes receipt-backed v245 structural tier and v250 uniquely **observed leading** (not season-certified) class roster. Cross-checks the 13 exact class↔ItemSet IDs, homogeneous source ItemSparse base ilvl, 5 distinct physical IDs by slot, 65 unique IDs across classes, 2pc/4pc spell candidate presence, and v250 source status. Produces 13 exact class physical records, explicit four-piece slots [head, shoulders, hands, legs], fixed schema, no class name lookup or old set ID seeds.
- `select_for_simc`: optional **per one requested DPS specialization**; reads existing authenticated first-party SimC v229 seed using existing v231 code and matches ONLY `class_id + item_set_id + exact set of five physical ItemIDs + bonus sizes [2,4]`. Requires exactly one SimC set option candidate, then calls the existing `v231.select` to validate actual SimC-generated item_data; never accepts a user/website tier name as the matching key. If the first-party seed is absent, different build, or doesn't contain the matching item set, the outcome remains blocked/pending rather than guessed.
- `runner/v216_environment_build_coordinator.py`: existing fresh-DB2 path now appends `fresh_tier_simc_candidate_bridge` with v217 SHA-sealed stage output when v250 finds an unambiguous active-raid-correlated full class roster. Missing/ambiguous source => skip with 0 further HTTP and pending result. This **does not invoke `select_for_simc` without a first-party seed**, does not call Native, does not install the candidate as current-season 65, does not mark source season verified, and does not change the adaptive optimizer.
- Reuses source data in place and reads each bounded input JSON once for hashing/compile. New v251 stage is 0 HTTP; same-build rerun returns REUSED_VERIFIED without recomputation. Existing v161/v245/v250 source caches, session storage, DPS cache, and user-facing option catalog stay unchanged.

## Actual checks and limits

- [Final source-contract CI #41454624275](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41454624275): Ubuntu and Windows each ran **357 tests; 0 FAIL, 4 SKIP**. Native output absent in the receipt. Tests cover 13×5 candidate binding, ambiguous/replaced proof rejection, source ID exact SimC set option selection through mocked `v231` call, mismatched SimC source/ID rejection, sealed stage reuse, and normal v216 integration. Mocked SimC option test is NOT real generated SimC-source acceptance.
- [Immediately preceding integration CI #41454376657](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41454376657) also passed both OS after a fixture-root correction. Any historical failed Actions for synthetic test fixture setup are not new product source errors; do not erase them.
- No new real v229 SimC same-build source receipt or exact 26-DPS SimC acceptance in this task; **SimC real `set_option` equivalence for this correlated roster remains UNVERIFIED**. Source-only physical candidate is not v168 certified production itemset, v232 production G work, or end-to-end environment.

## Next bounded work, priority

1. If an existing authenticated same-build v229 first-party SimC seed is available, reuse it to exercise `select_for_simc` for one representative DPS and then 13 classes; avoid downloading/recompiling every SimC source or running Native without source changes. A mismatch is source incompatibility pending, not a cue for tier names or ID heuristics.
2. Continue mandatory *season-wide G/J/F/O* automatic source build/recalculation, validated best-quality options, B/T accounting and representative profile composition, using existing v222–v240 stages. Native should validate only actually changed static rating assumptions. Preserve cache/95% adaptive status and main dev chat ownership.
3. Require actual same-build season/item evidence before promoting a current-season roster, and report pending facts precisely. Do not create a new all-season gear DB or season tier authorization gate.
