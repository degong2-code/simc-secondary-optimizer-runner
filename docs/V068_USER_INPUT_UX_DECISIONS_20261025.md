# v068 UX INPUT DECISIONS — user-approved additions, not implemented yet

Date: 2026-10-25 KST. Authority: direct user's latest agreement to the proposed default/simple+advanced input UX. This note is a **scoped UX decision record on the isolated development branch**, NOT a change to official Project Sources, `main`, Work OS, or a claim of implementation/Native PASS.

## Confirmed decisions

1. **Embellishments ("장식"): default selection count = 2.** Show two independent user-facing choice controls, "장식 1" and "장식 2"; **user selects the specific effect for EACH**. Neither choice is silently inferred from a preconfigured profile; don't default both to an unapproved effect. Actual selection is fixed throughout one CHMV DPS optimization. The approved v1.2 backend limit remains **max 2**, with 0–1 support preserved if user configures an advanced exception; "default 2" is not a SimC guarantee that every selected item/slot combination is equipable.
2. **Omnium tome ("옴니움 장서") fourth UI column**: a required explicit user choice from **critical strike / haste / mastery / versatility** (CHMV). The other three UI columns stay according to standard preset / existing approved profile and are not extra user-required selectors. Distinguish "the 4th UI column" from the 4th serialized SimC `omnium_talents` token: the legacy reference changed the token `136821`↔`136815` (haste/crit) in a sequence without proving positional equivalence. Do **not** hard-code `split('/')[3]` for the 4th UI column. Verify the corresponding exact SimC rune/talent ID mapping for all four choices using authoritative source before implementation; pass through to SimC unmodified, and let SimC calculate effect/APL/DPS.
3. Omnium fourth-column choice is **fixed user combat/scenario condition for one optimization**, NOT a fifth CHMV rating, NOT added automatically to the official `T=G+J+F` budget, and NOT a fifth optimizer dimension. It must contribute to exact SimC source/scenario and DPS cache identity; changing the choice triggers a distinct numeric-calibration/profile identity where appropriate (v063/v066 profile scoped).
4. Keep UX mode defaults from the user's accepted proposal: basic page includes class/spec/race/talents/target ilvl334, two trinkets, two independently selected embellishments, special items/gem, encounter settings, and Omnium fourth column. Expert controls (manual T, gem/socket, buff/flask/food, iterations/threads, manual IDs/option lines) remain under advanced settings. The season item naming/catalog need not be complete to allow user manual exact item ID; no item-effect/proc gate or gear combination optimization.

## Suggested visual inputs (text only)

- 장식 1: [효과 검색/선택] (required when default 2)
- 장식 2: [효과 검색/선택] (required when default 2)
- 옴니움 장서 — 4번째 열: (치명타 | 가속 | 특화 | 유연성) single-choice, explicit required.

## v068 implementation contract / acceptance still pending

- Add two individually named `embellishment` UX choices, resolve their **exact** final item ID/slot/level/options to existing v061 `equipment.crafted` entries with 0–2 max; avoid conflicting tier/special slots and avoid locking initial crafted 50:50 stat distribution.
- Add the explicit Omnium fourth-column enum as a **versioned scenario field** so earlier v061 payloads do not silently drift; exact four-choice SimC rune IDs are **not approved/verified from this chat message alone**.
- Render user-friendly labels backed by exact SimC-compatible IDs, with manual fallback (no season-wide recipe DB).
- Preserve selection across entire single run, rerun calibrated numeric input check after changed Omnium; hash as part of DPS cache; maintain formula `T=G+J+F`.
- Regression cases: two different embellishments, deliberate user-chosen same effect where SimC allows it (do not invent a separate proc support gate), no selection blocking due to unobserved trinket static row, Omnium all four choices mapping and distinct cache identities, no effect modeling.
- Existing v061-v067 code/Native results **unchanged**. No v068 Native proof asserted.

This note supplements and does not replace the user-applied v1.2 Project Source.
