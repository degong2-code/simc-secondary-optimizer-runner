# v176 — 26 DPS current-season representative physical SimC smoke

**2026-10-30 KST: user-requested full-specialization physical coverage.**

## Verified actual scope

- Execution: [Actions run #40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357), isolated branch `probe/chat-cache-v035-20261024`, triggering commit `5bba261f01da150a3b7cc881ff1cf7969d7c780c`.
- All **26/26 DPS** specialization profiles compiled using **511 candidate current-season gear DB**, including the returning Mythic+ dungeon candidate pool, and **13-class/65-tier-piece** source-first tier set. Augmentation Evoker remains outside user-approved product scope.
- Scenario: **target ilvl 334**, each specialization's two current-season-DB-eligible starter trinkets, class/spec/race/talents, internal four-tier/ordinary gear/weapons, **O=0**. No user-selected special-effect or crafted item. **35 requested iterations per profile**, no rating optimization.
- Real Native: **25 new one-shot SimC calls**, **1 v174 exact SHA-verified paladin/retribution physical receipt reused**. SimC revision `7bc10711b5`, exact binary SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e` reused from GitHub cache, no binary rebuild.
- **26 PASS / 0 FAIL / 0 BLOCKED**. Every original per-spec JSON2 SHA256 matched its native receipt, with single-player positive mean DPS. The preceding all-spec preflight did 0 new Native calls.
- Inputs, raw SimC logs, JSON2, receipts and summary: [artifact #12941461212](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357/artifacts/12941461212), 7-day retention. Actions logs persist separately.
- Focused offline **3 PASS / 0 FAIL**. Adaptive search **0 new calls**; 95% candidate ranking, global optimum, special effect variants, exact L, O>0, manual final T and non-334 target ilvls are **not established**. The sample DPS means below are diagnostics, **not a cross-spec performance ranking**; talents/trinkets vary by spec.

## Native evidence summary

| Specialization | Physical test | SimC sample mean DPS |
|---|---|---:|
| `deathknight/frost` | PASS | 179,550.05 |
| `deathknight/unholy` | PASS | 175,385.61 |
| `demonhunter/devourer` | PASS | 195,122.79 |
| `demonhunter/havoc` | PASS | 199,562.95 |
| `druid/balance` | PASS | 157,893.84 |
| `druid/feral` | PASS | 178,874.14 |
| `evoker/devastation` | PASS | 166,782.86 |
| `hunter/beast_mastery` | PASS | 210,241.62 |
| `hunter/marksmanship` | PASS | 195,689.40 |
| `hunter/survival` | PASS | 199,601.74 |
| `mage/arcane` | PASS | 147,850.12 |
| `mage/fire` | PASS | 144,087.54 |
| `mage/frost` | PASS | 155,504.68 |
| `monk/windwalker` | PASS | 176,009.37 |
| `paladin/retribution` | PASS | 179,593.14 |
| `priest/shadow` | PASS | 154,728.65 |
| `rogue/assassination` | PASS | 190,232.51 |
| `rogue/outlaw` | PASS | 200,436.97 |
| `rogue/subtlety` | PASS | 218,820.50 |
| `shaman/elemental` | PASS | 205,759.70 |
| `shaman/enhancement` | PASS | 172,675.44 |
| `warlock/affliction` | PASS | 171,272.25 |
| `warlock/demonology` | PASS | 171,082.90 |
| `warlock/destruction` | PASS | 160,371.54 |
| `warrior/arms` | PASS | 193,693.58 |
| `warrior/fury` | PASS | 204,856.40 |

## Continuity

Keep existing v098/v106/v113 production profile/session/cache identities unchanged until the standard P1 flow is deliberately integrated. Do not rerun all 26 without an actual invalidating change; reuse this exact evidence. Earlier v175 static CHMV first-seed verification is separate and applies only to paladin/retribution. `main`, `v003`, original product, Project UI and Work OS remain unchanged.
