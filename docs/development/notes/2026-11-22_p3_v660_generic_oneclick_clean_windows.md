# 2026-11-22 — v660 범용 SimC 자동 확보·제로베이스 Windows 검증

## 제품 범위
v657 공식 Nightly 다중 후보·소스 원본 검증, v658 원본 SHA 고정 Windows CLI CMake/CPack 자체 빌드, v659 ZIP 안전 설치/롤백 기능을 보존하고, **v660 제품 한 개만으로 바이너리 검색→다운로드→검증→설치→캐시 재사용**을 연결한다. 코드의 게임 빌드/revision은 동적으로 얻으며 특정 70961 SHA는 시험·1회 공개 캐시 생성에서만 사용한다. 26개 DPS/SimC DPS 목적함수, 시즌 G/J/F/O, 캐시·세션·95% 통계·v653 CSS를 변경하지 않는다.

## 구현
- `runner/v660_simc_one_click_provision.py`: 명시적 사용자 액션 `prepare_one_click`, 실제 KR Live 관측→현재 관리 바이너리 SHA와 CLI 내장 빌드 검증 후 재사용→공식 호환 Nightly 검증·설치→외부 인증 없이 읽을 수 있는 GitHub 공개 **자체 빌드 시험용 prerelease** 탐색→공식 SimulationCraft 원본 SHA의 3헤더 일치→GitHub Release 자산 SHA256 검증 HTTPS 다운로드→기존 v659 ZIP 영수증·archive/CLI SHA 및 v193 안전 설치·롤백. 공식/자체 빌드 provenance를 별도로 보존하고 한 번의 사용자 승인 외 자동 설치하지 않는다.
- 새 인증된 로컬 API `POST /api/v1/simc-updates/prepare-auto`; 실행 중 SimC 작업이 있으면 차단. 기존 token/origin/loopback/JSON gate 유지.
- 기존 설정의 `SimC 자동 확보·설치` 버튼 추가. 수동 `.7z` 및 수동 자체 빌드 ZIP 설치 유지.
- `requirements-web.txt`의 `py7zr>=1.1.4,<1.2`, `START_HERE_AUTO_SETUP_AND_RUN.bat`에서 관리 가상환경 자동 준비. 외부 7z.exe가 있다면 기존 경로 유지, 없으면 **안전 메타데이터 검사 후 `simc.exe`만 추출**하는 Python fallback. 7z 파일 수·크기·중복·상대 경로·심볼릭 링크·암호화 차단, PE x64 검사.
- 공개 캐시가 없어 원격 Windows CLI를 신규 빌드해야 하는 상황에서는 **`SOURCE_BUILD_REQUIRES_REMOTE_BUILDER`**로 정확히 보고한다. Github 일반 사용자 익명 workflow_dispatch가 불가능하므로 무인 원격 컴파일을 수행하지 않는다. 사용자 GitHub 토큰·개인 비밀키·C++ BuildTools를 요구하거나 출처 없는 바이너리를 허용하지 않는다.

## 실제 Live Windows 증거
- 소스 원본 `simulationcraft/simc` full Git SHA `6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7`, Live `12.1.5.70961`, 실행파일 SHA256 `1195a3401a716c9f28b4de113d228cc3a669aebf83c0c47e5989db521d87c3c9`.
- isolated workflow [#45012615920](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45012615920)에서 기존 검증 artifact를 **신규 컴파일 없이** GitHub 공개 **EXPERIMENTAL prerelease**로 등록. tag `simc-cli-source-6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7`, asset `simc-win64-cli-6924096-12.1.5.70961.zip`, 8,834,290 bytes, SHA256 `8f94209f1b7013da23fca47ada972630d18a371abd0e3d86f491bbad27dec2fd`. **공식 SimC 배포본·제품 공식 승격 아님**.
- [v660 offline #45012483521](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45012483521): Python3.12/3.14 각각 **48/48 PASS**, 외부 7z 없을 때 py7zr 보안·PE 및 official/cache/release/no broker 회귀. Native DPS0.
- [실제 CPack Python-only 압축 해제 #45012562682](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45012562682): **SUCCESS**, real `.7z`→`simc.exe` 추출 후 원래 exe SHA 일치. Native0.
- [실제 Windows 제로베이스 #45012696519](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45012696519): **SUCCESS**. Windows2022 최초 관리 폴더/SimC 없음, 외부 7-Zip 탐색 강제로 OFF, py7zr 자동 준비, **실제 KR Live BPSV 70961**, 검증된 public prerelease 자동 발견→실제 HTTPS 다운로드→7z 추출→SHA/CLI 내장 빌드→설치, 첫 `PUBLIC_SELF_BUILT_BINARY_INSTALLED`, 두 번째 `ALREADY_COMPATIBLE_MANAGED`로 중복 다운로드·컴파일 없이 재사용, 원자 롤백. DPS Native0.
- Windows 베타 제품 ZIP 재패키징 및 사용자 브라우저 클릭+로컬 HTTP의 완전 실제 통합 테스트는 별도 검증 대상으로 관리한다. 동결 CSS 손대지 않았고, user-facing wording에 Python 7z fallback 반영.

## 남은 설계·권한 경계
사용자 PC에 공개 배포·캐시조차 없을 때 **신규 원격 컴파일을 자동 요청하는 중앙 신뢰 브로커는 미구현**. GitHub Actions의 default-branch schedule 또는 인증된 중앙 broker 등 사용자 별도 권한/배포 구성이 필요하며 main 병합/Project UI/공식 Work OS나 제품 승격으로 간주하지 않는다. CI 오프라인 통과는 시즌 GJFO 준비나 26 전문화 DPS 보증이 아니다. 업데이트 조회 시 불필요한 신규 Native 호출·전 전문화 컴파일 없음.
