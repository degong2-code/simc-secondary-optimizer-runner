# P3-BN — SimC owns default max level; optional character choices; environment owns all item/effect inputs
2026-11-03 · latest direct user decision (supersedes conflicting P3-BM level preflight)

## Product decision, implemented scope

1. **Character level**: do not infer from Blizzard expansion + WCL + DB2, hardcode level 90 in new-season profile, ask the normal user for a level, or create a new gate. Pinned SimC source revision `710c2408bfd3ae4df71b8cd55cdf01f63fd6c926` has `engine/config.hpp: constexpr int MAX_LEVEL = 90`, `engine/player/player.hpp: default_level=MAX_LEVEL` and `player.cpp: true_level(default_level)`. As the binary advances, its compiled default is its own responsibility; runtime/profile/source compatibility must still be checked. Normal `v233` and `v234` profiles **omit `level=`**; an internal optional explicit level remains for legacy/probe reproducibility, NOT a new user field.
2. **Race**: if user supplies it, keep it. If omitted, null, empty, or whitespace, **dwarf** (explicitly labeled in UI). Dwarf cannot be a druid, demon hunter, or evoker; those specializations must supply an eligible race instead of a hidden auto-substitution. Existing v143 evoker limited-race contract and native acceptance remain. Prior sessions with an explicitly selected race remain unchanged.
3. **Talents**: if provided, use exact submitted code after existing validation; if omitted/null/blank, pick the already verified **per-class/per-specialization representative talent code** from the product's pinned compact `v146_character_starter_examples.json` (24) or existing source-only two-spec starter records (balance druid, devastation evoker). No heavy complete SimC profiles are needed at runtime, and no sample gear or consumables are imported. The historical pinned representatives are example defaults, **not declared global DPS-optimal or independently new-season proof**. Updating season-appropriate talent examples may be considered using the same pinned SimC source evidence, only if shown necessary.
4. **Program authority**: ordinary representative gear/weapons/4pc, special gear, trinkets, crafted options, gems, flask, food, potion, oil, enchants, Omnium/special modules and their **G/J/F/O/L/E/CHMV account ownership** remain **wholly under the environment/normal user-choice/profile compiler**. SimC processes effect mechanics/APL/procs/DPS and is a reference for optional sample gear IDs/talents, item metadata and physical Native stat acceptance; its sample profile consumables or worn gear are **never copied as the environment budget or user choice**.
5. **Source-only physical G**: `v216` dropped `_source_expansion_level` and its v163-based numeric level gate, uses validated `v113` effective race+talents with no level; `v233` receipt marks `level_mode: SIMC_COMPILED_MAX_LEVEL`; v217 preserves per-character source profiles and hash-sealed inputs; `v234` and `v236` honor this exact default-level profile without changing their 0/1 Native execution cap, binary/source SHA, gear identity, cache or readiness constraints. Explicit-level older v236 input order remains accepted with strict byte checking.
6. **Input UX**: `v106.user_scenario` now accepts optional `race`/`talents`, resolves effective values before profile/session/cache identity, and preserves explicit values. HTML shows `미입력 시 dwarf` and `비우면 기본 대표 특성`, warns users whose class cannot be dwarf; the optional SimC import accepts a single class/spec with race/talents if present and imports **no gear, stat totals, trinkets, consumables, effects or current equipment**. Imported missing fields are handled by the same normal fallbacks.
7. **Old UI and prior sessions** remain readable; backend source `standard_controls` examples still provide their original explicit example races/talents for regression/reference, but new UI fields start empty to **visibly indicate optional selection**. Backend omitted vs explicit values are both normalized and bound to effective `user.character` before session-key construction. No user level field added.

## Real code and CI scope

- Code changes:
  - `a50d45a9d0edd5ff5fc6acb4cf5c89d537333bb2`: optional user race/talent resolution and explicit UI fallback, plus tests.
  - `ab4bc83af075de73fc54f42916355f549fa4de30`: removed expansion gate and made v233/v234 level optional; first CI **failed** on exact-profile seal and one substring assertion.
  - `34327ac9256fbd4f46a25dfbd0a5a5146499278e`: fixed the profile-order compatibility, updated v236 byte-exact validation for absent level, added Native0 sealed regression, corrected line-only assertion; final **backend** tested SHA.
  - `3c781c12a275a1e7edb08af548a5119f61aafae2`: optional SimC import race/talents to match user defaults, plus UI source test; final **functional** SHA including UI import.
- Backend regression at `34327ac...`:
  - [v212 #41561544788](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41561544788): Ubuntu/Windows each **428 tests, 0 FAIL, 4 SKIP**.
  - [v113 #41561544839](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41561544839): Ubuntu/Windows each **204 tests, 0 FAIL**.
  - [v181 #41561544797](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41561544797): SUCCESS Windows beta (two Python versions).
  - [v182 #41561544799](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41561544799): SUCCESS Ubuntu+Windows UI.
- Final `3c781c...` UI-import+test SHA workflow:
  - [v113 #41561808378](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41561808378)
  - [v181 #41561808381](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41561808381)
  - [v182 #41561808389](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41561808389)
  - [v167 #41561808395](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41561808395)
  - [v177 #41561808380](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41561808380)
  - [v180 #41561808408](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41561808408)
- **Final SHA `3c781c12...` verification: all six workflows above completed SUCCESS**, including two-OS v113 (204 tests each), two-OS v182 UI (92+82+2 suites), Windows v181 beta (142 tests for each Python version + existing loopback HTTP 3-plan restore), v167 focused (14 tests, 1 SKIP), and v177/v180 offline flow. The `v180` real Native six-case job is guarded by a special one-time commit token and was not activated by this commit.
- These CI runs are *offline / synthetic* (some legacy job names contain the word Native or actual historical scenarios). **New actual SimC Native 0, new real game HTTP 0** in P3-BN. The failing intermediate runs are deliberately preserved, not described as a product engine failure once corrected.
- No G/J/F/O/B/T numeric values were established or promoted; active-season 13/14 gear and full tier identity still need independent current evidence; Env READY and complete target user DPS E2E remain pending. Full native/source compatibility is not automatically proven by omission of level.
- Latest user's exact policy on highest-quality item choices, oil not double-added, fixed L within G, manual T priority, 26 DPS and 95% inference remains in force.

## Most efficient continuation

Continue core **authenticated season G/J/F/O source build → B/T via v222 → validated highest quality choices/Policy A → representative exact SimC profile → existing adaptive DPS/caches/cancel-resume**. Prioritize actual selected physical items and season/tier membership, reuse existing v233/v234/v236/v046 evidence for one minimum G observation if useful, not speculative global WSE, no new optimization engine. SimC representative profiles may supply **candidate IDs, talents or structural hints only**, while all item choices, item levels, static rating constraints and profiles remain compiled and approved by our environment engine. Evaluate and optimize source-stage caching before additional heavy live API/Native operations; don't repeat 26 specs.

## Authority boundaries

Only branch `probe/chat-cache-v035-20261024` changed. Existing primary product developer chat owns product implementation and ordinary Native runs. Do not merge main, mutate immutable v003, original v016, Project Sources/UI, official Work OS shared state or WEQUIP. User decision makes this policy current even if not Project UI promoted.
