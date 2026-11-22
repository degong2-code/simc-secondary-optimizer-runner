# P3 v655 — KR Live 빌드 일치형 SimC 다운로드 안내 (2026-11-22)

## 사용자 실증과 요구
- 사용자 PC에서 v653 UI 변경 확인, v654 `.7z` 설치 `ARCHIVE_LINK_OR_ENCRYPTION_REFUSED` 후 read-only 속성 오탐 수정. 그러나 `0d19401` Windows nightly가 내장한 Live 70783은 당시 KR Live 70961과 불일치할 수 있으므로 **단지 설치 성공만으로 시즌 G/J/F/O 빌드가 READY가 되지 않음**.
- 최신 사용자 지시: 자동 설치 전 현재 KR Live 빌드와 SimC 생성 데이터 빌드를 비교하고, **일치가 확인된 공식 Windows SimC 다운로드 링크**를 보여주되, 확인 불가 시 거짓 최신/일치 링크를 만들어내지 않는다. AI 런타임 의존성 0 유지.

## 근거와 데이터 정체성
- 공식 KR Retail 게임 버전: 기존 `runner/v289_retail_live_build_source.py::discover(region="KR")`가 공개 Blizzard BPSV `https://us.version.battle.net/wow/versions`의 `Region/VersionsName/BuildId` 일치값을 검증하여 반환한다. 매번 사용자가 명시적으로 버튼을 누를 때만 호출한다. 외부 TLS fail closed; 출처와 SHA 반환. 조회 실패 시 임의의 게임 빌드를 추정하지 않는다.
- official Windows Nightly: 기존 `v193` HTTPS 호스트 `downloads.simulationcraft.org/nightly/` 목록의 허용 형식 .7z filename에서 Git revision을 추출한다. GitHub `simc-publish` Actions artifact는 실제 Git revision/게임 빌드가 확인되지 않으면 **일치 다운로드라고 표시하지 않는다**. 전체 Actions 실패라도 Win64 job은 성공할 수 있으며, GitHub 로그인 후 run Artifacts를 확인하는 **미검증 수동 기록 링크**만 유지.
- pinned git source triple: 공식 `raw.githubusercontent.com/simulationcraft/simc/<revision>/engine/dbc/generated/{item_set_bonus.inc,gem_data.inc,temporary_enchant.inc}`의 첫 헤더를 HTTPS 동일 URL·동일 호스트·허용 short SHA·예상 접두사로 각각 검증. 3종의 생성 데이터 빌드가 모두 정확히 같은 경우에만 source_build 관측. 이는 **소스 커밋의 헤더 정합성**이며 해당 .7z executable 내장 데이터, SimC 프로필/APL, 26개 DPS 실제 작동의 독립 보증이 아니다. 원본 확인 실패·빌드 불일치 시 신규 일치 링크/자동 설치 후보를 제공하지 않는다.
- 2026-11-22 웹 원본 비교 기준: 공개 Retail 빌드 `12.1.5.70961` 관측, 소스 `0d19401`의 Live 생성헤더 `70783`, `9933ffb`의 Live 생성헤더 `70961`. 단, **9933ffb 소스 Git commit 링크는 컴파일 완료된 Windows 바이너리 다운로드 링크가 아니다**. 해당 정확 revision의 공개 Windows 실행파일 배포 검증은 아직 없다.

## 코드 연결
1. `runner/v193_simc_local_updater.py`: **기존 `check()` 계약 불변** (기존 단독 호출과 테스트 보존), 별도 `check_for_retail_compatibility()`가 Blizzard 공개 KR 빌드→기존 공식 목록 후보→GitHub 3종 헤더 순서로 검사. 3종 소스 일치인 경우에도 `SOURCE_BUILD_MATCHED_BINARY_UNVERIFIED`로 명시. 불일치 `SIMC_SOURCE_BUILD_MISMATCH`, 현재 빌드 미확정 `LIVE_BUILD_UNKNOWN`, 원본 미확정 `SIMC_SOURCE_BUILD_UNVERIFIED`, 다운로드 미확정 `NO_VERIFIED_MATCHING_DOWNLOAD`. `season_ready=false`, `binary_embedded_build_verified=false`, `dps_native_calls_now=0`. 링크는 공식 목록에서 실제 제공된 HTTPS URL만 재사용하고 가공·추정하지 않는다.
2. 동시성 보완: `check(retain_offer=False)`로 기존 후보가 출처 검사 중 일시적으로 설치 대상으로 노출되지 않게 함. 원본·KR 비교 **모두 성공한 후** 검증된 offer를 단일 lock 구역에서 활성화한다. 테스트/호출자가 쓰는 이전 `check()` 기본 계약은 보존.
3. `runner/v113_local_web_api.py`: 원래 `POST /api/v1/simc-updates/check` 원형을 변경하지 않고, 같은 loopback token/Origin/job-active 보호를 재사용하는 **명시 전용** `POST /api/v1/simc-updates/check-compatible` 추가. 기존 v645 저장 SimC `observed_game_build`는 **지난 관측값**임을 구분해서 보여주며 파일 경로·비밀정보 노출 안 함. 진짜 현재 CLI 기동/출처 인증으로 과장하지 않음.
4. `runner/webui/app.js`: 유저가 '공식 업데이트 확인' 클릭 시 새 API 사용. KR Live·후보 원본 3종·관측된 지난 SimC를 비교해 표시. source match인 경우에만 기존 official index 직접 `.7z` URL 링크와 설치 버튼. no-match/불확실은 안내와 공식 GitHub run 페이지/수동 다운로드 링크만 유지. `index.html`·`styles.css` 레이아웃은 **v653 그대로**.
5. 기존 v193 설치 안전성 (TLS 검증, allowlist, .7z 경로/크기/PE64, 실행 `display_build=2`, atomic pointer, 이전 바이너리·캐시 보존, .7z 안전속성 v654)과 P1/SimC runtime/Native/계산 코드는 변하지 않음.

## 변경 코드 검증 및 패키지
- v655 UI+API+업데이터 **정확한 Git blob SHA1 대조**:
  - `runner/v193_simc_local_updater.py`: `2dd28801edaaa26b7ea015426b948731b7ad5312`.
  - `runner/v113_local_web_api.py`: `c0112c3fc0909c567eb04a483241d54dfb05d9b2`.
  - `runner/webui/app.js`: `b6d9522ae80e4f2732a4cb8e76216969e2f2301a`.
  - unchanged v653 `runner/webui/styles.css`: `47e3ed5b9dd7d704106d761e19a70c3d38e89766`; `index.html`: `d78907fef5677476e749c6cbe78d051daae7fe32`.
- 실제 변경 소스와 동일 바이트를 `v654` PC ZIP에 적용하여 **오프라인 focused 6/6 PASS**, Python py_compile PASS, Node --check PASS; 추가 FastAPI TestClient 인증된 신규 POST 200·미인증 POST 403·local health/HTML/JS/CSS 200 PASS. Github `tests/test_v193_simc_local_updater.py`에 해당 build match/mismatch/unknown/raw redirect/후보 동시성 회귀 테스트 추가. 오프라인 모의 원본/HTTP 테스트이므로 실제 KR BPSV 외부 URL, 실제 GitHub raw HTTPS, 실제 .7z 최신 Windows binary를 다운로드·실행했다는 증거는 아님.
- v655 사용자 전달 ZIP `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA_v655_PC_TEST.zip` **1,516,982 bytes**, SHA256 `61a224653458eaf4a036880a4f4c1e827d64886da96a2c9cb9122593cf66bcca`. v654 대비 product **283개+manifest1**, **3개 파일 교체**, 이전 바이트 **280개 불변**. CRC PASS, manifest 283/283 sha/size PASS; manifest SHA256 `e3215ddbdb34858c50ef99065d1475d63d76207a4c884a1f7a176de70be05076`. 원본 ZIP/기존 사용자 파일을 덮어쓰지 않고 새 이름으로 전달.
- **미실행:** 새 Windows Python 3.12/3.14 GitHub Actions 전체 regression, Windows 실 PC 포터블 HTTP·SimC 기동/시즌 GJFO/Native DPS, 공식 다운로드 서버 실제 파일 HEAD/GET. 최신 KR 버전 확인이 그 PC에서 가능하고 정확히 호환되는 official Windows 빌드가 있는지는 실제 버튼 응답에서 확인. **현재 확정된 일치 Windows 바이너리 링크 없음**; 있다면 새 검증 경로에서만 노출. GitHub에서 현재 배포할 수 없는 9933ffb **소스**를 다운로드 가능한 Win64 exe처럼 소개하지 않는다.
- 새로운 SimC Native/기존 Native64 반복=0, 공식 Season DB2/Blizzard/WCL 인증·데이터 수집=0, v229/v217 지문·서명·세션·캐시·95% 통계 변경=0.

## 사용자 PC 다음 테스트
- **새 v655 ZIP을 별도 폴더**에 모두 압축 해제→`START_HERE_AUTO_SETUP_AND_RUN.bat` 실행→설정 '공식 업데이트 확인' 클릭(사용자가 명시적으로 요청한 시점에만 Blizzard 공개 BPSV, SimC official, GitHub source를 조회).
- `KR Live x / 후보 source y`가 다르면 설치 버튼 비활성, 기존 예전 SimC 설치 자체는 삭제하지 않음. matched link가 나오면 공식 .7z 다운로드/설치 후 실제 `SimC 연결 확인·저장`으로 관측 빌드 확인; 설치 성공이라도 `시즌 환경 READY`는 실제 별도 v216/v229 검증이 결정한다.
- exact matching Windows exe 없으면 '일치 배포 미확인'과 공식 출처 및 수동 경로만 안내, 신규 전체 컴파일·AI 런타임 의존성 도입하지 않음.
- v653 디자인 롤백 버전 기록 그대로, v654 설치·인증서 fail closed 보존. `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10`; isolated branch만 코드 변경. main/v003 immutable/Project UI/Work OS·주 제품 개발 채팅 권한 불변.
