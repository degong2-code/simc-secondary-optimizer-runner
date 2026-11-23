# P3 v673 — F/J 단계 진단·실행 입력 재사용 보완 + 장식 제작장비 가로 2열

2026-11-23 KST · 격리 브랜치 `probe/chat-cache-v035-20261024`

## 사용자 PC에서 관측된 문제 (신규 PC 성공 주장 금지)

- 사용자 v671 JSON: 빌드 `12.1.5.70961`, ilvl334, 동일 영약 ItemID241320 품질2 F165·보석 `240890/240898/240906/240914` J92, 2개 원본 설치본. `SOURCE_STAGES`, `STAGED_SOURCE_MANIFEST`, `V216_PREFLIGHT_SEAL`만 다른 것으로 관측. 현재 Retail build 일치 미확정.
- 사용자 v672 실제 UI 캡처에서 두 설치본 모두 `물리 구성 동일 · 개별 선택 보류`. v672의 원본 실행 입력 동등성 판정이 사용자 PC 데이터에선 아직 통과하지 않음. 원인으로 v216 preflight-only 미승인 메타데이터 차이가 가능한 반면, 실제 내부 재검증 실패/실행 자료 차이도 가능하므로 동등성 통과를 가정하지 않음.
- 같은 캡처에서 `장식 제작장비 1`과 `2`가 세로로 표시. 원인은 `#crafted-rows`에 2열 grid를 넣었지만 실제 두 `.gear-row`는 그 안의 **한 개** `.gear-group` 하위에 생성되는 DOM 구조 불일치. UI 디자인 정책은 두 장식 나란히 같은 폭, 각 카드 내부 2열, ItemID 가로 전체 폭, 반응형 좁은 화면에서만 세로.

## 변경된 코드 (선택 범위만)

1. `runner/v113_local_web_api.py`: v672 기존 `_v672_verified_runtime_inputs_digest`에서 **별개 v212 staged 문서와 v113 profile stage 및 exact v212 install을 기존 verifier로 검증한 이후**에만 `v212_environment`의 `pending_core_requirements`, `optional_item_missing` 두 **사전 검증 단계 미승인·보류 진단값**을 실행 입력 비교에서 제외. 이 두 값은 staged NOT INSTALLED 전용 상태와 개별 선택적 보류 사유이고, 최종 설치본의 필수 G/J/F/O·검증 옵션·실제 SimC 프로필의 권한이 아님. 이외 `numeric_budget_preview_unadmitted`, `versioned_policy_A_prepared_options_unpublished`, 승인 원본, installed manifest 전항목, source stage 입력, 실제 v113 프로필·장비/예산 데이터는 계속 엄격히 비교.
2. 동일 backend는 stage/install/runtime 세 범주 내부 digest를 구분하되 외부에 원문/해시를 공개하지 않음. 미통과 중복 그룹에 한하여 `RECEIPT_PROOF_UNAVAILABLE`, `DIFFERENT_INSTALLED`, `DIFFERENT_SOURCE_STAGE`, `DIFFERENT_RUNTIME_SNAPSHOT` 중 고정 범주 코드를 노출. 정상적인 단일 설치본 경로는 변경하지 않고, 임의 SHA/latest 선택 금지 유지. **모든 영수증 재검증·3범주 실행 입력 동등성** 통과 후에만 기존 v672 deterministic 대표 설치본 하나 표시하고, 실제 세션은 다시 exact SHA 검증.
3. `runner/webui/app.js`: 차단 원인이 있을 때 한국어 진단으로 UI 표기; 기존 영약·보석 exact 선택 경로 및 비용 낮은 읽기 전용 조회 유지.
4. `runner/webui/styles.css`: 실제 `#crafted-rows > .gear-group > .gear-row` sibling에 2열 grid를 적용. 내부 입력도 2열 균등 배치, 수동 장비 ItemID 전체 폭, 숨김 bonus 등 내부 필드가 grid 공간을 차지하지 않음. 680px 이하 카드 세로, 420px 이하 내부 필드 세로. 기존 row 생성·입력 계약·유효성 검증 변경 없음.

## 회귀·효율

- 신규 `tests/test_v669_verified_fj_physical_identity_offline.py` 보강: 봉인 실행입력 동등성·미승인 preflight 두 목록 차이 통과·실제 숫자 소스/원본/profiles 차이 차단·stage/install/profile 세부 비교·UI 비밀키 미노출·정확 F/J 대표 선택·생성 DOM 구조에 맞는 2열·숨김 label·breakpoint.
- [Windows Actions #45110180126](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45110180126) `c356e39ee3abdde58640b1a1bc4edcc01d8bf513`: Windows Python 3.12 / 3.14 **각 352 PASS, 0 FAIL** 및 개별 패키징 확인 5 PASS, WIN launcher / loopback HTTP / 3 plans, 신규 Native 0.
- [Local Web API #45110180032](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45110180032): Windows 3.14 / Ubuntu 3.12 **각 511 tests OK, 1 SKIP, 0 FAIL**.
- [Focused #45110179995](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45110179995) 및 v401 contract #45110180103 SUCCESS.
- Actions wrapper artifact `14789261374`; 추출한 진짜 제품 ZIP `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip`: **1,535,661 bytes**, SHA-256 `b5fefbd6d3fc2f82de9c2a079f31a3ef200906a362bf68186386a2c06a6a0008`. CRC PASS, 패키지 manifest 286/286 size+SHA PASS, 제품 ZIP에 simc.exe 없음. 사용자용 파일명은 `SIMC_SECONDARY_OPTIMIZER_v673_WINDOWS_BETA.zip`.
- 비용 검토: 추가 API 캐시/스키마 변경 없음; 이미 발견된 소수의 **충돌 설치 그룹에서만** 기존 sealed v212/v113 파일을 bounded read/verify; DB2 / 네트워크 / Native / DPS 반복 0. 동일 시즌 정적 원본·DPS 캐시·세션/취소/재개·95% 통계 변경 없음.

## 남은 사용자 PC 확인과 상태 분리

- v673 ZIP 새 폴더 설치. 기존 관리 SimC / source installs / cache / runs 보존. 설정: 기존 설치본 조회용 빌드 `12.1.5.70961`, ilvl334, 네 보석, 오일 미사용; 새 G/F 빌드·Native 체크 모두 off. 시즌 환경 설치 버튼·최적화 시작 버튼 누르지 않음.
- `2차 스탯 최적화 → 영약 → 검증된 환경 구성`에서 `검증된 동일 실행 입력 대표 설치본`이 나타나는지 검사. 나타나면 선택만 하고 화면을 확인; 아니면 드롭다운 아래 **새 실행 입력 차이 범주 메시지**를 확인. 캡처로 회신하여 실제 사용자 PC 근거 확보. 도출된 진단은 직접 PC 데이터로부터 나온 것이며 CI 오프라인 fixture와 구분.
- 실제 현재 Retail build 일치, 사용자 PC에서의 READY·전체 26 DPS E2E, 공식 승격은 여전히 PENDING. 이전 `15/78 COMPLETE`는 구현 퍼센트 아님, `next_review=B10`. 기존 주 개발 채팅 소유권 유지, main/immutable/Project UI·Work OS M0·Shared State 변경 없음.
