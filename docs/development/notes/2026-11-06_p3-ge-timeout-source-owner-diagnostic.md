# 2026-11-06 · P3-GE · 실 T1 읽기 시간초과 원본 단계 분리

- **Capability:** `SOURCE.SEAL`, `ENVIRONMENT.WEB`
- **Keywords:** timeout, v216, v242, v161, Wago, authenticated discovery, live 70783, no retry, zero Native
- **Prior evidence:** [P3-GD](2026-11-06_p3-gd-exact-git-blob-403-recovery.md) exact Git blob API fallback SHA verified in [real Actions #42165803925](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42165803925) forced raw-403 preflight. Subsequent original v216 T1 exited `ZERO_BASE_T1_BLOCKED` with `TimeoutError: The read operation timed out` after Retail build observed, with source_stage_status=null, Native0, so the exact timed-out source owner is not proven.
- **Decision:** `CONNECT` the original source boundary to existing error codes. No source/version change assumption, no new certifier, retries, Wago read, Native or stage/cache clearing.
- **Changes:** v216 catches unhandled TimeoutError separately in original v242 authenticated season discovery and original v161/v217 Wago stage; reports `V216_AUTHENTICATED_SEASON_DISCOVERY_TIMEOUT` vs `V216_FRESH_WAGO_SOURCE_TIMEOUT`. Existing v155/v161/v217 inputs and dependency fingerprints unchanged: same-build sealed caches remain reusable. Existing exception type preserved under v216 code.
- **Verification:** Offline synthetic timeout tests injected at both existing boundaries; Actions exact commit pending. Previous live T1 timeout remains undifferentiated and NOT_READY.
- **Remaining:** A next real T1 need only be considered after evidence indicates the external HTTP read is available; full zero-base re-query merely to distinguish transient endpoints is inefficient. Neck fallback v165→v232 and actual G/J/F/O/READY still need first real end-to-end proof.
- **Efficiency:** Zero HTTP/Native in this change, no duplicate source collection, no source-stage code fingerprint churn, no increased persisted data; minimal diagnostic connection.
