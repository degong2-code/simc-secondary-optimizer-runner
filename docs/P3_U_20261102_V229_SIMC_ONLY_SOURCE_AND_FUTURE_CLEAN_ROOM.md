# P3-U — 역사적 SimC 원본 전용 수집 시험과 최종 통제실험 해석 교정

> **최신 사용자 직접 교정, 2026-11-02:** 이 문서가 처음 가정한 "최종 통제실험 = SimC-only 외부 수집 차단"은 **잘못된 해석**이었으며 폐기한다. [P3-AA 단일 Environment Build 엔진·기존 자료 없는 신규 수집 통제실험](P3_AA_20261102_SINGLE_ENGINE_FRESH_SEASON_CONTROL_ACCEPTANCE.md)이 우선이다. SimC-only는 v229 하위 수집기의 **역사적 기술 시험 범위**로만 유지한다. 제품 엔진 및 최종 통제실험은 **정상 Wago DB2/Blizzard/WCL/공개 GitHub/SimC 신규 수집을 모두 허용**하고, 이전 확보 자료·시즌 값·캐시·Native 영수증의 재사용만 차단한다.\n\n**Date** 2026-11-02 KST. Isolated development on `probe/chat-cache-v035-20261024`. Not a main merge, immutable source change, Project Sources/Instructions UI update, official Work OS promotion or finished product endorsement.

## Purpose and authority

Continue building a reusable **season environment engine**, not one-off expansion scripts. The latest approved policy requires rebuilding **G/J/F/O** on each new season, proving quality/effect/ownership and recomputing B/T before the existing adaptive SimC optimizer runs. The user's 2026-11-02 decision additionally specifies a **post-engine-completion zero-base, controlled acceptance experiment** in which none of our previous data, historical Native receipts, static caches or G/J/F/O references can be read. The controlled acceptance runs the **unchanged normal Environment Build engine** with every standard *new external source retrieval enabled*; previously retained Wago/Blizzard/SimC raw archives, installed season catalogs, prior Native evidence and caches must not be read as inputs.

The zero-base full-product experiment is **planned, not executed** this turn. It must NOT be mistaken for offline synthetic tests or a normal sparse checkout.

## New source acquisition work: v229

`runner/v229_simc_only_source_seed.py` (first-party SimC source-only collector) and the opt-in `.github/workflows/v229_simc_only_source_seed.yml` provide a narrow, measurable first step towards cold-start sourcing:

1. Caller explicitly supplies exact 40-hex `simulationcraft/simc` commit, its generated game build, previous game build and season event; no default historical commit, branch head, or numeric J/F/O.
2. Fetch only the three necessary first-party files at that commit:
   - `engine/dbc/generated/item_set_bonus.inc` — all source-backed set bonus family/class relationships and attached candidate item IDs, including historical set rows;
   - `.../gem_data.inc` — candidate gem-property→enchant IDs, **not** gem item IDs or proven gem rating;
   - `.../temporary_enchant.inc` — candidate SimC temporary enchant tokens, **not** approved weapon oils or their static O.
   - Optional `.../item_data.inc` (large, explicitly opted in), used as an immutable raw source for future representative gear parsing. Its presence by itself proves no numeric G or season selection.
3. Walk only the immutable Git commit's `engine/dbc/generated` tree (without recursively downloading the repository); compare each raw downloaded file's exact Git blob SHA-1 with the upstream tree blob, and record its SHA-256. All sources must expose the same caller-specified game build. Per-file limits and atomic new destination prevent uncontrolled I/O or source overwrite.
4. Reuse the existing pure `v191.parse_generated` parser for gem properties and temporary enchants; group all set bonus rows by option, class and set ID without guessing that the lexicographically newest label is the current season.
5. Emit deterministic `simc_seed_receipt.json` with upstream commit, build, byte hashes, candidate counts and **all G/J/F/O/B/T=null**, `environment_ready=false`. Source ID evidence is not physical G/quality J/F/weapon applicability O. No Native, item-effect reimplementation, cache writes or user UI admission.

At the time of this v229 implementation, the GitHub workflow was **manual dispatch only**, has read-only contents permission, copies only three engine/test files into a temporary source-only workspace, and keeps a short-lived artifact of the newly fetched SimC sources. It never silently fetches previous Wago/Blizzard data. The temporary workspace has no copied `data/`, `integration_probes/` or `.git`; this is a useful **preliminary isolation check, not a security proof of full inaccessible prior data** (the runner's checkout and underlying host are not a securely isolated VM).

### Why this is not already a full G or complete environment builder

The SimC `item_set_bonus.inc` file contains many historical season sets and set-level IDs, not a verified active 13-class five-piece slot map. The gem property rows do not supply the complete gem item→property/quality equivalence join, nor their fixed J budget. Temporary enchant tokens do not show that an item is an applicable oil or prove O. A generated item database may be used for candidate discovery, but representative weapon family, armor, tier actual slot, static ilvl G and exact user profile execution still require additional source interpretation and native proof. Existing `v169/v226/v227/v228` need actual v167/v168 source artifacts and are not yet fed by v229; a passing v229 receipt is source discovery only.

**Efficiency**: never acquire `item_data.inc` (about 26 MB in the inspected pinned previous build) automatically merely for a source metadata check; explicitly request it only when the G source adapter needs it. Keep prior same-season caches valid as authorized in the normal product, but forbid all prior cache access **in the final controlled experiment**.

## Actual implementation proof vs pending

`tests/test_v229_simc_only_source_seed.py` provides synthetic first-party DBC input, immutable Git tree/blob mocked transport and failure tests (old build relabeling, mixed source build, modified blob, unexpected file, set IDs/count conflict, highest-quality non-certification, zero G/J/F/O publication, short-lived output). This test does NOT substitute for a future actual new-season source collection or zero-base experiment.

- [GitHub Actions #41389202581](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41389202581): Ubuntu/Windows **212 tests PASS each**, no Native; the new manual `v229` acquisition workflow itself was **not dispatched** and has no actual new-season HTTP retrieval receipt in this phase.
- Existing P3-T [#41387649921](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41387649921): 200/200 per platform, source/profile/Native JSON2 synthetic contract only, no Native.

## Future final zero-base experiment: strict acceptance protocol

**Trigger**: after substantive engine completion and current normal product flow for all 26 DPS specs. Do not repeatedly perform heavyweight zero-base experiments during incremental development.

**Inputs allowed**: the **actual installed product engine code and exactly the normal Build entrypoint/collectors**, SimC executable/source, and **fresh network collection via Wago DB2, WCL, Blizzard API and other approved public GitHub/item providers** as used by real season refresh. The request supplies the season/build/user scenario, not past-known gear/item IDs or budget values. **Forbidden as inputs/evidence**: previous GitHub Actions artifacts/source snapshots, installed season catalog DB, legacy Wago/Blizzard data files, Project historical reference files, v089 79×2 / G≈2850 numbers, old v165 J/F/O, past native/DPS receipts and static/DPS caches. Newly fetched source data is allowed even when its provider is the same URL as an old source. If a normal provider fails or required join is missing, record the exact failure rather than silently inject historical results.

**Isolation**: construct a new filesystem/VM/container that includes the **full actual product Build engine and its ordinary declared dependencies** but has no previous installed source catalog, item seed, cached Native/DPS results or old snapshots. Verify forbidden prior files and historical references cannot be opened. **Allow and record ordinary external Wago/Blizzard/WCL/public GitHub/SimC download paths**, provide only the credentials/environment necessary for normal approved public/API collection; do not silently substitute cached downloads. Instrument read/write/network accesses, output identities and cache provenance. A sparse checkout alone is insufficient proof of isolation.

**Execution**: from an empty source state request normal Environment Build, record each source retrieval's URL/commit/build/hash, select 13-class tier/representative gear without old IDs, derive/verifiably measure G for target ilvl and weapon archetype, discover high-quality gem/flask/oil J/F/O and E/L ownership, derive B/T and manual T override, generate a native-accepted representative SimC profile, and run a bounded adaptive DPS optimization. All 26 DPS specializations and their relevant weapon categories are eventually covered, using cached repeated proof within this *new* experiment rather than redundant all-ilvl per-spec Native sweeps. Preserve cancellation/resume, cache identity, 95% SEM/statistical dominance and observed-best versus global-proof distinction.

**Independent evaluation**: seal the newly generated artifact and outcome before allowing any existing historical source or result into the evaluator. Only after sealing can a separate evaluator compare it with old proven same-build Native evidence. Verdicts: VERIFIED_COMPLETE, SOURCE_INSUFFICIENT, SIMC_VERSION_UNSUPPORTED, G_UNVERIFIED, J_F_O_UNVERIFIED, PROFILE_OR_NATIVE_FAILED, or ISOLATION_BREACH. A failure caused by genuinely missing **normal approved source** data is a valid finding. Do not mask it with previous season references or a separate SimC-only path.

**Next development**: unify the existing v160~v171 normal Wago/Blizzard/WCL collection, SimC-generated data, v191/v211/v213 catalog assembly, season-specific G/J/F/O→B/T, policy A and v216/v098 installation into **one Build execution path**. Reuse relevant v229~v237 parsers/Native observation as components, NOT as a competing environment engine. Complete normal product Build first; use the identical Build in the final zero-history acceptance.
