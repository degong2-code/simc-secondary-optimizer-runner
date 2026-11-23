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
