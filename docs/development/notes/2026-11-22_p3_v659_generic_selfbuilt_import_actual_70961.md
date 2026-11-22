# 2026-11-22 P3 v659 — 범용 SimC 자체 빌드 ZIP 안전 가져오기

## 목적과 상태
v657 공식 Windows Nightly 여러 후보 탐색 → v658 공식 소스 전체 SHA 고정 Windows CLI 빌드 → v659 **사용자 제공 자체 빌드 Actions ZIP**을 v193의 기존 안전 설치·SHA·롤백 경로로 가져오도록 연결. 특정 70961/6924096은 테스트 영수증에만 존재하고 범용 가져오기 엔진에는 하드코딩되지 않는다.

## 실제 성공한 Windows CLI
- 원본: `simulationcraft/simc` 40자리 Git SHA `6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7`.
- Live 생성 원본: `12.1.5.70961` (client_data_version + item_set_bonus + gem_data + temporary_enchant).
- 공식 CMake/CPack Windows x64 Release GUI OFF로 컴파일한 자체 빌드, [Windows run #45007868837](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45007868837) **SUCCESS**.
- artifact `simc-win64-cli-6924096-12.1.5.70961` / ID `14749195593`; Actions wrapper SHA256 `2058b99125a201b947f2d095426a057179a888e2786fccf47646a92506cfb1fc`. 내부 `simc-1210.01.6924096-win64.7z` 8,832,633 bytes / SHA256 `670ec659a44d8867f46ac267ed1e52db0d02eac8460472bf78aafa286b797c98`; CLI `simc.exe` 121,702,400 bytes / SHA256 `1195a3401a716c9f28b4de113d228cc3a669aebf83c0c47e5989db521d87c3c9`. 실제 CLI display_build=2는 `World of Warcraft 12.1.5.70961 Live` 출력, 비-DPS 기동 정상.
- **공식 SimulationCraft 배포본이 아닌** 공식 소스 기반 자체 빌드이며 전체 26 전문화 DPS, 시즌 G/J/F/O READY를 증명한 것은 아니다.

## v659 연결
- 신규 `runner/v659_simc_self_built_artifact.py`: 로컬 선택 ZIP의 **정확한 4개 멤버**만 허용. ZIP 파일 경로·목록·symlink/암호·크기·CRC·매니페스트 스키마·full SHA·Live 빌드·source_proof 4종·7z magic·7z SHA/바이트·CLI SHA·smoke 출력 일치 확인. 임의 경로 추출 금지, 스트리밍·상한 적용, 사용자가 ZIP을 바꾼 경우 복사 전 digest 재검증.
- `runner/v193_simc_local_updater.py`: 원래 `install`의 안전 7z 목록 검사/CLI PE/해시/임시 staging/원자적 pointer/rollback 사용. 패키지의 exe SHA와 실제 추출된 실행파일 SHA를 검증하고 설치 경로의 실제 `display_build=2` 내장 Live 빌드가 요청한 빌드와 일치해야 활성화. 실패 시 기존 active 불변. 저장된 entry는 `source_revision_full`·`source_game_build`·로컬 ZIP SHA·receipt SHA를 유지.
- `runner/v113_local_web_api.py`: 인증된 loopback POST `/api/v1/simc-updates/install-self-built` (`artifact_path`) 및 Active SimC 작업 중 충돌 차단.
- `runner/webui/index.html`/`app.js`: 기존 v653 CSS/기존 기본 UI 유지, 설정 안에 '자체 빌드 Actions ZIP' 경로와 사용자 확인 버튼만 추가. HTTPS 임의 우회/무인 설치 없음.
- **중요 provenance**: `build_receipt.json`과 artifact ZIP은 사용자가 제공하므로 그 사실만으로 GitHub 출처 인증/공식 서명이 입증되지 않는다. `source_origin_authenticated: false`, `archive_source: USER_SELECTED_SELF_BUILT_RECEIPT_UNAUTHENTICATED` 로 명시. 실제 서버 CI 영수증은 별도 출처 검증에 사용한다.

## 실제 검증
- [v659 offline #45009229475](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45009229475): Python3.12/3.14 **각 35/35 PASS**, 신규 archive malformed/hash/TOCTOU/provenance/CLI mismatch/install/rollback/route linkage와 기존 updater 회귀.
- [Windows v181 #45009262147](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45009262147): Python3.12/3.14 **각 309/309 PASS**, 패키징5 PASS, 추출 후 Windows CMD/localhost HTTP 3 plans PASS, Native DPS0. 새 API token/active job 차단 포함.
- [실제 artifact 재사용 일회성 #45009357618](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45009357618): **SUCCESS**, 기존 70961 컴파일 결과 네 파일을 다운로드하여 v659 ZIP importer가 receipt/.7z SHA 통과. 새 컴파일/Native DPS 0.
- 실제 다운로드된 artifact ZIP을 v659 제품 ZIP에서 꺼낸 동일 importer Python 코드에 다시 넣어 로컬 검사 **PASS**. .7z SHA, CLI SHA, source SHA, 빌드 반환을 확인함.
- 사용자 전달 테스트 ZIP `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA_v659_PC_TEST.zip`: **1,511,828 bytes, SHA256 `17eff529b3c637240c6a438549bc0d5f5c9826a04c40c5a40a274d422feb2f03`**, v181 source product 284/284 SHA·size+ZIP CRC PASS, SimC 바이너리/세션 포함하지 않음. SimC 자체 빌드 ZIP은 별도 사용자 선택.

## 남은 범용 관리자 과제
- 사용자 PC에서 직접 빌드를 실행하거나 장기 토큰을 저장하도록 강요하지 않는다. 공식 Nightly·기존 캐시 우선, 호환 바이너리 공백 시 GitHub Actions 별도 빌드 요청을 현재 격리 브랜치의 **명시적 요청 파일 변경**으로 수행한다. 자동 무인 요청/다운로드는 GitHub 인증 및 artifact 만료/영속 배포 설계 전에는 구현된 것처럼 표시하지 않는다.
- 다음 단계 P3은 (a) 현재 게임 빌드의 실제 바이너리 캐시 재사용 검사, (b) authenticated GitHub artifact 또는 별도 버전별 영구 배포 경로, (c) 검증 완료 ZIP 한 번 클릭 설치, (d) 70961 사용자 PC 실행/최소 Native DPS 확인. 공식 배포와 자체 빌드를 동일 provenance로 합치지 않으며 CI 성공을 시즌 환경 구축 완료로 잘못 표시하지 않는다.
- 기존 main/v003 immutable/Project UI/MAIN-WORK/주 제품 채팅의 소유권·v653 디자인·G/J/F/O/95% 통계·DPS 캐시 identity 불변.
