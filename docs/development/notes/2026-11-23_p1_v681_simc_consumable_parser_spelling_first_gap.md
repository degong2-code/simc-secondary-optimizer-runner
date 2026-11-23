# P1 v681 — 기존 70961 SimC 파서 원본 기준 소모품 입력 토큰 첫 결손 최소 교정

2026-11-23 KST. 사용자 `진행` 승인. 격리 브랜치 `probe/chat-cache-v035-20261024`. 코드 작업 직전 HEAD `b017ee608c658b1c44e986b3052c7c2a4559fbdc`.

## 사용자 가치 및 실제 소비 지점

시즌 1회 준비 → v216 Wago 물리 ID / v189 등록 주문 / v230 DBC 이름 → v212 설치 원장 → v113 선택 → v218/v098 SimC food/potion 입력. v680은 물리 아이템과 주문을 연결했더라도 `v484.candidate_token`이 ASCII 구두점을 모두 밑줄로 바꾸어 SimC 본래 소비품 파서의 토큰과 다른 입력을 생성할 수 있었다. 이를 실제로 읽은 같은 시즌 SimC commit `9933ffb946fb55b1fa66657b848f519ac19006e1`의 `engine/util/util.cpp::tokenize`, `engine/player/consumable.cpp::find_consumable`에서 확인했다.

- 예: `Sweet-and-Sour Skewers`: 기존 `sweet_and_sour_skewers_3` ≠ SimC 정규화 `sweetandsour_skewers_3`.
- SimC는 하이픈·아포스트로피 등을 **삭제**하고 공백을 밑줄로 바꾸며, 한 자리 숫자 품질 접미사를 해석한다.
- `v484.candidate_token`의 공통 정규화만 보수적으로 교정했다. SimC는 유지하지만 기존 설치 토큰 문법이 수용할 수 없는 `+`, `.`, `%` 문자는 무리하게 다른 문자열로 대체하지 않고 해당 선택을 보류한다.
- 소스별 아이템 하드코딩, 자체 음식 효과 해석, 새로운 등록/Native 인증 Gate, G/J/F/O 예산·캐시·기존 설치본 변경은 하지 않는다.

## 검증 경계

- 테스트 추가: `tests/test_v680_one_build_optional_consumables.py`에 핀된 70961 규칙의 하이픈/아포스트로피·단일 자리 품질·안전 미지원 입력 사례.
- 기존 실제 시즌 70961 Wago/SimC 원본의 소모품 후보 **등록 수**, 토큰이 해당 **물리 ItemID를 선택하는지**, `str_in_str_ci` 부분문자열 충돌, 실제 소모품 SimC Native 실행, 높은 품질 수치적 비열등성은 **여전히 미확인**. 이번 패치는 parser-compatible 후보 문자열 교정일 뿐 실제 선택 인증이나 전체 환경 구축 완료가 아니다.
- 이전 v680 오프라인/Windows 영수증은 역사 재사용. 이 수정의 신규 CI/NATIVE/HTTP 실행은 결과가 확인된 이후만 별도 보고한다.

## 다음 최초 미완료 경계 및 STOP

기존 봉인된 실제 시즌 소스/캐시에서 **한 번의 v216 Build**로 나온 음식·물약 `v212` 선택지가 실제 생성되는지부터 관측한다. 이어서 같은 설치 SHA의 v113/v218/SimC 입력 중 첫 불일치만 수정한다. 필요한 실 소스가 GitHub/기존 Actions에 없으면 출처 제약을 명시하고 전체 Wago/DB2 또는 전 전문화 Native로 확대하지 않는다. 동일 효과·사용조건에서 높은 품질이 모든 수치에서 열등하지 않다는 원본 근거 없이 전체 최고 품질 자동 등록 PASS를 선언하지 않는다.

공식 `15/78 COMPLETE`(구현률 아님), `full_product_e2e=PENDING`, `next_review=B10` 및 main/v003 immutable/v016/Project UI/Work OS/기존 주 제품 개발 채팅 권한 불변.
