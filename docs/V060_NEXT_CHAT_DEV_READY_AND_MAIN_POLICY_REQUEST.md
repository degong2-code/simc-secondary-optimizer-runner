> **2026-10-25 사용자 정정:** 이 문서의 'next-chat' 표현은 **지금 새 채팅으로 이동하라는 의미가 아니다**. 현재 개발은 기존 채팅에서 계속 수행한다. 새 일반 채팅에서도 정확히 복원할 수 있게 개발 상태를 **지속 보존**한다는 뜻이다. 최신 상태는 [CURRENT_PRODUCT_DEVELOPMENT_STATE.md](./CURRENT_PRODUCT_DEVELOPMENT_STATE.md), 현재 사용자 승인 정책 보충은 [DEVELOPER_NOTES_CURRENT_POLICY_ADDENDUM_20261025.md](./DEVELOPER_NOTES_CURRENT_POLICY_ADDENDUM_20261025.md)를 우선 참조한다. Project Instructions/Sources 공식 갱신은 **미적용**이고 MAIN 적용 절차가 필요하다.

# v060 handoff: development-ready, MAIN application separately pending

**Date:** 2026-10-25 KST. **Owner boundary:** isolated development branch only. This file is not an official MAIN, Work OS, Project Source or CURRENT promotion.

## User's latest authoritative direction

**Trust SimC to model item effects, consumable mechanics, APL and DPS.** Our code sends exact selected ID, itemlevel and options, computes static CHMV budgets/fixed minimums and candidate vectors, validates numeric SimC JSON2 targets, and compares DPS/SEM. Do not build independent proc verification/implementation gates.

- An absent trinket static JSON2 gear record **does not bar selection**. `Mindpiercer's Sigil` id 250224 is allowed; v056 ran SimC with it.
- Craftable cloth/leather/mail/plate armor, weapons and supporting shared slots are representative gear to hold **two user-selected embellishments**; do not optimize gear combinations. Initial crafting stat pair 50:50 is **not** an optimizer fixed floor. Current recipe link catalog lists 51 IDs but is not exhaustive; accept manual IDs with compatible class input.
- Static item cache is season+item+ilevel+variant-keyed and does **not** invalidate on SimC version change alone; report conflicts and change old stats only after user-requested correction. DPS result cache includes SimC binary and APL.
- Protect officially user-approved v1.0 total `T=G+J+F`; v059 oil +32 was **bounded pilot** only and is not generalized policy. v1.1_CANDIDATE is not official.
- Preserve WEQUIP runtime independence, protected v003, MAIN/WORK owner boundaries, and separation of official Work OS M0 from product work.

## Most recent evidence

- Source branch current HEAD is a moving value; query before work.
- `runner/v059_candidate_runner_bridge.py`: selected equipment→CHMV candidate→Native JSON2→DPS/SEM with stat parity. Run [#40157655114](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40157655114), **256 pass / 2 skipped, two actual Native runs**; **not** general adaptive optimization nor proven product v015-v016 integration.
- v059 benchmark for one 334 Arcane Mage scenario: T3184 (scenario-specific G2849+J138+F165+O32), target A 600/1140/1115/329 DPS192324.1023 ±SEM1379.5784; B750/990/1115/329 DPS191574.5434 ±SEM1285.6370, statistically unresolved.
- `runner/v055_simc_item_selection.py` and `runner/v058_lazy_crafted_native.py`: 51 grounded crafted recipe item IDs, manual item fallback, effect-agnostic trinket admission; exactly one Native static lookup for missing *nontrinket* item. v058 data 455 IDs and 1759 Native stat variants.
- Proven Linux binary SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`; Actions artifact storage may expire; do not promise permanent availability.

## Next work sequence

0. Read Project Source `SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.0.md`. Re-read source/branch SHA and evidence. Seek original v015-v016 product engine bytes/lineage before **claiming actual product merge** (not found in this isolated repo). Its absence is not a blocker to isolated code tests.
1. Generalize scenario input contract for class/spec, target ilvl or manual T, user gear & 2 trinkets/embellishments, 4pc, traits, consumables, combat settings, stat bounds and retry budget. No v059 Mage-only constants as policy.
2. Assemble class-compatible representative gear with preserved 4pc/selected specials and static G/fixed floor, lazy Native stat cache, and exact external trinket semantics. No item effect inspection.
3. Generalize observed SimC gear_* stat injection/double-addition reconciliation; preserve officially confirmed v1.0 T. Compare numeric target vs actual JSON2, not proc details.
4. Wire lineage-confirmed **existing** adaptive scheduler to v059 evaluation interface; retain iterations, persistent cache, confidence intervals, near-performing materially distinct alternatives. Do not rebuild v015/v032 without need.
5. Expand bounded cross-class/spec DPS tests incl. tanks/healers, then UX progress/cancel/resume/results.

## MAIN policy boundary

User requested policy reflection. In the 2026-10-25 portable next-chat handoff are:
`SIMC_SECONDARY_OPTIMIZER_POLICY_SUPPLEMENT_20261025.md`,
`SIMC_SECONDARY_OPTIMIZER_MAIN_POLICY_APPLY_REQUEST_20261025.md`.
**Official Project Instructions/Project Sources were not edited by this branch; MAIN still must perform and record the formal application under its existing approval contract.** Do not mistake this staging note for main policy application. Do not mutate GitHub main/CURRENT/Shared State as a side effect.

## Readiness verdict

**ISOLATED_DEVELOPMENT_READY** based on successful GitHub Actions and reproducible v059 evidence. **PRODUCT_MAINLINE_INTEGRATION_AWAITING_SOURCE_LINEAGE**, **MAIN_POLICY_APPLICATION_PENDING**. No local Windows or PyCharm installation is required to start GitHub-isolated development.
