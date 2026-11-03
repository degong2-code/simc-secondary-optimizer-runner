# SIMC SECONDARY OPTIMIZER — 2026-11-03 P3-BO → 범용 G/J/F/O Environment Build 개발 인계 정본

**기준:** 2026-11-03 KST, P3-BO까지의 코드·GitHub Actions 및 최신 직접 사용자 결정.
**목적:** 다음 채팅이 기존 프로젝트를 재시작하거나 역사 Native/원본/CI를 무조건 재실행하지 않고 현재의 **하나의 Environment DB Build 엔진** 개발을 정확히 이어가도록 한다.
**저장소 / 격리 브랜치:** \`degong2-code/simc-secondary-optimizer-runner\` / \`probe/chat-cache-v035-20261024\`.
**인계 작성 전 읽기 전용 확인 HEAD:** \`0e592afae1e5b131ed1786776a511aff004977f2\`; \`main\`: \`07133e0aaf738d6e4816a6486057b1cd49c018de\`.
**최신 기능+시험 SHA:** \`a831bbfdea07a10f50ef85cf1f49c79aa0506b74\` (P3-BO). \`0e592afa...\`는 그 위의 **문서 전용 커밋**. 이 인계 자체를 쓰는 다음 커밋 뒤에는 HEAD가 다시 달라지므로 새 채팅에서 **실제 Git HEAD를 다시 조회**한다.
**첫 응답 계약:** 첫 응답은 **읽기·복원·검증 보고까지만**. 사용자 **"진행"** 전에 코드·문서 수정, 커밋, Actions 재실행, Native, 신규 외부 데이터 수집을 시작하지 말고 보고 후 중단한다.

## 1. 최신 승인 정책 — 오래된 문구보다 우선

1. **장기 목표는 기능 하나가 아닌 재사용 가능한 범용 엔진:** 시즌/확장팩마다 동일한 Environment Build에서 콘텐츠·아이템·조건을 신규 발견→원본 수집→동일 시즌/빌드 관계 확인→정규화/품질 검증→G/J/F/O 자동 구축→B/T→검증 선택지 자동 등록→대표 프로필→기존 적응형 SimC 실행. 특정 아이템/시즌에 대한 수동 규칙, 대규모 전체 장비 DB, 다른 최적화 엔진, 효과·proc 재구현, 새 certification Gate는 기본 목적이 아니다. 매 작업에서 "다음 시즌에도 같은 수집/검증/완료 계약이 작동하는가?"를 자가점검한다.
2. **26 DPS 전문화만**(증강 기원사·탱커·힐러 제외). 미래 목표 ilvl 기본 334 또는 사용자 지정 최종 CHMV 총량 T의 **절대 rating**을 SimC DPS 최대화로 탐색. 결과 DPS, SEM/오차, 오직 95% 통계 판정, 관측 1순위, 실질적으로 다른 근접 대안, rating 비율. 관측 최고를 전역 최적 증명으로 포장 금지.
3. **공식 회계:** \`G\` 목표 레벨 대표 일반 비장신구 장비/무기, \`J\` 최고 품질 기본 보석 고정예산, \`F\` 최고 품질 영약, \`O\` 실제 적용 무기 기름 고정벡터. \`B=G+J+F\`, \`T=B+O\`, \`c_final=c_base+o\`. 사용자 수동 최종 T 우선. 기름 O는 fixed/비자유분배이며 gear_*에 **한 번만** 반영, 선택 특수장비 정적 L은 G에 이미 포함/스탯 하한, E는 해당 승인 회계에 따라 한 번만; 장신구 고정 스탯은 자유 G 바깥. 제작 50:50 시작 분배는 L이 아니다. 신규 시즌에 과거 F=165, J=138, 오일/기존 79×2 참조를 자동 복제하지 않는다. 정확한 G Native는 유효한 시즌 참조가 없을 때의 선택적 최소 경로이며 모든 전문화×전 ilvl 전수 Gate가 아니다.
4. **2026-11-03 최신 사용자 캐릭터 결정(P3-BN):** 사용자 특성 명시→그 값, 미입력→기존 검증된 전문화별 대표 특성. 사용자 종족 명시→그 값, 미입력→**dwarf**이며 UI에 반드시 "미입력 시 dwarf" 표기. 드루이드·악마사냥꾼·기원사는 dwarf가 불가능하므로 명시 종족 요구, 임의 대체 금지. 캐릭터 레벨은 일반 SimC 프로필에서 \`level=\`을 **생략**하고 해당 컴파일 바이너리의 MAX_LEVEL 기본값 사용. 앞선 P3-BM "확장팩 11/게임 12.x일 때 자체 레벨 90 산출"은 최신 결정에 의해 **폐기/코드 제거됨**; 새 채팅에서 되살리지 않는다.
5. **장비·장신구·장식·보석·음식·물약·영약·기름·영구 마부·선택 모듈 등, DPS나 CHMV에 영향을 주는 아이템 입력/선택·정확한 ID·품질·조건·계산 소유권은 전부 우리 환경 엔진.** SimC는 기본 APL, 게임 효과/proc 및 DPS, 원본 참고·최소 Native 정적 rating 확인을 담당. SimC 시즌 샘플 프로필은 ID/구조/특성의 **선택적 참고 공급원**일 뿐 사용자 장비/소모품·예산을 무단 복사하지 않는다. 최고 품질은 동일 효과/조건/범위·수치 비열등을 입증한 중복 품질만 숨김. 영구 마부는 지원; 일반 임시 마부 제외; **무기 기름**은 지원. 확장팩 특수 시스템은 선택 모듈로 분리.
6. **캐시·권한:** 같은 시즌 정적 아이템 캐시는 SimC revision 변경만으로 폐기하지 않는다. 실행 바이너리 SHA/revision, 캐릭터·APL, 프로필, 전투, 후보, O, iterations에 따라 DPS 캐시 분리(P3-BE/BF). 기존 v217 SHA 단계 영수증, 캐시·취소·재개 유지. 승인 v1.4.3 + DPS26 교정 + P3-AA + 사용자 11/3 직접 결정이 역사 v1.4.1의 "27 DPS" 또는 P3-BM의 자체 레벨 조건보다 우선.
7. **P3-AA 최종 인수:** 완성 후 **같은 정상 Environment Build 엔진**을 현재 시즌의 옛 DB/캐시/ID seed/영수증 없는 신규 데이터 상태에서 실행. 정상 신규 Wago·Blizzard·WCL·SimC·공개 소스 다운로드는 허용. 테스트 전 기존 시즌 답으로 보충 금지; 출력 먼저 봉인 후 독립 비교. 별도 "SimC-only 최종 엔진"이나 네트워크 차단 시험 아님.

## 2. 필독·복원 순서 (중복 최소화)

1. **이 문서 전체** (\`docs/CHAT_CONTINUITY_HANDOFF_20261103_P3_BO_ENGINE_GJFO_NEXT.md\`). 반드시 현재 HEAD·main을 GitHub에서 별도로 확인.
2. \`docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md\` **최상단 최신 P3-BO→BN→... 요약**. 파일 하단 오래된 대규모 이력은 역사 스냅샷; P3-BF 시점 인계보다 이 문서가 최신.
3. 설계 권위: \`docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md\` → \`docs/DPS26_SCOPE_CORRECTION_20261031.md\` → \`docs/P3_AA_20261102_SINGLE_ENGINE_FRESH_SEASON_CONTROL_ACCEPTANCE.md\` → \`docs/DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md\`. 이 문서의 11/3 최신 캐릭터·SimC 책임 직접 결정은 해당 승인 문서와 함께 우선 적용.
4. 최신 세부 구현: \`docs/P3_BO_20261103_PINNED_SIMC_V189_WAGO_V190_CONSUMABLE_STAGE.md\` 및 \`docs/P3_BN_20261103_SIMC_DEFAULT_LEVEL_OPTIONAL_CHARACTER_AND_ENGINE_OWNED_ITEMS.md\`. 예산 준비 \`docs/P3_BG_20261103_PREPROFILE_GJFO_ACCOUNTING_BRIDGE.md\`; 보석 \`docs/P3_BH_20261103_FRESH_SEASON_GEM_SOURCE_JOIN_IN_NORMAL_BUILD.md\`; 장비 출처 \`docs/P3_BI_20261103_SELECTED_GEAR_SEASON_PROVENANCE_AND_G_PENDING.md\`; G 물리 프로필 \`docs/P3_BL_20261103_ONE_SPEC_V233_G_PROFILE_IN_ORIGINAL_ENVIRONMENT_BUILD.md\`; 실행 v234 \`docs/P3_BM_20261103_OFFICIAL_EXPANSION_LEVEL_AND_V234_SOURCE_REPLAY.md\`의 **레벨 설계는 역사/최신 BN으로 덮임**. WSE 연구 \`P3_BJ/P3_BK\`는 참고만: 사용자 판단으로 **추가 전용 WSE 판별 연구 종료**.
5. 원본·과거 근거가 필요한 경우에만 \`docs/P3_BA_20261103_REAL_WAGO_SIMC_ONE_SPEC_SOURCE_COVERAGE.md\`, \`docs/P3_BF_20261103_ENV_BUILD_SESSION_SIMC_REVISION_BRIDGE.md\`, 과거 \`docs/CHAT_CONTINUITY_HANDOFF_20261103_P3_BF_ENGINE_GJFO_NEXT.md\`, 기존 Source/Native 기록 참조. 수십 개의 역사 회귀를 재감사하지 않는다.
6. 최신 실제 구현 \`runner/v113_local_web_api.py\` → \`v106_user_session_controller.py\` → \`v216_environment_build_coordinator.py\`, \`v217_stage_execution_engine.py\`; 신규 시즌 물리 \`v161/v163/v165/v166/v167/v232/v233/v234/v236\`, 티어 \`v245/v250/v251\`, 보석 \`v221\`, 소모품 \`v189/v190\`, 증거 재고 \`v224\`, 회계 \`v222\`, 카탈로그/프로필 \`v196/v212/v098\`, 적응형 v093–v095. GitHub Actions의 **jobs 및 logs**에서 SHA/OS/건수/실제 Native 범위를 대조한다.

## 3. 가장 최근 개발 P3-BG→BO: 구현과 한계

| 범위 | 코드·CI로 완료한 구체 내용 | 여전히 미완료 |
|---|---|---|
| **P3-BG** | 원본 \`v222.preprofile_budget\`를 프로필 전 회계로 분리, \`reconcile\` 유지, 소스 미인증 시 숫자/READY 불승격 | 실물 G/J/F/O 공급 |
| **P3-BH** | 같은 빌드 v161+v221 보석 \`gem_property\`→아이템 ID 관계와 v217 봉인 | 최고 품질 J/소켓/실제 rating |
| **P3-BI/BJ** | v163→v167의 DisplaySeason/WSE·journal source identity 보존; 조건부 M+는 **내부만** 보관, 사용자 선택·G 승인 금지 | 실제 선택 부위/티어 시즌 소속 및 G |
| **P3-BK** | 실제 동일 빌드 Wago JournalEncounterItem 23,991행, WSE 양수 606행(2.53%); 같은 아이템에 조건부/무조건부 행 공존 | WSE는 시즌 드롭 확정 구분자가 아님; **사용자 결정으로 추가 연구 중단** |
| **P3-BL/BM** | 기존 v216→v232→v233 G Native 입력 준비, v234 같은 v167 DB exact replay, 요청별 v217 cache 분리, v113 사용자 입력 연결 | 신규 시즌 실제 G 측정/인증; P3-BM 레벨 매핑은 최신 BN으로 폐기 |
| **P3-BN** | SimC 컴파일 기본 레벨에 맡김, 종족/특성 생략 UI 정책 적용, v233/v234/v236 봉인 호환·Native0 regression, SimC 업로드에서 장비/소모품 미복사 | 새 시즌 대표 특성의 실제 적합성은 별도 보증 아님 |
| **P3-BO** | \`v216._fresh_consumable_item_source_stage\`가 기존 pinned SimC \`v189\`의 \`unique_gear_midnight.cpp\` 소스 **작은 파일 1개**와 동일 빌드 Wago v161 Item/ItemSparse를 이용해 **기존 v190 음식·물약 item 후보를 조인**, v217 봉인·요청 재사용·소스 drift 차단. \`fresh_food_potion_item_sources\` 반환. | **음식/물약 후보 원본만**, F 영약/J 보석/O 기름 수치 아님. 품질·정확 입력·영약 적용·UI 정책 A 미승인, G/J/F/O/B/T/READY 여전히 NULL/false. 신규 실제 HTTP/Native 실행 증거 아님 |

**현재 제품 판정:** 정상 사용자의 신규 시즌 요청에서 실제 동일 시즌 G/J/F/O→B/T→최고 품질 Policy A→READY/설치→기존 적응형 SimC 최종 결과까지 한 번에 증명하지 못했다. 개별 소스 단계 PASS를 전체 제품 완료로 표시 금지. 이전 동일 시즌 v223/79×2 참조를 새 시즌 값으로 이식하거나 과거 PvP 원본 \`G=2847\`을 재사용하지 않는다.

## 4. GitHub·원본·Native·CI 증거의 엄격한 적용 범위

### 최신 실행 코드·Actions (GitHub jobs/logs 2026-11-03 대조)

- P3-BO **기능+테스트 SHA \`a831bbfdea07a10f50ef85cf1f49c79aa0506b74\`**:
  - [v212 #41564705945](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41564705945): Ubuntu 24.04와 Windows 2022 각각 **430 tests / 0 FAIL / 4 SKIP**, Native0 검사 PASS.
  - [v113 #41564705863](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41564705863): 양 OS 각각 **206 tests PASS**.
  - [v181 #41564705853](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41564705853): Windows Python 3.12/3.14 각 **142 PASS**, 기존 **로컬 loopback HTTP** 3-plans restore Native0.
  - [v182 #41564706079](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41564706079): 양 OS 각각 **92 + 82 + focused 2** UI 테스트 PASS.
  - 중간 \`7797a62...\`, \`e949ca7...\` 수정 전 [v212 #41564545830](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41564545830) 및 v113 #41564545841 등에서 synthetic source transport **예상 7 vs 관측 9** 요청 수 단언이 실패한 이력을 보존; 테스트 입력을 업데이트하고 최종 CI PASS. **Mocked transport 8 first pass, repeat 0 additional**은 제품 실제 네트워크 호출량을 측정했다는 뜻이 아니다.
- P3-BN 최종 코드 SHA \`3c781c12a275a1e7edb08af548a5119f61aafae2\`: v113/UI/Windows 6개 관련 CI SUCCESS, 실제 신규 Native0. P3-BG/BH/BI/BJ/BL/BM은 별도 파일의 SHA와 범위·실패 이력 참조. **P3-BO에서 새 실제 외부 Wago/SimC/Blizzard HTTP 수집 0회, 새 실제 Native 0회**.
- 역사 실원본(재사용 증거): Wago 빌드 \`12.1.5.70575\`와 SimC Git 소스 \`710c2408bfd3ae4df71b8cd55cdf01f63fd6c926\` 기준, 기존 P3-BA에서 징벌 성기사 13부위 후보/정적 물리 cross-check **328/328**. 과거 13직업 × 5티어 ID 대조, **26 DPS Native 프로필 물리 PASS**(26번 실제 적응형 DPS 최적화 아님). \`G=2847\`은 과거 PvP 혼합으로 **유효한 대표 G에서 제외**. P3-BK에서만 이 대화 중 실제 Wago Journal 3테이블 재수집 조사 완료; 시즌 WSE 전용 판정기 확대는 불허.
- **증거 분류:** A. 사용자 정책 승인, B. GitHub 코드·focused/합성 CI, C. 실제 Wago/SimC 원본 SHA/빌드, D. 실제 Native JSON2/바이너리, E. 재사용 역사 증거, F. 미구현/미승격. 원본 행의 발견이나 handler 등록은 최고 품질·실제 효과 조건·UI 사용 가능성 인증 아님.

## 5. 바로 다음 구현 (제안 별칭 P3-BP, 아직 개발 완료 아님)

**대상: 원래 \`v216\` 정상 Build의 동일 빌드 G/J/F/O를 실제로 확정해 기존 \`v222.preprofile_budget\`에 전달하는 누락 구간.**

- **병렬 묶음 G:** 실제 한 DPS 전문화(예: 징벌 성기사)·목표 ilvl 334부터. 선택 대표 일반 장비/무기/티어 4세트의 **실제 활성 시즌 소속, 슬롯, 정확한 변형** 확인. 기존 v163·v166/167·v232·v245/250/251·SimC 원본/샘플은 **후보/구조 증거**로만 활용; 샘플 프로필 장비/현재 스탯을 그대로 G로 승격 금지. 유효한 시즌별 G 참조 우선, 필요 부위에 한정하여 기존 v233/v234/v236 또는 v226–v228/v046의 **최소 Native**. G 수치·정확/근사·시즌/빌드/ilvl/장비·기름/마부·출처를 seal, 실제 사용자 READY는 모든 필수 예산 충족 전까지 보류.
- **병렬 묶음 J/F/O:** 기존 v221 gem ID↔gem property 조인, v189/v190 음식·물약(선택 옵션), 기존 v191/v196/v220/SimC 소스에서 같은 시즌 **최고 품질 기본 보석 J, 영약 F, 무기 기름 O**의 실제 아이템 ID/효과·정적 rating/품질 동등성/적용 무기 손을 정합. 영구 마부 E·선택 L의 귀속은 독립 확인. 일반 임시 마부는 제외. 필수 예산 미확정은 READY 금지, 선택적 음식/물약 미인증은 **그 항목만 보류**.
- **공통 접합/한 꼭지 완료:** 두 묶음이 **동일 빌드/시즌/SimC 소스 identity**와 인수 가능한 검증 영수증을 만들면 기존 \`v222.preprofile_budget\` 호출→\`B=G+J+F\`, \`T=B+O\`, 수동 T 우선, L/E/O 한 번만→\`v222.reconcile\`→v212/v098 환경 설치·정확 대표 프로필→기존 adaptive SimC와 user UI. 이미 있는 \`v224\` inventory에서 **진짜 부족한 증거만** 보완. 자동 Policy A는 증명된 최고 품질·정확 조건만; 숫자 없는 합성 self-declared proof로 READY 우회하지 않는다.
- **효율 검토:** 같은 시즌 DB2/SimC 핀 원본·v217 receipt·동일 시즌 정적 캐시 재사용, HTTP/Native 중복 제거, 소스 단계 입력 SHA·캐시 무효화 영향 검토. 독립 G와 J/F/O는 **한 개발 묶음 안에서 병행**, 출처·통계·UI 인증은 독립 판정. focused CI→변경 범위의 최소 실물 수집/Native만 실행. 모든 26 전문화×전 ilvl·모든 아이템 전수 재수집/재시험 금지. WSE 표현식 전용 전수 해석기·별도 시즌 엔진·SimC 샘플 소모품 수입 금지.

**이번 즉시 한 꼭지 완료 정의:** 실제 동일 시즌/빌드에 대해 (a) 대표 13/14부위·티어의 승인 가능한 G 또는 유효 참조 영수증, (b) J/F/O 각각의 독립적인 정적 수치·품질·적용 조건 근거, (c) 이 네 항목을 기존 v222에서 모순 없이 계산하고 중복 회계를 검증한 영수증이 다음 실행에 재사용 가능하게 생산됨. 단순 코드/CI PASS나 음식/물약 후보 수집만으로 해당 꼭지 완료가 아니다.

## 6. 간결한 장·단기 로드맵과 효율적 대안

- **단기 P1:** 같은 정상 Build의 선택 대표 장비·티어 → G와 독립 J/F/O 실제 시즌 수치 증거 확보; v222에서 B/T 완료 (현재 최우선).
- **단기 P2:** 최고 품질 정책 A 자동 선택지 등록, 검증된 필수 환경만 READY/설치, 사용자 선택 항목별 보류.
- **중기 P3:** 일반 사용자의 Build→내부 대표 프로필→기존 적응형 SimC DPS·SEM·95%·대안·캐시/취소/재개를 한 전문화 실제 E2E로 확인.
- **장기 P4:** P3-AA 기존 자료가 완전히 빈 상태에서 동일 단일 실사용 엔진으로 새 시즌 환경을 재구축하고 봉인 후 독립 검증, 이후 26 DPS·시즌 변경 보편성 확장.

**대안 평가:** 광범위한 WorldStateExpression 조사, 종족/레벨 추론기, 전 아이템 재수집, 새 효과/APL·최적화 엔진, 불필요한 G Native 전수화보다 기존 v216 수집·검증·v217 캐시·v222 회계의 **누락된 타입/영수증 접합**을 우선하는 것이 단순하고 빠르며 정확한 재사용 경계다.

## 7. 권한, 전달, 미승격·불변 경계

- 이 인계 준비의 GitHub 쓰기는 **격리 브랜치 문서 3개 범위**(신규 인계 정본, CURRENT 포인터, 개발자 실행 노트 포인터). 제품 코드, \`main\`, immutable v003, 원본 \`v016_SCENARIO_CONTRACT\`, 공식 Project Instructions/Sources UI, Work OS M0/Shared State, WEQUIP authority는 변경/승격하지 않는다.
- v1.4.3은 승인 정책이며 **본문을 재작성하지 않는다**; 개발자 실행 노트에 최신 캐릭터 정책과 이 인계 참조를 추가할 수 있다. GitHub 문서 작성 ≠ ChatGPT Project UI 등록. 원본 v016의 실제 바이트/receipt 독립 직접 통합 완료 **미확인**, 제품 최신 원본 기준선이라는 사용자 보고만 유지.
- "현재 주 개발 채팅 소유"라는 이전 정책을 새로운 MAIN/Work 운영권 이전으로 해석하지 않는다. 사용자가 직접 **새 채팅 인계**를 요청했으므로 새 채팅은 기록을 읽고 복원 보고한 뒤 사용자의 **'진행'** 지시를 받을 때까지 코드를 수정하지 않는다. 이후 범위 허용 시 격리 브랜치의 기존 엔진 개발을 이어가며 별도 main/공식 승격 권한을 주장하지 않는다.
- 과거 BF 인계는 역사 정본으로 남긴다. **이 파일 하나를 새 채팅에 전달하고, 나머지 문서는 위 링크/읽기 순서로 참조**한다. 파일 본문을 다중 첨부나 여러 복제 인계에 중복 삽입하지 않는다.
- 이번 인계의 증거 감사 자체는 **새 코딩·Native·실 외부 게임 DB 수집이 아니며** 별도 제품 CI 통과로 주장하지 않는다.

## 8. 새 채팅 시작 프롬프트 (전문 복사)

> **SIMC SECONDARY OPTIMIZER — P3-BO 이후 단일 Environment Build 엔진 복원 요청.**
>
> GitHub 저장소 \`degong2-code/simc-secondary-optimizer-runner\` 격리 브랜치 \`probe/chat-cache-v035-20261024\`의 **현재 실제 HEAD**를 먼저 확인하고, 최신 인계 정본 \`docs/CHAT_CONTINUITY_HANDOFF_20261103_P3_BO_ENGINE_GJFO_NEXT.md\` **전체**를 읽어라.
>
> 그 문서의 순서대로 CURRENT 최신 부분, 승인 개발자 노트 v1.4.3, DPS26 교정, P3-AA 단일 엔진 최종 통제실험, 개발자 실행 보충 노트, P3-BO/P3-BN 및 필요한 P3-BG~BM 근거를 읽고, 현재 실제 GitHub HEAD·main, 기능 SHA와 문서 SHA, Actions **jobs/logs** 및 역사 실제 Wago/SimC/Native 영수증의 범위를 비교해라. 승인 정책과 실제 구현·CI·Native·READY·Project UI 승격을 혼동하지 마라.
>
> **프로젝트의 최종 목표는 시즌별 개별 기능 구현이 아니라, 새 시즌의 원본·아이템·선택지·G/J/F/O를 반복적으로 발견·수집·검증·구축·갱신하는 하나의 범용 Environment DB 구축 '엔진' 개발이다.** 모든 구현 전후에 이 장기 목표를 지속적으로 **자가점검**하라. 동일한 데이터 계약·출처·검증 기준과 재사용 가능한 완료 판정을 유지하라.
>
> 다음 우선 개발은 검증된 시즌 대표 일반 장비·무기·티어→정확 G 및 별도로 검증된 최고 품질 J/F/O→기존 v222 B/T→정책 A→사용자 내부 대표 프로필→기존 적응형 SimC DPS/SEM/95%/근접 대안이다. **독립적인 G와 J/F/O 작업은 효율적으로 묶어 수행**하되 근거/완료 검증은 분리하고, 동일 기준의 완료 검증을 **재사용**하라. 불필요한 전수 원본/Native 반복·WSE 추가 연구·기존 탐색기 재개발·새 효과 엔진을 금지한다. HTTP/Native 호출, 캐시 정체성/무효화, 메모리, I/O, 소요시간, 구조 단순화를 매 변경마다 검토하라.
>
> 최신 캐릭터 정책은 SimC 기본 MAX_LEVEL(일반 \`level=\` 생략), 종족 선택 입력/미입력 **dwarf** 명시(불가 직업은 사용자 명시 종족 필요), 특성 선택 입력/미입력 기존 검증 대표 특성이다. 장비·장신구·장식·영약·보석·기름·마부 등 **모든 최적화 영향 아이템 입력과 회계는 우리 환경 엔진이 통제**하고 SimC가 효과·APL·DPS를 계산한다. 제품은 **26 DPS만**, 기본 ilvl 334/사용자 최종 T, \`B=G+J+F\`, \`T=B+O\`, O 단 한 번 반영, L/E 중복 금지, 95% 통계만 사용.
>
> **첫 응답에서는 반드시 복원·검증만 수행하라.** 장기 목적, 간결한 장·단기 로드맵, 직전 P3-BO에서 실제 구현된 것/미구현, 최신 브랜치 HEAD·main·CI·실원본·Native 영수증의 적용 범위, 현재 가장 큰 장애와 더 효율적인 다음 작업, 권한·미승격 항목을 보고하라. 보고 후 **즉시 중단하고 사용자 '진행'을 기다려라.** 그 전에는 코드/문서 편집·커밋·Actions·Native·신규 외부 원본 수집을 하지 마라. 사용자의 별도 지시 없이 \`main\`, immutable v003, 원본 v016, Project UI, Work OS 또는 공식 Shared State를 변경하지 마라.

**끝 — P3-BO 최신 인계.**
