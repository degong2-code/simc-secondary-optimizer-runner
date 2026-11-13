# v408 — A8 사용자 바이너리 경로와 저장 세션 재개 경계

- **Capability:** `SOURCE.SEAL` (A8 exact SimC binary/source identity)
- **Keywords:** A8, SimC revision, binary SHA256, v113, v106, saved session, symlink, resume
- **Prior evidence:** [A8 v407 scoped historic + source regression](2026-11-13_p1-v407-a8-historical-source-binary-identity-and-alias-guard.md); v342/v344 unchanged Windows evidence
- **Decision:** `EXTEND` only existing v113 plan and resume binary-path checks; `REUSE` v106 SHA session identity and v291 JSON2/DPS checks
- **Changes:** Reject direct symlink input before `resolve()` in `LocalJobs.plan` and saved `args_for_existing`; add two zero-Native user-API negative regressions; no identity schema, oil, budget, or cache changes
- **Verification:** v113 offline existing Linux/Windows CI will decide PASS/FAIL on this commit; no new SimC call; historic v342/v344 scope unchanged
- **Remaining:** A8 generic/current_source/product_integration remain PENDING; a single current real request still needs source revision/engine bytes/compiled build relation checked without treating a CLI banner as independent compiled DB proof
- **Efficiency:** Native 0; DB2 0; new SimC source downloads 0; SHA computed only by unchanged v106 session path; no separate Gate or duplicated Native run

The local user can select their binary normally. Only symlink aliases are forbidden at the two existing boundaries. A previously saved binary replaced by different bytes is already rejected by v106 session identity before worker restart; preserving that code also preserves existing valid resume/caches.
