# P3-AP — Pinned Wago game build is NOT an active-season item filter (2026-11-02)

## Direct user question and actual source answer

- Wago `https://wago.tools/db2/{Table}/csv?build={build}&locale=enUS` returns the named **entire client DB2 table snapshot for one build**; this URL does not filter all rows by release season. Build identity and season ownership are distinct dimensions.
- Actual Wago ItemSet, ItemSetSpell and ChrSpecialization bytes for build `12.1.5.70575` were fetched in previous research receipt [#41429876635](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41429876635). The same build contains Midnight S1 class tier ItemSetIDs 1978–1990 AND S2 tier ItemSetIDs 2055–2067, each with 13 class sets, 5 physical pieces and 2pc/4pc specialization bonuses. So the user hypothesis is refuted by direct source counterexample, not only by documentation.
- `ItemSparse.ExpansionID` is an expansion attribute, NOT a season discriminator. There is no proven `ItemSet/ItemSetSpell` current-season flag; no ID ordering, latest build, most recent appearance, or high ilvl guess can become a season certification. New-season PTR builds can contain forthcoming gear before it is live.

## Implemented in existing source engine

- v245 source-first `discover(expansion_id=None)` now groups physically verified tier candidates by `observed_expansion_id` without requiring WCL or Blizzard credentials. It still requires same requested game build and original sealed v161 ItemSparse/Item, checks 13-class item-set specs/2+4 plus exact 5 slots and class masks, and never guesses current expansion or season.
- v216 normal `collect_wago_new_season_source` now invokes DB2-first tier candidates even when v155/v163 cannot establish unique season scope; it records `expansion_selection_source=UNSCOPED_OBSERVED_EXPANSIONS_ONLY`, `source_season_verified=false`, `current_season_selection=null`, `environment_ready=false`, and G/J/F/O/B/T remain null. When authenticated v163 scope does exist, it still restricts expansion and remains season-pending.
- On a malformed/partial Wago physical CSV header, v245 now rejects early *before* 3 additional Wago HTTP requests. Valid same-build `ItemSet`, `ItemSetSpell`, `ChrSpecialization` are each fetched once and sealed with the existing v217 stage engine; repeated Build uses zero network requests. No browser/publisher/name-first fallback, manual tier-name input, or historical item IDs.
- Normal Build synthetic end-to-end test with **no authenticated credentials**, a legitimate 10-table Wago fixture plus 3 extra tier tables and two separate tier rosters for 13 classes, returns 26 valid candidate sets in expansion 11, zero selected current-season sets. 13 Wago requests once; second run 0. Synthetic fixtures are tests, not external source proof.

## Actual CI evidence and boundaries

- [Final environment CI #41433274984](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41433274984), code SHA c32331a4ba8dfee2c155a7081ad36e3ad242a0e1: Ubuntu and Windows successful, no Native outputs, 4 historical skips per platform. Initial #41433129150 had 1 test-only error from invalid empty auth mapping `{}`, fixed by using existing v242 strict empty four-field credential contract. This is NOT a newly installed season environment.
- Prior actual source probe [#41429876635](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41429876635) remains independent proof of the Wago same-build DB2 source availability; no repeat Native or historical DB2 real source pull this turn.
- Still missing: independently verified current-season→ItemSet mapping (token conversion, seasonal metadata or another authenticated source), source-only 13x5 real physical snapshot from new season, seasonal G/J/F/O→B/T, and final v168→user profile→v212 install. Do NOT mark ready. No main merge, Project UI registration or authority transfer.

## Next high-value work

Obtain a source-derived exact season→ItemSet relationship using existing Blizzard/Wago datasets without returning to third-party name list scraping. Prefer joining raid tier/reward-token data or the native SimC season index; if there is no sound mapping, preserve discovered candidate sets and PENDING status. Avoid blanket Native reruns, unnecessary global item DB, or using a build number as a season filter.
