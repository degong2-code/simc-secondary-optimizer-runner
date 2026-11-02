## Follow-up P3-AM: actual public source was fetched and parsed

After the offline tests recorded below, a bounded one-shot real HTTP pilot succeeded: GitHub Actions #41422198932, two source GETs, HTML 14,018 bytes SHA a2642f38bdc3022a15505ff694695ceab2a895dbe328c7578eceb99850507a7b and Wago ItemSet CSV 92,549 bytes SHA 0ae48ff20e117ba0d4bc30d6934819b752785cca0d61cbb0b5812ed99bd19bc6, exactly 13 publisher classes and 13 unique physical set identity IDs matched by the same parser. This is CURRENT SAME-SEASON SOURCE PARSING ONLY; not future-season identity, live 65-piece physical evidence, full environment build, GJFO, or Native DPS. See P3_AM_20261102_LIVE_TIER_PUBLIC_SOURCE_PILOT.md.

# P3-AL 2026-11-02: New-season tier-name source to original v168 (evidence and limits)

## Goal, original flow and actual result

One normal per-season Environment Build, not a duplicate gear database. On an explicit fresh source Build, the existing v161 sealed Wago 10-table source and v155/v163 observed season join can now call the new *source-only* v243 intake, which then delegates the physical 13-class x five-piece check to the EXISTING v168.

A source URL that is expected to update season to season is https://guildloot.de/en/set/retail/. The official current-release corroboration is https://worldofwarcraft.blizzard.com/en-gb/news/24294369; this official article is not automatically fetched by runtime. v243 fetches GuildLoot HTML and just one additional Wago table ItemSet, pinned to the same requested game build. ItemSet.Name_lang and ID exist in the WoWDBDefs ItemSet definition: https://raw.githubusercontent.com/wowdev/WoWDBDefs/master/definitions/ItemSet.dbd.

v243 requires a unique publisher class label adjacent to its exact full set title for all 13 classes, a unique ItemSet.Name_lang match per class in the fresh CSV, and matching publisher and independently observed WCL Mythic+ season number. It seals source URL, raw source SHA/size and outputs with the EXISTING v217. No old itemset IDs, fixed old class names, v144 seeds, or current_season_tier_source_anchors.json are inputs in this new-season route.

Existing v168 still verifies the physical ItemSparse.ItemSet identity, 5 exact core slots and 65 unique physical item IDs, class masks, armor subtype and expansion. Its new optional verified_item_set_ids mapping is only supplied after v243 strict matching. Therefore the marketing title can differ from every physical piece name; e.g. Evoker Echo of Calamity includes differently named chest/legs. The original v168 legacy substring lookup remains for valid same-season historical use, not new-source intake. No Catalyst variant or SimC mechanic is independently certified.

If v163 season scope is not unique, or new publisher source/page structure/set IDs do not match, the normal Build returns a clear PENDING state. It does not reuse last season data or install a half-built environment. Missing G/J/F/O, v222 B/T, v212 manifest and profile still prevent READY. Source URL and build should be revalidated in later seasons.

## New code/test/CI evidence

Isolated functional HEAD e54961ab5487cf754a0413f6d6fbd20639a0ee0b. The CI on initial v243 flattened text matching had two test errors: Hunter could falsely match Demon Hunter class labels. It was corrected to strict adjacent visible HTML text nodes, failing closed if publisher markup no longer supplies a unique pair.

Final v212 environment-manifest offline run #41421659257: Ubuntu and Windows each Ran 340 tests, OK (skipped=4), 0 failures and zero Native artifacts. Final v113 offline API #41421659111: Ubuntu and Windows each Ran 187 tests, OK, 0 failures. The positive synthetic regression explicitly runs mock new-build v161 ten CSV, existing v163 source scope, new v243 publication/ItemSet lookup and existing v168 65-piece verifier within one v216 Build call. Same input reuses stage receipts without repeated external source fetch.

These are OFFLINE test outcomes: 0 real GuildLoot or Wago ItemSet HTTP, 0 new Native. The live publisher HTML shape and Wago CSV bytes have NOT yet been independently fetched/confirmed as passing v243. No new-season installed environment or optimized DPS is established.

## Next P1 tasks

First perform a small bounded real-source 2-URL pilot (GuildLoot Retail and same-build Wago ItemSet) to verify HTML/text-label extraction and source status. Do not treat a publisher update or a matching title alone as proof of global season membership. Then integrate existing v162 Localbots and exact effect relation, v165-v167 representative gear, v189/v190 consumables, already wired v191→v211→v213, season-verified G/J/F/O, v222 B/T, v212 fresh install and SimC profile/worker. Generic expansion discovery (v155 currently Midnight-specific) and multi-raid current-season ambiguity remain known blockers. Final zero-history acceptance only uses the same normal engine with newly fetched sources.

Efficiency: only 2 bounded new URL downloads when v163 provides unique season scope; same-build sealed stage reuse avoids repeat HTTP, v168 retains existing physical checks. No new product-wide Native regression or duplicate gear DB. main/v003/original v016/Project Sources UI/visibility/formal Work OS/chat ownership untouched.
