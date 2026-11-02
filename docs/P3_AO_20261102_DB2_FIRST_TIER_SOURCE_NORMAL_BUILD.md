## Final focused code validation after request-accounting fix

- Code commit: 7ba332e04587120e58b57e38219eac28b57f6517.
- [v212 offline contract #41430340938](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41430340938): **Ubuntu 345 tests, OK (skipped=4); Windows 345 tests, OK (skipped=4)**, 0 FAIL, Native artifact absence assertion PASS. Includes new test for real attempted-HTTP accounting on partial failure.
- [v113 local API #41430297062](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41430297062), [v181 Windows source beta #41430297063](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41430297063), [v182 user UI #41430297181](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41430297181) all concluded SUCCESS at code commit b813162ecb44c44ef24df86e7d354f021d97d1a3 (before subsequent focused new-test-only commit). No new Native.
- Real source pilot remains limited to 3 smaller relations, not a full real source 13x5 `ItemSparse` profile or current-season certainty.

# P3-AO — Source DB2-first tier candidate discovery replaces name-first Build

## User decision, applicability

2026-11-02 approved direction: completely abandon *tier-name-first discovery* in the NEW-SEASON normal product Build. No GuildLoot/fixed public page, no historic current_season_tier_source_anchors.json, no old ItemSet ID or name seed, and no publisher fallback in this route. Previous v243 code/test remain as historical evidence only, no longer imported or invoked by v216.

## Actual implementation

- New runner/v245_db2_first_tier_discovery.py obtains **3 small exact-build Wago tables** (ItemSet, ItemSetSpell, ChrSpecialization) through one existing v217 receipt stage, then scans original v161 same-build ItemSparse and Item once each and reuses v168 physical class/slot/armor definitions. It never loads a full season gear recommendation DB.
- Derive candidate set/5 physical IDs from ItemSet.ItemID_0..16. Join ItemSetSpell by ItemSetID and ChrSpecialization by ChrSpecID→ClassID; require at least two specs belonging to one class, each with 2pc+4pc SpellID, exactly five distinct slots, correct class mask, armor subclass, expansion, and ItemSparse.ItemSet membership. Names are retained as display-only observations, never matched, searched or used to select an ID.
- Existing normal v216.collect_wago_new_season_source now calls _db2_first_tier_stage instead of _source_first_tier_stage. No HTTP request to guildloot.de or another page, even if DB2 is missing; zero prior tier sources on the input path. If authenticated v155/v163 season scope is insufficient, no extra sources fetched and status TIER_SEASON_SCOPE_PENDING. If DB2 source/structure is insufficient, explicit TIER_DB2_STRUCTURAL_CANDIDATES_PENDING.
- DB2 output status DB2_CLASS_TIER_CANDIDATES_SEASON_PENDING, current_season_selection=null, source_season_verified=false, environment_ready=false, installed=false, G/J/F/O null. Even complete 13-class 5-piece rosters cannot be promoted without independent season mapping: S1 and S2 meet identical structural requirements. v168 remains authoritative for the final exact 13x5 physical tier after valid season selection; v245 only produces possible sets, not a final roster.
- Original v217 stage SHA identities ensure unchanged build reuse without repeat HTTP; new stage adds at most 3 bounded Wago requests. Request attempt count is explicitly preserved on partial failures. Static source item cache scoped to build and bytes, DPS/Native untouched. Season-independent class IDs remain stable, no SimC profile/Native module imported merely to compute DB2 structural candidates.

## Fresh evidence and exact limitations

- [Real 3-URL Wago source probe #41429876635](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41429876635), pinned build 12.1.5.70575: ItemSet 92,549 bytes, SHA 0ae48ff20e117ba0d4bc30d6934819b752785cca0d61cbb0b5812ed99bd19bc6; ItemSetSpell 68,835 bytes, SHA 5f81a5ee83788a17314f610de58654363a1a285eef7843ab4a6da600a078903e; ChrSpecialization 9,536 bytes SHA 4e67c0772fca8cfc857e8a7fc9952538c35018e91f2734284f71089087d60c69. All source CSV schema accepted; 162 same-build source-only five-item/2+4-spec-class structural sets across 13 classes (including older seasons), NOT 162 current-season sets.
- [Offline environment contract #41429666124](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41429666124): Ubuntu/Windows each 344 tests, OK (skipped 4), 0 FAIL, no Native outputs. After lightweight code fingerprint decoupling, [#41430048281](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41430048281) also PASS Ubuntu/Windows. Final incremental request-accounting tests being checked separately. A synthetic complete future build with TWO full 13-class tier rosters yields 26 structurally accepted sets and **zero** current-season selections; repeated same build uses zero new DB2 network requests.
- These test runs do not prove the full 65 pieces on a freshly acquired REAL v161 ItemSparse/Item build, authenticated new season membership, SimC tier profile, or G/J/F/O. No new-seas​​on-ready environment was installed, no new SimC Native DPS measurements, no class tier effects reimplemented.

## Next work without redoing finished research

1. Establish an independently verified NEW season→ItemSet relation, preferably Blizzard Game Data season rewards/token conversion or another native DB2 relation. Actual direct ItemSet physical item→JournalEncounterItem intersection was zero for both S1 and S2: do not repeat that approach. Do not silently select highest ID or use season-only expansion. If source relation cannot be proved, mark candidate stage pending, do not resurrect name-first HTML parsing.
2. Once season membership is proven, feed exact 13-class set IDs and existing v161 physical snapshot into original v168, and use original SimC tier/profile stage rather than new mechanics. Source level proof and actual SimC profile acceptance remain separate claims.
3. Integrate remaining season G/J/F/O auto construction, B/T, automatic verified choices and v212 user profile/adaptive SimC execution. Avoid a separate large tier pipeline or blanket new Native sweep.

Permissions unchanged: isolated branch only, main/v003/v016 immutable, Project UI/Instructions/WorkOS or main dev-chat authority untouched.
