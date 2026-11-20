# P3 v642 — SimulationCraft 공식 업데이트 관리자 정확성·효율·실행 안전성 수정

**2026-11-20 KST · 격리 브랜치만 변경 · 제품 실행 엔진/예산/세션/캐시 불변 · 제품 SimC DPS Native 재시험 없음**

## 사용자 흐름·원인 및 수정

실제 사용: 로컬 BAT → 브라우저 설정 → SimulationCraft 연결 및 업데이트 → **사용자가 명시적으로** 공식 버전 조회/설치 또는 로컬 .7z 선택 → 새 바이너리 활성화 후 미래 목표 CHMV 최적화 실행. 설치 전 SimC 원본은 별도로 보존하며, 버전 변경 시 새 세션·DPS 캐시 식별자를 사용한다.

1. **공식 주소 정확화:** 기존 v193 `https://download.simulationcraft.org/nightly/`(단수)와 단수 호스트 allowlist는 [SimC 공식 다운로드 페이지](https://www.simulationcraft.org/download.html)의 `https://downloads.simulationcraft.org/nightly/`(복수)와 불일치. `BASE`, 후보 URL, HTML fetch 최종 URL, .7z 다운로드 리다이렉트 검사에서 복수 공식 호스트로 통일. HTTPS/TLS 검사와 동일 출처 필수, 임의 도메인·쿼리·경로 거부는 유지. **실제 이번 Windows CI에서 외부 공식 서버로 직접 다운로드했거나 현재 서버 TLS 장애가 해소됐다고 주장하지 않는다.**
2. **설치 검증:** ZIP의 합성 PE 여부만 검사하던 한계를 보완하여 실제 설치 위치 `simc.exe`를 `display_build=2`로 20초 제한 실행. upstream [simulationcraft/simc engine/sc_main.cpp](https://github.com/simulationcraft/simc/blob/midnight/engine/sc_main.cpp)에서 이 설정은 버전·빌드 출력 뒤 `execute()` 이전 정상 종료. exit code 0, 합리적 출력 길이·`SimulationCraft` 문자열 확인 후에만 `installed.json` 원자적 active pointer 갱신. 실행 실패/타임아웃/DLL 불능 때 fail-closed, **이전에 활성화된 버전·수동 경로/세션·캐시 변경 금지**. 실패로 신규 생성된 관리 version 폴더만 정리; 이미 존재하던 버전은 삭제하지 않는다. 이는 **DPS 계산이 아닌 실제 CLI 프로세스 1회**를 새 설치 때 수행하는 경로다.
3. **중복 비용 최소화:** 최근 공식 후보 filename과 현재 활성 관리 version의 filename·`OFFICIAL_HTTPS_NIGHTLY` 출처가 동일하고 파일 SHA가 정상인 경우 다운로드·압축 해제·CLI 검사를 건너뛰고 `MANAGED_SIMC_ALREADY_CURRENT` 반환. 포인터 재작성 없음. 임의로 이름을 바꾼 **사용자 로컬 .7z에는 이 생략을 적용하지 않음**. UI는 이미 설치됨·신규 파일 변경 없음이라고 별도 표시.
4. **외부 조회 절제:** 공식 인덱스 실패 후에만 공식 GitHub Actions 공개 메타데이터 조회. 최근 최대 4개 workflow run을 확인하여 최악의 경우 초기 목록1+상세4=**5 HTTP metadata requests**로 축소(이전 최대9). GitHub ZIP 자동 다운로드/알려지지 않은 URL 자동 실행 없음. 검색 범위 감소로 후보가 없으면 수동 다운로드 링크를 안내한다.
5. **계산 중 읽기 전용 상태:** 실행 중인 SimC 작업을 보호하는 409 차단은 `POST check/install/install-local/rollback`에서 유지. 인증된 `GET /api/v1/simc-updates/status`는 로컬 상태만 읽으므로 실행 중에도 200 허용, 외부 fetch나 포인터 변경 없음.
6. **호출 수 보고:** 실제 새 설치 `native_calls_now=1`, `non_dps_cli_smoke_calls=1`, `dps_native_calls_now=0`; 동일 공식 revision 재사용 `native_calls_now=0`, `non_dps_cli_smoke_calls=0`. 이 값은 **실제 사용자 설치 경로에서의 예정 동작을 코드·모의 회귀로 확인한 계약**이며 이번 CI에서 실제 Nightly CLI를 실행했다는 뜻은 아니다.
7. **테스트 의존성 분리:** 일부 Linux Starlette TestClient에서 신규 `httpx2` 필요가 확인되어 `requirements-web-test.txt`에만 `httpx2>=2.13,<3.0` 추가, v388 offline CI가 이 시험용 의존성을 사용하도록 수정. 사용자 서버 런타임 `requirements-web.txt`에는 `httpx`/`httpx2`를 추가하지 않았다.

## 실제 CI·비용

- 완료 소스 기준 [Windows package + loopback HTTP #44651392153](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44651392153) **Python 3.12/3.14 양쪽 SUCCESS**, 각각 기존 패키징5 PASS + 웹·세션·보안·업데이트 **277 PASS**, 실제 압축 해제/로컬 웹·3 plans PASS. 기존 v181 workflow에서 simc 바이너리는 포함되지 않으며 신규 Native0.
- [v388 Linux test-dependency correction #44650770729](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44650770729) SUCCESS; [v113 local web #44650770773](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44650770773) Linux 3.12/Windows3.14 SUCCESS; [v401 formal completion policy #44651392169](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44651392169) SUCCESS.
- 실제 제품 함수를 호출하는 유닛 테스트에서 공식 host/허용 범위, CLI `display_build=2` 호출/exit/출력/timeout/OSError, 설치 전 포인터 보존·실패 orphan 삭제, 이미 정상 공식 설치된 같은 revision의 downloader0/probe0, ZIP 안전·PE64/이전 버전 복원, API 403/422/계산 중 GET200·mutation409을 확인. **실제 Windows 공식 Nightly 원본 .7z 다운로드·압축 해제 후 실 simc.exe 기동 시험은 이번 Actions에서 실행하지 않았다.** 기존 합성 PE 테스트를 실 SimC 관측으로 둔갑시키지 않는다.
- 현재 배포 후보 [artifact #14590972200](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44651392153/artifacts/14590972200) 내부 `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip` SHA256 **`754bb9448524bed3e32e72d1e4639315930d31fa3eacff9e118be448009216e3`**. 282 source files+manifest 1=283 ZIP entries, **282/282 원본 SHA 재대조 PASS**, 실제 `runner/v193` 변경사항 포함. 원본 역사적 70575 source `automatic_ui_promotion=false`; SimC 실행파일·개인 키·사용자 세션·Native 데이터 포함하지 않음.
- 추가 원본 시즌 Blizzard/WCL/DB2 조회0, 새 실제 DPS Native0, 기존 Native64 재실행0, SimC 컴파일0. 기존 v638 E+ Native4/v639 E0 Native64 실증은 **계산 코드·예산/프로필/세션 변경하지 않은 범위**로 재사용. 새로운 업데이트 바이너리의 정확한 실제 DPS 결과는 별도 사용자 관측 전 미확정.

## 종료 경계·후속

현재 v642는 **구조·결정론적 안전성·Windows 배포 검증 PASS**, 첫 실사용 PC의 공식 서버 HTTPS 접속, 진짜 현재 Nightly 패키지 구성, 실제 7-Zip·CLI 기동, 사용자 기업망/TLS/백신 조건은 PENDING. 인증서 우회, 자동 설치 동의, 전체 시즌 데이터·전 26 DPS Native 재검증으로 확대하지 않는다. 오래된 관리 버전의 자동 삭제는 재현 가능성과 복원/사용자 세션을 위해 **도입하지 않음**. 선택적 수동 정리는 별도 명시 요청/공간 부족 근거가 있을 때 검토.

공식 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10` 불변. 주 제품 채팅 소유권, main/v003 불변, Project UI·Work OS·공식 승격 권한 불변.
