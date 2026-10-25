# v083 — Blood Elf Retribution Paladin, Plate / Single Two-Handed Native Acceptance

**2026-10-26 KST. Isolated GitHub product-development test only.** Not original v015/v016 integrated product, official Work OS gate, comprehensive season gear DB, cross-spec optimum proof, or project policy promotion.

## Source and representative fixture

- Original source: SimulationCraft midnight repository commit `12aa5dc041b03bf9f9fdd1db00dbc8d3ec0cebb7`, `profiles/MID2/MID2_Paladin_Retribution.simc`, actual Git blob **`864e857c5d8cdbaa5b03939f077fcb657a4784aa`**.
- Character: `paladin` / `retribution`, original race Dwarf intentionally set to **Blood Elf** for test coverage. Native SimC was responsible for confirming it could execute this exact race/profile; user-facing race eligibility database was not invented.
- Armor **plate**, **one two-handed mainhand** ID **268213**, **no offhand at all**. The same weapon ID and original item source are retained; all representative gear variants normalized explicitly to target ilvl **334**, preserving source identifiers rather than silently claiming native original bonus properties.
- Four source Paladin tier items **head/shoulders/chest/hands**. A **fifth tier legs** slot from Paladin upstream ID **271464** was replaced by source-backed *non-tier plate legs* ID **271878** from the already pinned Fury source `3225992ed5b754ad5d61e8b785d9d859f1eed1be`. Tier 4 not 5. One representative crafted wrists slot, two original source-backed trinkets, total **15 occupied equipment slots**.
- The original SimC Retribution APL **41 action lines** and talents are byte-preserved. No custom APL/proc/item effect implementation or certification gate was added; all effects and actual weapon validity are deferred to real SimC.
- Fixture uses explicit `flask_of_the_blood_knights_2` with scenario-declared **F haste+165**; not independently established as universal consumable-effect formula. Gem J=138 and weapon oil O omitted. Official product formula **`T=G+J+F`**, oil remains external if ever selected.

## Efficiency: reused existing executable core

Instead of copying the 22k-character v082 Fury runner for another class, v082 `run` gained optional **profile_factory / expected_slots / status / artifact prefix** parameters. With old defaults it still runs original 16-slot Fury; new v083 only composes 15-slot Paladin inputs and passes them to the same runner. Shared v061 scenario, v062 budget, v063/v064 static target application/Native observation, v066 preflight, v065 original v015-derived scheduler and SHA-verifying Native cache remain unchanged. Six additional offline regression checks include fixture ID, original APL, tier count, no offhand, static exact variant missing fail-close, old Fury default runner persistence, and no Native overclaims. No subclass-specific optimizer or full item database.

## Actual GitHub Actions and Native receipts

[Actions **40239319582**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40239319582): **SUCCESS**, request commit **`2874940371582a468c87320a312d022a756883bb`**. Python regression **474 total: 472 PASS / 2 SKIP**, including six new tests. Pinned SimC binary SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`, runtime revision `7bc10711b5`.

- Exactly **four new** bounded 35-iteration SimC Native executions, all PASS (34 usable DPS samples each): one initial exact G static Native; two independent static official-T candidates; one original v015-derived adaptive scout.
- Actual nontrinket exact Native static **G=2849**, declared **J=138**, **F=165**, official **T=3152**. No oil in test. Unobserved trinket stat is not presumed zero. Initial Native `DPS=170796.11523257455, SEM=696.4332046621012`, JSON2 SHA **`96173185393b15bb402ce21d251cf8bea35738ff1461f031bd138040a3a420bb`**: static first-use bootstrap, NOT official target-T ranking.
- Two official actual SimC source/JSON2 cases supplied to **unmodified `v066.prepare_static`** → `READY_STATIC_CHMV_PROFILE_SCOPED`. Original v015-derived scheduler chooses distinct unseen candidate C; existing evaluator and Native executor bind its static target, sum and DPS/SEM. All three `target_static_c == verified_static_c` while separate `buffed_simc_observed` is retained. This fixture's buffed observed values happen to equal c; NOT a universal requirement.

| Case | Static crit | Haste | Mastery | Vers | Real DPS mean | SEM | Native JSON2 SHA256 |
|---|---:|---:|---:|---:|---:|---:|---|
| Official A | 788 | 788 | 788 | 788 | **178239.51865875057** | **804.1814728229649** | `9a1b27c047c86393dc802616d75d2c4ae97fcfa3789f4bd27240f74c76fea258` |
| Official B | 688 | 888 | 788 | 788 | **175959.20097436008** | **606.8048549901147** | `7bd267dab34769e1616176557167ad4fa8e9056134a4b26cab92e1d3c0a0b570` |
| v015-derived scout C | 888 | 688 | 788 | 788 | **178677.66762931016** | **1026.007277842615** | `123454ebc9f3ce6ecd91c7fe79dd58fbad4809f7b2b884112581d37c32031ad5` |

Four Native input and JSON2 result files were **SHA-checked and replayed via cache-only with ZERO new SimC calls**. Durable attempt cap was 4/4 and old results not silently overwritten. Artifact name `simc-v083-paladin-single-twohand-40239319582`, ID **12616730627**, GitHub-reported artifact SHA256 digest **`c55e65973d3bcfe8270e7d21440e8fd4e8fed61b10fd60a55472666a28b17101`** and size **289670 bytes**. Digest metadata confirmed; original zipped artifact was not independently CRC-audited.

## What is still open

This is new **plate / SINGLE twohand/no-offhand** structural evidence, distinct from Fury plate dual-twohand, Hunter ranged/no-offhand, Shaman mail shield; existing Rogue/Mage historical evidence has separate limitations.

- The most important unproven representative weapon form under user-requested six-case matrix is **Arcane Mage cloth / one-hand plus nonweapon offhand** with exact Human character, static c mode. Rogue leather dual-onehand case already has real Native evidence but newer static-c semantics must be assessed before counting it as fully current.
- The old Shaman one-hand+shield success used legacy/buffed-target semantics and must be replayed or tested with corrected static-c semantics to be counted under new contract.
- Full general profile/consumable F/E source attribution, user-selected oil O input separate from T, 0/1/2 embellishment variants, arbitrary ilvl/manual T and original v015/v016 integration remain. Complete all-class/role proof and global stat optimum not claimed.
- Next efficient native structural coverage: **Human Arcane Mage cloth, one-handed mainhand plus nonweapon offhand**, reuse the same generalized static core and preferably source-backed original APL. Do not add new per-spec optimizer and do not repeat full 320-iteration Rogue/Hunter runs.

No Work OS/MAIN/shared Project Sources/current-state governance/promotion action taken; user-approved notes v1.2 preserved, user DPS-only immediate testing constraint observed, official legacy all-role scope conflict still recorded. GitHub protected main, immutable v003 and historical original v015/v016 are untouched.
