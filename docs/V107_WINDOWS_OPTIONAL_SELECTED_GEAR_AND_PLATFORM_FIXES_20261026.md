# v107 — Optional special/crafted items in Windows user UI; first real Windows platform validation

**2026-10-26 KST · isolated GitHub branch only.** Final current support scope is **27 DPS specializations**, not tanks/healers. Six source-backed DPS archetypes currently available in beta. Product is target ilvl (default 334) or manual final oil-inclusive CHMV T, **not current-gear rebalancing** or season-wide equipment recommendation.

## Implemented P1 behavior

- Extended existing `runner/v106_user_session_controller.py` with optional user-selected `special_items` / `embellishments` in **exact pre-existing v098 schema**. Added `selected_rows_from_form` typed parser that omits empty rows and blocks incomplete/invalid entries; it never implements item effects, procs, gear search, solver or DPS statistics. A special and crafted item cannot occupy the same slot, and crafted options require explicit `embellishment` while catalyst redirected source cannot be treated as crafted.
- `runner/v107_optional_items_dialog.py` implements a **small optional** Tk dialog, two rows for selected special effect gear and two rows for crafted embellishments; only user-chosen slot/ID + exact SimC syntax modifiers are exposed. Special supports `bonus_id` and `redirected_base_stats`, crafted supports `crafted_stats`, `embellishment`, `bonus_id`. These tokens are passed to the already existing `v098/v101` source-backed composer and then directly into SimC. **This UI does NOT independently certify source effect procs and does not imply universal coverage of all source option types.** Maximum 2 user-selected special rows **in current UI only** versus up to 8 in the underlying v098 contract.
- Windows `runner/v106_windows_simple_gui.py` adds the dialog launcher and optional **exact static Native item variant cache JSON picker**. A selected special with no cache is blocked at session creation. If a cache was provided but lacks the **exact** selected non-trinket special item/ilvl/options static record, the existing v098 static-L budget preflight blocks before any SimC Native call, never treating unobserved L as zero. Trinkets do **not** require a Native static record, are outside G, and remain two user-choice IDs. Crafted initial `crafted_stats` are not locked as L. Selected catalyst tier is **one physical slot** with user original ID + tier 4set contribution + exact fixed L once; SimC owns full item/source effects. 4-of-5 tier placement is guarded by the existing shared composer.
- Canonical session key already binds the user's exact selected items and their option tokens plus binary/revision and **selected static cache byte SHA**. Thus altered item/option or cache bytes never silently share an earlier Native DPS result. Same identity continues to use the existing v094 durability, cancellation and cache replay. No duplicated optimizer or new Native API.
- Fixed Windows-specific worker output: `PYTHONIOENCODING=utf-8` in subprocess and `print_user_result` UTF-8 fallback for console-codepage-limited output. No conversion of SimC Numeric data; Korean GUI results can be written to the worker log without `UnicodeEncodeError`.
- Added **root `.gitattributes`** `integration_probes/fixtures/*.simc text eol=lf` to preserve SHA-pinned original SimC source bytes even if a Windows Git checkout has `core.autocrlf=true`. Never globally relax native provenance or rewrite original pinned source SHA requirements.

## Exact validation and historical failures

| Proof | Scope | Status |
| --- | --- | --- |
| [Focused Linux Actions #40340509660](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40340509660) | UI/controller full focused offline 197 tests, existing P1 + 6 new v107 examples, compile/pilot | **PASS 197 / FAIL 0; new Native 0** |
| [Linux Actions #40341136985](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40341136985) | After Windows UTF-8 fixes, full P1 focused offline suite | **PASS 197 / FAIL 0; new Native 0** |
| [Initial Windows Actions #40340779415](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40340779415) | Actual Windows 2022, default Git worktree CRLF and cp1252 stdout exposed original-source SHA/Unicode failures | **FAIL historical**; not recast as PASS |
| [Corrected Windows Actions #40341246603](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40341246603) | Windows 2022 Tcl/Tk headless runtime import; real Windows `msvcrt` exclusive worker lock, cancel marker, user scenario/catalyst synthetic-static tests and pilot; checkout globally configured LF | **PASS 14 focused Windows tests, new Native 0** |
| [Default Windows checkout Actions #40341783290](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40341783290) | Explicit `core.autocrlf=true` checkout, real all-six SHA-pinned weapon source fixture integrity, Tk import, same 14 Windows controller/selection tests and pilot | **PASS 14 Windows tests, new Native 0** |
| [Previous actual Native #40335091679](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40335091679) | One actual v105 Paladin full user→Native DPS/SEM/95%→6/6 cache replay | **historical real Native 6 calls, not rerun or broadened** |

The new cross-module selection tests use **explicitly synthetic** exact static cache records (Shaman catalyst fifth head + crafted shoulders) and prove one locked L, four tier slots, preserved original ID in `redirected_base_stats`, stable free B/final T, and correct Native cache identity. No new Native record for that exact special item was created or certified. Overlapping special/crafted slots, invalid options, absent exact static cache, bad unsupported slots fail closed. The legacy default 334 reference is `B=3150`, oil applied once `O=crit16+haste16=32`, final `T=3182` (Shaman one-weapon example likewise). A `manual final T` is user override and must not be confused with this default.

## Still not implemented or proven

- Windows Tk **actual interactive click** and a locally installed **Windows simc.exe** real DPS+SEM Native run with interrupted execution, on-click stop and same-session full resume. Windows CI is **platform+input/offline** validation, not real Windows SimC or visual GUI test.
- Full user-selected gem/socket, Omnium, flask, food, potion etc.; other source item options not exposed in current bounded dialog; exact user item IDs must still be known, not a complete gear or loot-name search.
- One-click standalone packaged app without Python/Tk/SimC installation. SimC executable and matching revision are still user setup fields; prior Linux real Native binary is not a Windows executable.
- Other 21 DPS specs beyond six source-backed profiles; tanks/healers **deliberately excluded** by latest user direct scope decision. No assertions of global optimum, season-wide proc certification or any new effect mechanism.

## Next efficient P1

1. Native Windows local smoke when access to actual installed Windows SimC is available; exercise GUI on-click cancellation/resume **once** and preserve original error/receipt without redundant historic Native sweeps.
2. Finish gem/Omnium and flask/food/potion user input serializers using SimC-native options and existing `G+J+F+O` formulas; avoid converting source effects into our own mechanics or expanding the full equipment DB.
3. Once the full user flow is simple, reuse existing 6 verified source profiles and small class/spec-tier/weapon data to expand toward 27 DPS; do not conflate interface progress with all-27 Native coverage.

**Authority:** only isolated `probe/chat-cache-v035-20261024` branch modified. No main merge, protected v003 change, official Work OS/M0 or Project UI Sources/Instructions application. Primary separate product chat retains general product owner role.
