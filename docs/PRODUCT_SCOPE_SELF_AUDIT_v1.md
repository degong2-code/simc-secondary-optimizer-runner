# SIMC SECONDARY OPTIMIZER — Product-Purpose Self-Audit v1 (working note)

**Status:** NON-AUTHORITATIVE WORKING CHECKLIST. This is not a new approved product policy, not the official roadmap, not Project Sources, not Work OS M0, and not a product promotion. Its sole purpose is to prevent future Chat/GitHub development from losing the approved purpose. Official reference: `SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.0.md` (sections 1–5, 11–13, 15–17). The user's later clarified scope regarding **delegating equipment proc computations to SimC** is reflected here as an implementation interpretation, not an amendment to Developer Notes.

## Immutable purpose until separately changed by the user

**Find an actionable DPS-maximizing allocation of the four secondary-stat CHMV ratings at a user-selected target total and fixed combat/equipment scenario, and present statistically defensible nearby alternatives.**

- **Optimizer owns:** scenario/input integrity; level-appropriate representative equipment; correct CHMV total; immutable static item floors; correct flexible rating allocation; prevention of double counts; candidate generation, cache, adaptive sampling, statistical DPS comparison, results and operation.
- **SimC owns:** combat rotation/APL, damage formula, temporary procs/buffs/debuffs, their runtime magnitudes, proc frequency and contribution to DPS. The optimizer supplies the correct item/bonus/effect settings and reads **actual SimC DPS**; it does **not** duplicate SimC's proc simulation or calculate proc DPS separately.
- **Minimal SimC conformance the optimizer needs:** proper item ID/level/options and preserved user-selected effects, tier/set, trinkets, embellishments, gems and consumables; enough observable evidence that expected mechanisms are recognized rather than silently absent. If SimC cannot support/recognize the requested effect, flag/block that scenario. Deep internal spell/driver/stat-delta reconstruction is *not* a default release requirement.
- **Outside scope:** selecting gear combinations or farming routes, complete general-equipment DB, independently implementing complex spell mechanics or profession-specific APLs, chasing global mathematical optimality beyond agreed run budget, forced precision beyond sampling evidence.
- **Nonnegotiable distinction:** the +201 mastery on the specific ilvl334 special head is an example of **static fixed CHMV** that belongs once inside the equipment budget and is not freely movable; the dynamic Venomcursed gain/loss remains SimC's job and is not added to static CHMV. This *example* does not establish live-game catalyst bonus ownership or a general budget total.

## Five-question audit before every proposed development or test

1. **Direct value:** Which user-visible CHMV optimization requirement will this change unblock or improve? Point to Developer Notes v1.0 section or an explicit subsequent user instruction. No clear benefit => defer.
2. **Correct owner:** Is this something our optimizer must compute or verify, or is SimC already the authoritative implementation? If SimC owns the mechanism, verify input/effect recognition and use resulting DPS. Do not reverse-engineer its entire runtime unless a demonstrated failure prevents correct product output.
3. **Minimum sufficient evidence:** What is the cheapest reliable test that would falsify the expected behavior? Prefer current artifacts, offline checks and the existing pinned SimC cache over repeated Native queries and new infrastructure. Stop after adequate evidence.
4. **Keep budget semantics:** Distinguish static free CHMV, fixed nontrinket CHMV floor, external fixed stats, and temporary proc effects. Keep official v1.0 `T=G+J+F` as the current policy; `T=G+J+F+O` remains an unpromoted candidate. Do not reconcile 3182/3184 or adopt manually tested 3284 as actual ilvl budget without SimC/source evidence.
5. **Change and authority safety:** Are we keeping the v016 product baseline separate from GitHub v032+ experiments until code lineage and feature inheritance are proved? Does the change avoid editing main, Project Sources/Instructions, CURRENT/Shared State, Work OS and v003 immutable without separate authority? Don't claim acceptance when the evidence is only a narrow Native pilot.

**Decision:** Classify candidate work as `CORE` (implements optimizer), `REQUIRED_CONFORMANCE` (proves input/stock SimC DPS integrity), `DELEGATED_TO_SIMC` (no new solver responsibility), or `OUT_OF_SCOPE`. Implement CORE and needed REQUIRED_CONFORMANCE; minimize or defer the rest.

## Post-change audit (one compact record in each receipt/report)

- `direct_requirement`: v1.0 section / later approved instruction.
- `scope_class`: CORE / REQUIRED_CONFORMANCE / DELEGATED_TO_SIMC / OUT_OF_SCOPE.
- `minimum_test_and_result`: evidence actually checked, including limitations and missing independent proof.
- `cost_and_complexity_delta`: Native calls, repeated/cache hits, API calls if any, I/O and code surface; identify removable redundant steps.
- `test_success`: PASS / FAIL / BLOCKED, **separate from** `product_code_integrated`: true/false and `official_policy_promoted`: true/false.
- `unverified_and_next`: explicitly name what remains; do not promote research candidates or simulated artifacts to live-game truth.

A PASS on a narrowly bounded SimC trial never means a complete product integration, and higher GitHub version numbers do not override the user's product baseline v016_SCENARIO_CONTRACT. v016–v031 original sources/receipts have not been independently verified in the current successor chat; current lineage remains unproven.

## Scope correction learned from v043

Querying Venomcursed dynamic DBC values (+362.9923/-60.49704 in the pinned spell-query experiment) was research and can remain as non-authoritative evidence, but **no further per-proc mechanic reconstruction belongs on the critical path** absent a concrete SimC recognition or DPS validity defect. The next core bottlenecks are accurate target-ilvl static G/T and locked floors, gem/flask/oil/injection attribution without double counts, representative SimC profile fidelity, and integration with the existing adaptive CHMV/DPS engine.

**Maintenance rule:** Before substantive product work, reread official Developer Notes v1.0 and this working checklist, then state the requirement, minimum test, and explicit completion boundary in the development receipt. Do not treat this page as superior to official policy. Keep it short; avoid growing a new Work OS or runtime dependency.
