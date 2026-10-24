# v042 — Catalyst provenance, dynamic-stat and CHMV budget evidence firewall

**Scope:** bounded technical verification only. Not a formal roadmap, product release, user gear selection, policy change, or Work OS M0 gate.

## Authority and state corrections (2026-10-25)

- The approved product policy is Developer Notes **v1.0**; v1.1/v1.2 are unpromoted candidates. Approved v1.0 describes T=G+J+F, whereas the candidate adds oil via T=G+J+F+O. Do not choose or replace either by inference. Resolve actual in/out-of-injection effects and gear-item budgets before requesting any new user policy choice.
- 3182 versus 3184 and manual 3284 are **separate provenance questions**, not implicit common totals. Native v037 tested 3284 as a manual total, not as proven ilvl334 equipment budget.
- v016 through v031: **previously reported complete / currently not independently verified from original ZIP and receipts** in this chat.
- v016 product baseline → GitHub v032–v041 ancestry, feature preservation and final integration path: **NOT ATTESTED**. Higher version number means neither product promotion nor formal OS state change.
- Evidence always records **(a) trial/native PASS, (b) product integration, (c) formal policy promotion separately**.

## Verified prerequisite

- Isolated development/cache branch: probe/chat-cache-v035-20261024, not main.
- The v041 receipt and GitHub Run 40112424280 attested one pinned Linux native trial of tier head 271564, original static stats 271874, ilvl334, diagnostic bonus 13846, preserved gem 240967, static mastery 201, 4-set, crit rune and venomcursed_mastery runtime proc.
- Pinned SimC source: 7bc10711b5a4514066fa402ca0a71c9ba4b7c9dd, binary SHA256: 64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e.
- In the pinned upstream engine/player/unique_gear_midnight.cpp, venomcursed() constructs a stat_buff_t using effect.driver()->effectN(1).average(effect) and effectN(2).average(effect). These are runtime effect quantities; *existence of a buff or code implementation does not independently establish the actual positive/negative rating values or game scaling*.
- Public item information for original 271874 with bonus 13846 does **not** establish the live-game bonus list of the **catalyzed 334 tier item**.

## Added files and gates

- runner/v042_catalyst_evidence_firewall.py: runs the byte-preserved v041 native profile **once maximum**, re-audits real JSON2, keeps the tier ID / original stat ID / diagnostic bonus / gem separate. The **static item CHMV** is verified only from the gear head fields, and the buff is tagged **dynamic (not a static addition to G/T)**. No inferred +363/-60 values or invented new G/T totals.
- tests/test_v042_catalyst_evidence_firewall.py: offline negative and positive boundary checks. Claims of user selection, product integration, formal promotion, 334 game bonus attestation, and budget total are refused.
- .github/workflows/v042_catalyst_evidence.yml: push trigger ONLY for integration_probes/requests/v042_once.json on the existing cache branch; exactly one authorized request-file diff, exact JSON contract, pinned source identity, cached pinned binary (MISS/altered → BLOCKED, no rebuild), one SimC call maximum, report both success and failure.
- Every receipt reports native trial success, product code integration and official policy promotion separately. A bounded trial PASS must still report product_admission=BLOCKED_MISSING_INDEPENDENT_EVIDENCE.

## Exit conditions of this v042 trial

1. Offline negative guards pass, unchanged earlier tests pass.
2. Requested native calls <=1, SHA-pinned Linux binary cache HIT, no C++ rebuild.
3. Native JSON2 shows expected head/gem/tier/rune/proc identity and static 201 only once.
4. Runtime buff amounts remain **unverified** (not backfilled from static item stats), no game-334 bonus or real G/T attestation, no DPS comparison or global optimum claim.
5. Artifact includes input source, raw JSON2, v041 and v042 trial receipts with checksums. Verify exact run ID, artifacts, ZIP, JSON2 in an independent audit where accessible.

## Pending after v042 (not silently approved)

Actual *catalyzed* level334 bonus ID provenance; positive and negative proc rating changes and scaling; real head/slot based recalculation of G/T; 3182/3184, oil and other fixed/outside budget attribution; gemstone socket mechanic; v016→v032 original-code lineage; full live product scenario integration.

**Policy gate:** no modifications to main, v003 immutable, Work OS, Project Instructions/Sources/CURRENT/Shared State; no WEQUIP runtime dependency.
