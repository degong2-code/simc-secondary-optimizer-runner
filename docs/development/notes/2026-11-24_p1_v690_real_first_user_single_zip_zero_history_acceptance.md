# v690 — Windows에서 단일 ZIP, 빈 사용자 환경, 최초 UI·시즌·실제 SimC로 이어지는 제로베이스 시험

2026-11-24. 최신 사용자 결정: '내 환경이라고 생각하고 제로베이스 시험' 요구. 격리 브랜치 기준 `9107504f5fc339d06cd30a0b8d5e47878a939bee`.

이전 증거: v640(실 ZIP 첫 웹 의존성·사용자 동의), v570(빈 세션→Chrome 시즌 구축→생존 사냥꾼 DPS64), v639(추출 ZIP→70961 Chrome64·결과 재열람), v689(70961 징벌 성기사+Bloo­ming Feast API→Native6/DPS SEM95) **각각 다른 실행**이다. 이를 한 번의 사용자 초기 설치 흐름으로 합칠 수 없다.

이번 수락 실험은 기존 `v181`의 **현재 HEAD 동일 소스 ZIP**을 만들고 `v573`의 실제 Windows BAT/venv 동의 취소·승인·pip 설치·Chrome 첫 화면을 재사용한다. 추출 뒤 원본 역사 데이터는 격리(이전 시즌 값 사용 금지), 사용자 HOME/LOCALAPPDATA/run/managed-SimC 비어 있어야 한다. v573의 신규 opt-in before/continue hooks 기본값 None으로 역사 동작/회귀 불변.

같은 실행에서 신규 브라우저가 UI의 **Blizzard/WCL 인증정보**를 사용자처럼 등록하며 비밀키를 로그·보고서·ZIP에 포함하지 않는다. Windows 공개 SimC **'자동 확보·설치'** 버튼을 실제 클릭하며 **기존 70961 바이너리를 주입하지 않는다.** 설치가 되지 않으면 `PENDING_PUBLIC_SIMC_NOT_INSTALLABLE`로 정확히 중단한다. 성공한 경우 **흑마법사/파괴**로 앞선 두 전문화와 다른 대상을 선택하고, 기존 원래 첫 클릭 `v113/v216/v217/v212`로 빌드 자동 확인 → 실제 같은 SHA 설치 → 원래 사용자 목록 장신구 두 개 선택 → 원래 최적화 버튼을 사용한다. 정상 조건에선 기존 사용자 장기 적응형 Native64, DPS/SEM/95% UI 표시까지 같은 창에서 확인. 새로운 Native/효과 엔진·모의 HTTP·수동 예산·과거 GJFO 값 주입 없음.

**CI에서 미리 제공되는 전제:** Windows 2022, Python3.12/Chrome, Github Actions Secret에 적법하게 사전 저장된 소스 API 인증정보와 인터넷 연결. 이는 개인 PC 설치(winget·Windows 권한·가정 네트워크) 증명은 아님. 바이너리는 자동 다운로드가 되는 경우에 한해서만. 새 게임 빌드 원본 G/J/F/O가 미검증이면 정상 READY로 승격하지 않고 원래 첫 차단을 기록. 실패 시 동일 시즌 원본/Native를 무조건 반복하지 않으며 첫 원인만 수정한다.

검증 영수증: ZIP 파일 SHA/동의 검증은 v573의 기존 bounded 리포트; v690은 신규 사용자 원본 세션과 실제 UI 상태·선택 전문화·SHA/B/T·최종 화면 DPS/SEM/95%에 한해 기록. 비밀키/세션 개인 정보/소스 원본/프로필 전체 절대 수집하지 않음. 실제 Native 결과는 단 하나의 최초 성공 시나리오이며 새 시즌/26전문화 완전 범용성 증명 아님. `15/78 COMPLETE`와 `full_product_e2e=PENDING`, 개인 PC 시험 보류 및 main/v003/v016/Project UI/Work OS 권한 불변.

**실행 증거가 없으면 어떤 PASS도 주장하지 않는다.**

## 첫 실제 Windows #45230565019 — 패키징 선행 차단, 원본/Native 0

[GitHub Actions #45230565019](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45230565019)는 새 ZIP 빌드 전 `V181_MINIMUM_PRODUCT_RUNTIME_FILES_MISSING`로 실패했다. `v181_windows_beta_packager.py`가 항상 `data/current_season_source_to_catalog.json`을 과거 packaging source metadata로 요구하지만 새 체크아웃에는 해당 바이너리/과거 소스가 없다. 다른 런타임 모듈은 존재함을 repo 파일 목록으로 확인. 이번 실행은 사용자 화면·Native 이전에 종료되어 *사용자 제로베이스 PASS가 아니고* Native0, 소스 수집0.

**최소 원래 계약 재사용:** 기존 정상 `v181_windows_beta_packaging.yml`과 동일하게 과거 **봉인된 v213 read-only source artifact** #13104842881 (Actions #41360273361)를 ZIP **메타데이터 생성 단계에만** 바인딩한다. 압축 해제 직후 사용자 앱이 시작되기 **전에** v690이 해당 역사 소스 파일을 별도 격리 폴더로 이동/삭제하여 최초 시즌 빌드와 세션이 과거 내용을 소비하지 못하게 한다. 사용자 준비물도, 새 시즌 원본·G/J/F/O 인증도 아니며 역사 70783(?) 수치를 새 시즌으로 복제하지 않는다. 현재 `v181` 패키저 자체의 역사 메타데이터 의존성은 범용 패키지 설계 과제로 명시적으로 남긴다(한 번의 시즌 Build 실행 경로와 분리). 신규 원본 Native 호출은 아직 없고 수정 후 실제 1회 Actions 결과가 나와야 통합 성공 여부를 판정한다.
