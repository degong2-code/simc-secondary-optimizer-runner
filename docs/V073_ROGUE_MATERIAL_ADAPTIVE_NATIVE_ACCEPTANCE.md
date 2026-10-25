# v073 — Rogue material-distance adaptive Native scouting

**2026-10-25 KST**. Isolated development branch probe/chat-cache-v035-20261024.

## CI and evidence
- First Actions [#40186665980](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40186665980): **FAIL** at newly added Python test-file syntax; all Native steps skipped, **zero new SimC**. Failure retained.
- Corrected Actions [#40186754387](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40186754387): **SUCCESS**, commit fe5be8caaf7764357e66d2debb391961927c5613. **397 PASS / 2 SKIP (399 tests)**. Two new actual Native scouts and verified two-case cache replay (zero additional Native).
- Artifact simc-v073-material-native-40186754387, ID **12596393313**; GitHub-reported artifact digest **sha256:993e0dd820884503527348fbf2ddecf99ae564c50add9c3188526665bd77a0ab**. This metadata was observed from GitHub; the ZIP was not independently downloaded/CRC-audited in this chat.

## Real input provenance and scope

Six previous real Native results authenticated and reused with zero re-runs: two individual v069 numeric witnesses (v069 workflow overall FAIL preserved), one v070 official GJF candidate, one v071 first v015-derived adaptive scout, and two v072 320-iteration actual independent confirmations. Historical v072 original input SHA256, JSON2 SHA256, native receipt SHA256, scenario/input/gear/rating identity and actual DPS/SEM revalidated after artifact relocation. Calibration witnesses are not miscounted as official-T exploration candidates.

User's Void Elf Rogue Subtlety / target ilvl334 talents, tier, special gear IDs, separate two trinkets/embellishments, Omnium fourth column mastery, special gem B, Patchwerk 1 target 300s, raid buffs ON and original APL are preserved. Official **T=G2847+J138+F165=3150**, fixed special **L=(100,201,0,0)** and user-profile numerical offset **(+165,0,0,0)**. Weapon oil stays outside T, unknown trinket static gear is not zero. No independent item effects/APL/proc checks.

## v073 implementation and efficiency

- New runner: runner/v073_rogue_material_adaptive_scout.py; reuses existing v065 original-v015 policy next_scout, v064 numeric request/output and v065 execute_one cache/Native executor. **No third optimizer or effect engine**.
- v015 neighbor transfer step is **350 rating = 11.11% of T3150**; at most **two** sequential newly selected candidates, 60 requested iterations per candidate. Both materially differ from the v072 A high-iteration anchor. One new policy decision made after first scout; old 35-iteration witnesses never passed off as equivalent to v072 high-precision anchors.
- New test module: tests/test_v073_rogue_material_adaptive_scout.py, five offline regressions. New GitHub workflow is v073_rogue_material_adaptive_native.yml, guarded by explicit one-shot user-scoped request.
- Two Native executions; final JSON2 four rating integers **match both targets**, SHA-validated exact cache replay **2/2 HIT, 0 calls**. Same-season static cache unmodified. Durable per-run identity/attempt limit and cancellation/partial-output refusal persist.
- No 320-iteration confirmations executed in v073.

## Observed DPS (actual Native)

| Result | A (v072 independent high precision) | C (v073 fresh scout) | D (v073 fresh scout) |
|---|---:|---:|---:|
| Crit | 813 | 463 | 1163 |
| Haste | 913 | 913 | 913 |
| Mastery | 712 | 712 | 712 |
| Versatility | 712 | 1062 | 362 |
| Total T | 3150 | 3150 | 3150 |
| DPS | 223489.6739647237 | 222293.33954267605 | 225788.43840312897 |
| SEM | 367.8797924393748 | 782.0226142887427 | 843.9470953638553 |
| Samples | 319 | 59 | 59 |
| Native seed | 7721403478798083602 | 7299737894407333987 | 11523049160159966242 |
| JSON2 SHA256 | 92bf0aee6ac60916cfb16c3d014405ca4fa742c7b59ad2a4f90eb40499492f89 | 373b3583db9f64845258ee020095bb50d4057562c709c4f3fb9c8384fa517b36 | f51cddf61d64d784b8b066b7b69223c7892bc62a6a8d2dc175729f5c59f145c9 |

C−A DPS **−1196.3344**; independent-normal approximate descriptive 95% interval **[−2890.1957, +497.5269]**. D−A DPS **+2298.7644**, interval **[+494.3387, +4103.1902]**. C measured loss 0.535% versus A; D measured gain 1.029%. Both move 350 rating relative to A and are within 1% loss threshold by observed mean only.

**Critical interpretation**: D is an exploratory 60-iteration candidate selected after examining two scouts, compared with A's 320-iteration independent prior measurement. Descriptive unadjusted CI excludes zero for D−A, but **this is not a pre-registered independent confirmation or multiple-comparison adjusted optimized-winner demonstration**. No certified new winner, convergence, global optimal distribution, or proven high-precision near-best materially different alternative. C may be a prospective different near-best distribution but is also only an exploratory signal.

## Precise next development
v074: independent scenario-matched **320-iteration D confirmation** as the highest-priority candidate; compare to already confirmed v072 A with uncertainty and adaptive selection explicitly addressed, preserve high-iteration result SHA/cache. Do not run many further noisy scouts or needlessly re-run A. If materially different near-performing alternatives are still needed, conditionally refine C and/or another region, under bounded Native budget using the same v065 engine. The full adaptive convergence, all-spec support, generic UI, and five gem/enchant stat-source-attribution ambiguity remain pending.

The official Project Source v1.2, GitHub main, Work OS CURRENT/Shared State, v003 immutable, original v015/v016 and all historical result bytes are untouched.
