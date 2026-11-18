# P1 v609 — 정식 v212 설치 → v096 프로필 E0 1회 소비자 통합과 실제 원본 접근 경계 (2026-11-19 KST)

## 목적·현재 첫 장애

본 제품은 **26개 DPS 전문화**의 미래 목표 ilvl(기본 334) 또는 사용자 수동 T에서 CHMV **최적 절대 rating**을 SimC DPS로 검색한다. 해당 작업은 기존 마부 제품 등록 경로 P1의 마지막 단계이며 독립 solver, 새 효과 엔진, 현재 장비 재분배, 장비 추천/전체 시즌 장비 DB 작업이 아니다.

v607은 봉인된 v191+v583 원본 최고 품질 계열 → 네 기존 Policy A 증거 생산을 연결했고, v608은 SimC 주문/발동이 있더라도 **정적 CHMV item_mod가 없는 마부의 정확 E0**를 회계 증명하도록 확장했다. v608의 신규 통합 테스트는 **v196의 승인된 설치 준비 목록**에서 종료됐다. **v609는 실제 기존 v212 설치 함수 및 v096의 정확한 프로필 ID 소비 경로까지 연결**하고, 현 세션이 이용할 수 있는 실물 원본의 범위를 확인했다.

## 실행한 개발

- 신규 `tests/test_v609_original_v212_enchant_install_boundary.py`: 기존 `SameFreshCatalogChain`의 **명시적인 합성 시즌 원본**을 사용. 일반 장비 `feet`의 SimC 소유 주문 마부(정적 CHMV 0)를 가정해 **기존 v211→v213→v216 staged source → v220 Policy A → v196 → v212.compile_fresh_installed_environment**를 호출한다. 신뢰 증거/숫자/아이템 ID는 테스트 fixture이며 실제 시즌 Wago/Native 증거가 아니므로 실제 제품 READY로 승격 금지.
- 정상 경우 `published_verified_option_count=1`, `enchant_id`·`feet`·원본 token·정확 fixed_E 네 0, B/T=3110, 수동 T3500 우선, 실제 v212 서명 manifest 검증과 설치 없는 baseline의 G/J/F/O 독립성을 확인한다.
- 기존 `v212.preview_installed_selected_enchant_budget`로 올바른 부위/ItemID만 허용하고 다른 장비 부위는 차단한다. 이어 **원래 `v096._signed_installed_user_E0_profile`**를 직접 호출해 임시 SimC 텍스트에서 `feet=id=<item>,enchant_id=<id>`를 정확히 한 번 요구하며 다른 부위 중복 `enchant_id`를 거부한다. SimC 사용/전투 효과·JSON2 DPS 자체를 인증하지 않는다.
- 원본 기존 `v583` 집중 워크플로에 해당 1개 테스트만 추가. 마부 등록 엔진·최적화 탐색/SEM/95%/DPS 캐시 및 공식 제품 상태를 변경하지 않음.

## 실제 역사 원본 재확인과 재실행 불가 경계

- [실제 12.1.5.70783 Wago↔SimC 관계 #44217110154](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44217110154)의 기존 artifact ID `14389266267`을 **실제로 다운로드해 ZIP 내용 검사**: `p1-v582-wago-permanent-enchant-relation.json` 한 파일(94,706 bytes), 76건 물리 ItemID/인챈트 연결 및 38개 품질 계열. 역사 실제 source SHA와 `production_v583_same_original_bytes_crosscheck.status=EXACT_PAIR_SET_EQUAL`은 보존되지만 **원래 v216 stage root 전체(`v191/v211/v213/v583/v212` 파일 및 stage receipts)는 없음**. 이 연구 JSON은 원래 production `v583` stage schema/receipt와 동일하지 않으므로 이를 **직접 product_input 승인 증거로 사칭하여 설치하지 않음**.
- [ZERO-SOURCE 실제 기존 DPS #44046442654](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44046442654) 기존 artifact ID `14312325613`도 다운로드하여 확인. `V552_TRUE_ZERO_SOURCE_TO_USER.json` 단일 compact report(14,360 bytes), 기존 환경 `M2.installed=true`와 설치 manifest SHA가 있으나 **전체 제품 실행에 필요한 봉인 실파일/원본 영수증을 포함하지 않음**. 기존 설치 PASS는 보존하되 새 마부의 실제 설치 테스트 대신 전용하지 않음.
- 이 접근 환경에서는 사용자의 PC 로컬 시즌 stage root 또는 원본 GitHub Actions의 보존되지 않은 runtime 임시 디렉터리를 직접 읽을 수 없음. 파일이 없다고 새로 SHA를 만들거나 신뢰 증거를 조합하지 않고, 현재 시즌 자동 등록 개수와 새 마부 Native DPS/SEM/95%는 **미측정·PENDING**.
- [v570 Windows 64 Native 사용자 기본 E2E #44074372451](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44074372451), v572 재개 등의 역사 실증은 유지. 이번 변경의 등록한 실마부 새 DPS E2E로 주장하지 않음.

### 최종 정밀화: 설치 파일과 v217 영수증 실기록/재사용

추가 테스트-only commit `352d17743bdc11c0d8d518da3882623a725b78ba`는 합성 승인된 한 마부에 대해 **원본 `v216._install_verified_fresh_environment_only`의 `v217.execute_stage`를 실제 실행**한다. 첫 번째 실행에서 `EXECUTED_AND_SEALED` + 실제 `v212_installed_*.json` 파일 저장/manifest SHA 검증, 똑같은 두 번째 요청에서 `REUSED_VERIFIED` + 동일 파일 경로/manifest SHA 재사용 확인. 이어 `v096._signed_installed_user_E0_profile`의 입력을 메모리 사본이 아닌 **저장된 설치 문서**로 변경해 부위/ItemID/마부ID 한 번 적용과 중복 거부를 확인했다. **해당 ZIP/receipt는 합성 테스트로만 생성되고 70783 실제 새 마부 승인 증거는 아님.** [최종 focused CI #44423460159](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44423460159) **SUCCESS**.

## Actions 확인, 변경과 비용

최종 코드/테스트 commit `48e2cbc727a303dcf2a8e9cc02a861da6a43c133` 기준:
- [v583 + 원본 v212→v096 통합 #44422800875](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44422800875) **SUCCESS**, 새 v609 통합 테스트 포함, 원래 v583/v584/v585/v216/v220/v607 등 집중 PASS.
- [공통 오프라인 #44422800883](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44422800883) **SUCCESS, 683 실행·2 SKIP·0 FAIL**.
- [78 규약 #44422800760](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44422800760) SUCCESS.
- 초기 새 테스트에서는 모듈 경로 누락 [#44422387564](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44422387564)과 이어 예외 클래스명 오기 [#44422767546](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44422767546)로 실패했고, 각각 정확한 import와 원래 `v096.EntryBlocked`로 수정한 최종 실행은 PASS. 중간 실패를 숨기거나 게임 실행 실패로 잘못 귀속하지 않는다.
- 신규 게임 HTTP/DB2 **0**, SimC Native **0**, 기존 정적 캐시/기존 DPS 캐시 폐기 **0**. 작은 합성 카탈로그 1회 컴파일과 동일 v212 예산/프로필 판정 재사용, 추가 solver/효과 Gate **0**.

## P1 실제 완료에 필요한 마지막 실행

현재 확보한 것은 **실제 원본 관계 70783 compact + 역사 기본 환경 영수증 + 합성 정상 제품 설치/프로필 소비자 PASS**다. 첫 실제 마부 결과에는 **원래 동일 게임 빌드의 이미 봉인된 전체 Build workspace 또는 정상 product/Windows 실행 session**이 필요하다. 사용 가능한 원본이 있으면 재수집하지 않고 그대로 사용:
1. 실제 `v216`의 원본 stage root(`v191/v211/v213/v583` stage + budget G/J/F/O)를 동일 revision/빌드로 로드하여 신규 `product_input` 및 `chmv_budget`를 검증. 항목별 유효 4 receipt가 있으면 `v212`가 자동 등록.
2. 등록 마부 중 E0 일반 장비 한 부위에 대해 최종 대표 item의 SimC 원본 물리 mask를 확인하고 `v106→v098→v096`에 사용자 선택 전달. 원본 `enchant_id` 1회 및 설치 SHA/선택/캐시 identity 확인.
3. 실제 같은 스코프 역사 Native 결과가 없을 때만 **한정된 단일 Windows SimC 사용자 DPS**를 실행해 DPS·SEM·95%·취소/재개 확인. 실패 시 첫 missing source/option만 남기고 다른 항목과 기본 G/J/F/O는 보류시키지 않음.

**STOP:** 이 챗의 이전 작업과 동일하게 등록·Native 실사용 PASS를 주장하거나 신규 26전문화 전체 Native를 반복하지 않는다. 실 stage root 없이 효과 수치 비교나 신규 Gate를 추가하지 않는다. 공식 **15/78 COMPLETE**, `full_product_e2e=PENDING`; 격리 브랜치만 변경, main/immutable/v016/Project UI/M0·Shared State/기존 주 제품 개발 채팅 소유권 불변.
