# P1 v680 — 제로베이스 1회 시즌 구축의 소모품 선택지 소유권 연결 (진행)

2026-11-23 KST · 격리 브랜치 probe/chat-cache-v035-20261024.
최신 사용자 결정: [제로베이스 구축·Wago/SimC 신뢰·게이머 중심 UI](../POLICY_ONE_BUILD_SOURCE_TRUST_GAMER_FIRST_20261123.md).

## 실제 사용자 문제와 근본 원인

신규 시즌 일반 입력→시즌 환경 구축→대표 장비/예산→사용자 음식·물약 선택→SimC 실행 프로필→기존 DPS/95% 출력.
v679까지 음식·물약은 Wago/SimC 후보를 수집하면서도 UI/실행에서는 상수 source_default만 허용했다. 이는 특정 음식 ID의 수동 인증 부족이 아니라, **원래 환경 구축 v216이 생산한 자료를 v212 설치 원장과 v113/v218/v098이 소비하지 않는 구조적 단절**이다.

이번 변경은 **개별 시즌 아이템 하드코딩이나 v108 역사 토큰 재승격 없이**, 새 시즌 zero-base Build가 소모품 옵션을 원래 v212 설치 기록에 포함시키고 사용자 선택·프로필 생성·복구가 동일한 설치 기록을 사용하도록 한다.

## 실제 구현 내용

1. v280의 기존 Wago ItemXItemEffect+ItemEffect ID 연결을 원래 v216 Build에서 음식·물약까지 **소스 데이터 변환**으로 확대한다. v280의 기존 flask/oil 기본 join 동작은 변경하지 않고, v680 stage는 이전에 확보한 **같은 빌드 원본 CSV**를 재사용한다. 수집한 Wago 바이트에 대해 별도 효과 인증을 하지 않으며, 새 ItemEffect 다운로드/Native 0. 반복 호출에서는 v217 봉인 스테이지를 재사용해 큰 CSV를 다시 읽거나 해싱하지 않는다.
2. 같은 Build에서 Wago의 정확한 ItemID·사용 주문과 pinned SimC v189 지원 핸들러 및 v230 generated item_data의 품목 종류/품질을 연결한다. SimC 등록의 **minimum_game_version** 이후 효과만 통과, 동일 게임 빌드와 revision 확인. 아이템 이름만으로 다른 효과를 묶지 않는다. 정확한 SimC 입력 토큰의 최종 파서 사용 가능 여부는 실제 SimC가 결정하며 오류가 발생하면 원문을 보고한다.
3. 해당 source join을 source+revision+code SHA로 구분한 v217 경량 projection stage에 한 번 보존한다. 재구축 시 큰 SimC item_data.inc의 반복 파싱을 회피하며, 원본 변경이나 구현 변경이 기존 정적 캐시를 폐기하지 않고 새 content-addressed stage로 분리된다.
4. v212 compile_fresh_installed_environment의 새 옵션 인자로 source_owned_optional_consumables를 수용한다. **새로 생성된 설치 매니페스트**에만 optional menu + 원본/빌드 정체성을 포함하고, 기존 설치본의 bytes/예산/캐시/영구마부 등을 수정하지 않는다. 효과·사용조건 그룹을 원본 그대로 유지하며 서로 동등하게 식별된 그룹의 품질 순위 상위 한 항목을 후보로 표시한다. 동률/중복 ID·SimC 토큰 충돌은 해당 옵션만 보류하고 BASE 전체를 막지 않는다.
5. v113 /season-option-catalog과 v677 read-only installed-budget는 **동일한 검증된 v212 매니페스트**로부터 같은 projection을 제공한다. 사용자 PC에서 이미 설치된 검증 환경을 선택한 경우도 기존 예산 응답 한 번으로 UI 옵션을 갱신하므로 추가 네트워크 GET이 필요 없다.
6. 웹에서 선택 가능한 음식·물약·증강룬은 해당 설치 SHA의 메뉴만 사용한다. 과거 세션의 history 토큰은 화면 복원에만 사용되며 현재 설치 승인으로 전환되지 않는다. v218→v098/SimC 생성 경로는 실제 선택형 항목이 있을 때만 해당 v212의 아이템 입력을 검사한다. 기본 source_default/disabled 실행은 기존 경로 그대로이며 **추가 디스크 읽기 0**.
7. v680 음식·물약 안내를 개발자 용어보다 게임 용어 중심으로 수정했다. 시즌 기본 소모품 제외로 계산 시 효과를 반영하지 않는다는 사실은 계속 표시한다.

## 새로 실행한 검증과 증거 경계

- 합성 source/오프라인: v680 테스트는 Wago 아이템→사용 주문, 기존 ItemEffect 요청 1회 재사용, 추가 네트워크 0, SimC generated item metadata/handler 결합, 최신 입력 revision·최저 버전 분기, 효과/사용 조건별 최고 품질 분류, 동률·토큰 충돌 비선택, 실제 JS 설치 SHA 전환, v218 선택/기본 disabled 경계, 동일 소스 반복 호출 시 item_data 재파싱 금지를 확인한다.
- 실제 원래 v212 테스트에 **선택형 메뉴가 들어간 새 설치 매니페스트** 계약을 추가하여 G/J/F/O/B/T 계산·v212 봉인 일치와 기존 매니페스트 불변을 비교한다.
- **실제 코드 HEAD `f48a283dd18e734e16d089eba35948eb30a23f84`의 CI 완료·성공**:
  - [API #45152990800](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45152990800): Windows Python3.14/Ubuntu Python3.12 **각 540 tests OK, 1 SKIP, 0 FAIL**.
  - [Windows ZIP #45152990735](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45152990735): Windows Python3.12/3.14 **각 389 tests OK, 0 FAIL**, 패키징 **5 PASS**, 실제 ZIP 추출·CMD·로컬 HTTP 3계획·세션 복원 **Native0**. Wrapper artifact [#14808020590](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45152990735/artifacts/14808020590); 래퍼 digest `sha256:8892803c6c917b3e88933f1a6ced27a1f88128d5b6793eb466ffb3e5fe3400db`는 내부 ZIP 해시와 다르다.
  - [v212 설치 계약 #45152990885](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45152990885), [UI #45152990775](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45152990775), [기존 focused #45152990813](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45152990813), [v410 분류 #45152990679](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45152990679) 모두 성공.
  - 개인 사용자 PC 실측 및 신규 DPS/G/F Native **0회**. 테스트는 실제 최신 시즌 전체 소모품 등록 PASS가 아닌 **합성 원본+기존 제품 계약의 오프라인 PASS**다.
- 기존 11/8 고양 주술사 소모품 Native 시험, 기존 v639 최적화/95% 결과는 *역사 재사용*이다. 이번 코드의 새 시즌 실제 실행 PASS가 아니다.

## 아직 미해결 — 완료를 과장하지 않음

- **최신 게임 빌드에서 실제 1회 제로베이스 구축으로 음식·물약이 몇 개 등록되는지는 미실측**. Wago 물리 사용 주문과 SimC 등록 spell이 같은 ID로 연결되지 않는 음식은 이 source join에서 후보가 되지 않는다. 다음에는 최신 실제 봉인 데이터로 그 연결을 1회 검증하고, 필요하면 SimC 원래 consumable option 파서/ID 정보를 재사용해 **범용적으로** 수정해야 한다. 다른 시즌 아이템 하드코딩/새 효과 인증 Gate 금지.
- 아이템 이름에서 파생한 token과 실제 SimC parser의 허용 여부는 원본 generated item_data만으로는 완전히 입증되지 않는다. 실제 입력 오류는 SimC 원문을 보여준다. 모든 동일 효과·사용조건의 품질별 **관련 수치 비열등**이 원본에서 확정됐다고 주장하지 않는다. 근거가 불충분한 그룹은 사용자에게 정상 선택지로 과장하지 말아야 한다.
- 새로운 시즌의 모든 음식·물약·증강룬·마부·기름 선택지가 등록됐다는 전체 기능 PASS는 아직 아님. 증강룬은 현재 기본값만. 기존 고급 환경 UI의 개발자용 G/J/F/O, SHA, Native, B8 등의 전면 자연어 치환도 완료되지 않았다.
- 일반 user PC E2E/최신 KR Live 빌드 확인은 사용자 요청으로 보류. full_product_e2e=PENDING. 공식 78 계약과 next_review=B10 불변.

## 비용/권한

동일 시즌 원본 캐시 재사용, 기존 v217 stage 사용, 외부 DB2/Wago 추가 조회 0, 신규 SimC Native 0, DPS 캐시/세션/기존 v212 설치본 변경 0. 중복 Effect 인증 및 시즌 DB 재수집 0. 추후 필요한 검증은 빈 설치 시 실제 시즌 데이터→기본 G/J/F/O와 optional menu→실제 user profile까지의 **하나의 제로베이스 결과** 단위로 수행한다.

격리 브랜치 이외 main 병합/immutable v003 변경/공식 v016 원본/Project UI/Work OS·주 제품 개발 채팅 소유권 변경 없음.
