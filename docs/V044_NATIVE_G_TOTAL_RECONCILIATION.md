# v044 — CHMV G/T discrepancy: independent native evidence reconciliation

**2026-10-25. Test-only / working evidence. No change to approved Developer Notes v1.0, no product integration, no Work OS M0.**

## Direct finding

The six standard gems and flask were NEVER missing from the authoritative product contract:
- Approved `J=23×6=138`, `F=165`, `T=G+J+F` (Developer Notes v1.0 §5–7).
- For gear rating, take the **pinned SimC Native JSON2 gear records on the exact item/level/profile** as observed evidence over the historical unverified G=2847 report.
- Dynamically triggered special-item buffs belong to SimC's DPS computation, not the static CHMV allocation total.
- Existing v044 regression workflow Run [40123743273](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40123743273): success; **160 passed, 2 skipped**; **zero new Native calls**. This suite used unit/mock fixtures; the *real evidence crosscheck* below was performed separately on original v036 and v042 ZIP files.

## Independent exact native comparison

Both prior GitHub Artifacts have been downloaded. The original ZIP bytes and all entry CRCs were checked, and native JSON2 and input SHA256 verified.

| Source | Native G excluding trinkets | Head native secondary | Non-head static slot change |
|---|---:|---|---|
| historical v020 report | 2847 (not currently independently reproduced) | not used to override Native | not established |
| **v036** source Run 40101013866 | **2849** | 137 haste + 63 mastery = 200 | — |
| **v042** source Run 40120755711 | **2850** | 201 mastery = 201 | **none** |

v036 ZIP SHA256 `2657caaff2157bdbc6521e9b000034f4ce78171754687002d6193cfafb3b62b9`; selected CONFIRM_01 JSON2 SHA256 `6b8ea2fef531ad666e68b73049cf5203d85d60880ec941a5a36a4b1c138c028d`.

v042 ZIP SHA256 `eea36762a1d21db5e9ad5bcf72c6c94bff4d122fee28f3ea83cd700120b9dc7f`; selected JSON2 SHA256 `4367cfa9e911190af8e8441f44378cb0efab4d018fd059677e01fa054636ed55`.

The original reported 2847 is **2 below the original v036 Native G=2849**, and the v042 replacement adds **1** to G. **Do not attribute this discrepancy to random SimC error.**

Both inputs use `flask=flask_of_the_blood_knights_2`; the summed `gear_*_rating` overrides equal **3019**, and both final Native `buffed_stats.stats` sum to **3184**. Haste alone changes `975 → 1140`, i.e. **+165**, matching the already-approved flask allowance. A standalone causal-with/without-flask experiment was not performed, nor is it necessary merely to respect the known contractual F=165.

## Why historical totals 3182/3184 were confusing

The arithmetic below accounts for both observed totals without changing the v1.0 approved formula:

| Expression | Result | Meaning |
|---|---:|---|
| 2847 + 138 + 165 + 32 | **3182** | historically reported G combined with a 32 allowance |
| 2849 + 138 + 165 + 32 | **3184** | v036 native G plus the same 32 allowance |
| 2849 + 138 + 165 | **3152** | v036 Native G under the **approved v1.0 T formula** |
| 2850 + 138 + 165 | **3153** | v042 Native G under the **approved v1.0 T formula** |

The `+32` corresponds arithmetically to the existing test-scenario weapon oil allowance; the trial profiles equip `main_hand:thalassian_phoenix_oil_2`. **The equation alone is not independent proof of oil injection causality, nor approval of the oil-inclusive candidate formula.**

A v042 Native trial continued to use the earlier 3184 gear/final overrides **without recalibrating G after replacing the head**. Thus the continued 3184 final output is **not evidence that the changed gear has the same static G**.

## Acceptance boundaries and next action

- **Test success:** PASS, exact static slot/profile comparison and observed +165 input-output difference, zero additional Native executions.
- **Product code integration:** NO. v016 baseline→GitHub v032+ lineage remains unverified.
- **Official policy promotion:** NO. Official v1.0 T=G+J+F remains authoritative and J=138/F=165 are settled; do not ask user to reconfirm.
- **Remaining technical question:** whether oil +32 is already included in the injected gear_* rating space and how to prevent duplicate or omitted secondary stats when integrating a **new** target profile. Address with minimal SimC attribution only if needed for correct input→final mapping; do not revisit proc mechanic research.
- **Protect:** main, Work OS, Project Instructions/Sources, CURRENT/Shared State, v003 immutable.

The user's key correction is that **Native equipment data wins when it disagrees with an older equipment total**, while prior written contract J=138/F=165 retains authority.
