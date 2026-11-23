# P1 v682 — 실제 SimC 소모품 부분문자열 파서의 후보 충돌 최소 방어

2026-11-23 KST. 사용자 `진행`; 격리 브랜치 `probe/chat-cache-v035-20261024`. 패치 직전 HEAD `d4551dc912d9a6a5e87583bebca8dfa08b2a9c9b`.

## 사용자 위치 및 원인

단일 시즌 Build `v216`의 음식/물약 Wago 물리 ID + SimC source → `v212` 설치 사용자 선택지 → `v113` 웹 UI → `v218/v098` SimC food/potion 입력 중, **다른 실제 물리 아이템이 입력 후보를 가로챌 수 있는 부분문자열 경계**를 보강한다.

핀된 70961 SimC `simulationcraft/simc@9933ffb946fb55b1fa66657b848f519ac19006e1`:
- `engine/player/consumable.cpp::find_consumable`은 `util::str_in_str_ci(normalized_full_name, entered_name)`으로 **부분일치** 검색하고, 동일 crafting quality를 찾는다. 기본 rank 없이 입력 시 rank 1 조건. 아이템 순서가 사용자 목표 ID와 일치함을 보장할 수 없다.
- `engine/util/util.cpp::tokenize`는 이름의 하이픈·아포스트로피를 제거한다(v681에 공통 후보 변환 교정).

예컨대 동일 subclass/품질에서 `royal_roast_3`은 `impossibly_royal_roast_3`의 정규화된 이름에도 포함될 수 있다. 기존 v212 완전 동일 token 검사만으로는 이 구조를 배제하지 못한다.

## 코드 최소 변경

- `runner/v212_environment_manifest.py::project_fresh_optional_consumables`의 기존 후보 그룹 검증 후, 소스에서 관측된 **같은 카테고리·같은 품질** 아이템 사이에서 더 긴 이름의 부분문자열이 되는 입력 후보만 설치 선택지에서 제외한다.
- 검사에는 이미 `source["rows"]`로 전달된 ID/SimC source 토큰만 사용한다. 추가 전체 아이템 DBC 패스·Wago HTTP·Native·새 효과 메커니즘/인증 Gate·시즌 ID 하드코딩 없음.
- 다른 카테고리 및 품질의 이름은 충돌이라고 단정하지 않으며 모호한 일부 옵션만 보류한다. 여타 BASE G/J/F/O, 수동 T, L/E/O, 기존 설치본/캐시/세션 그대로.
- `tests/test_v680_one_build_optional_consumables.py`: 실제 SimC 파서 이름 사례 + 동일/다른 품질·음식/물약 분리를 합성 자료로 회귀 검증.

## 증거 경계 및 STOP

이 패치는 **현재 단계에서 이미 소스 연결에 성공한 후보**의 일부 잠재 오선택을 방지한다. SimC 전체 `item_data.inc` 내 미선택/미관측 ID까지 고려한 유일성 증명, 실제 최신 시즌 음식/물약 선택지 수, 진짜 Wago 사용 주문→핸들러 일치, 수치적 최고품질 비열등성 및 Native 실측은 아직 PENDING. 새 전체 parser 인증 Gate를 만든 것으로 서술하지 않는다.

기존 GitHub Actions에서 확인된 70961 영수증은 설치·DPS에 대한 한정된 범위이며, 음식/물약 Wago CSV 전체를 재사용 가능한 stage_root로 제공한 증거는 발견되지 않았다. 원본 stage가 연결된 환경에서 **기존 v216 한 번**의 실 구축 projection→v212/113/218 관통을 확인할 때 실제 근본 결손을 최종 판단한다. 이번 커밋으로 전체 제품·26전문화·실 소모품 등록 PASS를 주장하지 않는다.

공식 `15/78 COMPLETE`(구현률 아님), `full_product_e2e=PENDING`, `next_review=B10`; main/immutable/Project UI/Work OS 및 주 개발 채팅 소유권 변경 없음.
