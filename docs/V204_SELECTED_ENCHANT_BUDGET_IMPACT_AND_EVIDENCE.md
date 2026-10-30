# v204 — Selected permanent-enchant additive reference budget: cross-feature impact and status

Date: 2026-10-31 KST. Scope: isolated `probe/chat-cache-v035-20261024` development branch ONLY.
Authority: user's 2026-10-31 instruction. This **supersedes only** the old v197/v203 assertion that E never changes derived B/T. All original v203 Native artifacts are preserved as historical evidence.

## 1. Reason and exact accounting

The 79x2 ilvl reference table remains byte-for-byte unchanged. Its `v084_frost_cloth_1h_frill_native.py::source_profile` reconstructs reference equipment options from scratch with gem/crafted fields, not permanent `enchant_id` inputs; do not mistake the upstream raw fixture's preexisting enchant lines for the generated reference equipment. New permanent enchant is additional external **item-applied static rating** at the actual user choice, not universally present.

For a **derived ilvl reference** with a selected, exact-SimC-verified enchant and no baseline duplicate:

- `G_effective=G_reference+sum(E)`
- `B_effective=B_reference+sum(E)`
- `T_effective=B_effective+sum(O)`
- `E` is fixed inside `G_effective`, **not free allocation**. The existing v065 floor preserves its per-stat E, but does not add E to the resulting `gear_*` again. `gear_*` targets already sum to `T_effective` after oil O.
- For a **user-entered manual FINAL T**, that total **already includes the selected enchant and oil**. There is **no B/T increment**; the E floor is still enforced. If impossible, fail before Native.
- For **no enchant selected**, do not even enter v204 transformation; existing v089/v090/v091/v096/v098 results, scenarios and cache identities are unchanged.

334 / single-oil / exact `finger1 item158366 enchant8025` (`E={crit:0,haste:30,mastery:0,vers:0}`): unselected `B0=3150,T0=3182` vs selected auto `B=3180,T=3212`; selected manual final T 3182 remains `B=3150,T=3182`. Values are reference arithmetic, NOT newly observed DPS.

## 2. Safety boundaries / impact matrix

| Surface | v204 behavior and retained boundary |
|---|---|
| 79x2 Native reference | Never mutate the source JSON, row, SHA, original `B0`; include an explicit v204 receipt recording additive E and original row. |
| v089 / v061 legacy typed schema | Unchanged. Transform only the **resolved** reference selection after v089, recalculate existing normalized typed scenario and digest. Exact Native G mode not altered. |
| v090 reference compilation | Explicitly validate `resolved_B==reference_row_B+verified_E` when the signed v204 receipt is present; otherwise the existing exact baseline equality remains. Preserve existing provenance byte shape with no E. |
| v091 oil / v092 | Only the selected E affects derived B; fixed oil O is still injected once. Manual final T is converted to B=T-O first and not incremented. |
| v065 / v093 / v094 | Same candidates, floor mechanism, 95%/SEM, cancel/resume/cache engine; only new chosen E path receives larger fixed budget. No second optimizer. |
| Fixed special L / crafted | v203 blocks same finger1 selected L/crafted slot before profile build, retaining existing L and O floor tests. |
| v098 bootstrap / v096 entry | Pass verified E only for developer `verified_enchant` / `v202_verified_enchant_choice`, never through ordinary user v106/web fields. Exact v203 entire profile SHA must match *before budgeting*, and v096 admission still requires exact binary revision, Native evidence SHA and slot. |
| SimC numeric input | Selected E lives within B/T candidate targets and is therefore supplied to `gear_*` **once**, not added again on top of SimC's overridden permanent enchant. SimC owns APL/proc/DPS and effect semantics. |
| DPS case identity & resume | Changed scenario digest, effective B/T, gear option/source SHA and v202 evidence separate new result keys from v203. Do not promote old B3150/T3182 JSON2 or cache to B3180/T3212. Historic user sessions remain read-only. |
| Static item cache / memory / I/O | No cache invalidation, no new item download, no new DB; adds only a few proof JSON reads in selected path and one in-memory normalized scenario copy. |
| Season catalog / Windows UI | 38 permanent enchants remain read-only, normal v106 API rejects developer field, all existing consumable options preserved. Windows Native enchant and 37 others unverified. |
| Distribution / permissions | No user profile, secret or cache in public GitHub. Main, v003 immutable, original v015/v016, Work OS and ChatGPT Project UI unchanged. |

## 3. Implemented code and validation scope

- `runner/v204_selected_enchant_reference_budget.py`: typed minimal reference-delta transformer and proof revalidator. Only exact v202 Native E=haste30 is admitted; no E returns original object unchanged; manual T returns original selection unchanged.
- `runner/v091_weapon_oil_external_adapter.py`: opt-in E only, exact complete post-oil source profile SHA preflight; unaffected old call shape.
- `runner/v090_reference_total_native_candidate.py`: check reference row plus explicit signed E delta without changing row/registry SHA.
- `runner/v098_target_user_scenario_bootstrap.py`, `runner/v096_unified_product_entry.py`: selected developer field transferred through staging and unified manifest; exact v202 binary/source proof remains mandatory; output plan declares selected-auto vs selected-manual budget semantics.
- `tests/test_v204_selected_enchant_reference_budget.py`: no-choice identity, auto reference +30, manual final T unchanged, proof tamper rejection, wrong-profile failure. Existing v089/v091/v096/v202/v203 focused regressions also targeted.
- `.github/workflows/v204_selected_enchant_budget.yml`: one small Ubuntu/Windows **offline** regression matrix, no Native requests.
- `integration_probes/v204_selected_enchant_additive_native_cache_audit.py` and dedicated `.github/workflows/v204_selected_enchant_native_once.yml`: changed-B **exact** Linux frozen SimC binary, 6 fresh Native maximum, then 6 SHA-verified cache hits; one-time workflow triggered only by the workflow-file path (with separate manual dispatch), source only and compact receipt.

### Evidence classifications

**Historical, reused unchanged:** v199 natural +30, v201 gear override no extra, v203 old `B3150/T3182` 6 Native + 6 cache, v178 cancellation/resume, v176 26-spec physical, v180 36 Native, Windows source beta/HTTP offline.

**New code implemented:** conditional budget selection, provenance, scope guards and focused tests. **Do not infer PASS** until v204 workflow job logs prove it. The old v203 B3150/T3182 Native 6+6 cannot substantiate v204's changed B3180/T3212 DPS outcomes.

**Still pending:** real v204 CI and new changed-budget Native receipt until checked; Windows exact SimC Native, general end-user enchant selection, other enchants/loadouts, mid-Native forced interruption/recovery, original product/full installation and official promotions.

## 4. Efficiency and release boundary

No 26x Native rerun, no re-fetch of 79x2 reference, no static cache replacement, no extra runtime dependency; only one changed target session is worthy of fresh Native evidence. Fail closed on any proof/profile/legacy identity mismatch. Do not enable Windows UI or promote to main without exact scope-specific results and separate authority.
