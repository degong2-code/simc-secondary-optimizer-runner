# P2 v631 — 시즌 마부 E 증거 누락의 구조적 원인·자동 복구 경로 (2026-11-19)

## 핵심 목적
남은 8개 특정 ID를 하나씩 수동 등록하는 것이 목적이 아니다. 다음 확장팩·시즌에서 동일 증거 결손이 반복돼도 **기존 ZERO-SOURCE 환경 구축에서 원인을 분류하고, 정확히 계산되는 값은 등록하며, 나머지는 최소 Native 증거 수집 작업으로 안내/재개**하는 범용 설계가 목적이다. 시즌 전체 DB, 전투 효과 인증, 새 SimC/최적화 엔진 및 26개 전문화 Native 전수를 만들지 않는다.

## 1. 실증된 근본 원인
1. v629에서 확인한 **부위 증거 소비 누락**: 원래 봉인 `v213.catalog.enchants.items`의 반지/무기 가족 `slot_group/slot_resolution_status`가 `v196_enchant_source.rows` 투영에서 소실되었다. v629은 원본·투영 필드 교차 검증 후 원본을 기존 v220에 전달. **v630 실제 동일 빌드 ZERO-SOURCE 계열 실행으로 19→30 PASS**.
2. 이후 8개는 **원본 자체가 미수집된 것이 아님**. 기존 `v216._v217_policy_A_source_relation_receipts`는 정적 CHMV가 없는 출처에 대해서만 `fixed_E=0`을 증명했으며, 정적 CHMV가 있는 경우 이미 분류된 `v211` 자료에서 실수치까지 연결되지 않았다. 단순 `EVIDENCE_MISSING:chmv_budget` 표시는 원인(스케일링)과 복구 수단(표적 Native)을 구별하지 못했다.
3. 새 실환경 [v631 실제 70961 Windows #44474450046](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44474450046) **SUCCESS**; compact artifact [#14504649841](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44474450046/artifacts/14504649841), 설치 artifact [#14506170593](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44474450046/artifacts/14506170593) 원본 JSON 직접 확인:
   - 정확한 8 ID `7965,7969,7995,7997,8021,8023,8025,8027` 모두 단일 정적 CHMV 모드, `dbc_amount=0`, `scaling_id=-7`; 계수는 각각 **0.7136 또는 0.8623**. stat 종류는 치명/가속/특화/유연. 이것은 **데이터 누락이나 E=0이 아니라 SimC 스케일링 계산이 필요한 사실**을 뜻한다.
   - 설치 `published_verified_option_count=30`, 나머지 정확히 8건 `EVIDENCE_MISSING:chmv_budget` 보류. `G=2850,J=92,F=165,O=0,B=T=3107`, 환경 Native **6회**, 사용자 DPS Native **0회**, 동일 SimC 바이너리 재컴파일 **0**. `status=PASS_REAL_SEASON_V212_ENCHANTS_AUTO_REGISTERED`, 새 긍정적 E 승인 0.
   - 기존 임시 원본 stage 부재는 복원 필수 Gate가 아니었다. 새 시즌 원본을 기존 ZERO-SOURCE 제품 경로로 새로 만들면 된다. v567 전체 ZERO-SOURCE 역사 검증과 이번 70961 동일 빌드 재구축의 증거 범위는 구별한다.

## 2. 범용 코드 수정
- **정확한 무스케일 정적 E 자동 산출:** `runner/v216_environment_build_coordinator.py`는 동일 빌드의 봉인된 `v211/v213` DBC 원본에서 알려진 CHMV ITEM_ENCHANTMENT_STAT 하나 이상의 정확한 정수 금액, `scaling_id==0`, `coefficient==0`, 인식된 `item_mod_id`, 일치하는 stat 이름 및 미분류 없음 조건에서만 양수 `fixed_E`와 증거 SHA를 자동 생성. 기존 E0 경로도 보존. SimC spell/proc는 재구현·인증하지 않는다. **이 조건에 맞는 시즌에서 신규 Native 없이 등록 가능**; 70961의 8개는 `-7`이므로 등록되지 않는 것이 올바른 동작.
- **자동 결손 분석:** `runner/v220_catalog_auto_admission.py::plan_optional_permanent_enchant_budget_repair`는 기존 `decide`의 미확정 `chmv_budget`만 소스 원본·토큰·마스크·분류에 맞춰 판단. 정적 E0 영수증 연결 오류 / 정확한 SimC 스케일 수치 미확정 / 미분류 소스 / 영수증 identity 충돌을 구분. 다음 조치·stat scaling 필드·source identity SHA·아이템/슬롯 가족·최대 신규 Native 비용을 출력. 결과는 원래 `v216.preflight_new_season_source → source_compilation`을 통해 Build에 연결; 단순 실패 목록 대신 소스 기반 복구 작업을 전달.
- **측정 그룹화:** 동일 빌드·카탈로그·목표 ilvl·부위·클래스/마스크·컴포넌트 순서·scaling ID·amount·coefficient이고, CHMV 스탯 한 개 외에는 정적/주문 컴포넌트가 없는 항목에 한정해 stat 방향과 ID를 제외한 **수치형상 그룹**을 만든다. 각 그룹 1개의 기존 SimC 비교 우선, 해당 identity의 캐시가 있으면 0회, 없으면 최대 2회라는 계획을 출력. **그룹화는 동등한 스케일 소스 구조의 증거일 뿐 E 금액이나 다른 아이템 자동 승인 증거가 아니다.** 정확한 SimC 실측·소스 동치 재검증 전 `numeric_transfer_approved=False`. 범위/손/부가 spell이 다르면 그룹을 쪼갠다.
- **보존/무중복:** 검증된 기본 G/J/F/O와 v212 설치는 미확정 선택 마부 때문에 중단하지 않음. 수동 T 우선, E/L/O 1회 보호, profile/SimC/case cache identity, 관측 1순위·SEM·95%·취소/재개는 기존 코드 그대로. 원본 stage를 지속 보관하는 신규 필수 요구사항 없음. 기존 real probe는 compact 수치 복구 작업만 artifact에 남긴다.
- **하위 호환 교정:** 초기 E0 오류 메시지 변화로 일부 오프라인 테스트 실패가 발생하여 `V216_POLICY_A_ORIGINAL_STATIC_E0_SOURCE_PROOF_DRIFT` 원래 오류 계약을 복구. v607 합성 fixture 원본/투영 마스크 일치 정정; 실제 사용 가능 증거로 오해하지 않는다.

## 3. 새 검증과 분리된 한계
- 최종 그룹화 코드 HEAD `0e3816e746e4165eec1b697fc8395f533e8491bd` 대상 [focused #44475207857](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44475207857) **685 PASS, 2 SKIP**; [v212 Windows/Ubuntu #44475207820](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44475207820) 각 **531 PASS, 4 SKIP**; [v583 #44475207788](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44475207788) SUCCESS; [v113 #44475207795](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44475207795) SUCCESS; [78 정적 #44475207854](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44475207854) SUCCESS.
- 방금의 실제 Windows 증거 `#44474450046`은 **수치 그룹화 코드 추가 이전**이며 source E0/E+ 자동 산출·결손 원인 분류까지를 실측. 그 후 그룹화는 원본 source와 동등한 합성 fixture로 오프라인 PASS; **새 그룹화 후 다시 6 Native를 돌리지 않았다**. 실제 8개가 두 coefficient 종류라는 것은 실측이며 2개 그룹으로 모으는 정확한 최종 manifest 결과는 후속 단계 검증 대상이다.
- **미완료:** 그룹별 SimC Native 전/후 정적 E 측정의 자동 실행·봉인/중단 재개·검증된 측정값을 동일 빌드 v216→v220→v212 등록으로 돌려보내는 소비자 연결. 따라서 8개를 READY 또는 38개 모두 등록이라고 주장할 수 없음. 별도 전투효과 인증 Gate를 추가하지 않는다.

## 4. 다음 최소 제품 P2
1. 이미 존재하는 `v198` 정확한 before/after SimC JSON2, `v278/v297` 초기 총 gear stats·content-addressed Native 재사용 경로 중 목표 ilvl 대표 프로필에 맞는 **원래 비교 경로**를 선택. 한 그룹·한 정적 숫자 측정부터 시작해 같은 소스 수치형상 그룹에만 적용 가능한지 source/실측 조건 확인. 최대 추가 2 Native/그룹, 캐시 HIT 0회; 미일치·SimC 오류면 해당 아이템만 보류.
2. 실측 E의 게임 빌드·원본 프로필·바이너리 SHA·실제 ItemID/손·소스 스케일형상·Native 전후 receipt SHA를 기존 Policy A `chmv_budget` 내부 증거로 자동 전달. 그룹 내 모든 옵션의 E를 이름·계수만으로 추정하지 않으며 차이가 있으면 개별 재측정. 기존 v212의 양수 E accounting, 수동 T, E 총합, G/L/O 중복 방지를 그대로 재사용.
3. 딱 1회 사용자 입력→기본 환경→추가 정적 E 선택→기존 SimC→결과/중단·재개의 실제 제품 경로 검증으로 P3를 연결. 전수 Native 반복과 불필요한 산출정밀화 금지.

**권한/상태:** 격리 브랜치만. `main`, `v003` 불변 원본, Project UI, Work OS M0·Shared State, 제품 주 개발 채팅 권한 변경 없음. 공식 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10` 불변.
