# SIMC SECONDARY OPTIMIZER — P1 v677 최신 독립 복원 / 결과 우선 인계 정본

2026-11-23 KST. 인계 문서만 작성하며 제품 코드·시즌 원본·캐시·Native·Actions·공식 상태를 변경하지 않는다.

> **시작 정본:** repo \`degong2-code/simc-secondary-optimizer-runner\`, isolated branch \`probe/chat-cache-v035-20261024\`, 본 인계 작성 직전 확인된 HEAD \`718bfe63a3ba97910176f639ae6a6991ca976266\`. 이 SHA는 당시 스냅샷일 뿐이다. **새 채팅은 가장 먼저 최신 HEAD와 CURRENT를 다시 확인한다.**
>
> **새 채팅 첫 응답:** READ-ONLY 독립 복원 → 아래 **7개 항목** 보고 → **STOP**. 별도 사용자 \`진행\` 전에는 새 코드/문서 변경, Actions/Native/HTTP/DB2 시험, 공식 승격 금지. 인계 자체는 기존 주 제품 개발 채팅의 권한 이전이 아니다.

## 1. 제품의 최상위 목적과 사용자 가치

**26개 DPS 전문화만 지원한다.** 증강 기원사·탱커·힐러는 개발 범위 밖이다. 미래 목표 ilvl(현재 기본 334) 또는 사용자가 수동 지정한 최종 T에서 실제 **SimulationCraft DPS를 최대화하는 치명/가속/특화/유연 CHMV 절대 rating**을 찾는 Windows 프로그램이다. 결과는 관측 1순위, 절대 rating/비율, DPS·SEM·95% 통계적 판정, 실질적으로 다른 근접 대안, 취소·재개·캐시·저장·재열람을 포함한다. \`global_optimum_proven\` 없이 전역 최적이라 주장하지 않는다.

일반 사용자: 직업/전문화/종족/특성, 목표 ilvl 또는 수동 T, 장신구 2개, 선택 특수효과 장비·장식 최대 2개, 보석/영약/음식/물약/기름/마부/전투 조건 입력. 전체 현재 착용 장비와 현재 CHMV 합계는 입력하지 않는다. 내부 대표 일반 장비·무기·티어 4세트·주능력치·기존 SimC APL을 사용한다. 개인 SimC 프로필 업로드는 선택적 캐릭터/특성 불러오기이며 현재 장비를 목표 예산으로 복사하지 않는다.

**정식 제품 경로:** 사용자 입력 → 필요한 SimC 및 같은 시즌 G/J/F/O 환경 확보·검증 → B/T·선택 고정치 회계 → 내부 대표 프로필 생성 → **이미 구현된 적응형 SimC 탐색** → 절대 rating/DPS/SEM/95%/대안·캐시·저장·재열람.

\`B=G+J+F\`, \`T=B+O\`, 수동 최종 T 우선(\`B=T-O\`), \`c_final=c_base+o\`. 기름 O 비자유분배·중복 가산 금지, 선택 특수장비 고정 L은 G 내부이며 하한만 보호, 정적 마부 E도 승인된 owner에 따라 1회만 반영. 장신구 정적 기여는 자유 G 밖이며 미관측을 0이라고 단정하지 않는다. 제작장비 초기 50:50은 L이 아니다.

새 시즌 G/J/F/O **모두 그 시즌 소스와 증거로** 자동 산출한다. 이전 70961 또는 과거 79×2 참조 숫자를 새 시즌의 검증값처럼 복사하지 않는다. 선택 효과·품질이 실제로 동일하다고 확인된 경우에만 최고 품질 대표 목록에 올린다. 시즌 특수 시스템은 선택형 모듈, 비선택 시 관련 효과·예산/캐시 흔적 없음. 음식·기름·장신구·장식·APL·proc·DPS의 메커니즘은 **SimC 자체 책임**, 제품은 입력/정적 rating/예산·중복 방지/통계·캐시 책임.

**하지 않는 일:** 현재 장비 재분배, 장비 추천/획득 경로, 시즌 전체 장비·제작품 DB, 신규 APL·proc·효과 엔진, 전 품목 인증 Gate, 새 최적화 알고리즘, 별도 AI 런타임, 불필요한 원격 빌더 플랫폼부터 만드는 일.

## 2. 반드시 재사용할 실제 성공 자산

- **v567** ZERO-SOURCE 시즌 환경 자동 구축 성공. 새 시즌에도 기존 엔진 우선 재사용.
- **v611** 동일 70961 조건의 \`G2850/J92/F165/O0/B=T3107\`. 해당 조건 범위의 근거이지 전 시즌·전 전문화 정밀 G 아님.
- **v629~v633** 영구 마부 38/38 검증 등록. 현재 사용자 UI의 마부 후보와 실제 적용 범위를 별도 확인.
- **v570** 실제 GitHub Windows Chrome에서 대표 1건 시즌 구축 → Native64 → 실제 DPS·SEM·95% 표시 E2E.
- **v572** Windows ZIP 기반 중단·서버 재시작·기존 세션 복원·재개 실측.
- **v624, v636~v638** E0/양수 E, 자동/수동 T, Native·취소·재개·저장·재열람 관련 범위별 증거.
- **v639** [실제 배포 ZIP 최종64 회귀](development/notes/2026-11-19_p3-v639_published_zip_70961_final_result_restore.md), [Actions #44539361949](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44539361949): 70961 ilvl334 징벌 성기사, 장신구 270175/270173·가슴 마부 E0·O0·T3107에서 관측 \`CHMV=1098/922/922/165\`, DPS \`161718.63\`, SEM \`243.11\`, 95% 우위 **미확정**, 근접 대안 5개, Native64·저장·HTTP 재시작·재열람 성공. 동일 조건의 E2E를 습관적으로 다시 수행하지 않는다.

이 성과들은 **각각의 사용 빌드·장비·전문화·영수증 한정**. 전26 전문화 및 개인 PC 현재 설치의 성공 증거로 확대하지 않는다. 이미 수집한 같은 시즌 정적 캐시는 SimC revision만으로 폐기하지 않으며, DPS 캐시는 실제 바이너리·프로필·장비·후보·O·전투조건·iterations 정체성에 따라 구분한다.

## 3. v657~v677 실 구현·최근 PC 판단

- v657~v661: 공식 Windows Nightly 확인, 원본 full Git SHA 고정 자체 빌드·확인된 캐시 재사용·안전 압축 해제·설치/롤백·게시. **공식 배포와 자체 빌드 prerelease는 구분**. 공식/공개 캐시 모두 없는 신규 패치의 무자격 원격 빌드 브로커는 **미구현**, 현재 제품 사용 P1의 선행 Gate로 격상 금지.
- v665~v668: 소모품/마부/공식 아이콘·영구 마부 후보·기름 ON/OFF·B8 특수장비 차단 분리, 정확한 오류/상태 위계·Win 사용자 UI 가독성 개선. 디자인 v653 및 이후 사용자 피드백을 존중한다.
- **v669~v675 회고:** 같은 F/J 설치본 2개의 \`SOURCE_STAGES/STAGED_SOURCE_MANIFEST/V216_PREFLIGHT_SEAL\`, v113 입력 차이 분석·SHA간 동등성 증명이 개발 목적을 압도했다. 실측은 \`12.1.5.70961\`, ilvl334, 영약 #241320 품질2 F165, 기본 보석 #240890/#240898/#240906/#240914 J92, O0였다. 이런 **설치본 상호 비교는 사용자 최적화 목적의 필수 조건이 아님**. 같은 수치만으로 무단 병합하지는 않되 서로를 증명할 필요도 없다. 이미 얻은 진단 자산은 보존하되 **새 세부 비교 Gate/버전 개발 중단**.
- **v676:** [상세](development/notes/2026-11-23_p1_v676_independent_installed_environment_selection_product_flow.md). 독립적으로 검증된 각 v212/v113 설치본을 정확한 SHA로 선택 가능하도록 연결. 개인 PC에서 화염 마법사/드워프, ilvl334, 4보석, O0, \`검증 환경 1\` 선택 성공 **실제 화면 확인**. 번호는 성능 순위가 아님. 이때 T는 여전히 ‘시즌 구성 검증 후 표시’.
- **v677:** [상세](development/notes/2026-11-23_p1_v677_readonly_exact_installed_budget_to_user_T.md). 새로운 \`GET /api/v1/environment/installed-budget\`가 **선택된 정확한 SHA**의 기존 봉인 v212/v113·동일 빌드/ilvl/F/J/O/G track·B/T 회계를 read-only로 검증. 선택 환경 검증 버튼 및 최적화 사전 준비는 해당 경로를 먼저 사용하며 **기존 설치본이 있으면 새 G/F Native를 자동 요구하지 않음**. 수동 T 우선·변경 시 표시 근거 철회. 외부 소스/캐시 수정·신규 Native0. **개인 PC에서 v677 버튼을 눌러 T가 실제 표시되는지는 아직 미확인**.

## 4. 최신 v677 실제 검증·배포 신분

- 인계 작성 직전 확인된 GitHub HEAD \`718bfe63a3ba97910176f639ae6a6991ca976266\`(최신 여부 새 채팅 재조회). 제품 코드 HEAD \`5ae25da68260174a09b84b0466e5d76b03e57bc3\`; API 테스트 HEAD \`9fae15d6a4d4049a6db07f59f874a6f5df8d1147\`.
- [Windows #45128051271](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45128051271): API 확인 시 \`completed/success\`; Windows Python3.12/3.14 각각 **357 PASS/0 FAIL**, 패키징5 PASS.
- [API #45128081605](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45128081605): 확인 시 \`completed/success\`; Windows/Ubuntu 각 **521 테스트, 1 SKIP/0 FAIL**.
- v677 Windows wrapper artifact **#14796064684**의 내부 **단일 제품 ZIP** \`SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA.zip\`: **1,538,784 bytes**, SHA256 \`18a9119e486a3a5a9b469c8c848504a752dc3331a69deea915193bb5b42c3eeb\`, CRC 및 V181 286/286 manifest SHA·size PASS. 관리형 SimC 바이너리 미포함; 기존 연결을 보존할 것.
- 이번 v677 변경 신규 DPS Native0, G/F Native0, 원본 DB2/HTTP 수집0. 이는 **새 코드/CI 검증**이지 사용자 개인 PC의 최적화 결과, 현 KR Retail 호환 또는 공식 전제품 READY의 신규 증거가 아니다. CI 실패/취소·SKIP는 그 실행 범위를 구별하여 보고하며 과거 green으로 지우지 않는다.

## 5. 지금 실제 사용자에게 남은 첫 미완료 접합

**단 하나의 첫 실사용 동작:** v677을 기존 캐시·관리형 SimC·세션을 유지한 새 폴더에서 실행 → 조회용 게임빌드 \`12.1.5.70961\`, ilvl334, 화염 마법사/드워프, 기존 특성, 기본 일반 보석4, 영약 F165, O0, 선택 특수장비/장식 없음, \`검증 환경 1\`(독립 검증 exact SHA) 선택 → **\`선택 환경 검증·준비\` 1회**. 기대: 읽기 전용 기존 원본 확인으로 G/J/F/O·B/T, 자동 최종 T 숫자 표시, 신규 Native0. 실패하면 **최초 실패 코드/단계 하나만** 기록해 기존 GET/원본과 대조. 새 시즌 구축 체크·새 Native/DB2를 동시에 켜지 않는다.

기존 70961은 **조회용 설치본 빌드**다. 사용자가 과거 수동 지정한 \`710c240\` SimC CLI 실제 내장 게임빌드 **70575**와도 구분. 이후 v676 관리형 SimC에서 표시한 70961은 그 설치본의 내장 빌드일 뿐 **현재 KR Live 게임빌드가 70961이라는 증거는 없다**. 신규 시즌·현재 KR Live에 억지로 기존 정적 원본을 승인하지 않는다.

v677 준비 성공 **이후** 현재 게임빌드/실 SimC 일치 확인과 정상 사용자 조건(필수 장신구 2개 포함), 사용자 대표 프로필을 연결해 실제 기존 적응형 SimC 한 사례로 DPS/SEM/95%/근접 대안·저장/재열람을 확인. 역사 v639 Native64를 단지 버전번호가 올라갔다고 그대로 재실행하지 않는다. 새로 검증해야 하는 변경 경계만 최소 실행.

**기름 OFF(O0)와 선택 특수장비/장식 OFF는 정상 BASE 경로**다. 기름 ON을 무단 OFF로 바꾸거나, 선택하지 않은 B8/특수 아이템의 미검증을 BASE 전체 차단으로 바꾸지 않는다. 기본 환경에서 필수 G/J/F/O 미확정이면 READY를 허위 표시하지 않는다. 선택 아이템만 미확정이면 그 선택만 보류.

## 6. 현재 개발 우선순위 및 비용·STOP 원칙

**P0 — v677 개인 PC 실제 결과 1회 확인:** read-only 설치 SHA→G/J/F/O/B/T→최종 T, 실패 시 첫 blocker만 최소 FIX. 기대 비용 읽기/검증만, 신규 Native/HTTP 외부 원본0. STOP: 준비 결과가 정확히 확인되면 동등성 조사·진단 확장 끝.

**P1 — 실제 사용자 최적화 결과 경로:** 현재 호환 SimC/시즌 환경, 필수 장신구2, 내부 표준 일반 장비·무기·티어4pc, 기존 적응형 SimC를 기존 캐시/세션·후보·95%·저장/재열람에 연결. 최단의 대표 한 시나리오. **이미 성공한 64 Native를 재현하려고 또 64번 실행하지 않음**. 최초 누락한 입력/JSON2/계산 경계만 검증. STOP: 사용자가 절대 rating·DPS·SEM·95%/대안과 저장된 결과를 정상 확인. 새 제품 COMPLETE/26전문화 전범위 주장 아님.

**P2 — 현재 사용자가 선택한 옵션만 증분 완성:** 기름 O의 시즌 ItemID/품질/무기·손/고정 budget/SimC 입력은 시즌 환경 단계에서 검증하고 일반 사용자는 선택만. B8 선택 특수장비·장식의 정확 variant/프로필 미스는 기존 캐시와 **그 변형만** 필요 최소 Native. 장신구 정적 JSON2 미관측을 0/지원 불가로 판단하지 않음. 선택하지 않은 옵션 미완료는 기본 경로를 막지 않음.

**P3 — 시즌 최고 품질 소모품·UI:** 음식·물약·영약·영구 마부 선택의 검증된 원본과 **실제 SimC 적용** 연결. 최고 품질은 실제 동일 효과·조건·범위 확인 후만 중복 낮은 품질 숨김. v653 기반 UI, v674 가독성(소모품 2열·F/J 전폭)·v673 장식 가로 2열·v668 상태 위계 유지. 정확 한국어 이름/아이콘·후보 결손 범위 개선은 사용자의 결과 획득과 직접 연결되는 것부터. UI에서 ‘사용’ 표시는 SimC 적용 성공 근거가 아님.

**P4 — 실제 신규 패치에만 필요한 원격 SimC 요청:** v657~v661 공식 Nightly/공개 자체 빌드 캐시를 우선 활용; 둘 다 없는 상황의 일반 사용자 broker는 미구현. P0/P1을 막는 실제 필요가 생기기 전 새 서버·권한·Actions 플랫폼을 만들지 않음.

매 변경 **코드 전에** 실제 UI 소비 단계 / 보이는 장애 / 기존 코드·원본 재사용 가능성 / 불필요한 검증·자료 수집과 중단 근거 / Native·DB2·HTTP·캐시·메모리·I/O·Actions 비용·STOP 조건을 짧게 밝힌다. [제품 우선 정책](development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md)과 [실제 소비 감사](development/PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md)를 따르며 **정책 문서/새 승인 Gate를 재복제하지 않는다**. 실행 선택은 **\`STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW\`**. 코드/합성 회귀 PASS/기존 역사 Native/이번 신규 Native/실 PC E2E/미구현 구분.

## 7. 공식 상태·권한 및 새 채팅 7항목 보고 계약

공식 과거 상태 \`15/78 COMPLETE\`는 제품 구현률이 아니다. \`full_product_e2e=PENDING\`, \`next_review=B10\`; B10·Work OS M0은 일반 제품 개발·허용된 최소 SimC 시험의 선행 차단 조건이 아니다. 사용자 별도 지시 없이는 GitHub \`main\` 병합, v003 immutable, v016 원본 직접 통합 완료 선언, Project Sources/Instructions 적용 완료 선언, Work OS M0/Shared State·78개 공식 승격, 주 개발 채팅 소유권 이전, WEQUIP 영구 런타임 의존성, 외부 배포 서버 운영권한 신설을 하지 않는다.

새 채팅은 아래 **정확히 7개**를 읽기 전용 보고 후 STOP:
1. **최신 GitHub 실상:** 재조회 HEAD, CURRENT, v677 제품 ZIP/Actions 최신 상태, 테스트 성공/실패/취소/SKIP, 역사/신규 Native 분리.
2. **최종 제품 취지:** 26 DPS 미래 ilvl/T 절대 CHMV, SimC DPS/SEM/95%/대안, G/J/F/O·L/E/O, AI 런타임0, 배제 범위.
3. **재사용 성공:** ZERO-SOURCE v567, G/J/F/O v611, 마부38/38, v570 Windows Chrome E2E, v572 취소/재개, v639 실제 ZIP Native64·저장/재열람, 캐시 경계.
4. **최근 제품 개발:** v657~v668 기반, v669~v675 설치본 상호 비교가 불필요했음을 확인한 교훈, v676 독립 원본 SHA 선택 실 PC 성공, v677 read-only 예산/자동 T 코드·CI **vs PC 미검증**.
5. **실사용 장애·미확정:** 개인 PC v677 자동 T·준비 아직 미확인, 이전 70575↔70961/현재 KR Live 불확정, 기름 ON·선택 B8·기타 소모품 실제 적용 후순위·범위 한계.
6. **가장 작은 다음 1건:** 개인 PC v677에서 \`검증 환경 1 → 선택 환경 검증·준비 1회 → G/J/F/O/T 확인\`; 실패하면 최초 오류 한 개; 성공 후 필요한 최소 대표 SimC DPS E2E 연결. 비용·STOP·기존 엔진 재사용 강조.
7. **공식 상태·권한:** 15/78 의미 제한, full_product_e2e=PENDING/B10, v653 디자인, main/immutable/Project UI·Work OS/주 개발 채팅 제한.

**새 채팅 첫 응답에 코드·GitHub 문서 수정/새 Actions·Native·HTTP/DB2/공식 승격 없음. 일곱 항목 후 STOP.** 사용자가 별도 \`진행\`을 지시하면 그 시점 최신 HEAD와 실제 첫 미완료 접합부터 좁게 다시 확인하고 격리 브랜치에서만 개발한다.

## 읽는 순서

1. 이 인계 문서
2. \`docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md\`
3. \`docs/development/notes/2026-11-23_p1_v677_readonly_exact_installed_budget_to_user_T.md\`
4. \`docs/development/notes/2026-11-23_p1_v676_independent_installed_environment_selection_product_flow.md\`
5. \`docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md\`
6. \`docs/development/PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md\`
7. \`docs/development/notes/2026-11-19_p3-v639_published_zip_70961_final_result_restore.md\`
8. \`docs/development/UI_DESIGN_VERSION_REGISTRY.md\`
9. \`WINDOWS_BETA_START_HERE.md\`
10. 필요 시 \`docs/CHAT_CONTINUITY_HANDOFF_20261123_P3_V668_PRODUCT_FLOW_FIRST_PC_FIRST_CAUSE.md\`(역사 비교용: **우선순위는 v677이 우선**)

**끝: 최적화 엔진·시즌 구축 엔진을 재개발하지 않는다. 일반 사용자가 실제 절대 rating과 SimC DPS를 얻는 첫 미완료 접합 하나를 가장 적은 비용으로 해결한다.**
