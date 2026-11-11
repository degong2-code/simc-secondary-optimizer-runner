# P2 — 일반 사용자 연속 실행

- **Capability:** `OPTIMIZER.POLICY`, `PRODUCT.E2E`, `DEV.CONTINUITY`.
- **Keywords:** v290, v293, continuous, UI, search.
- **Prior evidence:** [N56 적용](notes/2026-11-11_p2-product-v290-default-n56.md).
- **Decision:** `CONNECT` — 기존 durable runner를 기본 실행에 연결. 내부 상한 64 (v331 비교 기준), 900초 기존 안전 상한, 명시 재개. 기존 API 기본값 유지.
- **Changes:** continuous opt-in worker passes None for per-invocation cap, retains cumulative bound and cancellation; browser primary start/resume/cancel uses existing longrun API. Hide legacy developer controls; native select search and item labels without IDs. Official Korean localization still incomplete; do not invent translations.
- **Verification:** Added worker regression; CI pending. No new Native.
- **Remaining:** actual Native primary path, full official Korean source localization, all dynamic selectors and settings cleanup, browser UX validation.
- **Efficiency:** one worker, one durable invocation; no polling-triggered native execution or repeated journal replay between batches.
