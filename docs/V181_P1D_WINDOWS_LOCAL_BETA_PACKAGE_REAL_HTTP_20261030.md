# v181 P1-D — Windows 로컬 웹 베타 ZIP / 실제 Windows HTTP 통합 검증

**실행일:** 2026-10-30 KST. **실제 격리 브랜치:** `probe/chat-cache-v035-20261024`.

## 사용자 목적 및 경계

- 목적: 26개 DPS 전문화의 미래 목표 ilvl 266–344 또는 수동 최종 T에 맞춰 치명·가속·특화·유연의 최적 **절대 rating**을 SimC DPS로 찾는 로컬 Windows 프로그램. 입력은 직업/전문화/종족/특성, 시즌 장신구 2개·선택 특수장비/장식·소모품·기름·전투조건이며 일반 장비·무기·티어는 내부 생성. 결과는 기존 v094의 95% 판단·관측 1순위·DPS·SEM·근접 대안·캐시/취소/재개.
- v181의 범위는 **이미 존재하던 Windows CMD/로컬 웹 UI를 일반 사용자가 압축을 풀어 바로 시작할 수 있도록 소스 베타 ZIP화**하는 것. 대규모 최적화 엔진 변경, 장비 DB 확대, Native 전수 재실측, 전용 EXE 설치 관리자/SimC 바이너리 배포는 **하지 않음**.
- 기존 로컬 Windows 실행 경로 `START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd`, `runner/v113_local_web_api.py`, `runner/v106_user_session_controller.py`, `runner/v098→v096→v094` **변경하지 않음**. v181은 패키지 생성기·테스트·배포 안내·Actions만 추가.

## 구현 내용

- `integration_probes/v181_windows_beta_packager.py`: 명시적 허용 폴더에서 **168개** 필요한 소스·시즌 메타데이터·SimC 참조 파일 선택, 재현성 있는 ZIP 메타데이터, SHA256 전부 기록한 `V181_PACKAGE_MANIFEST.json` 포함. Windows `START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd`, `requirements-web.txt`, `WINDOWS_BETA_START_HERE.md` 포함. `simc.exe`/DLL/개인 실행 캐시/이전 영수증/테스트 결과/.git/.github 포함하지 않음. ZIP 생성 과정 네트워크·Native 호출 없음. 기본 로컬 세션은 계속 `%USERPROFILE%\SIMC_Secondary_Optimizer\runs`에 따로 존재하고 배포 ZIP과 혼합되지 않음.
- `integration_probes/v181_windows_beta_live_http.py`: GitHub의 **진짜 Windows 러너**에서 생성한 ZIP을 별도 임시 폴더에 압축 해제하고, 그 폴더 안의 CMD를 `--check`로 호출한 뒤, 압축 해제한 앱의 **진짜 Uvicorn HTTP 프로세스**를 127.0.0.1의 로컬 포트에서 가동한다. `/api/v1/health`, 26개 기본 사용자 입력, 최신 시즌 장비목록/HTML/JS, 징벌 성기사334·분노 전사321·냉기 마법사344의 HTTP `plan`(3건, Native 0), 세션복원·미실행 상태, 미인증·외부 Host·외부 Origin 차단 등을 실제 검증. 가짜 비실행 `simc.exe`는 임시파일일 뿐, 실제 SimC subprocess는 시작하지 않음.
- `tests/test_v181_windows_beta_package_offline.py`: 두 ZIP 바이트의 재현성, 168개 원본 SHA256 정확히 일치, 민감/실행/로컬 캐시 제외, 필수 파일 부재 차단 확인.
- `WINDOWS_BETA_START_HERE.md`: Python 3.12+, requirements 설치 한 줄, 실제 사용자 소유 SimC Windows CLI 경로와 대응하는 Git revision 지정, 계획(Native0)과 계산 실행의 차이, 저장 세션/캐시 보존, 실행 문제 해결 절차.

## 실제 GitHub Actions 결과

**[v181 실제 Windows Actions #40981704073](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40981704073) — SUCCESS (두 job 모두).**

| 실행 환경 | 소스 ZIP 재현성 테스트 | 압축 해제 후 CMD --check | 실제 로컬 웹·3개 계획·세션 복원·보안 | 기존 오프라인 회귀 | Native |
|---|---|---|---|---|---|
| Windows Server 2022 / Python 3.12 | 2 PASS | PASS | PASS | 59 PASS | 0 |
| Windows Server 2022 / Python 3.14 | 2 PASS | PASS | PASS | 59 PASS | 0 |

- 배포 ZIP: [Artifact #12945206666](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40981704073/artifacts/12945206666), **7일 보존**, artifact 표시 크기 **597,712 bytes** (GitHub 자체 다운로드 포장 형식 포함). 사용자 ZIP 내부 `V181_PACKAGE_MANIFEST.json`에서 소스별 SHA 확인 가능.
- 환경별 새 배포 시험 성공: `V181_WINDOWS_SOURCE_ZIP_PASS files 168`, `V181_WINDOWS_EXTRACTED_LAUNCHER_CHECK_PASS`, `V181_WINDOWS_HTTP_PLAN_PASS` 334/321/344 각1, `V181_WINDOWS_LIVE_HTTP_SECURITY_PASS`, `V181_WINDOWS_BETA_LIVE_3_PLANS_RESTORE_ZERO_NATIVE_PASS`.
- 기존 59회/환경 회귀는 Windows loopback security, user session, SHA/cache, UI/JS, current season 26-spec logic 및 비334 선택 경로 관련 **오프라인** 검증. 최신 기본 v180 Linux 실제 SimC **36/36 + cache36/36**는 기존 영수증 재사용했고 이번 Actions에서 수행하지 않음.

## 미완료 및 정확한 주장 범위

1. **실제 새 시즌 v180 Windows 사용자 PC에서의 SimC Native 6후보 실행, DPS·SEM·95% 결과 조회 및 브라우저 버튼 취소/재개**는 v181에서 수행하지 않았다. 실제 Windows 64비트 SimC 실행 바이너리/본인 환경이 Actions ZIP에 없고, Native0회 계획 검증과 구별해야 한다. 과거 v111 Windows 실제 Native PASS와 새 시즌 Linux v180 실측은 별도 범위 증거.
2. ZIP은 **Python 소스 웹 베타**, 독립형 .exe 설치 패키지가 아니다. Python 3.12+ + 웹 의존성을 사용자가 설치하고, SimC CLI 경로·실제 git revision을 입력해야 한다. 자동 pip/SimC 다운로드/실행, 시스템 PATH 수정, OS 설치 서비스는 추가하지 않았다.
3. 오래된 `v147_batch`가 있을 경우 **읽기 전용 열람**만 한다. 캐시 전환/영구 WEQUIP 의존 없음. special L 미확보 차단과 user-specific 소비품 조건은 기존 정책 유지.
4. 사용자 지정 Windows PC 실측이 완료되면 P1-D 실제 사용 확인을 확정할 수 있다. 이 단계의 결과만으로 독립 앱 설치/전체 제품 release-ready라고 주장하지 않는다.
5. 원래 `main` 병합, 불변 `v003` 변경, 사용자 Project Sources/Instructions UI 업데이트, 공식 Work OS 승격은 없음.

**실행 안내:** [WINDOWS_BETA_START_HERE.md](../WINDOWS_BETA_START_HERE.md). 최신 상태 [CURRENT_PRODUCT_DEVELOPMENT_STATE.md](./CURRENT_PRODUCT_DEVELOPMENT_STATE.md).
