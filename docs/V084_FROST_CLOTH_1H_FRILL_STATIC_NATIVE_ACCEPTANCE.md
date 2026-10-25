# v084 — Human Frost Mage Cloth / 1H plus Nonweapon Offhand, Real Native Static CHMV

**2026-10-26 KST — isolated product-development branch only.** User explicitly selected **Frost rather than Arcane** after previous Arcane trials. This is a bounded structural acceptance check, **not** all-specialization coverage or a converged DPS/stat optimization, and not integration of the original v015/v016 product.

## Authentic source, equipment and design boundaries

- Original **Frost Mage** from SimulationCraft midnight, upstream commit `12aa5dc041b03bf9f9fdd1db00dbc8d3ec0cebb7`, file `profiles/MID2/MID2_Mage_Frost.simc`, exact Git blob **`b787824a95020a7cdd0934ed5e004695726db138`**.
- Original race Tauren was explicitly changed to **Human**; source class Mage, specialization **Frost**, role spell and **71 original SimC APL action lines and original talents** preserved. Native SimC accepted and executed this Human exact profile; no independent game class/race rules model was built.
- Armor **cloth**, **one-handed mainhand item ID 271092** and **nonweapon offhand item ID 245769**, both extracted from the pinned original Frost source; exact 16-slot representative gear normalized to **ilvl334**, with explicit deterministic option tokens in place of original variable bonus choices. Crafted representative waist + offhand, two source-backed trinkets, no new item or gear selection DB.
- Exactly **four Mage tier pieces: shoulders/chest/hands/legs**. The original fifth tier head ID 271564 was replaced with **non-tier cloth head ID 271874** present in upstream original MID2 Fire Mage `profiles/MID2/MID2_Mage_Fire.simc`, exact Git blob `9fae08d2f1c49f3a964f9415540929723384e6fe`. These two Git-source files and SHAs are pinned as fixtures; no claim that this choice is a best-in-slot recommendation. SimC itself owns usability and item effects.
- The original Frost flask `flask_of_the_shattered_sun_2` was retained and its **static F contribution was caller-declared as crit +165** for this test, not certified as the universal effect of every flask or combat setting. `J=138`, oil O not selected; official `T=G+J+F`, oil if selected remains fixed outside T. Frost class buffs/talents/APL, gear/trinket effects and DPS are all SimC's responsibility, never reimplemented.

## Minimal runtime change: generalize declared F without new optimizer

Existing `runner/v082_fury_plate_dual_twohand_native.py` gained a **single optional per-scenario declared_F argument** and the sum-of-F check. The previous default `DECLARED_F=(0,165,0,0)` remains unchanged for v082 Fury and v083 Paladin, including their existing cache identities. New `runner/v084_frost_cloth_1h_frill_native.py` is ONLY a source-locked profile producer, passing `declared_F=(165,0,0,0)` and the existing 16-slot expected count into the same runner. Native static G, budget, candidate construction, v066 static-c profile-neutral preflight, existing v015-derived v065 guided proposal and Native execution/SHA cache are reused. No new Frost-specific optimization algorithm or stat/talent effect certification.

Six new offline regression cases: original actions and exact one-hand/frill source IDs, Human/cloth/four tier, F crit vs legacy F haste and O policy, exact static-cache-miss fail close, upstream file byte drift detection, input-plan-only not labeled Native PASS.

## GitHub Actions and genuine Native results

[Actions run **40240772747**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40240772747) **SUCCESS**, isolated trigger commit `10fcb98f6b3468dcd215a61cfbb03fe20395ac4a`. Full offline suite **480 total / 478 PASS / 2 SKIP**. SHA-pinned actual SimC binary `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`, revision `7bc10711b5`. Four **actual new** Native 35-iteration executions were successful, with 34 usable DPS samples per run: one exact nontrinket static G discovery followed by two official static-c witnesses, v066 preflight and one old v015-derived adaptive scout.

- Exact Native static nontrinket **G=2845**, declared **J=138**, **F=165** (crit vector), official **T=3148**.
- Initial source-profile Native `DPS=175969.34481786485`, SEM `712.6881258161683`, SHA256 `7c595ecf00edbaebaec46d7175c01543f900faa08f2452f89816de234d8c0c69`. Used to obtain true static G; **not** a target-T DPS candidate.
- Both real official-T input+JSON2 receipts passed **`v066.prepare_static`** returning **`READY_STATIC_CHMV_PROFILE_SCOPED`**. Existing v015-derived static scout selected a distinct third candidate, evaluated by unmodified common Native executor, not by a Frost optimization module. For all three candidates `target_static_c == verified_static_c`; Native `buffed_stats` is recorded separately and is **NOT** required to equal the static target.

| Role | Static crit | Haste | Mastery | Versatility | DPS mean | SEM | Actual Native JSON2 SHA256 |
|---|---:|---:|---:|---:|---:|---:|---|
| Official A | 787 | 787 | 787 | 787 | 180702.95306485504 | 901.213933126358 | `8c3ea1b0a45e44f9feb574b5ba6a767b8a0a727d4f06988cfd9e2c06f7c7ac2a` |
| Official B | 687 | 887 | 787 | 787 | 176959.64300947924 | 689.9525400407362 | `8fcc841dcb57f1bba175d9986efb56aa188796f490ceb0ed81e4d0ec6c029da7` |
| Existing v015 adaptive C | 887 | 687 | 787 | 787 | 182156.59329094095 | 882.2340346651362 | `252728f6bf67f4249cac8c738f871bfe1bf2df8a716f0644226030a8d244420e` |

For adaptive C, requested static `c=(887,687,787,787)` sums to T=3148. Actual observed SimC JSON2 `buffed_stats=(905,736,803,803)`; the difference is preserved as an **observed value**, never reverse-engineered into forced static c. In this profile the differences include more than a single static flask contribution; the app leaves them to SimC. This is important evidence that simple `buffed_stats == c` would be an incorrect verification gate.

All four exact Native input+JSON2 were SHA verified by cache-only execution; **4 HIT, 0 new SimC calls**. 4/4 bounded new Native calls and preserved stdout/stderr. Artifact `simc-v084-frost-cloth-1h-frill-native-40240772747`, ID **12616002901**, GitHub-reported digest `sha256:a7551fa8a96ceff036fda267f1791d02a43d9b32d55c0995eb9059c603717f7a`, size **249006 bytes**. Artifact provider metadata verified; zip CRC not independently checked here.

## Status, limitations, and efficient next

**PASS in isolated trial:** Human Frost cloth / one-hand + actual nonweapon frill, original APL and two selected trinkets, four-tier representative source, real Native budget G and official T, explicit static F crit vector and separate talent-influenced buffed rating, v066 static-c / original v015-derived common scout, real DPS/SEM, SHA cache replay, full regression.

**Not verified:** A universal F/E/O vector resolver across consumables; selected oil fixed contribution (O remains OUTSIDE approved T); 0/1/2 embellishment variants and selected specialized gear; all level/manual-T combinations; the original v015/v016 product source integration; global optimum, confidence-based preferred alternative or all DPS specs. The earlier Rogue dual one-hand and Shaman one-hand+shield Native histories were on older numeric/buffed contract and should be audited or selectively replayed under static-c before counting them as equal evidence. A fully automatic profile producer remains future work.

**Next recommended:** After structurally covering mail/ranged, plate dual 2H, plate single 2H, and cloth 1H+nonweapon offhand with corrected static-c, focus on **legacy one-hand+shield and Rogue dual one-hand static-c migration** plus generalized F/E/O numerical attribution and original product lineage verification rather than repeated exploration of Frost or Arcane. No new separate item-effect/proc gates, full season DB, or loot optimizer.

Isolated branch `probe/chat-cache-v035-20261024` only. Protected `main`, immutable v003, original v015/v016, Project Sources, Work OS and MAIN shared state untouched. User-directed DPS-only immediate scope is distinguished from original approved Developer Notes v1.2 all-role statement without silently altering the latter.
