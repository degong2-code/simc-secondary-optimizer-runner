# P3-AX — Lazy full pinned SimC item source inside normal Environment Build

**Date:** 2026-11-03 KST. **Authority:** current DPS26/v1.4.3/P3-AA engine-first policies. **Branch:** `probe/chat-cache-v035-20261024`; main / immutable v003 / original v016 / Project UI / Work OS unchanged.

## What changed

The original `v216.collect_wago_new_season_source` now extends the already-collected, pinned small `v229` SimC source only when **all** of the following exist: one validated DPS specialization/target-ilvl request, source-backed v167 ordinary gear candidate, v251 raid-correlated tier candidate, and a pinned v229 small three-file source.

A new `v216._lazy_full_pinned_simc_item_stage` reuses `v229.inventory`, `v229.discover_generated_tree`, `v229.git_blob`, and the original immutable source revision. The stage rechecks the already-sealed small receipt against all three exact source bytes, then walks the fixed 4 Git tree endpoints, checks the original three tree blobs and downloads **only** `item_data.inc`. It checks max 32 MB, exact byte count, Git blob SHA-1 and generated game build; writes a separate full four-file source directory with a new v229 receipt, sealed and cached by existing `v217`. The three original small files and receipts are not mutated or re-downloaded.

A successfully pinned full directory is passed to the existing `v251.select_for_simc` / `v232.find_candidate` one-spec stage. This is still a source-only candidate: actual current-season membership, SimC static item effects, physical G, verified J/F/O and B/T, Policy-A user option admission, and user Start/DPS are NOT proved. Incomplete source and network failures return honest PENDING statuses and never auto-install a season or replace it with old PvP/old gear.

The new stage's immutable identity includes full 40-hex SimC revision, build, original verified small receipt SHA and code fingerprint including v216, v229 parser, v217. Stage reuse: no new Git tree walk or item download. Source memory is bounded to original v229 `MAX_ITEM_FILE`; source hashing/cached verification uses the existing streaming SHA path.

## New tests and actual evidence

- `tests/test_v256_lazy_full_pinned_simc_in_build.py`: 5 synthetic tests: initial 4 Git-tree calls + 1 file transfer; same input 0 HTTP; original small receipt immutable; missing requested gear/tier produces 0 HTTP; tampered small bytes reject before network; bad exact Git blob fails closed; old game build item_data fails closed.
- Existing `v212 Environment Manifest offline contract` Ubuntu/Windows CI now includes the new test module, not a separate verification engine.
- **CI for first functional version:** [Actions #41475760128](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41475760128), code `7dead85691ec465b2d1a6c0e87a9d6587748092a`, actual Ubuntu and Windows **376 tests each / 0 FAIL / 4 SKIP / SUCCESS**, offline and Native0.
- **Final code** `7b7bdf5072d5cd206453622595e96308b76c3a74` added v216 orchestration code to the stage fingerprint. [Final v212 Actions #41476043867](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41476043867) — record its real final PASS/FAIL independently. Never infer PASS from the first run alone.
- **New real external Wago or SimC fetch: 0**, **new Native: 0** in this P3-AX task. The HTTP counts are synthetic transport observations; no assertion of complete real source coverage or validated G.

## Remaining practical critical path

1. The `v113` API currently forwards a validated spec/target ilvl but **not an automatically resolved full SimC Git revision and new-season provenance**. Standard user requests may supply only a shortened SimC revision; never treat 7-hex as an immutable 40-hex source identity. Connect the existing SimC binary updater/revision metadata to the internal pinned source identity, with current game build independently checked.
2. Run **one bounded actual same-build SimC full-item source acquisition**, preferably reusing existing P3-AT pinned revision/receipts, followed by a one-spec `v167×v251×v232` real candidate coverage check. Missing ordinary gear/weapons should be reported as exact missing slots, not filled from old PvP gear.
3. Build/verify the representative level-specific G (using the already-existing bounded Native static workflow when required); in parallel automatically acquire and prove top-quality J/F/O and enchant E under the approved once-only accounting. Reuse v222 for B/T and existing v098/v212/optimizer; do not create a parallel solver or repeat a full 26-spec Native matrix.
4. The final same-engine zero-prior-data acceptance is still pending. Historical receipts are background guidance, not clean acceptance inputs.

**Explicit completion boundary:** P3-AX implements a lazy source extension with synthetic two-OS CI; it does NOT complete an automatic seasonal Environment DB or a full end-user workflow.
