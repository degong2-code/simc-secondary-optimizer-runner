> **이 문서는 역사 v382 인계입니다. 2026-11-13 최신 사용자 결정과 이후 v383–v386 개발을 승계한 [v386 최신 독립 인계](CHAT_CONTINUITY_HANDOFF_20261113_P1_V386_ZERO_SOURCE_GENERALIZATION.md)를 먼저 읽으십시오.** 범용 기능의 완료 판정은 [현재 시즌 ZERO-SOURCE 자동 발견 PASS 정책](development/POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md)가 우선하며, 미래 시즌 미출시 사실만으로 해당 ENGINE 기능을 계속 PENDING으로 둘 수 없습니다. 아래 시점·HEAD·'첫 작업'은 역사가 된 정보이므로 최신 GitHub HEAD/78원장 확인이 필요합니다.

# SIMC SECONDARY OPTIMIZER — 2026-11-13 단일 인계 정본
## v382 · 78개 준비 요소별 완료 관리·기존 실증 재사용·P1 제품 통합

> **2026-11-13 후속 사용자 직접 결정 (v382 작성 후 문서 증분):** 새 채팅에서 [범용 개발·정합성·미래 시즌 검증 운영 헌장](development/OPERATING_CHARTER_FUTURE_SEASONS_AND_EVIDENCE_20261113.md)을 **매 개발 착수 전 가장 먼저 참조**한다. 현재 실제 시즌 ZERO-INSTALL/엄격 ZERO-SOURCE, 가상 미래 시즌 ZERO-CONTRACT, 사용자 USER-E2E를 혼동하지 않고, 미래 시즌 READY를 현재 선승인하지 않는다. 이번 추가 권한은 GitHub 문서화에 한정하며 별도 '진행' 전 제품 코드·시험 금지 및 main/공식 UI 권한은 유지한다.

> **이번 사용자 직접 요청의 최우선 목적:** 기존 통상적 ‘개발 상태 인계’보다 **[78개 준비 요소 추적표](development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md)**를 중심으로 단기 로드맵을 세우고, 새 일반 채팅에서 각 요소를 **이미 갖춘 것 / 끊긴 연결 / 부족한 증거 / 실제 완료**로 구분하여 하나씩 준비 완료시킨다. 이 인계보다 더 오래된 일반 프롬프트와 v365 이전 인계의 시간상 ‘최신’ 서술은 우선하지 않는다. 사용자가 새 일반 채팅으로 이전하라고 명시 요청했으므로 **이 업무의 후속 작업 채팅을 새 채팅으로 지정**하되, **첫 응답은 읽기 전용 복원 후 STOP**. 사용자의 별도 “진행”이 있어야 이후 실제 개발을 시작한다.
>
> **인계 기준 시점·HEAD:** 격리 브랜치 `probe/chat-cache-v035-20261024` 실제 조회 기준 v381 HEAD `f13cf187474507ca6b120a3c6bb631946d888818` (단일 인계·추적표 커밋 **이전**). `main` HEAD `07133e0aaf738d6e4816a6486057b1cd49c018de`. **이 문서를 커밋하면 격리 HEAD가 달라지므로 새 채팅은 반드시 실시간 조회**. GitHub 문서 작성은 실제 Project Sources 등록·main 병합·Work OS 승격이 아님.
>
> **증거 신분:** 이 인계는 첨부 `LAST_Q&A(1).txt`의 78개 감사와 현재 GitHub 코드·기존 영수증을 연결한 **문서 작업**이다. 신규 SimC Native/Actions/실 API·DB2 수집/제품 Windows 실행 **0회**. 78개의 실제 완료 시험을 새로 수행한 것이 아니다.

## 1. 최종 목적·최신 승인 정책

- **26 DPS 전문화만**(증강 기원사·탱커·힐러 제외). 사용자는 미래 목표 ilvl(기본334) 또는 **직접 지정 최종 T**에서 SimC DPS가 최대인 **치명·가속·특화·유연 절대 rating**을 구한다. 결과는 예상 DPS·SEM·95% 통계, 관측 1순위·확정 여부·실질적으로 다른 근접 대안·비율.
- 장비 조합/파밍 경로 추천·시즌 전체 장비 DB·현재 착용 장비 총량 재분배는 목표가 아니다. 사용자는 직업/전문화/종족/특성·장신구 2개·특수장비·장식 최대2·보석/영약/기름/소모품/전투조건을 선택하며 대표 일반 방어구/무기/티어는 내부 생성. SimC 프로필 업로드는 선택 편의 기능이고 현재 장비를 목표로 복사하지 않는다.
- **모든 시즌에서 G/J/F/O를 해당 시즌 원본으로 자동 구축.** `B=G+J+F`, `T=B+O`, `c_final=c_base+o`; 수동 최종 T 우선. 선택 특수 장비 L은 G 안 포함/하한, 정적 마부 E·기름 O는 한 번만 반영, 장신구 정적은 자유 G 밖. 제작 초기 50:50은 고정 하한 아님. 새 시즌에 역사 `G/J/F/O` 수치를 검증 없이 복사하지 않는다.
- **티어는 5부위 ID 전부 수집**, 실제 장착은 특수/장식 충돌을 고려해 **4세트** 확보. 기존 `v101/v098/test_v187`에서 유동 장착 **이미 구현**; 새 시즌 개인 변형의 소스/프로필 연결만 미완.
- 영약 F는 검증된 최고품질의 효과별 정적 rating이 핵심이며 대표 기본 영약 1종을 우선 사용. F로 최종 특정 스탯 rating=0 불가능할 수 있으나 **장비 자유분배량 0 후보는 허용**. 필요하면 다른 F로 바꾼 별도 SimC/캐시 시나리오를 기존 최적화 엔진으로 비교한다.
- 현재 지원 기름은 적용 손당 **치명과 가속에 동일 q**; 손 적용의 공통 규칙을 시즌마다 새 연구로 반복하지 않는다. 시즌 수치 q/선택 아이템·손은 정확한 소스로 검증. 주술사 질풍/불꽃혓바닥 무기는 같은 손 일반 기름과 배타적으로 처리할 연결 필요; DK 룬벼리기는 영구 무기마부. `O=0`은 v222의 명시 증거로만 확정. 사용자 UI 기본 기름 ON과 시즌 공통 Build의 기준 O0는 서로 다름.
- **최고 품질만 일반 UI 노출**: 동일 효과·사용조건·범위·수치 비열등성 확인 후에만 하위 품질 중복 제거. 일반 임시 마부 전체는 **제품 범위 제외**, 영구 마부/별도 무기 기름 지원. 확장팩 전용 시스템은 선택형 모듈. 증거 충족 선택지는 Policy A로 자동 등록, 미선택/미확정 후보는 해당 항목만 보류.
- SimC가 proc·장비/소모품 효과·APL·DPS 소유. 앱이 원본/장비·CHMV 예산·고정치·gear_* 중복·JSON2·탐색·95%·캐시·취소재개 소유. 독립 효과 인증 Gate·시즌 전체 아이템 인증·새 적응형 엔진 구축 금지.
- 신규 시즌 READY에는 **필수로 소비하는 출처/빌드/대표 장비·무기·티어5·G/J/F/O/B/T·최고 품질·입력 정합과 영수증**이 충족되어야 한다. 사용자 미선택 아이템의 WSE/획득경로 미해석을 전체 READY 차단으로 만들지 않는다. **기본 시즌 READY와 선택 사용자 변형 READY는 다르다.**
- 출처는 실제 자동 수집한 **Blizzard API, WCL API(승인 외부), 같은 빌드 DB2, pinned SimC** 및 봉인 영수증. GPT 웹검색/공지 비교/수작업 추론으로 런타임 READY를 승인하지 않는다.
- 우선순위: **최신 사용자 직접 결정 > 승인 [v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) 및 충돌 없는 v1.4 계열 > GitHub 현재 코드·영수증 > 과거 노트**. v1.4.1에 남은 27 DPS는 역사로만 해석.

## 2. 새 인계의 기준 지도: 78개 전부, READY Gate는 최소

| 묶음 | 수 | 구분 | 주요 관리 대상 |
|---|---:|---|---|
| A | 11 | 시즌·원본 | 시즌/빌드·Blizzard/WCL/DB2/SimC·JOIN·영수증 |
| B | 12 | 대표 장비 | 26 DPS·대표 무기/주능력/G·티어5원본/4pc·촉매·소켓 |
| C | 14 | 소모품·마부 | 보석·영약·기름·직업 무기 강화·영구 E·음식/물약 |
| D | 9 | 사용자 선택 | 장신구·특수 L·제작/장식·충돌·수동 ItemID·모듈 |
| E | 9 | 예산/주입 | G/J/F/O, B/T, 수동 T, L/E, floor/gear_*·JSON2 |
| F | 7 | 사용자 SimC 프로필 | 특성·업로드·APL·기본/고급 전투·실 바이너리 |
| G | 10 | 제품 운영 | 원본 실행·공통/개인 READY·캐시·UI·한글·Windows |
| **A–G 소계** | **72** | **환경 구축+사용자 경로** | 기본 필수와 선택 사용 시 필수의 분리 |
| H | 6 | 환경 이후 최적화 | v290/95%·SEM/대안·자원·취소재개·결과 |
| **총계** | **78** | **개발 추적 단위** | 독립 Native 78회 또는 전역 Gate 78개 아님 |

**각 항목의 정확한 ID·필요정보·과거 구현 수준·기존 코드·다음 완료작업은 반드시 [78개 추적표](development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md)를 사용.** 최초 29개 개요를 다시 기준으로 삼지 않는다. 항목별 `READY_SCOPED`에는 실제 조건·원본·검증 영수증을 연결해야 하며 무조건 78개 신규 실증을 요구하지 않는다. 상태가 미확정인 항목을 미구현으로 단정하지 않는다.

## 3. 역사적으로 확인한 구현·실증, 지금 미실증

| 구분 | 이미 있는 것/증거 | 한계 |
|---|---|---|
| 기본 환경 70783, ilvl334 | [v337 실 Native 기본 4보석](development/notes/2026-11-11_p1-v337-real-coldstart-environment-ko-reuse.md), [v343 Windows 기본 G2850 J92 F165 O0 B=T3107](development/notes/2026-11-11_p1-v343-current-70783-windows-source-native-once.md) | 이 빌드/기본 구성 한정. 다른 시즌/8소켓/특수/기름 사용 증거 아님 |
| 사용자 Chrome → 환경 → DPS | [v344 Windows 신규 DPS Native64·취소/재개](development/notes/2026-11-12_p1-v344-real-windows-browser-native64-once.md) | 해당 한 전문화·조건 실증, 최신 v381 또는 현 사용자 PC 전체 실증 아님 |
| 공통 시즌 vs 사용자 변형 | [v350 Windows/API 회귀](development/notes/2026-11-12_p1-v350-common-season-user-variant-split.md), `v113/v098` | 사용자가 변경한 F/O/소켓 exact 설치 SHA 없으면 HTTP422/Native0, 신규 변형 양성 Native 미실증 |
| 티어 유동 장착 | `v101/v098/test_v187`로 5중4 조합 기존 구현 | 새 시즌 `season_profile_inputs` 특수/장식 입력 연결 제한 |
| 기본 F·하한 | [P3-GL/GN/GP 실 F+165 범위](development/notes/2026-11-06_p3-gp-single-flask-only-real-native-attempt.md), `v065/v124` | 대표 F가 전문화별 최적의 전역 증거 아님 |
| v365 WSE 파서 | [v365 4개 Actions 경로](development/notes/2026-11-12_p1-v365-db2-conditional-season-parse.md) | 시즌 전체 장비 소속 해석/새 환경 READY는 별도 |
| v374–v381 최근 | [개별 노트와 코드](development/INDEX.md): 요청 범위 분리, 티어·F/O 정정, 과거 연구 지도, v379 UI 원인·v380 9 입력 공급자·v381 G/J/F/O owner 보고 | 대부분 로컬 focused/assertions·소스 감사. 후속 전체 GitHub Actions/Windows Native 양성 **미실증**, v381은 READY 판정 자체 변경 없음 |

**마지막 제품 코드:** v381 격리 HEAD `f13cf187474507ca6b120a3c6bb631946d888818`. 인계 중 새 제품 코드·테스트는 수정하지 않는다. **이번 작업은 문서/추적표 기록만**.

## 4. 실제 병목·실제 개발 시작점

1. **증거 분리:** `runner/v216_environment_build_coordinator.py`의 `required_core_source_owner_report`와 `source_compilation.missing`을 실제 Build 영수증 기준으로 대조. 사용자 v163 후보 JSON(434후보)은 전체 실제 `source_compilation.missing` 또는 해당 실 Windows G/J/F/O source owner가 없음. 부족한 실제 필드를 확보하기 전 특정 READY 차단 원인을 추측하지 않는다.
2. **카탈로그와 숫자:** `v274/v275/v241`의 9개 완전 카탈로그 파일 입력은 `v191/v211/v213` 컴파일 계약이고 **G/J/F/O 수치 인증 9종**이 아니다. `v222/v212`는 별도 정확 원본·B/T 정합 설치 소유. v380–v381은 진단만 연결; 미검증 카탈로그를 READY로 우회하면 안 된다.
3. **기본 READY**: 유효한 v343/v344 봉인된 같은 시즌 자료를 우선 재사용, 필요한 새 선택·빌드 값만 기존 수집기로 확인, `v216→v222→v212` 한 정상 조건 설치. 시즌이 달라졌으면 숫자 복사 금지.
4. **개인 변형**: 기존 `v101` 유동 4pc와 `v098` 사용자 특수장비/장식 연계, 1개 변경된 소켓·영약 F·기름 O의 원본·예산·설치 SHA를 확인. 사용자 선택 미검증이면 422 유지.
5. **SimC 제품 최종 연결**: 기존 `v290/v291/v293` 적응형 N56/후보 정밀320/95%·캐시/취소재개를 써서 한 개인 변형의 JSON2·DPS·SEM·관측1순위·대안·비율까지 실제 출력. 이후 나머지 26 DPS/선택지·시즌 업데이트를 **변경 영향 범위만** 증분 확인.

## 5. 단기 실행 로드맵: 작업 묶음별 인수 조건

### M0 — 78개 분해·기능/증거 역추적 (읽기 전용부터)
- 이번 추적표는 이미 78/78 목록화. 새 채팅은 INDEX→FILE_MAP→EVIDENCE_INDEX에서 **P1 직결 항목**의 기존 코드/시험·영수증만 다시 대조한다. **전 문서 전수 독서 금지.**
- 선행 결과: 선택된 시나리오의 정확한 시즌/빌드/ilvl/소켓/F/O·설치 상태와 각 원본 소유자의 `missing` 확정. 보고 없는 항목은 `PENDING_EVIDENCE`, 코드가 있다는 이유로 새 ‘준비 완료’로 세지 않음.

### M1 — 기본 공통 Environment Build READY
- **REUSE/CONNECT:** A 필수 소스 → B 대표 장비/티어5/무기/G → C 기본 J/F/선택 O0 → E B/T·고정 하한/gear_* → G v212 정상 설치. 같은 시즌 유효한 v337/v343 Native 영수증 재사용.
- 완료: 한 명시 시즌/빌드/ilvl에 대해 정확한 source owner/SHA, 설치된 기본 프로필/정적 숫자 확인, 기존 v212 `READY`; 미선택 아이템·모듈은 전역 Gate 아님. 비밀키 비노출.

### M2 — 선택 사용자 변형 설치·정적 정합
- **CONNECT:** 기존 v350 개인 변형 검증, v101 5→4, 정확한 장신구2/특수장비/장식 최대2, 보석/소켓·F/O·영구 E·수동 최종 T를 동일 조건에 반영. 주술사 기름 배타는 **해당 전문화 선택 시만** 필수.
- 완료: 한 검증된 사용자 변형에 대해 설치 SHA와 v098 정상 프로필, G/J/F/O/L/E·T/JSON2 정적 rating 일치; 변형 미검증은 422 유지.

### M3 — 최종 제품 E2E·회복·출력
- **REUSE:** v290 적응형 SimC, N56→정밀320, 95% 및 의미있는 대안, v293 캐시·취소/재개, Windows 입력/결과.
- 완료: 한 검증된 사용 조건에서 SimC native JSON2·DPS/SEM·관측 1순위/95% 결과·비율·대안/한계와 정상 세션 보존, 재실행 시 캐시와 중단/재개 일관. 현재 증거의 적용조건을 명시.

### M4 — 나머지 78개 범위 증분 완료
- A~G의 BASE/USER/OPTION 혼합을 **선택한 기능의 소비 필요 정보**에 따라서만 검증하고, H6까지 사용자 출력 성공 후 다른 전문화·고급 전투·F 변경·주술사·시즌 모듈을 개별 추가.
- 제품의 비지원 항목(일반 임시 마부, 증강, 탱커/힐러 등)은 `NOT_APPLICABLE_SCOPE`로 관리하고 새로운 구현 Gate로 만들지 않음. 기능별 `READY_SCOPED`는 적용 조건·증거 포함.

## 6. 매 반복 개발의 의무 기록

각 사용자의 “진행”마다 `78개 추적표`에서 우선순위와 의존 관계에 따른 **1개 또는 연결된 최소 묶음**을 선택하고, `REUSE/CONNECT/EXTEND/REPLACE/NEW/STOP` 결정 → 기존 구현·Native·캐시 재사용 조회 → 최소 변경 → 국소 테스트/필요 최소 Native → 실제 증거와 상태 갱신 → 다음 요소를 정한다. 모든 요소를 무의미하게 하나씩 신규 Native 실행하지 않는다. 부정확한 기존 구현 판정은 새 증거와 함께 정정한다.

결과는 **구현**, **오프라인 PASS**, **Actions PASS**, **실 Windows Native PASS**, **사용자 실제 E2E**, **아직 미실증**, **BLOCKED**를 별도로 기록하고, `README`·`CURRENT`·INDEX·DECISIONS·EVIDENCE_INDEX는 **실제 해당 변경이 있을 때만** 수정한다. 사소한 새 노트를 날짜순으로 INDEX 상단에 누적시키지 않는다.

**권한:** 이 요청은 사용자가 *후속 새 일반 채팅으로 해당 계획을 인계*하라는 **명시적 지시**다. 중복 진행을 피하기 위해 첫 복원 후 해당 새 채팅이 후속 개발 흐름을 맡되, **사용자의 별도 '진행' 전 실행 금지**. `main`, immutable v003, 원본 v016, Project UI/Sources/Instructions, 공식 Work OS M0·Shared State·공식 승격은 별도 승인 없이 변경하지 않는다. WEQUIP 운영 의존성 금지. 사용자 로컬 API 비밀정보는 GitHub/로그/채팅에 넣지 않는다.

## 7. 새 일반 채팅 첫 자료 읽는 순서

1. **이 단일 인계 정본**.
2. **[78개 요소별 준비 추적표](development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md)**. A–H 78개, 상태·범위·증거·다음 작업이 본 업무의 중심.
3. [START_HERE](development/START_HERE.md) → [INDEX](development/INDEX.md) → [FILE_MAP](development/FILE_MAP.md) → [EVIDENCE_INDEX](development/EVIDENCE_INDEX.md) → [DECISIONS](development/DECISIONS.md) → [PROTOCOL](development/PROTOCOL.md). 필요한 P1 관련 범위만.
4. [v1.4.3 최신 시즌 자동 G/J/F/O 정책](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md)·최신 사용자 v377 결정과 충돌없는 자료. [v365 전 인계](CHAT_CONTINUITY_HANDOFF_20261112_P1_V365_UI_FREEZE_SOURCE_JOIN_NEXT.md)는 과거 성공/문제 복원용.
5. 구체 작업을 시작할 때만 `v113/v216/v274/v275/v222/v212`, `v101/v098/v350`, `v290/v291/v293` 및 실제 tests/Actions. 장문 `CURRENT`·역사 287노트 전체 재독 금지.

## 8. 새 일반 채팅용 독립 시작 프롬프트 (복사)

> **SIMC SECONDARY OPTIMIZER — 78개 환경·제품 준비 요소 기반 후속 개발 인계.**
>
> 이번 인계의 **최상위 목적**은 예전 일반적인 프로젝트 인계문을 복원하는 것이 아니라, 사용자 승인된 2026-11-13 **A–G 환경 72개 + H 최적화 6개 = 총78개 세부 항목을 실증과 함께 하나씩 준비 완료시키는 단기·장기 개발 운영**이다. 78개는 78개 독립 Gate/Native 수행 의무가 아니며, 시즌 공통 BASE READY와 사용자 USER/OPTION 변형 READY는 분리한다. 개발은 기존 구현·실증을 먼저 재사용하고 끊긴 연결만 최소 수정한다.
>
> 저장소는 `degong2-code/simc-secondary-optimizer-runner`, 최근 격리 브랜치는 `probe/chat-cache-v035-20261024`, 인계 작성 **전** 코드 HEAD는 `f13cf187474507ca6b120a3c6bb631946d888818`(v381), `main`은 `07133e0aaf738d6e4816a6486057b1cd49c018de`였다. **반드시 GitHub 최신 HEAD를 별도 재조회**, 인계 문서 커밋 후 SHA가 달라짐을 이해해라. `main` 병합 금지.
>
> **최신 단일 인계 정본:** `docs/CHAT_CONTINUITY_HANDOFF_20261113_P1_V382_78_ELEMENT_READINESS.md`. **78개 핵심 관리표:** `docs/development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md`. **읽는 순서:** 단일 인계 → 78개 표 → `docs/development/START_HERE.md` → `INDEX.md` → `FILE_MAP.md` → `EVIDENCE_INDEX.md` → `DECISIONS.md` → `PROTOCOL.md` → `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md` → 필요할 때만 관련 v343/v344/v350/v365/v374–v381 코드·시험·원본 영수증. 과거 대화·장문 CURRENT·전체 노트를 전수 재감사하지 마라. 원본 `LAST_Q&A(1).txt`의 78요소 감사 내용은 GitHub 표에 전사됐으나 새롭게 78개 시험했다는 뜻은 아니다.
>
> **제품:** 증강 제외 **26 DPS**, 미래 목표 ilvl(기본334) 또는 수동 최종 T의 SimC DPS 최대 CHMV 절대 rating. `B=G+J+F`, `T=B+O`, 수동 T 우선; 티어5 원본·실제4pc, 영약 F 고정 스탯 하한과 자유분배0, 기름 손당 치명/가속 동일 q 및 1회 가산, 주술사 무기 강화 충돌, 선택 L/E 회계·현재 장비 미복사. SimC 효과/APL/Proc/DPS 책임, 95% SEM 판정, 캐시·취소/재개. 일반 임시 마부·장비 파밍 추천·시즌 전 아이템 DB·무관한 WSE 인증 금지.
>
> **기존 성과:** v343 70783 기본 G2850/J92/F165/O0·B=T3107/Windows Native, v344 특정 조건 Chrome→DPS Native64/재개, v350 시즌 공통과 개인 변형 검증 분리, v101/v098/v187 5티어 중4 유동 조합, v290·v291·v293 최적화/캐시. v374–v381은 요청 범위·카탈로그 입력·기본 G/J/F/O 소유자 진단 중심 **국소 개선**으로 전체 시즌 READY 완료가 아니다.
>
> **첫 재개 P1:** 실제 v216 `source_compilation.missing` 및 `required_core_source_owner_report`에서 9개 카탈로그 입력 부족과 제품 필수 G/J/F/O 증거 부족을 구별하고, 기존 v275/봉인 원본·v343 성공 경로를 재사용해 기본 시즌 READY→개인 정확 설치→기존 SimC v290 최적화 E2E로 연결. 모든 항목은 `REUSE/CONNECT/EXTEND/REPLACE/NEW/STOP`, `READY_SCOPED` 증거, 남은 의존성을 78개 표에 갱신. 78개 전수 재연구·Native 재실행 금지.
>
> **첫 응답은 읽기 전용 복원 결과만:** 실제 HEAD·승인 정책/정확한 실증 범위·A~H 78개 현황·중복 구현 방지·단기 M0–M4 로드맵·첫 작업 항목 ID와 완료 조건·권한을 보고하고 **즉시 STOP**. 사용자가 별도로 **“진행”**이라고 하기 전에는 코드·GitHub 문서 변경, 테스트, Actions, Native, API/DB2 신규 수집, 커밋·병합, Project UI·공식 승격·비밀키 취급을 절대 시작하지 마라. 개발 시작 승인은 새 일반 채팅의 후속 작업에 한정되고 main/Work OS 권한으로 확대되지 않는다.
