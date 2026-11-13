# SIMC SECONDARY OPTIMIZER — 단독 앱 파일·78기능 추적 운영 규칙

> **최신 사용자 결정 (2026-11-13):** 완성 앱에 포함할 파일을 한눈에 관리하고 문제 발생 시 어떤 파일·테스트·78개 요소를 확인할지 기록한다. **복제된 소스 폴더를 별도로 만들지 않는다.** 하나의 저장소 원본을 사용하고, 기존 배포기가 선정한 파일만 묶어 앱으로 전달한다. 이 문서는 READY나 전체 제품 출시 승인 증거가 아니다.

## 1. 이미 있는 단일 근거를 재사용한다

| 목적 | 현재 정본 | 역할 |
|---|---|---|
| 실제 배포 파일 선정 | [`integration_probes/v181_windows_beta_packager.py`](../../integration_probes/v181_windows_beta_packager.py) `select()` | `BASE_FILES`와 허용 확장자·폴더/필수 파일을 기준으로 현재 Windows 베타 소스를 추출. 새 소스 복사나 두 번째 수동 리스트 금지. |
| **파일명만 TXT로 확인** | `python integration_probes/v181_windows_beta_packager.py --list-files APP_BETA_FILE_LIST.txt` | **같은 `select()`의 결과를 정렬해 TXT로 저장**. 이때 ZIP 생성/네트워크/SimC/Native/원본 DB2 호출 없음. 파일에 `CURRENT_BETA_PACKAGE_CANDIDATES`를 명시한다. |
| 실제 ZIP 바이트·SHA-256 | `python integration_probes/v181_windows_beta_packager.py --out OUTPUT.zip` | 기존 `V181_PACKAGE_MANIFEST.json`이 ZIP 안의 파일 상대경로·길이·SHA256과 빌드 입력 정체성을 기록. 두 ZIP 바이트 재현성/서명 검사는 기존 회귀를 재사용한다. |
| 기능→담당 코드·관련 테스트 | [`FILE_MAP.md`](FILE_MAP.md) · [`FILE_INVENTORY.md`](FILE_INVENTORY.md) | 장애 시 해당 모듈·상하류 호출·회귀 테스트를 찾는 지도. |
| **78개 기능의 실제 준비 상태** | [`ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md`](ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md) | A1~H6 각각의 증거·실제 적용범위·`PENDING_SCOPE/READY_SCOPED` 판정을 관리하는 **유일한 원장**. |

**중요:** 현재 `v181` 패키저는 `runner/`의 `.py/.html/.js/.css`, 허용된 JSON·SIMC 폴더를 기준으로 **폭넓게** 수집한다. 따라서 `APP_BETA_FILE_LIST.txt`가 생성되거나 파일이 ZIP에 들어 있다고 해서 해당 파일이 독립적으로 검증된 최종 출시 구성이라는 뜻이 아니다. 추후 최종 출시본을 축소·정돈할 때는 별도 파일 복사가 아니라 **이 단일 패키저의 배포 선택 조건을 수정**하고 검증된 최소 필수 모듈·의존성만 남긴다. 현재 소스 트리 대이동/전면 패키징 리팩터링은 하지 않는다.

## 2. 78개 기능 = 78개 파일이 아님

**한 기능이 여러 파일에 걸쳐 동작하거나, 하나의 소스가 여러 기능을 담당한다.** 예를 들면:

| 범위 | 주 호출·담당 파일 예시 | 이상 시 함께 확인할 경계 |
|---|---|---|
| A1~A11 시즌/원본 | `v289_retail_live_build_source.py`, `v155_season_api_probe.py`, `v242_authenticated_season_source_stage.py`, `v163_zero_seed_db2_join.py`, `v161_wago_db2_snapshot.py`, `v217_stage_execution_engine.py`, `v216_environment_build_coordinator.py` | 출처·빌드·시즌 정체성 → 원본 봉인·SHA → 실제 유일 시즌 관계 |
| B1~B12 대표 장비 | `v143_specialization_contracts.py`, `v167_product_season_gear_adapter.py`, `v232_simc_only_ordinary_representative.py`, `v251_db2_raid_tier_simc_bridge.py` | 26 DPS 대상·방어구/무기·원본 티어5/실제 4pc |
| C1~C14 소모품·마부 | `v221_gem_item_db2_relation.py`, `v266_gem_enchant_raw_stat_source.py`, `v271_user_socket_gem_layout.py`, `v281_consumable_simc_relation.py`, `v285_consumable_weapon_source.py`, `v296_pinned_oil_static_rating_source.py` | 최고품질·스탯 J/F/O/E·적용 조건·손·선택 항목 |
| D1~D9 사용자 선택 | `v098_target_user_scenario_bootstrap.py`, `v139_pure_target_profile_composer.py`, `v113_local_web_api.py` | 장신구·특수장비·장식/시즌 모듈·프로필 변형 |
| E1~E9 예산·설치 | `v222_season_budget_contract.py`, `v220_catalog_auto_admission.py`, `v212_environment_manifest.py`, `v216_environment_build_coordinator.py` | `B=G+J+F`, `T=B+O`, L/E/O 중복·고정치 보호, SHA 설치 |
| F1~F7 프로필·SimC | `v098_target_user_scenario_bootstrap.py`, `v139_pure_target_profile_composer.py`, `v096_unified_product_entry.py`, `v094_durable_inclusive_adaptive_runner.py` | 게임 스탯·APL·실 바이너리/프로필 정확 입력과 Native JSON2 |
| G1~G10 제품 운영 | `v113_local_web_api.py`, `runner/webui/index.html`, `runner/webui/app.js`, `v348_windows_user_source_credentials.py`, `START_HERE_AUTO_SETUP_AND_RUN.bat` | 사용자 클릭 → 제품 API → 설치·로컬 보안·Windows 실행 |
| H1~H6 최적화·결과 | `v290_multiscale_adaptive_policy.py`, `v291_durable_multiscale_native_runner.py`, `v293_local_longrun_session.py` | DPS/SEM/95%·대안·정확 캐시·취소·재개 |

이 표는 **주요 파일을 찾는 탐색 지도**이며 완전한 의존성 목록도 파일별 품질 판정도 아니다. 자세한 실제 호출·테스트는 `FILE_MAP`, 실제 배포 파일은 패키저에서 생성한 TXT/ZIP manifest, 완성 판정은 78개 원장이 각각 소유한다.

## 3. 결함 수정·출시 등록 방법

1. 증상·해당 **78개 ID**와 실행 조건(시즌·빌드·캐릭터·선택 옵션) 확인.
2. `FILE_MAP`으로 직접 담당 모듈과 그 **수입/수출 경계 및 의존 모듈** 확인. 수정은 가능한 한 원인 파일에 국소 적용하며, 연결 지점에서 증상이 나타났다고 무조건 그 파일만 수정하지 않는다.
3. 관련 테스트와 기존 Native/Actions·영수증을 비교하고, 현재 변경 영향이 있는 최소 범위만 재검증. `READY`는 실제 범위 증거로만 판정.
4. 패키지 대상이 바뀌면 `v181.select()` 하나만 갱신하고 TXT 목록 재생성 + 기존 SHA ZIP/Windows 추출·실행 테스트. **원본 복제/손수 TXT 추가와 패키지 선정 불일치 금지**.
5. 최종 단독 앱의 배포 범위/설치 형태(EXE 여부)는 전체 78 요소 및 최종 현재 시즌 ZERO-SOURCE→USER-E2E 통합 시험과 별도로 배포 시험을 거쳐 확정. 현재 배포는 **Python 소스 Windows 베타 ZIP이며 독립 설치형 EXE 아님**, Windows SimC CLI는 별도이며 키·기밀·사용자 캐시는 ZIP에 포함하지 않는다.

## 4. 이번 변경의 실제 검증 범위

- **구현:** 기존 `v181_windows_beta_packager.py`의 `select()`를 재사용해 `--list-files`로 별도의 TXT *출력물* 생성. 기존 `--out OUTPUT.zip` 경로 불변.
- **신규 회귀:** `tests/test_v181_windows_beta_package_offline.py`에 TXT 정렬/선정 일치·원본 필수경로·테스트/문서/EXE 제외·비TXT 경로 차단을 보강.
- **미관측:** 이 턴의 신규 실제 CI/Windows ZIP·EXE·Native PASS는 아직 없음. 파일 리스트도 로컬/Actions에서 생성된 실제 최신 TXT를 열어 검증하기 전에는 후보 목록 생성 **코드만 존재**한다. 앞선 v181/v345 ZIP·Windows 성공은 과거 조건의 증거로 구분.
- **비용/권한:** 기존 제품/SimC 엔진·캐시·DB 수집 0 변경, 추가 Native/API 0, 기존 ZIP의 바이트/선택 조건 변경 없음. `main`, 사용자 PC/Project UI/공식 승격 변경 없음.
