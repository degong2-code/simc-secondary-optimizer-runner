# P3-BB — Active-season context and removal of spurious previous-client-build gates

**2026-11-03 KST.** Isolated `probe/chat-cache-v035-20261024` only. No main/v003/v016/Project UI/Work OS changes.

## Current external season context — separated proofs

1. **Official Blizzard, 2026-10-13**: Midnight's **12.1.5** content update is live and provides **Season 2 mid-season refresh**. [Blizzard live update](https://worldofwarcraft.blizzard.com/en-us/news/24307306/midnight-s-12-1-5-content-update-is-now-live).
2. **Official Blizzard, 2026-10-31 publication (October 30 hotfixes)**: 12.1.5 continues receiving hotfixes. A hotfix does not by itself assert a new client build. [Blizzard hotfixes](https://worldofwarcraft.blizzard.com/en-us/news/24307310/).
3. **Community client-build record**: Warcraft Wiki public client builds listed Retail 12.1.5.**70575**, dated **2026-10-22** when checked. This is a separately sourced client-build record, not a real-time handshake with a user's executable. [Public client builds](https://warcraft.wiki.gg/wiki/Public_client_builds).
4. Existing **P3-BA actual Wago + exact SimC** source evidence is for the identical Retail build `12.1.5.70575`; Wago `Item`/`ItemSparse`/`ItemXItemEffect` 328/328 plain candidates physically corroborated; `paladin/retribution` 13 slots. See [P3-BA](P3_BA_20261103_REAL_WAGO_SIMC_ONE_SPEC_SOURCE_COVERAGE.md).
5. **Never equate these sources**: official patch/season announcement, community build listing, Wago DB2 build identity, exact pinned SimC source revision, actual user's SimC executable and item active-season membership have distinct proof scopes. M+ world-state and Localbots alone do not prove the selected representative.

This allows treating P3-BA as a reusable **same-build** source proof when the actual local game/SimC build is `12.1.5.70575`. It does **not** prove each selected item or an exact target-334 Native G / E / J / F / O.

## Implementation — no need to invent the previous game client build

- `runner/v224_season_gjfo_evidence_inventory.py`: `core_source_preflight` and `compile_inventory` no longer require a *locally recorded previous game build* when event is `season_change` or `expansion_change`. Nor do they claim a new season must necessarily have a **different client build**; transition membership is independently sourced. Build syntax and exact same-build gear/tier/budget identities remain required. Receipts preserve `request_event`, `previous_game_build`, `previous_build_record_status` and `previous_build_is_not_season_proof`.
- `runner/v225_season_source_bundle_intake.py`: immutable manifest accepts an explicitly absent previous local build (`null`), and the CLI argument `--previous-game-build` is optional. The manifest/request previous-build identity must still match; source locator host, pinned source build, SHA and G/J/F/O origin checks remain unchanged. Outputs expose prior-history status, all G/J/F/O/B/T remain `null`, user option promotion false, Native0.
- No change to existing `v222` arithmetic, `v223` same-season budget verification, `v089` approximate reference, `v234` optional Native G, v216 original season Build, old DPS caches or optimizer. This is a necessary dependency correction, not finished season GJF/O auto-construction.

## CI and evidence

`tests/test_v224_season_gjfo_evidence_inventory.py`: 12.1.5 same-client-build new-season source can still only produce unverified component ratings; no-local-history new expansion source preflight; malformed previous build rejected; cross-build source mixing rejected. `tests/test_v225_season_source_bundle_intake.py`: no-history immutable manifest and CLI, correct prior-history receipt, bad prior syntax and wrong source links rejected, all GJFO/T pending.

Early intermediate workflow runs `#41481399582`, `#41481422110`, `#41481520787` failed due to tests that **still asserted the now superseded requirement** that previous client build must exist/differ. They are preserved as evidence of intermediate test/code contract mismatch; subsequently updated, not portrayed as passing.

**Updated focused code+test receipt** [Actions #41481804619](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41481804619): completed SUCCESS, verifying the new v224/v225 contract before the final CLI addition. **Final updated CLI test receipt** [Actions #41481925936](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41481925936): check actual jobs and logs independently before marking final PASS.

## Next product milestone

Keep current 12.1.5/Season 2 physical source cached and compare actual local active/SimC binary build against it; do not recollect identical data. Validate season membership and selected physical loadout, reuse exact same-season `v223/v089` budget sources **only within their already-approved boundaries**; verify selected top-quality J/F/O and relevant permanent E once. Then connect existing `v222` B/T and v098 adaptive DPS with strict Native JSON2 G and 95%-only reporting. **Do not introduce a separate optimization engine or 26-spec Native sweep.**

**Not complete:** new automatic G/J/F/O environmental budget, verified representative profile, active local binary comparison, final user-facing E2E.
