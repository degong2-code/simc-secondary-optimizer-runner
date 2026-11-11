# P2 2026-11-11 — v320 IDEA-001 SEM 실측 기반 35/120/320 예산 진단 (오프라인)

- **Capability:** `OPTIMIZER.POLICY`, `DEV.CONTINUITY`.
- **Keywords:** v320, IDEA-001, SEM, 35, 120, 320, Native JSON2 actual samples, fixed-reference variance, 95 nominal, 120 gate.
- **Prior evidence:** [v319 fresh Windwalker 128 DPS Native](../research_receipts/p2_v319_windwalker_auto_T_real_v290_v318_compact.json), [#42941245130](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42941245130).
- **Decision:** `EXTEND` IDEA-001 as **offline/advisory** only; keep v291's exact 35/320 phases and v290 product default. Do not add 120 tier before empirical economic and exact-cache validation.
- **Changes:** Add pure [v320 advisor](../../../runner/v320_idea001_sem_tier_advisory.py) and [focused tests](../../../tests/test_p2_v320_sem_tier_advisory_offline.py). Uses real observed samples, SEM, differential gap and reference SEM floor; predicted n is never called a Native observation.
- **Verification:** Existing v319 original 8+8 same-CHMV 35/320 scout→confirmation matched pairs: SEM35/SEM320 medians ≈3.089/2.999 for original v290/v318 respectively; original benchmark 44 focused PASS and P1 Build3, 128 DPS Native. **New v320 CI and 120 Native NOT YET RUN at this note's initial creation**.
- **Remaining:** Verify new focused CI; use new-specialization profile source Build/SimC for any *new* Native experiment. Measure 120 tier survival fraction at equivalent effective iterations and process wall before inserting into v291.
- **Efficiency:** No extra SimC, old histories reused for diagnostic; v291 already rejects 120 in confirm phase, and extra 120→320 cost is ~45% of direct320 on previously measured Linux profiles. An intermediate tier helps only if enough candidates are screened out; do not recompute full seasonal DB or old DPS.
