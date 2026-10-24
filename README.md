# SIMC SECONDARY OPTIMIZER — v033 remote SimC execution pilot

> **Status: OFFLINE_VALIDATED; CLOUD_SIMC_NOT_YET_RUN.**
>
> This repository contains a small, stand-alone GitHub Actions **compatibility pilot**. It does **not** include or replace the full v032 adaptive optimizer implementation, does not run Work OS/M0, and is not a product release.

## What it does

Runs the same **334-ilvl Dwarf Arcane Mage / tier 4 / crafted Arcanoweave Linings x2 / user enchants / Royal Roast / Gebbo's Bottomless Bag + Twisted Horror's Tendril** reference scenario that completed in v031R3 on Windows.

- Builds a Linux SimC CLI from the **pinned upstream source commit `7bc1071`**, rather than taking an unverified latest SimC binary. **The Linux build has not yet been attempted in GitHub Actions; commit availability is checked at runtime and must not be silently substituted.**
- Runs two bounded tests by default, **haste vs crit Omnium row 4**, with the same *static* CHMV vector `600/1140/1115/329` (total `3184`) and unchanged other equipment/settings.
- Verifies native JSON2 equipment IDs, tier effect, crafted embellishment buff, selected rune buff, DPS, and final CHMV.
- Uploads **JSON2 and receipts** even if the run fails.
- Offers **60 iterations** (default smoke) or **320 iterations** (additional evaluation) per candidate. This is **not full CHMV optimization** and not a statistically powered comparison of Omnium rune optima.

## Exact user guide

Follow [`SETUP_KO.md`](SETUP_KO.md). The default is **Private GitHub repository**. A public repo would expose this very profile, its talent export string, and artifacts.

## Run from GitHub

1. Open **Actions** > **v033 Pinned Linux SimC Compatibility Pilot**.
2. Click **Run workflow** (on the default branch).
3. Inputs `rune = both`, `iterations = 60` (recommended first).
4. Start the workflow and inspect the status.
5. Download the `simc-v033-native-evidence-...` artifact from the run summary and return it to the development chat.

Only `workflow_dispatch` triggers runs; `permissions: contents: read`; it does not need secrets, a Blizzard token, an API key, or an always-on server. The GitHub workflow saves outputs for 7 days.

## Reference vs cloud caveats

The Windows reference used SimC `1210-01` git revision `7bc1071` and yielded **194233.24 DPS**, **320 requested iterations / 319 effective samples**, `3184` CHMV. A Linux recompile at the same upstream revision is not necessarily bit-identical to the Windows binary, and this first smoke uses fewer iterations, so **no exact DPS parity is claimed**. The code keeps the difference diagnostic only.

If a required rune buff isn't found or an item is unsupported in the pinned Linux build, the run returns BLOCKED and saves its JSON2/logs for investigation; it must never be treated as PASS.

## Files

- `.github/workflows/remote-simc-v033.yml`: manual Actions workflow
- `runner/pilot.py`: pinned profile generation, bounded SimC invocation, native validation, receipts
- `inputs/v031r3_reference.simc`: portable user-proven Windows baseline, with local output path removed
- `fixtures/v031r3_reference_summary.json`: minimal SHA256+numeric evidence (no private Windows path)
- `tests/test_pilot.py`: offline test suite
- `SETUP_KO.md`: Korean installation and failure-response guide

## Scope boundary

Do not upload `.env`, tokens, full prior handoff ZIPs, original WoW player exports beyond the supplied scenario, Project Sources, protected immutable v003, Work OS artifacts, or full v032 source without separately reviewing visibility. This pilot does not run official Work OS M0 and does not promote Project Instructions / CURRENT / Shared State.
