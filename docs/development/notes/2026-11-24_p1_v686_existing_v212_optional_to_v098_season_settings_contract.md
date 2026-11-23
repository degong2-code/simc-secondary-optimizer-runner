# P1 v686 — 기존 설치 원장 1개에서 승인된 소모품 → v098 시즌 입력 연결

2026-11-24 KST. 격리 브랜치 `probe/chat-cache-v035-20261024`, 기반 HEAD `6a9ff2c96734f7114053eddbb3635be0cc2e70c4`.

## 목표 / 증거

기존 실제 70961 [v684 Windows source-only #45198409461](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45198409461)는 Wago→SimC 연결 59개(음식42/물약17), v212 **source projection** 음식35/물약1을 증명했으나 **설치 SHA→프로필 입력→DPS**를 실측한 것은 아니다. v685는 `v113.plan` 선택 특수/장식 경로의 검증값 전달 누락을 고쳤고 Windows·Ubuntu 웹/API 543 tests(1 SKIP)/0 FAIL이다.

이번 작업은 새 source 수집/Native/검증 체계를 늘리는 대신 기존 `tests/test_v212_environment_manifest.py::FreshEnvironmentSourceStageTests.test_fresh_install_uses_original_v222_v196_and_v217_not_preview`의 **이미 서명·검증된 synthetic v212 설치 manifest**와 기존 SimC consumer를 한 번 연결한다. 실제 Wago 원본/물리 수치라고 주장하지 않는다.

## 단일 수락 경로

1. 동일 기존 테스트에서 원래 v222 G/J/F/O와 v191/v213 원본의 `compile_fresh_installed_environment(...source_optional_consumables=...)`가 만든 **`with_optional` 실제 함수 반환 문서**를 `verify_fresh_installed_environment`로 검사한다. v212 정확한 설치 토큰 `example_food_3` 외 임의 토큰은 추가하지 않는다.
2. **동일 문서**를 `v218.current_season_approved_optional_choices`와 `_verified_fresh_season_consumables`에 전달해 사용자가 고른 음식 토큰이 그대로 인식되고 미사용 물약·증강은 `disabled`인지 확인한다. 잘못된 과거/비등록 토큰은 차단.
3. 기존 `v098._season_settings_from_v216`에 같은 승인된 토큰과 GJFO **합성 일치 J/F·보석 수치**를 전달하여 `default_consumables.food`가 사용자 선택값이며 `potion/augmentation`은 disabled인지 확인. 기존 v139 최종 profile serializer는 이 필드를 SimC `food=`, `potion=`에 기록하도록 설계됨(기존 코드 소비 확인).
4. 원본 G/J/F/O·B/T 서명 및 설치 문서 불변, 새 영구 캐시/세션/Native/HTTP/DB2 동작 없음. 이 테스트의 도달 범위는 **v098 시즌 설정**이며 최종 SimC 프로필 물리 장비·실제 Native 음식 효과 처리까지 PASS로 승격하지 않는다.

## STOP / 비용

기존 v212 offline workflow와 기존 테스트 파일만 활용, 새로운 독립 Gate·워크플로·품목 하드코딩·캐시/원본 버전 폐기 없음. 테스트 합성 데이터에서 J/F 수치를 실제 시즌 70961 값처럼 복사하지 않음. 새 70961 실수집/Native/외부 HTTP0. 다음 진짜 수락은 **검증된 같은 시즌 실제 설치 SHA에서 v113 사용자 UI → v098 최종 SimC 프로필/기존 DPS**를 한 번 관측, 소스 재수집이나 고정 L/E/O 새 인증 엔진으로 확장하지 않음.

공식 `15/78 COMPLETE`(완료율 아님), `full_product_e2e=PENDING`, `next_review=B10`; PC v677 개인 시험 보류; 주 개발 채팅/main/immutable v003/v016/Project UI/Work OS 승격 권한 불변.
