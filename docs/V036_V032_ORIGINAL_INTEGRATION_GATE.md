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

---

## 2026-10-24 successor: original v032 received, independent regression and bounded Linux native PASS

The original archive was subsequently supplied. **The earlier SOURCE_PACKAGE_REQUIRED block above remains accurate as a historical first preflight**, but it is no longer the current integration blocker.

- Exact original archive SHA256: `072a18d24d37770d454a35ece1cb2a3d1b72624655c32e46dc4f2fc551a6968b`; 191/191 manifest entries and ZIP CRC verified.
- **Independent original v032 offline regression: 429/429 PASS**. This is distinct from v036 cloud runtime checks.
- Privacy-scoped Linux payload: 17 original Python source files byte-for-byte preserved; two native-evidence ZIPs derived by redacting 8 Windows JSON2 output paths while retaining JSON2 evidence unchanged. Payload SHA256 `38d5956ae50965a61abe253b1a3d680a9c5e59bfc322208dc3361cef7b52eac6`.
- Original Windows SimC SHA pin was mapped in the **cloud-only adapter**, not in original v032 source, after independently validating pinned Linux binary SHA `64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e`. Windows JSON2 revision `7bc1071` and Linux JSON2 revision `7bc10711b5` are pinned to the same upstream full commit.
- Successful execution: [GitHub Actions Run 40101013866](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40101013866), on the isolated `probe/chat-cache-v035-20261024` branch where cache reuse was verified; **Cache HIT**, no C++ recompilation.
- User scope: fixed dwarf Arcane Mage representative scenario, total **3184 CHMV**, crit Omnium row-4 rune. One compatibility probe plus **six 120-iteration scout candidates and two 320-iteration confirmation candidates**. All 9 native cases independently inspected with exact CHMV and rune buff, 8/8 actual v032 adaptive engine native passes.
- Confirmation 1: `600/1140/1115/329`, DPS `194635.636`, SEM `537.070`. Confirmation 2: `605/1369/605/605`, DPS `195555.295`, SEM `523.404`. Difference `+919.659` DPS (2 minus 1), combined approximate 95% difference half-width `1469.865`. **No statistically established winner, global optimum, cross-spec readiness or product completion claim.**
- Independent machine-readable receipt: [V036_ORIGINAL_V032_NATIVE_ACCEPTANCE_20261024.json](V036_ORIGINAL_V032_NATIVE_ACCEPTANCE_20261024.json). Downloaded Actions artifact ID: `12562553738`.
- First two Linux attempts were blocked (relative SimC input path; revision-string mismatch) and retained as failure evidence. No unbounded retry or silent bypass.
- v033 on `main`, official Work OS `M0_STAT_INJECTION_FEASIBILITY`, Project Instructions/Sources, CURRENT/Shared State, and immutable v003 remain unchanged.
- **Remaining product work:** broaden inputs/specs and target-ilvl policies, real item/effect support, validated optimizer coverage, statistics and distinct alternatives, usable UI, and trusted production branch/cache strategy.

This successor result supersedes only the gate's earlier source-unavailable operational conclusion. It does not rewrite that evidence or approve changes to the product specification or official Work OS.
