# 제품 한국어 입력·기술 설정 단순화 (2026-11-11)
- **Capability:** `PRODUCT.E2E`, `DEV.CONTINUITY`.
- **Keywords:** user UI, ko_KR, Korean race, SimC, accessibility, season setup, fixed 26 DPS.
- **Prior evidence:** [기본 v290 통합](2026-11-11_p2-continuous-user-launch.md), [기존 CI](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42976577993), [블리자드 공식 종족](https://worldofwarcraft.blizzard.com/ko-kr/game/races).
- **Decision:** `CONNECT` — UI presentation only. Official race display maps to original SimC tokens. Do not fabricate unavailable official Korean item names, maintain source-only English fallback.
- **Changes:** Race datalist of verified Blizzard Korean names and bidirectional input/restore; season internals and SimC technical controls folded; detailed optimization cap folded; shorter primary copy. New UI regression and old confirmation assertion updated.
- **Verification:** Changes in GitHub, new offline CI pending; no Native/caches touched.
- **Remaining:** Proven item ID→ko_KR localization source and searchable dynamic gear/trinket chooser, runtime browser usage, UI visual review. Separate archived older UI runners preserved.
- **Efficiency:** No extra API fetch, no SimC calls, same input/session identity; only a static local race dictionary.
