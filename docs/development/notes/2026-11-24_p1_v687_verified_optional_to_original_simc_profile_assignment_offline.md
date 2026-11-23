# P1 v687 — 설치 v212 승인 소모품 → 기존 v098 설정 → 실제 SimC 입력 문자열

작성 2026-11-24 KST. 기준 SHA `64d578416b8b8447565bfa01cd93ca06ad42c94a`; 격리 개발 브랜치의 이미 검증한 `v212`, `v218`, `v098`, `v139` 함수만 연결.

## 사용자 시나리오 / 범위

- 이미 실제 Windows source-only 70961 증거에는 Wago→SimC 연결 행 59개, v212 소스 투영 food35/potion1이 있으나 원본 스테이지 전체는 artifact에 보존되지 않았다. 이미 봉인된 70961 **실제 optional 포함 설치**가 있다는 뜻이 아니며 이번에 재수집하지 않는다.
- v686의 기존 `test_fresh_install_uses_original_v222_v196_and_v217_not_preview`는 합성 원본으로 기존 v212 설치 문서 `with_optional`→v218 사용자 승인→v098 정확한 `default_consumables.food` 전달 및 B/T 보존을 실함수로 확인했다.
- 이번 추가는 **같은 v098 시즌 설정**을 기존 `v139_pure_target_profile_composer.compose`에 넣어, SimC 최종 소모품 구문 `food=example_food_3`, `potion=disabled`, `augmentation=disabled`가 각 한 번 정확히 생성되는지 검증한다. 음식 선택 해제 BASE는 동일 설정/캐릭터/대표 장비 문자열에서 **food 한 줄만 다름**을 보장한다.
- v139의 물리 장비 fixture는 기존 패키지 대표 장비를 **오직 테스트 전용으로 재사용**하며, 이는 합성 설치 시즌/대표 장비가 같은 빌드라는 증거가 아니다. `STAGED_NOT_USER_READY`/Native0, 실제 시즌 프로필 원본 바이트·마부·트링킷·발동·DPS/SEM/95%까지 승인하는 테스트가 아님.
- 새 실행 원장·기능·UI·원본 fetch·Native/SimC·DPS 캐시·효과 인증 Gate **모두 0 변경**. 제품 코드 수정 없이 기존 v212 CI 한 테스트의 검증 범위만 확장한다.

## STOP 및 다음 목표

새 원본 stage를 임의 복제하거나 v684 원본 투영 결과를 기존 70961 v212 설치에 사후 주입하지 않는다. 실제 설치 SHA의 사용자 메뉴/세션 프로필 수락이 가능해지는 경우에 한하여 정확 한 경로를 실측한다. 현재는 최초 독립 증거가 없는 범위까지 PASS로 승격하지 않는다. 개인 PC v677 시험 보류, 공식 `15/78 COMPLETE`(완료율 아님)/`full_product_e2e=PENDING`/`next_review=B10`, 주 개발/main/v003/v016/Project UI/Work OS 권한 그대로.

## v687.1 — 신규 오프라인 비교 문자열 오탈자 교정

최초 v687 commit `2b0c724f861b8544f7d408bd1703b08c514b9da4`의 [v212 CI #45221057497](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45221057497)는 Windows/Ubuntu 각각 536 tests 중 신규 연결 테스트에서 1 FAIL(4 SKIP). Actions의 실제 assertion 출력에는 이미 `food=example_food_3`, `potion=disabled`, `augmentation=disabled`가 SimC profile text에 정상 포함됨. 실패는 테스트 기대 문자열의 `\\\\n`(리터럴 backslash+n) 사용으로 Python 실제 줄바꿈 `\\n`과 불일치했기 때문. 신규 비교문 4개만 `chr(10)`으로 정정하여 escaping 오해를 제거; **제품 코드, 실원본, 설치 SHA, 기존 GJFO 및 Native/DPS 경로는 불변**. 최종 PASS 여부는 수정 커밋의 Actions 결과로 구분해 기록한다.

## 최종 실제 CI 영수증 — v687.1

첫 v687 원본 [v212 Actions #45221057497](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45221057497)은 Python 테스트 예상 문자열의 잘못된 backslash+n 표기로 Windows/Ubuntu 각 1 FAIL. 실제 프로필 문자열 자체는 `food=example_food_3`, `potion=disabled`, `augmentation=disabled`로 정상 출력돼 있었음.

**개행 비교만** 고친 v687.1 커밋 `c8d7361cf070908427d1d3df56926cec418bf262`의 [v212 Environment Manifest offline contract #45221396337](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45221396337)는 Windows 2022·Ubuntu 24.04 **각 536 tests, 4 SKIP, 0 FAIL**. 두 OS 로그의 `test_fresh_install_uses_original_v222_v196_and_v217_not_preview` 개별 결과 **ok**, Native/원본 수집 없음.

한 테스트 함수 안에서 동일 합성 v212 설치 문서→v218 승인→v098 시즌 설정→v139 프로필 문자열 연결, BASE 음식 disabled와 정확히 한 줄 차이, 비등록 소모품 차단, G/J/F/O/B/T 불변이 확인됨. 이 합성 프로필의 대표 장비는 다른 테스트 fixture이고 실제 동일 70961 시즌 원본과 병합하지 않았음. 실제 70961 optional source-only 음식35/물약1 관측은 별도, **동일 SHA 실제 v212 설치→v113 UI→최종 Native SimC DPS 및 95% 결과는 미실증**.
