# v206–v207: non-CHMV ring enchant selected in the current-season user product

**Owner and scope:** Isolated branch `probe/chat-cache-v035-20261024`, 2026-10-31.
No main merge, no original v016 byte integration, no Project UI/Work OS change,
no second optimizer and no 26-specialization Native rerun.

## Accounting decision

An enchant being selected is **not** evidence that its effect adds a secondary
rating. Only an exact confirmed **permanent static CHMV** increase contributes
`E` to the **auto-derived** target reference `B` once; manual inclusive `T`
remains user-authoritative. Other enchant effects are passed to SimC through
the precise item `enchant_id` and **do not change B/T by themselves**.

- Source `v191` already knows 38 highest-rank season enchant IDs, token,
  class/slot mask, and quality, not full effect magnitudes or item/recipe IDs.
- Source `v197` classifies ring `enchant_ring__eyes_of_the_eagle`
  `enchant_id=7967` as **critical-strike effectiveness**, *not crit rating*.
  The remaining 8 ring enchant families are rating-type candidates without
  new independently measured static values, and other categories are unresolved.
- New actual official Windows SimC [v206 #41107497147](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41107497147):
  the **same source-generated current-season Ret Paladin 334 baseline**
  compared finger1 without enchant vs with `7967` using the existing v198
  physical-character precombat stats parser. **Exactly 2 new Native PASS**,
  measured E={crit:0, haste:0, mastery:0, vers:0}, other gear identical,
  existing binary SHA `0ad16368cd1effb19c793dbce63518ccb72fec89c72f6ef75d9afca239a039e8`.
  Exact compact input and two Native JSON2 hashes are pinned at
  [data/v206_eagle_7967_windows_E0_proof.json](../data/v206_eagle_7967_windows_E0_proof.json).
  Original artifact #13002860372, GitHub artifact ZIP SHA
  `ff244c358d6fdb100e77e9081d2c750f869224ca1af1f897c0fc83a6a7920ec3`.
  **This is one static rating comparison, not 26-DPS or complete effect-mechanism validation.**

## Implemented v206 input boundary

- `runner/v206_nonchmv_eagle_selection.py` validates pinned v191 source
  ID/token/slot/source category, exact existing v206 Windows E=0 witness,
  selected slot and absence of competing enchant or selected special/crafted.
- Optional end-user `enchant_choices={"finger1":7967}` enters `v106`,
  becomes explicit `selected_season_enchants` in `v098`, writes
  `enchant_id=7967` to the internally generated representative finger1,
  and is checked again in `v096` after the external oil SHA update.
  The **existing v091/v093/v094** B/T/SimC/95%/cancel-resume/cache engine
  is unchanged. `v096` reports the nonCHMV choice without adding a numeric E.
  Omitted optional field retains the *exact old* user identity and default
  gear profile; selected choice changes source/profile/session/case identity.
- Local `v113` HTTP rejects other enchant IDs before Native. Web UI offers
  exactly one ring option `7967`, only when the independent source/native E0
  evidence exists; other **37** remain locked. A corrupted/absent proof
  disables this choice without removing the 38 source rows or currently
  supported food/potion choices.
- Auto unenchanted `B=3150,T=3182`; selected Eagle also
  `B=3150,T=3182`; selected custom inclusive T remains unchanged.
  Comparison uses a single oil O=32, counted once.
- [Focused Linux/Windows #41108975367](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41108975367):
  **130/130 PASS on each OS, zero Native**. [Initial #41108763669](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41108763669)
  Linux 130/130 success, Windows 3 line-ending-only UI-test FAIL because
  Git checkout converted authored LF to CRLF. Reused precheckout LF policy
  already employed by v181; new Windows and Linux both 130/130 PASS.
  Do not erase historical FAIL.
- [Windows v181 packaging/real HTTP #41108713935](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41108713935)
  also completed SUCCESS after the v206 UI/catalog path change;
  it is **plan/HTTP only**, not Native.
- [v207 exact one-selected-Eagle real Windows 6 Native + cache replay](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41109265120)
  was **IN PROGRESS when this document was first written**. Read actual job
  logs and exact artifact before claiming PASS, DPS, SEM or cache verification.

## Strict boundaries and next best work

No 38-item effect-magnitude full extraction, no two-ring support, no full
26-spec Windows rating validation or independent proc-mechanism model. SimC
owns the selected critical-effectiveness behavior and observed DPS, not us.
The fixed rating `8025` remains a separate exact limited v204 E+30 pilot
(not generally selectable); it must not share the E0 policy.

Next, confirm v207 real Windows selected profile/cache if successful, then
resume higher-value product P1 exact fixed-L user self-service. For broader
marshalling of all 38 enchant families, extend the existing v191 source
import with SimC native effect registration details and strict unknown type
fallback; preserve unverified effects locked and do not require 38×26 Native
recalculation or duplicate source collection.

## v207 actual selected-Eagle Windows user/native/cache — independently verified SUCCESS

[Actions #41109265120](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41109265120), job `124247140107`, original source commit `c92cfa06341b237617b137191201a418e5f6742a`, **SUCCESS**. The already-verified official Win64 binary SHA `0ad16368cd1effb19c793dbce63518ccb72fec89c72f6ef75d9afca239a039e8` was used with the one source-generated **paladin/retribution ilvl334, finger1 enchant_id=7967** user case.

- Confirmed from the actual job's complete log and original receipt artifact `13003341874`: `B=3150`, fixed oil `O=32`, `T=3182`, **6 new Windows Native** calls, **6/6 SHA-validated cache-only hits**, **0 additional Native** during replay. Observed best mean DPS `185221.06034702563`, SimC SEM `270.9787148736912`, confidence `0.95`, `global_optimum_proven=false`.
- Original artifact ZIP SHA `a53257540435bcf576b465a8f44c94029d20f94c406ef9f491c7ec6b5b36a651`. Its six individual Native JSON2 case SHA witnesses and original immutable provenance are preserved in [v207 successor receipt](V207_EAGLE_SELECTED_NATIVE_VALIDATED_SUCCESSOR_20261031.json); original ZIP was also downloaded and parsed. A generic field `no_enchant_selection_promotion=true` in the original v205-reused probe had been inherited into the v207 output incorrectly: this **does not mean Eagle was unselected**. A separate metadata-only source fix and successor receipt identify the sole enabled Eagle choice and leave other 37 locked, **without re-running Native** or mutating the original receipt.
- Reused v205 no-enchant Windows sample is a separate session and has different source/profile/cache identity. **No paired 95% statistical DPS gain claim** between v205 and v207. The current product merely accepts the user's single Eagle option, renders the selected SimC effect through the existing calculation, and leaves CHMV budget constant. No effect model or second solver was added.
- Native/scope limit: a single Windows Ret Paladin 334 loadout; not all 26, not Windows GUI mouse-click E2E, not all 38 enchants. General user-selected Eagle field exists only in the isolated branch and requires updated source deployment; previous downloaded Windows ZIPs are not patched in place.

**P1 next:** cache-first internal exact static `L` acquisition when the user selects a special-effect item; do not require user-managed profile/filler/cache, do not assume missing `L=0`, and do not re-run completed v207 or v204 Native evidence.
