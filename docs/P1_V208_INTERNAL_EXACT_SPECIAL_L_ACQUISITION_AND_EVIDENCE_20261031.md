# P1 v208 — Internal exact special-L lookup on user Start (2026-10-31)

**Scope/authority:** isolated development branch only. Not main/v003/v016
integration or Project UI promotion. Prior v205–v207 and v176/v180 native
results remain independent history. No effect/proc model and no new solver.

## Actual product change

- Existing `v098` now has a strictly internal, **no-write / no-Native**
  `static_special_probe_only` stage. It uses the **identical character,
  target ilvl, trinkets, representative gear/tier, optional special/embellishment,
  consumables and oil** as the user scenario. It returns an exact source-bound
  SimC physical profile and selected-special item/ilvl/options rows BEFORE
  the existing static-L budget check, without creating a user result.
- New `v208_internal_exact_special_L_hydrator.py` uses the existing
  `v046` Native JSON2 parser/append-only variant cache and `v062` exact
  variant identity. **One** real 1-iteration SimC physical-source call can
  observe all missing special rows within that same user profile. Only actual
  observed slot records matching exact ID, ilvl, options are admitted. Static
  cache is **same-season** and does not vanish when the SimC binary revision
  changes. Existing source cache is never mutated. The next complete static
  cache is an immutable content-addressed snapshot; a tiny latest pointer is
  advisory only. An old sealed session stays bound to its original snapshot.
  New binary/revision still segregates DPS caches.
- `v113 /api/v1/sessions/plan` stays **0 Native** and may report missing L
  before an initial cache population. On explicit user **Start**, `v113`
  first runs the internal static hydration if exact L is absent, creates a
  new sealed session using the resulting immutable static snapshot, then
  invokes the unchanged `v106→v098→v096→v094` adaptive DPS worker (max
  6 DPS candidates). The API separately reports static-L Native count (max
  1 physical Native on a miss). Cache-only DPS replay is unchanged.
- The static selected-special attribution rule of existing `v062` remains
  authoritative. An item with ambiguous permanent gem/enchant numeric
  modifiers cannot have all decorated stats mislabeled as bare fixed L.
  The v208 preflight checks this **before** spending a Native; it returns
  `SPECIAL_L_DECORATED_NUMERIC_VARIANT_NOT_YET_ATTRIBUTABLE`. This is
  existing stat-accounting safety, **not an independent proc authorization**.

## New evidence, precise scope

- [Windows + Ubuntu focused v208 #41148491803](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41148491803):
  offline fake SimC JSON2 user-start/cache-replay/session tests PASS both OS,
  no real Native; historical initial #41148407698 failed due test expectation
  and old UI text, corrected and preserved.
- [v208 source-only cloak preflight #41148906955](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41148906955):
  **113 focused cases** on Windows and Ubuntu, confirming current-season
  cloak item `159288` at ilvl331 has **no ambiguous gem/enchant options**.
- [Windows real official SHA-pinned Native #41148967010](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41148967010),
  job `124380645128`, exact source commit
  `8fadea25ca5e54eb1de2e560d9608a75df0f9219`, **SUCCESS**:
  shaman/elemental 331, selected source-listed
  `Cloak of the Restless Tribes` item `159288`, slot `back`,
  exact options empty. Actual static **one Native**, observed exact L
  `crit=0,haste=0,mastery=51,vers=61` (112 rating total),
  then **0 Native** v098/v096 plan accepted `B=3110,T=3142`,
  and same exact variant **0 additional** static Native on cache replay.
  Official Windows SimC binary SHA
  `0ad16368cd1effb19c793dbce63518ccb72fec89c72f6ef75d9afca239a039e8`;
  original JSON2 SHA
  `1ed29065eff63bb8274d033d48da2eeaa91c240a429ba3ad1cf0a98249105d0b`;
  output artifact #13021778963, ZIP SHA
  `3d1cfa5b6ef702c1a585f5df04384415684d0c6726b253642f699cf027a1bee8`.
  This is **static-L acquisition and accepted zero-DPS-call planning**,
  not a fresh six-DPS session or DPS result.
- Initial actual special neck item `268250` / ilvl331
  [#41148641946](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41148641946)
  reached one real Native but its audit assumed wrong empty options.
  Next [#41148763112](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41148763112)
  and [#41148833439](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41148833439)
  showed actual `v062` `SPECIAL_LOCK_NEEDS_UNDECORATED_NUMERIC_VARIANT`
  for automatically decorated neck. **These are legitimate non-passing
  product cases, not silently called PASS.** No attempt to treat gem rating
  as bare fixed L. Preflight now avoids this unnecessary Native.
- Latest focused post-preflight [#41149118458](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41149118458)
  was still running at first documentation. Check final job log before
  claiming final PASS.

## Remaining P1 and P2

1. Exactly separate **bare special item L** from any ordinary gems J or
   permanent enchant E in an embellished/generated item. Reuse existing
   `v046/v062` same-season Native records and real SimC; prove the bare
   variant and keep actual selected decorated item in DPS profile. Do not
   lock decorated stats as L. Do not reimplement effects or manufacture L=0.
2. Ensure all user-visible selected special paths can use this automatic
   hydration, including catalyst/tier conflict rules; never claim all 26 specs
   or all 14 special-gear candidates passed because one cloak did.
3. Existing v191 current-season 38-enchant list contains token/ID/rank/slot
   but not general exact effect magnitudes. Extend source handling for
   stat-family categorization separately; only confirmed fixed CHMV E may
   affect auto reference B/T; manual T is always authoritative.
4. Test genuine Windows browser click E2E on user PC separately from
   GitHub hosted Windows real SimC and TestClient/loopback HTTP.

**Avoid:** new global eligibility gate, all-spec Native rerun, full season
DB recollection, newly invented item mechanics, WEQUIP dependencies.

## v209 exact one selected-special full Windows Native user journey — SUCCESS

[Windows Actions #41149327977](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41149327977), job `124381809616`, original commit `aae422680d5a16b64ef0fb3db3dcde04c3293be7`: **SUCCESS**, official SimC Windows executable SHA `0ad16368cd1effb19c793dbce63518ccb72fec89c72f6ef75d9afca239a039e8`.

- **One real current-season user session**: elemental shaman ilvl331, source-listed selected special `back` item `159288`, options empty. Initial plan without exact L rejected **before Native**, as designed. Explicit Start performed **one physical Native L**, then launched the unchanged adaptive **six new real SimC DPS Native candidates** and returned DPS/SEM/95% via the existing local FastAPI endpoint. The six SHA-validated cache cases replayed **6/6**, extra DPS Native **0**, extra static-L Native **0**. The immutable static snapshot SHA was unchanged.
- Native observed `L={crit:0,haste:0,mastery:51,vers:61}`; `B3110,O32,T3142`, no extra L added to B/T. Observed first-choice DPS `201953.1715231995`, SEM `337.3012247806419`; confidence **95%**, global optimum **not proven**. This is a result of the exact sample, not a performance comparison against another profile.
- Actual artifact #`13022640419` has outer ZIP SHA `6f7c1abda4df33a4f8dfd6d559046e1772e091a7f9ea51e0ff522ddb9dd56dec`; original artifact ZIP was downloaded and JSON contents confirmed. Exact six native JSON2 SHA + static Native SHA are recorded in [v209 verified successor](V209_WINDOWS_ONE_SPECIAL_COMPLETE_NATIVE_VERIFIED_20261031.json), **not** invented before the job.
- [Latest post-preflight focused #41149118458](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41149118458): **Ubuntu 114/114, Windows 114/114 PASS**, no SimC Native. Prior [#41148407698](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41148407698) test-only and [#41148641946](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41148641946)/[#41148763112](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41148763112)/[#41148833439](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41148833439) exact decorated-neck witness failures remain historical; the latter established the existing v062 unadorned-L boundary.
- This **does not** certify a gem-decorated special, every 14 source candidate, every class, Windows GUI mouse clicks, user PC, or original v016. No new solver/SimC effect model and no 26-spec rerun. A spurious v180 workflow triggered by touched source/UI completed offline, but its **36-Native job was SKIPPED** by its existing exact one-time execution guard.
