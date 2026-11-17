# SIMC SECONDARY OPTIMIZER — 최신 GitHub 독립 복원 및 제품 완성 개발 인계

SIMC SECONDARY OPTIMIZER 프로젝트의 **현재 실제 개발 상태를 GitHub 코드·CURRENT·Actions·Native·현 시즌 원본 영수증에서 읽기 전용으로 독립 복원**하라. 이 인계는 과거 개발을 다시 시작하거나 기능을 중복 구현하는 작업이 아니다. **이미 실증된 기능과 캐시를 재사용하고, 신규 사용자가 실제 결과를 얻는 데 필요한 최초 필수 연결만 최소 비용으로 완성**하기 위한 것이다.

## 1. 첫 조회와 최상위 정본

- 저장소: `degong2-code/simc-secondary-optimizer-runner`
- 격리 브랜치: `probe/chat-cache-v035-20261024`
- **가장 먼저 읽을 최신 인계:** `docs/CHAT_CONTINUITY_HANDOFF_20261117_V535_PRODUCT_PRIORITY_READONLY_RESTORE.md`
- 이어서 `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 맨 앞의 v535, `docs/development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md`, `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json`, INDEX/FILE_MAP/EVIDENCE_INDEX, 제품우선 최소검증 정책, 실제 런타임 소비 감사, 승인 `v1.4.3` 시즌 G/J/F/O 정책을 읽는다.
- HEAD SHA·Actions 상태는 **인계 당시 스냅샷**이다. 이번 채팅에서 반드시 최신 브랜치 HEAD·커밋·Actions를 새로 조회한다. v1.4.1·과거 파일의 **27 DPS(증강 포함)**, 오래된 보석 J138·기본 334를 모든 시즌의 확정값으로 삼는 문구보다 최신 승인 **26 DPS(증강 제외)**·현재 시즌 실제 원본이 우선이다.
- 업로드된 `LAST_Q&A(5).txt`는 수동 T+양수 E 연결의 세 차단점을 발견한 시점의 대화다. **그 후 GitHub v534에서 수동 최종 T3200+8025 E30의 실제 Windows SimC Native PASS, v535에서 정확 조건의 UI 옵션 오프라인 PASS가 생겼으므로 최신 사실로 덮어쓴다.**

## 2. 제품 목적과 책임

26개 DPS 전문화, 미래 목표 ilvl(시즌별 자동 결정) 또는 사용자가 직접 입력한 **최종 CHMV 총량 T**에서 치명·가속·특화·유연의 DPS가 높은 **절대 rating**을 기존 적응형 SimC로 찾는다. 일반 장비·무기·4티어·주능력치는 내부에서 대표 구성한다. 사용자는 캐릭터/특성, 장신구 2개, 선택 특수/제작장비·장식 최대2, 검증된 보석/영약/기름/영구 마부, 전투조건을 선택한다. 현재 전체 착용 장비를 최적화 기준으로 재분배하거나 장비·파밍 경로를 추천하지 않는다.

`B=G+J+F`, `T=B+O`, `c_final=c_base+o`. **수동 최종 T가 항상 우선**하고 `B=T-O`. 정확한 특수장비 L은 G 안의 고정 하한, E/O는 원본 승인 회계대로 한 번만 포함한다. 마부 E 양수는 자동 ilvl의 **사용자별** B를 증가시킬 수 있지만, **수동 T에서는 E를 T 위에 더하지 않고 T 내부의 고정 하한**으로 보호한다. 장신구 고정치는 자유 G 밖이다. SimC만 proc/APL/아이템 효과/DPS를 계산하고, 프로그램은 정확 ID/ilvl·정적 예산·고정 하한·입력/JSON2·기존 탐색·캐시·95% 판정/결과를 책임진다. **제품 실행 중 AI 판단/호출 0회**, 95% 우위와 단순 관측 1순위, 전역 최적성 미입증을 구별한다.

## 3. 최신 실증과 미완료를 혼동하지 말 것

- M1: 동일 빌드 실제 원본 70783에서 기본 ilvl **334** 확인. 미래 시즌으로 복사하지 않는다.
- M2: 실제 Windows 기본 G2850/J92/F165/O0→B=T3107→v212 설치와 내부 사용자 프로필 실증. **M2를 다시 만드는 것이 현재 우선순위가 아니다.**
- M3/M4: v525~v527 장신구 여러 쌍·특수 목걸이+제작/장식2+4티어 복합 시나리오별 실제 Native. v528 영구 마부 `7967 E0`, `8025 가속+30`, `7965 특화+26`의 정확한 정적 원본. v530 E0 자동 T3107, v532 가속+30 자동 T3137, v533 특화+26 자동 T3133 **각 기존 적응형 SimC Native6/SEM/95%·cache-only6/추가 Native0 PASS**.
- **v534:** `8025`+수동 `T3200` 실제 Windows Native6/SEM/95%/캐시 PASS. E30을 **T3200 내부 하한**으로 보존, 자동 T3137을 덮어쓰지 않음. 이 경로를 다시 미구현으로 판단하거나 Native를 처음부터 반복하지 않는다.
- **v535:** `v113 /api/v1/season-option-catalog`의 검증된 단일 범위 `verified_exact_user_enchant_runtime` → `webui/app.js` 반지1의 `7967/8025/7965` UI 선택이 **정확한 70783·생존 사냥꾼/human 334·장신구 270175/270173·선택 특수/장식/기름 없음·설치 v212 SHA 조건에서만 Ubuntu/Windows 오프라인 PASS**. 일반 미승인 카탈로그는 여전히 비선택 상태, 입력 변동 시 fail-closed. **실제 브라우저 catalog→선택→plan→start→result E2E는 아직 PENDING**.
- **소켓 5/6개:** `J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING`. J115/138은 미승인 후보이며 게임 내 소켓 부여/적법성·정확 J 근거 전까지 설치·DPS 금지. 해당 선택 옵션 미확정으로 검증된 일반 4보석 BASE를 차단하지 않는다.
- 공식 78요소 **15/78 COMPLETE**, `full_product_e2e=PENDING`. 원장 `next_review=B10`은 검토 위치이지 개발 순서가 아니다. 실 Native 성공, UI 오프라인 PASS, 개인 Windows 설치·브라우저 수락, 26개 DPS 전체 완료를 혼동하지 않는다.

## 4. M0~M7 현재 우선순위

M0 정본·캐시 재사용 → M1 시즌 ilvl 원본 실증 → M2 시즌 G/J/F/O·v212 실 설치 재사용 → M3 기존 SimC 적응형/통계/캐시 재사용 → M4 검증된 사용자 옵션만 정확 범위로 연결·미검증 소켓 보류 → M5 26개 DPS 중 신규 무기·티어·물리 구조 유형만 최소 점검 → **M6 실제 Windows 첫 사용자 선택·실행·결과 수락** → M7 최종 ZERO-SOURCE→USER-E2E 및 78 원장 완료 수락.

**지금 가장 중요한 다음 작업 하나:** 최신 HEAD의 v535 UI/로컬 웹 API/정확 v212 설치를 실제 사용자가 소비하는 **브라우저 catalog→검증된 반지 마부 선택→plan→start→result**로 끝까지 확인한다. 앞서 완료된 Native·캐시·예산을 우선 재사용하고, 실제 GUI 필수 검증에서만 최소 Native를 쓴다. 화면의 선택 조건 변경·오류 코드·기본 BASE 비차단도 점검한다. 여기서 첫 실제 장애만 CONNECT/FIX한다. 장비 옵션 전체/26전문화 Native 전수, 새 스케줄러, 추가 Gate, 효력 재구현 금지.

## 5. 지속 개발 규칙·권한

매 작업: `INDEX → FILE_MAP → EVIDENCE_INDEX → 생산자·소비자 실제 코드 → 같은 시즌 원본/설치 SHA·기존 Actions·Native·캐시 → 첫 실제 결손`. 판단 순서 `STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW`. 변경 전에 실제 사용자 단계/불편/재사용 근거/하지 않을 일/예상 Native·HTTP·DB2·CPU·I/O와 STOP 조건을 짧게 설명한다. 정적 아이템 캐시는 같은 시즌의 SimC revision만으로 폐기 금지, DPS 캐시는 바이너리·프로필·선택·O/E·T·전투·iterations identity 분리. 코드 구현/오프라인 PASS/역사 Native 재사용/신규 Native/브라우저 E2E/공식 수락 구분.

격리 브랜치 후속 개발은 사용자가 나중에 명시적으로 **`진행`**할 때만 진행한다. **main 병합, v003 immutable, 원본 v016 직접 통합 완료 주장, ChatGPT Project Sources/Instructions 적용 주장, Work OS M0/Shared State·공식 승격, MAIN/WORK·타 채팅의 임의 운영권한 이전 금지.**

## 6. 이번 새 채팅의 첫 응답 — 읽기 전용 후 STOP

실제 GitHub를 조회하고 아래 **7가지만** 보고한다.

1. 최신 브랜치·HEAD·최근 Actions PASS/FAIL/CANCELLED/SKIPPED
2. 현재 실제 사용 가능한 제품 기능 vs 남은 연결·출시 차단
3. 역사 Native·최근 Native·실 시즌 원본·오프라인 PASS의 차이
4. M0~M7 위치와 공식 78요소/최종 E2E 상태
5. 필수 미완료·선택형 보류·확인된 결함
6. 비용 대비 다음 작업 **하나**, 기존 재사용과 최소 실행 비용
7. 미확인 증거·권한 경계

**첫 응답에서는 코드/문서 변경, 테스트·Actions·Native·HTTP·DB2 실행, 커밋·병합을 절대 하지 않는다.** 7가지를 보고한 뒤 **STOP**. 사용자가 다음 메시지에서 별도로 `진행`하면 그때 최신 HEAD와 첫 실제 장애를 재확인하고 최소 개발을 재개한다.
