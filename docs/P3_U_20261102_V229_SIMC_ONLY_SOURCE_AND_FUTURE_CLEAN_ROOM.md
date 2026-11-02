# P3-U — SimC-only first-party source collector and future zero-base controlled experiment

**Date** 2026-11-02 KST. Isolated development on `probe/chat-cache-v035-20261024`. Not a main merge, immutable source change, Project Sources/Instructions UI update, official Work OS promotion or finished product endorsement.

## Purpose and authority

Continue building a reusable **season environment engine**, not one-off expansion scripts. The latest approved policy requires rebuilding **G/J/F/O** on each new season, proving quality/effect/ownership and recomputing B/T before the existing adaptive SimC optimizer runs. The user's 2026-11-02 decision additionally specifies a **post-engine-completion zero-base, controlled acceptance experiment** in which none of our previous data, historical Native receipts, static caches or G/J/F/O references can be read. The permitted base is the engine plus SimC access; do not quietly grant existing Wago/Blizzard/archive data access for an apparent pass.

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

The GitHub workflow is **manual dispatch only**, has read-only contents permission, copies only three engine/test files into a temporary source-only workspace, and keeps a short-lived artifact of the newly fetched SimC sources. It never silently fetches previous Wago/Blizzard data. The temporary workspace has no copied `data/`, `integration_probes/` or `.git`; this is a useful **preliminary isolation check, not a security proof of full inaccessible prior data** (the runner's checkout and underlying host are not a securely isolated VM).

### Why this is not already a full G or complete environment builder

The SimC `item_set_bonus.inc` file contains many historical season sets and set-level IDs, not a verified active 13-class five-piece slot map. The gem property rows do not supply the complete gem item→property/quality equivalence join, nor their fixed J budget. Temporary enchant tokens do not show that an item is an applicable oil or prove O. A generated item database may be used for candidate discovery, but representative weapon family, armor, tier actual slot, static ilvl G and exact user profile execution still require additional source interpretation and native proof. Existing `v169/v226/v227/v228` need actual v167/v168 source artifacts and are not yet fed by v229; a passing v229 receipt is source discovery only.

**Efficiency**: never acquire `item_data.inc` (about 26 MB in the inspected pinned previous build) automatically merely for a source metadata check; explicitly request it only when the G source adapter needs it. Keep prior same-season caches valid as authorized in the normal product, but forbid all prior cache access **in the final controlled experiment**.

## Actual implementation proof vs pending

`tests/test_v229_simc_only_source_seed.py` provides synthetic first-party DBC input, immutable Git tree/blob mocked transport and failure tests (old build relabeling, mixed source build, modified blob, unexpected file, set IDs/count conflict, highest-quality non-certification, zero G/J/F/O publication, short-lived output). This test does NOT substitute for a future actual new-season source collection or zero-base experiment.

- [GitHub Actions #41389202581](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41389202581): Ubuntu/Windows **212 tests PASS each**, no Native; the new manual `v229` acquisition workflow itself was **not dispatched** and has no actual new-season HTTP retrieval receipt in this phase.
- Existing P3-T [#41387649921](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41387649921): 200/200 per platform, source/profile/Native JSON2 synthetic contract only, no Native.

## Future final zero-base experiment: strict acceptance protocol

**Trigger**: after substantive engine completion and current normal product flow for all 26 DPS specs. Do not repeatedly perform heavyweight zero-base experiments during incremental development.

**Inputs allowed**: engine source and its declared dependencies, a fresh pinned SimC executable and its generated DBC / Git sources, minimal experimental request (game build/season, class/spec, target ilvl 334 or manual final T, user selections). The experiment may fetch only new source data that the declared policy explicitly permits. Under the user's requested **strict SimC-only mode**, no Blizzard API, Wago, Wowhead, previous Github Actions artifacts, Project Sources, previous collected reference JSON, v089 79×2 tables, old v165 J/F/O, or historical v046/DPS cache is allowed. If SimC alone cannot supply the required tier/gear/consumable identity or quality proof, **fail with a precise missing-source explanation**; do not grant extra access invisibly.

**Isolation**: construct a separate filesystem/VM/container with only an explicit engine-file allowlist and fresh SimC, no mounted old repository tree, no previous cache/credential volumes, no host/user HOME. Deny or log external network routes other than explicitly approved SimC endpoints. Include a canary audit proving forbidden files/paths cannot be opened; instrument read/write/network accesses, check process environment and ephemeral output. A sparse checkout or copy into a temporary directory alone is insufficient proof of full isolation.

**Execution**: from an empty source state request normal Environment Build, record each source retrieval's URL/commit/build/hash, select 13-class tier/representative gear without old IDs, derive/verifiably measure G for target ilvl and weapon archetype, discover high-quality gem/flask/oil J/F/O and E/L ownership, derive B/T and manual T override, generate a native-accepted representative SimC profile, and run a bounded adaptive DPS optimization. All 26 DPS specializations and their relevant weapon categories are eventually covered, using cached repeated proof within this *new* experiment rather than redundant all-ilvl per-spec Native sweeps. Preserve cancellation/resume, cache identity, 95% SEM/statistical dominance and observed-best versus global-proof distinction.

**Independent evaluation**: seal the newly generated artifact and outcome before allowing any existing historical source or result into the evaluator. Only after sealing can a separate evaluator compare it with old proven same-build Native evidence. Verdicts: VERIFIED_COMPLETE, SOURCE_INSUFFICIENT, SIMC_VERSION_UNSUPPORTED, G_UNVERIFIED, J_F_O_UNVERIFIED, PROFILE_OR_NATIVE_FAILED, or ISOLATION_BREACH. A failure due to genuine SimC-only source limitations is a useful engine capability finding and not a reason to silently broaden permission.

**Next development**: consume actual SimC item database and set metadata into an appropriately scoped season-agnostic representative gear/tier adapter; implement fresh source item↔gem/flask/oil quality relationships; bind actual Native executable/profile JSON2 and build provenance to G; then safely join to v222/v216/v098. These should be normal production engine components, not special logic only to pass the zero-base exam.
