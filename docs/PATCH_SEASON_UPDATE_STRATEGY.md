# SIMC Secondary Optimizer — Patch / New Season Update Strategy (P1 policy)

Status: **operational design / decision procedure, NOT an installed automatic patch watcher**. Latest approved v1.4 user flow and actual GitHub CURRENT/receipts retain separate authority. Do not promote historic v145/v147 bundles or overwrite immutable receipts. No Work OS MAIN takeover.

## 0. Immutable baseline

- Season catalog, class/spec contracts, gear/weapon/4-tier IDs, gem/flask/oil budget, exact user input and SimC executable revision are explicit inputs. User chooses target ilvl (current independent representative compiler is **334 only**) or optional final total T including fixed O.
- Physical Native acceptance verifies that a generated equipment + weapon + trinket + gem/socket + SimC default APL profile executes. An actual six-candidate adaptive run evaluates DPS/SEM and a pairwise 95% judgment, **NOT** a global optimum.
- **Real Windows evidence already recorded**: previous independent balance/devastation; new v147 24/24 physical plus 24/24 existing adaptive on the exact 7bc1071 binary, user-uploaded summary+console and user-confirmed 24/24 read-only portable original hash viewing. These form a baseline, not a mandate to rerun.
- Static item/gear cache (season + exact ID/options/ilvl) stays valid across a mere SimC revision unless an actual identified static value or season data changes. Correct original values only through explicit user-approved correction. Do not silently replace observation with estimated zero.
- DPS Native cache identity stays segregated by executable SHA + revision, generated character/profile, complete equipment/options, candidate vector + fixed oil O + combat settings + iterations. A code-only UI change must not invalidate those bytes.
- Existing receipts stay immutable; new evidence is additive and labeled by its origin.

## 1. Classify change, then scope verification

| Trigger | P1 update | Native default |
|---|---|---|
| UI/report/format-only patch | offline regression, original cached result display unchanged | **0** |
| Same-season static item data **unchanged**, SimC binary/revision changes | hash binary, check new version/compatibility + affected APL / data, segregate new DPS cache | scoped first; no default 24×6 |
| Spec talent/APL/balance change | changed class/spec and its affected character/combats/gear | impacted spec one physical smoke if profile validity changed; run relevant adaptive DPS on requested cases |
| Trinket/embellishment/consumable change | exact ID/option, special L lower bounds, budget/physical effect; preserve unaffected caches | scoped to affected selected gear and user cases |
| Season equipment budget/tier/weapons/gem/ilevel change | replace season catalog with versioned exact identities, verify B/T/L/O contract, four-tier/weapon representation; do not clone old season caches | 1 physical acceptance/spec when needed for new representative coverage; run adaptive selectively after acceptance |
| Cross-cutting profile serializer/SimC schema/API change | targeted offline regression + representative spread first, escalate only if risk is genuinely all-spec | bounded coverage; full 24 once only if cross-spec risk evidence warrants it |

## 2. New-season bootstrap, not always all 168

1. Select a **new season catalog identity**. Validate source authenticity of item IDs, tier 4pc candidates, weapon forms, target-level representative gear, approximate G/B references, fixed J/F/O, optional static L. The exact target default is user approved; do not copy the previous catalog and claim new season supported.
2. Build every currently supported representative profile **offline**, verify no missing catalog components and preserve exact 15/16-slot physical layout, complete basic two trinkets and non-reimplemented SimC effects.
3. If changes affect physical gear/weapon/APL for all specs, run a **small physical acceptance** per affected spec (1/spec); if unchanged, reuse historic evidence and do not redo for ceremonial coverage. A new season often affects all, so a batch of 26 (or eventual tank/healer specs) may be sensible.
4. Run the **existing adaptive solver** only for the changed/representative scenarios required for release or requested by users. Six candidate calls/spec is *not* a mandatory season-install gate.
5. Release versioned catalog + exact SimC compatibility, separate resulting caches, show user version and scope; old season results remain selectable with correct labels, never relabeled to new season.
6. Reevaluate as users bring new specs or meaningful cross-spec failure evidence. If in doubt, label limited evidence rather than inventing a blanket approval.

## 3. Current implementation vs future

- **Implemented:** target334 24 source-independent P1 planning/user session route via explicit identity field `independent_334`; 2 historical pure product profiles; versioned immutable v147 real receipts and read-only v148 result viewing; existing v096/v094 candidate engine and session cache/cancel/resume. Full offline CI under v113 and v098. 
- **Not yet done:** automatic upstream WoW/SimC patch detection, fully standardized every target ilevel or every tank/healer spec, automatic safe cross-PC *execution* cache migration, new-season catalog ingestion/Native support, first real user-UI 24× individual changed-input Native smoke. No unsupported auto-update claims.
- Practical principle: P1 user input → representative season profile → same existing adaptive SimC → result. Keep runtime simple; compare cache identity before running expensive Native, and never add unnecessary repeated gates.
