# P2 — v290 제품 신규 세션 기본 N56/320 적용 (2026-11-11)

- **Capability:** `OPTIMIZER.POLICY`, `PRODUCT.E2E`, `DEV.CONTINUITY`.
- **Keywords:** v331, v290, v293, default N56, legacy35, session seal, cache, web UI.
- **Prior evidence:** [v331 343 Native](../research_receipts/p2_v331_unholy_fixed_N_343_native_compact.json), [인계](../../CHAT_CONTINUITY_HANDOFF_20261111_P2_V331_PRODUCT_FINALIZATION.md). Same-wall discovery N56 best; same-iterations N35 better; one spec, no universal winner.
- **Decision:** User '진행' after read-only handoff; adopt engineering N56/320 for new v293 product sessions, retain v290, permanent legacy35, same identity/cache rules. No new algorithm research.
- **Changes:** v293 DEFAULT=56 only (legacy=35, allowed 35/48/56/64); existing v093 rebind and v291 execution preserved. Actual default regression, HTTP start/resume sealed N check, UI progress/result N from API. No rewriting old config or cache. Ordinary legacy six-candidate button still separate from v290 longrun route; address this concrete integration gap in next product step, not by silently changing legacy execution.
- **Verification:** Code/HTTP/UI regression added. Existing push-triggered common and web offline CI must be checked on new HEAD; no fresh PASS claim until receipts. Actual N56 user-product Native E2E remains pending; v331 raw verification reused, not rerun.
- **Remaining:** Confirm new CI, minimal real user N56 path with actual input and JSON2 if needed; unify ordinary product launch with existing durable v290 path while retaining legacy compatibility; UI and Windows real-use validation.
- **Efficiency:** No additional engine or dependency, no environment rebuild or repeated v331 experiment, no new Native in this change. N56 cost higher per scout; v331 discovery earlier, no universal speed/quality guarantee. Existing cache-only identity unchanged.
