# P1 v618→v619 — 실제 영구 마부 자동 등록 19건 → 최종 대표 장비 → 기존 SimC DPS/SEM/95% 실증

2026-11-19 KST · 실제 게임 빌드 **12.1.5.70961** · Windows 2022 · 개발 격리 브랜치 `probe/chat-cache-v035-20261024`

## 목적과 정책

제품은 사용자의 **미래 목표 ilvl(기본 334) 또는 수동 최종 CHMV T**에 대해 26 DPS 전문화의 **최적 절대 치명·가속·특화·유연 rating**을 SimC DPS로 찾는다. 현재 장비 재분배나 시즌 장비 조합 추천이 아니다. 시즌별 `G/J/F/O`, `B=G+J+F`, `T=B+O`, 선택 L/E/기름 O의 정확한 1회 예산 회계, 최고 품질 실물 ID, SimC가 자체 실행하는 효과/proc/APL/DPS, 95% 통계, 캐시·취소·재개를 유지한다. 제품 전투효과 인증/등급별 효과 계수 우월성 Gate는 만들지 않는다.

**실행 증거와 GitHub 링크:**
- 실제 신규 마부 등록: [v618 #44438148520](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44438148520) **SUCCESS**, GitHub artifact `p1-v618-real-current-70961-v212-enchant-admission` (ID **14490621359**)와 `p1-v618-real-70961-verified-v212-installed` (ID **14489588587**)를 직접 다운로드해 원본 내용 확인.
- 실제 단일 사용자 마부 SimC: [v619 #44440673155](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44440673155) **SUCCESS**, artifact `p1-v619-actual-installed-E0-one-user-native` (ID **14491256825**)의 세 JSON(`V610_REAL_ENCHANT_ADMISSION_ONE_BUILD.json`, `V619_REAL_USER_ENCHANT_DPS.json`, `V618_REAL_INSTALLED_V212.json`)을 직접 다운로드·대조. 원본 SimC revision `9933ffb946fb55b1fa66657b848f519ac19006e1`, 이 실행의 source-bound Windows binary SHA256 **4f4472ac8687d029cd7d6041741f44aa98750ea1b3e953dfa7002dee1f38879f**. 이전 70783 정적/실 DPS 데이터를 70961에 가져오지 않음.

## 실제 70961 시즌 설치·품질·마부 등록

원래 `v113.LocalJobs→v216/v217/v212` 새 빌드 원본 검증과 설치:
- ilvl334 목표, `G=2850, J=92, F=165, O=0, B=T=3107`. 이번 v619 기본 환경 Native **6회**.
- 최고 품질 원본 `v191+v583` 정확 38 계열(물리 품질 ID 76개); `source_relation=38, simc_input=38, product_input=38, chmv_budget=30`, 네 증거 모두 존재한 30 ID 중 최종 실제 장비 적용부위·손 원본까지 입증되어 **`v212.published_verified_option_count=19`**.
- 실제 등록 부위는 가슴/머리/발/어깨. 모든 등록 마부의 `verified_fixed_E`는 네 개의 **정적 rating 0**. 비CHMV 효과·발동이 없다는 뜻이 아님. `EXACT_PHYSICAL_SLOT_OR_HAND_RELATION_NOT_VERIFIED` 19건, 정적 E 미확정 8건은 **해당 옵션만 보류**, 검증된 기본 환경은 정상 설치.
- v619 실제 설치 SHA256 **382318ace517f08034b619c0bc2c2304e4540ba1b1c9762bb852a424dc33acce**, stage receipt SHA256 **f73fefa5d15ba1fd824486b125cbf959323edb10556d7d8ea1c87e611df5cb5d**. 이 SHA는 v618의 이전 독립 실행에서 받은 설치 SHA와 달라도 정상이며, **같은 실행 내 원본 source/receipt/manifest 귀속**만 주장.

## 최초 사용자 선택 → 원래 v098/v096/v094 SimC DPS

- 정확한 v212 등록 `enchant_id=7957`, `enchant_chest__mark_of_nalorakk` (가슴 마부, 최고 출처 rank 2, E0)를 선택.
- `v106.standard_controls((paladin,retribution))`에서 사용자 간소 입력을 구성(전체 장비 선택 없음), `v098.preview_from_environment_build`가 검증된 **동일 70961 v212 원본과 대표 장비**를 사용하여 `READY_SOURCE_BOUND_SEASON_MANIFEST_ZERO_NATIVE` → 실제 `v096.run_manifest` 계획 및 프로필을 생성.
- **최종 대표 chest ItemID 268222**에 `enchant_id=7957`이 **정확히 1회** 존재, 전체 프로필에서 중복 0, `B=T=3107`, E0 예산 무중복, 최종 프로필 SHA256 **84a27bfa46eb0355ad319e3bf954fb023c8a10e395aa17a5385e4bd14a4c9a01**, 장비 줄 SHA256 **c8233f46a505b6c4c08112b3dd9f132c1f647a57a5bc0b13a725b04dc90321f4**.
- 기존 `v096→v094` 적응형 SimC **Native DPS 6회**, 검증된 `PASS_BOUNDED_GENERIC_NATIVE_SEARCH_AND_CACHE`, 신규 후보 관측 **4개**. 이 첫 실행 DPS 캐시 hit **0**(신규 바이너리/프로필/후보), 기존 역사 캐시 삭제 **0**.
- 관측 최고 **DPS 158565.16559398346, SimC SEM 246.50167802403055**. 절대 rating **치명736 / 가속736 / 특화735 / 유연900** (합 3107).
- 실질적 근접 대안 **DPS 157790.25965839627, SEM 236.04294383832664**, rating **치명425 / 가속1047 / 특화735 / 유연900**, 관측 상대 DPS -**0.489%**.
- `confidence_level=0.95`, `confirmation_pair_direction_supported_at_95=true`, `confirmation_scope=TWO_FRESH_SELECTED_CANDIDATES_ONLY_NOT_GLOBAL`. **관측 1순위/근접 대안 사이의 95% 판단만 확인한 것이며 전역 최적해 검증이 아님**.

## 범위·효율·남은 제품 작업

1. 이 v619는 **실제로 등록된 마부 하나 + 프로그램의 기존 최종 대표 장비·사용자 설정(징벌 성기사) + 실제 Native DPS/SEM/95%** 증명이다. 다만 브라우저 UI에서 일반 사용자가 등록 마부를 고르고, 26개 DPS 전문화 모두 동일하게 실제 SimC 성공했다는 증거는 **아직 없다**. 현재 웹 API는 별도의 읽기 전용 `verified_installed_enchant_registrations`를 제공하고 `runtime_selectable=false`를 유지한다. 거짓 선택 가능 표시 금지.
2. **다음 P1:** 검증된 19개 중 **E0·실물 부위 확정된 것만** 실제 사용자 선택 컨트롤과 원래 `v106.enchant_choices→v098/v096`에 연결하고, 현재 final representative item에 대해 정확한 원본 마스크를 확인해 기존 웹 Start/Cancel/Resume 및 캐시 identity 검증. E>0·손/무기·보류 19개를 증거 없이 UI 승격하지 않음.
3. v618은 같은 빌드 source-bound SimC CLI를 SHA 및 source revision 메타와 함께 **GitHub Actions cache**에 기록; v619는 정확한 키/실 SHA를 검증 후 캐시 HIT로 사용하므로 **새 CLI 컴파일 0회**. v619 시즌 Build 환경 Native **6회**, 사용자 DPS Native **6회**; 전체 26 DPS 전수 **0회**. 동일 시즌 정적 캐시를 revision만 바뀌었다고 폐기하지 않음.
4. 프로젝트 공식 현황은 이전 원장 `15/78 COMPLETE`, `full_product_e2e=PENDING`을 **그대로 유지**. 단일 마부 사용의 실제 Native PASS가 전체 사용자 웹 제품 통합/신규 release 검증은 아니기 때문이다.
5. 코드 v619는 작은 probe `integration_probes/p1_v619_real_70961_user_enchant_dps_once.py`, 기존 v610의 **선택적** downstream callback, 새 캐시 복원 Actions만 추가. 탐색 엔진/전투 효과 로직/시즌 DB 구조/기본 v096·v094·Native 실행 알고리즘 수정 **없음**.

**권한:** 격리 브랜치만 변경. main 병합·immutable v003/v016 원본·Project UI 적용·공식 Work OS M0/Shared State·기존 주 제품 개발 채팅의 개발 소유권 변경 없음.
