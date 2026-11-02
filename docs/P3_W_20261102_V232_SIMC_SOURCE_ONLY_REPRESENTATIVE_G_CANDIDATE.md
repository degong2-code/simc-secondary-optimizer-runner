# P3-W — v232 SimC-only source → one-spec provisional ordinary gear and weapons

Date: 2026-11-02 KST. **Isolated branch** `probe/chat-cache-v035-20261024`; no main merge, immutable v003 change, original v016 integration claim, Project UI/Instructions mutation or Work OS promotion.

## Objective

Make meaningful progress toward the approved **season-environment G/J/F/O construction engine**, not a feature-specific one-off. The previous v229 immutable SimC source collector, v230 exact C++ item-data parser, v231 five-piece physical tier join and v169 existing 26-DPS representative selector were separately available, but did not provide a **complete one-spec source-only equipment candidate**. This update connects them without importing historical gear IDs, historical 79×2 G, J/F/O or Native caches.

## Implemented end-to-end *candidate* flow

```text
v229 new generated-SimC source receipt (pinned full commit + Git blob/SHA)
  -> v231 one-spec five-piece source tier candidate (needs explicit set option)
  -> v230 streamed item_data.inc metadata:
        5 exact tier item IDs + bounded ordinary/weapon candidate rows
  -> v232 source-only in-memory ordinary/weapon eligibility filtering
  -> v169.available_plain and v169.shape_weapons (REUSED physical selectors)
  -> v232 one-spec 13 or 14 G-slot IDs, zero Native, G/J/F/O/B/T unknown
  -> [FUTURE] real active-season selection, item effects/real SimC Native
       profile resolution and G static rating proof
  -> [FUTURE] J/F/O verified quality and effect applicability
  -> [FUTURE] validated B/T, original adaptive SimC optimizer, caches and 95%
```

**v230 upgrade:** `parse_exact` accepts **either** exact requested item IDs (unchanged original behavior) **or** a narrowly bounded candidate-filter callback on the generated 28-field C++ records. Both modes retain the same one-pass generated stat-array reference, chunk/count, build and malformed-row validation; candidate mode has a hard 4,500 item memory/resource cap and the result is labelled `SOURCE_CANDIDATE_UNAPPROVED`. It does not download extra source data, run Native or derive numeric scaled ratings.

**v231 upgrade:** exact five tier slots now also retain per-slot source base ilvl and quality, preventing a new-season adapter from applying hard-coded previous-season quality/level thresholds.

**v232 new:** `runner/v232_simc_only_ordinary_representative.py` requires the exact v229/v231 receipt, rechecks the same SimC commit/build, Git blob SHA, tier set/ID/2pc/4pc, actual tier physical rows, class/spec armor restrictions and selected source slot IDs. It builds a compact, request-specific in-memory inventory from source-only item-data rows. Provisional candidates must be non-set items, of the observed tier quality, within a **declared 20 base-ilvl search window around the five tier source levels**, restricted to relevant equipment slots, compatible item type/class mask and armor subclass. The window is a **candidate-search heuristic**, NOT a game item scaling formula or proof of current-season membership. Weapons must satisfy the existing `v169.shape_weapons` primary-stat and weapon-form rules, including Titan's Grip dual 2H, shields/offhands, ranged, etc. Missing source candidates cause an explicit blocked result; **no historical fallback**. Select 4 tier G slots, 4 plain armor slots, 4 shared slots and required weapon slots (13 or 14 G slots).

**Critical safety:** `v232` does **not** pass a source-only candidate through `v167.validate` with a forged `CURRENT_SEASON_CANDIDATE_SELECTION_ONLY` status, nor fabricate a `v225` bundle, assume item-effect absence from `item_set_id=0`, or mark G numeric. It directly reuses the physical selector helpers, returning:
- `SIMC_SOURCE_PHYSICAL_CANDIDATE_NOT_ACTUAL_SEASON_PROOF`;
- tier source and SimC item-data hashes, character/spec/weapon form, exact per-slot IDs and original base levels;
- `same_season_membership_not_proven=true`, `item_effects_absence_not_proven=true`, `native_physical_and_static_G_still_required=true`;
- `G/J/F/O/B/T=null`, `environment_ready=false`, Native0 and cache writes0.

**Manual workflow** `.github/workflows/v229_simc_only_source_seed.yml` now copies v229–v232 + v143/v167/v169 selector code into the separate temporary source-only workspace, checks no old data copied, runs the offline tests, and (when exact source commit/build plus an opt-in large `item_data.inc`, a class/spec/set option are supplied) attempts v231 and v232. The provisional source preview stage has `continue-on-error` because inability to find suitable *optional physical candidates* must not silently discard already acquired immutable SimC source evidence; the workflow logs a candidate-stage failure and retains the short-lived source artifact. It **does not dispatch automatically**, change the existing production season DB or run Native.

## Evidence and efficiency

- v230 source-only filter and v231 tier-quality changes retain backward compatibility with existing exact-ID callers.
- New `tests/test_v232_simc_only_ordinary_representative.py`: synthetic source-only paladin retribution 13 G slots; ordinary chest versus fifth-tier chest; two distinct rings; rejected wrong armor, quality, class mask and base itemlevel; exact expected weapon; corrupted source SHA/receipt; no historical files; deterministic requests; missing waist/weapon failures; target ilvl change never injects historical G or scaling; CLI output. Synthetic fixture IDs/rating types **are not actual Native measurements**.
- Focused [Actions #41391974540](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41391974540) **Ubuntu 237/237 PASS; Windows 237/237 PASS; Native0**.
- Added a one-spec Fury Titan's Grip fixture validating *two distinct* SimC source-only 2H weapon IDs and 14 selected G slots, without any actual Native rating proof. [Follow-up offline Actions #41392328508](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41392328508) covers the additional regression; the run result is authoritative.
- The optional v229 manual source-collection workflow update is code-reviewed but **not dispatched**; no new real 26MB SimC item-data download or actual zero-base experiment has taken place. Existing v229–v231 test evidence is separate from a real season dataset.
- A single v230 generated source scan is reused for five tier rows and all one-spec generic gear/weapon candidates; 4,500 candidate hard limit and requested-only physical output avoid a huge persistent user equipment DB. Previously verified same-season static cache remains reusable in normal product, never in future zero-base exam.

## Product readiness and next efficient step

The long-term purpose is **SimC DPS optimized future absolute CHMV** for 26 DPS specs, not redistribution of current stats, full character gear selection, item recommendation or all-season DB.

**Not complete:** Current-season tier-set option is still a caller-supplied source token, not authenticated game-season discovery. A non-set item with matching physical metadata is not automatically a normal/effect-free item or a verified *in-season* representative. Native item acceptance and binary/game-build/profile provenance are not newly executed. J/F/O actual same-season highest-quality values, E/L accounting, B/T and P1 user-profile runtime integration are pending. Do NOT report `v232` as new-season ready or G measured.

**Next:** derive authenticated season identity, or an independently verified SimC source signal, without copying old names; then connect the provisional chosen 13/14 slots to the existing v226/v227/v228 exact Native static G measurement path (without forging v225 receipts), and validate real G → J/F/O → B/T. Only after engine completion perform the user's final **strict SimC-only zero-base controlled experiment**, where historical source files, old caches/receipts and Wago/Blizzard access are actually blocked and audited; compare the sealed outcome with historic evidence only afterward.
