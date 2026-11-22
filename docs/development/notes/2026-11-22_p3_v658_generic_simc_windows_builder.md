# 2026-11-22 P3 v658 — 범용 SimC Windows x64 CLI 자체 빌드 경로

## 범위 및 위치
격리 브랜치 probe/chat-cache-v035-20261024 전용. main, v003, Project UI, 기존 주 개발 채팅의 소유권, v653 동결 디자인, 최적화·세션·환경 G/J/F/O, 기존 v193 안전 설치/롤백은 변경하지 않는다.

## 설계
v657은 공식 패키지를 최대 12개 확인하고, 현재 KR Live와 생성 소스가 맞더라도 패키지가 없다면 다운로드/설치를 제공하지 않는 구조다. v658은 그런 경우를 위한 **독립적, 명시적 빌드** 경로다.

- 입력은 build_requests/simc_win64_cli.json 문서의 정확한 upstream Git 40자리 SHA, game_build, windows-x64-cli, official_binary_unavailable. 70961 및 9933ffb는 빌더 코드·워크플로에 하드코딩하지 않는다.
- GitHub Actions의 Windows 2022에서 공식 simulationcraft/simc를 전체 SHA로 checkout한다. client_data_version.inc 및 item_set_bonus.inc, gem_data.inc, temporary_enchant.inc 4개 원본 일치를 확인하고, 공식 CMake/Ninja/CPack을 통해 Release, BUILD_GUI=OFF, BUILD_TESTING=OFF, IPO=ON으로 1개의 Windows CLI 패키지를 만든다.
- 결과 .7z / 소스 영수증 / 패키지 SHA·exe SHA / display_build=2 비-DPS smoke를 GitHub Actions artifact에 14일 보관한다. 컴파일은 전문화별로 수행하지 않는다.
- workflow_dispatch는 파일이 default branch에 존재해야 실행 가능하므로, 사용자 별도 승인 없이 main에 추가하지 않는다. 격리 브랜치에서 **빌드 요청 파일 변경(push)** 으로만 실행한다. 기본 사용자 PC는 컴파일러가 필요 없다.
- package receipt는 자체 컴파일본임을 분명히 표시하고 공식 바이너리로 위장하지 않는다. 표시된 embedded build가 없으면 source-only 확인과 구분하고, 불일치가 관측되면 차단한다.
- GitHub Actions artifact 다운로드에는 GitHub 인증과 만료 제약이 있다. 사용자 PC 업데이트 버튼에서 자동 빌드를 지시하거나 private artifact를 토큰 없이 다운로드하는 기능은 아직 미구현이다. 그 경계는 후속 P3에서 결정한다.

## 검증
v658 신규 offline 계약 시험은 request strictness/원본 SHA·4종 파일/Windows x64 PE·SHA/실행 smoke/워크플로 범용성. 실제 Windows CPack 빌드 및 70961 실행은 별도 요청 CI 결과로 판정한다. Native 26개 전수 재실행 금지. 소스 일치 및 CLI 실행이 시즌 READY/GJFO 또는 전체 26 DPS 검증을 의미하지 않는다.

## 첫 실측 증거 및 상태 (2026-11-22)
- source revision `6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7`은 실제 official GitHub의 `client_data_version.inc` 및 generated 헤더 3종 모두 Live `12.1.5.70961`를 포함한다.
- 요청 commit `e6052ed98d9ae60ec09d86a27bcdfa0bf599f6d6` → [run #45007770060](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45007770060): Windows 소스 체크아웃 성공, CRLF-only 포맷 오탐으로 source proof FAIL, 컴파일 전 종료. v658 스크립트만 CRLF·LF 양쪽을 동일하게 인식하도록 수정, 회귀 테스트 추가.
- [v658 offline #45007898407](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45007898407): Python3.12/3.14 양쪽 5 PASS.
- [Windows run #45007868837](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45007868837): 동일 pinned SHA와 game build의 재요청, source proof·CMake 구성은 PASS, Windows CLI Release 컴파일·CPack 진행 중인 시점의 관측. 결과 미완료를 PASS로 표시하지 않는다.
- 업무상 본 소스 전용 CI 구성을 제품의 자동 업데이트 완료로 주장하지 않으며, 사용자가 컴파일 도구를 설치해야 한다고 요구하지 않는다. 실 다운로드 자동화는 장기 보존·인증·배포 경로가 정해진 뒤 연결할 별도 범위다.
