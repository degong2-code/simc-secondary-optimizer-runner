# P1 v683 — Wago 물리 소모품 중 SimC DBC 미수록 ID 하나가 전체 선택지를 지우던 구조적 단절 교정

2026-11-23 KST; `probe/chat-cache-v035-20261024`; 패치 기준 `ccb120ec2474bec8458c013a3cbb738a8292e9cd`. 사용자 `진행`에 따른 격리 구현.

## 실제 사용자 위치·첫 원인

사용자 **시즌 환경 준비 1회 → v216 소모품 원본 후보 → v230 같은 빌드 SimC generated item metadata → v212 설치 선택지 → v113 UI → v218/v098 SimC 실제 입력**.

최신 v682의 `_fresh_v680_source_owned_food_potion_uncached`는 Wago ItemID 중 모든 사용주문 후보를 `v230.from_seed(directory,item_ids=ids)`의 **완전한 ID 집합**으로 요구했다. Wago에는 있는 물리 아이템이 같은 빌드 SimC generated `item_data.inc`에 없으면 `V230_GENERATED_ITEM_DATA_INCOMPLETE_OR_REQUEST_MISSING` 예외 → v216의 optional catch에서 **rows=[] 전체 탈락**이 된다. 이는 소모품 효과·게임 지원 인증 부족이 아닌, 서로 다른 두 권위 있는 원본 사이 **후보 집합 불일치에 대한 all-or-nothing 구현** 문제다.

## 최소 수정

- `v230.parse_exact/from_seed`에 **명시 선택형 `allow_missing=False` 기본값**. 일반/필수 ID 조회는 기존 완전 ID 일치 실패 정책과 응답 필드를 보존한다.
- 오직 `v216`의 선택형 음식·물약 대량 원본 연결만 `allow_missing=True` 호출한다. 한 번의 해시·한 번의 전체 item_data 패스에서 관측한 정확한 동일 ID들만 반환하고, 없는 물리 ID를 `missing_item_ids`로 구분. 선택형 0개면 옵션 부재로 처리하며 유효한 BASE를 막지 않는다.
- 원본 v229 receipt·Git blob·SHA·동일 게임빌드·SimC revision 검증, C++ 구문·전체 chunk·stat pointer 오류 차단, 클래스/서브클래스/품질·SimC handler 결합 및 v212 토큰 충돌 방어 유지.
- `v680` 합성 source fixture에 **Wago만 보유한 4번째 ID**를 넣고, v230에 없는 해당 ID 때문에 기존 3개 선택지 소실하지 않는 회귀를 추가. `v230` 회귀에서 strict default와 optional partial/전체미관측/빌드 drift/핀된 seed SHA 보존 검사.

## 검증 및 비용 경계

기존 v680 Windows ZIP (Actions #45152990735) 내부의 실제 v230·v216 원본을 로컬 추출해 **기존 strict 예외 재현**; 교정 코드를 동일 파일에 적용한 뒤 같은 fixture의 **부분일치 성공**, `v216` 1개 미수록/1개 정상 ID의 소스 연결 성공 및 Python 문법 검사까지 수행. 이는 **합성 오프라인 재현**이며 새 시즌 Wago→SimC 파서 Native 승인 또는 실제 설치된 최신 소모품 수를 실측한 것이 아니다. 기존 인증 설치 v630 artifact #14504332493는 **v680 이전** 설치본으로 소모품 CSV 원본이 들어 있지 않음. GitHub Actions가 업로드한 작은 설치 영수증을 실제 원본 DB2 보존으로 오인하지 않는다.

변경된 v230·v216 코드 fingerprint로 이후 compact v217 projection만 구분. 기존 시즌 정적 캐시·개인 설치·DPS 캐시 폐기 0. 신규 Native/게임 DB2·HTTP 수집 0. 새로운 별도 효과·품질 인증 Gate, Wago 또는 SimC 메커니즘 재구현, 전 전문화 Native 반복 없음.

## 남은 정확한 연결 / STOP

1. 실제 새 시즌 `v216` **1회 원본 Build**의 음식·물약 원본 ID/handler/SimC DBC **부분일치 수** 및 v212 설치 선택지 수는 원본 CSV stage가 전달되지 않아 **미확인**.
2. SimC 단어 부분문자열 검색의 **전체 DBC** 유일성, 등록 토큰 실제 Native 인식, 동일 효과·사용조건 품질의 **수치적 비열등** 미증명은 각 선택 옵션만 보류할 원인. v681/682 source-known 방어를 전체 파서 검증으로 과장하지 않음.
3. 개인 PC v677 자동 T/DPS 시험은 사용자 재개 지시까지 보류.

공식 `15/78 COMPLETE`(구현률 아님), `full_product_e2e=PENDING`, `next_review=B10`, main/v003 immutable/v016/Project UI/Work OS/주 개발 채팅 소유권 그대로.
