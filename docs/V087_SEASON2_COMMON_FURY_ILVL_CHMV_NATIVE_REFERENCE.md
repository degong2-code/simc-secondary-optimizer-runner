# v087 — Midnight Season 2 item-level CHMV baseline reference (DATASET ONLY)

Date: 2026-10-26 KST. **Isolated development reference, NOT original v015/v016 product integration or official Work OS/Project Sources promotion.**

## User decision and approved contract

The user requested a lightweight **two-track absolute static CHMV budget lookup by target item level**:
- Common DPS and other specializations: **334 → 3150 rating**
- **Fury Warrior specifically using Titan's Grip dual 2H weapons**: **334 → 3350 rating**.
- Differences of 5–10 rating between correct representative generic gear compositions need not trigger individual equipment catalog research. Users can still input a manual target sum and retain exact selected special-item fixed floors L. Do not extrapolate a universal fixed +200 at every ilvl.

The accepted Developer Notes v1.2 formal formula remains **T=G+J+F**, with selected weapon temporary oil O, trinket fixed static and other fixed external values outside T under their original treatment. This is a **rounded reference value** for such a T, **not** a replacement for the per-input exact variant computation mode or a retroactive unapproved formula promotion. For these two representative S2 profiles J=138 and F=165 are explicitly declared; other seasons/consumables are unverified. SimC owns APL, items/effects/procs, native stats and DPS, and the program should inject the static target c, not invert talent-inflated buffed_stats.

## Real bounded SimC gear-budget evidence

The reference registry `integration_probes/data/midnight_s2_ilvl_chmv_reference_v1.json` contains 79 directly evaluated integer ilvls **266..344**, each a pair of rounded T values. Two complete existing, previously SHA-verified real SimC representative input files were used:
1. **Common model**: v084 Human **Frost Mage** cloth 1H+non-weapon offhand, original input SHA256 `73ebcc4bb5802c5d02a5e50915e27ff2f28e72cc0b8050d6bd8babc648955631`, original [v084 Native](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40240772747) produced G=2845 at 334.
2. **Fury model**: v082 Dwarf **Fury Warrior** plate dual two-hand, source input SHA256 `60668f667a6f69a98b971d29aa9ff109d1b6aa8511ad33f733a8ec8bc5dd2ca1`, original [v082 Native](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40209200603) produced G=3049 at 334.

Same actual pinned binary SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`, SimC rev `7bc10711b5`. Exactly **158 additional new 1-iteration SimC Native gear-static queries** (79 levels × 2 profiles) returned success. For every profile, all 16 selected Native gear slot ilvls equal the requested ilvl, positive unclassified `unknown` is absent among the nontrinket rows, the JSON2 report version is 2.0.0, and sums are monotonic across 266..344. The single iteration is sufficient to read deterministic *static gear*, not to claim meaningful DPS or SEM.

Every ilvl: actual Native nontrinket CHMV gear total `G` plus the declared `J=138` and `F=165` gives `T_native`. Reference target `T_ref` is `round_half_up(T_native / 10) × 10`, a rounding delta **at most ±5 rating**. At 334: Common `G2845 + J138 + F165 = T3148 →3150`; Fury `G3049 + J138 + F165 = T3352 →3350`. This avoids estimating cross-ilvl growth from a single anchor and permits scale differences in Titan's Grip extra two-hand.

## Extra common cross-class Native spot checks

Two additional existing original inputs were scaled at **266/292/321/334/344**, 1-iteration Native per level:
- v083 Blood Elf **Retribution Paladin**, plate single 2H.
- corrected v086 Troll **Beast Mastery Hunter**, mail ranged (random-secondary head and feet already replaced with fixed-option mail).

All **10 additional real Native** stat queries returned correct per-slot ilvl, no positive unclassified nontrinket stat, and difference against Frost common *unrounded Native T* of **at most 5 rating**. This supports the user's 5–10 tolerance **for the sampled representative gear**; it is not every spec, talent or ilvl fully attested. An additional 334 Frost Native with gems removed confirmed the gear JSON2 `G=2845` unchanged, supporting separation of declared J and G in this tested scenario.

## Deliverables / permanence

The isolated GitHub branch now stores `integration_probes/data/midnight_s2_ilvl_chmv_reference_v1.json` (79 level lookup pairs, recorded Native provenance metadata and source identity). Full local-file proofs are separately preserved as a versioned user artifact package `SIMC_MIDNIGHT_S2_ILVL_CHMV_REFERENCE_v1.zip`, SHA256 `3724a96c7eda084abee9da94ae6d0e885d461aacfeb770b590e2a4bfd309d247`, including:
- season upgrade-rank CSV (23 current season ilvls incl special 344)
- full integer 266–344 CSV (79 rows, **both native G/T and rounded target T**)
- spreadsheet XLSX with seasonal/table/source sheets
- compact JSON lookup for direct later integration
- **158 input SHA + actual SimC JSON2 SHA evidence** in detailed provenance JSON
- 10 additional cross-class spot-check JSON2 SHA and deltas
- README and SHA256 file manifest.

Season-available upgrade ranks 266–334 and mythic-raid special 344 are grounded by contemporary Retail S2 guides such as https://stykasheets.com/midnight-season-2-gearing-chart/ and https://www.method.gg/guides/all-midnight-season-2-upgrade-tracks-and-item-levels. Other individual integer ilvls in between are **real technically simulated ilvl budgets**, not assertions of official upgrade-track levels.

**Important status:** The table was obtained and versioned, not yet wired into the original optimizer's request/UI, candidate floor or runtime. Do not claim integration, all-specialization validation, an optimized DPS curve or an effect/proc certification gate. Manual target T override remains part of the future interface contract. The prior Shaman random-secondary filler issue remains a separate representative profile option defect and cannot invalidate the exact Native source traces of this table.

No changes to GitHub main, immutable v003, original v015/v016, Work OS or Project Sources.