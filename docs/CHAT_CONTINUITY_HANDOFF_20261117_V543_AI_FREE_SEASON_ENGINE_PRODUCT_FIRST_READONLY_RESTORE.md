# SIMC SECONDARY OPTIMIZER — v543 이후 범용 시즌 엔진 최우선 / 최신 GitHub 독립 복원 인계

**기록일:** 2026-11-17 KST · **인계 스냅샷:** `probe/chat-cache-v035-20261024` @ `201be9ef1671607fdd6b265242c1ad3cc0333127` · **신규 대화의 첫 응답:** READ-ONLY 7항목 보고 후 STOP.

> **핵심 목적:** WoW 26개 DPS 전문화에서 **미래 파밍 목표의 치명·가속·특화·유연 절대 rating**을 기존 적응형 SimulationCraft DPS로 탐색하는 **실제 사용할 수 있는 프로그램**을 완성한다. 특히 **새 시즌·확장팩마다 AI 호출 없이 동일한 제품 Environment Build 엔진이 필요한 시즌 원본/대표 장비/G/J/F/O를 자동 수집·검증·설치하도록 하는 범용 기능이 최우선**이다. 현 시즌 자료를 더 수집·수작업 등록하는 프로젝트가 아니다. 기존 정상 코드·원본·Native·캐시를 재사용하고 제품이 쓰지 않는 데이터/효과/옵션 검증은 만들지 않는다.

## 1. 읽는 순서, 권한, 최신성

1. GitHub `degong2-code/simc-secondary-optimizer-runner`, `probe/chat-cache-v035-20261024`의 **최신 ref HEAD/최근 Actions**부터 독립 재조회한다. 위 HEAD는 작성 당시 스냅샷이며 고정 정본이 아니다.
2. **본 문서** → `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` **최신 최상단** → `docs/development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md` → `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json`.
3. `docs/development/INDEX.md`, `FILE_MAP.md`, `EVIDENCE_INDEX.md`, `POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`, `PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md`를 실제 작업에 필요한 부분만 읽는다.
4. 승인 정책 `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md` 및 최신 사용자 직접 결정을 우선한다. v1.4.1의 **27 DPS/증강 기원사 포함** 등 오래된 조항은 최신 **26 DPS/증강 기원사 제외**에 반한다.
5. `docs/CHAT_CONTINUITY_HANDOFF_20261117_V535_PRODUCT_PRIORITY_READONLY_RESTORE.md`, `LAST_Q&A(6).txt` 및 과거 인계들은 역사를 보완하는 자료이며 최신 상태나 우선순위에 우선하지 않는다. 업로드된 마지막 대화 기록에는 **v543 완료, 실제 신시즌 E2E 미실행**이 적혀 있다.

**우선권:** 최신 사용자 직접 결정 > 최신 승인 정책 > GitHub 실제 코드·CURRENT·Actions·Native 영수증 > 역사 기록. 승인 설계·오프라인 코드 PASS·실제 Native·Windows 브라우저 E2E·공식 제품 수락은 별개의 지위.

**권한:** 격리 브랜치 내 사용자 별도 `진행`에 따른 최소 개발은 가능. `main` 병합, v003 immutable, 원본 v016 제품 직접 통합 완료 주장, Project Sources/Instructions UI 실제 적용, 공식 Work OS M0·Shared State 승격·MAIN/WORK의 개발 주도권 이전은 **별도 사용자 권한 필요**. 이 인계 문서 기록은 그 어떤 승격도 뜻하지 않는다.

## 2. 불변 제품 정의와 사용자 흐름

- **지원:** 딜러 26개 전문화만; **증강 기원사·탱커·힐러 제외**. 목적함수는 SimC DPS 최대화. 95% 통계 판정만 사용.
- **입력:** 직업/전문화/종족/특성, 새 시즌 기본 목표 ilvl 또는 사용자가 지정한 ilvl·**기름 포함 최종 T**, 장신구 2개, 선택 특수/제작장비·장식 최대 2개, 보석·최고 품질 영약·음식·물약·기름·영구 마부·전투조건. 캐릭터 SimC 업로드는 선택 기능.
- **내부:** 사용자 전체 착용 장비를 요구하지 않고, 목표 시즌 일반 대표 장비/무기·주능력치·티어4pc·SimC 기본 APL 프로필을 스스로 구성한다.
- **출력:** 치명/가속/특화/유연 **최적 관측 절대 rating**, 스탯 비율, DPS·SEM/오차, **관측 1순위와 95% 우위 확정 여부의 구별**, 실질적으로 다른 근접 대안, 실행 조건·캐시·보존된 결과. 전역 최적해를 입증한 것으로 표현 금지.
- **공식 수식:** `G`=대표 일반 장비·무기, `J`=기본 보석, `F`=최고 품질 영약, `O`=무기 기름의 **고정/비자유분배**; `B=G+J+F`, `T=B+O`, `c_final=c_base+o`. 사용자 수동 최종 `T`가 **무조건 우선**하고 `B=T-O`로 환산. 정적 고정 `L/E/O`는 승인된 소유 회계 내 **한 번만**; 수동 T의 E는 T 내부 스탯 하한이지 추가 가산 아님. 장신구 고정치는 자유 G 밖, 누락 gear 정적 레코드는 0으로 단정 금지, 제작장비 50:50 초기 스탯 잠금 금지.
- **책임:** SimC가 장비 효과/proc/APL/DPS를 계산. 프로그램은 정확한 ID·ilvl·옵션·시즌/빌드, 예산/고정 하한/JSON2 rating, 후보 스케줄·SEM·95%, 정적/DPS 캐시·취소/재개·출력을 담당. **제품 런타임 AI 호출·판단 0회**.
- **범위 밖:** 현재 장비 재분배, 장비 추천·파밍 경로, 시즌 전체 장비 DB, 새 최적화/효과/APL 엔진, 전수 스펠 메커니즘·발동 인증, 미사용 모든 옵션 테스트, 26 전문화×아이템레벨 Native 전수.

## 3. 최우선 개발 목표: AI 없는 **단일 범용 Environment Build 엔진**

**최우선 P0:** 새 시즌/확장팩에서 실제 제품의 **동일한 단일 엔진**이 AI 없이 `시즌·빌드/기본 ilvl 판정 → 해당 시즌 원본 신규 수집(Wago DB2/Blizzard/WCL/공개 GitHub·Localbots/SimC) → 동일 빌드 대표 장비·양손 무기 형태·티어/정적 예산 → G/J/F/O 검증 → B/T·고정 L/E/O → 최고 품질·영구 마부·유효 선택지 자동 등록(정책 A) → 내부 설치 v212·사용자 대표 프로필 → 기존 적응형 SimC`를 처리하도록 완성한다.

- **새 시즌 수치를 현재 시즌 70783의 G2850/J92/F165/O0·ilvl334·79×2 참조표·옛 기름16/16로 복사하지 말 것.** G부터 포함해 새 시즌의 실제 소스와 유효 영수증으로 다시 결정한다.
- **일반 25개 vs 분노 전사 Fury Titan's Grip 2×양손 무기의 두 G 트랙**은 유일한 별도 G 구조. 공통 실행/프로필 로직은 재사용하되 시즌 별 G 숫자/물리 무기 원본은 정확 분리한다. 과거 전문화 Native 성공을 신시즌 26개 Native PASS라고 승계하지 않는다.
- 최고 품질 중복 제거는 **동일 효과·사용 조건·적용 범위가 검증된 경우만**. 일반 임시 마부는 지원 제외, 무기 기름은 예외로 계속 지원. 확장팩 고유 특수 콘텐츠는 **ON/OFF 선택 모듈**, AI/GPT를 런타임 자동 호출하지 않는다.
- **정책 A:** 정확한 ID/빌드·SimC 입력·범위·예산 소유권 검증 후 별도 항목별 수동 승인 없이 자동 등록. 후보 존재/핸들러 존재만으로 노출 금지.
- 기본 필수 G/J/F/O가 실제 미확정이면 READY 불가. **미선택 선택 옵션만 PENDING이면 그 옵션만 보류**하고 검증된 BASE의 사용자 SimC는 계속 사용 가능해야 한다.
- ZERO-SOURCE 최종 통제시험은 **별도 전용 엔진이 아니라 일반 사용자의 실제 단일 Build**를 깨끗한 데이터 상태에서 실행하되, 신규 Wago/Blizzard/WCL/SimC **정상 수집은 허용**한다. 기존 시즌 캐시/정답 자료 입력만 격리. 산출물 봉인 후 대조한다. 코드 생성/Actions PASS만으로 이 통제시험 성공 선언 금지.

## 4. 실제 완료 증거 vs 미완료

**재사용할 역사 실측(원 범위에서만 유효):**
- `12.1.5.70783` 및 목표 ilvl334의 기본 시즌 원본, **G2850/J92/F165/O0 → B=T3107**, `v113→v216/v217→v277/v281→v222→v212→v098/v096` Windows 실제 GJFO/Native 설치 성공(v524 계열). 같은 조건의 새 측정 불필요.
- v525~v527 장신구·특수/제작/장식2·티어4pc **각 정확한 시나리오** Native; 다른 모든 옵션과 동시에 승인 아님.
- v528 E 정적 실증, v530 E0, v532 8025 가속 E30, v533 7965 특화 E26, v534 **사용자 수동 최종 T3200+8025 E30** 실제 Windows Native6·DPS·SEM·95%·cache-only 재실행 성공. [v534 실제 Native](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43974259684), [v534 compact](development/research_receipts/p1_v534_70783_manual_T3200_8025_E30_user_native_compact.json). **전 시즌/전문/동시 모든 조합의 승인 아님**.
- v535 UI의 정확한 반지1 마부 7967/8025/7965 표시·계획 API 연결은 Windows/Ubuntu **오프라인 PASS**. 실제 설치된 브라우저 catalog→선택→plan→start→result **미실행**.
- 추가 소켓 5/6개는 실제 적용·J 소유권 근거 부족하여 **미승인**. 이 옵션 때문에 4소켓 BASE 차단 금지.

**최근 코드와 오프라인 증거 (v536~v543):**
- **v536~v537:** 신규 시즌 Native 관측 영약 F가 복수 CHMV 스탯(예: 치명80+가속96)일 때도 `v216→v139→v098` source-only로 합계/벡터 전달, 사용자 수동 T 우선. 실제 미래 시즌 Native/최고 품질·옵션 승격 증거 아님.
- **v538~v539:** 과거 `v176` 26전문화 기본 Native 입증을 **새 시즌 전체 Native PASS로 표시/승계 금지**; 검증된 공통 구조·프로필/SimC 실행/캐시 방법만 재사용, 새 시즌에서 실제 바뀐 항목만 최소 확인.
- **v540~v541:** 분노 전사 별도 `fury_dual_2h` G 측정·봉인 원본·기존 `v222/v212` 분리 설치/캐시/user plan 연결. 일반 G/분노 G SHA 섞임 방지. 별도 새 Native 엔진·신규 숫자 하드코딩 없음. **코드 및 합성 오프라인 PASS**, 실제 새로운 시즌 Fury G Native는 미실행.
- **v542:** 신규 시즌 저장 세션 launch/resume/cache-only에서 v212 G 트랙과 전문화 일치 재검증. 일반/분노 자동 및 분노 수동 T 예외 유지. **오프라인 PASS**, 실제 새 시즌 user GUI/DPS E2E 미실행.
- **v543:** 실제 신규 게임빌드의 **완전한 새 G/J/F/O 검증 설치가 현재 없음**을 확인. Fury 자동 T와 정확한 전용 G 설치 없음 시 일반적인 `BUILD_NOT_FOUND` 대신 `WEB_FRESH_FURY_DISTINCT_G_AUTO_BUDGET_SOURCE_REQUIRED`와 한국어 다음 행동 표시. 다른 BASE/분노 수동 T 경로 보호. [v113 Windows·Ubuntu 각 427 PASS/1 SKIP](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43999490708), [focused 674 PASS/2 SKIP](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43999490646), [UI offline SUCCESS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43999446075), [78 정합 SUCCESS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43999742807). 이후 GitHub 최신 결과 독립 확인.

**AI 의존성 최소 감사:** 주요 실제 실행 Python 경로·의존성 파일에서 AI SDK/간접 필수 호출 **발견되지 않음**. 기존 Native 영수증의 런타임 AI0와 구분하고, 전체 저장소의 'AI 의존 없음' 수학적 전수 증명으로 과장 금지. **새 전수 감사/영구 감사 Gate 불필요**. 대신 신규 시즌의 과거 고정값 무단 소비가 실제 나타날 때만 그 위치에서 수정.

**현재 공식 상태:** 78개 계약, `generic PASS 27`, `current_source PASS 27`, `product_integration PASS 15`, `historical PASS 13`; **공식 15/78 COMPLETE**, `full_product_e2e=PENDING`, `next_review=B10`은 원장 검토 포인터이지 제품 다음 작업 우선순위가 아니다. 정확한 근거 없이 계약 값 변경 금지.

## 5. 올바른 최신 우선순위 (구 v535 인계의 'M6 제1순위' 교정)

**지금 개발의 1순위는 범용 시즌·확장팩 Environment Build 엔진 완성**이다. v535 UI 검증은 중요한 사용자 제품 하위 연결이지만 이를 전체 개발 1순위로 바꾸지 않는다.

1. **P0 — AI 없는 단일 자동 시즌 환경 구축:** 실제 새 빌드의 원본을 다시 수집하고 대표 일반/분노 G, J/F/O, 장비·티어·기본 ilvl, 시즌·SimC 출처를 정확 연결. 기존 `v155/v161/v163/v191/v211/v213/v216/v217/v277/v281/v222/v212` 호출자와 결과 소비자를 읽고 **첫 실제 누락만** 수정한다.
2. **P1 — B/T·선택지·사용자 대표 프로필:** 수동 최종 T 우선, L/E/O 중복 방지, 최고 품질/정책 A 및 미검증 옵션 국소 보류, 실제 v098/v096 사용. 무의미한 독립 인증 Gate 신설 금지.
3. **P2 — 기존 적응형 SimC 사용자 실행:** 한 **실제 유효한 신규 시즌 설치**가 확보되는 즉시 기존 v113/v106/v098/v096/v094·캐시·취소/재개·SEM/95%·결과를 사용자 한 건의 전체 경로로 수락. 원본이 없으면 실제 무슨 자료/권한/빌드가 부족한지 정확히 보고하고, 70783 성공을 다시 Native 실행하지 않는다.
4. **P3 — Windows UI/설치와 정확 옵션 흐름:** 기존 v535 마부 선택 포함, 실제 사용자 catalog→plan→start→result 및 결과·캐시/재개를 필요한 첫 사례만 확인. 검증된 BASE를 선택 옵션 미확정으로 차단하지 않는다.
5. **최종 M7:** 실제 단일 엔진의 신규 설치 **ZERO-SOURCE→USER-E2E**와 기존 78 계약의 관련 수락 근거를 최종 평가. M0~M7은 작업 설명용 단계이지 각각 새로운 의무 Gate/Native 전수 실행이 아니다.

**가장 가까운 실제 작업 하나:** 최신 HEAD에서 `v113` 시즌 Build → `v216` 원본 발견/조인 → G(일반 및 필요 시 Fury)·J/F/O → `v222/v212` 설치 → 사용자 v098/v096 프로필 → 기존 SimC/cache 경로를 **하나의 실제 선택된 신규 빌드에 대해** 추적한다. 유효한 새 빌드의 필수 원본/인증 환경이 없으면 E2E 성공을 꾸미지 않는다. 동일 시즌 증거를 더 캐는 대신 **새 시즌에서 제품이 멈추는 첫 필수 수집·검증·설치 접합점**만 해결한다. 그 다음 실제 빌드가 준비됐을 때 정확한 사용자 1건 실행. v535 UI 일괄 재감사/미사용 옵션 전수/분노 G 반복 실험은 하지 않는다.

## 6. 후속 개발의 STOP/REUSE/비용 지침

**`STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW`**. INDEX/FILE_MAP/EVIDENCE_INDEX→실제 생산자/호출자/소비자→CURRENT/Actions/Native/SHA/캐시를 대조한 다음, 실제 필요한 것만 수정한다.

- 매 변경 전에 **사용자 화면/내부 처리의 정확한 위치 → 현재 불편/첫 장애 → 기존 자산 → 만들지 않을 것 → Native·HTTP/DB2·CPU/RAM/I/O/캐시 비용 → STOP**을 간결하게 설명한다. 설명은 별도 승인 Gate가 아니다.
- **'우리 프로그램에 필요한 기능만 작동하면 해당 범위 PASS'**: 실제 소비하지 않는 SpellEffect, 미사용 아이템/전체 마부/전 아이템레벨 검증을 만들지 않는다. 핵심 예산·선택 원본/정적 rating/SimC 실제 실행의 정확성은 절대 생략하지 않는다.
- **선택형 옵션 증거 미확정 ≠ 기본 환경 실행 중단.** 증거가 없는 선택만 차단/숨김. 장신구 정적 record 누락을 0으로 취급하거나 전체 선택 중단으로 승격하지 않는다.
- 기존 70783 Native 및 v535~v543의 오프라인 증거/동일 시즌 캐시를 재사용. **정적 아이템 캐시**는 같은 시즌 SimC revision만으로 무효화하지 않음. **DPS 캐시**는 실제 binary, 캐릭터·프로필/APL, 게임 빌드·장비·장신구/장식·마부 E·기름 O·T·후보·전투조건·iterations·모듈 identity 엄격 분리.
- 과거 Native로 일반 프로그램 구조·무기 슬롯 불변조건을 재사용할 수 있어도 **새 시즌 아이템/GJFO/26개 전문화 Native PASS 선언은 불가**. 전 전문화 재실행 대신 실제 변화가 있는 물리 구조·사용 시나리오만.
- 구현 완료 / 오프라인 PASS / 과거 Native 재사용 / 이번 Native / 실 브라우저 E2E / 공식 원장 COMPLETE를 **항상 별도로** 보고한다. 첫 실제 결손이 해결됐으면 STOP; 오류가 없으면 중복 코드를 만들지 않는다.
- 원본 소스 오류·SimC 오류는 실제 문구대로 전달. 출처를 못 읽었으면 **미확인** 처리, 이름/품질/아이템 ID/시즌 값을 추정하지 않는다.

## 7. **새 채팅 첫 응답 계약: 읽기 전용 독립 복원 후 STOP**

새 채팅은 위 실제 GitHub URL을 연결해 최신 ref·CURRENT·78 JSON·Actions/Native/시즌 원본을 **읽기 전용**으로 재조회한 후 아래 **7개만** 보고한다.

1. 정확 최신 브랜치·HEAD·Actions SUCCESS/FAIL/CANCELLED/SKIP를 최신 head별로 분리.
2. 실제 사용 가능한 기능과 신규 시즌 일반 사용자 경로의 첫 장애/미완료.
3. 기존 시즌 원본/Native 실증 vs v536~v543 코드·오프라인 회귀 vs 새 시즌 Native/Windows GUI E2E 미실행의 구분.
4. M0~M7 위치, 공식 78개 원장 상태·`full_product_e2e`.
5. 필수 환경 G/J/F/O·선택 기능·AI 없는 실행/캐시·일반/분노 G 구분의 실제 결손과 국소 보류.
6. **가장 중요한 다음 사용자 제품 작업 하나**, 기존 생산자·소비자·Native/HTTP/DB2/캐시 비용/STOP.
7. 불명확한 원본·상충 정책·GitHub/Project UI/Work OS/main/immutable·원본 v016 권한 경계.

**첫 응답에서는 GitHub 코드/문서 수정, 테스트·Actions·Native·HTTP/DB2 수집 실행, 커밋·병합 금지.** 일곱 항목 보고 후 **STOP**. 다음 메시지에서 사용자가 별도로 `진행`이라고 해야 최신 HEAD/첫 실제 장애를 다시 확인하고 격리 브랜치 최소 개발을 재개한다. 

---
**인계문서 자체는 새 시즌 Native PASS, 78개 계약 상태 변경, 제품 완성, UI Project Source 실제 등록이나 운영 권한 이전의 증거가 아니다.**
