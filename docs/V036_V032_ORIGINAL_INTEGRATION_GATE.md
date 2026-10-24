# v036 — Exact v032 source acquisition gate

**Status:** `SOURCE_PACKAGE_REQUIRED`; original `SIMC_SECONDARY_OPTIMIZER_OMNIUM_ADAPTIVE_v032.zip` bytes unavailable in this Chat/Project/GitHub as of 2026-10-24.

This is an integration **preflight** only, not a rewritten v032 engine, not a v032 regression and not a native SimC run. Existing v033/v035 native pilot results remain valid separately.

## Source requirement

Obtain the **original** ZIP from the prior v032 development chat, not an identically named reconstruction or v033 bundle. Review archive before any remote push. It must contain exactly one `SIMC_OMNIUM_CHMV_ADAPTIVE_v032.py` and must not contain credentials. The acquisition scan computes the original ZIP SHA256, file-level hashes, validates ZIP CRC by reading members, rejects traversal/symlinks and suspicious secret filenames. A matching file name is **not** identity proof; independently compare source to original provenance and rerun v032's 429 offline regressions before trusting it.

Invoke from the repository root:

```bash
python runner/v036_source_gate.py \
  --source _incoming_v032/SIMC_SECONDARY_OPTIMIZER_OMNIUM_ADAPTIVE_v032.zip \
  --receipt run-output/V036_SOURCE_ADMISSION.json
```

Missing ZIP produces `BLOCKED / SOURCE_PACKAGE_REQUIRED` with exit 3 and receipt. Candidate inspection returns `SOURCE_CANDIDATE_INSPECTED` with exit 0; this is **not** `VERIFIED_V032` or an optimization pass. `--expected-sha256` is optional, and should be supplied only if the hash is independently attested. Internal contents require manual review; this preflight is not an exhaustive secret scanner.

**Scope rules:** branch-only v036 experiments; no changes to Work OS M0/Project Sources/Instructions/CURRENT/Shared State/v003. Don't alter user-approved CHMV budget, fixed items, Omnium default crit selection, or scenario policies. Do not interpret fixed-vector v033-v035 results as CHMV optimization.

**Next technical gate after original arrives:** original ZIP hashes/contents/provenance → v032 original 429/429 regression reproduction → source/build compatibility check → v035 pinned Linux binary cache on the same trusted branch → actual adaptive candidates native JSON2 with budget/rune/effects verification → statistically defensible DPS rankings and meaningfully distinct alternative ratings. Never silently substitute v015 or v033.