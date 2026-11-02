# P3-Z — Existing Wago DB2 product season path reused, SimC-only boundary retained

> **2026-11-02 최신 사용자 교정:** 이 문서의 SimC-only 표기는 역사적 제한 원본 조사 경로를 가리킬 뿐, 최종 통제실험의 데이터 수집 차단 정책이 아니다. 최종 시험은 **동일한 실사용 Environment Build 엔진**, **기존 데이터·캐시·영수증의 입력 사용 금지**, **정상 Wago/Blizzard/WCL/공개 GitHub/SimC 신규 수집 허용** 조건을 따른다. [P3-AA 최신 승인 기준](P3_AA_20261102_SINGLE_ENGINE_FRESH_SEASON_CONTROL_ACCEPTANCE.md)이 우선한다.

Date: 2026-11-02 KST. Isolated development branch only; no main merge, immutable v003 mutation, original v016 integration promotion or Project UI application.

## User correction: static G remains numerically meaningful

The real Native v237 observation G=2,847 for exact 14 chosen ilvl 334 gear pieces was a **correct SimC static rating sum**, not a rating-calculation error. Previous representative G≈2,850 is a rounded cross-armor-family reference compatible with that observation, *for the specific historic game build and conditions*. Its limitation was representativeness of gear source: four Primal Leywarden tier pieces but ten otherwise chosen legacy Sinful Gladiator pieces, due to the SimC-only v232 source level ±20 heuristic and ascending item IDs. Actual G and provenance should not be conflated; do not elevate G=2,847 automatically to a new-season verified G or equate to a complete B/T.

## The already existing production gear source (do not recreate it)

Existing **normal product mode** is already Wago-tools DB2-based, NOT a pure SimC item catalog:
- v160/v161 downloaded ten exact-build Wago.tools DB2 CSV tables.
- v163 joined WCL present-season 10 boss encounters, 8 M+ dungeons, and DB2 JournalEncounterItem/Map/season/CraftingData/ItemSparse/Item. Wago.tools is the **public DB2 export website**, not the GitHub source repository.
- v162 obtained an optional curated delve source `balovich-matje/localbots` from **public GitHub** `data/delve-loot.json` and checked its 79/79 names against exact-build DB2 ItemSparse. It is a *community provider*, not complete official server-side delve evidence.
- v165/v166/v167 and v171 saved 511 source-first role candidates: 328 ordinary representative, 106 selectable-stat craft, 63 trinkets, 14 special effect gear. Sources: 223 M+ journal, 103 raid journal, 106 craft, 79 Localbots delve. Some M+ WorldStateExpression conditions unresolved; old-expansion IDs may legitimately appear in a current **returning M+ dungeon** loot candidate. Do not reject by old ID or old expansion alone.
- Existing v168/v169 used this same-season catalog plus tier and v176 reported 26/26 positive physical Native smoke. Do not confuse physical profile compatibility with full adaptive optimizer acceptance.

The special **v229-v237 SimC-only source experiment** deliberately did not load this existing catalog, so its non-tier selector picked the first compatible historic ids. It was a known source-scope experiment, NOT evidence that the original product lost Wago season equipment ingestion.

## Minimal code update — optional provider prefilter; not a new gear DB engine

`runner/v232_simc_only_ordinary_representative.py` now accepts optional `season_gear_db` and CLI `--season-gear-db`:
1. Reuse existing `v167.validate`, requiring same SimC generated **game build** and `no_old_catalog_seed=true`.
2. Narrow non-tier candidate item IDs to existing validated `plain_representative_candidate` source-role IDs with explicit `source_kinds`. Keep the v230 exact SimC row/scaled-effects responsibility and v169 physical ordinary/weapon selectors.
3. With explicit season candidate source, no longer treat tier item's source base-ilvl ±20 and quality as a season eligibility surrogate; these can differ legitimately for returning M+ current-rotation items. Validate the selected metadata class/subclass/inventory and set-free variant against the generated SimC rows, fail closed on mismatches or missing slots. No silent SimC-only fallback.
4. Include source mode, per-slot Wago source-kind labels, same-build provider content hash, and unresolved M+ WorldState marker in the candidate receipt. Preserve `G/J/F/O/B/T=null`, `same_season_membership_not_proven=true`, `environment_ready=false`, zero Native/cache writes. This remains an **option-specific candidate** not a season-eligibility certification.
5. Omitting `season_gear_db` preserves this component's **narrow historic SimC-source-only diagnostic**. The user's final zero-history acceptance **must not use this narrow branch as a separate engine**: it runs the **same normal Build entrypoint** and must **freshly collect** Wago DB2/Blizzard/WCL/public GitHub and SimC source data without reading the previously installed season candidate DB or old caches. A newly constructed v167 source artifact from that run can be used by the common engine.
6. `runner/v233_source_only_G_probe_profile.py` accepts the same optional provider for exact candidate regeneration and no extra Native. The sealed `v236` profile route remains source-byte bound for future optional executions.

**Verification:** [Actions #41398876278](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41398876278), Ubuntu **279/279 PASS**, Windows **279/279 PASS**, new real Native **0**. New synthetic regression proves preferred same-build Wago role candidate 9028 is selected over first SimC-only candidate 9011 and that absent DB cannot replay the provider mode; a mismatched game build blocks. This is *synthetic test* proof, not a newly executed Native comparison of the real 511-row catalog, nor a proof that every WorldState conditional M+ item currently drops.

## Efficient next step

Continue using original v167/v169 Wago DB2 product path and existing 26 physical receipts as primary product evidence. For provider-mode v232, do a bounded **offline join** of actual 511 local DB rows with the same-build v229 raw SimC generated item data, assess which 13/14 slots can be filled and trace provenance; only if an actual missing G evidence gap remains should one new Native be justified. Never repeat the known mixed-tier/historic G=2,847 Native call simply because its names are old. Maintain per-season G/J/F/O source authentication and wire these reusable parsers into the **single normal Environment Build**, rather than treating a separate SimC-only path as the final engine. Never inflate normal-product proof from experimental source-only fixtures.
