# P3 v640 — 사용자 Windows 첫 실행 의존성 축소·배포 ZIP·동의형 설치 인수

**검증일:** 2026-11-20 KST. **소유권/권한:** 격리 브랜치 전용; 제품 SimC·후보탐색·예산·UI 실행기·main·v003 변경 없음. 기존 [v639 ZIP Native64 최종 결과/재열람](2026-11-19_p3-v639_published_zip_70961_final_result_restore.md) PASS를 재사용해 Native 재실행 0.

## 1. 최초 사용자 설치에서 확인한 실제 결손과 최소 수정

- **기존 `requirements-web.txt`:** 사용자에게 설치하는 런타임 요구사항이 `fastapi, uvicorn, httpx2`였다. 실제 원본 282파일 ZIP의 모든 Python import를 확인했을 때 런타임 `v113_local_web_api.py`만 FastAPI·Uvicorn·Pydantic을 import하며, **`httpx2` import는 0개**였다. 오프라인 FastAPI/Starlette TestClient용 HTTP 클라이언트는 이미 별도 `requirements-web-test.txt`에 `httpx>=0.27,<1.0`으로 포함. 따라서 사용자용 **불필요한 `httpx2` 설치를 제거**하고 테스트용 httpx는 보존. 실제 웹 서버 사용 기능/의존성 필요 라이브러리 삭제 아님; Pydantic은 FastAPI 종속으로 설치.
- **Windows 동의 검증 스크립트:** 기존 `p1_v573`·`p1_v575`의 fresh venv 검증이 테스트 전용 `httpx2` import를 필수로 오인하고 있어, **실제 사용 서버 라이브러리 `fastapi,uvicorn,pydantic` 확인**으로 국소 변경. 사용자가 N을 눌렀을 때 설치 금지, Y일 때만 사용자 로컬 venv, 재실행 재설치 없음, stale PATH에서 검증된 Python 선택 경계는 유지.
- **원인 재발 방지:** `tests/test_v181_windows_beta_package_offline.py`에 사용자 런타임·별도 테스트 의존성 분리 검사를 추가. `.github/workflows/v181_windows_beta_packaging.yml`의 기존 ZIP 변경감시 목록에 **`requirements-web.txt`, `requirements-web-test.txt`, `START_HERE_AUTO_SETUP_AND_RUN.bat`** 추가. 별도 파일 복사/새 패키저를 만들지 않고 **기존 `v181.select()` 단일 목록** 그대로.
- **사용자 실제 안내:** `WINDOWS_BETA_START_HERE.md`의 첫 실행에 기존 ZIP v638 Native4와 v639 Native64 결과 실증을 명시하고, Python 설치·Y/N 동의·로컬 8765 포트·SimC 실행파일 및 KR 빌드/API 키 미확정 시 대처를 최소 추가. **개인 PC 설치 확인·전 전문화 완료로 승격하지 않음**.

## 2. 실제 새 ZIP·Windows Actions 증거

- [**Windows v181 Actions #44635274309**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44635274309) **3.12/3.14 모두 SUCCESS**. 각 회귀 **5 tests/0 FAIL** (단일 패키저), 기존 로컬 서버/세션/보안 **270 tests/0 FAIL**, 실제 Windows 압축해제 CMD·127.0.0.1 HTTP·3개 계획·인증정보 로컬 보안 동작 PASS; 이 과정 Native0. 기존 source `v213`는 `automatic_ui_promotion=false` 및 native0의 **역사 미승인 자료**이며 현재 70961 설치라고 오인하지 않음.
- [실제 새 ZIP artifact **#14583976250**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44635274309/artifacts/14583976250), **원본 내부** `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip` SHA256 `db6d030832b1fcb852c56b4002774d9416c810d2c5582fe67a72c4491e3086c2`, 282개 실제 제품 파일·283 ZIP 엔트리(매니페스트 포함); 내부 **282/282 SHA 일치**, `requirements-web.txt`에 `fastapi,uvicorn`만, 최신 안내 포함, SimC 실행파일·개인 세션·키 미포함.
- **첫 v640 단발 시험 [#44635699547](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44635699547) FAIL·Native0:** 검증 workflow가 현재 원본 fixture를 주입하지 않은 checkout에서 이미 v181 양 버전 PASS한 **전체 패키저 검증**을 중복 재호출해 `V181_MINIMUM_PRODUCT_RUNTIME_FILES_MISSING`. **실제 ZIP/제품 장애 아님.** 실패지점에서 즉시 STOP해 기존 v181 전체 PASS 재사용, 별도의 v640은 setup 관련 **2개 unit test만** 수행하도록 scope를 교정.
- [**최종 Windows v640 Actions #44635822469 SUCCESS**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44635822469), [실제 compact artifact **#14584826071**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44635822469/artifacts/14584826071), `V573_WINDOWS_COLD_SETUP_EXPLICIT_CONSENT_COMPACT.json` SHA256 `f1ea4507cc9a3a32ce90a903495ca36bc8cca28b83aaa681a26058d4904b5cc8`; receipt `status=PASS_REAL_WINDOWS_ZIP_COLD_WEB_DEPENDENCY_CONSENT_AND_FIRST_CHROME_NATIVE_ZERO` 및 source ZIP SHA **위와 동일**. 실제 원본 ZIP 압축해제, 기존 Python3.12+ 감지, 사용자 **N→venv 미생성**, **Y→완전 신규 로컬 user `%LOCALAPPDATA%` 격리 venv+실제 pip 설치**, 두번째 `--check` 재설치/상태 변경 0, 초기 Chrome 26 DPS·ZERO-SOURCE 버튼 표시, **자동 시즌 수집/Native0**, 개인 세션 변경0. 단, 실제 `winget`로 Python 자체를 새로 설치한 시험도, 사용자 개인 PC 시험도 아님.
- v575 표준 Python3.12 경로에서 stale PATH 복구 Y/N·실 venv 구축은 앞선 [Windows #44088065693](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44088065693) PASS **역사 재사용**, 이번 턴 재실행 0. v574 실제 winget 설치는 본래 harmless stub dryrun만 증거이며 실 설치 성공을 주장하지 않음.

## 3. 사용자 배포 인수와 다음 경계

- **이번의 구현/검증 완료:** 불필요 런타임 package 제거, CI source/installer 변경 자동 감시, Windows3.12·3.14 ZIP/로컬HTTP/270회귀 PASS, 새 ZIP에서 실제 사용자 동의 N/Y·신규 최소 웹 venv·재기동·첫 Chrome PASS. **새 Native0, 컴파일0, 시즌 수집0, 제품 최적화 코드 변경0**, 기존 v638/v639 제품 계산 증거 그대로 유효하되 **새 ZIP의 안내와 의존성만 달라서** SimC64 재실행 불필요.
- **아직 남은 개인 PC/최종 릴리스 범위:** 실제 소비자 PC의 다양한 정책에서 winget 설치, 자체 설치형 EXE 또는 SimC 동봉, API 키 미보유 사용자 시나리오, 시즌 변경과 전체 26개 DPS 및 모든 사용 선택. 현재 ZIP은 **Python 소스 베타**이며 독립 EXE가 아니다. 사용자가 별도 설치·API 동의를 할 수 있도록 안내. 기존 캐시·세션 디렉터리 삭제 금지.
- **STOP:** 동일 ZIP 설치 동의·버전 시험을 추가 반복하지 말고 베타 사용자 피드백에서 첫 장애가 재현될 때만 국소 수정. **공식 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10` 그대로**, main/v003/Project UI/Work OS/주 제품 개발 소유권 불변.
