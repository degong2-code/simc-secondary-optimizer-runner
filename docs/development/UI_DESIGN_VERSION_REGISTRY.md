# SIMC SECONDARY OPTIMIZER — UI design versions & rollback authority

Design history is preserved in immutable Git commits on the isolated development branch. The latest user-approved visual design is **not** overwritten by a prototype. This registry records design-only diffs and a precise restoration target; it does not authorize a main merge, invalidate signed session receipts, or change formal 78-element completion state.

## v651 — rollback baseline (2026-11-20)

- Commit: `071cc1f48c8159ec75469c00049c2f753b8c8542`.
- Product UI: v647-approved section separators/low row-rule density plus v649 idle polling and v650 equipment-choice memoization.
- File blob IDs at baseline: `index.html` `1ee8afbcd1a24ee14099b967953d69d347e0c43b`, `styles.css` `9d67b03b8a3a09ffe063814da157b7fc0a312cf0`, `app.js` `0d8ea388f9d5bc7abfe8f187ad9f7a252714300d`.
- v651 Windows CI (after UI performance changes) is **not** claimed as run. v647 original ZIP/Windows receipt is historical.

## v652 — user-directed environment layout (2026-11-20)

- **Scope:** `runner/webui/index.html`, `styles.css`, `app.js`; no Python budget, SimC, Native, v229/v217 stage code, cache keys or API protocol changes.
- Environment row 1: targets / duration / socket total / weapon-oil **사용·미사용 dropdown**. Legacy `optimizer-oil-enabled` remains hidden and drives the exact existing O=0 / selected verified oil behavior. The dropdown reflects the legacy state; a UI-only selection does not create a verified installation.
- Environment row 2: food / **actual verified installed flask select** (`season-verified-flask`, moved from advanced) / potion / **existing augmentation rune select** (`augmentation`, moved from the bottom row). All controls keep their existing IDs and validated source choices.
- Omnium special-season optional selector remains separately full width; raid buff checkbox remains available.
- Enchants visually use 4-column rows: main-hand weapon / off-hand weapon / ring1 / ring2; chest / legs (2 columns each); helm / shoulders / back / boots; waist / hands / wrists / neck. **Weapon semantics are unchanged:** main/off hand are separate slots, not two aliases called “weapon” and “main-hand.” Hidden `season_enchant_other` compatibility input remains.
- Uniform label and 36px control heights, CSS grid 4 columns desktop / 2 columns <=880px; v647 panel borders/typography preserved. Selected environment verification button and its current status receive muted shaded background and left emphasis, without changing readiness gates.
- Added `tests/test_p3_v652_environment_grid_design_offline.py` for HTML order / uniqueness, CSS and oil dropdown JS wiring.
- **Rollback:** from the isolated branch (after reconciling any later edits), run:
  `git restore --source=071cc1f48c8159ec75469c00049c2f753b8c8542 -- runner/webui/index.html runner/webui/styles.css runner/webui/app.js`
  This restores the three v651 UI files only; review diff and commit the restoration. Do not use `git reset --hard` or delete user session data.
- Source SHA after UI implementation (before final docs): `index.html` `75ea7c56a9ee7f70de2396a727ceca433f334523`, `styles.css` `c14434c2f14b573754288631be565697098597f1`, `app.js` `d98f4b26342db404d4587ce18f09752a27ff87c6`.
- **Validation distinction:** static DOM/string contract inspection performed. Official Windows beta CI / new ZIP, actual Chrome on Windows and SimC Native are not claimed complete until there is corresponding new receipt. The unresolved user-PC V229 code has not been touched.

### Rules for future design revisions

1. Record a unique UI version, commit baseline, file scope, rollback target and what actually changed.
2. Preserve stable form IDs, accessible labels, verified-source selection, old-session restore and status/ready meaning; run actual tests before claiming regressions passed.
3. First apply user-approved targeted UI changes; avoid global CSS overrides, unrelated code refactors or designs whose behavior is disconnected from the product.
4. User reference images can guide styling; changes remain reversible. Do not infer Project UI/Source publication from GitHub documentation.
