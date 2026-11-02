# P3-AM — one-time original public tier source HTTP pilot, 2026-11-02

The original one-shot GitHub Actions run [#41422198932](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41422198932) COMPLETED SUCCESS. It used actual external HTTP GETs, not offline fixtures, for exactly two sources:

- GuildLoot current Retail tier HTML: 14,018 bytes; SHA-256 a2642f38bdc3022a15505ff694695ceab2a895dbe328c7578eceb99850507a7b.
- Wago ItemSet.csv pinned to build 12.1.5.70575, locale enUS: 92,549 bytes; SHA-256 0ae48ff20e117ba0d4bc30d6934819b752785cca0d61cbb0b5812ed99bd19bc6.
- The exact same v243 parser matched 13 publisher class names to 13 distinct ItemSet.Name_lang rows for current season 2: P3_TIER_PUBLISHER_ITEMSET_MATCH_PASS (classes 13; unique_sets 13; season 2). No user credentials, no SimC Native, no full 10-table Wago repetition, and no DPS-cache mutation.
- This was a **same-season live source parser pilot**, not a future/new-season zero-history end-to-end acceptance. It did NOT fetch fresh ItemSparse/Item or prove the 65 physical pieces against real bytes in this run; the original v168 65-piece physical check was independently proven on synthetic same-build DB2 in the shared Ubuntu/Windows CI. No new season G/J/F/O, budget B/T, registered options, v212 install or full adaptive SimC are proven by this source pilot.

The temporary workflow was a one-time research instrument; after confirming success it was removed from the ongoing branch. Its GitHub Actions run/logs and the code/test source receipts remain inspectable. The production normal Build path uses v216→v243→existing v168 directly; it does not depend on a permanent GitHub Actions workflow or GPT invocation.

Next: when the game actually publishes a different season/build, let the **same Build engine** fetch both current public tier titles and requested-build Wago ItemSet, independently verify current expansion/season via v155/v163, and require all 13 exact pairings + existing v168 physical constraints. Fail closed to pending if the external publisher HTML layout changes, names are missing, or the current raid/season identity cannot be verified. No historical class set title/ID may become a source seed.
