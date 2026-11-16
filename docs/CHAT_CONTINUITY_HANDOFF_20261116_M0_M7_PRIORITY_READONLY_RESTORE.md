# SIMC SECONDARY OPTIMIZER — M0~M7 제품 우선 최신 인계 (2026-11-16)

> **용도: 다음 일반 채팅의 읽기 전용 독립 복원 + 현재 우선순위 안내.** 작성 전 실제 격리 브랜치 HEAD \`a60acd6b0bff09fe649212a9ea68437b82f46253\`와 최근 커밋, Actions, CURRENT, M0~M7 로드맵, v1.4.3 및 78 JSON을 확인했다. 이 HEAD·PASS 수치·다음 작업은 **작성 당시 스냅샷**이다. 이 문서 생성 후 HEAD가 바뀌며, 새 채팅은 반드시 GitHub 최신 HEAD/실제 코드/영수증을 다시 조회한다. 본 인계는 새 기능 구현·테스트 실행·Native·DB2 수집·main 병합·공식 승격이 아니다.

## 1. 읽기 정본과 제품의 변하지 않는 목표

- 저장소: \`degong2-code/simc-secondary-optimizer-runner\`. 실제 최근 개발 브랜치: \`probe/chat-cache-v035-20261024\` (다른 브랜치 이동 여부는 새 채팅에서 독립 확인). \`main\`을 최신 제품 개발 정본이라고 가정하지 않는다.
- 처음 확인할 파일: \`docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md\` (최근 기록), 본 문서, \`docs/development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md\`, \`docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json\`, \`docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md\`, \`docs/development/PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md\`, \`docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md\`, \`docs/development/78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md\`, \`docs/CHAT_HANDOFF_DYNAMIC_GITHUB_RECONSTRUCTION_20261115.md\`. 옛 \`CHAT_CONTINUITY_HANDOFF_20261115_V490_M0_M7_READONLY_RESTORE.md\`는 v490 시점 역사 기준. FILE_MAP/EVIDENCE_INDEX/DECISIONS는 해당 작업에 필요할 때만 연다.
- 제품: 정확히 **26개 DPS 전문화** (증강 기원사·탱커·힐러 제외). 사용자가 목표 ilvl 기본 334 또는 **기름 포함 수동 최종 T**를 정하면, 내부 대표 일반 장비·무기·티어 4pc·주능력치 및 검증된 선택 장비/소모품을 사용해 기존 적응형 SimC **DPS 최대화** 기준 치명·가속·특화·유연 **절대 rating**을 찾는다. 출력 DPS, SEM, **95%만**, 관측 1순위, 실질적으로 다른 근접 대안, 스탯 비율. 전역 최적 증명이라고 하지 않는다.
- 사용자 입력: 직업·전문화·종족·특성, 목표 ilvl/최종 T, 장신구 2개, 선택 특수·제작장비, 장식 최대 2개, 최고 품질 보석·영약·기름·영구 마부 및 검증된 선택 소모품·전투 설정. 전체 장비 선택/현재 착용 스탯 총합을 목표로 재분배하지 않는다. 업로드 SimC 프로필은 캐릭터 정보·특성 추출의 선택 입력.
- 회계: \`B=G+J+F\`, \`T=B+O\`, \`c_final=c_base+o\`. 수동 최종 T 최우선 (\`B=T-O\`). 고정 특수 L은 G에 포함되어 하한으로만 보호, 영구 E는 승인 회계 한 번, 고정 O는 적용 무기/손과 gear_*에 한 번, 장신구 정적 스탯은 자유 G 밖. 제작 초기 50:50은 L이 아님. 옛 시즌 79×2, J=138, F=165, 기름 16/16을 새 시즌 근거로 복사하지 않는다.
- SimC가 아이템·proc·장식·APL·DPS를 담당. 우리 코드는 원본 정확 ID·빌드·ilvl·옵션·원본 SHA, 시즌 G/J/F/O/B/T, 정적 rating/JSON2, 프로필·세션, 적응형 실행/95%·캐시·복구를 담당한다. 장비 추천/파밍 경로·전체 시즌 DB·독립 효과 메커니즘 인증·새 탐색 알고리즘은 범위 밖.

## 2. 실제 현재 개발 위치: 최근 수정과 영수증

**기존 자산을 버리지 않는다.** v216/v217/v212 단일 시즌 Build/봉인, v222 예산, v218/v098/v096 대표 실행 프로필, v113 UI/API, v094/v290/v291/v292/v293/v106 적응형 SimC·캐시·취소/재개, v220 선택 자동 등록을 먼저 재사용한다. v343/v417/v439/v440 등 기존 실 Native·JSON2/95%와 다전문화 영수증은 정확히 일치하는 시즌·빌드·장비·프로필·입력·바이너리 범위에서만 재사용하며 재실행을 의례화하지 않는다.

- **v486~v490(11/15):** 누락 v113 스냅샷 재구축/재사용; 동일 F의 여러 J 설치 SHA를 최신 파일로 임의 선택하지 않음; 기존 UI의 재검증 안내; 유일 F+기본 4보석+O=0인 경우 영약 선택에 따라 정확한 v212 설치 SHA·장신구·실행 프로필 재결합. 당시 API Ubuntu/Windows 각 398 PASS·신규 Native 0. 옛 인계 문서의 현재 판단은 이 시점에 한정.
- **11/16 M3 UI:** 설치 응답 중 기름·소켓·F/ilvl 등 입력이 바뀌면 과거 SHA/T를 적용하지 않도록 POST/GEAR GET 양쪽 검사; 빈 영약 선택에서 고급 물리 F ItemID 보존; 사용자 목표 ilvl 변경 시 시즌 Build 기본 ilvl 동기화(고급 명시 override 유지). 관련 UI/HTTP 오프라인 Actions 통과.
- **11/16 M3 결과 표시:** 재개가 차단되거나 작업자가 불완전한 회차에 이전 \`V291_RESULT.json\`을 새 완료 결과처럼 표시하지 않음. 관측·캐시를 삭제하지 않고 정상 pause 결과는 유지.
- **11/16 기름 O:** 동일 기름에 복수 F/J 설치본이면 자동 SHA 임의 선택 금지; 유일한 검증된 기본 4보석/일치 F와 oil 손 조건에서만 exact v212 재결합, 이미 기본 선택한 기름은 고급 ‘검증된 기름 설치본 연결’로 명시 적용. 첫 정규식 이스케이프 코드 FAIL 교정 후 오프라인 PASS; 이력이 CURRENT에 기록됨. 다중 변형 일반 선택 UX는 미완성·증거 없으면 보류.
- **11/16 M1/M2:** 기존 v212+v113 봉인 프로필이 있으면 SimC 바이너리 입력 없이 시즌 환경 **Native 0회 재사용**; 캐시 miss로 신규 G/F가 필요하면 실제 바이너리 필수, 추가 우회 엔진 없음. 일반 사용자 입력이 명시한 새 시즌 설치 SHA와 물리 F가 우선하도록 과거 시즌 메모리/사라진 F 파일의 선조회 제거. API/JS 회귀 PASS.
- **가장 최근 M3 결함(11/16):** v113 장기 SimC 세션은 worker spawn 전에 \`QUEUED\` 기록. 로컬 로그 I/O나 \`subprocess.Popen\` 실패 시 가짜 QUEUED가 남는 결함을 [코드 \`dfe2ab4f\`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/dfe2ab4fb9ce0b5cc14fde4cf7597f14ed12df8d)로 **BLOCKED_OR_PARTIAL**, \`V293_WORKER_LAUNCH_FAILED_BEFORE_NATIVE\`로 안전 확정. [HTTP 회귀 \`ab3abb59\`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/ab3abb5920924039eff5ec23fbe792840325063e): OS spawn 실패 강제→QUEUED 제거·이전 DPS 바이트 보존·같은 봉인 세션 재개 PASS. [API Ubuntu/Windows #43788718073](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43788718073), [공통 #43788718084](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43788718084), [78 최종 #43789031893](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43789031893) SUCCESS. 이 수정의 신규 SimC Native/DB2 **0회**. [CURRENT 기록 \`a60acd6b\`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/a60acd6b0bff09fe649212a9ea68437b82f46253). **실제 신규 시즌 적응형 DPS 성공 증거가 아님**.

**2026-11-16 인계 직전 공식 JSON 재집계:** \`generic 27 PASS\`, \`current_source 27 PASS\`, \`product_integration 15 PASS\`, \`historical 13 PASS\`; **15/78 COMPLETE**, \`policy.next_review=B10\`(검토 위치일 뿐 개발 순서 아님), \`full_product_e2e=PENDING\`. 15/78은 실제 구현률 19%라는 뜻이 아니다. 인계 후 새 HEAD의 JSON을 재확인한다.

## 3. 승인 M0~M7: 제품 기준·현 위치

| 단계 | 현재 의미/증거 | 중단하지 않을 필수 목표 |
|---|---|---|
| M0 | 기존 소스·실 Native·캐시·CURRENT 재사용 기준 확보 | 증거 동일성 확인, 역사 전수 감사 STOP |
| M1 | 단일 v216 시즌 Build 구현 및 특정 시즌 실 Native/원본 있음; **새 시즌 ZERO-SOURCE 최종 미수락** | 해당 시즌 대표 일반 장비·무기·4pc·원본 ID·G/J/F/O 구축 |
| M2 | v222 예산·수동 T·v212/v098 프로필/JSON2 일부 실증 | 정확한 B/T, L/E/O 단일 귀속, 최종 rating 일치 |
| **M3** | 기본 사용자→실행/결과/캐시/취소/재개 상당 부분 구현, 최근 오류 회귀 통과 | **정상 BASE가 실제 사용자 선택에서 SimC 결과·95%/복원까지 이어지는 잔여 소비 경계 확인** |
| M4 | 일부 고품질 선택 기능/원본·자동 등록 경로 존재 | 검증된 선택만 등록. 미확정 옵션은 개별 PENDING, BASE 비차단 |
| M5 | 26 DPS 계약·대표 무기 유형·여러 Native 증거 | 신규 경계만 대표적으로 확인, 전 전문화 Native 전수 금지 |
| M6 | 로컬 웹/API·Windows 베타 ZIP/HTTP·진행/복구 회귀 있음 | 일반 사용자 패키지/첫 실행·오류·세션·결과 실제 사용 수락 |
| M7 | **PENDING** | 기존 season seed/정적·DPS 캐시/영수증을 시험에서 격리한 **단일 정상 Environment Build → USER-E2E** 수락 |

M0~M7은 제품 완성 관리 체계이지 번호순 의무 작업표가 아니다. 78개 계약 역시 증거 관리 원장이지 별도 번호순 개발 계획이 아니다.

## 4. 단기 실행 순서 — 다음 채팅은 다음 ‘첫 실제 장애’ 하나부터

1. **첫 응답은 읽기 전용 독립 복원 후 STOP.** 최신 브랜치/HEAD/Actions, CURRENT 최근 기록, 78 JSON, 마지막 dfe2/ab3/a60 변경 및 관련 실제 코드/테스트를 확인. 수정·실행 금지; 현재 제품의 실제 가능/막힘을 구분.
2. 사용자 별도 **‘진행’** 후 M3 **정상 BASE 긍정 흐름** 우선: 선택(전문화/종족/특성·목표 ilvl 또는 수동 T·장신구2·검증 J/F/O/전투설정) → 정확한 v212 설치 SHA/대표 4pc 프로필 → v113.plan/longrun_prepare → 기존 적응형 SimC start/status/result/cancel/resume → DPS/SEM/95%·비율·캐시. 최근 v490 이후 수정된 UI/스폰 예외를 처음부터 다시 구현·전수 검증하지 않는다. **기존 영수증으로 이미 충분하면 REUSE/STOP**; 새 코드 결함이 *재현된 경계*에만 최소 FIX.
3. M3에서 새 필수 결함이 없으면 M1/M2 **단일 정상 시즌 Build**의 실제 새 시즌 필수 대표 장비/무기/티어 및 G/J/F/O→B/T→수동 T·L/E/O→v212/v113/v098 프로필 연결 중 **미구현/미검증 필수 소비 한 곳**을 확인. 옛 시즌 예산/Native를 새 시즌 근거로 복사하지 않는다.
4. 기본 BASE가 작동한다면 M4는 실제 등록 증거가 이미 충분한 최고 품질 영구 마부·소모품/특수·장식 등 **사용자 선택 항목만** 작게 병행. 음식/물약 v484/485 source-only ≠ 실제 등록; 미확정 옵션은 해당 옵션만 보류.
5. M5/M6는 지원 26 DPS의 무기/티어/소켓 유형별 실제 차이, Windows 패키지 최초 실행·복원·결과에서 재현된 문제만 수정. 최종 M7 엄격 E2E 수락은 별도 기준에 따라 마지막에 실시.

**다음 최소 비용 판정:** 현 상태에서 확인된 모든 **과거 수정의 오프라인 성공**을 다시 늘리는 것이 아니라, 현재 실제 BASE의 정상 경로에 근거상 남은 첫 연결이 무엇인지 특정한다. 필요하면 정확히 1개 조건의 기존 Native 영수증/캐시부터 재사용하고, 새 Native가 결과 판정을 실제 바꿀 때만 한정·기록해 실행. 실제 장애가 없으면 즉시 REUSE/STOP하고 다음 필수 연결로 이동.

## 5. 중기 로드맵 (기능별 완료 조건)

1. **M1/M2 단일 시즌 일반화:** 새 확장팩/빌드의 대표 ID·G/J/F/O 원본→자동 B/T/수동 T→정적 JSON2/실행 프로필을 기존 한 엔진으로 연결; 정확 원본 부족이면 해당 시나리오 차단. 동일 시즌 캐시는 재사용, 별도 SimC-only 새 엔진 금지.
2. **M4 검증 선택:** 정확한 ItemID/품질/적용 범위/SimC 입력/CHMV 소유권이 증명된 최고 품질만 자동 등록(정책 A). 영구 마부 지원, 일반 임시 마부 제외·기름 예외, 시즌 특수 콘텐츠는 독립 ON/OFF 모듈. 기본 BASE에 새 선택 Gate 만들지 않음.
3. **M5 범용성:** 26 DPS·주능력치·대표 무기 형태/4pc·기본 APL·결과 통계·캐시 identity에 필요한 유형별 기존 영수증+최소 새 경계 검증. 관측 1순위와 95% 확정·전역 미증명 구별.
4. **M6 운영:** Windows 배포, 로컬 SimC 바이너리 설정, 시즌 갱신, 사용자 세션 복원/취소/재개/오류원문/결과 재열기, 안전한 캐시/정적 자료 호환.
5. **M7 최종 수락:** 캐시/과거 시즌 seed/역사 영수증을 시험 입력에서 분리한 정상 단일 엔진 ZERO-SOURCE→USER-E2E. 새 공개 원본 수집은 정상 제품 경로에서 허용. 제품 전체 통합 PASS/78 유효 증거/권한 완료까지 정식 출시·COMPLETE라고 주장하지 않는다.

## 6. 상시 준수·비용·권한

- **매번 코드/엔진 검증 추가 이전 사용자에게 5가지 짧게 설명:** (1) 실제 화면·버튼/내부 이용 위치, (2) 사용자가 못 하는 일과 수정 효과, (3) 기존 코드/데이터/캐시/영수증 재사용, (4) 불필요한 과잉 작업과 STOP, (5) 신규 Native·HTTP/DB2·CPU·RAM/I/O·캐시 영향 및 최소 회귀 범위. 설명 정책이지 새 Gate나 매번 별도 승인 아님.
- 판단 순서 **STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW**. 미관측을 0으로, 임의 최신 설치 SHA를 정답으로, 이전 시즌 예산을 새 시즌 근거로 간주하지 않음. 검증된 설치 예산 숫자만 복사해 새 프로필 승인 우회 금지. 이전 G/F 재측정 위험이 있어도 검증·실행 원본/캐시 일치를 훼손하는 우회 복구 엔진 금지.
- 새 적응형 최적화 알고리즘, 미선택 추가 소켓/전체 아이템·SpellEffect DB, proc/APL 효과 독립 인증, 26 DPS Native 전수, 78 감사 재시작, SEM 미세화, 또 하나의 Gate/관리 시스템 금지. 기존 코드 삭제 전 실제 세션·호출자·호환성 확인.
- 매 변경마다 직접 수정한 기능만 오프라인 회귀 → 기존 동일 조건 실제 Native/Actions 재사용 → **정말 부족한 최소 실제 SimC 시험** 순서. 신규 PASS/FAIL과 재사용 Native, 실제 USER-E2E 및 정식 78 COMPLETE를 분리하여 기록. HTTP/DB2/Native/메모리/I/O/실행시간·캐시 미스·중복 작업을 점검.
- 원본 보고 \`v016_SCENARIO_CONTRACT\`는 실제 바이트·영수증 확인 전 **직접 통합 완료라고 주장 금지**. ChatGPT Project Sources/UI 실제 적용은 GitHub 문서 기록과 별개.
- 개발 격리 브랜치는 유지. 별도 사용자 명령 없이는 \`main\` 병합, v003 immutable 변경, 원본 v016 수정, Project Sources/Instructions UI 적용 주장, 공식 Work OS M0/Shared State·승격, MAIN/WORK 제품 개발 소유권 이전 금지. **새 채팅 인계 요청 자체는 개발 소유권 이전·공식 승격 승인이 아님**.
- 다음 채팅 첫 요청은 **오직 읽기 전용**. 관련 GitHub 현재 자료를 확인하고 ①최신 HEAD ②현재 실제 사용자 가능/막힘 ③기존 PASS/Native 재사용 ④M0~M7·78 ⑤필수 미완료와 선택 PENDING ⑥가장 작은 다음 장애 후보 ⑦권한/미확인 자료를 간결히 보고한 뒤 **STOP**. 별도 \`진행\` 전 수정·GitHub 문서 추가·테스트/Actions/Native/수집 금지.

**종료: 본 문서의 SHA는 인계 시점 스냅샷이며 새 채팅에서 현재 사실로 복제하지 않는다.**
