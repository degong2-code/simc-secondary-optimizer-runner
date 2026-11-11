# 제품 한국어 입력·기술 설정 단순화 (2026-11-11)
- **Capability:** `PRODUCT.E2E`, `DEV.CONTINUITY`.
- **Keywords:** user UI, ko_KR, Korean race, SimC, accessibility, season setup, fixed 26 DPS.
- **Prior evidence:** [기본 v290 통합](2026-11-11_p2-continuous-user-launch.md), [기존 CI](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42976577993), [블리자드 공식 종족](https://worldofwarcraft.blizzard.com/ko-kr/game/races).
- **Decision:** `CONNECT` — UI presentation only. Official race display maps to original SimC tokens. Do not fabricate unavailable official Korean item names, maintain source-only English fallback.
- **Changes:** Race datalist of verified Blizzard Korean names and bidirectional input/restore; folded technical controls; searchable listboxes preserve select IDs. Added v332 official Blizzard ko_KR item lookup with exact ID/source hash/season catalog SHA and optional read-only display mapping. No effect/budget changes.
- **Verification:** Changes in GitHub, new offline CI pending; no Native/caches touched.
- **Remaining:** v332 authorized live name receipt / populated static item map not yet verified; actual browser interaction/visual review; unknown non-SimC item IDs remain English. Separate archived older UI runners preserved.
- **Efficiency:** Normal product startup does zero new network and Native. v332 is explicit one-time name-only acquisition (max 128 IDs, 4 workers); static catalog validates SHA and is reused across runs. SimC input/session identity untouched.
