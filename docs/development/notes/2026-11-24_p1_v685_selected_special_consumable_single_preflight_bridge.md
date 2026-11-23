# P1 v685 — 등록된 소모품 + 선택 특수장비/장식의 원장 전달 오류 수정

작성 2026-11-24 KST; 기존 v684.2 HEAD `3347606312e072c3b8a9370bdfe759fdbbe1eae7`의 실코드 점검 기준. 격리 브랜치 `probe/chat-cache-v035-20261024`.

## 제품 단위와 원인

제품 사용자가 같은 v212 설치 환경에서 음식·물약을 선택한 뒤 특수장비나 장식도 선택하면, `v113.LocalJobs.plan`은 먼저 `_v680_preflight_optional_consumables(self.root,params,user)`로 정확 v212 설치 SHA/게임빌드/ilvl의 허용 토큰을 검증한다. 그런데 승인된 반환값을 **버리고**, `selected_fresh` 분기에서 `profile_stage._verified_fresh_season_consumables(user)`를 다시 호출하면서 **설치 원장 미전달**로 승인 목록을 `source_default`로 축소했다. 그 결과 원본에서 정상 승인된 음식·물약과 특수장비/장식을 함께 고른 사용자는 `FRESH_SEASON_OPTIONAL_CONSUMABLE_NOT_INSTALLED`로 잘못 차단될 수 있다.

이는 Wago/SimC 새 검증 Gate가 필요한 문제가 아니라 **기존 승인값의 단계 간 전달 누락**이다. 이전 v680 오프라인 테스트는 UI→v218 선택만 확인하고 이 분기와 결합한 실행 경로는 놓쳤다.

## 최소 수리

`plan` 진입에서 **기존 preflight의 반환값**을 `season_optional_controls`로 저장해 바로 같은 `selected_fresh` preview `season_controls`에 전달한다. 승인 규칙·서명·등록된 v212·기름·수동 T·고정 L/E/O, SimC JSON2, DPS 캐시, 세션 identity, 기본 미선택 BASE 경로 변경 없음. 선택 소모품의 실제 저장을 위해 **원장 추가 재읽기 0회**; 이미 실행한 SHA 검사와 확인 결과를 재사용한다.

`tests/test_v680_one_build_optional_consumables.py`에 실제 `LocalJobs.plan`의 선택 특수장비 + 등록된 음식 컨트롤을 구성하여, 동일 preflight 결과가 `bootstrap.preview_from_environment_build`까지 전달되는지를 검사한다. 그 직후 의도적으로 종료, Native/Popen 0·새 세션 0. 생산 코드와 별도 원본 fixture를 보유하지 않아 실제 70961 전체 Native 승인이나 선택 B8의 최종 실행 성공을 주장하지 않는다.

## 수락·비용·STOP

최소 신규 회귀: 실제 v113 코드 분기의 `preflight exactly once`, 같은 `season_controls`, 검증 fresh 환경 객체, 세션·Native 이전 중단, 기존 `v212/v218` 검증 테스트 보존. 기존 v684 실제 동일 시즌 Wago 원본 stage Actions/영수증을 확보하지 못했으므로 실 음식·물약 자동 등록 개수는 **미확정**. 추가 Native·HTTP·Wago/DB2 0, 환경/정적/DPS 캐시 변화 없음.

사용자 PC v677 T/DPS 시험 보류, 기존 v570/v639 Native 이력 재사용, 26전문화 Native 전수·새 효과 인증/최적화기/완료 Gate 금지. 공식 `15/78 COMPLETE`는 완료율 아님, `full_product_e2e=PENDING`, `next_review=B10`. main/immutable v003/v016 원본/Project UI/Work OS/기존 주 제품 개발 채팅 권한 변함 없음.

## v685.1 — 신규 회귀의 CI 실제 실행 경로 조정

P1 v388 focused Actions #45205277833의 로그에는 `tests/test_v113_local_web_api_offline.py` 96 PASS가 보이지만 `tests/test_v680_one_build_optional_consumables.py`는 해당 job에서 호출되지 않았다. 따라서 v685의 새 결합 회귀를 PASS로 과장하지 않으며 **새로 만든 CI 워크플로 없이**, 해당 새 테스트 하나를 이미 실행되는 웹/API `LocalWebAPIOffline` 클래스로 이동했다. 기존 v680 원본 연결·토큰 테스트는 원래 파일에 그대로 둔다. 다음 focused Actions에 정확 `test_selected_special_preview_reuses_exact_installed_consumable_preflight`의 개별 ok가 찍힌 경우에만 신규 테스트 PASS로 보고한다. 이 이동은 제품 동작·데이터·Native·HTTP·캐시 0 변경.

## v685.2 — 실제 70961 원본 영수증 회수 및 신규 테스트 CI 첫 실패 정정

기존 `[v684-source-once]` commit `7c556c493af3c7293069490b1d47dd24defb7b2e`에서 이미 실행된 [Actions #45198409461](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45198409461) Windows job `one-source-only`은 **SUCCESS**이고 실제 로그 `V684_SOURCE_ONLY_VERDICT`는 다음을 보고했다: 동일 빌드 Wago 음식 물리 후보 192개·물약 61개, Wago→SimC source-owned 연결 행 **59개(음식42·물약17)**, `v212.project_fresh_optional_consumables`의 **음식35·물약1·증강0(미구축)**, 원본 source compilation `FRESH_V191_V211_V213_COMPILED_UNADMITTED`, Native 호출 **0**. 이는 설치된/실제로 SimC 실행된 사용자 옵션 36건이나 품질 비열등 Native 승인으로 승격하지 않는다. `v684` 진단 artifact #14830042126가 존재하며 원본 CSV 전체는 없다. 기존 영수증을 먼저 조회하지 못해 '실행 미확인'이라고 표현했던 상태를 **실행 증거 확인**으로 정정한다. 동일 시즌 원본을 재수집하지 않는다.

v685.1 code commit `cb157da94e26a4b36e30f32bb5281801472c0660`의 기존 [v113 API #45205602235](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45205602235) / [v388 focused #45205602181](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45205602181)는 신규 테스트에서 **NameError: BUILD is not defined**로 FAIL. 제품 경로의 값 전달 결함 자체가 검증 실패한 것은 아니며 이전 v680 테스트 모듈에 있던 상수를 `test_v113`으로 옮기며 복사 누락한 테스트 코드 오류. 이번 v685.2는 신규 테스트 안에서 문자 그대로 `build="12.1.5.70961"`, `revision="a"*40`으로 고쳤다. 신규 focused PASS는 다음 Actions 로그 개별 ok를 확인한 뒤에만 보고한다. 코드/Native/수집/제품 캐시 수정 0. 

## 최종 검증 영수증 — 실제 실행 조회 완료 (문서 전용)

v685.1에서 테스트를 기존 `test_v113_local_web_api_offline`로 옮기는 과정에서 `BUILD/REV` 모듈 상수를 정의하지 않아 초기 v113/v388 CI가 **NameError FAIL**. v685.2 commit `0681b4c85246b58c7ebe61692b79fba2bcad99c8`에서는 신규 테스트 안의 빌드·revision을 지역 상수로 정정. **제품 런타임 코드는 v685 최초 수정 후 변경 0**.

해당 커밋의 검증:
- [v388 focused #45206141247](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45206141247) SUCCESS; 테스트명 `test_selected_special_preview_reuses_exact_installed_consumable_preflight` 포함 **97 PASS / 0 FAIL** 확인.
- [v113 offline API #45206141446](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45206141446) Windows Python3.14·Ubuntu Python3.12 **각 543 tests, 1 SKIP, 0 FAIL**.
- [v181 Windows ZIP #45206141232](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45206141232), [v182 UI #45206141285](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45206141285), [offline #45206141251](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45206141251), [공식 78 scope #45206141253](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45206141253): SUCCESS. 신규 소모품·특수장비 **최종 실제 SimC 실행·Native 수락을 검증한 것은 아님**.

실제 70961 v684 [Windows #45198409461](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45198409461)에서 Wago 192 food/61 potion 후보 중 59 연결(42/17), v212 소스 투영 35 food/1 potion/0 augmentation, Native0. 이는 선택형 소모품 원본의 SOURCE PROJECTION 성공이며 **v212 설치된 G/J/F/O/프로필 예산과 같은 SHA로 실행했음을 인증하는 자료가 아님**. 이미 사용한 Wago 본 수집 반복하지 않음. 다음 수락은 동일 설치 SHA로 UI와 실제 SimC 선택이 연결되는 1건, 미해결이면 최초 누락 단계만 보완. 공식 15/78은 진척률이 아니며 기존 권한 불변.
