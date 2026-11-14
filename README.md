> **SIMC SECONDARY OPTIMIZER 제품 개발·인계 상시 우선 정책 (2026-11-14 사용자 직접 결정):** [제품 우선·최소 충분 검증](docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md) → [새 채팅 상시 인계](docs/CHAT_CONTINUITY_HANDOFF_20261114_PRODUCT_FIRST_SCOPE_CONTROL.md) → [현 개발 상태](docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md). **78요소는 완료 증거를 기록하기 위한 관리표이지, 번호 순서로 신규 DB·SpellEffect·Native를 전수 조사하는 개발 로드맵이 아님.** 기본 G/J/F/O→대표 프로필→기존 SimC→DPS/95% 결과를 완성하고 선택 미검증 기능만 격리한다. 최신 PASS/HEAD/Actions는 해당 시점에 재조회하며 아래 누적 '최신' 항목은 역사 기록.

> **v405 최신 A7 ZERO-SOURCE 엔진 실 검증:** [실 KR70783 Blizzard/WCL/Wago→v163→v165→v166→v167→v405 자동 후보 출처·시즌 대조](docs/development/notes/2026-11-13_p1-v405-a7-automated-current-source-selection-verified.md) 성공. [실 Actions #43375839959](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43375839959) 원본 434·자동 출처 대조 209·사용자 공개 후보 134, WSE 진단 전용·수동 item ID/AI 선택/Native0·동일 원본 캐시 HTTP0. [78개 자동 판정표](docs/development/78_ELEMENT_STATUS_GENERATED.md): **범용7/현재 원본7/역사3/제품통합0, A7 제품 E2E PENDING, 다음 A8 SimC revision**. [정책 CI #43376626773](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43376626773) 16 PASS. v404 이하 'A7 PENDING' 표현은 해당 시점 이력.

> **v404 최신 A7 직접 결정(이전 v403보다 우선):** [WSE 검증을 필수 시즌 가입 Gate에서 제외하고 현재 raid/M+·같은 빌드 DB2 ID/저널 관계를 엔진이 자동 검사](docs/development/notes/2026-11-13_p1-v404-a7-wse-diagnostic-only-source-first-membership.md). [focused CI #43373512035](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43373512035) **134 PASS/3 SKIP/0 FAIL**, 신규 API/Native0. WSE 원문은 diagnostics로 보존, 잘못된 시즌/불명확한 출처는 계속 보류. A7 제품 전체/실 계정 E2E 검증은 아직 PENDING. 정본 [78개 완료 계약](docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json).

> **2026-11-13 v402 최신 78개 완료 기준 (우선 읽기):** [강제 운영 정책](docs/development/POLICY_78_ELEMENT_COMPLETION_GATE_V401.md) → [상태 정본 JSON](docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json) → [자동 생성 78개 판정표](docs/development/78_ELEMENT_STATUS_GENERATED.md) → [A4~A6 기존 실 원본·범용 회귀 재판정](docs/development/notes/2026-11-13_p1-v402-a4-a6-generic-scope-reassessment.md). **범용 PASS A1~A6 6 / 현재 원본 PASS 같은 6 / 역사 PASS 3 / 제품 통합 PASS 0 / 최종 E2E PENDING**. 기존 A4~A6 단순 source READY 표기는 v402 이전 이력. [CI 정책 검사](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43369491683) 실제 14 PASS, 증거 상태 일치 검사이지 SimC Native 실증 아님. 다음 **A7**. 주 제품 채팅 소유권/main/Project UI 변경 없음.

> **앱 파일 목록·담당 기능 최신 규칙 (2026-11-13 격리 개발):** [단일 배포 파일 선정 + 자동 TXT 목록 + 78개 기능 대응](docs/development/APP_PACKAGE_FILE_REGISTRY_20261113.md). `python integration_probes/v181_windows_beta_packager.py --list-files APP_BETA_FILE_LIST.txt`로 **현재 Windows 베타 ZIP 후보 파일명**을 얻는다. 원본 복사/수동 중복 목록 없이 실제 ZIP의 `V181_PACKAGE_MANIFEST.json`이 바이트 SHA를 보관한다. 배포 후보 ≠ 최종 앱 READY. 실제 준비 상태는 [78개 원장](docs/development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md), 최신 인계는 [v386](docs/CHAT_CONTINUITY_HANDOFF_20261113_P1_V386_ZERO_SOURCE_GENERALIZATION.md)이며 신규 CI/Windows PASS를 주장하지 않는다. 아래 README의 v033/v18x 내용은 역사 자료다.

> **2026-11-10 현재 지식 지도(격리 개발만):** [START_HERE](docs/development/START_HERE.md) → [INDEX](docs/development/INDEX.md) → [FILE_MAP](docs/development/FILE_MAP.md) → [EVIDENCE_INDEX](docs/development/EVIDENCE_INDEX.md) → [DECISIONS](docs/development/DECISIONS.md). 아래 v033/v18x README 안내는 역사 호환 설명으로 최신 제품 판정이 아니다. [P3-HAW](docs/CHAT_CONTINUITY_HANDOFF_20261110_P3_HAW_OPTIMIZER_RESUME_ENGINE_FIRST.md) 기준. main/Project UI/공식 승격 변경 아님.

---

> **2026-10-30 최신 v182/v183:** 사용자용 Windows 베타는 [v182 갱신 ZIP (7일 보관)](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40986181287/artifacts/12946803072)이며, 기존 v181 ZIP은 역사 버전입니다. [현재 상태 CURRENT](docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md), [새 채팅 정본 인계·시작 프롬프트](docs/CHAT_CONTINUITY_HANDOFF_20261030_V183.md), [최신 개발자 노트 보충](docs/DEVELOPER_NOTES_v1.4.2_LATEST_USER_POLICY_ADDENDUM_20261030.md), [설치 절차](WINDOWS_BETA_START_HERE.md). **26 DPS/증강 제외, 목표 ilvl266–344, 사용자 장비 ID/bonus 수동 부담 제거, 옴니움 4열 선택**. UI 회귀 Windows·Ubuntu PASS, 유연 옴니움 최초 SimC 오류는 정확 source ID 교정으로 Native1회 PASS. 별도 Windows 사용자 냉법 낮은 DPS 원인과 실제 티어/효과 입력 정합은 아직 미확정입니다. **본 README·GitHub 갱신은 Project Sources/Instructions 실제 UI 적용이 아닙니다.**

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
