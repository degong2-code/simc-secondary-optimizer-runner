# P1-WEB-3 v121 — v104 template without json2 → strict Native candidate (2026-10-27)

**Scope:** isolated branch `probe/chat-cache-v035-20261024`, preserving user PC's original session and all prior Native/cache receipts.

## Actual user evidence — BLOCKED, not Native tested

- Local Chrome Rogue/Subtlety session `04fe21c0e61b180d305f`, ilvl334, selected `240967` (selection is from the in-progress user scenario; verify against saved `user.json` before final Native claims).
- Progress evidence `V094_PROGRESS(4).json`: `PARTIAL_OR_BLOCKED`, `InjectionError:MISSING_OR_DUPLICATE_INPUT:json2=`, completed 0/6, `new_native_attempts=0`, cache0. Native binary has **not been invoked** by this attempt.
- `V094_SESSION_IDENTITY(2).json`: `B3150/T3214`, oil main/off-hand +32 crit/+32 haste = O64, SHA `b0ea12ee3ac233a4a590609e2a5bd4c4db45c5f8ae6f8994b1b8d0de4d5acff4`, revision `7bc1071`.
- Source inspection: `v104_shared_pinned_rogue_shaman_composer` assembles a representative profile with four `gear_*` and `iterations=35` but **no `json2=` assignment**. Both original pinned Rogue/Shaman SimC source fixtures also omit `json2=`. `v063_numeric_injection.input_parts` previously required *exactly one* `json2=` even when reading a sealed template, so first seed candidate creation fails before Native. Paladin's working profile is separate.

## Minimal source-level correction

- `runner/v063_numeric_injection.py`: add keyword-only `allow_missing_json2_template=False` to `input_parts`. **Default remains strict**: exactly one `json2=`, exactly one `iterations=`, all four gear overrides; duplicate `json2=` always refused. Only explicit template readers use `allow_missing_json2_template=True`, allowing zero or one `json2=` on pre-render sealed source profiles.
- `render_static_chmv_candidate` and `render_candidate` now generate the destination-specific `json2=<absolute path>` when absent, or replace it when present. The rendered Native candidate is immediately passed through **default strict `input_parts`**, so it **always** has exactly one json2 destination. `stable_sha256` excludes only the established mutable gear/iterations/json2 lines: original gear IDs/options, talents, consumables/APL stay byte-stable. **Never rewrite saved `profile.simc` or sealed manifest.**
- `runner/v093_inclusive_adaptive_scheduler_bridge.py` and `runner/v064_adaptive_evaluator_port.py`: source *template* stable-hash checks explicitly opt into missing-json2 compatibility. Strict validations of rendered input, cache receipts, binary identity, scenario SHA and 95% statistics unchanged.
- `tests/test_v063_numeric_injection.py`: 2 new offline tests; omitted template json2 still rejected by default but allowed in explicit template mode, both dynamic/affine and static candidate rendering get one destination and unchanged stable hash; duplicated json2 or missing iterations remain blocked.
- `tests/test_v098_target_user_scenario_bootstrap.py`: new actual v098→v096→v093 request-construction test for Rogue/Subtlety and Shaman/Elemental `240967`: source profile unchanged and lacks json2, Native candidate has one json2 + one iterations, B/O/T conserved, no SimC launched.

## Evidence levels & next bounded verification

- Historical verified Windows 69/69 focused PASS was **before this fix**; do not claim it covers v121.
- Current correction committed, **new Windows regression PASS pending**. Seven relevant modules now have **101 tests** total (v098 29, v101 11, v114 11, v062 19, v063 15, v093 5, v064 11). `unittest` focused command is given in chat. These are *offline* Python tests, expected to execute no Native.
- Only after PASS, open the exact pre-existing Rogue session `04fe21c0e61b180d305f` on company PC under the new repo folder's server and press same-session resume once; candidate count may reach up to six with first real SimC Native. Preserve original runs root and read actual Native stdout/stderr if any new blocker.
- `240967` source physical 6 ordinary gems and 4 colors: offline composition regression covered, but actual Native socket/effect validation is **still pending** and is not proved by this bug fix.
- Main, v003 immutable, Project UI, official Work OS, Shared State unchanged. No new optimizer/Native gate, no repeated Native searches, no static cache rev invalidation, no unapproved release promotion.
