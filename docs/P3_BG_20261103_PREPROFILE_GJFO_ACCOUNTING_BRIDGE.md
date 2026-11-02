# P3-BG — Fresh-season G/J/F/O pre-profile accounting boundary (2026-11-03)

**Authority / scope:** Approved v1.4.3 + DPS26 correction + P3-AA single normal Environment Build; user continuation approval after the P3-BF restoration. Isolated `probe/chat-cache-v035-20261024` branch only. **This is one contract seam, not an automatic new-season G/J/F/O collector or product readiness.**

## Existing integration gap

- The normal `v216` source intake already collects/stages pinned Wago/season and SimC physical candidates, yet the actual new season's representative membership and G/J/F/O remain unverified.
- The existing `v222.reconcile` had all four component arithmetic and fixed L/E/O guards, but required a `v098` profile plan before it could calculate B/T. For fresh seasons, that reverses the desired build order: verified G/J/F/O must become the profile budget, and the generated v098 plan must then be checked against that budget.
- The existing same-season installed `v223` reference remains a bounded historical reference, never proof of an automatically built new-season G/J/F/O.

## Implementation on commit `34e9396cc5f8d928e02fd10056d004d2c41801aa`

1. `runner/v222_season_budget_contract.py` adds pure `preprofile_budget(source_catalog,source_artifact_sha256,evidence,target_ilevel,manual_final_T)`. It retains original source identity and four-component presence checks, manual final T precedence, `O` physical hands, per-stat fixed L/E and double-count prevention. Its result explicitly says source authentication is **external**; no Native/network/cache action or READY admission.
2. Existing `v222.reconcile(...,plan,...)` now calls the same pre-profile calculator and then verifies `v098.plan` B/T/O equality. One arithmetic implementation, no competing new engine and no silent plan drift.
3. `runner/v216_environment_build_coordinator.py::preflight_new_season_source` accepts an **optional internal proposed budget evidence** and calculates `proposed_budget_arithmetic_unadmitted` only after the existing fresh-source catalog/UI PENDING checks. The top-level G/J/F/O/B/T remain null, `environment_ready=false`; it marks independent origin/rating authentication as pending. This optional contract is **not yet wired to a real fresh-season source verifier**.

## CI / evidence

- [v212 contract run #41545848346](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41545848346), tested source SHA `34e9396cc5f8d928e02fd10056d004d2c41801aa`: Ubuntu and Windows **413 tests each, 0 FAIL, 4 SKIP**, SUCCESS. Four additional focused tests cover pre-profile equivalence, manual T/oil, incomplete/wrong-season proof blocking, and fresh-preflight unadmitted arithmetic.
- [v113 #41545848391](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41545848391): Ubuntu and Windows **194 tests each**, SUCCESS, Native0.
- [v181 #41545848264](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41545848264): Windows Python 3.12/3.14 **139 tests each**, SUCCESS, Native0.
- [v182 #41545848107](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41545848107): Ubuntu/Windows focused **2 tests each**, SUCCESS, Native0.
- Current P3-BG changes: actual new SimC Native **0**, real new Wago/SimC source HTTP **0**; tests are deterministic **offline/synthetic** evidence. No new G/J/F/O evidence authenticated, no new environment installation or adaptive DPS trial. P3-BF original real source/runtime separation remains unchanged.

## Concrete immediate next implementation — no rework

1. Use **existing** `v216` fresh ordinary/tier candidate receipts and `v163/v165-v169/v245/v250/v251/v232` source/season joins to authenticate *selected* representative nontrinket equipment for one requested DPS spec/target ilvl (334 first). Old PvP or Localbots-only unverified source membership must remain PENDING; do not reuse invalid historical G=2847.
2. Connect independently verified same-season `G` (valid season-specific reference or exact selected variant using `v226/v227/v228` and minimal Native) and top-quality/slot-applicable `J/F/O` / permanent E from existing collectors `v221/v224/v225/v190/v191/v211`. Missing/ambiguous proof is component-specific PENDING, not an old v089/J138/F165/O16+16 default.
3. Pass the **authenticated** complete evidence to the new `v222.preprofile_budget`, then construct/validate a v098 profile and call unchanged `v222.reconcile` to check plan equality. Join Policy A `v220/v196`, v212 installation and existing v093-v095 adaptive optimizer only after the real source gate.
4. Every new test must distinguish the external source provenance, arithmetic contract, selected profile/Native JSON2 and DPS behavior. Reuse same-season pinned source/cache/receipts; avoid duplicate HTTP/Native, read huge CSVs once, and keep optional items from blocking a verified basic environment.

**Boundary:** Since this commit does not authenticate origin or produce missing G/J/F/O, its correct acceptance is **P3-BG accounting-seam PASS / full Environment Build still PENDING**. P3-AA zero-history same-engine acceptance remains unrun. No main, v003 immutable, v016 original, Project UI, Work OS/Shared State or WEQUIP authority changes.
