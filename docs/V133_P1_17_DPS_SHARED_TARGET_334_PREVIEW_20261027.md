# P1/v133 — one target-level representative-profile preview for 17 new DPS sources

2026-10-27 · only isolated `probe/chat-cache-v035-20261024` branch.

## Actual new baseline evidence
User's home Windows `v132 --audit`: offline **17/17 exact SHA/APL/slot PASS, Native0**. Then `v132 --simc "C:\\Users\\degong2\\Desktop\\Wow\\SSfindout\\SIMC\\simc-1210.01.7bc1071-win64\\simc.exe" --max-new 17`: **all seventeen original MID2 source profiles actual Native PASS**, binary SHA256 `b0ea12ee3ac233a4a590609e2a5bd4c4db45c5f8ae6f8994b1b8d0de4d5acff4`, `native_calls_this_run=17`, `status=PASS_ALL_ATTEMPTED`. Preserve these as **original-source smoke** receipts. Do not rerun them, and do not confuse them with target334 representative CHMV optimization.

## What is actually newly implemented

A **single common v133 source→target-level draft generator** `runner/v133_mid2_target_representative_preview.py`, not another class-specific optimization engine:
- Reads all 17 existing exact-source v132 fixture bytes through v132 validated SHA/class/spec/APL/gear read path, reuses v129 common gear parser, v128 source-preserving line emitter, and v055 exact physical equipment format, level default **334**.
- Groups class five-tier identity in one explicit data table using currently pinned v127 IDs plus both new MID2 same-class sources and the three independently identified season items. Missing source-tier witnesses **Monk hands 271520**, **Priest shoulders 271553**, **Warlock head 271546** are grounded in public Midnight S2 item-identity references (WoWTopGear, WoWDB/Wowhead, TransmogDB), **not guessed by contiguous ID arithmetic**. These are item identities, not independently verified Native gear static ratings.
- Applies one **family-level** fourth-tier/off-slot policy: plate legs `271878` (earlier source-verified warrior); leather chest `251159`; mail head `249317`; cloth head `271874`. All target gear rows are at the specified ilvl and original source APL/action order and exact weapon/trinket identity stay intact. Original exact source character/talents/Omnium are not manufactured. Original-source *non-tier items* remain provisional; they are **not certified ordinary/no-proc across all 17**.
- Replaced off-slot cannot inherit crafted/random effect options. For head-only mail/cloth replacements with source-observed diamond and earlier socket witness, retain only observed diamond IDs; any unsupported six ordinary socket pattern, four gem colors for `240967`, or source consumable/flask F/Omnium mapping is **explicitly reported**, not automatically faked.
- Produces a group report and 17 preview-only `*.simc` files with a single shared generation function. Stage files are deliberately **NOT a v098 executable user manifest and NOT a v094 candidate**; they have no CHMV budget/Native JSON2 identity and are not enabled in the public UI. No old session files, receipts, caches, or product controls changed. Each record reports `ready_for_user_optimizer=False`, `native_calls=0`, unresolved conditions.

## Offline test evidence, scoped

`tests/test_v133_mid2_target_representative_preview.py` exercises all seventeen profiles in one suite: APL preserved exactly, 4/5 tier ID match in target ilvl 334, retained original 15/16 physical slots, weapon/trinket identities, source immutable after rendering, ilvl 321 alternative, diamond retained only on source-backed head IDs, incomplete remaining conditions and no Native/UI write. The previous v132 source SHA/one-call mock/cache-resume regression is run alongside in the **existing** automatic cross-platform `v132_mid2_sources_batch_offline.yml` workflow. Result must be taken from actual head Actions run, not presumed. No repeat of the 17 actual source Native smokes or 3 prior Windows full 6/6 product examples.

## Why this does not claim 24 supported target optimizers yet

The old validated seven-spec `v127/v101/v098/v122/v094` executable API remains unchanged; all seventeen new source-backed profiles **still need** source-neutral ordinary filler treatment (especially copied special/crafted source gear), real gem socket/diamond and consumption F mapping to the target-budget `T=B+O`, and independent single-profile representative Native acceptance, after which the same existing adaptive engine can be used. The previously source-known 24/27 roster leaves 3 missing official MID2 original profile sources: Balance Druid, Devastation Evoker and Augmentation Evoker. No 27×6 repetition or per-effect gate.

Efficiency: one shared generator rather than 17 factories, no new Native, no new item DB, no redundant cache invalidation; fixes only truly invalidated source-to-target path.

main/v003/Project UI/official Work OS or Shared State untouched.
