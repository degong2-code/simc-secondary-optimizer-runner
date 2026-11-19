# P2 v633 — 신규 시즌 영구 마부 전수 검토→필요한 E만 SimC Native→기존 Policy A 자동 등록

2026-11-19 KST · 격리 브랜치 `probe/chat-cache-v035-20261024`

## 1. 사용자 요구 및 범용 설계

새 시즌에 발견된 **모든 영구 마부**(이번 시즌 38개)의 정적 CHMV를 빠짐없이 판정한다. **38개라는 수를 코드의 영구 목록으로 고정하지 않는다.** 원래 `v191→v211→v213` 실제 시즌 원본·최고 품질·적용 조건을 전부 살펴, 정확한 정적 E0 혹은 무스케일 E는 봉인된 SimC 소스로 판정하고, 나머지 확정되지 않은 E만 **동일 대표 장비의 마부 없음/있음 Native 두 경우**로 측정한다. 수치가 검증되면 추가 수동 승인 없이 원래 `v220→v196→v212` 경로에 증거를 반환한다.

장비 조합 추천, 새 최적화 엔진, 마부 효과·proc 재구현, 26개 전문화 Native 전수, 상시 AI 런타임 호출은 만들지 않는다. 공식 `B=G+J+F`, `T=B+O`, E/L/O 각 1회 처리, 수동 최종 T 우선·95% 판정·취소/재개·캐시는 기존 기능으로 보존한다. 비정적 효과는 SimC가 그대로 담당한다.

## 2. 실제 구현

- `runner/v632_permanent_enchant_native_E.py` 신규 **작은 어댑터**, 별도 Native 엔진 아님. 기존 **`v278.run_case`의 콘텐츠 주소 기반 불변/실패/캐시 영수증**과 **`v297.parse_total_gear/compare`의 SimC 자체 초기 `total gear stats`**를 재사용한다. `v233` 정확 물리 대표 프로필에 `gear_*`가 없음을 확인하고, 한 선택 슬롯의 `enchant_id`만 다르게 구성한다. JSON2에서 실제 선택 ID·아이템 ID/ilvl·비대상 장비 불변을 검증한다. 초기 장비 정적 CHMV를 비교하고 스탯 비정합·SimC 실패·부정확한 JSON2는 E0로 처리하지 않고 보류. 같은 무마부 baseline은 8종에서 Native **1회만** 실행한 뒤 캐시 공유한다.
- `v216._fresh_source_owner_recover_permanent_enchant_scaled_E`: 기존 ZERO-SOURCE normal Environment Build **설치 직전** E 미확정 목록만 순회. 같은 실행 내 이미 인증된 `v232/v233` 원본·stage SHA, `v230` 물리 대표 ItemID/부위·SimC 적용 마스크, `v213` 봉인 원본, `v583`의 원래 product/품질 receipt, source-bound 바이너리/Native case SHA와 일치할 때만 기존 Policy A의 `chmv_budget` 증거를 작성한다. `v220.decide`와 `v196/v212`의 기존 atomic 등록 판단을 거친다. 조건 미충족은 옵션별 보류; **기본 시즌 G/J/F/O 설치를 차단하지 않는다**.
- 같은 source scaling ID·계수의 grouping은 **측정 계획/중복 작업 감소 힌트**이지 미측정 아이템의 수치 자동 승인 근거가 아니다. 70961의 8개는 **각각 실측**했고 하나의 bare baseline만 캐시 공유. 기본 G/J/F/O Native와 DPS 캐시는 변경하지 않았다.
- `integration_probes/p1_v610_real_installed_enchant_one_build.py`에 검증 범위를 설명하는 bounded compact `original_v633_E_native_repair` 기록 추가. 같은 70961 빌드 원본을 다시 생성하는 기존 v611 Workflow의 1회 opt-in을 사용. 역사 70783 E값·지난 artifact의 임시 stage를 사용자 제품 원본으로 재사용하지 않았다.
- 신규 `tests/test_v632_permanent_enchant_native_E.py`는 아이템 하나 외 변경 거부, 버프 없는 초기 스탯 E, 캐시 hit, E0/JSON2 변조 차단을 검증. 기존 focused / v212 Win+Ubuntu offline workflow에 추가.

## 3. 실제 Windows 70961 검증 — 38/38 등록 PASS

- [정확한 Windows v633 실행 #44478946469](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44478946469) **SUCCESS** · 실행 코드 HEAD `c223d3754b43041ae06febc0832de2a4ca60af65`.
- [컴팩트 원본 artifact #14507572779](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44478946469/artifacts/14507572779) 원본 `V611_REAL_70961_ENCHANT_ADMISSION_ONE_BUILD.json`, SHA256 `54f0113597173c6d8cc87409f8b2b36157cdf46ace3a452d8430e8ecc6364c79`. `original_v633_E_native_repair.status=OPTIONAL_ENCHANT_SCALED_E_ALL_TARGETS_VERIFIED`, `original_source_candidates=38`, `attempted_enchant_ids=[7965,7969,7995,7997,8021,8023,8025,8027]`, `native_E_registered=8`, `native_E_pending=[]`, `new_native_calls=9`; **마부 없는 baseline 1회 + 적용 8회**. 모든 38개를 Native 2회씩 실행한 것이 아니다.
- [실제 설치 원본 artifact #14507418763](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44478946469/artifacts/14507418763) `V618_REAL_INSTALLED_V212.json` (오래된 파일명은 기존 v610 출력 호환): 원본 SHA256 `498655bedb663f394497f2d3a1c713d339c183e2c4c12b717e8ee513d1550b68`, `manifest_sha256=55da83764eb4dafa3b1da57fc6f6f65c8e48b5641b635e6f1a4cb645746b41d6`, `published_verified_option_count=38`, `optional_other_proof_pending_by_id={}`, 같은 원본 카탈로그 SHA256 `494f672a35e4eba6026495bbd0a26b6b58363dad3087be59109959b25ffb03d1`.
- 검증된 **정적 rating E** (목표 ilvl334, 70961의 *실제 SimC 대표 물리 장비 조건*):
  - 특화: `7965=+24`, `7969=+29`
  - 치명: `7995=+24`, `7997=+29`
  - 가속: `8021=+24`, `8025=+29`
  - 유연: `8023=+24`, `8027=+29`
  - 기존 **30개 E0**는 해당 시즌 봉인 DBC 원본으로 이미 정적 CHMV 부재가 검증되어 Native를 반복하지 않았다. E0는 발동·전투 효과가 없다는 뜻이 아님.
- 동일 빌드 `12.1.5.70961`, SimC revision `9933ffb946fb55b1fa66657b848f519ac19006e1`, 정확 바이너리 SHA256 `4f4472ac8687d029cd7d6041741f44aa98750ea1b3e953dfa7002dee1f38879f`. `G=2850,J=92,F=165,O=0,B=T=3107` 기본 공식 예산(선택 E는 v212가 후속 기존 회계에서 처리). **이번 전체 환경 Native15회 = G/J/F/O용 기존 6회 + E 실측 9회, 신규 사용자 DPS Native0, SimC 재컴파일0(정확 SHA 캐시), 역사 캐시 폐기0**. `status=PASS_REAL_SEASON_V212_ENCHANTS_AUTO_REGISTERED`.
- [새 focused #44478693863](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44478693863) **688 PASS, 2 SKIP**, [v212 Win+Ubuntu #44478719625](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44478719625) 각 **534 PASS, 4 SKIP**. 이것은 해당 오프라인 범위 증거이지 26전문화 전부의 SimC DPS 성공 증거가 아니다.

## 4. 정확한 수락 경계와 다음 P2/P3

- **완료:** 새 시즌 발견 범위 38건을 source/E 분류, E0 30개 재측정 생략, E 미확정 8건 실제 SimC 물리 전후 Native 검증, 정적 CHMV +24/+29 기록, 기존 v220/v196/v212 최종 **38개 실제 자동 등록**. 미검증 항목 또는 숫자를 수동 주입한 이력 없음.
- **추가 인수 필요:** 양수 E 실제 일반 사용자 웹 선택 → `v098/v096` 최종 프로필의 정확한 부위·`enchant_id` 1회 삽입 → 자동 ilvl·수동 최종 T에서 E 추가/하한/중복 검증 → 실제 SimC DPS·SEM/95%·캐시·취소/재개. 이번 E 비교 Native 9회를 사용자 DPS 계산으로 오해하지 않는다. 38개 모든 가능한 전 장비·손·전문화 조합까지 동작이 확정된 것은 아님; 사용자 최종 장비에 대해 기존 적용 마스크·손 검증 유지.
- 새 시즌 원본 자체가 다른 마부 ID 수/효과를 갖더라도 **38/8/24/29는 소스 기반 현 시즌 결과일 뿐 엔진 상수 아님**. 미래 시즌은 새 source/SimC/binary identity로 분류·검증·등록; 측정 실패/타임아웃은 해당 아이템 보류, 기존 Native 캐시 재사용, 정상 기본 제품 차단 금지. 별도 effects Gate·무분별한 전수 Native 반복 금지.

**권한:** `main` 병합·`v003` immutable·Project UI 적용·Work OS M0/Shared State·기존 주 제품 개발 채팅 권한 불변. 공식 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10` 유지.
