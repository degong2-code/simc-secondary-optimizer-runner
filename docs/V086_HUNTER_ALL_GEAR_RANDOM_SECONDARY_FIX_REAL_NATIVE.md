# v086 — Beast Mastery Hunter randomized secondary gear discovery and fixed mail replacement

**Date 2026-10-26 KST, isolated branch.** This is a **single bounded exact input/static budget audit**, not a full gear database, item-effect gate, optimal gear finder, or proof of global DPS optimum. User explicitly asked to replace randomly rolled stat items with ordinary representative pieces and examine ALL the Hunter’s other equipped items once.

## Original evidence: all 15 actual Hunter Native gear slots

Original [v079 Hunter Native run #40199924239](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40199924239), SHA-verified artifact `simc-v079-hunter-ranged-native-40199924239`, old exact source input and Native JSON2 `native/raw/case_00` inspected.

**13 nontrinket slots** (head, neck, shoulders, chest, wrists, hands, waist, legs, feet, fingers 1–2, back, ranged mainhand) plus **2 trinkets**. Exactly TWO nontrinket inputs were problematic:
- **Head `271441`**: original exact `ilevel=334`, no crafted stats token, Native gear four CHMV ratings absent, `unknown:251`. Original upstream profile for that random-secondary item had a `crafted_stats=36/49` option, omitted in generated variant.
- **Feet `271440`**: original exact `ilevel=334`, no crafted stats token, Native gear four CHMV ratings absent, `unknown:188`. Original upstream profile had `crafted_stats=36/32`, omitted in generated variant.
- **Other 11/13 nontrinket slots**: four-stat CHMV could be read, no positive `unknown` field observed. Both trinkets remain **outside G** per approved v1.2; missing trinket gear/secondary stat is neither an inferred zero nor a blocking condition. The source body (original APL, talents) was unchanged.

Prior old Native static `G=2494, J=138, F=165`, hence T2797, was a valid arithmetic sum for the **defective exact source variant**, NOT a legitimate representative 334 budget. Old real JSON2/DPS receipts are retained with their historical identity.

## Replacement fixed-secondary MAIL armor (representative only)

Selected two **real fixed-secondary raid mail items**, confirmed as mail head/feet with non-random crit+haste / crit+vers by [Wowhead Frenzy's Rebuke](https://www.wowhead.com/item=249317) and [Wowhead Sabatons of Obscurement](https://www.wowhead.com/item=249320). Current-season item recommendation is not the purpose: these are only **source-identified, scaled ilvl334 generic model placeholders**, not guaranteed ordinarily obtainable at that item level, a full loot catalogue, or automatic equipment optimization.

- **Head replacement ID 249317**, exact `ilevel=334,gem_id=240983` and no random secondary `crafted_stats`: actual Native crit **139**, haste **62**, CHMV total **201**.
- **Feet replacement ID 249320**, exact `ilevel=334` with no random secondary option: actual Native crit **48**, vers **102**, CHMV total **150**.
- Every other 13 exact equipped item lines (including both trinkets and original four-tier pieces) was retained **byte-for-byte** from the original Hunter first-use profile; only `json2` destination plus head/feet lines changed. No APL/talent/effect behavior was modeled independently.

## One NEW real pinned Native simulation in working runtime

The exact original v079 source profile was recovered from its stored ZIP, the two gear lines were replaced, and **ONE NEW real SimC Native** with **35 iterations** was executed using the exact preserved SimC ELF SHA256 `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`, revision `7bc10711b5`. SimC returned exit status 0 and a real JSON2 `report_version=2.0.0`. The execution emitted advisory `Implementation Not Yet Verified` notices for other unrelated SimC effects; they were reported as emitted, not converted into new proc verification gates or silently called an error.

- Exact input SHA256 is recorded in the proof ZIP's `source_provenance.json` and bound to the saved input bytes; no digest is reconstructed from memory.
- **Native JSON2 SHA256 `e55bfa2fa9b255bf2f3b74bb85b255eebf774ba939b43348ab314c7b782f27c2`**.
- **All 13 nontrinket equipped gear slots** inspected again: no positive `unknown`, every static CHMV sum observed.
- Old nontrinket `G=2494`. New Native `G=2845`, increase **201+150=351**. Keep J138 and the same scenario-declared F165, so **T=2845+138+165=3148** (previous T2797). This is a real Native-derived G/T for the corrected exact input, not the unverified hypothetical T from a previous answer.
- Representative one-shot Native DPS **199155.65319113643**, SEM **516.549987336559**, 34 samples. **This is NOT a confirmed DPS-optimal static CHMV target**; the source retains initial raw `gear_* 700/700/700/700`, and updated target-T candidates have not been run.
- New Native proof bundle `V086_HUNTER_FIXED_MAIL_NATIVE_PROOF.zip`, **SHA256 `2d80cbb0faf34ffe20677540943f77375bb8c75a6ab44a181288b5e062d9b8bd`**. Contains original-free corrected input.simc, real JSON2, stdout/stderr, full 15-slot CSV+JSON audit and input provenance; **does NOT include the large executable**. Audit JSON SHA256 `ddc50dfa1a3c428f1c67da40be0f9c2c2e995d40d741ca1f5944b5e0fb32e38a`.

## Durable product correction with no extraneous SimC calls

`runner/v086_hunter_fixed_mail_representative.py` now constructs corrected exact source and filler variants by adapting existing `v079.source_profile`. It changes only two head/feet lines, preserves baseline SimC APL, talents, tier 4, trinkets 2 and all unchanged selected gear identity, and rebuilds profile hash. The existing old v079 source/Native proof was **NOT overwritten**; the new representative fixture is distinctly versioned.

`runner/v046_static_item_cache.py` corrected a genuine static data bug: for an equipped **nontrinket** returning positive `unknown` in real Native gear, the item variant is now **fail closed** rather than silently accepting absent CHMV as a normal 0-stat filler. **Trinket gear/unknown remains nonblocking** by original contract. This is no new SimC game-effect, activation, proc, or class-specific validation Gate; it is exact item option and static budget data quality only. Existing static cache entry revisions are not expired or overwritten. The old malformed variant/Native historical evidence is retained.

[GitHub Actions v086 #40243741960](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40243741960) **SUCCESS**, 491 regression tests total, **489 PASS/2 SKIP**; input identity and safe unclassified handling regression PASS. **Actions used ZERO additional Native calls** (the single new SimC Native was already executed in working runtime and preserved separately). This is separate from prior v079-v081 official target DPS runs, whose defective 2797 representative budget is NOT rehabilitated.

## Next exact step (only if necessary)

Current user request of one all-slot check plus ordinary mail replacement is fulfilled. Any future new optimization candidate run should use this corrected variant **T3148** and newly scoped cache identity. Other affected Shaman `271441` representative head still requires a separate input correction before its official GJF benchmark can be considered normal. Do not rerun old Rogue/Arcane profile or expand to effect certification, loot recommendations, recipe DB, old Work OS gate, or protected artifacts.

Protected GitHub main, original v015/v016 source, Project Sources/Work OS, immutable v003 and governance unchanged.
