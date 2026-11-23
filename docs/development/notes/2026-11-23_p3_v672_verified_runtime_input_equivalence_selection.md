# P3 v672 — 서로 다른 v216 사전 SHA: 실제 실행 입력이 같을 때만 기존 F/J 설치본 재사용

2026-11-23 KST · 격리 브랜치 `probe/chat-cache-v035-20261024`
제품 코드 및 ZIP HEAD: `c9f10a6ce5547f0e6cf5226c5b1d773e6002138e`

## 실제 사용자 PC 증거와 설계 경계

- 사용자 v670: `12.1.5.70961`, ilvl334, 검증 설치본 2개, 같은 영약 `241320` 품질2 F165, 보석 `240890/240898/240906/240914` J92, 차이 `SOURCE_STAGES`만.
- 사용자 v671: 차이를 `STAGED_SOURCE_MANIFEST`와 `V216_PREFLIGHT_SEAL`로 좁힘; v217 v191/v211/v213 출력 영수증의 차이는 미검출. 과거 사전 검증 전체 객체는 저장 경로상 복원 불가. 단순 SHA 다름=모두 동등함이라는 결론은 허용하지 않음.
- 기존 `v212_installed_<sha>.json`, `v212_environment_<stage_sha>.json`, `v113_profile_<sha>.json`은 각 영수증과 함께 사용자 PC에 저장되는 원본. 사용자 본문/SHA를 외부로 제출하지 않고 로컬에서 비교 가능.
- 정본 정책: 같은 물리 F/J·예산만으로 선택 금지. 이전 stage SHA가 다르면 역사적 preflight 입력이 같았다고 주장하지 않음. 현재 KR Live 빌드 미인증은 별도.

## 제품 목적에 직접 연결하는 최소 변경

- `runner/v113_local_web_api.py::_v672_verified_runtime_inputs_digest`: 기존 `find_verified_installed_season_environment(...exact SHA)`를 **이미 통과한** O=0/4보석 검증 설치본 각각에 대해, 원본 v212 사전 환경 출력·v113 저장 프로필의 v217 단계 영수증을 다시 검증. 설치 SHA·사전 preflight SHA·해당 SHA로 식별되는 stage 연결 필드 **만** 비교에서 제외. 실제 저장된 v212 설치 문서의 다른 모든 필드, source-stage의 모든 다른 필드, v113 실행 프로필 구성의 모든 다른 필드를 내용 기준으로 엄격히 비교. 누락/불일치/단계 영수증 검증 실패면 `None`으로 fail-closed.
- 같은 영약 ItemID·품질/F/J/소켓/4보석 물리 ItemID인 그룹의 **모든** 설치본에서 비교 지문이 존재하고 같을 때만, deterministic lexical min SHA를 **이미 동일한 실행 입력으로 검증된 대표본의 내부 exact locator**로 등록. 최신 시각·해시 정렬·수치 동률만으로 대표본을 고르지 않음. 같은 그룹의 다른 설치본은 UI 선택 금지 유지.
- `runner/webui/app.js`: 서버가 원본 비교로 등록한 `verified_runtime_equivalent_representative:true`만 중복 그룹에서 선택 가능 표시. 사용자가 직접 선택한 후 기존 `chooseInstalledFlask`→exact v212 SHA read-only 조회와 기존 v113/v216/v217 검증을 다시 거치며, source READY/현재 KR Live 인증/Native DPS 자동 승격은 없음. 서버의 승인 근거를 바꾸지 않음.
- 다른 물리 구성, 다른 예산·프로필·원본 출력, 불완전 영수증, 신규 build에는 적용하지 않음. 저장된 `preflight` 전체 원본 없이 그 과거 입력이 같았다고 주장하거나 강제로 합치지 않음.
- 신규 DB2/HTTP 수집, SimC C++ 빌드, 신규 DPS Native·시즌 G/F/O 측정·캐시 삭제·원본 변경 **0회**. 기존 적응형 SimC·95%·저장/취소/재개·O/L/E/B/T 회계 불변. 단순 오프라인 로컬 v212+v113 검증용 파일 read/hash만 중복 그룹에 추가. 일반 단일 설치본의 재검증 추가 없음.

## 테스트 및 Windows 배포

- 기존 `tests/test_v669_verified_fj_physical_identity_offline.py`에 같은 실행 입력/서로 다른 연결 preflight SHA의 동일 지문, 단계 출력 또는 v098 입력 차이 시 불일치, 원본 영수증 없을 때 차단, 실제 JS에서 대표본 한 개만 활성화 회귀를 추가. 실제 PC 영수증은 테스트로 재현하거나 읽었다고 주장하지 않음.
- 초기 CI Windows에서 새 합성 스냅샷 테스트가 `Path.write_text`의 CRLF 변환 때문에 FAIL: 실제 v113은 `write_bytes`로 canonical LF를 봉인함. 합성 fixture만 LF 바이트 저장으로 수정; 과거 FAIL은 증거에서 삭제하지 않음.
- 최종 [Windows #45107663421](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45107663421): Windows Python 3.12/3.14 각각 **351 tests PASS/0 FAIL**, package 5 PASS, 기존 추출 CMD·local HTTP·3 plans PASS, 신규 DPS Native 0.
- 최종 [v113 API #45107663438](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45107663438): Ubuntu3.12/Windows3.14 각 **510 tests OK(skip1)**.
- ZIP wrapper [artifact #14788750429](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45107663421/artifacts/14788750429); 내부 단일 `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip` **1,534,434 bytes**, SHA256 `9c65a5d4b3d5ec89c337a6cd3330112ceeacbea73a3dc560439233a8302b75da`, manifest **286/286 SHA·size PASS**, CRC PASS. SimC exe 및 개인 세션 포함 없음.

## 다음 실제 사용자 행동과 STOP

1. v672 ZIP은 기존 CMD 종료/탭 정리 후 **새 폴더에** 풀고 실행. 기존 설치·세션·캐시·관리형 SimC 70961 보존.
2. **오직 로컬 과거 설치본 조회 용도**로 게임 빌드 12.1.5.70961/ilvl334/4보석/기름 미사용/특수·장식 없음, 환경 새 G/F·Native 체크박스 모두 해제. 현재 KR Live 일치와는 별개.
3. `2차 스탯 최적화 > 영약 > 검증된 환경 구성` 확인. `검증된 동일 실행 입력 대표 설치본`이 활성화됐으면 기존 v212+v113 단계별 영수증과 저장 실행 입력 동등성에 대해 **현장 신규 관측**으로만 보고; 이후 exact SHA 조회/READY도 별도 확인. 활성화 안 됐으면 안전 차단 유지, 신규 Native나 무조건 재빌드 금지.
4. 처음 사용자 PC 화면에서 여전히 선택 불가면 파일 직접 제출·SHA 수동 입력을 강요하지 말고, 남아 있는 원본 stage/프로필 실제 변경값을 한 번만 분류해 필수 입력과 선택적 진단을 구분. 현재 build 인증 없이 DPS E2E 완료 주장 금지.

공식 `15/78 COMPLETE`는 제품 구현률 아님; `full_product_e2e=PENDING`, `next_review=B10` 유지. main, v003 immutable, Project Sources/Instructions UI 적용, Work OS/Shared State·원본 v016 직접 통합·기존 주 제품 개발 채팅 권한 변경 없음.
