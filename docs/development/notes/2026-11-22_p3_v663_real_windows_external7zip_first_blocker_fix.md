# 2026-11-22 P3 v663 — v660 단일 ZIP에서 실제 Windows 외부 7z 우선 선택으로 발생한 압축 속성 차단 최소 수정

## 실제 사용자 목적과 오류 범위
제품 목표는 목표 ilvl/수동 최종 T의 26 DPS 전문화에 대해 미래 CHMV 최적 절대 rating과 실제 SimC DPS/SEM/95%/근접 대안을 제공하는 것이다. v660 단일 Windows ZIP의 SimC 자동 확보는 그 선행 경로일 뿐이며, 새 optimizer·APL·장비 DB나 원본 인증 Gate를 개발하지 않는다.

## 원본 v660 단일 ZIP을 변경하지 않고 재현한 첫 실제 Windows 장애
- [v662 재현 #45019076230](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45019076230): Windows2022에 외부 7z.exe가 존재하며, **기존 v660 단일 ZIP 원본** 285파일 SHA/CRC·역사 자료 임시 격리 검증 PASS. 실제 KR Live 12.1.5.70961, 공개 후보 1. 공식 source SHA `6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7`/3개 generated header PASS, 공개 GitHub Release ZIP HTTPS 다운로드·digest PASS, 네 파일 자체 빌드 receipt PASS.
- **첫 차단:** 기존 v193의 `find_extractor()`는 Windows 외부 7z.exe 우선. 실제 `install_self_built`에서 `ARCHIVE_ATTRIBUTES_UNRECOGNIZED` 발생. v660은 내부 예외를 소비하고 `SOURCE_BUILD_REQUIRES_REMOTE_BUILDER`를 반환(`public_release_candidates_checked=1`, `public_release_errors=1`), 외부 다운로드·원본 부재처럼 오인될 수 있었다. 파일의 실제 7z `Attributes` 문자열 전체는 이 영수증에 기록하지 않았으므로 단정하지 않는다.
- 이전 [v660 성공 #45012696519](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45012696519)은 외부 7z 선택을 강제로 비활성화한 py7zr 안전 추출 경로. 현재 재현은 기존 성공 범위와 다른 **외부 7z 설치된 PC** 조건을 노출했다.

## 최소 코드 변경
- **단일 제품 런타임 파일:** `runner/v660_simc_one_click_provision.py`만 `importlib.util.find_spec('py7zr')`로 관리 Python 설치 여부를 확인하고, 사용자 별도 `sevenzip` 지정이 없다면 기존 `v193_simc_local_updater.PY7ZR_TOOL`을 자동 확보의 우선 추출기로 선택. py7zr가 없으면 과거 외부 7zip 경로/기존 오류 유지. 수동 설치 명시 override와 v193 원본 외부 도구 검증 규칙 자체는 변경하지 않는다.
- py7zr는 기존 v660 패키지의 `requirements-web.txt`에 이미 들어 있어, 사용자 PC에 외부 7z.exe 또는 새 컴파일러 설치를 요구하지 않는다. 경로/링크/중복/암호/확장 크기/PE x64/CLI SHA·내장 게임빌드/원자적 설치·rollback은 기존 모듈 그대로. 파일 I/O는 기존 한번의 압축 해제, 신규 HTTP·Native DPS 호출은 추가하지 않는다. Python 안전 경로의 실행 시간은 외부 7z보다 느릴 수 있으나 실제 새 Windows 테스트에서 성공했다.
- 신규 regression 2개(외부 7z 존재해도 안전 Python 선택, 명시적 외부 도구 override 보존)는 `tests/test_p3_v660_one_click_simc_offline.py`에 추가. 기존 CSS·UI v653, G/J/F/O·L/E/O, 적응형 SimC/95%, 사용자 세션·DPS 캐시/저장/취소·재개/rollback, v229/Stage fingerprint **변경 0**.

## 신규 PASS/과거 증거 구분
- [v663 자동 설치 focused #45019234222](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45019234222): Python 3.12/3.14 각각 **50 tests OK(skip 1), FAIL 0**, Native DPS0.
- [v663 전체 Windows 패키징·회귀 #45019234227](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45019234227): Windows3.12/3.14 각각 **325/325 PASS**, 패키징5, 추출 CMD/localhost HTTP3 plans/세션 PASS, DPS Native0. 이전 코드만 포함한 [#45019216083](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45019216083)도 양쪽 Windows SUCCESS이며 **바로 이 run의 3.12 제품 ZIP을 v663 실제 보안 재현 확인에 사용**. 새 runner 소스는 동일, test 파일 2개만 차이.
- **실제 고친 제품 ZIP Windows 통합 [#45019362451](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45019362451) SUCCESS**: 한 개 제품 ZIP의 SHA256 **`cf0289e4a3a0d29f087d264baedf2adc493d24b4d998d08e2cfd4ad19deb0e43`**, 매니페스트 285파일 SHA/CRC, 임시 실험 폴더에서 이전 시즌 JSON 13개 격리, **외부 7z.exe 존재 확인=true**, 실제 Live70961/공식 source 3헤더 검증/공개 asset ZIP+receipt 검증/`py7zr` 설치 PASS. `PUBLIC_SELF_BUILT_BINARY_INSTALLED`, Windows CLI 12.1.5.70961 SHA 기존 검증값, **로컬 인증 POST `/simc-connection/confirm` 실제 실행 및 저장된 연결 GET 재열람 PASS**. CLI 기동 1회(비-DPS), 신규 자체 컴파일0, 최적화 Native DPS0.
- 같은 실제 ZIP에서 **계절 원본 첫 경계** `POST /environment/season-build`를 실행하되, 시험 목적상 `auto_initial_core_build=false`, G/F/O Native 전부 false로 선언해 **의도적으로 신규 원본 G/J/F/O를 완성하지 않음**. API 응답 `source_compilation.status=COLLECTED_COMPILER_INPUTS_PENDING`, `zero_history_build=SOURCE_COLLECTED_GJFO_PENDING_NOT_INSTALLED`, G Native·보석 J·영약 F·기름 O·대표 장비 등 requires 리스트 존재. 이것은 실제 정상 구축 완료/실패 증명이 아닌 *source first boundary* 시험이다. v229 사용자 PC의 최초 오류가 해결됐다는 증거가 아님.
- 제품 ZIP: 위 실사용 버전은 [Windows run #45019216083 artifact #14752684074](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45019216083/artifacts/14752684074) 내 `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip`이며 **이 ZIP 1개만** 필요. 사용자별 SimC ZIP/외부 7z 수동 준비는 새 기본 흐름 아님. Actions artifact 인증/7일 만료 제약은 그대로, 공식 제품 Release 승격 아님.
- v639의 과거 원본 ZIP Native64/95%/저장/재열람과 v660의 초기 Linux/Windows 클린 py7zr 설치 PASS는 **이전 증거 재사용**. v663에서 64 Native나 26개 전문화 전체를 재실행하지 않았다.

## 남은 첫 사용자 PC 경계와 STOP
- **이번 첫 오류 `ARCHIVE_ATTRIBUTES_UNRECOGNIZED`는 안전 경로 우선 선택으로 이번 Windows 재현 조건에서 FIX/PASS**. 실제 개인 PC에서 새 ZIP 클릭 후 완주 여부는 아직 미검증. 원래 개인 PC `V229_SET_BONUS_BUILD_OR_HEADER_MISMATCH`는 source revision·실제 게임빌드·기존 v217 sealed stage 진단 영수증이 없어 원인 미확정; 파서/receipt 임의 편집 금지.
- 다음은 별도 사용자 PC의 최신 **이 단일 ZIP**에서 `SimC 자동 확보·설치` → `SimC 연결 확인·저장` → `시즌 환경 준비`를 확인하고 첫 실패의 `진단 영수증 복사`를 민감정보 제외 전달받는 것. 실제 화면은 UI v653 규격 보존. 그때 최소 G/J/F/O 검증 및 적응형 최적화 연결을 한다. 미확정 항목을 전수 Native 이유로 삼지 않는다.
- `main` 병합, v003 immutable, Project Sources UI, Work OS M0·78개 공식 승격, 주 제품 개발 채팅 소유권 변경 없음. 공식 full_product_e2e=PENDING; 15/78은 제품 진행률 표현에 사용하지 않음.
