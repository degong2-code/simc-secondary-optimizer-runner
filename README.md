> **2026-10-30 Windows 로컬 웹 베타 v181:** [다운로드/실행 안내](WINDOWS_BETA_START_HERE.md) · [실제 Windows 3.12/3.14 ZIP/HTTP PASS 증거](docs/V181_P1D_WINDOWS_LOCAL_BETA_PACKAGE_REAL_HTTP_20261030.md). 설치형 EXE가 아닌 **소스 ZIP**이며 사용자 Windows SimC CLI가 필요합니다. 계획/복원/보안은 Windows 실측, 새 시즌 사용자 SimC Native 계산은 기존 Linux v180 증거와 구분합니다.

> **2026-10-29 제품 개발 현재 기준 (격리 브랜치):** 아래 v033 기록은 역사적 호환성 파일이며 최신 사용자 제품 설계가 아닙니다. 최신 사용자 승인 입력 기준은 [장비 엔진/사용자 선택 정책](docs/APPROVED_PRODUCT_GEAR_USER_FLOW_20261029.md), 실제 검증·미완료는 [CURRENT](docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md)를 우선 확인하십시오. **DPS 26개 (증강 제외), 목표 ilvl 266~344 기본334, 절대 CHMV rating 최적화.** 사용자는 **이번 시즌 목록의 장신구 2개·선택 특수효과 장비** 및 **장식 제작장비 최대 2개의 정확 ID 예외**만 장비로 입력합니다. 일반 대표 방어구·무기·티어 4세트는 내부 고정 구성하고 사용자에게 ID 자유입력·후보 선택·조회 기능을 제공하지 않습니다. 내부 검증 로직은 유지, SimC 효과/DPS 및 기존 캐시/중단·재개를 재사용. 신규 Native 검증이 없으면 제품 완성이라고 주장하지 않습니다. GitHub에 문서를 썼다고 Project UI의 Instructions/Sources가 변경된 것은 아닙니다.

---

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
