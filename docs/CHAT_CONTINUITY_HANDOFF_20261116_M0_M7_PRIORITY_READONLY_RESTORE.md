# SIMC SECONDARY OPTIMIZER — M0~M7 제품 우선 최신 인계 (2026-11-16)

> **2026-11-16 최신 재점검 인계 정본.** 확인 당시 실제 격리 브랜치 HEAD `3c358998f698a19903c23592ec31130c4e83b079`; 최신 코드/검증 HEAD는 `de951a23a345d21cd785305e49bee4d293827212`, 그 이후 CURRENT 문서만 갱신됐다. 코드 HEAD 11개 GitHub Actions SUCCESS, 최신 CURRENT HEAD의 78 계약 검사 SUCCESS. 모두 **작성 당시 스냅샷**이며 새 채팅은 브랜치·HEAD·Actions·Native 영수증·78 JSON을 다시 읽는다. 이 인계의 다음 채팅 **첫 응답은 오직 읽기 전용 복원 후 STOP**, 이후 사용자의 별도 '진행' 전에는 코드·문서 수정, 테스트/Actions/Native/DB2/HTTP·공식 승격을 하지 않는다. 본 파일 갱신 자체는 제품 코드/SimC 실행이 아니다.

## 1. 읽기 정본과 제품의 변하지 않는 목표

- 저장소: `degong2-code/simc-secondary-optimizer-runner`. 실제 최근 개발 브랜치: `probe/chat-cache-v035-20261024` (다른 브랜치 이동 여부는 새 채팅에서 독립 확인). `main`을 최신 제품 개발 정본이라고 가정하지 않는다.
- 처음 확인할 파일: `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` (최근 기록), 본 문서, `docs/development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md`, `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json`, `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`, `docs/development/PRODUCT_PURPOSE_RUNTIME_CONSUMPTION_AUDIT_20261115.md`, `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md`, `docs/development/78_ELEMENT_ACCEPTANCE_NECESSITY_AUDIT_V441.md`, `docs/CHAT_HANDOFF_DYNAMIC_GITHUB_RECONSTRUCTION_20261115.md`. 옛 `CHAT_CONTINUITY_HANDOFF_20261115_V490_M0_M7_READONLY_RESTORE.md`는 v490 시점 역사 기준. **오판 방지 우선순위:** 기능 존재·미구현을 판단하기 전 `docs/development/INDEX.md` → `FILE_MAP.md` → `EVIDENCE_INDEX.md`를 먼저 검색하고 실제 값 생성자·호출자·소비자, Native/Actions·캐시·CURRENT를 대조한다. `DECISIONS`는 필요할 때만 열고 역사 전수 재감사는 하지 않는다.
- 제품: 정확히 **26개 DPS 전문화** (증강 기원사·탱커·힐러 제외). 사용자가 목표 ilvl 기본 334 또는 **기름 포함 수동 최종 T**를 정하면, 내부 대표 일반 장비·무기·티어 4pc·주능력치 및 검증된 선택 장비/소모품을 사용해 기존 적응형 SimC **DPS 최대화** 기준 치명·가속·특화·유연 **절대 rating**을 찾는다. 출력 DPS, SEM, **95%만**, 관측 1순위, 실질적으로 다른 근접 대안, 스탯 비율. 전역 최적 증명이라고 하지 않는다.
- 사용자 입력: 직업·전문화·종족·특성, 목표 ilvl/최종 T, 장신구 2개, 선택 특수·제작장비, 장식 최대 2개, 최고 품질 보석·영약·기름·영구 마부 및 검증된 선택 소모품·전투 설정. 전체 장비 선택/현재 착용 스탯 총합을 목표로 재분배하지 않는다. 업로드 SimC 프로필은 캐릭터 정보·특성 추출의 선택 입력.
- 회계: `B=G+J+F`, `T=B+O`, `c_final=c_base+o`. 수동 최종 T 최우선 (`B=T-O`). 고정 특수 L은 G에 포함되어 하한으로만 보호, 영구 E는 승인 회계 한 번, 고정 O는 적용 무기/손과 gear_*에 한 번, 장신구 정적 스탯은 자유 G 밖. 제작 초기 50:50은 L이 아님. 옛 시즌 79×2, J=138, F=165, 기름 16/16을 새 시즌 근거로 복사하지 않는다.
- SimC가 아이템·proc·장식·APL·DPS를 담당. 우리 코드는 원본 정확 ID·빌드·ilvl·옵션·원본 SHA, 시즌 G/J/F/O/B/T, 정적 rating/JSON2, 프로필·세션, 적응형 실행/95%·캐시·복구를 담당한다. 장비 추천/파밍 경로·전체 시즌 DB·독립 효과 메커니즘 인증·새 탐색 알고리즘은 범위 밖.

## 2. 실제 현재 개발 위치: 최근 수정과 영수증

**기존 자산을 버리지 않는다.** v216/v217/v212 단일 시즌 Build/봉인, v222 예산, v218/v098/v096 대표 실행 프로필, v113 UI/API, v094/v290/v291/v292/v293/v106 적응형 SimC·캐시·취소/재개, v220 선택 자동 등록을 먼저 재사용한다. v343/v417/v439/v440 등 기존 실 Native·JSON2/95%와 다전문화 영수증은 정확히 일치하는 시즌·빌드·장비·프로필·입력·바이너리 범위에서만 재사용하며 재실행을 의례화하지 않는다.

- **v486~v490(11/15):** 누락 v113 스냅샷 재구축/재사용; 동일 F의 여러 J 설치 SHA를 최신 파일로 임의 선택하지 않음; 기존 UI의 재검증 안내; 유일 F+기본 4보석+O=0인 경우 영약 선택에 따라 정확한 v212 설치 SHA·장신구·실행 프로필 재결합. 당시 API Ubuntu/Windows 각 398 PASS·신규 Native 0. 옛 인계 문서의 현재 판단은 이 시점에 한정.
- **11/16 M3 UI:** 설치 응답 중 기름·소켓·F/ilvl 등 입력이 바뀌면 과거 SHA/T를 적용하지 않도록 POST/GEAR GET 양쪽 검사; 빈 영약 선택에서 고급 물리 F ItemID 보존; 사용자 목표 ilvl 변경 시 시즌 Build 기본 ilvl 동기화(고급 명시 override 유지). 관련 UI/HTTP 오프라인 Actions 통과.
- **11/16 M3 결과 표시:** 재개가 차단되거나 작업자가 불완전한 회차에 이전 `V291_RESULT.json`을 새 완료 결과처럼 표시하지 않음. 관측·캐시를 삭제하지 않고 정상 pause 결과는 유지.
- **11/16 기름 O:** 동일 기름에 복수 F/J 설치본이면 자동 SHA 임의 선택 금지; 유일한 검증된 기본 4보석/일치 F와 oil 손 조건에서만 exact v212 재결합, 이미 기본 선택한 기름은 고급 ‘검증된 기름 설치본 연결’로 명시 적용. 첫 정규식 이스케이프 코드 FAIL 교정 후 오프라인 PASS; 이력이 CURRENT에 기록됨. 다중 변형 일반 선택 UX는 미완성·증거 없으면 보류.
- **11/16 M1/M2:** 기존 v212+v113 봉인 프로필이 있으면 SimC 바이너리 입력 없이 시즌 환경 **Native 0회 재사용**; 캐시 miss로 신규 G/F가 필요하면 실제 바이너리 필수, 추가 우회 엔진 없음. 일반 사용자 입력이 명시한 새 시즌 설치 SHA와 물리 F가 우선하도록 과거 시즌 메모리/사라진 F 파일의 선조회 제거. API/JS 회귀 PASS.
- **이전 M3 결함(11/16, 이미 수정·검증):** v113 장기 SimC 세션은 worker spawn 전에 `QUEUED` 기록. 로컬 로그 I/O나 `subprocess.Popen` 실패 시 가짜 QUEUED가 남는 결함을 [코드 `dfe2ab4f`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/dfe2ab4fb9ce0b5cc14fde4cf7597f14ed12df8d)로 **BLOCKED_OR_PARTIAL**, `V293_WORKER_LAUNCH_FAILED_BEFORE_NATIVE`로 안전 확정. [HTTP 회귀 `ab3abb59`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/ab3abb5920924039eff5ec23fbe792840325063e): OS spawn 실패 강제→QUEUED 제거·이전 DPS 바이트 보존·같은 봉인 세션 재개 PASS. [API Ubuntu/Windows #43788718073](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43788718073), [공통 #43788718084](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43788718084), [78 최종 #43789031893](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43789031893) SUCCESS. 이 수정의 신규 SimC Native/DB2 **0회**. [CURRENT 기록 `a60acd6b`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/a60acd6b0bff09fe649212a9ea68437b82f46253). **실제 신규 시즌 적응형 DPS 성공 증거가 아님**.

- **11/16 이후 M3 안정화 — 이미 구현/검증되어 재개발 STOP:** [기술지도 J4 연결 기록 `446693bd`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/446693bdda7ee8c8513d0de91afc6f6f8911a0f3); 영약/기름 설치 GET 도중 목표 ilvl·게임 빌드 변경 시 이전 응답 표시를 막고 **최대 1회 bounded retry** [UI `63373dbf`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/63373dbfd5269879cab4efed5ccb3cd4ccca10df) + [JS 실함수 회귀 `d7cfc4e2`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/d7cfc4e2a5348086a83a2ed6fabf047cd89b2065), 해당 HEAD Actions 5/5 SUCCESS. 기존 `v106` 세션 키 계산의 SimC 바이너리·정적 캐시 SHA를 원본 바이트와 동일한 **스트리밍 해시**로 교체 [`53d398be`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/53d398beff84c5386991c097d840cfe81dd89e54)·[`9686a588`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/9686a588e5dee4981f57d27644d2adba4c4d1cee); 기존 SHA/세션 키 및 캐시 identity 변경 없음.
- **11/16 M1 필수 원본 누락 비용 방지:** 새 시즌 일반 사용자의 **기본 자동 구축에 한해서** 원본 수집 후 기존 `v274.discover`가 컴파일 불가임을 알면 G Native를 건너뜀 [원본 코드 `db61fa5f`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/db61fa5fbd0fd485fde8672b092c60a513ec26ff) → [일반 사용자 전용 범위 `c2a68369`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/c2a683699034292cf4e78275bc68a4d9f151e0af) → [v113 모드 연결 `ce9587d7`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/ce9587d71a22b33f0e2365c9d759c14612b7a177). 명시적 개발용 G+F는 기존대로. [회귀 `84ab9721`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/84ab9721fb82c24949d892353f08312dc65c5268), [focused Actions #43813781659](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43813781659) 672 PASS/2 SKIP/0 FAIL. 해당 변경의 실제 Native0.
- **11/16 최신 M3 세션/정적 캐시 경계와 API 호환성:** `v113`에서 서로 다른 파일 경로의 정적 캐시를 봉인된 기존 세션에 재결합할 때 **바이트 동일성 SHA 비교**를 스트리밍으로 변경 [`ef57136d`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/ef57136dff17155774d0ec7c373eff1b2d40b828) + [`a754711e` 테스트](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/a754711edc14685cf886d8cd855bcea3e8507d5e). 기존 M1 신규 플래그를 False일 때도 서버에 추가해 **A1/API 계약 1건 FAIL** 발생한 사실을 숨기지 않음; [`de951a23`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/de951a23a345d21cd785305e49bee4d293827212)에서 일반 요청 필드 제거, 기본 자동 구축 True일 때만 전달해 회복. [최종 API Windows/Ubuntu #43816299019](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43816299019) 각각 409 PASS/1 SKIP·0 FAIL, **최종 코드 HEAD `de951a23` Actions 11/11 SUCCESS**. 문서 인계 직전 HEAD [`3c358998`](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/3c358998f698a19903c23592ec31130c4e83b079)의 78 계약 검사 [#43816586864](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43816586864) SUCCESS. 이번 모든 수정의 **신규 실제 Native/DB2/외부 원본 수집 0**.
- **첨부 LAST_Q&A(4).txt의 주의:** `data/season_ordinary_gem_nominal/12.1.5.70783.json` 1개만 보고 “신규 시즌 J 자동 구축 기능 자체가 미구현”으로 단정한 과거 판단은 **부정확**하다. 이미 `v221` 같은 빌드 보석 ItemID → `v268/v266` 최고 품질·2스탯 후보/명목 수치 → `v271` 4종 일반보석·각 2스탯 합계·실제 `gem_id` 장착 → `v216` J 소유자 → `v222/v212` B/T/설치 경로가 있고 70783/334 **16+7=23 × 일반4 = J92**는 실제 SimC·설치·DPS 실증. `v269` buffed SimC 보석 델타는 명목 J/최고 품질 인증의 대체물이 아님. **신규 시즌에 해당 원본/정확 수치가 실제로 확보되는지 검증해야 하는 미확정**과 **기능 자체 부재**를 구별하라. 새 보석 엔진·전수 DB·불필요한 진단 Native 만들지 말라.

**2026-11-16 최신 HEAD JSON 재집계:** `generic 27 PASS`, `current_source 27 PASS`, `product_integration 15 PASS`, `historical 13 PASS`; **15/78 COMPLETE**, `policy.next_review=B10`(검토 위치일 뿐 개발 순서 아님), `full_product_e2e=PENDING`. 15/78은 실제 구현률 19%라는 뜻이 아니다. 인계 후 새 HEAD의 JSON을 재확인한다.

## 3. 승인 M0~M7: 제품 기준·현 위치

| 단계 | 현재 의미/증거 | 중단하지 않을 필수 목표 |
|---|---|---|
| M0 | 기존 소스·실 Native·캐시·CURRENT 재사용 기준 확보 | 증거 동일성 확인, 역사 전수 감사 STOP |
| M1 | 단일 v216 시즌 Build/기존 실 Native·원본 있음; **차기 시즌 ZERO-SOURCE 최종 미수락** | **현재 최우선**: 신규 시즌 실제 대표 일반 장비·무기·4pc 및 G/J/F/O의 원본 생산→소비 첫 미확정 연결 |
| M2 | v222 예산·수동 T·v212/v098 프로필/JSON2 일부 실증 | 정확한 B/T, L/E/O 단일 귀속, 최종 rating 일치 |
| **M3** | 기본 사용자→실행/결과/캐시/취소/재개 구현, 70783 v343/v344/v417 실제 Native 사용자 경로 있음, 최근 오류 회귀 통과 | **동일 조건 성공 경로 REUSE/STOP**. 새로운 실제 사용자 차단 사례만 최소 FIX |
| M4 | 일부 고품질 선택 기능/원본·자동 등록 경로 존재 | 검증된 선택만 등록. 미확정 옵션은 개별 PENDING, BASE 비차단 |
| M5 | 26 DPS 계약·대표 무기 유형·여러 Native 증거 | 신규 경계만 대표적으로 확인, 전 전문화 Native 전수 금지 |
| M6 | 로컬 웹/API·Windows 베타 ZIP/HTTP·진행/복구 회귀 있음 | 일반 사용자 패키지/첫 실행·오류·세션·결과 실제 사용 수락 |
| M7 | **PENDING** | 기존 season seed/정적·DPS 캐시/영수증을 시험에서 격리한 **단일 정상 Environment Build → USER-E2E** 수락 |

M0~M7은 제품 완성 관리 체계이지 번호순 의무 작업표가 아니다. 78개 계약 역시 증거 관리 원장이지 별도 번호순 개발 계획이 아니다.

## 4. **현재 최우선 과제와 다음 실제 작업 하나** (제품 중심)

**핵심 판정:** 기존 70783의 M3 일반 사용자 정상 BASE 경로는 `v343/v344/v417` Native와 후속 API/UI 회귀로 이미 실증되어 **REUSE/STOP**이다. 부재를 추정해 M3 엔진/카운터·SEM·캐시를 재개발하지 않는다. 이제 가장 높은 개발 우선순위는 **M1/M2의 다른 시즌/확장팩에서 원본→G/J/F/O→B/T→검증된 정확 설치→사용자 프로필로 이어지는 필수 실사용 연결**이다. 다만 한 시즌의 성공은 전 시즌/전 26 DPS 성공 증명이 아니다.

1. **다음 채팅 첫 응답 = 읽기 전용 독립 복원 → STOP.** 최신 브랜치·HEAD·최근 Actions(성공과 실패 모두)·CURRENT 최근 5개 기록·본 문서·`INDEX/FILE_MAP/EVIDENCE_INDEX`·78 JSON·실제 70783 Native 한정 범위를 재확인. 코드·문서·테스트·Native/DB2/HTTP 실행·커밋/병합 금지.
2. 별도의 사용자 **“진행” 이후 가장 먼저 할 작업 하나:** 실제 새 시즌 일반 사용자 `시즌 환경 구축` 입력에서 **첫 필수 원본/소비 차단을 한 곳만 특정**한다. 기존 `v113` 사용자 기본 요청 → `v216` 수집/원본 소유자 → `v274/v241/v213` 컴파일 → 시즌 대표 일반 장비·무기·티어 4pc의 G → 일반4 보석 J·최고 품질 영약 F·선택 기름 O/손 → `v222` B/T → `v212` 정확 SHA 설치 → `v218/v098/v096` 사용자 프로필·정적 rating. 이미 있는 source_inventory/`source_compilation.missing`·예산/선택 옵션별 원본 증거·설치 SHA와 과거 영수증을 **먼저 읽고 재사용**한다. 미관측을 0으로, 구시즌 값을 대체 입력으로 쓰지 않는다.
3. **첫 차단이 실제 재현되면** 기존 원본 생산자·소비자 **그 한 연결만** CONNECT/FIX; 선택형 파일 부족이 정상 기본 BASE를 막는지 정확히 입증한 경우에만 기존 봉인 규칙을 유지하며 최소 교정한다. 추정된 `v274` 옵션 파일 의존성 자체를 근거 없이 빈 데이터/우회 Gate로 무효화하지 않는다. 초기 원본이 없으면 필요한 출처/빌드/권한 문제로 보고하고 READY로 위장하지 않는다.
4. M1/M2에 필수 장애가 없다면 M3는 사용자 **새 조합에서 실제로 재현되는** SHA/J/F/O/수동 T/대표 프로필/SimC 실행·결과·95%·취소/재개 오류만 최소 수정. 그렇지 않으면 해당 경로를 재개발하지 않는다.
5. 다음은 **M4** 선택 검증(선택받은 아이템만), **M5** 새 유형의 26DPS 물리 무기/4pc·옵션 일반화, **M6** Windows 배포 및 사용·복구 품질, 마지막 **M7** 엄격한 ZERO-SOURCE→USER-E2E 실제 수락 순서. 코드 구현과 공식 완료/유저 PC 품질 수락을 혼동하지 않는다.

**실행비/STOP:** 이 첫 복원 작업과 인계서 작성은 Native/DB2/HTTP 0회. 다음 “진행” 이후에도 기존 로컬 설치본/정적 아이템 캐시·DPS 캐시/70783 Native receipt를 재사용하고, 변경 경계 focused 오프라인 회귀부터 진행. 실제 SimC Native/외부 수집은 해당 시즌 필수 원본이 없고 그 실행으로 제품 판단이 바뀔 때만 최소 1회 또는 필요한 한정 수. 26전문화 Native 전수·78항목 재감사·새 G/J 엔진·불필요한 성능 최적화는 STOP.

## 5. 중기 로드맵 (기능별 완료 조건)

1. **M1/M2 단일 시즌 일반화:** 새 확장팩/빌드의 대표 ID·G/J/F/O 원본→자동 B/T/수동 T→정적 JSON2/실행 프로필을 기존 한 엔진으로 연결; 정확 원본 부족이면 해당 시나리오 차단. 동일 시즌 캐시는 재사용, 별도 SimC-only 새 엔진 금지.
2. **M4 검증 선택:** 정확한 ItemID/품질/적용 범위/SimC 입력/CHMV 소유권이 증명된 최고 품질만 자동 등록(정책 A). 영구 마부 지원, 일반 임시 마부 제외·기름 예외, 시즌 특수 콘텐츠는 독립 ON/OFF 모듈. 기본 BASE에 새 선택 Gate 만들지 않음.
3. **M5 범용성:** 26 DPS·주능력치·대표 무기 형태/4pc·기본 APL·결과 통계·캐시 identity에 필요한 유형별 기존 영수증+최소 새 경계 검증. 관측 1순위와 95% 확정·전역 미증명 구별.
4. **M6 운영:** Windows 배포, 로컬 SimC 바이너리 설정, 시즌 갱신, 사용자 세션 복원/취소/재개/오류원문/결과 재열기, 안전한 캐시/정적 자료 호환.
5. **M7 최종 수락:** 캐시/과거 시즌 seed/역사 영수증을 시험 입력에서 분리한 정상 단일 엔진 ZERO-SOURCE→USER-E2E. 새 공개 원본 수집은 정상 제품 경로에서 허용. 제품 전체 통합 PASS/78 유효 증거/권한 완료까지 정식 출시·COMPLETE라고 주장하지 않는다.

## 6. 상시 준수·비용·권한

- **매번 코드/엔진 검증 추가 이전 사용자에게 5가지 짧게 설명:** (1) 실제 화면·버튼/내부 이용 위치, (2) 사용자가 못 하는 일과 수정 효과, (3) 기존 코드/데이터/캐시/영수증 재사용, (4) 불필요한 과잉 작업과 STOP, (5) 신규 Native·HTTP/DB2·CPU·RAM/I/O·캐시 영향 및 최소 회귀 범위. 설명 정책이지 새 Gate나 매번 별도 승인 아님.
- 판단 순서 **STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW**. 미관측을 0으로, 임의 최신 설치 SHA를 정답으로, 이전 시즌 예산을 새 시즌 근거로 간주하지 않음. 검증된 설치 예산 숫자만 복사해 새 프로필 승인 우회 금지. 이전 G/F 재측정 위험이 있어도 검증·실행 원본/캐시 일치를 훼손하는 우회 복구 엔진 금지.
- 새 적응형 최적화 알고리즘, 미선택 추가 소켓/전체 아이템·SpellEffect DB, proc/APL 효과 독립 인증, 26 DPS Native 전수, 78 감사 재시작, SEM 미세화, 또 하나의 Gate/관리 시스템 금지. **기술지도에 이미 기록된 기능을 빠뜨리고 ‘신규 엔진 필요’라고 주장하는 것도 금지.** 기존 코드 삭제 전 실제 세션·호출자·호환성 확인.
- 매 변경마다 직접 수정한 기능만 오프라인 회귀 → 기존 동일 조건 실제 Native/Actions 재사용 → **정말 부족한 최소 실제 SimC 시험** 순서. 신규 PASS/FAIL과 재사용 Native, 실제 USER-E2E 및 정식 78 COMPLETE를 분리하여 기록. HTTP/DB2/Native/메모리/I/O/실행시간·캐시 미스·중복 작업을 점검.
- 원본 보고 `v016_SCENARIO_CONTRACT`는 실제 바이트·영수증 확인 전 **직접 통합 완료라고 주장 금지**. ChatGPT Project Sources/UI 실제 적용은 GitHub 문서 기록과 별개.
- 개발 격리 브랜치는 유지. 별도 사용자 명령 없이는 `main` 병합, v003 immutable 변경, 원본 v016 수정, Project Sources/Instructions UI 적용 주장, 공식 Work OS M0/Shared State·승격, MAIN/WORK 제품 개발 소유권 이전 금지. **새 채팅 인계 요청 자체는 개발 소유권 이전·공식 승격 승인이 아님**.
- 다음 채팅 첫 요청은 **오직 읽기 전용**. 관련 GitHub 현재 자료를 확인하고 ①최신 HEAD ②현재 실제 사용자 가능/막힘 ③기존 PASS/Native 재사용 ④M0~M7·78 ⑤필수 미완료와 선택 PENDING ⑥가장 작은 다음 장애 후보 ⑦권한/미확인 자료를 간결히 보고한 뒤 **STOP**. 별도 `진행` 전 수정·GitHub 문서 추가·테스트/Actions/Native/수집 금지.

**종료: 본 문서의 SHA는 인계 시점 스냅샷이며 새 채팅에서 현재 사실로 복제하지 않는다.**
