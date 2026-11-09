# P3-HAS · 새 사용자 무기 기름 O0 기본값 정합성

- **Keywords:** fresh v212 O0, current-season user web default, oil per hand, original v106, session restore, no source-free O.

- **Capability:** `PRODUCT.E2E`.
- **Prior evidence:** Corrected real T3500 run #42552942329 installed exact `official_O=0`; `v106.source_defaults` returns historical oil hands for some class/specs, while `webui.fillDefault` prechecked the fresh form's main-hand oil. This created unprovable user O>0 against v212 O0 and could block an unchanged default user plan.
- **Decision:** `CONNECT` — new current-season browser plans must default to **no oil**, while saved existing sessions restore the actual selected oil hands and explicit oil selections still require exact season item/hand/static-O provenance. No effects reimplemented or unknown O silently assumed zero.
- **Changes:** `runner/webui/index.html` has unchecked default main-hand oil plus brief O0/provenance explanation; `runner/webui/app.js:fillDefault` unchecks both hands (historical v106 source defaults retained for legacy), `fillSessionInputs` restores chosen hands; explicit invalid selected oil maps `SEASON_PROFILE_OIL_PHYSICAL_ITEMS_OR_HANDS_DRIFT` to user-actionable Korean guidance. `tests/test_v114_local_web_ui_offline.py` guards default/restore/API guidance.
- **Verification:** [web #42560987527](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42560987527) **247 PASS each Linux+Windows**; [focused #42560987504](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42560987504) **489 PASS + 2 SKIP**, [UI #42560987522](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42560987522) Linux/Windows PASS, **0 new Native** for change.
- **Remaining:** User-selected O>0 awaits approved per-hand oil source link and v096 fresh installed path still explicitly supports O0; no claim that extra O has been admitted. Reuse existing v281/v278/v286 evidence only in exact season/scope and verify effective profile/B/T once.
- **Efficiency:** UI-only correction, no season rebuild, no additional DB/caches/native or historical session invalidation.
